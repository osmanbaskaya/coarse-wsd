import os
import shutil
from multiprocessing import Pool
from utils import cd


class IMS(object):

    def __init__(self, target_words, input_path, ims_lib_path='../ims/ims_0.9.2.1'):
        self.target_words = target_words
        self.input_path = input_path
        self.is_trained = False
        self.is_tested = False
        self.ims_lib_path = ims_lib_path  # ims_lib_path
        self.train_sh = './train_one.bash'
        self.test_sh = './test_one.bash'
        self.score_sh = './scorer.bash'

        output_path, num_fold = IMS.prepare(input_path)

        self.num_fold = num_fold
        self.output_path = output_path

    @staticmethod
    def prepare(data_path):
        head_path, data_dir = os.path.split(data_path)
        directory_to_write = '/tmp/{}-run'.format(data_dir)
        num_fold = len(os.listdir(data_path))

        # create folding files to write models etc.
        try:
            os.mkdir(directory_to_write)
            map(lambda fold: os.mkdir(os.path.join(directory_to_write, "fold-%d" % fold)), xrange(1, num_fold+1))
        except OSError:
            pass

        return directory_to_write, num_fold

    def train(self):
        with cd(self.ims_lib_path):
            for fold in xrange(1, self.num_fold+1):
                fold = "fold-%d" % fold
                for target_word in self.target_words:
                    root_path = os.path.join('../../datasets/ims', fold)
                    train_xml = os.path.join(root_path, "%s.train.xml" % target_word)
                    key_file = os.path.join(root_path, "%s.train.key" % target_word)
                    out = os.path.join(self.output_path, fold)
                    command = "{} {} {} {}".format(self.train_sh, train_xml, key_file, out)
                    os.system(command)
                    break
                break

    def test(self):
        pass

    def score_micro(self):
        pass

    def score_macro(self):
        pass

    def score(self):
        return 0

    def evaluate(self, remove_intermediate):
        self.train()
        self.test()
        self.score()
        if remove_intermediate:
            shutil.rmtree(self.output_path)

