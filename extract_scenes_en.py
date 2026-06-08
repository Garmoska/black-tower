"""
Scene extractor for the English translation of "Dungeons of the Black Tower".

Reads black-tower-en.docx and produces a structured Excel file with one row
per scene. Each row contains:
    ID       - scene number
    Text     - cleaned narrative
    Exits    - comma-separated outgoing scene IDs
    Items    - items mentioned in the scene (noun + offset code)
    Enemies  - enemies (with their stats) introduced in the scene
    Notes    - special remarks (e.g. relative-numbering exits "(+ 16)")

The book has 655 numbered scenes. A scene begins with a paragraph containing
only its number, separated by blank paragraphs from surrounding text.

The English translation is mechanical and slightly inconsistent: enemy stats
appear as either "Dexterity X Strength Y" or "Agility X Strength Y" or
"Skill X Strength Y" (and rarely "Stamina" instead of "Strength"). Item codes
in the source use both "(- N)" and "(+ N)" forms — both are item references,
not exits. Only standalone "(+ N)" without a preceding noun is treated as a
relative-exit note, per the spec.
"""

from __future__ import annotations

import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

from docx import Document
from openpyxl import Workbook
from openpyxl.styles import Alignment, Font
from openpyxl.utils import get_column_letter


# -- Source loading ----------------------------------------------------------


def load_source_lines(path: Path) -> list[str]:
    """Return a list of paragraph texts from the .docx file."""
    doc = Document(str(path))
    return [p.text for p in doc.paragraphs]


# -- Scene splitting ---------------------------------------------------------


SCENE_HEADER = re.compile(r"^\s*(\d+)\s*$")


@dataclass
class Scene:
    id: int
    raw_lines: list[str] = field(default_factory=list)

    @property
    def text(self) -> str:
        lines = [ln.rstrip() for ln in self.raw_lines]
        while lines and not lines[0].strip():
            lines.pop(0)
        while lines and not lines[-1].strip():
            lines.pop()
        return "\n".join(lines)


def split_scenes(lines: list[str]) -> list[Scene]:
    """Split paragraphs into ordered Scene objects.

    A scene begins with a paragraph that contains only the next expected ID.
    The introduction at the top of the book is discarded — collection starts
    once scene 1 is encountered, and only strictly incrementing IDs are
    accepted thereafter so stray numeric lines inside a scene body do not
    confuse the splitter.
    """
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
#   2. "- 123"            absolute, after dash / en-dash / em-dash
#   3. "123."             absolute, end-of-sentence number
#   4. "(+ 12)"           relative offset (positive only) — added as a note
#   5. "(- 12)"           item code — skipped from exits

ABS_PAREN = re.compile(r"\((\d+)\)")
ABS_DASH = re.compile(r"(?<!\d)[-–—]\s*(\d+)")
ABS_TRAIL = re.compile(r"(?<![\d.,])(\d+)\.")
ABS_INTRO = re.compile(
    r"\b(?:then|go to|go back to|back to|return to|returning to|turn to|turn to paragraph|"
    r"paragraph|reading paragraph|at paragraph)\s+(\d+)\b",
    re.IGNORECASE,
)
# Pattern 3 from spec: a bare number "XX" used as an exit. In the English
# source, the genuinely-uncaught bare case occurs almost exclusively in
# branched conditionals like "...then 463; if not - 593." where the first
# branch number is followed by ";". Other bare-number positions are
# already covered by ABS_INTRO (intro verbs) or ABS_TRAIL (trailing dot).
# Restricting to the ";" follower keeps recall high without injecting
# quantities ("1 gold", "Loyalty drops below 3") as fake exits.
ABS_BARE = re.compile(r"(?<![\w.,\-+(])\b(\d{1,3})\s*;")
REL_OFFSET = re.compile(r"\(\s*\+\s*(\d+)\s*\)")
ITEM_CODE = re.compile(r"\(\s*-\s*(\d+)\s*\)")


def extract_exits(text: str) -> tuple[list[str], list[str]]:
    """Return (exits, notes).

    exits: ordered, deduplicated list of exit scene IDs (as strings).
    notes: special remarks about relative-number references "(+ N)".
    """
    notes: list[str] = []
    skip_spans: list[tuple[int, int]] = []

    for m in REL_OFFSET.finditer(text):
        notes.append(f"relative +{m.group(1)}")
        skip_spans.append(m.span())
    for m in ITEM_CODE.finditer(text):
        skip_spans.append(m.span())

    def in_skip(span: tuple[int, int]) -> bool:
        return any(rs <= span[0] and span[1] <= re_ for rs, re_ in skip_spans)

    found: list[str] = []
    seen: set[str] = set()

    def add(num_str: str) -> None:
        if num_str not in seen:
            seen.add(num_str)
            found.append(num_str)

    for m in ABS_PAREN.finditer(text):
        if in_skip(m.span()):
            continue
        add(m.group(1))

    for m in ABS_DASH.finditer(text):
        if in_skip(m.span()):
            continue
        add(m.group(1))

    for m in ABS_TRAIL.finditer(text):
        if in_skip(m.span()):
            continue
        add(m.group(1))

    for m in ABS_INTRO.finditer(text):
        if in_skip(m.span()):
            continue
        add(m.group(1))

    # Pattern 3: bare numbers followed by a semicolon, e.g. the first
    # branch of "...then 463; if not - 593."
    for m in ABS_BARE.finditer(text):
        if in_skip(m.span()):
            continue
        add(m.group(1))

    return found, notes


# -- Enemy extraction --------------------------------------------------------

