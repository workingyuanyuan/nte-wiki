# Writes the anomaly pages from records/anomalies.json (pipeline/build_records.py --monsters),
# called by build_pages.py:
#   - anomalies/index.md       the anomaly commissions of the monster list, with code, difficulty and anomaly
#   - anomalies/<slug>.md      one page per anomaly file: its facts, the quotation and every part of the file
#   - anomalies/enemies.md     the enemy manual: every entry, by kind
# Traditional Chinese is the record's conversion of the Simplified text; every other language
# is the game's own edition.

import json
import os
import re
import sys

from build_pages import DOCS, LANGS, PREFIX, TODAY, L, cells, md_escape, paragraphs, table_rows, write_archive, yaml_str

AL = {
    'en': dict(
        index='Anomalies', manual='Enemy manual',
        index_desc='Anomalies that the player defeats in {n} NTE anomaly commissions; {a} of them have an archive file.',
        page_desc='{name} is an anomaly with the code {code}.',
        manual_desc="NTE's enemy manual has {n} entries: {b} bosses, {e} elite and {c} common enemies.",
        fact='Fact', value='Value', code='Code', anomaly='Anomaly', permission='Permission', level='Level',
        commission='Anomaly commission', difficulty='Difficulty', sep=', ',
        enemy='Enemy', place='Location', material='Material', file='Anomaly file',
        kinds={'Elite': 'Elite enemies', 'Normal': 'Common enemies'},
        src_file='nanoka.cc game data {v}, {name} file in {lang}', src_list='nanoka.cc game data {v}, monster list',
        src_ax='nanoka.cc game data {v}, anomaly files in {lang} (example: {name})',
        src_ex='nanoka.cc game data {v}, enemy files in {lang} (example: {name})'),
    'zh-tw': dict(
        index='異象列表', manual='敵人圖鑑',
        index_desc='玩家在《異環》{n} 個異象委託中擊敗的異象，其中 {a} 個有異象檔案。',
        page_desc='{name}是異象，編號 {code}。',
        manual_desc='《異環》的敵人圖鑑共 {n} 筆：首領 {b} 個、精英敵人 {e} 個、普通敵人 {c} 個。',
        fact='項目', value='內容', code='編號', anomaly='異象', permission='權限', level='等級',
        commission='異象委託', difficulty='難度', sep='、',
        enemy='敵人', place='地點', material='材料', file='異象檔案',
        kinds={'Elite': '精英敵人', 'Normal': '普通敵人'},
        src_file='nanoka.cc 遊戲資料 {v}，{name}檔案（{lang}）', src_list='nanoka.cc 遊戲資料 {v}，怪物列表',
        src_ax='nanoka.cc 遊戲資料 {v}，異象檔案（{lang}，例：{name}）',
        src_ex='nanoka.cc 遊戲資料 {v}，敵人檔案（{lang}，例：{name}）',
        caveat='文字為遊戲簡體中文版的內容，以繁體字和台灣用詞寫出；台港澳版的用詞可能不同。'),
    'zh-cn': dict(
        index='异象列表', manual='敌人图鉴',
        index_desc='玩家在《异环》{n} 个异象委托中击败的异象，其中 {a} 个有异象档案。',
        page_desc='{name}是异象，编号 {code}。',
        manual_desc='《异环》的敌人图鉴共 {n} 条：首领 {b} 个、精英敌人 {e} 个、普通敌人 {c} 个。',
        fact='项目', value='内容', code='编号', anomaly='异象', permission='权限', level='等级',
        commission='异象委托', difficulty='难度', sep='、',
        enemy='敌人', place='地点', material='材料', file='异象档案',
        kinds={'Elite': '精英敌人', 'Normal': '普通敌人'},
        src_file='nanoka.cc 游戏数据 {v}，{name}档案（{lang}）', src_list='nanoka.cc 游戏数据 {v}，怪物列表',
        src_ax='nanoka.cc 游戏数据 {v}，异象档案（{lang}，例：{name}）',
        src_ex='nanoka.cc 游戏数据 {v}，敌人档案（{lang}，例：{name}）'),
    'ja': dict(
        index='異象一覧', manual='敵図鑑',
        index_desc='NTE（異環）の異象依頼{n}件でプレイヤーが倒す異象。そのうち{a}体に異象ファイルがある。',
        page_desc='{name}は異象で、コードは{code}である。',
        manual_desc='NTE（異環）の敵図鑑は{n}件で、ボス{b}体、エリート敵{e}体、通常の敵{c}体である。',
        fact='項目', value='内容', code='コード', anomaly='異象', permission='権限', level='レベル',
        commission='異象依頼', difficulty='難易度', sep='、',
        enemy='敵', place='場所', material='素材', file='異象ファイル',
        kinds={'Elite': 'エリート敵', 'Normal': '通常の敵'},
        src_file='nanoka.cc ゲームデータ{v}、{name}のファイル（{lang}）', src_list='nanoka.cc ゲームデータ{v}、モンスター一覧',
        src_ax='nanoka.cc ゲームデータ{v}、異象のファイル（{lang}、例：{name}）',
        src_ex='nanoka.cc ゲームデータ{v}、敵のファイル（{lang}、例：{name}）'),
    'ko': dict(
        index='이상 목록', manual='적 도감',
        index_desc='이환(NTE)의 이상 의뢰 {n}개에서 플레이어가 처치하는 이상으로, 그중 {a}개에 이상 파일이 있다.',
        page_desc='이상 {name}의 코드는 {code}다.',
        manual_desc='이환(NTE)의 적 도감은 {n}개로, 보스 {b}개, 엘리트 적 {e}개, 일반 적 {c}개다.',
        fact='항목', value='내용', code='코드', anomaly='이상', permission='권한', level='등급',
        commission='이상 의뢰', difficulty='난이도', sep=', ',
        enemy='적', place='장소', material='재료', file='이상 파일',
        kinds={'Elite': '엘리트 적', 'Normal': '일반 적'},
        src_file='nanoka.cc 게임 데이터 {v}, {lang} {name} 파일', src_list='nanoka.cc 게임 데이터 {v}, 몬스터 목록',
        src_ax='nanoka.cc 게임 데이터 {v}, {lang} 이상 파일 (예: {name})',
        src_ex='nanoka.cc 게임 데이터 {v}, {lang} 적 파일 (예: {name})'),
}
SRC = {'en': 'en', 'zh-cn': 'zh', 'ja': 'ja', 'ko': 'ko'}
# The enemy manual's two kinds of boss are the bosses of two activities: the progression page
# names each boss with its activity (build_anomalies checks that they agree), and its tables
# give the activity's name in each language.
ACTIVITY = {'WeeklyBoss': 'Anomaly Hunt', 'Boss': 'Anomaly Pilgrimage'}
KIND_ORDER = ['WeeklyBoss', 'Boss', 'Elite', 'Normal']
NONE = '—'


