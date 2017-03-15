from preprocess.mt import preprocess_mt_input_file
import utils


def run():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--input-file', required=True)
    parser.add_argument('--model-dir', required=True)
    parser.add_argument('--write-every-n-line', default=200000, type=int)
    parser.add_argument('--directory-to-write', default='/tmp/mt-data')
    parser.add_argument('--log-level', default='debug')
    args = parser.parse_args()

    utils.configure_logger(args.log_level)
    logger = utils.get_logger()
    logger.debug("Args: {}".format(args))

    preprocess_mt_input_file(args.input_file, args.model_dir, args.directory_to_write, args.write_every_n_line)
    logger.info('Done')


if __name__ == '__main__':
    run()
