from stats import get_sense_counts, get_sense_pagelinks
from utils import calc_perplexity
import tabulate
import codecs


def create_sense_count_table(data_dir, page_fn):
    word_sense_count = get_sense_counts(data_dir)
    sense_page_link = get_sense_pagelinks(page_fn)
    table = []
    header = ['Word', 'Perplexity', 'Sense', 'Sense-URL', 'Percentage', 'Total']
    for word, sense_dist in word_sense_count.iteritems():
        total = float(sum(sense_dist.values()))
        perplexity = calc_perplexity(sense_dist)
        for sense, count in sense_dist.iteritems():
            table.append((word, perplexity, sense, sense_page_link[sense], count / total, total))

    out = 'wiki-data-stats.txt'
    with codecs.open(out, 'w', encoding='utf-8') as f:
        f.write(tabulate.tabulate(table, headers=header))


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--function', required=True)
    parser.add_argument('--args', required=False, nargs='+')
    args = parser.parse_args()

    globals()[args.function](*args.args)


if __name__ == '__main__':
    main()
