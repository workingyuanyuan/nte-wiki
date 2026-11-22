// Compares the sources of this site with what its pages were written from.
// upstream/README.md says what is watched, what each line of the report means and how to
// update the pages.
//
//   pnpm upstream            report. Exit 0: no difference. 1: differences. 2: the check could not be made
//   pnpm upstream --write    also record the notices seen and the fingerprints of the cited notices
//                            in upstream/manifest.json (exit 0 whatever it reports)
//
// Four things are watched, all read from the English pages and the sources:
//
//   1. The official notice list (nte.perfectworld.com/en/article/news/), newest first, until a
//      page of notices that are known or older than the record: a new patch notes or
//      maintenance notice is a difference, any other new notice a note.
//   2. The article text of the official notices that the pages cite from the current version
//      on (the earliest notice the newest version page cites): a SHA-256 in the manifest.
//   3. The game data version that the pages cite (static.nanoka.cc/nte/<version>/): a few
//      HEAD requests for the next versions. nanoka.cc is not crawled (AGENTS.md).
//   4. Dates in each page's caveat that were in the future when the page was verified and are
//      past now. This needs no network.
//
// Prydwen and Game8 are not watched: their pages carry no version and change every week.

import { createHash } from 'node:crypto';
import { readFileSync, writeFileSync, readdirSync, existsSync, mkdirSync } from 'node:fs';
import { dirname, join, relative } from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = fileURLToPath(new URL('..', import.meta.url));
const DOCS = join(ROOT, 'src/content/docs');
const MANIFEST = join(ROOT, 'upstream/manifest.json');
const write = process.argv.includes('--write');

const OFFICIAL = 'https://nte.perfectworld.com';
const LIST = '/en/article/news/';
const LIST_PAGES = 5;
const NOTICE_URL = /^https:\/\/nte\.perfectworld\.com\/en\/article\/news\/[a-z]+\/(\d{8})\/(\d+)\.html$/;
const GAME_DATA = 'https://static.nanoka.cc/nte/';
const GAME_DATA_URL = /^https:\/\/static\.nanoka\.cc\/nte\/(\d+)\.(\d+)\.(\d+)\//;
// Only these words mark a version: "Version 1.4 NTE x Porsche Fan Creation Contest" also starts with a version number.
const VERSION_TITLE = /\bpatch notes\b|\bupdate notes\b/i;
const MAINTENANCE_TITLE = /\bmaintenance\b/i;
const LANGUAGE_DIRS = new Set(['zh-tw', 'zh-cn', 'ja', 'ko']);
// A plain client name, without personal details (see the root AGENTS.md).
const HEADERS = { 'user-agent': 'Mozilla/5.0 (compatible; docs-site-upstream-check)' };

const fingerprint = (text) => ({ sha256: createHash('sha256').update(text).digest('hex'), characters: text.length });
const day = (value) => (value instanceof Date ? value.toISOString().slice(0, 10) : String(value ?? ''));

/** Fetches a URL. Returns null for a 404, throws for any other failure; tries once more after a network error or a 5xx. */
async function request(url, method = 'GET', tries = 2) {
	let res;
	let body;
	try {
		res = await fetch(url, { method, headers: HEADERS, signal: AbortSignal.timeout(30_000) });
		if (res.ok && method === 'GET') body = await res.text();
	} catch (error) {
		if (tries > 1) return retry(url, method, tries);
		throw new Error(`${url}: ${error.cause?.code ?? error.name}`);
	}
	if (res.status === 404) return null;
	if (res.status >= 500 && tries > 1) return retry(url, method, tries);
	if (!res.ok) throw new Error(`${url}: HTTP ${res.status}`);
	return body ?? '';
}
async function retry(url, method, tries) {
	await new Promise((resolve) => setTimeout(resolve, 5_000));
	return request(url, method, tries - 1);
}

/** The English pages: id (`characters/elyms`) and frontmatter. */
function englishPages(YAML) {
	const pages = [];
	const walk = (dir) => {
		for (const entry of readdirSync(dir, { withFileTypes: true })) {
			const path = join(dir, entry.name);
			if (entry.isDirectory()) {
				if (dir !== DOCS || !LANGUAGE_DIRS.has(entry.name)) walk(path);
			} else if (entry.name.endsWith('.md')) {
				const text = readFileSync(path, 'utf8');
				const match = text.match(/^---\n([\s\S]*?)\n---/);
				if (!match) throw new Error(`${relative(ROOT, path)}: no frontmatter`);
				pages.push({ id: relative(DOCS, path).replace(/\.md$/, ''), data: YAML.parse(match[1]) });
			}
		}
	};
	walk(DOCS);
	return pages.sort((a, b) => a.id.localeCompare(b.id));
}