def drops():
    # {English boss name: {'activity': ..., lang: (activity, material, characters cell)}} from the
    # material tables of the progression page, whose rows are in the same order in every language.
    rows = {lang: [cells(r) for r in table_rows(open(f'{DOCS}/{PREFIX[lang]}systems/progression.md', encoding='utf-8').read()) if len(cells(r)) == 3] for lang in LANGS}
    out = {}
    for i, r in enumerate(rows['en']):
        m = re.match(r'(Anomaly (?:Hunt|Pilgrimage)):? "?([^"]+)"?$', r[1])
        if not m:
            continue
        out[m.group(2)] = {'activity': m.group(1)}
        for lang in LANGS:
            c = rows[lang][i]
            act = re.match(r'(.+?)\s*「', c[1]) or re.match(r'(Anomaly (?:Hunt|Pilgrimage))', c[1])
            out[m.group(2)][lang] = (act.group(1), c[0], c[2])
    return out


def sources(lang, files, rec):
    lab, v, base = {**L[lang], **AL[lang]}, rec['version'], 'https://static.nanoka.cc/nte/' + rec['version']
    out = []
    for k in ['en', 'zh-cn', 'ja', 'ko']:
        for name, f in files:
            out.append((lab['src_file'].format(v=v, name=name, lang=lab['langs'][k]), f'{base}/{SRC[k]}/monster/{f}.json'))
    return out


