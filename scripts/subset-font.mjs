// Cuts the pixel font down to the characters the site shows, so the download is
// about 100 KB instead of 700 KB. Runs before every build (see package.json); the
// output public/fonts/pixel.woff2 is generated and not committed.
//
// Source: assets/fonts/fusion-pixel-12px-proportional-zh_hant.otf.woff2
// (Fusion Pixel Font 2026.11.10, SIL OFL 1.1, licence in assets/fonts/OFL.txt).

import { readFile, writeFile, mkdir, readdir } from 'node:fs/promises';
import { join, extname } from 'node:path';
import { fileURLToPath } from 'node:url';
import subsetFont from 'subset-font';

const root = fileURLToPath(new URL('..', import.meta.url));
const SOURCE = join(root, 'assets/fonts/fusion-pixel-12px-proportional-zh_hant.otf.woff2');
const OUT = join(root, 'public/fonts/pixel.woff2');
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

const chars = new Set();
// Printable ASCII is always kept: Starlight's own interface text is not in src/.
for (let c = 0x20; c < 0x7f; c++) chars.add(String.fromCharCode(c));
for (const input of INPUTS) {
	for await (const file of walk(join(root, input))) {
		for (const ch of await readFile(file, 'utf8')) if (ch > ' ') chars.add(ch);
	}
}
// Starlight's Traditional Chinese interface text (search, table of contents, pagination).
for (const ch of '搜尋本頁內容上一頁下一頁概述選擇主題語言深色淺色自動選單跳到內容取消清除目錄') chars.add(ch);

const subset = await subsetFont(await readFile(SOURCE), [...chars].join(''), { targetFormat: 'woff2' });
await mkdir(join(root, 'public/fonts'), { recursive: true });
await writeFile(OUT, subset);
console.log(`pixel font: ${chars.size} characters, ${(subset.length / 1024).toFixed(0)} KB`);
