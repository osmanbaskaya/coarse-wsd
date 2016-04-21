SHELL := /bin/bash
.SECONDARY:

SEED=1
CPU=20
SNLI=../datasets/snli_1.0
JAVA_HOME=/ai/home/obaskaya/java/jdk1.8.0_65/
export PATH:=/ai/home/obaskaya/java/jdk1.8.0_65/bin/:${PATH}

EXCLUDE_LIST=mg new_york old_man fig cm hr bronchial_artery one two c pa tsh carbon_tetrachloride l 0 no 1 radio_emission men bull\'s_eye mm 30_minutes ma business_concern yes ml a los_angeles sense_of_touch m lb kansas_city interior_designer gm

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

%-filtered.txt: %.txt
	echo Input file: `wc $<`
	cat $< | python scripts/target_word_excluder.py ${EXCLUDE_LIST} > $@
	echo Output file: `wc $@`

extract_synsets: %.txt
	python extract_synsets.py $<

# example: make fetch-instances-from-wiki FILENAME=wikipages.txt
fetch-instances-from-wiki: ${FILENAME}
	python fetch_instances.py --filename ${FILENAME} --log-level info --num-process 6


