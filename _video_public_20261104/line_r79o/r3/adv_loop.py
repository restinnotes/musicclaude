"""11-11 晚 I02 换方向（自动绊线：写线层改了 5 套、3 轮，最好版本的中等问题没减少；L33a 是 GPT-6 同一方案第 3 次，到上限）。
证据：17 个版本（含用户认可过的 K11g、当前最好 K28b）两首、三位开放评审，“原地打转”每一版都排前三，多数第一。
两位顾问各自独立：根因；每人三套互为独立假设的方案（可改写线 A1/A2/A4、也可改屏幕稿写法，可删层并层）；这是不是设定或标准本身的冲突（供 I16）。
python r3/adv_loop.py → r3/s24/adv_loop_{g6|g56}.json；提示词落到 _thread_evo_20261019/schemes/L34_{j}{n}_{层}.txt
"""
import json, os, sys, re
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
os.environ.setdefault('PUB_SRC', 'r2e')
import prompt_lint
from pub24 import S, R2, rd, call, parse, G6, G56
sys.stdout.reconfigure(encoding='utf-8')
NL = chr(10); SCH = Path('D:/musicclaude/_thread_evo_20261019/schemes'); PUB = Path('D:/musicclaude/_video_public_20261104')

ASK = """你是顾问。我们把两首钢琴曲（肖邦船歌 Op.60、幻想波兰舞曲 Op.61）做成给普通观众“边听边看”的视频屏幕稿。上游用一条大模型流水线写一条“线”：一个人在这首曲子里经历的一件事，从全曲的核心处境（Center）长出来，按音乐分段（13–14 段），每段 2–4 条；“珠子”是不同听众在这一刻的感受、画面、比喻。下游把线和珠子写成屏幕稿：大字是线的原话（只切不改，这是用户定的，因为改写会丢人话），小字是珠子。

【一直治不住的问题】
不看标准的开放评审（GPT-6、GPT-5.6、Argon 三位，两首）读成品，“原地打转”在我们做过的每一个版本里都排前三、多数排第一：人物在几种状态之间一轮轮重来（想靠近→怕失去→安心→又怕；怀念→委屈→怀疑离开→怕孤单→又怀念），同一个领悟、同一个决定被当成新的反复宣布，读到中段能猜到下一屏。共 17 个版本：
- K11g：用户看过、比较认可的一版（固定锚点）。打转排第一。
- K28b：当前最好（线经过多轮打磨，绝对验收中等问题两首合计 26 条）。打转排第一。
- K29 各套：只改屏幕稿写法。打转仍排前列。
- L30 四套：在写好的线上事后改（去环、写清处境和认识边界等）。打转仍排第一第二。
- L31–L33 五套：改写线流水线的提示词（两位顾问各自的方案，交回过两到三次）。不打磨时中等问题：旧提示词对照 88；最好的 L32a 53（“每段一样具体的新东西、两难只正面想一次、写经历不写分析”，但幻想线很薄，24 条 681 字，盲比输锚点）；要求写足以后的 L33a 86，打转重新排第一，人话、核心在盲比里 4:0 输锚点。
规律：线越厚，打转越重；线变薄，打转轻一些，但核心和人话输给锚点，观众觉得空。

【约束（现在的设定）】
- 不编外加的事件、前史、对白、物件来推动故事（允许一个从头到尾不变的轻处境加小动作）。
- 写线时不看珠子原文（只看珠子去掉画面情节后的体验性质）；音乐分段不变；Center 不变；两首用同一套提示词；提示词里不放具体作品的内容或例子，写“这首钢琴曲”。
- 大字用线的原话，只切不改。
- 大众版标准全文见下。

【请回答】
1. 根因：为什么打转在所有版本里都活下来？可能的方向（不限于）：设定本身（一件心事、没有外部事件、13–14 段每段 2–4 条，必然把同一个两难说很多遍）；音乐本身有再现，线跟着音乐回到旧状态；大字数量太多（每首约 55 块大字全是线的心理活动）；评审口径。引材料说明。
2. 方案：你一个人出三套，互为独立的假设（不是同一个想法的三种强度）。每套写：假设、改哪一层（写线 A1/A2/A4、屏幕稿写法 WRITE，可以删层、并层、整层重写）、给改后的完整提示词（不改的层写“不改”）、预期在两首上会怎样、怎么判断成没成。至少一套不只是“在提示词里要求不打转”。
3. 标准或设定冲突：你认为“不打转”和现有设定（一件核心的事、不编事件、段数、大字用线原话）或大众版标准某一条之间是否存在无法同时满足的冲突？是的话，说清是哪一条和哪一条、证据、建议怎么改、改了能解决什么；不是的话，说清怎么在现设定下同时满足。

只输出 JSON：{"diagnosis":"…","conflict":{"verdict":"是|否|部分","which":"…","evidence":"…","suggest":"…"},"schemes":[{"name":"…","hypothesis":"…","layers":"…","prompts":{"A1":"完整提示词或“不改”","A2":"…","A4":"…","WRITE":"…"},"expect":"…","check":"…"}]}
占位符必须原样保留：A1 有 {NAME} {SECTIONS} {K} {CENTER}；A2 的候选路线会附在提示词末尾；A4 有 {SECTIONS} {ROUTES} {TARGETS} {CENTER}；WRITE 有 {BUDGET} {DAGSTD} {FINAL} {BEADS} {BASE}，输出格式不能变。回答时请不要进行联网搜索。

【大众版标准】
{STD}

【A1 经历骨架 原文（旧，K28b 的线出自它和 A4，再经打磨）】
{A1}

【A2 选路 原文】
{A2}

【A4 写线 原文】
{A4}

【L32a 的 A4（最好的一次改法）】
{A4L32}

【WRITE 屏幕稿写法 原文（K28b）】
{WRITE}

【K28b 两首的线和 Center】
{LINES}

【开放评审关于打转的原话（K28b）】
{LOOP}
"""


