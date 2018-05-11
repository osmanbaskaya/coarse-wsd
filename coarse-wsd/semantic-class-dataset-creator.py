import glob
import logging
import os
import sys

import utils
from utils import configure_logger
from wiki.sc import create_page_id_link_mapping_file, get_categories_for_senses

logging.basicConfig(stream=sys.stdout, level=logging.INFO,
                    format='[%(asctime)s] p%(process)s %(name)s:%(lineno)d %(levelname)s - %(message)s')


def run():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--uwsd-dataset', required=False,
                        default='../datasets/wiki')
    parser.add_argument('--category-file', required=False,
                        default='../datasets/wikipedia-miner/en_20090306/categorylink.csv')
    parser.add_argument('--generality-file', required=False,
                        default='../datasets/wikipedia-miner/en_20090306/generality.csv')
    parser.add_argument('--pageid-title-file', required=False,
                        default='../datasets/wikipedia-miner/en_20090306/page.csv')
    parser.add_argument('--num-process', help="Number of process for parallel processing", required=False, default=1,
                        type=int)
    parser.add_argument('--log-level', required=False, default="info")
    args = parser.parse_args()

    configure_logger(args.log_level)
    logger = utils.get_logger()

    logger.info("Running.")

    files = sorted(glob.glob(os.path.abspath(args.uwsd_dataset) + "/*.tw.txt"))
    create_page_id_link_mapping_file(files, args.uwsd_dataset)
    # files = sorted(glob.glob(os.path.abspath(args.uwsd_dataset) + "/*.pageid.txt"))
    # get_categories_for_senses(files, args.category_file, args.pageid_title_file, args.generality_file)

    logger.info("Done")


if __name__ == '__main__':
    run()
