// Reads game text from everness.info, which renders it with JavaScript: the archive entries and the
// outfit, Arc and item descriptions in Traditional Chinese (nanoka.cc has no Traditional Chinese
// files; the text on everness.info is the Taiwan localisation, not a conversion of the Simplified
// text), and, for an English or Japanese edition that the nanoka.cc files leave untranslated, the
// archive entries and outfit descriptions in that language.
// A bounded list of named pages, one at a time (everness.info sets ai-train=no; see AGENTS.md).
// Output: pipeline/cache/everness/<key>.json (Traditional Chinese) and <key>.<edition>.json,
// not committed. Pages already read are skipped.
//
//   CHROMIUM=/path/to/chrome-headless-shell node pipeline/fetch_everness.mjs $(python3 pipeline/everness_keys.py)
//
// Arguments: character ids, then --outfits, --arcs, --items, each followed by comma-separated keys.
// --edition en|ja|zh-Hant switches the language for the arguments after it (default zh-Hant).

import fs from 'node:fs';
import path from 'node:path';
import { chromium } from 'playwright-core';

// The label of the profile tab, and the heading that ends an outfit, Arc or item text, per edition.
const EDITIONS = {
	'zh-Hant': { profile: '個人檔案', cosmetics: '來源', arcs: '攻擊力', items: '來源' },
	en: { profile: 'Profile', cosmetics: 'Sources' },
	ja: { profile: '公式資料', cosmetics: '出典' },
};
const FLAGS = { '--outfits': 'cosmetics', '--arcs': 'arcs', '--items': 'items' };

const jobs = []; // [edition, part, key]; part 'espers' for a character id
let edition = 'zh-Hant';
let part = 'espers';
const args = process.argv.slice(2);
for (let i = 0; i < args.length; i++) {
	const a = args[i];
	if (a === '--edition') {
		edition = args[++i];
		part = 'espers';
		if (!EDITIONS[edition]) throw new Error(`unknown edition ${edition}`);
	} else if (a in FLAGS) part = FLAGS[a];
	else for (const key of a.split(',').filter(Boolean)) jobs.push([edition, part, key]);
}

const dir = path.join(path.dirname(new URL(import.meta.url).pathname), 'cache', 'everness');
fs.mkdirSync(dir, { recursive: true });

const browser = await chromium.launch({ executablePath: process.env.CHROMIUM });
const page = await browser.newPage();
const wait = (ms) => page.waitForTimeout(ms);
// The site sometimes stalls; try a page three times, 30 seconds apart.
async function open(url) {
	for (let i = 0; ; i++) {
		try {
			return await page.goto(url, { waitUntil: 'networkidle', timeout: 60000 });
		} catch (e) {
			if (i === 2) throw e;
			await wait(30000);
		}
	}
}

async function profile(ed) {
	await page.getByText(EDITIONS[ed].profile, { exact: true }).first().click();
	await wait(800);
	const panel = page.locator('[role=tabpanel][data-state=active]');
	// The card's title layer covers the toggle button, so click it through the DOM.
	await panel.evaluate((el) => el.querySelectorAll('button[aria-expanded="false"]').forEach((b) => b.click()));
	await wait(1000);
	return panel.evaluate((el) =>
		[...el.querySelectorAll(':scope > div > div')].map((card) => {
			const title = card.querySelector('p.font-semibold')?.innerText.trim() ?? '';
			const lines = card.innerText.split('\n').map((l) => l.replace(/\s+$/, ''));
			const drop = new Set(['”', 'MESSAGE', title]);
			const body = lines.filter((l) => !drop.has(l.trim())).join('\n').replace(/^\n+|\n+$/g, '').replace(/\n{3,}/g, '\n\n');
			return { title, text: body };
		}),
	);
}

// An outfit, Arc or item page shows: a rarity letter, the name, sometimes a price, a quotation
// mark „, the text, then a heading that ends it. An item's text is its use (one line), then its
// description.
async function described(ed, pt) {
	const text = await page.evaluate(() => document.querySelector('main')?.innerText ?? document.body.innerText);
	const lines = text.split('\n').map((l) => l.trim());
	const start = lines.indexOf('„');
	const end = lines.indexOf(EDITIONS[ed][pt], start);
	let rarity = -1;
	for (let i = 0; i < start; i++) if (/^[A-Z]$/.test(lines[i])) rarity = i;
	if (start < 1 || end < start || rarity < 0) return null;
	const name = lines.slice(rarity + 1, start).find(Boolean);
	const body = lines.slice(start + 1, end).filter(Boolean);
	if (pt === 'items') return { name, use: body[0] ?? '', description: body.slice(1).join('\n') };
	return { name, description: body.join('\n') };
}

const failed = [];
for (const [ed, pt, key] of jobs) {
	if (!EDITIONS[ed][pt === 'espers' ? 'profile' : pt]) throw new Error(`${pt} pages are not set up for ${ed}`);
	const out = path.join(dir, ed === 'zh-Hant' ? `${key}.json` : `${key}.${ed}.json`);
	if (fs.existsSync(out)) continue;
	const url = `https://everness.info/${ed}/${pt}/${key}`;
	await open(url);
	const read = new Date().toISOString().slice(0, 10);
	let rec;
	if (pt === 'espers') rec = { url, read, entries: await profile(ed) };
	else {
		const d = await described(ed, pt);
		if (d) rec = { url, read, ...d };
	}
	if (!rec) {
		console.log(ed, key, 'layout not recognised');
		failed.push(`${ed}:${key}`);
	} else {
		fs.writeFileSync(out, JSON.stringify(rec, null, 1));
		console.log(ed, key, rec.entries ? `${rec.entries.length} entries` : `${rec.name}, ${rec.description.length} characters`);
	}
	await wait(2000);
}
if (failed.length) console.log('not read:', failed.join(' '));

await browser.close();
