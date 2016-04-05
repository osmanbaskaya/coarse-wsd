import wikipedia
from bs4 import BeautifulSoup
import requests
import sys
from wikipedia.exceptions import PageError
import logging

BASE_URL = "https://en.wikipedia.org"
WHAT_LINKS_HERE_URL = "https://en.wikipedia.org/w/index.php?title=Special:WhatLinksHere/{}&limit={}"
MIN_SENTENCE_SIZE = 8

LOGGER = logging.getLogger(__name__)


def extract_instances(content, word):
    instances = []
    instances_replaced = []
    for line in content.split('\n'):
        tokens = line.split()
        num_of_tokens = len(tokens)
        if num_of_tokens >= MIN_SENTENCE_SIZE:
            for i in xrange(num_of_tokens):
                if word in tokens[i].lower():
                    instances.append(u"{} <target_word>{}</target+word> {}".format(u' '.join(tokens[:i]),
                                                                                  tokens[i],
                                                                                  u' '.join(tokens[i+1:])))

                    instances_replaced.append(u"{} <target_word>{}</target+word> {}".format(u' '.join(tokens[:i]),
                                                                                            word,
                                                                                            u' '.join(tokens[i+1:])))

    return instances, instances_replaced


def extract_from_page(page_title, word, offset, fetch_links):

    print page_title
    try:
        p = wikipedia.page(page_title)
    except PageError as e:
        LOGGER.info("Page '{}' not found for target word '{}'.".format(page_title, word, ))
        # wikipedia library has a possible bug for underscored page titles.
        if '_' in page_title:
            title = page_title.replace('_', ' ')
            LOGGER.info("Trying '{}'".format(title))
            return extract_from_page(title, word, offset, fetch_links)
        else:
            return [], []

    instances, instances_replaced = extract_instances(p.content, word)
    if fetch_links:
        links = fetch_what_links_here(p.title)
        for link in links[:5]:
            link_page_title = link[6:]
            link_page = wikipedia.page(link_page_title)
            link_instances, link_instances_replaced = extract_instances(link_page.content, word)
            instances.extend(link_instances), instances_replaced.extend(link_instances_replaced)
    return instances, instances_replaced


def extract_instances_for_word(senses):
    instances = []
    instances_replaced = []
    for sense_args in senses:
        sense_instances, sense_instances_replaced = extract_from_page(**sense_args)
        instances.extend(sense_instances)
        instances_replaced.extend(sense_instances_replaced)

    # TODO: create a file in ..datasets/wiki/ and write instances.


def fetch_what_links_here(title, limit=500):
    url = WHAT_LINKS_HERE_URL.format(title, limit)
    links = []
    print "Processing: ", url
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        rows = soup.find(id='mw-whatlinkshere-list').find_all('li', recursive=False)
        links = [row.find('a')['href'] for row in rows]
    else:
        print >> sys.stderr, "Error while link fetching: ", url

    assert len(links) <= limit, "Fetched links are more than the limit."
    return links


if __name__ == '__main__':
    pass
