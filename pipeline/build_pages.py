# Writes the game's own text from the records into the pages:
#   - one archive page per character and language: characters/<slug>/archive.md
#   - one voice line page per character and language: characters/<slug>/voice.md (records/voices/)
#   - a row linking that page in the Profile table of the character page
#   - the lists of archive and voice line pages: characters/archives.md, characters/voices.md
#     (pipeline/character_lists.py)
#   - a description column in the Outfits table of the character page
#   - a description table at the end of the Arcs page (records/arcs.json) and of the
#     progression page (records/items.json)
#   - the anomaly list, one page per anomaly file and the enemy manual (records/anomalies.json,
#     pipeline/anomaly_pages.py)
#   - the item and achievement lists (records/lists.json, pipeline/list_pages.py)
# Each language gets its own game text (Traditional Chinese from the Taiwan localisation,
# Simplified Chinese from the Simplified data, never converted). Run it after
# scripts/to-zh-cn.py, which skips the archive pages and whose Outfits cells this replaces.
#
#   python3 pipeline/build_pages.py [slug ...]   (no slug: every record, Arcs and items too)

import datetime
import glob
import json
import os
import re
import sys

DOCS = 'src/content/docs'
LANGS = ['en', 'zh-tw', 'zh-cn', 'ja', 'ko']
PREFIX = {'en': '', 'zh-tw': 'zh-tw/', 'zh-cn': 'zh-cn/', 'ja': 'ja/', 'ko': 'ko/'}
TODAY = datetime.date.today().isoformat()

