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
        key_fn = os.path.join(directory, "%s.key" % fn)
        senses = open(key_fn).read().splitlines()
        sense_map = dict(zip(set(senses), count(1)))
        replaced_instances = []
        for line, sense in izip(codecs.open(f, encoding='utf8'), senses):
            line = line.strip()
            instance = regex.sub(u"{}.{}".format(target_word, sense_map[sense]), line)
            replaced_instances.append(instance)
        with codecs.open(os.path.join(directory_to_write, '%s.txt' % target_word), 'w', encoding='utf8') \
                as out:
            out.write('\n'.join(replaced_instances))
        with open(os.path.join(directory_to_write, "%s.keydict.txt" % target_word), 'w') as keydict_out:
            keydict_out.write("\n".join((["{}\t{}".format(*sense) for sense in sense_map.iteritems()])))
            keydict_out.write('\n')

