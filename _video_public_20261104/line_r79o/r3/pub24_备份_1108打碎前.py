"""屏幕稿：珠子和线揉在一起写，上下交替排（线一行、感受一行），线的关键词放大，感受小字散开；局部小节的感受到时出现。
内容这一步直接从完整珠子 + 定稿线出发，不再先拆词再配线。顾问只用 GPT（GPT-6、GPT-5.6）。
python pub24.py adv                两位顾问各给一份通用提示词 → r3/s24/prompt_{a}.txt
python pub24.py write CAND         两首同写 → r3/s24/screen_{w}_{CAND}.json，并转成 script_{w}_{CAND}.json 供已有测法用
python pub24.py show CAND [段...]
"""
import json, os, re, sys
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
os.environ.setdefault('PUB_WORKS', 'op60,op61')
os.environ.setdefault('PUB_LA_CAL', '2')   # 11-07：整屏累积问题默认用第二版评委
import pub2, pub3, pub16
from pub2 import G6, G56, JUDGES, WORKS, call, parse, rd, wr
R3 = pub3.OUT; R2 = pub2.OUT; S = R3/'s24'; S.mkdir(exist_ok=True)

FORMAT = '{"plan":"全曲怎么排、哪些词前后呼应","sections":[{"sec":"S01","rows":[{"kind":"line","text":"线这一行的话","keys":["要放大的关键词，照抄 text 里连续的字"],"emotion":"炽热|欢喜|亲密|安心|孤单|不安|悬着 选一个","from":["S01-1"]},{"kind":"feel","items":[{"text":"一块感受","bead":"S01-B2","bars":"可选：这块只属于珠子里写明的某几小节时写，如 12–14；否则空字符串"}]}]}]}'

ADV = """你是顾问。我们做钢琴曲的“边听边看”视频（给普通观众的大众版）：下半屏是音乐动画，上半屏是文字。文字有两种来源：珠子（听的人此刻心里和身上的感受，有的写明只属于某几小节）和线（一个人经历的一件事，把珠子串起来）。两者都已定稿，见下面的材料。

【用户看完视频的原话（按时间）】
1. “感觉你现在这个线还是太啰嗦……现在抓不到线的要点 在看视频的时候 可能应该要提炼出要点 然后要点中间要能够前后呼应 感觉到有整体性 独立性 不能翻译珠子……会不会有一些我们删掉的东西 比如形容词副词 句子中间的连接部分 其实起到了太关键的作用 我们最后肯定要形成一个平衡 注意力必须最经济”
2. “现在珠子看起来都没有那种在一个段里的几小节了……我之前说的动画也就只针对这个……我看你这压缩 一个是人话衰退太多了 然后我想的是 这种左右布局是不是有问题 一段珠子一段线一段珠子会不会更好 这样能帮他决定阅读顺序 缺点就是不太能一起看 但我觉得一起看应该本来就是不合理的吧 ……珠子和线本来就没有必要分的那么清吧 现在因为珠子和线是分开来的 所以才导致这个 我们不去给他分开来 给他揉到一块 还有可能就解决了 反正我们现在只要保证那些指标不掉不就可以了吗？我想的是长段 连贯的话一定是恶心人的 一定不可能一眼扫过去的时候会这样细读的 就是应该比如线的关键字放大 然后珠子的一些散落感受小一点这样 你可能应该先回去修内容 一个是我们现在颗粒度变粗了 一个是这个刚刚说的”

【大众版标准（目的）】
{STD}

【测到的事实】
- 现在的屏幕：左边一条线是定稿原句（平均 39 字、2.4 个逗号），右边是从珠子拆出的短词。线的要点平均只有 11 字，六到八成落在句子后部，扫的人先看到铺垫。
- 原稿最精细的体验主要靠连接转折（约三成）和比喻画面（约三成）撑着，形容词、副词不到一成。拆成短词以后，约七成精细体验“变粗”：比如“只剩一条单薄、孤零零的旋律，在空中漫无目的地游走”成了“脚下没了支撑”；“身体还在这里，心却已经慢慢漂远”成了“心慢慢漂远”。颗粒度变粗，是这一版最大的问题之一。
- 试过把线压短、改成“大字要点 + 小字补充”：好扫每次都赢，但“知道他为什么这样”和“细腻”每次都输，人话也变差（电报句、“他因……而……”）。不带逗号的写法会写出一口气读不完的长句。
- 珠子里写明只属于某几小节的（每首约四成），现在屏幕上不再到时出现，局部动画没了。

【一段的材料示例（船歌 S02，约 56 秒）】
{SAMPLE}

【请你回答】
1. 判断：珠子和线“揉到一块”写成一份屏幕稿，是否能同时解决要点、颗粒度、人话、阅读顺序？会丢什么，怎么防？
2. 定下这份屏幕稿的形态：一段里线的行和感受的行怎么交替；线这一行写成什么样（多长、关键词放大哪些、要不要完整句）；感受这一行写成什么样（多碎、怎样保住颗粒度、局部小节怎么标）；两者怎样不互相翻译又接得上；前后段怎样呼应。
3. 写一份通用提示词，直接发给写手。不能提任何具体作品的内容，对任何作品都能用。用这些占位符（照原样写，脚本会替换）：{BEADS} 定稿珠子全文（带编号、小节、角色），{LINES} 定稿线（带编号），{SECONDS} 每段秒数。写手必须只输出这个 JSON（写进提示词）：
{FORMAT}
   rows 按屏幕上从上到下的顺序；kind 只有 line 和 feel；feel 的每块都要写 bead（来自哪颗珠子的编号），脚本据此决定它在哪几小节出现；不来自任何珠子的感受不许写。line 的 from 写依据的定稿线编号。
   要守住的指标（写手要知道）：原稿（珠子+线）的意思在屏幕上留住的比例不能比现在低（现在约七成）；人话不比定稿的线差（句式多变、不像提纲、不用书面词和格言）；不编原文没有的事；不把珠子里的比喻写成真的发生的事；人称和称呼跟定稿一样。

只输出 JSON：{"judgement":"第1问","form":"第2问","prompt":"第3问的提示词全文"}
"""


REV = """你是顾问。上一轮你给写手的提示词（附在最后）已经两首同跑。下面是写出来的结果和测量，请改提示词。

【测量（两首）】
{STATS}
- 现在视频的屏幕（左线右词）每首约 2600 字；你这版是它的 {RATIO} 倍。另一位顾问的版本：{OTHER}
- 正文里出现了小节号（如“第12–14小节”）{BARS} 处。小节号不该给观众看：它只用来决定这块什么时候出现。新格式里 feel 的每块可以写 bars 字段，脚本核对它落在原珠子写明的范围内，再按它定时出现。
- 纯音乐描写（旋律、和弦、步态、三连音这类）的感受块约占 {MUSIC}。标准说音乐只在帮观众对上感受时才提。

【你这版的屏幕（节选）】
{SAMPLE}

【用户的要求（原话节选）】
“长段 连贯的话一定是恶心人的 一定不可能一眼扫过去的时候会这样细读的 就是应该比如线的关键字放大 然后珠子的一些散落感受小一点这样”；“注意力必须最经济”；“颗粒度变粗了”要修；“反正我们现在只要保证那些指标不掉”；人话不能衰退。

【这一轮要解决的】
同时做到：观众扫得动（总量和每段的密度要和音乐时长相称，不能整篇搬上屏）、颗粒度不粗（保住那些换个说法就没了的细节，但不是所有细节都上屏）、人话不退、局部小节到时出现。请想清楚：在细节多于观众扫得动的地方，按什么挑；同一颗珠子的几种听法怎么取舍；线还要不要每条都上屏。

写一份新的通用提示词，规则同上一轮：不提具体作品内容；占位符 {BEADS}、{LINES}、{SECONDS} 照原样写；写手只输出这个 JSON：
{FORMAT}

只输出 JSON：{"diagnosis":"三五句","prompt":"新提示词全文"}

【上一轮的提示词】
{PROMPT}
"""

MUSIC = re.compile(r'小节|旋律|和弦|音型|步态|三连音|左手|右手|低音|高音|声部|节奏|音乐|琶音|主题')


def stats(cand):
    out = []; tot = 0
    for w in WORKS:
        r = rd(S/f'screen_{w}_{cand}.json'); rows = [x for s in r['sections'] for x in s['rows']]
        L = [x['text'] for x in rows if x['kind'] == 'line']; F = [i['text'] for x in rows if x['kind'] == 'feel' for i in x['items']]
        n = sum(map(len, L))+sum(map(len, F)); tot += n
        out.append(f"- {w}：线 {len(L)} 行，平均 {sum(map(len, L))//max(1, len(L))} 字；感受 {len(F)} 块，平均 {sum(map(len, F))//max(1, len(F))} 字；全屏合计 {n} 字")
    bars = sum(len(re.findall(r'\d+\s*[–—-]\s*\d+\s*小节|第\s*\d+', i['text'])) for w in WORKS for s in rd(S/f'screen_{w}_{cand}.json')['sections'] for x in s['rows'] if x['kind'] == 'feel' for i in x['items'])
    F = [i['text'] for w in WORKS for s in rd(S/f'screen_{w}_{cand}.json')['sections'] for x in s['rows'] if x['kind'] == 'feel' for i in x['items']]
    music = f"{round(100*sum(bool(MUSIC.search(x)) for x in F)/max(1, len(F)))}%"
    return chr(10).join(out), round(tot/2/2600, 1), bars, music


def revise(name, other):
    st, ratio, bars, music = stats(name); ost, oratio, *_ = stats(other)
    sample = []
    for s in rd(S/f'screen_op60_{name}.json')['sections'][1:5]:
        sample.append(s['sec'])
        for x in s['rows']: sample.append(('【线】'+x['text']) if x['kind'] == 'line' else ('　感：'+' / '.join(i['text'] for i in x['items'])))
    msg = REV.replace('{STATS}', st).replace('{RATIO}', str(ratio)).replace('{OTHER}', f'{oratio} 倍').replace('{BARS}', str(bars)).replace('{MUSIC}', music).replace('{SAMPLE}', chr(10).join(sample)).replace('{FORMAT}', FORMAT).replace('{PROMPT}', (S/f'prompt_{name}.txt').read_text(encoding='utf-8'))
    ans = call(f'pub24_rev_{name}', msg, G56 if name == 'g56' else G6, 'gpt3s', 'public24-rev'); r = parse(ans) or {}
    (S/f'rev_{name}.md').write_text(ans or '', encoding='utf-8')
    if r.get('prompt'): (S/f'prompt_{name}2.txt').write_text(r['prompt'], encoding='utf-8')
    print(name, '诊断', (r.get('diagnosis') or '')[:400], '提示词', len(r.get('prompt') or ''), flush=True)