L = {
    'en': dict(
        named_text='{name}: {text}',
        arcs_h='Arc descriptions', items_h='Item descriptions', arc='Arc', item='Item', evx='Everness, {kind} pages in Traditional Chinese (example: {name}, read {read})', kinds={'outfit': 'outfit', 'arc': 'Arc', 'item': 'item'},
        evo='Everness, outfit {name} in Traditional Chinese (read {read})', title='{name} archive', archive='Archive', no='No.', entry='Entry', named='Characters named',
        desc='Description', profile='Profile', outfits='Outfits', applies='Game data {v}',
        description='{name} has {n} archive entries in NTE.',
        caveat="The game's language editions can differ in wording and detail.",
        src='nanoka.cc game data {v}, character file in {lang}', ev='Everness, {name} page in {lang} (read {read})',
        langs={'zh-tw': 'Traditional Chinese', 'en': 'English', 'zh-cn': 'Chinese', 'ja': 'Japanese', 'ko': 'Korean'}, sep=', ', none='None'),
    'zh-tw': dict(
        named_text='{name}：{text}',
        arcs_h='弧盤說明', items_h='材料說明', arc='弧盤', item='材料', evx='Everness，{kind}頁面（繁體中文，例：{name}，{read} 讀取）', kinds={'outfit': '時裝', 'arc': '弧盤', 'item': '道具'},
        evo='Everness，時裝「{name}」（繁體中文，{read} 讀取）', title='{name}個人檔案', archive='個人檔案', no='序號', entry='條目', named='提及的角色',
        desc='說明', profile='角色資料', outfits='時裝', applies='遊戲資料 {v}',
        description='《異環》角色{name}的個人檔案共有 {n} 則。',
        caveat='遊戲各語言版本的用字與細節可能不同。',
        src='nanoka.cc 遊戲資料 {v}，角色檔案（{lang}）', ev='Everness，{name}頁面（{lang}，{read} 讀取）',
        langs={'zh-tw': '繁體中文', 'en': '英文', 'zh-cn': '中文', 'ja': '日文', 'ko': '韓文'}, sep='、', none='無'),
    'zh-cn': dict(
        named_text='{name}：{text}',
        arcs_h='弧盘说明', items_h='材料说明', arc='弧盘', item='材料', evx='Everness，{kind}页面（繁体中文，例：{name}，{read} 读取）', kinds={'outfit': '时装', 'arc': '弧盘', 'item': '道具'},
        evo='Everness，时装「{name}」（繁体中文，{read} 读取）', title='{name}个人档案', archive='个人档案', no='序号', entry='条目', named='提及的角色',
        desc='说明', profile='角色资料', outfits='时装', applies='游戏数据 {v}',
        description='《异环》角色{name}的个人档案共有 {n} 则。',
        caveat='游戏各语言版本的用字与细节可能不同。',
        src='nanoka.cc 游戏数据 {v}，角色档案（{lang}）', ev='Everness，{name}页面（{lang}，{read} 读取）',
        langs={'zh-tw': '繁体中文', 'en': '英文', 'zh-cn': '中文', 'ja': '日文', 'ko': '韩文'}, sep='、', none='无'),
    'ja': dict(
        named_text='{name}：{text}',
        arcs_h='弧盤の説明', items_h='素材の説明', arc='弧盤', item='素材', evx='Everness、{kind}のページ（繁体字中国語、例：{name}、{read}取得）', kinds={'outfit': 'コスチューム', 'arc': '弧盤', 'item': 'アイテム'},
        evo='Everness、コスチューム「{name}」（繁体字中国語、{read}取得）', title='{name}のアーカイブ', archive='アーカイブ', no='番号', entry='項目', named='登場するキャラクター',
        desc='説明', profile='プロフィール', outfits='コスチューム', applies='ゲームデータ {v}',
        description='NTE（異環）のキャラクター、{name}のアーカイブは{n}件である。',
        caveat='ゲームの各言語版では、表現や細部が異なることがある。',
        src='nanoka.cc ゲームデータ{v}、キャラクターファイル（{lang}）', ev='Everness、{name}のページ（{lang}、{read}取得）',
        langs={'zh-tw': '繁体字中国語', 'en': '英語', 'zh-cn': '中国語', 'ja': '日本語', 'ko': '韓国語'}, sep='、', none='なし'),
    'ko': dict(
        named_text='{name}: {text}',
        arcs_h='아크 설명', items_h='재료 설명', arc='아크', item='재료', evx='Everness, {kind} 페이지(번체 중국어, 예: {name}, {read} 확인)', kinds={'outfit': '코스튬', 'arc': '아크', 'item': '아이템'},
        evo='Everness, 코스튬 「{name}」(번체 중국어, {read} 확인)', title='{name} 아카이브', archive='아카이브', no='번호', entry='항목', named='언급된 캐릭터',
        desc='설명', profile='프로필', outfits='코스튬', applies='게임 데이터 {v}',
        description='이환(NTE) 캐릭터 {name}의 아카이브는 {n}건이다.',
        caveat='게임의 언어판마다 표현과 세부 내용이 다를 수 있다.',
        src='nanoka.cc 게임 데이터 {v}, {lang} 캐릭터 파일', ev='Everness, 「{name}」 페이지({lang}, {read} 확인)',
        langs={'zh-tw': '번체 중국어', 'en': '영어', 'zh-cn': '중국어', 'ja': '일본어', 'ko': '한국어'}, sep=', ', none='없음'),
}

# Labels of the voice line pages.
VL = {
    'en': dict(v_title='{name} voice lines', v_label='Voice lines', v_desc='{name} has {d} daily and {b} combat voice lines in NTE.', v_daily='Daily', v_battle='Combat', v_char='Character', v_lines='Voice lines', v_head='Title', v_text='Line'),
    'zh-tw': dict(v_title='{name}語音', v_label='語音', v_desc='《異環》角色{name}有日常語音 {d} 句、戰鬥語音 {b} 句。', v_daily='日常', v_battle='戰鬥', v_char='角色', v_lines='語音', v_head='標題', v_text='台詞'),
    'zh-cn': dict(v_title='{name}语音', v_label='语音', v_desc='《异环》角色{name}有日常语音 {d} 句、战斗语音 {b} 句。', v_daily='日常', v_battle='战斗', v_char='角色', v_lines='语音', v_head='标题', v_text='台词'),
    'ja': dict(v_title='{name}のボイス', v_label='ボイス', v_desc='NTE（異環）のキャラクター、{name}のボイスは日常{d}件、戦闘{b}件である。', v_daily='日常', v_battle='戦闘', v_char='キャラクター', v_lines='ボイス', v_head='タイトル', v_text='セリフ'),
    'ko': dict(v_title='{name} 보이스', v_label='보이스', v_desc='이환(NTE) 캐릭터 {name}의 보이스는 일상 {d}개, 전투 {b}개다.', v_daily='일상', v_battle='전투', v_char='캐릭터', v_lines='보이스', v_head='제목', v_text='대사'),
}
for _k, _v in VL.items():
    L[_k].update(_v)


