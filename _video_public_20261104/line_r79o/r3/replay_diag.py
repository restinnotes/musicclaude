"""11-12 回放测试（Fable 审查第三节）：把 11-11 晚第一轮出方案时的材料原样、改用新的诊断提问模板（i02_诊断提问模板.txt）重问两位顾问，
看它们会不会自己提出正面对照、放开设定，把哪个假设排第一；和我当时实际做的（CTRLf/CTRLe/拆开的 CTRLn）比。
python r3/replay_diag.py → r3/s24/replay_diag_{g6|g56}.json"""
import json, sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import adv_loop as A
from adv_loop import S, SCH, PUB, rd, call, parse, G6, G56, lines_text
sys.stdout.reconfigure(encoding='utf-8')
TPL = (Path(__file__).parent/'i02_诊断提问模板.txt').read_text(encoding='utf-8')
ASK = A.ASK.split('【请回答】')[0].replace('【约束（现在的设定）】', '【现在的设定（谁定的、能不能放开见下；你可以建议放开任何一条，属于用户的由主持人去问）】') \
      + TPL[TPL.index('请回答：'):] + '\n回答时请不要进行联网搜索。\n\n' + A.ASK[A.ASK.index('【大众版标准】'):]


def one(jm):
    j, m = jm; p = S/f'replay_diag_{j}.json'
    if not p.exists():
        rt = lambda f: (SCH/f).read_text(encoding='utf-8')
        msg = (ASK.replace('{STD}', (PUB/'大众版标准.md').read_text(encoding='utf-8')).replace('{A1}', rt('Q6_A1.txt')).replace('{A2}', rt('Q6_A2.txt'))
               .replace('{A4}', rt('Q15_A4.txt')).replace('{A4L32}', rt('L32_g6_A4b.txt')).replace('{WRITE}', (S/'prompt_K28b.txt').read_text(encoding='utf-8'))
               .replace('{LINES}', lines_text()).replace('{LOOP}', (S/'loop_evidence.txt').read_text(encoding='utf-8')))
        r = parse(call(f'replaydiag_{j}', msg, m, 'gpt3s', 'dag-advisor')); p.write_text(json.dumps(r, ensure_ascii=False, indent=1), encoding='utf-8')
    r = rd(p); print('====', j, '最怀疑：', r.get('most_suspect'))
    for h in r.get('hypotheses') or []: print('  -', h.get('cause', '')[:120], '｜验证：', h.get('cheapest_test', '')[:160])
    print('  设定冲突：', json.dumps(r.get('setting_conflict'), ensure_ascii=False)[:400])


if __name__ == '__main__':
    with ThreadPoolExecutor(2) as ex: list(ex.map(one, [('g6', G6), ('g56', G56)]))
