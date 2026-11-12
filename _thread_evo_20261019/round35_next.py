"""R35 在当前最好版本上继续：
  repair TAG SOURCE  用 SOURCE 自己的开放评审做局部修订（round32 的提示词，deep）
  merge  TAG SOURCE DRAFT  把另一稿里真正往前走的发展吸收进 SOURCE，口气不变
结果用 round34_restore.apply 套用（支持 replace / insert_after / delete），路由看 THREAD_ROUTE。"""
import glob, json, os, random, sys
from concurrent.futures import ThreadPoolExecutor
os.environ.setdefault('JV', '2')
import pipe, screen_flow as F, v6fix as V
import round32_repair as R32, round34_restore as R34

MERGE = """下面是同一个人同一件事的两稿“线”（按音乐段落分段写成条目），后面是听感记录（珠子）和评委对另一稿的评价。

【当前稿】口气好：平常、具体，像一个人在讲自己的事。它的弱点是有些段落原地打转，同一个问题问了又问。
【另一稿】口气偏书面，但有些段落真正往前走了：人物想到了新东西，后面的念头因此不一样。

你的任务：在当前稿上做修改，把另一稿里真正往前走的发展吸收进来，换掉当前稿里原地打转的部分。
- 吸收的是“人物走到了哪里”，不是另一稿的句子；用当前稿的口气重新说，写他具体在乎什么、怕什么，少用概括心理的词。
- 只换打转的地方。当前稿已经写得好的条目、转折和决定一字不动。
- 换完要读得通：前面没出现过的前因要有交代，后面提到的东西要有着落；结尾的决定仍要接得上。
- 不新增事件、前史、对白、物件、第三人和对方的新举动；不把珠子的画面和情节写成真的发生的事。
- 每段 2–4 条，每条一句；整篇不加长。

【当前稿】（方括号里是条目编号）
{SOURCE}

【另一稿】
{DRAFT}

【珠子】
{BEADS}

【评委怎么看另一稿】
{JUDGES}

只输出 JSON：
{{"edits":[{{"id":"S09-1","op":"replace","text":"改后的一句"}},{{"id":"S10-2","op":"insert_after","text":"新增的一句"}},{{"id":"S11-3","op":"delete"}}],"note":"一句话说吸收了什么"}}"""


def own_reviews(w, tag):
    out = []
    for f in sorted(glob.glob(f'runs/eo2_{w}_{tag}_*')):
        d = V.parse(os.path.basename(f))
        if d:
            out.append({'problems': d.get('problems'), 'top3': d.get('top3')})
    return json.dumps(out, ensure_ascii=False, indent=0)


def draft_judges(w, draft):
    out = []
    for j in ('g6', 'g56'):
        rid = f'v6b2_{w}_{j}_{draft}_vsqurefs'
        d = V.parse(rid)
        if d:
            new, old = ('X', 'Y') if random.Random(rid).random() < .5 else ('Y', 'X')
            out.append((d.get('better_why') or '').replace(new, '另一稿').replace(old, '旧稿'))
    return json.dumps(out, ensure_ascii=False)


def repair(tag, source, w):
    g = V.graph_of(w, source)
    msg = R32.PROMPT.format(RULE=R32.RULES[os.environ.get('REPAIR_RULE', 'deep')], LINE=V.view(g, ids=True), BEADS=V.beads(w), REVIEWS=own_reviews(w, source))
    R34.apply(w, tag, source, pipe.call(f'sc{tag}_{w}_A5', msg, 'g6', tag))


def merge(tag, source, draft, w):
    msg = MERGE.format(SOURCE=V.view(V.graph_of(w, source), ids=True), DRAFT=V.view(V.graph_of(w, draft)),
                       BEADS=V.beads(w), JUDGES=draft_judges(w, draft))
    R34.apply(w, tag, source, pipe.call(f'sc{tag}_{w}_A7', msg, 'g6', tag))


if __name__ == '__main__':
    F.configure()
    mode, tag, source = sys.argv[1:4]
    fn = (lambda w: repair(tag, source, w)) if mode == 'repair' else (lambda w: merge(tag, source, sys.argv[4], w))
    with ThreadPoolExecutor(max_workers=2) as pool:
        list(pool.map(fn, F.WORKS))
