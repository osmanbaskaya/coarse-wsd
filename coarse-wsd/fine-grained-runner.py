from utils import configure_logger, get_logger
from data_loader import DataSet
from disambiguate.model import NeuralDisambiguator


def run():
    configure_logger()
    logger = get_logger()

    dataset = DataSet('../datasets/wiki-new')

    FLAGS = {"embedding_length": 10,
             "min_counts": 10,
             "batch_size": 16,
             "hidden_unit_size": 10,
             "learning_rate": .001}

    disambiguator = NeuralDisambiguator(dataset, FLAGS, use_pretrained_embeddings=False)
    disambiguator.fit(max_steps=2000)


if __name__ == '__main__':
    run()

