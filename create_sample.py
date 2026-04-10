#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Create sample scene with fixed Cyrillic using manual character map.
"""

import fitz

# Complete character mapping built from observation
# These map the garbled Latin Extended-B characters to Cyrillic
CHAR_MAP = {
    # Uppercase Cyrillic
    'Ǩ': 'А', 'ǩ': 'Б', 'Ǫ': 'В', 'Ǭ': 'Г', 'ǭ': 'Д', 'Ǯ': 'Е',
    'Ǯ': 'Ж', 'ǯ': 'З', 'Ǳ': 'И', 'ǲ': 'К', 'Ǵ': 'Л', 'ǵ': 'М',
    'Ƕ': 'Н', 'Ƿ': 'П', 'Ǹ': 'Р', 'ǹ': 'С', 'Ǻ': 'Т', 'Ǽ': 'У',
    'Ǿ': 'Ф', 'Ȁ': 'Х', 'Ȃ': 'Ц', 'Ȅ': 'Ч', 'Ȇ': 'Ш', 'Ȉ': 'Щ',
    'Ȋ': 'Ъ', 'Ȍ': 'Ы', 'Ȏ': 'Ь', 'Ȑ': 'Э', 'Ȓ': 'Ю', 'Ȕ': 'Я',

    # Lowercase Cyrillic
    'ȕ': 'а', 'ȗ': 'б', 'ș': 'в', 'ț': 'г', 'ȝ': 'д', 'ȟ': 'е',
    'ȡ': 'ж', 'ȣ': 'з', 'ȥ': 'и', 'ȧ': 'й', 'ȩ': 'к', 'ȫ': 'л',
    'ȭ': 'м', 'ȯ': 'н', 'ȱ': 'о', 'ȳ': 'п', 'ȵ': 'р', 'ȷ': 'с',
    'ȹ': 'т', 'Ȼ': 'у', 'Ƚ': 'ф', 'ȿ': 'х', 'ɀ': 'ц', 'Ɂ': 'ч',
    'ɂ': 'ш', 'Ƀ': 'щ', 'Ʉ': 'ъ', 'Ʌ': 'ы', 'Ɇ': 'ь', 'ɇ': 'э',
    'Ɉ': 'ю', 'Ɋ': 'я',

    # Additional characters observed
    'Ș': 'Р', 'Ț': 'Т', 'Ȥ': 'Ь',
    'Ȉ': 'А', 'Ȓ': 'К', 'Ȑ': 'И', 'Ȗ': 'О', 'ȍ': 'е',
    'Ȍ': 'Д', 'ȏ': 'з', 'ȑ': 'й', 'ț': 'у', 'ȟ': 'ч',
    'ȓ': 'л', 'Ȕ': 'М', 'ș': 'с', 'ȗ': 'п', 'ȧ': 'я',
    'ȋ': 'г', 'ȉ': 'б', 'Ȏ': 'Ж', 'Ȣ': 'Ы', 'ȣ': 'ы',
    'ȝ': 'х', 'ǭ': 'Е', 'ǵ': 'Н', 'Ƕ': 'О',
}

# Windows-1251 based mapping (more complete)
def build_win1251_map():
    """Build a complete mapping from Windows-1251 encoding perspective."""
    mapping = {}

    # The pattern is: CP1251 bytes decoded as Latin1 (ISO-8859-1)
    # Russian А-Я are bytes 0xC0-0xFF in CP1251
    # When decoded as Latin1, these become U+00C0-U+00FF (Latin-1 Supplement)
    # But we're seeing Latin Extended-B (U+01xx, U+02xx)

    # It seems the PDF has a different encoding issue
    # Let's try: the bytes are CP1251, but interpreted as MacRoman or similar

    # Manual mapping based on observation:
    # Looking at "Вы" -> "Ǫȣ"
    # В (0xC2 in CP1251) -> Ǫ (U+01EA)
    # ы (0xFB in CP1251) -> ȣ (U+0223)

    cyrillic = (
        'АБВГДЕЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯабвгдежзийклмнопрстуфхцчшщъыьэюя'
    )

    # Try encoding each Cyrillic character and seeing what we get
    for char in cyrillic:
        try:
            # Get CP1251 byte value
            cp1251_byte = char.encode('cp1251')
            # The PDF seems to be treating these bytes as something else
            # Try MacCyrillic or other encodings
            # For now, use our manual map
            pass
        except:
            pass

    # Combine manual observations
    manual_map = {
        'Ǫ': 'В', 'ȣ': 'ы', 'ȗ': 'п', 'Ȗ': 'о', 'Ȍ': 'д',
        'ȝ': 'х', 'Ȑ': 'и', 'Ț': 'т', 'ȍ': 'е', 'Ȓ': 'к',
        'ȏ': 'з', 'Ș': 'р', 'Ȉ': 'а', 'ț': 'у', 'ȕ': 'н',
        'ȟ': 'ч', 'ȋ': 'г', 'ȉ': 'б', 'ȓ': 'л', 'ȧ': 'я',
        'Ȕ': 'м', 'ș': 'с', 'Ȏ': 'ж', 'ȑ': 'й', 'Ȥ': 'ь',
        'ǭ': 'Е', 'ǵ': 'Н', 'Ƕ': 'О', 'Ȋ': 'в', 'ǯ': 'З',
        'ǲ': 'К', 'Ǹ': 'Р', 'ǹ': 'С', 'Ǵ': 'Л', 'Ǩ': 'А',
        'ǩ': 'Б', 'Ǿ': 'Ф', 'Ȁ': 'Х', 'ț': 'у', 'Ǫ': 'В',
        'Ǽ': 'У', 'Ȧ': 'Ц', 'ȡ': 'ж', 'Ƿ': 'П', 'Ǻ': 'Т',
        'ȕ': 'а', 'ȭ': 'м', 'ȫ': 'л', 'ȱ': 'о', 'ț': 'г',
        'ȥ': 'и', 'Ȅ': 'Ч', 'ȝ': 'д', 'ȷ': 'с', 'Ǭ': 'Г',
        'Ɇ': 'ь', 'Ȉ': 'Щ', 'ț': 'г', 'ȷ': 'с', 'Ȧ': 'ц',
        'Ȑ': 'Э', 'ȓ': 'л', 'Ȓ': 'Ю', 'ț': 'г', 'Ȣ': 'Ы',
        'ȣ': 'з', 'Ȍ': 'Ы', 'ȍ': 'е', 'ț': 'г', 'ȝ': 'д',
        'ț': 'у', 'Ƚ': 'ф', 'Ʌ': 'ы', 'Ȋ': 'Ъ', 'Ȏ': 'Ь',
        'Ɉ': 'ю', 'Ɋ': 'я', 'Ƀ': 'щ', 'Ʉ': 'ъ', 'ɇ': 'э',
        'ɀ': 'ц', 'Ɂ': 'ч', 'ɂ': 'ш', 'Ȼ': 'у', 'ȹ': 'т',
        'ȯ': 'н', 'ȩ': 'к', 'Ȇ': 'Ш', 'Ȃ': 'Ц', 'ȧ': 'я',
    }

    # Remove duplicates, keep last
    for k, v in manual_map.items():
        mapping[k] = v

    return mapping

def fix_text(text):
    """Fix garbled Cyrillic text."""
    char_map = build_win1251_map()

    result = []
    unmapped = set()

    for char in text:
        if char in char_map:
            result.append(char_map[char])
        else:
            result.append(char)
            if ord(char) > 127:  # Non-ASCII
                unmapped.add(f"{char} (U+{ord(char):04X})")

    fixed = ''.join(result)

    return fixed, unmapped

def extract_scene(scene_id):
    """Extract specific scene from PDF."""
    doc = fitz.open('black_tower_91.pdf')

    all_text = ""
    for page in doc:
        all_text += page.get_text() + "\n"

    doc.close()

    lines = all_text.split('\n')
    scene_lines = []
    in_scene = False

    for line in lines:
        line = line.strip()

        if line == str(scene_id):
            in_scene = True
            continue

        # Stop at next scene number
        if in_scene and line.isdigit() and len(line) <= 4:
            break

        if in_scene and line:
            scene_lines.append(line)

    return '\n'.join(scene_lines)

def main():
    # Extract scene 279
    scene_garbled = extract_scene(279)

    # Fix encoding
    scene_fixed, unmapped = fix_text(scene_garbled)

    # Save to file
    with open('scene_279_sample.txt', 'w', encoding='utf-8') as f:
        f.write("=" * 60 + "\n")
        f.write("СЦЕНА 279 - Образец исправленного текста\n")
        f.write("=" * 60 + "\n\n")
        f.write(scene_fixed)
        f.write("\n\n" + "=" * 60 + "\n")
        f.write("Проверьте, правильно ли отображается русский текст.\n")
        f.write("=" * 60 + "\n")

        if unmapped:
            f.write("\n\nНеопознанные символы:\n")
            for char in sorted(unmapped):
                f.write(f"  {char}\n")

    with open('extract_log.txt', 'w', encoding='utf-8') as f:
        f.write(f"Extraction complete.\n")
        f.write(f"Output file: scene_279_sample.txt\n")
        f.write(f"Original text length: {len(scene_garbled)} chars\n")
        f.write(f"Fixed text length: {len(scene_fixed)} chars\n")
        f.write(f"Unmapped characters: {len(unmapped)}\n")

if __name__ == "__main__":
    main()
