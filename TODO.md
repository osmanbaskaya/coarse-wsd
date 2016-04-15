#### Sprint #3
- using instances fetched #1, train word2vec model and represent each **sense** 
- cluster these sense embeddings.
- tokenization is missing in fetch. Also the same tokenization methodology should be used in Word2Vec training.
- list number of senses for each target word

### DONE
#### Sprint #2
- Fetch synsets in BabelNet related with the target word, from Wikipedia.
#### Sprint #1
- Read word list provided by David, find synsets and their offset number for each word.
- Find Wikipedia page id for each synset. (Java)
- Extract wiki page of each word and first degree neighbors of each word ("What links here").
- Find all sentence where the target word occurs. This (mostly) unambigious sentence (i.e., only one sense of the word is active in the context) will be the instance of our dataset.
