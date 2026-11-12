"""Run blind judging of packed batches through gpt3, and aggregate.

  python judge.py run --tag J1 --prompt judge_v1 --reps 1
  python judge.py agg --tag J1
"""
import argparse, json, re, sys, threading
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import evo  # noqa

ROOT = evo.ROOT


def parse(resp):
    m = re.findall(r"```json\s*(.*?)```", resp, re.S)
    return json.loads(m[-1] if m else resp)


def cmd_run(a):
    ths = []
    for bd in sorted((ROOT / "evaluations" / a.tag).glob("batch*")):
        key = json.loads((bd / "key.json").read_text(encoding="utf-8"))
        labels = [k["label"] for k in key]
        tpl = (ROOT / "prompts" / f"{a.prompt}.md").read_text(encoding="utf-8")
        text = tpl.replace("{N}", str(len(labels))).replace("{LABELS}", "、".join(labels))
        for r in range(1, a.reps + 1):
            out = bd / f"gpt6_{a.prompt}_{r}"
            if (out / "output.txt").exists():
                continue
            ths.append(threading.Thread(target=evo.gpt3_call, args=(text, out, [bd / "articles.md"])))
    for t in ths: t.start()
    for t in ths: t.join()


def cmd_agg(a):
    base = ROOT / "evaluations" / a.tag
    per = defaultdict(list)     # run -> list of (judge, normalized rank, scores)
    rows = []
    for bd in sorted(base.glob("batch*")):
        key = {k["label"]: k for k in json.loads((bd / "key.json").read_text(encoding="utf-8"))}
        for jd in sorted(bd.iterdir()):
            f = jd / "output.txt" if jd.is_dir() else None
            if not f or not f.exists():
                continue
            try:
                j = parse(f.read_text(encoding="utf-8"))
            except Exception as e:
                print("parse fail", jd, e); continue
            rk = j["ranking"]; n = len(rk)
            for i, lab in enumerate(rk):
                lab = lab.strip()
                if lab not in key:
                    continue
                k = key[lab]; s = j["articles"].get(lab, {})
                nr = 1 - i / (n - 1) if n > 1 else 1.0   # 1 = best in batch
                per[k["run"]].append({"judge": f"{bd.name}/{jd.name}", "nrank": nr, **{x: s.get(x) for x in ("thread", "alive", "accumulation", "music_credibility", "overall")},
                                      "fp": s.get("false_positives", []), "cond": k["cond"], "prompt": k["prompt"]})
    bycond = defaultdict(list)
    for run, L in per.items():
        for x in L:
            bycond[(x["prompt"], x["cond"])].append(x)
    def avg(L, k):
        v = [x[k] for x in L if isinstance(x.get(k), (int, float))]
        return round(sum(v) / len(v), 2) if v else None
    lines = ["group\tn_judgements\tnrank\toverall\tthread\talive\taccum\tmusic\tFP counts"]
    for g, L in sorted(bycond.items(), key=lambda kv: -avg(kv[1], "nrank")):
        fp = defaultdict(int)
        for x in L:
            for q in x["fp"]: fp[q[:2]] += 1
        lines.append(f"{g[0]}/{g[1]}\t{len(L)}\t{avg(L,'nrank')}\t{avg(L,'overall')}\t{avg(L,'thread')}\t{avg(L,'alive')}\t{avg(L,'accumulation')}\t{avg(L,'music_credibility')}\t{dict(fp)}")
    lines.append("")
    lines.append("run\tnrank\toverall\tjudges")
    for run, L in sorted(per.items(), key=lambda kv: -avg(kv[1], "nrank")):
        lines.append(f"{run}\t{avg(L,'nrank')}\t{avg(L,'overall')}\t{len(L)}")
    txt = "\n".join(lines)
    (base / "aggregate.tsv").write_text(txt, encoding="utf-8")
    (base / "per_run.json").write_text(json.dumps(per, ensure_ascii=False, indent=1), encoding="utf-8")
    sys.stdout.reconfigure(encoding="utf-8"); print(txt)


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); sp = ap.add_subparsers(dest="c", required=True)
    r = sp.add_parser("run"); r.add_argument("--tag", required=True); r.add_argument("--prompt", default="judge_v1"); r.add_argument("--reps", type=int, default=1)
    g = sp.add_parser("agg"); g.add_argument("--tag", required=True)
    a = ap.parse_args()
    {"run": cmd_run, "agg": cmd_agg}[a.c](a)
