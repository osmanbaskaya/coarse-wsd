import sys
from baseline import BaselineEvaluator
from utils import find_files

dataset_path = sys.argv[1]
key_files = list(find_files(dataset_path, "*.test.key"))
print len(key_files)
evaluator = BaselineEvaluator(key_files)
print "MFS\t{:.3}".format(evaluator.mfs_baseline())
print "RandomShuffle\t{:.3}".format(evaluator.random_shuffled_baseline())
print "Random\t{:.3}".format(evaluator.random_baseline())
