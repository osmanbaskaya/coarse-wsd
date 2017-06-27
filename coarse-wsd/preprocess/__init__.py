# -*- coding: utf-8 -*-
import os
import re
from multiprocessing import Pool
from collections import Counter
import codecs
from xml.sax.saxutils import escape
import shutil
import random
from operator import itemgetter
from sklearn.model_selection import StratifiedKFold

import utils

LOGGER = None

regex = re.compile(u"<target>(\w+)</target>")


def create_sense_dataset(files, directory_to_write, preserve_surface_form=True):
    """
    It creates a dataset by concatenating each target word with its sense. This may help to create sense aware
    word embeddings. This method creates an input for embeddings methods (i.e. Word2Vec)
    :param files:
    :param directory_to_write:
    :return:
    """

    global LOGGER

    LOGGER = utils.get_logger()

    try:
        os.mkdir(directory_to_write)
    except OSError:
        LOGGER.debug("{} is already exist. Directory is removed.".format(directory_to_write))
        shutil.rmtree(directory_to_write)  # remove the directory with its content.
        os.mkdir(directory_to_write)

    for f in files:
        directory, fn = os.path.split(f)
        fn, ext = os.path.splitext(fn)
        target_word = fn.split('.')[0]
        surface_form = target_word
        d = dict()
        replaced_sentence = []
        for line in codecs.open(f, encoding='utf8'):
            line = line.strip().split('\t')
            sentence, sense = line[0], line[2]
            sense_id = d.get(sense, None)
            if sense_id is None:
                sense_id = len(d)
                d[sense] = sense_id
            if preserve_surface_form:
                surface_form = regex.search(sentence).group(1)
            sentence = regex.sub(u"{}.{}".format(surface_form, sense_id), sentence)
            replaced_sentence.append(sentence)
        with codecs.open(os.path.join(directory_to_write, '%s.txt' % target_word), 'w', encoding='utf8') \
                as out:
            out.write('\n'.join(replaced_sentence))
        with open(os.path.join(directory_to_write, "%s.keydict.txt" % target_word), 'w') as keyfile:
            keyfile.write("\n".join((["{}\t{}".format(*sense) for sense in d.iteritems()])))
            keyfile.write('\n')


def transform_into_IMS_input_format(lines, out_fn, target_word, data_idx):
    """<?xml version="1.0" encoding="iso-8859-1" ?><!DOCTYPE corpus SYSTEM "lexical-sample.dtd">
         <corpus lang='english'>
         <lexelt item="bank.n">
            <instance id="bank.n.bnc.00000728" docsrc="BNC">
            <context>
            not pay it into the <head>bank</head> until we have received the signed Deed of Covenant .
            </context>
            </instance>

            ...
            ...

        </lexelt>
        </corpus>
    """

    start = u"""<?xml version="1.0" encoding="iso-8859-1" ?><!DOCTYPE corpus SYSTEM "lexical-sample.dtd">
      <corpus lang='english'>
      <lexelt item="{}">\n""".format(target_word)

    instance = u"""
            <instance id="{}.{}" docsrc="BNC">
            <context>
            {}
            </context>
            </instance>\n"""

    end = u"</lexelt>\n</corpus>\n"

    # replace_set = [(u"–", ' '), (u"被", " "), (u"給", " ")]

    with codecs.open(out_fn, 'w', encoding='utf8') as out:
        out.write(start)
        for line, i in zip(lines, data_idx):
            sentence = line.split('\t')[0]
            sentence = utils.remove_non_ascii(sentence)
            sentence = escape(sentence)
            # for t in replace_set:
            #     sentence = sentence.replace(*t)
            # TODO: remove 1 in sub function and add '/' second target tag after David changes the java code.
            sentence = re.sub("&lt;target&gt;\w+&lt;/target&gt;", "<head>%s</head>" % target_word,
                              sentence, 1)
            assert "<head>%s</head>" % target_word in sentence, "headword not found."
            out.write(instance.format(target_word, i, sentence))
        out.write(end)


