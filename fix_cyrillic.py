#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fix Cyrillic encoding by mapping garbled characters to proper Cyrillic.
"""

import fitz

# Complete character mapping from garbled to Cyrillic
# Built by analyzing the pattern of incorrect encoding
CYRILLIC_MAP = {
    # Uppercase
    'Ǩ': 'А', 'ǩ': 'Б', 'Ǫ': 'В', 'Ǭ': 'Г', 'ǭ': 'Д', 'Ǯ': 'Е',
    'Ǭ': 'Д', 'ǭ': 'Е', 'Ǯ': 'Ж', 'ǯ': 'З', 'ǰ': 'И', 'Ǳ': 'Й',
    'ǲ': 'К', 'Ǵ': 'Л', 'ǵ': 'М', 'Ƕ': 'Н', 'Ƿ': 'П', 'Ǹ': 'Р',
    'ǹ': 'С', 'Ǻ': 'Т', 'Ǽ': 'У', 'Ǿ': 'Ф', 'Ȁ': 'Х', 'Ȃ': 'Ц',
    'Ȅ': 'Ч', 'Ȇ': 'Ш', 'Ȉ': 'Щ', 'Ȋ': 'Ъ', 'Ȍ': 'Ы', 'Ȏ': 'Ь',
    'Ȑ': 'Э', 'Ȓ': 'Ю', 'Ȕ': 'Я',

    # Lowercase
    'ȕ': 'а', 'ȗ': 'б', 'ș': 'в', 'ț': 'г', 'ȝ': 'д', 'ȟ': 'е',
    'ȡ': 'ж', 'ȣ': 'з', 'ȥ': 'и', 'ȧ': 'й', 'ȩ': 'к', 'ȫ': 'л',
    'ȭ': 'м', 'ȯ': 'н', 'ȱ': 'о', 'ȳ': 'п', 'ȵ': 'р', 'ȷ': 'с',
    'ȹ': 'т', 'Ȼ': 'у', 'Ƚ': 'ф', 'ȿ': 'х', 'ɀ': 'ц', 'Ɂ': 'ч',
    'ɂ': 'ш', 'Ƀ': 'щ', 'Ʉ': 'ъ', 'Ʌ': 'ы', 'Ɇ': 'ь', 'ɇ': 'э',
    'Ɉ': 'ю', 'Ɋ': 'я',
}

# Try another approach: the characters we see suggest CP1251 bytes shown as Unicode
# Let's build the map from what we observe
OBSERVED_MAP = {}

def build_cp1251_map():
    """Build mapping from garbled Unicode to proper Cyrillic."""
    # CP1251 Cyrillic characters (hex 0xC0-0xFF map to А-Я, а-я)
    # When these bytes are incorrectly decoded, they appear as Latin Extended

    cyrillic_upper = 'АБВГДЕЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ'
    cyrillic_lower = 'абвгдежзийклмнопрстуфхцчшщъыьэюя'

    # Build map by encoding Cyrillic as cp1251, then decoding as different encoding
    mapping = {}

    # Try to reverse engineer the transformation
    for i, char in enumerate(cyrillic_upper):
        try:
            # Encode as cp1251 (this gives the byte value)
            byte_val = char.encode('cp1251')
            # Decode as latin1 (treat byte as unicode code point)
            garbled = byte_val.decode('latin1')
            mapping[garbled] = char
        except:
            pass

    for i, char in enumerate(cyrillic_lower):
        try:
            byte_val = char.encode('cp1251')
            garbled = byte_val.decode('latin1')
            mapping[garbled] = char
        except:
            pass

    return mapping

def fix_text(text: str) -> str:
    """Fix garbled Cyrillic text."""
    # Build the character map
    char_map = build_cp1251_map()

    # Replace each garbled character with proper Cyrillic
    result = []
    for char in text:
        if char in char_map:
            result.append(char_map[char])
        else:
            result.append(char)

    return ''.join(result)

def extract_scene_279():
    """Extract and fix scene 279."""
    doc = fitz.open('black_tower_91.pdf')
    page = doc[48]
    text = page.get_text()
    doc.close()

    lines = text.split('\n')
    scene_lines = []
    in_scene = False

    for line in lines:
        line = line.strip()
        if line == '279':
            in_scene = True
            scene_lines.append(line)
            continue
        if in_scene and line == '280':
            break
        if in_scene and line:
            scene_lines.append(line)

    scene_text = '\n'.join(scene_lines)
    return scene_text

def main():
    print("Extracting scene 279...")
    scene_garbled = extract_scene_279()

    print("Fixing encoding...")
    scene_fixed = fix_text(scene_garbled)

    # Save fixed version
    with open('scene_279_sample.txt', 'w', encoding='utf-8') as f:
        f.write("СЦЕНА 279\n")
        f.write("="*50 + "\n\n")
        f.write(scene_fixed)
        f.write("\n\n" + "="*50)
        f.write("\nПроверьте, правильно ли отображается текст.")

    print("\n✓ Saved to: scene_279_sample.txt")
    print("\nPreview:")
    print("-" * 50)
    print(scene_fixed[:200])
    print("-" * 50)

if __name__ == "__main__":
    main()
