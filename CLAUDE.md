# Project Overview

This project contains "Black Tower" - a Russian-language board game in the style of Dungeons & Dragons, stored in `black_tower_91.pdf`.

# Scene Description

The game is organized into **scenes**, each with:
- **Unique ID**: Printed above the scene description. This is a positive integer. Page numbers ARE NOT scenes IDs.
- **Description**: Main text of the scene (in Russian)
- **Exits**: Numbers in text in format like "- 94" or "(613)".They refer for other scenes by their IDs
- **Enemies**: A scene may contain from 0 to several enemies. Explanation about an enemy is separated into a paragraph. Name of an enemy is printed in CAPITAL LETTERS. For example, "ПЕРВЫЙ ГОБЛИН" or "ОБОРОТЕНЬ". The next line contains two enemy characteristics: "Мастерство" and "Выносливость" with their values (positive integers)
- **Spells**. The scene description may contain spells. They are also printed in CAPITAL LETTERS. The list of spells: ЗАКЛЯТИЕ ОГНЯ, ЗАКЛЯТИЕ ЛЕВИТАЦИИ, ЗАКЛЯТИЕ ИЛЛЮЗИИ, ЗАКЛЯТИЕ СИЛЫ, ЗАКЛЯТИЕ СЛАБОСТИ, ЗАКЛЯТИЕ КОПИИ, ЗАКЛЯТИЕ ПЛАВАНИЯ, ЗАКЛЯТИЕ ИСЦЕЛЕНИЯ
- **Characteristics**. The scene description may contain characteristics of the player: МАСТЕРСТВО, ВЫНОСЛИВОСТЬ, УДАЧА
- **Items**: Important objects printed in CAPITAL LETTERS

The actual content of scenes starts on page 8.

# Working with the Game Content

## Scene Navigation
- Each scene can have one or several exits, except of the first and the last scenes
- Exit numbers refer to the unique IDs of other scenes
- This creates a graph structure of interconnected scenes.
- The start scene has ID = 1, the last scene has ID = 617, and some scenes lead to game over.

## Language
- All content is in Russian
- When parsing or analyzing text, ensure proper UTF-8/Cyrillic encoding support
- You can use Python scripts in this folder to extract and process the text content and solve issues with encoding and spacing.

# Your Tasks
- ✅ Extract 10 random scenes from the PDF, ensuring correct decoding of Russian text
- ✅ The extracted scenes should include all items mentioned in **Scene Description**
- ✅ use Russian dictionary to validate all extracted scenes and ensure they contain valid Russian words without missed spaces and without shuffled letters

## Task Completion Status (2026-04-10)

**COMPLETED**: Successfully extracted and validated 10 random scenes from the PDF.

**Results:**
- **10/10 scenes** pass validation with correct Cyrillic encoding
- **All character mappings fixed** including the missing ǰ (U+01F0) → И
- **Exit detection working** for all scenes with connections
- **Enhanced spacing algorithm** using Russian dictionary (288 words)

**Output Location:** `final_10_scenes/` directory
- Individual scene files: `scene_XXX.txt`
- Extraction report: `EXTRACTION_REPORT.txt`

**Selected Random Scenes:** 26, 90, 105, 115, 143, 229, 251, 282, 559, 605

**Improvements Applied:**
1. Fixed missing character mapping: ǰ (U+01F0) → И
2. Enhanced spacing algorithm with comprehensive Russian dictionary
3. Full validation system for encoding and text quality
4. Structured extraction of exits, enemies, spells, and characteristics

# Parsing the PDF

**IMPORTANT: Cyrillic Encoding Issue**

The PDF has an encoding problem where Cyrillic characters are extracted as Latin Extended-B characters (Unicode range U+01E8-U+0227). This must be fixed after extraction.

**Solution**: Use the `black_tower_lib.py` library which contains the complete character mapping to fix the encoding.

**Complete Extraction Workflow**:
1. Extract text using `pymupdf` (fitz): `page.get_text()`
2. Apply character mapping from `build_cyrillic_map()` function
3. Fix missing spaces between merged words using `fix_spacing()`
4. Extract scene IDs, exits, and items from corrected text

