from ims import predict
import utils
from multiprocessing import cpu_count


def run():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--input-dir', required=True)
    parser.add_argument('--directory-to-write', required=True)
    parser.add_argument('--model-dir', required=True)
    parser.add_argument('--log-level', default='debug')
    parser.add_argument('--fresh-start', action="store_true")
    parser.add_argument('--num-of-process', default=cpu_count()-1, type=int)
    args = parser.parse_args()

    input_dir = args.input_dir
    output_dir = args.directory_to_write
    model_dir = args.model_dir

    utils.configure_logger(args.log_level)
    logger = utils.get_logger()
    logger.debug("Args: {}".format(args))

    predict(model_dir, input_dir, output_dir, num_of_process=args.num_of_process, fresh_start=args.fresh_start)
    logger.info('Done')


if __name__ == '__main__':
    run()
