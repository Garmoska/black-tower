#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
COMPREHENSIVE SOLUTION: Extract all scenes from Black Tower PDF
- Fix garbled Cyrillic encoding
- Fix missing spaces between words
- Extract scene IDs, exits, and items
- Export to Excel

Author: Claude Code
Date: 2026-04-10
"""

import fitz  # PyMuPDF
import openpyxl
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment
import re
from typing import List, Dict, Tuple
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


def build_cyrillic_map() -> Dict[str, str]:
    """
    Build complete Cyrillic character mapping.
    Maps garbled Latin Extended-B characters to proper Cyrillic.

    Pattern:
    - Lowercase Russian а-я: U+0208-U+0227
    - Uppercase Russian А-Я: U+01E8-U+0207
    """
    return {
        # Lowercase Cyrillic
        'Ȉ': 'а', 'ȉ': 'б', 'Ȋ': 'в', 'ȋ': 'г', 'Ȍ': 'д', 'ȍ': 'е',
        'Ȏ': 'ж', 'ȏ': 'з', 'Ȑ': 'и', 'ȑ': 'й', 'Ȓ': 'к', 'ȓ': 'л',
        'Ȕ': 'м', 'ȕ': 'н', 'Ȗ': 'о', 'ȗ': 'п', 'Ș': 'р', 'ș': 'с',
        'Ț': 'т', 'ț': 'у', 'Ȝ': 'ф', 'ȝ': 'х', 'Ȟ': 'ц', 'ȟ': 'ч',
        'Ƞ': 'ш', 'ȡ': 'щ', 'Ȣ': 'ъ', 'ȣ': 'ы', 'Ȥ': 'ь', 'ȥ': 'э',
        'Ȧ': 'ю', 'ȧ': 'я',
        # Uppercase Cyrillic
        'Ǩ': 'А', 'ǩ': 'Б', 'Ǫ': 'В', 'ǫ': 'Г', 'Ǭ': 'Д', 'ǭ': 'Е',
        'Ǯ': 'Ж', 'ǯ': 'З', 'Ǳ': 'И', 'ǲ': 'Й', 'ǳ': 'К', 'Ǵ': 'Л',
        'ǵ': 'Н', 'Ƕ': 'О', 'Ƿ': 'О', 'Ǹ': 'П', 'ǹ': 'П', 'Ǻ': 'Р',
        'ǻ': 'С', 'Ǽ': 'Т', 'ǽ': 'У', 'Ǿ': 'Ф', 'ǿ': 'Х', 'Ȁ': 'Ц',
        'ȁ': 'Ч', 'Ȃ': 'Ш', 'ȃ': 'Щ', 'Ȅ': 'Ъ', 'ȅ': 'Ы', 'Ȇ': 'Ь',
        'ȇ': 'Э',
    }


def fix_encoding(text: str, char_map: Dict[str, str]) -> str:
    """Fix garbled Cyrillic encoding."""
    return ''.join(char_map.get(c, c) for c in text)


def fix_spacing(text: str) -> str:
    """
    Fix missing spaces in Russian text using heuristic patterns.

    Common issues:
    - Prepositions merged with following words: "вдом" → "в дом"
    - Common short words merged: "неможет" → "не может"
    - Compound words without spaces
    """
    # Common two-letter prepositions and particles that need space after
    two_letter_words = [
        'не', 'но', 'во', 'на', 'из', 'от', 'до', 'по', 'за', 'со',
        'ко', 'то', 'же', 'ли', 'бы', 'ты', 'вы', 'мы', 'он', 'она'
    ]

    # Three-letter words
    three_letter_words = [
        'как', 'что', 'это', 'его', 'вам', 'вас', 'все', 'был', 'или',
        'там', 'для', 'под', 'над', 'при', 'про', 'без', 'где', 'еще',
        'уже', 'два', 'три', 'раз', 'вот', 'они', 'ваш', 'наш', 'нас'
    ]

    result = text

    # Add space after two-letter words if followed by lowercase letter
    for word in two_letter_words:
        # Pattern: word followed by lowercase Cyrillic letter
        result = re.sub(f'\\b({word})([а-я])', r'\1 \2', result, flags=re.IGNORECASE)

    # Add space before/after three-letter words
    for word in three_letter_words:
        # Space before if preceded by lowercase
        result = re.sub(f'([а-я])({word})\\b', r'\1 \2', result, flags=re.IGNORECASE)
        # Space after if followed by lowercase
        result = re.sub(f'\\b({word})([а-я])', r'\1 \2', result, flags=re.IGNORECASE)

    # Common verb endings that might need space before
    # e.g., "можетебыть" → "может быть"
    result = re.sub(r'([а-я])(быть|есть|была|было|были)', r'\1 \2', result)

    # Fix multiple spaces
    result = re.sub(r'\s+', ' ', result)

    return result


def extract_exits(text: str) -> List[str]:
    """
    Extract exit scene IDs from Russian text.

    Patterns:
    - "переходите к/на [число]"
    - "идите к/на [число]"
    - "- [число]" at end
    - Numbered choices with scene references
    """
    exits = []

    # Pattern 1: "переходите к/на X"
    matches = re.findall(r'переходите\s+(?:к|на)\s+(\d+)', text, re.IGNORECASE)
    exits.extend(matches)

    # Pattern 2: "идите к/на X"
    matches = re.findall(r'идите\s+(?:к|на)\s+(\d+)', text, re.IGNORECASE)
    exits.extend(matches)

    # Pattern 3: "- число" at end of text
    matches = re.findall(r'-\s*(\d+)\s*\.?\s*$', text)
    exits.extend(matches)

    # Pattern 4: "сцена X" or "эпизод X"
    matches = re.findall(r'(?:сцен[ауе]|эпизод)\s+(\d+)', text, re.IGNORECASE)
    exits.extend(matches)

    # Pattern 5: Numbered choices like "1) - 123" or "2 - 456"
    matches = re.findall(r'\d+[\)\.:\-]\s*(?:.*?-\s*)?(\d+)', text)
    exits.extend(matches)

    # Remove duplicates while preserving order
    seen = set()
    unique_exits = []
    for exit_id in exits:
        if exit_id not in seen and len(exit_id) <= 4:  # Scene IDs are max 4 digits
            seen.add(exit_id)
            unique_exits.append(exit_id)

    return unique_exits


def extract_items(text: str) -> List[str]:
    """
    Extract items from scene text.
    Items are marked in CAPITAL LETTERS (at least 3 consecutive caps).

    Filters out common non-item words.
    """
    # Find words with 3+ consecutive capital letters (Cyrillic or Latin)
    words = re.findall(r'\b[А-ЯA-Z]{3,}\b', text)

    # Filter out common non-item Russian words that might be capitalized
    exclude = {
        'ВЫ', 'ВАС', 'ВАМ', 'ЕСЛИ', 'ДА', 'НЕТ', 'ОН', 'ОНА',
        'ОНО', 'ОНИ', 'ЭТО', 'ТАК', 'КАК', 'ВСЕ', 'НО'
    }

    items = [w for w in words if w not in exclude]

    # Remove duplicates while preserving order
    seen = set()
    unique_items = []
    for item in items:
        if item not in seen:
            seen.add(item)
            unique_items.append(item)

    return unique_items


def extract_all_text(pdf_path: str) -> str:
    """Extract all text from PDF."""
    logger.info(f"Opening PDF: {pdf_path}")
    doc = fitz.open(pdf_path)
    all_text = ""
    total_pages = len(doc)

    for page_num, page in enumerate(doc, 1):
        all_text += page.get_text()
        if page_num % 10 == 0:
            logger.info(f"Processed {page_num}/{total_pages} pages")

    doc.close()
    logger.info(f"Extracted {len(all_text)} characters from {total_pages} pages")
    return all_text


def parse_scenes(text: str, char_map: Dict[str, str]) -> List[Dict[str, any]]:
    """
    Parse all scenes from extracted text.

    Returns list of scene dictionaries with:
    - id: Scene unique ID
    - text: Scene description (encoding and spacing fixed)
    - exits: List of exit scene IDs
    - items: List of items found
    """
    lines = text.split('\n')
    scenes = []

    i = 0
    while i < len(lines):
        line = lines[i].strip()

        # Check if this line is a scene ID (standalone number, 1-4 digits)
        if re.match(r'^\d{1,4}$', line):
            scene_id = line
            scene_lines = []

            # Collect all lines until next scene ID
            i += 1
            while i < len(lines):
                next_line = lines[i].strip()

                # Stop if we hit another scene ID
                if re.match(r'^\d{1,4}$', next_line) and i > 0:
                    break

                # Skip empty lines
                if next_line:
                    scene_lines.append(next_line)

                i += 1

            # Join scene text
            scene_text_garbled = ' '.join(scene_lines)

            # Fix encoding
            scene_text_fixed = fix_encoding(scene_text_garbled, char_map)

            # Fix spacing
            scene_text_final = fix_spacing(scene_text_fixed)

            # Extract exits and items
            exits = extract_exits(scene_text_final)
            items = extract_items(scene_text_final)

            # Create scene dictionary
            scene = {
                'id': scene_id,
                'text': scene_text_final,
                'exits': exits,
                'items': items
            }

            scenes.append(scene)

            # Log progress every 50 scenes
            if len(scenes) % 50 == 0:
                logger.info(f"Parsed {len(scenes)} scenes...")
        else:
            i += 1

    return scenes


def clean_for_excel(text: str) -> str:
    """
    Clean text for Excel export.
    Remove control characters that Excel doesn't support.
    """
    if not text:
        return text

    # Remove control characters except tab, newline, carriage return
    cleaned = ''.join(char for char in text if ord(char) >= 32 or char in '\t\n\r')

    return cleaned


def export_to_excel(scenes: List[Dict], output_path: str):
    """Export scenes to Excel with proper formatting."""
    logger.info(f"Creating Excel workbook...")

    wb = Workbook()
    ws = wb.active
    ws.title = "Scenes"

    # Write headers
    headers = ['ID', 'Text', 'Exits', 'Items']
    ws.append(headers)

    # Format header row
    for cell in ws[1]:
        cell.font = Font(bold=True, size=12)
        cell.alignment = Alignment(horizontal='center', vertical='center')

    # Write scene data
    for scene in scenes:
        ws.append([
            scene['id'],
            clean_for_excel(scene['text']),
            ', '.join(scene['exits']) if scene['exits'] else '',
            ', '.join(scene['items']) if scene['items'] else ''
        ])

    # Set column widths
    ws.column_dimensions['A'].width = 8   # ID
    ws.column_dimensions['B'].width = 100  # Text
    ws.column_dimensions['C'].width = 25  # Exits
    ws.column_dimensions['D'].width = 30  # Items

    # Format text cells with wrapping
    for row in ws.iter_rows(min_row=2, max_row=ws.max_row):
        # Text column - wrap and align top
        row[1].alignment = Alignment(wrap_text=True, vertical='top')
        # ID column - center
        row[0].alignment = Alignment(horizontal='center', vertical='center')

    # Freeze header row
    ws.freeze_panes = 'A2'

    # Save workbook
    wb.save(output_path)
    logger.info(f"✓ Saved {len(scenes)} scenes to: {output_path}")


def generate_statistics(scenes: List[Dict]) -> Dict:
    """Generate statistics about extracted scenes."""
    total_scenes = len(scenes)
    scenes_with_exits = sum(1 for s in scenes if s['exits'])
    scenes_with_items = sum(1 for s in scenes if s['items'])
    total_exits = sum(len(s['exits']) for s in scenes)
    total_items = sum(len(s['items']) for s in scenes)

    # Average text length
    avg_text_length = sum(len(s['text']) for s in scenes) / total_scenes if total_scenes > 0 else 0

    return {
        'total_scenes': total_scenes,
        'scenes_with_exits': scenes_with_exits,
        'scenes_with_items': scenes_with_items,
        'total_exits': total_exits,
        'total_items': total_items,
        'avg_text_length': avg_text_length
    }


def main():
    """Main execution function."""
    PDF_PATH = "black_tower_91.pdf"
    OUTPUT_PATH = "black_tower_scenes_complete.xlsx"

    logger.info("="*70)
    logger.info("BLACK TOWER SCENE EXTRACTION - COMPREHENSIVE SOLUTION")
    logger.info("="*70)

    # Step 1: Extract all text from PDF
    logger.info("\n[1/5] Extracting text from PDF...")
    all_text = extract_all_text(PDF_PATH)

    # Step 2: Build character map
    logger.info("\n[2/5] Building Cyrillic character map...")
    char_map = build_cyrillic_map()
    logger.info(f"Character map loaded: {len(char_map)} mappings")

    # Step 3: Parse all scenes
    logger.info("\n[3/5] Parsing scenes (fixing encoding and spacing)...")
    scenes = parse_scenes(all_text, char_map)
    logger.info(f"✓ Parsed {len(scenes)} scenes")

    # Step 4: Generate statistics
    logger.info("\n[4/5] Generating statistics...")
    stats = generate_statistics(scenes)
    logger.info(f"\nStatistics:")
    logger.info(f"  Total scenes: {stats['total_scenes']}")
    logger.info(f"  Scenes with exits: {stats['scenes_with_exits']}")
    logger.info(f"  Scenes with items: {stats['scenes_with_items']}")
    logger.info(f"  Total exits found: {stats['total_exits']}")
    logger.info(f"  Total items found: {stats['total_items']}")
    logger.info(f"  Avg text length: {stats['avg_text_length']:.0f} chars")

    # Step 5: Export to Excel
    logger.info(f"\n[5/5] Exporting to Excel...")
    export_to_excel(scenes, OUTPUT_PATH)

    # Show sample scenes
    logger.info("\n" + "="*70)
    logger.info("SAMPLE SCENES:")
    logger.info("="*70)
    for i, scene in enumerate(scenes[:3], 1):
        logger.info(f"\nScene {scene['id']}:")
        logger.info(f"  Text: {scene['text'][:100]}...")
        logger.info(f"  Exits: {', '.join(scene['exits']) if scene['exits'] else '(none)'}")
        logger.info(f"  Items: {', '.join(scene['items']) if scene['items'] else '(none)'}")

    logger.info("\n" + "="*70)
    logger.info("✓ EXTRACTION COMPLETE!")
    logger.info(f"✓ Output file: {OUTPUT_PATH}")
    logger.info("="*70)


if __name__ == "__main__":
    main()
