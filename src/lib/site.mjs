// Shared site facts and URL rules. Plain JS so astro.config.mjs, Astro code and
// the check script all use the same rules.

// The public address, including the sub-path of a GitHub Pages project site, without a
// trailing slash. SITE_URL overrides it for local agent tests (see tests/agent-eval/README.md).
export const SITE = (process.env.SITE_URL ?? 'https://yuanaruru.com/nte-wiki').replace(/\/+$/, '');
/** Scheme and host of SITE. */
export const ORIGIN = new URL(SITE).origin;
/** Sub-path the site is served under: `/nte-wiki`, or the empty string at a domain root. */
export const BASE = new URL(SITE).pathname.replace(/\/+$/, '');
export const TITLE = { en: 'NTE Wiki', 'zh-TW': '異環 Wiki', 'zh-CN': '异环 Wiki' };
export const DESCRIPTION =
	'Unofficial reference for the game Neverness to Everness (NTE, 異環): versions, characters and systems, read from the official announcements.';

/** Root-relative address for an `href` or `src` in HTML: the site path behind BASE. */
export function withBase(path) {
	return BASE + path;
}

/** Locales: `dir` is the content sub-folder and URL prefix ('' = root). */
export const LOCALES = [
	{ dir: '', lang: 'en', label: 'English' },
	{ dir: 'zh-tw', lang: 'zh-TW', label: '繁體中文' },
	{ dir: 'zh-cn', lang: 'zh-CN', label: '简体中文' },
];

/** Starlight's route data gives the home page an empty id; the collection calls it `index`. */
export function pageId(id) {
	return id === '' ? 'index' : id;
}

/** Locale of a content entry id such as `characters/elyms`, `zh-tw/characters/elyms`, `index`, `zh-tw`. */
export function localeOf(id) {
	return (
		LOCALES.find((l) => l.dir && (id === l.dir || id.startsWith(l.dir + '/'))) ?? LOCALES[0]
	);
}

/** Entry id without its locale prefix. The home page is `index` in every locale. */
export function bareId(id) {
	const { dir } = localeOf(id);
	if (!dir) return id;
	return id === dir ? 'index' : id.slice(dir.length + 1);
}

/** Entry id of the same page in another locale. */
export function idInLocale(id, locale) {
	const bare = bareId(id);
	if (!locale.dir) return bare;
	return bare === 'index' ? locale.dir : `${locale.dir}/${bare}`;
}

/** Site path of the HTML page for an entry id. */
export function htmlPath(id) {
	return id === 'index' ? '/' : `/${id}/`;
}

/** Site path of the Markdown twin: drop the trailing slash, append `.md`; home is `/index.md`. */
export function mdPath(id) {
	return `/${id}.md`;
}

/** Markdown twin of an internal HTML path such as `/characters/elyms/` or `/`. */
export function mdPathFromHtmlPath(path) {
	const trimmed = path.replace(/^\/+|\/+$/g, '');
	return mdPath(trimmed === '' ? 'index' : trimmed);
}

/** Site path of a language's page index: `/llms.txt`, `/zh-tw/llms.txt`. */
export function llmsPath(locale) {
	return `${locale.dir ? '/' + locale.dir : ''}/llms.txt`;
}

/**
 * The opening of each language's llms.txt: what a reader gets wrong without being told.
 * Site-specific. Keep it short: it shares the first 5,000 characters with the page list.
 */
