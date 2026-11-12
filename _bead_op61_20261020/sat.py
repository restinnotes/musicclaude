"""Op.61 copy of _bead_saturation_20261018/sat.py; only the production stages gen_b,rev1_b,rev2_b,final_b,piece_b,final2_b are used.
Op.60 semantic-saturation experiment (DAG A) — all model work via local gpt3 (GPT Web, GPT-6 Thinking / max).

Tasks per segment (cached under runs/<stage>/<seg>.*; a task with parsed.json is never redone):
  gen    fresh   ranked marginal-value ladder from Pool + 24 A
  rev1   fresh   clean reviewer lists the segment's experiences from 24 A only (sees no candidate)
  rev2   resume rev1 session: reviewer scores the anonymised ladder k by k
  final  resume gen session: generator answers the review and writes the final STRUCT
  prod   fresh   one-shot production candidate (Pool + A -> STRUCT, no ladder, no review)
  nopool fresh   one-shot without Pool (ablation, subset)
  cmp    fresh   blind comparison of final / prod / nopool
Scheduler: dependency-aware worker pool; concurrency read live from runs/parallel.txt.
A call that failed after submission is marked 'uncertain' and never resubmitted automatically.

  python sat.py run --stages gen,rev1,rev2,final,prod,cmp --segs all
  python sat.py status
"""
import argparse, hashlib, json, random, re, subprocess, sys, threading, time, zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
GPT3 = "D:/musicclaude/gpt2agent-safechain/bin/gpt3.cmd"
GPT3_RUNS = Path("D:/musicclaude/gpt2agent-safechain/runs/gpt3")
RUNS = ROOT / "runs"
INP = ROOT / "inputs"
STRUCT = json.loads((INP / "structure.json").read_text(encoding="utf-8"))
SEGS = {f"S{i+1:02d}": (mm, lab) for i, (mm, lab) in enumerate(STRUCT["frozen_segments"])}
A = {p.stem: p.read_text(encoding="utf-8-sig") for p in sorted((INP / "A").glob("*.md"))}
assert len(A) == 24 and not any(x in k.lower() for k in A for x in ("muse", "opus", "sonnet")), "need exactly the 24 non-Muse, non-Claude A sources"
class _Pool(dict):
    def __missing__(self, s):
        self[s] = json.loads((ROOT / "runs" / "pool_v2" / "pool" / f"{s}.parsed.json").read_text(encoding="utf-8")); return self[s]
POOL = _Pool()  # lazy: rev1 does not need the pool
SEC_PER_MEASURE = 2.7  # ~13 min / 288 measures; rough attention budget only
NOPOOL_SEGS = []
MIN_GAP = 6.0


def mm(seg):
    return SEGS[seg][0].replace("-", "–")


def nmeas(seg):
    a, b = map(int, SEGS[seg][0].split("-")); return b - a + 1


SEGLIST = "；".join(f"{s} 第{mm(s)}小节 {lab}" for s, (_, lab) in SEGS.items())


def norm(s):
    return re.sub(r"[\s\*`“”\"'‘’「」『』《》，。、；：！？,.;:!?（）()\-—–…·]", "", s or "")


NA = {k: norm(v) for k, v in A.items()}


def quote_ok(src, q):
    q = norm(q); return bool(q) and src in NA and q in NA[src]


def sources_zip():
    z = RUNS / "sources.zip"
    if not z.exists():
        RUNS.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(z, "w", zipfile.ZIP_DEFLATED) as f:
            for k, v in A.items():
                f.writestr(f"A/{k}.md", v)
    return z


def tpl(name):
    return (ROOT / "prompts" / f"{name}.md").read_text(encoding="utf-8")


def fill(t, seg, **kw):
    for k, v in kw.items():
        t = t.replace("{" + k + "}", v)
    return (t.replace("{SEG}", seg).replace("{MM}", mm(seg)).replace("{LABEL}", SEGS[seg][1])
             .replace("{SEGLIST}", SEGLIST).replace("{SEC}", str(round(nmeas(seg) * SEC_PER_MEASURE))))


