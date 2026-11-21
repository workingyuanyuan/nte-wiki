# Agent test

Checks whether an agent with only a fetch tool answers questions about the game better from this site than from the official site and guide sites.

## Files

| File | Role |
| --- | --- |
| `questions.json` | Ten pilot questions with the expected answer, the qualifier that is easy to miss, and the page that holds them. Written from the official notices; q09 also uses the guide sites |
| `fetch.mjs` | The fetch tool given to the agent. Modelled on the MCP reference Fetch server: main-article extraction, Markdown output, 5,000 characters per call, `start_index` to continue. Every call is logged to `runs/<run>.log` |
| `results/<date>/` | Answers and fetch logs of each recorded run |

## How to run

1. Build the site with a local address and serve it:

```
SITE_URL=http://127.0.0.1:4399/nte-wiki pnpm build
pnpm preview
```

2. Give a fresh agent the questions (without the expected answers), the fetch command below as its only source, a start URL, and a budget of 3 fetches per question.

```
node tests/agent-eval/fetch.mjs --run <run-name> --q <question-id> <url> [start_index]
```

Start URL for this site: `http://127.0.0.1:4399/nte-wiki/`. Start URLs for the baseline: `https://nte.perfectworld.com/en/`, `https://www.prydwen.gg/neverness-to-everness/` and `https://game8.co/games/Neverness-to-Everness`.

3. Score each answer against `questions.json`: pass needs the answer and the qualifier; partial is one of the two or an unverified inference; fail is a wrong or missing answer.

4. Run `pnpm verify` afterwards so that `dist/` carries the public address again.

## Search test

Checks whether an agent that starts from a question, with no URL, finds this site. It runs on the live site once its pages are indexed. It is a record, not a gate for publishing.

1. Give a fresh agent the questions from `questions.json` (without the expected answers, and without this site's name or address), a web search tool, and the fetch command above as its only way to read a page. No start URL.
2. Record the search tool, the queries the agent made and its answers. The fetch log holds the URLs it read.
3. Score each question: pass needs a page of this site among the pages read, and the answer with its qualifier. Record "not found" when no page of this site was read.
4. For each miss, find the cause: the page is not indexed (sitemap, links, `robots.txt`); it is indexed but not chosen (the question's words are not in its title or headings, it has nothing the source lacks, nothing links to the site); or it was read and the qualifier was lost.

## Results

### 2026-11-18

| Run | Pass | Partial | Fail | Fetches (from the log) |
| --- | --- | --- | --- | --- |
| This site, start URL `http://127.0.0.1:4400/nte-wiki/` | 10 | 0 | 0 | 12 |
| Original sources, within the budget of 3 fetches per question | 2 (q01, q02) | 1 (q05) | 7 | 97 in total; 7 questions went over the budget |
| Original sources, budget ignored | 5 (q01, q02, q04, q08, q09) | 2 (q03, q05) | 3 (q06, q07, q10) | 97 |

What the reader of the original sources ran into: Prydwen returned 403 to the test's fetch tool; the official home page returned one line of consent text; the official news index shows three notices per page; no fetched page gave Traditional Chinese names (q07); the server rule was not found (q05); Game8 lists "Fighting with a Dragon" as a spinoff with no trace of its release as a main story episode (q10).

Limits of this result:

- One reader model (Claude Sonnet, as a subagent) and one run per side.
- The questions and the expected answers were written by the author of the site, from the official notices.
- The site was served locally, built with `SITE_URL=http://127.0.0.1:4400/nte-wiki`.
- The reader of the original sources did not keep to the fetch budget, so its fetch count is not a like-for-like comparison.
- The run used the English pages. The Chinese pages were finished after it, and the note about the Boards announced for 2026-12-02 was added after it.