/** Reads one page of the official notice list. */
function parseList(html, JSDOM) {
	const doc = new JSDOM(html).window.document;
	return [...doc.querySelectorAll('.listNews a[href]')].map((a) => ({
		url: new URL(a.getAttribute('href'), OFFICIAL).href,
		title: a.querySelector('.title')?.textContent.trim() ?? '',
		date: a.querySelector('.date')?.textContent.trim() ?? '',
		type: a.querySelector('.type')?.textContent.trim() ?? '',
	}));
}

/** The text of an official notice, whitespace folded. */
function noticeText(html, JSDOM) {
	const doc = new JSDOM(html).window.document;
	const article = doc.querySelector('.articleCont');
	if (!article) return null;
	return article.textContent.replace(/\s+/g, ' ').trim();
}

/** Dates in a caveat with their time, as a moment in UTC+8. A date without a time counts from the end of that day. */
function caveatMoments(caveat) {
	return [...String(caveat ?? '').matchAll(/(\d{4}-\d{2}-\d{2})(?: (?:at )?(\d{2}:\d{2}))?/g)].map(([text, date, time]) => ({
		text,
		date,
		at: Date.parse(`${date}T${time ?? '23:59'}:00+08:00`),
	}));
}

async function main() {
	// Imported here, so that a failure to load them is "check not made" (exit 2), not exit 1.
	const YAML = (await import('yaml')).default;
	const { JSDOM } = await import('jsdom');
	if (!write && !existsSync(MANIFEST)) throw new Error('upstream/manifest.json is missing; run --write once the pages agree with the sources');
	const old = existsSync(MANIFEST) ? JSON.parse(readFileSync(MANIFEST, 'utf8')) : {};
	const oldNotices = old.notices ?? [];
	const oldCited = old.cited ?? {};

	const pages = englishPages(YAML);
	const differences = [];
	const notes = [];
	const failures = [];

	// 4. Caveat dates. First, because it needs no network.
	// UPSTREAM_NOW (an ISO date and time) stands in for the present, to test this check.
	const now = process.env.UPSTREAM_NOW ? Date.parse(process.env.UPSTREAM_NOW) : Date.now();
	if (Number.isNaN(now)) throw new Error('UPSTREAM_NOW is not a date');
	for (const { id, data } of pages) {
		const verified = day(data.lastVerified);
		for (const moment of caveatMoments(data.caveat)) {
			if (moment.date > verified && moment.at < now) differences.push(`caveat date passed: ${id}: ${moment.text}`);
		}
	}

	// What the pages cite.
	const citedBy = new Map();
	const gameData = new Map();
	for (const { id, data } of pages) {
		for (const { url } of data.sources ?? []) {
			if (NOTICE_URL.test(url)) citedBy.set(url, [...(citedBy.get(url) ?? []), id]);
			const version = url.match(GAME_DATA_URL);
			if (version) {
				const v = version.slice(1, 4).map(Number);
				gameData.set(v.join('.'), { v, pages: (gameData.get(v.join('.'))?.pages ?? 0) + 1 });
			}
		}
	}
	const versionPages = pages.filter(({ id }) => /^versions\/\d+-\d+$/.test(id));
	if (versionPages.length === 0) throw new Error('no version pages');
	const current = versionPages
		.map((page) => ({ page, v: page.id.slice(9).split('-').map(Number) }))
		.sort((a, b) => b.v[0] - a.v[0] || b.v[1] - a.v[1])[0].page;
	// The current version starts at the earliest English notice its page cites (the patch notes);
	// effectiveDate moves on to the newest notice used, such as the second half's maintenance notice.
	const since = (current.data.sources ?? []).map(({ url }) => url.match(NOTICE_URL)?.[1]).filter(Boolean).sort()[0];
	if (!since) throw new Error(`${current.id}: cites no English official notice`);

	// 1. The notice list, newest first. The list is ordered by its shown date, and an edited notice
	// can move back to the top, so a known notice does not end the reading: a page does when every
	// notice on it is known or older than the oldest notice recorded (`floor`). Without a manifest,
	// --write reads up to the page that holds a cited notice and records every notice read.
	const known = new Set([...oldNotices.map((n) => n.url), ...citedBy.keys()]);
	const floor = oldNotices.map((n) => n.date).sort()[0] ?? '';
	const read = [];
	const seen = [];
	try {
		let done = false;
		for (let n = 0; n < LIST_PAGES && !done; n++) {
			const html = await request(`${OFFICIAL}${LIST}${n === 0 ? 'index' : `index${n}`}.html`);
			const items = html === null ? [] : parseList(html, JSDOM);
			if (items.length === 0) throw new Error(`notice list page ${n + 1}: no notices found`);
			read.push(...items);
			const fresh = items.filter((item) => !known.has(item.url) && !(floor && item.date < floor));
			seen.push(...fresh);
			done = floor ? fresh.length === 0 : items.some((item) => known.has(item.url));
		}
		if (!done) throw new Error(`the notice list did not reach known notices in ${LIST_PAGES} pages`);
		for (const item of seen) {
			const id = item.url.match(/(\d+)\.html$/)?.[1] ?? item.url;
			const line = `${id}: ${item.title} (${item.date}, ${item.type}) ${item.url}`;
			if (VERSION_TITLE.test(item.title)) differences.push(`new version notice: ${line}`);
			else if (MAINTENANCE_TITLE.test(item.title)) differences.push(`new maintenance notice: ${line}`);
			else notes.push(`note: new notice: ${line}`);
		}
	} catch (error) {
		failures.push(error.message);
	}

	// 2. The cited notices of the current version.
	const cited = {};
	for (const [url, ids] of citedBy) {
		const [, date, id] = url.match(NOTICE_URL);
		if (date < since) continue;
		try {
			const html = await request(url);
			const text = html === null ? null : noticeText(html, JSDOM);
			const by = `cited by ${ids.join(', ')}`;
			if (html === null) { differences.push(`cited notice gone: ${id}: ${url}, ${by}`); continue; }
			if (text === null) throw new Error(`${url}: no article in the page`);
			cited[url] = fingerprint(text);
			if (!oldCited[url]) differences.push(`not in the manifest: ${id}: ${url}, ${by}`);
			else if (oldCited[url].sha256 !== cited[url].sha256) differences.push(`cited notice changed: ${id}: ${url}, ${by}`);
		} catch (error) {
			failures.push(error.message);
		}
	}

	// 3. The next game data versions.
	if (gameData.size > 0) {
		const pinned = [...gameData.values()].sort((a, b) => b.v[0] - a.v[0] || b.v[1] - a.v[1] || b.v[2] - a.v[2]);
		const [x, y, z] = pinned[0].v;
		const candidates = [[x, y, z + 1], [x, y, z + 2], [x, y, z + 3], [x, y + 1, 0], [x, y + 1, 1], [x, y + 1, 2]];
		const cites = pinned.map((p) => `${p.v.join('.')} (${p.pages} sources)`).join(', ');
		for (const v of candidates) {
			try {
				if ((await request(`${GAME_DATA}${v.join('.')}/character.json`, 'HEAD')) !== null) {
					differences.push(`new game data: ${v.join('.')}: the pages cite ${cites}`);
				}
			} catch (error) {
				failures.push(error.message);
			}
		}
	}

	for (const line of [...differences, ...notes]) console.log(line);
	console.log(`${seen.length} new notices read, ${Object.keys(cited).length} cited notices of ${current.id} read, ${pages.length} pages; ${differences.length} differences, ${notes.length} notes.`);
	if (failures.length) throw new Error(failures.join('; '));

	if (write) {
		const byUrl = new Map([...oldNotices, ...read].map((n) => [n.url, n]));
		const notices = [...byUrl.values()].sort((a, b) => b.date.localeCompare(a.date) || b.url.localeCompare(a.url));
		const manifest = { origin: OFFICIAL, list: LIST, read: new Date().toISOString().slice(0, 10), notices, cited };
		mkdirSync(dirname(MANIFEST), { recursive: true });
		writeFileSync(MANIFEST, JSON.stringify(manifest, null, '\t') + '\n');
		console.log('manifest updated.');
		return 0;
	}
	return differences.length ? 1 : 0;
}

try {
	process.exitCode = await main();
} catch (error) {
	console.error(`check not made: ${error.message}`);
	process.exitCode = 2;
}
