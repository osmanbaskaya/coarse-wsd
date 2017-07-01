from preprocess.data.feed_dict_based import read_data, build_vocab
from legacy_disambiguate import NeuralDisambiguator
from utils import configure_logger, get_logger


def run():
    sense_vocab = build_vocab('../datasets/senses.train.txt', num_already_allocated_tokens=0)
    word_vocab = build_vocab('../datasets/sentences.train.txt')

    configure_logger()
    logger = get_logger()

    logger.info("{} {}".format(word_vocab.size, sense_vocab.size))

    train_iter = read_data(word_vocab, sense_vocab, data_path='../datasets/')
    disambiguator = NeuralDisambiguator(hidden_unit_size=25, learning_rate=0.001, num_senses=sense_vocab.size,
                                        vocab_size=word_vocab.size, embedding_length=50)
    disambiguator.fit(train_iter, max_steps=2000)


if __name__ == '__main__':
    run()

