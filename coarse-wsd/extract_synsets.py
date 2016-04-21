import logging
import sys
from extract.wordnet import WordNetExtractor

logging.basicConfig(stream=sys.stdout, level=logging.INFO,
                    format='[%(asctime)s] p%(process)s %(name)s:%(lineno)d %(levelname)s - %(message)s')

input_file = sys.argv[1]

WordNetExtractor().fetch_offset_numbers(input_file)

