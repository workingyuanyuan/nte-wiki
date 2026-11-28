# The pipeline: game text from records, and writers' references

Read this before running a script in this folder, translating a page into Japanese or Korean, or adding a portrait. `../AGENTS.md` holds the rules and the commands every change needs; `../SOURCES.md` the sources; each script's header says what it reads and writes.

## Commands

```
# game text from records (after any zh-tw change, in this order; no slug = everything)
python3 pipeline/fetch_nanoka.py                                              # nanoka.cc files to pipeline/cache/
CHROMIUM=<chrome-headless-shell> node pipeline/fetch_everness.mjs $(python3 pipeline/everness_keys.py)   # Traditional Chinese
python3 pipeline/build_records.py [slug ...]                                  # records/
python3 pipeline/build_records.py --voices [slug ...]                         # records/voices/
uv run --with opencc-python-reimplemented pipeline/build_records.py --monsters   # records/anomalies.json (after fetch_nanoka.py --monsters)
uv run --with opencc-python-reimplemented pipeline/build_records.py --lists      # records/lists.json (after fetch_nanoka.py --lists and fetch_everness.mjs)
uv run --with opencc-python-reimplemented scripts/to-zh-cn.py
python3 pipeline/build_pages.py [slug ...]
python3 pipeline/build_community.py                                           # records/community/ -> community/ in every language (after to-zh-cn.py)
```

## Fixed renderings

- Attributes in Chinese: 光 Cosmos, 靈 Anima, 咒 Incantation, 魂 Psyche, 暗 Chaos, 相 Lakshana. Arc types in Chinese are followed by the English in parentheses, 固態 (Solid); 聚合 (Condensate) replaced the earlier 凝聚態.
- Core terms: Arc 弧盤 / 아크, Board ボード / 보드, Esper Cycle 異能連環 / 에스퍼 사이클, Console ギア / 콘솔, Cartridge 駆動コア / 카트리지, Awakening 覚醒 / 각성; skill slots 通常攻撃, バイレールスキル, EXレール終結, サポートスキル / 일반 공격, 바이레일 스킬, 울티메이트, 서포트 스킬.

## Portraits

- Portraits go in `public/art/characters/<slug>.webp`, cropped from the official site's mobile poster (left 95, top 150, width 560, height 686 of the 750×836 image). Characters without a profile on the official site have no portrait.

## Folders

| Path | Role |
| --- | --- |
| `pipeline/`, `records/` | Game text: fetch (`pipeline/cache/`, not committed), records, and the scripts that write it into the pages |
| `assets/fonts/`, `scripts/subset-font.mjs` | Pixel font source with its licence, and the subsetter |

## Fonts

- The pixel font is Fusion Pixel 12px (SIL OFL; Korean glyphs from Galmuri, licences in `assets/fonts/LICENSES/`), used at 12, 24 or 36 px only. `scripts/subset-font.mjs` cuts it to the characters the pages use before every build and writes `public/fonts/pixel*.woff2`, which are not committed.
- `:root[lang]` swaps in the body fonts of each script, so punctuation and kana sit right; every stack also names fonts of the other scripts, because the names page mixes all five in one table.

## Japanese and Korean

- Japanese and Korean pages: translated from the English page with the same facts, headings, tables and links; Japanese である調, Korean 한다체. Names come from the Japanese and Korean game data for in-game text and from the official `/jp/` and `/kr/` notices for versions, events, Boards and outfits; a name with neither stays in English. Those notices write UTC+9; the pages keep the UTC+8 times of the English pages. Every page lists the Japanese and Korean counterparts of the notices and data files it cites.

## What the list scripts leave out

- Agent's choices on the lists (2026-11-26): mod parts whose English, Japanese or Korean text is still the Simplified original are left out; dishes that characters prefer and achievement rewards are left out.
