import unittest
from baseline import BaselineEvaluator
from random import randint


class TestBaselineEvaluator(unittest.TestCase):

    def setUp(self):
        key_files = ['/tmp/agent.key', '/tmp/artificial.key']
        self.create_key_files(key_files)
        self.evaluator = BaselineEvaluator(key_files)

    def create_key_files(self, key_files):
        target_words = ['agent', 'artificial']
        key_file_line_format = 'BNC {target_word}.{instance_id} {sense}\n'
        for i, fn in enumerate(key_files):
            target_word = target_words[i]
            senses = ["%s.sense1" % target_word, "%.sense2" % target_word]
            num_sense = len(senses)
            with open(fn, 'w') as f:
                for j in xrange(10):
                    d = dict(target_word=target_word, instance_id=j, sense=senses[randint(num_sense)])
                    f.write(key_file_line_format.format(d))

    def test_mfs_baseline(self):
        print self.evaluator.mfs_baseline()

    def test_random_shuffled_baseline(self):
        pass

    def test_random_baseline(self):
        pass