def yaml_str(s):
    if re.search(r': |^[\'"&*!|>%@`#\-?{\[]|#', s) or s != s.strip():
        return "'" + s.replace("'", "''") + "'"
    return s


def page_title(path):
    m = re.search(r'^title: (.*)$', open(path, encoding='utf-8').read(), re.M)
    return m.group(1).strip().strip("'\"")


def md_escape(line):
    # Game text is shown as written: every character Markdown would read as markup is escaped.
    # `~` included: GitHub-flavoured Markdown strikes through text between single tildes ("好啊~…~").
    # `&` before an entity name, and a run of `#` at the end, which would close a heading.
    line = line.replace('\\', '\\\\')
    line = re.sub(r'([*_`~\[\]<>|])', r'\\\1', line)
    line = re.sub(r'&(?=#?\w+;)', r'\\&', line)
    line = re.sub(r'(\s)(#+\s*)$', r'\1\\\2', line)
    line = re.sub(r'^(\s*)([#+\-=]|\d+[.)])', lambda m: m.group(1) + '\\' + m.group(2) if m.group(2)[0] in '#+-=' else m.group(1) + m.group(2)[:-1] + '\\' + m.group(2)[-1], line)
    return line


def paragraphs(text):
    # Each line of the game text becomes a paragraph; empty lines are dropped.
    return '\n\n'.join(md_escape(l.strip()) for l in text.split('\n') if l.strip())


def characters():
    out = {}
    for f in sorted(glob.glob(f'{DOCS}/characters/*.md')):
        slug = os.path.basename(f)[:-3]
        if slug == 'index':
            continue
        out[slug] = {lang: page_title(f'{DOCS}/{PREFIX[lang]}characters/{slug}.md') for lang in LANGS}
    return out


def named(rec, chars, slug):
    # Characters named in an entry, read from the English text (whole words), so that
    # every language lists the same characters.
    res = []
    for e in rec['archive']['en']:
        hit = [s for s, t in chars.items() if s != slug and re.search(r'\b' + re.escape(t['en']) + r'\b', e['title'] + '\n' + e['text'])]
        res.append(hit)
    return res


def write_archive(path, md):
    # lastVerified moves only when the game text in the body changes: an edit to the
    # site's own wording (description, caveat) or to how Markdown escapes the text does not
    # re-read the page against its sources.
    date = re.compile(r'^lastVerified: .*$', re.M)
    body = lambda t: re.sub(r'\\(.)', r'\1', t.split('\n---\n', 1)[-1])
    if os.path.exists(path):
        old = open(path, encoding='utf-8').read()
        if date.sub('', old) == date.sub('', md):
            return
        if body(old) == body(md) and date.search(old):
            md = date.sub(lambda _: date.search(old).group(0), md, count=1)
    open(path, 'w', encoding='utf-8').write(md)


