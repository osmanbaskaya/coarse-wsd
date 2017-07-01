"""
Module that covers functionality to prepare disambiguation dataset for training and testing.
"""
import os
import gzip
import pickle
import numpy as np
import tensorflow as tf
import threading
from collections import Counter
import spacy

NLP = spacy.en.English()

START_TOKEN = "<<START>>"
OOV_TOKEN = "<<PAD>>"
PAD_TOKEN = "<<OOV>>"
END_TOKEN = "<<END>>"

SPECIAL_TOKENS = {PAD_TOKEN: 0, START_TOKEN: 1, OOV_TOKEN: 2, END_TOKEN: 3}


class DataSet(object):

    def __init__(self, train_dir, validate_dir, test_dir):
        self.train_dir = train_dir
        self.validate_dir = validate_dir
        self.test_dir = test_dir
        dir = os.path.dirname(train_dir)
        vocab_dir = os.path.join(dir, "vocab")
        if not os.path.exists(vocab_dir):
            os.mkdir(vocab_dir)
        self.vocab_file = os.path.join(vocab_dir, "vocabulary")


def fopen(filename, *args, **kwargs):
    func = open
    if filename.endswith('.gz'):
        func = gzip.open
    return func(filename, *args, **kwargs)


def dataset_size(filenames, *args, **kwargs):
    return sum(map(lambda fn: len(fopen(fn, *args, **kwargs).read().splitlines()), filenames))


def tokenize(sentence):
    return [t.text for t in NLP(sentence)]


def build_vocab(path, vocab_file, min_counts=5, save_vocab=True):

    # If vocab is already exists, read it.
    if os.path.exists(vocab_file):
        word2idx, idx2word = pickle.load(vocab_file)
    else:
        counts = Counter()
        for line in fopen(path):
            tokens = tokenize(line.strip())
            for token in tokens:
                counts[token] += 1

        word2idx = {word: idx + len(SPECIAL_TOKENS) for idx, (word, count) in enumerate(counts.most_common()) if count > min_counts}
        word2idx.update(SPECIAL_TOKENS)

        idx2word = {idx: word for word, idx in word2idx.items()}

        if save_vocab:
            pickle.dump([word2idx, idx2word], vocab_file)

    return word2idx, idx2word


def map_token_to_id(sentence, word2idx):
    id_vec = [word2idx[START_TOKEN]]

    for token in sentence.split():
        id_vec.append(word2idx.get(token, OOV_TOKEN))

    id_vec.append(word2idx[END_TOKEN])

    return id_vec, len(id_vec)


def prepare_data(path, word2idx, **opts):
    with tf.device("/cpu:0"):
        enqueue_data, dequeue_batch = prepare_queues(
            path, word2idx, batch_size=opts["batch_size"])
        source = tf.placeholder_with_default(dequeue_batch[0], (None, None))
        label = tf.placeholder_with_default(dequeue_batch[1], None)
        sequence_length = tf.placeholder_with_default(dequeue_batch[2], None)
    return enqueue_data, source, label, sequence_length


def prepare_queues(sess, filenames, word2idx, batch_size, skip_header_lines=0, shuffle=False):
    filename_queue = tf.train.string_input_producer(filenames, shuffle=shuffle)
    reader = tf.TextLineReader(skip_header_lines=skip_header_lines)

    filename, line_op = reader.read(filename_queue)
    sentence_ph = tf.placeholder(tf.int32, shape=[None])
    label_ph = tf.placeholder(tf.int32, shape=None)
    length_ph = tf.placeholder(tf.int32, shape=None)

    # [[int32, ...], int32, int32]
    # TODO: Check if string for label also works.
    queue = tf.PaddingFIFOQueue(shapes=[[None, ], [], []], dtypes=[tf.int32, tf.int32, tf.int32], capacity=10000)
    enqueue_op = queue.enqueue([sentence_ph, label_ph, length_ph])

    def enqueue_data(coord):
        while not coord.should_stop():
            try:
                line = sess.run(line_op)
                sentence, label = line.strip().split('\t')
                sentence, length = map_token_to_id(sentence, word2idx)
                sess.run(enqueue_op, {sentence_ph: line, label_ph: int(label), length_ph: length})
            except tf.errors.OutOfRangeError:
                print("Done training")
                exit()

    dequeue_op = queue.dequeue_many(batch_size)

    # TODO: Add batch mode if necessary.
    # dequeue_op = queue.dequeue()
    # dequeue_batch = tf.train.batch([dequeue_op], batch_size=batch_size, num_threads=num_threads, capacity=1000,
    #                                dynamic_pad=True, name="batch_and_pad")

    return enqueue_data, dequeue_op



