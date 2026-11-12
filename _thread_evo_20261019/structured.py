"""Structured Thread (user 10-21: final output structured, not prose, to serve video). From the concrete C1 prose + its
skeleton, GPT writes JSON directly; the script validates segments, counts formula sentences, renders markdown.
  gen    : ids st_<thread>_r<j>  -> evaluations/structured/<id>.json + .md
  render : re-render all
Schema: {center, arc, segments:[{bars, headline, because:[{from, what}], revises, toward, weight(1-3)}]}"""
import json, re, sys
import arts, evo, fmt4, node2b, plain, seg

OUT = evo.ROOT / "evaluations" / "structured"
ST = ("把下面这篇文章整理成结构化的 Thread，供之后做讲解视频用。后面附有这篇文章的“骨架”，是必须保留的内容清单："
      "Center、每段的前因（包括远处段落的前因）、每段改写了之前的哪个认识、跨越多段的呼应——这些都不能丢；可以丢的只有重复、铺垫、过渡和修饰。\n"
      "只输出一个 ```json 代码块，格式：\n"
      "{\"center\": \"整篇围绕的那件事（一句人话）\", \"arc\": \"这件事从头到尾怎样变（两三句人话）\",\n"
      " \"segments\": [{\"bars\": \"{FIRST}\", \"headline\": \"……\", \"because\": [{\"from\": \"段落小节号\", \"what\": \"……\"}],\n"
      "   \"revises\": \"原以为……，现在……（这一段没有改写之前的认识就留空）\", \"toward\": \"它把他推向哪里\", \"weight\": 2}]}\n"
      "要求：\n- segments 必须按顺序覆盖这些段落，一个不多一个不少：{BARS}。\n"
      "- headline：像一个懂人心的朋友，用平常说话的语气，直接点破他此刻怎么了——其实在怕什么、想要什么、在骗自己什么。句子长短和句式自然变化。\n"
      "- because：一到两条；from 写明是哪一段（原因在更早的段落就写那一段，不要一律写上一段）。\n"
      "- weight：这一段新发生的事有多少（1 = 几乎没有新变化，只需一句带过；2 = 一般；3 = 关键转折）。weight 为 1 的段落，because、revises、toward 可以留空。\n"
      "- 不要用这些套路句式：“越……越……”“不是……而是……”“X 不等于 Y／不代表”“真正的……是……”“与其……不如……”，也不要对仗、格言式的金句。\n\n")


def bars(work):
    return [f"{s['start']}–{s['end']}" for s in seg.load(work)["segments"]]


def render(j, title):
    md = [f"# {title}", "", f"**这件事：**{j['center']}", "", f"**走向：**{j['arc']}", ""]
    for s in j["segments"]:
        md += [f"### {s['bars']}", "", f"**{s['headline']}**"]
        for b in s.get("because") or []:
            md.append(f"← 因为（{b.get('from')}）{b.get('what')}")
        if s.get("revises"):
            md.append(f"↺ {s['revises']}")
        if s.get("toward"):
            md.append(f"→ 于是{s['toward'].removeprefix('于是')}")
        md.append("")
    return "\n".join(md)


def save(rid, work):
    j = evo.parse_json(evo.output(rid))
    got = [s["bars"].replace("-", "–").replace("—", "–") for s in j["segments"]]
    ok = got == bars(work)
    heads = [s["headline"] for s in j["segments"]]
    formula = sum(any(re.search(v, h) for v in fmt4.PAT.values()) for h in heads)
    OUT.mkdir(parents=True, exist_ok=True)
    j.update(work=work, source=rid, segments_valid=ok, formula_headlines=formula)
    (OUT / f"{rid}.json").write_text(json.dumps(j, ensure_ascii=False, indent=1), encoding="utf-8")
    (OUT / f"{rid}.md").write_text(render(j, rid), encoding="utf-8")
    far = sum(1 for i, s in enumerate(j["segments"]) for b in s.get("because") or [] if i > 0 and b.get("from") not in (j["segments"][i - 1]["bars"], "上一段"))
    print(rid, "segments ok" if ok else f"SEGMENTS MISMATCH {got}", "formula", formula, "far-because", far,
          "revises", sum(bool(s.get("revises")) for s in j["segments"]), "chars", len(render(j, "")), flush=True)


TIGHT = ("\n长度约束（很重要，成品要一眼就看完）：\n"
         "- headline 不超过 35 字。\n"
         "- because 只写一条，不超过 35 字：只点最关键的那一个前因；真正的原因在更早的段落，就写那一段，不要罗列多个段落。\n"
         "- revises 只在 weight 为 2 或 3 的段落写，不超过 35 字。\n"
         "- toward 不超过 20 字。\n"
         "- weight 为 1 的段落只写 headline。\n\n")
P2 = len(sys.argv) > 2 and sys.argv[2] == "tight"
PFX = "st2" if P2 else "st"

if __name__ == "__main__":
    ph = sys.argv[1]; jobs = []
    if ph == "gen":
        for w, ts in plain.THREADS.items():
            b = bars(w)
            for t in ts:
                sk = (evo.ROOT / "evaluations" / "skeleton" / f"{t}.json").read_text(encoding="utf-8")
                msg = ST.replace("{FIRST}", b[0]).replace("{BARS}", "、".join(b)) + (TIGHT if P2 else "") + arts.clean(evo.output(f"pc_C1_{t}_r1")) + "\n\n========== 骨架（必须保留） ==========\n" + sk
                for j in (1, 2):
                    rid = f"{PFX}_{t}_r{j}"
                    if not evo.done(rid):
                        jobs.append(node2b.job(rid, msg, {"stage": "structured", "thread": t}))
        evo.run_parallel(jobs, 4)
    for w, ts in plain.THREADS.items():
        for t in ts:
            for j in (1, 2):
                if evo.done(f"{PFX}_{t}_r{j}"):
                    save(f"{PFX}_{t}_r{j}", w)
