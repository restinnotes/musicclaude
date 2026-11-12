"""把视频稿导出成可读文字。"""
import json, sys
sys.stdout.reconfigure(encoding='utf-8')
names = {'op60': ('船歌', 'r1'), 'op61': ('幻想波兰舞曲', 'r2')}
for w, (n, tag) in names.items():
    d = json.load(open(f'runs/script_{w}_{tag}.json', encoding='utf-8'))
    rows = [f'# {n} · 大众版文字（{tag}）', '', '珠子是观众正听到的，线是这个人为什么这样。屏幕上先出珠子，再落线（全曲第一拍例外）。线里加粗的是高亮短语，也是右栏短语。', '', '右栏阶段：'+' → '.join(p['label'] for p in d['phases']), '']
    for s in d['sections']:
        rows.append(f"## {s['sec']}")
        for b in s['beats']:
            rows += ['- '+x['text'] for x in b['beads']]
            l = b['line']; rows += ['', '**线：**'+l['text'].replace(l['key'], f"**{l['key']}**", 1), '']
    open(f'out/{n}_大众版文字.md', 'w', encoding='utf-8').write('\n'.join(rows))
