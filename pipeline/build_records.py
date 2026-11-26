# Builds the game-text records from the cached game data, in each page language:
#   records/characters/<slug>.json  archive entries (`profile_detail`) and outfit descriptions
#   records/voices/<slug>.json      voice lines (`voices`: daily and combat), when they were read
#   records/arcs.json               the description of each Arc in the All Arcs table
#   records/items.json              the description of each item on the progression page
#   records/anomalies.json          anomaly commissions, archive files and enemy manual entries (--monsters)
#   records/lists.json              glider skins, mod parts, figurines, gifts and achievements (--lists)
# English, Simplified Chinese, Japanese and Korean come from the nanoka.cc files
# (pipeline/fetch_nanoka.py); Traditional Chinese from everness.info (pipeline/fetch_everness.mjs).
# The text is kept as the game writes it; only line endings are normalised. The exceptions:
# no Traditional Chinese source has the anomaly files and enemy manual, nor most achievements,
# so their Traditional Chinese is converted from the Simplified text (OpenCC s2twp, names from
# the Taiwan pages); so is the text of a listed item that everness.info lacks.
#
#   python3 pipeline/build_records.py [slug ...]
#   python3 pipeline/build_records.py --voices [slug ...]   (voice lines only)
#   uv run --with opencc-python-reimplemented pipeline/build_records.py --monsters
#   uv run --with opencc-python-reimplemented pipeline/build_records.py --lists

import glob
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(__file__))
from build_pages import DOCS, cells, sections, table_rows  # noqa: E402
from fetch_nanoka import BASE, CACHE, VERSION, character_ids  # noqa: E402

NANOKA = {'en': 'en', 'zh-cn': 'zh', 'ja': 'ja', 'ko': 'ko'}
EVERNESS = os.path.join(os.path.dirname(__file__), 'cache', 'everness')
OUT = 'records/characters'


def first_cells(md, which):
    # First cells of the table rows in the given sections, with lines such as A → B → C split.
    names = []
    for title, text in sections(md):
        if which(title):
            for row in table_rows(text):
                names += cells(row)[0].split(' → ')
    return names


def arc_names(md):
    # The All Arcs table: the second section of the Arcs page in every language.
    secs = [t for t, _ in sections(md)]
    return first_cells(md, lambda t: t == secs[1])


def item_names(md, skip):
    # Every table after the first section (levels) of the progression page.
    secs = [t for t, _ in sections(md)]
    return first_cells(md, lambda t: t != secs[0] and t != skip)


def arc_keys():
    arcs = load(os.path.join(CACHE, 'weapon.json'))
    by = {a['en']: k for k, a in arcs.items()}
    names = arc_names(open(f'{DOCS}/systems/arcs.md', encoding='utf-8').read())
    missing = [n for n in names if n not in by]
    if missing:
        sys.exit(f'Arcs not in weapon.json: {missing}')
    return {n: by[n] for n in names}


def item_keys():
    from build_pages import L
    items = load(os.path.join(CACHE, 'en', 'item.json'))
    by = {}
    for i in items.values():
        by.setdefault(i['name'], []).append(i['id'])
    names = item_names(open(f'{DOCS}/systems/progression.md', encoding='utf-8').read(), L['en']['items_h'])
    bad = {n: by.get(n) for n in names if len(by.get(n, [])) != 1}
    if bad:
        sys.exit(f'items without exactly one match in item.json: {bad}')
    return {n: by[n][0] for n in names}


# The item lists (pipeline/list_pages.py): {list: [item id]} in item.json order. Mod parts whose
# English, Japanese or Korean text is still the Simplified original (or an English name with Han
# characters in it) are left out; so are items
# without a name, and figurine-cabinet entries with no text (the "Remove" button).
LISTS = ('gliders', 'mod-parts', 'figurines', 'gifts')


def list_keys():
    data = {lang: {i['id']: i for i in load(os.path.join(CACHE, src, 'item.json')).values()} for lang, src in NANOKA.items()}
    out = {k: [] for k in LISTS}
    for key, i in data['en'].items():
        if not i['name']:
            continue
        tags = i.get('tag_ids') or []
        if i['type_id'] == 'ITEM_TYPE_GLIDE':
            out['gliders'].append(key)
        if i['type_id'] == 'ITEM_TYPE_VEHICLE_SKIN' and not re.search(r'[\u4e00-\u9fff]', i['name']) and not any(
                chinese(data[lang][key][f] or '', lang) for lang in ('en', 'ja', 'ko') for f in ('name', 'context', 'description')):
            out['mod-parts'].append(key)
        if 'FIGURES' in tags and (i['description'] or i['context']):
            out['figurines'].append(key)
        if 'Gift' in tags:
            out['gifts'].append(key)
    return out