# Enemy name lines are written in capital letters, e.g.:
#     FIRST WOODCUTTER
#     GREEN KNIGHT
#     CHIEF OF THE GUARD
# Words like "OF", "THE" must be allowed in the middle of multi-word names.
CAPS_LINE = re.compile(r"^[A-Z][A-Z\- ]*[A-Z]$|^[A-Z]$")
STAT_LINE = re.compile(
    r"(Dexterity|Agility|Skill)\s+(\d+)\s+(Strength|Stamina)\s+(\d+)"
    r"(?:\s+Loyalty\s+(\d+))?"
)


def extract_enemies(text: str) -> list[str]:
    """Detect enemies by the paired pattern:
        line N   - all-caps name (one or more words)
        line N+1 - "(Dexterity|Agility|Skill) X (Strength|Stamina) Y [Loyalty Z]"
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
        _skill_label, skill_val, _str_label, str_val, loy_val = m.groups()
        # Spec: always emit "Dexterity" regardless of whether the source
        # used "Dexterity", "Agility", or "Skill". Strength/Stamina is
        # likewise normalized to "Strength".
        descr = f"{name} (Dexterity {skill_val}, Strength {str_val}"
        if loy_val is not None:
            descr += f", Loyalty {loy_val}"
        descr += ")"
        enemies.append(descr)
    return enemies


# -- Item extraction ---------------------------------------------------------

# Items in the source are written as ordinary noun phrases followed by an
# offset code in parentheses, e.g. "an elegant bronze whistle (- 214)" or
# "a tinderbox (+ 111)". We anchor on the offset and grab a short noun phrase
# (1–4 words: ASCII letters, optional possessive 's, optional hyphenation)
# that sits immediately before it.

ITEM_PATTERN = re.compile(
    r"((?:[A-Za-z]+(?:['’]s)?(?:-[A-Za-z]+)?\s+){0,3}"
    r"[A-Za-z]+(?:['’]s)?(?:-[A-Za-z]+)?)"
    r"\s*\(\s*[+\-]\s*(\d+)\s*\)"
)

STOP_WORDS = {
    "a", "an", "the",
    "and", "or", "but",
    "of", "in", "on", "at", "with", "from", "by", "to", "for",
    "into", "onto", "upon", "off",
    "is", "was", "are", "were", "be", "been", "being",
    "has", "have", "had",
    "this", "that", "these", "those",
    "his", "her", "your", "my", "their", "our", "its",
    "him", "she", "you", "they", "we", "i",
    "as", "if", "so", "then", "than",
    "not", "no",
    "only", "just", "very", "also",
    "can", "could", "will", "would", "should", "may", "might", "must",
    "do", "does", "did",
    "one", "two", "three", "four", "five",
    "some", "any", "all", "each",
    "now", "here", "there",
    "out", "up", "down",
}


def extract_items(text: str) -> list[str]:
    items: list[str] = []
    seen: set[str] = set()
    for m in ITEM_PATTERN.finditer(text):
        phrase = " ".join(m.group(1).split())
        sign_match = re.search(r"\(\s*([+\-])\s*\d+", text[m.start() : m.end()])
        sign = sign_match.group(1) if sign_match else "-"
        offset = m.group(2)

        words = phrase.split()
        while words and words[0].lower() in STOP_WORDS:
            words.pop(0)
        if not words:
            continue
        cleaned = " ".join(words)
        label = f"{cleaned} ({sign}{offset})"
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

    # Scene-specific exit overrides: where an item code "(- N)" also functions
    # as a navigable exit (e.g. when handing the item over advances the story).
    EXIT_OVERRIDES: dict[int, list[str]] = {
        296: ["223"],
    }
    NOTE_OVERRIDES: dict[int, list[str]] = {
        520: ["relative -25"],
    }

    for scene in scenes:
        text = scene.text
        exits, notes = extract_exits(text)
        for extra in EXIT_OVERRIDES.get(scene.id, []):
            if extra not in exits:
                exits.append(extra)
        for extra_note in NOTE_OVERRIDES.get(scene.id, []):
            if extra_note not in notes:
                notes.append(extra_note)
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

    widths = {1: 6, 2: 90, 3: 25, 4: 40, 5: 40, 6: 30}
    for col_idx, width in widths.items():
        ws.column_dimensions[get_column_letter(col_idx)].width = width

    for row in ws.iter_rows(min_row=2, max_row=ws.max_row):
        for cell in row:
            cell.alignment = Alignment(wrap_text=True, vertical="top")

    wb.save(path)


# -- Entry point -------------------------------------------------------------


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python extract_scenes_en.py <input_docx_file>")
        print("Example: python extract_scenes_en.py black-tower-en.docx")
        sys.exit(1)

    input_path = Path(sys.argv[1])
    if not input_path.exists():
        print(f"Error: File '{input_path}' not found")
        sys.exit(1)

    if not input_path.suffix.lower() == ".docx":
        print(f"Error: Input file must be a .docx file")
        sys.exit(1)

    # Generate output filename: replace .docx with _scenes.xlsx
    output_path = input_path.with_name(input_path.stem + "_scenes.xlsx")

    print(f"Reading from: {input_path}")
    print(f"Writing to: {output_path}")

    lines = load_source_lines(input_path)
    scenes = split_scenes(lines)
    print(f"Parsed {len(scenes)} scenes")
    if scenes:
        first, last = scenes[0].id, scenes[-1].id
        print(f"First scene: {first}, last scene: {last}")
        ids = {s.id for s in scenes}
        missing = [i for i in range(1, last + 1) if i not in ids]
        if missing:
            print(f"WARNING: missing scene IDs: {missing}")
    write_excel(scenes, output_path)
    print(f"Successfully wrote {output_path}")


if __name__ == "__main__":
    main()
