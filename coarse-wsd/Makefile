SHELL := /bin/bash
.SECONDARY:

SEED=1
CPU=7
SNLI=../datasets/snli_1.0

### PATH
CORE_NLP=java -cp "../tools/stanford-corenlp/*" -Xmx6g edu.stanford.nlp.pipeline.StanfordCoreNLP -replaceExtension -cpu ${CPU}

# make pos-snli-train.txt
pos-snli-%.txt:
	tail -n +1 ${SNLI}/snli_1.0_$*.txt | cut -f6 > $@  # sentence 1
	tail -n +1 ${SNLI}/snli_1.0_$*.txt | cut -f7 >> $@ # sentence 2
	${CORE_NLP} -annotators tokenize,ssplit,pos,lemma -file $@
