#!/usr/bin/env python3
import sys
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

from black_tower_lib import load_russian_dictionary

dictionary = load_russian_dictionary()

# Check which words are missing
test_words = ['куда', 'используя', 'кострову', 'острову']

for word in test_words:
    if word.lower() in dictionary:
        print(f"✓ {word} - in dictionary")
    else:
        print(f"✗ {word} - MISSING")
