"""ModelTrace through the current gpt3 CLI route (yi account, max): 3 official challenges per model, serial per model,
then the closed-set fingerprint ranking.  usage: python mt_gpt3.py <model> <outdir>"""
import importlib.util, json, random, subprocess, sys, time
from pathlib import Path

P = Path(r"C:\Users\zuoyi\Documents\Codex\2026-09-26\j\work\modeltrace-ab-20260927")
GPT3 = r"D:\musicclaude\gpt2agent-safechain\bin\gpt3.cmd"
spec = importlib.util.spec_from_file_location("fp", P / "ModelTrace" / "fingerprint.py")
fp = importlib.util.module_from_spec(spec); spec.loader.exec_module(fp)
bank = fp.load_bank(P / "ModelTrace" / "data" / "unified_bank.json")
ch = json.loads((P / "challenges" / "official_modeltrace_challenges.json").read_text(encoding="utf-8"))
model, out = sys.argv[1], Path(sys.argv[2]); out.mkdir(parents=True, exist_ok=True)
outs, recs = [], []
for i, c in enumerate(ch):
    f = out / f"{model}_{i + 1}.txt"; f.write_text(c["prompt"], encoding="utf-8")
    t = time.time()
    cp = subprocess.run([GPT3, "ask", "--file", str(f), "--json", "--model", model, "--allow-topic-stream"], capture_output=True)
    dt = round(time.time() - t)
    try:
        j = json.loads(cp.stdout.decode("utf-8", "replace")); text = j.get("response") or j.get("text") or ""; md = j.get("metadata") or {}
    except Exception:
        j, text, md = None, "", {}
    (out / f"{model}_{i + 1}.out.json").write_bytes(cp.stdout)
    n = len(fp.parse_numbers(text))
    recs.append({"probe": i + 1, "rc": cp.returncode, "seconds": dt, "numbers": n, "expected": c["expected_count"],
                 "model": md.get("model"), "effort": md.get("thinking_effort"), "err": cp.stderr.decode("utf-8", "replace")[-300:] if cp.returncode else ""})
    print(json.dumps(recs[-1], ensure_ascii=False), flush=True)
    if n >= max(80, int(c["expected_count"] * .55 + .999)):
        outs.append({"text": text, "expected_count": c["expected_count"]})
    elif cp.returncode:
        break
    time.sleep(20 + random.random() * 10)
an = fp.analyze_global_outputs(outs, bank) if outs else None
(out / f"{model}_summary.json").write_text(json.dumps({"probes": recs, "analysis": an}, ensure_ascii=False, indent=1), encoding="utf-8")
print(json.dumps(an, ensure_ascii=False)[:1500] if an else "no valid outputs", flush=True)
