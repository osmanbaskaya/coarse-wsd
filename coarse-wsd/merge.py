from ims import IMSOutputMerger
import utils


def run():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--input-file', required=True)
    parser.add_argument('--wsd-output-dir', required=True)
    parser.add_argument('--directory-to-write', required=True)
    parser.add_argument('--log-level', default='debug')
    args = parser.parse_args()

    utils.configure_logger(args.log_level)
    logger = utils.get_logger()
    logger.debug("Args: {}".format(args))

    merger = IMSOutputMerger()
    merger.merge(args.input_file, args.wsd_output_dir, args.directory_to_write)
    logger.info('Merge Done.')


if __name__ == '__main__':
    run()
