"""Find player guides on Bilibili and read what comes with them, for the community section.

  pnpm scout search <keyword> [<keyword> ...] [--since YYYY-MM-DD] [--pages N]
      Newest videos for each keyword, one line each: date, BV id, length, views, creator, title.
      Videos already in records/community/sources.json are marked "*".
  pnpm scout read <BV id or URL> [--out DIR]
      Writes DIR/<BV>/video.json (title, creator, date, description, tags) and comments.json
      (the creator's pinned comment, every reply the creator wrote under any thread, the
      most-liked comments), and downloads the pictures of the creator's comments to DIR/<BV>/.
      Prints a summary. DIR defaults to $TMPDIR/scout; nothing it writes is committed.

Where a guide's tier chart or one-image summary (一圖流) is, it is usually the creator's pinned
comment, and corrections or extra results ("298 萬 with a fourth teammate") are the creator's
replies under viewers' questions. The pinned comment comes only from the WBI-signed endpoint
/x/v2/reply/wbi/main (its top.upper); the plain /x/v2/reply/main leaves it out.

Anonymous requests work. A cookie file in Netscape format, named by the environment variable
BILIBILI_COOKIES, is used when set (more comments per page). Requests are paced 3 s apart.
Exit 0 on success, 2 when Bilibili refuses.
"""

import hashlib
import http.cookiejar
import json
import os
import re
import sys
import tempfile
import time
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CST = timezone(timedelta(hours=8))  # Bilibili dates are China Standard Time
UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36'
MIXIN = [46, 47, 18, 2, 53, 8, 23, 32, 15, 50, 10, 31, 58, 3, 45, 35, 27, 43, 5, 49, 33, 9, 42, 19, 29, 28, 14, 39, 12, 38, 41,
         13, 37, 48, 7, 16, 24, 55, 40, 61, 26, 17, 0, 1, 60, 51, 30, 4, 22, 25, 54, 21, 56, 59, 6, 63, 57, 62, 11, 36, 20, 34, 44, 52]

jar = http.cookiejar.MozillaCookieJar()
if os.environ.get('BILIBILI_COOKIES'):
    jar.load(os.environ['BILIBILI_COOKIES'], ignore_discard=True, ignore_expires=True)
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))
_last = [0.0]
_mixin = []


def fetch(url, referer='https://www.bilibili.com/', raw=False):
    if not any(c.name == 'buvid3' for c in jar) and url != 'https://www.bilibili.com/':
        fetch('https://www.bilibili.com/', raw=True)  # an anonymous visitor needs buvid3 first, or the API answers 412
    for attempt in range(4):
        wait = 3 - (time.time() - _last[0])
        if wait > 0:
            time.sleep(wait)
        _last[0] = time.time()
        req = urllib.request.Request(url, headers={'User-Agent': UA, 'Referer': referer, 'Origin': 'https://www.bilibili.com'})
        try:
            body = opener.open(req, timeout=30).read()
        except urllib.error.HTTPError as e:
            if e.code in (412, 429, 567) and attempt < 3:
                time.sleep(10 * (attempt + 1))
                continue
            raise SystemExit(f'scout: Bilibili refused {url.split("?")[0]}: HTTP {e.code}') from None
        if raw:
            return body
        d = json.loads(body)
        if d.get('code') == -412 and attempt < 3:
            time.sleep(10 * (attempt + 1))
            continue
        if d.get('code') != 0:
            print(f'scout: {url.split("?")[0]}: {d.get("code")} {d.get("message")}', file=sys.stderr)
            sys.exit(2)
        return d['data']
    sys.exit(2)


def signed(params):
    """WBI signature. Values are percent-encoded with %20, not '+', or the server answers -403."""
    if not _mixin:
        img = fetch('https://api.bilibili.com/x/web-interface/nav', raw=True)
        img = json.loads(img)['data']['wbi_img']
        raw = ''.join(u.rsplit('/', 1)[1].split('.')[0] for u in (img['img_url'], img['sub_url']))
        _mixin.append(''.join(raw[i] for i in MIXIN)[:32])
    p = {k: re.sub(r"[!'()*]", '', str(v)) for k, v in {**params, 'wts': int(time.time())}.items()}
    q = urllib.parse.urlencode(sorted(p.items()), quote_via=urllib.parse.quote)
    return q + '&w_rid=' + hashlib.md5((q + _mixin[0]).encode()).hexdigest()


def day(ts):
    return datetime.fromtimestamp(ts, CST).strftime('%Y-%m-%d')


def known_videos():
    f = ROOT / 'records' / 'community' / 'sources.json'
    if not f.exists():
        return set()
    return {m.group(0) for s in json.loads(f.read_text(encoding='utf-8'))['sources'] for m in [re.search(r'BV\w{10}', s['url'])] if m}


def search(words, since=None, pages=1):
    known = known_videos()
    seen = set()
    for word in words:
        print(f'# {word}')
        for page in range(1, pages + 1):
            data = fetch('https://api.bilibili.com/x/web-interface/wbi/search/type?' + signed(
                {'search_type': 'video', 'keyword': word, 'order': 'pubdate', 'page': page}))
            for v in data.get('result') or []:
                if v['bvid'] in seen or (since and day(v['pubdate']) < since):
                    continue
                seen.add(v['bvid'])
                title = re.sub(r'<[^>]+>', '', v['title'])
                mark = '*' if v['bvid'] in known else ' '
                print(f"{mark} {day(v['pubdate'])}  {v['bvid']}  {v['duration']:>6}  {v['play']:>7}  {v['author']}  {title}")


