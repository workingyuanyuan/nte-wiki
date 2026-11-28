"""Write the zh-cn text of every claim in records/community/claims.json from its zh-tw text.

  uv run --with opencc-python-reimplemented pipeline/community_zh_cn.py

Claims of the guide pages (pull, gain, rotation, reason, tip) carry their own sentences in each
language; the Simplified Chinese one is converted from the Traditional one with the same wording
table as the pages (scripts/to-zh-cn.py), never written by hand. Names inside {char:…}, {arc:…},
{cart:…} are left as they are: build_community.py resolves them.
"""

import importlib.util
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
spec = importlib.util.spec_from_file_location('to_zh_cn', os.path.join(ROOT, 'scripts', 'to-zh-cn.py'))
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

PATH = os.path.join(ROOT, 'records', 'community', 'claims.json')


def conv(text):
    parts = re.split(r'(\{(?:char|arc|cart):[^}]+\})', text)
    return ''.join(p if p.startswith('{') else mod.conv(p) for p in parts)


def walk(x):
    if isinstance(x, dict):
        if 'zh-tw' in x and 'en' in x and isinstance(x['zh-tw'], str):
            x['zh-cn'] = conv(x['zh-tw'])
        for v in x.values():
            walk(v)
    elif isinstance(x, list):
        for v in x:
            walk(v)


data = json.load(open(PATH, encoding='utf-8'))
for c in data['claims']:
    if c['kind'] in ('pull', 'gain', 'rotation', 'reason', 'tip'):
        walk(c)
open(PATH, 'w', encoding='utf-8').write(json.dumps(data, ensure_ascii=False, indent=1))
print('zh-cn written for the guide claims')