REV3 = """你是顾问。你上一轮的提示词（附在最后）两首同跑后测完了。请再改一次提示词。

【结果】
- 扮观众和现在的视频盲比：{VS}。评委一致说新排法好扫、抓得到要点、感受更细；输的是“知道他为什么这样”，评委原话：
{WHY}
- 对原稿（珠子+线）的覆盖：原稿每个要点判“留住/部分/没有”。{COVER}
  判“没有”的原稿要点举例（两位评委都判没有的）：
{MISSING}
- 精细体验：评委从原稿每段挑最精细、换个说法就没了的地方，看屏幕上还在不在。{FINE}
  丢了而且损失大的举例：
{FINELOST}
- 人话（N09 开放评审，满分 10）：{LANG}
- 全屏字数是现在视频的 {RATIO} 倍。

【这一轮要解决的】
排法和写法已经证明对观众有效，不要退回去。要做的是把覆盖和精细体验补回来，同时不丢掉好扫：
- 总量可以回到和现在视频相当（约 1 倍），但多出来的字要花在“没有”的要点和丢掉的精细体验上，不是把句子写长。
- 线要保住让人知道“为什么”的那一步因果，但仍然先说要点、关键词放大。
- 不要为了覆盖把同一颗珠子的近似说法都搬上来；一块感受只说一种体验。
- 感受必须保持碎片（用户：“看起来完全不碎啊？还是句子？？”）：短词组，各自一扫就懂；单独看不懂的碎片（只剩一个抽象词、半个意思）不要；同一颗珠子的碎片之间要有主次，不要把相近的说法堆在一起。
- 珠子严格覆盖（只看感受、具体的画面/身体感觉/比喻/心里话还在才算）：{BEADCOV}。
- 人话标准对线和感受同样适用（用户看截图说过“完全不是人话”：书面短语、把一句话硬切成几块都不行）；每条线选一种情绪色，组和组之间要看得出不一样。
写一份新的通用提示词，规则同上一轮：不提具体作品内容；占位符 {BEADS}、{LINES}、{SECONDS}、{BUDGET} 照原样写（{BUDGET} 是每段现在视频的字数参照，新稿每段大致相当）；写手只输出：
{FORMAT}

只输出 JSON：{"diagnosis":"三五句","prompt":"新提示词全文"}

【上一轮的提示词】
{PROMPT}
"""


REV4 = """你是顾问。你的提示词（附在最后）已经跑了几轮，下面是用户和测量的反馈。请写一份新的通用提示词，线的形态这次指定为：{FORM}

【用户看了截图后的原话】
“你这几张截图看起来完全不是人话 之前那些标准还是成立的”；“多种颜色那个还是要保留啊”；“线的话 如果说碎裂的更好可能也是可以搞成碎裂的”。
截图里被说“不是人话”的字，例如：“身体不必踩实，交给船底温柔托举”“对方没有退开，仍愿意亲近，他才渐渐放松下来”“丰满的声音只剩一条单薄的旋律 / 孤零零地在空中漫无目的游走”。这类是把原文压成书面短语，或把一句话硬切成几块。人话的标准没有变：像一个人平常说话，句式多变，不像提纲，不用书面词和格言；感受也一样要是人话，不只是线。

【几轮下来的测量】
- 扮观众盲比：上下交替、关键词放大的排法 8/8 胜过现在的视频，好扫、抓得到要点、感受更细；输在“知道他为什么这样”。
- 总量在两头摆：第二轮只有现在视频的 0.6–0.7 倍，覆盖掉到 36–55%（现在 70–76%）、精细体验少了；第三轮又到 1.7 倍，重新变成要细读的段落。这次每段给你一个参照：{BUDGET} 里是现在视频这一段屏幕上的字数，新稿每段大致相当，可以按内容上下浮动，但不要成倍。
- 颜色：每条线选一种情绪（炽热、欢喜、亲密、安心、孤单、不安、悬着），它下面的感受跟它同色。同一段里性质不同的几条线要真的不一样，颜色本身带情绪。

【线的形态：{FORM}】
{FORMNOTE}

规则同前：不提具体作品内容；占位符 {BEADS}、{LINES}、{SECONDS}、{BUDGET} 照原样写；写手只输出：
{FORMAT}

只输出 JSON：{"diagnosis":"三五句","prompt":"新提示词全文"}

【你上一轮的提示词】
{PROMPT}
"""
FORMS = {'s': ('句子', '线是一句完整、自然的话，先说要点，保住让人知道“为什么”的那一步因果，关键词放大。'),
         'f': ('碎裂', '线也拆碎：一行线是几个短的片段，用“ / ”隔开，各自一扫就懂，合起来是这个人此刻的处境和原因；关键词放大。碎片也要是人话，不能是书面词组，也不能把一句话机械切断。让人知道“为什么”的那一步因果要保住，可以是一个独立的片段。')}


def revise4(name, form):
    fn, note = FORMS[form]
    msg = REV4.replace('{FORM}', fn).replace('{FORMNOTE}', note).replace('{FORMAT}', FORMAT).replace('{PROMPT}', (S/f'prompt_{name}23.txt').read_text(encoding='utf-8'))
    ans = call(f'pub24_rev4_{name}_{form}', msg, G56 if name == 'g56' else G6, 'gpt3s', 'public24-rev'); r = parse(ans) or {}
    (S/f'rev4_{name}_{form}.md').write_text(ans or '', encoding='utf-8')
    if r.get('prompt'): (S/f'prompt_{name}4{form}.txt').write_text(r['prompt'], encoding='utf-8')
    print(name, form, '诊断', (r.get('diagnosis') or '')[:300], '提示词', len(r.get('prompt') or ''), 'BUDGET' if '{BUDGET}' in (r.get('prompt') or '') else '缺BUDGET', flush=True)


BEADCOV = """下面是一首钢琴曲视频的两份文字。“原稿珠子”是听的人当下的感受，已按句拆成要点；“屏幕上的感受”是视频里实际显示的感受短句（不含叙事的话）。

逐条判断原稿的每个要点，在同一段屏幕上的感受里还在不在。要求严格：
- 留住：那个具体的东西还在，例如同一个画面、同一种身体感觉、同一个比喻、同一句心里话、同一个转折。说法可以不同、可以更短。
- 部分：只剩大意或情绪，具体的画面、身体感觉、比喻或转折没了；或者几种听法只留了一种。
- 没有：屏幕上的感受里找不到。
只看感受，不要因为叙事的话里说到了同样的情绪就算留住。纯描写音乐本身（声部、和弦、小节）的要点，它带出的那个感受在就算留住。

只输出 JSON：{"items":[{"id":"S01-B1-p1","verdict":"留住|部分|没有"}]}，逐条给全。

【屏幕上的感受】
{SCREEN}

【原稿珠子】
{SOURCE}
"""


BCALL = os.environ.get('PUB_BC_ALL') == '1'   # 11-08：珠子和线揉在一起后，珠子的具体体验可能写在大字里；整屏所有文字都算（w23 同样按整屏重测）
BC_PRE = 'beadcovA' if BCALL else 'beadcov'
BEADCOV_ALL = BEADCOV.replace('“屏幕上的感受”是视频里实际显示的感受短句（不含叙事的话）。', '“屏幕上的文字”是视频里实际显示的全部文字（叙事的话和感受短语都算，两者可能写在同一句里）。').replace('在同一段屏幕上的感受里还在不在', '在同一段屏幕上的文字里还在不在').replace('- 没有：屏幕上的感受里找不到。', '- 没有：屏幕上找不到。').replace('只看感受，不要因为叙事的话里说到了同样的情绪就算留住。', '不管写在叙事的话里还是感受短语里都算；但只说到同样的情绪、没有那个具体的东西，只算部分。').replace('【屏幕上的感受】', '【屏幕上的文字】')
assert BEADCOV_ALL.count('屏幕上的文字') >= 3


def feel_screen(w, tag):
    NL = chr(10)
    if BCALL:
        rows = []
        if tag.startswith('w'):
            for s in rd(R3/f'script_{w}_{tag}.json')['sections']:
                rows.append(NL+'### '+s['sec']+NL+NL.join(' '.join(l['text'] for l in g['lines'])+' / '+' / '.join(b['text'] for b in g['beads']) for g in s['groups']))
        else:
            for s in rd(S/f'screen_{w}_{tag}.json')['sections']:
                rows.append(NL+'### '+s['sec']+NL+NL.join(x['text'] if x['kind'] == 'line' else ' / '.join(i['text'] for i in x['items']) for x in s['rows']))
        return NL.join(rows)
    rows = []
    if tag.startswith('w'):
        for s in rd(R3/f'script_{w}_{tag}.json')['sections']:
            rows.append(f"\n### {s['sec']}\n"+' / '.join(b['text'] for g in s['groups'] for b in g['beads']))
    else:
        for s in rd(S/f'screen_{w}_{tag}.json')['sections']:
            rows.append(f"\n### {s['sec']}\n"+' / '.join(i['text'] for x in s['rows'] if x['kind'] == 'feel' for i in x['items']))
    return '\n'.join(rows)


def bead_cov(a):
    w, j, tag = a; p = S/f'{BC_PRE}_{w}_{j}_{tag}.json'
    src = '\n'.join(f"\n### {s['sec']}\n"+'\n'.join(f"- {q['id']}：{q['text']}" for b in s['beads'] for q in b['points']) for s in rd(R2/f'{w}_src.json')['sections'])
    if not p.exists():
        for k in range(3):
            ans = call(f'pub24BC{"A" if BCALL else ""}_{w}_{j}_{tag}'+('' if not k else f'_r{k}'), (BEADCOV_ALL if BCALL else BEADCOV).replace('{SCREEN}', feel_screen(w, tag)).replace('{SOURCE}', src), JUDGES[j], 'gpt3s', 'public24-beadcov')
            try: r = parse(ans); assert r['items']; wr(p, r); break
            except Exception as ex: print('不合格', w, j, repr(ex)[:150], flush=True)
    r = rd(p); c = Counter(x.get('verdict') for x in r['items']); n = sum(1 for _ in re.finditer(r'^- ', src, re.M))
    print(w, j, tag, '珠子严格覆盖', dict(c), '/', n, '留住', f"{round(100*c['留住']/n)}%", '留住+部分', f"{round(100*(c['留住']+c['部分'])/n)}%", flush=True)
    return c['留住']/n


