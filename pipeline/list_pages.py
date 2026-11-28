# Writes the item and achievement lists from records/lists.json (pipeline/build_records.py --lists),
# called by build_pages.py:
#   - items/gliders.md        glider skins: name and description
#   - items/mod-parts.md      vehicle mod parts: name, use (the vehicle and part) and description
#   - items/figurines.md      figurines: name, where they come from and description
#   - items/gifts.md          gifts: name, the characters who prefer them, the affection they gain and
#                             description; then the prices that guide videos show (records/gift-prices.json),
#                             each with a footnote to its video
#   - items/achievements.md   achievements by category: name, condition and whether hidden
# English, Simplified Chinese, Japanese and Korean are the game's own editions. Traditional Chinese
# is everness.info's Taiwan text where it has the entry, else the record's conversion of the
# Simplified text.

import json
import os

from build_pages import DOCS, LANGS, PREFIX, TODAY, L, characters, md_escape, write_archive, yaml_str

LL = {
    'en': dict(
        groups={'furniture': 'Furniture', 'figurines': 'Figurines', 'flowers': 'Flowers', 'music': 'Music', 'other': 'Other gifts'},
        colon=': ',
        titles={'gliders': 'Glider skins', 'mod-parts': 'Mod parts', 'figurines': 'Figurines', 'gifts': 'Gifts', 'achievements': 'Achievements'},
        desc={'gliders': '{n} glider skins in NTE.', 'mod-parts': '{n} vehicle mod parts in NTE.',
              'figurines': '{n} figurines in NTE, shown in the home figurine cabinet.', 'gifts': '{n} gifts in NTE; {p} of them are preferred by at least one character.',
              'achievements': '{n} achievements in NTE in {c} categories; {h} of them are hidden.'},
        name={'gliders': 'Glider skin', 'mod-parts': 'Mod part', 'figurines': 'Figurine', 'gifts': 'Gift', 'achievements': 'Achievement'},
        favor='Affection when preferred', prices='Prices', price='Price (Fons)', vid='叫我棉被 and 零号攻略组, {name} guide video, Bilibili, in Simplified Chinese ({date})', at='{t}, {ts}', use='Use', source='Source', fans='Preferred by', cond='Condition', hidden='Hidden', yes='Yes',
        src_items='nanoka.cc game data {v}, item list in {lang}', src_ach='nanoka.cc game data {v}, achievement list in {lang}',
        src_char='nanoka.cc game data {v}, character files in {lang} (example: {name})',
        src_evach='Everness, achievements page in Traditional Chinese (read {read})'),
    'zh-tw': dict(
        groups={'furniture': '家具', 'figurines': '手辦', 'flowers': '花', 'music': '音樂', 'other': '其他禮物'},
        colon='：',
        titles={'gliders': '滑翔翼造型', 'mod-parts': '改裝件', 'figurines': '手辦', 'gifts': '禮物', 'achievements': '成就'},
        desc={'gliders': '《異環》的 {n} 款滑翔翼造型。', 'mod-parts': '《異環》的 {n} 個載具改裝件。',
              'figurines': '《異環》的 {n} 個手辦，可擺放在住處的手辦櫃。', 'gifts': '《異環》的 {n} 件禮物，其中 {p} 件有角色偏好。',
              'achievements': '《異環》的 {n} 項成就，分為 {c} 類，其中 {h} 項為隱藏成就。'},
        name={'gliders': '滑翔翼造型', 'mod-parts': '改裝件', 'figurines': '手辦', 'gifts': '禮物', 'achievements': '成就'},
        favor='偏好時好感度', prices='售價', price='售價（方斯）', vid='叫我棉被、零號攻略組，{name}攻略影片，Bilibili（簡體中文，{date}）', at='{t}，{ts}', use='用途', source='來源', fans='偏好的角色', cond='條件', hidden='隱藏', yes='是',
        src_items='nanoka.cc 遊戲資料 {v}，道具列表（{lang}）', src_ach='nanoka.cc 遊戲資料 {v}，成就列表（{lang}）',
        src_char='nanoka.cc 遊戲資料 {v}，角色檔案（{lang}，例：{name}）',
        src_evach='Everness，成就頁面（繁體中文，{read} 讀取）',
        # The caveat names the edition most of the page's text comes from.
        caveat_tw='多數文字出自遊戲台港澳版；其餘出自簡體中文版，以繁體字和台灣用詞寫出，用詞可能與台港澳版不同。',
        caveat_cn='多數文字出自遊戲簡體中文版，以繁體字和台灣用詞寫出；台港澳版的用詞可能不同。'),
    'zh-cn': dict(
        groups={'furniture': '家具', 'figurines': '手办', 'flowers': '花', 'music': '音乐', 'other': '其他礼物'},
        colon='：',
        titles={'gliders': '滑翔翼皮肤', 'mod-parts': '改装件', 'figurines': '手办', 'gifts': '礼物', 'achievements': '成就'},
        desc={'gliders': '《异环》的 {n} 款滑翔翼皮肤。', 'mod-parts': '《异环》的 {n} 个载具改装件。',
              'figurines': '《异环》的 {n} 个手办，可摆放在住处的手办柜。', 'gifts': '《异环》的 {n} 件礼物，其中 {p} 件有角色偏好。',
              'achievements': '《异环》的 {n} 项成就，分为 {c} 类，其中 {h} 项为隐藏成就。'},
        name={'gliders': '滑翔翼皮肤', 'mod-parts': '改装件', 'figurines': '手办', 'gifts': '礼物', 'achievements': '成就'},
        favor='偏好时好感度', prices='售价', price='售价（方斯）', vid='叫我棉被、零号攻略组，{name}攻略视频，Bilibili（简体中文，{date}）', at='{t}，{ts}', use='用途', source='来源', fans='偏好的角色', cond='条件', hidden='隐藏', yes='是',
        src_items='nanoka.cc 游戏数据 {v}，道具列表（{lang}）', src_ach='nanoka.cc 游戏数据 {v}，成就列表（{lang}）',
        src_char='nanoka.cc 游戏数据 {v}，角色档案（{lang}，例：{name}）',
        src_evach='Everness，成就页面（繁体中文，{read} 读取）'),
    'ja': dict(
        groups={'furniture': '家具', 'figurines': 'フィギュア', 'flowers': '花', 'music': '音楽', 'other': 'その他のプレゼント'},
        colon='：',
        titles={'gliders': 'グライダースキン', 'mod-parts': '改造パーツ', 'figurines': 'フィギュア', 'gifts': 'プレゼント', 'achievements': '実績'},
        desc={'gliders': 'NTE（異環）のグライダースキン{n}種。', 'mod-parts': 'NTE（異環）の乗り物の改造パーツ{n}種。',
              'figurines': 'NTE（異環）のフィギュア{n}種。住居のフィギュア棚に飾れる。', 'gifts': 'NTE（異環）のプレゼント{n}種。そのうち{p}種を好むキャラクターがいる。',
              'achievements': 'NTE（異環）の実績{n}件で、{c}つのカテゴリに分かれ、そのうち{h}件は隠し実績である。'},
        name={'gliders': 'グライダースキン', 'mod-parts': '改造パーツ', 'figurines': 'フィギュア', 'gifts': 'プレゼント', 'achievements': '実績'},
        favor='好む場合の好感度', prices='価格', price='価格（ファンス）', vid='叫我棉被・零号攻略组、{name}攻略動画、Bilibili、簡体字中国語（{date}）', at='{t}、{ts}', use='用途', source='入手方法', fans='好むキャラクター', cond='条件', hidden='隠し', yes='はい',
        src_items='nanoka.cc ゲームデータ{v}、アイテム一覧（{lang}）', src_ach='nanoka.cc ゲームデータ{v}、実績一覧（{lang}）',
        src_char='nanoka.cc ゲームデータ{v}、キャラクターファイル（{lang}、例：{name}）',
        src_evach='Everness、実績のページ（繁体字中国語、{read}取得）'),
    'ko': dict(
        groups={'furniture': '가구', 'figurines': '피규어', 'flowers': '꽃', 'music': '음악', 'other': '기타 선물'},
        colon=': ',
        titles={'gliders': '글라이더 스킨', 'mod-parts': '튜닝 부품', 'figurines': '피규어', 'gifts': '선물', 'achievements': '업적'},
        desc={'gliders': '이환(NTE)의 글라이더 스킨 {n}종.', 'mod-parts': '이환(NTE)의 탈것 튜닝 부품 {n}종.',
              'figurines': '이환(NTE)의 피규어 {n}종으로, 집의 피규어 진열장에 놓을 수 있다.', 'gifts': '이환(NTE)의 선물 {n}종으로, 그중 {p}종은 선호하는 캐릭터가 있다.',
              'achievements': '이환(NTE)의 업적 {n}개로, {c}개 분류로 나뉘며 그중 {h}개는 숨겨진 업적이다.'},
        name={'gliders': '글라이더 스킨', 'mod-parts': '튜닝 부품', 'figurines': '피규어', 'gifts': '선물', 'achievements': '업적'},
        favor='선호 시 호감도', prices='가격', price='가격(폰즈)', vid='叫我棉被·零号攻略组, {name} 공략 영상, Bilibili, 중국어 간체({date})', at='{t}, {ts}', use='용도', source='획득처', fans='선호 캐릭터', cond='조건', hidden='숨김', yes='예',
        src_items='nanoka.cc 게임 데이터 {v}, {lang} 아이템 목록', src_ach='nanoka.cc 게임 데이터 {v}, {lang} 업적 목록',
        src_char='nanoka.cc 게임 데이터 {v}, {lang} 캐릭터 파일 (예: {name})',
        src_evach='Everness, 업적 페이지(번체 중국어, {read} 확인)'),
}
ORDER = ['gliders', 'mod-parts', 'figurines', 'gifts', 'achievements']
SRC = {'en': 'en', 'zh-cn': 'zh', 'ja': 'ja', 'ko': 'ko'}
NONE = '—'


