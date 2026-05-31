# Project Overview

This project extracts scenes from "Подземелья Черного замка" (Dungeons of the Black Tower) by Dmitry Braslavsky (1991) - a Russian-language gamebook. The source material is a "choose your own adventure" style game where numbered scenes link to each other through numbered exits.

# Core Assets

- `black-tower.txt`: Primary source - extracted text content containing ~821 numbered game scenes in Russian

# Gameplay

The player starts from the initial scene and moves through the scenes until they either die or reach the final scene.
The player has a backpack where they can store items. Items take part in determining possible transitions to other scenes. 
The player can fight enemies and use spells. They have personal attributes.

## Hero's Attributes

- ЛОВКОСТЬ
- СИЛА
- ОБАЯНИЕ
- УДАЧА
- МОЩНОСТЬ УДАРА
- ЛОЯЛЬНОСТЬ

All the attributes are positive integers.

## Hero's Spells

They named "заклятья"

- ЗАКЛЯТИЕ ЛЕВИТАЦИИ
- ЗАКЛЯТИЕ ОГНЯ
- ЗАКЛЯТИЕ ИЛЛЮЗИИ
- ЗАКЛЯТИЕ ЛОВКОСТИ
- ЗАКЛЯТИЕ СЛАБОСТИ
- ЗАКЛЯТИЕ КОПИИ
- ЗАКЛЯТИЕ ИСЦЕЛЕНИЯ
- ЗАКЛЯТИЕ ПЛАВАНИЯ

## Money

Player operates with gold coins (золотые). This is a positive integer.

# Scene Structure

The book contains scenes. This is chunks of text that are linked together by numbered exits. The scenes are placed in the source file subsequently, starting with 1. Some scenes lead to the hero's death, and they do not have exits (game over). The last scene is the final scene of the game and also has no exits (victory).

Each scene in the gamebook has:

## Scene ID

A positive integer that uniquely identifies the scene. This number precedes the scene. It is separated from the scene text by two blank lines. It is also separated from the previous scene by two blank lines. 

## Scene Description

Russian-language narrative text describing the scene. The text contains important information about the scene, such as the hero's location, the items mentioned, the enemies present, and exits leading to other scenes.

### How to identify exists

Exists are positive integers specially formatted. You need to indentify them in the text. Here are the patterns (X is a number):
1. "(XXX)", for example, (564)
2. "- XXX", for example, - 182
3. "XX", for example, 58
4. a rare example of relative numbering: "(+ XX)", for example, (+ 16). The relative number can be positive only. In this case, make a special note in the output Excel file.

### How to identify enemies

There are two signs that precisely determine the description of the enemy in the text:

1. It is stated at the new line with capital letters. For example, "ГИЕНА" or "ЗЕЛЕНЫЙ РЫЦАРЬ".
2. The second line always contains this pattern: "Ловкость X Сила X" (X is a number).

In a scene might be mentioned several enemies, and each of them is described separately.

### How to identify items

They are always nouns, and the text explains that you can either take them with you or use them. Also, it’s not uncommon that having some item available allows a transition to another scene.

# Text Processing Challenges

- All content is in Russian (Cyrillic script)
- Always ensure UTF-8 encoding when working with text

## Development Environment

**Language**: Python 3.10+

**Common Python libraries used**:
- `openpyxl` or `pandas`: Excel file creation
- Standard library: `re` for regex pattern matching, text processing

# Your Goal

Extract all scenes from the source text into a structured Excel file.

- **ID**: Scene unique identifier
- **Text**: Scene description in Russian
- **Exits**: Comma-separated list of scene IDs reachable from this scene (with conditions if present)
- **Items**: List of items (CAPITAL LETTERS words) mentioned in the scene
- **Enemies**: List of enemies mentioned in the scene.