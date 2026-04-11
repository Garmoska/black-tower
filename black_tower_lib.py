#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Black Tower Library - Core functions for PDF extraction and text processing.

This module provides:
- Character mapping for Cyrillic decoding
- Text spacing fixes using Russian dictionary
- Scene extraction and validation
- Game element parsing (exits, enemies, spells)
"""

import re
import fitz
from typing import Dict, Set, List, Tuple


def build_cyrillic_map() -> Dict[str, str]:
    """
    Build complete Cyrillic character mapping.

    The PDF uses Latin Extended-B encoding (U+01E8-U+0227) instead of proper
    Cyrillic (U+0400-U+04FF). This mapping fixes the encoding.

    Returns:
        Dictionary mapping garbled characters to correct Cyrillic
    """
    return {
        # Lowercase а-я (U+0208-U+0227)
        'Ȉ': 'а', 'ȉ': 'б', 'Ȋ': 'в', 'ȋ': 'г', 'Ȍ': 'д', 'ȍ': 'е',
        'Ȏ': 'ж', 'ȏ': 'з', 'Ȑ': 'и', 'ȑ': 'й', 'Ȓ': 'к', 'ȓ': 'л',
        'Ȕ': 'м', 'ȕ': 'н', 'Ȗ': 'о', 'ȗ': 'п', 'Ș': 'р', 'ș': 'с',
        'Ț': 'т', 'ț': 'у', 'Ȝ': 'ф', 'ȝ': 'х', 'Ȟ': 'ц', 'ȟ': 'ч',
        'Ƞ': 'ш', 'ȡ': 'щ', 'Ȣ': 'ъ', 'ȣ': 'ы', 'Ȥ': 'ь', 'ȥ': 'э',
        'Ȧ': 'ю', 'ȧ': 'я',

        # Uppercase А-Я (U+01E8-U+0207)
        'Ǩ': 'А', 'ǩ': 'Б', 'Ǫ': 'В', 'ǫ': 'Г', 'Ǭ': 'Д', 'ǭ': 'Е',
        'Ǯ': 'Ж', 'ǯ': 'З', 'ǰ': 'И', 'Ǳ': 'Й', 'ǲ': 'К', 'ǳ': 'К',
        'Ǵ': 'Л', 'ǵ': 'Н', 'Ƕ': 'О', 'Ƿ': 'О', 'Ǹ': 'П', 'ǹ': 'П',
        'Ǻ': 'Р', 'ǻ': 'С', 'Ǽ': 'Т', 'ǽ': 'У', 'Ǿ': 'Ф', 'ǿ': 'Х',
        'Ȁ': 'Ц', 'ȁ': 'Ч', 'Ȃ': 'Ш', 'ȃ': 'Щ', 'Ȅ': 'Ъ', 'ȅ': 'Ы',
        'Ȇ': 'Ь', 'ȇ': 'Э',
    }


def fix_encoding(text: str, char_map: Dict[str, str]) -> Tuple[str, Set[Tuple[str, int]]]:
    """
    Apply character mapping to fix Cyrillic encoding and remove control characters.

    Args:
        text: Text with garbled encoding
        char_map: Character mapping dictionary

    Returns:
        Tuple of (fixed_text, unmapped_characters)
    """
    result = []
    unmapped = set()

    for char in text:
        # Remove control characters except newline, tab, carriage return
        if ord(char) < 32 and char not in '\n\t\r':
            continue  # Skip control characters

        if char in char_map:
            result.append(char_map[char])
        else:
            result.append(char)
            # Track unmapped Latin Extended characters
            if 0x0180 <= ord(char) <= 0x024F:
                unmapped.add((char, ord(char)))

    return ''.join(result), unmapped


def load_russian_dictionary() -> Set[str]:
    """
    Load comprehensive Russian dictionary for word segmentation.

    Returns:
        Set of lowercase Russian words with inflected forms
    """
    words = {
        # Core pronouns
        'я', 'ты', 'он', 'она', 'оно', 'мы', 'вы', 'они', 'мне', 'тебе', 'ему', 'ей', 'нам', 'вам', 'им',

        # Prepositions & conjunctions (most critical for segmentation)
        'в', 'на', 'и', 'с', 'к', 'по', 'за', 'из', 'у', 'о', 'от', 'до', 'при', 'через', 'про',
        'а', 'но', 'или', 'что', 'как', 'если', 'когда', 'где', 'куда', 'почему', 'чтобы',
        'без', 'для', 'под', 'над', 'перед', 'между', 'со', 'ко', 'обо', 'во',

        # Particles & adverbs
        'не', 'ни', 'же', 'ли', 'бы', 'уже', 'еще', 'ещё', 'даже', 'только', 'очень', 'так',
        'там', 'тут', 'здесь', 'теперь', 'тогда', 'потом', 'всегда', 'быстро', 'медленно', 'вдруг',
        'сразу', 'снова', 'опять', 'вместе', 'почти', 'совсем', 'вообще', 'никогда',

        # Common game verbs with inflections
        'вы', 'идете', 'идти', 'идите', 'пойти', 'пойдете', 'выбирать', 'выбрать', 'выбираете',
        'попадаете', 'попасть', 'попадете', 'оказываетесь', 'оказаться',
        'находите', 'найти', 'найдете', 'видите', 'увидеть', 'увидите',
        'слышите', 'услышать', 'чувствуете', 'почувствовать',
        'можете', 'мочь', 'сможете', 'хотите', 'захотите',
        'придется', 'придётся', 'пришлось', 'удается', 'удастся', 'следует', 'остается',
        'подходите', 'подойти', 'подойдете', 'переходите', 'перейти', 'перейдете',
        'доходите', 'дойти', 'входите', 'войти', 'выходите', 'выйти', 'проходите', 'пройти',
        'открываете', 'открыть', 'откроете', 'закрываете', 'закрыть', 'закроете',
        'берете', 'взять', 'возьмете', 'делаете', 'сделать', 'сделаете',
        'начинается', 'начаться', 'кажется', 'показаться',
        'замечаете', 'заметить', 'заметите', 'наблюдаете', 'понаблюдать',
        'думаете', 'подумать', 'знаете', 'узнать', 'понимаете', 'понять', 'помните', 'вспомнить',
        'сражаться', 'драться', 'бороться', 'атаковать', 'нападает', 'напасть', 'убивать', 'убить', 'побеждать', 'победить',
        'поискать', 'искать', 'ищете', 'осмотреть', 'смотреть', 'посмотреть',
        'продолжить', 'продолжать', 'продолжаете', 'остановиться', 'останавливаться', 'расслабляетесь',
        'воспользоваться', 'пользоваться', 'использовать', 'попробуйте', 'попробуете', 'пробовать',
        'достаньте', 'достать', 'доставать', 'направиться', 'направляться',
        'отвечают', 'отвечать', 'ответить', 'принимают', 'принимать', 'принять',
        'раздваивается', 'открывается', 'вампридетсядратьсясостражей',

        # Common nouns with forms
        'дом', 'дома', 'домик', 'комната', 'комнате', 'комнаты', 'коридор', 'коридоре',
        'дверь', 'двери', 'дверью', 'окно', 'окна', 'стена', 'стены', 'стене', 'пол', 'полу',
        'путь', 'пути', 'дорога', 'дороге', 'дороги', 'тропа', 'тропе',
        'лес', 'леса', 'лесу', 'дерево', 'деревья', 'гора', 'горе', 'горы',
        'река', 'реке', 'реки', 'пещера', 'пещере', 'башня', 'башне', 'башни',
        'сундук', 'сундука', 'сундуке', 'ящик', 'ящика', 'ключ', 'ключа', 'ключик', 'ключом',
        'меч', 'меча', 'мечом', 'щит', 'щита', 'щитом',
        'золото', 'золотая', 'серебро', 'монета', 'монеты',
        'враг', 'врага', 'врагом', 'друг', 'друга', 'человек', 'люди', 'людей',
        'монстр', 'монстра', 'гоблин', 'гоблина', 'волк', 'волка', 'мышь', 'мыши', 'мышей', 'гарпия', 'гарпий', 'гарпиями',
        'свет', 'света', 'тьма', 'тьме', 'огонь', 'огня', 'вода', 'воде', 'воду', 'водой',
        'зеркало', 'зеркала', 'зеркалу', 'рама', 'раме', 'рамой', 'изображение', 'изображения', 'изображениями', 'изображением',
        'орнамент', 'орнамента', 'орнаментом',
        'день', 'дня', 'ночь', 'ночи', 'ночью', 'утро', 'утра', 'вечер', 'вечера',
        'час', 'часа', 'время', 'времени', 'луна', 'луны', 'солнце', 'солнца',
        'жизнь', 'жизни', 'смерть', 'смерти', 'опасность', 'опасности',
        'страх', 'страха', 'храбрость', 'сила', 'силы', 'слабость',
        'удача', 'удачи', 'победа', 'победы', 'поражение', 'битва', 'битвы', 'битве',
        'выбор', 'выбора', 'решение', 'решения', 'выход', 'выхода',
        'заклятие', 'заклятия', 'магия', 'магии', 'волшебство', 'приключение', 'история', 'развилка',
        'убежище', 'укрытие', 'ставни', 'ставень', 'цветы', 'цветов', 'огурец', 'лук', 'луку', 'грядка', 'грядке',
        'кольцо', 'кольца', 'свисток', 'четки', 'предмет', 'предмета', 'пропуск',
        'мастерство', 'выносливость', 'удача',
        'сторона', 'стороны', 'воин', 'воина', 'воинов', 'стража', 'стражей', 'стражник', 'стражники',
        'сцена', 'сцены', 'сцен', 'проход', 'прохода', 'проходе',
        'смех', 'смехом',

        # Adjectives with inflections
        'большой', 'большая', 'большое', 'большие', 'маленький', 'маленькая', 'маленькие',
        'длинный', 'короткий', 'короткая', 'короткие', 'высокий', 'низкий',
        'старый', 'старая', 'новый', 'новая', 'новые', 'древний', 'древняя',
        'красивый', 'красивая', 'прекрасный', 'прекрасная', 'прекрасным', 'страшный', 'страшная',
        'темный', 'темная', 'светлый', 'светлая', 'яркий', 'яркая',
        'холодный', 'холодная', 'теплый', 'теплая', 'горячий', 'горячая',
        'сильный', 'сильная', 'слабый', 'слабая', 'слабые', 'хилые', 'хилая',
        'быстрый', 'быстрая', 'медленный', 'медленная', 'легкий', 'легкая', 'тяжелый', 'тяжелая',
        'правый', 'правая', 'правые', 'левый', 'левая', 'левые',
        'верхний', 'верхняя', 'нижний', 'нижняя', 'передний', 'передняя',
        'первый', 'первая', 'второй', 'вторая', 'последний', 'последняя',
        'другой', 'другая', 'другие', 'такой', 'такая', 'такие', 'каждый', 'каждая',
        'весь', 'вся', 'всё', 'все', 'целый', 'целая', 'один', 'одна', 'одно', 'много',
        'хороший', 'хорошая', 'плохой', 'плохая', 'странный', 'странная',
        'необычный', 'необычная', 'таинственный', 'зачарованный',
        'тихий', 'тихая', 'громкий', 'громкая', 'живой', 'живая', 'мертвый', 'мертвая',
        'открытый', 'открытая', 'закрытый', 'закрытая', 'запертый', 'запертая',
        'золотой', 'золотая', 'золотые', 'серебряный', 'серебряная', 'бронзовый', 'медный', 'заброшенный',

        # Numbers
        'один', 'одна', 'одно', 'два', 'две', 'три', 'четыре', 'пять', 'шесть', 'семь', 'восемь', 'девять', 'десять',
        'несколько', 'много', 'мало',

        # Other important words
        'через', 'около', 'примерно', 'долгое', 'без', 'столько', 'какой', 'какая', 'какую', 'каких',
        'который', 'которая', 'которую', 'которые', 'нет', 'да', 'это', 'то', 'все', 'всё', 'ничего', 'никакой', 'никакая',
        'поблизости', 'вокруг', 'справа', 'слева', 'впереди', 'позади',
        'вправый', 'влевый', 'вам', 'вас', 'нужны', 'нужен', 'им', 'их', 'ими',
        'реперь', 'теперь', 'сражаясь',
        # Additional inflected forms
        'куда', 'острову', 'остров', 'острова', 'островом', 'берег', 'берега', 'берегу',
        'используя', 'использовать', 'используете', 'направитесь', 'направитесь',
        'стражей', 'стража', 'стражу', 'стражником', 'стражниками',
        'передняя', 'переднюю', 'передней', 'дверь', 'двери', 'дверью',
        'открывается', 'открываться', 'открывающийся',
        'раздваивается', 'раздваиваться', 'раздваивающийся',
        'правый', 'правая', 'левый', 'левая', 'вправый', 'влевый',
        'проход', 'прохода', 'проходом', 'проходе',
    }

    return {w.lower() for w in words}


def segment_word(text: str, dictionary: Set[str], max_len: int = 20) -> str:
    """
    Segment merged words using dynamic programming with dictionary.

    Args:
        text: Merged word text
        dictionary: Set of valid Russian words
        max_len: Maximum word length to consider

    Returns:
        Segmented text with spaces
    """
    text_lower = text.lower()
    n = len(text_lower)

    # dp[i] = (score, word_boundaries, word_count)
    dp = [(-float('inf'), [], 0)] * (n + 1)
    dp[0] = (0, [], 0)

    for i in range(1, n + 1):
        for j in range(max(0, i - max_len), i):
            word = text_lower[j:i]
            word_len = len(word)

            # Skip single chars in middle (except for valid single-char words)
            if word_len == 1 and j > 0 and i < n:
                if word not in {'в', 'к', 'с', 'у', 'о', 'и', 'а', 'я'}:
                    continue

            # Calculate score - prefer longer words over many small ones
            if word in dictionary:
                if word_len == 1:
                    # Single-char prepositions: important but not too high
                    score = 5
                elif word_len == 2:
                    # 2-char words: good but prefer longer
                    score = word_len * 6
                elif word_len >= 3:
                    # Longer words: strongly preferred (exponential bonus)
                    score = word_len * word_len  # Quadratic scoring!
            elif word_len >= 5:
                score = word_len * 0.3
            elif word_len >= 3:
                score = word_len * 0.1
            elif word_len == 2:
                score = -2
            else:
                score = -10

            # Penalize fragmentation: penalty for each additional word
            word_count = dp[j][2] + 1
            fragmentation_penalty = word_count * 2.0  # Increased from 0.5 to 2.0

            new_score = dp[j][0] + score - fragmentation_penalty
            if new_score > dp[i][0]:
                dp[i] = (new_score, dp[j][1] + [i], word_count)

    # Reconstruct
    if dp[n][0] > -float('inf'):
        boundaries = [0] + dp[n][1]
        words = [text[boundaries[i]:boundaries[i+1]] for i in range(len(boundaries)-1)]
        return ' '.join(words)
    return text


def fix_spacing(text: str, dictionary: Set[str]) -> str:
    """
    Fix spacing in text using dictionary-based segmentation.

    Args:
        text: Text with merged words
        dictionary: Russian word dictionary

    Returns:
        Text with proper spacing
    """
    lines = text.split('\n')
    fixed_lines = []

    for line in lines:
        # Skip structural lines
        if not line.strip() or line.strip().startswith('===') or \
           line.strip().startswith('СЦЕНА'):
            fixed_lines.append(line)
            continue

        # Process Cyrillic word chunks
        result = []
        last_end = 0

        for match in re.finditer(r'[а-яА-ЯёЁ]+', line):
            result.append(line[last_end:match.start()])
            word = match.group()

            # Segment words that are likely merged (threshold lowered to 5 to catch more cases)
            if len(word) > 5:
                segmented = segment_word(word, dictionary)
                result.append(segmented)
            else:
                result.append(word)

            last_end = match.end()

        result.append(line[last_end:])
        fixed_lines.append(''.join(result))

    return '\n'.join(fixed_lines)


def extract_scene_from_pdf(pdf_path: str, scene_id: int) -> str:
    """
    Extract specific scene from PDF.

    Args:
        pdf_path: Path to PDF file
        scene_id: Scene ID to extract

    Returns:
        Raw scene text
    """
    doc = fitz.open(pdf_path)
    all_text = ""

    # Extract from pages 8+ (scenes start on page 8)
    for page_num in range(7, len(doc)):
        all_text += doc[page_num].get_text()

    doc.close()

    # Find scene
    lines = all_text.split('\n')
    scene_lines = []
    in_scene = False
    start_idx = -1

    for i, line in enumerate(lines):
        stripped = line.strip()

        if stripped == str(scene_id) and not in_scene:
            in_scene = True
            start_idx = i
            continue

        if in_scene:
            # Stop at next scene number
            if stripped.isdigit() and len(stripped) <= 4 and i > start_idx + 1:
                if 1 <= int(stripped) <= 700:
                    break

            if stripped:
                scene_lines.append(stripped)

    return '\n'.join(scene_lines)


def validate_scene(text: str) -> Tuple[bool, List[str]]:
    """
    Validate Russian text quality.

    Args:
        text: Scene text to validate

    Returns:
        Tuple of (is_valid, list_of_issues)
    """
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


def extract_scene_info(text: str) -> Dict[str, List[str]]:
    """
    Extract game elements from scene text.

    Args:
        text: Scene text

    Returns:
        Dictionary with exits, enemies, spells, characteristics
    """
    info = {
        'exits': [],
        'enemies': [],
        'spells': [],
        'characteristics': [],
    }

    # Extract exits
    patterns = [r'-\s*(\d{1,3})\b', r'\((\d{1,3})\)',
                r'переходите.*?(\d{1,3})', r'идите.*?(\d{1,3})']
    for pattern in patterns:
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
    enemy_keywords = ['ГОБЛИН', 'ОРК', 'ТРОЛЛЬ', 'ОБОРОТЕНЬ', 'ДРАКОН', 'МЫШЬ']
    for keyword in enemy_keywords:
        if keyword in text.upper():
            pattern = rf'\b([А-ЯЁ\s]{{0,15}}{keyword}[А-ЯЁ\s]{{0,10}})\b'
            matches = re.findall(pattern, text.upper())
            info['enemies'].extend(m.strip() for m in matches if 3 <= len(m.strip()) <= 30)

    return info
