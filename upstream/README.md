# Following the sources of this site

The pages are written from the official notices of the global service (`nte.perfectworld.com`), the versioned game data on nanoka.cc and a few guide sites. The game changes every version, and a version's second half brings new Boards. `pnpm upstream` compares the sources with what the pages were written from.

```
pnpm upstream            # report. Exit 0: no difference. 1: differences. 2: the check could not be made
pnpm upstream --write    # also record the notices seen and the fingerprints of the cited notices in upstream/manifest.json
```

It needs no token and changes no page. It reads the English pages only: the other languages carry the same facts, dates and sources.

## What is watched, and where the record is

| Watched | Compared with | Kept in |
| --- | --- | --- |
| The official notice list `/en/article/news/index.html`, `index1.html`, ... (three notices a page), newest first, until a page whose notices are all known or older than the oldest one recorded, at most five pages. The list is ordered by its shown date, and an edited notice can move back to the top, so one known notice does not end the reading | The notices already known: those the pages cite and those read at the last `--write` | The pages (`sources`) and `manifest.json` (`notices`) |
| The article text of every official English notice that a page cites, dated on or after the earliest English notice that the newest version page cites (its patch notes) | A SHA-256 from the last `--write` | `manifest.json` (`cited`) |
| Game data versions after the one the pages cite: HEAD requests for `static.nanoka.cc/nte/<version>/character.json`, three patch numbers and the next minor version's `.0` to `.2` | The version in the pages' `sources` URLs | The pages |
| Dates in each page's `caveat` | `lastVerified` of the page and the present (UTC+8; a date without a time counts from the end of the day) | The pages |

The game text that `pipeline/` writes (archives, outfit, Arc and material descriptions) follows the game data version: its records cite the same version, so a new version is reported as above. Its Traditional Chinese text comes from everness.info, which needs a browser, so the scheduled run cannot read it; it is read again with the pipeline when the version moves.

Prydwen and Game8 are not watched: their pages carry no version and change every week, and they follow the patch notes, which are watched. nanoka.cc and everness.info refuse AI training and AI crawlers; the check sends six HEAD requests to nanoka.cc and keeps nothing. A version that skips a number past the candidates is not found by the probe; the patch notes notice still is.

## The report

One line for each difference, then the notes, then a count. A line reads `kind: id: detail`, where the id is a notice id, a game data version or a page.

| Line | Meaning | What to do |
| --- | --- | --- |
| `new version notice` | A notice titled "patch notes" or "update notes" | A new version: follow "A new version" below |
| `new maintenance notice` | A notice with "maintenance" in its title. The second Board of a version and mid-version changes are announced in "Server Maintenance Notice" | Read it. A new Board: follow "A new Board" below. Otherwise update what it changes |
| `cited notice changed` | The text of a cited notice of the current version differs from the last `--write` (a corrected time, an added item) | Read the notice, update the pages it names in every language |
| `cited notice gone` | A cited notice answers 404 | Find where it went in the notice list and update the URL in every language |
| `not in the manifest` | A cited notice of the current version has no fingerprint yet | Check that the pages it names agree with it, then `--write` |
| `new game data` | nanoka.cc has a game data version after the one the pages cite | Check against the patch notes that its content is released (1.5.4 carried Exe before release), then re-read the game data files of the affected pages and move every cited URL to the new version |
| `caveat date passed` | A date in the caveat (`2026-12-02 at 05:59` or `2026-12-02 05:59`) was in the future when the page was verified and is past now: a Board or event has closed | Update the caveat and the sentences that name it (the next Board, "closed on", the home page) in every language |
| `note: new notice` | Any other new notice: events, account actions, guidelines | Nothing is due. Read the title; `--write` records it as known |

`check not made` with exit 2 is not a report: fix the cause it names and run again. It prints the lines it found first. "did not reach known notices in 5 pages" means more than about fifteen notices appeared since the last `--write`, or the list's markup or addresses changed: read the list, update the pages, then `--write` (it stops with the same message, so raise `LIST_PAGES` in the script for that run).

## A new version

1. Read the patch notes in English, then in Simplified Chinese (`/cn/`), Japanese (`/jp/`), Korean (`/kr/`) and the Taiwan post, as `AGENTS.md` says under Sources.
2. Add the version page in every language, add the Board to `systems/boards.md` and to the three A-Class pages that share it, add the new characters' pages, and update the home page (current version, current Boards, tables), the caveats that name the previous version, and `LLMS_NOTES` in `src/lib/site.mjs`.
3. Run `scripts/to-zh-cn.py` for the Simplified Chinese pages.
4. Move `VERSION` in `pipeline/fetch_nanoka.py`, delete `pipeline/cache/everness/`, and run the game text commands in `AGENTS.md` (Commands); new characters, outfits and Arcs are picked up from the pages' rows.

## A new Board

Add it to `systems/boards.md`, to the A-Class pages that share it and to the page of each character it features, and update the home page and the caveats that named the closing date.

## After updating

1. Set `lastVerified` of each page that was read again, and `effectiveDate` to the date of the newest notice used.
2. `pnpm upstream --write`, then `pnpm upstream` until no line is left (`--write` leaves with 0 whatever differences it reports, and with 2 without writing when the check could not be made), then `pnpm verify`.
3. The owner confirms the content before the push.

`--write` records every notice read as known and every cited notice as it is now. Run it after the pages agree with them, not before: a new patch notes notice that is recorded as seen is no longer reported. It cannot hide a passed caveat date or a game data version: those are read from the pages.

`lastVerified` moves only for a page that was read against its sources again. A run without a difference moves nothing.

## Schedule

`.github/workflows/upstream.yml` runs the command every day (owner, 2026-11-25; once a week from 2026-11-22, which reported a new version up to six days late) and by hand (`gh workflow run upstream.yml`). A difference on the default branch opens one issue with the label `upstream`, assigned to the owner; later runs replace its text, comment when a line other than a note is added or removed, and close it when there is no difference. A run that could not make the check fails the workflow and leaves the issue as it is.

GitHub stops scheduled workflows in a public repository after 60 days without activity in it; `gh workflow enable upstream.yml` starts them again.
