"""把屏幕稿或线导出成可读文本，给我逐屏读（不调模型）。python r3/dump.py screen TAG [SRC] | line SRC"""
import json, sys, os
from pathlib import Path
sys.stdout.reconfigure(encoding='utf-8')
D = Path('D:/musicclaude/_dag2_video_20261104/读稿'); D.mkdir(exist_ok=True)
H = Path(__file__).resolve().parents[1]
def win(w, src):
    d = json.load(open(H/src/f'{w}_src.json', encoding='utf-8')); return {s['sec']: s['window'] for s in d['sections']}
if sys.argv[1] == 'line':
    src = sys.argv[2]
    for w in ('op60', 'op61'):
        d = json.load(open(H/src/f'{w}_src.json', encoding='utf-8')); out = [f"# {w} {src}  Center：{d['center']}"]
        for s in d['sections']:
            out.append(f"\n## {s['sec']}（{s.get('relation', '')}）")
            for l in s['lines']: out.append(f"- {l['text']}  〔珠子 {'、'.join(l.get('beads') or [])}〕")
        (D/f'线_{src}_{w}.md').write_text('\n'.join(out), encoding='utf-8')
else:
    tag = sys.argv[2]; src = sys.argv[3] if len(sys.argv) > 3 else 'r2c'
    for w in ('op60', 'op61'):
        d = json.load(open(H/'r3/s24'/f'screen_{w}_{tag}.json', encoding='utf-8')); W = win(w, src); out = []; tot = 0
        for s in d['sections']:
            a, b = W[s['sec']]; n = 0; blk = 0; body = []
            for r in s['rows']:
                at = f"（{r['at']:g}秒）" if 'at' in r else ''
                if r['kind'] == 'line':
                    t = r['text']
                    for k in r.get('keys') or []: t = t.replace(k, f'【{k}】', 1)
                    body.append(f"大：{t}{at}"); n += len(r['text']); blk += 1
                else:
                    body.append('   小：' + ' / '.join(i['text'] + (f"〔{i['bars']}小节〕" if i.get('bars') else '') + (f"（{i['at']:g}秒）" if 'at' in i else '') for i in r['items'])); n += sum(len(i['text']) for i in r['items']); blk += len(r['items'])
            for nt in s.get('notes') or []: body.append(f"   旁注〔{nt['bars']}〕：{nt['text']}"); n += len(nt['text'])
            tot += n; out.append(f"\n## {s['sec']}（{round(b-a)} 秒，{n} 字，{blk} 块，每秒 {n/(b-a):.1f} 字）"); out += body
        (D/f'{tag}_{w}.md').write_text(f"# {tag} {w} 共 {tot} 字\n" + '\n'.join(out), encoding='utf-8'); print(tag, w, tot, '字')
