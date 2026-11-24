// Site settings for scripts/prose-review.mjs (the prose ledger).
//
// - derived: locales a script writes from another (Simplified Chinese from Traditional,
//   scripts/to-zh-cn.py); their prose is the source locale's, converted, and is read there.
// - skip(path, lang): text the page shows as the game writes it (pipeline/build_pages.py from
//   records/): archive entries, outfit descriptions, and the Arc and item description tables.
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
		const ch = /^characters\/([a-z0-9-]+)\/(archive\/)?$/.exec(bare);
		if (ch && existsSync(new URL(`../records/characters/${ch[1]}.json`, import.meta.url))) {
			const rec = json(`records/characters/${ch[1]}.json`);
			if (ch[2]) return found(path, (rec.archive?.[key(lang)] || []).flatMap((e) => [e.title, e.text]));
			return found(path, named(rec.outfits || {}, lang));
		}
		if (bare === 'systems/arcs/') return found(path, named(json('records/arcs.json').arcs, lang));
		if (bare === 'systems/progression/') return found(path, named(json('records/items.json').items, lang));
		return [];
	},
};
