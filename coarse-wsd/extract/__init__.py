# -*- coding: utf-8 -*-

import wikipedia
import codecs
from bs4 import BeautifulSoup
import utils
import requests
import re
from multiprocessing import Pool
import os
import spacy
from wikipedia.exceptions import PageError, DisambiguationError, WikipediaException
from collections import defaultdict as dd
from functools import partial
from requests.exceptions import ConnectionError, ContentDecodingError
from time import sleep
from utils import get_target_words
import urllib


BASE_URL = u"https://en.wiki.org"
# What Links Here url. Redirection pages omitted.
WHAT_LINKS_HERE_URL = u"https://en.wikipedia.org/w/index.php?title=Special:WhatLinksHere/{}&limit={}&hideredirs=1"
MIN_SENTENCE_SIZE = 8
SLEEP_INTERVAL = 1
MAXIMUM_RETRY = 5
LINK_EXCLUDE_TYPES = {"/wiki/Talk:", "/wiki/User_talk:", "/wiki/User:", "/wiki/Wikipedia:", "/wiki/Template:"}

LOGGER = None
NLP = spacy.en.English()


def extract_instances(content, word, pos, sense_offset, target_word_page, categories, url=None):
    instances = []
    regex = re.compile(r"({}\w*)(\W*)".format(word), flags=re.I)
    for line in content.split('\n'):
        line = NLP(line)
        for s in line.sents:
            if word in s.lower_:
                tokens = list(s)
                num_of_tokens = len(tokens)
                if num_of_tokens > MIN_SENTENCE_SIZE:
                    ss = " ".join([t.text for t in tokens])
                    for m, m_lem in zip(regex.finditer(ss), regex.finditer(s.lemma_)):
                        sentence_not_replaced = "{}<target>{}</target>{}{}".format(ss[:m.start()], m.group(1),
                                                                                   m.group(2), ss[m.end():])

                        lemmatized = "{}<target>{}</target>{}{}".format(s.lemma_[:m_lem.start()], m_lem.group(1),
                                                                        m_lem.group(2),
                                                                        s.lemma_[m_lem.end():])

                        sentence = "{}<target>{}</target>{}{}".format(ss[:m.start()], word, m.group(2), ss[m.end():])

                        tokenized = sentence_not_replaced.split()
                        index = -1
                        for i in range(len(tokenized)):
                            if tokenized[i].startswith("<target>"):
                                index = i  # index of the target word.

                        instances.append(u"{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}"
                                         .format(ss, sense_offset, index, sentence_not_replaced, sentence, lemmatized,
                                                 pos, m.group(1), word, target_word_page, url, u'|||'.join(categories)))
    return instances


def wiki_page_query(page_title, num_try=1):

    p = get_wiki_page(page_title, num_try)
    if p is not None:
        try:
            categories = p.categories
        except KeyError:  # Somehow sometimes wiki library can't fetch any category.
            categories = []
        return p.title, p.content, p.url, categories


def get_wiki_page(page_title, num_try=1):
    global LOGGER

    LOGGER = utils.get_logger()

    if num_try > MAXIMUM_RETRY:
        return None

    global SLEEP_INTERVAL

    try:
        LOGGER.debug(u'Retrieving {} from Wikipedia'.format(page_title))
        p = wikipedia.page(page_title, auto_suggest=False)
        SLEEP_INTERVAL = 1
        return p
    except KeyError as e:
        if '%' in page_title:
            title = urllib.parse.unquote(page_title)
            return get_wiki_page(title)
        else:
            LOGGER.debug(u"PageError: {}".format(page_title, e))
    except PageError as e:
        # wiki library has a possible bug for underscored page titles.
        if '%' in page_title:
            title = urllib.parse.unquote(page_title)
            return get_wiki_page(title)
        else:
            LOGGER.debug(u"PageError: {}".format(page_title, e))

    # This is most likely the "What links here" page and we can safely skip it.
    except DisambiguationError as e:
        match = re.search("\((.*)\)", page_title)
        if match:
            query = match.group(1)
            for option in e.options:
                if query in option:
                    LOGGER.info("{} is disambiguated: {}. Options: {}".format(page_title, option, e.options))
                    return get_wiki_page(option, num_try=num_try+1)
    except ConnectionError as e:
        SLEEP_INTERVAL *= 4
        LOGGER.info(u"ConnectionError: Sleeping {} seconds for {}.".format(SLEEP_INTERVAL, page_title))
        sleep(SLEEP_INTERVAL)
        get_wiki_page(page_title, num_try + 1)  # try again.
    except WikipediaException:
        get_wiki_page(page_title, num_try + 1)  # try again.
    except ContentDecodingError as e:
        LOGGER.info(u"ContentDecodingError: Trying ({})".format(num_try+1))
        get_wiki_page(page_title, num_try+1)
    except ValueError as e:
        LOGGER.info(u"ValueError... Sleep and Trying ({})".format(num_try+1))
        sleep(4)
        get_wiki_page(page_title, num_try+1)


