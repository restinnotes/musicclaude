"""R45 重新标段落关系：改过正文后，每段的“没在想/还说不清/正在面对”要按实际写出的内容重标（标准：按这一段实际写出的内容来标）。
只改标签，正文不动。usage: python round45_label.py TAG SOURCE"""
import json, os, sys
from concurrent.futures import ThreadPoolExecutor
os.environ.setdefault('JV', '2')
import pipe, screen_flow as F, v6fix as V

PROMPT = """下面是一条“线”：一个人在这首曲子里经历的一件事，按音乐段落分段。整件事（Center）是：{CENTER}

请按每一段实际写出的内容，标他此刻和 Center 这件事的关系。只看 Center 这件事本身，他在想别的事不算在面对它：
- 没在想：他这时没去想 Center 这件事，注意力在别的感受或别的念头上。
- 还说不清：Center 这件事已经在他心里起作用，但他还没看清它，只是隐约不安、说不出是什么。他能说清自己怕别的什么，并不等于看清了这件事。
- 正在面对：他清楚意识到 Center 这件事本身，正在为它权衡、挣扎、承受或做决定。

人物通常是一步步走到面对这件事的，标签应该如实反映这种变化；不要因为一段情绪强或想得多就标“正在面对”。只按这一段写了什么来标。

{LINE}

只输出 JSON：{{"relations":[{{"sec":"S01","relation":"还说不清"}}]}}"""


def one(tag, source, w):
    d = json.loads((V.OUT / f'{w}_{source}.json').read_text(encoding='utf-8'))
    g = d['graph']
    line = '\n'.join(f"{s['sec']}：" + ' '.join(i['text'] for i in s['items']) for s in g['segments'])
    answer = pipe.call(f'sc{tag}_{w}_A11', PROMPT.format(CENTER=g['center'], LINE=line), 'g6', tag)
    rel = {x['sec']: x['relation'] for x in answer['relations']}
    if set(rel) != {s['sec'] for s in g['segments']} or set(rel.values()) - {'没在想', '还说不清', '正在面对'}:
        raise ValueError(f'{w}: 标签不全或不合法')
    changed = [s['sec'] for s in g['segments'] if s.get('relation') != rel[s['sec']]]
    for s in g['segments']:
        s['relation'] = rel[s['sec']]
    d['base'] = f'{source}，重标段落关系（改了 {changed}）'
    (V.OUT / f'{w}_{tag}.json').write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding='utf-8')
    (V.OUT / f'{w}_{tag}.md').write_text(f'# {w}｜线（{tag}）\n\n' + V.view(g), encoding='utf-8')
    print(w, tag, '改标签', changed, flush=True)


if __name__ == '__main__':
    F.configure()
    tag, source = sys.argv[1:3]
    with ThreadPoolExecutor(max_workers=2) as pool:
        list(pool.map(lambda w: one(tag, source, w), F.WORKS))
