"""Assemble deliverables from model outputs (no model calls; texts are copied verbatim, never rewritten).

deliverable/
  C_最终Bead阅读稿.md        14 段最终 Bead / STRUCT 全文（按音乐顺序）
  struct/Sxx.json            最终 STRUCT（final2 若存在则用 final2，否则 final）
  A_实验数据/curves.json      每段侧面阶梯 + 逐 k 审稿 + 累计涵盖
  A_实验数据/阶梯全文.md       每段全部候选文字、来源、生成者与审稿者的判断
  A_实验数据/cmp.json         盲评结果（解码后的版本映射）
  A_实验数据/calls.json       全部 GPT Web 调用记录
"""
import json, shutil, statistics
from pathlib import Path
import sat

D = sat.ROOT / "deliverable"; AD = D / "A_实验数据"
for p in (D / "struct", AD):
    p.mkdir(parents=True, exist_ok=True)


def final_of(seg):
    if sat.load("final2_c", seg):
        return f"{sat.CHOSEN[seg]}→整曲修订(final2_c)", sat.load("final2_c", seg)
    return sat.CHOSEN[seg], sat.load(sat.CHOSEN[seg], seg)


def q(xs):
    return "；".join(f"{s.get('src', '').replace('SRC-', '')}「{s.get('quote')}」" + ("" if s.get("quote_verified") else "（未逐字命中）")
                    for s in xs or [])


ROLE_ORDER = ["主体验", "段内变化", "另一侧面", "另一种理解", "演奏条件"]


def reader_md():
    out = ["# 肖邦《船歌》Op.60 · 十四段最终 Bead / STRUCT\n",
           "按 PTNA／朝山冻结十四段的音乐顺序排列。每段先是给听者的连续正文（「读者正文」），然后是本段 STRUCT 中经过精选的全部体验条目、它们之间的关系与段内变化。",
           "每段取最后一轮三方盲评的胜者（生产链路 final_b 9 段；第一次实验采样 final 4 段；S08 取经整曲修订与精简后的 final3），再对这一整套做整曲检查，被点名的 4 段回原会话修订。版本来源标在每段末尾。所有文字为本地 gpt3（GPT Web，GPT-6 Thinking / max，Temporary + Unpersonalized）的原样输出，脚本只做拼接与逐字引文核验，没有人工改写。素材只用 24 份无 Muse 原稿；未输入旧短稿或旧 STRUCT。",
           "情景与人物动作是聆听比喻，不是作曲家生平或唯一演奏解释。「另一种理解」表示不同的听法，不是同一个人的连续经历。\n"]
    for s in sat.SEGS:
        st, d = final_of(s)
        secs = round(sat.nmeas(s) * sat.SEC_PER_MEASURE)
        out.append(f"\n---\n\n## {s} · 第 {sat.mm(s)} 小节（{sat.SEGS[s][1]}，约 {secs} 秒）｜{d.get('title')}\n")
        out.append("### 读者正文\n")
        out.append(d.get("reader", "").strip() + "\n")
        uses = set(d.get("reader_uses") or [])
        out.append(f"### 本段体验条目（{len(d['beads'])} 条）\n")
        for b in d["beads"]:
            tag = "" if b["id"] in uses else "（正文未用，备选）"
            out.append(f"**{b['id']}｜{b.get('role')}｜第 {b.get('measures')} 小节**{tag}\n")
            out.append(b.get("text", "").strip() + "\n")
            if b.get("performance_condition"):
                out.append(f"> 演奏条件：{b['performance_condition']}\n")
            if b.get("vivid_lines"):
                out.append(f"> 可直接上屏的原句：{q(b['vivid_lines'])}\n")
            vl = {(x.get("src"), x.get("quote")) for x in b.get("vivid_lines") or []}
            rest = [x for x in b.get("sources") or [] if (x.get("src"), x.get("quote")) not in vl]
            if rest:
                out.append(f"> 其他依据：{q(rest)}\n")
            if b.get("also_expressed_by"):
                out.append(f"> 并入的其他说法：{q(b['also_expressed_by'])}\n")
        if d.get("relations"):
            out.append("### 关系\n")
            for r in d["relations"]:
                out.append(f"- {r.get('a')} ↔ {r.get('b')}：**{r.get('type')}**。{r.get('note', '')}")
            out.append("")
        if d.get("timeline"):
            out.append("### 段内先后\n")
            for t in d["timeline"]:
                ev = t.get("music_event") or t.get("event") or t.get("music") or t.get("description") or ""
                out.append(f"- 第 {t.get('measures')} 小节：{ev}（{', '.join(t.get('beads') or t.get('bead_ids') or [])}）")
            out.append("")
        out.append(f"### 为什么停在这里\n\n{d.get('stop_reason', '')}\n")
        if d.get("not_kept"):
            out.append("### 未保留的重要候选\n")
            for n in d["not_kept"]:
                out.append(f"- {n.get('what')} —— {n.get('why')}")
            out.append("")
        out.append(f"<sub>版本：{st}；引文 {d['_quotes']['n']} 条，未逐字命中 {d['_quotes']['unverified']} 条。</sub>\n")
    return "\n".join(out)