def extract_from_page(page_title, word, offset, fetch_links):
    pos = offset[-1]

    response = wiki_page_query(page_title)
    if response is not None:
        title, content, url, categories = response
    else:
        LOGGER.warning(u'No page found for {}'.format(page_title))
        return []

    instances = extract_instances(content, word, pos, offset, True, categories, url)
    if fetch_links:
        links = fetch_what_links_here(title, limit=1000)
        for link in links:
            link_page_title = link.replace(u'/wiki/', '')
            link_page_response = wiki_page_query(link_page_title)
            if link_page_response is not None:
                title, content, url, categories = link_page_response
                link_instances = extract_instances(content, word, pos, offset, False, categories, url)
                instances.extend(link_instances)

    return instances


def write2file(filename, lines):
    with codecs.open(filename, 'w', encoding='utf8') as f:
        LOGGER.info("Writing {}".format(filename))
        f.write(u'\n'.join(lines))
        f.write('\n')


def extract_instances_for_word(senses, wiki_dir):
    LOGGER.info(u"Processing word: %s" % senses[0]['word'])
    instances = []
    for sense_args in senses:
        sense_instances = extract_from_page(**sense_args)
        instances.extend(sense_instances)

    write2file(os.path.join(wiki_dir, u'%s.txt' % senses[0]['word']), instances)


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
                links = filter(lambda link: '(disambiguation)' not in link, links)
                links = list(filter(lambda link: not any(map(lambda e: link.startswith(e), LINK_EXCLUDE_TYPES)), links))
                special_pages = [link for link in links if ':' in link]
                if len(special_pages) > 0:
                    LOGGER.info("Links that contain ':' -> {}".format(special_pages))
                total_link_processed += len(links)
                all_links.extend(links)
            else:
                LOGGER.error(u"Error while link fetching: %s and %s" % (next_page_url, response.status_code))
                break
        except ValueError:
            LOGGER.warning("ValueError occured 1 for {}".format(title))
            exit(-1)

    return all_links


def extract_from_file(filename, num_process, dataset_path, fetch_links=True):
    import utils

    global LOGGER
    LOGGER = utils.get_logger()

    # get processed words
    processed_words = get_target_words(dataset_path)

    jobs = dd(list)
    for line in codecs.open(filename, encoding='utf-8'):
        line = line.split()
        target_word, page_title, offset = line[:3]
        if target_word not in processed_words:
            jobs[target_word].append(dict(word=target_word, page_title=page_title, offset=offset,
                                          fetch_links=fetch_links))

    LOGGER.info("Total {} of jobs available. Num of consumer = {}".format(len(jobs), num_process))
    if num_process > 1:
        pool = Pool(num_process)
        func = partial(extract_instances_for_word, wiki_dir=dataset_path)
        pool.map(func, jobs.values())
    else:
        for v in jobs.values():
        # for v in [jobs['milk']]:
            extract_instances_for_word(v, dataset_path)

    LOGGER.info("Done.")


if __name__ == '__main__':
    pass
