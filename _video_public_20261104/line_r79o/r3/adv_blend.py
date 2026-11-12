"""11-08 迭代准则 I02（DAG2 照此执行后第一次）：两位顾问看标准、硬约束、试验记录、现在的产物和问题，各给三套写稿提示词（大改、彼此不同），一批并行快筛。
结果 r3/s24/adv_blend_{g6|g56}.md 和 r3/s24/prompt_BL{g6|g56}{1,2,3}.txt
"""
import json, sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import blend, prompt_lint
from pub24 import S, G6, G56, call, parse, view_text
sys.stdout.reconfigure(encoding='utf-8')
B = Path(__file__).resolve().parents[2]


def cut(t, secs):
    out, keep = [], False
    for ln in t.split('\n'):
        if ln.startswith('### '): keep = any(ln.startswith('### '+s) for s in secs)
        if keep: out.append(ln)
    return '\n'.join(out)


LOG = """（都是两首同跑；评委是扮观众的 GPT，看文字版屏幕，和现在的旧视频比）
1. 把定稿线压缩成短句：好扫、要点清楚，但“知道他为什么这样”“前后是一件事”几乎全输：压缩时删掉了原因、动机、转折。在压缩线上每条补字没用。
2. 线换回定稿原文：“为什么”赢回来，但“扫得动”大输。扫读评委对字多会扣分，不是评委偏差。
3. 一行一个因果（原因和结果同一行用连接词连上）：“为什么”从输变成大胜。但一行最多一个逗号会把因果拆断，“为什么”又输。
4. 扫不动主要来自停留短的段字太密（如 18 秒的段放 250 多字）；按秒数删感受碎片能救扫得动，删到旧视频的字数就删过头，覆盖掉到旧视频以下。
5. 修线修人话时把疑问改成断言、把具体说法改笼统、加了定稿没有的话，“为什么”就掉；这种修改要能被查出来。
6. 感受碎片：书面词、把一句话硬切成两半都算不是人话；用户要的珠子形态是“全部 break 开”的短语，同一种感受只留一个说法。
7. 这些试验里屏幕都是“一行话、一行感受”交替，内容按来源分开（话只放线，感受只放珠子）。用户 11-08 指出这不是要的“揉在一起”。
8. 第一版“揉在一起”写稿提示词（附在最后）：写手仍写成每段几句话、后面跟一大串感受，没揉起来；停留 18 秒的段放了两句长话加 15 块短语。"""

ASK = """你是顾问。我们做钢琴曲的“边听边看”视频（大众版）：下半屏音乐动画，上半屏文字。文字来自两份定稿：线（一个人经历的一件事）和珠子（听的人此刻心里和身上的感受）。我们用大模型写屏幕稿（一次写全曲），再用大模型评委按标准测。现在需要新的写稿提示词。

请先诊断：为什么写手明明被告知“珠子和线揉在一起、连贯和散落都可以”，还是写成按来源分开的“几句话 + 一串感受”？为什么短段会塞太多？然后给出三套写稿提示词，要大改、彼此思路不同（例如：先按“这一刻他的处境 + 此刻的感受”组织成几个小单元再落笔；或先定每段最核心的一两件事再往里织感受；或别的你认为更好的办法），每套都是完整、可直接发给写手的提示词。

要求：
- 提示词里不放任何具体作品的内容或例子（硬约束：换任何作品都能照样跑）；不写只针对眼前某处毛病的规定。
- 不写死字数、秒数上限；密度靠写手按停留秒数判断，可以给写手看每段秒数和旧视频字数作参照（材料里会有）。
- 输出格式必须保持（下游渲染和测法要用），提示词里要写明：{FORMAT}
- 材料会接在提示词后面，占位符照写：{{BUDGET}}（每段秒数和参照字数）、{{DAGSTD}}（线和珠子定稿时用的标准）、{{FINAL}}（定稿的线，带编号）、{{BEADS}}（定稿的珠子，带编号，标明哪些只属于某几小节）。

只输出 JSON：{"diagnosis":"诊断，几句","prompts":[{"name":"一个词","idea":"思路一句","prompt":"完整提示词"}]}，三套。回答时请不要进行联网搜索。

【标准（修订稿）】
{STD}

【线和珠子定稿时用的标准】
{DAGSTD}

【用户原话（11-05 以后，按时间）】
{LATER}

【试验记录】
{LOG}

【第一版“揉在一起”写出来的样子（一首的三段；话 = 大字，【】放大；感受 = 小字短语）】
{SAMPLE}

【第一版写稿提示词（材料部分省略）】
{BLEND}
"""
FORMAT = '只输出 JSON：{"sections":[{"sec":"S01","rows":[{"form":"连贯","text":"…","keys":["照抄 text 里连续的字，1–2 个"],"emotion":"炽热|欢喜|亲密|安心|孤单|不安|悬着","from":["S01-1","S01-B2"]},{"form":"散落","items":[{"text":"…","from":["S01-B2"],"bars":"只属于某几小节时写，如 12–14，否则空"}]}]}]}，所有段都要有，按段的顺序；from 写用到的定稿线和珠子编号。'

