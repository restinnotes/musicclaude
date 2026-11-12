"""11-09 晚 绝对验收第三版的校准对照：从一个屏幕稿出发，只改一处，脚本生成（不调模型），只用于校准，不进成品。
CL 打转：后半的三屏，把话换成往前数第四屏的话（人物原地重复）。
CS 分开：每屏先放全部话，再把全部感受并成一行放在最后（按来源分成两块）。
CN 去音乐（正向）：删掉讲音乐本身的小字块（含声部、左右手、和弦、技法等词）。
CV 笼统：每个小字块换成它所在那行情绪的笼统说法。
python r3/ctl.py 来源TAG     → r3/s24/screen_{作品}_{来源TAG}{CL|CS|CN|CV}.json
"""
import sys, copy, re
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from pub24 import S, rd, wr, WORKS
sys.stdout.reconfigure(encoding='utf-8')
MUS = re.compile('左手|右手|声部|声线|和弦|八度|颤音|琶音|音型|调性|旋律|低音|高音|伴奏|主题|三连音|装饰音|内声|节奏|小节|花腔|音区')
VAGUE = {'炽热': '很激动', '欢喜': '很开心', '亲密': '很温暖', '安心': '很安心', '孤单': '很孤单', '不安': '很不安', '悬着': '有点忐忑'}


def make(w, tag):
    d = rd(S/f'screen_{w}_{tag}.json'); secs = d['sections']; n = len(secs)
    cl = copy.deepcopy(d)
    for i in (n//2, n//2+2, n//2+4):
        if i < n and i-4 >= 0:
            src = [r for r in secs[i-4]['rows'] if r['kind'] == 'line']; k = 0
            for r in cl['sections'][i]['rows']:
                if r['kind'] == 'line' and src:
                    s0 = src[k % len(src)]; r['text'] = s0['text']; r['keys'] = list(s0.get('keys') or []); k += 1
    cs = copy.deepcopy(d)
    for s in cs['sections']:
        L = [r for r in s['rows'] if r['kind'] == 'line']; F = [i for r in s['rows'] if r['kind'] == 'feel' for i in r['items']]
        s['rows'] = L + ([{'kind': 'feel', 'items': F}] if F else [])
    cn = copy.deepcopy(d); cut = 0
    for s in cn['sections']:
        rows = []
        for r in s['rows']:
            if r['kind'] == 'feel':
                keep = [i for i in r['items'] if not MUS.search(i['text'])]; cut += len(r['items'])-len(keep)
                if keep: rows.append(dict(r, items=keep))
            else: rows.append(r)
        s['rows'] = rows
    cv = copy.deepcopy(d)
    for s in cv['sections']:
        emo = '悬着'
        for r in s['rows']:
            if r['kind'] == 'line': emo = r.get('emotion') or emo
            else:
                for i in r['items']: i['text'] = VAGUE.get(emo, '有点忐忑')
    for suf, x in (('CL', cl), ('CS', cs), ('CN', cn), ('CV', cv)): wr(S/f'screen_{w}_{tag}{suf}.json', x)
    print(w, tag, '对照已生成；CN 删了讲音乐的小字', cut, '块', flush=True)


if __name__ == '__main__':
    for w in WORKS: make(w, sys.argv[1])
