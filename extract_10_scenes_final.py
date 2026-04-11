#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Final comprehensive scene extraction with all fixes applied:
1. Updated character mapping (including ǰ → И)
2. Enhanced spacing algorithm with Russian dictionary
3. Full validation and structured data extraction
"""

import sys
import re
import random
import fitz
from pathlib import Path

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

def build_complete_cyrillic_map():
    """Build complete Cyrillic character mapping with all fixes."""
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
        'ǰ': 'И',  # U+01F0 *** FIXED ***
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

def fix_encoding(text, char_map):
    """Apply character mapping to fix encoding."""
    result = []
    unmapped = set()

    for char in text:
        if char in char_map:
            result.append(char_map[char])
        else:
            result.append(char)
            # Track unmapped characters in Latin Extended range
            if 0x0180 <= ord(char) <= 0x024F:
                unmapped.add((char, ord(char)))

    return ''.join(result), unmapped

def load_russian_dictionary():
    """Load comprehensive Russian dictionary."""
    words = {
        # Core words
        'я', 'ты', 'он', 'она', 'мы', 'вы', 'они', 'мне', 'тебе', 'ему', 'ей', 'нам', 'вам', 'им',
        'в', 'на', 'и', 'с', 'к', 'по', 'за', 'из', 'у', 'о', 'от', 'до', 'при', 'через', 'про',
        'а', 'но', 'или', 'что', 'как', 'если', 'когда', 'где', 'куда', 'почему', 'чтобы',
        'не', 'ни', 'же', 'ли', 'бы', 'уже', 'еще', 'ещё', 'даже', 'только', 'очень', 'так',
        'там', 'тут', 'здесь', 'теперь', 'тогда', 'потом', 'всегда', 'быстро', 'медленно', 'вдруг',

        # Common game verbs
        'вы', 'идете', 'идти', 'идите', 'пойти', 'выбирать', 'выбрать', 'выбираете',
        'попадаете', 'оказываетесь', 'находите', 'видите', 'слышите', 'чувствуете',
        'можете', 'хотите', 'придется', 'удается', 'следует', 'остается',
        'подходите', 'переходите', 'доходите', 'входите', 'выходите', 'проходите',
        'открываете', 'закрываете', 'берете', 'делаете', 'начинается', 'кажется',
        'замечаете', 'наблюдаете', 'думаете', 'знаете', 'понимаете', 'помните',
        'сражаться', 'драться', 'атаковать', 'нападает', 'убивать', 'побеждать',
        'поискать', 'осмотреть', 'продолжить', 'остановиться', 'расслабляетесь',
        'воспользоваться', 'попробуйте', 'попробуете', 'достаньте', 'направиться',

        # Common nouns
        'дом', 'домик', 'комната', 'коридор', 'дверь', 'окно', 'стена', 'пол',
        'путь', 'дорога', 'тропа', 'лес', 'дерево', 'гора', 'река', 'пещера', 'башня',
        'сундук', 'ящик', 'ключ', 'ключик', 'меч', 'щит', 'золото', 'серебро', 'монета',
        'враг', 'друг', 'человек', 'монстр', 'гоблин', 'волк', 'мышь', 'мыши', 'гарпия',
        'свет', 'тьма', 'огонь', 'вода', 'зеркало', 'рама', 'изображение', 'орнамент',
        'день', 'ночь', 'утро', 'вечер', 'час', 'время', 'луна', 'солнце',
        'жизнь', 'смерть', 'опасность', 'страх', 'храбрость', 'сила', 'слабость',
        'удача', 'победа', 'поражение', 'битва', 'выбор', 'решение', 'выход',
        'заклятие', 'магия', 'волшебство', 'приключение', 'история', 'развилка',
        'убежище', 'укрытие', 'ставни', 'цветы', 'огурец', 'лук', 'грядка',
        'кольцо', 'свисток', 'четки', 'предмет', 'пропуск',
        'мастерство', 'выносливость', 'удача',

        # Adjectives
        'большой', 'маленький', 'длинный', 'короткий', 'высокий', 'низкий',
        'старый', 'новый', 'древний', 'красивый', 'прекрасный', 'страшный',
        'темный', 'светлый', 'яркий', 'холодный', 'теплый', 'горячий',
        'сильный', 'слабый', 'быстрый', 'медленный', 'легкий', 'тяжелый',
        'правый', 'левый', 'верхний', 'нижний', 'первый', 'второй', 'последний',
        'другой', 'такой', 'каждый', 'весь', 'целый', 'один', 'много',
        'хороший', 'плохой', 'странный', 'необычный', 'таинственный', 'зачарованный',
        'тихий', 'громкий', 'живой', 'мертвый', 'открытый', 'закрытый', 'запертый',
        'золотой', 'серебряный', 'бронзовый', 'медный', 'заброшенный',

        # Numbers and quantifiers
        'один', 'одна', 'одно', 'два', 'три', 'четыре', 'пять', 'шесть', 'семь',
        'несколько', 'много', 'мало',

        # Other
        'через', 'около', 'примерно', 'долгое', 'без', 'столько', 'какой', 'какую',
        'который', 'которую', 'нет', 'да', 'это', 'то', 'все', 'ничего', 'никакой',
        'поблизости', 'вокруг', 'справа', 'слева', 'впереди', 'позади',
    }

    return {w.lower() for w in words}

def segment_word(text, dictionary, max_len=18):
    """Segment a long word into smaller dictionary words using DP."""
    text_lower = text.lower()
    n = len(text_lower)

    # dp[i] = (score, word_boundaries)
    dp = [(-float('inf'), [])] * (n + 1)
    dp[0] = (0, [])

    for i in range(1, n + 1):
        for j in range(max(0, i - max_len), i):
            word = text_lower[j:i]
            word_len = len(word)

            # Skip single chars in the middle
            if word_len == 1 and j > 0 and i < n:
                continue

            # Calculate score
            if word in dictionary:
                score = word_len * 3  # Strong preference for dictionary words
            elif word_len >= 4:
                score = word_len * 0.5  # Allow unknown longer words
            elif word_len >= 2:
                score = word_len * 0.2  # Small penalty for short unknown
            else:
                score = -5  # Large penalty for single chars

            new_score = dp[j][0] + score
            if new_score > dp[i][0]:
                dp[i] = (new_score, dp[j][1] + [i])

    # Reconstruct segmentation
    if dp[n][0] > -float('inf'):
        boundaries = [0] + dp[n][1]
        words = [text[boundaries[i]:boundaries[i+1]] for i in range(len(boundaries)-1)]
        return ' '.join(words)
    return text

def fix_spacing(text, dictionary):
    """Fix spacing in text using dictionary-based segmentation."""
    lines = text.split('\n')
    fixed_lines = []

    for line in lines:
        # Skip structural lines
        if not line.strip() or line.strip().startswith('===') or \
           line.strip().startswith('СЦЕНА') or line.strip().startswith('Выходы:') or \
           line.strip().startswith('EXTRACTED') or line.strip().startswith('VALIDATION'):
            fixed_lines.append(line)
            continue

        # Process Cyrillic word chunks
        result = []
        last_end = 0

        for match in re.finditer(r'[а-яА-ЯёЁ]+', line):
            # Add text before match
            result.append(line[last_end:match.start()])

            word = match.group()
            # Segment long words
            if len(word) > 15:
                segmented = segment_word(word, dictionary)
                result.append(segmented)
            else:
                result.append(word)

            last_end = match.end()

        # Add remaining text
        result.append(line[last_end:])
        fixed_lines.append(''.join(result))

    return '\n'.join(fixed_lines)

def extract_scene_from_pdf(pdf_path, scene_id):
    """Extract a specific scene from the PDF."""
    doc = fitz.open(pdf_path)
    all_text = ""

    # Extract all text from pages starting from page 8
    for page_num in range(7, len(doc)):
        page = doc[page_num]
        all_text += page.get_text()

    doc.close()

    # Find the scene
    lines = all_text.split('\n')
    scene_lines = []
    in_scene = False
    start_idx = -1

    for i, line in enumerate(lines):
        stripped = line.strip()

        # Check if this line is our scene ID
        if stripped == str(scene_id) and not in_scene:
            in_scene = True
            start_idx = i
            continue

        if in_scene:
            # Stop if we hit another scene number
            if stripped.isdigit() and len(stripped) <= 4 and i > start_idx + 1:
                # Check it's likely a scene ID (reasonable range)
                if 1 <= int(stripped) <= 700:
                    break

            # Collect non-empty lines
            if stripped:
                scene_lines.append(stripped)

    return '\n'.join(scene_lines)

def validate_scene(text):
    """Validate Russian text quality."""
    issues = []

    # Check for garbled characters
    garbled = set()
    for char in text:
        if 0x0180 <= ord(char) <= 0x024F:
            garbled.add(f'{char}(U+{ord(char):04X})')

    if garbled:
        issues.append(f"Garbled characters: {', '.join(list(garbled)[:5])}")

    # Check Cyrillic ratio
    cyrillic = sum(1 for c in text if '\u0400' <= c <= '\u04FF')
    letters = sum(1 for c in text if c.isalpha())

    if letters > 0 and cyrillic / letters < 0.8:
        issues.append(f"Low Cyrillic ratio: {cyrillic/letters:.1%}")

    return len(issues) == 0, issues

def extract_scene_info(text):
    """Extract game elements from scene."""
    info = {
        'exits': [],
        'enemies': [],
        'spells': [],
        'characteristics': [],
    }

    # Extract exits
    for pattern in [r'-\s*(\d{1,3})\b', r'\((\d{1,3})\)', r'переходите.*?(\d{1,3})', r'идите.*?(\d{1,3})']:
        info['exits'].extend(re.findall(pattern, text))

    info['exits'] = sorted(set(info['exits']), key=int)

    # Extract spells
    spells = ['ЗАКЛЯТИЕ ОГНЯ', 'ЗАКЛЯТИЕ ЛЕВИТАЦИИ', 'ЗАКЛЯТИЕ ИЛЛЮЗИИ',
              'ЗАКЛЯТИЕ СИЛЫ', 'ЗАКЛЯТИЕ СЛАБОСТИ', 'ЗАКЛЯТИЕ КОПИИ',
              'ЗАКЛЯТИЕ ПЛАВАНИЯ', 'ЗАКЛЯТИЕ ИСЦЕЛЕНИЯ']
    for spell in spells:
        if spell in text.upper():
            info['spells'].append(spell)

    # Extract characteristics
    for char in ['МАСТЕРСТВО', 'ВЫНОСЛИВОСТЬ', 'УДАЧА']:
        if char in text.upper():
            info['characteristics'].append(char)

    # Extract enemies
    for keyword in ['ГОБЛИН', 'ОРК', 'ТРОЛЛЬ', 'ОБОРОТЕНЬ', 'ДРАКОН', 'МЫШЬ', 'МЫШИ']:
        if keyword in text.upper():
            pattern = rf'\b([А-ЯЁ\s]{{0,15}}{keyword}[А-ЯЁ\s]{{0,10}})\b'
            matches = re.findall(pattern, text.upper())
            info['enemies'].extend(m.strip() for m in matches if 3 <= len(m.strip()) <= 30)

    return info

def main():
    print("="*70)
    print("FINAL SCENE EXTRACTION WITH ALL IMPROVEMENTS")
    print("="*70)

    # Setup
    pdf_path = "black_tower_91.pdf"
    output_dir = Path("final_10_scenes")
    output_dir.mkdir(exist_ok=True)

    # Load resources
    print("\nLoading character mapping...")
    char_map = build_complete_cyrillic_map()
    print(f"Character map: {len(char_map)} mappings (including ǰ → И fix)")

    print("Loading Russian dictionary...")
    dictionary = load_russian_dictionary()
    print(f"Dictionary: {len(dictionary)} words")

    # Select 10 random scenes (use same seed for reproducibility)
    random.seed(42)
    all_scene_ids = list(range(1, 618))
    selected_ids = sorted(random.sample(all_scene_ids, 10))

    print(f"\nSelected 10 random scenes: {selected_ids}")

    # Process each scene
    results = []

    for scene_id in selected_ids:
        print(f"\n{'='*70}")
        print(f"Processing Scene {scene_id}...")

        # Extract from PDF
        raw_text = extract_scene_from_pdf(pdf_path, scene_id)

        if not raw_text:
            print(f"  [WARNING] Scene {scene_id} not found in PDF")
            continue

        # Apply encoding fix
        fixed_text, unmapped = fix_encoding(raw_text, char_map)

        # Apply spacing fix
        spaced_text = fix_spacing(fixed_text, dictionary)

        # Validate
        is_valid, issues = validate_scene(spaced_text)

        # Extract info
        info = extract_scene_info(spaced_text)

        # Save
        output_file = output_dir / f"scene_{scene_id:03d}.txt"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("="*70 + "\n")
            f.write(f"СЦЕНА {scene_id}\n")
            f.write("="*70 + "\n\n")
            f.write(spaced_text)
            f.write("\n\n" + "="*70 + "\n")
            f.write("SCENE INFORMATION:\n")
            f.write("="*70 + "\n")
            if info['exits']:
                f.write(f"Exits: {', '.join(info['exits'])}\n")
            if info['enemies']:
                f.write(f"Enemies: {', '.join(set(info['enemies']))}\n")
            if info['spells']:
                f.write(f"Spells: {', '.join(info['spells'])}\n")
            if info['characteristics']:
                f.write(f"Characteristics: {', '.join(info['characteristics'])}\n")
            f.write("\n" + "="*70 + "\n")
            f.write(f"VALIDATION: {'[PASSED]' if is_valid else '[ISSUES]'}\n")
            if issues:
                for issue in issues:
                    f.write(f"  - {issue}\n")
            if unmapped:
                f.write(f"Unmapped characters: {len(unmapped)}\n")
            f.write("="*70 + "\n")

        results.append({
            'id': scene_id,
            'valid': is_valid,
            'issues': issues,
            'info': info
        })

        print(f"  Status: {'[VALID]' if is_valid else '[HAS ISSUES]'}")
        if issues:
            for issue in issues:
                print(f"    {issue}")
        if info['exits']:
            print(f"  Exits: {', '.join(info['exits'])}")
        if info['enemies']:
            print(f"  Enemies: {', '.join(set(info['enemies']))}")

    # Summary report
    summary_file = output_dir / "EXTRACTION_REPORT.txt"
    with open(summary_file, 'w', encoding='utf-8') as f:
        f.write("="*70 + "\n")
        f.write("FINAL SCENE EXTRACTION REPORT\n")
        f.write("="*70 + "\n\n")
        f.write(f"Total scenes extracted: {len(results)}\n")
        f.write(f"Valid scenes: {sum(1 for r in results if r['valid'])}\n")
        f.write(f"Scenes with issues: {sum(1 for r in results if not r['valid'])}\n\n")

        f.write("IMPROVEMENTS APPLIED:\n")
        f.write("  1. Fixed character mapping (added ǰ → И)\n")
        f.write("  2. Enhanced spacing algorithm with Russian dictionary\n")
        f.write("  3. Comprehensive validation\n\n")

        f.write("="*70 + "\n")
        f.write("SCENE DETAILS:\n")
        f.write("="*70 + "\n\n")

        for r in results:
            f.write(f"Scene {r['id']}:\n")
            f.write(f"  Status: {'[VALID]' if r['valid'] else '[ISSUES]'}\n")
            if r['issues']:
                for issue in r['issues']:
                    f.write(f"    - {issue}\n")
            if r['info']['exits']:
                f.write(f"  Exits: {', '.join(r['info']['exits'])}\n")
            if r['info']['enemies']:
                f.write(f"  Enemies: {', '.join(set(r['info']['enemies']))}\n")
            if r['info']['spells']:
                f.write(f"  Spells: {', '.join(r['info']['spells'])}\n")
            f.write("\n")

    print(f"\n{'='*70}")
    print("EXTRACTION COMPLETE!")
    print(f"{'='*70}")
    print(f"Output directory: {output_dir}/")
    print(f"Extraction report: {summary_file}")
    print(f"Valid scenes: {sum(1 for r in results if r['valid'])}/{len(results)}")
    print(f"{'='*70}")

if __name__ == "__main__":
    main()
