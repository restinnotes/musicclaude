"""11-09 晚 I12 第 2 次：K23b（GPT-5.6 修订）、K23c（GPT-6 修订）过了机械预检和我的一屏读稿，扫读明显变好（绝对验收中等约减半），
但核心内容丢了一大半（意思单元核心留住 0.24–0.44，K11g 0.82–0.83）。交回提出者：这条路本来不行，还是方向对、怎么改。
补给他们一样新能力：旁注可以挂局部珠子的某条要点，按要点自己的时间窗出现、过后淡出（同一时刻的字不变多，颗粒度可以保住）。
python r3/adv_k23r.py   → r3/s24/adv_k23r_{g6|g56}.json；提示词 r3/s24/prompt_K23r_{g6|g56}_{screen|line|map}.txt
"""
import json, sys, re, os
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
os.environ.setdefault('PUB_SRC', 'r2c')
import prompt_lint
from pub24 import S, rd, call, parse, G6, G56
sys.stdout.reconfigure(encoding='utf-8')
NL = chr(10); D = Path('D:/musicclaude/_dag2_video_20261104/读稿')
MINE = {'g56': ('P2', 'g68K23b', 'r2k23b', 'prompt_K22r_g56_P2'), 'g6': ('P1', 'g68K23c', 'r2k23c', 'prompt_K22r_g6_P1')}

ASK = """你是上一轮的顾问。你修订过的方案（附在最后：你的改线、对应、写屏幕稿提示词）这次跑出来了。好消息和坏消息都很明确，请判断下一步。

【结果】（两首；“中等”是逐屏绝对验收报的中等问题条数，两位评委各一遍；“核心留住”是把原料拆成意思单元后，核心单元在屏幕上留住的比例）
{TABLE}

【我自己读的】
- 好：每屏一两条大字、三四块短感受，一眼看得到入口；对着具体小节的感受到时出现，旁注一行一条。这是这几轮里第一次真正“扫得动”的版本。
- 坏 1（最大）：全曲只剩约 1100–1300 字（现在的 K11g 约 3100、旧视频约 2600）。珠子各剩一个锚点，颗粒度明显变粗。用户 11-06 原话：“珠子不能少、颗粒度不能变粗”。下面是你这版丢掉的一些核心单元（原料原文，供你看丢的是什么样的东西，不能写进提示词）：
{LOST}
- 坏 2：改过的线短了，但骨架和原线一样：原线里来回说同一个事实的几段（例如船歌几次“对方仍亲近、没退开”）都还在，“同一事实全曲只交代一次”的规则没有起作用。
- 坏 3（只 K23c）：有一屏把这一屏最关键的转折放成了小字，大字反而是次要的。
- 测法提醒：意思单元清单里三分之二被标成“核心”（每屏约 10 个），偏宽；所以不要把“核心留住”追到 0.83，但从 0.83 掉到 0.3 说明确实丢了大量具体内容。

【新增的能力（上一轮没有）】
旁注可以挂局部珠子的某一条要点（输入里局部珠子下面列了“要点 编号（这一屏第几秒）”），按那条要点自己的时间出现、至少留 5 秒、过后淡出。输出时在旁注里写 "pt":"要点编号"（写了 pt 就不用写 bars）。因为旁注出现了又会淡出，不会在屏上越积越多，所以局部珠子可以按要点拆成几条依次出现的旁注（每条仍不超过 30 字、同一时刻最多两三条），颗粒度不必压到一个锚点。主文字区仍是累积显示，容量照旧（舒服的字号下一屏约 120–180 字）。

请回答：这条路本来不行（为什么），还是方向对？方向对就给出改过的完整提示词（改线、对应、写屏幕稿三份，不改的原样给）。要求：
- 同时守住“扫得动”（这一版做到的不能退）和“颗粒度不变粗”：说清楚哪些内容放主区、哪些放按时间出现的旁注、怎么排，才能两样都做到。
- 线的打转要真的解决：同一个事实只完整交代一次，后面只写它带来的新东西；没有新东西就合并。
- 提示词里不放任何具体作品的内容或例子。占位符和输出格式同上一轮；旁注可以写 {"text":"…","from":["…"],"pt":"要点编号"} 或 {"text":"…","from":["…"],"bars":"…"}。
只输出 JSON：{"verdict":"不行|方向对","why":"…","fix":"…","prompt_screen":"…","prompt_line":"…","prompt_map":"…"}。回答时请不要进行联网搜索。

【你上一轮修订的提示词】
=== 改线 ===
{PL}
=== 对应 ===
{PM}
=== 写屏幕稿 ===
{PS}
"""


