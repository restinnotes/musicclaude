# 版本登记表：扫描 evaluations/v6fix 下的每个线版本，列出来历和已有测量，写到 VERSIONS.md
# 用法：python versions.py
import glob, json, os, re
from datetime import datetime
from zoneinfo import ZoneInfo

D = "evaluations/v6fix"


def load(p):
    try:
        return json.load(open(p, encoding="utf-8"))
    except Exception:
        return None


def chars(g):
    n = 0
    for s in (g or {}).get("segments", []):
        for it in s.get("items", []):
            n += len(it.get("text", "") if isinstance(it, dict) else str(it))
    return n


def cov(tag):
    c = load(f"{D}/cov2_{tag}.json")
    if not c:
        return "未测", "未测"
    out = []
    for w, n in (("op60", 50), ("op61", 53)):
        v = [str(c.get(f"{w}_{j}", {}).get("total", {}).get("说清", "?")) for j in ("g6", "g56")]
        out.append(f"{'/'.join(v)}（共{n}）")
    return out[0], out[1]


def alone(tag):
    a = load(f"{D}/alone2_{tag}.json")
    if not a:
        return "未测"
    out = []
    for w in ("op60", "op61"):
        v = []
        for j in ("g6", "g56"):
            s = a.get(f"{w}_{j}", {}).get("self", {})
            v.append(f"{s.get('成立', 0)}/{sum(s.values())}" if s else "未测")
        out.append(" ".join(v) or "?")
    return "；".join(out)


rows = []
for p in glob.glob(f"{D}/op60_*.json"):
    tag = os.path.basename(p)[5:-5]
    d = load(p)
    if not isinstance(d, dict) or "graph" not in d:
        continue
    d61 = load(f"{D}/op61_{tag}.json") or {}
    c60, c61 = cov(tag)
    import scoreboard
    extra = "；".join(f"{w} {scoreboard.e2e(w, tag)}" for w in ("op60", "op61"))
    blinds = sorted(os.path.basename(b) for b in glob.glob(f"{D}/blind2_{tag}_vs*.json"))
    blinds += sorted(os.path.basename(b) for b in glob.glob(f"{D}/fair_{tag}_vs*.json"))
    rows.append((os.path.getmtime(p), tag, str(d.get("base", "")).replace("|", "/")[:90],
                 chars(d.get("graph")), chars(d61.get("graph")) if d61.get("graph") else "未生成", c60, c61, alone(tag),
                 extra, " ".join(blinds) or "未测"))

rows.sort()
L = ["# 线版本登记表（脚本生成，勿手改；`python versions.py` 重建）", "",
     "仅列JV=2测量；历史旧评审不混算。覆盖 = GPT-6/GPT-5.6 判“说清”的颗数；单独读 = 每首 GPT-6、GPT-5.6 判“成立”的段数；开放评审只用来找问题，不作验收。时间为America/New_York；缺测不记0。", "",
     "| 时间 | 版本 | 来历（base 字段） | 字数 60/61 | 覆盖 Op.60 | 覆盖 Op.61 | 单独读 | 开放评审 | 盲评文件 |",
     "|---|---|---|---|---|---|---|---|---|"]
for t, tag, base, n60, n61, c60, c61, al, lo, bl in rows:
    stamp = datetime.fromtimestamp(t, ZoneInfo('America/New_York')).strftime('%m-%d %H:%M')
    L.append(f"| {stamp} | {tag} | {base} | {n60}/{n61} | {c60} | {c61} | {al} | {lo} | {bl} |")
open("VERSIONS.md", "w", encoding="utf-8").write("\n".join(L) + "\n")
print(len(rows), "versions")
