from utils import configure_logger
import utils
import logging
import sys
from wiki.sc import *

logging.basicConfig(stream=sys.stdout, level=logging.INFO,
                    format='[%(asctime)s] p%(process)s %(name)s:%(lineno)d %(levelname)s - %(message)s')


if __name__ == '__main__':
    configure_logger("INFO")
    logger = utils.get_logger()
    # create_page_id_link_mapping_file("fiber.txt")
    get_categories_for_senses(['fiber.pageid.txt'], '/Users/obaskaya/Desktop/en_20090308/categorylink.csv',
                              '/Users/obaskaya/Desktop/en_20090306/page.csv',
                              '/Users/obaskaya/Desktop/en_20090306/generality.csv')
