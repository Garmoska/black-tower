#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Analyze character codes to build proper mapping.
"""

import fitz

def analyze_characters():
    """Extract text and analyze character codes."""
    doc = fitz.open('black_tower_91.pdf')
    page = doc[48]
    text = page.get_text()
    doc.close()

    # Get scene 279
    lines = text.split('\n')
    scene_lines = []
    in_scene = False

    for line in lines:
        line = line.strip()
        if line == '279':
            in_scene = True
            continue
        if in_scene and line == '280':
            break
        if in_scene and line:
            scene_lines.append(line)

    scene_text = '\n'.join(scene_lines)

    # Analyze first line character by character
    first_line = scene_lines[0] if scene_lines else ""

    print("First line analysis:")
    print("="*60)
    for i, char in enumerate(first_line[:30]):  # First 30 chars
        print(f"{i}: '{char}' -> U+{ord(char):04X} ({ord(char)})")

    # Try different decoding approaches
    print("\n" + "="*60)
    print("Trying different approaches:")
    print("="*60)

    # Approach 1: Direct bytes if possible
    try:
        # Get bytes from the garbled text
        byte_list = [ord(c) for c in first_line]
        print(f"\nByte values: {byte_list[:20]}")

        # Try to decode these as cp1251
        # But these are already unicode code points, not bytes
        # Need to map unicode code points to cp1251 bytes

    except Exception as e:
        print(f"Error: {e}")

    # Approach 2: Build mapping from observation
    # Sample text should be something like: "Вы подходите к зеркалу"
    # Let's see what we have:
    print(f"\nGarbled text: {first_line[:50]}")

    # Known Russian words to test:
    # Вы = Ǫȣ
    # подходите = ȗȖȌȝȖȌȐȚȍ
    # к = Ȓ
    # зеркалу = ȏȍȘȒȈȓț

    # Build character map from these known words
    known_pairs = [
        ('Ǫ', 'В'),  # V
        ('ȣ', 'ы'),  # y
        ('ȗ', 'п'),  # p
        ('Ȗ', 'о'),  # o
        ('Ȍ', 'д'),  # d
        ('ȝ', 'х'),  # h
        ('Ȑ', 'и'),  # i
        ('Ț', 'т'),  # t
        ('ȍ', 'е'),  # e
        ('Ȓ', 'к'),  # k
        ('ȏ', 'з'),  # z
        ('Ș', 'р'),  # r
        ('Ȉ', 'а'),  # a
        ('ț', 'у'),  # u
        ('ȕ', 'н'),  # n
        ('ȟ', 'ч'),  # ch
        ('ȋ', 'г'),  # g
        ('ȉ', 'б'),  # b
        ('ȓ', 'л'),  # l
        ('ȧ', 'я'),  # ya
        ('Ȕ', 'м'),  # m
        ('ș', 'с'),  # s
        ('Ȏ', 'ж'),  # zh
        ('ȕ', 'н'),  # n
        ('Ȉ', 'а'),  # a
        ('Ȕ', 'м'),  # m
        ('Ȥ', 'ь'),  # soft sign
        ('Ǭ', 'Е'),  # E
        ('ǵ', 'Н'),  # N
        ('Ƕ', 'О'),  # O
        ('ȡ', 'ж'),  # zh
        ('ȑ', 'й'),  # y
        ('Ȧ', 'ц'),  # ts
        ('ȍ', 'е'),  # e
    ]

    return known_pairs, scene_text

def build_full_map(known_pairs):
    """Build complete character mapping."""
    char_map = {}
    for garbled, correct in known_pairs:
        char_map[garbled] = correct

    return char_map

def apply_mapping(text, char_map):
    """Apply character mapping to text."""
    result = []
    for char in text:
        result.append(char_map.get(char, char))
    return ''.join(result)

def main():
    known_pairs, scene_text = analyze_characters()

    # Build map
    char_map = build_full_map(known_pairs)

    # Apply mapping
    fixed_text = apply_mapping(scene_text, char_map)

    # Save
    with open('scene_279_sample.txt', 'w', encoding='utf-8') as f:
        f.write("СЦЕНА 279\n")
        f.write("="*50 + "\n\n")
        f.write(fixed_text)
        f.write("\n\n" + "="*50)
        f.write("\nПроверьте, правильно ли отображается текст.")

    print("\nSaved to: scene_279_sample.txt")
    print("\nFixed text preview:")
    print(fixed_text[:200])

if __name__ == "__main__":
    main()