def chinese(text, lang):
    # True when English, Japanese or Korean text is the Simplified Chinese original: mostly Han
    # characters, with no kana or hangul to speak of.
    if not text:
        return False
    han = len(re.findall(r'[\u4e00-\u9fff]', text)) / len(text)
    own = len(re.findall(r'[\u3040-\u30ff]' if lang == 'ja' else r'[\uac00-\ud7a3]', text)) / len(text)
    return han > 0.3 and (lang == 'en' or own < 0.02)


def outfit_keys(slug, cid):
    from build_pages import outfit_groups
    md = open(f'{DOCS}/characters/{slug}.md', encoding='utf-8').read()
    data = load(os.path.join(CACHE, 'en', 'character', cid + '.json'))
    groups = outfit_groups(md, {f['name']: f['fashion_id'] for f in data['fashion']}, slug)
    return [k for g in groups for k in g]


def clean(s):
    return s.replace('\r\n', '\n').replace('\r', '\n').strip()


def load(path):
    return json.load(open(path, encoding='utf-8'))


# everness.info edition for a page language whose nanoka.cc text is untranslated.
EDITION = {'en': 'en', 'ja': 'ja'}


def untranslated(text, lang):
    # True when English or Japanese game text is still the Simplified Chinese original
    # (Elyms's archive in 1.5.4): mostly Han characters, and no kana for Japanese.
    if lang not in EDITION or not text:
        return False
    han = len(re.findall(r'[\u4e00-\u9fff]', text)) / len(text)
    kana = len(re.findall(r'[\u3040-\u30ff]', text)) / len(text)
    return han > 0.3 and (lang == 'en' or kana < 0.02)


def character_data(cid):
    return {lang: load(os.path.join(CACHE, src, 'character', cid + '.json')) for lang, src in NANOKA.items()}


def untranslated_parts(cid):
    # [(lang, 'espers', cid) or (lang, 'cosmetics', fashion_id)] whose text comes from everness.info.
    data, out = character_data(cid), []
    for lang, d in data.items():
        if any(untranslated(e['name'] + e['desc'], lang) for e in d['profile_detail']):
            out.append((lang, 'espers', cid))
        out += [(lang, 'cosmetics', f['fashion_id']) for f in d['fashion'] if untranslated(f['desc'] or '', lang)]
    return out


def record(slug, cid):
    data = character_data(cid)
    ev = load(os.path.join(EVERNESS, cid + '.json'))
    archive = {lang: [{'title': clean(e['name']), 'text': clean(e['desc'])} for e in d['profile_detail']] for lang, d in data.items()}
    archive['zh-tw'] = [{'title': clean(e['title']), 'text': clean(e['text'])} for e in ev['entries']]
    sources = {lang: f'{BASE}/{src}/character/{cid}.json' for lang, src in NANOKA.items()} | {'zh-tw': ev['url']}
    reads = {'zh-tw': ev['read']}
    fixes = untranslated_parts(cid)
    for lang, part, key in fixes:
        if part == 'espers':
            e = zh_tw(f'{key}.{EDITION[lang]}')
            archive[lang] = [{'title': clean(x['title']), 'text': clean(x['text'])} for x in e['entries']]
            sources[lang], reads[lang] = e['url'], e['read']
    # A character whose archive the game has not opened yet has one placeholder entry.
    if [e['title'] for e in archive['en']] == ['Profile locked']:
        archive = {}
    counts = {lang: len(v) for lang, v in archive.items()}
    if archive and len(set(counts.values())) != 1:
        sys.exit(f'{slug}: archive entry counts differ: {counts}')

    outfits = {}
    for lang, d in data.items():
        for f in d['fashion']:
            outfits.setdefault(f['fashion_id'], {})[lang] = {'name': clean(f['name']), 'text': clean(f['desc'] or '')}
    for fid, o in outfits.items():
        p = os.path.join(EVERNESS, fid + '.json')
        if os.path.exists(p):
            e = load(p)
            o['zh-tw'] = {'name': e['name'], 'text': e['description'], 'url': e['url'], 'read': e['read']}
    for lang, part, key in fixes:
        if part == 'cosmetics':
            e = zh_tw(f'{key}.{EDITION[lang]}')
            outfits[key][lang] = {'name': e['name'], 'text': e['description'], 'url': e['url'], 'read': e['read']}

    return {
        'slug': slug,
        'id': cid,
        'version': VERSION,
        'sources': sources,
        'reads': reads,
        'archive': archive,
        'outfits': outfits,
    }


