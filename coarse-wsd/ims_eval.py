from ims import IMS
import sys


def run(tw_file, data_path):
    target_words = open(tw_file).read().splitlines()
    ims = IMS(target_words, data_path)
    print ims.evaluate(remove_intermediate=False)


if __name__ == '__main__':
    run(sys.argv[1], sys.argv[2])