def render_pool(seg):
    out = []
    for it in POOL[seg]["items"]:
        rr = it["src_range"]; ms = it["measures"]
        loc = f"原稿范围 {rr} → 判断 {ms}" if rr.replace("mm. ", "") != ms else f"{ms}"
        out.append(f"- {it['id']}｜{it['src']}｜{loc}｜{it['type']}｜原话「{it['quote']}」｜复述：{it['experience']}")
    return "\n".join(out)


# ---------------- gpt3 ----------------
_gap_lock = threading.Lock(); _last = [0.0]
LOG = RUNS / "calls.jsonl"; _log_lock = threading.Lock()


def log(rec):
    with _log_lock:
        with LOG.open("a", encoding="utf-8") as f:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")


def call(stage, seg, prompt_text, attach=(), session=None):
    out = RUNS / stage; out.mkdir(parents=True, exist_ok=True)
    pf = out / f"{seg}.prompt.txt"; pf.write_text(prompt_text, encoding="utf-8")
    assert len(prompt_text) <= 65000, f"{stage}/{seg} prompt too long: {len(prompt_text)}"
    for attempt in range(2):
        with _gap_lock:
            w = MIN_GAP - (time.time() - _last[0])
            if w > 0:
                time.sleep(w)
            _last[0] = time.time()
        cmd = [GPT3] + (["resume", session] if session else ["ask"]) + ["--file", str(pf), "--json"]
        for a in attach:
            cmd += ["--attach", str(a)]
        t0 = time.time(); started = time.strftime("%Y-%m-%dT%H:%M:%S")
        cp = subprocess.run(cmd, capture_output=True)
        dt = time.time() - t0
        (out / f"{seg}.stdout.bin").write_bytes(cp.stdout); (out / f"{seg}.stderr.bin").write_bytes(cp.stderr)
        try:
            j = json.loads(cp.stdout.decode("utf-8"))
        except Exception:
            j = {}
        md = j.get("metadata") or {}
        job = md.get("job_directory")
        if not job:
            m = re.search(rb'"job_directory":\s*"((?:[^"\\]|\\.)*)"', cp.stdout + cp.stderr)
            job = json.loads(b'"' + m.group(1) + b'"') if m else None
        ok = cp.returncode == 0 and j.get("completed") is True and j.get("response")
        rec = {"stage": stage, "seg": seg, "attempt": attempt, "started": started, "seconds": round(dt),
               "rc": cp.returncode, "completed": bool(ok), "model": md.get("model"), "effort": md.get("thinking_effort"),
               "temporary": md.get("temporary"), "unpersonalized": md.get("unpersonalized"),
               "policy_verified": md.get("generation_policy_verified"), "resume": bool(session),
               "session_handle": md.get("session_handle"), "job": job,
               "prompt_chars": len(prompt_text), "prompt_sha256": hashlib.sha256(prompt_text.encode()).hexdigest()}
        if ok:
            if md.get("model") != "gpt-6-thinking" or md.get("thinking_effort") != "max" or not md.get("temporary") or not md.get("unpersonalized"):
                rec["completed"] = False; rec["why"] = "policy mismatch"; log(rec)
                print(f"[{stage}/{seg}] POLICY MISMATCH {md.get('model')}/{md.get('thinking_effort')}", flush=True)
                return None
            resp = j["response"]
            rec["response_chars"] = len(resp); log(rec)
            (out / f"{seg}.response.txt").write_text(resp, encoding="utf-8")
            (out / f"{seg}.meta.json").write_text(json.dumps(rec, ensure_ascii=False, indent=1), encoding="utf-8")
            print(f"[{stage}/{seg}] ok {dt:.0f}s {len(resp)} chars", flush=True)
            return resp, md.get("session_handle")
        if b"gpt3_session_expired" in cp.stderr:  # refused locally before any request: not submitted, retry is useless
            rec["why"] = "session expired"; log(rec)
            print(f"[{stage}/{seg}] SESSION EXPIRED (not submitted)", flush=True)
            return None
        if not job:  # gpt3 failure output often omits job_directory: find our job by prompt text
            cands = [d for d in GPT3_RUNS.glob("pro-bridge-*") if d.stat().st_mtime >= t0 - 5 and (d / "prompt.txt").exists()
                     and (d / "prompt.txt").read_text(encoding="utf-8-sig").strip() == prompt_text.strip()]
            job = str(max(cands, key=lambda d: d.stat().st_mtime)) if cands else None
            rec["job"] = job
        # unknown job => treat as possibly submitted (never risk a duplicate submission)
        submitted = (not job) or (Path(job) / "submitted.json").exists()
        rec["submitted"] = submitted
        rec["stderr_tail"] = cp.stderr.decode("utf-8", "replace")[-600:]
        log(rec)
        print(f"[{stage}/{seg}] FAILED rc={cp.returncode} {dt:.0f}s submitted={submitted}", flush=True)
        if submitted:
            (out / f"{seg}.uncertain.json").write_text(json.dumps(rec, ensure_ascii=False, indent=1), encoding="utf-8")
            return None
        time.sleep(45)
    return None


