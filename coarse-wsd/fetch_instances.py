from utils import configure_logger
import os
from extract import extract_from_file


def run():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--filename', required=False, default='wikipages.txt')
    parser.add_argument('--num-process', help="Number of process for parallel processing", required=False, default=1,
                        type=int)
    parser.add_argument('--log-level', required=False, default="info")
    args = parser.parse_args()

    logger = configure_logger(args.log_level)

    logger.info("Input file: {}".format(args))

    directory = '../datasets/wiki/'
    try:
        os.mkdir(directory)
    except OSError:
        logger.debug("{} is already exist".format(directory))

    extract_from_file(args.filename, args.num_process)




if __name__ == '__main__':
    run()

