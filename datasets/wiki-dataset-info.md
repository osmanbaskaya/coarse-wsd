### Wikipedia Dataset Information 
------

There are two types of files.

- target_word.tw.txt
- target_word.txt

In `target_word.tw.txt` file, all occurrences of a target word are replaced with lemma form (i.e., target_word). On the other hand, `target_word.txt`, original form of the token are kept. In both files, all occurrences of a target_word are surrended by `<target>` tag.

In both files, columns are separated with eachother with \t and organized as follows:


`Sentence` `POS_Tag` `Sense_Offset` `Does_Sentence_Belong_to_the_Main_Article_Page?` `URL_of_the_Page Categories(All are tab separated and varying size)`

#### Some info about non-trivial columns

- `Does_Sentence_Belong_to_the_Main_Article_Page?`: `True` indicates that this sentence is fetched from main article of the target_word. In other words, this article page url is provided by BabelNet. `False` indicates that this sentence comes from `What Links Here` page of the target word.

- `Categories`: These are the categories to which Wikipedia users assigned. They contains space that is why categories are separated by \t, as well. Also, it seems that although some categories are not seen in Browser, Wikipedia API provides all. These missing categories are mostly irrelevant for an end user and we need not to consider most of them (and need to find a way to avoid them).


#### How to get the original content of each sentence? 

In order to get the original content of each sentence, there is a target in the Makefile called `target-label-remove`.

```bash
cd coarse-wsd  # the directory where the Makefile exists.
make target-label-remove
```


