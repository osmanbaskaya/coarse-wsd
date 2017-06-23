#### Sprint #3
- Build WSD model by using the same data used to train IMS
- Some statistics about the IMS training dataset.
    - how many target words
    - how many senses for each target word.
    - how many nouns, verbs etc.
    - sense frequency.
- Create coarse-grained dataset to build SCD model. This dataset will be built by using the same data used to train IMS. 
    - either use Wikipedia Taxonomy
    - or Wordnet
- Some filtering to senses.
- Fetch external links for each articles?
- Refactor makefile and scripts: input/output logic.
- using instances fetched #1, train word2vec model and represent each **sense** 
- cluster these sense embeddings.
- tokenization is missing in fetch. Also the same tokenization methodology should be used in Word2Vec training.

### DONE

#### Sprint #2
- Fetch synsets in BabelNet related with the target word, from Wikipedia.
#### Sprint #1
- Read word list provided by David, find synsets and their offset number for each word.
- Find Wikipedia page id for each synset. (Java)
- Extract wiki page of each word and first degree neighbors of each word ("What links here").
- Find all sentence where the target word occurs. This (mostly) unambigious sentence (i.e., only one sense of the word is active in the context) will be the instance of our dataset.
