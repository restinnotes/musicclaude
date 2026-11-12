"""R34 回补：修订版更短更平实，但盲比认为丢了推动发展的环节。把两份盲比原话交回，只补该补的。
usage: python round34_restore.py TAG REVISED ORIGINAL
读 v6b2_{w}_{j}_{REVISED}_vs{ORIGINAL}，脚本套用，查形态。路由看 THREAD_ROUTE。"""
import copy, json, os, random, re, sys
from concurrent.futures import ThreadPoolExecutor
os.environ.setdefault('JV', '2')
import pipe, screen_flow as F, v6fix as V

PROMPT = """下面是同一条“线”的两个版本（一个人在这首曲子里经历的一件事，按音乐段落分段写成条目），后面是听感记录（珠子）和评委的逐段比较。

【修订版】比原版短，口气更平常，重复也少，几位评委都认可这一点。
但评委认为它删过了头：有些真正推动发展的环节没了，后面的转折和决定少了来由，有些听感也没了着落。

你的任务：在修订版上补回确实该回来的东西，让它既保住现在的口气和简洁，又不丢人物真正走过的路。

怎么判断该不该补：
- 该补：转折或决定前的那一步；人物走到新地方的那个念头；这一段某种听感唯一的落脚处。
- 不该补：只是重说前面说过的意思；只是把同一个心理动作再走一遍。评委列的“丢失”不一定都该回来，你自己判断。
- 优先改写修订版已有的一条，把缺的意思带进去；确实放不下才新增一条。

怎么写：
- 用修订版的口气：平常人讲自己的事，写他此刻具体在乎什么、怕什么，少用概括心理的词，不替他总结；不要照搬原版的说法，原版的说法如果本身就平常可以用。
- 不新增事件、前史、对白、物件、第三人和对方的新举动；不把珠子的画面和情节写成真的发生的事。
- 每段 2–4 条，每条一句。没动的条目一字不动。整篇尽量不超过原版字数的九成。

【修订版】（方括号里是条目编号）
{REVISED}

【原版】
{ORIGINAL}

【珠子】
{BEADS}

【评委的比较】（“新”指修订版，“旧”指原版）
{JUDGES}

只输出 JSON：
{{"edits":[{{"id":"S05-1","op":"replace","text":"改后的一句"}},{{"id":"S13-1","op":"insert_after","text":"新增的一句"}},{{"id":"S09-2","op":"delete"}}],"note":"一句话说补了什么"}}"""


def judges(w, revised, original):
    out = []
    # 正反盲比的票优先（v6b3），没有再用旧的单向票（v6b2）
    runs = [(f'v6b3_{w}_{j}_{revised}_vs{original}_{s}', s == 'newX') for j in ('g6', 'g56') for s in ('newX', 'newY')]
    if not any(os.path.exists(f'runs/{r}/output.txt') for r, _ in runs):
        runs = [(r, random.Random(r).random() < .5) for r in (f'v6b2_{w}_{j}_{revised}_vs{original}' for j in ('g6', 'g56'))]
    for rid, flip in runs:
        d = V.parse(rid) if os.path.exists(f'runs/{rid}/output.txt') else None
        if not d:
            continue
        new, old = ('X', 'Y') if flip else ('Y', 'X')
        name = {new: '新', old: '旧', '差不多': '差不多'}
        def swap(s):
            return s.replace(f'{new}', '新').replace(f'{old}', '旧') if isinstance(s, str) else s
        secs = [{'sec': s['sec'], 'alone': name.get(s.get('alone')), 'alone_why': swap(s.get('alone_why')),
                 'cover': name.get(s.get('cover')), 'cover_why': swap(s.get('cover_why')),
                 '新版丢了': [swap(x.get('what')) for x in s.get(f'lost_in_{new}') or []]} for s in d['sections']]
        out.append({'overall': swap(d.get('better_why')), 'sections': secs})
    return json.dumps(out, ensure_ascii=False, indent=0)


def clean(text):
    # 输入里带引用标记，模型偶尔抄进正文：〔1–3 ②〕[S01-2]
    return re.sub(r'\s*\[S\d+-\d+\]', '', re.sub(r'\s*〔[^〕]*〕', '', text)).strip()


def apply(w, tag, revised, answer):
    g = copy.deepcopy(V.graph_of(w, revised))
    for e in answer.get('edits', []):
        if 'text' in e:
            e['text'] = clean(e['text'])
        ids = e['id'].replace('＋', '+').split('+')
        e['id'] = ids[0]
        extra = ids[1:]
        for s in g['segments']:
            for k, it in enumerate(list(s['items'])):
                if it['id'] == e['id']:
                    if e['op'] == 'replace':
                        it['text'] = e['text']; it['key'] = e['text'][:8]
                    elif e['op'] == 'delete':
                        s['items'].remove(it)
                    elif e['op'] == 'insert_after':
                        n = len(s['items']) + 1
                        new_id = f"{s['sec']}-{n + 10}"
                        s['items'].insert(s['items'].index(it) + 1,
                                          {'id': new_id, 'text': e['text'], 'key': e['text'][:8], 'follows': False, 'explains': [], 'cite': []})
                if it['id'] in extra:
                    s['items'].remove(it)
    alive = {i['id'] for s in g['segments'] for i in s['items']}
    for s in g['segments']:
        if not 2 <= len(s['items']) <= 4:
            raise ValueError(f"{w} {s['sec']}: {len(s['items'])} 条")
        for it in s['items']:
            it['cite'] = [c for c in it.get('cite', []) if c in alive]
    V.tidy(g)
    rows = json.loads((V.OUT / f'{w}_{revised}.json').read_text(encoding='utf-8'))['rows']
    (V.OUT / f'{w}_{tag}.json').write_text(json.dumps({'graph': g, 'rows': rows, 'base': f'{revised} 回补'}, ensure_ascii=False, indent=1), encoding='utf-8')
    (V.OUT / f'{w}_{tag}.md').write_text(f"# {w}｜线（{tag}）\n\n" + V.view(g), encoding='utf-8')
    print(w, tag, '字', sum(len(i['text']) for s in g['segments'] for i in s['items']), '条', len(alive), answer.get('note', '')[:120], flush=True)


def one(tag, revised, original, w):
    msg = PROMPT.format(REVISED=V.view(V.graph_of(w, revised), ids=True), ORIGINAL=V.view(V.graph_of(w, original)),
                        BEADS=V.beads(w), JUDGES=judges(w, revised, original))
    apply(w, tag, revised, pipe.call(f'sc{tag}_{w}_A6', msg, 'g6', tag))


if __name__ == '__main__':
    F.configure()
    tag, revised, original = sys.argv[1:4]
    works = sys.argv[4].split(',') if len(sys.argv) > 4 else F.WORKS
    with ThreadPoolExecutor(max_workers=2) as pool:
        list(pool.map(lambda w: one(tag, revised, original, w), works))
