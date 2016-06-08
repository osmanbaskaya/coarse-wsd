import os
from itertools import izip, count
import re
import codecs
import utils

LOGGER = None

regex = re.compile(u"<target>\w+<target>")


def sense_mapping(files, directory_to_write):
    global LOGGER

    LOGGER = utils.get_logger()

    try:
        os.mkdir(directory_to_write)
    except OSError:
        LOGGER.debug("{} is already exist".format(directory_to_write))

    for f in files:
        directory, fn = os.path.split(f)
        fn, ext = os.path.splitext(fn)
        target_word = fn.split('.')[0]
        d = dict()
        replaced_sentence = []
        for line in codecs.open(f, encoding='utf8'):
            line = line.strip().split('\t')
            sentence, sense = line[0], line[2]
            sense = sense.replace('wn:', '')  # remove the first wn: part. Just in case for preprocessing options (may remove all punctuations and we can end up)
            sense_id = d.get(sense, None)
            if sense_id is None:
                sense_id = len(d)
                d[sense] = sense_id
            sentence = regex.sub(u"{}.{}".format(target_word, sense_id), sentence)
            replaced_sentence.append(sentence)
        with codecs.open(os.path.join(directory_to_write, '%s.txt' % target_word), 'w', encoding='utf8') \
                as out:
            out.write('\n'.join(replaced_sentence))
        with open(os.path.join(directory_to_write, "%s.keydict.txt" % target_word), 'w') as keyfile:
            keyfile.write("\n".join((["{}\t{}".format(*sense) for sense in d.iteritems()])))
            keyfile.write('\n')




