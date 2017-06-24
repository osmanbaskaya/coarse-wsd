from utils import configure_logger
import utils
import logging
import sys
from wiki.sc import create_page_id_link_mapping_file, get_categories_for_senses
import glob

logging.basicConfig(stream=sys.stdout, level=logging.INFO,
                    format='[%(asctime)s] p%(process)s %(name)s:%(lineno)d %(levelname)s - %(message)s')


if __name__ == '__main__':
    configure_logger("INFO")
    logger = utils.get_logger()
    import os
    files = glob.glob(os.path.abspath('../datasets/wiki') + "/*.tw.txt")
    create_page_id_link_mapping_file(files, '../datasets/wiki/')

    # get_categories_for_senses(['fiber.pageid.txt'], '/Users/obaskaya/Desktop/en_20090308/categorylink.csv',
    #                           '/Users/obaskaya/Desktop/en_20090306/page.csv',
    #                           '/Users/obaskaya/Desktop/en_20090306/generality.csv')
