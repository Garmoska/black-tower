#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fix Cyrillic encoding and add missing spaces.
"""

import fitz
import re

def build_complete_cyrillic_map():
    """Build complete Cyrillic character mapping."""
    char_map = {
        # Lowercase
        'Ȉ': 'а',  # U+0208
        'ȉ': 'б',  # U+0209
        'Ȋ': 'в',  # U+020A
        'ș': 'в',  # U+0219 (alternate)
        'ȋ': 'г',  # U+020B
        'Ȍ': 'д',  # U+020C
        'ȍ': 'е',  # U+020D
        'Ȏ': 'ж',  # U+020E
        'ȏ': 'з',  # U+020F
        'Ȑ': 'и',  # U+0210
        'ȑ': 'й',  # U+0211
        'Ȓ': 'к',  # U+0212
        'ȓ': 'л',  # U+0213
        'Ȕ': 'м',  # U+0214
        'ȕ': 'н',  # U+0215
        'Ȗ': 'о',  # U+0216
        'ȗ': 'п',  # U+0217
        'Ș': 'р',  # U+0218
        'ș': 'с',  # U+0219
        'Ț': 'т',  # U+021A
        'ț': 'у',  # U+021B
        'Ȝ': 'ф',  # U+021C
        'ȝ': 'х',  # U+021D
        'Ȟ': 'ц',  # U+021E
        'ȟ': 'ч',  # U+021F
        'Ƞ': 'ш',  # U+0220
        'ȡ': 'щ',  # U+0221
        'Ȣ': 'ъ',  # U+0222
        'ȣ': 'ы',  # U+0223
        'Ȥ': 'ь',  # U+0224
        'ȥ': 'э',  # U+0225
        'Ȧ': 'ю',  # U+0226
        'ȧ': 'я',  # U+0227

        # Uppercase
        'Ǩ': 'А',  # U+01E8
        'ǩ': 'Б',  # U+01E9
        'Ǫ': 'В',  # U+01EA
        'ǫ': 'Г',  # U+01EB
        'Ǭ': 'Д',  # U+01EC
        'ǭ': 'Е',  # U+01ED
        'Ǯ': 'Ж',  # U+01EE
        'ǯ': 'З',  # U+01EF
        'Ǳ': 'И',  # U+01F1
        'ǲ': 'Й',  # U+01F2
        'ǳ': 'К',  # U+01F3
        'Ǵ': 'Л',  # U+01F4
        'ǵ': 'Н',  # U+01F5
        'Ƕ': 'О',  # U+01F6
        'Ƿ': 'О',  # U+01F7
        'Ǹ': 'П',  # U+01F8
        'ǹ': 'П',  # U+01F9
        'Ǻ': 'Р',  # U+01FA
        'ǻ': 'С',  # U+01FB
        'Ǽ': 'Т',  # U+01FC
        'ǽ': 'У',  # U+01FD
        'Ǿ': 'Ф',  # U+01FE
        'ǿ': 'Х',  # U+01FF
        'Ȁ': 'Ц',  # U+0200
        'ȁ': 'Ч',  # U+0201
        'Ȃ': 'Ш',  # U+0202
        'ȃ': 'Щ',  # U+0203
        'Ȅ': 'Ъ',  # U+0204
        'ȅ': 'Ы',  # U+0205
        'Ȇ': 'Ь',  # U+0206
        'ȇ': 'Э',  # U+0207
    }
    return char_map

def fix_text(text, char_map):
    """Apply character mapping to fix text."""
    result = []
    for char in text:
        result.append(char_map.get(char, char))
    return ''.join(result)

def add_spaces(text):
    """
    Add missing spaces to Russian text based on common patterns.
    This is scene-specific manual correction.
    """
    # Known word boundaries for scene 279
    replacements = [
        # Line 2
        ('Егообрамляетзолотаярамасизображениямисцен', 'Его обрамляет золотая рама с изображениями сцен'),
        # Line 4
        ('орнаментомвамнедают', 'орнаментом вам не дают'),
    ]

    result = text
    for old, new in replacements:
        result = result.replace(old, new)

    return result

def add_spaces_automatic(text):
    """
    Attempt to add spaces automatically using common Russian word patterns.
    This is a heuristic approach.
    """
    # Common two-letter words that should be separated
    two_letter = ['не', 'но', 'во', 'на', 'из', 'от', 'до', 'по', 'за', 'со', 'ко']

    # Common three-letter words
    three_letter = ['как', 'это', 'его', 'вам', 'вас', 'все', 'был', 'или', 'там', 'для']

    result = text

    # Try to separate common words (simple pattern matching)
    # This is very basic and won't work for all cases
    for word in two_letter:
        # Add space after these words if followed by a letter
        result = re.sub(f'({word})([а-яА-Я])', r'\1 \2', result)

    for word in three_letter:
        # Add space before these words if preceded by a letter
        result = re.sub(f'([а-яА-Я])({word})([а-яА-Я])', r'\1 \2\3', result)

    return result

def extract_scene(scene_id):
    """Extract specific scene from PDF."""
    doc = fitz.open('black_tower_91.pdf')
    all_text = ""
    for page in doc:
        all_text += page.get_text()
    doc.close()

    lines = all_text.split('\n')
    scene_lines = []
    in_scene = False
    start_idx = -1

    for i, line in enumerate(lines):
        if line.strip() == str(scene_id):
            in_scene = True
            start_idx = i
            continue

        if in_scene:
            if line.strip().isdigit() and len(line.strip()) <= 4 and i > start_idx + 1:
                break
            if line.strip():
                scene_lines.append(line.strip())

    return '\n'.join(scene_lines)

def main():
    print("Extracting scene 279...")
    scene_garbled = extract_scene(279)

    print("Building character map...")
    char_map = build_complete_cyrillic_map()

    print("Fixing encoding...")
    scene_fixed = fix_text(scene_garbled, char_map)

    print("Adding missing spaces...")
    scene_with_spaces = add_spaces(scene_fixed)

    # Also try automatic spacing for remaining issues
    scene_with_spaces = add_spaces_automatic(scene_with_spaces)

    # Save to file
    with open('scene_279_sample.txt', 'w', encoding='utf-8') as f:
        f.write("="*70 + "\n")
        f.write("СЦЕНА 279\n")
        f.write("="*70 + "\n\n")
        f.write(scene_with_spaces)
        f.write("\n\n" + "="*70 + "\n")
        f.write("Проверьте, правильно ли отображается русский текст.\n")
        f.write("Все символы должны читаться корректно.\n")
        f.write("Пробелы добавлены между словами.\n")
        f.write("="*70 + "\n")

    print("\nCreated: scene_279_sample.txt")
    print("\nPreview:")
    print("-" * 70)
    # Print first 3 lines of actual content
    for line in scene_with_spaces.split('\n')[:4]:
        if line.strip():
            # Encode to utf-8 bytes then decode for safe printing
            try:
                print(line)
            except:
                print(line.encode('utf-8', errors='replace').decode('utf-8'))

if __name__ == "__main__":
    main()
