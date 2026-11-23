# Builds the game-text records from the cached game data, in each page language:
#   records/characters/<slug>.json  archive entries (`profile_detail`) and outfit descriptions
#   records/arcs.json               the description of each Arc in the All Arcs table
#   records/items.json              the description of each item on the progression page
# English, Simplified Chinese, Japanese and Korean come from the nanoka.cc files
# (pipeline/fetch_nanoka.py); Traditional Chinese from everness.info (pipeline/fetch_everness.mjs).
# The text is kept as the game writes it; only line endings are normalised.
#
#   python3 pipeline/build_records.py [slug ...]

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


def save(path, obj):
    json.dump(obj, open(path, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)


if __name__ == '__main__':
    ids = character_ids()
    os.makedirs(OUT, exist_ok=True)
    if not sys.argv[1:]:
        save('records/arcs.json', arcs_record())
        save('records/items.json', items_record())
        print('records/arcs.json, records/items.json written')
    for slug in sys.argv[1:] or list(ids):
        r = record(slug, ids[slug])
        save(os.path.join(OUT, slug + '.json'), r)
        print(slug, len(r['archive'].get('en', [])), 'entries,', len(r['outfits']), 'outfits')
