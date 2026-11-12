"""11-11 I02（DAG 写线层）：开放评审三位在 K28b 和四套事后改线（L30f–i）上都把“原地打转”列为头号问题；事后改线改不动（旧教训：结构要在写线那一步修）。
两位顾问各自独立：诊断打转从写线流水线的哪一步来（A1 经历骨架、A2 选路、A4 写线），给改后的完整提示词。
python r3/adv_dagline.py → r3/s24/adv_dagline_{g6|g56}.json；提示词落到 _thread_evo_20261019/schemes/L31_{j}_{A1|A2|A4}.txt
"""
import json, os, sys, re
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
os.environ.setdefault('PUB_SRC', 'r2e')
import prompt_lint
from pub24 import S, R2, rd, call, parse, G6, G56
sys.stdout.reconfigure(encoding='utf-8')
NL = chr(10); SCH = Path('D:/musicclaude/_thread_evo_20261019/schemes')

ASK = """你是顾问。我们用一条大模型流水线为一首钢琴曲写一条“线”：一个人在这首曲子里经历的一件事，从全曲的核心处境（Center）长出来，按音乐分段，每段 2–4 条。线之后会和听众的感受（珠子）一起做成给普通观众边听边看的视频屏幕稿。

【问题】给不看标准的开放评审（三位、两首）读成品，“原地打转”在每一版都是头号问题：人物在几种状态之间一轮轮重来（想靠近→怕→安心→又怕；怀念→委屈→怀疑离开→怕孤单→又怀念），读到中段就能猜到下一屏；同一个领悟、同一个决定被当成新的反复出现。
我们试过在写好的线上事后改（四套：去环、把处境和认识边界写清、两位顾问各写两套），端到端都没治住，开放评审里打转仍排第一第二。以往实验也有同样的结论：事后改写改不动结构，同一个两难反复说要在写线那一步修。

写线流水线现在是：A1 经历骨架（不看珠子，写 3 条这个人的经历路线）→ A2 选路（不看珠子，给 3 条路线排序）→ A3 体验性质（把珠子去掉画面情节，只留体验性质）→ A4 写线（看路线、宏观评审结果和体验性质，一次写完）。下面是三份提示词原文、两首现在的线和 Center、开放评审关于打转的原话。

约束（不能改）：不编外加的事件、前史、对白、物件来推动故事（“没有外部动作”不算缺点；允许一个从头到尾不变的轻处境加小动作）；写线时不看珠子原文；音乐分段不变；Center 不变；两首用同一套提示词；提示词里不放具体作品的内容或例子，写“这首钢琴曲”。

【请回答】
1. 诊断：打转主要是哪一步造成的？（A1 的路线本身就在打转？A2 的排序没惩罚打转？A4 写的时候把每段写成同一个两难的又一次出现？音乐分段多、情绪起伏多，而“一件事”太窄、撑不起这么多段？）引用提示词原文和线的原文说明。
2. 改法：给改后的完整提示词（只改你认为该改的那几步，其余写“不改”）。改法要能让每一段都给这件事增加真正新的东西（新的认识、新的所求、新的代价、新的选择），而不是同一个两难换说法；同时不编外部事件。
3. 怎么验证：改完重跑两首写线，怎么判断打转真的少了（除了开放评审还能看什么）。

只输出 JSON：{"diagnosis":"…","prompts":{"A1":"完整提示词或“不改”","A2":"…","A4":"…"},"keep_placeholders":"说明你保留了哪些占位符","verify":"…"}。占位符必须原样保留：A1 有 {NAME} {SECTIONS} {K} {CENTER}；A2 的候选路线会附在提示词末尾；A4 有 {SECTIONS} {ROUTES} {TARGETS} {CENTER}。回答时请不要进行联网搜索。

【A1 经历骨架 原文】
{A1}

【A2 选路 原文】
{A2}

【A4 写线 原文】
{A4}

【两首现在的线和 Center】
{LINES}

【开放评审关于打转的原话】
{LOOP}
"""


def lines_text():
    out = []
    for w in ('op60', 'op61'):
        src = rd(R2/f'{w}_src.json'); out.append(f"=== {w}  Center：{src['center']}")
        for s in src['sections']: out.append(f"### {s['sec']}" + NL + NL.join(f"- {l['id']}：{l['text']}" for l in s['lines']))
    return NL.join(out)


