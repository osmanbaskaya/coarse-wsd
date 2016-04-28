from representation import run_word2vec, load_wiki_data, load_model


def run():
    sentences = list(load_wiki_data())
    print "Total {} sentences have been read".format(len(sentences))
    model_id = run_word2vec(list(sentences))
    test_model(model_id)


def test_model(model_id):
    model = load_model(model_id)
    print model


run()
