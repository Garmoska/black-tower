#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Complete Cyrillic fix using the discovered mapping pattern.

Pattern discovered:
- Lowercase а-я: U+0208-U+0227 range
- Uppercase А-Я: U+01E8-U+0207 range
"""

import fitz

def build_complete_cyrillic_map():
    """Build complete Cyrillic character mapping."""

    # Confirmed mappings from analysis
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
        'Ǳ': 'И',  # U+01F1 (treating as single char)
        'ǲ': 'Й',  # U+01F2
        'ǳ': 'К',  # U+01F3
        'Ǵ': 'Л',  # U+01F4
        'ǵ': 'Н',  # U+01F5 (fixed: Н not М)
        'Ƕ': 'О',  # U+01F6
        'Ƿ': 'О',  # U+01F7
        'Ǹ': 'П',  # U+01F8
        'Ǹ': 'О',  # U+01F8
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
        # Special cases
        'Ј': 'Ю',  # might be needed
        'Љ': 'Я',  # might be needed
    }

    return char_map

def fix_text(text, char_map):
    """Apply character mapping to fix text."""
    result = []
    unmapped = []

    for char in text:
        if char in char_map:
            result.append(char_map[char])
        else:
            result.append(char)
            # Track unmapped Cyrillic-range characters
            if 0x01E8 <= ord(char) <= 0x0227 or 0x0180 <= ord(char) <= 0x024F:
                unmapped.append((char, ord(char)))

    return ''.join(result), unmapped

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

    # Find scene
    for i, line in enumerate(lines):
        if line.strip() == str(scene_id):
            in_scene = True
            start_idx = i
            continue

        if in_scene:
            # Stop at next scene number
            if line.strip().isdigit() and len(line.strip()) <= 4 and i > start_idx + 1:
                break
            if line.strip():
                scene_lines.append(line.strip())

    return '\n'.join(scene_lines)

def main():
    print("Building complete character map...")
    char_map = build_complete_cyrillic_map()
    print(f"Character map size: {len(char_map)} characters")

    print("Extracting scene 279...")
    scene_text = extract_scene(279)

    print("Applying fix...")
    fixed_text, unmapped = fix_text(scene_text, char_map)

    # Save fixed scene
    with open('scene_279_sample.txt', 'w', encoding='utf-8') as f:
        f.write("="*70 + "\n")
        f.write("СЦЕНА 279\n")
        f.write("="*70 + "\n\n")
        f.write(fixed_text)
        f.write("\n\n" + "="*70 + "\n")
        f.write("Проверьте, правильно ли отображается русский текст.\n")
        f.write("Все символы должны читаться корректно.\n")
        f.write("="*70 + "\n")

        if unmapped:
            f.write("\n\nНеопознанные символы:\n")
            for char, code in unmapped:
                f.write(f"  '{char}' (U+{code:04X})\n")

    print(f"\nСоздан файл: scene_279_sample.txt")
    print(f"Неопознанных символов: {len(set(unmapped))}")

    if unmapped:
        print("\nНеопознанные символы:")
        for char, code in set(unmapped):
            print(f"  '{char}' (U+{code:04X})")

if __name__ == "__main__":
    main()
