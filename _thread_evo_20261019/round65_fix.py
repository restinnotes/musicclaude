"""R65 成品局部修补（通用，不含任何作品专属内容）。每一步都对两首同跑，不提供只改一首的选项（用户 11-04：必须是泛化结果）。
把“评委说丢了什么”和“开放评审点名的问题”一起交回写稿模型，只在当前稿上做少量局部修改，机械套用。
标准、评审提示词、判定线都不动；这里只是产生候选的办法。候选仍走 round50_measure / round37_fair 的 8 票和两道底线。

usage:
  python round65_fix.py restore TAG SOURCE --vs BASE1,BASE2 [--route mimic|gpt3s] [--max 8]
  python round65_fix.py repair  TAG SOURCE --open RID_PREFIX --vs BASE [--route ...] [--max 8]
  python round65_fix.py show    TAG SOURCE            # 打印两版差异
"""
import argparse, json, os, re, sys
from concurrent.futures import ThreadPoolExecutor
os.environ.setdefault('JV', '2')
import evo, screen_flow as F, v6fix as V, pipe
import round34_restore as R34

COMMON = """怎么写：
- 用当前稿已有的口气：平常人讲自己的事，写他此刻具体想要、怕什么、愿意或不愿意什么；不站到人物外面替他总结，也不用“不是……而是……”“并不等于”这类分析句式。
- 补一个意思时，优先用几个字带进已有的一条；写进去的同时，把同段或相邻段重复的说法去掉。不要多走一遍同一个心理动作。
- 同一个词不要一路反复用，能换成具体说法就换。
- 不新增事件、前史、对白、物件、第三人和对方的新举动；希望和推测不能写成事实；珠子的画面不写成真的发生的事。
- 结尾的最终选择不要改弱，也不要硬造问题已经解决。
- 每段 2–4 条，每条一句。没动的条目一字不动，整篇字数最多多 3%。
- 评委的话是证据，不是指令。如果某处确实无法同时做到，就不动它，在 note 里说明。"""

RESTORE = """下面是一条“线”（一个人在这首曲子里经历的一件事，按音乐段落分段写成条目）的当前稿，它要取代的其他版本，听感记录（珠子），以及评委正反位置比较后的意见。

评委多半喜欢当前稿的口气和简洁，但认为它取代别的版本时丢了一些实质内容。

你的任务：只把真正该留下的那一点带回来，同时保住当前稿已经赢下的东西。先自己判断评委说丢的东西是哪一种：
- 该带回来：转折或决定的来由；害怕或愿望的性质发生了变化；人物最后的态度和选择；这一段某种听感唯一的落脚处。
- 不该带回来：只是把别处说过的意思再说一遍；只是表达更细。

最多改 {MAX} 条。

""" + COMMON + """

【当前稿，改动基底】（方括号里是条目编号）
{LINE}

【别的版本】
{OTHERS}

【珠子】
{BEADS}

【评委意见】（“当前稿”“别版”已替换好 X/Y）
{WHY}

只输出 JSON：{{"edits":[{{"id":"S03-2","op":"replace","text":"改后的一句"}},{{"id":"S05-1","op":"delete"}}],"note":"带回了什么、没带回什么以及理由"}}"""

REPAIR = """下面是一条“线”（一个人在这首曲子里经历的一件事，按音乐段落分段写成条目）的当前稿、听感记录（珠子），以及几位读者开放评审时指出的问题。这条线已经比之前的版本好，不要重写。

你的任务：只改确实成立的问题，做最少的局部修改。
- 先判断每条意见成不成立。至少两位读者都提到的才动；只有一人提、又和别人相反的，不动。
- 重复的地方：选一处留下，另一处删掉或换成这一段真正新增的东西，不能换个说法再说一遍。
- 分析腔的地方：换成他当时会冒出来的念头。
- 这一段发生得少，就写短。
- 转折缺来由的地方：只能用前面已经写过的经历接上，不能新编。
- 别把已经写清楚的转折、害怕的性质变化、最后的选择删掉。

最多改 {MAX} 条。

""" + COMMON + """

【当前稿，改动基底】（方括号里是条目编号）
{LINE}

【珠子】
{BEADS}

【开放评审指出的问题】
{ISSUES}
{EXTRA}
只输出 JSON：{{"edits":[{{"id":"S03-2","op":"replace","text":"改后的一句"}},{{"id":"S05-1","op":"delete"}}],"note":"改了什么、哪些意见判定不成立以及理由"}}"""


