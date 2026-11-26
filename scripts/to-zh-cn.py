# Writes the Simplified Chinese pages (src/content/docs/zh-cn/) from the Traditional
# Chinese pages (src/content/docs/zh-tw/). Run it after every change to a zh-tw page:
#
#   uv run --with opencc-python-reimplemented scripts/to-zh-cn.py
#
# Steps: replace Taiwan wording with the wording of the official Simplified Chinese
# notices (VOC), convert the characters (OpenCC tw2s), swap the title with its
# Simplified alias, and point links at /zh-cn/. Source URLs are kept as they are.
# Then run pipeline/build_pages.py, which puts the official Simplified game text into the
# archive and voice line pages and the Outfits tables, and writes the lists of those pages
# (characters/archives.md, characters/voices.md), the anomaly pages
# (anomalies/) and the item and achievement lists (items/) from their records in every language.
# OpenCC's phrase mode (tw2sp) is not used: it rewrites game terms (支援技能, 角色資料).

import glob
import os
import re
import sys

from opencc import OpenCC

cc = OpenCC('tw2s')
root = sys.argv[1] if len(sys.argv) > 1 else 'src/content/docs'

# Taiwan wording -> wording found in the notices under nte.perfectworld.com/cn/.
# Applied in order, before the character conversion. Add a pair when a zh-tw page
# brings in a new Taiwan term or a name that the two services write differently.
VOC = [
    # Names that differ between the Taiwan and the Simplified Chinese notices
    ('掏方斯記', '淘方斯记'), ('末班公車之夜', '末班公交车之夜'), ('神秘鈕扣', '神秘纽扣'),
    # Wording
    ('簡訊對話', '消息对话'), ('預先下載', '预下载'), ('永久販售', '永久在售'), ('販售', '出售'),
    ('攝影機', '摄像机'), ('機車', '摩托车'), ('儲存格', '单元格'), ('選單列', '菜单栏'),
    ('選單', '菜单'), ('身分', '身份'), ('背景設定', '背景设定'), ('設定', '设置'), ('介面', '界面'),
    ('伺服器', '服务器'), ('透過', '通过'), ('帳號', '账号'), ('登入', '登录'), ('資訊', '信息'),
    ('邀請連結', '邀请链接'), ('行動裝置', '移动设备'), ('儲值', '充值'), ('儲存空間', '存储空间'),
    ('64 位元', '64 位'), ('記憶體', '内存'), ('字元', '字符'), ('電子信箱', '电子邮箱'),
    ('無須課金', '无须付费'), ('連線', '联机'), ('台港澳', '港澳台'), ('洋裝', '连衣裙'),
    ('計畫', '计划'), ('網路', '网络'), ('型態', '形态'), ('暫存空間', '临时空间'),
    ('滑翔翼造型', '滑翔翼皮肤'),
]

# The names page quotes Traditional Chinese names in its prose; put them back after conversion.
NAMES_FIX = [
    ('有两种写法：法帝娅（官网角色介绍）与法蒂娅（', '有两种写法：法帝婭（官网角色介绍）与法蒂婭（'),
    ('光、灵、咒、魂出自港澳台服', '光、靈、咒、魂出自港澳台服'),
    ('繁体中文栏位依港澳台服为准，简体中文栏位依', '繁体中文一栏以港澳台服为准，简体中文一栏以'),
]


def conv(s):
    for a, b in VOC:
        s = s.replace(a, b)
    # 支援 is 'support' as a game role (kept) and 'supports' as a verb (支持 in Simplified usage).
    s = re.sub('支援(?!技能|角色)', '支持', s)
    return cc.convert(s)


def page(src, rel):
    text = open(src, encoding='utf-8').read()
    m = re.match(r'---\n(.*?)\n---\n(.*)', text, re.S)
    lines, body = m.group(1).split('\n'), m.group(2)

    title = next(l for l in lines if l.startswith('title:'))[6:].strip()
    start = next((k for k, l in enumerate(lines) if l.startswith('aliases:')), None)
    aliases, end = [], None
    if start is not None:
        end = start + 1
        while end < len(lines) and lines[end].startswith('  - '):
            aliases.append(lines[end][4:])
            end += 1
    # The Simplified name is an alias of the zh-tw page: it becomes the title, and the
    # Traditional title takes its place among the aliases.
    simplified = conv(title)
    if simplified != title:
        if simplified not in aliases:
            sys.exit(f'{rel}: add the alias "{simplified}" to the zh-tw page')
        aliases = [title if a == simplified else a for a in aliases]
        title = simplified

    out = []
    for k, l in enumerate(lines):
        if l.startswith('title:'):
            out.append('title: ' + title)
        elif start is not None and start < k < end:
            out.append('  - ' + aliases[k - start - 1])
        elif l.lstrip().startswith('url:'):
            out.append(l)
        else:
            out.append(conv(l))
    front = '\n'.join(out)

    if rel == 'names.md':
        # Table rows hold names in each script and stay as written; only header rows are converted.
        body = '\n'.join(
            l if l.startswith('| ') and not l.startswith('| 英文') else conv(l) for l in body.split('\n')
        )
        for a, b in NAMES_FIX:
            if a not in front + body:
                sys.exit(f'names.md: NAMES_FIX entry no longer matches: {a}')
            front, body = front.replace(a, b), body.replace(a, b)
    else:
        if '```' in body:
            sys.exit(f'{rel}: code blocks are not handled; keep them unconverted before using them')
        body = conv(body)
    body = body.replace('/zh-tw/', '/zh-cn/')

    dst = os.path.join(root, 'zh-cn', rel)
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    open(dst, 'w', encoding='utf-8').write('---\n' + front + '\n---\n' + body)


base = os.path.join(root, 'zh-tw')
files = sorted(glob.glob(base + '/**/*.md', recursive=True))
# Archive pages carry each language's own game text; pipeline/build_pages.py writes the
# Simplified Chinese ones from the Simplified game data, so they are not converted here.
files = [f for f in files if not re.search(r'/characters/[^/]+/(archive|voice)\.md$|/characters/(archives|voices)\.md$|/anomalies/|/items/', f)]
for f in files:
    page(f, os.path.relpath(f, base))
print(len(files), 'pages written to', os.path.join(root, 'zh-cn'))
