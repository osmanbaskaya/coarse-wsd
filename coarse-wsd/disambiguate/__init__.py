from abc import abstractclassmethod
import numpy as np
import tensorflow as tf
from tensorflow.contrib.rnn import LSTMCell, LSTMStateTuple


LOGGER = None


class SimpleDisambiguator(object):

    @abstractclassmethod
    def fit(self, training_data_iterator, validation_data_iterator=None, max_steps=None):
        raise NotImplementedError("Implement this method")

    @abstractclassmethod
    def disambiguate(self, sentence_iterator):
        raise NotImplementedError("Implement this method")

    @abstractclassmethod
    def score(self, test_data_iterator):
        raise NotImplementedError("Implement this method")


class NeuralDisambiguator(SimpleDisambiguator):

    def __init__(self, hidden_unit_size, learning_rate, num_senses, embedding_weights=None, embedding_length=None,
                 vocab_size=None):

        # FIXME: Input check should be extended. Vocab_size should be checked.
        if not any([embedding_weights, embedding_length]) or all([embedding_weights, embedding_length]):
            raise ValueError("Either embedding_weights or embedding_size should be provided.")

        self.sentences = tf.placeholder(shape=(None, None), dtype=tf.int32, name='sentences')
        self.sentence_lengths = tf.placeholder(shape=(None,), dtype=tf.int32, name='sentences_length')
        # the word idx to disambiguate. (we keep the word index)
        self.target_words = tf.placeholder(shape=(None,), dtype=tf.int32, name='target_words')
        # Target labels
        self.senses = tf.placeholder(shape=(None,), dtype=tf.int64, name='senses')

        # TODO: Add Dropout layer later.
        self.dropout_keep_prob = tf.placeholder(tf.float32, name="dropout_keep_prob")

        # LOGGER.info("Embeddings shape {}".format(embedding_weights.shape))

        if embedding_weights:
            # TODO: embedding might be trainable.
            embedding_length = embedding_weights.shape[1]
            self.embeddings = tf.Variable(embedding_weights, dtype=tf.float32, trainable=False)
        else:
            self.embeddings = tf.Variable(tf.random_uniform([vocab_size, embedding_length], -1.0, 1.0), dtype=tf.float32)

        self.target_words_embedded = tf.nn.embedding_lookup(self.embeddings, self.target_words)
        self.sentences_embedded = tf.nn.embedding_lookup(self.embeddings, self.sentences)
        encoder_cell = LSTMCell(hidden_unit_size)

        (encoder_fw_outputs, encoder_bw_outputs), (encoder_fw_final_state, encoder_bw_final_state) = \
            tf.nn.bidirectional_dynamic_rnn(cell_fw=encoder_cell, cell_bw=encoder_cell, inputs=self.sentences_embedded,
                                            sequence_length=self.sentence_lengths, dtype=tf.float32, time_major=True)

        encoder_final_state_c = tf.concat((encoder_fw_final_state.c, encoder_bw_final_state.c), 1)
        encoder_final_state_h = tf.concat((encoder_fw_final_state.h, encoder_bw_final_state.h), 1)
        encoder_final_state = LSTMStateTuple(c=encoder_final_state_c, h=encoder_final_state_h)

        self.encoder_target_embedding = encoder_final_state.c
        # encoder_target_embedding = tf.concat((encoder_final_state.c), 1)
        # encoder_target_embedding = tf.concat((encoder_final_state.c, self.target_words_embedded), 1)

        with tf.name_scope("output"):
            # W = tf.Variable(tf.truncated_normal([hidden_unit_size * 2 + embedding_length, num_senses], stddev=0.1), name="W")
            W = tf.Variable(tf.truncated_normal([hidden_unit_size * 2, num_senses], stddev=0.1), name="W")
            b = tf.Variable(tf.constant(0.1, shape=[num_senses]), name="b")
            self.scores = tf.matmul(self.encoder_target_embedding, W) + b
            self.predictions = tf.argmax(self.scores, 1, name="predictions")

        with tf.name_scope('cross_entropy'):
            self.labels = tf.one_hot(self.senses, num_senses)
            self.diff = tf.nn.softmax_cross_entropy_with_logits(labels=self.labels, logits=self.scores)

        with tf.name_scope('loss'):
            self.loss = tf.reduce_mean(self.diff)

        with tf.name_scope('train'):
            self.train_step = tf.train.AdamOptimizer(learning_rate).minimize(self.loss)

        with tf.name_scope('accuracy'):
            with tf.name_scope('correct_prediction'):
                correct_prediction = tf.equal(tf.argmax(self.predictions, 1), tf.argmax(self.senses, 1))
            with tf.name_scope('accuracy'):
                self.accuracy = tf.reduce_mean(tf.cast(correct_prediction, tf.float32))

        self.sess = tf.Session()
        self.sess.run(tf.global_variables_initializer())

    def get_feed_dict_for_next_batch(self, data_iterator):

        sentences, sentence_lengths, senses = next(data_iterator)
        target_words = [0 for sentence in sentences]
        return {self.sentences: sentences, self.sentence_lengths: sentence_lengths, self.target_words: target_words,
                self.senses: senses}

    def disambiguate(self, test_data_iterator):
        pass

    def fit(self, training_data_iterator, validation_data_iterator=None, max_steps=1000):
        for i in range(1, max_steps + 1):
            feed_dict = self.get_feed_dict_for_next_batch(training_data_iterator)
            _, loss = self.sess.run([self.train_step, self.loss], feed_dict=feed_dict)
            print(loss)
            if i % 100 == 0 and validation_data_iterator is not None:
                feed_dict = self.get_feed_dict_for_next_batch(validation_data_iterator)
                accuracy = self.sess.run([self.accuracy], feed_dict=feed_dict)
                print("Accuracy for step {}:".format(i, accuracy))

    def score(self, test_data_iterator):
        pass





