"""R36 只修底线没过的段：把这些段掉的珠子交给写的人，同样口气改这几段，别的段一字不动。
usage: python round36_floor.py TAG SOURCE BASE   路由看 THREAD_ROUTE。"""
import json, os, re, sys
os.environ.setdefault('JV', '2')
import pipe, screen_flow as F, v6fix as V, covjudge
import round34_restore as R34

PROMPT = """下面是一条“线”：一个人在这首曲子里经历的一件事，按音乐段落分段写成条目；另有听感记录（珠子）会和线排在一起给读者看。

这条线整体已经很好，口气平常、具体，不要动。只有下面列出的几段，有些珠子的感受在线的这一段里找不到情境相近的原因。

你的任务：只改这几段，让这些听感有个着落。
- 相关就行，不必逐颗解释；一条可以同时接住几颗。
- 不翻译珠子：珠子里的画面、比喻、想象出的情节不能变成线里真的发生的事。写的是他自己的处境和心思，让读者感到这种听感为什么会出现在这里。
- 用这条线现在的口气：平常人讲自己的事，具体，不概括心理，不总结。
- 不新增事件、前史、对白、物件、第三人和对方的新举动；后文已有的内容不要提前说掉；前后要接得上。
- 每段 2–4 条，每条一句；不要写长。
- 只动列出的段。

【线】（方括号里是条目编号）
{LINE}

【要修的段和接不上的珠子】
{TARGETS}

只输出 JSON：
{{"edits":[{{"id":"S03-2","op":"replace","text":"改后的一句"}},{{"id":"S13-1","op":"insert_after","text":"新增的一句"}}],"note":"一句话"}}"""


def status(w, j, tag):
    d = V.parse(f'cov2_{w}_{j}_{tag}')
    return {(x['sec'], str(x['bead'])): x for x in d['beads']}


def failed_sections(w, tag, base):
    state = F.floor_state(tag, base, 'coverage')
    return [m.group(1) for f in state['failures'] for m in [re.match(rf'{w} (S\d+)', f)] if m]


def targets(w, tag, base, secs):
    text = {}
    for b in covjudge.beads(w):
        text[(b['sec'], b['id'].split('-')[-1])] = b
    out = []
    for sec in secs:
        rows = []
        for key, b in text.items():
            if key[0] != sec or b['role'] == '演奏条件':
                continue
            now = [status(w, j, tag)[key] for j in F.JUDGES]
            was = [status(w, j, base)[key]['status'] for j in F.JUDGES]
            if any(x['status'] != '说清' for x in now):
                rows.append(f"- {key[1]}［{b['role']}］{b['text']}\n  评委：" + '；'.join(str(x.get('why') or x.get('reason') or x.get('status')) for x in now))
        out.append(f'### {sec}\n' + '\n'.join(rows))
    return '\n'.join(out)


def main():
    F.configure()
    tag, source, base = sys.argv[1:4]
    for w in F.WORKS:
        secs = failed_sections(w, source, base)
        if not secs:
            R34.apply(w, tag, source, {'edits': [], 'note': '无底线问题，不改'})
            continue
        msg = PROMPT.format(LINE=V.view(V.graph_of(w, source), ids=True), TARGETS=targets(w, source, base, secs))
        answer = pipe.call(f'sc{tag}_{w}_A9', msg, 'g6', tag)
        bad = [e['id'] for e in answer.get('edits', []) if e['id'].split('-')[0] not in secs]
        if bad:
            raise ValueError(f'{w}: 改了没要求的段 {bad}')
        R34.apply(w, tag, source, answer)


if __name__ == '__main__':
    main()
