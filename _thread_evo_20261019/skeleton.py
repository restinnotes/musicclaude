"""What the original line holds and what compression must keep (user 10-21): Center, History ledger, Connections
(incl. long-range), per-segment why-now + mechanism. Washable: repetition, transitions, abstract stance words, music text.
  sk   : GPT-6 extracts the skeleton of each original line -> evaluations/skeleton/<thread>.json
  f8   : rewrite the concrete C1 prose with the skeleton as a must-keep list, natural speech, no formula sentences
  check: GPT-5.6 checks F6 / F7 / F8 against the skeleton item by item -> evaluations/skeleton/rows.json
ids: sk_<thread>, fm_F8_<thread>_r<j>, skc_<version>"""
import json, sys
import arts, evo, fmt4, node2b, plain

OUT = evo.ROOT / "evaluations" / "skeleton"
SK = ("下面是一篇按段落写的“线”：它讲一件属于人的事怎样一步步发生。之后它会被大幅压缩，请先把它的内在逻辑整理成骨架，作为压缩时必须保留的清单。"
      "要抓的是内容，不是措辞：重复的意思只算一次，修辞、过渡、音乐描写都不要。\n"
      "只输出一个 ```json 代码块：\n"
      "{\"center\": \"整篇围绕的那一件事（一句人话）\", \"arc\": \"这件事从头到尾怎样变（两三句）\",\n"
      " \"segments\": [{\"seg\": \"1–23\", \"now\": \"他此刻怎么了（一句）\", \"mechanism\": \"背后的心理机制（一句人话）\",\n"
      "   \"because\": [{\"from\": \"更早的段落，如 1–23\", \"what\": \"那里的什么导致了此刻\"}],\n"
      "   \"revises\": \"这一段改写了之前的哪个认识（原以为……现在……），没有就空\",\n"
      "   \"still_active\": [\"到这里已经成立、仍在起作用的经历或认识\"], \"open\": \"留下的问题\"}],\n"
      " \"links\": [{\"from\": \"段落\", \"to\": \"段落\", \"what\": \"跨越多段的呼应或回指\"}]}\n"
      "because 里要包括原文写到的远处前因，不只是上一段。\n\n========== 原文 ==========\n")
F8 = ("把下面这篇文章改写成极凝练的要点。后面附有这篇文章的“骨架”，是必须保留的内容清单：Center、每段的前因（包括远处段落的前因）、"
      "每段改写了之前的哪个认识、跨越多段的呼应——这些都不能丢；可以丢的只有重复、铺垫、过渡和修饰。\n"
      "格式：\n第一行加粗写“这件事：”加一句人话，说清整篇围绕的那件事。\n然后保留原来的分段标题，每段：\n"
      "- 一行加粗：像一个懂人心的朋友，用平常说话的语气，直接点破他此刻怎么了——其实在怕什么、想要什么、在骗自己什么。句子长短和句式要自然变化。\n"
      "- “← 因为”：是前面哪一段的什么导致了它；如果原因在更早的段落，写明是哪一段（如“（1–23）那时……”）。\n"
      "- 如果这一段改写了之前的某个认识，加一行“↺ 原以为……，现在……”。\n"
      "- “→ 于是”：它把他推向哪里。\n"
      "这一段没有新的变化，就只写加粗那一行。最后一段要让人看出这一路是同一件事走到了这里。\n"
      "不要用这些套路句式：“越……越……”“不是……而是……”“X 不等于 Y／不代表”“真正的……是……”“与其……不如……”，"
      "也不要写前后对仗、像格言或金句的句子。不要前言、总结、过渡和修饰。只输出改写后的内容。\n\n")
CHK = ("下面是一篇“线”的骨架（从原稿抽出的必须保留的内容），以及一份压缩稿。请逐项判断压缩稿是否保留：\n"
       "1. center：读者读完压缩稿，能否看出整篇围绕的是骨架里的这件事？（yes/partial/no）\n"
       "2. 每段的每条 because（尤其是来自更远段落的）：压缩稿是否写出了这层因果？（kept/weak/lost）\n"
       "3. 每段的 revises（若非空）：是否写出了这次认识的改写？（kept/weak/lost）\n"
       "4. 每条 links：跨段呼应是否还在？（kept/weak/lost）\n"
       "5. still_active：读者在后面的段落里，能否感到前面成立的东西仍在起作用（整体打分 1–10）。\n"
       "只输出一个 ```json 代码块：{\"center\": \"yes\", \"because\": {\"<seg>#<i>\": \"kept\"}, \"revises\": {\"<seg>\": \"kept\"}, "
       "\"links\": {\"<i>\": \"kept\"}, \"history_score\": 1, \"note\": \"一句话说最大的丢失\"}\n\n"
       "========== 骨架 ==========\n{SK}\n\n========== 压缩稿 ==========\n{TXT}")


