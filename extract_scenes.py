#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Black Tower Scene Extractor

Extracts and processes scenes from black_tower_91.pdf with proper Cyrillic
encoding and spacing fixes.

Usage:
    python extract_scenes.py              # Extract 10 random scenes
    python extract_scenes.py --all        # Extract all scenes
    python extract_scenes.py --scene 279  # Extract specific scene
"""

import sys
import random
import argparse
from pathlib import Path

# Configure Windows console for UTF-8
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

from black_tower_lib import (
    build_cyrillic_map,
    fix_encoding,
    load_russian_dictionary,
    fix_spacing,
    extract_scene_from_pdf,
    validate_scene,
    extract_scene_info
)


def process_scene(pdf_path, scene_id, char_map, dictionary):
    """Process a single scene with all fixes."""
    # Extract from PDF
    raw_text = extract_scene_from_pdf(pdf_path, scene_id)

    if not raw_text:
        return None

    # Apply encoding fix
    fixed_text, unmapped = fix_encoding(raw_text, char_map)

    # Apply spacing fix
    spaced_text = fix_spacing(fixed_text, dictionary)

    # Validate
    is_valid, issues = validate_scene(spaced_text)

    # Extract info
    info = extract_scene_info(spaced_text)

    return {
        'id': scene_id,
        'text': spaced_text,
        'valid': is_valid,
        'issues': issues,
        'info': info,
        'unmapped': len(unmapped)
    }


def save_scene(scene_data, output_dir):
    """Save scene to file."""
    scene_id = scene_data['id']
    output_file = output_dir / f"scene_{scene_id:03d}.txt"

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("="*70 + "\n")
        f.write(f"СЦЕНА {scene_id}\n")
        f.write("="*70 + "\n\n")
        f.write(scene_data['text'])
        f.write("\n\n" + "="*70 + "\n")
        f.write("SCENE INFORMATION:\n")
        f.write("="*70 + "\n")

        info = scene_data['info']
        if info['exits']:
            f.write(f"Exits: {', '.join(info['exits'])}\n")
        if info['enemies']:
            f.write(f"Enemies: {', '.join(set(info['enemies']))}\n")
        if info['spells']:
            f.write(f"Spells: {', '.join(info['spells'])}\n")
        if info['characteristics']:
            f.write(f"Characteristics: {', '.join(info['characteristics'])}\n")

        f.write("\n" + "="*70 + "\n")
        f.write(f"VALIDATION: {'✓ PASSED' if scene_data['valid'] else '✗ ISSUES'}\n")
        if scene_data['issues']:
            for issue in scene_data['issues']:
                f.write(f"  - {issue}\n")
        if scene_data['unmapped'] > 0:
            f.write(f"Unmapped characters: {scene_data['unmapped']}\n")
        f.write("="*70 + "\n")


def main():
    parser = argparse.ArgumentParser(description='Extract scenes from Black Tower PDF')
    parser.add_argument('--scene', type=int, help='Extract specific scene ID')
    parser.add_argument('--all', action='store_true', help='Extract all scenes')
    parser.add_argument('--count', type=int, default=10, help='Number of random scenes (default: 10)')
    parser.add_argument('--output', type=str, default='extracted_scenes', help='Output directory')
    args = parser.parse_args()

    print("="*70)
    print("BLACK TOWER SCENE EXTRACTOR")
    print("="*70)

    # Setup
    pdf_path = "black_tower_91.pdf"
    output_dir = Path(args.output)
    output_dir.mkdir(exist_ok=True)

    # Load resources
    print("\nLoading character mapping...")
    char_map = build_cyrillic_map()
    print(f"✓ Character map: {len(char_map)} mappings")

    print("Loading Russian dictionary...")
    dictionary = load_russian_dictionary()
    print(f"✓ Dictionary: {len(dictionary)} words")

    # Determine which scenes to extract
    if args.scene:
        scene_ids = [args.scene]
        print(f"\n→ Extracting scene {args.scene}")
    elif args.all:
        scene_ids = list(range(1, 618))
        print(f"\n→ Extracting all {len(scene_ids)} scenes")
    else:
        random.seed(42)
        scene_ids = sorted(random.sample(range(1, 618), args.count))
        print(f"\n→ Extracting {args.count} random scenes: {scene_ids}")

    # Process scenes
    results = []
    for i, scene_id in enumerate(scene_ids, 1):
        print(f"\n[{i}/{len(scene_ids)}] Processing scene {scene_id}...", end=' ')

        scene_data = process_scene(pdf_path, scene_id, char_map, dictionary)

        if scene_data is None:
            print("✗ NOT FOUND")
            continue

        # Save scene
        save_scene(scene_data, output_dir)
        results.append(scene_data)

        status = "✓" if scene_data['valid'] else "⚠"
        print(f"{status} Saved")

        if scene_data['info']['exits']:
            print(f"    Exits: {', '.join(scene_data['info']['exits'])}")
        if scene_data['info']['enemies']:
            print(f"    Enemies: {', '.join(set(scene_data['info']['enemies']))}")

    # Summary
    print(f"\n{'='*70}")
    print("EXTRACTION COMPLETE")
    print(f"{'='*70}")
    print(f"Total scenes extracted: {len(results)}")
    print(f"Valid scenes: {sum(1 for r in results if r['valid'])}")
    print(f"Scenes with issues: {sum(1 for r in results if not r['valid'])}")
    print(f"Output directory: {output_dir}/")
    print(f"{'='*70}")


if __name__ == "__main__":
    main()
