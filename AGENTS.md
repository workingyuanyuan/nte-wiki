# Rules for agents maintaining this site

This site is an unofficial wiki for the game Neverness to Everness (NTE, 異環). Its first readers are AI agents; humans come second. Markdown source is the only content source, and the HTML is a skin over it. The rules in `../AGENTS.md` apply; this file holds what is specific to this site.

## Decisions by the owner

- Languages: English, Traditional Chinese (`/zh-tw/`) and Simplified Chinese (`/zh-cn/`, added by the owner on 2026-11-18).
- Scope of the first release: 35 pages. Home, one page per version (1.0 to 1.5), one page per playable character (25), two system pages (Boards, platforms) and the names page.
- Second release (2026-11-19): six system pages (Esper Cycles, Arcs, Consoles, progression materials, vehicles, properties) and Growth and Awakenings sections on every character page. The owner asked to prefer facts that two sites share and to leave out time-limited facts.
- Game data: the owner accepted the versioned game data that nanoka.cc publishes (`static.nanoka.cc/nte/<version>/`, English and Simplified Chinese) as the source of in-game text: names, Arc stats and effects, Cartridge sets, Awakenings, base stats, materials, vehicles, properties. Only released content goes in (Exe and the Arc "Dotted Horizon" were in 1.5.4 data before release). Check samples against mysqil, Everness and the official notices, take a bounded number of files, and do not crawl the sites: nanoka.cc and everness.info carry `ai-train=no` and block AI crawlers.
- Primary source: the global official site `nte.perfectworld.com`, because it is readable with a plain HTTP fetch. The Taiwan site `nte.iwplay.com.tw` is used only for Traditional Chinese names.
- Do not label the service region beside each date. The pages state once, in the home page caveat and in `llms.txt`, that dates follow the global official site in UTC+8 and that mainland China is not covered.
- Official art is used, by the owner's decision, although the publisher's Derivative Work Guidelines forbid direct copying of official materials. Credits go in the `art` frontmatter field and appear in the page notes at the end of the page, never under the picture. Remove an image when the publisher asks.
- The first screen of a page shows content. Scope, caveat, dates and sources are shown in the page notes after the body.
- No disclaimers in the visible text: do not write what a page leaves out, what the notes fail to say, or what is unverified. Leave the fact out, or state the positive fact.
- Character pages describe skills. Skill names and effects come from Prydwen and are checked against Game8; damage values, tier lists and team builds are not copied.
- Guide sites may supply a fact that the official sources lack when at least two of them agree, and the page names them in `sources`. A fact from one guide site is attributed in the sentence ("Game8 says").
- Look: pixel terminal in the official colours, cyan `#39d5fc` and pink `#fb5692`. Motion is sparing: the title is typed once, the first blocks print in once, the cursors blink. The owner had these removed as too much: the logo mark, the signal meter, the moving band under the header, motion and scan lines on images, the status line. Do not add them back.
- `robots.txt` carries `ai-train=no`. Address: `https://workingyuanyuan.github.io/nte-wiki/`.

## Commands

```
pnpm verify      # subset the font, build, then run the acceptance checks. Run this before you call a change done.
pnpm build       # subset the font and build
pnpm check       # acceptance checks on an existing dist/
uv run --with opencc-python-reimplemented scripts/to-zh-cn.py   # write the zh-cn pages from the zh-tw pages
pnpm preview     # serve dist/ at http://127.0.0.1:4399/nte-wiki/ with GitHub Pages style headers
```

## Content rules

