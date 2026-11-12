"""11-07 V2.03d 按停留秒数删感受碎片（线不动）。
来由：从定稿线重写后（g68RB、g68RD），“为什么”“前后一件事”赢回来了，op60 却一直输“扫得动”；评委点名的几乎都是停留短、字最密的段
（op60 S05 18 秒放了 259 字，现在的视频 187 字）。覆盖和精细远高于 w23（0.93 对 0.71、0.97 对 0.80），余量在感受碎片上。
只删整块碎片、不改字；每颗珠子至少留一块；只动“每秒字数”超过现在视频同一段的段，删到大致和现在视频这一段的总字数相当。
python trimfeel.py SRC NEW
"""
import copy, os, sys
from concurrent.futures import ThreadPoolExecutor
import pub16
from pub24 import S, R3, rd, wr, call, parse, G6, WORKS, to_script

TRIM = """下面是一首钢琴曲大众版“边听边看”视频屏幕稿里的几段。每段有大字的“线”（一个人经历的事）和小字的“感受碎片”（听的人此刻的感受，[ ] 里是碎片编号，后面是它来自的珠子）。观众边听边扫，每段只停留写明的秒数。

扮观众的评委说这几段字太密，几秒钟里扫不完（别的段没问题）。线不动；请在每段删掉一些感受碎片，让这一段的总字数（线 + 碎片）大致降到写明的参照字数。

删哪些（按顺序优先）：
1. 同一颗珠子里意思相近的碎片，只留最具体、最有画面或身体感的那一块；
2. 重说了线已经说过的意思的碎片；
3. 只剩一个抽象情绪词、或要懂音乐术语才看得懂的碎片（如调性、曲式名）；
4. 和别的段重复、没有新东西的碎片。
不能删：每颗珠子至少留一块；标“到时出现”的碎片尽量留（它跟着音乐出现，观众不用一次读完）。只删整块，不改字、不合并、不新写。

只输出 JSON：{"sections":[{"sec":"S05","drop":["碎片编号", "..."]}]}，只列要动的段。

{SECS}
"""


def dense(w, tag):
    """每秒字数超过现在视频同一段的段 → {段: (秒数, 现在视频这一段总字数)}"""
    win = pub16.windows(w); d = rd(R3/f'script_{w}_w23.json')
    w23 = {s['sec']: sum(len(l['text']) for g in s['groups'] for l in g['lines'])+sum(len(b['text']) for g in s['groups'] for b in g['beads']) for s in d['sections']}
    out = {}
    for s in rd(S/f'screen_{w}_{tag}.json')['sections']:
        n = sum(len(x['text']) for x in s['rows'] if x['kind'] == 'line')+sum(len(i['text']) for x in s['rows'] if x['kind'] == 'feel' for i in x['items'])
        if n > w23[s['sec']]: out[s['sec']] = (round(win[s['sec']][1]-win[s['sec']][0]), w23[s['sec']], n)
    return out


def one(a):
    w, src, new = a; p = S/f'screen_{w}_{new}.json'
    if p.exists(): to_script(w, new, rd(p)); return True
    scr = copy.deepcopy(rd(S/f'screen_{w}_{src}.json')); ds = dense(w, src); txt = []; idmap = {}
    for s in scr['sections']:
        if s['sec'] not in ds: continue
        sec, ref, n = ds[s['sec']]
        if os.environ.get('PUB_TF_HALF') == '1': ref = ref + (n - ref)//2   # 11-07：删到 w23 删过头（覆盖掉到 0.58），这一版只删超出部分的一半
        txt.append(f"\n### {s['sec']}（停留 {sec} 秒；现在 {n} 字，参照 {ref} 字）"); k = 0
        for r in s['rows']:
            if r['kind'] == 'line': txt.append('线：'+r['text'])
            else:
                for i in r['items']:
                    k += 1; fid = f"{s['sec']}-{k}"; idmap[fid] = i
                    txt.append(f"  [{fid}] {i['text']}（{i['bead']}{'，到时出现' if i.get('bars') else ''}）")
    msg = TRIM.replace('{SECS}', '\n'.join(txt))
    for t in range(3):
        ans = call(f'pub24TF_{w}_{new}'+('' if not t else f'_r{t}'), msg, G6, 'gpt3s', 'public24-trimfeel')
        try:
            r = parse(ans); drop = {f for x in r['sections'] for f in x.get('drop') or [] if f in idmap}; dropped = {id(idmap[f]) for f in drop}
            nd = 0; kept_back = 0
            for s in scr['sections']:
                if s['sec'] not in ds: continue
                beads = {i['bead'] for x in s['rows'] if x['kind'] == 'feel' for i in x['items']}
                for x in s['rows']:
                    if x['kind'] == 'feel':
                        before = len(x['items']); x['items'] = [i for i in x['items'] if id(i) not in dropped]; nd += before - len(x['items'])
                left = {i['bead'] for x in s['rows'] if x['kind'] == 'feel' for i in x['items']}
                orig = [x for x in rd(S/f'screen_{w}_{src}.json')['sections'] if x['sec'] == s['sec']][0]['rows']
                for b in beads - left:   # 每颗珠子至少留一块：删光了就把它原来的第一块放回原来那一行、原来的位置
                    for j, x in enumerate(orig):
                        if x['kind'] != 'feel': continue
                        k = next((q for q, i in enumerate(x['items']) if i['bead'] == b), None)
                        if k is not None:
                            keep = [i for i in x['items'] if any(i['text'] == y['text'] for y in s['rows'][j]['items'])] + [x['items'][k]]
                            s['rows'][j]['items'] = [i for i in x['items'] if i in keep]; kept_back += 1; break
                s['rows'] = [x for x in s['rows'] if x['kind'] == 'line' or x['items']]
            wr(p, scr); to_script(w, new, scr)
            after = dense(w, new)
            print(w, new, '动了', len(ds), '段，删', nd, '块，放回', kept_back, '块；仍超过参照的段', len(after), flush=True); return True
        except Exception as ex: print('不合格', w, new, repr(ex)[:200], flush=True)
    return False


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    src, new = sys.argv[1], sys.argv[2]
    with ThreadPoolExecutor(2) as ex: print(list(ex.map(one, [(w, src, new) for w in WORKS])), flush=True)
