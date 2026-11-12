# -*- coding: utf-8 -*-
"""Mechanical audit of every S01 Pool run.

    python tools\\analyze.py

Checks, per run:
  - output JSON extracted at all
  - sources_checked covers all 24, and its counts agree with items
  - every item.quote occurs verbatim in the named source (exact / whitespace-insensitive / missing)
  - quote length <= 40 and experience <= 50
  - web trace vs self-reported web_sources

Writes analysis/summary.json and analysis/summary.md.
"""
import json
import re
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "input"
RUNS = ROOT / "runs"
OUT = ROOT / "analysis"


def read(p):
    return Path(p).read_text(encoding="utf-8", errors="replace")


def canon(s):
    s = unicodedata.normalize("NFKC", s or "")
    s = s.replace("\u200b", "").replace("\ufeff", "")
    s = re.sub(r"\s+", "", s)
    s = s.replace("“", '"').replace("”", '"').replace("‘", "'").replace("’", "'")
    return s


SOURCES = {p.stem: read(p) for p in sorted((INPUT / "A").glob("*.md"))}
CANON = {k: canon(v) for k, v in SOURCES.items()}


def quote_status(q, src):
    if not q:
        return "empty"
    if src in SOURCES and q in SOURCES[src]:
        return "exact"
    cq = canon(q)
    if not cq:
        return "empty"
    if src in CANON and cq in CANON[src]:
        return "whitespace"
    hits = [k for k, v in CANON.items() if cq in v]
    if hits:
        return "wrong_src:" + ",".join(hits[:3])
    return "missing"


def audit(run):
    meta = json.loads(read(run / "meta.json"))
    trace = json.loads(read(run / "trace.json")) if (run / "trace.json").exists() else {}
    obj = None
    try:
        obj = json.loads(read(run / "output.json"))
    except Exception:
        obj = None
    web = (obj or {}).get("web_sources") or []
    items = (obj or {}).get("items") or []
    exc = (obj or {}).get("excluded") or []
    checked = (obj or {}).get("sources_checked") or {}

    qs = {"exact": 0, "whitespace": 0, "missing": 0, "wrong_src": 0, "empty": 0}
    bad_quotes = []
    for it in items:
        st = quote_status(it.get("quote"), it.get("src"))
        key = st.split(":")[0]
        qs[key] = qs.get(key, 0) + 1
        if key not in ("exact", "whitespace"):
            bad_quotes.append({"id": it.get("id"), "src": it.get("src"), "status": st,
                               "quote": it.get("quote")})
    exc_qs = {"exact": 0, "whitespace": 0, "missing": 0, "wrong_src": 0, "empty": 0}
    for it in exc:
        st = quote_status(it.get("quote"), it.get("src"))
        exc_qs[st.split(":")[0]] += 1

    long_q = [it.get("id") for it in items if len(it.get("quote") or "") > 40]
    long_e = [it.get("id") for it in items if len(it.get("experience") or "") > 50]
    by_src = {}
    for it in items:
        by_src[it.get("src")] = by_src.get(it.get("src"), 0) + 1
    missing_src = sorted(set(SOURCES) - set(checked))
    extra_src = sorted(set(checked) - set(SOURCES))
    mismatch = {k: {"checked": checked.get(k), "items": by_src.get(k, 0)}
                for k in sorted(set(checked) | set(by_src))
                if checked.get(k) != by_src.get(k, 0)}

    cls = trace.get("classification") or {}
    trace_urls = []
    for s in trace.get("searches") or []:
        trace_urls += (s.get("results") or [])
    for f in trace.get("fetches") or []:
        if f.get("url"):
            trace_urls.append(f["url"])
    trace_urls = {u.rstrip("/") for u in trace_urls if u}
    reported = [w.get("url") for w in web if w.get("url")]
    reported_norm = {u.rstrip("/") for u in reported}

    notes = (obj or {}).get("web_notes", "")
    searched = bool(trace.get("searches"))
    fetched = bool(trace.get("fetches"))
    if not searched and not fetched and not reported:
        used = "no_web"
    elif searched and not reported and not url_list(str(notes)):
        used = "searched_not_used"
    elif reported:
        used = "reported_web_sources"
    else:
        used = "web_trace_only"

    return {
        "run": run.name,
        "harness": meta.get("harness"),
        "model": meta.get("model"),
        "seconds": meta.get("seconds"),
        "exit_code": meta.get("exit_code"),
        "output_json": obj is not None,
        "items": len(items),
        "excluded": len(exc),
        "quotes": qs,
        "excluded_quotes": exc_qs,
        "quote_total": len(items),
        "quote_bad": len(bad_quotes),
        "bad_quote_examples": bad_quotes[:8],
        "long_quote_ids": long_q,
        "long_experience_ids": long_e,
        "sources_checked": len(checked),
        "missing_sources": missing_src,
        "extra_sources": extra_src,
        "checked_count_mismatch": mismatch,
        "sources_with_zero": sorted(k for k, v in checked.items() if v == 0),
        "web_mode": cls.get("mode"),
        "searches": cls.get("searches"),
        "fetches": cls.get("fetches"),
        "fetch_ok": cls.get("fetch_ok"),
        "fetch_failed": cls.get("fetch_failed"),
        "tool_errors": cls.get("tool_errors"),
        "file_reads": cls.get("file_reads"),
        "trace_urls": len(trace_urls),
        "reported_web_sources": len(web),
        "reported_urls": reported,
        "reported_in_trace": sorted(reported_norm & trace_urls),
        "reported_not_in_trace": sorted(reported_norm - trace_urls),
        "web_notes": notes,
        "web_use": used,
    }


