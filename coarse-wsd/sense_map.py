from preprocess import sense_mapping
import utils
import os


def run():
    utils.configure_logger('debug')
    logger = utils.get_logger()
    input_directory = '../datasets/wiki'
    out_directory = '../datasets/wikisenses'
    files = filter(lambda f: '.replaced-all.txt' in f, os.listdir(input_directory))
    files = [os.path.join(input_directory, f) for f in files]
    logger.info('total number of files: %d' % len(files))
    sense_mapping(files, out_directory)


if __name__ == '__main__':
    run()
