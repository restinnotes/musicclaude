"""11-09 晚 机械预检（迭代准则 I04 第一步，免费）：K22 四套都在我读第一屏时才发现旁注成段、带小节号、全曲过长，这些脚本就能查。
查：旁注超过 32 字；正文（含旁注）写了小节号；小字单块超过 30 字；大字单行超过 45 字；讲音乐本身的词；每屏每秒字数（大字+小字，不含旁注）。
只报，不改。python r3/k22check.py TAG [SRC]
"""
import json, re, sys
from pathlib import Path
H = Path(__file__).resolve().parents[1]
sys.stdout.reconfigure(encoding='utf-8')
MUS = re.compile('左手|右手|声部|声线|和弦|八度|颤音|琶音|音型|调性|大调|小调|旋律|低音区|高音区|伴奏|三连音|装饰音|内声|切分')
BAR = re.compile(r'\d+\s*[–\-—~～]?\s*\d*\s*小节|第\s*\d+')


def check(tag, src='r2c', quiet=False):
    bad = {}
    for w in ('op60', 'op61'):
        d = json.load(open(H/'r3/s24'/f'screen_{w}_{tag}.json', encoding='utf-8'))
        win = {s['sec']: s['window'] for s in json.load(open(H/src/f'{w}_src.json', encoding='utf-8'))['sections']}
        c = {'旁注超长': 0, '写了小节号': 0, '小字超长': 0, '大字超长': 0, '讲音乐': 0, '超密屏': 0}; tot = 0; dens = []
        for s in d['sections']:
            a, b = win[s['sec']]; n = 0
            texts = []
            for r in s['rows']:
                if r['kind'] == 'line':
                    texts.append(r['text']); n += len(r['text']); c['大字超长'] += len(r['text']) > 45
                else:
                    for i in r['items']: texts.append(i['text']); n += len(i['text']); c['小字超长'] += len(i['text']) > 30
            for nt in s.get('notes') or []: texts.append(nt['text']); c['旁注超长'] += len(nt['text']) > 32
            c['写了小节号'] += sum(1 for t in texts if BAR.search(t)); c['讲音乐'] += sum(len(MUS.findall(t)) for t in texts)
            rate = n/(b-a); dens.append(rate); c['超密屏'] += rate > 6.5; tot += n
        bad[w] = c
        if not quiet: print(f"{tag} {w}：全曲 {tot} 字，每屏每秒最高 {max(dens):.1f} 字；" + '，'.join(f'{k} {v}' for k, v in c.items()), flush=True)
    return bad


if __name__ == '__main__':
    check(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else 'r2c')