def parse_json(resp):
    m = re.findall(r"```json\s*(.*?)```", resp, re.S)
    txt = m[-1] if m else resp
    try:
        return json.loads(txt)
    except Exception:
        s = txt[txt.find("{"): txt.rfind("}") + 1]
        return json.loads(s)


def load(stage, seg):
    p = RUNS / stage / f"{seg}.parsed.json"
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else None


def handle(stage, seg):
    p = RUNS / stage / f"{seg}.meta.json"
    return json.loads(p.read_text(encoding="utf-8")).get("session_handle") if p.exists() else None


def save(stage, seg, d):
    (RUNS / stage / f"{seg}.parsed.json").write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")


def verify_quotes(d):
    """Mark every {src, quote} in the structure with quote_verified."""
    n = bad = 0
    def walk(x):
        nonlocal n, bad
        if isinstance(x, dict):
            if "src" in x and "quote" in x and isinstance(x.get("quote"), str):
                x["quote_verified"] = quote_ok(x["src"], x["quote"]); n += 1; bad += not x["quote_verified"]
            for v in x.values():
                walk(v)
        elif isinstance(x, list):
            for v in x:
                walk(v)
    walk(d)
    return n, bad


def finish(stage, seg, r):
    if not r:
        return False
    resp, _ = r
    try:
        d = parse_json(resp)
    except Exception as e:
        print(f"[{stage}/{seg}] PARSE ERROR {e}", flush=True)
        (RUNS / stage / f"{seg}.parse_error.txt").write_text(str(e), encoding="utf-8")
        return False
    n, bad = verify_quotes(d)
    d["_quotes"] = {"n": n, "unverified": bad}
    save(stage, seg, d)
    return True


# ---------------- renderers ----------------
def render_ladder(seg, st="gen"):
    g = load(st, seg); out = []
    for f in g["ladder"]:
        rel = "；".join(f"{r.get('type')}（对 {','.join(r.get('to') or []) or '—'}）" for r in f.get("relation", []))
        src = "\n".join(f"  - {s.get('src')}：「{s.get('quote')}」" for s in f.get("sources", []))
        alt = "\n".join(f"  - {s.get('src')}：「{s.get('quote')}」" for s in f.get("also_expressed_by", []) or [])
        blk = (f"### 第 {f['k']} 个侧面（{f['id']}）\n小节：{f.get('measures')}（{f.get('placement')}）\n"
               f"写作者标注的关系：{rel or '—'}\n")
        if f.get("performance_condition"):
            blk += f"演奏条件：{f['performance_condition']}\n"
        blk += f"正文：{f['text']}\n依据原话：\n{src}\n"
        if alt:
            blk += f"并入的其他原稿说法：\n{alt}\n"
        out.append(blk)
    return "\n".join(out)