def cell(text):
    return md_escape(' '.join(text.split())) if text else NONE


def frontmatter(lang, kind, desc, rec, src, taiwan):
    fm = ['---', 'title: ' + yaml_str(LL[lang]['titles'][kind]), 'description: ' + yaml_str(desc), 'aliases:']
    seen = {LL[lang]['titles'][kind]}
    for k in LANGS:
        t = LL[k]['titles'][kind]
        if t not in seen:
            fm.append('  - ' + yaml_str(t))
            seen.add(t)
    fm += ['appliesTo: ' + yaml_str(L[lang]['applies'].format(v=rec['version'])),
           'caveat: ' + yaml_str(L[lang]['caveat'] if lang != 'zh-tw' or taiwan == 1 else LL['zh-tw']['caveat_tw' if taiwan >= 0.5 else 'caveat_cn']),
           f'lastVerified: {TODAY}', 'sidebar:', f'  order: {ORDER.index(kind)}', 'sources:']
    for t, u in src:
        fm += ['  - title: ' + yaml_str(t), '    url: ' + u]
    return '\n'.join(fm + ['---'])


def sources(lang, rec, kind, rows):
    lab, base = LL[lang], 'https://static.nanoka.cc/nte/' + rec['version']
    v, langs = rec['version'], L[lang]['langs']
    if kind == 'achievements':
        out = [(lab['src_ach'].format(v=v, lang=langs[k]), f'{base}/{SRC[k]}/achievement.json') for k in SRC]
        page = rec['achievements_page']
        if page and page['matched']:
            out.append((lab['src_evach'].format(read=page['read']), page['url']))
        return out
    out = [(lab['src_items'].format(v=v, lang=langs[k]), f'{base}/{SRC[k]}/item.json') for k in SRC]
    if kind == 'gifts':
        chars = characters()
        slug = next(s for r in rows for s in r['fans'])
        cid = character_id(slug)
        out += [(lab['src_char'].format(v=v, lang=langs[k], name=chars[slug][lang]), f'{base}/{SRC[k]}/character/{cid}.json') for k in SRC]
        out += [(video_title(lang, lab, x, chars), x['url']) for x in videos()[1]]
    # The Traditional Chinese text's source, in every language, as on the progression page.
    ex = next((r for r in rows if r['id'] in rec['everness']), None)
    if ex:
        e = rec['everness'][ex['id']]
        out.append((L[lang]['evx'].format(kind=L[lang]['kinds']['item'], name=ex[lang]['name'], read=e['read']), e['url']))
    return out


