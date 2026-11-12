"""11-12 夜 I02/I03（骨架这一步）：用户：“你这个问题不能也去按照流程去走吗……我们现在就先对这个局部返回来去修改”。
问题不是开放评审先报的，是定位出来的（准则 I02 四项）：线的每一段缺只属于这一段的理由，根在骨架。两位顾问各自独立：先诊断，再各出两套骨架改法（可连带改选路、写线）。
python r3/adv_sk.py → r3/s24/adv_sk_{g6|g56}.json；提示词落到 schemes/L42_{j}{n}_{A1|A2|A4}.txt 和 L42{j}{n}.json"""
import json, os, re, sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1])); os.environ.setdefault('PUB_SRC', 'r2e')
import prompt_lint
from pub24 import S, rd, call, parse, G6, G56
sys.stdout.reconfigure(encoding='utf-8')
SCH = Path('D:/musicclaude/_thread_evo_20261019/schemes'); RUNS = SCH.parent/'runs'
rt = lambda f: (SCH/f).read_text(encoding='utf-8')
ASK = (Path(__file__).parent/'adv_sk_ask.txt').read_text(encoding='utf-8')


def a3ex():
    r = parse((RUNS/'scL34g61_op60_A3'/'output.txt').read_text(encoding='utf-8')); return json.dumps(r['sections'][6], ensure_ascii=False, indent=1)[:2600]


def skex():
    r = parse((RUNS/'scL40sk_op60_A1'/'output.txt').read_text(encoding='utf-8')); x = (r.get('routes') or r.get('items'))[0]
    return '这件事：' + str(x.get('situation')) + '\n' + '\n'.join(f"{s['sec'][:3]}｜{s.get('delta_type')}｜不同：{s.get('flavor_diff')}｜为什么：{s.get('why_now')}｜说明不了：{s.get('unexplained')}" for s in x['segments'] if s['sec'][:3] in ('S02', 'S06', 'S07', 'S11', 'S13'))


def lineex():
    out = []
    for t, nm in (('r2e', '主线'), ('r2L34g61', 'L34g61'), ('r2L40sk', 'L40sk')):
        d = rd(Path(__file__).resolve().parents[1]/t/'op60_src.json')
        out += [f"{nm} {s['sec']}：" + ' / '.join(l['text'] for l in s['lines']) for s in d['sections'] if s['sec'] in ('S06', 'S07')]
    return '\n'.join(out)


def one(jm):
    j, model = jm; p = S/f'adv_sk_{j}.json'
    if not p.exists():
        msg = ASK.replace('{A1}', rt('L34_g61_A1.txt')).replace('{A2}', rt('L34_g61_A2.txt')).replace('{A4}', rt('L34_g61_A4b.txt')).replace('{A3EX}', a3ex()).replace('{SKEX}', skex()).replace('{LINEEX}', lineex())
        r = None
        for k in range(3):
            try:
                r = parse(call(f'adv_sk_{j}' + ('' if not k else f'_r{k}'), msg, model, 'gpt3s', 'dag-advisor'))
                assert len(r['schemes']) >= 1 and all('{SECTIONS}' in s['A1'] and '{CENTER}' in s['A1'] for s in r['schemes']); break
            except Exception as ex: print('不合格', j, repr(ex)[:200], flush=True); r = None
        if not r: return
        p.write_text(json.dumps(r, ensure_ascii=False, indent=1), encoding='utf-8')
    r = rd(p); print(f'\n===== {j} 最怀疑：', r.get('most_suspect'), '\n设定冲突：', json.dumps(r.get('setting_conflict'), ensure_ascii=False), flush=True)
    for h in r.get('hypotheses', []): print('  假设：', h.get('cause', '')[:260])
    base = json.loads((SCH/'L34g61.json').read_text(encoding='utf-8'))
    for n, s in enumerate(r['schemes'], 1):
        tag = f'L42{j}{n}'; d = json.loads(json.dumps(base)); d['name'] = tag; d['note'] = f"{tag}：11-12 夜 adv_sk（{s.get('name')}）"; lint = []
        for st in d['steps']:
            sid = st['id']
            if sid == 'A3': st.pop('after', None); continue
            t = s.get(sid) or '不改'
            if sid == 'A4' and t.strip() != '不改' and not all(k in t for k in ('{SECTIONS}', '{CENTER}', '{ROUTES}', '{TARGETS}')): print('  ！', tag, 'A4 缺占位符，沿用旧的'); t = '不改'
            if t.strip() == '不改': continue
            f = f'L42_{j}{n}_{sid}.txt'; (SCH/f).write_text(t, encoding='utf-8'); st['prompt_file'] = f
            lint += prompt_lint.find(re.sub(r'\{[A-Z_]+\}', '', t)) or []
            if sid == 'A1':
                if '{TARGETS}' in t: st['replace']['{TARGETS}'] = 'step:A3'
                else: st['replace'].pop('{TARGETS}', None)
        (SCH/f'{tag}.json').write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding='utf-8')
        print(f"  方案 {tag}：{s.get('name')}｜搜索 {s.get('search')}｜改了 {[k for k in ('A1', 'A2', 'A4') if (s.get(k) or '不改').strip() != '不改']}｜泛化检查 {lint or '过'}\n     治：{str(s.get('fixes'))[:200]}\n     险：{str(s.get('risks'))[:200]}", flush=True)


if __name__ == '__main__':
    with ThreadPoolExecutor(2) as ex: list(ex.map(one, [('g6', G6), ('g56', G56)]))
