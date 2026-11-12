"""11-02 (迭代准则 §六, user: "需要一些评分和简短例子能更直观的看出我们真的好了多少"): human-facing progress table.
Not used for decisions. Reads the JV=2 measurements (cov2_ / alone2_ / eo2_ / blind2_) of each version and writes 进度表.md:
one row per version + side-by-side examples of the segments where the blind judges agreed most.
usage: python scoreboard.py <base> <tag> [<tag> ...]     e.g. python scoreboard.py m6w pa qa"""
import json, os, re, sys
from collections import Counter
from pathlib import Path
import v6fix as V

D = V.OUT; HERE = Path(__file__).parent
NAME = {"op60": "Op.60", "op61": "Op.61"}
GOAL = {"1": "单独成立", "2": "不啰嗦", "3": "人话", "4": "接得上珠子"}


def load(p):
    try:
        return json.loads(Path(p).read_text(encoding="utf-8"))
    except Exception:
        return None


def chars(w, t):
    try:
        g = V.graph_of(w, t)
    except Exception:
        return "?"
    return sum(len(i["text"]) for s in g["segments"] for i in s["items"])


def cov(w, t):
    c = load(D / f"cov2_{t}.json") or {}
    v = [str((c.get(f"{w}_{j}") or {}).get("total", {}).get("说清", "?")) for j in ("g6", "g56")]
    n = {"op60": 50, "op61": 53}[w]
    return f"{'/'.join(v)}（共{n}）"


def alone(w, t):
    a = load(D / f"alone2_{t}.json") or {}
    out = []
    for j in ("g6", "g56"):
        x = a.get(f"{w}_{j}") or {}
        s = x.get("self") or {}
        if s:
            out.append(f"{s.get('成立', 0)}/{sum(s.values())}")
    rep = [str((a.get(f"{w}_{j}") or {}).get("repeat", "?")) for j in ("g6", "g56")]
    tr = [str(((a.get(f"{w}_{j}") or {}).get("trans") or {}).get("复述珠子", "?")) for j in ("g6", "g56")]
    return " ".join(out) or "?", "/".join(rep), "/".join(tr)


def e2e(w, t):
    import e2e_open as E
    cnt = Counter()
    expected = completed = 0
    # The held-out Gemini review must not become a required repair reader.
    # A bound continuation records the deliberately GPT-only review scope.
    binding = load(HERE / 'runs/_batches/continue_r80' / f'{t}_open_binding.json')
    bound_ids = {r['rid'] for r in binding.get('reviews', [])} if binding else None
    for ww, j, k in E.runs():
        if ww != w:
            continue
        if bound_ids is not None and f'eo2_{w}_{t}_{j}_r{k}' not in bound_ids:
            continue
        expected += 1
        e = V.parse(f"eo2_{w}_{t}_{j}_r{k}") or {}
        if not isinstance(e.get("problems"), list):
            continue
        completed += 1
        for p in e.get("problems") or []:
            if p.get("severity") in ("严重", "中等"):
                cnt[str(p.get("goal", "")).strip()[:1]] += 1
    if not completed:
        return "未测"
    counts = " ".join(f"{GOAL[g][:2]}{cnt.get(g, 0)}" for g in "1234")
    return counts if completed == expected else f"不完整（{completed}/{expected}）；已收取：{counts}"


def blind_all(t, base):
    b = dict(load(D / f"blind2_{t}_vs{base}.json") or {})
    b.update(load(D / f"blind2_{t}_vs{base}_r2.json") or {})
    return b


def blind(t, base):
    b = blind_all(t, base)
    if b:
        pick = sum(s["better"] in ("新版", t) for s in b.values()); n = len(b)
        net = {k: sum(s["cnt"][k]["new"] - s["cnt"][k]["base"] for s in b.values()) / n for k in ("alone", "lean", "plain", "cover")}
        return f"{pick}/{n} 选新版；净胜 单独{net['alone']:+.1f} 啰嗦{net['lean']:+.1f} 人话{net['plain']:+.1f} 覆盖{net['cover']:+.1f}", b
    f = load(D / f"fair_{t}_vs{base}.json") or {}   # R37 正反 8 票（新版排前/排后各一次）
    if f.get("complete"):
        n, pick = f["complete"], f.get("wins", 0)
        net = f.get("net_sums") or {}
        phase = '正反8票' if n == 8 else '4票快筛' if n == 4 else '部分已收取'
        return (f"{pick}/{n} 选新版（{phase}），{f.get('no_regress', 0)}/{n} 不退步；"
                f"净胜 单独{net.get('alone', 0):+d} 啰嗦{net.get('lean', 0):+d} "
                f"人话{net.get('plain', 0):+d} 覆盖{net.get('cover', 0):+d}"), {}
    return "", {}


def blind_work(t, base, work):
    """Show each work explicitly; a strong work must not hide its partner."""
    f = load(D / f"fair_{t}_vs{base}.json") or {}
    rows = [r for r in f.get('rows', []) if r.get('w') == work]
    if not rows:
        return None
    n = len(rows)
    net = {k: sum(r['net'][k] for r in rows) for k in ('alone','lean','plain','cover')}
    return (f"{sum(r['new_win'] for r in rows)}/{n} 选新，"
            f"{sum(r['no_regress'] for r in rows)}/{n} 不退步；"
            f"净胜 单独{net['alone']:+d} 啰嗦{net['lean']:+d} "
            f"人话{net['plain']:+d} 覆盖{net['cover']:+d}")