def tw_names():
    # {slug: (English names, Traditional Chinese short name)}: the names build_pages links a voice
    # line by, and the page title's last part (異能者·零 gives 零).
    from build_pages import characters, voice_names
    chars = characters()
    names = voice_names(chars)
    return {s: (names[s], t['zh-tw'].split('·')[-1]) for s, t in chars.items()}


TW_NAMES = {}


def voices_record(slug, cid):
    # The voice lines in two lists, daily and combat (`battle`), in the game's order. Traditional
    # Chinese from the voice tab of everness.info, matched by position: each list must have the
    # same length in every language, and a title's parts (split at ·) must match in number.
    data = character_data(cid)
    if not data['en']['voices']['daily']:
        return None
    p = os.path.join(EVERNESS, cid + '.voices.json')
    if not os.path.exists(p):
        return None
    ev = load(p)
    lines = {lang: {k: [{'title': clean(e['name']), 'text': clean(e['desc'])} for e in d['voices'][k]] for k in ('daily', 'battle')}
             for lang, d in data.items()}
    lines['zh-tw'] = {k: [{'title': clean(e['title']), 'text': clean(e['text'])} for e in ev[k]] for k in ('daily', 'battle')}
    for k in ('daily', 'battle'):
        counts = {lang: len(v[k]) for lang, v in lines.items()}
        if len(set(counts.values())) != 1:
            sys.exit(f'{slug}: {k} voice line counts differ: {counts}')
        for a, b in zip(lines['zh-cn'][k], lines['zh-tw'][k]):
            if a['title'].count('·') != b['title'].count('·'):
                sys.exit(f"{slug}: {k} voice lines out of step: {a['title']} / {b['title']}")
        # A line about another character must name that character in its Traditional Chinese
        # title too, so that a reordered list cannot link a line to the wrong character.
        for e, t in zip(lines['en'][k], lines['zh-tw'][k]):
            # A Taiwan title may shorten a three-character name to its first two (明音凜, 明音).
            for other, (en, tw) in TW_NAMES.items():
                if other != slug and any(re.search(r'\b' + re.escape(n) + r'\b', e['title']) for n in en) and tw[:2] not in t['title']:
                    sys.exit(f"{slug}: {k} voice line {e['title']!r} has the Traditional Chinese title {t['title']!r}, without {tw}")
        empty = [(lang, e['title']) for lang, v in lines.items() for e in v[k] if not e['text']]
        if empty:
            sys.exit(f'{slug}: voice lines without text: {empty}')
    return {
        'slug': slug,
        'id': cid,
        'version': VERSION,
        'sources': {lang: f'{BASE}/{src}/character/{cid}.json' for lang, src in NANOKA.items()} | {'zh-tw': ev['url']},
        'reads': {'zh-tw': ev['read']},
        'lines': lines,
    }


def zh_tw(key):
    p = os.path.join(EVERNESS, key + '.json')
    if not os.path.exists(p):
        sys.exit(f'{key}: no Traditional Chinese text in {EVERNESS}; run pipeline/fetch_everness.mjs')
    return load(p)


def arcs_record():
    out = {}
    for name, key in arc_keys().items():
        o = {}
        for lang, src in NANOKA.items():
            d = load(os.path.join(CACHE, src, 'weapon', key + '.json'))
            o[lang] = {'name': clean(d['name']), 'text': clean(d['description'] or '')}
        e = zh_tw(key)
        o['zh-tw'] = {'name': e['name'], 'text': e['description'], 'url': e['url'], 'read': e['read']}
        out[key] = o
    return {'version': VERSION, 'sources': {lang: f'{BASE}/{src}/weapon/' for lang, src in NANOKA.items()}, 'arcs': out}


