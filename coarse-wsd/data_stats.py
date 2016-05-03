from stats import get_sense_counts, get_sense_pagelinks
import tabulate


def create_sense_count_table(data_dir, page_fn):
    word_sense_count = get_sense_counts(data_dir)
    sense_page_link = get_sense_pagelinks(page_fn)


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--function', required=True)
    parser.add_argument('--args', required=False, nargs='+')
    args = parser.parse_args()

    globals()[args.function](*args.args)


if __name__ == '__main__':
    main()
