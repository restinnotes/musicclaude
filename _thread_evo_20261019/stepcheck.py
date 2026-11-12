"""Loss with a baseline: (1) GPT-6 extracts a fixed causal-step inventory from each original line;
(2) each compressed version is checked step by step against that same inventory (kept/weakened/lost/wrong) and scanned
for additions not in the original (paraphrase vs new fact/event). One checker model for all versions, so counts compare.
usage: python stepcheck.py inv | check   -> evaluations/stepcheck/<thread>.json, rows.json"""
import json, sys
import arts, evo, plain

OUT = evo.ROOT / "evaluations" / "stepcheck"
VERS = [("pl_PL", (1,)), ("pc_C1", (1, 2)), ("pc_C2", (1, 2)), ("pc_C3", (1, 2))]
INV = ("下面是一篇按段落写的文章，它讲一件属于人的事怎样一步一步发生。请把它拆成一份完整的“因果步骤清单”："
       "每一步是一个最小的推进——因为前面已经发生/相信/发现了什么，所以此刻怎样（新的认识、新的所求、新的决定或新的困惑）。"
       "同一个意思在原文里反复说的，只算一步；纯修辞、纯音乐描写不算步骤。按原文顺序列出，标明所在段落。\n"
       "只输出一个 ```json 代码块：{\"steps\": [{\"id\": \"S01\", \"segment\": \"1–23\", \"because\": \"……\", \"so\": \"……\"}]}\n\n========== 原文 ==========\n")
CHK = ("下面有一份“因果步骤清单”（从原文抽出），以及一篇改写稿。请逐条判断改写稿有没有保留每一步：\n"
       "- kept：意思完整保留（换了说法没关系）；\n- weakened：还在，但因果或关键限定弱化、模糊了；\n"
       "- lost：没有了；\n- wrong：被说成了不同的意思。\n"
       "然后反过来，列出改写稿里**原文没有**的内容：paraphrase（只是把原文意思说得更具体、更口语，没有新增事实）"
       "或 new（新增了原文没有的事实、事件、动作、人物、物件或新的认识）。\n"
       "只输出一个 ```json 代码块：{\"steps\": {\"S01\": \"kept\", ...}, \"additions\": [{\"type\": \"new\", \"segment\": \"…\", \"text\": \"改写稿原句短引\"}]}\n\n"
       "========== 因果步骤清单 ==========\n{INV}\n\n========== 改写稿 ==========\n{TXT}")


def threads():
    return [t for ts in plain.THREADS.values() for t in ts]


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    if sys.argv[1] == "inv":
        evo.run_parallel([(f"inv_{t}", (lambda t=t: evo.call(f"inv_{t}", INV + arts.clean(evo.output(t)), prompt_text=INV, meta={"stage": "step_inventory"})))
                          for t in threads()], 4)
        for t in threads():
            r = evo.output(f"inv_{t}")
            if r:
                (OUT / f"{t}.json").write_text(json.dumps(evo.parse_json(r), ensure_ascii=False, indent=1), encoding="utf-8")
                print(t, len(evo.parse_json(r)["steps"]), "steps")
    else:
        jobs = []
        for t in threads():
            inv = (OUT / f"{t}.json").read_text(encoding="utf-8")
            for v, js in VERS:
                for j in js:
                    n = f"{v}_{t}_r{j}"; rid = f"chk_{n}"
                    msg = CHK.replace("{INV}", inv).replace("{TXT}", arts.clean(evo.output(n)))
                    jobs.append((rid, (lambda rid=rid, msg=msg: evo.call(rid, msg, prompt_text=CHK[:300], model=evo.G56, meta={"stage": "step_check"}))))
        evo.run_parallel(jobs, 6)
        rows = []
        for t in threads():
            N = len(json.loads((OUT / f"{t}.json").read_text(encoding="utf-8"))["steps"])
            for v, js in VERS:
                for j in js:
                    r = evo.output(f"chk_{v}_{t}_r{j}")
                    if not r:
                        continue
                    c = evo.parse_json(r); st = list(c.get("steps", {}).values()); ad = c.get("additions", [])
                    rows.append({"thread": t, "version": v.split("_")[1], "rep": j, "total": N,
                                 **{k: st.count(k) for k in ("kept", "weakened", "lost", "wrong")},
                                 "add_new": sum(a.get("type") == "new" for a in ad), "add_para": sum(a.get("type") == "paraphrase" for a in ad),
                                 "new_examples": [a.get("text") for a in ad if a.get("type") == "new"][:5],
                                 "chars": len(arts.clean(evo.output(f"{v}_{t}_r{j}")))})
        (OUT / "rows.json").write_text(json.dumps(rows, ensure_ascii=False, indent=1), encoding="utf-8")
        for r in rows:
            print(f"{r['thread']:20s} {r['version']:3s} r{r['rep']} 保留{r['kept']}/{r['total']} 弱化{r['weakened']} 丢{r['lost']} 错{r['wrong']} 新增{r['add_new']} 字{r['chars']}")
