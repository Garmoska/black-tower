# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This project contains "Black Tower" - a Russian-language board game in the style of Dungeons & Dragons, stored in `black_tower_91.pdf`.

## Game Structure

The game is organized into **scenes**, each with:
- **Unique ID**: Printed above the scene description
- **Description**: Main text of the scene (in Russian)
- **Exits**: Numbered options that reference other scene IDs
- **Items**: Important objects printed in CAPITAL LETTERS

## Working with the Game Content

### Scene Navigation
- Each scene can have one or several exits
- Exit numbers refer to the unique IDs of other scenes
- This creates a graph structure of interconnected scenes

### Items
- Items are marked in CAPITAL LETTERS within scene descriptions
- These are significant game objects that players can interact with

### Language
- All content is in Russian
- When parsing or analyzing text, ensure proper UTF-8/Cyrillic encoding support

## Common Tasks

### Scene Extraction to Excel

See `scenes-extration.md` for the specification. The goal is to extract all scenes from `black_tower_91.pdf` into an Excel document with columns:
- **ID**: Scene unique identifier
- **Text**: Scene description (in Russian)
- **Exits**: Scene IDs that can be visited next (include conditions if present)
- **Items**: Items mentioned in the scene description (marked in CAPITAL LETTERS)

**Key Scripts**:
- `complete_fix.py`: ✅ Production-ready script with complete 65-character Cyrillic mapping
- `extract_scenes.py`: Initial extraction script (produces garbled Cyrillic, superseded)
- `create_scene_279_clean.py`: Example of fixing encoding + spacing for a single scene
- Output: `black_tower_scenes.xlsx` (currently 821 scenes extracted, encoding needs fix)

**Workflow for Complete Extraction**:
1. Use `complete_fix.py` as base for character mapping
2. Extract all scenes with scene IDs
3. Apply encoding fix to each scene's text
4. Apply spacing corrections (manual or pattern-based)
5. Re-run exit detection on corrected Russian text
6. Extract items (CAPITAL LETTERS)
7. Export to Excel with all columns populated

**Known Issues**:
- Exit detection failed in initial extraction due to encoding issues
- Words merged together after PDF extraction (spacing issue)
- Both issues are now understood and solvable with the complete workflow above

### Parsing the PDF

**IMPORTANT: Cyrillic Encoding Issue**

The PDF has an encoding problem where Cyrillic characters are extracted as Latin Extended-B characters (Unicode range U+01E8-U+0227). This must be fixed after extraction.

**Solution**: Use `complete_fix.py` which contains the complete character mapping to fix the encoding.

**Complete Extraction Workflow**:
1. Extract text using `pymupdf` (fitz): `page.get_text()`
2. Apply character mapping from `build_complete_cyrillic_map()` function
3. Fix missing spaces between merged words
4. Extract scene IDs, exits, and items from corrected text

**Character Mapping Pattern**:
- Garbled: Latin Extended-B characters (Ǫ, ȣ, ȗ, Ȗ, etc.)
- Correct: Cyrillic characters (В, ы, п, о, etc.)
- Lowercase Russian а-я: U+0208-U+0227
- Uppercase Russian А-Я: U+01E8-U+0207

See `complete_fix.py` for the full 65-character mapping table.

**Spacing Issue**: 
After encoding fix, some words are merged together without spaces (e.g., "Егообрамляетзолотаярамасизображениямисцен" should be "Его обрамляет золотая рама с изображениями сцен"). This requires:
- Manual correction for critical text
- Pattern-based word boundary detection for bulk processing
- Reference to properly spaced examples (see `scene_279_sample.txt`)

### Creating Navigation Tools
When building scene navigation or game analysis tools:
- Parse scene IDs and map the scene graph
- Extract exit connections to build the game flow
- Identify and catalog items across scenes
- Consider creating a scene index or game map

### Data Extraction Pattern

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

## Example Files

- `scene_279_sample.txt`: ✅ Correctly decoded sample scene with proper spacing (verified correct)
- `character_mapping.txt`: Character mapping reference (first 20 mappings discovered)
- `complete_fix.py`: ✅ Production-ready encoding fix script with full 65-character map
- `create_scene_279_clean.py`: Example implementation of encoding fix + spacing for one scene

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
