from ims import IMS
import sys


def run(tw_file, data_path, num_process):
    print >> sys.stderr, tw_file, data_path, num_process
    target_words = open(tw_file).read().splitlines()
    ims = IMS(target_words, data_path, num_process=int(num_process))
    print ims.evaluate(remove_intermediate=False)


if __name__ == '__main__':
    run(sys.argv[1], sys.argv[2], sys.argv[3])




