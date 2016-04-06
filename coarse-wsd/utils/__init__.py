#! /usr/bin/python
# -*- coding: utf-8 -*-

from collections import defaultdict as dd
import logging
import logging.handlers
import sys

__author__ = "Osman Baskaya"

LOGGER = None


def configure_logger(log_level='INFO'):
    global LOGGER
    if LOGGER is None:
        logging.getLogger('requests').setLevel(logging.WARNING)

        root_logger = logging.getLogger('')
        root_logger.setLevel(logging.DEBUG)

        file_handler = logging.FileHandler("coarse-wsd.log", encoding='utf8', mode='w')
        console_handler = logging.StreamHandler(stream=sys.stdout)
        console_handler.setLevel(logging.getLevelName(log_level.upper()))
        file_handler.setLevel(logging.DEBUG)

        detailed_formatter = logging.Formatter('[%(asctime)s] p%(process)s %(pathname)s:%(lineno)d %(levelname)s - %(message)s')
        formatter = logging.Formatter('[%(asctime)s] p%(process)s %(filename)s:%(lineno)d %(levelname)s - %(message)s')

        file_handler.setFormatter(detailed_formatter)
        console_handler.setFormatter(formatter)

        root_logger.addHandler(file_handler)
        root_logger.addHandler(console_handler)

        LOGGER = root_logger
    return LOGGER


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

def run():
    method = globals()[sys.argv[1]] 
    files = sys.argv[2:]
    method(files)

if __name__ == "__main__":
    run()


#python __init__.py top_words ../../datasets/2013-test.filtered.gz.txt ../../datasets/2014-train-test.filtered.gz.txt ../../datasets/2015-raw-sts.filtered.gz.txt ../../datasets/snli-top2000-lemmatized.txt > freq_sorted.txt