def precheck(tag):
    """送测前的机械预检：感受是不是碎片、总量有没有超、每条线有没有情绪色。不过就不送测。"""
    ok = True; msg = []
    for w in WORKS:
        r = rd(S/f'screen_{w}_{tag}.json'); F = [i['text'] for s in r['sections'] for x in s['rows'] if x['kind'] == 'feel' for i in x['items']]
        L = [x for s in r['sections'] for x in s['rows'] if x['kind'] == 'line']
        avg = sum(map(len, F))/max(1, len(F)); punct = sum(bool(re.search('[，。；]', f)) for f in F)/max(1, len(F)); emo = sum(bool(x.get('emotion')) for x in L)/max(1, len(L))
        good = avg <= 8 and punct <= .1 and emo == 1
        msg.append(f"{w} 碎片均 {avg:.1f} 字、带标点 {punct:.2f}、线带情绪 {emo:.2f}")
        ok &= good
    _, ratio, _, _ = stats(tag); ok &= ratio <= 1.4
    print(tag, '预检', '过' if ok else '不过', f'字数 {ratio} 倍；', '；'.join(msg), flush=True)
    return ok


DIMS = {'scan': '扫得动', 'point': '抓要点', 'why': '为什么', 'whole': '前后一件事', 'fine': '感受细腻'}


def gate(tag, base='w23'):
    """按 DAG2 V2.04 的门槛对照现在的视频（w23）。每首两位评委取平均；两首都过才算过。"""
    def avg(xs): xs = [x for x in xs if x is not None]; return round(sum(xs)/len(xs), 2) if xs else None
    def cov(w, t):
        out = []
        for j in JUDGES:
            p = R3/f'cover_{w}_{j}_{t}.json'
            if p.exists():
                it = rd(p)['items']; out.append(sum(x.get('verdict') == '留住' for x in it)/max(1, len(it)))
        return avg(out)
    def bcov(w, t):
        out = []
        for j in JUDGES:
            p = S/f'{BC_PRE}_{w}_{j}_{t}.json'
            if p.exists():
                it = rd(p)['items']; out.append(sum(x.get('verdict') == '留住' for x in it)/max(1, len(it)))
        return avg(out)
    def fine(w, t):
        # 11-07：旧测法（audit21）每次现挑句子、两次几乎不重合，不可比；换成 pub25 固定清单逐条判，“在”的比例
        import pub25
        return pub25.score(w, t)[0]
    def num(x):
        try: return float(str(x).split('/')[0])
        except Exception: return None
    def lines_of(w, t):
        p = S/f'screen_{w}_{t}.json'
        return [x['text'] for sec in rd(p)['sections'] for x in sec['rows'] if x['kind'] == 'line'] if p.exists() else None
    def lang(w, t):
        # 11-06 晚：同一套线三次测出 7.88、7.62、7.38。线一字不差的版本，人话测量合在一起平均（只测线，碎片不影响这一项）
        tags = [t]
        if t != 'FINAL':
            me = lines_of(w, t)
            tags = sorted({q.stem.split('_', 2)[2] for q in S.glob(f'screen_{w}_*.json') if lines_of(w, q.stem.split('_', 2)[2]) == me})
        return avg([num(rd(R3/f'lang_{w}_{j}_{u}.json').get('score')) for u in tags for j in JUDGES if (R3/f'lang_{w}_{j}_{u}.json').exists()])
    def lall(w, t):
        sc = []; med = []; sev = []
        for j in JUDGES:
            p = S/f'langall{ {"1": "C", "2": "D"}.get(os.environ.get("PUB_LA_CAL", ""), "")}_{w}_{j}_{t}.json'
            if p.exists():
                r = rd(p); sc.append(num(r.get('score') or r.get('overall_score'))); med.append(sum((c.get('severity') or '') in ('中等', '严重', '较重') for c in r.get('cumulative') or []))
                sev.append(sum((c.get('severity') or '') in ('严重', '较重') for c in r.get('cumulative') or []))
        return avg(sc), avg(med), avg(sev)
    def vs(w):
        r = [rd(p) for p in S.glob(f'vs_{w}_*_{tag}_*.json')]; return sum(x['better'] == x['seat'] for x in r), len(r)
    def vs2(w):
        # 11-07：盲比有强烈的“后出现占优”位置偏差（两位顾问问诊后确认）。新判法：同一评委、同一座位，原顺序和交换顺序各判一次，
        # 两次都选旧（稳定选旧）必须为 0；五个分项（扫得动、抓要点、为什么、前后一件事、感受细腻）在 16 次判断里新版赢的次数不少于旧版
        st = {'新': 0, '敏感': 0, '旧': 0}; dims = {d: [0, 0] for d in DIMS}; n = 0
        for j in JUDGES:
            for seat in 'XY':
                a, b = S/f'vs_{w}_{j}_{tag}_{seat}.json', S/f'vsR_{w}_{j}_{tag}_{seat}.json'
                if not (a.exists() and b.exists()): continue
                ra, rb = rd(a), rd(b); na, nb = ra['better'] == seat, rb['better'] == seat; n += 1
                st['新' if na and nb else '旧' if not (na or nb) else '敏感'] += 1
                for r in (ra, rb):
                    for d in DIMS:
                        v = (r.get('nets') or {}).get(d)
                        if v in ('X', 'Y'): dims[d][0 if v == seat else 1] += 1
        if n < 2*len(JUDGES): return None, st, dims
        return st['旧'] == 0 and all(a >= b for a, b in dims.values()), st, dims
    def frag(w):
        F = [i['text'] for s in rd(S/f'screen_{w}_{tag}.json')['sections'] for x in s['rows'] if x['kind'] == 'feel' for i in x['items']]
        L = [x['text'] for s in rd(S/f'screen_{w}_{tag}.json')['sections'] for x in s['rows'] if x['kind'] == 'line']
        return len(F), round(sum(map(len, F))/max(1, len(F)), 1), round(sum(bool(re.search('[，。；]', f)) for f in F)/max(1, len(F)), 2), len(L), round(sum(map(len, L))/max(1, len(L)), 1)
    ok_all = True; rows = []
    for w in WORKS:
        v = vs(w); c, c0 = cov(w, tag), cov(w, base); b, b0 = bcov(w, tag), bcov(w, base); f, f0 = fine(w, tag), fine(w, base)
        l, l0 = lang(w, tag), lang(w, 'FINAL'); (la, lm, ls), (la0, lm0, ls0) = lall(w, tag), lall(w, base); fr = frag(w)
        v2, st, dims = vs2(w)
        # 11-07：累积问题改用第二版评委（PUB_LA_CAL=2）；“中等”条数区分力弱（顾问建议不当硬门槛），只报；“严重”条数不得多于 w23
        checks = {'盲比（交换顺序配对）': v2, '原稿覆盖': None if c is None or c0 is None else c >= c0, '珠子严格': None if b is None or b0 is None else b >= b0,
                  '精细': None if f is None or f0 is None else f >= f0, '线人话': None if l is None or l0 is None else l >= l0, '整屏严重累积问题': None if ls is None or ls0 is None else ls <= ls0}
        ok = all(x is not False for x in checks.values()) and None not in checks.values(); ok_all &= ok
        rows.append(f"{w}：盲比 稳定选新 {st['新']}、位置敏感 {st['敏感']}、稳定选旧 {st['旧']}；分项新:旧 " + '、'.join(f"{DIMS[d]} {a}:{b}" for d, (a, b) in dims.items()) + f"（原顺序 {v[0]}/{v[1]}）；原稿覆盖 {c}（{base} {c0}）；珠子严格 {b}（{b0}）；精细 {f}（{f0}）；线人话 {l}（定稿 {l0}）；整屏人话 {la}、中等以上累积 {lm}、严重 {ls}（{base} {la0}、{lm0}、{ls0}）；碎片 {fr[0]} 块、均 {fr[1]} 字、带标点 {fr[2]}；线 {fr[3]} 行、均 {fr[4]} 字 → " + ('过' if ok else '没过：'+'、'.join(k for k, x in checks.items() if x is False)+('；未测：'+'、'.join(k for k, x in checks.items() if x is None) if None in checks.values() else '')))
    _, ratio, _, _ = stats(tag)
    print(f"== {tag} 字数 {ratio} 倍 →", '两首都过' if ok_all else '没过'); print('\n'.join(rows), flush=True)
    return ok_all


FIXLINES = """下面是一首钢琴曲视频屏幕稿里的“线”（大字的那一行，一个人经历的事），已经按段列出。感受碎片不动，这次只改线。

两位评委按“人话”标准（像一个人平常讲自己的经历：句式多变，不像提纲，不用书面词和格言，相邻句子不彼此太像）挑出了下面的问题。请只改被点到的线，以及累积问题里列为证据的线；其余逐字不动。

改的时候：
- 意思不变，不加定稿没有的事，人称和称呼不变。可以参照定稿的线找更自然的说法。
- 不变长：改后的线不比原来多出几个字，仍然一扫读得完。
- keys 是要放大的关键词，必须是改后 text 里连续的原字；关键词尽量在前半句。
- 累积问题（同一个词反复用、相邻几段句式一样）要按评委划的范围分散开改，不要全部换成同一个新词。

只输出 JSON：{"lines":[{"sec":"S03","idx":0,"text":"改后的线","keys":["…"]}]}，idx 是这条线在该段所有线里的序号（从 0 起），只列改了的。

【评委挑出的问题】
{ISSUES}

【现在的线（每段按序号）】
{LINES}

【定稿的线（参照）】
{FINAL}
"""