def lost(tag, n=10):
    out = []
    for w in ('op60', 'op61'):
        units = {u['uid']: u for u in rd(S/f'units_{w}.json')}
        vs = {}
        for j in ('g6', 'g56'):
            p = S/f'cov3_{w}_{j}_{tag}.json'
            if p.exists():
                for x in rd(p).get('items') or []: vs.setdefault(x['uid'], []).append(x.get('verdict'))
        gone = [u for u, v in vs.items() if units.get(u, {}).get('tier') == '核心' and sum(1 for x in v if x == '没有') * 2 > len(v)]
        out += [f"- {w} {u}：{units[u]['what']}" for u in gone[:n]]
    return NL.join(out)


def table():
    rows = []
    for tag in ('g68K11g', 'g68K23b', 'g68K23c'):
        for w in ('op60', 'op61'):
            med = [sum(1 for s in rd(S/f'openA3_{w}_{j}_{tag}_run1.json').get('screens') or [] for x in s.get('issues') or [] if x.get('severity') == '中等') for j in ('g6', 'g56')]
            chars = sum(len(r['text']) if r['kind'] == 'line' else sum(len(i['text']) for i in r['items']) for s in rd(S/f'screen_{w}_{tag}.json')['sections'] for r in s['rows'])
            rows.append(f"- {tag} {w}：主区 {chars} 字；中等 {med[0]}、{med[1]}")
    return NL.join(rows) + NL + '- 核心留住：K11g 0.83 / 0.82；K23b 0.29 / 0.24；K23c 0.43 / 0.44（船歌 / 幻想）'


def one(jm):
    j, m = jm; p = S/f'adv_k23r_{j}.json'; pid, tag, src, pp = MINE[j]
    if p.exists(): r = rd(p)
    else:
        rp = lambda k: (S/f'{pp}_{k}.txt').read_text(encoding='utf-8')
        msg = ASK.replace('{TABLE}', table()).replace('{LOST}', lost(tag)).replace('{PL}', rp('line')).replace('{PM}', rp('map')).replace('{PS}', rp('screen'))
        if j == 'g56': msg = msg.replace('- 坏 3（只 K23c）：有一屏把这一屏最关键的转折放成了小字，大字反而是次要的。' + NL, '')
        print('材料', j, len(msg), flush=True); r = None
        for k in range(3):
            try: r = parse(call(f'adv_k23r_{j}' + ('' if not k else f'_r{k}'), msg, m, 'gpt3s', 'public24-adv')); assert r.get('verdict'); break
            except Exception as ex: print('不合格', j, repr(ex)[:150], flush=True); r = None
        if not r: return
        p.write_text(json.dumps(r, ensure_ascii=False, indent=1), encoding='utf-8')
    print(f"== {j}：{r.get('verdict')}；{(r.get('why') or '')[:400]}{NL}   改法：{(r.get('fix') or '')[:700]}", flush=True)
    for kind in ('screen', 'line', 'map'):
        tpl = (r.get('prompt_' + kind) or '').replace('{{', '{').replace('}}', '}')
        if len(tpl) < 50: continue
        bare = re.sub(r'\{(BUDGET|DAGSTD|FINAL|BEADS|CURRENT|CENTER|LINE|SEGS)\}', '', tpl)
        try: prompt_lint.lint(bare, f'adv_k23r_{j}_{kind}')
        except SystemExit as ex: print('泛化检查没过', j, kind, ex, flush=True)
        (S/f"prompt_K23r_{j}_{kind}.txt").write_text(tpl, encoding='utf-8')


if __name__ == '__main__':
    with ThreadPoolExecutor(2) as ex: list(ex.map(one, [('g6', G6), ('g56', G56)]))