def character_id(slug):
    from fetch_nanoka import character_ids
    return character_ids()[slug]


def item_page(rec, kind, lang):
    lab, p = LL[lang], PREFIX[lang]
    rows = rec[kind]
    if kind == 'gifts':
        chars = characters()
        desc = lab['desc'][kind].format(n=len(rows), p=sum(1 for r in rows if r['fans']))
    else:
        desc = lab['desc'][kind].format(n=len(rows))
    # Share of rows whose text is everness.info's Taiwan text; the Source column is always converted.
    taiwan = sum(1 for r in rows if r['id'] in rec['everness']) / len(rows) * (0.99 if kind == 'figurines' else 1)
    fm = frontmatter(lang, kind, desc, rec, sources(lang, rec, kind, rows), taiwan)
    # Columns: the name, then what the list is looked up by, then the game's description.
    cols = {'gliders': [], 'mod-parts': ['use'], 'figurines': ['sources'], 'gifts': ['fans', 'favor']}[kind]
    head = [lab['name'][kind]] + [{'use': lab['use'], 'sources': lab['source'], 'fans': lab['fans'], 'favor': lab['favor']}[c] for c in cols] + [L[lang]['desc']]
    # Gifts come in sections by item type: one table of 175 rows was all that a readability-style
    # extractor kept of the page.
    parts = [(None, rows)] if kind != 'gifts' else [(lab['groups'][g], [r for r in rows if GROUP.get(r['type'], 'other') == g]) for g in GROUPS]
    out = []
    for title, part in parts:
        if not part:
            continue
        if title:
            out += [('\n' if out else '') + '## ' + title, '']
        out += table(lang, kind, lab, cols, head, part, chars if kind == 'gifts' else None)
    if kind == 'gifts':
        out += prices(lang, lab, rows, chars)
    return fm + '\n\n' + '\n'.join(out) + '\n'