def items_record():
    data = {lang: {i['id']: i for i in load(os.path.join(CACHE, src, 'item.json')).values()} for lang, src in NANOKA.items()}
    out = {}
    for name, key in item_keys().items():
        o = {lang: {'name': clean(d[key]['name']), 'text': clean(d[key]['description'] or '')} for lang, d in data.items()}
        e = zh_tw(key)
        if '\n' in clean(data['zh-cn'][key]['context'] or ''):
            sys.exit(f'{key}: the use text has several lines; the Traditional Chinese page cannot be split')
        o['zh-tw'] = {'name': e['name'], 'text': e['description'], 'url': e['url'], 'read': e['read']}
        out[key] = o
    return {'version': VERSION, 'sources': {lang: f'{BASE}/{src}/item.json' for lang, src in NANOKA.items()}, 'items': out}


def tw_glossary():
    # {Simplified name: Taiwan name} for the conversion of the anomaly and enemy text, longest
    # first: character names (page titles), the Anomaly Hunt bosses of the progression page
    # (its Taiwan names, matched to the game's Simplified names through the English rows),
    # the Han names of the names page, the names quoted on the version pages and in the
    # achievements that everness.info shows.
    from build_pages import characters
    out = {}
    for t in characters().values():
        for cn, tw in zip([t['zh-cn']] + t['zh-cn'].split('·'), [t['zh-tw']] + t['zh-tw'].split('·')):
            out[cn] = tw
    zh = {clean(v['en']): clean(v['zh']) for v in load(os.path.join(CACHE, 'monster.json')).values()}
    rows = lambda md: [cells(r) for r in table_rows(md) if len(cells(r)) == 3]
    for en, tw in zip(rows(open(f'{DOCS}/systems/progression.md', encoding='utf-8').read()), rows(open(f'{DOCS}/zh-tw/systems/progression.md', encoding='utf-8').read())):
        m, n = re.search(r'Anomaly Hunt:? "?([^"]+)"?$', en[1]), re.search(r'異象追獵「(.+)」$', tw[1])
        if m and n and m.group(1) in zh:
            out[zh[m.group(1)]] = n.group(1)
    for r in table_rows(open(f'{DOCS}/zh-tw/names.md', encoding='utf-8').read()):
        c = cells(r)
        if len(c) == 5 and re.fullmatch(r'[一-鿿·]{2,}', c[1]) and re.fullmatch(r'[一-鿿·]{2,}', c[2]):
            out[c[2]] = c[1]
    # Names quoted on the version pages (Taiwan notices), paired in order with the same names on
    # the Simplified pages that scripts/to-zh-cn.py writes from them: anomaly commissions and events.
    for f in sorted(glob.glob(f'{DOCS}/zh-tw/versions/*.md')):
        q = lambda path: re.findall(r'「([^」\n]+)」', open(path, encoding='utf-8').read())
        tw, cn = q(f), q(f.replace('/zh-tw/', '/zh-cn/'))
        if len(tw) == len(cn):
            for a, b in zip(cn, tw):
                out.setdefault(a, b)
    # Names quoted in the conditions of the achievements that everness.info shows in Traditional
    # Chinese (anomaly commissions, items), paired in order with the Simplified condition's names.
    if os.path.exists(os.path.join(EVERNESS, 'achievements.json')):
        from opencc import OpenCC
        match, _ = achievement_match(OpenCC('s2twp'))
        zh = {a['id']: a for c in load(os.path.join(CACHE, 'zh', 'achievement.json'))['categories'] for a in c['achievements']}
        q = lambda t: re.findall(r'「([^」\n]+)」', t)
        for aid, e in match.items():
            cn, tw = q(clean(zh[aid]['desc'])), q(e['desc'])
            if len(cn) == len(tw):
                for a, b in zip(cn, tw):
                    out.setdefault(a, b)
    return dict(sorted(out.items(), key=lambda kv: -len(kv[0])))


# Forms s2twp leaves that the Taiwan pages write otherwise (AGENTS.md: 計畫, as the site writes it).
TW_FORMS = [('計劃', '計畫'), ('想象', '想像'), ('后街', '後街')]


def to_tw(text, cc, gloss):
    # OpenCC s2twp with the glossary's names kept as the Taiwan pages write them.
    keep = []
    for cn, tw in gloss.items():
        if cn in text:
            text = text.replace(cn, f'{len(keep)}')
            keep.append(tw)
    text = cc.convert(text)
    for a, b in TW_FORMS:
        text = text.replace(a, b)
    return re.sub('(\\d+)', lambda m: keep[int(m.group(1))], text)