def fix_lines(a):
    w, src, new = a; p = S/f'screen_{w}_{new}.json'
    if p.exists(): to_script(w, new, rd(p)); return True
    r = rd(S/f'screen_{w}_{src}.json'); iss = []
    for j in JUDGES:
        q = R3/f'lang_{w}_{j}_{src}.json'
        if not q.exists(): continue
        d = rd(q)
        iss += [f"- {x.get('where')}「{x.get('quote')}」：{x.get('why')}（评委建议：{x.get('better')}）" for x in d.get('issues') or []]
        for c in d.get('cumulative') or []:
            iss.append(f"- 累积问题（{c.get('severity')}）：{c.get('phenomenon')} 证据：" + '；'.join(f"{e.get('where')}「{e.get('quote')}」" for e in c.get('evidence') or []) + f" 范围：{c.get('boundary') or c.get('scope') or ''}")
    lines = '\n'.join(f"{s['sec']} idx {i}：{x['text']}" for s in r['sections'] for i, x in enumerate([x for x in s['rows'] if x['kind'] == 'line']))
    msg = FIXLINES.replace('{ISSUES}', '\n'.join(iss)).replace('{LINES}', lines).replace('{FINAL}', lines_text(w))
    strict = os.environ.get('PUB_FL_STRICT') == '1'   # 11-06：修线每轮都变长、盲比跟着掉；严格版要求改后字数不超过原来，超了的不采用
    if strict: msg = msg.replace('- 不变长：改后的线不比原来多出几个字，仍然一扫读得完。', '- 硬性要求：改后的线字数不能超过原来（一个字都不能多），能更短更好；做不到就别改这条。')
    for k in range(3):
        ans = call(f'pub24FL{"S" if strict else ""}_{w}_{new}'+('' if not k else f'_r{k}'), msg, G6, 'gpt3s', 'public24-fixlines')
        try:
            fx = {(x['sec'], int(x['idx'])): x for x in parse(ans)['lines']}; n = 0
            for s in r['sections']:
                for i, x in enumerate([x for x in s['rows'] if x['kind'] == 'line']):
                    y = fx.get((s['sec'], i))
                    if y and y.get('text') and not (strict and len(y['text']) > len(x['text'])):
                        x['text'] = y['text']; x['keys'] = [k2 for k2 in y.get('keys') or [] if k2 and k2 in y['text']] or x.get('keys', []); n += 1
            wr(p, r); to_script(w, new, r); print(w, new, '改了线', n, flush=True); return True
        except Exception as ex: print('不合格', w, new, repr(ex)[:200], flush=True)
    return False


def export(tag, out, line_tag='r78a'):
    """屏幕稿导出成可读文档：每段从上到下，线一行（【】是放大的关键词，后面是情绪色），感受碎片一行（「到时」表示只在那几小节出现）。"""
    from pathlib import Path
    names = {'op60': '《船歌》Op.60', 'op61': '《幻想波兰舞曲》Op.61'}; Path(out).mkdir(parents=True, exist_ok=True)
    for w in WORKS:
        r = rd(S/f'screen_{w}_{tag}.json'); win = pub16.windows(w)
        src = {b['id']: b for s in rd(R2/f'{w}_src.json')['sections'] for b in s['beads']}
        loc = {b for b, x in src.items() if any(p['local'] for p in x['points'])}
        rows = [f"# {names[w]}：屏幕稿 {tag}（线 {line_tag}）", '', '每段从上到下排。**线**一行，【】里是放大的关键词，括号里是这条线的情绪色；下面一行是感受碎片，同一颗珠子的碎片挨在一起，标「到时」的只在写明的几小节出现。', '']
        for s in r['sections']:
            a, b = win[s['sec']]; rows.append(f"## {s['sec']}（{round(b-a)} 秒）"); rows.append('')
            for x in s['rows']:
                if x['kind'] == 'line':
                    t = x['text']
                    for k in sorted(x.get('keys') or [], key=len, reverse=True): t = t.replace(k, f'【{k}】', 1)
                    rows.append(f"**{t}**（{x.get('emotion') or ''}）")
                else:
                    parts = []; last = None
                    for i in x['items']:
                        mark = '「到时」' if (i.get('bars') or i.get('bead') in loc) else ''
                        parts.append(('　·　' if last and i.get('bead') != last else ' / ' if last else '') + i['text'] + mark); last = i.get('bead')
                    rows.append(''.join(parts))
                rows.append('')
        Path(out, f'{w}_屏幕稿_{tag}.md').write_text('\n'.join(rows), encoding='utf-8')
    print('已导出', out, flush=True)



FIXLINES2 = """下面是一首钢琴曲视频屏幕稿里的“线”（大字的那一行，一个人经历的事），已经按段列出。感受碎片不动，这次只改线。

两种评委看过这一版：
1. 人话评委按“人话”标准（像一个人平常讲自己的经历：句式多变，不像提纲，不用书面词和格言，相邻句子不彼此太像）挑出了问题。
2. 看片评委是没读过原文的普通观众，边听边扫屏幕，把这一版和旧视频比。旧视频的线是完整原句。他们选旧版的理由在下面：多半是旧版把“他为什么这样、前后怎么变”连成了因果，这一版要观众自己拼。

请只改被点到的线、累积问题里列为证据的线，以及因果断开的地方；其余逐字不动。改的时候：
- 每段的线要让人一扫就明白他此刻为什么这样、和上一段比变了什么。可以把定稿里那个起作用的连接（因为什么、可是、反而、这才、却）带回来，但只带最关键的一个。
- 句子像人话，不写成“他因……而……”这种电报句。
- 仍然一扫读得完：每条改后最多比原来多 6 个字。关键词仍放在前半句。
- 意思不变，不加定稿没有的事，人称和称呼不变。不要把珠子里的感受搬进线。
- keys 是要放大的关键词，必须是改后 text 里连续的原字。
- 累积问题（同一个词反复用、相邻几段句式一样）要按评委划的范围分散开改，不要全部换成同一个新词。

只输出 JSON：{"lines":[{"sec":"S03","idx":0,"text":"改后的线","keys":["…"]}]}，idx 是这条线在该段所有线里的序号（从 0 起），只列改了的。

【人话评委挑出的问题】
{ISSUES}

【看片评委选旧版的理由】
{VS}

【现在的线（每段按序号）】
{LINES}

【定稿的线（参照）】
{FINAL}
"""


def fix_lines2(a):
    """V2.03b 第二版（11-06）：修线时同时看人话问题和看片盲比里选旧版的理由（因果断开），每条最多长 6 个字。"""
    w, src, new = a; p = S/f'screen_{w}_{new}.json'
    if p.exists(): to_script(w, new, rd(p)); return True
    r = rd(S/f'screen_{w}_{src}.json'); iss = []
    for j in JUDGES:
        q = R3/f'lang_{w}_{j}_{src}.json'
        if not q.exists(): continue
        d = rd(q)
        iss += [f"- {x.get('where')}「{x.get('quote')}」：{x.get('why')}（评委建议：{x.get('better')}）" for x in d.get('issues') or []]
        for c in d.get('cumulative') or []:
            iss.append(f"- 累积问题（{c.get('severity')}）：{c.get('phenomenon')} 证据：" + '；'.join(f"{e.get('where')}「{e.get('quote')}」" for e in c.get('evidence') or []) + f" 范围：{c.get('boundary') or c.get('scope') or ''}")
    vs = []
    for q in sorted(S.glob(f'vs_{w}_*_{src}_*.json')):
        d = rd(q); seat = q.stem.split('_')[-1]; me, old = seat, ('Y' if seat == 'X' else 'X')
        t = (d.get('why') or '') + ' ' + (d.get('regress') or '')
        t = re.sub(r'(?<![A-Za-z])'+me+r'(?![A-Za-z])', '〈这一版〉', re.sub(r'(?<![A-Za-z])'+old+r'(?![A-Za-z])', '〈旧视频〉', t))
        vs.append(('- 选了旧视频：' if d['better'] != seat else '- 选了这一版：') + t.strip())
    lines = chr(10).join(f"{s['sec']} idx {i}：{x['text']}" for s in r['sections'] for i, x in enumerate([x for x in s['rows'] if x['kind'] == 'line']))
    msg = FIXLINES2.replace('{ISSUES}', chr(10).join(iss)).replace('{VS}', chr(10).join(vs)).replace('{LINES}', lines).replace('{FINAL}', lines_text(w))
    why = os.environ.get('PUB_FL_WHY') == '1'   # 11-07：顺序交换后“为什么”一项 32 票全输、和位置无关；零星补几处（+6 字）不够，这一版每段都要接上因果，最多 +12 字
    grow = 12 if why else 6
    nogrow = os.environ.get('PUB_FL_NOGROW') in ('1', '2')   # 11-07：从定稿线重写后“为什么”赢回来了，修人话不许把线写长（变长会把扫得动拖回去）
    keep = os.environ.get('PUB_FL_NOGROW') == '2'   # 11-08：第一版修线把疑问改成断言、具体说法变笼统、加了定稿没有的话，op60“为什么”从 32:14 掉到约五五开
    if nogrow:
        grow = 0; msg = msg.replace('每条改后最多比原来多 6 个字', '改后不比原来长').replace('请只改被点到的线、累积问题里列为证据的线，以及因果断开的地方；其余逐字不动。', '请只改被点到的线和累积问题里列为证据的线；其余逐字不动。原因和结果仍放在同一行，不要拆开，也不要删掉“可、却、所以、这才、也许”这类连接和语气。')
        if keep: msg = msg.replace('其余逐字不动。原因和结果仍放在同一行', '其余逐字不动。改的时候守住意思：定稿里的疑问句仍写成疑问句，不改成断言；猜测、拿不准的语气（也许、说不定、还不知道）不改成确定；具体说法（如“被当作自己人的日子”“只能自己扛”“连这样待着都没了”）不换成笼统的词；不加定稿没有的话或结论；每条线里的原因和结果一个不丢。只改说法，不改意思。原因和结果仍放在同一行', 1)
    if why:
        msg = msg.replace('请只改被点到的线、累积问题里列为证据的线，以及因果断开的地方；其余逐字不动。',
                          '这一轮的重点是“为什么”：看片评委无论哪种先后顺序，都一致认为旧视频更能让人知道他为什么这样、前后是一件事。请逐段检查：每段至少有一条线说清楚他此刻为什么这样（起因或顾虑），并和上一段接上（因为、可是、反而、这才、却……）；做不到的段都要改。')
        msg = msg.replace('每条改后最多比原来多 6 个字', '每条改后最多比原来多 12 个字')
    for k in range(3):
        ans = call(f'pub24FL2{"W" if why else ""}{"N" if nogrow else ""}{"K" if keep else ""}_{w}_{new}'+('' if not k else f'_r{k}'), msg, G6, 'gpt3s', 'public24-fixlines2')
        try:
            fx = {(x['sec'], int(x['idx'])): x for x in parse(ans)['lines']}; n = m = 0
            for s in r['sections']:
                for i, x in enumerate([x for x in s['rows'] if x['kind'] == 'line']):
                    y = fx.get((s['sec'], i))
                    if y and y.get('text'):
                        if len(y['text']) > len(x['text']) + grow: m += 1; continue
                        x['text'] = y['text']; x['keys'] = [k2 for k2 in y.get('keys') or [] if k2 and k2 in y['text']] or x.get('keys', []); n += 1
            wr(p, r); to_script(w, new, r); print(w, new, '改了线', n, '超长没采用', m, flush=True); return True
        except Exception as ex: print('不合格', w, new, repr(ex)[:200], flush=True)
    return False