def archive_page(rec, chars, lang):
    lab, slug, v = L[lang], rec['slug'], rec['version']
    name = chars[slug][lang]
    titles = {k: L[k]['title'].format(name=chars[slug][k]) for k in LANGS}
    entries = rec['archive'][lang]
    who = named(rec, chars, slug)
    p = PREFIX[lang]
    src = []
    for k in ['en', 'zh-cn', 'ja', 'ko', 'zh-tw']:
        u = rec['sources'][k]
        if 'everness.info' in u:
            src.append((lab['ev'].format(name=name, lang=lab['langs'][k], read=rec['reads'][k]), u))
        else:
            src.append((lab['src'].format(v=v, lang=lab['langs'][k]), u))
    fm = ['---', 'title: ' + yaml_str(titles[lang]),
          'description: ' + yaml_str(lab['description'].format(name=name, n=len(entries), v=v)),
          'aliases:'] + ['  - ' + yaml_str(titles[k]) for k in LANGS if k != lang] + [
          'appliesTo: ' + yaml_str(lab['applies'].format(v=v)),
          'caveat: ' + yaml_str(lab['caveat']),
          f'lastVerified: {TODAY}',
          'hideAnswer: true',
          'sidebar:', '  hidden: true',
          'sources:']
    for t, u in src:
        fm += ['  - title: ' + yaml_str(t), '    url: ' + u]
    fm.append('---')
    rows = [f"| {lab['no']} | {lab['entry']} | {lab['named']} |", '| --- | --- | --- |']
    for i, (e, w) in enumerate(zip(entries, who), 1):
        links = lab['sep'].join(f'[{chars[s][lang]}](/{p}characters/{s}/)' for s in w) or lab['none']
        rows.append(f"| {i} | {md_escape(e['title'])} | {links} |")
    body = ['', '\n'.join(rows), '']
    for e in entries:
        body += ['## ' + md_escape(e['title']), '', paragraphs(e['text']), '']
    return '\n'.join(fm) + '\n' + '\n'.join(body)


def voice_named(rec, chars, slug):
    # Characters named in the English titles of the voice lines (whole words), with the
    # positions of those lines: [(slug, [(list, index), ...])] in order of first mention.
    out = {}
    names = voice_names(chars)
    for k in ('daily', 'battle'):
        for i, e in enumerate(rec['lines']['en'][k]):
            for s in chars:
                if s != slug and any(re.search(r'\b' + re.escape(n) + r'\b', e['title']) for n in names[s]):
                    out.setdefault(s, []).append((k, i))
    return list(out.items())


def voice_names(chars):
    # {slug: English names a voice line title may call the character by}: the page title, the
    # slug as a name ("Zero"), and the first word of a longer name when no other character
    # shares it ("Akane" for Akane Rin).
    first = [t['en'].split(' ')[0] for t in chars.values()]
    out = {}
    for s, t in chars.items():
        n = {t['en'], s.replace('-', ' ').title()}
        w = t['en'].split(' ')
        if len(w) > 1 and w[0] != 'Esper' and first.count(w[0]) == 1:
            n.add(w[0])
        out[s] = n
    return out


def voice_page(rec, chars, lang):
    lab, slug, v = L[lang], rec['slug'], rec['version']
    name = chars[slug][lang]
    titles = {k: L[k]['v_title'].format(name=chars[slug][k]) for k in LANGS}
    lines = rec['lines'][lang]
    p = PREFIX[lang]
    src = []
    for k in ['en', 'zh-cn', 'ja', 'ko', 'zh-tw']:
        u = rec['sources'][k]
        if 'everness.info' in u:
            src.append((lab['ev'].format(name=name, lang=lab['langs'][k], read=rec['reads'][k]), u))
        else:
            src.append((lab['src'].format(v=v, lang=lab['langs'][k]), u))
    fm = ['---', 'title: ' + yaml_str(titles[lang]),
          'description: ' + yaml_str(lab['v_desc'].format(name=name, d=len(lines['daily']), b=len(lines['battle']))),
          'aliases:'] + ['  - ' + yaml_str(titles[k]) for k in LANGS if k != lang] + [
          'appliesTo: ' + yaml_str(lab['applies'].format(v=v)),
          'caveat: ' + yaml_str(lab['caveat']),
          f'lastVerified: {TODAY}',
          'hideAnswer: true',
          'sidebar:', '  hidden: true',
          'sources:']
    for t, u in src:
        fm += ['  - title: ' + yaml_str(t), '    url: ' + u]
    fm.append('---')
    body = ['']
    who = voice_named(rec, chars, slug)
    if who:
        rows = [f"| {lab['v_char']} | {lab['v_lines']} |", '| --- | --- |']
        for s, at in who:
            rows.append(f"| [{chars[s][lang]}](/{p}characters/{s}/) | {md_escape(lab['sep'].join(lines[k][i]['title'] for k, i in at))} |")
        body += ['\n'.join(rows), '']
    body += ['## ' + lab['v_daily'], '']
    for e in lines['daily']:
        body += ['### ' + md_escape(e['title']), '', paragraphs(e['text']), '']
    body += ['## ' + lab['v_battle'], '', f"| {lab['v_head']} | {lab['v_text']} |", '| --- | --- |']
    for e in lines['battle']:
        body.append(f"| {md_escape(e['title'])} | {md_escape(' '.join(e['text'].split()))} |")
    body.append('')
    return '\n'.join(fm) + '\n' + '\n'.join(body)


