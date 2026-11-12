"""11-12 凌晨 I02 第三轮（试验，未经用户确认）：I11 正面对照 CTRLf/CTRLe 证明打转根在“无外部事件”设定，已提 I16（每首 3–5 件和音乐相称的事）。
这一轮按放宽后的设定，请两位顾问把 CTRLe 的做法写成写线流水线的正式提示词，并治 CTRLe 剩下的问题。不进主线，等用户定。
python r3/adv_loop3.py → r3/s24/adv_loop3_{g6|g56}.json；提示词落到 _thread_evo_20261019/schemes/L37_{j}{n}_{层}.txt
"""
import json, re, sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import adv_loop as A
from adv_loop import S, SCH, PUB, rd, call, parse, G6, G56, prompt_lint, NEED, lines_text

OLD_C = '- 不编外加的事件、前史、对白、物件来推动故事（允许一个从头到尾不变的轻处境加小动作）。'
NEW_C = ('- 【这一轮按放宽后的设定做试验】每首允许 3–5 件真实发生的事：只放在音乐情绪真正转折的段落；分量和那段音乐相称（会改变关系或人物处境，不是流水账日常）；'
         '从 Center 推出来，不加新的重要人物；前后因果有铺垫。其余段落不加事件，写这些事带来的变化和体验，每段往前一点、不回头重新挣扎。不编前史、不编大段对白。')
assert OLD_C in A.ASK
ASK2 = A.ASK.replace(OLD_C, NEW_C).replace('【请回答】', '{L34}\n\n【请回答】').replace(
    '2. 方案：你一个人出三套', '2. 方案：这一轮的任务是把 CTRLe 的做法变成写线流水线（A1 骨架定转折段和事件、A2 选路、A4 写线）的正式提示词，并治 CTRLe 剩下的问题（人话、事件铺垫、结尾讲道理、高潮段的事件分量）。你一个人出三套').replace(
    '至少一套不只是“在提示词里要求不打转”。', '三套在“事件在哪一层定、怎么保证分量和铺垫、人话靠什么”上互为独立。WRITE 一律写“不改”。')
for k in ('放宽后的设定', '{L34}', 'CTRLe 的做法', 'WRITE 一律'): assert k in ASK2, k


def one(jm):
    j, model = jm; p = S/f'adv_loop3_{j}.json'
    if not p.exists():
        rt = lambda f: (SCH/f).read_text(encoding='utf-8')
        msg = (ASK2.replace('{L34}', (S/'ctrl_evidence.txt').read_text(encoding='utf-8'))
               .replace('{STD}', (PUB/'大众版标准.md').read_text(encoding='utf-8')).replace('{A1}', rt('Q6_A1.txt')).replace('{A2}', rt('Q6_A2.txt'))
               .replace('{A4}', rt('Q15_A4.txt')).replace('{A4L32}', rt('L32_g6_A4b.txt')).replace('{WRITE}', (S/'prompt_K28b.txt').read_text(encoding='utf-8'))
               .replace('{LINES}', lines_text()).replace('{LOOP}', (S/'loop_evidence.txt').read_text(encoding='utf-8')))
        print(j, '材料', len(msg), '字', flush=True)
        r = None
        for k in range(3):
            try: r = parse(call(f'advloop3_{j}' + ('' if not k else f'_r{k}'), msg, model, 'gpt3s', 'dag-advisor')); assert len(r.get('schemes') or []) >= 2; break
            except Exception as ex: print('不合格', j, repr(ex)[:150], flush=True); r = None
        if not r: return
        p.write_text(json.dumps(r, ensure_ascii=False, indent=1), encoding='utf-8')
    r = rd(p); print('====', j, '诊断：', r.get('diagnosis')); print('冲突：', json.dumps(r.get('conflict'), ensure_ascii=False))
    for n, sc in enumerate(r.get('schemes') or [], 1):
        print(f'-- {j}{n} {sc.get("name")}｜{sc.get("layers")}｜假设：{sc.get("hypothesis")}')
        for k, v in (sc.get('prompts') or {}).items():
            if v and v.strip().strip('“”"') != '不改':
                (SCH/f'L37_{j}{n}_{k}.txt').write_text(v, encoding='utf-8')
                h = prompt_lint.find(re.sub(r'\{[A-Z_]+\}', '', v))
                print(f'   {k}：{len(v)} 字｜泛化检查 {h or "过"}｜缺占位符 {[x for x in NEED.get(k, []) if x not in v] or "无"}')


if __name__ == '__main__':
    with ThreadPoolExecutor(2) as ex: list(ex.map(one, [('g6', G6), ('g56', G56)]))
