"""N03 work-parameterized upstream entry.
production: reuse sat.py's pool -> gen_b -> rev1_b -> rev2_b -> final_b -> piece_b -> flagged final2_b.
render: capture every production prompt offline from existing parsed payloads.
Legacy pool/synth/audit/report/build/display stages remain available; prompt versions come from chain_config.json.
Use --work KEY or WORK, with metadata in _thread_evo_20261019/works/KEY/work.json.
"""
import argparse, os, hashlib, json, random, re, subprocess, sys, threading, time, zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CFG = json.loads((ROOT / "chain_config.json").read_text(encoding="utf-8"))
GPT3 = CFG["gpt3"]
sys.path.insert(0, str(ROOT.parent / "_thread_evo_20261019"))
import work_meta
META = None
INP = ROOT / "inputs"
SEGS = {}; SHORT = {}; A = {}; NA = {}


def configure(work=None):
    global ROOT, META, INP, SEGS, SHORT, A, NA
    META = work_meta.load(work or os.environ.get("WORK", "op61"))
    sd = work_meta.segmentation(META)
    # Preserve old paths for registered experiments; new works have their own cache namespace.
    ROOT = Path(META.get("bead_legacy_root") or META["_dir"] / "bead")
    INP = ROOT / "inputs"
    SEGS = {x["id"]: (f"{x['start']}-{x['end']}", x.get("label", "")) for x in sd["segments"]}
    SHORT = {x["segment"]: x for x in json.loads((INP / "short_beads_ref.json").read_text(encoding="utf-8"))} if (INP / "short_beads_ref.json").exists() else {}
    A = {p.stem: p.read_text(encoding="utf-8-sig") for p in sorted(work_meta.source_dir(META).glob("*.md"))}
    NA = {k: norm(v) for k, v in A.items()}
    return sd



def mmr(seg):
    return SEGS[seg][0].replace("-", "–")


def norm(s):
    return re.sub(r"[\s\*`“”\"'‘’「」『』《》，。、；：！？,.;:!?（）()\-—–…·]", "", s or "")


def quote_ok(src, q):
    q = norm(q)
    return bool(q) and src in NA and q in NA[src]


def span(s):
    m = re.findall(r"\d+", s or "")
    return (int(m[0]), int(m[-1])) if m else None


def overlaps(seg, measures):
    a, b = span(SEGS[seg][0]); sp = span(measures)
    return sp is None or (sp[0] <= b and sp[1] >= a)


def in_seg(seg, measures):
    a, b = span(SEGS[seg][0]); sp = span(measures)
    return sp is not None and a <= sp[0] <= sp[1] <= b


# ---------------- gpt3 ----------------
_lock = threading.Lock(); _last = [0.0]


def gpt3(prompt_text, attach, outdir: Path, name):
    for attempt in range(1 + CFG.get("retries", 1)):
        r = _gpt3_once(prompt_text, attach, outdir, name)
        if r is not None:
            return r
        time.sleep(30)
    return None


