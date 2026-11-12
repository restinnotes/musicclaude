"""10-29 delivery of the v6 repair (PLAN_v6修补_20261029.md): the final line joined with the bead graph, both line graphs,
v6 for comparison, the blind regression check and the gate reviews of the final round, the plan with every round's record.
No model calls. usage: python deliver_v6fix.py <final tag> -> deliver_20261029/ and C:/Users/zuoyi/Downloads/Thread_v6修补_<date>.zip"""
import json, re, shutil, sys, time, zipfile
from pathlib import Path
import evo, v6fix as V

ROOT = evo.ROOT
OUT = ROOT / "deliver_20261029"
ROUNDS = [("w2", "v6 整首一次修补"), ("w3", "按盲评意见整首再修"), ("w4", "再按盲评意见整首再修"),
          ("w5", "只对仍丢内容的 10 段逐段聚焦重修"), ("w6", "按交付前评定意见再逐段聚焦重修 9 段"),
          ("w8", "按 w6 评定意见再逐段聚焦重修 8 段（w7 与 w7x 并行、段落不重叠，合并）"),
          ("w9", "按 w8 盲评和评定列出的全部丢失逐段重修 19 段（覆盖反而下降）"), ("w10", "w8、w9 按段取绝对覆盖高的"),
          ("w13", "w10 + 补 4 处覆盖缺口 + 按 w10 评定意见定向收尾 11 段"), ("w14", "w13 覆盖下降的三段退回 w10"),
          ("w15", "按 w14 评定补 5 段整合性认识"), ("w17", "Op.60 w15 + Op.61 两段三个候选里排序评比第一的"),
          ("w20", "w17 + Op.60 S10 找回 + 7 段两个候选按排序评比挑选"), ("w22", "w20 + Op.61 三段三个候选按排序评比挑选"),
          ("w24", "w20 + Op.61 按 8 份重复盲评里反复被点的丢失逐段找回（各两候选，排序评比挑选）"),
          ("w27", "去翻译：只重写被判复述珠子的条目（覆盖下降）"), ("w30", "先列原因再写（变短但变抽象、覆盖下降）"),
          ("w31", "以 w24 为底按顺序逐段只删重复（覆盖保住，但长句、箭头过多、后段丢内容）"),
          ("w34", "w31 + 找回丢失、复述改原因、守 v6 短条目形式（线自己站得住，覆盖下降）"),
          ("w35", "w34 + 补覆盖与丢失（覆盖回来，但带进了珠子情节）"),
          ("w37", "w35 清理情节与复述、收紧啰嗦段，再点修三处"),
          ("w38", "w37 + 8 份重复盲评里反复被点的丢失和交付前评定点名的几处，逐段找回（每段最多长三成）")]


def blind_rows(T):
    f = V.OUT / f"blind_{T}.json"
    if not f.exists():
        return None
    S = json.loads(f.read_text(encoding="utf-8")); rows = []
    for rid, s in S.items():
        c = s["cnt"]
        rows.append(f"| {T} | {'Op.60' if s['w'] == 'op60' else 'Op.61'} | {'gpt-6' if s['j'] == 'g6' else '5.6'} | {s['better']} | "
                    f"{c['cover']['new']}:{c['cover']['base']} | {c['lean']['new']}:{c['lean']['base']} | {c['plain']['new']}:{c['plain']['base']} | "
                    f"{s['new_regress']} | {len(s['lost_new'])} |")
    return rows


