SHELL := /bin/bash
.SECONDARY:

SEED=1
CPU=6
SNLI=../datasets/snli_1.0
JAVA_HOME=/ai/home/obaskaya/java/jdk1.8.0_65/
export PATH:=/ai/home/obaskaya/java/jdk1.8.0_65/bin/:${PATH}

TARGET_WORD_EXCLUDE_LIST=mg new_york old_man fig cm hr bronchial_artery one two c pa tsh carbon_tetrachloride l 0 no 1 radio_emission men bull\'s_eye mm 30_minutes ma business_concern yes ml a los_angeles sense_of_touch m lb kansas_city interior_designer gm
PAGE_EXCLUDE_LIST=album song EP


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
	cut -f1 $< | sed -re 's|<\w+\.\w\.[0-9]+>||g' -e 's|</\w+\.\w\.[0-9]+>||g' | uniq > ../datasets/wiki-orig/$@

%-filtered.txt: %.txt
	echo Input file: `wc $<`
	cat $< | python scripts/target_word_excluder.py ${TARGET_WORD_EXCLUDE_LIST} > $@
	echo Output file: `wc $@`

extract_synsets: %.txt
	python extract_synsets.py $<

semcor-pages.txt: semcor-synset-info-txt
	#TODO: test it
	javac -cp ../BabelNet-API-3.6/babelnet-api-3.6.jar:../BabelNet-API-3.6/lib/*:../BabelNet-API-3.6/.:../BabelNet-API-3.6/config ../coarse-wsd-java/src/WikipediaDataProvider.java
	java -cp ../BabelNet-API-3.6/babelnet-api-3.6.jar:../BabelNet-API-3.6/lib/*:../BabelNet-API-3.6/.:../BabelNet-API-3.6/config WikipediDataProvider.java $< $@

# example: make fetch-instances-from-wiki FILENAME=wikipages.txt
fetch-instances-from-wiki: ${FILENAME}
	python fetch_instances.py --filename ${FILENAME} --log-level debug --num-process ${CPU}

%-pagetypes.txt: %.txt
	cat $< | cut -f2 | grep -oP "\(.*\)" | sort | uniq -c | sort -rn > $@

# make fetch-instances-from-wiki FILENAME=semcor-pages-filtered.txt CPU=1
%-filtered.txt: %.txt
	echo Input file: `wc $<`
	cat $< | python scripts/wiki_page_excluder.py ${PAGE_EXCLUDE_LIST} > $@
	echo Output file: `wc $@`