def render_review(seg, s1="rev1", s2="rev2"):
    r2 = {k: v for k, v in load(s2, seg).items() if not k.startswith("_")}
    r1 = load(s1, seg)
    ex = {e["id"]: e for e in r1.get("experiences", [])}
    ids = sorted({m.get("id") for m in r2.get("missing", []) if m.get("id") in ex})
    ref = [{"id": i, "what": ex[i].get("what"), "best_quote": ex[i].get("best_quote"), "measures": ex[i].get("measures"),
            "sources": [s.get("src") for s in ex[i].get("sources", [])]} for i in ids]
    txt = "```json\n" + json.dumps(r2, ensure_ascii=False, indent=0) + "\n```\n"
    txt += "\n审稿意见中的 E 编号是审稿人自己从原稿列出的体验编号。"
    if ref:
        txt += "审稿人认为遗漏的体验详情：\n```json\n" + json.dumps(ref, ensure_ascii=False, indent=0) + "\n```\n"
    return txt


def render_struct(d):
    beads = "\n".join(f"- [{b.get('role')}｜{b.get('measures')}] {b.get('text')}" for b in d.get("beads", []))
    return f"### 标题\n{d.get('title')}\n\n### 读者正文\n{d.get('reader')}\n\n### 结构化体验条目\n{beads}\n"


# ---------------- tasks ----------------
def t_gen(seg):
    p = fill(tpl("gen_v1"), seg, POOL=render_pool(seg), NPOOL=str(len(POOL[seg]["items"])))
    return finish("gen", seg, call("gen", seg, p, [sources_zip()]))


def t_rev1(seg):
    return finish("rev1", seg, call("rev1", seg, fill(tpl("rev1_v1"), seg), [sources_zip()]))


def t_rev2(seg):
    h = handle("rev1", seg)
    return finish("rev2", seg, call("rev2", seg, fill(tpl("rev2_v1"), seg, LADDER=render_ladder(seg)), session=h))


def t_final(seg):
    spec = fill(tpl("struct_spec_v1"), seg)
    p = fill(tpl("final_v1"), seg, STRUCT_SPEC=spec, REVIEW=render_review(seg))
    return finish("final", seg, call("final", seg, p, session=handle("gen", seg)))


def t_prod(seg, with_pool=True, ver="prod_v1", st=None):
    spec = fill(tpl("struct_spec_v1"), seg)
    if with_pool:
        note = "- 文末的 Pool：此前从这 24 份原稿中为本段登记的原文条目。原话已逐字核对；`→` 后的位置是登记者的判断，可能有误，有疑问请回原稿核对上下文。Pool 只是检索索引，不是必须保留的清单。"
        block = f"\n## Pool（{seg}，共 {len(POOL[seg]['items'])} 条）\n\n" + render_pool(seg)
    else:
        note = "- 请自己从 24 份原稿中找出关于本段音乐的内容；原稿范围宽或跨段时，按原稿描述的音乐事件判断它是否真落在本段。"
        block = ""
    chars = str(max(100, round(nmeas(seg) * SEC_PER_MEASURE * 5 / 10) * 10))
    p = fill(tpl(ver), seg, STRUCT_SPEC=spec, POOL_NOTE=note, POOL_BLOCK=block, CHARS=chars)
    st = st or ("prod" if with_pool else "nopool")
    return finish(st, seg, call(st, seg, p, [sources_zip()]))


def t_cmp(seg, tg=None, out="cmp"):
    tg = tg or (["final", "prod"] + (["nopool"] if seg in NOPOOL_SEGS else []))
    labels = ["甲", "乙", "丙"][:len(tg)]
    order = tg[:]; random.Random(f"{out}-{seg}").shuffle(order)
    mapping = dict(zip(labels, order))
    vs = "\n".join(f"## 版本{l}\n\n{render_struct(load(mapping[l], seg))}" for l in labels)
    ok = finish(out, seg, call(out, seg, fill(tpl("cmp_v1"), seg, VERSIONS=vs), [sources_zip()]))
    if ok:
        d = load(out, seg); d["_mapping"] = mapping; save(out, seg, d)
    return ok


