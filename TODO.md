#### Sprint #3
- Build WSD model by using the same data used to train IMS
- Some statistics about the IMS training dataset.
    - how many target words
    - how many senses for each target word.
    - how many nouns, verbs etc.
    - sense frequency.
- Create coarse-grained dataset to build SCD model. This dataset will be built by using the same data used to train IMS. 
    - either use Wikipedia Taxonomy
        - This might be more difficult than what I expected. We didn't fetch sentences from only one wiki pages. Multiple pages mean multiple categories to decide. We're still able to find common category using these all categories related with one sense. Let's write a script that finds all the categories from nearest to farest, for a specific sense. Then, another script finds 25 categories to cover all senses. We have two optimization constraints: (1) Number of categories should be as small as possible. (2) These categories are enough to distinguish all senses. If we use all the senses as semantic classes, then first constraint is ignored. If we use only one category, we cannot distinguish all senses which means the second constraint is ignored.
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
