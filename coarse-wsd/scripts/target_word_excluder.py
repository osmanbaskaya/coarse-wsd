import sys

exclude_set = set(sys.argv[1:])


for word in sys.stdin:
    word = word.strip()
    # Exclude words both in exclude list and very short lengths.
    if word not in exclude_set and len(word) > 2 and not '_' in word:
        print word

