# -*- coding: utf-8 -*-
import os
import re
from multiprocessing import Pool
import gzip
from collections import defaultdict as dd
import codecs
from xml.sax.saxutils import escape
import shutil
from constant import MODEL_PATH

import utils

LOGGER = None

regex = re.compile(u"<target>(\w+)</target>")

IRREGULAR_NOUNS = set(["boy",])


def transform_into_IMS_input_format(f, out_fn, target_word):
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
        for line in codecs.open(f, mode='rt', encoding='utf8'):
            line = line.strip().split('\t')
            assert len(line) == 3, u"Line should have 3 elements. %s" % line
            instance_id, sentence = line[:2]
            sentence = utils.remove_non_ascii(sentence)
            sentence = escape(sentence)
            # for t in replace_set:
            #     sentence = sentence.replace(*t)
            sentence = re.sub("&lt;target&gt;\w+&lt;/target&gt;", "<head>%s</head>" % target_word,
                              sentence, 1)
            # assert "<head>%s</head>" % target_word in sentence, "headword not found."
            out.write(instance.format(target_word, instance_id, sentence))
        out.write(end)


def prepare_one_target_word(args):
    f, directory_to_write = args
    _, fn = os.path.split(f)
    target_word = fn.split('.')[0]

    print "Processing {}".format(target_word)
    out_dir = os.path.join(directory_to_write)
    out_fn_data = os.path.join(out_dir, '%s.xml' % target_word)
    transform_into_IMS_input_format(f, out_fn_data, target_word)


def create_IMS_formatted_dataset(files, directory_to_write, num_of_process=1):
    """
    It creates a k-fold datasets for IMS.
    """
    # create_directory_here

    global LOGGER

    LOGGER = utils.get_logger()

    try:
        os.mkdir(directory_to_write)
    except OSError:
        LOGGER.debug("{} is already exist. Directory is removed.".format(directory_to_write))
        shutil.rmtree(directory_to_write)  # remove the directory with its content.
        os.mkdir(directory_to_write)

    args = [(f, directory_to_write) for f in sorted(files)]
    if num_of_process > 1:
        pool = Pool(num_of_process)
        pool.map(prepare_one_target_word, args)
    else:
        map(prepare_one_target_word, args)


def get_single_and_plural_form(word):
    if word.endswith("y") and word not in IRREGULAR_NOUNS:
        plural = word[:-1] + "ies"
    elif word.endswith("x"):
        plural = word[:-1] + "es"
    else:
        plural = word + "s"

    return word, plural


def create_IMS_formatted_dataset_for_MT(file='giga-fren.release2.fixed.en.lem.small.gz', directory_to_write='/tmp/mt-dataset',
                                        write_every_n_line=200000):
    """Create IMS formatted dataset for Machine translation task"""

    global LOGGER

    LOGGER = utils.get_logger()

    def write2files():
        for key, lines in sentences.iteritems():
            fn = os.path.join(directory_to_write, "%s.txt" % key)
            if fn in file2descriptor:
                f = file2descriptor[fn]
            else:
                f = codecs.open(fn, 'w', encoding='utf8')
                file2descriptor[fn] = f
            for curr_line in lines:
                f.write(curr_line)

    try:
        os.mkdir(directory_to_write)
    except OSError:
        LOGGER.debug("{} is already exist. Directory is removed.".format(directory_to_write))
        shutil.rmtree(directory_to_write)  # remove the directory with its content.
        os.mkdir(directory_to_write)

    # load models into a set.
    words = map(get_single_and_plural_form, os.listdir(MODEL_PATH))
    model_map = {}
    for word, plural in words:
        model_map[plural] = word
        model_map[word] = word  # seems stupid; you're right Mr. Sherlock.

    words_with_models = set(model_map.keys())

    sentences = dd(list)

    # FIXME: change /tmp directory.
    unmatched_f = codecs.open(os.path.join("/tmp", 'unmatched-sentences.txt'), 'w', encoding='utf8')

    file2descriptor = dict()

    num_of_matched = 0
    total_matched = 0
    j = 0

    for j, line in enumerate(gzip.open(file), 1):
        line = line.decode('utf-8')
        line = line.strip().split('\t')[0]  # get the original sentence.
        tokens = line.split()
        tokens_lowercase = line.lower().split()
        matched_sentences = []
        for i, word in enumerate(tokens_lowercase):
            if word in words_with_models:
                num_of_matched += 1
                matched_sentences.append((word, u"{} <target>{}</target> {}".format(u" ".join(tokens[:i]), tokens[i],
                                                                                      u" ".join(tokens[i+1:]))))

        # TODO add translation at the end of the line and remove the line at the end.
        if len(matched_sentences) == 0:
            unmatched_f.write(u"{}\t{}\t{}\n".format(j, line, "translation"))
        elif len(matched_sentences) == 1:
            word, matched_sentence = matched_sentences[0]
            sentences[model_map[word]].append(u"{}\t{}\t{}\n".format(j, matched_sentence, "translation"))
        else:
            for i, (word, matched_sentence) in enumerate(matched_sentences):
                sentences[model_map[word]].append(u"m-{}-{}\t{}\t{}\n".format(i, j, matched_sentence, "translation"))

        if num_of_matched >= write_every_n_line:
            total_matched += num_of_matched
            LOGGER.info("{} processed. Total match: {}".format(j, total_matched))
            write2files()
            sentences = dd(list)
            LOGGER.info("sentences dict length now is {}".format(len(sentences)))
            num_of_matched = 0

    total_matched += num_of_matched
    LOGGER.info("{} processing. Total match: {}".format(j, total_matched))
    write2files()
