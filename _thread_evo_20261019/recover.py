"""Recover answers of calls whose caller died after submitting (10-24: the resume chain was restarted while ~36 bridge
workers were still generating). For every runs/<id>/ without output.txt, find a bridge job of this account whose
prompt.txt equals our input.txt and whose result.json is ok with the requested model at max effort, and write its
response as output.txt, so the next run skips it instead of submitting the same prompt again.
usage: python recover.py [run-id-glob ...]"""
import fnmatch, json, sys
from pathlib import Path
import evo


def jobs():
    out = {}
    for j in evo.GPT3_RUNS.glob("pro-bridge-*"):
        try:
            rj = json.loads((j / "result.json").read_text(encoding="utf-8"))
            rt = (j / "response.txt").read_text(encoding="utf-8-sig")
            pt = (j / "prompt.txt").read_text(encoding="utf-8-sig")
        except Exception:
            continue
        if str(rj.get("ok")) == "True" and str(rj.get("thinkingEffort")) == "max" and rt.strip():
            out.setdefault(pt.strip(), []).append((j.name, rj.get("model"), rt))
    return out


def wanted_model(d):
    """the same prompt often goes to both judges, so the model must match too: failure logs name it, else the run id"""
    for f in sorted(d.glob("call_fail_*.log")):
        cmd = json.loads(f.read_text(encoding="utf-8")).get("command", "")
        if "--model" in cmd:
            return cmd.split("--model")[1].split()[0]
    n = d.name
    if n.endswith("_g56"):   # judge runs end with the judge; check this before the draft name inside the id
        return evo.G56
    if n.endswith("_g6"):
        return evo.G6
    if "56_op6" in n:
        return evo.G56
    if "6_op6" in n:
        return evo.G6
    return None


def claimed():
    """jobs some run already took (repeated samples share one prompt, so a job may be used once only)"""
    out = set()
    for c in evo.RUNS.glob("*/call.log"):
        try:
            r = json.loads(c.read_text(encoding="utf-8"))
        except Exception:
            continue
        j = r.get("job_directory") or r.get("recovered_from_job")
        if isinstance(j, str):
            out.add(Path(j).name)
    return out


if __name__ == "__main__":
    pats = sys.argv[1:] or ["*"]; js = jobs(); n = 0; used = claimed()
    for d in sorted(evo.RUNS.iterdir()):
        if not d.is_dir() or (d / "output.txt").exists() or not (d / "input.txt").exists() or not any(fnmatch.fnmatch(d.name, p) for p in pats):
            continue
        want = wanted_model(d)
        hit = [h for h in js.get((d / "input.txt").read_text(encoding="utf-8").strip(), []) if want and h[1] == want and h[0] not in used]
        if d.name.endswith("_x") and (evo.RUNS / d.name[:-2] / "output.txt").exists():
            hit = []   # the retry id is only needed when the first id has no answer
        if hit:
            name, model, rt = sorted(hit)[-1]; used.add(name)
            (d / "output.txt").write_text(rt, encoding="utf-8")
            (d / "call.log").write_text(json.dumps({"run_id": d.name, "recovered_from_job": name, "model": model, "account": evo.ACCOUNT},
                                                   ensure_ascii=False, indent=1), encoding="utf-8")
            n += 1; print(d.name, "<-", name, model, len(rt))
    print(n, "recovered")
