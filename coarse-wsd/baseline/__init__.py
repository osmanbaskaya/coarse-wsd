from __future__ import division
from collections import Counter, defaultdict as dd
import numpy as np
from random import shuffle, randint
import copy


class BaselineEvaluator(object):

    def __init__(self, key_files):
        """Key files should be a list which contains keyfile path of each target word."""
        self.key_files = key_files
        self.instance_sense_map = dd(dict)
        self._prepare()

    def _prepare(self):
        for key_file in self.key_files:
            for line in open(key_file):
                _, instance, key = line.split()
                target_word = instance.rsplit('.', 1)[0]
                self.instance_sense_map[target_word][instance] = key

    def mfs_baseline(self):
        true_pos = 0
        total = 0
        for target_word, instance_dict in self.instance_sense_map.iteritems():
            values = np.array(Counter(instance_dict.values()).values())
            total += values.sum()
            true_pos += values.max()

        return true_pos / total

    def random_shuffled_baseline(self):
        true_pos = 0
        total = 0
        for target_word, instance_dict in self.instance_sense_map.iteritems():
            values = copy.deepcopy(instance_dict.values())
            shuffled = copy.deepcopy(values)
            shuffle(shuffled)
            matches = [i == j for i, j in zip(values, shuffled)]
            true_pos += sum(matches)
            total += len(matches)

        return true_pos / total

    def random_baseline(self):
        true_pos = 0
        total = 0
        for target_word, instance_dict in self.instance_sense_map.iteritems():
            senses = Counter(instance_dict.values()).keys()
            num_sense = len(senses)
            matches = [senses[randint(num_sense)] == i for i in instance_dict.values()]
            true_pos += sum(matches)
            total += len(matches)

        return true_pos / total



