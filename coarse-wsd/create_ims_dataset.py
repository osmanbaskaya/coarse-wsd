from preprocess import create_IMS_formatted_dataset
import utils
import os


def run():
    utils.configure_logger('debug')
    logger = utils.get_logger()
    input_directory = '../datasets/wiki-filtered'
    out_directory = '../datasets/ims-10'
    files = os.listdir(input_directory)
    files = [os.path.join(input_directory, f) for f in files]
    logger.info('total number of files: %d' % len(files))
    create_IMS_formatted_dataset(files, out_directory)
    logger.info('done')


if __name__ == '__main__':
    run()
