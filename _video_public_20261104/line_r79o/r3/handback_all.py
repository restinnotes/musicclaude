"""11-12 用户：“一个评委提出问题并说可能解法 然后你修完 然后再评定完 就直接给他丢掉了吗……我之前说要给他继续试 除非这种解法被认为是不可能修成功”。
把 L34、L35 两批 12 套方案的结果各自交回提出它的顾问（并行），由提出者判断：这条路不可能修成功（写明为什么），还是改哪里（给改后的完整提示词）。
设定按方案提出时的（不加外部事件）；放宽事件的方向另由 L37 试。
python r3/handback_all.py → r3/s24/hb2_{批}{ID}.json；改后的提示词落到 _thread_evo_20261019/schemes/L38_{批}{ID}_{层}.txt
"""
import glob, json, os, re, sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
os.environ.setdefault('PUB_SRC', 'r2e')
import prompt_lint
from pub24 import S, rd, call, parse, G6, G56
sys.stdout.reconfigure(encoding='utf-8')
SCH = Path('D:/musicclaude/_thread_evo_20261019/schemes'); R3 = Path(__file__).resolve().parent; HERE = R3.parent
NEED = {'A1': ['{NAME}', '{SECTIONS}', '{K}', '{CENTER}'], 'A4': ['{SECTIONS}', '{ROUTES}', '{TARGETS}', '{CENTER}'], 'A2': [],
        'WRITE': ['{BUDGET}', '{DAGSTD}', '{FINAL}', '{BEADS}', '{BASE}']}

ASK = """你是顾问。你之前出的一套方案（治“原地打转”，原提示词附在最后）已经两首同跑、测完。用户的规矩是：方案没成，交回提出者；除非提出者判断这条路不可能修成功，否则继续改。现在交回给你。

【这套方案】{NAME}：{HYP}

【结果】（端到端：你的提示词写线 → 换进同一份原料 → 同一份屏幕稿写法 → 不打磨直接测。对照：旧提示词不打磨 中等 88；当前主线 K28b 打磨过多轮 中等 26。中等 = 绝对验收两首、两位评委合计）
{RES}

【开放评审（三位，不给标准，只找问题）每份的前三条】
{OPEN}

【你这套写出的线（船歌）】
{LINE}

【全局背景】两批共 12 套改写线的方案（Center 改成单向弧、先写完整经历再分段、固定处境、骨架记账、线砍到三分之一、去掉逐段体验性质……）都还在打转。正面对照显示：允许几件真实发生的事以后打转消失——但这一轮仍按你提方案时的设定（不加外部事件），不要靠加事件来解决；加事件的方向另有一批在试。

【请判断】
- 这条路不可能修成功：写明为什么（根因是什么、为什么改提示词也绕不过去）。
- 还能修：说清上次为什么没成（引结果），只改哪一处，给改后的完整提示词（只给要改的层，不改的层写“不改”）。已经好过对照的指标不许退。

只输出 JSON：{"verdict":"不可能|改","why":"…","change":"改了什么","prompts":{"A1":"完整提示词或“不改”","A2":"…","A4":"…","WRITE":"…"}}
占位符必须原样保留：A1 有 {NAME} {SECTIONS} {K} {CENTER}；A2 的候选路线会附在末尾；A4 有 {SECTIONS} {ROUTES} {TARGETS} {CENTER}；WRITE 有 {BUDGET} {DAGSTD} {FINAL} {BEADS} {BASE}，输出格式不能变。提示词里不放具体作品的内容或例子。回答时请不要进行联网搜索。

【你原来的提示词】
{PROMPTS}
"""


def scheme_info(b, i):
    adv = rd(S/f'adv_loop{"" if b == "34" else "2"}_{"g6" if i.startswith("g6") else "g56"}.json')
    sc = (adv.get('schemes') or [])[int(i[-1]) - 1]
    return sc.get('name', ''), sc.get('hypothesis', '')


def results(b, i):
    out = []
    for tag in [f'g68L{b}{i}'] + [x for x in (f'g68L{b}{i}b', f'g6L{b}{i}') if (S/f'screen_op60_{x}.json').exists()]:
        for lg in glob.glob(str(R3/f'run_L{b}{i}*.log')) + glob.glob(str(R3/f'run_L{b}_{i}*.log')) + [str(R3/f'pipe_{tag}test.log')]:
            if not os.path.exists(lg): continue
            for l in open(lg, encoding='utf-8', errors='ignore'):
                if (f' {tag} ' in l or f'v5b{tag} ' in l) and re.match(r'^(绝对验收5b|盲比5|op6\d .*大块)', l): out.append(l.strip()[:260])
    return '\n'.join(dict.fromkeys(out)) + '\n（盲比日志里 A 是锚点 K11g，B 是你这套；human=人话、core=核心、big=大字）'


def opens(b, i):
    out = []
    for op in ('op60', 'op61'):
        for j in ('g6', 'g56', 'argon'):
            p = S/f'openF3_{op}_{j}_g68L{b}{i}.json'
            if p.exists():
                out.append(f'- {op} {j}：' + ' ｜ '.join(x['problem'][:150].replace('\n', ' ') for x in rd(p)['issues'][:3]))
    return '\n'.join(out)


def line(b, i):
    p = HERE/f'r2L{b}{i}'/'op60_src.json'
    if not p.exists(): return '（这套只改屏幕稿，线是原来的）'
    return '\n'.join(f"{s['sec']} " + ' / '.join(l['text'] for l in s['lines']) for s in rd(p)['sections'])


def one(bi):
    b, i = bi; p = S/f'hb2_{b}{i}.json'
    if not p.exists():
        files = {k: SCH/f'L{b}_{i}_{k}.txt' for k in ('A1', 'A2', 'A4', 'WRITE')}
        pr = '\n\n'.join(f'【{k}】\n' + f.read_text(encoding='utf-8') for k, f in files.items() if f.exists())
        name, hyp = scheme_info(b, i)
        msg = (ASK.replace('{NAME}', name).replace('{HYP}', hyp).replace('{RES}', results(b, i)).replace('{OPEN}', opens(b, i))
               .replace('{LINE}', line(b, i)).replace('{PROMPTS}', pr))
        model = G6 if i.startswith('g6') else G56
        r = None
        for k in range(3):
            try: r = parse(call(f'hb2_{b}{i}' + ('' if not k else f'_r{k}'), msg, model, 'gpt3s', 'dag-advisor')); assert r.get('verdict'); break
            except Exception as ex: print('不合格', b, i, repr(ex)[:150], flush=True); r = None
        if not r: return
        p.write_text(json.dumps(r, ensure_ascii=False, indent=1), encoding='utf-8')
    r = rd(p); print(f'==== L{b}{i}：{r.get("verdict")}｜{(r.get("why") or "")[:300]}｜改：{(r.get("change") or "")[:200]}', flush=True)
    if r.get('verdict') == '改':
        for k, v in (r.get('prompts') or {}).items():
            if v and v.strip().strip('“”"') != '不改':
                (SCH/f'L38_{b}{i}_{k}.txt').write_text(v, encoding='utf-8')
                h = prompt_lint.find(re.sub(r'\{[A-Z_]+\}', '', v))
                print(f'   {k}：{len(v)} 字｜泛化检查 {h or "过"}｜缺占位符 {[x for x in NEED.get(k, []) if x not in v] or "无"}', flush=True)


if __name__ == '__main__':
    todo = [(b, i) for b in ('34', '35') for i in ('g61', 'g62', 'g63', 'g561', 'g562', 'g563')]
    with ThreadPoolExecutor(12) as ex: list(ex.map(one, todo))
