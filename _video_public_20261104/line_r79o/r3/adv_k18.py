"""11-09 下午 迭代准则 I01：一条路连着走不通，把证据交给两位顾问（GPT-6、GPT-5.6）独立诊断，各给一套下一步的写稿或改稿提示词。
起因：用户 11-09：“我感觉你这现在的dag2内容看上去还是很像我们之前那个版本的，好像就没有做太多的修改”。K11g 有 99% 的字沿用 K3A；
之后从头重写六版（K15a/b、K16a/b、K17a/b），分阶段快筛全部输给 K11g（多数输在船歌）。
python r3/adv_k18.py      → r3/s24/adv_k18_{g6|g56}.json（diagnosis、route、prompt）；prompt 另存 r3/s24/prompt_BLk18{a|b}.txt
"""
import json, glob, sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import prompt_lint
from pub24 import S, rd, call, parse, G6, G56, view_text
sys.stdout.reconfigure(encoding='utf-8')
NL = chr(10)

ASK = """你是顾问。我们在做两首钢琴曲的大众版“边听边看”视频屏幕稿：下半屏音乐动画，上半屏文字；普通观众第一次看，边听边扫。原料是已定稿的“线”（一个人经历的一件事，分段）和“珠子”（听的人每段的感受：画面、身体感觉、比喻、心里话），定稿里写明了每条线对应哪几颗珠子。

【目标】做出一版屏幕稿，按下面的标准做绝对尺度验收时，剩下的问题都只是轻微的（严重 0、中等 0）。同时它要真的比现在的最好版更好，不只是删短。

【大众版标准（只有用户能改）】
{STD}

【现在的最好版 K11g 是怎么来的】
11-08 一位写手按“珠子和线揉在一起、每行自选连贯或散落”写出 K3A（每首约 3900 字）→ 删小节号 → 只删感受里多余的小句、按评委点名回补、收紧过密的屏、修语病 → K11g（约 3100–3200 字）。K11g 有 99% 的字是 K3A 原字，结构没变。
K11g 的绝对验收（两首 × 两位评委 × 多遍，共 24 次）：严重 0；中等 13 条，几乎都是“某屏偏密”（停留 18–38 秒的屏装了两段话加两条长感受）和“小字感受是一长串多层意思的句子，扫不动”；轻微 58 条（同屏同一层意思说两遍、书面腔、“越……越……”反复）。
在 K11g 上继续删（K12）、加放大词（K13）、再收紧（K14），都输给 K11g（为什么、连贯、单独成立明显变差）。

【从头重写的六版，全部输给 K11g】（盲比：两位评委 × 两种先后顺序；“稳定选”= 两种顺序都选同一版）
- K10（三版，11-09 凌晨）：揉进同一句，连贯和“为什么”大赢，但写到 4500–6400 字，扫读和简洁全输；有一版把听众的比喻写成了他的经历。
- K15：每屏按停留秒数给字数硬上限（每秒 5.5 字，90–300 字），加“打碎成短语”。结果线照抄定稿、珠子被切成上百块碎片（“后来”“接着”单独成块、留着音型描写）。船歌或幻想两位评委都稳定选 K11g：来回跳、近义短句堆叠。
- K16：散落每块要完整、大字把对应珠子的感受揉进处境。评委说更连贯，但大字占 80%、小字只剩约 430 字，船歌珠子覆盖 0.44（旧视频 0.665，K11g 约 0.55–0.6）；细腻输（具体说法被改成概括），K11g 的放大词更醒目，“也可以听成”太多。
- K17：每屏大字最多 55%，小字用珠子原词写成 3–10 字短语。船歌两位评委都稳定选 K11g。理由见下。
（参照：旧视频 w23 每首约 2500–2700 字，大字 60%、小字 40%，小字是从珠子取的 3–8 字原词短语；K11g 盲比全胜 w23。）

【K17 船歌盲比的评委原话】
{WHY}

【K11g 船歌全文（文字稿；【】是放大加亮的词；“到时出现”的到那几小节才出现、之后留到这屏结束）】
{K11G}

【K17a 船歌全文】
{K17}

请回答：
1. 诊断：为什么从头重写总是输给 K11g？K11g 好在哪里、是重写难以复现的？现在的盲比和快筛有没有让重写吃亏的地方（如果有，说清楚怎么改测法、怎么验证）？
2. 路线：下一步应该（A）再从头写，还是（B）以 K11g 为底逐屏重新组织（每屏可以大改：重排、合并、改写、换形态，但从 K11g 出发），还是（C）别的？为什么？
3. 给出这条路线的完整提示词（给写手 / 改稿人用）。要求：
   - 不放任何具体作品的内容或例子（上面的原文只给你看，不能写进提示词）。
   - 用这些占位符：{{BUDGET}}（每屏停留秒数和字数上限）、{{DAGSTD}}（上面的大众版标准）、{{FINAL}}（定稿线，每条后面写了对应哪几颗珠子）、{{BEADS}}（定稿珠子，标了哪些只属于某几小节）；走路线 B 的再用 {{CURRENT}}（当前最好版全曲，和下面输出格式相同的 JSON）。
   - 输出格式必须是：{"sections":[{"sec":"S01","rows":[{"form":"连贯","text":"…","keys":["照抄 text 里连续的字"],"emotion":"炽热|欢喜|亲密|安心|孤单|不安|悬着","from":["S01-1","S01-B2"]},{"form":"散落","items":[{"text":"…","from":["S01-B2"],"bars":"只属于某几小节时写，否则空"}]}]}]}，所有段都要有。

只输出 JSON：{"diagnosis":"…","route":"A|B|C","route_why":"…","measure_fix":"测法要不要改、怎么改（不改就写不改）","prompt":"完整提示词"}。回答时请不要进行联网搜索。
"""


