import unittest
from baseline import BaselineEvaluator
from random import randint, seed


class TestBaselineEvaluator(unittest.TestCase):

    def setUp(self):
        key_files = ['/tmp/agent.key', '/tmp/artificial.key']
        self.create_key_files(key_files)
        self.evaluator = BaselineEvaluator(key_files)

    def create_key_files(self, key_files):
        seed(42)
        target_words = ['agent', 'artificial']
        key_file_line_format = 'BNC {target_word}.{instance_id} {sense}\n'
        for i, fn in enumerate(key_files):
            target_word = target_words[i]
            senses = ["%s.sense1" % target_word, "%s.sense2" % target_word]
            num_sense = len(senses)
            with open(fn, 'w') as f:
                for j in xrange(10):
                    line = key_file_line_format.format(target_word=target_word, instance_id=j,
                                                       sense=senses[randint(0, num_sense-1)])
                    f.write(line)

    def test_mfs_baseline(self):
        score = self.evaluator.mfs_baseline()
        self.assertEquals(score, 0.55)

    def test_random_shuffled_baseline(self):
        score = self.evaluator.random_shuffled_baseline()
        self.assertEquals(score, 0.5)

    def test_random_baseline(self):
        score = self.evaluator.random_baseline()
        self.assertEquals(score, 0.45)
