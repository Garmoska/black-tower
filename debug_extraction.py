#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Debug why spacing isn't working."""

import sys
import re
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

from black_tower_lib import (
    build_cyrillic_map,
    fix_encoding,
    load_russian_dictionary,
    fix_spacing,
    extract_scene_from_pdf,
    segment_word
)

# Extract scene 105
pdf_path = "black_tower_91.pdf"
scene_id = 105

print(f"Extracting scene {scene_id}...\n")
raw_text = extract_scene_from_pdf(pdf_path, scene_id)
print("=== RAW TEXT ===")
print(raw_text)
print()

char_map = build_cyrillic_map()
fixed_text, unmapped = fix_encoding(raw_text, char_map)
print("=== AFTER ENCODING FIX ===")
print(fixed_text)
print()

# Check each line
lines = fixed_text.split('\n')
for line in lines:
    if line.strip():
        print(f"Line: {line}")
        # Find Cyrillic chunks
        for match in re.finditer(r'[а-яА-ЯёЁ]+', line):
            word = match.group()
            if len(word) > 12:
                print(f"  Long word ({len(word)} chars): {word}")

print()
dictionary = load_russian_dictionary()
spaced_text = fix_spacing(fixed_text, dictionary)
print("=== AFTER SPACING FIX ===")
print(spaced_text)