def main(T):
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir()
    md = (V.OUT / f"成品_按段一屏_{T}.md").read_text(encoding="utf-8")       # 10-29 user: "为什么这么多分屏" -> one screen per segment
    md = re.sub(r"^# .*$", f"# 成品：线与珠子关系图结合（按段一屏，在 v6 上修补，{T}）", md, count=1, flags=re.M)
    (OUT / "01_成品_线与珠子关系图_按段一屏_Op60_Op61.md").write_text(md, encoding="utf-8")
    for w, W in (("op60", "Op60"), ("op61", "Op61")):
        g = V.graph_of(w, T)
        (OUT / f"02_新线_{W}_关系图.md").write_text(f"# {W.replace('Op', 'Op.')}｜关系图（在 v6 上修补，最终版 {T}）\n\n" + V.view(g), encoding="utf-8")
        shutil.copy(ROOT / "deliverable" / "thread_v6" / f"{W}_关系图.md", OUT / f"03_v6原版_{W}_关系图.md")
    for src, dst in ((V.OUT / f"checklist_{T}.md", "04a_回退检查_v6好内容固定清单逐条核对.md"),
                     (V.OUT / f"cov_{T}.md", "04b_珠子覆盖_最终版逐颗判定.md"), (V.OUT / "cov_v6.md", "04c_珠子覆盖_v6逐颗判定_对照.md"),
                     (V.OUT / f"blind_{T}.md", "04_回退检查_和v6匿名盲评_最终版.md"),
                     (V.OUT / f"alone_{T}.md", "04d_线单独读_与复述珠子判定_最终版.md"), (V.OUT / "alone_v6.md", "04e_线单独读_v6对照.md"),
                     (ROOT / "reviews" / f"交付前评定_v6修补_{T}.md", "05_交付前评定_gpt3新对话_最终版.md"),
                     (ROOT / "PLAN_v6修补_20261029.md", "06_计划与每轮记录.md")):
        if src.exists():
            shutil.copy(src, OUT / dst)
    table = ["| 轮 | 曲 | 评委 | 整体更好 | 覆盖 新:v6 | 啰嗦更少 新:v6 | 人话 新:v6 | 判退步 | 列出丢失 |", "|---|---|---|---|---|---|---|---|---|"]
    for t, _ in ROUNDS:
        r = blind_rows(t)
        if r:
            table += r
        if t == T:
            break
    stats = []
    for w, W in (("op60", "Op.60"), ("op61", "Op.61")):
        a, b = V.v6(w), V.graph_of(w, T)
        na = sum(len(s["items"]) for s in a["segments"]); nb = sum(len(s["items"]) for s in b["segments"])
        ca = sum(len(it["text"]) for s in a["segments"] for it in s["items"]); cb = sum(len(it["text"]) for s in b["segments"] for it in s["items"])
        stats.append(f"- {W}：条目 {na} → {nb}，字数 {ca} → {cb}")
    covtab = ["评委只看一版线（不知道是哪版）和全部珠子，逐颗判 说清 / 偏弱 / 相反 / 没有。“说清”=线给出了此刻为什么会这样的具体原因。", "",
              "| 版本 | 曲 | 评委 | 说清 | 偏弱 | 相反 | 没有 | 主体验说清 |", "|---|---|---|---|---|---|---|---|"]
    for t in ("v6", T):
        f = V.OUT / f"cov_{t}.json"
        if f.exists():
            for k, v in json.loads(f.read_text(encoding="utf-8")).items():
                tt = v["total"]; mm = v["by_role"].get("主体验", {})
                covtab.append(f"| {t} | {'Op.60' if k.startswith('op60') else 'Op.61'} | {'gpt-6' if k.endswith('g6') else '5.6'} | {tt.get('说清', 0)}/{v['n']} | "
                              f"{tt.get('偏弱', 0)} | {tt.get('相反', 0)} | {tt.get('没有', 0)} | {mm.get('说清', 0)}/{sum(mm.values())} |")
    chktab = ["两位诊断评审列的 v6 实质好内容合并去重成固定清单（Op.60 43 条、Op.61 59 条），每版两位评委逐条判 保留 / 更好地取代 / 丢失。"
              "开放式盲评每次列的“丢失”都不一样、照着修不收敛（w9 修完反而覆盖下降），所以回退以这份固定清单为准。", "",
              "| 曲 | 评委 | 保留 | 更好地取代 | 丢失 |", "|---|---|---|---|---|"]
    f = V.OUT / f"checklist_{T}.json"
    if f.exists():
        for w, r in json.loads(f.read_text(encoding="utf-8")).items():
            for j, c in r["cnt"].items():
                chktab.append(f"| {'Op.60' if w == 'op60' else 'Op.61'} | {'gpt-6' if j == 'g6' else '5.6'} | {c['保留']} | {c['更好地取代']} | {c['丢失']} |")
    alonetab = ["评委只拿到线（没有珠子），判每段“他此刻为什么这样”在线里是否成立；另一次对照珠子逐条判：自己的原因 / 复述珠子 / 两者都有。", "",
                "| 版本 | 曲 | 评委 | 段成立 | 条目 | 箭头 | 纯复述珠子 | 两者都有 | 自己的原因 |", "|---|---|---|---|---|---|---|---|---|"]
    for t in ("v6", "w24", T):
        f = V.OUT / f"alone_{t}.json"
        if f.exists():
            for k, v in json.loads(f.read_text(encoding="utf-8")).items():
                tr = v.get("trans") or {}
                alonetab.append(f"| {t} | {'Op.60' if k.startswith('op60') else 'Op.61'} | {'gpt-6' if k.endswith('g6') else '5.6'} | "
                                f"{(v.get('self') or {}).get('成立', 0)}/{sum((v.get('self') or {}).values())} | {v.get('items')} | {v.get('arrows')} | "
                                f"{tr.get('复述珠子', 0)} | {tr.get('两者都有', 0)} | {tr.get('自己的原因', 0)} |")
    gate = (ROOT / "reviews" / f"交付前评定_v6修补_{T}.md")
    verdict = []
    if gate.exists():
        g = gate.read_text(encoding="utf-8")
        for name in ("gpt-6", "gpt-5.6"):
            part = g.split(f"## {name}", 1)[1] if f"## {name}" in g else ""
            m = re.search(r"结论：\s*\**\s*(大致可用|不可用)", part)
            verdict.append(f"{name}：{m.group(1) if m else '（没找到结论行）'}")
    readme = [f"# 先读我：在 v6 上修三个问题，并让线自己站得住（最终版 {T}，{time.strftime('%Y-%m-%d %H:%M')}）", "",
              "三个问题：P1 覆盖不足、P2 啰嗦废话、P3 不说人话。底稿是 v6，形式不变（Center 不改；每段标他和 Center 的关系；→ 段内由上一条引出；← 指回前面某段；⟲ 前面仍在起作用），只去掉了 ✦ 标签。", "",
              "## 文件", "",
              "- `01_成品_线与珠子关系图_按段一屏_Op60_Op61.md`：新线和珠子关系图结合，每段一屏：上面是这段的线，下面是这段的珠子（逐字原文），每颗珠子标出由线的哪几条说明。",
              "- `02_新线_*_关系图.md`：两首的新线；`03_v6原版_*`：v6 原样，方便对照。",
              "- `04_回退检查_*`：最终版和 v6 的匿名盲评原文（gpt-6、5.6，随机顺序）；`04a` 固定清单核对；`04b/04c` 珠子覆盖；`04d/04e` 线单独读与复述珠子。",
              "- `05_交付前评定_*`：最终版交给 gpt3 新对话（附 10-29 ChatGPT 对话记录、v6、新线、珠子图、结合成品、盲评）的评定原文。",
              "- `06_计划与每轮记录.md`：做法、每轮结果、每次改提示词的原因。", "",
              "## 篇幅", "", *stats, "",
              "## 珠子覆盖（绝对数，逐颗判定）", "", *covtab, "",
              "## 线自己站得住吗、是不是在翻译珠子", "", *alonetab, "",
              "## 回退检查：v6 好内容固定清单逐条核对", "", *chktab, "",
              "## 每轮和 v6 的匿名盲评（逐段计数，新:v6）", "", *table, "",
              "盲评的“判退步”问的是：用新版整个替换 v6，会不会丢掉 v6 已经说清的东西。每轮都有评委列出丢失，修补就是按这些清单逐条找回；",
              "同一位评委对只差几段的两版，逐段计数会差很多（例如 Op.61 覆盖 8:5 和 2:11），所以看的是多轮趋势和丢失清单本身。",
              "w5 Op.60 gpt-6 的“啰嗦”“人话”两栏，评委没写 X/Y 标签、只写了理由，表里计成 0:0；按理由逐条读，啰嗦是新版 12 段、v6 2 段（S05、S06）。", "",
              "## 交付前评定结论", "", *(f"- {v}" for v in verdict), ""]
    todo = ROOT / "deliver_todo.md"
    if todo.exists():
        readme += [todo.read_text(encoding="utf-8"), ""]
    (OUT / "00_先读我.md").write_text("\n".join(readme), encoding="utf-8")
    zp = Path("C:/Users/zuoyi/Downloads") / f"Thread_v6修补_{time.strftime('%Y%m%d')}.zip"
    with zipfile.ZipFile(zp, "w", zipfile.ZIP_DEFLATED) as z:
        for f in sorted(OUT.iterdir()):
            z.write(f, f"Thread_v6修补/{f.name}")
    print(OUT, zp, flush=True)


if __name__ == "__main__":
    main(sys.argv[1])
