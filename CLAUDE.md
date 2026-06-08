# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This project extracts scenes from "Подземелья Черного замка" (Dungeons of the Black Tower), a 1991 Russian gamebook by Dmitry Braslavsky. The codebase processes both Russian and English versions of the text, parsing numbered scenes into structured Excel files.

The gamebook is a "choose your own adventure" style game with ~655 numbered scenes that link to each other through numbered exits. Players navigate scenes, collect items, fight enemies, and use spells.

## Core Files

### Source Documents
- `black-tower.txt` - Russian source text (~821 scenes)
- `black-tower.docx` - Russian source in Word format
- `black-tower-en.docx` - English translation
- `black_tower_91.pdf` - Original PDF scan

### Extraction Scripts
- `extract_scenes.py` - Extracts Russian scenes from `black-tower.txt`
- `extract_scenes_en.py` - Extracts English scenes from `black-tower-en.docx`

### Output Files
- `black_tower_scenes.xlsx` - Structured Russian scene data
- `black_tower_scenes_en.xlsx` - Structured English scene data

### Specifications
- `spec-ru.md` - Russian version extraction requirements
- `spec-en.md` - English version extraction requirements

## Running the Scripts

```bash
# Activate virtual environment
.venv/Scripts/activate  # Windows
source .venv/bin/activate  # Unix

# Extract Russian scenes
python extract_scenes.py

# Extract English scenes
python extract_scenes_en.py
```

## Dependencies

Core packages (installed in `.venv`):
- `openpyxl` - Excel file creation and manipulation
- `python-docx` - Reading Word documents (.docx)
- `pandas` - Data processing (optional, openpyxl is primary)

Install missing dependencies:
```bash
pip install openpyxl python-docx pandas
```

## Text Processing Architecture

Both extraction scripts follow the same pipeline but differ in language-specific patterns:

### 1. Scene Splitting
Scenes are identified by a standalone number on a line, separated by blank lines. The splitter uses strict sequential ordering (1, 2, 3...) to avoid false positives from numbers inside scene text.

### 2. Exit Extraction
Exits are scene IDs in specific formats:
- **Russian**: `(123)`, `- 123`, `123.`
- **English**: Same patterns plus handling of `(+ N)` relative offsets and `(- N)` item codes

**Critical distinction**:
- Absolute exits: `(123)`, `- 123` → navigable scene references
- Relative offsets: `(+ 16)` → noted but not exits
- Item codes: `(- 214)` (Russian), `(+ 111)` or `(- 111)` (English) → item references when preceded by nouns

### 3. Enemy Extraction
Enemies are identified by a two-line pattern:
```
ALL-CAPS NAME
Ловкость X Сила Y [Лояльность Z]  # Russian
Dexterity/Agility/Skill X Strength/Stamina Y [Loyalty Z]  # English
```

**English note**: The translation is inconsistent—enemy stat labels vary (Dexterity vs Agility vs Skill, Strength vs Stamina). The regex handles all variants.

### 4. Item Extraction
Items are noun phrases followed by offset codes:
- **Russian**: `золотой свисток (- 156)` → extracts "золотой свисток"
- **English**: `elegant bronze whistle (- 214)` → extracts "elegant bronze whistle"

The extractor anchors on the offset code and captures 1-4 preceding words, filtering out stop words.

## Key Implementation Details

### Scene Header Regex
```python
SCENE_HEADER = re.compile(r"^\s*(\d+)\s*$")
```
Matches lines containing only a scene number. Used in strict-sequence mode to avoid false matches.

### Stop Words Filtering
Both scripts maintain extensive stop-word lists (Russian: prepositions, articles, common verbs; English: articles, prepositions, auxiliary verbs) to clean extracted items.

### Encoding
Always use UTF-8 encoding. Russian text requires proper Cyrillic support:
```python
text = SOURCE.read_text(encoding="utf-8")
```

### Excel Output Structure
Both scripts produce identical Excel layouts:
- **ID**: Scene number
- **Text**: Full scene narrative
- **Exits**: Comma-separated scene IDs
- **Items**: Semicolon-separated items with offset codes
- **Enemies**: Semicolon-separated enemies with stats
- **Notes**: Special remarks (relative numbering, warnings)

Column widths: ID (6), Text (90), Exits (25), Items (40), Enemies (40), Notes (30)

## Pattern-Matching Philosophy

The scripts intentionally avoid NLP or "smart" parsing. They rely exclusively on the explicit formatting conventions documented in `spec-ru.md` and `spec-en.md`. This keeps extraction precise and predictable.

**Do not**:
- Add semantic analysis for item detection
- Infer scene exits from narrative context
- Use spaCy/NLTK for entity recognition

**Do**:
- Trust the documented patterns (caps lines, offset codes, numbered references)
- Validate output against expected scene counts (~655-821 scenes)
- Report missing scene IDs as warnings

## Game Mechanics Context

Understanding the game structure helps interpret extraction edge cases:

### Player Attributes
- Russian: ЛОВКОСТЬ, СИЛА, ОБАЯНИЕ, УДАЧА, МОЩНОСТЬ УДАРА, ЛОЯЛЬНОСТЬ
- English: SKILL, STRENGTH, CHARM, LUCK, STRIKE POWER, LOYALTY

### Spells (Заклятья)
- LEVITATION, FIRE, ILLUSION, AGILITY, WEAKNESS, COPY, HEALING, SWIMMING

### Currency
Gold coins (золотые) - positive integers

### Scene Types
- **Normal scenes**: Have 1+ exits
- **Death scenes**: No exits (game over)
- **Victory scene**: Final scene, no exits (scene ~655 or ~821)

## Common Issues

### Missing Scenes
If extraction reports missing scene IDs, check:
1. Was the source file truncated?
2. Does a scene header contain extra whitespace or punctuation?
3. Are there scenes with non-sequential numbering?

### Incorrect Exit Counts
If exits seem wrong:
1. Check for item codes `(- N)` being mistaken for exits
2. Verify relative offsets `(+ N)` are flagged in Notes column, not Exits
3. Look for exit patterns inside quoted dialogue (should still be extracted)

### Empty Item Lists
Items require offset codes. If items are missing:
1. Confirm they follow the pattern `noun_phrase (± N)`
2. Check if stop words need updating
3. Verify the item actually has an offset in the source text

## Version Control Notes

- `.venv` is gitignored (recreate with `python -m venv .venv`)
- Excel output files are tracked (they're the deliverable)
- Source documents (`.txt`, `.docx`, `.pdf`) are tracked
