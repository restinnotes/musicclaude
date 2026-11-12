"""11-10 局部修补（碎块格式）：顾问给的修补提示词，只改被点名的块，其余照抄。被点名的问题 = 绝对验收第四版两位评委的中等以上问题 + 走样（每位评委报的都给）。
输出过 fragwrite 的机械检查，不过就退回重写（最多 3 次）。
python r3/fragrepair.py NEW 来源TAG 提示词文件 [g6|g56]
"""
import json, os, re, sys, glob
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1])); sys.path.insert(0, str(Path(__file__).resolve().parent))
import prompt_lint
from pub24 import S, rd, wr, call, parse, G6, G56, WORKS, to_script
import blend, fragwrite
sys.stdout.reconfigure(encoding='utf-8')
NL = chr(10)


def issues(w, tag):
    out = []
    for j in ('g6', 'g56'):
        p = S/f'openA4_{w}_{j}_{tag}_run1.json'
        if p.exists():
            r = rd(p)
            for s in r.get('screens') or []:
                for x in s.get('issues') or []:
                    if x.get('severity') in ('中等', '严重'): out.append(f"- {s.get('sec')}（标准 {x.get('std')}）「{x.get('quote', '')}」：{x.get('why', '')}")
            for x in r.get('whole') or []:
                if x.get('severity') in ('中等', '严重'): out.append(f"- 全曲（标准 {x.get('std')}）「{x.get('quote', '')}」：{x.get('why', '')}")
        p = S/f'faith_{w}_{j}_{tag}.json'
        if p.exists():
            for x in rd(p).get('issues') or []:
                out.append(f"- {x.get('sec')}（意思走样）屏幕「{x.get('screen', '')}」←原料「{x.get('source', '')}」：{x.get('why', '')}")
    us = {u['uid']: u for u in rd(S/f'units_{w}.json')}; votes = {}
    for j in ('g6', 'g56'):
        p = S/f'cov3_{w}_{j}_{tag}.json'
        if p.exists():
            for x in rd(p).get('items') or []: votes.setdefault(x['uid'], []).append(x.get('verdict'))
    for u, v in votes.items():   # 11-10：覆盖对 w23 的硬检查，幻想不够；确认丢了的核心内容也让修补补回
        if us.get(u, {}).get('tier') == '核心' and sum(1 for x in v if x == '没有')*2 > len(v): out.append(f"- {us[u]['sec']}（内容丢了，要补回，可以补成小块或旁注）原料：{us[u]['what']}")
    return NL.join(out)


def one(a):
    w, new, src, pf, who = a; p = S/f'screen_{w}_{new}.json'
    if p.exists(): return True
    tpl = (S/pf).read_text(encoding='utf-8')
    prompt_lint.lint(re.sub(r'\{(SCREEN|ISSUES|BUDGET|DAGSTD|FINAL|BEADS)\}', '', tpl), pf)
    cur = sorted(glob.glob(str(S/f'frag_{w}_{src}_try*.json')))[-1]
    msg = (tpl.replace('{SCREEN}', Path(cur).read_text(encoding='utf-8')).replace('{ISSUES}', issues(w, src)).replace('{DAGSTD}', blend.DAGSTD)
           .replace('{BUDGET}', blend.budget(w)).replace('{FINAL}', blend.lines_map(w)).replace('{BEADS}', blend.beads_text(w)))
    fb = ''
    for k in range(4):
        ans = call(os.environ.get('PUB_BL_PFX', 'frep') + f'_{w}_{new}' + ('' if not k else f'_r{k}'), msg + fb, G56 if who == 'g56' else G6, 'gpt3s', 'public24-frep')
        try:
            r = parse(ans); scr, bad, miss = fragwrite.convert(w, r)
            (S/f'frag_{w}_{new}_try{k}.json').write_text(json.dumps(r, ensure_ascii=False, indent=1), encoding='utf-8')
            if bad and k < 3:
                print(w, new, f'第 {k+1} 次机械检查没过 {len(bad)} 处，交回', flush=True)
                fb = '\n\n【你上一次的输出没过机械检查，下面这些地方要改；其余照原要求，整份重新输出】\n' + '\n'.join(bad[:40]); continue
            wr(p, scr); to_script(w, new, scr)
            old = rd(S/f'screen_{w}_{src}.json'); chg = sum(1 for s0, s1 in zip(old['sections'], scr['sections']) for x0, x1 in zip(s0['rows'], s1['rows']) if x0 != x1)
            print(w, new, f'修补完成；剩余机械问题 {len(bad)}；和来源比约 {chg} 行有变化；没用到的珠子 {miss}', flush=True); return True
        except Exception as ex: print('不合格', w, new, repr(ex)[:200], flush=True)
    return False


if __name__ == '__main__':
    new, src, pf = sys.argv[1:4]; who = sys.argv[4] if len(sys.argv) > 4 else 'g6'
    with ThreadPoolExecutor(2) as ex: print(list(ex.map(one, [(w, new, src, pf, who) for w in WORKS])), flush=True)