def blocks(desc):
    return [b.strip() for b in clean(desc).split('\n\n') if b.strip()]


def archive_parts(desc, titled):
    # An anomaly file is blocks of text separated by empty lines: a quotation (and, in some
    # files, text before the first title), then parts that each start with a title line
    # ("【异象故事】" in Simplified Chinese and Japanese, "[이상 스토리]" in Korean, a bare line in
    # English; the brackets are dropped) and run on over the untitled
    # blocks after it. `titled` holds the indexes of the blocks that start a part, read from the
    # Simplified file, whose titles are marked; every edition has the same blocks.
    bl = blocks(desc)
    first = min(titled) if titled else len(bl)
    quote, parts = bl[0] if first else '', []
    if first > 1:
        parts.append({'title': '', 'text': '\n'.join(bl[1:first])})
    for i in range(first, len(bl)):
        if i in titled:
            title, _, text = bl[i].partition('\n')
            parts.append({'title': re.sub(r'^(?:【(.*)】|\[(.*)\])$', lambda m: m.group(1) or m.group(2), title.strip()), 'text': text.strip()})
        else:
            parts[-1]['text'] = (parts[-1]['text'] + '\n' + bl[i]).strip()
    return quote, parts


def slugify(name):
    return re.sub(r'[^a-z0-9]+', '-', name.lower()).strip('-')


def bare(name):
    return re.sub(r'^[「"“](.*)[」"”]$', r'\1', clean(name))


def monsters_record():
    from opencc import OpenCC
    cc, gloss = OpenCC('s2twp'), tw_glossary()
    index = load(os.path.join(CACHE, 'monster.json'))
    files = {lang: {k: load(os.path.join(CACHE, src, 'monster', k + '.json')) for k, v in index.items() if v['source_type'] in ('DT_Vision', 'DT_MonsterManualConfig')} for lang, src in NANOKA.items()}
    anomalies, enemies, commissions = {}, [], []
    for k in sorted(files['en']):
        en = files['en'][k]
        v = en.get('Vision') or {}
        if v.get('VisionManualId') and v.get('VisionDesc') and v['VisionManualId'] not in anomalies:
            a = {'id': v['VisionManualId'], 'file': k, 'slug': slugify(bare(v['VisionManualName'])), 'code': v['VisionCode']}
            zb = blocks(files['zh-cn'][k]['Vision']['VisionDesc'])
            titled = {i for i, b in enumerate(zb) if re.match(r'【[^】\n]+】(\n|$)', b)}
            for lang in NANOKA:
                d = files[lang][k]['Vision']
                if untranslated(d['VisionDesc'], lang):
                    sys.exit(f'{k}: the {lang} anomaly file is the Simplified Chinese original')
                if len(blocks(d['VisionDesc'])) != len(zb):
                    sys.exit(f'{k}: the {lang} anomaly file has {len(blocks(d["VisionDesc"]))} blocks, the Simplified file {len(zb)}')
                quote, parts = archive_parts(d['VisionDesc'], titled)
                a[lang] = {'name': bare(d['VisionManualName']), 'code': clean(d['VisionCode']), 'permission': clean(d['VisionPermission']), 'level': clean(d['VisionLevel']), 'quote': quote, 'parts': parts}
            z = a['zh-cn']
            a['zh-tw'] = {'name': to_tw(z['name'], cc, gloss), 'code': z['code'], 'permission': to_tw(z['permission'], cc, gloss), 'level': z['level'],
                          'quote': to_tw(z['quote'], cc, gloss), 'parts': [{'title': to_tw(p['title'], cc, gloss), 'text': to_tw(p['text'], cc, gloss)} for p in z['parts']]}
            anomalies[a['id']] = a
        if v.get('VisionName'):
            # An anomaly commission: its name, code and difficulty, the anomaly file it leads to
            # and the enemy manual entry it belongs to.
            c = {'id': v['VisionId'], 'file': k, 'anomaly': v.get('VisionManualId') if v.get('VisionDesc') else None,
                 'enemy': k if index[k]['source_type'] == 'DT_MonsterManualConfig' else None}
            for lang in NANOKA:
                d = files[lang][k]['Vision']
                if untranslated(d['VisionName'], lang):
                    sys.exit(f'{k}: the {lang} anomaly commission name is the Simplified Chinese original')
                c[lang] = {'name': bare(d['VisionName']), 'code': clean(d['VisionCode']), 'difficulty': clean(d['DifficultyDisplayText'])}
            z = c['zh-cn']
            c['zh-tw'] = {'name': to_tw(z['name'], cc, gloss), 'code': z['code'], 'difficulty': z['difficulty']}
            commissions.append(c)
        if index[k]['source_type'] == 'DT_MonsterManualConfig':
            e = {'id': k, 'sort': en['Sort'], 'type': en['EnemyType'], 'anomaly': v.get('VisionManualId') if v.get('VisionDesc') else None}
            for lang in NANOKA:
                d = files[lang][k]
                if untranslated(d['DiscoveredDesc'], lang):
                    sys.exit(f'{k}: the {lang} enemy manual entry is the Simplified Chinese original')
                e[lang] = {'name': clean(d['MonsterName']), 'place': clean(d['EnemyPlace']), 'text': clean(d['DiscoveredDesc']), 'hint': clean(d['UndiscoveredDesc'] or '')}
            e['zh-tw'] = {f: to_tw(e['zh-cn'][f], cc, gloss) for f in ('name', 'place', 'text', 'hint')}
            enemies.append(e)
    enemies.sort(key=lambda e: e['sort'])
    return {'version': VERSION, 'sources': {lang: f'{BASE}/{src}/monster/' for lang, src in NANOKA.items()}, 'glossary': gloss,
            'anomalies': sorted(anomalies.values(), key=lambda a: a['id']), 'enemies': enemies,
            'commissions': sorted(commissions, key=lambda c: c['en']['code'])}


