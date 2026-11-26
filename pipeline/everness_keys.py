# Prints the arguments for pipeline/fetch_everness.mjs: the character ids (archive, then voice lines), then the keys of
# the outfits, Arcs and items whose descriptions the pages show (the progression page and the item
# lists), the achievements page, then the English or Japanese
# pages for text that the nanoka.cc files leave untranslated. The keys come from the
# English rows of the pages and the cached nanoka.cc files, so run pipeline/fetch_nanoka.py first.
#
#   CHROMIUM=... node pipeline/fetch_everness.mjs $(python3 pipeline/everness_keys.py)

import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from build_records import EDITION, arc_keys, character_ids, item_keys, list_keys, outfit_keys, untranslated_parts  # noqa: E402

if __name__ == '__main__':
    ids = character_ids()
    print(' '.join(ids.values()),
          '--voices', ','.join(ids.values()),
          '--outfits', ','.join(k for slug in ids for k in outfit_keys(slug, ids[slug])),
          '--arcs', ','.join(arc_keys().values()),
          '--items', ','.join(dict.fromkeys([*item_keys().values(), *(k for ks in list_keys().values() for k in ks)])),
          '--achievements', end='')
    # English or Japanese text that the nanoka.cc files leave untranslated.
    fixes = [f for cid in ids.values() for f in untranslated_parts(cid)]
    for ed in sorted({EDITION[lang] for lang, _, _ in fixes}):
        esp = [k for lang, p, k in fixes if EDITION[lang] == ed and p == 'espers']
        cos = [k for lang, p, k in fixes if EDITION[lang] == ed and p == 'cosmetics']
        print('', '--edition', ed, *esp, *(['--outfits', ','.join(cos)] if cos else []), end='')
    print()