def t_piece(stage="final", out="piece"):
    blocks = []
    for s in SEGS:
        d = load(stage, s)
        blocks.append(f"## {s}（第 {mm(s)} 小节，{SEGS[s][1]}）\n\n{render_struct(d)}")
    p = tpl("piece_v1").replace("{ALL}", "\n".join(blocks))
    return finish(out, "ALL", call(out, "ALL", p, [sources_zip()]))


def piece_for(seg, src="piece"):
    d = load(src, "ALL") or {}
    ps = [x for x in d.get("per_segment", []) if x.get("segment") == seg]
    rt = [x for x in d.get("repeated_templates", []) if seg in (x.get("segments") or [])]
    fx = [x for x in d.get("fixes", []) if x.get("segment") == seg]
    ci = [x for x in d.get("continuity_issues", []) if seg in json.dumps(x, ensure_ascii=False)]
    return {"per_segment": ps, "repeated_templates": rt, "fixes": fx, "continuity_issues": ci}


def needs_fix(seg, src="piece"):
    p = piece_for(seg, src)
    own = (p["per_segment"] or [{}])[0].get("own_experience")
    return bool(p["fixes"]) or own in ("部分", "否") or any(x.get("is_problem") for x in p["repeated_templates"])


def t_fix(seg, src="piece", gen="gen", out="final2"):
    spec = fill(tpl("struct_spec_v1"), seg)
    txt = "```json\n" + json.dumps(piece_for(seg, src), ensure_ascii=False, indent=0) + "\n```"
    p = fill(tpl("fix_v1"), seg, STRUCT_SPEC=spec, PIECE=txt)
    return finish(out, seg, call(out, seg, p, session=handle(gen, seg)))


def t_trim(seg):
    d = load("cmp2", seg); inv = {v: k for k, v in d["_mapping"].items()}
    v = d["versions"][inv["final"]]
    note = {"attention_fit": v.get("attention_fit"), "attention_note": v.get("attention_note"), "errors": v.get("errors", [])}
    txt = "```json\n" + json.dumps(note, ensure_ascii=False, indent=0) + "\n```"
    p = fill(tpl("trim_v1"), seg, STRUCT_SPEC=fill(tpl("struct_spec_v1"), seg), NOTE=txt)
    return finish("final3", seg, call("final3", seg, p, session=handle("gen", seg)))


def t_cmp3(seg):
    best = "final3"
    d = load("cmp2", seg); m = d["_mapping"]; winner = [m[x] for x in d["ranking"] if m[x] != "final"][0]
    return t_cmp(seg, [best, winner, "final"], "cmp3")


# ---- Pool (bead_chain pool_v2 prompt, same fill/parse/quote check as chain.st_pool; run here so one process paces all gpt3 calls) ----
def t_pool(seg):
    st = "pool_v2/pool"
    r = call(st, seg, fill(tpl("pool_v2"), seg), [sources_zip()])
    if not r:
        return False
    try:
        d = parse_json(r[0])
    except Exception as e:
        print(f"[pool/{seg}] PARSE ERROR {e}", flush=True)
        (RUNS / st / f"{seg}.parse_error.txt").write_text(str(e), encoding="utf-8"); return False
    for it in d.get("items", []):
        it["quote_verified"] = quote_ok(it.get("src", ""), it.get("quote", ""))
    save(st, seg, d)
    return True


# ---- DAG B validation: the proposed production chain run fresh (separate sessions, *_b stages) ----
def t_gen_b(seg):
    p = fill(tpl("gen_v1"), seg, POOL=render_pool(seg), NPOOL=str(len(POOL[seg]["items"])))
    return finish("gen_b", seg, call("gen_b", seg, p, [sources_zip()]))


def t_rev1_b(seg):
    return finish("rev1_b", seg, call("rev1_b", seg, fill(tpl("rev1_v1"), seg), [sources_zip()]))


