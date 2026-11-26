# Writes the two lists of the characters' game-text pages, one page per language:
#   - characters/archives.md: every character with an archive page, and its number of entries
#   - characters/voices.md: every character with a voice line page, and its numbers of lines
# Each page set has its own list, linked from the home page, so that every archive and voice
# page is linked within the first 5,000 extracted characters of a page the home page links:
# three links on each row of the character list ran past that limit with 25 characters.
# Called from build_pages.py, after the archive and voice pages are written.

import glob
import json
import os
import re

from build_pages import DOCS, LANGS, PREFIX, TODAY, L, characters, write_archive, yaml_str

SRC = {'en': 'en', 'zh-cn': 'zh', 'ja': 'ja', 'ko': 'ko'}

CL = {
    'en': dict(a_title='Archives', v_title='Voice lines', char='Character', entries='Entries',
               a_desc='{n} of the {t} playable characters in NTE have an archive.',
               v_desc_all='All {t} playable characters in NTE have daily and combat voice lines.',
               v_desc='{n} of the {t} playable characters in NTE have voice lines.',
               a_caveat='{names} has no archive in game data {v}.',
               src='nanoka.cc game data {v}, character files in {lang} (example: {name})',
               ev='Everness, character pages in Traditional Chinese (example: {name}, read {read})'),
    'zh-tw': dict(a_title='個人檔案列表', v_title='語音列表', char='角色', entries='條目數',
                  a_desc='《異環》{t} 位可遊玩角色中有 {n} 位有個人檔案。',
                  v_desc_all='《異環》{t} 位可遊玩角色都有日常語音和戰鬥語音。',
                  v_desc='《異環》{t} 位可遊玩角色中有 {n} 位有語音。',
                  a_caveat='遊戲資料 {v} 中{names}沒有個人檔案。',
                  src='nanoka.cc 遊戲資料 {v}，角色檔案（{lang}，例：{name}）',
               ev='Everness，角色頁面（繁體中文，例：{name}，{read} 讀取）'),
    'zh-cn': dict(a_title='个人档案列表', v_title='语音列表', char='角色', entries='条目数',
                  a_desc='《异环》{t} 位可游玩角色中有 {n} 位有个人档案。',
                  v_desc_all='《异环》{t} 位可游玩角色都有日常语音和战斗语音。',
                  v_desc='《异环》{t} 位可游玩角色中有 {n} 位有语音。',
                  a_caveat='游戏数据 {v} 中{names}没有个人档案。',
                  src='nanoka.cc 游戏数据 {v}，角色档案（{lang}，例：{name}）',
               ev='Everness，角色页面（繁体中文，例：{name}，{read} 读取）'),
    'ja': dict(a_title='アーカイブ一覧', v_title='ボイス一覧', char='キャラクター', entries='項目数',
               a_desc='NTE（異環）のプレイアブルキャラ{t}名のうち、{n}名にアーカイブがある。',
               v_desc_all='NTE（異環）のプレイアブルキャラ{t}名全員に日常ボイスと戦闘ボイスがある。',
               v_desc='NTE（異環）のプレイアブルキャラ{t}名のうち、{n}名にボイスがある。',
               a_caveat='ゲームデータ{v}では{names}にアーカイブがない。',
               src='nanoka.cc ゲームデータ{v}、キャラクターファイル（{lang}、例：{name}）',
               ev='Everness、キャラクターのページ（繁体字中国語、例：{name}、{read}取得）'),
    'ko': dict(a_title='아카이브 목록', v_title='보이스 목록', char='캐릭터', entries='항목 수',
               a_desc='이환(NTE)의 플레이 가능 캐릭터 {t}명 중 {n}명에게 아카이브가 있다.',
               v_desc_all='이환(NTE)의 플레이 가능 캐릭터 {t}명 모두에게 일상 보이스와 전투 보이스가 있다.',
               v_desc='이환(NTE)의 플레이 가능 캐릭터 {t}명 중 {n}명에게 보이스가 있다.',
               a_caveat='게임 데이터 {v}에는 {names}의 아카이브가 없다.',
               src='nanoka.cc 게임 데이터 {v}, {lang} 캐릭터 파일 (예: {name})',
               ev='Everness, 캐릭터 페이지(번체 중국어, 예: {name}, {read} 확인)'),
}