def set_voice_row(md, slug, chars, lang):
    # A row after the archive row of the Profile table links the voice line page.
    lab, p = L[lang], PREFIX[lang]
    s = section(md, lab['profile'])
    lines, idx = table_bounds(md, *s)
    row = f"| {lab['v_label']} | [{lab['v_title'].format(name=chars[slug][lang])}](/{p}characters/{slug}/voice/) |"
    at = next((i for i in idx if cells(lines[i])[0] == lab['v_label']), None)
    if at is not None:
        lines[at] = row
    else:
        after = next((i for i in idx if cells(lines[i])[0] == lab['archive']), idx[-1])
        lines.insert(after + 1, row)
    return md[:s[0]] + '\n'.join(lines) + md[s[1]:]


def section(md, heading):
    m = re.search(r'^## ' + re.escape(heading) + r'\n', md, re.M)
    if not m:
        return None
    n = re.search(r'^## ', md[m.end():], re.M)
    return m.end(), m.end() + (n.start() if n else len(md[m.end():]))


def sections(md):
    # [(heading, text)] for each level-2 section of the body.
    parts = re.split(r'^## (.*)\n', md[md.index('\n---\n', 4) + 5:], flags=re.M)
    return list(zip(parts[1::2], parts[2::2]))


def table_rows(text):
    # The data rows of every table in the text (no header or separator rows).
    rows, prev = [], False
    for l in text.split('\n'):
        is_row = l.startswith('|')
        if is_row and prev and not re.match(r'^\|[\s|:-]+\|$', l):
            rows.append(l)
        prev = is_row
    return [r for r in rows]


def table_bounds(md, start, end):
    lines = md[start:end].split('\n')
    idx = [i for i, l in enumerate(lines) if l.startswith('|')]
    return lines, idx


def cells(row):
    return [c.strip() for c in row.strip().strip('|').split(' | ')]


def set_profile_row(md, rec, chars, lang):
    lab, p, slug = L[lang], PREFIX[lang], rec['slug']
    s = section(md, lab['profile'])
    if not s:
        sys.exit(f'{lang}/{slug}: no "{lab["profile"]}" section')
    lines, idx = table_bounds(md, *s)
    row = f"| {lab['archive']} | [{lab['title'].format(name=chars[slug][lang])}](/{p}characters/{slug}/archive/) |"
    for i in idx:
        if cells(lines[i])[0] == lab['archive']:
            lines[i] = row
            break
    else:
        lines.insert(idx[-1] + 1, row)
    return md[:s[0]] + '\n'.join(lines) + md[s[1]:]


def set_outfit_column(md, rec, lang, order):
    lab = L[lang]
    s = section(md, lab['outfits'])
    if not s:
        return md, 0
    lines, idx = table_bounds(md, *s)
    head = cells(lines[idx[0]])
    if head[-1] != lab['desc']:
        lines[idx[0]] = lines[idx[0]] + f" {lab['desc']} |"
        lines[idx[1]] = lines[idx[1]] + ' --- |'
        width = len(head)
    else:
        width = len(head) - 1
    for i, group in zip(idx[2:], order):
        texts = []
        for fid in group:
            o = rec['outfits'][fid].get(lang)
            if not o:
                sys.exit(f"{lang}/{rec['slug']}: no {lang} text for outfit {fid}")
            t = ' '.join(o['text'].split())
            # A row with several outfits names each before its text.
            texts.append(lab['named_text'].format(name=o['name'], text=t) if len(group) > 1 else t)
        c = cells(lines[i])[:width]
        lines[i] = '| ' + ' | '.join(c + [md_escape(' '.join(texts))]) + ' |'
    return md[:s[0]] + '\n'.join(lines) + md[s[1]:], len(order)


