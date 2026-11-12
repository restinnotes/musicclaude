"""ModelTrace control through MimicGate (real browser container, High): same 3 challenges, unmodified prompt text.
usage (cwd = _thread_evo_20261019): python mt_mimic.py <g6|g56> <outdir>"""
import importlib.util, json, sys, time
from pathlib import Path
sys.path.insert(0, r"D:\musicclaude\_thread_evo_20261019")
import evo, mg_call

P = Path(r"C:\Users\zuoyi\Documents\Codex\2026-09-26\j\work\modeltrace-ab-20260927")
spec = importlib.util.spec_from_file_location("fp", P / "ModelTrace" / "fingerprint.py")
fp = importlib.util.module_from_spec(spec); spec.loader.exec_module(fp)
bank = fp.load_bank(P / "ModelTrace" / "data" / "unified_bank.json")
ch = json.loads((P / "challenges" / "official_modeltrace_challenges.json").read_text(encoding="utf-8"))
which, out = sys.argv[1], Path(sys.argv[2]); out.mkdir(parents=True, exist_ok=True)
model = evo.G6 if which == "g6" else evo.G56
outs, recs = [], []
for i, c in enumerate(ch):
    rid = f"mtmg_{which}_{i + 1}_20261027"; (evo.RUNS / rid).mkdir(parents=True, exist_ok=True)
    t = time.time()
    try:
        text = mg_call.call(rid, c["prompt"], c["prompt"], model, {"web": True, "stage": "modeltrace"}) or ""
    except Exception as e:
        text = ""; print(rid, "error", repr(e)[:300], flush=True)
    (out / f"mimic_{which}_{i + 1}.txt").write_text(text, encoding="utf-8")
    n = len(fp.parse_numbers(text))
    recs.append({"probe": i + 1, "seconds": round(time.time() - t), "numbers": n, "expected": c["expected_count"]})
    print(json.dumps(recs[-1]), flush=True)
    if n >= max(80, int(c["expected_count"] * .55 + .999)):
        outs.append({"text": text, "expected_count": c["expected_count"]})
an = fp.analyze_global_outputs(outs, bank) if outs else None
(out / f"mimic_{which}_summary.json").write_text(json.dumps({"probes": recs, "analysis": an}, ensure_ascii=False, indent=1), encoding="utf-8")
print(json.dumps({"prediction": an and an["prediction"], "top": an and [(r["model"], round(r["probability"], 4)) for r in an["results"][:4]]}) if an else "no valid outputs", flush=True)
