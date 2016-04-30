import sys
import codecs
import re
import os

wiki_dir = sys.argv[1]

regex = re.compile('<target>')


# get all target words.
words = set(fn.split('.', 1)[0] for fn in os.listdir(wiki_dir))
print "{} words will be processed.".format(len(words))

for word in words:
    fn = os.path.join(wiki_dir, "%s.txt" % word)
    out = os.path.join(wiki_dir, "%s.orig.txt" % word)
    print "{} --> {}".format(fn, out)
    sentences = []
    with codecs.open(out, 'w', encoding='utf8') as f:
        for line in codecs.open(fn, encoding='utf8'):
            line = line.split('\t')
            line[0] = regex.sub('', line[0])
            sentences.append('\t'.join(line))
        f.writelines(sentences)
print "All done."


