#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Extract scenes from Black Tower PDF and export to Excel.
"""

import fitz  # PyMuPDF
import openpyxl
from openpyxl import Workbook
import re
from typing import List, Dict, Optional

def extract_text_from_pdf(pdf_path: str) -> str:
    """Extract all text from PDF file."""
    doc = fitz.open(pdf_path)
    text = ""
    for page in doc:
        text += page.get_text()
    doc.close()
    return text

def parse_scenes(text: str) -> List[Dict[str, any]]:
    """
    Parse scenes from extracted text.

    Expected format:
    - Scene ID on its own line (number)
    - Scene description
    - Exits marked with numbers (references to other scene IDs)
    - Items in CAPITAL LETTERS
    """
    scenes = []

    # Split text into potential scene blocks
    # Look for patterns like standalone numbers followed by text
    lines = text.split('\n')

    current_scene = None
    current_text = []

    for i, line in enumerate(lines):
        line = line.strip()
        if not line:
            continue

        # Check if line is a scene ID (standalone number)
        # Scene IDs are typically short numbers
        if re.match(r'^\d+$', line) and len(line) <= 4:
            # Save previous scene if exists
            if current_scene is not None:
                current_scene['text'] = ' '.join(current_text).strip()
                current_scene['items'] = extract_items(current_scene['text'])
                current_scene['exits'] = extract_exits(current_scene['text'])
                scenes.append(current_scene)

            # Start new scene
            current_scene = {
                'id': line,
                'text': '',
                'exits': [],
                'items': []
            }
            current_text = []
        elif current_scene is not None:
            # Add to current scene text
            current_text.append(line)

    # Don't forget the last scene
    if current_scene is not None:
        current_scene['text'] = ' '.join(current_text).strip()
        current_scene['items'] = extract_items(current_scene['text'])
        current_scene['exits'] = extract_exits(current_scene['text'])
        scenes.append(current_scene)

    return scenes

def extract_items(text: str) -> List[str]:
    """
    Extract items from scene text.
    Items are marked in CAPITAL LETTERS.
    """
    # Find words that are in all caps (2+ chars, Russian or English)
    # Exclude common Russian words that might be capitalized
    words = re.findall(r'\b[А-ЯA-Z][А-ЯA-Z]+\b', text)

    # Filter out common non-item words
    exclude = {'ЕСЛИ', 'ВЫ', 'ВАС', 'ВАМ', 'ВЫ', 'ДА', 'НЕТ', 'ОН', 'ОНА', 'ОНО', 'ОНИ'}
    items = [w for w in words if w not in exclude and len(w) >= 3]

    # Remove duplicates while preserving order
    seen = set()
    unique_items = []
    for item in items:
        if item not in seen:
            seen.add(item)
            unique_items.append(item)

    return unique_items

def extract_exits(text: str) -> List[str]:
    """
    Extract exit information from scene text.
    Look for patterns like "переходите к X" or numbered choices.
    """
    exits = []

    # Pattern 1: "переходите к/на [число]"
    pattern1 = re.findall(r'переходите\s+(?:к|на)\s+(\d+)', text, re.IGNORECASE)
    exits.extend(pattern1)

    # Pattern 2: "идите к/на [число]"
    pattern2 = re.findall(r'идите\s+(?:к|на)\s+(\d+)', text, re.IGNORECASE)
    exits.extend(pattern2)

    # Pattern 3: Numbered choices like "1) переход к X" or "1 - переход к X"
    pattern3 = re.findall(r'(?:\d+[\)\.:\-]\s*.*?)(?:переход|идите|к)\s+(?:к|на)?\s*(\d+)', text, re.IGNORECASE)
    exits.extend(pattern3)

    # Pattern 4: Direct reference like "сцена X" or "эпизод X"
    pattern4 = re.findall(r'(?:сцен[ау]|эпизод)\s+(\d+)', text, re.IGNORECASE)
    exits.extend(pattern4)

    # Pattern 5: Look for standalone numbers in context (at end of sentences or in choices)
    # This is more aggressive and might catch false positives
    # pattern5 = re.findall(r'[\.;:]\s+(\d{1,3})\s*[\.;]', text)
    # exits.extend(pattern5)

    # Remove duplicates while preserving order
    seen = set()
    unique_exits = []
    for exit_id in exits:
        if exit_id not in seen:
            seen.add(exit_id)
            unique_exits.append(exit_id)

    return unique_exits

def clean_text_for_excel(text: str) -> str:
    """
    Clean text to remove characters that are illegal in Excel.
    Excel doesn't support control characters and some Unicode ranges.
    """
    if not text:
        return text

    # Remove control characters except tab, newline, carriage return
    cleaned = ''.join(char for char in text if ord(char) >= 32 or char in '\t\n\r')

    # Try to fix encoding issues - looks like Latin Extended-B instead of Cyrillic
    # This is a mapping attempt for common issues
    replacements = {
        # Map some problematic characters to closest equivalents or remove them
    }

    for old, new in replacements.items():
        cleaned = cleaned.replace(old, new)

    return cleaned

def export_to_excel(scenes: List[Dict], output_path: str):
    """Export scenes to Excel file."""
    wb = Workbook()
    ws = wb.active
    ws.title = "Scenes"

    # Write header
    headers = ['ID', 'Text', 'Exits', 'Items']
    ws.append(headers)

    # Make header bold
    for cell in ws[1]:
        cell.font = openpyxl.styles.Font(bold=True)

    # Write data
    for scene in scenes:
        ws.append([
            scene['id'],
            clean_text_for_excel(scene['text']),
            ', '.join(scene['exits']) if scene['exits'] else '',
            ', '.join(scene['items']) if scene['items'] else ''
        ])

    # Adjust column widths
    ws.column_dimensions['A'].width = 10  # ID
    ws.column_dimensions['B'].width = 80  # Text
    ws.column_dimensions['C'].width = 20  # Exits
    ws.column_dimensions['D'].width = 30  # Items

    # Enable text wrapping for Text column
    for row in ws.iter_rows(min_row=2, max_row=ws.max_row, min_col=2, max_col=2):
        for cell in row:
            cell.alignment = openpyxl.styles.Alignment(wrap_text=True, vertical='top')

    wb.save(output_path)
    print(f"Exported {len(scenes)} scenes to {output_path}")

def main():
    pdf_path = "black_tower_91.pdf"
    output_path = "black_tower_scenes.xlsx"

    print(f"Extracting text from {pdf_path}...")
    text = extract_text_from_pdf(pdf_path)

    print(f"Extracted {len(text)} characters")
    print("(Text contains Cyrillic characters)")
    print("="*50)

    print("Parsing scenes...")
    scenes = parse_scenes(text)

    print(f"Found {len(scenes)} scenes")

    if scenes:
        print("\nFirst scene example:")
        print(f"ID: {scenes[0]['id']}")
        print(f"Text length: {len(scenes[0]['text'])} characters")
        print(f"Exits: {scenes[0]['exits']}")
        print(f"Items: {scenes[0]['items']}")

    print(f"\nExporting to {output_path}...")
    export_to_excel(scenes, output_path)
    print("Done!")

if __name__ == "__main__":
    main()
