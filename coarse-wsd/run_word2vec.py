import sys
from representation import run_word2vec, load_wiki_data, load_model


def run():
    input_dir = sys.argv[1]
    num_process = int(sys.argv[2])
    embedding_dim = int(sys.argv[3])
    sentences = list(load_wiki_data(input_dir))
    print "Total {} sentences have been read".format(len(sentences))
    model_id = run_word2vec(list(sentences), size=embedding_dim, window=5, min_count=20, workers=num_process)
    print "Model has been saved as {}".format(model_id)


def test_model(model_id):
    model = load_model(model_id)
    print model


if __name__ == '__main__':
    run()
