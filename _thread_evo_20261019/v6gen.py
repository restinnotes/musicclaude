"""10-31 general pipeline (user: "我们不能只是把某一个作品修好就行 我们需要让他能够泛化地修好"). Everything here is piece-agnostic;
no hand-written notes. What reading Op.61 taught (Center's 旧梦 drifted into 亲近 over several rewrites, 2/78 items in v6 ->
15/44 in f8) becomes three general steps:
  gloss : from the ORIGINAL line (v6) and its Center, extract what each part of the Center refers to in this line, in the
          original's own terms (gl_<w>).
  write : one rewrite of a base line combining everything learned (plain speech; merge meanings not words; relate to beads, not
          explain; one thing per item; in-sentence mention + item-level cite; a directed exploration — each stage tries a way,
          finds where it stops working, carries that on; returns say what is new; 没在想 lived, not deliberated; no closing list
          of principles) + the glossary as a hard constraint (no narrowing / swapping) (gw_<w>_<out>).
  fix   : notes ONLY from judges' automatic output on the written line — line-alone weak segments, checklist items both judges
          call lost, beads both coverage judges call 相反, glossary-drift findings (v6drift.py) (gx_<w>_<out>).
usage: python v6gen.py gloss | write <base> <out> | fix <base> <out>"""
import json, sys
import covjudge, evo, v6fix as V

GLOSS = """下面是肖邦{NAME}的一条“线”（Thread）：一个人在这首曲子里经历的一件事，按段写成关系图，开头是这件事的 Center（贯穿全曲的那个问题）。
请把 Center 拆成几个部分（Center 里的每个名词短语，以及说它们怎样相关的那部分），说出每一部分在这条线里具体指什么——用这条线自己的说法，尽量完整（它包括哪几面、为什么对他重要），
并写出改写时最容易把它改窄或换掉的方式（例如把一整种生活缩成其中一面）。只根据这条线，不要加线里没有的东西。

【线】
{LINE}

只输出 json：
```json
{{"terms": [{{"term": "……", "means": "……", "facets": ["……"], "do_not_narrow_to": ["……"]}}]}}
```"""

WRITE = """下面是肖邦{NAME}的一条“线”（Thread）：一个人在这首曲子里经历的一件事，按段写成条目，每段标了小节和他此刻与整件事（Center）的关系。
这条线会和另一批人写的听感记录（珠子）放在一起读：珠子写此刻听到、感到的样子；线讲他自己的经历，作用是把这些听感串起来——意思和珠子大体接近、让读的人感受到那是一种什么处境就够了，不必逐条去“解释”某一种感受。线自己也要读得通。

请把它改写一遍，内容沿用，改的是写法：
1. 说人话：像一个人平平常常讲自己的事，句子完整自然、有主语、用口语；不要提纲式、电报式、文言式的短句，不要为了省字把话压紧。
2. 压缩靠合并意思，不靠删字：一件事能用一句话说清的，不要拆成好几句；几条说同一件事的合成一条；可有可无的删掉。但一条只说一件事：不同的事分开，不要用分号把几件事串进一条。每条一般二三十字、最多五十字；一段通常两到四条。全文不超过 {N} 个字。
3. 写成一场有方向的探索，不是在迷宫里来回打转：每个阶段读者要看得出他这回在试什么办法、走下去在哪里不管用了（或者给了他什么），然后带着这个进入下一段。回到以前到过的地方，要说出这次哪里不一样、他现在多知道了什么；“又”只用在真的回到原处。只给自己定规矩、却没有新认识的条目，删掉。不要用“试”“发现”这种标签，用他自己的话。
4. 标“没在想”的段落，他是真的没在权衡：写他沉在什么里、在做什么，前因接得上即可，不要替他想道理。结尾不要收成一串原则，写他走到这里手里实际剩下了什么、还不知道什么。
5. 不用“提供理由 / 说明 / 限制 / 仍在起作用”之类的关系标签。某条确实因为前面某一条才这样，就在句子里用平常话直接提到那件事，并在 cite 写那一条的编号；只是主题相近的不提。每段开头要看得出他为什么从上一段走到这里，用自然的因果说出来，不靠重复上一段末句衔接，也不写“这时”“接着”这类空连接词。
6. Center 的每一部分在这条线里指什么，见下面的【Center 各部分指什么】。改写时必须守住：不能把它改窄（只剩其中一面）、换成别的东西，或者用更具体的日常事情替代它。
7. 不写总结句、整齐的对照句、哲理句，不由作者替他宣布“他终于明白”；不写声音、画面、身体感受；第三人称“他”；不新增线里没有的事件、人物、背景。段落、小节、每段与 Center 的关系都不变。
编号规则：条目按你写出的顺序编号，第 1 段是 S01-1、S01-2……；cite 只能写前面段落里你写出的条目编号。

Center：{CENTER}

【Center 各部分指什么】
{GLOSS}

【现在的线】（方括号里是旧条目编号；← 后面是旧写法的关系标签，改写时去掉）
{LINE}

只输出 json：
```json
{{"segments": [{{"sec": "S01", "items": [{{"text": "……", "cite": []}}]}}]}}
```"""

