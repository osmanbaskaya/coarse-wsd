#! /usr/bin/python
# -*- coding: utf-8 -*-

from collections import defaultdict as dd
import logging
import sys

__author__ = "Osman Baskaya"


def configure_logger():
    logging.getLogger('requests').setLevel(logging.WARNING)
    logging.basicConfig(stream=sys.stdout, level=logging.INFO,
                        format='[%(asctime)s] p%(process)s %(name)s:%(lineno)d %(levelname)s - %(message)s')


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
