SHELL := /bin/bash
.SECONDARY:

SEED=1
CPU=6
SNLI=../datasets/snli_1.0
JAVA_HOME=/ai/home/obaskaya/java/jdk1.8.0_65/
export PATH:=/ai/home/obaskaya/java/jdk1.8.0_65/bin/:${PATH}

TARGET_WORD_EXCLUDE_LIST=mg new_york old_man fig cm hr bronchial_artery one two c pa tsh carbon_tetrachloride l 0 no 1 radio_emission men bull\'s_eye mm 30_minutes ma business_concern yes ml a los_angeles sense_of_touch m lb kansas_city interior_designer gm
PAGE_EXCLUDE_LIST=album song EP
NUM_OF_FOLD=5
WORD_EMBEDDING_DIM=100


# Machine translation input preprocessing parameters
MT_INPUT_FILE=nmt-input-data.raw.1k-sample.tsv.gz
LOG_LEVEL=debug
MODEL_DIR='../datasets/models'
FRESH_START="--fresh-start"
CHECK_POOL_EVERY=150
WRITE_EVERY_N_LINE=500000

### PATH
CORE_NLP=java -cp "../tools/stanford-corenlp/*" -Xmx60g edu.stanford.nlp.pipeline.StanfordCoreNLP -replaceExtension -cpu ${CPU}

# Project Docker
dockerized: ../dockerized/
	docker build -t ob/coarse-wsd:1 $<

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
target-label-remove: ../datasets/wiki
	python scripts/remove_target_label.py $<

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

# example: make fetch-instances-from-wiki FILENAME=semcor-pages.txt
fetch-instances-from-wiki: ${FILENAME}
	python fetch_instances.py --filename ${FILENAME} --log-level ${LOG_LEVEL} --no-fetching-links --num-process ${CPU}

%-pagetypes.txt: %.txt
	cat $< | cut -f2 | grep -oP "\(.*\)" | sort | uniq -c | sort -rn > $@

# make fetch-instances-from-wiki FILENAME=semcor-pages-filtered.txt CPU=1
%-filtered.txt: %.txt
	echo Input file: `wc $<`
	cat $< | python scripts/wiki_page_excluder.py ${PAGE_EXCLUDE_LIST} > $@
	echo Output file: `wc $@`

create_sense_count_table: ../datasets/wiki semcor-pages-filtered.txt
	python data_stats.py --function $@ --args $^

../datasets/ims: ../datasets/wiki-filtered
	python create_ims_dataset.py $< $@ ${NUM_OF_FOLD} ${CPU}

ims.tw-list.txt: ../datasets/ims
	ls $</fold-1 | grep ".train.xml" | sed 's|.train.xml||g' > $@

# call example: make evaluate.ims CPU=4
evaluate.ims: ims.tw-list.txt ../datasets/ims ../ims/ims_0.9.2.1
	python ims_eval.py $^ ${CPU} 2>&1 | tee $@.out

../ims/ims_0.9.2.1:
	#wget http://www.comp.nus.edu.sg/~nlp/sw/IMS_v0.9.2.1.tar.gz
	wget http://www.comp.nus.edu.sg/~nlp/sw/lib.tar.gz
	-mkdir ../ims
	-mv IMS_v0.9.2.1.tar.gz lib.tar.gz ../ims/
	tar xzvf ../ims/IMS_v0.9.2.1.tar.gz -C ../ims
	tar xzvf ../ims/lib.tar.gz -C $@
	chmod +x $@/*.bash
	cd $@; make
	touch $@

%.key: ../datasets/%
	cat ../datasets/ims/fold-*/*.test.key > $@
	wc $@

calculate_baseline.%: %.key 
	python calculate_baseline.py $<

# wiki-filtered comes from Stanford CoreNLP
../datasets/wiki-senses: ../datasets/wiki-filtered
	python sense_map.py $< $@

run-word2vec: ../datasets/wiki-senses
	python run_word2vec.py $< ${CPU} ${WORD_EMBEDDING_DIM}

wiki-tags.txt: ../datasets/wiki-filtered
	cat $</*.clean.txt | grep -P "\tTrue\t" | cut -f6- | tr '\t' '\n' | sort | uniq -c | sort -nr > $@

wiki-sense-tag-mapping.txt: ../datasets/wiki-filtered blacklist-for-tags.txt
	python -m wiki.__init__ $^ $@

neighbors-%d.txt: wiki-word2vec-%.mdl wiki-sense-tag-mapping.txt
	python neighbors.py $^ ../datasets/wiki-senses $@ drive hat bill branch seed hit left race lot

jaccard_sims.txt: wiki-sense-tag-mapping.txt
	python sense_similarity.py $^ ../datasets/wiki-senses

preprocess-mt-dataset: 
	-mkdir ../datasets/mt
	python preprocess-mt-dataset.py --input-file ${MT_INPUT_FILE} --model-dir ${MODEL_DIR} --directory-to-write ../datasets/mt/data --log-level ${LOG_LEVEL} --write-every-n-line ${WRITE_EVERY_N_LINE}

create-ims-formatted-mt-data:
	python ims_formatted_data_for_mt.py --input-dir ../datasets/mt/data/words --directory-to-write ../datasets/mt/ims-data --log-level ${LOG_LEVEL} --num-of-process ${CPU}

ims-disambiguate:
	python ims-disambiguate.py --input-dir ../datasets/mt/ims-data --directory-to-write ../datasets/mt/ims-output --model-dir ${MODEL_DIR} --num-of-process ${CPU} --log-level ${LOG_LEVEL} ${FRESH_START} --check-pool-every ${CHECK_POOL_EVERY}

merge: 
	python merge.py --input-file ${MT_INPUT_FILE} --wsd-output-dir ../datasets/mt/ims-output-merged --directory-to-write ../datasets/mt/mt-input --log-level ${LOG_LEVEL}

# first: make ../ims/ims_0.9.2.1
# make create-disambiguated-dataset CPU=10 MT_INPUT_FILE=nmt-input-data.raw.1k-sample.tsv.gz
create-disambiguated-dataset: preprocess-mt-dataset create-ims-formatted-mt-data ims-disambiguate merge

create-semantic-class-data:
	python semantic-class-dataset-creator.py
