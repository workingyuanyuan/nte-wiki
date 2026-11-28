# Rules for agents maintaining this site

An unofficial wiki for the game Neverness to Everness (NTE, 異環), at `https://yuanaruru.com/nte-wiki/`. The rules in `../AGENTS.md` apply; this file holds what is specific to this site.

Read before the work: `SOURCES.md` before fetching a source or taking game text from one (what each allows, how to read it, what each kind of game text is taken from, verified pitfalls); `pipeline/README.md` before running a pipeline script, translating into Japanese or Korean, or adding a portrait; `upstream/README.md` when `pnpm upstream` reports a difference, a version changes or a Board opens; `../COMMUNITY.md` before working on `community/` and when a version lands. The question list and test results are in `tests/agent-eval/`.

## Decisions

By the owner unless marked `agent`.

- Languages: English, Traditional Chinese (`/zh-tw/`), Simplified Chinese (`/zh-cn/`, written by script from `zh-tw`; 2026-11-18), Japanese (`/ja/`) and Korean (`/ko/`; 2026-11-22), the last two translated from the English pages by delegates.
- Primary source: the global official site `nte.perfectworld.com`, readable with a plain HTTP fetch. The Taiwan site `nte.iwplay.com.tw` is used only for Traditional Chinese names. Mainland China is not covered.
- One clock: dates follow the global official site in UTC+8, stated once in the home page caveat and in `llms.txt`, with no label of the service region beside each date.
- Game data (2026-11-19): the versioned game data that nanoka.cc publishes (`static.nanoka.cc/nte/<version>/`) is the source of in-game text: names, Arc stats and effects, Cartridge sets, Awakenings, base stats, materials, vehicles, properties, skill multipliers. Only released content goes in. Check samples against mysqil, Everness and the official notices, take a bounded number of files, and do not crawl: nanoka.cc and everness.info carry `ai-train=no` and block AI crawlers.
- Game text is shown as the game writes it, in each language's own edition, never paraphrased (2026-11-23 to 2026-11-26): character archives, voice lines, outfit descriptions, the descriptions of Arcs and progression materials, anomaly files and enemy manual entries, and the names and descriptions on the item and achievement lists. English, Simplified Chinese, Japanese and Korean come from the nanoka.cc files; Traditional Chinese from everness.info, whose text is the Taiwan localisation. Remove text when the publisher asks.
- Traditional Chinese is never converted from Simplified with OpenCC, with one exception (2026-11-25): text that no Traditional source has (anomaly stories, enemy manual entries, most achievements) is made from the Simplified game text until a Traditional source has it, then replaced.
- Game text is written into the pages by script from records (2026-11-23); those pages and parts are not edited by hand.
- Official character introductions (2026-11-24): their facts (post, team, workplace, named weapon or companion) go in a Role row of the Profile table, in each language's wording; the descriptions of character and manner are left out. No sentence reports what the introduction says.
- Anomaly files come from the nanoka.cc monster files, not from GameKee's player transcriptions: GameKee's user agreement (4.5) forbids copying and compiling its content.
- The anomaly list (2026-11-26) has one row per anomaly commission in the nanoka.cc monster list, those without an archive file included; other commissions are not listed. A character whose archive the game has not opened gets no archive page.
- Character pages describe skills. Skill names and effects come from Prydwen and are checked against Game8; damage values, tier lists and team builds are not copied; teams and builds appear only under `community/`. Each page ends with the per-level values of its four skills from the game data (2026-11-22).
- Guide sites may supply a fact that the official sources lack when at least two of them agree, and the page names them in `sources`. A fact from one guide site, from the NGA forum or from the Bilibili channel 零号攻略组 alone is attributed in the sentence (2026-11-21).
- Community section 社群攻略 (2026-11-28): first sources are the character guides of 叫我棉被 with 零号攻略组 on Bilibili, chosen by the owner; `pipeline/build_community.py` writes `community/` in every language from `records/community/`, each character showing only its newest version's guides (agent).
- Time-limited facts are left out; prefer facts that two sites share.
- The home page reaches the character pages through the character list, and each new set of pages the same way, through an index page it links (2026-11-23, 2026-11-25); `INDEX_PAGES` in `scripts/check-dist.mjs` names them. System pages are a plain link list on the home page. Each set of pages per character has an index page of its own under `characters/` (`archives`, `voices`), one row and one link per character; the character list keeps Character, Class and Attribute and links no sub-pages (2026-11-26). A new page set per character gets its own index page the same way.
- Official art is used, although the publisher's Derivative Work Guidelines forbid direct copying of official materials. Remove an image when the publisher asks.
- Look: pixel terminal in the official colours, cyan `#39d5fc` and pink `#fb5692`. Motion is sparing: the title is typed once, the first blocks print in once, the cursors blink. Removed as too much, not to be added back: the moving logo mark, the signal meter, the moving band under the header, motion and scan lines on images, the status line. The mark before the site name is two slanted cards, cyan over pink, drawn in CSS; it does not move, the cursor after the name does (2026-11-25).
- `pnpm upstream` runs every day in a workflow that keeps one issue (2026-11-25); it also compares the text of the cited notices of the current version.

## Commands