def achievement_match(cc):
    # {achievement id: everness entry} for the achievements that everness.info's achievements page
    # shows in Traditional Chinese: among the achievements with the same reward, the one whose
    # converted title and condition are closest to the Taiwan text, if clearly closer than the next.
    from difflib import SequenceMatcher
    p = os.path.join(EVERNESS, 'achievements.json')
    if not os.path.exists(p):
        return {}, None
    ev = load(p)
    zh = [a for c in load(os.path.join(CACHE, 'zh', 'achievement.json'))['categories'] for a in c['achievements']]
    out = {}
    for e in ev['entries']:
        score = sorted(((SequenceMatcher(None, cc.convert(clean(a['title'])) + '\n' + cc.convert(clean(a['desc'])), e['title'] + '\n' + e['desc']).ratio(), a['id'])
                        for a in zh if f"x{a['reward']}" == e['reward'][0]), reverse=True)
        if score and score[0][0] >= 0.75 and (len(score) == 1 or score[1][0] < score[0][0] - 0.05):
            if score[0][1] in out:
                sys.exit(f"everness.info achievements page: two entries match {score[0][1]}")
            out[score[0][1]] = e
    return out, ev


def lists_record():
    from opencc import OpenCC
    cc, gloss = OpenCC('s2twp'), tw_glossary()
    data = {lang: {i['id']: i for i in load(os.path.join(CACHE, src, 'item.json')).values()} for lang, src in NANOKA.items()}
    ids = character_ids()
    fans = {}
    for slug, cid in ids.items():
        for g in load(os.path.join(CACHE, 'en', 'character', cid + '.json')).get('preferrable_gifts') or []:
            fans.setdefault(g['item_id'].lower(), []).append(slug)
    lists, read = {}, {}
    for name, keys in list_keys().items():
        rows = []
        for key in keys:
            o = {'id': key, 'rarity': data['en'][key]['rarity'], 'type': data['en'][key]['type_id']}
            for lang in NANOKA:
                d = data[lang][key]
                o[lang] = {'name': clean(d['name']), 'use': clean(d['context'] or ''), 'text': clean(d['description'] or ''), 'sources': [clean(x) for x in d['sources']]}
            z = o['zh-cn']
            tw = {f: to_tw(z[f], cc, gloss) for f in ('name', 'use', 'text')}
            tw['sources'] = [to_tw(x, cc, gloss) for x in z['sources']]
            ep = os.path.join(EVERNESS, key + '.json')
            if os.path.exists(ep):
                # The page's first text line is the use only when the item has one; a page without
                # the use line (noUse) has only the name and description, and the use stays converted.
                e = load(ep)
                if e.get('noUse'):
                    # An empty description there, for an item the Simplified data describes, is
                    # text everness.info lacks: the converted text stays.
                    tw.update(name=e['name'], text=e['description'] or tw['text'])
                else:
                    body = [x for x in [e['use'], *e['description'].split('\n')] if x]
                    use, text = (body[0], body[1:]) if z['use'] else ('', body)
                    tw.update(name=e['name'], use=use, text='\n'.join(text))
                read[key] = {'url': e['url'], 'read': e['read']}
            o['zh-tw'] = tw
            if name == 'gifts':
                o['fans'] = fans.get(key.lower(), [])
            rows.append(o)
        lists[name] = rows
    match, ev = achievement_match(cc)
    ach = {lang: load(os.path.join(CACHE, src, 'achievement.json'))['categories'] for lang, src in NANOKA.items()}
    cats = []
    for i, c in enumerate(ach['en']):
        cat = {'id': c['id'], 'achievements': []}
        for lang in NANOKA:
            if ach[lang][i]['id'] != c['id']:
                sys.exit(f"achievement.json: category {i} is {ach[lang][i]['id']} in {lang}, {c['id']} in English")
            cat[lang] = {'label': clean(ach[lang][i]['type_label']), 'name': clean(ach[lang][i]['name'])}
        cat['zh-tw'] = {f: to_tw(cat['zh-cn'][f], cc, gloss) for f in ('label', 'name')}
        for j, a in enumerate(c['achievements']):
            r = {'id': a['id'], 'hidden': a['is_hidden']}
            for lang in NANOKA:
                b = ach[lang][i]['achievements'][j]
                if b['id'] != a['id']:
                    sys.exit(f"achievement.json: achievement {j} of {c['id']} is {b['id']} in {lang}, {a['id']} in English")
                r[lang] = {'title': clean(b['title']), 'desc': clean(b['desc'])}
            e = match.get(a['id'])
            r['zh-tw'] = {'title': e['title'], 'desc': e['desc']} if e else {f: to_tw(r['zh-cn'][f], cc, gloss) for f in ('title', 'desc')}
            cat['achievements'].append(r)
        cats.append(cat)
    return {'version': VERSION, 'sources': {lang: f'{BASE}/{src}/' for lang, src in NANOKA.items()}, 'glossary': gloss,
            'everness': read, 'achievements_page': {'url': ev['url'], 'read': ev['read'], 'matched': sorted(match)} if ev else None,
            **lists, 'achievements': cats}


