// Sätteri plugin: puts the site's sub-path in front of root-relative links and images
// (`/characters/elyms/`, `/art/elyms.webp`), so content is written without it and
// still works on a GitHub Pages project site. The Markdown twins do not pass through
// here: src/lib/page-md.mjs turns the same links into absolute URLs.

import { defineHastPlugin } from 'satteri';
import { BASE } from './site.mjs';

export const hastBase = defineHastPlugin({
	name: 'site-base',
	element: {
		filter: ['a', 'img'],
		visit(node, ctx) {
			const key = node.tagName === 'a' ? 'href' : 'src';
			const value = node.properties?.[key];
			if (BASE && typeof value === 'string' && /^\/(?!\/)/.test(value)) {
				ctx.setProperty(node, key, BASE + value);
			}
		},
	},
});

// Readability-style extractors score a table body from its cells and keep the parent chain
// only while each parent scores at least a third of the best candidate. A table scores
// exactly a third of its body, so on a page with one long table (Arc effects in Japanese
// and Korean) rounding decided whether the extractor kept the whole article or only that
// table. Their class weighting counts "scroll" as a negative signal; this class lowers
// every table body so that the article container stays the best candidate. Not styled.
export const hastTableBody = defineHastPlugin({
	name: 'table-body-weight',
	element: {
		filter: ['tbody'],
		visit(node, ctx) {
			ctx.setProperty(node, 'className', ['rows-scroll']);
		},
	},
});