def frontmatter(lang, titles, desc, rec, src, order, hide=False):
    lab = {**L[lang], **AL[lang]}
    fm = ['---', 'title: ' + yaml_str(titles[lang]), 'description: ' + yaml_str(desc), 'aliases:']
    seen = {titles[lang]}
    for k in LANGS:
        if titles[k] not in seen:
            fm.append('  - ' + yaml_str(titles[k]))
            seen.add(titles[k])
    fm += ['appliesTo: ' + yaml_str(lab['applies'].format(v=rec['version'])),
           'caveat: ' + yaml_str(AL['zh-tw']['caveat'] if lang == 'zh-tw' else L[lang]['caveat']),
           f'lastVerified: {TODAY}']
    if hide:
        fm.append('hideAnswer: true')
    fm += ['sidebar:', f'  order: {order}', 'sources:']
    for t, u in src:
        fm += ['  - title: ' + yaml_str(t), '    url: ' + u]
    return '\n'.join(fm + ['---'])


def index_page(rec, lang):
    lab, p = AL[lang], PREFIX[lang]
    titles = {k: AL[k]['index'] for k in LANGS}
    base = 'https://static.nanoka.cc/nte/' + rec['version']
    ex = rec['anomalies'][0]
    src = [(lab['src_list'].format(v=rec['version']), f'{base}/monster.json')]
    src += [(lab['src_ax'].format(v=rec['version'], lang=L[lang]['langs'][k], name=ex[lang]['name']), f"{base}/{SRC[k]}/monster/{ex['file']}.json") for k in ['en', 'zh-cn', 'ja', 'ko']]
    fm = frontmatter(lang, titles, lab['index_desc'].format(n=len(rec['commissions']), a=len(rec['anomalies'])), rec, src, 0)
    enemies = {e['id']: e for e in rec['enemies']}
    rows = [f"| {lab['code']} | {lab['commission']} | {lab['difficulty']} | {lab['anomaly']} |", '| --- | --- | --- | --- |']
    for c in rec['commissions']:
        # The anomaly: its file's page, else its enemy manual entry, else none in the game data.
        a, e = rec['by_id'].get(c['anomaly']), enemies.get(c['enemy'])
        link = (f"[{md_escape(a[lang]['name'])}](/{p}anomalies/{a['slug']}/)" if a else
                f"[{md_escape(e[lang]['name'])}](/{p}anomalies/enemies/)" if e else NONE)
        rows.append(f"| {md_escape(c[lang]['code'])} | {md_escape(c[lang]['name'])} | {md_escape(c[lang]['difficulty'])} | {link} |")
    return fm + '\n\n' + '\n'.join(rows) + '\n'


def anomaly_page(rec, a, lang, enemy, drop):
    lab, p = AL[lang], PREFIX[lang]
    titles = {k: a[k]['name'] for k in LANGS}
    cs = [c for c in rec['commissions'] if c['anomaly'] == a['id']]
    files = [(a[lang]['name'], a['file'])] + [(c[lang]['name'], c['file']) for c in cs if c['file'] != a['file']]
    fm = frontmatter(lang, titles, lab['page_desc'].format(name=a[lang]['name'], code=a[lang]['code']), rec, sources(lang, files, rec), 2, hide=True)
    rows = [f"| {lab['fact']} | {lab['value']} |", '| --- | --- |',
            f"| {lab['code']} | {md_escape(a[lang]['code'])} |",
            f"| {lab['permission']} | {md_escape(a[lang]['permission'])} |",
            f"| {lab['level']} | {md_escape(a[lang]['level'])} |",
            f"| {lab['commission']} | {md_escape(lab['sep'].join(c[lang]['name'] for c in cs))} |",
            f"| {lab['difficulty']} | {md_escape(lab['sep'].join(dict.fromkeys(c[lang]['difficulty'] for c in cs)))} |"]
    if enemy:
        rows.append(f"| {lab['manual']} | [{md_escape(enemy[lang]['name'])}](/{p}anomalies/enemies/) |")
    if drop:
        rows.append(f"| {lab['material']} | [{drop[lang][1]}](/{p}systems/progression/){L[lang]['sep']}{drop[lang][2]} |")
    body = ['\n'.join(rows), '']
    if a[lang]['quote']:
        body += ['\n'.join('> ' + md_escape(l.strip()) for l in a[lang]['quote'].split('\n') if l.strip()), '']
    for part in a[lang]['parts']:
        # A part whose text is "/" is empty in the game too; text before the first title has no heading.
        if part['text'].strip() in ('/', ''):
            continue
        if part['title']:
            body += ['## ' + md_escape(part['title']), '']
        body += [paragraphs(part['text']), '']
    return fm + '\n\n' + '\n'.join(body)


