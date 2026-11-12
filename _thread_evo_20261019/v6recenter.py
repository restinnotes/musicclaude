"""DAG N09r (11-01): swap the Center of a finished line, changing only what the old Center put there.
User: "把最新的人话结果就只去修改 center 的机制不就行了吗" — h23 is best on coverage / lean / plain / alone but still carries the
10-21 Center ("……相互牵制"); the DAG's new Center (N04 v2, chosen2.json) lives only in the q line, which differs from h23 in
everything, so comparing q8w with h23 says nothing. Here one variable changes: the writer sees the line, the old and the new
Center (the sentence only: the N07 glossary of the new Center was extracted from the q line and would carry its plot over),
marks the items whose meaning rests on the old Center's frame, rewrites only those so the segment holds under the new Center,
and leaves every other item word for word. ids rc_<w>_<out>.  usage: python v6recenter.py <base> <out>"""
import json, os, sys
import covjudge, evo, v6fix as V
import center_dag
from v6gen import build
from v6human import line_json

NEW = json.loads((center_dag.OUT / "chosen2.json").read_text(encoding="utf-8"))

P = """下面是肖邦{NAME}的一条“线”：一个人在这首曲子里经历的一件事，按段写成条目（json，每条有编号和它引用的更早条目）。
Center 是读者回头看整首时，把各段组织起来的那件事；它不是每一段都要回应的题目，也不预告发展和结局。
这条线原来的 Center 是：「{OLD}」
现在 Center 换成：「{NEW}」

请只做换 Center 必须的改动，其余一字不动：
1. 先逐条判断：哪些条目的意思建立在旧 Center 的框架上（旧 Center 里的对象、旧 Center 说的那种关系），在新 Center 下不再成立、偏了方向，或者只是在反复重说旧 Center 的那一对关系。只改这些条目。
2. 改的时候，让这一段在新 Center 下说得通，同时保留原条目里不依赖旧 Center 的东西：具体的感受、它的来由、和前后段的衔接、原文的限定（一时、仿佛、还说不清、可能）。保持原来的说话口气和句子长短，说人话。
3. 新 Center 里的词不必每段都出现；不要把 Center 的原话塞进条目。
4. 不加新的事件、人物、场景、对白，不写声音、画面、身体感受；可能的不改成确定的。改动后某条变成多余的重说，可以删；一段至少留一条。
5. 第三人称“他”，另一个人叫“对方”。没改的条目照抄原文（包括 cite）；改过的条目 cite 照原条目填。

【线】
{LINE}

只输出 json：changed 列出改动的原条目编号和一句理由；segments 是改好后的整条线（每段全部条目，没改的照抄）。
```json
{{"changed": [{{"id": "S01-1", "why": "……"}}], "segments": [{{"sec": "S01", "items": [{{"text": "……", "cite": []}}]}}]}}
```"""


def run(base, out):
    def piece(w):
        g = V.graph_of(w, base); rid = f"rc_{w}_{out}"
        if not evo.done(rid):
            evo.call(rid, P.format(NAME=covjudge.NAME[w], OLD=g["center"], NEW=NEW[w], LINE=line_json(g)), model=evo.G6, meta={"stage": "v6-recenter"})
        e = V.parse(rid) or {}
        G, kept = build(w, base, out, e)
        f = V.OUT / f"{w}_{out}.json"; d = json.loads(f.read_text(encoding="utf-8"))
        d["graph"]["center"] = NEW[w]; d["base"] = f"{base} → {out}（只换 Center：{g['center']} → {NEW[w]}）"
        f.write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")
        (V.OUT / f"{w}_{out}.md").write_text(f"# {'Op.60' if w == 'op60' else 'Op.61'}｜线（{out}；{base} 只换 Center）\n\n" + V.view(d["graph"]), encoding="utf-8")
        old = [i["text"] for s in g["segments"] for i in s["items"]]; new = [i["text"] for s in d["graph"]["segments"] for i in s["items"]]
        print(w, out, "改动", len(e.get("changed") or []), "条", [c.get("id") for c in e.get("changed") or []], "条目", len(old), "→", len(new),
              "字数", sum(map(len, old)), "→", sum(map(len, new)), "原样保留", len(set(old) & set(new)), flush=True)
    evo.run_parallel([(w, (lambda w=w: piece(w))) for w in ("op60", "op61")], 2)


if __name__ == "__main__":
    run(sys.argv[1], sys.argv[2])
