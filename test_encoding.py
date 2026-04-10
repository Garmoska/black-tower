#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test different approaches to fix Cyrillic text encoding from PDF.
"""

import fitz  # PyMuPDF

def extract_single_scene(pdf_path: str, page_num: int = 48):
    """Extract text from a specific page and try to fix encoding."""
    doc = fitz.open(pdf_path)
    page = doc[page_num]

    # Method 1: Standard extraction
    text_standard = page.get_text()

    # Method 2: Try different encoding
    text_blocks = page.get_text("text")

    # Method 3: Get text with dict to see encoding info
    text_dict = page.get_text("dict")

    doc.close()

    return text_standard, text_blocks, text_dict

def try_remap_characters(text: str) -> str:
    """
    Attempt to remap garbled characters to proper Cyrillic.

    The text appears to be Windows-1251 (Cyrillic) bytes incorrectly
    interpreted as some other encoding (possibly Latin Extended).
    """
    # Try to encode as latin1 and decode as cp1251 (Windows Cyrillic)
    try:
        # First, try direct character mapping based on patterns we see
        # Common mappings observed:
        mapping = {
            'Ǫ': 'В',
            'ȣ': 'ы',
            'Ȑ': 'и',
            'Ƿ': 'П',
            'Ȗ': 'о',
            'Ȍ': 'д',
            'ȏ': 'з',
            'ȍ': 'е',
            'Ȕ': 'м',
            'ȍ': 'е',
            'Ȓ': 'л',
            'Ȥ': 'ь',
            'ȧ': 'я',
            'ȟ': 'ч',
            'ȍ': 'е',
            'Ș': 'р',
            'ȕ': 'н',
            'Ȗ': 'о',
            'ȋ': 'г',
            'ǯ': 'З',
            'Ȉ': 'а',
            'Ȕ': 'м',
            'Ȓ': 'к',
            'ǩ': 'Б',
            'ș': 'с',
            'ȓ': 'л',
            'Ȋ': 'в',
            'Ț': 'т',
            'Ȏ': 'ж',
            'Ȋ': 'в',
            'ȑ': 'й',
            'Ȉ': 'а',
            'Ș': 'р',
            'Ȥ': 'ь',
            'Ȋ': 'в',
            'ȟ': 'ч',
            'ǭ': 'Е',
            'ș': 'с',
            'ț': 'у',
            'Ȉ': 'а',
            'ȗ': 'п',
            'ȘȐ': 'ри',
            'ȝ': 'х',
            'Ȍ': 'д',
            'Ț': 'т',
            'ȟ': 'ч',
            'Ȉ': 'а',
            'ȧ': 'я',
        }

        result = text
        for old, new in mapping.items():
            result = result.replace(old, new)

        return result
    except Exception as e:
        return f"Remapping failed: {e}"

def extract_scene_279(text: str) -> str:
    """Extract scene 279 specifically."""
    lines = text.split('\n')

    # Find scene 279
    scene_lines = []
    in_scene = False

    for i, line in enumerate(lines):
        line = line.strip()

        # Start of scene 279
        if line == '279':
            in_scene = True
            scene_lines.append(line)
            continue

        # Next scene number (280) - stop
        if in_scene and line == '280':
            break

        if in_scene and line:
            scene_lines.append(line)

    return '\n'.join(scene_lines)

def main():
    pdf_path = "black_tower_91.pdf"

    print("Extracting text from PDF page 48...")
    text_standard, text_blocks, text_dict = extract_single_scene(pdf_path, 48)

    # Extract scene 279
    scene_text = extract_scene_279(text_standard)

    # Save original (garbled)
    with open('scene_279_original.txt', 'w', encoding='utf-8') as f:
        f.write("=== SCENE 279 - ORIGINAL (GARBLED) ===\n\n")
        f.write(scene_text)

    print("Saved original text to: scene_279_original.txt")

    # Try to fix encoding
    scene_fixed = try_remap_characters(scene_text)

    with open('scene_279_fixed.txt', 'w', encoding='utf-8') as f:
        f.write("=== SCENE 279 - FIXED (ATTEMPT) ===\n\n")
        f.write(scene_fixed)

    print("Saved fixed attempt to: scene_279_fixed.txt")

    # Also try byte-level approach
    try:
        # Try to encode the garbled text back to bytes and decode as cp1251
        scene_bytes_attempt = scene_text.encode('latin1').decode('cp1251')

        with open('scene_279_bytes_method.txt', 'w', encoding='utf-8') as f:
            f.write("=== SCENE 279 - BYTES METHOD ===\n\n")
            f.write(scene_bytes_attempt)

        print("Saved bytes method to: scene_279_bytes_method.txt")
    except Exception as e:
        print(f"Bytes method failed: {e}")

    print("\nDone! Please check the files.")

if __name__ == "__main__":
    main()
