import wikipedia
import codecs
from bs4 import BeautifulSoup
import requests
from multiprocessing import Pool
import os
from wikipedia.exceptions import PageError, DisambiguationError
from collections import defaultdict as dd

BASE_URL = "https://en.wikipedia.org"
WHAT_LINKS_HERE_URL = "https://en.wikipedia.org/w/index.php?title=Special:WhatLinksHere/{}&limit={}"
MIN_SENTENCE_SIZE = 8

LOGGER = None

def extract_instances(content, word, pos, starting_instance_id):
    instances = []
    instances_replaced = []
    for line in content.split('\n'):
        tokens = line.split()
        num_of_tokens = len(tokens)
        if num_of_tokens >= MIN_SENTENCE_SIZE:
            for i in xrange(num_of_tokens):
                if word in tokens[i].lower():
                    starting_instance_id += 1
                    instances.append(u"{} <{}.{}.{}>{}</{}.{}.{}> {}".format(u' '.join(tokens[:i]), word, pos, starting_instance_id,
                                                                                 tokens[i], word, pos, starting_instance_id,
                                                                                 u' '.join(tokens[i+1:])))

                    instances_replaced.append(u"{} <{}.{}.{}>{}</{}.{}.{}> {}".format(u' '.join(tokens[:i]), word, pos, starting_instance_id,
                                                                                word, word, pos, starting_instance_id,
                                                                                u' '.join(tokens[i+1:])))

    return instances, instances_replaced, len(instances)


def wiki_page_query(page_title):
    try:
        LOGGER.debug('Retrieving {} from Wikipedia'.format(page_title))
        p = wikipedia.page(page_title)
        return p
    except PageError:
        LOGGER.debug("Page '{}' not found.".format(page_title))
        # wikipedia library has a possible bug for underscored page titles.
        if '_' in page_title:
            title = page_title.replace('_', ' ')
            LOGGER.debug("Trying '{}'".format(title))
            return wiki_page_query(title)
    except DisambiguationError as e:
        LOGGER.warning('DisambiguationError for {}:{}'.format(e.title, '\t'.join(e.options)))
        return None  # This is most likely the "What links here" page and we can safely skip it.


def extract_from_page(page_title, word, offset, fetch_links):
    pos = offset[-1]

    p = wiki_page_query(page_title)
    if p is None:
        LOGGER.warning('No page found for {}'.format(page_title))
        return [], []

    instances, instances_replaced, count = extract_instances(p.content, word, pos, 0)
    if fetch_links:
        links = fetch_what_links_here(p.title)
        for link in links:
            link_page_title = link.replace('/wiki/', '')
            link_page = wiki_page_query(link_page_title)
            if link_page is not None:
                link_instances, link_instances_replaced, link_count = extract_instances(link_page.content, word, pos,
                                                                                        len(instances))
                instances.extend(link_instances), instances_replaced.extend(link_instances_replaced)

    return instances, instances_replaced


def extract_instances_for_word(senses, wiki_dir='../datasets/wiki/'):
    LOGGER.info("Processing word: %s" % senses[0]['word'])
    instances = []
    instances_replaced = []
    for sense_args in senses:
        sense_instances, sense_instances_replaced = extract_from_page(**sense_args)
        instances.extend(sense_instances)
        instances_replaced.extend(sense_instances_replaced)

    # TODO: create a file in ..datasets/wiki/ and write instances.
    # original version
    with codecs.open(os.path.join(wiki_dir, '%s.txt' % senses[0]['word']), 'w', encoding='utf8') as f:
        f.write('\n'.join(instances))

    # target word replaced version (e.g., dogs, DOG, Dog are replaced by 'dog')
    with codecs.open(os.path.join(wiki_dir, '%s_replaced.txt' % senses[0]['word']), 'w', encoding='utf8') as f:
        f.write('\n'.join(instances_replaced))


def fetch_what_links_here(title, limit=100):
    url = WHAT_LINKS_HERE_URL.format(title, limit)
    links = []
    LOGGER.debug("Processing link: %s" % url)
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        rows = soup.find(id='mw-whatlinkshere-list').find_all('li', recursive=False)
        links = [row.find('a')['href'] for row in rows]
    else:
        LOGGER.error("Error while link fetching: %s" % url)

    assert len(links) <= limit, "Fetched links are more than the limit."
    return links


def extract_from_file(filename, num_process):
    import utils

    global LOGGER
    LOGGER = utils.get_logger()

    pool = Pool(num_process)
    jobs = dd(list)
    for line in open(filename):
        line = line.split()
        target_word, page_title, offset = line[:3]
        jobs[target_word].append(dict(word=target_word, page_title=page_title, offset=offset, fetch_links=True))

    LOGGER.info("Total {} of jobs available. Consuming has been started.".format(len(jobs)))
    pool.map(extract_instances_for_word, jobs.values())
    # For debug:
    # for v in jobs.values():
    #     extract_instances_for_word(v)
    # LOGGER.info("Done.")


if __name__ == '__main__':
    pass
