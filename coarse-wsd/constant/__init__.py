MODEL_PATH = '../datasets/models-small'

WORD2VEC_PATH = '../data/embeddings/GoogleNews-vectors-negative300.bin.gz'
WORD2VEC_EMB_DIMENSION = 300

# Tokens
START_TOKEN = "<<START>>"
OOV_TOKEN = "<<PAD>>"
PAD_TOKEN = "<<OOV>>"
END_TOKEN = "<<END>>"

SPECIAL_TOKENS = {PAD_TOKEN: 0, START_TOKEN: 1, OOV_TOKEN: 2, END_TOKEN: 3}
