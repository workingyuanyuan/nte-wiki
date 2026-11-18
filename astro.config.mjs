// @ts-check
import { defineConfig } from 'astro/config';
import starlight from '@astrojs/starlight';
import starlightLinksValidator from 'starlight-links-validator';
import { ORIGIN, BASE, TITLE, DESCRIPTION } from './src/lib/site.mjs';
import { satteri } from '@astrojs/markdown-satteri';
import { hastBase } from './src/lib/hast-base.mjs';

export default defineConfig({
	site: ORIGIN,
	base: BASE || undefined,
	trailingSlash: 'always',
	// Content links are written without the sub-path; this adds it in the HTML.
	markdown: { processor: satteri({ hastPlugins: [hastBase] }) },
	integrations: [
		starlight({
			title: { en: TITLE.en, 'zh-TW': TITLE['zh-TW'] },
			description: DESCRIPTION,
			defaultLocale: 'root',
			locales: {
				root: { label: 'English', lang: 'en' },
				'zh-tw': { label: '繁體中文', lang: 'zh-TW' },
			},
			sidebar: [
				{
					label: 'Versions',
					translations: { 'zh-TW': '版本' },
					items: [{ autogenerate: { directory: 'versions' } }],
				},
				{
					label: 'Characters',
					translations: { 'zh-TW': '角色' },
					items: [{ autogenerate: { directory: 'characters' } }],
				},
				{
					label: 'Systems and names',
					translations: { 'zh-TW': '系統與名稱' },
					items: [{ slug: 'systems/boards' }, { slug: 'systems/platforms' }, { slug: 'names' }],
				},
			],
			customCss: ['./src/styles/nte.css'],
			components: {
				// Only two overrides: the site name with its links, and the answer above the body and the page notes after it.
				SiteTitle: './src/components/SiteTitle.astro',
				MarkdownContent: './src/components/MarkdownContent.astro',
				ThemeSelect: './src/components/ThemeSelect.astro',
			},
			routeMiddleware: './src/routeData.ts',
			credits: false,
			pagination: false,
			expressiveCode: {
				themes: ['night-owl', 'github-light'],
				// `patch` gets diff colours but keeps the literal +/- in the page text.
				// The `diff` language is not used: Expressive Code draws its +/- with CSS,
				// so an agent reading the HTML would not see which lines were added or removed.
				shiki: { langAlias: { patch: 'diff' } },
				styleOverrides: { borderRadius: '0', borderWidth: '1px', frames: { shadowColor: 'transparent' } },
			},
			plugins: [
				starlightLinksValidator({
					exclude: ['/**/*.md', '/*.md', '/llms.txt', '/**/llms.txt', '/index.json', '/**/index.json', '/**/art/**'],
				}),
			],
		}),
	],
});