def videos():
    """The guide videos that give gift prices, in the order of records/gift-prices.json."""
    if not os.path.exists('records/gift-prices.json'):
        return [], []
    prices = json.load(open('records/gift-prices.json', encoding='utf-8'))['prices']
    srcs = {s['id']: s for s in json.load(open('records/community/sources.json', encoding='utf-8'))['sources']}
    return prices, [srcs[i] for i in dict.fromkeys(p['source'] for p in prices)]


def video_title(lang, lab, src, chars):
    return lab['vid'].format(name=chars[src['subject']][lang], date=src['published'])


def prices(lang, lab, rows, chars):
    # Prices rest on one guide video each, so each row carries a footnote to that video at its gift table
    # (../AGENTS.md, Visible page); the section comes after the game data's tables.
    ps, vids = videos()
    if not ps:
        return []
    name = {r['id']: r[lang]['name'] for r in rows}
    num = {v['id']: i + 1 for i, v in enumerate(vids)}
    out = ['', '## ' + lab['prices'], '', f"| {lab['name']['gifts']} | {lab['price']} |", '| --- | --- |']
    for p in ps:
        out.append(f"| {md_escape(name[p['id']])} | {p['price']:,}[^{num[p['source']]}] |")
    out.append('')
    for v in vids:
        at = next(p['at'] for p in ps if p['source'] == v['id'])
        ts = f"{at // 60}:{at % 60:02d}"
        out.append(f"[^{num[v['id']]}]: [{lab['at'].format(t=video_title(lang, lab, v, chars), ts=ts)}]({v['url']}?t={at})")
    return out


GROUP = {'ITEM_TYPE_FURNITURE': 'furniture', 'ITEM_TYPE_FIGURES': 'figurines', 'ITEM_TYPE_SHOWCASE': 'figurines',
         'ITEM_TYPE_FLOWER': 'flowers', 'ITEM_TYPE_MUSIC': 'music'}
GROUPS = ['furniture', 'figurines', 'flowers', 'music', 'other']


def table(lang, kind, lab, cols, head, rows, chars):
    out = ['| ' + ' | '.join(head) + ' |', '|' + ' --- |' * len(head)]
    for r in rows:
        t = r[lang]
        cs = [md_escape(t['name'])]
        for c in cols:
            if c == 'use':
                cs.append(cell(t['use']))
            elif c == 'sources':
                cs.append(cell(L[lang]['sep'].join(t['sources'])))
            elif c == 'favor':
                cs.append(str(r['favor']) if 'favor' in r else NONE)
            else:
                # Plain names: a link per name made the table so link-dense that a readability-style
                # extractor dropped the page's answer and notes.
                cs.append(L[lang]['sep'].join(md_escape(chars[s][lang]) for s in r['fans']) or NONE)
        cs.append(cell(t['text']))
        out.append('| ' + ' | '.join(cs) + ' |')
    return out


def achievements_page(rec, lang):
    lab = LL[lang]
    cats = rec['achievements']
    n = sum(len(c['achievements']) for c in cats)
    h = sum(1 for c in cats for a in c['achievements'] if a['hidden'])
    desc = lab['desc']['achievements'].format(n=n, c=len(cats), h=h)
    taiwan = len((rec['achievements_page'] or {}).get('matched', [])) / n
    fm = frontmatter(lang, 'achievements', desc, rec, sources(lang, rec, 'achievements', None), taiwan)
    body = []
    for c in cats:
        body += [f"## {md_escape(c[lang]['label'])}{lab['colon']}{md_escape(c[lang]['name'])}", '']
        body += [f"| {lab['name']['achievements']} | {lab['cond']} | {lab['hidden']} |", '| --- | --- | --- |']
        for a in c['achievements']:
            body.append(f"| {md_escape(a[lang]['title'])} | {cell(a[lang]['desc'])} | {lab['yes'] if a['hidden'] else NONE} |")
        body.append('')
    return fm + '\n\n' + '\n'.join(body)


def build_lists():
    path = 'records/lists.json'
    if not os.path.exists(path):
        return
    rec = json.load(open(path, encoding='utf-8'))
    for lang in LANGS:
        d = f'{DOCS}/{PREFIX[lang]}items'
        os.makedirs(d, exist_ok=True)
        for kind in ORDER[:-1]:
            write_archive(f'{d}/{kind}.md', item_page(rec, kind, lang))
        write_archive(f'{d}/achievements.md', achievements_page(rec, lang))
    print(len(ORDER), 'item and achievement lists written per language')