def t_rev2_b(seg):
    lad = render_ladder(seg, "gen_b")
    return finish("rev2_b", seg, call("rev2_b", seg, fill(tpl("rev2_v1"), seg, LADDER=lad), session=handle("rev1_b", seg)))


def t_final_b(seg):
    spec = fill(tpl("struct_spec_v1"), seg)
    p = fill(tpl("final_v2"), seg, STRUCT_SPEC=spec, REVIEW=render_review(seg, "rev1_b", "rev2_b"))
    return finish("final_b", seg, call("final_b", seg, p, session=handle("gen_b", seg)))


# ---- selection (DAG A only): per-segment winner of the last blind 3-way comparison ----
CHOSEN = {"S01": "final_b", "S02": "final_b", "S03": "final", "S04": "final", "S05": "final_b", "S06": "final_b",
          "S07": "final", "S08": "final3", "S09": "final_b", "S10": "final_b", "S11": "final", "S12": "final_b",
          "S13": "final_b", "S14": "final_b"}
GEN_OF = {"final": "gen", "final2": "gen", "final3": "gen", "final_b": "gen_b", "final2_b": "gen_b"}


def materialize_chosen():
    (RUNS / "chosen").mkdir(parents=True, exist_ok=True)
    for s, st in CHOSEN.items():
        d = dict(load(st, s)); d["_from"] = st
        save("chosen", s, d)


def t_fix_c(seg):
    return t_fix(seg, "piece_c", GEN_OF[CHOSEN[seg]], "final2_c")


def t_fix_fresh(seg, src="piece_b", base="final_b", out="final2_b"):
    """Op.61: the gen_b sessions passed gpt3's 6 h lifetime, so the fix runs in a fresh session that is given
    the segment's own final_b STRUCT verbatim (minus script marks) plus the same 24 sources."""
    prev = {k: v for k, v in load(base, seg).items() if not k.startswith("_")}
    def strip(x):
        if isinstance(x, dict):
            return {k: strip(v) for k, v in x.items() if k not in ("quote_verified", "quote_found_in")}
        if isinstance(x, list):
            return [strip(v) for v in x]
        return x
    head = (f"下面是你此前为肖邦《幻想波兰舞曲》Op.61 的 {seg}（第 {mm(seg)} 小节，{SEGS[seg][1]}）写出的最终 Bead / STRUCT。"
            "附件 `sources.zip` 的 `A/` 是写作时依据的 24 份历史聆听原稿（文件名即来源 ID）。\n\n"
            "```json\n" + json.dumps(strip(prev), ensure_ascii=False, indent=0) + "\n```\n\n")
    spec = fill(tpl("struct_spec_v1"), seg)
    txt = "```json\n" + json.dumps(piece_for(seg, src), ensure_ascii=False, indent=0) + "\n```"
    p = head + fill(tpl("fix_v1"), seg, STRUCT_SPEC=spec, PIECE=txt)
    return finish(out, seg, call(out, seg, p, [sources_zip()]))


TASKS = {
    "gen": (t_gen, lambda s: []), "rev1": (t_rev1, lambda s: []),
    "rev2": (t_rev2, lambda s: [("gen", s), ("rev1", s)]),
    "final": (t_final, lambda s: [("rev2", s)]),
    "prod": (lambda s: t_prod(s, True), lambda s: []),
    "nopool": (lambda s: t_prod(s, False), lambda s: []),
    "prod2": (lambda s: t_prod(s, True, "prod_v2", "prod2"), lambda s: []),
    "cmp2": (lambda s: t_cmp(s, ["final", "prod", "prod2"], "cmp2"), lambda s: [("final", s), ("prod", s), ("prod2", s)]),
    "final3": (t_trim, lambda s: [("cmp2", s)]),
    "cmp3": (t_cmp3, lambda s: [("final3", s)]),
    "pool": (t_pool, lambda s: []),
    "gen_b": (t_gen_b, lambda s: [("pool", s)]), "rev1_b": (t_rev1_b, lambda s: []),
    "rev2_b": (t_rev2_b, lambda s: [("gen_b", s), ("rev1_b", s)]),
    "final_b": (t_final_b, lambda s: [("rev2_b", s)]),
    "cmpb": (lambda s: t_cmp(s, ["final_b", "final", "prod"], "cmpb"), lambda s: [("final_b", s)]),
    "final2_b": (lambda s: t_fix_fresh(s), lambda s: [("final_b", s)]),
    "final2_c": (t_fix_c, lambda s: []),
    "final2": (t_fix, lambda s: [("final", s)]),
    "cmp": (t_cmp, lambda s: [("final", s), ("prod", s)] + ([("nopool", s)] if s in NOPOOL_SEGS else [])),
}
PRIORITY = ["pool", "final_b", "rev2_b", "cmpb", "gen_b", "rev1_b", "final3", "cmp3", "final2", "prod2", "cmp2", "final", "rev2", "gen", "rev1", "cmp", "prod", "nopool"]


