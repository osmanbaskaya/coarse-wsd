SHELL := /bin/bash
.SECONDARY:

SEED=1
CPU=20
SNLI=../datasets/snli_1.0
JAVA_HOME=/ai/home/obaskaya/java/jdk1.8.0_65/
export PATH:=/ai/home/obaskaya/java/jdk1.8.0_65/bin/:${PATH}

### PATH
CORE_NLP=java -cp "../tools/stanford-corenlp/*" -Xmx60g edu.stanford.nlp.pipeline.StanfordCoreNLP -replaceExtension -cpu ${CPU}

# make pos-snli-train.txt
corenlp-%.out: %.txt
	#tail -n +1 ${SNLI}/$< | cut -f6 > $@  # sentence 1
	#tail -n +1 ${SNLI}/$< | cut -f7 >> $@ # sentence 2
	${CORE_NLP} -annotators tokenize,ssplit,pos,lemma -file $<
	mv $*.out $@

%.filtered.gz: corenlp-%.out
	cat $< | grep -P "lemma|<POS>" | gzip > $@

# Create original version of the instances fetched from Wikipedia.
# Call example: laptop.original.txt
%.original.txt: ../datasets/wiki/%.txt
	cat $< | sed -re 's|<\w+\.\w\.[0-9]+>||g' -e 's|</\w+\.\w\.[0-9]+>||g' > ../datasets/wiki/$@