def _gpt3_once(prompt_text, attach, outdir: Path, name):
    outdir.mkdir(parents=True, exist_ok=True)
    pf = outdir / f"{name}.prompt.txt"
    pf.write_text(prompt_text, encoding="utf-8")
    with _lock:
        w = CFG.get("min_start_gap_s", 7) - (time.time() - _last[0])
        if w > 0:
            time.sleep(w)
        _last[0] = time.time()
    cmd = [GPT3, "ask", "--file", str(pf), "--json"]
    for a in attach:
        cmd += ["--attach", str(a)]
    t0 = time.time()
    cp = subprocess.run(cmd, capture_output=True)
    dt = time.time() - t0
    (outdir / f"{name}.stdout.bin").write_bytes(cp.stdout)
    (outdir / f"{name}.stderr.bin").write_bytes(cp.stderr)
    m = re.search(rb'"job_directory":\s*"((?:[^"\\]|\\.)*)"', cp.stdout)
    job = Path(json.loads(b'"' + m.group(1) + b'"')) if m else None
    ok = cp.returncode == 0 and job and (job / "response.txt").exists() and b'"completed": true' in cp.stdout
    if not ok:
        print(f"[{name}] FAILED rc={cp.returncode} {dt:.0f}s", flush=True)
        return None
    resp = (job / "response.txt").read_text(encoding="utf-8")
    jr = json.loads((job / "result.json").read_text(encoding="utf-8"))
    tv = json.loads((job / "terminal-verification.json").read_text(encoding="utf-8"))
    fm = (tv.get("final_messages") or [{}])[0]
    meta = {"job_directory": str(job), "model": fm.get("model"), "effort": fm.get("effort"),
            "status": fm.get("status"), "terminal_completion_verified": tv.get("terminal_completion_verified"),
            "elapsed_seconds": jr.get("elapsed_seconds"), "tools_used": jr.get("toolsUsed"),
            "temporary": jr.get("temporary"), "unpersonalized": jr.get("unpersonalized"),
            "prompt_sha256": hashlib.sha256(prompt_text.encode("utf-8")).hexdigest(),
            "response_sha256": hashlib.sha256(resp.encode("utf-8")).hexdigest(),
            "attachments": [str(a) for a in attach]}
    (outdir / f"{name}.response.txt").write_text(resp, encoding="utf-8")
    (outdir / f"{name}.meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"[{name}] ok {dt:.0f}s model={meta['model']}/{meta['effort']}", flush=True)
    return resp


def parse_json(resp):
    m = re.findall(r"```json\s*(.*?)```", resp, re.S)
    return json.loads(m[-1] if m else resp)


def load(tag, stage, seg):
    p = ROOT / "runs" / tag / stage / f"{seg}.parsed.json"
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else None


def bundle_A():
    z = ROOT / "runs" / "sources.zip"
    if not z.exists():
        with zipfile.ZipFile(z, "w", zipfile.ZIP_DEFLATED) as f:
            for k, v in A.items():
                f.writestr(f"A/{k}.md", v)
    return z


def bundle_ref():
    z = ROOT / "runs" / "sources_with_short.zip"
    if not z.exists():
        with zipfile.ZipFile(z, "w", zipfile.ZIP_DEFLATED) as f:
            for k, v in A.items():
                f.writestr(f"A/{k}.md", v)
            f.write(INP / "structure.json", "structure.json")
            f.write(INP / "short_beads_ref.json", "short_beads_ref.json")
    return z


def fill(tpl, seg, **kw):
    s = tpl.replace("{SEG}", seg).replace("{MM}", mmr(seg)).replace("{LABEL}", SEGS[seg][1])
    for k, v in kw.items():
        s = s.replace("{" + k + "}", v)
    return s


def prompt(stage):
    return template(f"{stage}_{CFG['prompts'][stage]}")


# ---------------- stages ----------------
def st_pool(tag, seg):
    out = ROOT / "runs" / tag / "pool"
    if (out / f"{seg}.parsed.json").exists():
        return
    r = gpt3(fill(prompt("pool"), seg), [bundle_A()], out, seg)
    if r:
        d = parse_json(r)
        for it in d.get("items", []):
            it["quote_verified"] = quote_ok(it.get("src", ""), it.get("quote", ""))
        (out / f"{seg}.parsed.json").write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")


def st_synth(tag, seg):
    out = ROOT / "runs" / tag / "synth"
    if (out / f"{seg}.parsed.json").exists():
        return
    pool = load(tag, "pool", seg)
    if not pool:
        print(f"[{seg}] no pool; skip synth"); return
    items = [{k: v for k, v in it.items() if k != "quote_verified"} for it in pool["items"]]
    sb = SHORT[seg]
    r = gpt3(fill(prompt("synth"), seg, POOL=json.dumps(items, ensure_ascii=False, indent=0),
                  SHORT_TITLE=sb["title"], SHORT_BODY=sb["body"], SHORT_LEN=str(len(sb["body"]))),
             [bundle_ref()], out, seg)
    if r:
        (out / f"{seg}.parsed.json").write_text(json.dumps(parse_json(r), ensure_ascii=False, indent=1), encoding="utf-8")


def st_display(tag, seg, src_tag):
    out = ROOT / "runs" / tag / "display"
    if (out / f"{seg}.parsed.json").exists():
        return
    d = load(src_tag, "synth", seg)
    if not d:
        print(f"[{seg}] no synth in {src_tag}"); return
    st = {"timeline": d.get("timeline", []),
          "facets": [{k: f.get(k) for k in ("id", "measures", "placement", "dimensions", "claim", "image", "validity", "salience", "relations") if k in f} for f in d.get("facets", [])],
          "readings": [{k: r.get(k) for k in ("id", "summary", "facet_ids", "relation", "depends_on_performance")} for r in d.get("readings", [])],
          "carryover": [{k: c.get(k) for k in ("from_range", "claim")} for c in d.get("carryover", [])]}
    start = span(SEGS[seg][0])[0]
    r = gpt3(fill(prompt("display"), seg, STRUCT=json.dumps(st, ensure_ascii=False, indent=0), START=str(start)), [], out, seg)
    if r:
        (out / f"{seg}.parsed.json").write_text(json.dumps(parse_json(r), ensure_ascii=False, indent=1), encoding="utf-8")


def display_checks(tag, src_tag, seg):
    d = load(tag, "display", seg); s = load(src_tag, "synth", seg)
    if not d or not s:
        return None
    fids = [f["id"] for f in s["facets"]]; fm = {f["id"]: span(f.get("measures")) for f in s["facets"]}
    seen = []
    bad_place = []
    prev_end = None; step_errs = []
    for st in d.get("steps", []):
        sp = span(st.get("measures"))
        if not in_seg(seg, st.get("measures", "")):
            step_errs.append(f"out:{st.get('measures')}")
        if sp and prev_end is not None and sp[0] < prev_end:
            step_errs.append(f"overlap:{st.get('measures')}")
        if sp:
            prev_end = sp[1]
        for kind in ("now", "also"):
            for it in st.get(kind, []):
                seen.append(it.get("facet"))
                fsp = fm.get(it.get("facet"))
                if sp and fsp and not (fsp[0] <= sp[1] and fsp[1] >= sp[0]):
                    bad_place.append(f"{it.get('facet')}@{st.get('measures')}")
    seen += [it.get("facet") for it in d.get("base", [])]
    lines = [it.get("text", "") for st in d.get("steps", []) for k in ("now", "also") for it in st.get(k, [])] + [it.get("text", "") for it in d.get("base", [])]
    rids = [r["id"] for r in s.get("readings", [])]
    rseen = [it.get("reading") for it in d.get("readings", [])]
    return {"facets": len(fids), "missing": sorted(set(fids) - set(seen)), "duplicated": sorted({x for x in seen if seen.count(x) > 1}),
            "unknown": sorted(set(seen) - set(fids)), "readings_missing": sorted(set(rids) - set(rseen)),
            "carryover": f"{len(d.get('carryover', []))}/{len(s.get('carryover', []))}",
            "steps": len(d.get("steps", [])), "step_errors": step_errs, "placement_mismatch": bad_place,
            "line_len_max": max((len(x) for x in lines), default=0), "lines_over_34": sum(len(x) > 34 for x in lines)}


def render_version(target, seg):
    """Returns (reader_text, struct_text_or_None) for audit, stripped of source attributions."""
    if target == "short":
        b = SHORT[seg]; return f"{b['title']}\n\n{b['body']}", None
    if target == "v1":
        d = json.loads((INP / "baselines" / "v1" / f"{seg}.json").read_text(encoding="utf-8"))
        rb = d["reader_bead"]; s = d["struct"]
        st = {"facets": [{k: f.get(k) for k in ("id", "measures", "kind", "claim", "note")} for f in s.get("facets", [])],
              "alternative_readings": [{k: r.get(k) for k in ("id", "reading", "conflicts_with", "depends_on_performance")} for r in s.get("alternative_readings", [])],
              "internal_sequence": s.get("internal_sequence", [])}
        return f"{rb['title']}\n\n{rb['body']}", json.dumps(st, ensure_ascii=False, indent=0)
    d = load(target, "synth", seg)
    if not d:
        return None, None
    rb = d["reader_bead"]
    st = {"facets": [{k: f.get(k) for k in ("id", "measures", "source_range", "placement", "placement_note", "dimensions", "claim", "relations") if k in f} for f in d.get("facets", [])],
          "readings": [{k: r.get(k) for k in ("id", "summary", "anchor_sources", "facet_ids", "relation", "depends_on_performance")} for r in d.get("readings", [])],
          "timeline": d.get("timeline", [])}
    return f"{rb['title']}\n\n{rb['body']}", json.dumps(st, ensure_ascii=False, indent=0)


def st_audit(tag, seg, targets):
    out = ROOT / "runs" / tag / "audit"
    if (out / f"{seg}.parsed.json").exists():
        return
    labels = ["甲", "乙", "丙", "丁"][:len(targets)]
    order = list(targets)
    random.Random(f"{tag}-{seg}").shuffle(order)
    mapping = dict(zip(labels, order))
    blocks = []
    for lab in labels:
        rd, st = render_version(mapping[lab], seg)
        if rd is None:
            print(f"[{seg}] missing target {mapping[lab]}"); return
        blk = f"## 版本{lab}\n\n### 读者正文\n\n{rd}\n"
        blk += f"\n### 内部结构化资料\n\n```json\n{st}\n```\n" if st else "\n（此版本没有内部结构化资料）\n"
        blocks.append(blk)
    r = gpt3(fill(prompt("audit"), seg, LABELS="、".join(labels), VERSIONS="\n".join(blocks)), [bundle_A()], out, seg)
    if r:
        d = parse_json(r)
        d["_mapping"] = mapping
        for e in d.get("experiences", []):
            for s in e.get("sources", []):
                s["quote_verified"] = quote_ok(s.get("src", ""), s.get("quote", ""))
            e["in_segment"] = in_seg(seg, e.get("measures", ""))
        (out / f"{seg}.parsed.json").write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")


# ---------------- metrics ----------------
def audit_metrics(tag, segs):
    rows = []
    for seg in segs:
        d = load(tag, "audit", seg)
        if not d:
            continue
        ex = [e for e in d.get("experiences", []) if overlaps(seg, e.get("measures", ""))]
        good = {e["id"] for e in ex if e.get("validity") in ("solid", "plausible")}
        solid = {e["id"] for e in ex if e.get("validity") == "solid"}
        for lab, tgt in d["_mapping"].items():
            v = d["versions"].get(lab, {})
            rc = set(v.get("reader_covers") or []); sc = set(v.get("struct_covers") or []) if v.get("struct_covers") is not None else None
            allc = rc | (sc or set())
            errs = v.get("errors", [])
            rows.append({"seg": seg, "target": tgt, "n_exp": len(good), "n_solid": len(solid),
                         "reader_cov": len(rc & good) / max(1, len(good)),
                         "all_cov": len(allc & good) / max(1, len(good)),
                         "solid_cov": len(allc & solid) / max(1, len(solid)),
                         "dims": len(v.get("dimensions_present") or []), "readings": v.get("distinct_readings"),
                         "readability": v.get("readability"),
                         "err": len(errs), "err_types": [e.get("type") for e in errs]})
    return rows


def summarize(rows):
    by = {}
    for r in rows:
        by.setdefault(r["target"], []).append(r)
    lines = []
    for t, rs in by.items():
        n = len(rs); avg = lambda k: sum((r[k] or 0) for r in rs) / n
        et = {}
        for r in rs:
            for x in r["err_types"]:
                et[x] = et.get(x, 0) + 1
        lines.append(f"{t:6s} n={n} 正文覆盖={avg('reader_cov'):.0%} 总覆盖={avg('all_cov'):.0%} solid覆盖={avg('solid_cov'):.0%} "
                     f"维度={avg('dims'):.1f} 读法={avg('readings'):.1f} 可读性={avg('readability'):.2f} 错误/段={avg('err'):.1f} {et}")
    return "\n".join(lines)


def rel_errors(d):
    fm = {f["id"]: span(f.get("measures")) for f in d.get("facets", [])}
    bad = []
    for f in d.get("facets", []):
        a = fm.get(f["id"])
        for r in f.get("relations", []) or []:
            b = fm.get(r.get("to"))
            if not a or not b:
                continue
            if r.get("type") == "after" and a[0] < b[0]:
                bad.append(f"{f['id']} after {r['to']}")
            if r.get("type") == "before" and a[0] > b[0]:
                bad.append(f"{f['id']} before {r['to']}")
    return bad


def reading_errors(d):
    sup = {f["id"]: {x.get("src") for x in f.get("support", [])} for f in d.get("facets", [])}
    bad = []
    for r in d.get("readings", []):
        anc = set(r.get("anchor_sources") or [])
        if not anc:
            continue
        for fid in r.get("facet_ids", []):
            if fid in sup and not (sup[fid] & anc):
                bad.append(f"{r['id']}:{fid}")
    return bad


def st_report(tag, segs):
    rows = audit_metrics(tag, segs)
    out = ROOT / "runs" / tag
    (out / "audit_metrics.json").write_text(json.dumps(rows, ensure_ascii=False, indent=1), encoding="utf-8")
    s = summarize(rows)
    (out / "audit_summary.txt").write_text(s, encoding="utf-8")
    print(s)
    checks = {}
    for seg in segs:
        d = load(tag, "synth", seg); p = load(tag, "pool", seg)
        if not d:
            continue
        fids = {f["id"] for f in d.get("facets", [])}
        pids = {it["id"] for it in (p or {}).get("items", []) if it.get("applies") != "none"}
        disp = {x.get("pool_id") for x in d.get("ledger", [])}
        q = [(s.get("src"), s.get("quote")) for f in d.get("facets", []) for s in f.get("support", [])]
        checks[seg] = {
            "facets": len(fids), "readings": len(d.get("readings", [])),
            "pool_items": len(pids), "pool_undispositioned": sorted(pids - disp),
            "pool_sources_missing": sorted(set(A) - set((p or {}).get("sources_checked", {}))) if p else None,
            "pool_quote_ok": f"{sum(it['quote_verified'] for it in p['items'])}/{len(p['items'])}" if p else None,
            "facet_quote_ok": f"{sum(quote_ok(a, b) for a, b in q)}/{len(q)}",
            "facet_out_of_segment": [f["id"] for f in d.get("facets", []) if not in_seg(seg, f.get("measures", ""))],
            "relation_direction_errors": rel_errors(d),
            "reading_unanchored_facets": reading_errors(d),
            "reader_unknown_facets": sorted(set(d["reader_bead"].get("facet_ids", [])) - fids),
            "reader_chars": len(d["reader_bead"]["body"]), "short_chars": len(SHORT[seg]["body"])}
    if checks:
        (out / "checks.json").write_text(json.dumps(checks, ensure_ascii=False, indent=1), encoding="utf-8")
        for k, v in checks.items():
            print(k, v)


def st_build(tag, segs, out_dir):
    """Assemble deliverables verbatim from model outputs; no model calls, no human edits."""
    out = Path(out_dir); (out / "struct").mkdir(parents=True, exist_ok=True); (out / "evidence").mkdir(exist_ok=True)
    reader, diffs, ev = [], [], []
    for seg in segs:
        d = load(tag, "synth", seg)
        if not d:
            reader.append(f"## {seg} ·（缺失）\n"); continue
        for f in d.get("facets", []):
            for x in f.get("support", []):
                x["quote_verified"] = quote_ok(x.get("src", ""), x.get("quote", ""))
        (out / "struct" / f"{seg}.json").write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")
        rb = d["reader_bead"]
        reader.append(f"## {seg} · 第{mmr(seg)}小节｜{rb['title']}\n\n{rb['body'].strip()}\n")
        diffs.append(f"## {seg}\n\n短版：{SHORT[seg]['title']}（{len(SHORT[seg]['body'])}字）→ 新：{rb['title']}（{len(rb['body'])}字）\n\n{d.get('diff_vs_short','').strip()}\n")
        for st in ("pool", "synth", "audit"):
            m = ROOT / "runs" / tag / st / f"{seg}.meta.json"
            if m.exists():
                e = json.loads(m.read_text(encoding="utf-8")); e.update(segment=seg, stage=st); ev.append(e)
                for suf in ("prompt.txt", "response.txt"):
                    src = ROOT / "runs" / tag / st / f"{seg}.{suf}"
                    (out / "evidence" / f"{seg}.{st}.{suf}").write_text(src.read_text(encoding="utf-8"), encoding="utf-8")
    head = (f"# {work_meta.name(META)} · {work_meta.chinese_number(len(SEGS))}颗珠子\n\n沿用 {META['segmentation_source']}{work_meta.chinese_number(len(SEGS))}段。正文为 gpt3（GPT-6 Thinking / max）链路逐段生成的原样输出，"
            "未经人工改写；情景与人物动作是聆听比喻，不是作曲家生平或唯一演奏解释。\n\n")
    (out / "READER.md").write_text(head + "\n".join(reader), encoding="utf-8")
    (out / "DIFF_vs_short.md").write_text("# 与旧短版的差异（文字为模型自述，字数由脚本计算）\n\n" + "\n".join(diffs), encoding="utf-8")
    (out / "EVIDENCE.json").write_text(json.dumps(ev, ensure_ascii=False, indent=1), encoding="utf-8")
    for f in ("audit_summary.txt", "audit_metrics.json", "checks.json"):
        if (ROOT / "runs" / tag / f).exists():
            (out / f).write_text((ROOT / "runs" / tag / f).read_text(encoding="utf-8"), encoding="utf-8")
    print(f"built {out}")


def par_map(fn, segs, par):
    sem = threading.Semaphore(par)
    def w(s):
        with sem:
            try:
                fn(s)
            except Exception as e:
                print(f"[{s}] ERROR {type(e).__name__}: {e}", flush=True)
    ts = [threading.Thread(target=w, args=(s,)) for s in segs]
    [t.start() for t in ts]; [t.join() for t in ts]


def template(name):
    base = Path(__file__).resolve().parent / "prompts"
    file = base / f"{name}.param.md"
    if not file.exists():
        file = base / f"{name}.param.txt"
    return work_meta.render(file.read_text(encoding="utf-8"), META)


def production_runtime(history_root=None):
    """Reuse the production tasks and pacing/cache rules without changing sat.py."""
    import importlib.util
    spec = importlib.util.spec_from_file_location("_parameterized_bead_sat", Path(__file__).with_name("sat.py"))
    rt = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(rt)
    rt.ROOT = ROOT
    rt.RUNS = Path(history_root) if history_root else ROOT / "runs"
    rt.INP = INP
    rt.SEGS = SEGS
    rt.A = A; rt.NA = NA
    rt.SEC_PER_MEASURE = META["seconds_per_measure"]
    rt.SEGLIST = "；".join(f"{s} 第{rt.mm(s)}小节 {lab}" for s, (_, lab) in SEGS.items())
    rt.tpl = template
    rt.LOG = rt.RUNS / "calls.jsonl"

    class Pool(dict):
        def __missing__(self, seg):
            p = rt.RUNS / "pool_v2" / "pool" / f"{seg}.parsed.json"
            if not p.exists() and META.get("pool_sources") and not history_root:
                p = Path(META["pool_sources"]) / f"{seg}.parsed.json"
            self[seg] = json.loads(p.read_text(encoding="utf-8"))
            return self[seg]

    rt.POOL = Pool()
    original_done = rt.done

    def done(stage, seg):
        if stage == "pool" and META.get("pool_sources") and not history_root:
            return original_done(stage, seg) or (Path(META["pool_sources"]) / f"{seg}.parsed.json").exists()
        return original_done(stage, seg)

    rt.done = done

    def fix_fresh(seg):
        prev = {k: v for k, v in rt.load("final_b", seg).items() if not k.startswith("_")}

        def strip(x):
            if isinstance(x, dict):
                return {k: strip(v) for k, v in x.items() if k not in ("quote_verified", "quote_found_in")}
            if isinstance(x, list):
                return [strip(v) for v in x]
            return x

        head = rt.fill(template("fix_fresh_head").replace("{PREVIOUS}", json.dumps(strip(prev), ensure_ascii=False, indent=0)), seg)
        txt = "```json\n" + json.dumps(rt.piece_for(seg, "piece_b"), ensure_ascii=False, indent=0) + "\n```"
        msg = head + rt.fill(template("fix_v1"), seg, STRUCT_SPEC=rt.fill(template("struct_spec_v1"), seg), PIECE=txt)
        return rt.finish("final2_b", seg, rt.call("final2_b", seg, msg, [rt.sources_zip()]))

    rt.TASKS["final2_b"] = ((fix_fresh if META["fix_session"] == "fresh" else
                            lambda s: rt.t_fix(s, "piece_b", "gen_b", "final2_b")),
                           lambda s: [("final_b", s)])
    rt.parameterized_fix = rt.TASKS["final2_b"][0]
    return rt


def production(a):
    rt = production_runtime(a.history_root)
    segs = list(SEGS) if a.segs == "all" else a.segs.split(",")
    if a.stage == "render":
        if not a.render_dir:
            raise ValueError("render requires --render-dir; --history-root must supply prior stage payloads")
        prompts = {}

        def capture(stage, seg, prompt_text, attach=(), session=None):
            prompts[f"{stage.replace('/', '_')}.{seg}.txt"] = prompt_text
            return None  # finish() makes no writes without a response

        rt.call = capture
        rt.sources_zip = lambda: rt.RUNS / "sources.zip"  # no archive creation during rendering
        for s in segs:
            rt.t_pool(s); rt.t_gen_b(s); rt.t_rev1_b(s); rt.t_rev2_b(s); rt.t_final_b(s)
            prompts[f"struct_spec.{s}.txt"] = rt.fill(template("struct_spec_v1"), s)
        rt.t_piece("final_b", "piece_b")
        for s in segs:
            rt.parameterized_fix(s)
        work_meta.write_prompts(a.render_dir, prompts)
        return
    assert len(A) == 24 and not any(x in k.lower() for k in A for x in ("muse", "opus", "sonnet")), "need the 24 non-Muse, non-Claude A sources"
    rt.run(["pool", "gen_b", "rev1_b", "rev2_b", "final_b"], segs)
    if any(not rt.done("final_b", s) for s in SEGS):
        raise RuntimeError("final_b incomplete: stop before whole-piece review")
    if not rt.done("piece_b", "ALL"):
        if rt.blocked("piece_b", "ALL") or not rt.t_piece("final_b", "piece_b"):
            raise RuntimeError("piece_b blocked or failed")
    flagged = [s for s in SEGS if rt.needs_fix(s, "piece_b")]
    if flagged:
        rt.run(["final2_b"], flagged)
    if any(not rt.done("final2_b", s) for s in flagged):
        raise RuntimeError("flagged fixes incomplete")
    print("N03 complete:", rt.RUNS, "fixed:", flagged)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("stage", choices=["production", "render", "pool", "synth", "audit", "report", "build", "display", "all"])
    ap.add_argument("--tag", default="pool_v2")
    ap.add_argument("--work", default=os.environ.get("WORK", "op61"))
    ap.add_argument("--render-dir")
    ap.add_argument("--history-root", help="offline render: existing N03 runs directory")
    ap.add_argument("--segs", default="all")
    ap.add_argument("--targets", default="short,v1")
    ap.add_argument("--out", default=None)
    ap.add_argument("--from-tag", default=None, help="display: STRUCT source tag")
    ap.add_argument("--par", type=int, default=CFG.get("parallel", 4))
    a = ap.parse_args()
    configure(a.work)
    if a.stage in ("production", "render"):
        return production(a)
    assert len(A) == 24 and not any(x in k.lower() for k in A for x in ("muse", "opus", "sonnet")), "need the 24 non-Muse, non-Claude A sources"
    segs = list(SEGS) if a.segs == "all" else a.segs.split(",")
    tg = a.targets.split(",")
    if a.stage in ("pool", "all"):
        par_map(lambda s: st_pool(a.tag, s), segs, a.par)
    if a.stage in ("synth", "all"):
        par_map(lambda s: st_synth(a.tag, s), segs, a.par)
    if a.stage in ("audit", "all"):
        par_map(lambda s: st_audit(a.tag, s, tg), segs, a.par)
    if a.stage == "display":
        src = a.from_tag or a.tag
        par_map(lambda s: st_display(a.tag, s, src), segs, a.par)
        rep = {s: display_checks(a.tag, src, s) for s in segs}
        (ROOT / "runs" / a.tag / "display_checks.json").write_text(json.dumps(rep, ensure_ascii=False, indent=1), encoding="utf-8")
        for k, v in rep.items():
            print(k, v)
        return
    if a.stage in ("report", "all", "audit"):
        st_report(a.tag, segs)
    if a.stage in ("build", "all"):
        st_build(a.tag, segs, a.out or str(ROOT / "runs" / a.tag / "deliverable"))


if __name__ == "__main__":
    main()
else:
    configure()
