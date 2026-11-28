// @ts-check
import { defineConfig } from 'astro/config';
import starlight from '@astrojs/starlight';
import sitemap from '@astrojs/sitemap';
import starlightLinksValidator from 'starlight-links-validator';
import { sitemapOptions } from './src/lib/sitemap.mjs';
import { ORIGIN, BASE, TITLE, DESCRIPTION } from './src/lib/site.mjs';
import { satteri } from '@astrojs/markdown-satteri';
import { hastBase, hastTableBody, hastFootnotes } from './src/lib/hast-base.mjs';
import { readFileSync } from 'node:fs';

// The character guide pages of the community section, in the character list's order (pipeline/build_community.py writes it).
const GUIDES = JSON.parse(readFileSync(new URL('./src/community-guides.json', import.meta.url), 'utf-8'));

export default defineConfig({
	site: ORIGIN,
	base: BASE || undefined,
	trailingSlash: 'always',
	// Content links are written without the sub-path; this adds it in the HTML.
	markdown: { processor: satteri({ hastPlugins: [hastBase, hastTableBody, hastFootnotes] }) },
	integrations: [
		// Added here so that it takes options; Starlight then leaves its own copy out.
		sitemap(sitemapOptions()),
		starlight({
			title: TITLE,
			description: DESCRIPTION,
			defaultLocale: 'root',
			locales: {
				root: { label: 'English', lang: 'en' },
				'zh-tw': { label: '繁體中文', lang: 'zh-TW' },
				'zh-cn': { label: '简体中文', lang: 'zh-CN' },
				ja: { label: '日本語', lang: 'ja' },
				ko: { label: '한국어', lang: 'ko' },
			},
			sidebar: [
				{
					label: 'Versions',
					translations: { 'zh-TW': '版本', 'zh-CN': '版本', ja: 'バージョン', ko: '버전' },
					items: [{ autogenerate: { directory: 'versions' } }],
				},
				{
					label: 'Characters',
					translations: { 'zh-TW': '角色', 'zh-CN': '角色', ja: 'キャラクター', ko: '캐릭터' },
					items: [{ autogenerate: { directory: 'characters' } }],
				},
				{
					label: 'Anomalies',
					translations: { 'zh-TW': '異象', 'zh-CN': '异象', ja: '異象', ko: '이상' },
					items: [{ autogenerate: { directory: 'anomalies' } }],
				},
				{
					label: 'Items and achievements',
					translations: { 'zh-TW': '道具與成就', 'zh-CN': '道具与成就', ja: 'アイテムと実績', ko: '아이템과 업적' },
					items: [{ autogenerate: { directory: 'items' } }],
				},
				{
					label: 'Systems and names',
					translations: { 'zh-TW': '系統與名稱', 'zh-CN': '系统与名称', ja: 'システムと名前', ko: '시스템과 이름' },
					items: [
						{ slug: 'systems/boards' },
						{ slug: 'systems/esper-cycles' },
						{ slug: 'systems/arcs' },
						{ slug: 'systems/consoles' },
						{ slug: 'systems/progression' },
						{ slug: 'systems/vehicles' },
						{ slug: 'systems/properties' },
						{ slug: 'systems/platforms' },
						{ slug: 'names' },
					],
				},
				{
					label: 'Community guides',
					translations: { 'zh-TW': '社群攻略', 'zh-CN': '社群攻略', ja: 'コミュニティ攻略', ko: '커뮤니티 공략' },
					items: [{ slug: 'community' }, { slug: 'community/teams' }, { slug: 'community/builds' }, ...GUIDES.map((g) => ({ slug: `community/${g}` }))],
				},
			],
			customCss: ['./src/styles/nte.css'],
			components: {
				// Three overrides: the site name with its links, the answer above the body with the page notes after it, and the theme buttons.
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