def save(path, obj):
    json.dump(obj, open(path, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)


if __name__ == '__main__':
    ids = character_ids()
    os.makedirs(OUT, exist_ok=True)
    if sys.argv[1:] == ['--lists']:
        r = lists_record()
        save('records/lists.json', r)
        print('records/lists.json:', ', '.join(f'{len(r[k])} {k}' for k in LISTS), '|', sum(len(c['achievements']) for c in r['achievements']), 'achievements,',
              len(r['everness']), 'items and', len((r['achievements_page'] or {}).get('matched', [])), 'achievements with Traditional Chinese text from everness.info')
        sys.exit()
    if sys.argv[1:] == ['--monsters']:
        r = monsters_record()
        save('records/anomalies.json', r)
        print('records/anomalies.json:', len(r['commissions']), 'anomaly commissions,', len(r['anomalies']), 'anomaly files,', len(r['enemies']), 'enemy manual entries')
        sys.exit()
    if not sys.argv[1:]:
        save('records/arcs.json', arcs_record())
        save('records/items.json', items_record())
        print('records/arcs.json, records/items.json written')
    os.makedirs('records/voices', exist_ok=True)
    voices = '--voices' in sys.argv
    TW_NAMES.update(tw_names())
    for slug in [a for a in sys.argv[1:] if a != '--voices'] or list(ids):
        if voices:
            # Voice lines only: the archive and outfit records stay as they were read.
            v = voices_record(slug, ids[slug])
            if v:
                save(os.path.join('records/voices', slug + '.json'), v)
            print(slug, f"{len(v['lines']['en']['daily'])} daily, {len(v['lines']['en']['battle'])} combat voice lines" if v else 'no voice lines read')
            continue
        r = record(slug, ids[slug])
        save(os.path.join(OUT, slug + '.json'), r)
        print(slug, len(r['archive'].get('en', [])), 'entries,', len(r['outfits']), 'outfits')