def set_source(md, lang, kind, example, drop=None):
    # One source entry for the Traditional Chinese pages of a kind (outfit, Arc, item), naming
    # one page as the example. Entries this script wrote before are replaced.
    lab = L[lang]
    end = md.index('\n---\n', 4)
    front, rest = md[:end], md[end:]
    lines = front.split('\n')
    out, i = [], 0
    while i < len(lines):
        if lines[i].startswith('  - title: ') and i + 1 < len(lines) and re.match(r'    url: https://everness\.info/[^/]+/' + drop, lines[i + 1]):
            i += 2
            continue
        out.append(lines[i])
        i += 1
    front = '\n'.join(out)
    if example:
        title = lab['evx'].format(kind=lab['kinds'][kind], name=example['name'], read=example['read'])
        m = re.search(r'^sources:\n(?:  .*\n?)*', front + '\n', re.M)
        if not m:
            sys.exit(f'{lang}: no sources in the frontmatter')
        cut = min(m.end(), len(front))
        front = front[:cut].rstrip('\n') + f"\n  - title: {yaml_str(title)}\n    url: {example['url']}" + ('\n' + front[cut:].lstrip('\n') if front[cut:].strip() else '')
    return front + rest


def example(o, lang):
    # The Traditional Chinese page named as the example source, named in the page's language
    # by the game's own name for it.
    ex = dict(o['zh-tw'])
    ex['name'] = o[lang]['name']
    return ex


def set_sources(md, rec, chars, lang, order):
    # The character page cites the Traditional Chinese pages its outfit descriptions come from.
    ex = next((example(rec['outfits'][f], lang) for g in order for f in g if rec['outfits'][f].get('zh-tw')), None)
    md = set_source(md, lang, 'outfit', ex, drop='cosmetics/')
    # Outfit text taken from an English or Japanese page of everness.info (untranslated game data).
    lab = L[lang]
    for g in order:
        for f in g:
            for k in ['en', 'ja']:
                o = rec['outfits'][f].get(k, {})
                if 'url' in o:
                    end = md.index('\n---\n', 4)
                    title = lab['ev'].format(name=o['name'], lang=lab['langs'][k], read=o['read'])
                    md = md[:end] + f"\n  - title: {yaml_str(title)}\n    url: {o['url']}" + md[end:]
    return md


def set_desc_section(path, lang, heading, col, names, keys, rec_items, kind, part):
    # A table of the game's description of each Arc or item, after the last section.
    lab = L[lang]
    md = open(path, encoding='utf-8').read()
    s = section(md, heading)
    if s:
        md = md[:s[0] - len(f'## {heading}\n')].rstrip('\n') + '\n' + md[s[1]:]
    if len(names) != len(keys):
        sys.exit(f'{path}: {len(names)} names, {len(keys)} records')
    rows = [f"| {col} | {lab['desc']} |", '| --- | --- |']
    for n, k in zip(names, keys):
        t = rec_items[k][lang]['text']
        rows.append(f"| {n} | {md_escape(' '.join(t.split())) if t else '—'} |")
    md = md.rstrip('\n') + f"\n\n## {heading}\n\n" + '\n'.join(rows) + '\n'
    ex = example(rec_items[keys[0]], lang)
    md = set_source(md, lang, kind, ex, drop=part + '/')
    open(path, 'w', encoding='utf-8').write(md)


def outfit_groups(md, byname, slug):
    # One group of outfit ids per row of the English Outfits table; rows are in the same order
    # in every language. A row can name several outfits, separated by commas.
    s = section(md, L['en']['outfits'])
    if not s:
        return []
    lines, idx = table_bounds(md, *s)
    groups = []
    for i in idx[2:]:
        n = cells(lines[i])[0]
        names = [n] if n in byname else n.split(', ')
        missing = [x for x in names if x not in byname]
        if missing:
            sys.exit(f"{slug}: outfits {missing} are not in the game data")
        groups.append([byname[x] for x in names])
    return groups


