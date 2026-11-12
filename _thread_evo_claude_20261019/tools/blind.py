"""Anonymize Thread articles for blind review and run batched judging through gpt3.

  python blind.py pack --runs r1_*,r1x_* --tag J1 --batches 3 --anchor B0 --seed 1
  -> evaluations/<tag>/batch<k>/{articles.md, key.json}
"""
import argparse, json, random, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
B0 = ROOT / "pkg" / "01_提示词与基准" / "B0_仅十四段_阅读评审版.md"


def clean(t):
    t = re.sub(r"<text[^>]*>(.*?)</text>", r"\1", t, flags=re.S)
    t = re.sub(r"<Cite[^>]*/>", "", t)
    t = re.sub(r"</?WritingBlock[^>]*>", "", t)
    t = re.sub(r"</?[A-Za-z][A-Za-z]*(\s[^<>]*)?/?>", "", t)
    t = re.sub(r"【[^】]*†[^】]*】", "", t)
    out = []
    for line in t.splitlines():
        # drop meta lines that reveal which input material was provided
        if re.search(r"(参考材料|所给材料|附加材料|你提供的|你给出的|Bead|bead|reader|珠子|锚点|Kopp|PTNA|Rink|Samson|乐谱依据|音乐依据|谱面说明|小节划分|小节编号)", line) and len(line) < 400:
            continue
        out.append(line)
    t = "\n".join(out)
    # a section headed by the right-edge boundary 117 is a known P0 artifact: flagged separately, removed for blind reading
    t = re.sub(r"\n#{1,4}[^\n]*第\s*117\s*小节[^\n]*\n.*?(?=\n#{1,4}\s|\n---|\Z)", "\n", t, flags=re.S)
    return re.sub(r"\n{3,}", "\n\n", t).strip()


def flags(t):
    f = {}
    f["seg117"] = bool(re.search(r"第\s*117\s*小节\s*[｜|]|#+[^\n]*第?117(?![—–\-])", t))
    f["chars"] = len(t)
    f["headers"] = len(re.findall(r"^#{2,4}\s", t, re.M))
    f["bold_lessons"] = len(re.findall(r"\*\*[^*\n]{6,}\*\*", t))
    return f


def cmd_pack(a):
    runs = []
    for pat in a.runs.split(","):
        runs += sorted((ROOT / "runs").glob(pat))
    runs = [r for r in runs if (r / "output.txt").exists()]
    rng = random.Random(a.seed)
    items = []
    for r in runs:
        meta = json.loads((r / "run.json").read_text(encoding="utf-8"))
        items.append({"run": r.name, "cond": meta["cond"], "prompt": meta["prompt"],
                      "flags": flags((r / "output.txt").read_text(encoding="utf-8")),
                      "text": clean((r / "output.txt").read_text(encoding="utf-8"))})
    # stratify by (prompt,cond) so each batch is balanced
    groups = {}
    for it in items:
        groups.setdefault((it["prompt"], it["cond"]), []).append(it)
    batches = [[] for _ in range(a.batches)]
    for k in sorted(groups):
        g = groups[k]; rng.shuffle(g)
        for i, it in enumerate(g):
            batches[i % a.batches].append(it)
    out = ROOT / "evaluations" / a.tag
    for bi, b in enumerate(batches, 1):
        if a.anchor:
            b = b + [{"run": "B0", "cond": "B0", "prompt": "B0", "text": clean(B0.read_text(encoding="utf-8"))}]
        rng.shuffle(b)
        d = out / f"batch{bi}"; d.mkdir(parents=True, exist_ok=True)
        key, parts = [], []
        for j, it in enumerate(b):
            lab = f"文章{chr(65 + j)}"
            key.append({"label": lab, "run": it["run"], "cond": it["cond"], "prompt": it["prompt"], "flags": it.get("flags") or flags(it["text"])})
            parts.append(f"\n\n==================== {lab} ====================\n\n{it['text']}\n")
        (d / "articles.md").write_text("".join(parts).strip() + "\n", encoding="utf-8")
        (d / "key.json").write_text(json.dumps(key, ensure_ascii=False, indent=1), encoding="utf-8")
        print(d, len(b), sum(len(p) for p in parts))


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); sp = ap.add_subparsers(dest="c", required=True)
    p = sp.add_parser("pack"); p.add_argument("--runs", required=True); p.add_argument("--tag", required=True)
    p.add_argument("--batches", type=int, default=1); p.add_argument("--anchor"); p.add_argument("--seed", type=int, default=1)
    a = ap.parse_args()
    if a.c == "pack": cmd_pack(a)
