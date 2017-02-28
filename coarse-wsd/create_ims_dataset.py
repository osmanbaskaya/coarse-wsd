from preprocess import create_IMS_formatted_dataset
import utils
import os
import sys


def run():
    utils.configure_logger('debug')
    logger = utils.get_logger()
    input_directory = sys.argv[1]
    out_directory = sys.argv[2]
    num_of_fold = int(sys.argv[3])
    num_of_processor = int(sys.argv[4])
    files = os.listdir(input_directory)
    files = [os.path.join(input_directory, f) for f in files]
    logger.info('total number of files: %d' % len(files))
    create_IMS_formatted_dataset(files, out_directory, k=num_of_fold, num_of_process=num_of_processor)
    logger.info('done')


if __name__ == '__main__':
    run()