FIX = """下面是肖邦{NAME}的一条“线”（Thread）。写法已经定了：像一个人平平常常讲自己的事，句子完整自然；一条只说一件事，最多五十字；有方向地往前走——每一步试什么、在哪里走不通、带走什么，回到老地方要说出这次哪里不同；“没在想”的段落不替他想道理；某条因为前面某一条才这样，就在句子里直接提，并在 cite 写那一条的编号；不用关系标签；不写声音、画面、身体感受；不新增事件、人物、背景；第三人称“他”；Center 各部分的意思守住，不改窄、不换掉。

评委（看不到彼此）对这一版指出了下面这些问题，按段列出：
{NOTES}

请只改上面点到的段落，把问题改掉；能并进现有条目就并，不要为了补而写成长句。如果同一段的几条意见互相矛盾（例如几种听感方向相反），取和线前后最连得上的那一种，不要硬塞进去。没点到的段落一字不改，照原样输出。
编号规则同前：第 1 段是 S01-1、S01-2……；cite 只能写前面段落里的条目编号。

Center：{CENTER}

【Center 各部分指什么】
{GLOSS}

【现在的线】（方括号里是条目编号，〔〕里是引用的前文）
{LINE}

只输出 json（全部段落）：
```json
{{"segments": [{{"sec": "S01", "items": [{{"text": "……", "cite": []}}]}}]}}
```"""


GT = __import__("os").environ.get("GLOSS_TAG", "")      # 10-31: gloss of another base line (DAG run), ids gl_<w>_<tag>
GID = lambda w: f"gl_{w}_{GT}" if GT else f"gl_{w}"


# 11-01 (user: the model copies the sentence shapes it has already written; open reviews: almost every item "他＋心理动词＋判断",
# 想…又怕…, …也…, the same insight re-explained in neighbouring segments). PLAIN_RULE goes into the writing step itself
# (WRITE_PLAIN=1) — a hint, not an assigned shape (assigned shapes, N09v, read as contrived).
PLAIN_RULE = """8. 句式：不要让大多数条目都是“他＋心理动词（想、怕、觉得、明白）＋判断”；能直接说出那件事、那个念头的，就直接说。同一种句式（例如“想……又怕……”“……也……”“越……越……”“不再……”）不要在相邻条目里重复。一个认识说过一次，后面要用就在句子里提一下并 cite，不要在相邻段落再完整说一遍。不要为了变化而变化，平直的句子照样可以用；不加口语填充词和夸张说法。"""

# Per-segment writing (WRITE_SEG): each segment in its own call, in parallel; the model sees the whole old line as CONTENT
# but none of the newly written sentences, so there is nothing of its own to imitate. Items carry src (old item ids);
# cites are written as old ids and mapped by the script to the new item that carries that src.
SEG = """下面是肖邦{NAME}的一条“线”（Thread）的旧写法：一个人在这首曲子里经历的一件事，按段写成条目。现在要一段一段地重写，你这次只写其中一段：{SEC}（{BARS} 小节，他此刻与整件事的关系：{REL}）。
这条线会和另一批人写的听感记录（珠子）放在一起读：线讲他自己的经历，作用是把这些听感串起来，意思大体接近即可，不必逐条解释某一种感受；线自己也要读得通。

写法要求：
{RULES}

只写 {SEC} 这一段：内容来自旧写法里这一段的条目（必要时可以参考前后段的意思来接上，但不要写进别段的事）。每条写出它来自旧写法的哪几条（src，写旧编号），以及它在句子里提到的前文（cite，写前面段落的旧编号）。

Center：{CENTER}

【Center 各部分指什么】
{GLOSS}

【旧写法的整条线】（方括号里是旧编号）
{LINE}

只输出 json：
```json
{{"items": [{{"text": "……", "src": ["S03-2"], "cite": ["S01-1"]}}]}}
```"""


def gloss_text(w):
    e = V.parse(GID(w)) or {}
    return "\n".join(f"- {t.get('term')}：{t.get('means')}" + (f"（包括：{'；'.join(t.get('facets') or [])}）" if t.get("facets") else "")
                     + (f"；不要改窄成：{'、'.join(t.get('do_not_narrow_to') or [])}" if t.get("do_not_narrow_to") else "")
                     for t in e.get("terms") or [])


