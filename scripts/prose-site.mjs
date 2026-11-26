// Site settings for scripts/prose-review.mjs (the prose ledger).
//
// - derived: locales a script writes from another (Simplified Chinese from Traditional,
//   scripts/to-zh-cn.py); their prose is the source locale's, converted, and is read there.
// - skip(path, lang): text the page shows as the game writes it (pipeline/build_pages.py from
//   records/): archive entries, voice lines, outfit descriptions, the Arc and item description tables,
//   the anomaly files and enemy manual entries (records/anomalies.json), and the names, uses, sources,
//   descriptions and achievement conditions of the item and achievement lists (records/lists.json).
//   Where their Traditional Chinese is converted from the Simplified game text, it is the game's text
//   all the same.
//   That text is the game's, not the site's prose. The Markdown renderer turns straight quotes,
//   "..." and "--" into typographic ones, so each record line is looked up in the built page
//   with either form allowed, and the page's own spelling of it is returned.

import { readFileSync, existsSync } from 'node:fs';
import { JSDOM, VirtualConsole } from 'jsdom';

const json = (rel) => JSON.parse(readFileSync(new URL(`../${rel}`, import.meta.url), 'utf8'));
const squash = (text) => text.replace(/\s+/g, ' ').trim();
// Records key languages as en, zh-tw, zh-cn, ja, ko; index.json writes zh-TW and zh-CN.
const key = (lang) => lang.toLowerCase();

/** The record's strings for one language: each whole (a table cell joins its lines) and line by line. */
function strings(list) {
	return list.filter(Boolean).flatMap((s) => [s, ...s.split('\n')]).map(squash).filter((s) => s.length > 1);
}

/** A pattern that matches a record line as the renderer prints it. */
function pattern(s) {
	const re = s
		.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')
		.replace(/\\\.\\\.\\\./g, '(?:\\.\\.\\.|…)')
		.replace(/-{2,3}/g, '(?:---|--|—|–)')
		.replace(/'/g, "['‘’]")
		.replace(/"/g, '["“”]');
	return new RegExp(re);
}

/** The built page's text, as prose-review reads it. */
function pageText(path) {
	const file = new URL(`../dist/${path}index.html`, import.meta.url);
	if (!existsSync(file)) return '';
	const dom = new JSDOM(readFileSync(file, 'utf8'), { virtualConsole: new VirtualConsole() });
	const text = squash(dom.window.document.querySelector('main .sl-markdown-content')?.textContent || '');
	dom.window.close();
	return text;
}

function found(path, list) {
	const text = pageText(path);
	return strings(list).map((s) => (text.includes(s) ? s : text.match(pattern(s))?.[0])).filter(Boolean);
}

const named = (obj, lang) => Object.values(obj).flatMap((o) => (o[key(lang)] ? [o[key(lang)].name, o[key(lang)].text] : []));

export default {
	derived: ['zh-cn'],
	skip(path, lang) {
		const bare = path.replace(/^(zh-tw|zh-cn|ja|ko)\//, '');
		const vo = /^characters\/([a-z0-9-]+)\/voice\/$/.exec(bare);
		if (vo && existsSync(new URL(`../records/voices/${vo[1]}.json`, import.meta.url))) {
			const lines = json(`records/voices/${vo[1]}.json`).lines[key(lang)] || {};
			return found(path, [...(lines.daily || []), ...(lines.battle || [])].flatMap((e) => [e.title, e.text]));
		}
		const ch = /^characters\/([a-z0-9-]+)\/(archive\/)?$/.exec(bare);
		if (ch && existsSync(new URL(`../records/characters/${ch[1]}.json`, import.meta.url))) {
			const rec = json(`records/characters/${ch[1]}.json`);
			if (ch[2]) return found(path, (rec.archive?.[key(lang)] || []).flatMap((e) => [e.title, e.text]));
			return found(path, named(rec.outfits || {}, lang));
		}
		if (bare.startsWith('anomalies/') && existsSync(new URL('../records/anomalies.json', import.meta.url))) {
			const rec = json('records/anomalies.json');
			const l = key(lang);
			const a = rec.anomalies.find((x) => bare === `anomalies/${x.slug}/`);
			const commissions = (rec.commissions || []).map((c) => c[l].name);
			if (a) return found(path, [a[l].name, a[l].permission, a[l].quote, ...a[l].parts.flatMap((p) => [p.title, p.text]), ...commissions]);
			return found(path, [...rec.anomalies.flatMap((x) => [x[l].name, x[l].permission]), ...commissions, ...rec.enemies.flatMap((e) => [e[l].name, e[l].place, e[l].text, e[l].hint])]);
		}
		if (bare.startsWith('items/') && existsSync(new URL('../records/lists.json', import.meta.url))) {
			const rec = json('records/lists.json');
			const l = key(lang);
			const items = ['gliders', 'mod-parts', 'figurines', 'gifts'].flatMap((k) => rec[k].flatMap((r) => [r[l].name, r[l].use, r[l].text, ...r[l].sources]));
			const ach = rec.achievements.flatMap((c) => [c[l].label, c[l].name, `${c[l].label}：${c[l].name}`, `${c[l].label}: ${c[l].name}`, ...c.achievements.flatMap((a) => [a[l].title, a[l].desc])]);
			return found(path, [...items, ...ach]);
		}
		if (bare === 'systems/arcs/') return found(path, named(json('records/arcs.json').arcs, lang));
		if (bare === 'systems/progression/') return found(path, named(json('records/items.json').items, lang));
		return [];
	},
};
