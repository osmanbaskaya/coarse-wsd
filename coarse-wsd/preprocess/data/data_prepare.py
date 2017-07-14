"""
This module helps to convert wikipedia dataset into the dataset that Neural WSD needs. Neural WSD expects input data
should be as follow:

<SENTENCE> <TAB> <LABEL/SENSE> <TAB> <TARGET_WORD_INDEX>
"""

import os
import re
import spacy
from data_loader import fopen

REGEX = re.compile("<target>(\w+)(\W*)<target>")
NLP = spacy.en.English()
SENTENCE_BOUNDARY_MARKERS = {'.', '?', '!'}

def convert_files_into_proper_format(files, output_dir):

    num_file = len(files)
    for i, fn in enumerate(files, 1):
        basename = os.path.basename(fn)
        print("{}/{}. {} is processing".format(i, num_file, basename))
        with open(os.path.join(output_dir, basename), 'wt'):
            for line in fopen(fn):
                line = line.strip().split('\t')
                sentence = line[0]
                match = REGEX.search(sentence)
                start, end = match.span()
                sentence = "{}<target>{}</target>{}{}".format(sentence[:start], match.group(1), match.group(2),
                                                               sentence[end:])









