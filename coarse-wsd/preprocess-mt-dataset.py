from preprocess.mt import create_IMS_formatted_dataset_for_MT
import utils
import os
import sys


def run():
    utils.configure_logger('debug')
    logger = utils.get_logger()
    # input_directory = sys.argv[1]  # '../datasets/wiki-filtered'
    # out_directory = sys.argv[2]  # '../datasets/wiki-senses'
    # files = os.listdir(input_directory)
    # files = [os.path.join(input_directory, f) for f in files]
    # logger.info('total number of files: %d' % len(files))
    create_IMS_formatted_dataset_for_MT()
    logger.info('done')


if __name__ == '__main__':
    run()