def lines_text():
    out = []
    for w in ('op60', 'op61'):
        src = rd(R2/f'{w}_src.json'); out.append(f"=== {w}  Center：{src['center']}")
        for s in src['sections']: out.append(f"### {s['sec']}" + NL + NL.join(f"- {l['id']}：{l['text']}" for l in s['lines']))
    return NL.join(out)


NEED = {'A1': ['{NAME}', '{SECTIONS}', '{K}', '{CENTER}'], 'A4': ['{SECTIONS}', '{ROUTES}', '{TARGETS}', '{CENTER}'], 'A2': [],
        'WRITE': ['{BUDGET}', '{DAGSTD}', '{FINAL}', '{BEADS}', '{BASE}']}


def one(jm):
    j, model = jm; p = S/f'adv_loop_{j}.json'
    if not p.exists():
        rt = lambda f: (SCH/f).read_text(encoding='utf-8')
        msg = (ASK.replace('{STD}', (PUB/'大众版标准.md').read_text(encoding='utf-8')).replace('{A1}', rt('Q6_A1.txt')).replace('{A2}', rt('Q6_A2.txt'))
               .replace('{A4}', rt('Q15_A4.txt')).replace('{A4L32}', rt('L32_g6_A4b.txt')).replace('{WRITE}', (S/'prompt_K28b.txt').read_text(encoding='utf-8'))
               .replace('{LINES}', lines_text()).replace('{LOOP}', (S/'loop_evidence.txt').read_text(encoding='utf-8')))
        print(j, '材料', len(msg), '字', flush=True)
        r = None
        for k in range(3):
            try: r = parse(call(f'advloop_{j}' + ('' if not k else f'_r{k}'), msg, model, 'gpt3s', 'dag-advisor')); assert len(r.get('schemes') or []) >= 2; break
            except Exception as ex: print('不合格', j, repr(ex)[:150], flush=True); r = None
        if not r: return
        p.write_text(json.dumps(r, ensure_ascii=False, indent=1), encoding='utf-8')
    r = rd(p); print('====', j, '诊断：', r.get('diagnosis')); print('冲突：', json.dumps(r.get('conflict'), ensure_ascii=False))
    for n, sc in enumerate(r.get('schemes') or [], 1):
        print(f'-- {j}{n} {sc.get("name")}｜{sc.get("layers")}｜假设：{sc.get("hypothesis")}')
        for k, v in (sc.get('prompts') or {}).items():
            if v and v.strip().strip('“”"') != '不改':
                (SCH/f'L34_{j}{n}_{k}.txt').write_text(v, encoding='utf-8')
                h = prompt_lint.find(re.sub(r'\{[A-Z_]+\}', '', v))
                print(f'   {k}：{len(v)} 字｜泛化检查 {h or "过"}｜缺占位符 {[x for x in NEED.get(k, []) if x not in v] or "无"}')


if __name__ == '__main__':
    with ThreadPoolExecutor(2) as ex: list(ex.map(one, [('g6', G6), ('g56', G56)]))
