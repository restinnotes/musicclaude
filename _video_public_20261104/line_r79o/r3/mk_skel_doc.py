"""11-12 夜：把“之前的骨架 + 当时对它的评价”整理成可读文档（用户要看）。取最近一轮完整的写线 L34g61（骨架不看珠子），外加 L31a 骨架被全部打回的评语。"""
import json, os, sys
sys.path.insert(0, 'D:/musicclaude/_video_public_20261104/line_r79o'); os.environ['PUB_SRC'] = 'r2e'
sys.stdout.reconfigure(encoding='utf-8')
from pub24 import parse
RUNS = 'D:/musicclaude/_thread_evo_20261019/runs/'; NAME = {'op60': '船歌 Op.60', 'op61': '幻想波兰舞曲 Op.61'}
ld = lambda t, w, s: parse(open(f'{RUNS}sc{t}_{w}_{s}/output.txt', encoding='utf-8').read())


def md(x, depth=0):
    pad = '  ' * depth
    if isinstance(x, dict): return '\n'.join(f'{pad}- **{k}**：' + (str(v) if not isinstance(v, (dict, list)) else '\n' + md(v, depth + 1)) for k, v in x.items())
    if isinstance(x, list): return '\n'.join((f'{pad}- ' + str(v)) if not isinstance(v, (dict, list)) else md(v, depth) + ('\n' if isinstance(v, dict) else '') for v in x)
    return pad + str(x)


out = ['# 之前的骨架，和当时对它的评价（11-12 整理）', '',
       '骨架 = 写线的第一步：GPT-6 不看珠子，只拿段落顺序和 Center，写 3 条“这个人十几段里经历了什么”的路线。第二步由 GPT-6 给 3 条路线逐条评价、选一条。第三步照选中的路线写成线。',
       '下面是最近一轮完整跑通的写线（11-11，代号 L34g61）的骨架原文和第二步的评价原文，都没有删改。最后附 11-11 另一轮（L31a，要求每段必须有新东西）骨架被全部打回的评语。', '',
       '字段说明：state = 这一段此刻的情况；delta_type = 这一段算哪一类（新变化 / 后果 / 延续 / 回到旧处但有新增……）；delta = 相对前面真正新增的内容；still_open = 还悬着的问题；established = 全篇“已经成立的事”的账本。', '']
for w in ('op60', 'op61'):
    a1 = ld('L34g61', w, 'A1'); a2 = ld('L34g61', w, 'A2'); a4 = ld('L34g61', w, 'A4'); rs = a1.get('routes') or a1.get('items'); base = str(a4.get('base_route'))
    out += [f'## {NAME[w]}', '']
    for r in rs:
        sel = '（被选中，线照它写）' if str(r.get('route_id')) == base else '（没选）'
        out += [f"### 路线 {r.get('route_id')} {sel}", '', f"**这件事：**{r.get('situation')}", '']
        if r.get('hinge'): out += ['**铰链：**' + (r['hinge'] if isinstance(r['hinge'], str) else json.dumps(r['hinge'], ensure_ascii=False)), '']
        out += ['| 段 | 此刻的情况 | 类别 | 真正新增的 | 还悬着的 |', '|---|---|---|---|---|']
        f = lambda v: ('；'.join(map(str, v)) if isinstance(v, list) else str(v or '')).replace('\n', ' ').replace('|', '｜')
        out += [f"| {str(s['sec'])[:3]} | {f(s.get('state'))} | {f(s.get('delta_type'))} | {f(s.get('delta'))} | {f(s.get('still_open'))} |" for s in r['segments']]
        out += ['', '**已经成立的事（账本）：**', md(r.get('established') or []), '']
    out += [f'### {NAME[w]}：第二步对三条路线的评价（原文）', '', md(a2), '']
    out += [f'### {NAME[w]}：照选中的路线写出来的线', '']
    for s in a4['segments']: out += [f"**{str(s['sec'])[:3]}**　" + ' / '.join(i['text'] for i in s['items']), '']
out += ['## 附：11-11 另一轮（L31a）骨架被全部打回的评语', '']
for w in ('op60', 'op61'):
    a4 = ld('L31a', w, 'A4'); out += [f'**{NAME[w]}：**' + '；'.join(b.get('reason', '') for b in a4.get('blocked_sections', [])), '']
p = 'D:/musicclaude/_dag2_video_20261104/读稿/之前的骨架与评价_1112.md'
open(p, 'w', encoding='utf-8').write('\n'.join(out)); print(len('\n'.join(out)), '字')
