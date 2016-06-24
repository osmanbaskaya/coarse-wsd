from utils import get_all_files
import codecs
import re


def filter_tags(tags, regex):
    tags = set(tags)
    filtered_tags = []
    for tag in tags:
        if not regex.search(tag):
            filtered_tags.append(tag)
    return filtered_tags


def find_and_write_wiki_tags(directory, excluded_tag_file, output_filename='wiki-sense-tag-mapping.txt'):
    files = get_all_files(directory, "*.clean.txt")
    excluded_tag_set = open(excluded_tag_file).read().splitlines()
    regex = re.compile("|".join(excluded_tag_set), re.I)
    d = dict()
    for i, fn in enumerate(files, 1):
        if i % 10 == 0:
            print "\r%d files read" % i,
        with codecs.open(fn, encoding='utf8') as f:
            for line in f:
                line = line.strip().split('\t')
                is_original_wiki_article_for_sense = line[3]
                sense = line[2]
                if is_original_wiki_article_for_sense and sense not in d:
                    tags = line[5:]
                    filtered_tags = filter_tags(tags, regex)
                    d[sense] = filtered_tags

    print  # it's for previous print trick.

    with codecs.open(output_filename, 'w', encoding='utf8') as f:
        for sense, tags in d.iteritems():
            f.write(u"{}\t{}\n".format(sense, ";".join(tags)))


if __name__ == '__main__':
    import sys
    find_and_write_wiki_tags(*sys.argv[1:])
