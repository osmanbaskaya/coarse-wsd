from ims import IMS
import sys


def run(tw_file, data_path, ims_path, num_process):
    print >> sys.stderr, tw_file, data_path, num_process
    target_words = open(tw_file).read().splitlines()
    ims = IMS(target_words, data_path, num_process=int(num_process),
            ims_lib_path=ims_path)
    f1macro, f1micro = ims.evaluate(remove_intermediate=False)
    print "F1-Macro\t{:.3}\nF1-Micro\t{:.3}".format(f1macro, f1micro)


if __name__ == '__main__':
    run(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])




