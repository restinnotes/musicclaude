"""11-09 交付用：把一版屏幕稿导出成给用户看的文字稿（不渲染）。
python r3/export_md.py TAG 输出目录
每首一份：每屏停留秒数、话（放大的关键词加粗）、感受（/ 隔开；到时出现的标出来）；末尾附这一版绝对验收里报的全部问题（按轻重）。
"""
import os, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
os.environ.setdefault('PUB_BC_ALL', '1')
import pub16, pub24
from pub24 import S, rd, WORKS
sys.stdout.reconfigure(encoding='utf-8')
NAMES = {'op60': '船歌 Op.60', 'op61': '幻想波兰舞曲 Op.61'}


def local_ids(w):
    src = rd(pub24.R2/f'{w}_src.json')
    loc = {b['id'] for s in src['sections'] for b in s['beads'] if any(p.get('local') for p in b['points'])}
    lpt = {p['id'] for s in src['sections'] for b in s['beads'] for p in b['points'] if p.get('local')}
    return loc, lpt


def export(tag, out):
    out = Path(out); out.mkdir(parents=True, exist_ok=True)
    for w in WORKS:
        scr = rd(S/f'screen_{w}_{tag}.json'); win = pub16.windows(w); loc, lpt = local_ids(w); L = []
        total = 0
        L.append(f"# {NAMES[w]} 屏幕稿（{tag}）\n")
        L.append("读法：每段标题后是这一屏的停留时间。**加粗**的是大字里放大加亮的关键词；“感受”是小字，用 / 隔开；标「到时出现」的，音乐走到对应的那几小节才出现，之后留到这一屏结束。\n")
        for s in scr['sections']:
            dur = win[s['sec']][1]-win[s['sec']][0]; n = 0
            L.append(f"\n## {s['sec']}（停留 {round(dur)} 秒）\n")
            for x in s['rows']:
                if x['kind'] == 'line':
                    t = x['text']; n += len(t)
                    for k in sorted(x.get('keys') or [], key=len, reverse=True): t = t.replace(k, f'**{k}**', 1)
                    L.append(f"话：{t}\n")
                else:
                    parts = []
                    for i in x['items']:
                        n += len(i['text'])
                        lo = i.get('bars') or (i.get('pt') in lpt if i.get('pt') else i.get('bead') in loc)
                        parts.append(i['text'] + ('「到时出现」' if lo else ''))
                    L.append("感受：" + ' / '.join(parts) + "\n")
            total += n
            L.append(f"<small>这一屏约 {n} 字，每秒约 {n/dur:.1f} 字</small>\n")
        L.insert(2, f"整屏共约 {total} 字。\n")
        (out/f'{w}_{tag}.md').write_text('\n'.join(L), encoding='utf-8')
        print('写好', out/f'{w}_{tag}.md', total, '字', flush=True)


if __name__ == '__main__':
    export(sys.argv[1], sys.argv[2])
