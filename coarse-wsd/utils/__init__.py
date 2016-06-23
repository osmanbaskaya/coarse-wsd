#! /usr/bin/python
# -*- coding: utf-8 -*-

from collections import defaultdict as dd
from contextlib import contextmanager
import logging
import logging.handlers
import sys
from unidecode import unidecode
import math
import fnmatch
import os

__author__ = "Osman Baskaya"

LOGGER = None


# *-*-*- Context Managers -*-*-*
@contextmanager
def cd(path):
    old_dir = os.getcwd()
    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(old_dir)


# *-*-*- Utility Functions -*-*-*

def get_target_words(directory='../datasets/wiki'):
    return set(fn.split('.', 1)[0] for fn in os.listdir(directory))


def get_logger():
    assert LOGGER is not None, "Configure Logger first"
    return LOGGER


def configure_logger(log_level='INFO'):
    global LOGGER
    if LOGGER is None:
        logging.getLogger('requests').setLevel(logging.WARNING)

        root_logger = logging.getLogger('')
        root_logger.setLevel(logging.DEBUG)

        file_handler = logging.FileHandler("coarse-wsd.log", encoding='utf-8', mode='a+')
        console_handler = logging.StreamHandler(stream=sys.stdout)
        console_handler.setLevel(logging.getLevelName(log_level.upper()))
        file_handler.setLevel(logging.DEBUG)

        detailed_formatter = logging.Formatter(u'[%(asctime)s] p%(process)s %(pathname)s:%(lineno)d %(levelname)s - %(message)s')
        formatter = logging.Formatter(u'[%(asctime)s] p%(process)s %(filename)s:%(lineno)d %(levelname)s - %(message)s')

        file_handler.setFormatter(detailed_formatter)
        console_handler.setFormatter(formatter)

        root_logger.addHandler(file_handler)
        root_logger.addHandler(console_handler)

        LOGGER = root_logger


def top_words(files):
    d = dd(float)
    for fn in files:
        with open(fn) as f:
            print >> sys.stderr, fn
            for line in f:
                word, _, freq = line.strip().split('\t')
                d[word] += float(freq)

    freq_sorted = sorted(d.iteritems(), key=lambda t: t[1], reverse=True)

    for word, freq in freq_sorted:
        print "{}\t{}".format(word, freq)


def find_files(topdir, pattern):
    for path, dirname, filelist in os.walk(topdir):
        for name in filelist:
            if fnmatch.fnmatch(name, pattern):
                yield os.path.join(path,name)


def calc_perplexity(d):
    """
    >>> d = {u'bn:00289737n': 10, u'wn:07739125n': 10}
    >>> calc_entropy(d)
    2.0
    """
    total = float(sum(d.values()))
    e = 0
    for count in d.values():
        p = count / total
        e -= p * math.log(p, 2)

    return 2 ** e


def remove_non_ascii(text):
    return unidecode(text)


def get_all_files(path, regex=None):
    matches = []
    for root, dirnames, filenames in os.walk(path):
        if regex is None:
            matches.extend(map(lambda fn: os.path.join(root, fn), filenames))
        else:
            for filename in fnmatch.filter(filenames, regex):
                matches.append(os.path.join(root, filename))

    return matches


def get_all_target_words(dataset_path, regex=None):
    files = get_all_files(dataset_path, regex)
    files = map(lambda path: os.path.split(path)[-1], files)
    target_words = set(map(lambda t: t.split('.')[0], files))
    return target_words


def get_sense_wiki_link_dict(path='../datasets/wiki-filtered'):
    pass


def run():
    method = globals()[sys.argv[1]] 
    args = sys.argv[2:]
    method(args)

if __name__ == "__main__":
    run()


#python __init__.py top_words ../../datasets/2013-test.filtered.gz.txt ../../datasets/2014-train-test.filtered.gz.txt ../../datasets/2015-raw-sts.filtered.gz.txt ../../datasets/snli-top2000-lemmatized.txt > freq_sorted.txt
