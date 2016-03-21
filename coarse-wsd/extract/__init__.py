import wikipedia
from bs4 import BeautifulSoup
import requests
import sys

BASE_URL = "https://en.wikipedia.org"
WHAT_LINKS_HERE_URL = "https://en.wikipedia.org/w/index.php?title=Special:WhatLinksHere/{}&limit={}"


def extract_instances(content, word):
    pass


def fetch_page(title, fetch_links=False):
    p = wikipedia.page(title)
    content = p.content
    if fetch_links:
        links = fetch_what_links_here(p.title)
        print links[:10]
        # here we need to call the function again for neighbors without fetching the links:
        # fetch_page(link, fetch_links=False)

    print content[:50]


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


word = "Apple_Inc."  # will get this from BabelNet.
fetch_page(word, fetch_links=True)