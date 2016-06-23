import os
import shutil
from multiprocessing import Pool
from utils import cd
import re
from subprocess import check_output


def f1score(p, r):
    return (2 * p * r) / (p + r)


def run_parallel(command):
    print command
    return check_output(command.split())


class IMS(object):

    def __init__(self, target_words, input_path, num_process=2, ims_lib_path='../ims/ims_0.9.2.1'):
        self.target_words = target_words
        self.input_path = input_path
        self.is_trained = False
        self.is_tested = False
        self.ims_lib_path = ims_lib_path  # ims_lib_path
        self.train_sh = './train_one.bash'
        self.test_sh = './test_one.bash'
        self.score_sh = './scorer.bash'
        self.num_process = num_process

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

    def run(self, commands):
        if self.num_process > 1:
            pool = Pool(self.num_process)
            return pool.map(run_parallel, commands)
        else:
            return map(run_parallel, commands)

    def train(self, override=False):
        print "Training started"
        with cd(self.ims_lib_path):
            commands = []
            for fold in xrange(1, self.num_fold+1):
                fold = "fold-%d" % fold
                for target_word in self.target_words:
                    root_path = os.path.join('../../datasets/ims', fold)
                    train_xml = os.path.join(root_path, "%s.train.xml" % target_word)
                    key_file = os.path.join(root_path, "%s.train.key" % target_word)
                    out = os.path.join(self.output_path, fold, target_word)
                    try:
                        os.mkdir(out)  # create target directory for saving models and stats data.
                    except OSError:
                        pass
                    if not override:
                        if os.path.exists(os.path.join(out, "%s.model.gz" % target_word)):
                            continue  # model is already there. Skip it.
                    command = "{} {} {} {}".format(self.train_sh, train_xml, key_file, out)
                    commands.append(command)
            self.run(commands)
        print "Training finished"

    def test(self, override=False):
        print "Test started"
        with cd(self.ims_lib_path):
            commands = []
            for fold in xrange(1, self.num_fold+1):
                fold = "fold-%d" % fold
                for target_word in self.target_words:
                    root_path = os.path.join('../../datasets/ims', fold)
                    test_xml = os.path.join(root_path, "%s.test.xml" % target_word)
                    out = os.path.join(self.output_path, fold, target_word)
                    if not override:
                        if os.path.exists(os.path.join(out, "%s.result" % target_word)):
                            continue  # model is already there. Skip it.
                    command = "{} {} {} {}".format(self.test_sh, out, test_xml, out)
                    commands.append(command)
            self.run(commands)
        print "Test finished"

    def _score(self):
        with cd(self.ims_lib_path):
            commands = []
            for fold in xrange(1, self.num_fold+1):
                fold = "fold-%d" % fold
                for target_word in self.target_words:
                    root_path = os.path.join('../../datasets/ims', fold)
                    system_key = os.path.join(self.output_path, fold, target_word, target_word + ".result")
                    key_file = os.path.join(root_path, "%s.test.key" % target_word)
                    command = "{} {} {}".format(self.score_sh, system_key, key_file)
                    commands.append(command)
            scores = self.run(commands)

        scores = ''.join(scores)
        recalls = map(float, re.findall('recall: (\d\.\d+)', scores))
        precisions = map(float, re.findall('precision: (\d\.\d+)', scores))
        instance_count = map(int, re.findall('(\d+)\.\d+ in total\)', scores))

        return recalls, precisions, instance_count

    def score(self):
        recalls, precisions, instance_count = self._score()
        total_instance_count = 0
        micro_score = 0
        macro_score = 0
        for r, p, c in zip(recalls, precisions, instance_count):
            f1 = f1score(p, r)
            micro_score += f1 * c
            macro_score += f1
            total_instance_count += c

        f1_macro = macro_score / float(len(recalls))
        f1_micro = micro_score / total_instance_count

        return f1_macro, f1_micro

    def evaluate(self, remove_intermediate):
        self.train()
        self.test()
        scores = self.score()
        if remove_intermediate:
            shutil.rmtree(self.output_path)
        return scores

