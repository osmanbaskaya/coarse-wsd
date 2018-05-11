import sys
from utils import get_sense_idx_map
from wiki import get_wiki_tag_and_link_maps


def calculate_jaccard_sim(tags1, tags2):
    size_of_intersect = len(tags1.intersection(tags2))
    size_of_union = len(tags1.union(tags2))
    return float(size_of_intersect) / size_of_union


def calculate_sense_similarity(word, wiki_tag_file, keydict_path, similarity_function='jaccard', threshold=0):
    tag_map, link_map = get_wiki_tag_and_link_maps(wiki_tag_file)
    sense_idx_map = get_sense_idx_map(keydict_path, word)
    for sense1, idx1 in sense_idx_map.iteritems():
        tags1 = set(tag_map[sense1])
        for sense2, idx2 in sense_idx_map.iteritems():
            if sense1 != sense2:
                tags2 = set(tag_map[sense2])
                sim_score = None
                if similarity_function == 'jaccard':
                    sim_score = calculate_jaccard_sim(tags1, tags2)
                if sim_score > threshold:
                    print "{}\t{}-{}\t{}".format(word, sense1, sense2, sim_score)
