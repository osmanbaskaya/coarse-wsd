import sys
import re

exclude_set = set(sys.argv[1:])

regex = re.compile("_\((.*)\)")


for line in sys.stdin:
    tokens = line.strip().split('\t')
    match = regex.search(tokens[1])
    if match is not None:
        if any(map(lambda exclude_word: exclude_word in match.group(1), exclude_set)):
            continue
    print line,