if __name__ == '__main__':
    later = __import__('gate_review', fromlist=['LATER']).LATER if False else (Path(__file__).resolve().parent/'gate_review.py').read_text(encoding='utf-8').split('LATER = """')[1].split('"""')[0]
    later += '\n11-08：“揉起来的目的就是为了让它这个内部能够更连贯，它读起来不会太跳跃 我们肯定是希望保留原来的内容，所以才需要去测和dag的覆盖率”；“dag和dag2应该是两套标准”；“异质性其实就是不啰嗦啊”；“我当时做dag的时候没想清楚后面还是有dag2 有很多内容方面的东西 可能dag的标准也是适用于dag2的 这些标准不能丢”。'
    std = (B/'大众版标准_修订草稿_1108.md').read_text(encoding='utf-8'); std = std[:std.index('## 和现在门槛的差别')]
    sample = cut(view_text('op60', 'g68BA'), ['S05', 'S06', 'S07'])
    msg = (ASK.replace('{FORMAT}', FORMAT).replace('{STD}', std).replace('{DAGSTD}', blend.DAGSTD).replace('{LATER}', later).replace('{LOG}', LOG)
           .replace('{SAMPLE}', sample).replace('{BLEND}', blend.BLEND.split('【每段停留秒数')[0]))
    print(len(msg), flush=True)

    def one(a):
        name, model = a; ans = call(f'adv_blend_{name}', msg, model, 'gpt3s', 'public24-adv-blend'); r = parse(ans) or {}
        (S/f'adv_blend_{name}.md').write_text(f"# {name}\n\n## 诊断\n{r.get('diagnosis')}\n\n" + '\n\n'.join(f"## {p.get('name')}：{p.get('idea')}\n\n{p.get('prompt')}" for p in r.get('prompts') or []), encoding='utf-8')
        for k, p in enumerate(r.get('prompts') or [], 1):
            t = p.get('prompt') or ''; ok = all(x in t for x in ['{BUDGET}', '{FINAL}', '{BEADS}'])
            h = prompt_lint.find(t.replace('{BUDGET}', '').replace('{DAGSTD}', '').replace('{FINAL}', '').replace('{BEADS}', ''))
            (S/f'prompt_BL{name}{k}.txt').write_text(t, encoding='utf-8')
            print(name, k, p.get('name'), '占位符齐' if ok else '占位符缺', '泛化', '过' if not h else f'没过 {h[:6]}', len(t), flush=True)
        print(name, '诊断', (r.get('diagnosis') or '')[:300], flush=True)
    with ThreadPoolExecutor(2) as ex: list(ex.map(one, [('g6', G6), ('g56', G56)]))