def seg_votes(t, base, w):
    """per segment: how many judge-dimension votes went to the new version minus the base"""
    b = blind_all(t, base)
    rid_map = {}
    for rid in b:
        if b[rid]["w"] == w:
            rid_map[rid] = b[rid]
    votes = Counter()
    for rid in rid_map:
        d = V.parse(rid) or {}
        mp_new_is_X = None
        # recover which side was new from the stored summary counts is not possible per segment; re-derive from v6fix's rule
        import random
        flip = random.Random(rid).random() < 0.5
        newlab = "X" if flip else "Y"
        for s in d.get("sections") or []:
            for k in ("alone", "lean", "plain", "cover"):
                v = s.get(k)
                if v in ("X", "Y"):
                    votes[s.get("sec")] += 1 if v == newlab else -1
    return votes


def seg_text(w, t, sec):
    g = V.graph_of(w, t)
    s = next(x for x in g["segments"] if x["sec"] == sec)
    lines = []
    for i in s["items"]:
        cs = i.get("cite") or []
        lines.append(f"- {i['text']}" + (f"（cite: {', '.join(cs)}）" if cs else ""))
    return f"（{s.get('relation')}）\n" + "\n".join(lines)


LINK_RE = re.compile(r"(?<!\[)(?<!\]\()`?((?:evaluations|schemes)/[A-Za-z0-9_./-]+\.(?:md|txt|json))`?")
EVAL_SHORT_RE = re.compile(r"(?<![/\[])(?<!\]\()`?(op6[01]_[A-Za-z0-9_]+\.md)`?")
ROOT_DOCS = ("DAG.md", "试验记录.md", "标准.md", "迭代准则.md", "STATUS.md", "VERSIONS.md")
ROOT_PY_RE = re.compile(r"(?<![/\[A-Za-z0-9_])(?<!\]\()`?([A-Za-z][A-Za-z0-9_]*\.py)`?")


def linkify(line):
    """把版本说明里的文件路径变成链接；已经写成链接的保持不动。"""
    line = LINK_RE.sub(lambda m: f"[{m.group(1)}]({m.group(1)})", line)
    line = EVAL_SHORT_RE.sub(lambda m: f"[{m.group(1)}](evaluations/v6fix/{m.group(1)})", line)
    line = ROOT_PY_RE.sub(lambda m: f"[{m.group(1)}]({m.group(1)})" if (HERE / m.group(1)).exists() else m.group(0), line)
    for name in ROOT_DOCS:
        line = line.replace(f"`{name}`", f"[{name}]({name})")
    return line


def src_link(w, t):
    p = f"evaluations/v6fix/{w}_{t}.md"
    return f"[{p}]({p})"


def main(base, tags):
    base_label = {"qurefs": "qu（qurefs）"}.get(base, base)
    current = re.search(r'当前正文主线：`([^`]+)`', (HERE / 'DAG.md').read_text(encoding='utf-8'))
    current_label = f"当前已验收主线：`{current.group(1)}`；" if current else ''
    md = ["# 进度表（只给人看，不作判定）", "", f"{current_label}本表测量基准：`{base_label}`。评委为 11-02 对齐新标准后的版本（JV=2）。", "",
          "| 版本 | 作品 | 字数 | 覆盖（两位评委说清数） | 单独读成立段数 | 重说段数 | 复述珠子条数 | 开放评审中等以上问题 | 与测量基准盲比（按作品） |",
          "|---|---|---|---|---|---|---|---|---|"]
    for t in [base] + tags:
        bl, _ = blind(t, base) if t != base else ("—", {})
        for w in ("op60", "op61"):
            a, rep, tr = alone(w, t)
            wb = blind_work(t, base, w) if t != base else '—'
            if wb is None:
                wb = f'双曲合计：{bl}' if w == 'op60' and bl else ''
            md.append(f"| {t} | {NAME[w]} | {chars(w, t)} | {cov(w, t)} | {a} | {rep} | {tr} | {e2e(w, t)} | {wb} |")
    md += ["", "开放评审一栏：单独成立 / 不啰嗦 / 人话 / 接得上珠子各维度被挑出的中等以上问题数；未测或不完整明确标注，不以0代替缺测。盲比只列实际收取份数，完整性与通过仍由verdict检查。", ""]
    hs = os.environ.get("HS_FILE")     # blind 1-10 scores from human_score.py, shown above the examples
    if hs and (D / hs).exists():
        md += (D / hs).read_text(encoding="utf-8").replace("# 给人看的评分（不作判定）", "## 给人看的评分（不作判定）").replace("\n## Op", "\n### Op").split("\n") + [""]
    for t in (os.environ.get("EX_TAGS", "").split(",") if os.environ.get("EX_TAGS") else tags):
        note = HERE / "版本说明" / f"{t}_vs_{base}.md"
        if note.exists():
            md += [linkify(x) for x in note.read_text(encoding="utf-8").strip().split("\n")] + [""]
            continue
        for w in ("op60", "op61"):
            v = seg_votes(t, base, w)
            if not v:
                continue
            best = max(v, key=v.get); worst = min(v, key=v.get)
            md += [f"## 例子：{t} 对 {base}，{NAME[w]}", ""]
            for sec, why in ((best, "评委最一致认为新版更好的一段"), (worst, "评委最一致认为主线更好的一段")):
                if why.endswith("更好的一段") and sec == worst and v[sec] >= 0:
                    continue
                md += [f"**{sec}（{why}，票差 {v[sec]:+d}）**", "", f"主线 {base}（{src_link(w, base)}）：", seg_text(w, base, sec), "", f"新版 {t}（{src_link(w, t)}）：", seg_text(w, t, sec), ""]
    (HERE / "进度表.md").write_text("\n".join(md), encoding="utf-8")
    print("\n".join(md[:8 + 2 * (1 + len(tags))]))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2:])
