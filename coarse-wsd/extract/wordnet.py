from nltk.corpus import wordnet as wn
import logging


LOGGER = logging.getLogger(__name__)


class WordNetExtractor(object):

    def __init__(self):
        pass

    def fetch_offset_numbers(self, filename):
        # file format: word1\nword2\n
        LOGGER.info("Reading %s", filename)
        f = open('../coarse-wsd-java/synset-info.txt', 'w')
        for word in open(filename):
            word = word.strip()
            try:
                synsets = wn.synsets(word)
            except Exception as e:
                LOGGER.error("Synsets of %s cannot be found. Skipping. %s", word, e.message)
                continue

            for synset in synsets:
                s = "{}\t{}\t{}\twn:{:08d}{}\t{}\t{}\n".format(word, synset.offset(), synset.pos(), synset.offset(),
                                                           synset.pos(), sum(lemma.count() for lemma in synset.lemmas()),
                                                               synset.definition())
                f.write(s)

        LOGGER.info("Writing %s", f.name)
        f.close()

