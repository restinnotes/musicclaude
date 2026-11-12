"""Assemble gpt3 outputs into deliverables + quote verification."""
import json, re, hashlib
from pathlib import Path

W = Path(__file__).resolve().parent.parent
OUT, DEL = W / "out", W / "deliverable"
(DEL / "struct").mkdir(parents=True, exist_ok=True)
A = {p.stem: p.read_text(encoding="utf-8-sig") for p in (W / "input" / "A").glob("*.md")}
short = {b["segment"]: b for b in json.load(open(W / "input" / "short_beads_ref.json", encoding="utf-8"))}


def norm(s):
    return re.sub(r"[\s\*`“”\"'‘’「」『』《》，。、；：！？,.;:!?（）()\-—–…·]", "", s)


NA = {k: norm(v) for k, v in A.items()}
reader, diffs, evidence, qstats = [], [], [], []
for seg in sorted(short):
    rp = OUT / f"{seg}.response.txt"
    if not rp.exists():
        reader.append(f"## {seg} · （缺失：gpt3 调用未成功）\n")
        continue
    raw = rp.read_text(encoding="utf-8")
    m = re.search(r"```json\s*(.*?)```", raw, re.S)
    d = json.loads(m.group(1) if m else raw)
    meta = json.loads((OUT / f"{seg}.result.json").read_text(encoding="utf-8"))
    job = Path(meta["job_directory"])
    tv = json.loads((job / "terminal-verification.json").read_text(encoding="utf-8"))
    jr = json.loads((job / "result.json").read_text(encoding="utf-8"))
    sm = json.loads((OUT / f"{seg}.raw_stdout.txt").read_text(encoding="utf-8"))["metadata"]
    # quote check
    tot = hit = 0
    for kind in ("facets", "alternative_readings"):
        for f in d["struct"].get(kind, []):
            for s in f.get("support", []):
                tot += 1
                src = s.get("src", "").strip()
                q = norm(s.get("quote", ""))
                found = bool(q) and src in NA and q in NA[src]
                s["quote_verified"] = found
                hit += found
    d["quote_check"] = {"total": tot, "verbatim_found": hit}
    (DEL / "struct" / f"{seg}.json").write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")
    rb = d["reader_bead"]
    mm = d.get("measures", "")
    reader.append(f"## {seg} · 第{mm}小节｜{rb['title']}\n\n{rb['body'].strip()}\n")
    diffs.append(f"## {seg}\n\n- 短版标题：{short[seg]['title']}　→　新标题：{rb['title']}\n"
                 f"- 正文字数：短版 {len(short[seg]['body'])} → 新 {len(rb['body'])}\n"
                 f"- facets {len(d['struct'].get('facets', []))} / 不同读法 {len(d['struct'].get('alternative_readings', []))} / 内部先后 {len(d['struct'].get('internal_sequence', []))} / 拒收 {len(d['struct'].get('rejected', []))}\n"
                 f"- 引文逐字可在所标原稿中找到：{hit}/{tot}\n\n{d.get('diff_vs_short', '').strip()}\n")
    final = (tv.get("final_messages") or [{}])[0]
    evidence.append({"segment": seg, "job_directory": str(job), "session_handle": sm.get("session_handle"), "temporary": sm.get("temporary"), "unpersonalized": sm.get("unpersonalized"),
                     "model": final.get("model"), "effort": final.get("effort"), "status": final.get("status"),
                     "terminal_completion_verified": tv.get("terminal_completion_verified"),
                     "response_sha256": hashlib.sha256(raw.encode("utf-8")).hexdigest(),
                     "seconds": jr.get("elapsed_seconds"), "tools_used": jr.get("toolsUsed")})
    (DEL / "raw_responses").mkdir(exist_ok=True)
    (DEL / "raw_responses" / f"{seg}.response.txt").write_text(raw, encoding="utf-8")
    (DEL / "raw_responses" / f"{seg}.prompt.txt").write_text((job / "prompt.txt").read_text(encoding="utf-8"), encoding="utf-8")

head = ("# 肖邦《船歌》Op.60 · 十四颗珠子（gpt3 正式生成版）\n\n沿用 PTNA／朝山十四段。每颗正文由 GPT-6 Thinking / max 经本地 gpt3（GPT Web）逐段一次生成，"
        "输入为 24 份非 Muse 历史 A 原稿与短版参考；本页为原样拼接，未经人工改写。情景与人物动作是聆听比喻，不是作曲家生平或唯一演奏解释。\n\n")
(DEL / "READER.md").write_text(head + "\n".join(reader), encoding="utf-8")
(DEL / "DIFF_vs_short.md").write_text("# 与短版的差异（各段 diff_vs_short 为模型自述；数字由脚本计算）\n\n" + "\n".join(diffs), encoding="utf-8")
(DEL / "EVIDENCE.json").write_text(json.dumps(evidence, ensure_ascii=False, indent=1), encoding="utf-8")
print(len(evidence), "segments assembled")
for e, dl in zip(evidence, diffs):
    print(e["segment"], e["model"], e["effort"], e["terminal_completion_verified"], dl.split("\n")[4])
