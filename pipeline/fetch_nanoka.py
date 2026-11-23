# Downloads the nanoka.cc game data files that the game-text records are built from:
# one character file per character page and language, item.json per language, and the
# Arc list (weapon.json) with one Arc file per Arc and language.
# A bounded list of named files, one request a second (nanoka.cc sets ai-train=no
# and blocks crawlers; see AGENTS.md). Files go to pipeline/cache/, which is not committed.
#
#   python3 pipeline/fetch_nanoka.py [slug ...]

import glob
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request

VERSION = '1.5.4'
LANGS = ['en', 'zh', 'ja', 'ko']
BASE = f'https://static.nanoka.cc/nte/{VERSION}'
CACHE = os.path.join(os.path.dirname(__file__), 'cache', VERSION)


def character_ids():
    ids = {}
    for f in sorted(glob.glob('src/content/docs/characters/*.md')):
        m = re.search(r'nanoka\.cc/nte/' + re.escape(VERSION) + r'/en/character/(\d+)\.json', open(f, encoding='utf-8').read())
        if m:
            ids[os.path.basename(f)[:-3]] = m.group(1)
    return ids


def get(url, dst):
    if os.path.exists(dst):
        return
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                data = r.read()
            break
        except (TimeoutError, urllib.error.URLError):
            if attempt == 2:
                raise
            time.sleep(30)
    open(dst, 'wb').write(data)
    time.sleep(2)


if __name__ == '__main__':
    ids = character_ids()
    want = sys.argv[1:] or list(ids)
    for lang in LANGS:
        get(f'{BASE}/{lang}/item.json', os.path.join(CACHE, lang, 'item.json'))
        for slug in want:
            get(f'{BASE}/{lang}/character/{ids[slug]}.json', os.path.join(CACHE, lang, 'character', ids[slug] + '.json'))
    if sys.argv[1:]:
        print(len(want), 'characters,', len(LANGS), 'languages in', CACHE)
        sys.exit()
    get(f'{BASE}/weapon.json', os.path.join(CACHE, 'weapon.json'))
    arcs = list(json.load(open(os.path.join(CACHE, 'weapon.json'), encoding='utf-8')))
    for lang in LANGS:
        for a in arcs:
            get(f'{BASE}/{lang}/weapon/{a}.json', os.path.join(CACHE, lang, 'weapon', a + '.json'))
    print(len(want), 'characters,', len(arcs), 'Arcs,', len(LANGS), 'languages in', CACHE)