FIXFEEL = """下面是一首钢琴曲视频的屏幕稿。每段有两种行：大字的“线”（一个人经历的事），和小字的“感受碎片”（听的人此刻的感受，按珠子成簇，同一颗珠子的碎片挨在一起）。观众边听边扫，每段屏幕只停留写明的秒数。

两位评委通读整屏后指出了下面的累积问题：近义说法堆在一起、同一个意象或同一个心理结论跨段反复出现、感受和线重复说同一件事。请只修被点到的地方。

改法：
- 同一簇里近义的碎片（说的是同一个印象），只留最具体、最有画面或身体感的那一个，其余删掉。说的是不同东西的碎片不要删。
- 同一个意象或结论在好几段反复出现时，留在它第一次出现、或最具体的那一段；后面的段删掉重复的那一条，或者换成这一簇里本来就有的、这一段特有的细节。
- 感受碎片只是在重说同段线里已经说过的结论时，删掉那一条碎片。
- 线里被点到的重复（比如几段连着说同一个事实），只做最小的改动，让后一段说出这段新的东西；改后不比原来长。
- 硬性要求：每一簇里原有的每颗珠子都至少留一条碎片；不加原来没有的内容；碎片仍是不带标点的短语，最多 8 个字；没被点到的行逐字不动。

只输出 JSON：{"feel":[{"sec":"S01","row":1,"items":[{"text":"……","bead":"S01-B1"}]}],"lines":[{"sec":"S05","idx":0,"text":"……","keys":["……"]}]}
feel 里给出改过的感受行的完整新内容（row 是这一行在该段里的序号），lines 只列改了的线（idx 是这条线在该段线里的序号）。

【评委指出的问题】
{ISSUES}

【屏幕稿】
{SCREEN}
"""


def fix_feel(a):
    """V2.03c（11-06）：按整屏人话评审的累积问题修感受碎片（合并近义堆叠、去跨段重复），每颗珠子至少留一条，碎片不变多。"""
    w, src, new = a; p = S/f'screen_{w}_{new}.json'
    if p.exists(): to_script(w, new, rd(p)); return True
    gentle = os.environ.get('PUB_FF_GENTLE') == '1'   # 11-06：第一版删掉四分之一碎片，覆盖和精细掉到 w23 以下；温和版每行最多删 2 条
    r = rd(S/f'screen_{w}_{src}.json'); win = pub16.windows(w); iss = []
    for j in JUDGES:
        q = S/f'langall{ {"1": "C", "2": "D"}.get(os.environ.get("PUB_LA_CAL", ""), "")}_{w}_{j}_{src}.json'
        if not q.exists(): continue
        d = rd(q)
        for c in d.get('cumulative') or []:
            iss.append(f"- 累积问题（{c.get('severity')}）：{c.get('phenomenon')} 证据：" + '；'.join(f"{e.get('where')}「{e.get('quote')}」" for e in c.get('evidence') or []))
        iss += [f"- {x.get('where')}「{x.get('quote')}」：{x.get('why')}" for x in d.get('issues') or []]
    out = []
    for s in r['sections']:
        a0, b0 = win[s['sec']]; out.append(f"## {s['sec']}（{round(b0-a0)} 秒）"); li = 0
        for k, x in enumerate(s['rows']):
            if x['kind'] == 'line': out.append(f"[行 {k}｜线 idx {li}] {x['text']}"); li += 1
            else: out.append(f"[行 {k}｜感受] " + ' / '.join(f"{i['text']}〈{i['bead']}〉" for i in x['items']))
    msg = FIXFEEL.replace('{ISSUES}', chr(10).join(iss)).replace('{SCREEN}', chr(10).join(out))
    if os.environ.get('PUB_FF_CROSS') == '1':   # 11-06：删同簇近义碎片会让看片盲比掉（16 票 14→9）；CROSS 只去跨段重复的结论和重说线的碎片
        msg = msg.replace('- 同一簇里近义的碎片（说的是同一个印象），只留最具体、最有画面或身体感的那一个，其余删掉。说的是不同东西的碎片不要删。', '- 同一簇里的近义碎片这次不动：它们是珠子本来的细腻。')
        msg = msg.replace('- 硬性要求：', '- 只处理跨段反复出现的同一个结论或同一句话（字面几乎一样的），每处只删后面段里的那一条；一行最多删 1 条。意象本身（水、船、步子）可以多段出现，只要每段说的是不同的样子。' + chr(10) + '- 硬性要求：')
    if gentle: msg = msg.replace('- 硬性要求：', '- 宁可少改：每一行最多删 2 条碎片，只删和同簇另一条几乎同义的；拿不准是不是同义就留着。覆盖和细腻比整洁更要紧。' + chr(10) + '- 硬性要求：')
    for t in range(3):
        ans = call(f'pub24FF{"X" if os.environ.get("PUB_FF_CROSS") == "1" else "G" if gentle else ""}_{w}_{new}'+('' if not t else f'_r{t}'), msg, G6, 'gpt3s', 'public24-fixfeel')
        try:
            d = parse(ans); nf = nl = bad = 0; sec = {s['sec']: s for s in r['sections']}
            for e in d.get('feel') or []:
                row = sec[e['sec']]['rows'][int(e['row'])]; assert row['kind'] == 'feel'
                old = row['items']; beads = {i['bead'] for i in old}; bars = {}
                for i in old: bars.setdefault(i['bead'], i.get('bars'))
                items = [{'text': i['text'].strip(), 'bead': i['bead'], 'bars': bars.get(i['bead'])} for i in e.get('items') or [] if i.get('text')]
                if {i['bead'] for i in items} != beads or len(items) > len(old) or (gentle and len(items) < len(old) - 2) or (os.environ.get('PUB_FF_CROSS') == '1' and len(items) < len(old) - 1) or any(len(i['text']) > 10 or re.search('[，。；、,]', i['text']) for i in items):
                    bad += 1; continue
                row['items'] = items; nf += 1
            for e in ([] if os.environ.get('PUB_FF_NOLINE') == '1' else d.get('lines') or []):   # 11-06：修碎片时改线会拉低线的人话，NOLINE 只动碎片
                L = [x for x in sec[e['sec']]['rows'] if x['kind'] == 'line']; x = L[int(e['idx'])]
                if e.get('text') and len(e['text']) <= len(x['text']):
                    x['text'] = e['text']; x['keys'] = [k2 for k2 in e.get('keys') or [] if k2 and k2 in e['text']] or [k2 for k2 in x.get('keys', []) if k2 in e['text']]; nl += 1
            wr(p, r); to_script(w, new, r); print(w, new, '改了感受行', nf, '不合格没采用', bad, '改了线', nl, flush=True); return True
        except Exception as ex: print('不合格', w, new, repr(ex)[:200], flush=True)
    return False


# 11-07 校准：N09 是给成段文字用的。屏幕上“感受”是散开的短词，同一行是同一刻几位听众各自的感受，观众扫一眼抓关键词；
# 原评审把同簇近义词当“堆叠”判中等，而看片盲比恰恰偏爱这些簇（删同簇近义碎片后 16 票 14→9）。校准版不让同簇近义算累积问题。
LACAL = """

【补充说明：这是视频屏幕，不是文章】
“感受”一行是散在屏幕上的短词，同一行是同一个时刻几位听众各自的感受，观众边听音乐边扫一眼抓关键词，不是逐句读。所以：
- 同一行里几个短词意思相近、互相呼应，是设计如此，不算累积问题，也不要列为局部问题。
- 仍然要找：跨段反复出现的同一个意象或结论；感受只是在重说同段大字已经说过的结论；大字（线/话）本身的人话问题和累积问题。
"""


# 11-07 第二版（两位顾问问诊后一致意见：同簇近义不能一律豁免，要改成有条件判断；原模板“当作一段完整的叙述”要撤掉；轻重要有定义）
def screen_tpl(tpl):
    a = tpl.split('请作为第一次读到它的普通中文读者')[0]
    tpl = tpl.replace(a, """请阅读下面这份视频屏幕稿。

这是一首钢琴曲“边听边看”视频的屏幕文字。每段有两种行：“话”是大字，按段连起来是一条线，写一个人在这首曲子里经历的一件事，希望像一个人平平常常讲自己的经历；“感受”是散在屏幕上的小字短词，同一行是同一个音乐时刻几位听众各自的感受。观众边听音乐边扫屏幕，每段只停留写明的秒数。允许含蓄，不要求补造具体人物、事件或场景。

""")
    tpl = tpl.replace("先从头到尾阅读，把它当作一段完整的叙述，而不是一组需要逐句批改的句子。",
                      "像观众边听边扫那样从头看到尾：大字的话连起来读，是一段完整的叙述；感受行扫一眼抓关键词，不要把感受行和大字串成一篇文章来读，也不要把同一行里几位听众的感受当成一个人在连续复述。")
    tpl = tpl.replace("最后作出整体判断。", """判断“重复”时的原则：相近的表达不等于重复，重复的表达也不一定是问题。只有同时满足下面三条，才算问题：
- 承担的是同一个功能（同一个印象、同一个心理结论），
- 没有带来新的感受、角度或发展（比如强度变化、身体感、画面、此刻特有的细节），
- 确实增加了观众扫屏的负担，或让人觉得“又是这个”。
同一行感受里，几位听众的感受相近、互相呼应，一般是合理的共鸣；但如果几乎是同一句话换了一两个字（例如“身体先记起舞步 / 隐约记起步子”），可以作为局部问题指出。主题在不同段的有意回归、人物反复纠结本身也不算问题，只有没有发展的原地重复才算。

轻重的标准：
- 严重：观众扫屏时会明显觉得整片都在重复，抓不住每段新东西。
- 中等：至少三段里反复出现、且观众扫读时就会察觉“又是这个”，或者在某一屏里明显占掉了新信息的位置。
- 轻微：要仔细逐字读才看得出来，扫读时基本不影响。

最后作出整体判断。""")
    return tpl.replace('"score": 0', '"score": 7')


def lang_all(a):
    """人话：N09 开放评审读整屏（线和感受都读）。PUB_LA_CAL=1 用校准版，结果存 langallC_*。"""
    w, j, tag = a; cal = os.environ.get('PUB_LA_CAL', ''); suf = {'1': 'C', '2': 'D'}.get(cal, ''); p = S/f'langall{suf}_{w}_{j}_{tag}.json'
    if not p.exists():
        tpl = (pub2.EVO/'DAG/prompts/N09_人话_开放评审/模板.txt').read_text(encoding='utf-8')
        text = view_text(w, tag).replace('【', '').replace('】', '').replace('（到时出现）', '')
        msg = tpl.replace('{{', '{').replace('}}', '}').replace('{TEXT}', text)
        if text not in msg: msg += '\n\n'+text
        if cal == '1': msg += LACAL
        if cal == '2': msg = screen_tpl(tpl.replace('{{', '{').replace('}}', '}')).replace('{TEXT}', text)
        for k in range(3):
            ans = call(f'pub24L{suf}_{w}_{j}_{tag}'+('' if not k else f'_r{k}'), msg, JUDGES[j], 'gpt3s', 'public24-langall')
            try: r = parse(ans); wr(p, r); break
            except Exception as ex: print('不合格', w, j, repr(ex)[:150], flush=True)
    r = rd(p); print(w, j, tag, '整屏人话分', r.get('score') or r.get('overall_score'), '局部问题', len(r.get('issues') or []), '累积', [(c.get('phenomenon', '')[:24], c.get('severity')) for c in r.get('cumulative') or []], flush=True)


