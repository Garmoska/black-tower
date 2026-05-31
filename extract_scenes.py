"""
Scene extractor for "Подземелья Черного замка" (Dungeons of the Black Tower).

Reads black-tower.txt and produces a structured Excel file with one row per
scene. Each row contains:
    ID       - scene number
    Text     - cleaned narrative
    Exits    - comma-separated outgoing scene IDs (with notes about relative
               numbering when present)
    Items    - items mentioned in the scene
    Enemies  - enemies (with their stats) introduced in the scene

The source file is a plain-text rendering of the 1991 gamebook. Scenes are
numbered 1..N (currently 655). A scene begins with a line containing only
its number, separated by two blank lines from the surrounding text.

This script intentionally avoids any "smart" NLP — it relies on the explicit
formatting conventions described in CLAUDE.md.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

from openpyxl import Workbook
from openpyxl.styles import Alignment, Font
from openpyxl.utils import get_column_letter


SOURCE = Path(__file__).with_name("black-tower.txt")
OUTPUT = Path(__file__).with_name("black_tower_scenes.xlsx")


# -- Scene splitting ---------------------------------------------------------


SCENE_HEADER = re.compile(r"^\s*(\d+)\s*$")


@dataclass
class Scene:
    id: int
    raw_lines: list[str] = field(default_factory=list)

    @property
    def text(self) -> str:
        # Strip leading/trailing blank lines, normalize internal whitespace
        # while keeping paragraph breaks.
        lines = [ln.rstrip() for ln in self.raw_lines]
        while lines and not lines[0].strip():
            lines.pop(0)
        while lines and not lines[-1].strip():
            lines.pop()
        return "\n".join(lines)


def split_scenes(source_text: str) -> list[Scene]:
    """Split source text into ordered list of Scene objects.

    A scene begins with a line containing only the next expected ID. The
    introduction at the top of the book (rules, foreword) is discarded — we
    start collecting once scene 1 is found and only accept strictly
    incrementing scene IDs after that. This avoids being fooled by stray
    numeric lines inside a scene's body.
    """
    lines = source_text.splitlines()
    scenes: list[Scene] = []
    current: Scene | None = None
    expected = 1

    for line in lines:
        m = SCENE_HEADER.match(line)
        if m:
            num = int(m.group(1))
            if num == expected:
                if current is not None:
                    scenes.append(current)
                current = Scene(id=num)
                expected += 1
                continue
        if current is not None:
            current.raw_lines.append(line)

    if current is not None:
        scenes.append(current)

    return scenes


# -- Exit extraction ---------------------------------------------------------


# Patterns:
#   1. "(123)"            absolute, parenthesised
#   2. "- 123"            absolute, after dash
#   3. "(+ 12)"           relative offset (positive only), inside parentheses
#   4. "  123."           absolute, end-of-sentence number
#
# Relative exit offsets like "(+ 16)" are NOT real exits — they are offsets
# you remember when later prompted. We detect them and skip them.
# Negative offsets like "(- 83)" are item modifiers, not relative exits.

ABS_PAREN = re.compile(r"\((\d+)\)")
ABS_DASH = re.compile(r"[-–—]\s*(\d+)")
ABS_TRAIL = re.compile(r"(?<![\d.,])(\d+)\.")
REL_OFFSET = re.compile(r"\(\s*\+\s*(\d+)\s*\)")


def extract_exits(text: str) -> tuple[list[str], list[str]]:
    """Return (exits, notes).

    exits: ordered, deduplicated list of exit scene IDs (as strings).
    notes: special remarks about relative-number references found in the
           scene (so we can flag them in the output).
    """
    notes: list[str] = []
    relative_spans: list[tuple[int, int]] = []
    for m in REL_OFFSET.finditer(text):
        num = m.group(1)
        notes.append(f"relative +{num}")
        relative_spans.append(m.span())

    def in_relative(span: tuple[int, int]) -> bool:
        return any(rs <= span[0] and span[1] <= re_ for rs, re_ in relative_spans)

    found: list[str] = []
    seen: set[str] = set()

    def add(num_str: str) -> None:
        if num_str not in seen:
            seen.add(num_str)
            found.append(num_str)

    # 1. Absolute references in parentheses, e.g. "(564)"
    for m in ABS_PAREN.finditer(text):
        if in_relative(m.span()):
            continue
        add(m.group(1))

    # 2. After a dash or hyphen, e.g. "- 182"
    for m in ABS_DASH.finditer(text):
        if in_relative(m.span()):
            continue
        add(m.group(1))

    # 3. Numbers ending with a period, e.g. "По правой дороге? - 86."
    for m in ABS_TRAIL.finditer(text):
        if in_relative(m.span()):
            continue
        add(m.group(1))

    # Drop tiny numbers that are obviously not scene references — anything
    # one-digit is suspicious. Two digits and up are kept (book has up to 655
    # scenes, the smallest legitimate single-digit references like "1", "3",
    # "7" are still valid). We keep all to stay faithful to CLAUDE.md.

    return found, notes


# -- Enemy extraction --------------------------------------------------------


CAPS_LINE = re.compile(r"^[А-ЯЁ]+(?:[ \-][А-ЯЁ]+)*$")
STAT_LINE = re.compile(
    r"Ловкость\s+(\d+)\s+Сила\s+(\d+)(?:\s+Лояльность\s+(\d+))?"
)


def extract_enemies(text: str) -> list[str]:
    """Detect enemies by the paired pattern:
        line N   - all-caps name (one or more words)
        line N+1 - "Ловкость X Сила X [Лояльность X]"
    """
    lines = text.splitlines()
    enemies: list[str] = []
    for i in range(len(lines) - 1):
        name = lines[i].strip()
        stat = lines[i + 1].strip()
        if not name or not CAPS_LINE.match(name):
            continue
        m = STAT_LINE.match(stat)
        if not m:
            continue
        agi, str_, loy = m.group(1), m.group(2), m.group(3)
        descr = f"{name} (Ловкость {agi}, Сила {str_}"
        if loy is not None:
            descr += f", Лояльность {loy}"
        descr += ")"
        enemies.append(descr)
    return enemies


# -- Item extraction ---------------------------------------------------------


# Items in the source are written as ordinary nouns followed by a numeric
# offset in parentheses, e.g. "золотой свисток (+ 156)" or "огниво (+ 111)".
# We anchor on the offset and grab a short noun phrase (1-3 words, lowercase
# Russian letters) that sits immediately before it. This gives us a high-
# precision item list without trying to parse free Russian prose.

# A noun phrase up to 3 lowercase words (allowing a hyphen) followed by an
# optional space and the offset annotation. Item offsets use negative numbers
# like "(- 214)".
ITEM_PATTERN = re.compile(
    r"((?:[а-яё]+(?:-[а-яё]+)?\s+){0,2}[а-яё]+(?:-[а-яё]+)?)"
    r"\s*\(\s*-\s*\d+\s*\)"
)


# Items missed by the offset-anchored pattern are usually quest objects whose
# offsets appear elsewhere. We don't try to invent items not flagged in the
# text — recall is bounded by the original formatting.

STOP_WORDS = {
    "если",
    "когда",
    "теперь",
    "также",
    "очень",
    "только",
    "может",
    "будет",
    "было",
    "был",
    "была",
    "были",
    "это",
    "этом",
    "этой",
    "этого",
    "вам",
    "вас",
    "вы",
    "ваш",
    "ваша",
    "ваше",
    "ваши",
    "не",
    "и",
    "а",
    "но",
    "то",
    "та",
    "тот",
    "те",
    "там",
    "там",
    "его",
    "ее",
    "её",
    "их",
    "себе",
    "собой",
    "так",
    "что",
    "как",
    "уже",
    "еще",
    "ещё",
    "одно",
    "одной",
    "одного",
    "одна",
    "один",
    "два",
    "две",
    "три",
    "четыре",
    "пять",
    "шесть",
    "семь",
    "восемь",
    "девять",
    "десять",
    "из",
    "в",
    "на",
    "за",
    "под",
    "над",
    "перед",
    "около",
    "после",
    "до",
    "от",
    "по",
    "с",
    "о",
    "об",
    "у",
    "к",
    "ко",
    "со",
    "для",
    "без",
    "через",
}


def extract_items(text: str) -> list[str]:
    items: list[str] = []
    seen: set[str] = set()
    for m in ITEM_PATTERN.finditer(text):
        phrase = " ".join(m.group(1).split())
        # Trim stop words from the start of the phrase
        words = phrase.split()
        while words and words[0].lower() in STOP_WORDS:
            words.pop(0)
        if not words:
            continue
        cleaned = " ".join(words)
        # Capture the offset for context (items use negative offsets)
        offset_match = re.search(r"\(\s*-\s*(\d+)\s*\)", text[m.start() : m.end()])
        if offset_match:
            num = offset_match.group(1)
            label = f"{cleaned} (-{num})"
        else:
            label = cleaned
        if label not in seen:
            seen.add(label)
            items.append(label)
    return items


# -- Excel output ------------------------------------------------------------


def write_excel(scenes: list[Scene], path: Path) -> None:
    wb = Workbook()
    ws = wb.active
    ws.title = "Scenes"

    headers = ["ID", "Text", "Exits", "Items", "Enemies", "Notes"]
    ws.append(headers)
    for col_idx, _ in enumerate(headers, start=1):
        cell = ws.cell(row=1, column=col_idx)
        cell.font = Font(bold=True)
        cell.alignment = Alignment(vertical="top")

    for scene in scenes:
        text = scene.text
        exits, notes = extract_exits(text)
        enemies = extract_enemies(text)
        items = extract_items(text)
        ws.append(
            [
                scene.id,
                text,
                ", ".join(exits),
                "; ".join(items),
                "; ".join(enemies),
                "; ".join(notes),
            ]
        )

    # Column sizing
    widths = {1: 6, 2: 90, 3: 25, 4: 40, 5: 40, 6: 30}
    for col_idx, width in widths.items():
        ws.column_dimensions[get_column_letter(col_idx)].width = width

    # Wrap text in narrative cells
    for row in ws.iter_rows(min_row=2, max_row=ws.max_row):
        for cell in row:
            cell.alignment = Alignment(wrap_text=True, vertical="top")

    wb.save(path)


# -- Entry point -------------------------------------------------------------


def main() -> None:
    text = SOURCE.read_text(encoding="utf-8")
    scenes = split_scenes(text)
    print(f"Parsed {len(scenes)} scenes")
    if scenes:
        first, last = scenes[0].id, scenes[-1].id
        print(f"First scene: {first}, last scene: {last}")
        ids = {s.id for s in scenes}
        missing = [i for i in range(1, last + 1) if i not in ids]
        if missing:
            print(f"WARNING: missing scene IDs: {missing}")
    write_excel(scenes, OUTPUT)
    print(f"Wrote {OUTPUT}")


if __name__ == "__main__":
    main()