def one(jm):
    j, model = jm; p = S/f'adv_dagline_{j}.json'
    if not p.exists():
        msg = (ASK.replace('{A1}', (SCH/'Q6_A1.txt').read_text(encoding='utf-8')).replace('{A2}', (SCH/'Q6_A2.txt').read_text(encoding='utf-8'))
               .replace('{A4}', (SCH/'Q15_A4.txt').read_text(encoding='utf-8')).replace('{LINES}', lines_text()).replace('{LOOP}', (S/'loop_evidence.txt').read_text(encoding='utf-8')))
        r = None
        for k in range(3):
            try: r = parse(call(f'advdagline_{j}' + ('' if not k else f'_r{k}'), msg, model, 'gpt3s', 'dag-advisor')); assert r.get('prompts'); break
            except Exception as ex: print('不合格', j, repr(ex)[:150], flush=True); r = None
        if not r: return
        p.write_text(json.dumps(r, ensure_ascii=False, indent=1), encoding='utf-8')
    r = rd(p); print('====', j, '诊断：', r.get('diagnosis')); print('验证：', r.get('verify'))
    for k, v in (r.get('prompts') or {}).items():
        if v and v.strip() not in ('不改', '“不改”'):
            f = SCH/f'L31_{j}_{k}.txt'; f.write_text(v, encoding='utf-8')
            h = prompt_lint.find(re.sub(r'\{(NAME|SECTIONS|K|CENTER|ROUTES|TARGETS|SEGMENTS|BEADS_TEXT)\}', '', v))
            need = {'A1': ['{NAME}', '{SECTIONS}', '{K}', '{CENTER}'], 'A4': ['{SECTIONS}', '{ROUTES}', '{TARGETS}', '{CENTER}'], 'A2': []}.get(k, [])
            print(f'  {k}：{len(v)} 字｜泛化检查 {h or "过"}｜缺占位符 {[x for x in need if x not in v] or "无"}')
        else: print(f'  {k}：不改')


FB = """你上一轮给的改法已经两首同跑（写线后不打磨，直接用同一份屏幕稿提示词做成成品，和旧写线提示词同样不打磨的对照比）。结果：
{RESULT}

请判断：这条路要继续（给改过的完整提示词，格式同上一轮），还是换方向（说清换什么）。特别回答：怎样在保住“每段真有新东西”的同时，让线读起来像一个人平常想事、说话，而不是心理分析；“同一个两难反复辩”怎样避免。只输出 JSON，格式同上一轮，另加 "continue": true/false。

==== 上一轮的问题和你的回答（原样）====
{PREV}
"""


def back(jm, result):
    j, model = jm; p = S/f'adv_dagline2_{j}.json'
    if p.exists(): return
    prev = (S/f'adv_dagline_{j}.json').read_text(encoding='utf-8')
    msg = FB.replace('{RESULT}', result[j]).replace('{PREV}', ASK[:2500] + NL + '……（原提示词、线和证据略）' + NL + prev)
    for k in range(3):
        try: r = parse(call(f'advdagline2_{j}' + ('' if not k else f'_r{k}'), msg, model, 'gpt3s', 'dag-advisor')); assert r.get('prompts'); p.write_text(json.dumps(r, ensure_ascii=False, indent=1), encoding='utf-8'); return
        except Exception as ex: print('不合格', j, repr(ex)[:150], flush=True)


def back3():
    j, model = 'g6', G6; p = S/'adv_dagline3_g6.json'
    if not p.exists():
        prev = (S/'adv_dagline2_g6.json').read_text(encoding='utf-8')
        res = (S/'dagline_result2.txt').read_text(encoding='utf-8')
        msg = FB.replace('{RESULT}', res).replace('{PREV}', ASK[:2500] + NL + '……（原提示词、线和证据略）' + NL + prev) + NL + '另：这一轮的输出里请把 prompts 写全 A1、A2、A4（不改的写“不改”）。'
        for k in range(3):
            try: r = parse(call(f'advdagline3_g6' + ('' if not k else f'_r{k}'), msg, model, 'gpt3s', 'dag-advisor')); assert r.get('prompts'); p.write_text(json.dumps(r, ensure_ascii=False, indent=1), encoding='utf-8'); break
            except Exception as ex: print('不合格', repr(ex)[:150], flush=True)
    r = rd(p); print('====', '继续' if r.get('continue') else '换方向', '｜', str(r.get('diagnosis'))[:1500])
    for k, v in (r.get('prompts') or {}).items():
        if v and v.strip() not in ('不改', '“不改”'): (SCH/f'L33_g6_{k}.txt').write_text(v, encoding='utf-8'); print('  ', k, len(v), '字')


if __name__ == '__main__' and len(sys.argv) > 1 and sys.argv[1] == 'back3': back3(); sys.exit()

if __name__ == '__main__' and len(sys.argv) > 1 and sys.argv[1] == 'back':
    common = open(sys.argv[2], encoding='utf-8').read()
    res = {'g6': common + NL + '你的方案（A1、A2、A4 都改）：两首的 A2 都判三条路线全不过、A4 交白卷；加一轮“按淘汰理由重写骨架再审”后仍全不过，没有产出。', 'g56': common + NL + '你的方案（A2、A4 改）：第一次船歌产出、幻想三条全不过；加一轮重写后两首都产出（船歌 1493 字、幻想 1742 字，对照 1882、2056 字）。成品结果见上。'}
    with ThreadPoolExecutor(2) as ex: list(ex.map(lambda jm: back(jm, res), [('g6', G6), ('g56', G56)]))
    for j in ('g6', 'g56'):
        p = S/f'adv_dagline2_{j}.json'
        if p.exists():
            r = rd(p); print('====', j, '继续' if r.get('continue') else '换方向', '｜', str(r.get('diagnosis'))[:600])
            for k, v in (r.get('prompts') or {}).items():
                if v and v.strip() not in ('不改', '“不改”'): (SCH/f'L32_{j}_{k}.txt').write_text(v, encoding='utf-8'); print('  ', k, len(v), '字')
    sys.exit()

if __name__ == '__main__':
    with ThreadPoolExecutor(2) as ex: list(ex.map(one, [('g6', G6), ('g56', G56)]))
