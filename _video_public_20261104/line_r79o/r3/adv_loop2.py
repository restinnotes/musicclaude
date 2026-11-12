"""11-11 夜 I05 判 L34 六套方向不成立（打转仍排第一，线砍到三分之一也一样）→ 回 I02 第二轮。
在 adv_loop.py 的材料上加：L34 六套结果、主持人两个假设（Center 是静态两极张力；按段生成逼每段一次心理变化）、相关教训。
python r3/adv_loop2.py → r3/s24/adv_loop2_{g6|g56}.json；提示词落到 _thread_evo_20261019/schemes/L35_{j}{n}_{层}.txt
"""
import json, re, sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import adv_loop as A
from adv_loop import S, SCH, PUB, rd, call, parse, G6, G56, prompt_lint, NEED, lines_text

ASK2 = A.ASK.replace('【请回答】', '{L34}\n\n【请回答】').replace(
    '2. 方案：你一个人出三套', '2. 方案：先逐条判断上面两个假设成不成立（写进 diagnosis）。然后你一个人出三套').replace(
    '至少一套不只是“在提示词里要求不打转”。', '至少一套不只是“在提示词里要求不打转”。不要重复上一批（L34）六套已经试过的机制；如果你认为主持人的假设成立，至少一套按它来写。')


def one(jm):
    j, model = jm; p = S/f'adv_loop2_{j}.json'
    if not p.exists():
        rt = lambda f: (SCH/f).read_text(encoding='utf-8')
        msg = (ASK2.replace('{L34}', (S/'l34_evidence.txt').read_text(encoding='utf-8'))
               .replace('{STD}', (PUB/'大众版标准.md').read_text(encoding='utf-8')).replace('{A1}', rt('Q6_A1.txt')).replace('{A2}', rt('Q6_A2.txt'))
               .replace('{A4}', rt('Q15_A4.txt')).replace('{A4L32}', rt('L32_g6_A4b.txt')).replace('{WRITE}', (S/'prompt_K28b.txt').read_text(encoding='utf-8'))
               .replace('{LINES}', lines_text()).replace('{LOOP}', (S/'loop_evidence.txt').read_text(encoding='utf-8')))
        print(j, '材料', len(msg), '字', flush=True)
        r = None
        for k in range(3):
            try: r = parse(call(f'advloop2_{j}' + ('' if not k else f'_r{k}'), msg, model, 'gpt3s', 'dag-advisor')); assert len(r.get('schemes') or []) >= 2; break
            except Exception as ex: print('不合格', j, repr(ex)[:150], flush=True); r = None
        if not r: return
        p.write_text(json.dumps(r, ensure_ascii=False, indent=1), encoding='utf-8')
    r = rd(p); print('====', j, '诊断：', r.get('diagnosis')); print('冲突：', json.dumps(r.get('conflict'), ensure_ascii=False))
    for n, sc in enumerate(r.get('schemes') or [], 1):
        print(f'-- {j}{n} {sc.get("name")}｜{sc.get("layers")}｜假设：{sc.get("hypothesis")}')
        for k, v in (sc.get('prompts') or {}).items():
            if v and v.strip().strip('“”"') != '不改':
                (SCH/f'L35_{j}{n}_{k}.txt').write_text(v, encoding='utf-8')
                h = prompt_lint.find(re.sub(r'\{[A-Z_]+\}', '', v))
                print(f'   {k}：{len(v)} 字｜泛化检查 {h or "过"}｜缺占位符 {[x for x in NEED.get(k, []) if x not in v] or "无"}')


if __name__ == '__main__':
    with ThreadPoolExecutor(2) as ex: list(ex.map(one, [('g6', G6), ('g56', G56)]))
