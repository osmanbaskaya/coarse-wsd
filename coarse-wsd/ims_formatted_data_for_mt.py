from preprocess.mt import create_IMS_formatted_dataset
import utils
import os


def run():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--input-dir', required=True)
    parser.add_argument('--directory-to-write', default='/tmp/ims-mt-data')
    parser.add_argument('--num-of-process', default=1, type=int)
    parser.add_argument('--log-level', default='debug')
    args = parser.parse_args()

    input_directory = args.input_dir
    out_directory = args.directory_to_write

    utils.configure_logger(args.log_level)
    logger = utils.get_logger()
    logger.debug("Args: {}".format(args))

    files = os.listdir(input_directory)
    files = [os.path.join(input_directory, f) for f in files]
    logger.info('total number of files: %d' % len(files))
    create_IMS_formatted_dataset(files, out_directory, args.num_of_process)
    logger.info('Done')


if __name__ == '__main__':
    run()
