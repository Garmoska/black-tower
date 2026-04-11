#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import re
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

from black_tower_lib import build_cyrillic_map, fix_encoding, extract_scene_from_pdf

raw_text = extract_scene_from_pdf("black_tower_91.pdf", 105)
char_map = build_cyrillic_map()
fixed_text, _ = fix_encoding(raw_text, char_map)

line = fixed_text.split('\n')[0]
print(f"Line: {line}")
print(f"Length: {len(line)}")
print()

# Check each character
for i, char in enumerate(line[:30]):
    in_range = 'а' <= char.lower() <= 'я' or char.lower() == 'ё'
    print(f"{i:2d}: '{char}' U+{ord(char):04X} in_range={in_range}")

print()
print("Testing regex:")
matches = list(re.finditer(r'[а-яА-ЯёЁ]+', line))
print(f"Found {len(matches)} matches")
for m in matches:
    print(f"  Match: {m.group()} (len={len(m.group())})")
