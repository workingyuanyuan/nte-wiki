// Heading levels: in the text column each level is smaller than the one above it, at a
// phone width and on a wide window. Starlight sizes h1-h4 from the --sl-text-h* tokens and
// raises them at 50em; a skin that sets one level and leaves the next to Starlight can put
// a larger h3 under its h2 (nte-wiki: 29px bold under a 24px h2, until 2026-11-25).
// The sizes are read from Starlight's props.css and the skin's own customCss files (not
// packages such as fonts), the skin
// winning as unlayered CSS does over Starlight's layer.

import { readFileSync } from 'node:fs';

const WIDTHS = [375, 1280, 2560];
const ROOT_PX = 16;

const isRoot = (selector) => selector?.split(',').some((s) => s.trim() === ':root');

// Declarations of --sl-text-* in `:root` blocks, each with the min-width (px) of the
// @media block around it, 0 when there is none.
function tokens(css) {
	const out = [];
	const stack = [];
	let buffer = '';
	for (const ch of css.replace(/\/\*[\s\S]*?\*\//g, '')) {
		if (ch === '{') {
			stack.push(buffer.trim());
			buffer = '';
		} else if (ch === '}') {
			if (isRoot(stack.at(-1))) {
				const media = stack.slice(0, -1).find((s) => s.startsWith('@media'));
				if (!media || /min-width/.test(media)) {
					const m = media?.match(/min-width:\s*([\d.]+)(em|rem|px)/);
					const minWidth = m ? Number(m[1]) * (m[2] === 'px' ? 1 : ROOT_PX) : 0;
					for (const decl of buffer.split(';')) {
						const d = decl.match(/^\s*(--sl-text-[\w-]+)\s*:\s*(.+?)\s*$/);
						if (d) out.push({ name: d[1], value: d[2], minWidth });
					}
				}
			}
			stack.pop();
			buffer = '';
		} else if (ch === ';' && !isRoot(stack.at(-1))) {
			buffer = '';
		} else {
			buffer += ch;
		}
	}
	return out;
}

function px(value, map, depth = 0) {
	const v = value.match(/^var\((--[\w-]+)\)$/);
	if (v) return depth < 10 && map.has(v[1]) ? px(map.get(v[1]), map, depth + 1) : NaN;
	const n = value.match(/^([\d.]+)(px|rem)$/);
	return n ? Number(n[1]) * (n[2] === 'px' ? 1 : ROOT_PX) : NaN;
}

export function checkHeadings(fail) {
	const config = readFileSync(new URL('../astro.config.mjs', import.meta.url), 'utf8');
	const skinFiles = [...(config.match(/customCss:\s*\[([^\]]*)\]/)?.[1] ?? '').matchAll(/'(\.\/[^']+)'/g)].map((m) => m[1]);
	// The package exports no path to its CSS, so it is read from node_modules.
	const props = new URL('../node_modules/@astrojs/starlight/dist/style/props.css', import.meta.url);
	const starlight = tokens(readFileSync(props, 'utf8'));
	const skin = skinFiles.flatMap((f) => tokens(readFileSync(new URL('../' + f.replace(/^\.\//, ''), import.meta.url), 'utf8')));
	for (const width of WIDTHS) {
		const map = new Map();
		for (const t of [...starlight, ...skin]) if (t.minWidth <= width) map.set(t.name, t.value);
		const size = (level) => px(map.get(`--sl-text-${level}`) ?? '', map);
		const levels = ['h2', 'h3', 'h4'].map((level) => [level, size(level)]);
		if (levels.some(([, s]) => Number.isNaN(s))) {
			fail('skin', `heading sizes at ${width}px could not be read: ${levels.map(([l, s]) => `${l} ${s}`).join(', ')}`);
			continue;
		}
		for (let i = 1; i < levels.length; i++) {
			const [upper, a] = levels[i - 1];
			const [lower, b] = levels[i];
			if (b >= a) fail('skin', `at ${width}px ${lower} is ${b}px, not smaller than ${upper} at ${a}px (set --sl-text-${lower} in the skin)`);
		}
	}
}
