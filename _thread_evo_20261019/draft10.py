"""Node 2 round D10 = P0+ (10-23, PLAN_解释池_20261023.md 四). The d9 drafts are out of the new DAG (user: "修正稿都说了有问题
我们难道还应该把它放到新dag里面吗？跑一次又不难咯"); a new bead-free pool must first cover the beads (covjudge.py).
P0 verbatim + the P0+ rules from the second ChatGPT discussion: several compatible feelings per segment allowed, a reason
that only fits this segment, no plot moves, no Center, five fields per segment (感受/Thread/用到的历史/新增历史/仍未解释).
Two ways of writing x two models x 3:
  c = chained, one call per segment carrying everything written so far (tests the local-attention idea)
  o = one call for the whole piece, same fields
ids: d10{c|o}{6|56}_<work>_r<j> (chained segments: ..._<Sxx>); assembled -> evaluations/draft10/<name>.json
usage: python draft10.py [c|o|all]"""
import json, sys
import evo, gen, node2b, segcheck

W = ("op60", "op61")
R = (1, 2, 3)
OUT = evo.ROOT / "evaluations" / "draft10"
RULES = ("这一次的写法（以这里为准）：\n"
         "1. 先想清楚这一段的感受：它和前面有什么不同？有哪些感受同时成立？以前出现过的东西，在这里有没有不同的分量？"
         "一段里可以有几种相容的感受，不必只挑最主要的一种。\n"
         "2. 再从已经确立的历史出发，找最有说服力的解释：经历过前面那些的人，为什么现在会这样感受？一个理由能解释几种相关的感受，"
         "就不要拆成几步；有几个相容、各有用处的理由，可以一起保留；这一段也可以只是前面的延续，没有新的认识或决定。\n"
         "3. 不要先编好一套心理故事，再让音乐去配合它。每一段都重新判断：这一段究竟有什么值得解释的新东西。"
         "不要让同一个抽象的心理矛盾包办所有段落；如果一个理由放到很多别的段落也同样成立，说明它还没有说出这一段的原因。\n"
         "4. 不要为了让故事往前走而编造自我劝说、提醒自己、突然想通、下决心，也不要编外部事件、物件、场景或对白。"
         "不要把音乐的变化本身当成他心里变化的原因。可以大胆提出你自己的理解——例如一次满足使仍未满足的东西显出来，"
         "后来的经历改变了前面的意义——只要解释这一段的感受确实需要它。\n"
         "5. 开头不要交代人物的过去、性格、习惯，也不要提前说出主题；任何一段都不要预告后面会怎样。\n"
         "6. 用普通人一遍能听懂的话说原因。不要描写声音、旋律、和声、意象，不写哲理总结。\n")
FIELDS = ('"feel": "这一段最值得解释的感受和变化，可以有几个侧面，一两句", '
          '"thread": "用尽可能少、但足以说清理由的话，解释这一段为什么会这样感受", '
          '"used": "具体依赖了前面哪些经历；没有就写 无", '
          '"new": ["这一段真正建立、以后可能起作用的历史，每条一句；没有就空列表"], '
          '"unexplained": "这条理解还解释不了的重要感受；没有就写 无"')
ONE = (RULES + "\n按上面给定的分段，从第一段写到最后一段。前面段落里确立的历史，后面可以用。每段写五项，"
       "只输出一个 json 代码块：\n```json\n{\"sections\": [{\"bars\": \"1–3\", " + FIELDS + "}]}\n```\n")


def segs(w):
    return segcheck.seg.load(w)["segments"]


def so_far(done_):
    if not done_:
        return "（这是第一段，前面还没有内容。）"
    return "\n\n".join(f"第{i + 1}段（{x['bars']}小节）\n感受：{x['feel']}\nThread：{x['thread']}\n新增历史：{'；'.join(x.get('new') or []) or '无'}"
                       for i, x in enumerate(done_))


def chained_msg(w, k, done_):
    s = segs(w)[k]
    return (gen.render("P0", w, "note") + "\n\n---\n现在不一次写完整篇，而是一段一段写。这一次只写第"
            f"{k + 1}段（第{s['start']}–{s['end']}小节）。前面各段你已经写好了，列在下面；这一段写完以后还会继续写后面的段落，"
            "所以不要预告后面。\n\n" + RULES + "\n【前面各段已经写下的】\n" + so_far(done_) +
            "\n\n只输出一个 json 代码块：\n```json\n{" + FIELDS + "}\n```\n")


def parse(rid):
    try:
        return evo.parse_json(evo.output(rid))
    except Exception:
        return None


def chain(name, w, mdl):
    done_ = []
    for k, s in enumerate(segs(w)):
        r = None
        for rid in (f"{name}_{s['id']}", f"{name}_{s['id']}_x"):   # one retry on a parse failure
            if not evo.done(rid):
                node2b.job(rid, chained_msg(w, k, done_), {"stage": "d10c", "work": w, "sec": s["id"]}, w=mdl)[1]()
            r = parse(rid) if evo.done(rid) else None
            if r and r.get("thread"):
                break
        if not (r and r.get("thread")):
            print(name, s["id"], "FAILED", flush=True); return
        done_.append(r | {"sec": s["id"], "bars": f"{s['start']}–{s['end']}"})
    save(name, done_)


def one(name, w, mdl):
    for rid in (name, name + "_x"):
        if not evo.done(rid):
            node2b.job(rid, gen.render("P0", w, "note") + "\n\n---\n" + ONE, {"stage": "d10o", "work": w}, w=mdl)[1]()
        r = parse(rid) if evo.done(rid) else None
        xs = (r or {}).get("sections") or []
        if len(xs) == len(segs(w)) and all(x.get("thread") for x in xs):
            return save(name, [x | {"sec": s["id"], "bars": f"{s['start']}–{s['end']}"} for x, s in zip(xs, segs(w))])
    print(name, "FAILED (sections != segments)", flush=True)


def save(name, xs):
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / f"{name}.json").write_text(json.dumps({"name": name, "sections": xs}, ensure_ascii=False, indent=1), encoding="utf-8")
    print(name, "saved", len(xs), flush=True)


if __name__ == "__main__":
    ph = sys.argv[1] if len(sys.argv) > 1 else "all"
    jobs = []
    for w in W:
        for m in ("6", "56"):
            mdl = "g6" if m == "6" else "g56"
            for j in R:
                for kind, fn in (("c", chain), ("o", one)):
                    name = f"d10{kind}{m}_{w}_r{j}"
                    if ph in (kind, "all") and not (OUT / f"{name}.json").exists():
                        jobs.append((name, lambda name=name, w=w, mdl=mdl, fn=fn: fn(name, w, mdl)))
    evo.run_parallel(jobs, 24)
