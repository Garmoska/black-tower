#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Test spacing algorithm on actual problem text."""

import sys
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

from black_tower_lib import load_russian_dictionary, segment_word

# Load dictionary
dictionary = load_russian_dictionary()
print(f"Dictionary loaded: {len(dictionary)} words\n")

# Test cases from actual scenes
test_cases = [
    "атакиеслабыеихилые",
    "каквы",
    "имвообщененужны",
    "Реперьвампридетсядратьсясостражей",
    "Предняядверьоткрываетсявкороткийкоридор",
    "раздваивается",
    "Выпойдетевправыйпроход",
    "иливлевый",
    "Йудавынаправитесь",
    "используязаклятие",
    "Йострову",
    "Надругойберег",
]

for test in test_cases:
    result = segment_word(test, dictionary)
    print(f"Original: {test}")
    print(f"Segmented: {result}")
    print()