def done(stage, seg):
    if stage == "pool":
        return (RUNS / "pool_v2" / "pool" / f"{seg}.parsed.json").exists()
    return (RUNS / stage / f"{seg}.parsed.json").exists()


def blocked(stage, seg):
    d = RUNS / ("pool_v2/pool" if stage == "pool" else stage)
    return (d / f"{seg}.uncertain.json").exists() or (d / f"{seg}.parse_error.txt").exists()


def parallel():
    try:
        return int((RUNS / "parallel.txt").read_text().strip())
    except Exception:
        return 6


def run(stages, segs):
    pending = {(st, s) for st in stages for s in segs if not (st == "nopool" and s not in NOPOOL_SEGS)}
    pending = {t for t in pending if not done(*t)}
    running, failed = set(), set()
    lock = threading.Lock()

    def worker(t):
        ok = False
        try:
            ok = TASKS[t[0]][0](t[1])
        except Exception as e:
            print(f"[{t[0]}/{t[1]}] EXC {e!r}", flush=True)
        with lock:
            running.discard(t)
            if not ok:
                failed.add(t)

    while True:
        with lock:
            for t in list(pending):
                if blocked(*t):
                    pending.discard(t); failed.add(t)
            ready = [t for t in pending if all(done(*d) for d in TASKS[t[0]][1](t[1]))]
            dead = [t for t in pending if any(d in failed for d in TASKS[t[0]][1](t[1]))]
            for t in dead:
                pending.discard(t); failed.add(t)
            ready.sort(key=lambda t: (PRIORITY.index(t[0]) if t[0] in PRIORITY else 0, t[1]))
            slots = parallel() - len(running)
            launch = ready[:max(0, slots)]
            for t in launch:
                pending.discard(t); running.add(t)
            if not pending and not running:
                break
        for t in launch:
            threading.Thread(target=worker, args=(t,), daemon=True).start()
            time.sleep(0.2)
        time.sleep(3)
    print("DONE; failed:", sorted(failed), flush=True)


def status():
    for st in TASKS:
        d = RUNS / st
        ok = sorted(p.name[:3] for p in d.glob("S*.parsed.json")) if d.exists() else []
        unc = sorted(p.name[:3] for p in d.glob("S*.uncertain.json")) if d.exists() else []
        print(f"{st:7s} done {len(ok):2d} {','.join(ok)}" + (f"  UNCERTAIN {unc}" if unc else ""))


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("cmd"); ap.add_argument("--stages", default="gen,rev1,rev2,final,prod,nopool,cmp")
    ap.add_argument("--segs", default="all"); a = ap.parse_args()
    segs = list(SEGS) if a.segs == "all" else a.segs.split(",")
    if a.cmd == "fixlist":
        print(",".join(s for s in SEGS if needs_fix(s)))
    elif a.cmd == "piece":
        if a.stages == "chosen":
            materialize_chosen()
        t_piece(a.stages, {"final": "piece", "final_b": "piece_b", "chosen": "piece_c"}.get(a.stages, "piece_" + a.stages))
    elif a.cmd == "run":
        run(a.stages.split(","), segs)
    else:
        status()
