// Cuts the pixel font down to the characters the site shows, so the download is
// about 100 KB instead of 700 KB. Runs before every build (see package.json); the
// output in public/fonts/ is generated and not committed.
//
// Sources: assets/fonts/fusion-pixel-12px-proportional-{zh_hant,ja,ko}.otf.woff2
// (Fusion Pixel Font 2026.11.10, SIL OFL 1.1, licences in assets/fonts/OFL.txt and
// assets/fonts/LICENSES/). The Traditional Chinese file serves English and both
// Chinese languages; Japanese and Korean pages each load their own file, with the
// glyph forms of that language.

import { readFile, writeFile, mkdir, readdir } from 'node:fs/promises';
import { join, extname } from 'node:path';
import { fileURLToPath } from 'node:url';
import subsetFont from 'subset-font';

const root = fileURLToPath(new URL('..', import.meta.url));
const DOCS = join(root, 'src/content/docs');
// Each output takes the shared files plus the content folders listed in `docs` (null: every
// folder except those of the other outputs) and Starlight's interface text in `ui`.
const FONTS = [
	{ source: 'zh_hant', out: 'pixel.woff2', docs: null, ui: ['zh-TW', 'zh-CN'] },
	{ source: 'ja', out: 'pixel-ja.woff2', docs: ['ja'], ui: ['ja'] },
	{ source: 'ko', out: 'pixel-ko.woff2', docs: ['ko'], ui: ['ko'] },
];
const OWN = FONTS.flatMap((f) => f.docs ?? []).map((d) => join(DOCS, d));
// Every file whose text can reach a page: content, labels, sidebar, components, skin.
const INPUTS = ['src', 'astro.config.mjs'];
const TEXT = new Set(['.md', '.mjs', '.ts', '.astro', '.css']);

async function* walk(path) {
	const entries = await readdir(path, { withFileTypes: true }).catch(() => null);
	if (!entries) {
		yield path;
		return;
	}
	for (const entry of entries) {
		const full = join(path, entry.name);
		if (entry.isDirectory()) yield* walk(full);
		else if (TEXT.has(extname(entry.name))) yield full;
	}
}

const shared = new Set();
// Printable ASCII is always kept: Starlight's own interface text is not in src/.
for (let c = 0x20; c < 0x7f; c++) shared.add(String.fromCharCode(c));
const perFolder = new Map(OWN.map((d) => [d, new Set()]));
const rest = new Set();
for (const input of INPUTS) {
	for await (const file of walk(join(root, input))) {
		const own = OWN.find((d) => file.startsWith(d + '/'));
		const target = own ? perFolder.get(own) : file.startsWith(DOCS + '/') ? rest : shared;
		for (const ch of await readFile(file, 'utf8')) if (ch > ' ') target.add(ch);
	}
}

await mkdir(join(root, 'public/fonts'), { recursive: true });
for (const font of FONTS) {
	const chars = new Set([...shared, ...(font.docs ? font.docs.flatMap((d) => [...perFolder.get(join(DOCS, d))]) : rest)]);
	// Starlight's own interface text (search, table of contents, theme and language labels).
	for (const lang of font.ui) {
		const file = join(root, `node_modules/@astrojs/starlight/dist/translations/${lang}.js`);
		for (const ch of await readFile(file, 'utf8')) if (ch > '~') chars.add(ch);
	}
	const source = join(root, `assets/fonts/fusion-pixel-12px-proportional-${font.source}.otf.woff2`);
	const subset = await subsetFont(await readFile(source), [...chars].join(''), { targetFormat: 'woff2' });
	await writeFile(join(root, 'public/fonts', font.out), subset);
	console.log(`pixel font ${font.out}: ${chars.size} characters, ${(subset.length / 1024).toFixed(0)} KB`);
}
