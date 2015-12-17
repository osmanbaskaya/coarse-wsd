from tempfile import NamedTemporaryFile
import sys
import ujson
import os
import os
from collections import defaultdict as dd
import numpy as np
from itertools import izip
from nltk.corpus.reader import BracketParseCorpusReader
import gzip
import matplotlib
matplotlib.use('Agg')
from nltk.stem import WordNetLemmatizer
from bs4 import BeautifulSoup
import matplotlib.pyplot as plt


def get_stats_from_snli_dataset(files, tagset=("NN", "NNS"), use_lemmas=False):

    lemmatizer = None
    if use_lemmas:
        lemmatizer = WordNetLemmatizer()

    stats = dd(int)
    num_of_token = 0

    for filename in files:
        f = NamedTemporaryFile()
        fields_to_read = {"sentence1_parse", "sentence2_parse"}
        for sent in open(filename):
            sent = ujson.loads(sent)
            for field in fields_to_read:
                f.write("%s\n" % sent[field])

        reader = BracketParseCorpusReader("/tmp", os.path.basename(f.name))
        for word, tag in reader.tagged_words():
            if tagset is None or tag in tagset:
                if use_lemmas:
                    word = lemmatizer.lemmatize(word, pos=tag.lower()[0])
                stats[word] += 1
                num_of_token += 1

    return stats, num_of_token


def get_stats_from_snli_dataset_parsed_by_core_nlp(filename, tagset=("NN", "NNS")):
    stats = dd(int)
    num_of_token = 0
    lemma = None
    for i, line in enumerate(gzip.open(filename)):
        line = line.strip()
        if i % 5000000 == 0:
            print >> sys.stderr, "Processed %d line" % i
        if i % 2 == 0:
            lemma = line[7:-8].lower()
        else:
            tag = line[5:-6]
            if tagset is None or tag in tagset:
                stats[lemma] += 1
                num_of_token += 1

    return stats, num_of_token


def draw_coverage(stats, total, fig_fn):
    coverage = [0]
    total = float(total)

    for word, count in stats:
        coverage.append(coverage[-1] + count)


    coverage = np.asarray(coverage) / total
    plt.figure(figsize=(15, 10))
    plt.plot(range(100, 2010, 100), coverage[100:2010:100], 'o')
    plt.title("Coverage for 2014 dataset")
    plt.xlabel("# of word used (total # of token = %d)" % total)
    plt.ylabel("Coverage (%)")
    plt.xticks(range(100, 2010, 100))
    plt.yticks(np.linspace(0.5, 1, 11))
    plt.grid()
    plt.savefig("../../datasets/%s" % fig_fn)


def write_topn_words(stats, total, fn, n=2000):

    total = float(total)
    f = open(fn, 'wb')
    # LOGGER.info("Writing top %d words into the file %s", n, fn)
    for word, count in stats[:n]:
        f.write("{}\t{}\t{}\n".format(word, count, count / total))
    f.close()


def draw_coverage_for_snli_dataset(filename, after_corenlp=True):
    if after_corenlp:
        filename = filename[0]
    	basename = os.path.basename(filename)
        stats, num_of_token = get_stats_from_snli_dataset_parsed_by_core_nlp(filename)
        fig_fn = "corenlp-lemmatized-%s.png" % basename
    else:
        files = ("../../datasets/snli_1.0/snli_1.0_train.jsonl",)
        stats, num_of_token = get_stats_from_snli_dataset(files, use_lemmas=True)
        fig_fn = "nltk-lemmatized"

    # LOGGER.info("# of unique word = %d \t # of different token: %d", len(stats), num_of_token
    # )
    stats = sorted(stats.items(), key=lambda t: t[1], reverse=True)
    write_topn_words(stats, num_of_token, "../../datasets/%s.txt" % basename, n=2000)
    draw_coverage(stats, num_of_token, fig_fn)


def main():
    # draw_coverage_for_snli_dataset()
    filename = sys.argv[1:]
    draw_coverage_for_snli_dataset(filename, after_corenlp=True)


if __name__ == '__main__':
    main()