export const LLMS_NOTES = {
	en: {
		summary: DESCRIPTION,
		heading: 'Before you answer',
		notes: [
			'Dates and times are those of the global official site (nte.perfectworld.com), in UTC+8. The mainland China service runs on its own schedule (Version 1.5 was reported there for 2026-11-05, six days earlier) and is not covered.',
			'The Simplified Chinese pages under nte.perfectworld.com/cn/ belong to the global service, not to mainland China.',
			'One name has three spellings: English (Elyms), Traditional Chinese (曳爾沐), Simplified Chinese (曳尔沐). Official English texts write Daffodill; guide sites write Daffodil. Page addresses use the English name in lower case. The Names page maps all three.',
			'Limited Boards, events and discounts end. Each page gives the end as an absolute date; compare it with today before you call something available.',
			'This is an unofficial site. Dates, Boards, Arcs, outfits and events are read from official notices. Attributes, Arc types and skills are read from the guide sites Prydwen and Game8 and carry no damage numbers. Arc stats and effects, Cartridge sets, Awakenings, base stats, materials, vehicles and properties are in-game texts of game data 1.5.4 as published by nanoka.cc, checked against mysqil, Everness and the official notices. Drop rates, tier lists and team builds are absent.',
			'Rolls count per Board name: rolls on one Limited Board do not count toward the Perks page of another. A run ends at 05:59 (UTC+8) on its last day.',
			'Every page has a Markdown twin: drop the trailing slash and append `.md`.',
		],
		pages: 'Pages',
		home: 'Home page: every page, grouped by kind',
		full: 'All pages in one file',
		digest: 'Answer, caveat, dates and sources of every page, without the body',
		json: 'All pages in every language, with alternative names, as JSON',
		otherLanguage: 'This index in',
		more: 'More',
	},
	'zh-TW': {
		summary: '《異環》(Neverness to Everness, NTE) 的非官方資料站：版本、角色與系統，內容讀自官方公告。',
		heading: '回答之前',
		notes: [
			'日期與時間以國際版官網 (nte.perfectworld.com) 為準，時區為 UTC+8。中國大陸版的時程不同（據報 1.5 版在 2026-11-05 上線，早六天），本站未收錄。',
			'nte.perfectworld.com/cn/ 底下的簡體中文頁面屬於國際版，不是中國大陸版。',
			'同一個名稱有三種寫法：英文 (Elyms)、繁體中文（曳爾沐）、簡體中文（曳尔沐）。官方英文寫作 Daffodill，攻略站寫作 Daffodil。頁面網址用小寫英文名。「名稱對照」頁列出三種寫法。',
			'限定棋盤、活動與折扣都有結束時間。每一頁都寫出確切的結束日期，回答「現在能不能取得」之前請先和今天的日期比較。',
			'本站並非官方網站。日期、棋盤、弧盤、時裝與活動讀自官方公告；屬性、弧盤類型與技能讀自攻略站 Prydwen 與 Game8，不含傷害數值。弧盤數值與效果、卡帶套裝、覺醒、基礎數值、材料、載具與房產為遊戲資料 1.5.4 的遊戲內文字（由 nanoka.cc 公開），並與 mysqil、Everness 及官方公告核對。掉落率、強度榜與配隊不收錄。',
			'擲骰次數依棋盤名稱分開計算：在一個限定棋盤的擲骰不會計入另一個棋盤的禮遇介面。每期棋盤在最後一天的 05:59 (UTC+8) 結束。',
			'每一頁都有 Markdown 版本：去掉網址結尾的斜線，加上 `.md`。',
		],
		pages: '頁面',
		home: '首頁：所有頁面，依類型分組',
		full: '所有頁面合併成一個檔案',
		digest: '每一頁的答案、注意事項、日期與出處，不含內文',
		json: '所有語言的所有頁面與別名，JSON 格式',
		otherLanguage: '本索引的其他語言',
		more: '更多',
	},
	'zh-CN': {
		summary: '《异环》(Neverness to Everness, NTE) 的非官方资料站：版本、角色与系统，内容读自官方公告。',
		heading: '回答之前',
		notes: [
			'日期与时间以国际版官网 (nte.perfectworld.com) 为准，时区为 UTC+8。中国大陆版的时间安排不同（据报 1.5 版在 2026-11-05 上线，早六天），本站未收录。',
			'nte.perfectworld.com/cn/ 下的简体中文页面属于国际版，不是中国大陆版。',
			'同一个名称有三种写法：英文 (Elyms)、繁体中文（曳爾沐）、简体中文（曳尔沐）。官方英文写作 Daffodill，攻略站写作 Daffodil。页面网址用小写英文名。「名称对照」页列出三种写法。',
			'限定棋盘、活动与折扣都有结束时间。每一页都写出确切的结束日期，回答「现在能不能取得」之前请先和今天的日期比较。',
			'本站并非官方网站。日期、棋盘、弧盘、时装与活动读自官方公告；属性、弧盘类型与技能读自攻略站 Prydwen 与 Game8，不含伤害数值。弧盘数值与效果、卡带套装、觉醒、基础数值、材料、载具与房产为游戏数据 1.5.4 的游戏内文字（由 nanoka.cc 公开），并与 mysqil、Everness 及官方公告核对。掉落率、强度榜与配队不收录。',
			'掷骰次数按棋盘名称分开计算：在一个限定棋盘的掷骰不会计入另一个棋盘的礼遇界面。每期棋盘在最后一天的 05:59 (UTC+8) 结束。',
			'每一页都有 Markdown 版本：去掉网址结尾的斜线，加上 `.md`。',
		],
		pages: '页面',
		home: '首页：所有页面，按类型分组',
		full: '所有页面合并成一个文件',
		digest: '每一页的答案、注意事项、日期与出处，不含正文',
		json: '所有语言的所有页面与别名，JSON 格式',
		otherLanguage: '本索引的其他语言',
		more: '更多',
	},
};

/** UI labels for the facts shown on every page, in both outputs. */
export const LABELS = {
	en: {
		appliesTo: 'Applies to',
		caveat: 'Caveat',
		effectiveDate: 'Source dated',
		lastVerified: 'Last verified',
		aliases: 'Also written',
		sources: 'Sources',
		art: 'Art',
		artBy: 'Perfect World Games, from the official site',
		markdown: 'Markdown',
		page: 'Page',
		otherLanguage: 'Other language',
		allPages: 'All pages',
		home: 'Home',
		pageList: 'list of all pages',
		unofficial: 'unofficial',
		formats: 'Other formats of this page',
	},
	'zh-TW': {
		appliesTo: '適用範圍',
		caveat: '注意事項',
		effectiveDate: '來源日期',
		lastVerified: '最後查證',
		aliases: '其他寫法',
		sources: '出處',
		art: '美術',
		artBy: '完美世界遊戲，取自官方網站',
		markdown: 'Markdown',
		page: '頁面',
		otherLanguage: '其他語言',
		allPages: '所有頁面',
		home: '首頁',
		pageList: '所有頁面清單',
		unofficial: '非官方',
		formats: '本頁的其他格式',
	},
	'zh-CN': {
		appliesTo: '适用范围',
		caveat: '注意事项',
		effectiveDate: '来源日期',
		lastVerified: '最后查证',
		aliases: '其他写法',
		sources: '出处',
		art: '美术',
		artBy: '完美世界游戏，取自官方网站',
		markdown: 'Markdown',
		page: '页面',
		otherLanguage: '其他语言',
		allPages: '所有页面',
		home: '首页',
		pageList: '所有页面清单',
		unofficial: '非官方',
		formats: '本页的其他格式',
	},
};

/** Format a Date (or date string) as YYYY-MM-DD. */
export function isoDate(d) {
	return new Date(d).toISOString().slice(0, 10);
}