def list_order():
    # The character list's order (its first column), which the two lists keep.
    md = open(f'{DOCS}/characters/index.md', encoding='utf-8').read()
    return re.findall(r'^\| \[[^\]]+\]\(/characters/([a-z0-9-]+)/\)', md, re.M)


def page(lang, kind, rows, total, chars, v):
    lab, cl, p = L[lang], CL[lang], PREFIX[lang]
    titles = {k: CL[k][kind + '_title'] for k in LANGS}
    n = len(rows)
    if kind == 'a':
        desc = cl['a_desc'].format(n=n, t=total)
        missing = [s for s in list_order() if s not in dict(rows)]
        caveat = cl['a_caveat'].format(names=lab['sep'].join(chars[s][lang] for s in missing), v=v) if missing else lab['caveat']
        head, cols = [cl['char'], cl['entries']], lambda r: [str(len(r['archive'][lang]))]
        path = 'archive'
    else:
        desc = (cl['v_desc_all'] if n == total else cl['v_desc']).format(n=n, t=total)
        caveat = lab['caveat']
        head, cols = [cl['char'], lab['v_daily'], lab['v_battle']], lambda r: [str(len(r['lines'][lang]['daily'])), str(len(r['lines'][lang]['battle']))]
        path = 'voice'
    # An example row whose text in every language but Traditional Chinese is nanoka.cc's.
    ex, er = next((s, r) for s, r in rows if all('nanoka.cc' in r['sources'][k] for k in SRC))
    cid = re.search(r'/character/(\d+)\.json', er['sources']['zh-cn']).group(1)
    fm = ['---', 'title: ' + yaml_str(titles[lang]),
          'description: ' + yaml_str(desc),
          'aliases:'] + ['  - ' + yaml_str(titles[k]) for k in LANGS if k != lang] + [
          'appliesTo: ' + yaml_str(lab['applies'].format(v=v)),
          'caveat: ' + yaml_str(caveat),
          f'lastVerified: {TODAY}',
          'sidebar:', f"  order: {1 if kind == 'a' else 2}",
          'sources:']
    for k in SRC:
        fm += ['  - title: ' + yaml_str(cl['src'].format(v=v, lang=lab['langs'][k], name=chars[ex][lang])),
               f'    url: https://static.nanoka.cc/nte/{v}/{SRC[k]}/character/{cid}.json']
    if 'everness.info' in er['sources']['zh-tw']:
        fm += ['  - title: ' + yaml_str(cl['ev'].format(name=chars[ex][lang], read=er['reads']['zh-tw'])),
               '    url: ' + er['sources']['zh-tw']]
    fm.append('---')
    body = ['', '| ' + ' | '.join(head) + ' |', '|' + ' --- |' * len(head)]
    for s, r in rows:
        body.append('| ' + ' | '.join([f'[{chars[s][lang]}](/{p}characters/{s}/{path}/)'] + cols(r)) + ' |')
    body.append('')
    return '\n'.join(fm) + '\n' + '\n'.join(body)


def build_character_lists():
    chars = characters()
    order = list_order()
    arch, voice = [], []
    for s in order:
        f = f'records/characters/{s}.json'
        if os.path.exists(f):
            r = json.load(open(f, encoding='utf-8'))
            if r['archive']:
                arch.append((s, r))
        f = f'records/voices/{s}.json'
        if os.path.exists(f):
            voice.append((s, json.load(open(f, encoding='utf-8'))))
    extra = {os.path.basename(f)[:-5] for f in glob.glob('records/voices/*.json')} - set(order)
    if extra:
        raise SystemExit(f'voice records for characters not in the character list: {sorted(extra)}')
    for kind, rows, name in (('a', arch, 'archives'), ('v', voice, 'voices')):
        for lang in LANGS:
            dst = f'{DOCS}/{PREFIX[lang]}characters/{name}.md'
            if not rows:
                if os.path.exists(dst):
                    os.remove(dst)
                continue
            v = rows[0][1]['version']
            write_archive(dst, page(lang, kind, rows, len(order), chars, v))
    print(len(arch), 'archives and', len(voice), 'voice line pages listed per language')
