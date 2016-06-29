import sys
from wikipedia import get_wiki_tag_and_link_maps
import codecs
from utils import get_sense_idx_map
from representation import load_model
import tabulate

# sense - wiki tags
# sense - idx (in targetword.keydict)
print sys.stdout.encoding


def run():
    model_id = sys.argv[1]
    tag_map, link_map = get_wiki_tag_and_link_maps(sys.argv[2])
    keydict_path = sys.argv[3]
    output_fn = sys.argv[4]
    words = sys.argv[5:]

    model = load_model(model_id)
    number_of_field = 15
    table = [[] for _ in xrange(number_of_field)]
    for word in words:
        sense_idx_map = get_sense_idx_map(keydict_path, word)
        i = 1
        for sense, idx in sense_idx_map.iteritems():
            try:
                similar_words = model.most_similar(positive=[idx], topn=10)
                table[i].extend([u"%s" % t[0] for t in similar_words])
                table[i].append(u",".join(tag_map[sense]))
                table[i].append(u"%s" % link_map[sense])
                i += 1
            except KeyError:
                pass

        for j in xrange(i, number_of_field):
            diff = len(table[1]) - len(table[j])
            for _ in xrange(diff):
                table[j].append("")

        for i in xrange(12):
            if i == 6:
                table[0].append(word)
            else:
                table[0].append("")

        for column in table:
            column.append(" ")

    table_filtered = []
    for column in table:
        if len(column) != 0:
            table_filtered.append(column)

    headers = ["target_word"]
    headers.extend(["sense-%d" % i for i in xrange(1, number_of_field)])

    with codecs.open(output_fn, 'w', 'utf-8') as f:
        t = tabulate.tabulate(zip(*table_filtered), tablefmt="simple", headers=headers)
        f.write(t)


if __name__ == '__main__':
    run()