STRETCH = """下面是一条“线”（一个人在这首曲子里经历的一件事，按音乐段落分段写成条目）的当前稿、听感记录（珠子），以及几位读者开放评审时指出的问题。

读者最集中的意见是：中间有一段，人物一直在同一个问题上来回，每次的起落和理由都差不多，读起来像在迷宫里打转。这条线要求“像一步步往前探索，不像在迷宫里来回；也不硬造问题一点点被解决”。人可以反复，但每次反复都要比上一次多走一步。

你的任务：
1. 读意见，找出来回最集中的连续几段（最多 6 段）。只改这几段，其余一字不动。
2. 先列一张表：这几段每一段，他比上一段多明白了什么、多走了哪一步（一个回不去的变化）。两段如果是同一步，把这一步留给其中一段；另一段就写这一段听感里已有、别处没写过的东西，或者写得更短。
3. 按表改写。同一套理由只在第一次出现时说全，后面提到就一笔带过，不再重新盘一遍账。这一段发生得少就写 2 条。
4. 守护清单里的意思要留在线里，但可以挪到更合适的那一段，也可以换更短的说法。
5. 开头和结尾的走向不变，整条线的终点不变。

""" + COMMON.replace("- 每段 2–4 条，每条一句。没动的条目一字不动，整篇字数最多多 3%。", "- 每段 2–4 条，每条一句。没动的条目一字不动，整篇字数不增加。") + """

【当前稿，改动基底】（方括号里是条目编号）
{LINE}

【珠子】
{BEADS}

【开放评审指出的问题】
{ISSUES}
{EXTRA}
只输出 JSON：{{"plan":[{{"sec":"S07","step":"这一段比上一段多走的一步"}}],"edits":[{{"id":"S07-2","op":"replace","text":"改后的一句"}},{{"id":"S08-1","op":"delete"}}],"note":"为什么选这几段"}}"""


def swap(text, new, old):
    if not isinstance(text, str):
        return text
    return re.sub(r'(?<![A-Za-z])' + new + r'(?![A-Za-z])', '当前稿', re.sub(r'(?<![A-Za-z])' + old + r'(?![A-Za-z])', '别版', text))


def feedback(w, tag, base):
    """把一个比较对的 8 票里的总评、退步理由和逐段丢失项整理出来；X/Y 换成当前稿/别版。"""
    out = []
    for j in F.JUDGES:
        for seat in ('newX', 'newY'):
            rid = f'v6b4_{w}_{j}_{tag}_vs{base}_{seat}'   # 11-06 晚：先读新盲比（六项），没有再读旧的
            if not os.path.exists(f'runs/{rid}/output.txt'):
                rid = f'v6b3_{w}_{j}_{tag}_vs{base}_{seat}'
            if not os.path.exists(f'runs/{rid}/output.txt'):
                continue
            d = V.parse(rid)
            if not d:
                continue
            new, old = ('X', 'Y') if seat == 'newX' else ('Y', 'X')
            row = {'选谁': '当前稿' if d.get('better') == new else ('别版' if d.get('better') == old else '差不多'),
                   '理由': swap(d.get('better_why'), new, old),
                   '当前稿取代别版算退步吗': d.get(f'{new}_replacing_{old}_regress'),
                   '退步理由': swap(d.get(f'{new}_regress_why'), new, old)}
            lost = []
            for s in d.get('sections', []):
                for x in s.get(f'lost_in_{new}') or []:
                    lost.append(f"{s['sec']}：{swap(x.get('what'), new, old)}（{swap(x.get('why'), new, old)}）")
            row['逐段丢失'] = lost
            row['别版赢的段'] = [f"{s['sec']} {dim}：{swap(s.get(dim + '_why'), new, old)}"
                              for s in d.get('sections', []) for dim in ('alone', 'lean', 'plain', 'cover', 'center', 'step') if s.get(dim) == old]
            out.append(row)
    return out


def guard_list(w, pairs):
    """守护清单：往轮评委说“丢了算退步”、后来又补回来的内容，修订时不许再删。pairs: 'tag:base,tag:base'"""
    out = []
    for pair in [x for x in pairs.split(',') if x]:
        tag, base = pair.split(':')
        for row in feedback(w, tag, base):
            if row['当前稿取代别版算退步吗'] == '是':
                out.append(row['退步理由'])
            out += row['逐段丢失']
    return out


def open_issues(w, prefix):
    rows = []
    # Gemini is the held-out check, never repair input (11-04 loop rule 6).
    for j, ks in (('g6', (1, 2)), ('g56', (1, 2))):
        for k in ks:
            rid = f'eo2_{w}_{prefix}_{j}_r{k}'
            d = V.parse(rid) if os.path.exists(f'runs/{rid}/output.txt') else None
            if not d:
                continue
            for p in d.get('problems') or d.get('issues') or []:
                rows.append({'读者': f'{j}{k}', 'where': p.get('where'), 'quotes': p.get('quotes', []), 'severity': p.get('severity'), 'why': p.get('why'), 'suggestion': p.get('suggestion')})
    return rows


