"""
Module that covers functionality to prepare disambiguation dataset for training and testing.
"""
import os
import gzip
import threading
import time
import sys
import glob
import pickle
import numpy as np
from gensim.models import KeyedVectors
import tensorflow as tf
from collections import Counter
from constant import SPECIAL_TOKENS, START_TOKEN, END_TOKEN, OOV_TOKEN, WORD2VEC_EMB_DIMENSION, WORD2VEC_PATH, PAD_TOKEN
import spacy

NLP = spacy.en.English()


class DataSet(object):

    def __init__(self, train_dir, validate_dir=None, test_dir=None):

        self.train_dir = train_dir
        self.validate_dir = validate_dir
        self.test_dir = test_dir

        self.training_files = glob.glob(os.path.join(self.train_dir, 'apartment.txt'))

        if self.validate_dir is not None:
            self.validate_files = glob.glob(os.path.join(self.validate_dir, '*.txt'))

        if self.test_dir is not None:
            self.test_files = glob.glob(self.test_dir)

        dir = os.path.dirname(train_dir)
        vocab_dir = os.path.join(dir, "vocab")
        if not os.path.exists(vocab_dir):
            os.mkdir(vocab_dir)
        self.vocab_file = os.path.join(vocab_dir, "vocabulary.pkl")


def fopen(filename, *args, **kwargs):
    func = open
    if filename.endswith('.gz'):
        func = gzip.open
    return func(filename, *args, **kwargs)


def dataset_size(filenames, *args, **kwargs):
    return sum(map(lambda fn: len(fopen(fn, *args, **kwargs).read().splitlines()), filenames))


def tokenize(sentence):
    return [t.text for t in NLP(sentence)]


def _aggregate(filename, token_counts, label2idx):

    label_id = len(label2idx)
    print(filename)
    for line in fopen(filename):
        sentence, label = line.strip().split('\t')[:2]
        tokens = sentence.split()
        for token in tokens:
            token_counts[token] += 1

        if label not in label2idx:
            label2idx[label] = label_id
            label_id += 1

    return token_counts, label2idx


def build_vocab(path, vocab_save_path=None, word2vec=None, min_counts=5, save_vocab=True):

    """
    This method builds 4 vocabulary dicts; word2idx, idx2word, label2idx, idx2label.

    :param path: path of the training file
    :param vocab_save_path: path of the vocabulary file to save
    :param word2vec: word2vec model from Gensim.
    :param min_counts: minimum number of observation to keep tokens in the vocabulary.
    :param save_vocab: it defines whether save the vocabulary dicts or not.
    :return: 4 dictionaries.
    """

    label2idx = {}

    # If vocab is already exists, read it.
    if os.path.exists(vocab_save_path):
        word2idx, idx2word, label2idx, idx2label = pickle.load(open(vocab_save_path, 'rb'))
    else:
        token_counts = Counter()
        if isinstance(path, list):
            for filename in path:
                token_counts, label2idx = _aggregate(filename, token_counts, label2idx)
        else:
            token_counts, label2idx = _aggregate(path, token_counts, label2idx)

        if word2vec is None:
            word2idx = {word: idx + len(SPECIAL_TOKENS) for idx, (word, count) in enumerate(token_counts.most_common())
                        if count > min_counts}
        else:
            word2idx = {word: idx + len(SPECIAL_TOKENS) for idx, (word, count) in enumerate(token_counts.most_common())
                        if count > min_counts and word in word2vec}

        idx2word = {idx: word for word, idx in word2idx.items()}
        idx2label = {idx: label for label, idx in label2idx.items()}

        word2idx.update(SPECIAL_TOKENS)  # add special tokens.

        if save_vocab:
            pickle.dump([word2idx, idx2word, label2idx, idx2label], open(vocab_save_path, 'wb'))

    return word2idx, idx2word, label2idx, idx2label


def map_token_to_id(sentence, word2idx):
    id_vec = [word2idx[START_TOKEN]]

    for token in sentence.split():
        id_vec.append(word2idx.get(token, SPECIAL_TOKENS[OOV_TOKEN]))

    id_vec.append(word2idx[END_TOKEN])

    return id_vec, len(id_vec)


