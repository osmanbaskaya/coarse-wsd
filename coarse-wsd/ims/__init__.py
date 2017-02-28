import os
from preprocess.mt import get_single_and_plural_form
import gzip
import glob
import utils
import codecs
import shutil
from multiprocessing import Pool
from utils import cd, create_fresh_dir
import re
from bs4 import BeautifulSoup
from subprocess import check_output
from collections import OrderedDict


LOGGER = None


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


class IMSPredictor(object):

    def __init__(self, model_dir, ims_lib_path='../ims/ims_0.9.2.1'):
        self.ims_lib_path = ims_lib_path
        self.model_dir = model_dir
        self.test_sh = './test_one.bash'
        self.target_words = set(fn.split('.', 1)[0] for fn in os.listdir(model_dir))

    def predict(self, target_word, test_xml):
        # LOGGER.info("{} - {}".format(target_word, "\n".join(self.target_words)))
        if target_word in self.target_words:
            curr_dir = os.getcwd()
            target_model_dir = os.path.join(curr_dir, self.model_dir, target_word)
            test_xml = os.path.join(curr_dir, test_xml)
            with cd(self.ims_lib_path):
                out = "/tmp"
                command = "{} {} {} {}".format(self.test_sh, target_model_dir, test_xml, out)
                check_output(command.split())

    def transform(self, target_word, test_xml):
        """
        This method transforms the output of IMS for next procedures such as Machine translation.
        """
        self.predict(target_word, test_xml)

        input_reader = IMSInputReader()
        output_reader = IMSOutputReader()

        input_instances = input_reader.read(test_xml, fill_sense_field=True)
        output_instances = output_reader.read('/tmp/{}.result'.format(target_word))
        instances = []
        for instance_id, sense in output_instances.iteritems():
            if sense == "U":
                instances.append(input_instances[instance_id].replace(".<SENSE>", u''))
            else:
                instances.append(input_instances[instance_id].replace("<SENSE>", sense))

        return instances


class IMSInputReader(object):

    def read(self, xml_file, fill_sense_field=False):
        d = dict()
        soup = BeautifulSoup(open(xml_file), 'xml')
        instances = soup.findAll('instance')
        for instance in instances:
            instance_id = instance['id']
            text = ""
            for c in instance.context.contents:
                if c.name == 'head':
                    c = c.text
                    if fill_sense_field:
                        c = "{}.<SENSE>".format(c)
                text = "{}{}".format(text, c)
            d[instance_id] = text.strip()
        return d


class IMSOutputReader(object):

    def read(self, result_file):
        d = OrderedDict()
        for line in open(result_file):
            _, instance_id, sense = line.split()
            d[instance_id] = sense
        return d


class IMSOutputMerger(object):
    """This class helps to merge instances where more than one target word are obverved in the test sentence. It's
    exactly the case for Machine translation input file. """

    def merge(self, input_file, ims_output_dir, directory_to_write):

        global LOGGER
        LOGGER = utils.get_logger()

        create_fresh_dir(directory_to_write)

        unmatched_f = codecs.open(os.path.join(directory_to_write, 'unmatched-sentences.txt'), 'w', encoding='utf8')
        matched_f = codecs.open(os.path.join(directory_to_write, 'disambiguated-sentences.txt'), 'w', encoding='utf8')
        LOGGER.info("Output will be written on: {}".format(directory_to_write))
        target_words = [f.split('.')[0] for f in os.listdir(ims_output_dir)]
        words = map(get_single_and_plural_form, target_words)
        model_map = {}
        for word, plural in words:
            model_map[plural] = word
            model_map[word] = word

        words_with_models = set(model_map.keys())
        file2descriptors = dict()

        for j, line in enumerate(gzip.open(input_file), 1):
            line = line.decode('utf8').strip().split('\t')
            line, translation = line[1:]
            tokens = line.split()
            tokens_lowercase = line.lower().split()
            sentence = []
            match = False
            for i, (token_lower, token) in enumerate(zip(tokens_lowercase, tokens)):
                if token_lower in words_with_models:
                    match = True
                    token = get_disambiguated_form(ims_output_dir, file2descriptors, model_map[token_lower], i)
                sentence.append(token)
            if match:
                matched_f.write(u"{}\t{}\n".format(u" ".join(sentence), translation))
            else:
                unmatched_f.write(u"{}\t{}\n".format(u" ".join(sentence), translation))


def get_disambiguated_form(ims_output_dir, file2descriptors, target_word, i):

    fn = os.path.join(ims_output_dir, "%s.txt" % target_word)
    if fn in file2descriptors:
        f = file2descriptors[fn]
    else:
        f = codecs.open(fn, 'rt', encoding='utf8')
        file2descriptors[fn] = f

    sentence = f.readline().strip().split()  # read the line
    return sentence[i]  # return the ith word (disambiguated word)


def __predict_parallel(args):
    predictor, input_xml_fn, output_dir = args
    LOGGER.info("Processing %s" % input_xml_fn)
    target_word = os.path.basename(input_xml_fn).split('.', 1)[0]
    LOGGER.info("Target word: {}".format(target_word))
    instances = predictor.transform(target_word, input_xml_fn)
    with codecs.open(os.path.join(output_dir, "%s.txt" % target_word), 'wt', encoding='latin') as f:
        f.write("\n".join(instances))


def predict(model_dir, input_dir, output_dir, num_of_process=1):
    global LOGGER

    LOGGER = utils.get_logger()

    files = sorted(glob.glob(os.path.join(input_dir, "*.xml")))

    try:
        os.mkdir(output_dir)
    except OSError:
        LOGGER.debug("{} is already exist. Directory is removed.".format(output_dir))
        shutil.rmtree(output_dir)  # remove the directory with its content.
        os.mkdir(output_dir)

    predictor = IMSPredictor(model_dir)

    args = [(predictor, fn, output_dir) for fn in sorted(files)]
    if num_of_process > 1:
        pool = Pool(num_of_process)
        pool.map(__predict_parallel, args)
    else:
        map(__predict_parallel, args)