def manual_page(rec, lang, anomaly_of, drop):
    lab, p = AL[lang], PREFIX[lang]
    titles = {k: AL[k]['manual'] for k in LANGS}
    es = rec['enemies']
    n = {k: sum(1 for e in es if e['type'] == k) for k in KIND_ORDER}
    base = 'https://static.nanoka.cc/nte/' + rec['version']
    ex = es[0]
    src = [(lab['src_list'].format(v=rec['version']), f'{base}/monster.json')]
    src += [(lab['src_ex'].format(v=rec['version'], lang=L[lang]['langs'][k], name=ex[lang]['name']), f"{base}/{SRC[k]}/monster/{ex['id']}.json") for k in ['en', 'zh-cn', 'ja', 'ko']]
    desc = lab['manual_desc'].format(n=len(es), b=n['WeeklyBoss'] + n['Boss'], e=n['Elite'], c=n['Normal'])
    fm = frontmatter(lang, titles, desc, rec, src, 1)
    heads = dict(lab['kinds'])
    for k, name in ACTIVITY.items():
        heads[k] = next(d[lang][0] for d in drop.values() if d['activity'] == name)
    ordered = [e for k in KIND_ORDER for e in es if e['type'] == k]
    rows = [f"| {lab['enemy']} | {lab['place']} | {lab['material']} | {lab['file']} |", '| --- | --- | --- | --- |']
    for e in ordered:
        a = rec['by_id'].get(anomaly_of(e))
        d = drop.get(e['en']['name'])
        mat = f"[{d[lang][1]}](/{p}systems/progression/)" if d else NONE
        link = f"[{md_escape(a[lang]['name'])}](/{p}anomalies/{a['slug']}/)" if a else NONE
        rows.append(f"| {md_escape(e[lang]['name'])} | {md_escape(e[lang]['place'])} | {mat} | {link} |")
    body = ['\n'.join(rows), '']
    for k in KIND_ORDER:
        body += ['## ' + heads[k], '']
        for e in ordered:
            if e['type'] != k:
                continue
            body += ['### ' + md_escape(e[lang]['name']), '']
            if e[lang]['hint']:
                body += ['> ' + md_escape(' '.join(e[lang]['hint'].split())), '']
            body += [paragraphs(e[lang]['text']), '']
    return fm + '\n\n' + '\n'.join(body)


def build_anomalies():
    path = 'records/anomalies.json'
    if not os.path.exists(path):
        return
    rec = json.load(open(path, encoding='utf-8'))
    rec['by_id'] = {a['id']: a for a in rec['anomalies']}
    by_name = {a['en']['name']: a['id'] for a in rec['anomalies']}
    # The anomaly file of an enemy: the one its own file carries, or the one with its English name.
    anomaly_of = lambda e: e['anomaly'] or by_name.get(e['en']['name'])
    unknown = {e['type'] for e in rec['enemies']} - set(KIND_ORDER)
    if unknown:
        sys.exit(f'{path}: enemy manual entries of an unknown kind: {sorted(unknown)}')
    drop = drops()
    kinds = {e['en']['name']: e['type'] for e in rec['enemies']}
    for name, d in drop.items():
        if name in kinds and ACTIVITY.get(kinds[name]) != d['activity']:
            sys.exit(f'{name}: the progression page names it a boss of {d["activity"]}, the enemy manual a {kinds[name]}')
    enemy_of = {anomaly_of(e): e for e in rec['enemies'] if anomaly_of(e)}
    for lang in LANGS:
        d = f'{DOCS}/{PREFIX[lang]}anomalies'
        os.makedirs(d, exist_ok=True)
        want = {'index.md', 'enemies.md'} | {a['slug'] + '.md' for a in rec['anomalies']}
        for f in os.listdir(d):
            if f.endswith('.md') and f not in want:
                os.remove(os.path.join(d, f))
                print('removed', os.path.join(d, f))
        write_archive(f'{d}/index.md', index_page(rec, lang))
        write_archive(f'{d}/enemies.md', manual_page(rec, lang, anomaly_of, drop))
        for a in rec['anomalies']:
            write_archive(f"{d}/{a['slug']}.md", anomaly_page(rec, a, lang, enemy_of.get(a['id']), drop.get(a['en']['name'])))
    print(len(rec['anomalies']), 'anomaly pages and the enemy manual written per language')
