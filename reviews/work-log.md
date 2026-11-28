# Work log

Who wrote and checked what, with which model, and how much was checked.

## 2026-11-28: community section 社群攻略

- Writer: Claude Opus 5.5. Sources: the 11 character guides of 叫我棉被 (with 零号攻略组) that the owner chose on Bilibili; `pipeline/scout_guides.py read` fetched each video's description, tags, pinned comment with its picture and the creator's replies.
- Transcription: each one-image summary (9 pinned pictures) and each card frame of the 小吱 and 娜娜莉 videos (8 frames) was transcribed twice, independently, by Gemini Hydrogen (high) and Gemini Argon (medium). Every field where the two differed, and every Arc list's operators, was settled by the writer against the picture at full resolution. No case was found where both readers agreed on a wrong value (one suspected case, a main stat, was right); each reader was wrong alone at least once, mostly on the operators between Arcs (`>` read where none is printed, `/` read for an unranked list).
- Passive numbering: 天赋1 and 天赋2 checked against the Exe guide, which names both passives on screen (Gemini Hydrogen read the video; the order matches the game data 1.5.4).
- Names: every character, Arc and cartridge set resolves against the site's pages and records (`pipeline/build_community.py` stops on an unknown name); Exe and Dotted Horizon from nanoka.cc 1.5.4 (`character.json`, `weapon.json`, the four `1074.json`), cartridge sets from the four `console.json`.
- Prose ledger: the rubric change had every unit of the site read again (6,241 units, reader gpt-6.2-sol through Codex). 100 flagged: the community notes and caveats were rewritten and the team tables restructured so that each table's header names the creator; 58 flags on other pages were accepted with reasons (names-page provenance where editions differ, lone secondary sources named in the sentence, notation of empty cells), none of them a change to those pages.
- Not done: the creator's replies were read but none changes a figure; the videos' narration was not transcribed.

## 2026-11-28: 零号攻略组's Esper Cycle video on the fact pages

- Writer: Claude Opus 5.5. `systems/esper-cycles` and `systems/combat` (en, zh-tw, ja, ko; zh-cn by script) take from `BV1E97868EJ7`: reaction base damage at level 80, the Cycle Intensity factor, how the character whose stats count is fixed, Hexed and Stain scaling, Scorch and Nova stacking, gauge sources, Mental RES, energy sharing. Each figure was read by the writer from the creator's captions in the frames, not from speech recognition. The closed-test video `BV1TLoxBtEZF` is not cited (see `SOURCES.md`).
- Checked: the writer against the frames; the prose ledger for the changed units; `pnpm verify`.
