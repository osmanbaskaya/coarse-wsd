import os
from collections import Counter, defaultdict as dd
import codecs


def get_sense_counts(wiki_dir='../data/wiki'):
    words = set(fn.split('.', 1)[0] for fn in os.listdir(wiki_dir))
    word_sense_dict = dd(list)
    for word in words:
        fn = os.path.join(wiki_dir, "%s.txt" % word)
        for line in codecs.open(fn, encoding='utf8'):
            line = line.strip().split('\t')
            sense = line[2]
            word_sense_dict[word].append(sense)

    word_sense_count = dict()

    for w, s in word_sense_dict.iteritems():
        word_sense_count[w] = Counter(s)

    return word_sense_count


def get_sense_pagelinks(fn='../semcor-pages'):
    sense_page_map = {}
    for line in codecs.open(fn, encoding='utf8'):
        line = line.strip().split('\t')
        page, sense = line[1:3]
        sense_page_map[sense] = page

    return sense_page_map


