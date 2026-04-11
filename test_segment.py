#!/usr/bin/env python3
import sys
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

from black_tower_lib import load_russian_dictionary, segment_word

dictionary = load_russian_dictionary()

# Test specific words
test_words = [
    "Кудавынаправитесь",
    "используязаклятие",
    "Надругойберег",
    "Кострову",
]

for word in test_words:
    result = segment_word(word, dictionary)
    print(f"{word:25s} → {result}")

# Check if "куда" is in dict
print(f"\n'куда' in dict: {'куда' in dictionary}")
print(f"'используя' in dict: {'используя' in dictionary}")
print(f"'кострову' in dict: {'кострову' in dictionary}")
print(f"'к' in dict: {'к' in dictionary}")
print(f"'у' in dict: {'у' in dictionary}")
print(f"'да' in dict: {'да' in dictionary}")
