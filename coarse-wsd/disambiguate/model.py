from abc import abstractclassmethod
import tensorflow as tf
from tensorflow.contrib.rnn import LSTMCell, LSTMStateTuple
from constant import WORD2VEC_EMB_DIMENSION, WORD2VEC_PATH
from data_loader import build_vocab, get_embedding_weights, get_word2vec_model, prepare_data, start_threads

LOGGER = None


class SimpleDisambiguator(object):

    @abstractclassmethod
    def fit(self, max_steps=None):
        raise NotImplementedError("Implement this method")

    @abstractclassmethod
    def disambiguate(self, sentence_iterator):
        raise NotImplementedError("Implement this method")

    @abstractclassmethod
    def score(self, test_data_iterator):
        raise NotImplementedError("Implement this method")


class NeuralDisambiguator(SimpleDisambiguator):

    def __init__(self, dataset, opts, use_pretrained_embeddings=True):

        # TODO: Add Dropout layer later.
        self.dropout_keep_prob = tf.placeholder(tf.float32, name="dropout_keep_prob")

        if use_pretrained_embeddings:
            word2vec = get_word2vec_model(WORD2VEC_PATH)
            word2idx, idx2word, label2idx, idx2label = build_vocab(dataset.training_files, dataset.vocab_file, word2vec,
                                                                   min_counts=opts['min_counts'])
            embedding_weights = get_embedding_weights(word2idx, word2vec)
            embedding_length = embedding_weights.shape[1]
            # TODO: embedding might be trainable.
            self.embeddings = tf.Variable(embedding_weights, dtype=tf.float32, trainable=False)
        else:
            word2idx, idx2word, label2idx, idx2label = build_vocab(dataset.training_files, dataset.vocab_file,
                                                                   min_counts=opts['min_counts'])
            embedding_length = opts['embedding_length']
            self.embeddings = tf.Variable(tf.random_uniform([len(word2idx), embedding_length], -1.0, 1.0),
                                          dtype=tf.float32)

        self.sess = tf.Session()

        self.enqueue_data, self.source, self.target_word, self.label, \
            self.sequence_length = prepare_data(self.sess, dataset.training_files, word2idx, label2idx, **opts)

        self.target_words_embedded = tf.nn.embedding_lookup(self.embeddings, self.target_word)
        self.sentences_embedded = tf.nn.embedding_lookup(self.embeddings, self.source)

        hidden_unit_size = opts['hidden_unit_size']
        num_senses = len(label2idx)

        encoder_cell = LSTMCell(hidden_unit_size)

        (encoder_fw_outputs, encoder_bw_outputs), (encoder_fw_final_state, encoder_bw_final_state) = \
            tf.nn.bidirectional_dynamic_rnn(cell_fw=encoder_cell, cell_bw=encoder_cell, inputs=self.sentences_embedded,
                                            sequence_length=self.sequence_length, dtype=tf.float32, time_major=True)

        encoder_final_state_c = tf.concat((encoder_fw_final_state.c, encoder_bw_final_state.c), 1)
        encoder_final_state_h = tf.concat((encoder_fw_final_state.h, encoder_bw_final_state.h), 1)
        encoder_final_state = LSTMStateTuple(c=encoder_final_state_c, h=encoder_final_state_h)

        # self.encoder_target_embedding = encoder_final_state.c
        self.encoder_target_embedding = tf.concat((encoder_final_state.c, self.target_words_embedded), 1)

        with tf.name_scope("output"):
            W = tf.Variable(tf.truncated_normal([hidden_unit_size * 2 + embedding_length, num_senses],
                                                stddev=0.1), name="W")
            b = tf.Variable(tf.constant(0.1, shape=[num_senses]), name="b")
            self.scores = tf.matmul(self.encoder_target_embedding, W) + b
            self.predictions = tf.argmax(self.scores, 1, name="predictions")

        with tf.name_scope('cross_entropy'):
            labels = tf.one_hot(self.label, num_senses)
            self.diff = tf.nn.softmax_cross_entropy_with_logits(labels=labels, logits=self.scores)

        with tf.name_scope('loss'):
            self.loss = tf.reduce_mean(self.diff)

        with tf.name_scope('train'):
            self.train_step = tf.train.AdamOptimizer(opts['learning_rate']).minimize(self.loss)

        with tf.name_scope('accuracy'):
            with tf.name_scope('correct_prediction'):
                correct_prediction = tf.equal(self.predictions, tf.argmax(labels, 1))
            with tf.name_scope('accuracy'):
                self.accuracy = tf.reduce_mean(tf.cast(correct_prediction, tf.float32))

        self.sess.run(tf.global_variables_initializer())

    def disambiguate(self, test_data_iterator):
        pass

    def fit(self, max_steps=1000):

        coord = tf.train.Coordinator()
        enqueue_threads = start_threads(self.enqueue_data, [coord, ])
        threads = tf.train.start_queue_runners(sess=self.sess, coord=coord)
        threads.extend(enqueue_threads)
        try:
            for i in range(max_steps):
                _, loss = self.sess.run([self.train_step, self.loss])
                if i % 100 == 0:
                    print(i, loss)
        except tf.errors.OutOfRangeError:
            print("Done training")
        except KeyboardInterrupt:
            print("Force stop.")
        coord.request_stop()
        coord.join(threads)

    def score(self, test_data_iterator):
        pass