def why():
    out = []
    for f in sorted(glob.glob(str(S/'vs3b_op60_*_g68K17aM__g68K11g_*.json'))):
        r = rd(f); seat = Path(f).stem.split('_')[-1]
        out.append(f"- 一位评委（K17a 在{'前' if seat == 'X' else '后'}）：选{'K17a' if r.get('better') == seat else 'K11g' if r.get('better') in 'XY' else '平'}。{r.get('why') or ''}")
    return NL.join(out)


def std():
    s = Path('D:/musicclaude/_video_public_20261104/大众版标准.md').read_text(encoding='utf-8')
    return s[s.index('## 内容（屏幕稿）'):s.index('## 画面')]


def one(jm):
    j, m = jm; p = S/f'adv_k18_{j}.json'
    if p.exists(): r = rd(p)
    else:
        msg = ASK.replace('{STD}', std()).replace('{WHY}', why()).replace('{K11G}', view_text('op60', 'g68K11g')).replace('{K17}', view_text('op60', 'g68K17aM'))
        r = None
        for k in range(3):
            try: r = parse(call(f'adv_k18_{j}' + ('' if not k else f'_r{k}'), msg, m, 'gpt3s', 'public24-adv')); assert r.get('prompt'); break
            except Exception as ex: print('不合格', j, repr(ex)[:150], flush=True); r = None
        if not r: return
        p.write_text(json.dumps(r, ensure_ascii=False, indent=1), encoding='utf-8')
    tpl = r['prompt'].replace('{{', '{').replace('}}', '}')
    try: prompt_lint.lint(tpl.replace('{BUDGET}', '').replace('{DAGSTD}', '').replace('{FINAL}', '').replace('{BEADS}', '').replace('{CURRENT}', ''), f'adv_k18_{j}')
    except SystemExit as ex: print('泛化检查没过', j, ex, flush=True)
    (S/f"prompt_BLk18{'a' if j == 'g6' else 'b'}.txt").write_text(tpl, encoding='utf-8')
    print(f"== 顾问 {j}：路线 {r.get('route')}；{r.get('route_why', '')[:300]}{NL}   诊断：{r.get('diagnosis', '')[:600]}{NL}   测法：{r.get('measure_fix', '')[:400]}", flush=True)


if __name__ == '__main__':
    with ThreadPoolExecutor(2) as ex: list(ex.map(one, [('g6', G6), ('g56', G56)]))
