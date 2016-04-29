# -*- coding: utf-8 -*-

import wikipedia
import codecs
from bs4 import BeautifulSoup
import requests
from multiprocessing import Pool
import os
from wikipedia.exceptions import PageError, DisambiguationError
from collections import defaultdict as dd
from requests.exceptions import ConnectionError, ContentDecodingError
from time import sleep
from wikipedia.exceptions import WikipediaException


BASE_URL = u"https://en.wikipedia.org"
# What Links Here url. Redirection pages omitted.
WHAT_LINKS_HERE_URL = u"https://en.wikipedia.org/w/index.php?title=Special:WhatLinksHere/{}&limit={}&hideredirs=1"
MIN_SENTENCE_SIZE = 8

LOGGER = None

SLEEP_INTERVAL = 1


def extract_instances(content, word, pos, sense_offset, target_word_page, categories, url=None):
    instances = []
    instances_replaced = []
    for line in content.split('\n'):
        tokens = line.split()
        num_of_tokens = len(tokens)
        if num_of_tokens >= MIN_SENTENCE_SIZE:
            sentence = []
            sentence_not_replaced = []
            is_observed = False
            for i in xrange(num_of_tokens):
                if word in tokens[i].lower():
                    sentence.append(u"<target>%s<target>" % word)  # replaced
                    sentence_not_replaced.append(u"<target>%s<target>" % tokens[i])
                    is_observed = True
                else:
                    sentence.append(tokens[i])
                    sentence_not_replaced.append(tokens[i])

            if is_observed:
                instances.append(u"{}\t{}\t{}\t{}\t{}\t{}".format(u' '.join(sentence_not_replaced),
                                                                  pos, sense_offset, target_word_page, url,
                                                                  u'\t'.join(categories)))
                instances_replaced.append(u"{}\t{}\t{}\t{}\t{}\t{}".format(' '.join(sentence), pos, sense_offset,
                                                                           target_word_page, url,
                                                                           u'\t'.join(categories)))

    return instances, instances_replaced


def wiki_page_query(page_title, num_try=1):

    if num_try > 5:
        return None

    global SLEEP_INTERVAL

    try:
        LOGGER.debug(u'Retrieving {} from Wikipedia'.format(page_title))
        p = wikipedia.page(page_title)
        SLEEP_INTERVAL = 1
        if p is not None:
            try:
                categories = p.categories
            except KeyError:  # Somehow sometimes wikipedia library can't fetch any category.
                categories = []
            return p.title, p.content, p.url, categories
        else:
            return None
    except PageError as e:
        LOGGER.info(u"PageError: {}".format(page_title, e))
        # wikipedia library has a possible bug for underscored page titles.
        if '_' in page_title:
            title = page_title.replace('_', ' ')
            return wiki_page_query(title)
    # This is most likely the "What links here" page and we can safely skip it.
    except DisambiguationError:
        LOGGER.debug(u'Disambiguation Error for {}... get skipped.'.format(page_title))
        return None
    except ConnectionError as e:
        SLEEP_INTERVAL *= 4
        LOGGER.info(u"ConnectionError: Sleeping {} seconds for {}.".format(SLEEP_INTERVAL, page_title))
        sleep(SLEEP_INTERVAL)
        wiki_page_query(page_title, num_try + 1)  # try again.
    except WikipediaException:
        wiki_page_query(page_title, num_try + 1)  # try again.
    except ContentDecodingError as e:
        LOGGER.info(u"ContentDecodingError: Trying ({})".format(num_try+1))
        wiki_page_query(page_title, num_try+1)
    except ValueError as e:
        LOGGER.info(u"ValueError... Sleep and Trying ({})".format(num_try+1))
        sleep(4)
        wiki_page_query(page_title, num_try+1)


def extract_from_page(page_title, word, offset, fetch_links):
    pos = offset[-1]

    response = wiki_page_query(page_title)
    if response is not None:
        title, content, url, categories = response
    else:
        LOGGER.warning(u'No page found for {}'.format(page_title))
        return [], []

    instances, instances_replaced = extract_instances(content, word, pos, offset, True, categories, url)
    if fetch_links:
        links = fetch_what_links_here(title, limit=1000)
        for link in links:
            link_page_title = link.replace(u'/wiki/', '')
            # skip irrelevant articles.
            if any(map(lambda x: link_page_title.startswith(x), ['Talk:', 'User_talk:', 'User:'])):
                continue
            link_page_response = wiki_page_query(link_page_title)
            if link_page_response is not None:
                title, content, url, categories = link_page_response
                link_instances, link_instances_replaced = extract_instances(content, word, pos, offset, False, categories, url)
                instances.extend(link_instances)
                instances_replaced.extend(link_instances_replaced)

    return instances, instances_replaced


