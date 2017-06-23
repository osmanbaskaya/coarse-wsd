from __future__ import print_function
import re
import sys
import codecs

input_fn = sys.argv[1]

REGEX = re.compile("(\w+)\.([wb]n:\d+\w)")

with codecs.open('wsd-input.tsv', 'wt', encoding='latin1') as out:
    for i, line in enumerate(codecs.open(input_fn, encoding='latin1'), 1):
        line = line.strip().replace('\n', '')
        line = line.split('\t')[0]
        word_line = REGEX.sub(r'\1', line)
        sense_line = REGEX.sub(r'\2', line)
        out.write(u"{}\t{}\n".format(word_line, sense_line))