def prepare_data(sess, path, word2idx, label2idx, **opts):
    with tf.device("/cpu:0"):
        enqueue_data, dequeue_batch = prepare_queues(sess, path, word2idx, label2idx, batch_size=opts["batch_size"])
        source = tf.placeholder_with_default(dequeue_batch[0], (None, None))
        target_word = tf.placeholder_with_default(dequeue_batch[1], None)
        label = tf.placeholder_with_default(dequeue_batch[2], None)
        sequence_length = tf.placeholder_with_default(dequeue_batch[3], None)
    return enqueue_data, source, target_word, label, sequence_length


def prepare_queues(sess, filenames, word2idx, label2idx, batch_size, skip_header_lines=0, shuffle=False):
    filename_queue = tf.train.string_input_producer(filenames, shuffle=shuffle)
    reader = tf.TextLineReader(skip_header_lines=skip_header_lines)

    filename, line_op = reader.read(filename_queue)
    sentence_ph = tf.placeholder(tf.int32, shape=[None])
    target_word_ph = tf.placeholder(tf.int32, shape=None)
    label_ph = tf.placeholder(tf.int32, shape=None)
    length_ph = tf.placeholder(tf.int32, shape=None)

    # [[int32, ...], int32, int32]
    # TODO: Check if string for label also works.
    queue = tf.PaddingFIFOQueue(shapes=[[None, ], [], [], []], dtypes=[tf.int32, tf.int32, tf.int32, tf.int32],
                                capacity=10000)
    enqueue_op = queue.enqueue([sentence_ph, target_word_ph, label_ph, length_ph])

    def enqueue_data(coord):
        while not coord.should_stop():
            try:
                line = sess.run(line_op).decode("utf-8")
                line = line.strip().split('\t')
                sentence, label, target_word_index = line[:3]
                target_word_index = int(target_word_index)
                # print(sentence, label, target_word_index, sep='\n')
                label = label2idx[label]  # label transformation
                sentence, length = map_token_to_id(sentence, word2idx)
                target_word = sentence[target_word_index + 1]  # +1 for starting token
                sess.run(enqueue_op, {sentence_ph: sentence, target_word_ph: target_word, label_ph: label, length_ph: length})
            except tf.errors.OutOfRangeError:
                print("Done training")
                exit()

    dequeue_op = queue.dequeue_many(batch_size)

    # TODO: Add batch mode if necessary.
    # dequeue_op = queue.dequeue()
    # dequeue_batch = tf.train.batch([dequeue_op], batch_size=batch_size, num_threads=num_threads, capacity=1000,
    #                                dynamic_pad=True, name="batch_and_pad")

    return enqueue_data, dequeue_op


def get_word2vec_model(path=WORD2VEC_PATH):
    return KeyedVectors.load_word2vec_format(path, binary=True)


def get_embedding_weights(vocabulary, word2vec_model):
    embedding_weights = np.random.rand(vocabulary.size, WORD2VEC_EMB_DIMENSION)
    embedding_weights[PAD_TOKEN, :] = np.zeros(WORD2VEC_EMB_DIMENSION)  # zeros for padding token.

    missing = set()
    for word, idx in vocabulary:
        if word in word2vec_model:
            embedding_weights[idx, :] = word2vec_model[word]
        else:
            print(u"{} not found.".format(word), file=sys.stderr)
            missing.add(word)

    print(u"Total number of missing words: {}".format(len(missing)), file=sys.stderr)
    return embedding_weights


def start_threads(thread_fn, args, n_threads=1):
    print("{} starting with {} threads.".format(thread_fn.__name__, n_threads))

    # TODO check this: "Having multiple threads causes duplicate data in the queue."

    threads = []
    for n in range(n_threads):
        t = threading.Thread(target=thread_fn, args=args, daemon=True)
        t.start()
        threads.append(t)

    time.sleep(1)  # enqueue a bunch before dequeue
    return threads