def url_list(text):
    return re.findall(r"https?://[^\s)\]\"']+", text or "")


def main():
    OUT.mkdir(exist_ok=True)
    rows = []
    for run in sorted(RUNS.iterdir()):
        if run.is_dir() and (run / "meta.json").exists() and (run / "output.md").exists():
            try:
                rows.append(audit(run))
            except Exception as e:
                rows.append({"run": run.name, "audit_error": repr(e)})
    (OUT / "summary.json").write_text(json.dumps(rows, ensure_ascii=False, indent=1), encoding="utf-8")

    lines = ["# S01 Pool — mechanical summary", ""]
    lines.append("| run | harness | model | items | quote exact/ws/missing | 24 sources | web | reported URLs |")
    lines.append("|---|---|---|---|---|---|---|---|")
    for r in rows:
        if "audit_error" in r:
            lines.append(f"| {r['run']} | — | — | — | — | — | audit error | {r['audit_error'][:60]} |")
            continue
        q = r["quotes"]
        lines.append(
            f"| {r['run']} | {r['harness']} | {r['model']} | {r['items']} | "
            f"{q['exact']}/{q['whitespace']}/{q['missing'] + q['wrong_src'] + q['empty']} | "
            f"{'yes' if not r['missing_sources'] and not r['extra_sources'] else 'NO'} | "
            f"{r['web_mode']} | {r['reported_web_sources']} |"
        )
    lines.append("")
    for r in rows:
        if "audit_error" in r:
            continue
        lines += [
            f"## {r['run']}",
            "",
            f"- {r['harness']} / `{r['model']}`, {r['seconds']}s, exit {r['exit_code']}, JSON {r['output_json']}",
            f"- items {r['items']}, excluded {r['excluded']}; quotes exact {r['quotes']['exact']}, "
            f"whitespace {r['quotes']['whitespace']}, missing {r['quotes']['missing']}, "
            f"wrong src {r['quotes']['wrong_src']}, empty {r['quotes']['empty']}",
            f"- sources_checked {r['sources_checked']}/24; missing {r['missing_sources']}; extra {r['extra_sources']}",
            f"- web: mode `{r['web_mode']}`, searches {r['searches']}, fetches {r['fetches']} "
            f"(ok {r['fetch_ok']}, failed {r['fetch_failed']}), reported {r['reported_web_sources']} "
            f"({len(r['reported_in_trace'])} also in trace)",
            f"- web_notes: {r['web_notes'][:300]}",
        ]
        if r["bad_quote_examples"]:
            lines.append(f"- bad quotes: {json.dumps(r['bad_quote_examples'], ensure_ascii=False)[:800]}")
        lines.append("")
    (OUT / "summary.md").write_text("\n".join(lines), encoding="utf-8")
    print(json.dumps({"runs": len(rows), "out": str(OUT)}, ensure_ascii=False))
    for r in rows:
        if "audit_error" not in r:
            print(f"{r['run']}: items={r['items']} quotes={r['quotes']} web={r['web_mode']} reported={r['reported_web_sources']}")


if __name__ == "__main__":
    main()
