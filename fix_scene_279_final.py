#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fix scene 279 with proper spacing - manual correction.
"""

import fitz

def build_complete_cyrillic_map():
    """Build complete Cyrillic character mapping."""
    char_map = {
        # Lowercase
        'Ȉ': 'а', 'ȉ': 'б', 'Ȋ': 'в', 'ș': 'в', 'ȋ': 'г', 'Ȍ': 'д',
        'ȍ': 'е', 'Ȏ': 'ж', 'ȏ': 'з', 'Ȑ': 'и', 'ȑ': 'й', 'Ȓ': 'к',
        'ȓ': 'л', 'Ȕ': 'м', 'ȕ': 'н', 'Ȗ': 'о', 'ȗ': 'п', 'Ș': 'р',
        'ș': 'с', 'Ț': 'т', 'ț': 'у', 'Ȝ': 'ф', 'ȝ': 'х', 'Ȟ': 'ц',
        'ȟ': 'ч', 'Ƞ': 'ш', 'ȡ': 'щ', 'Ȣ': 'ъ', 'ȣ': 'ы', 'Ȥ': 'ь',
        'ȥ': 'э', 'Ȧ': 'ю', 'ȧ': 'я',
        # Uppercase
        'Ǩ': 'А', 'ǩ': 'Б', 'Ǫ': 'В', 'ǫ': 'Г', 'Ǭ': 'Д', 'ǭ': 'Е',
        'Ǯ': 'Ж', 'ǯ': 'З', 'Ǳ': 'И', 'ǲ': 'Й', 'ǳ': 'К', 'Ǵ': 'Л',
        'ǵ': 'Н', 'Ƕ': 'О', 'Ƿ': 'О', 'Ǹ': 'П', 'ǹ': 'П', 'Ǻ': 'Р',
        'ǻ': 'С', 'Ǽ': 'Т', 'ǽ': 'У', 'Ǿ': 'Ф', 'ǿ': 'Х', 'Ȁ': 'Ц',
        'ȁ': 'Ч', 'Ȃ': 'Ш', 'ȃ': 'Щ', 'Ȅ': 'Ъ', 'ȅ': 'Ы', 'Ȇ': 'Ь',
        'ȇ': 'Э',
    }
    return char_map

def fix_text(text, char_map):
    """Apply character mapping."""
    return ''.join(char_map.get(c, c) for c in text)

def extract_scene(scene_id):
    """Extract scene from PDF."""
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
    # Extract and fix encoding
    scene_garbled = extract_scene(279)
    char_map = build_complete_cyrillic_map()
    scene_fixed = fix_text(scene_garbled, char_map)

    # Manual spacing corrections for scene 279
    # Original (no spaces): "Егообрамляетзолотаярамасизображениямисцен"
    # Correct: "Его обрамляет золотая рама с изображениями сцен"

    scene_corrected = scene_fixed.replace(
        'Егообрамляетзолотаярамасизображениямисцен',
        'Его обрамляет золотая рама с изображениями сцен'
    )

    # Original: "орнаментомвамнедают"
    # Correct: "орнаментом вам не дают"
    scene_corrected = scene_corrected.replace(
        'орнаментомвамнедают',
        'орнаментом вам не дают'
    )

    # Save to file
    with open('scene_279_sample.txt', 'w', encoding='utf-8') as f:
        f.write("="*70 + "\n")
        f.write("СЦЕНА 279\n")
        f.write("="*70 + "\n\n")
        f.write(scene_corrected)
        f.write("\n\n" + "="*70 + "\n")
        f.write("Проверьте, правильно ли отображается русский текст.\n")
        f.write("Все символы должны читаться корректно.\n")
        f.write("Пробелы добавлены в нужных местах.\n")
        f.write("="*70 + "\n")

if __name__ == "__main__":
    main()