def transform_into_IMS_key_format(lines, out_fn, target_word, test_idx):
    with codecs.open(out_fn, 'w', encoding='utf8') as out:
        for line, i in zip(lines, test_idx):
            sense = line.split('\t')[2]
            out.write(u"{} {}.{} {}\n".format("BNC", target_word, i, sense))


def create_directories_for_folding(directory_to_write, k):
    try:
        shutil.rmtree(directory_to_write)  # remove the path and its content.
    except OSError:
        pass

    os.mkdir(directory_to_write)
    map(lambda fold: os.mkdir(os.path.join(directory_to_write, "fold-%d" % fold)), range(1, k+1))


def get_filtered_instances(lines, k):
    if len(lines) > 0:
        y = map(lambda line: line.split('\t')[2], lines)
        sense_dict = Counter(y)

        pairs = sorted(sense_dict.items(), key=lambda t: t[1])
        pairs = filter(lambda p: p[1] > k, pairs)  # filter out senses that have less than k instances.
        pairs = set(map(lambda t: t[0], pairs))
        if len(pairs) > 1:
            idx = [i for i, sense in enumerate(y) if sense in pairs]
            filtered_lines = itemgetter(*idx)(lines)
            return filtered_lines

    return []


def prepare_one_target_word(args):
    f, directory_to_write, k = args
    _, fn = os.path.split(f)
    target_word = fn.split('.')[0]

    lines = codecs.open(f, encoding='utf8').read().splitlines()
    lines = get_filtered_instances(lines, k)
    y = map(lambda line: line.split('\t')[2], lines)

    if len(lines) > 100:
        print("Processing {}".format(target_word))
        if k > 1:
            skf = StratifiedKFold(y, k, shuffle=True)
            for fold, (train_idx, test_idx) in enumerate(skf, 1):
                train = itemgetter(*train_idx)(lines)
                test = itemgetter(*test_idx)(lines)
                out_dir = os.path.join(directory_to_write, "fold-%d" % fold)
                for dataset_type, dataset, data_idx in (('train', train, train_idx), ('test', test, test_idx)):
                    out_fn_data = os.path.join(out_dir, '%s.%s.xml' % (target_word, dataset_type))
                    out_fn_key = os.path.join(out_dir, '%s.%s.key' % (target_word, dataset_type))
                    transform_into_IMS_input_format(dataset, out_fn_data, target_word, data_idx)
                    transform_into_IMS_key_format(dataset, out_fn_key, target_word, data_idx)
        elif k == 1:
            # Create a data to train only. Use all the data for training.
            train = lines
            train_idx = range(len(lines))
            fold = 1
            out_dir = os.path.join(directory_to_write, "fold-%d" % fold)
            for dataset_type, dataset, data_idx in (('train', train, train_idx),):
                out_fn_data = os.path.join(out_dir, '%s.%s.xml' % (target_word, dataset_type))
                out_fn_key = os.path.join(out_dir, '%s.%s.key' % (target_word, dataset_type))
                transform_into_IMS_input_format(dataset, out_fn_data, target_word, data_idx)
                transform_into_IMS_key_format(dataset, out_fn_key, target_word, data_idx)

        else:
            raise ValueError("k should be bigger than 0")
    else:
        print("\tSkipping {}".format(target_word))


def create_IMS_formatted_dataset(files, directory_to_write, k=5, num_of_process=1):
    """
    It creates a k-fold datasets for IMS.
    """
    create_directories_for_folding(directory_to_write, k)
    random.seed(42)
    args = [(f, directory_to_write, k) for f in sorted(files)]
    if num_of_process > 1:
        pool = Pool(num_of_process)
        pool.map(prepare_one_target_word, args)
    else:
        map(prepare_one_target_word, args)