def outfit_order(md, rec):
    return outfit_groups(md, {o['en']['name']: fid for fid, o in rec['outfits'].items()}, rec['slug'])


def build_arcs_items():
    from build_records import arc_names, item_names
    arcs = json.load(open('records/arcs.json', encoding='utf-8'))
    items = json.load(open('records/items.json', encoding='utf-8'))
    for lang in LANGS:
        lab = L[lang]
        path = f'{DOCS}/{PREFIX[lang]}systems/arcs.md'
        set_desc_section(path, lang, lab['arcs_h'], lab['arc'], arc_names(open(path, encoding='utf-8').read()),
                         list(arcs['arcs']), arcs['arcs'], 'arc', 'arcs')
        path = f'{DOCS}/{PREFIX[lang]}systems/progression.md'
        set_desc_section(path, lang, lab['items_h'], lab['item'], item_names(open(path, encoding='utf-8').read(), lab['items_h']),
                         list(items['items']), items['items'], 'item', 'items')
    print('Arc and item descriptions written')


if __name__ == '__main__':
    chars = characters()
    if not sys.argv[1:]:
        build_arcs_items()
    slugs = sys.argv[1:] or [os.path.basename(f)[:-5] for f in sorted(glob.glob('records/characters/*.json'))]
    for slug in slugs:
        rec = json.load(open(f'records/characters/{slug}.json', encoding='utf-8'))
        order = outfit_order(open(f'{DOCS}/characters/{slug}.md', encoding='utf-8').read(), rec)
        for lang in LANGS:
            cp = f'{DOCS}/{PREFIX[lang]}characters/{slug}.md'
            md = open(cp, encoding='utf-8').read()
            if rec['archive']:
                dst = f'{DOCS}/{PREFIX[lang]}characters/{slug}/archive.md'
                os.makedirs(os.path.dirname(dst), exist_ok=True)
                write_archive(dst, archive_page(rec, chars, lang))
                md = set_profile_row(md, rec, chars, lang)
            md, n = set_outfit_column(md, rec, lang, order)
            md = set_sources(md, rec, chars, lang, order)
            open(cp, 'w', encoding='utf-8').write(md)
        print(slug, 'archive pages and character pages written,', len(order), 'outfit rows')
    # Voice line pages, from records/voices/ (every record there, whatever slugs were named).
    have = [os.path.basename(f)[:-5] for f in sorted(glob.glob('records/voices/*.json'))]
    for slug in have:
        rec = json.load(open(f'records/voices/{slug}.json', encoding='utf-8'))
        for lang in LANGS:
            dst = f'{DOCS}/{PREFIX[lang]}characters/{slug}/voice.md'
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            write_archive(dst, voice_page(rec, chars, lang))
            cp = f'{DOCS}/{PREFIX[lang]}characters/{slug}.md'
            md = open(cp, encoding='utf-8').read()
            open(cp, 'w', encoding='utf-8').write(set_voice_row(md, slug, chars, lang))
    # A character whose voice record is gone loses its page and its Profile row.
    for slug in sorted(set(chars) - set(have)):
        for lang in LANGS:
            dst = f'{DOCS}/{PREFIX[lang]}characters/{slug}/voice.md'
            if os.path.exists(dst):
                os.remove(dst)
                print('removed', dst)
            cp = f'{DOCS}/{PREFIX[lang]}characters/{slug}.md'
            md = open(cp, encoding='utf-8').read()
            out = re.sub(r'^\| ' + re.escape(L[lang]['v_label']) + r' \| \[[^\n]*/characters/' + re.escape(slug) + r'/voice/\) \|\n', '', md, flags=re.M)
            if out != md:
                open(cp, 'w', encoding='utf-8').write(out)
    print(len(have), 'voice line pages per language written')
    from character_lists import build_character_lists
    build_character_lists()
    from anomaly_pages import build_anomalies
    build_anomalies()
    from list_pages import build_lists
    build_lists()