def write2file(filename, lines):
    with codecs.open(filename, 'w', encoding='utf8') as f:
        LOGGER.info("Writing {}".format(filename))
        f.write(u'\n'.join(lines))
        f.write('\n')


def extract_instances_for_word(senses, wiki_dir=u'../datasets/wiki/'):
    LOGGER.info(u"Processing word: %s" % senses[0]['word'])
    instances = []
    instances_replaced = []
    for sense_args in senses:
        sense_instances, sense_instances_replaced = extract_from_page(**sense_args)
        instances.extend(sense_instances)
        instances_replaced.extend(sense_instances_replaced)

    write2file(os.path.join(wiki_dir, u'%s.txt' % senses[0]['word']), instances)
    write2file(os.path.join(wiki_dir, u'%s.tw.txt' % senses[0]['word']), instances_replaced)


def get_next_page_url(soup):
    # here we assume that next link is always in -6 index.
    element = soup.select_one('#mw-content-text').find_all('a')[-6]
    if element.text.startswith('next'):
        return u"{}{}".format(BASE_URL, element['href'])
    else:
        # No more element left.
        return None


def fetch_what_links_here(title, limit=1000, fetch_link_size=5000):
    # Max fetch link size is 5000.
    global SLEEP_INTERVAL

    fetch_link_size = min(limit, fetch_link_size)
    all_links = []
    next_page_url = WHAT_LINKS_HERE_URL.format(title, fetch_link_size)
    total_link_processed = 0
    content = None
    while total_link_processed < limit and next_page_url is not None:
        LOGGER.debug(u"Processing link: %s" % next_page_url)
        try:
            response = requests.get(next_page_url)
            content = response.content
            SLEEP_INTERVAL = 1
        except (ConnectionError, WikipediaException) as e:
            SLEEP_INTERVAL *= 2
            LOGGER.info(u"ConnectionError, WikiException: Sleeping {} seconds for {}.".format(SLEEP_INTERVAL, title))
            sleep(SLEEP_INTERVAL)
            continue  # try at the beginning
        except ValueError:
            LOGGER.warning("ValueError occured for {}".format(title))
        try:
            if response.status_code == 200 and content is not None:
                soup = BeautifulSoup(content, 'html.parser')
                rows = soup.find(id='mw-whatlinkshere-list').find_all('li', recursive=False)
                links = [row.find('a')['href'] for row in rows]
                next_page_url = get_next_page_url(soup)
                total_link_processed += len(links)
                all_links.extend(links)
            else:
                LOGGER.error(u"Error while link fetching: %s and %s" % (next_page_url, response.status_code))
                break
        except ValueError:
            LOGGER.warning("ValueError occured 1 for {}".format(title))
            exit(-1)

    return all_links


def extract_from_file(filename, num_process):
    import utils

    global LOGGER
    LOGGER = utils.get_logger()

    dataset_path = u'../datasets/wiki'
    # get processed words
    processed_words = set([word.split('.')[0] for word in
                           filter(lambda x: x.endswith('.replaced-all.txt'), os.listdir(dataset_path))])

    jobs = dd(list)
    for line in codecs.open(filename, encoding='utf-8'):
        line = line.split()
        target_word, page_title, offset = line[:3]
        if target_word not in processed_words:
            jobs[target_word].append(dict(word=target_word, page_title=page_title, offset=offset, fetch_links=True))

    LOGGER.info("Total {} of jobs available. Num of consumer = {}".format(len(jobs), num_process))
    if num_process > 1:
        pool = Pool(num_process)
        pool.map(extract_instances_for_word, jobs.values())
    else:
        # for v in jobs.values():
        for v in [jobs['milk']]:
            extract_instances_for_word(v)

    LOGGER.info("Done.")


if __name__ == '__main__':
    pass