def bvid_of(arg):
    m = re.search(r'BV\w{10}', arg)
    if not m:
        raise SystemExit(f'scout: no BV id in {arg}')
    return m.group(0)


def comment(r):
    c = r['content']
    return {'rpid': r['rpid'], 'creator': r['member']['uname'], 'mid': int(r['member']['mid']), 'date': day(r['ctime']),
            'likes': r['like'], 'text': c['message'], 'pictures': [p['img_src'] for p in c.get('pictures') or []],
            'replies': r.get('rcount', 0)}


def read(arg, out):
    bv = bvid_of(arg)
    page = f'https://www.bilibili.com/video/{bv}/'
    v = fetch(f'https://api.bilibili.com/x/web-interface/view?bvid={bv}', referer=page)
    mid = v['owner']['mid']
    tags = [t['tag_name'] for t in fetch(f'https://api.bilibili.com/x/tag/archive/tags?bvid={bv}', referer=page) or []]
    video = {'bvid': bv, 'aid': v['aid'], 'url': page, 'title': v['title'], 'creator': v['owner']['name'], 'mid': mid,
             'published': day(v['pubdate']), 'seconds': v['duration'], 'views': v['stat']['view'], 'description': v['desc'],
             'tags': tags, 'parts': [{'page': p['page'], 'title': p['part'], 'seconds': p['duration']} for p in v.get('pages') or []]}
    # Top-level comments by heat, then every thread with replies is opened for the creator's answers.
    pinned, top, threads, offset = None, [], [], ''
    for _ in range(10):
        d = fetch('https://api.bilibili.com/x/v2/reply/wbi/main?' + signed(
            {'oid': v['aid'], 'type': 1, 'mode': 3, 'pagination_str': json.dumps({'offset': offset}, separators=(',', ':')),
             'plat': 1, 'seek_rpid': '', 'web_location': 1315875}), referer=page)
        up = (d.get('top') or {}).get('upper')
        if up and not pinned:
            pinned = comment(up)
        for r in d.get('replies') or []:
            top.append(comment(r))
        offset = d['cursor'].get('pagination_reply', {}).get('next_offset', '')
        if d['cursor'].get('is_end') or not offset:
            break
    by_creator = [c for c in top if c['mid'] == mid]
    for c in [c for c in top if c['replies']]:
        for pn in range(1, 6):
            d = fetch(f"https://api.bilibili.com/x/v2/reply/reply?oid={v['aid']}&type=1&root={c['rpid']}&ps=20&pn={pn}", referer=page)
            rs = d.get('replies') or []
            for r in rs:
                if int(r['member']['mid']) == mid:
                    by_creator.append({**comment(r), 'under': {'rpid': c['rpid'], 'creator': c['creator'], 'text': c['text']}})
            if len(rs) < 20:
                break
    folder = Path(out) / bv
    folder.mkdir(parents=True, exist_ok=True)
    pics = []
    for c in ([pinned] if pinned else []) + by_creator:
        for i, src in enumerate(c['pictures']):
            name = f"{c['rpid']}-{i + 1}{Path(urllib.parse.urlparse(src).path).suffix or '.jpg'}"
            (folder / name).write_bytes(fetch(src.replace('http://', 'https://'), referer=page, raw=True))
            pics.append(str(folder / name))
    comments = {'pinned': pinned, 'by_creator': by_creator,
                'most_liked': sorted((c for c in top if c['mid'] != mid), key=lambda c: -c['likes'])[:15], 'top_level_read': len(top)}
    (folder / 'video.json').write_text(json.dumps(video, ensure_ascii=False, indent=1), encoding='utf-8')
    (folder / 'comments.json').write_text(json.dumps(comments, ensure_ascii=False, indent=1), encoding='utf-8')

    print(f"{video['title']}\n{video['creator']}  {video['published']}  {video['seconds']} s  {video['views']} views  {page}")
    print(f"tags: {'、'.join(tags)}\n\ndescription:\n{video['description']}\n")
    print('pinned:', f"{pinned['text']}  {pinned['pictures']}" if pinned else 'none')
    print(f'\nthe creator under viewers\' comments ({len(by_creator)}):')
    for c in by_creator:
        under = f"  [under {c['under']['creator']}: {c['under']['text'][:60]}]" if c.get('under') else ''
        print(f"- {c['text']}{under}")
    print(f"\npictures saved: {pics or 'none'}\nwritten: {folder}")


def main(argv):
    if len(argv) < 2 or argv[0] not in ('search', 'read'):
        print(__doc__)
        return 2
    opts = {}
    args = []
    it = iter(argv[1:])
    for a in it:
        if a.startswith('--'):
            opts[a[2:]] = next(it)
        else:
            args.append(a)
    if argv[0] == 'search':
        search(args, opts.get('since'), int(opts.get('pages', 1)))
    else:
        for a in args:
            read(a, opts.get('out', Path(tempfile.gettempdir()) / 'scout'))
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
