import sys
from wikipedia import get_wiki_tag_and_link_maps
from utils import get_sense_idx_map
from representation import load_model

# sense - wiki tags
# sense - idx (in targetword.keydict)


def run():
    model_id = sys.argv[1]
    keydict_path = sys.argv[2]
    tag_map, link_map = get_wiki_tag_and_link_maps(sys.argv[3])
    words = sys.argv[4:]

    model = load_model(model_id)
    for word in words:
        sense_idx_map = get_sense_idx_map(keydict_path, word)
        for sense, idx in sense_idx_map.iteritems():
            try:
                similar_words = model.most_similar(positive=[idx], topn=10)
                print '\n'.join(u'%s\t%f' % (word, sim) for word, sim in similar_words), '\n', \
                    tag_map[sense], '\n', link_map[sense]
                print
            except KeyError:
                pass


if __name__ == '__main__':
    run()
