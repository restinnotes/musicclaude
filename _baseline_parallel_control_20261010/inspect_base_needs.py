import json
from pathlib import Path
w = Path(r"D:\musicclaude\_dl_latest_zip_work")
# base needs (from audit): model job round
base_needs = [
    ("gpt6w", "A01", "r03"), ("gpt6w", "A01", "r04"),
    ("gpt56w", "A02", "r02"), ("gpt56w", "A03", "r03"),
    ("gpt6w", "A05", "r04"), ("gpt6w", "A06", "r01"),
    ("gpt6w", "B02", "r02"), ("gpt56w", "B02", "r04"),
    ("gpt6w", "B11", "r03"), ("gpt6w", "B18", "r04"),
    ("gpt6w", "C18", "r03"), ("gpt6w", "C18", "r04"),
    ("gpt6w", "C20", "r04"), ("gpt6w", "B23", "r01"),
]
for m, j, r in base_needs:
    d = w / "results" / "trials" / m / j
    meta_p = d / (r + ".meta.json")
    raw_p = d / (r + ".raw.json")
    err_p = d / (r + ".stderr.txt")
    meta = json.loads(meta_p.read_text(encoding="utf-8"))
    raw_txt = raw_p.read_text(encoding="utf-8", errors="replace") if raw_p.exists() else "<no raw>"
    err_txt = err_p.read_text(encoding="utf-8", errors="replace") if err_p.exists() else "<no stderr>"
    print("=" * 100)
    print(m, j, r, "| status:", meta.get("status"), "| phase:", meta.get("phase"),
          "| exit:", meta.get("exit_code"), "| elapsed:", meta.get("elapsed_seconds"),
          "| error:", meta.get("error"))
    print("  raw_bytes:", len(raw_txt), "| raw_head:", raw_txt[:400].replace("\n", "\\n"))
    print("  stderr_head:", err_txt[:400].replace("\n", "\\n"))
    # also check latest attempt files for any completed response
    for att in sorted(d.glob(r + ".attempt*.raw.json")):
        t = att.read_text(encoding="utf-8", errors="replace")
        print("  ATT", att.name, "bytes:", len(t), "head:", t[:200].replace("\n", "\\n"))