REV6 = """你是顾问。下面是你第三轮的提示词（附在最后）写出的屏幕稿，以及后来几轮的对照。请再改一次提示词。

【用户最新的原话】
“覆盖而言 我们原来只测了线对珠子的覆盖 那个是优化线 我们这个可能是后一步 是测精简版对于线+珠子的覆盖 你这个珠子看起来少了好多好多”；之前还说过：“长段 连贯的话一定是恶心人的……应该比如线的关键字放大 然后珠子的一些散落感受小一点”；“你这几张截图看起来完全不是人话 之前那些标准还是成立的”；“多种颜色那个还是要保留”。

【对照】
- 新加了只看珠子的严格覆盖：只看屏幕上的感受（不看线），原稿珠子里那个具体的画面、身体感觉、比喻、心里话、转折还在才算留住。
  你第三轮这版：留住 90–98%。把总量压到和现在视频相当的第四轮：49–74%。现在的视频：45–86%。
  也就是说，珠子要保得住，感受就得多、碎、散开；按现在视频的字数压，珠子就会被挤掉。
- 你第三轮这版其余结果：扮观众盲比 7/8 胜过现在的视频；精细体验还在 23–31（现在 12–17）；线的人话 7.5（定稿 7.5–8）；整屏人话 7–8。
- 问题在两处：
  1. 有的感受块把一句话硬切成几块，例如“丰满的声音只剩一条单薄的旋律 / 孤零零地在空中漫无目的游走”，用户说这种不是人话。每块必须自己是一句完整、自然的话或短语，一扫就懂。
  2. 线偏长（平均 26–28 字），一段线也多。线是大字，最贵的注意力在这里：线要短，靠关键词，让人知道是谁、怎么了、为什么；能并的线就并。

【这一轮要做到】
- 珠子：保住你第三轮的覆盖和颗粒度；感受块字小、散开，可以多，但每块自成一句人话，同一种体验不要说两遍，纯音乐描写只在帮观众对上感受时才用。
- 线：比第三轮明显更短、更少，关键词放大；人话不退。
- 每条线选一种情绪色，组和组之间看得出不一样；局部小节用 bars 字段。
- {BUDGET} 仍是每段现在视频的字数，只作参照：线的字数应少于它，感受可以多于它。

规则同前：不提具体作品内容；占位符 {BEADS}、{LINES}、{SECONDS}、{BUDGET} 照原样写；写手只输出：
{FORMAT}

只输出 JSON：{"diagnosis":"三五句","prompt":"新提示词全文"}

【你第三轮的提示词】
{PROMPT}
"""


REV7 = """你是顾问。你上一轮的提示词（附在最后）写出的屏幕稿测完了。下面是几轮的对照，请再改一次提示词。

【用户的原话】
“你这个珠子看起来少了好多好多”；“你这几张截图看起来完全不是人话 之前那些标准还是成立的”；“长段 连贯的话一定是恶心人的……应该比如线的关键字放大 然后珠子的一些散落感受小一点”；“注意力必须最经济”；“多种颜色那个还是要保留”。

【几轮下来，两头都试过了】
- 感受写得少而整（每条线下一两句完整的话）：字数和现在视频相当，但珠子严格覆盖只有 49–74%，看起来珠子少了很多。
- 感受写得全（你上一轮）：珠子严格覆盖 98–100%，线也短了（16–19 字），但全屏是现在的 1.8–1.9 倍，感受基本是把珠子原文按句切开搬上来，甚至留着“第116小节起”这种话；扮观众盲比降到 6/8，评委说比喻一个接一个、读不过来。
- 感受写得碎（把一句话切成几块）：用户说不是人话。

【要的是中间那种】
每块感受是一句很短的口语，只说一个具体的东西：一个画面、一种身体感觉、一句心里话、一个转折。块数可以多，散开放，字小。同一种体验只留一种说法；几种听法里，挑观众一下能对上的那一种或两种，不要全搬。纯音乐描写只在帮观众对上感受时才留，小节号永远不进正文。
好的例子（可以照这个口气）：“鼻子却有点酸”“像挨在一起说悄悄话，不说话也不尴尬”“话到嘴边又咽回去”“像长长呼出一口气，不是想通了，只是争累了”。
不好的例子：“身体不必踩实，交给船底温柔托举”（书面短语）；“丰满的声音只剩一条单薄的旋律 / 孤零零地在空中漫无目的游走”（一句话切成两块）；“第116小节起，音乐像换了一个人开口”（带小节号、照搬原文）。
线保持你上一轮的短，关键词放大，但要让人知道为什么；人话不能退（上一轮线的人话分有 6.5，定稿是 7.5–8）。
总量：{BUDGET} 是每段现在视频的字数。新稿每段大约是它的 1.3 倍：线的字数比现在少，多出来的给感受。

规则同前：不提具体作品内容；占位符 {BEADS}、{LINES}、{SECONDS}、{BUDGET} 照原样写；每条线必须带 emotion；写手只输出：
{FORMAT}

只输出 JSON：{"diagnosis":"三五句","prompt":"新提示词全文"}

【你上一轮的提示词】
{PROMPT}
"""


REV8 = """你是顾问。你上一轮的提示词（附在最后）写出来的感受还是一句一句的完整句子。用户看了说：“看起来完全不碎啊？还是句子？？”

【用户一直要的珠子形态（原话）】
“是否可以珠子就给他全部break开 就比如‘只剩单薄旋律’那一句 就只用单薄 孤零零 漫无目的 是不是就够了”；“珠子散开，线接得上”；“你这个珠子看起来少了好多好多”；“完全不是人话 之前那些标准还是成立的”；“注意力必须最经济”。

【这一轮要改的：感受必须是碎的】
- 每颗珠子拆成好几个碎片，碎片是短词组（大多两到八个字），各自一扫就懂，同一颗珠子的碎片挨在一起，散开放，不排成句子，不用句号。
- 碎片要是口语、有画面或身体感，不是书面词，也不是把一句话从中间切断的半句。
  好：“单薄 / 孤零零 / 漫无目的”“脚下没了底”“鼻子一酸”“话卡在嘴边”“肩挨着肩”“沉默也不尴尬”“像小船漂进雾里”“这幸福是真的吗？”
  不好：“温柔托举”“思绪难以拼凑”“无法解开的结”（书面词）；“丰满的声音只剩一条单薄的旋律 / 孤零零地在空中漫无目的游走”（一句话切两半，每半还很长）；“刚才还想牢牢攥紧，现在手却不知不觉松开了。”（这是句子，不是碎片）。
- 颗粒度靠碎片的数量保住：原稿珠子里每个具体的画面、身体感觉、比喻、心里话、转折，都尽量有一个碎片对得上；同一种体验只要一个碎片；几种听法都要有碎片，不要只留一种。纯音乐描写只在帮观众对上感受时才留，小节号不进正文。
- 一个碎片如果只属于珠子里写明的某几小节，写 bars。

【线】
保持你上一轮的短句（15–20 字左右）、关键词放大、让人知道为什么；人话不能退。每条线带 emotion。

【参照】
现在视频的词就是碎片（一首约 150–180 个），但颗粒度粗：严格看只有约 63% 的珠子要点还在。{BUDGET} 是每段现在视频的字数，新稿每段大约是它的 1.0–1.3 倍，线比现在少，碎片可以比现在多。

规则同前：不提具体作品内容；占位符 {BEADS}、{LINES}、{SECONDS}、{BUDGET} 照原样写；写手只输出：
{FORMAT}
（feel 的 items 里每个 text 就是一个碎片。）

只输出 JSON：{"diagnosis":"三五句","prompt":"新提示词全文"}

【你上一轮的提示词】
{PROMPT}
"""


def revise8(name, base):
    msg = REV8.replace('{FORMAT}', FORMAT).replace('{PROMPT}', (S/f'prompt_{base}.txt').read_text(encoding='utf-8'))
    ans = call(f'pub24_rev8_{name}', msg, G56 if name == 'g56' else G6, 'gpt3s', 'public24-rev'); r = parse(ans) or {}
    (S/f'rev8_{name}.md').write_text(ans or '', encoding='utf-8')
    if r.get('prompt'): (S/f'prompt_{name}8.txt').write_text(r['prompt'], encoding='utf-8')
    print(name, '诊断', (r.get('diagnosis') or '')[:300], '提示词', len(r.get('prompt') or ''), flush=True)


def revise7(name, base):
    msg = REV7.replace('{FORMAT}', FORMAT).replace('{PROMPT}', (S/f'prompt_{base}.txt').read_text(encoding='utf-8'))
    ans = call(f'pub24_rev7_{name}', msg, G56 if name == 'g56' else G6, 'gpt3s', 'public24-rev'); r = parse(ans) or {}
    (S/f'rev7_{name}.md').write_text(ans or '', encoding='utf-8')
    if r.get('prompt'): (S/f'prompt_{name}7.txt').write_text(r['prompt'], encoding='utf-8')
    print(name, '诊断', (r.get('diagnosis') or '')[:300], '提示词', len(r.get('prompt') or ''), flush=True)


def revise6(name, base):
    msg = REV6.replace('{FORMAT}', FORMAT).replace('{PROMPT}', (S/f'prompt_{base}.txt').read_text(encoding='utf-8'))
    if name == 'g6': msg = msg.replace('你第三轮这版：留住 90–98%', '第三轮 GPT-5.6 那版（感受更碎、更多）：留住 90–98%').replace('- 你第三轮这版其余结果：扮观众盲比 7/8', '- 你第三轮这版：扮观众盲比 8/8，原稿要点留住 80–90%，精细体验还在 13–21，线的人话 8；GPT-5.6 那版：盲比 7/8')
    ans = call(f'pub24_rev6_{name}', msg, G56 if name == 'g56' else G6, 'gpt3s', 'public24-rev'); r = parse(ans) or {}
    (S/f'rev6_{name}.md').write_text(ans or '', encoding='utf-8')
    if r.get('prompt'): (S/f'prompt_{name}6.txt').write_text(r['prompt'], encoding='utf-8')
    print(name, '诊断', (r.get('diagnosis') or '')[:300], '提示词', len(r.get('prompt') or ''), flush=True)