def threads():
    return [t for ts in plain.THREADS.values() for t in ts]


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True); ph = sys.argv[1]; jobs = []
    if ph == "sk":
        for t in threads():
            jobs.append((f"sk_{t}", (lambda t=t: evo.call(f"sk_{t}", SK + arts.clean(evo.output(t)), prompt_text=SK, meta={"stage": "skeleton"}))))
        evo.run_parallel(jobs, 4)
        for t in threads():
            r = evo.output(f"sk_{t}")
            if r:
                j = evo.parse_json(r); (OUT / f"{t}.json").write_text(json.dumps(j, ensure_ascii=False, indent=1), encoding="utf-8")
                far = sum(1 for s in j["segments"] for b in s.get("because", []) if b.get("from") and b["from"] != (j["segments"][max(0, j["segments"].index(s) - 1)]["seg"]))
                print(t, len(j["segments"]), "segs", sum(len(s.get("because", [])) for s in j["segments"]), "because,", far, "far,",
                      sum(1 for s in j["segments"] if s.get("revises")), "revises,", len(j.get("links", [])), "links")
    elif ph == "f8":
        for t in threads():
            sk = (OUT / f"{t}.json").read_text(encoding="utf-8")
            for j in (1, 2):
                rid = f"fm_F8_{t}_r{j}"
                if not evo.done(rid):
                    jobs.append(node2b.job(rid, F8 + arts.clean(evo.output(f"pc_C1_{t}_r1")) + "\n\n========== 骨架（必须保留） ==========\n" + sk,
                                           {"stage": "f8", "thread": t}))
        evo.run_parallel(jobs, 4)
    elif ph == "check":
        extra = sys.argv[2].split(",") if len(sys.argv) > 2 else None
        names = [(t, v) for t in threads() for v in (extra and [x.format(t=t) for x in extra] or (f"fm_F6_{t}_r1", f"fm_F7_{t}_r1", f"fm_F8_{t}_r1", f"fm_F8_{t}_r2"))]
        for t, v in names:
            if evo.done(v):
                import causal; txt = causal.text(v)
                msg = CHK.replace("{SK}", (OUT / f"{t}.json").read_text(encoding="utf-8")).replace("{TXT}", txt)
                jobs.append((f"skc_{v}", (lambda v=v, msg=msg: evo.call(f"skc_{v}", msg, prompt_text=CHK[:300], model=evo.G56, meta={"stage": "skeleton_check"}))))
        evo.run_parallel(jobs, 6)
        rows = []
        for t, v in names:
            r = evo.output(f"skc_{v}")
            if not r:
                continue
            c = evo.parse_json(r); b = list(c.get("because", {}).values()); rv = list(c.get("revises", {}).values()); lk = list(c.get("links", {}).values())
            pct = lambda xs: round(100 * xs.count("kept") / len(xs)) if xs else None
            rows.append({"thread": t, "version": v.split("_")[1], "name": v, "center": c.get("center"), "because_kept%": pct(b), "revises_kept%": pct(rv),
                         "links_kept%": pct(lk), "history": c.get("history_score"), "formula": None, "chars": len(__import__("causal").text(v)), "note": c.get("note")})
        (OUT / (f"rows_{sys.argv[3]}.json" if len(sys.argv) > 3 else "rows.json")).write_text(json.dumps(rows, ensure_ascii=False, indent=1), encoding="utf-8")
        for r in rows:
            print(f"{r['name']:32s} center {r['center']:7s} 前因保留 {r['because_kept%']}% 改写保留 {r['revises_kept%']}% 跨段呼应 {r['links_kept%']}% 累积 {r['history']} 套路句 {r['formula']} 字 {r['chars']}")
