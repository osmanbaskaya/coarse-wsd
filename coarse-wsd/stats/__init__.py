import os
from collections import Counter, defaultdict as dd
import codecs
from utils import get_target_words


def get_sense_counts(wiki_dir):
    words = get_target_words(wiki_dir)
    word_sense_dict = dd(list)
    for word in words:
        fn = os.path.join(wiki_dir, "%s.clean.txt" % word)
        for line in codecs.open(fn, encoding='utf8'):
            line = line.strip().split('\t')
            try:
                sense = line[2]
                word_sense_dict[word].append(sense)
            except IndexError:
                print "IndexError for %s - %s" % (word, line)

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
