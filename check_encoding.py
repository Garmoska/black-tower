#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Check encoding of problematic characters."""

import sys
import fitz

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Extract scene 105 raw
doc = fitz.open('black_tower_91.pdf')
all_text = ""
for page_num in range(7, len(doc)):
    all_text += doc[page_num].get_text()
doc.close()

lines = all_text.split('\n')
in_scene = False
for i, line in enumerate(lines):
    if line.strip() == '105':
        in_scene = True
        print("Found scene 105:")
        continue
    if in_scene:
        if line.strip().isdigit() and len(line.strip()) <= 3:
            break
        if line.strip():
            print(f"Raw: {repr(line.strip())}")
            for char in line.strip()[:20]:
                if ord(char) > 127:
                    print(f"  '{char}' = U+{ord(char):04X}")
