import wikipedia

""" This module is related with Semantic Class idea """


def create_page_id_link_mapping_file(target_word_fn):
    # File format is as follows:
    # PageID<TAB>PageTitle<TAB>PageLink<TAB>WordNet/BabelnetSenseTag
    processed = set()
    for line in open(target_word_fn):
        line = line.strip().split('\t')
        sense, url = line[2], line[4]
        if url not in processed:
            if sense.startswith('wn'):
                page = wikipedia.page(url)
                print(page.pageid, page.title)
                processed.add(url)


def get_categories_for_senses(pageid_mapping_fn, category_fn, until_level=None):
    """
    This method finds all categories: level 1 categories (nearest), level 2 categories
    (categories of nearest categories), and so on until `until_level`. If `until_level` is `None`, then if provides
    all categories for all levels for a sense in pageid_mapping file.
    """
    pass