def ladder_md(curves):
    out = ["# 实验数据：十四段侧面阶梯全文\n",
           "每段：生成者（gen）按边际价值排出的全部候选（含停止点之后的尾部候选），以及独立 clean 审稿（rev1 先盲列体验清单，rev2 再逐 k 评审）的判断。累计涵盖＝审稿者自己清单中本段体验的加权涵盖（核心 3／有价值 2／次要 1；部分传达计一半），只作相对参考。\n"]
    for c in curves:
        out.append(f"\n---\n\n## {c['seg']} · 第 {c['measures']} 小节（{c['label']}，约 {c['seconds']} 秒）\n")
        out.append(f"审稿清单：本段体验 {c['n_rev_experiences']} 条（核心 {c['n_core']}），另标出属于邻段或定位可疑 {c['n_offsite_flagged']} 条。")
        out.append(f"生成者建议停止：k={c['gen_stop']}；审稿建议保留：{c['rev_keep']}；最终 STRUCT：{c['final_beads']} 条。\n")
        out.append("| k | 生成者增益 | 审稿判定 | 值得注意力 | 鲜活 | 抽象 | 拼接 | 位置 | 累计涵盖 | 核心涵盖 | 累计字数 |")
        out.append("|---|---|---|---|---|---|---|---|---|---|---|")
        for r in c["rows"]:
            out.append(f"| {r['k']} | {r['gen_gain']} | {r['rev_case']} | {r['worth']} | {r['vivid']} | {r['abstract']} | {r['conjuncture']} | {r['location_ok']} | {r['cum_cov']:.2f} | {r['cum_core']:.2f} | {r['cum_chars']} |")
        out.append("")
        for r in c["rows"]:
            out.append(f"**k={r['k']}（{r['id']}，第 {r['measures']} 小节；生成者标注：{'、'.join(r['gen_relation'])}）**\n")
            out.append(r["text"] + "\n")
            out.append(f"- 来源：{', '.join(x.replace('SRC-', '') for x in r['sources'])}")
            out.append(f"- 生成者说新增：{r['gen_adds']}")
            out.append(f"- 审稿者说新增：{r['rev_new']}")
            if r["newly_covered"]:
                out.append("- 新涵盖的审稿清单体验：" + "；".join(f"[{n['importance']}] {n['what']}" for n in r["newly_covered"]))
            if r["relation_check"]:
                out.append(f"- 关系核对：{r['relation_check']}")
            for p in r["problems"]:
                out.append(f"- 问题：{p if isinstance(p, str) else json.dumps(p, ensure_ascii=False)}")
            out.append("")
        out.append(f"**生成者停止理由**：{c['gen_stop_reason']}\n")
        out.append(f"**审稿停止建议**：{c['rev_stop_reason']}\n")
        if c["missing"]:
            out.append("**审稿认为阶梯遗漏、值得补入**：\n")
            for m in c["missing"]:
                out.append(f"- {m.get('id')}：{m.get('what')} —— {m.get('why')}")
            out.append("")
        if c["template_check"]:
            out.append(f"**模板检查**：{c['template_check']}\n")
    return "\n".join(out)


def cmp_data():
    rows = []
    for st in ("cmp", "cmp2", "cmp3", "cmpb"):
        for s in sat.SEGS:
            d = sat.load(st, s)
            if not d:
                continue
            m = d["_mapping"]
            w = d.get("why", "")
            for k, v in m.items():
                w = w.replace(k, v)
            rows.append({"round": st, "seg": s, "ranking": [m[x] for x in d["ranking"]], "why_decoded": w,
                         "versions": {m[k]: v for k, v in d["versions"].items()}})
    return rows


def calls():
    recs = [json.loads(l) for l in (sat.RUNS / "calls.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]
    return recs


if __name__ == "__main__":
    import analyze
    cv = [c for c in (analyze.curve(s) for s in sat.SEGS) if c]
    cv2 = [c for c in (analyze.curve(s, "gen_b", "rev1_b", "rev2_b", "final_b") for s in sat.SEGS) if c]
    (AD / "curves.json").write_text(json.dumps(cv, ensure_ascii=False, indent=1), encoding="utf-8")
    (AD / "curves_run2.json").write_text(json.dumps(cv2, ensure_ascii=False, indent=1), encoding="utf-8")
    (AD / "阶梯全文.md").write_text(ladder_md(cv), encoding="utf-8")
    (AD / "阶梯全文_第二次采样.md").write_text(ladder_md(cv2).replace("# 实验数据：十四段侧面阶梯全文", "# 实验数据：十四段侧面阶梯全文（第二次独立采样，生产链路 gen_b / rev_b）", 1), encoding="utf-8")
    (AD / "cmp.json").write_text(json.dumps(cmp_data(), ensure_ascii=False, indent=1), encoding="utf-8")
    cr = calls()
    (AD / "calls.json").write_text(json.dumps(cr, ensure_ascii=False, indent=1), encoding="utf-8")
    for st, name in (("piece", "整曲模板检查_第一轮.json"), ("piece_c", "整曲模板检查_最终选定稿.json")):
        piece = sat.load(st, "ALL")
        if piece:
            (AD / name).write_text(json.dumps(piece, ensure_ascii=False, indent=1), encoding="utf-8")
    for s in sat.SEGS:
        st, d = final_of(s)
        (D / "struct" / f"{s}.json").write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")
    (D / "C_最终Bead阅读稿.md").write_text(reader_md(), encoding="utf-8")
    ok = [r for r in cr if r["completed"]]
    print("calls", len(cr), "ok", len(ok), "fail", len(cr) - len(ok))
    by = {}
    for r in ok:
        by.setdefault(r["stage"], []).append(r["seconds"])
    for k, v in by.items():
        print(k, len(v), "median", statistics.median(v), "max", max(v))
