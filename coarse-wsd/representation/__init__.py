from gensim.models import Word2Vec
import time
import os
import codecs


def load_wiki_data(directory='../datasets/wikisenses/'):
    files = filter(lambda f: 'keydict' not in f,  os.listdir(directory))
    for f in files:
        for line in codecs.open(os.path.join(directory, f), encoding='utf8'):
            yield line.split()


def run_word2vec(sentences, size=100, window=5, min_count=20, workers=10):
    model = Word2Vec(sentences, size=size, window=window, min_count=min_count, workers=workers)
    model_id = "wiki-word2vec-{}.mdl".format(time.time())
    model.save(model_id)
    return model_id


def load_model(model_id):
    return Word2Vec.load(model_id)
