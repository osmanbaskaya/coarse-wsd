from preprocess.mt import create_IMS_formatted_dataset_for_MT
import utils


def run():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--input-file', required=True)
    parser.add_argument('--directory-to-write', default='/tmp/mt-data')
    parser.add_argument('--log-level', default='debug')
    args = parser.parse_args()

    utils.configure_logger(args.log_level)
    logger = utils.get_logger()
    logger.debug("Args: {}".format(args))

    create_IMS_formatted_dataset_for_MT(file=args.input_file, directory_to_write=args.directory_to_write)
    logger.info('done')


if __name__ == '__main__':
    run()