def revise3(name, cand):
    from collections import Counter as C
    vs = [rd(p) for p in S.glob(f'vs_*_{cand}_*.json')]; nv = sum(r['better'] == r['seat'] for r in vs)
    why = '\n'.join(f"  - {r.get('regress')}" for r in vs[:6])
    cov = []; miss = []; src = {}
    for w in WORKS:
        for s in rd(R2/f'{w}_src.json')['sections']:
            for b in s['beads']:
                for q in b['points']: src[q['id']] = q['text']
            for l in s['lines']: src[l['id']] = l['text']
        its = {j: {x['id']: x.get('verdict') for x in rd(R3/f'cover_{w}_{j}_{cand}.json')['items']} for j in JUDGES}
        base = {j: {x['id']: x.get('verdict') for x in rd(R3/f'cover_{w}_{j}_w23.json')['items']} for j in JUDGES}
        for j in JUDGES:
            c = C(its[j].values()); b0 = C(base[j].values()); cov.append(f"{w} {j}：留住 {c['留住']}、部分 {c['部分']}、没有 {c['没有']}（现在的视频：{b0['留住']}、{b0['部分']}、{b0['没有']}）")
        both = [i for i in its['g6'] if its['g6'].get(i) == '没有' and its['g56'].get(i) == '没有']
        miss += [f"  - {w} {i}：{src.get(i, '')[:70]}" for i in both[:8]]
    fine = []; flost = []
    for w in WORKS:
        for j in JUDGES:
            p = R3/'audit21'/f'{w}_{j}_{cand}.json'; q = R3/'audit21'/f'{w}_{j}_w23.json'
            if not p.exists(): continue
            F = [f for s in rd(p)['sections'] for f in s.get('fine', [])]; F0 = [f for s in rd(q)['sections'] for f in s.get('fine', [])] if q.exists() else []
            fine.append(f"{w} {j}：在 {sum(f.get('screen') == '在' for f in F)}、变粗 {sum(f.get('screen') == '变粗' for f in F)}、没了 {sum(f.get('screen') == '没了' for f in F)}（现在的视频：在 {sum(f.get('screen') == '在' for f in F0)}、没了 {sum(f.get('screen') == '没了' for f in F0)}）")
            flost += [f"  - {w} {f.get('quote', '')[:60]}（靠{f.get('carrier')}）" for f in F if f.get('screen') != '在' and f.get('matter') == '大'][:4]
    lang = '；'.join(f"{w} {j} {rd(R3/f'lang_{w}_{j}_{cand}.json').get('score')}（定稿的线 {rd(R3/f'lang_{w}_{j}_FINAL.json').get('score')}）" for w in WORKS for j in JUDGES)
    _, ratio, _, _ = stats(cand)
    bc = '；'.join(f"{w} {j} 留住 {sum(x.get('verdict') == '留住' for x in rd(S/f'beadcov_{w}_{j}_{cand}.json')['items'])}/{len(rd(S/f'beadcov_{w}_{j}_{cand}.json')['items'])}" for w in WORKS for j in JUDGES if (S/f'beadcov_{w}_{j}_{cand}.json').exists())
    msg = REV3.replace('{BEADCOV}', bc or '没测').replace('{VS}', f'{nv}/{len(vs)} 选新').replace('{WHY}', why).replace('{COVER}', '；'.join(cov)).replace('{MISSING}', '\n'.join(miss)).replace('{FINE}', '；'.join(fine)).replace('{FINELOST}', '\n'.join(flost)).replace('{LANG}', lang).replace('{RATIO}', str(ratio)).replace('{FORMAT}', FORMAT).replace('{PROMPT}', (S/f'prompt_{cand}.txt').read_text(encoding='utf-8'))
    (S/f'rev3_{name}_msg.txt').write_text(msg, encoding='utf-8')
    ans = call(f'pub24_rev3_{name}', msg, G56 if name.startswith('g56') else G6, 'gpt3s', 'public24-rev'); r = parse(ans) or {}
    (S/f'rev3_{name}.md').write_text(ans or '', encoding='utf-8')
    if r.get('prompt'): (S/f'prompt_{cand}3.txt').write_text(r['prompt'], encoding='utf-8')
    print(name, '诊断', (r.get('diagnosis') or '')[:400], '提示词', len(r.get('prompt') or ''), flush=True)


def beads_text(w):
    rows = []
    for s in rd(R2/f'{w}_src.json')['sections']:
        rows.append(f"\n### {s['sec']}")
        rows += [f"[{b['id']}]（{b['role']}；小节 {b['where']}{'；局部' if any(p['local'] for p in b['points']) else ''}）{b['text']}" for b in s['beads']]
    return '\n'.join(rows)


def lines_text(w): return '\n'.join(f"{s['sec']} {l['id']}：{l['text']}" for s in rd(R2/f'{w}_src.json')['sections'] for l in s['lines'])
def budget(w):
    """每段现在视频（w23）屏幕上的字数，只作参照。"""
    d = rd(R3/f'script_{w}_w23.json'); win = pub16.windows(w)
    return chr(10).join(f"{s['sec']}（{round(win[s['sec']][1]-win[s['sec']][0])} 秒）：现在的屏幕约 {sum(len(l['text']) for g in s['groups'] for l in g['lines'])+sum(len(b['text']) for g in s['groups'] for b in g['beads'])} 字" for s in d['sections'])


def seconds(w): return '\n'.join(f"{k}：{round(b-a)} 秒" for k, (a, b) in pub16.windows(w).items())


def sample():
    s = next(x for x in rd(R2/'op60_src.json')['sections'] if x['sec'] == 'S02')
    d = next(x for x in rd(R3/'script_op60_w23.json')['sections'] if x['sec'] == 'S02')
    return ('定稿的线：\n' + '\n'.join(f"- {l['text']}" for l in s['lines']) + '\n\n定稿的珠子：\n' + '\n'.join(f"- [{b['id']}]（小节 {b['where']}）{b['text']}" for b in s['beads'])
            + '\n\n现在的屏幕（左线右词）：\n' + '\n'.join(' '.join(l['text'] for l in g['lines'])+'  →  '+' / '.join(b['text'] for b in g['beads']) for g in d['groups']))


def adv():
    msg = ADV.replace('{STD}', (pub2.ROOT/'大众版标准.md').read_text(encoding='utf-8').split('## 画面')[0]).replace('{SAMPLE}', sample()).replace('{FORMAT}', FORMAT)
    def one(a):
        name, model = a; ans = call(f'pub24_adv_{name}', msg, model, 'gpt3s', 'public24-adv'); r = parse(ans) or {}
        (S/f'adv_{name}.md').write_text(f"# {name}\n\n## 判断\n{r.get('judgement')}\n\n## 形态\n{r.get('form')}\n\n## 提示词\n{r.get('prompt')}\n", encoding='utf-8')
        if r.get('prompt'): (S/f'prompt_{name}.txt').write_text(r['prompt'], encoding='utf-8')
        print(name, len(ans or ''), '提示词', len(r.get('prompt') or ''), (r.get('judgement') or '')[:300], flush=True)
    with ThreadPoolExecutor(2) as ex: list(ex.map(one, [('g6', G6), ('g56', G56)]))


def to_script(w, tag, r):
    """屏幕稿 → 已有测法用的 script：每个 line 行一组，后面紧跟的 feel 行归它（第一行之前的 feel 归第一组）。"""
    src = {s['sec']: s for s in rd(R2/f'{w}_src.json')['sections']}; out = {'phases': rd(R3/f'script_{w}_w23.json').get('phases', []), 'sections': []}
    for s in r['sections']:
        sec = s['sec']; groups = []; pending = []
        for row in s['rows']:
            if row.get('kind') == 'line':
                groups.append({'rank': '主' if not groups else '次', 'emotion': row.get('emotion') if row.get('emotion') in pub3.EMOTIONS else '悬着', 'lines': [{'text': row['text'], 'keys': row.get('keys') or [], 'from': row.get('from') or []}], 'beads': pending}); pending = []
            else:
                its = [{'text': i['text'], 'keys': [], 'from': [i.get('bead')], 'bead': i.get('bead')} for i in row.get('items', []) if i.get('text')]
                (groups[-1]['beads'] if groups else pending).extend(its)
        if pending and groups: groups[0]['beads'] = pending+groups[0]['beads']
        elif pending: groups = [{'rank': '主', 'emotion': '悬着', 'lines': [], 'beads': pending}]   # 11-08：一段全是散落
        out['sections'].append({'sec': sec, 'groups': groups})
    assert {x['sec'] for x in out['sections']} == set(src), '段不全'
    wr(R3/f'script_{w}_{tag}.json', out); wr(R2/f'script_{w}_{tag}.json', out)


def parse_bars(x):
    if isinstance(x, list) and len(x) == 2: return int(x[0]), int(x[1])
    m = re.findall(r'\d+', str(x or ''))
    return (int(m[0]), int(m[-1])) if m else None


def bead_ranges(w):
    """每颗珠子写明的小节范围（所有数字的最小到最大），再限在所在段内。"""
    out = {}
    for s in rd(R2/f'{w}_src.json')['sections']:
        a0, z0 = [int(x) for x in re.findall(r'\d+', s['bars'])][:2] if re.findall(r'\d+', s['bars']) else (0, 9999)
        for b in s['beads']:
            n = [int(x) for x in re.findall(r'\d+', str(b['where']))]
            out[b['id']] = (max(a0, min(n)), min(z0, max(n))) if n else (a0, z0)
    return out