```
pnpm verify      # subset the font, build, then run the acceptance checks. Run this before you call a change done.
pnpm build       # subset the font and build
pnpm check       # acceptance checks on an existing dist/
pnpm upstream    # compare the sources with what the pages were written from (upstream/README.md)
pnpm preview     # serve dist/ at http://127.0.0.1:4399/nte-wiki/ with GitHub Pages style headers
node scripts/prose-review.mjs run      # after pnpm build: read the prose not yet in the ledger (PROSE_READER names the reader; `status` instead of `run`: count it)
uv run --with opencc-python-reimplemented scripts/to-zh-cn.py   # write the zh-cn pages from the zh-tw pages, then `python3 pipeline/build_pages.py`
```

Game text from records: after any `zh-tw` change run the scripts in the order `pipeline/README.md` gives.

## Content rules

- Pages live in `src/content/docs/` (English) and its `zh-tw/`, `zh-cn/`, `ja/` and `ko/` folders. Addresses use the official English name in lower case: `characters/elyms`, `characters/daffodill`, `versions/1-5`.
- Written by script, never by hand: every `zh-cn` page; the archive and voice line pages (`characters/<slug>/archive`, `/voice`) and their lists; the pages under `anomalies/`, `items/` and `community/`; the Outfits description column, the Profile rows, and the description tables at the end of the Arcs and progression pages.
- `scripts/to-zh-cn.py` replaces Taiwan wording with the wording of the official Simplified notices, converts the characters, swaps the title with its Simplified alias and points links at `/zh-cn/`; it skips the game-text pages. Run it after every change to a `zh-tw` page. When a `zh-tw` page brings in a new name, check it against the notices under `nte.perfectworld.com/cn/` and add a pair to `VOC` if the two differ. A `zh-tw` page whose title changes in Simplified characters needs that title among its aliases.
- Links and images are root-relative and without the site's sub-path: `/characters/elyms/`, `/art/characters/elyms.webp`. In `zh-tw` pages, links start with `/zh-tw/`; image paths do not.
- Optional frontmatter: `effectiveDate` (date of the newest official notice used), `aliases`, `art`, `hideAnswer` (archive pages: no visible answer line). Title and aliases together are the same set of strings in every language. `appliesTo` names the game version; `caveat` names the end of anything limited as an absolute date and time with `(UTC+8)`. Quote a value that contains a colon followed by a space.
- Names: English from the English notes, Traditional Chinese from the Taiwan notices, Simplified Chinese from the `/cn/` notes. When no Taiwan text has a name, Chinese pages use the Simplified name in Traditional characters with Taiwan vocabulary (計畫, 介面), and the names page leaves that Traditional cell empty.
- Chinese pages use the game's own Chinese names for skills, skill states and game terms; English pages keep the English names. Chinese Skills tables name each skill without its slot prefix (猛撞, not 普通攻擊：猛撞), except Critical Ripostes, and quote names in running text with 「」. Where Prydwen's English has no game counterpart, the Chinese uses the game's wording for the thing. Game Simplified names must survive the round trip to `zh-cn` unchanged.
- Fixed renderings (the six attributes and Arc types in Chinese, the core terms in Japanese and Korean) and the portrait crop are in `pipeline/README.md`; use them as given. Characters without a profile on the official site have no portrait.
- Japanese and Korean pages are translated from the English page with the same facts, headings, tables and links; read `pipeline/README.md` (Japanese and Korean) first: register, where names come from, the clock, the sources to list.
- Character pages follow one structure: portrait, Profile (with voice actors), How to obtain, Skills, Growth, Awakenings, then Signature Arc, Outfits, Story and modes where they apply, then Skill multipliers: one table per skill with Lv. 1–13, labels in the page language, `*` written as `×`, and a row that is the same at every level written as a sentence under the table.
- Archive and voice pages are hidden from the autogenerated sidebar; `src/routeData.ts` adds the archive as a child row under its character. Outfit rows that name several outfits put each name before its text.
- The body of the English home page ends a few hundred characters under the 5,000 limit (the check counts absolute URLs). Shorten cells or drop duplicate links before adding rows; another page there needs a change the owner decides, such as a systems index page. An endgame modes page waits for that.

## Skin rules

- The skin is `src/styles/nte.css`. Text drawn with CSS `content` (marks, prefixes, counters, the cursor) needs a pattern in check 5 of `scripts/check-dist.mjs`.
- The pixel font is Fusion Pixel 12px, used at 12, 24 or 36 px only; `scripts/subset-font.mjs` cuts it before every build. Licences, the Korean glyphs and the body font stacks per script: `pipeline/README.md` (Fonts).
- Images are shown in a frame with an offset shadow. Screenshots need a wait of about two seconds for the opening animation.
- Overrides: `SiteTitle`, `MarkdownContent`, `ThemeSelect`. The header links the six sections in the sidebar's order, community guides last.

## Where things are

| Path | Role |
| --- | --- |
| `src/lib/site.mjs` | Site URL and sub-path, locales, URL rules, `llms.txt` notes, labels |
| `src/lib/hast-base.mjs` | Sätteri plugin that adds the sub-path to links and images and the class `rows-scroll` to table bodies |
| `src/routeData.ts` | Markdown alternate link, JSON-LD, the archive row in the sidebar |
| `scripts/prose-site.mjs` | Prose ledger settings: `zh-cn` is written by a script; game text is not read |