def gloss():
    evo.run_parallel([(w, (lambda w=w: evo.done(GID(w)) or evo.call(GID(w), GLOSS.format(NAME=covjudge.NAME[w], LINE=V.view(V.v6(w) if not GT else V.graph_of(w, GT))),
                                                                       model=evo.G6, meta={"stage": "v6-gloss"}))) for w in ("op60", "op61")], 2)
    for w in ("op60", "op61"):
        print(w, "\n" + gloss_text(w), flush=True)


def build(w, base, out, e, allow_empty=False):
    """allow_empty: only for steps that legitimately change a few segments (fixlost / revert). 10-31: a failed model call used
    to fall through here and copy the base unchanged as if it were the rewrite (Op.61 d1) — now it stops the DAG."""
    if not allow_empty and not (e or {}).get("segments"):
        raise RuntimeError(f"{w} {out}: the model returned nothing usable; not copying {base} forward")
    g = V.graph_of(w, base); got = {s.get("sec"): s for s in e.get("segments") or []}
    G = {"center": g["center"], "segments": []}; kept = []
    for s in g["segments"]:
        n = got.get(s["sec"])
        if not n or not n.get("items"):
            kept.append(s["sec"]); G["segments"].append(json.loads(json.dumps(s))); continue
        seen = {it["id"] for x in G["segments"] for it in x["items"]}
        items = [{"id": f"{s['sec']}-{k}", "text": it["text"], "key": it["text"][:8], "follows": False, "explains": [],
                  "cite": [c for c in it.get("cite") or [] if isinstance(c, str)]} for k, it in enumerate(n["items"], 1)]
        links = [{"from": c, "to": it["id"], "rel": "引用"} for it in items for c in it["cite"] if c in seen]
        G["segments"].append({"sec": s["sec"], "bars": s["bars"], "relation": s.get("relation"), "items": items, "because": links})
    V.tidy(G)
    rows = json.loads((V.OUT / f"{w}_{base}.json").read_text(encoding="utf-8"))["rows"]
    json.dump({"graph": G, "rows": rows, "base": f"{base} → {out}（通用流程）"}, open(V.OUT / f"{w}_{out}.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    W = "Op.60" if w == "op60" else "Op.61"
    (V.OUT / f"{w}_{out}.md").write_text(f"# {W}｜线（{out}；不标关系，前文在句中直接提，〔〕里是出处：小节和第几条）\n\n" + V.view(G), encoding="utf-8")
    return G, kept


def write(base, out):
    def piece(w):
        g = V.graph_of(w, base); C = sum(len(i["text"]) for s in g["segments"] for i in s["items"])
        rid = f"gw_{w}_{out}"
        if not evo.done(rid):
            T = WRITE.replace("\n编号规则：", "\n" + PLAIN_RULE + "\n编号规则：") if __import__("os").environ.get("WRITE_PLAIN") else WRITE
            evo.call(rid, T.format(NAME=covjudge.NAME[w], N=int(C * 0.65 // 100 * 100), CENTER=g["center"], GLOSS=gloss_text(w),
                                       LINE=V.view(g, ids=True, center=False)), model=evo.G6, meta={"stage": "v6-genwrite"})
        G, kept = build(w, base, out, V.parse(rid) or {})
        T = [i["text"] for s in G["segments"] for i in s["items"]]
        print(w, out, "条目", len(T), "字数", sum(map(len, T)), f"（原 {C}）", "没写出的段", kept, flush=True)
    evo.run_parallel([(w, (lambda w=w: piece(w))) for w in ("op60", "op61")], 2)


def write_seg(base, out):
    rules = WRITE.split("请把它改写一遍，内容沿用，改的是写法：")[1].split("编号规则：")[0].strip() + "\n" + PLAIN_RULE
    rules = rules.replace("全文不超过 {N} 个字。", "这一段和旧写法相比要压缩，大约旧写法这段字数的六成。").replace("{{", "{").replace("}}", "}")
    def piece(w):
        g = V.graph_of(w, base); line = V.view(g, ids=True, center=False); jobs = []
        for s in g["segments"]:
            rid = f"gs_{w}_{out}_{s['sec']}"
            if not evo.done(rid):
                msg = SEG.format(NAME=covjudge.NAME[w], SEC=s["sec"], BARS=s["bars"], REL=s.get("relation") or "", RULES=rules, CENTER=g["center"], GLOSS=gloss_text(w), LINE=line)
                jobs.append((rid, (lambda rid=rid, msg=msg: evo.call(rid, msg, model=evo.G6, meta={"stage": "v6-genwrite-seg"}))))
        evo.run_parallel(jobs, 8)
        segs, owner, missing = [], {}, []
        for s in g["segments"]:
            its = (V.parse(f"gs_{w}_{out}_{s['sec']}") or {}).get("items") or []
            if not its:
                missing.append(s["sec"])
            for k, it in enumerate(its, 1):
                nid = f"{s['sec']}-{k}"
                for o in it.get("src") or []:
                    owner.setdefault(o, nid)
            segs.append({"sec": s["sec"], "items": its})
        if missing:
            raise RuntimeError(f"{w} {out}: segments not written {missing}")
        for x in segs:   # old-id cites -> the new item that carries that old item (only earlier segments)
            for it in x["items"]:
                it["cite"] = sorted({owner[c] for c in it.get("cite") or [] if c in owner and owner[c].split("-")[0] < x["sec"]})
        G, _ = build(w, base, out, {"segments": segs})
        T = [i["text"] for s in G["segments"] for i in s["items"]]
        print(w, out, "逐段写：条目", len(T), "字数", sum(map(len, T)), flush=True)
    evo.run_parallel([(w, (lambda w=w: piece(w))) for w in ("op60", "op61")], 2)


def notes_for(w, base):
    N = {}
    add = lambda sec, x: N.setdefault(sec, []).append(x)
    al = json.loads((V.OUT / f"alone_{base}.json").read_text(encoding="utf-8"))
    for k, v in al.items():
        if k.startswith(w):
            for x in v.get("weak_secs") or []:
                add(x[0], f"只读线时“{x[1]}”：{x[2]}")
    ck = json.loads((V.OUT / f"checklist_{base}.json").read_text(encoding="utf-8")).get(w) or {}
    K = {k["id"]: k for k in json.loads((V.OUT / f"checklist_{w}.json").read_text(encoding="utf-8"))["items"]}
    for kid in ck.get("lost_both") or []:
        add(K[kid]["sec"], f"原来那一版说清、两位评委都认为这一版丢了的内容：{K[kid]['what']}")
    opp = {}
    for j in V.JUDGES:
        for x in (V.parse(f"cov_{w}_{j}_{base}") or {}).get("beads") or []:
            if x.get("status") == "相反":
                opp.setdefault((x["sec"], x["bead"]), []).append(x.get("why", ""))
    for (sec, b), whys in opp.items():
        if len(whys) == len(V.JUDGES):
            add(sec, f"线和这一段的听感方向相反（两位评委都这么判）：{whys[0]}")
    dr = V.OUT / f"drift_{base}.json"
    if dr.exists() and __import__("os").environ.get("FIX_USE_DRIFT"):    # 10-31: drift judge too unstable to drive fixes (g2: untouched segments newly flagged); monitor only
        for x in (json.loads(dr.read_text(encoding="utf-8")).get(w) or []):
            add(x["sec"], f"Center 的意思被改窄或换掉：{x['why']}")
    return N


def fix(base, out):
    def piece(w):
        g = V.graph_of(w, base); N = notes_for(w, base); bars = {s["sec"]: s["bars"] for s in g["segments"]}
        rid = f"gx_{w}_{out}"
        if N and not evo.done(rid):
            nt = "\n".join(f"- {sec}（{bars.get(sec, '')} 小节）：\n" + "\n".join(f"  · {x}" for x in xs) for sec, xs in sorted(N.items()))
            evo.call(rid, FIX.format(NAME=covjudge.NAME[w], NOTES=nt, CENTER=g["center"], GLOSS=gloss_text(w), LINE=V.view(g, ids=True, center=False)),
                     model=evo.G6, meta={"stage": "v6-genfix"})
        e = V.parse(rid) or {} if N else {}
        # untouched segments must come back word for word; if not, keep the base text
        got = {s.get("sec"): s for s in e.get("segments") or []}
        for s in g["segments"]:
            n = got.get(s["sec"])
            if s["sec"] not in N and n and [i.get("text") for i in n.get("items") or []] != [i["text"] for i in s["items"]]:
                got[s["sec"]] = {"sec": s["sec"], "items": [{"text": i["text"], "cite": [b["from"] for b in s["because"] if b.get("to") == i["id"] and b.get("rel") == "引用"]} for i in s["items"]]}
        G, kept = build(w, base, out, {"segments": list(got.values())} if got else {})
        print(w, out, "按评委意见改的段", sorted(N), "字数", sum(len(i["text"]) for s in G["segments"] for i in s["items"]), flush=True)
    evo.run_parallel([(w, (lambda w=w: piece(w))) for w in ("op60", "op61")], 2)


if __name__ == "__main__":
    a = sys.argv[1:]
    {"gloss": lambda: gloss(), "write": lambda: write(a[1], a[2]), "writeseg": lambda: write_seg(a[1], a[2]), "fix": lambda: fix(a[1], a[2])}[a[0]]()
