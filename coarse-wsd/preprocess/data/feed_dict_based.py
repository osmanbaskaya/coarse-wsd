from constant import NUM_ALREADY_ALLOCATED_TOKEN, UNKNOWN_TOKEN_ID, END_OF_SENTENCE_ID
import numpy as np
import os
from itertools import cycle
import tensorflow as tf
from collections import Counter

LOGGER = None


class Vocabulary(object):
    def __init__(self, word_to_id, num_of_already_allocated_tokens=0):
        self.word_to_id = word_to_id
        self.num_of_already_allocated_tokens = num_of_already_allocated_tokens
        self.__vocab_size = len(word_to_id) + num_of_already_allocated_tokens

    def __iter__(self):
        for word, idx in self.word_to_id.items():
            yield word, idx

    def __getitem__(self, item):
        return self.word_to_id[item]

    @property
    def size(self):
        return self.__vocab_size

    def get(self, item, default=None):
        return self.word_to_id.get(item, default)

    @staticmethod
    def build(words, min_occurrence=1, num_already_allocated_tokens=0):
        counter = Counter(words)

        # Remove words that are observed fewer than the threshold.
        remove_list = [w for w, f in counter.items() if f < min_occurrence]
        list(map(counter.pop, remove_list))

        range_start = num_already_allocated_tokens
        range_finish = len(counter) + num_already_allocated_tokens

        word_to_id = dict(zip(counter.keys(), range(range_start, range_finish)))
        return Vocabulary(word_to_id, num_already_allocated_tokens)


def _read_words(filename):
    with tf.gfile.GFile(filename, "r") as f:
        return f.read().split()


def _read_lines(filename):
    with tf.gfile.GFile(filename, "r") as f:
        return f.read().splitlines()


def _read_lines_by_batch(filename, batch_size):
    batch = []
    with tf.gfile.GFile(filename, "r") as f:
        lines = f.read().splitlines()
        for i, line in enumerate(cycle(lines), 1):
            batch.append(line.strip())
            if i % batch_size == 0:
                yield batch
                batch = []

    if len(batch) != 0:
        yield batch


def _read_labels(filename, batch_size):
    return _read_lines_by_batch(filename, batch_size)


def build_vocab(filename, min_occurrence=1, num_already_allocated_tokens=NUM_ALREADY_ALLOCATED_TOKEN):
    # TODO: add functionality to replace infrequent words with <unk>.
    data = _read_words(filename)
    vocabulary = Vocabulary.build(data, min_occurrence=min_occurrence,
                                  num_already_allocated_tokens=num_already_allocated_tokens)
    return vocabulary


def _file_to_word_ids(filename, word_to_id, batch_size, unknown_token_id=UNKNOWN_TOKEN_ID):
    data_iter = _read_lines_by_batch(filename, batch_size)
    for batch in data_iter:
        max_length = -1
        lines = []
        for line in batch:
            words = line.split()
            word_ids = [word_to_id.get(word, unknown_token_id) for word in words]
            word_ids.append(END_OF_SENTENCE_ID)
            lines.append(word_ids)

        lengths = list(map(len, lines))
        max_seq_length = max(lengths)
        padded_batch = np.zeros(shape=[len(lengths), max_seq_length], dtype=np.int32)
        for i, seq in enumerate(lines):
            for j, elem in enumerate(seq):
                padded_batch[i, j] = elem

        padded_batch = padded_batch.swapaxes(0, 1)

        yield padded_batch, lengths


def _file_to_sense_ids(filename, vocabulary, batch_size):
    data_iter = _read_lines_by_batch(filename, batch_size)
    for batch in data_iter:
        lines = []
        for sense in batch:
            lines.append(vocabulary[sense])
        yield lines


def read_data(word_vocab, label_vocab, data_path="", dataset_type='train', batch_size=128):
    sentences_fn = os.path.join(data_path, "sentences.%s.txt" % dataset_type)
    labels_fn = os.path.join(data_path, "senses.%s.txt" % dataset_type)

    sentences_iter = _file_to_word_ids(sentences_fn, word_vocab, batch_size=batch_size)
    labels_iter = _file_to_sense_ids(labels_fn, label_vocab, batch_size=batch_size)

    for (sentences, sentence_lengths), labels in zip(sentences_iter, labels_iter):
        yield sentences, sentence_lengths, labels