- Pages live in `src/content/docs/` (English), `src/content/docs/zh-tw/` (Traditional Chinese) and `src/content/docs/zh-cn/` (Simplified Chinese). Page addresses use the official English name in lower case: `characters/elyms`, `characters/daffodill`, `versions/1-5`.
- Do not edit `zh-cn` pages by hand. They are written from the `zh-tw` pages by `scripts/to-zh-cn.py`: it replaces Taiwan wording with the wording of the official Simplified Chinese notices, converts the characters, swaps the title with its Simplified alias and points links at `/zh-cn/`. Run it after every change to a `zh-tw` page. When a `zh-tw` page brings in a new name, check it against the notices under `nte.perfectworld.com/cn/` and add a pair to `VOC` in the script if the two differ (three did: 淘方斯记, 末班公交车之夜, 神秘纽扣). Every `zh-tw` page whose title changes in Simplified characters needs that Simplified title among its aliases.
- Write links and images root-relative and without the site's sub-path: `/characters/elyms/`, `/art/characters/elyms.webp`. In `zh-tw` pages, links start with `/zh-tw/`; image paths do not. The sub-path is added at build time (`src/lib/hast-base.mjs`).
- Required frontmatter is enforced by `src/content.config.ts`. Optional: `effectiveDate` (date of the newest official notice used), `aliases` (the subject's name in the other scripts), `art` (credit links for the images on the page). The title and aliases together are the same set of strings in every language; the check script compares them.
- `appliesTo` names the game version. `caveat` names the end of anything limited as an absolute date and time with `(UTC+8)`.
- Quote a frontmatter value that contains a colon followed by a space.
- Names: English from the English notes, Traditional Chinese from the Taiwan notices, Simplified Chinese from the `/cn/` notes. When no Taiwan text has a name, Chinese pages use the Simplified name in Traditional characters with Taiwan vocabulary (計畫, 介面); the names page leaves that Traditional cell empty. Skill names and the names of skill states in the Skills tables stay in English in both languages (written before game data was a source). The Growth, Awakenings and system tables use the game's own Chinese text, converted to Traditional characters with Taiwan forms (後台, 舞台, 回復); game Simplified names in them must survive the round trip to `zh-cn` unchanged.
- Attributes in Chinese: 光 Cosmos, 靈 Anima, 咒 Incantation, 魂 Psyche (Taiwan news posts); 暗 Chaos, 相 Lakshana (Traditional Chinese guide sites). Arc types in Chinese are followed by the English in parentheses, for example 固態 (Solid). The game's Chinese text names the five types 固态, 液态, 气态, 等离子 and 聚合 (Condensate); 聚合 replaced the earlier 凝聚態.
- Character pages follow one structure: portrait, Profile (with voice actors), How to obtain, Skills, Growth, Awakenings, then Signature Arc, Outfits, Story and modes where they apply. Portraits go in `public/art/characters/<slug>.webp`, cropped from the official site's mobile poster (left 95, top 150, width 560, height 686 of the 750×836 image). Adler, Edgar, Haniel, Aurelia and Skia have no profile on the official site and so no portrait.
- When a version changes: add the version page, add the Board to `systems/boards.md` and to the three A-Class pages that share it, update the home page (current version, current Boards, tables), the caveats that name "Version 1.5", and `LLMS_NOTES`.
- The home page must link every page within its first 5,000 extracted characters. The English home page is about 50 characters under the limit (the check counts absolute URLs): shorten cells or drop duplicate links before adding rows. System pages are a plain link list there.

## Skin rules

- The header links to the Markdown twin, `llms.txt` and `index.json` are shown in capitals with a key hint (`[M]`, `[L]`, `[J]`), as on the reference site; the keys work as shortcuts. Capitals and hints come from CSS.
- All marks, prefixes, key hints, counters and the cursor are drawn with CSS and never typed into page text. If you add text through CSS `content`, add a pattern for it to check 5 in `scripts/check-dist.mjs`.
- Three Starlight components are overridden: `SiteTitle`, `MarkdownContent` and `ThemeSelect` (three buttons, so each theme is one click away; it keeps Starlight's storage key `starlight-theme`).
- The hidden note, the answer and the page notes are direct children of the article container, with no wrapper. A wrapper made a readability-style extractor keep the notes and drop the body. The hidden note repeats scope and caveat at the top so that they fall within the first 5,000 extracted characters while the visible notes sit after the body.
- Starlight wraps each heading in `div.sl-heading-wrapper`; sibling selectors must target the wrapper, not `h2`.
- The body font stack names Traditional Chinese fonts; `:root[lang='zh-CN']` in `nte.css` swaps in Simplified ones, so punctuation sits at the baseline on Simplified pages.
- The pixel font is Fusion Pixel 12px (SIL OFL). The `zh_hant` file also holds every Simplified character the pages use (checked on 2026-11-18). `scripts/subset-font.mjs` cuts it down to the characters found in `src/` before every build and writes `public/fonts/pixel.woff2`, which is not committed. Use the font at 12, 24 or 36 px only.
- Images are shown as they are, in a frame with an offset shadow: no overlay, no motion.
- Wide windows: the table of contents keeps the sidebar's width and the text column sits in the middle of the space between the two ("Wide windows" block in `nte.css`). The text column is 50rem, and 60rem from a 110rem window.
- All motion sits inside `@media (prefers-reduced-motion: no-preference)`. Screenshots need a wait of about two seconds for the opening animation.

## Where things are

| Path | Role |
| --- | --- |
| `src/lib/site.mjs` | Site URL and sub-path, locales, URL rules, `llms.txt` notes, labels |
| `src/lib/hast-base.mjs` | Sätteri plugin that adds the sub-path to links and images in the HTML |
| `src/lib/page-md.mjs` | Builds each page's Markdown twin |
| `src/lib/llms.mjs`, `src/pages/[...dir]/` | `llms.txt` and the full and digest bundles for each language |
| `src/pages/index.json.ts` | Machine-readable page list with aliases |
| `src/pages/robots.txt.ts` | `robots.txt`; on a project site crawlers read only the domain root's file |
| `src/routeData.ts` | Markdown alternate link, JSON-LD |
| `src/components/`, `src/styles/nte.css` | The three overrides and the skin |
| `assets/fonts/`, `scripts/subset-font.mjs` | Pixel font source with its licence, and the subsetter |
| `scripts/check-dist.mjs`, `scripts/preview.mjs` | Acceptance checks, local preview |
| `scripts/indexnow.mjs` | Lists pages whose Markdown twin differs from the live one; the deploy workflow submits them to IndexNow |
| `scripts/to-zh-cn.py` | Writes the Simplified Chinese pages from the Traditional Chinese ones |
| `tests/agent-eval/` | Fetch tool, questions and method for the agent test |

## Sources checked on 2026-11-18 and 2026-11-19 (plain HTTP fetch unless noted)

| Source | Result | Use |
| --- | --- | --- |
| `nte.perfectworld.com/en/article/news/index.html`, `index2.html` to `index40.html` | Full list of notices, three per page. The per-category indexes (`gamenews/`, `gamebroad/`, `gameevent/`) miss some notices | Finding notices |
| `nte.perfectworld.com/en/` news articles | Full text | Primary |
| `nte.perfectworld.com/cn/` articles; list at `/cn/article/news/index.html`, `index2.html` and on (79 notices) | Full text, Simplified Chinese, global service | Simplified Chinese names and wording |
| `nte.perfectworld.com/en/main.html?nav=2&role=20` | Profiles of 20 characters as text; the names are images; poster URLs are in the HTML | Profiles, portraits |
| `nte.iwplay.com.tw/news/view/...` articles and `/index.html` | Full text. `/news/` returns 403; `/news/list_1.html` and `list_1_1.html` to `list_1_14.html` list the articles. Full maintenance notices exist from Version 1.3 on; before that only news posts | Traditional Chinese names |
| `prydwen.gg/neverness-to-everness/characters/<slug>` | Full text with the in-game skill text, updated for 1.5 on its release day. The character index is not readable. Rarity and role are blank in the page text | Skills, attribute, Arc type |
| `game8.co/games/Neverness-to-Everness/archives/<id>` | Full text after about 2,000 characters of site navigation. Build pages name the main skill of each slot; Arc type is an image. Character list: `592067` | Cross-check, rank |
| `wiki.biligame.com/nte/<name>` | Returns a portal page instead of the article | Not readable |
| `neverness.gg` | Data pages render with JavaScript; its mirrored patch notes differ from the official ones in places | Do not use |
| `static.nanoka.cc/nte/1.5.4/{en,zh}/` (`item.json`, `console.json`, `vehicle.json`, `home.json`, `character/<id>.json`, `weapon/<id>.json`; `weapon.json` and `character.json` at the version root) | Plain JSON of the game data, versioned; no Traditional Chinese. Some English fields hold untranslated Chinese (vehicle brands and a few names; their English names come from the patch notes) | In-game text |
| `wiki.mysqil.com` | Static Simplified Chinese guide site, CC BY-NC-SA 4.0; takes part of its data from nanoka.cc and everness.info, so it is not independent of them; lags behind the game data (51 Arcs, 6 properties at 1.5) | Cross-check |
| `everness.info` | Data renders with JavaScript (a browser is needed); same game data as nanoka.cc | Cross-check |
| `prydwen.gg/neverness-to-everness/guides/<slug>` | System guides as plain text (`esper-cycles`, `modules-generic`, `modules-cartridge`, `character-progression`) | Mechanics not in the game data |
| Fandom, Mobalytics, wiki.gg, thegameswiki.com | 403, 403, 401, 429 | Not readable |

Mid-version changes (the second Board of each version) are announced in notices titled "Server Maintenance Notice", not in the patch notes.

## Verified pitfalls (Astro 7.4, Starlight 0.43)

- Astro 7 renders Markdown with Sätteri. `markdown.remarkPlugins` fails without `@astrojs/markdown-remark`; write a Sätteri plugin (`defineHastPlugin`) and pass it through `markdown.processor: satteri({ hastPlugins })`.
- `starlight-links-validator` accepts a zh-tw link without the `/zh-tw/` prefix because the English page exists. The home page check in `check-dist.mjs` catches it.
- The official character names on `nte.perfectworld.com` are images. Take names from the patch notes.
- Official English texts write "Daffodill"; Prydwen and Game8 write "Daffodil" (Prydwen's page slug is `daffodil`).
- Vite rewrites `url('/fonts/pixel.woff2')` in `nte.css` with the site's sub-path; no manual prefix is needed.
- A float does not work inside a flex or grid container, so the page notes cannot be moved below the body with CSS `order` while the portrait floats. The notes are placed after the body in the DOM instead.