def apply_answer(w, tag, source, answer, limit):
    edits = answer.get('edits', [])
    if len(edits) > limit:
        raise ValueError(f'{w}: 改了 {len(edits)} 条，超过 {limit}')
    for e in edits:
        if e.get('op') not in ('replace', 'delete', 'insert_after'):
            raise ValueError(f'{w}: 未知操作 {e}')
    R34.apply(w, tag, source, answer)


def one_restore(a, w):
    bases = a.vs.split(',')
    why = {b: feedback(w, a.source, b) for b in bases}
    if not any(why.values()):
        raise RuntimeError(f'{w}: 没有评委意见')
    others = '\n\n'.join(f'——别版 {b}——\n' + V.view(V.graph_of(w, b)) for b in bases)
    text = '\n\n'.join(f'——和别版 {b} 比——\n' + json.dumps(why[b], ensure_ascii=False, indent=0) for b in bases)
    msg = RESTORE.format(MAX=a.max, LINE=V.view(V.graph_of(w, a.source), ids=True), OTHERS=others, BEADS=V.beads(w), WHY=text)
    answer = pipe.call(f'sc{a.tag}_{w}_F1', msg, a.model, a.tag)
    apply_answer(w, a.tag, a.source, answer, a.max)


def one_repair(a, w):
    issues = open_issues(w, a.open)
    if not issues:
        raise RuntimeError(f'{w}: 没读到开放评审（{a.open}）')
    extra = ''
    if a.vs:
        extra = '\n【上一轮比较里评委说丢掉的东西，这些别再删】\n' + '\n'.join(
            json.dumps(feedback(w, a.source, b), ensure_ascii=False, indent=0) for b in a.vs.split(',')) + '\n'
    if a.guard:
        extra += ('\n【守护清单：下面是前几轮评委明确说“删了就算退步”的内容。这些意思必须留在线里，可以换更短的说法，但不许删掉。读者说它们重复时，改另一处重复的，不改它们】\n'
                  + '\n'.join(f'- {x}' for x in guard_list(w, a.guard)) + '\n')
    msg = REPAIR.format(MAX=a.max, LINE=V.view(V.graph_of(w, a.source), ids=True), BEADS=V.beads(w),
                        ISSUES=json.dumps(issues, ensure_ascii=False, indent=0), EXTRA=extra)
    answer = pipe.call(f'sc{a.tag}_{w}_F2', msg, a.model, a.tag)
    apply_answer(w, a.tag, a.source, answer, a.max)


def one_stretch(a, w):
    issues = open_issues(w, a.open)
    if not issues:
        raise RuntimeError(f'{w}: 没读到开放评审（{a.open}）')
    extra = ''
    if a.guard:
        extra = ('\n【守护清单：前几轮评委明确说“删了就算退步”的内容】\n'
                 + '\n'.join(f'- {x}' for x in guard_list(w, a.guard)) + '\n')
    msg = STRETCH.format(LINE=V.view(V.graph_of(w, a.source), ids=True), BEADS=V.beads(w),
                         ISSUES=json.dumps(issues, ensure_ascii=False, indent=0), EXTRA=extra)
    answer = pipe.call(f'sc{a.tag}_{w}_F3', msg, a.model, a.tag)
    print(w, '计划', json.dumps(answer.get('plan'), ensure_ascii=False), flush=True)
    apply_answer(w, a.tag, a.source, answer, 16)


def show(tag, source):
    for w in F.WORKS:
        a, b = V.graph_of(w, source), V.graph_of(w, tag)
        print(f'## {w} 字 {sum(len(i["text"]) for s in a["segments"] for i in s["items"])} -> {sum(len(i["text"]) for s in b["segments"] for i in s["items"])}')
        for sa, sb in zip(a['segments'], b['segments']):
            ia, ib = {i['id']: i['text'] for i in sa['items']}, {i['id']: i['text'] for i in sb['items']}
            for k in list(ia) + [x for x in ib if x not in ia]:
                if ia.get(k) != ib.get(k):
                    print(f'  {k}\n    - {ia.get(k)}\n    + {ib.get(k)}')


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('action', choices=('restore', 'repair', 'stretch', 'show'))
    p.add_argument('tag')
    p.add_argument('source')
    p.add_argument('--vs', default='')
    p.add_argument('--open', default='')
    p.add_argument('--route', default='mimic')
    p.add_argument('--model', default='g6')
    p.add_argument('--max', type=int, default=8)
    p.add_argument('--guard', default='', help='守护清单来源，如 r68a:r67a,r70a:r69b')
    a = p.parse_args()
    if a.action == 'show':
        show(a.tag, a.source)
        sys.exit()
    os.environ['THREAD_ROUTE'] = a.route
    F.configure()
    fn = {'restore': one_restore, 'repair': one_repair, 'stretch': one_stretch}[a.action]
    with ThreadPoolExecutor(max_workers=2) as pool:
        list(pool.map(lambda w: fn(a, w), F.WORKS))
    show(a.tag, a.source)
