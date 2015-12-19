#! /usr/bin/python
# -*- coding: utf-8 -*-
__author__ = "Osman Baskaya"
from collections import defaultdict as dd
import os
import sys


def top_words(files, path='.', output_fn):
    d = dd(float)
    for fn in files:
        fn = os.path.join(path, fn)
        with open(fn) as f:
            for line in f:
                word, _, freq = line.strip().split('\t')
                d[word] += freq

    with open(output_fn, 'w') as f:
        for word, freq in d.iteritems():
            f.write("%s\t%f\n".format(word, freq))

def run():
    method = globals()[sys.argv[1]] 
    args = sys.argv[2:-2]
    path = sys.argv[-2]
    method(args)


if __name__ == "__main__":
    run()
