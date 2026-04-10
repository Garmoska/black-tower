#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Final attempt: Build precise character mapping by analyzing the actual transformation.
"""

import fitz

def extract_sample():
    """Extract scene 279."""
    doc = fitz.open('black_tower_91.pdf')
    all_text = ""
    for page in doc:
        all_text += page.get_text()
    doc.close()

    lines = all_text.split('\n')
    for i, line in enumerate(lines):
        if line.strip() == '279':
            # Get next few lines
            scene_lines = []
            for j in range(i+1, min(i+10, len(lines))):
                if lines[j].strip().isdigit() and len(lines[j].strip()) <= 4:
                    break
                if lines[j].strip():
                    scene_lines.append(lines[j].strip())
            return '\n'.join(scene_lines)
    return ""

def analyze_and_build_map():
    """
    Analyze the garbled text pattern.

    Expected: "Вы подходите к зеркалу"
    Got: "Ǫȣ ȗȖȌȝȖȌȐȚȍ Ȓ ȏȍȘȒȈȓț"
    """
    # Build mapping from the known transformation
    # Comparing expected vs actual character by character

    expected = "Вы подходите к зеркалу, но не замечаете ничего необычного"
    garbled = "Ǫȣ ȗȖȌȝȖȌȐȚȍ Ȓ ȏȍȘȒȈȓț, ȕȖ ȕȍ ȏȈȔȍȟȈȍȚȍ ȕȐȟȍȋȖ ȕȍȖȉȣȟȕȖȋȖ"

    # Build character map
    char_map = {}

    # Make sure lengths match (they should if this is character-by-character substitution)
    if len(expected) == len(garbled):
        for exp_char, garb_char in zip(expected, garbled):
            if garb_char != ' ' and garb_char != ',' and garb_char != '.':
                char_map[garb_char] = exp_char

    return char_map

def apply_fix(text, char_map):
    """Apply character mapping."""
    result = []
    for char in text:
        result.append(char_map.get(char, char))
    return ''.join(result)

def main():
    # Extract scene
    scene_garbled = extract_sample()

    # Build map from known transformation
    char_map = analyze_and_build_map()

    # Apply fix
    scene_fixed = apply_fix(scene_garbled, char_map)

    # Save
    with open('scene_279_sample.txt', 'w', encoding='utf-8') as f:
        f.write("=" * 70 + "\n")
        f.write("СЦЕНА 279\n")
        f.write("=" * 70 + "\n\n")
        f.write(scene_fixed)
        f.write("\n\n" + "=" * 70 + "\n")
        f.write("Проверьте правильность отображения русского текста.\n")
        f.write("Если текст читается правильно, значит кодировка исправлена.\n")
        f.write("=" * 70 + "\n")

    # Also save the character map for reference
    with open('character_mapping.txt', 'w', encoding='utf-8') as f:
        f.write("Character Mapping (Garbled -> Correct):\n")
        f.write("=" * 50 + "\n\n")
        for garb, correct in sorted(char_map.items(), key=lambda x: x[1]):
            f.write(f"'{garb}' (U+{ord(garb):04X}) -> '{correct}'\n")

    print(f"Created: scene_279_sample.txt")
    print(f"Created: character_mapping.txt")
    print(f"Total mapped characters: {len(char_map)}")

if __name__ == "__main__":
    main()