def write_one(a):
    w, cand = a; p = S/f'screen_{w}_{cand}.json'
    if p.exists(): to_script(w, cand, rd(p)); return True
    tpl = (S/f"prompt_{cand.split('-')[0]}.txt").read_text(encoding='utf-8')
    msg = tpl.replace('{BEADS}', beads_text(w)).replace('{LINES}', lines_text(w)).replace('{SECONDS}', seconds(w)).replace('{BUDGET}', budget(w))
    ids = {b['id'] for s in rd(R2/f'{w}_src.json')['sections'] for b in s['beads']}
    for k in range(3):
        ans = call(f'pub24W_{w}_{cand}'+('' if not k else f'_r{k}'), msg, G6, 'gpt3s', 'public24-write')
        try:
            r = parse(ans); bad = [i.get('bead') for s in r['sections'] for row in s['rows'] if row.get('kind') == 'feel' for i in row.get('items', []) if i.get('bead') not in ids]
            if bad: print(w, cand, '感受没有合法来源', bad[:5], flush=True)
            rng = bead_ranges(w); nb = 0
            for s in r['sections']:
                for row in s['rows']:
                    if row.get('kind') == 'feel':
                        row['items'] = [i for i in row.get('items', []) if i.get('bead') in ids]
                        for i in row['items']:
                            ab = parse_bars(i.get('bars')); lo, hi = rng.get(i['bead'], (None, None))
                            if ab and lo is not None and lo <= ab[0] <= ab[1] <= hi: i['bars'] = list(ab)
                            else:
                                nb += bool(i.get('bars')); i['bars'] = None
                    else: row['keys'] = [x for x in row.get('keys') or [] if x and x in row.get('text', '')]
            if nb: print(w, cand, '小节不在原珠子范围内、已去掉', nb, flush=True)
            wr(p, r); to_script(w, cand, r); return True
        except Exception as ex: print('不合格', w, cand, repr(ex)[:200], flush=True)
    return False


def show(cand, secs=None):
    for w in WORKS:
        r = rd(S/f'screen_{w}_{cand}.json'); rows = [row for s in r['sections'] for row in s['rows']]
        L = [x for x in rows if x['kind'] == 'line']; F = [i for x in rows if x['kind'] == 'feel' for i in x['items']]
        src = {b['id']: b for s in rd(R2/f'{w}_src.json')['sections'] for b in s['beads']}
        loc = {b for b, x in src.items() if any(p['local'] for p in x['points'])}
        print(f"== {w} {cand} 线行 {len(L)} 字 {sum(len(x['text']) for x in L)} 均 {sum(len(x['text']) for x in L)//max(1,len(L))} 逗号/行 {round(sum(len(re.findall('[，；：]', x['text'])) for x in L)/max(1,len(L)),2)} 放大词/行 {round(sum(len(x.get('keys') or []) for x in L)/max(1,len(L)),1)} 感受块 {len(F)} 字 {sum(len(i['text']) for i in F)} 均 {sum(len(i['text']) for i in F)//max(1,len(F))} 用到珠子 {len({i['bead'] for i in F})}/{len(src)} 局部珠子用到 {len({i['bead'] for i in F} & loc)}/{len(loc)}")
        print('  安排：', (r.get('plan') or '')[:240])
        for s in r['sections']:
            if secs and s['sec'] not in secs: continue
            print(' ', s['sec'])
            for x in s['rows']:
                if x['kind'] == 'line': print('    【线】', x['text'], '  放大：', '、'.join(x.get('keys') or []))
                else: print('    　感：', ' / '.join(i['text'] for i in x['items']))


VS = """你是普通观众，边听一首钢琴曲边扫屏幕，没读过任何原文。下面是同一首曲子视频屏幕的两个版本，每段屏幕只停留写明的秒数，你还在听音乐。
版本的排法可能不同：有的是左边一句话、右边一堆短词；有的是从上到下一行话一行感受交替，话里【】中的字放大加亮，感受字小，标“到时出现”的感受只在音乐走到那几小节时才出现。

如果你是观众，哪个版本让你：扫得动、抓得到每段要点、知道这个人为什么这样、感到前后是一件事、感受细腻具体不粗糙？不要因为字多或字少本身加减分，要按你在这几秒里实际能得到的来判断。

只输出 JSON：{"better":"X|Y","regress":"你选的版本有没有哪里明显不如另一个：有/无，写一句","nets":{"scan":"X|Y|平","point":"X|Y|平","why":"X|Y|平","whole":"X|Y|平","fine":"X|Y|平"},"why":"两三句"}

【X】
{X}

【Y】
{Y}
"""


def view_text(w, tag):
    win = pub16.windows(w); rows = []
    if tag.startswith('w'):
        for s in rd(R3/f'script_{w}_{tag}.json')['sections']:
            rows.append(f"\n### {s['sec']}（屏幕停留 {round(win[s['sec']][1]-win[s['sec']][0])} 秒）")
            for g in s['groups']: rows.append('左：'+' '.join(l['text'] for l in g['lines'])+'\n  右：'+' / '.join(b['text'] for b in g['beads']))
        return '\n'.join(rows)
    for s in rd(S/f'screen_{w}_{tag}.json')['sections']:
        rows.append(f"\n### {s['sec']}（屏幕停留 {round(win[s['sec']][1]-win[s['sec']][0])} 秒）")
        loc = set(b for b, x in {b['id']: b for x in rd(R2/f'{w}_src.json')['sections'] for b in x['beads']}.items() if any(p['local'] for p in x['points']))
        for x in s['rows']:
            if x['kind'] == 'line':
                t = x['text']
                for k in sorted(x.get('keys') or [], key=len, reverse=True): t = t.replace(k, f'【{k}】', 1)
                rows.append('话：'+t)
            else: rows.append('感受：'+' / '.join(i['text']+('（到时出现）' if i.get('bars') or i['bead'] in loc else '') for i in x['items']))
    return '\n'.join(rows)


def vs_one(a):
    w, j, tag, seat = a; p = S/f'vs_{w}_{j}_{tag}_{seat}.json'
    if not p.exists():
        a1, b1 = view_text(w, tag), view_text(w, 'w23'); x, y = (a1, b1) if seat == 'X' else (b1, a1)
        for k in range(3):
            ans = call(f'pub24V_{w}_{j}_{tag}_{seat}'+('' if not k else f'_r{k}'), VS.replace('{X}', x).replace('{Y}', y), JUDGES[j], 'gpt3s', 'public24-vs')
            try: r = parse(ans); assert r['better'] in ('X', 'Y'); wr(p, {'seat': seat, **r}); break
            except Exception as ex: print('不合格', repr(ex)[:150], flush=True)
    r = rd(p); new = r['better'] == seat
    print(w, j, seat, '选新' if new else '选旧', {k: ('新' if v == seat else '旧' if v in 'XY' else '平') for k, v in (r.get('nets') or {}).items()}, '|', (r.get('regress') or '')[:90], '|', (r.get('why') or '')[:170], flush=True)
    return w, new, r


def test(tag):
    """覆盖、人话、颗粒度、看片盲比 8 票。"""
    import pub_cover, pub18, pub21
    jobs = [('beadcov', (w, j, tag)) for w in WORKS for j in JUDGES]+[('langall', (w, j, tag)) for w in WORKS for j in JUDGES]+[('cover', (w, j, tag)) for w in WORKS for j in JUDGES]+[('lang', (w, j, tag)) for w in WORKS for j in JUDGES]+[('fine2', (w, j, tag)) for w in WORKS for j in JUDGES]+[('vs', (w, j, tag, s)) for w in WORKS for j in JUDGES for s in 'XY']+[('vsR', (w, j, tag, s)) for w in WORKS for j in JUDGES for s in 'XY']
    def run(job):
        k, a = job
        try:
            if k == 'beadcov': bead_cov(a)
            elif k == 'langall': lang_all(a)
            elif k == 'cover': pub_cover.judge(a)
            elif k == 'lang': pub18.lang_one(a)
            elif k == 'audit': pub21.audit(a)
            elif k == 'fine2': __import__('pub25').judge(a)
            elif k == 'vsR': __import__('vs_order').one(a)   # 11-07：交换顺序的盲比，gate 按配对判
            else: return vs_one(a)
        except Exception as ex: print('出错', k, a, repr(ex)[:200], flush=True)
    with ThreadPoolExecutor(int(os.environ.get('PUB_PAR', '8'))) as ex: res = list(ex.map(run, jobs))
    for w in WORKS: pub18.meter(w, tag)
    pub21.summarize()
    __import__('vs_order').report(tag)
    vs = [x for x in res if x]; print(tag, '看片盲比选新', sum(n for _, n, _ in vs), '/', len(vs), {w: sum(n for ww, n, _ in vs if ww == w) for w in WORKS}, flush=True)


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    c = sys.argv[1]
    if c == 'adv': adv()
    elif c == 'test': test(sys.argv[2])
    elif c == 'fixfeel':
        with ThreadPoolExecutor(2) as ex: print(list(ex.map(fix_feel, [(w, sys.argv[2], sys.argv[3]) for w in WORKS])), flush=True)
    elif c == 'fixlines2':
        with ThreadPoolExecutor(2) as ex: print(list(ex.map(fix_lines2, [(w, sys.argv[2], sys.argv[3]) for w in WORKS])), flush=True)
    elif c == 'fixlines':
        with ThreadPoolExecutor(2) as ex: print(list(ex.map(fix_lines, [(w, sys.argv[2], sys.argv[3]) for w in WORKS])), flush=True)
    elif c == 'precheck':
        for x in sys.argv[2:]: precheck(x)
    elif c == 'gate':
        for x in sys.argv[2:]: gate(x)
    elif c == 'beadcov':
        with ThreadPoolExecutor(8) as ex: list(ex.map(bead_cov, [(w, j, t) for t in sys.argv[2:] for w in WORKS for j in JUDGES]))
    elif c == 'revise4':
        with ThreadPoolExecutor(4) as ex: list(ex.map(lambda a: revise4(*a), [(n, f) for n in ('g6', 'g56') for f in 'sf']))
    elif c == 'revise8':
        with ThreadPoolExecutor(2) as ex: list(ex.map(lambda a: revise8(*a), [('g56', 'g567'), ('g6', 'g67')]))
    elif c == 'revise7':
        with ThreadPoolExecutor(2) as ex: list(ex.map(lambda a: revise7(*a), [('g56', 'g566'), ('g6', 'g66')]))
    elif c == 'revise6':
        with ThreadPoolExecutor(2) as ex: list(ex.map(lambda a: revise6(*a), [('g56', 'g5623'), ('g6', 'g623')]))
    elif c == 'revise3':
        pairs = [tuple(x.split(':')) for x in sys.argv[2:]] or [('g6', 'g62'), ('g56', 'g562')]
        with ThreadPoolExecutor(len(pairs)) as ex: list(ex.map(lambda a: revise3(*a), pairs))
    elif c == 'stats':
        for x in sys.argv[2:]: print(x, stats(x))
    elif c == 'revise':
        with ThreadPoolExecutor(2) as ex: list(ex.map(lambda a: revise(*a), [('g6', 'g56'), ('g56', 'g6')]))
    elif c == 'write':
        with ThreadPoolExecutor(2) as ex: print(list(ex.map(write_one, [(w, sys.argv[2]) for w in WORKS])), flush=True)
        show(sys.argv[2], ['S02', 'S05'])
    elif c == 'show': show(sys.argv[2], sys.argv[3:] or None)