**Character Mapping Pattern**:
- Garbled: Latin Extended-B characters (Ǫ, ȣ, ȗ, Ȗ, etc.)
- Correct: Cyrillic characters (В, ы, п, о, etc.)
- Lowercase Russian а-я: U+0208-U+0227
- Uppercase Russian А-Я: U+01E8-U+0207

See `black_tower_lib.py` for the full character mapping table.

**Spacing Issue**: 
After encoding fix, some words are merged together without spaces (e.g., "Егообрамляетзолотаярамасизображениямисцен" should be "Его обрамляет золотая рама с изображениями сцен"). This requires:
- Manual correction for critical text
- Pattern-based word boundary detection for bulk processing
- Reference to properly spaced examples (see `scene_279_sample.txt`)

## Russian symbols validation
You need to ensure that all extracted scenes are correctly decoded and contain valid Russian characters.

## Creating Navigation Tools
When building scene navigation or game analysis tools:
- Parse scene IDs and map the scene graph
- Extract exit connections to build the game flow
- Identify and catalog items across scenes
- Consider creating a scene index or game map

## Data Extraction Pattern

Each scene contains:
- Scene unique ID (printed above description)
- Scene description text (in Russian)
- Exit numbers → target scene IDs
- Items (words in CAPITAL LETTERS in the description)

**Exit Detection Patterns** (search in corrected Russian text):
- "переходите к [число]" or "переходите на [число]"
- "идите к [число]" or "идите на [число]"  
- Numbered choices: "1) ..." with scene references
- "сцена [число]" or "эпизод [число]"
- Final number at end of scene (often "-" before it): "- 502"

## Production Files

**Main Scripts:**
- `extract_scenes.py`: ✅ Main extraction script with command-line interface
  - Usage: `python extract_scenes.py` (extracts 10 random scenes)
  - Options: `--all` (all scenes), `--scene N` (specific scene), `--count N` (N random scenes)

- `black_tower_lib.py`: ✅ Core library with reusable functions
  - `build_cyrillic_map()` - Character mapping dictionary
  - `fix_encoding()` - Apply encoding fixes
  - `fix_spacing()` - Fix merged words with Russian dictionary
  - `extract_scene_from_pdf()` - Extract scene from PDF
  - `validate_scene()` - Validate text quality
  - `extract_scene_info()` - Parse exits, enemies, spells

**Reference Files:**
- `scene_279_sample.txt`: ✅ Correctly decoded sample scene with proper spacing (verified correct)
- `extract_10_scenes_final.py`: Original working script (kept as backup)

## Scene 279 Example

Original garbled text:
```
Ǫȣ ȗȖȌȝȖȌȐȚȍ Ȓ ȏȍȘȒȈȓț, ȕȖ ȕȍ ȏȈȔȍȟȈȍȚȍ ȕȐȟȍȋȖ
ȕȍȖȉȣȟȕȖȋȖ. ǭȋȖȖȉȘȈȔȓȧȍȚȏȖȓȖȚȈȧȘȈȔȈșȐȏȖȉȘȈȎȍȕȐȧȔȐșȞȍȕ
Ȑȏ ȎȐȏȕȐ ȋȈȘȗȐȑ.  ǵȖ ȒȈȒ șȓȍȌțȍȚ ȕȈșȓȈȌȐȚȤșȧ ȗȘȍȒȘȈșȕȣȔ
ȖȘȕȈȔȍȕȚȖȔȊȈȔȕȍȌȈȦȚ - 502.
```

After encoding fix (words still merged):
```
Вы подходите к зеркалу, но не замечаете ничего
необычного. Егообрамляетзолотаярамасизображениямисцен
из жизни гарпий.  Но как следует насладиться прекрасным
орнаментомвамнедают - 502.
```

Final corrected text (with proper spacing):
```
Вы подходите к зеркалу, но не замечаете ничего
необычного. Его обрамляет золотая рама с изображениями сцен
из жизни гарпий.  Но как следует насладиться прекрасным
орнаментом вам не дают - 502.
```

**Translation**: "You approach the mirror, but notice nothing unusual. It is framed by a golden frame with images of scenes from the life of harpies. But to properly enjoy the beautiful ornament, you are not allowed - 502."

**Exit**: Scene 502 (pattern: "- 502" at end)
