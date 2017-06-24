from extract import get_wiki_page
import pickle
from collections import OrderedDict, defaultdict as dd
import tabulate
import os

""" This module is related with Semantic Class idea """


def create_page_id_link_mapping_file(files, dir='.'):
    # File format is as follows:
    # PageID<TAB>PageTitle<TAB>PageLink<TAB>WordNet/BabelnetSenseTag
    for target_word_fn in files:
        tw = os.path.basename(target_word_fn).split('.')[0]
        out_fn = os.path.join(os.path.dirname(target_word_fn), "%s.pageid.txt" % tw)
        with open(out_fn) as out_f:
            processed = set()
            for line in open(target_word_fn):
                line = line.strip().split('\t')
                if line[3] == "True":  # use only direct sense - wiki links.
                    sense, url = line[2], line[4]
                    title = url.split('/')[-1]
                    if title not in processed:
                        processed.add(title)
                        if sense.startswith('wn'):
                            print(url)
                            page = get_wiki_page(title)
                            if page is not None:
                                out_f.write("{}\t{}\t{}\t{}\n".format(page.pageid, page.title, page.url, sense))


def get_categories_for_senses(pageid_mapping_files, category_fn, pageid_fn, generality_fn, until_level=5):
    """
    This method finds all categories: level 1 categories (nearest), level 2 categories
    (categories of nearest categories), and so on until `until_level`. If `until_level` is `None`, then if provides
    all categories for all levels for a sense in pageid_mapping file.
    """
    results = dict()

    print("category pageid map is started to create")
    category_map = dd(set)
    with open(category_fn) as input_f:
        for line in input_f:
            parent_category, category = line.strip().split(',')
            category_map[category].add(parent_category)

    print("pageid map is started to create")
    pageid_map = dict()
    with open(pageid_fn) as input_f:
        for line in input_f:
            pageid, title = line.strip().split(',')[:2]
            pageid_map[pageid] = title

    print("generality map is started to create")
    generality_map = dict()
    with open(generality_fn) as input_f:
        for line in input_f:
            pageid, generality_score = line.strip().split(',')
            generality_map[pageid] = generality_score.strip()

    f = open('/tmp/table.txt', 'wt')
    for pageid_mapping_fn in pageid_mapping_files:

        print("processing: %s" % pageid_mapping_fn)
        tw = os.path.basename(pageid_mapping_fn).split('.')[0]
        print("pageid sense map is started to create")
        sense_pageid_map = dict()
        with open(pageid_mapping_fn) as input_f:
            for line in input_f:
                line = line.strip().split('\t')
                page_id, sense = line[0], line[-1]
                sense_pageid_map[sense] = page_id

        results[tw] = []
        for key, val in sense_pageid_map.items():
            generality_result = dd(set)
            level = 0
            already_visited = set()
            # Breadth-first traverse
            current_level = [val]
            while current_level:
                level += 1
                next_level = []
                print("Level is: {}, length is: {}".format(level, len(current_level)))
                for e in current_level:
                    rank = generality_map.get(e, None)
                    if rank is not None:
                        if e not in already_visited:
                            already_visited.add(e)
                            for parent in category_map[e]:
                                # Only add parent's generality rank is lower than current word's rank.
                                parent_generality_rank = generality_map.get(parent, None)
                                if parent_generality_rank is not None:
                                    if parent_generality_rank < rank:
                                        generality_result[rank].add(pageid_map[e])
                                        next_level.append(parent)
                current_level = next_level
            ordered_generality_result = OrderedDict(sorted(generality_result.items()))
            f.write(tabulate.tabulate(ordered_generality_result, headers=ordered_generality_result.keys()))
            f.write('\n\n')
            results[tw].append(generality_result)

    pickle.dump(results, open("generality-result.pkl", 'wb'))

