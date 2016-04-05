from extract import extract_instances_for_word
import logging
from utils import configure_logger
import os
from multiprocessing import Pool
from collections import defaultdict as dd


def run():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--filename', required=False, default='wikipages.txt')
    parser.add_argument('--num-process', help="Number of process for parallel processing", required=False, default=1,
                        type=int)
    args = parser.parse_args()

    LOGGER.info("Input file: {}".format(args.filename))

    directory = '../datasets/wiki'
    try:
        os.mkdir(directory)
    except OSError:
        LOGGER.info("{} is already exist".format(directory))

    pool = Pool(args.num_process)
    jobs = dd(list)
    for line in open(args.filename):
        line = line.split()
        target_word, page_title, offset = line[:3]
        jobs[target_word].append(dict(word=target_word, page_title=page_title, offset=offset, fetch_links=True))

    LOGGER.info("Total {} of jobs available. Consuming has been started.".format(len(jobs)))
    list(pool.imap_unordered(extract_instances_for_word, jobs.values()))
    LOGGER.info("Done.")

if __name__ == '__main__':
    configure_logger()
    LOGGER = logging.getLogger(__name__)
    run()

