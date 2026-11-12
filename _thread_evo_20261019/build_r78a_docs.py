"""Generate the r78a vs r49b chain note and the complete final comparison.

Reads products, raw model returns, frozen review results and acceptance records.
No model calls; no hand-copied numbers, links or body text.
"""
from __future__ import annotations

import difflib
import hashlib
import json
import os
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent
os.environ.setdefault("JV", "2")
sys.path.insert(0, str(ROOT))

import v6fix as V
import round34_restore as R
import verdict as VERDICT

TAG = "r78a"
BASE = "r49b"
WORKS = ("op60", "op61")
NAMES = {"op60": "《船歌》Op.60", "op61": "《幻想波兰舞曲》Op.61"}
OUT = ROOT / "evaluations" / "v6fix"
RUNS = ROOT / "runs"
NOTES = ROOT / "版本说明"
DELIVER = ROOT / "deliver_20261104_r78a"
BATCH = RUNS / "_batches" / "r78a_restore"

DIM_ORDER = ("alone", "lean", "plain", "cover")
DIM_NAMES = {"alone": "单独成立", "lean": "不啰嗦", "plain": "人话", "cover": "接得上珠子"}
SEVERITY_ORDER = {"严重": 0, "中等": 1, "轻微": 2}

STEPS = [
    {"tag": "r50progress1", "base": "r49b", "suffix": "A5", "mode": "写后局部修订",
     "receipt": ROOT / "runs/_batches/round50_from_r49b/r50progress1_applied.json"},
    {"tag": "r50progress1r", "base": "r50progress1", "suffix": "A5", "mode": "回补",
     "receipt": ROOT / "runs/_batches/round50_from_r49b/r50progress1r_applied.json"},
    {"tag": "r50progress1rr", "base": "r50progress1r", "suffix": "A5", "mode": "回补",
     "receipt": ROOT / "runs/_batches/round50_from_r49b/r50progress1rr_applied.json"},
    {"tag": "r54weave", "base": "r50progress1rr", "suffix": "P1", "mode": "整篇重组（GlobalReweave）",
     "receipt": ROOT / "runs/_batches/round54_broader/r54weave_applied.json"},
    {"tag": "r55repair", "base": "r54weave", "suffix": "P1", "mode": "写后修订（RepairRestore）",
     "receipt": ROOT / "runs/_batches/round55_current/r55repair_applied.json"},
    {"tag": "r55restored", "base": "r55repair", "suffix": "A5", "mode": "反馈回补",
     "receipt": ROOT / "runs/_batches/round50_from_r49b/r55restored_applied.json"},
    {"tag": "r65a", "base": "r55restored", "suffix": "F1", "mode": "回补（F1，最多改 8 条）"},
    {"tag": "r66a", "base": "r65a", "suffix": "F2", "mode": "局部修订（F2，最多改 8 条）"},
    {"tag": "r67a", "base": "r66a", "suffix": "F1", "mode": "回补（F1，最多改 6 条）"},
    {"tag": "r68a", "base": "r67a", "suffix": "F2", "mode": "局部修订（F2，最多改 8 条）"},
    {"tag": "r78a", "base": "r68a", "suffix": "F1",
     "mode": "回补（F1，最多改 6 条；评委意见只来自 `r67a` 的正反比较）",
     "receipt": BATCH / "r78a_applied.json"},
]


def read(path: Path) -> str:
    return Path(path).read_text(encoding="utf-8")


def load(path: Path):
    return json.loads(read(path))


def digest(path: Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def link(path: Path, label: str | None = None) -> str:
    path = Path(path).resolve()
    assert path.exists(), path
    return f"[{label or path.name}](<{path.as_posix()}>)"


def g(tag: str, w: str):
    return V.graph_of(w, tag)


def chars(graph) -> int:
    return sum(len(item["text"]) for section in graph["segments"] for item in section["items"])


def item_count(graph) -> int:
    return sum(len(section["items"]) for section in graph["segments"])


def step_dir(step, w: str) -> Path:
    return RUNS / f"scr{step['tag'][1:]}_{w}_{step['suffix']}"


def check_step(step, w: str) -> dict:
    folder = step_dir(step, w)
    prompt, output = folder / "prompt.txt", folder / "output.txt"
    assert prompt.exists(), prompt
    assert output.exists(), output
    return {
        "folder": folder,
        "prompt": prompt,
        "output": output,
        "prompt_sha": digest(prompt),
        "output_sha": digest(output),
    }


def verify_apply(step, w: str) -> bool:
    """Re-parse the raw answer and check it explains the target graph exactly."""
    parsed = V.parse(step_dir(step, w).name)
    assert parsed and isinstance(parsed.get("edits"), list), step_dir(step, w)
    source, target = g(step["base"], w), g(step["tag"], w)
    src = {item["id"]: item["text"] for section in source["segments"] for item in section["items"]}
    tgt = {item["id"]: item["text"] for section in target["segments"] for item in section["items"]}
    touched = set()
    for edit in parsed["edits"]:
        eid = edit["id"].replace("＋", "+").split("+")[0]
        touched.add(eid)
        text = R.clean(edit.get("text", ""))
        if edit["op"] == "replace":
            assert tgt.get(eid) == text, (step["tag"], w, eid, tgt.get(eid), text)
        elif edit["op"] == "delete":
            assert eid not in tgt, (step["tag"], w, eid)
        else:
            raise AssertionError((step["tag"], w, edit["op"]))
    for iid, text in src.items():
        if iid not in touched:
            assert tgt.get(iid) == text, (step["tag"], w, iid, tgt.get(iid), text)
    return True


def write_receipt() -> Path:
    BATCH.mkdir(parents=True, exist_ok=True)
    source_rids, prompt_hashes, output_hashes, graph_hashes = {}, {}, {}, {}
    for w in WORKS:
        folder = RUNS / f"scr{TAG[1:]}_{w}_F1"
        source_rids[w] = folder.name
        prompt_hashes[w] = digest(folder / "prompt.txt")
        output_hashes[w] = digest(folder / "output.txt")
        graph_hashes[w] = digest(OUT / f"{w}_{TAG}.json")
        step = next(x for x in STEPS if x["tag"] == TAG)
        assert verify_apply(step, w)
    data = {
        "tag": TAG,
        "base": "r68a",
        "comparison_baseline": "r67a",
        "prompt_source": "round65_fix.py RESTORE (F1)",
        "max_edits": 6,
        "successful_model_calls": len(WORKS),
        "body_source": "model edits only, mechanically applied to the r68a graph",
        "source_rids": source_rids,
        "source_prompt_hashes": prompt_hashes,
        "source_output_hashes": output_hashes,
        "graph_hashes": graph_hashes,
        "verification": "re-parsed edits; replace targets and untouched item texts match r78a exactly",
    }
    path = BATCH / "r78a_applied.json"
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def fair_rows() -> dict:
    data = load(OUT / f"fair_{TAG}_vs{BASE}.json")
    assert data["complete"] == 8 and len(data["rows"]) == 8, data
    assert data["wins"] == 8 and data["no_regress"] == 8, data
    return data


def cov_count(w: str, judge: str, tag: str) -> int:
    return load(OUT / f"cov2_{tag}.json")[f"{w}_{judge}"]["total"]["说清"]


def alone_count(w: str, judge: str, tag: str) -> int:
    return load(OUT / f"alone2_{tag}.json")[f"{w}_{judge}"]["self"]["成立"]


def cov_transition(w: str) -> str:
    start = "/".join(str(cov_count(w, j, BASE)) for j in ("g6", "g56"))
    now = "/".join(str(cov_count(w, j, TAG)) for j in ("g6", "g56"))
    return f"{start} → {now}"


def work_net(fair: dict, w: str, dim: str) -> int:
    return sum(row["net"][dim] for row in fair["rows"] if row["w"] == w)


def biggest_cov_drop(w: str):
    before = {j: VERDICT.cov_secs(w, j, BASE) for j in ("g6", "g56")}
    after = {j: VERDICT.cov_secs(w, j, TAG) for j in ("g6", "g56")}
    assert before["g6"] and before["g56"], w
    best = None
    for sec in before["g6"]:
        d = (before["g6"].get(sec, 0) - after["g6"].get(sec, 0),
             before["g56"].get(sec, 0) - after["g56"].get(sec, 0))
        key = max(d)
        if best is None or key > best[0]:
            best = (key, sec, d)
    return best[1], best[2]



def open_rows() -> list[dict]:
    rows = []
    for w in WORKS:
        for judge, seats in (("g6", (1, 2)), ("g56", (1, 2)), ("gem", (1,))):
            for k in seats:
                rid = f"eo2_{w}_{TAG}_{judge}_r{k}"
                data = V.parse(rid)
                assert data and isinstance(data.get("problems"), list), rid
                for problem in data["problems"]:
                    rows.append({"w": w, "rid": rid, "severity": problem.get("severity", ""),
                                 "goal": str(problem.get("goal", "")).strip()[:1],
                                 "where": problem.get("where", "")})
    assert rows, "no open reviews"
    return rows


def section_changes(w: str):
    a, b = g(BASE, w), g(TAG, w)
    body, meta = [], []
    for sa, sb in zip(a["segments"], b["segments"]):
        ta = {item["id"]: item["text"] for item in sa["items"]}
        tb = {item["id"]: item["text"] for item in sb["items"]}
        ca = {item["id"]: item.get("cite", []) for item in sa["items"]}
        cb = {item["id"]: item.get("cite", []) for item in sb["items"]}
        if ta != tb:
            body.append(sb["sec"])
        elif sa.get("relation") != sb.get("relation") or ca != cb:
            meta.append(sb["sec"])
    return body, meta


def render_graph(graph, tag: str) -> list[str]:
    out = []
    for section in graph["segments"]:
        out += [f"#### {section['sec']}｜{section['bars']} 小节", "",
                f"**{tag} 原文**", "", f"关系：{section.get('relation')}", ""]
        for item in section["items"]:
            out.append(f"- `{item['id']}` {item['text']}")
            cites = item.get("cite") or []
            if cites:
                out.append(f"  引用：{'、'.join(cites)}。")
        out.append("")
    return out


def render_pair(w: str) -> list[str]:
    """Interleave the two versions section by section, as the fixed format requires."""
    old, new = g(BASE, w), g(TAG, w)
    assert len(old["segments"]) == len(new["segments"]), w
    out = []
    for sa, sb in zip(old["segments"], new["segments"]):
        assert sa["sec"] == sb["sec"], (w, sa["sec"], sb["sec"])
        out += [f"#### {sa['sec']}｜{sa['bars']} 小节", ""]
        for tag, section in ((BASE, sa), (TAG, sb)):
            out += [f"**{tag} 原文**", "", f"关系：{section.get('relation')}", ""]
            for item in section["items"]:
                out.append(f"- `{item['id']}` {item['text']}")
                cites = item.get("cite") or []
                if cites:
                    out.append(f"  引用：{'、'.join(cites)}。")
            out.append("")
    return out


def render_diff(old_tag: str, new_tag: str, w: str) -> list[str]:
    old = V.view(g(old_tag, w), ids=True).splitlines()
    new = V.view(g(new_tag, w), ids=True).splitlines()
    return list(difflib.unified_diff(old, new, fromfile=old_tag, tofile=new_tag, lineterm=""))


def build_note() -> Path:
    fair = fair_rows()
    net = "/".join(f"{fair['net_sums'][k]:+d}" for k in DIM_ORDER)
    op60_prompt = RUNS / f"scr{TAG[1:]}_op60_F1" / "prompt.txt"
    op61_prompt = RUNS / f"scr{TAG[1:]}_op61_F1" / "prompt.txt"
    applied = BATCH / "r78a_applied.json"
    edit_counts = {w: len(V.parse(f"scr{TAG[1:]}_{w}_F1")["edits"]) for w in WORKS}
    cov = {w: cov_transition(w) for w in WORKS}
    complete = fair["complete"]

    md = ["<!-- Generated by build_r78a_docs.py; do not hand edit. -->",
          f"## {TAG} 对 {BASE}：两首同跑回补", "",
          "### 提示词改动", "",
          "本次改动是 `r68a → r78a` 的一次回补（restore，F1），不是重写。实际提示词要求：只把评委指出、确实该留下的那一点带回来，同时保住当前稿已经赢下的东西；该带回来的是转折或决定的来由、害怕或愿望性质的变化、人物最后的态度和选择、某一段听感唯一的落脚处；不该带回来的是只是把别处说过的意思再说一遍、只是表达更细。两首同跑，最多改 6 条；未改条目逐字不动，不新增事件、前史、对白、物件、第三人和对方的新举动，不把希望和推测写成事实，不把珠子画面写成情节，结尾选择不改弱。",
          "",
          "这次生成只把上一版 `r67a` 的正反比较作为评委意见交回；对 `r49b` 的八票是生成之后的测量，不是生成输入。",
          "",
          f"- op60 实际输入：{link(op60_prompt)}，SHA256 `{digest(op60_prompt)}`。",
          f"- op61 实际输入：{link(op61_prompt)}，SHA256 `{digest(op61_prompt)}`。",
          f"- 机械套用记录：{link(applied)}。",
          "",
          f"边界：这步只做局部回补，不清理珠子、不解决 Op.60 后半和 Op.61 中段的回环，也不能为 Op.61 S07 补出前文没有的事实依据；开放评审的中等以上问题仍在。实际改动 op60 {edit_counts['op60']} 条、op61 {edit_counts['op61']} 条，未改条目逐字不动。",
          "",
          "### 实际测量与处置", "",
          f"对 `{BASE}`：已完整阅读并绑定实际两版输入 {complete}/{complete} 票；选新版 {fair['wins']}/{complete}，不退步 {fair['no_regress']}/{complete}；四维净胜总和 {net}。原覆盖逐段底线与单独读底线均过；绝对覆盖 Op.60 {cov['op60']}、Op.61 {cov['op61']}，仍是残余问题。",
          "",
          f"原始八票：{link(OUT / f'fair_{TAG}_vs{BASE}.json')}。覆盖：{link(OUT / f'cov2_{TAG}.json')}。单独读：{link(OUT / f'alone2_{TAG}.json')}。主线推进记录：{link(ROOT / 'DAG.md')} 的 11-04 修订记录。",
          ""]

    for w in WORKS:
        md += [f"### {w} 全部前后差别", "",
               f"模型完整原文：{link(RUNS / f'scr{TAG[1:]}_{w}_F1' / 'output.txt')}。", "", "```diff"]
        md += render_diff("r68a", TAG, w)
        md += ["```", ""]

    path = NOTES / f"{TAG}_vs_{BASE}.md"
    path.write_text("\n".join(md), encoding="utf-8")
    return path


def build_final() -> Path:
    fair = fair_rows()
    applied = BATCH / "r78a_applied.json"
    complete, wins, no_regress = fair["complete"], fair["wins"], fair["no_regress"]
    cov = {w: cov_transition(w) for w in WORKS}
    op60_extra = chars(g(TAG, "op60")) - chars(g(BASE, "op60"))
    op60_lean = work_net(fair, "op60", "lean")
    drops = {w: biggest_cov_drop(w) for w in WORKS}
    template = (RUNS / f"scr{TAG[1:]}_op60_F1" / "prompt.txt").read_text(encoding="utf-8").splitlines()
    cut = next(i for i, line in enumerate(template) if line.startswith("【当前稿"))
    template_text = "\n".join(template[:cut]).rstrip()

    md = ["<!-- Generated by build_r78a_docs.py; do not hand edit. -->",
          f"# 最终版本：{TAG} vs {BASE}", "",
          f"版本：`{TAG}`；固定比较起点：`{BASE}`。", "",
          "收敛状态：未收敛。没有收敛审计；`r78a` 是 11-04 当前已验收主线，只表示对 `r49b` 的直接八票和两道底线已通过，不表示已经收敛或全面胜过 `r49b`。", "",
          "本文件由脚本从两版正文、模型原始返回、冻结评审输入和验收记录生成；没有手选示例。正文差异逐段完整列出，引用与关系标签另列。", "",
          "迭代中的成品验收跟随当时最新已验收主线，接纳后推进基准；中间步骤只与当前流程的同位置产物快筛。本文件的固定起点只用于最终对照，不替代滚动的验收基准。", "",
          f"生成器：{link(ROOT / 'build_r78a_docs.py')}。本次生成不请求模型，不改正文、珠子、评审或判定线。", "",
          "## 提示词与实际生成链", "",
          "实际产物继承顺序：`r49b` → `r50progress1` → `r50progress1r` → `r50progress1rr` → `r54weave` → `r55repair` → `r55restored` → `r65a` → `r66a` → `r67a` → `r68a` → `r78a`。", ""]

    for step in STEPS:
        line = f"- `{step['base']} → {step['tag']}`：{step['mode']}"
        if step.get("receipt") and Path(step["receipt"]).exists():
            line += f"；机械套用记录：{link(step['receipt'])}"
        line += "。"
        md.append(line)
        for w in WORKS:
            info = check_step(step, w)
            md.append(f"  {w}：{link(info['prompt'], '完整实发输入')} · {link(info['output'], '模型完整返回')}。")
        md.append("")

    md += ["<details>", "<summary>r78a 回补提示词原文（模板部分，两首相同）</summary>", "", "```text",
           template_text, "```", "", "</details>", "",
           "最后一步的机械套用记录："
           f"{link(applied)}。该记录由脚本重新解析这一步的 output.txt，并把 edits 套回 r68a；替换目标和未改条目均与 r78a 逐字一致。", "",
           "## 直接比较的测量", "",
           f"本节只比较 `{TAG}` 与 `{BASE}`。完整收取且已全文核验、与当前两版输入逐字匹配：{wins}/{complete} 票。", "",
           "| 整体选新版 | 不退步 | 单独成立净胜总和 | 不啰嗦净胜总和 | 人话净胜总和 | 接珠子净胜总和 |",
           "|---:|---:|---:|---:|---:|---:|",
           f"| {wins}/{complete} | {no_regress}/{complete} | {fair['net_sums']['alone']:+d} | {fair['net_sums']['lean']:+d} | {fair['net_sums']['plain']:+d} | {fair['net_sums']['cover']:+d} |",
           "",
           "净胜总和是逐票“新版赢的段数−起点版赢的段数”相加，不是提升百分比。", "",
           "| 作品 | 评委 | 新版座位 | 选新版 | 不退步 | 单独 / 简洁 / 人话 / 覆盖 | 原始返回 |",
           "|---|---|---|---|---|---|---|"]

    for row in fair["rows"]:
        w, judge, seat = row["w"], row["j"], row["seat"]
        rid = f"v6b3_{w}_{judge}_{TAG}_vs{BASE}_{seat}"
        net = "/".join(f"{row['net'][k]:+d}" for k in DIM_ORDER)
        md.append(f"| {w} | {judge} | {seat} | {'是' if row['new_win'] else '否'} | "
                  f"{'是' if row['no_regress'] else '否'} | {net} | "
                  f"{link(RUNS / rid / 'output.txt')} |")

    md += ["",
           f"门槛同时要求至少 6 票选新版、至少 6 票不退步，单独成立/简洁/人话净胜非负，以及原逐段底线通过。本组 {wins}/{complete}、{no_regress}/{complete}，前三项净胜均为正；按原完整门槛计算：**通过**。底线见下节。", "",
           "## 原覆盖与单独读底线", "",
           "| 作品 / 评委 | 起点说清珠子数 | 当前说清珠子数 | 起点单独成立段 | 当前单独成立段 |",
           "|---|---:|---:|---:|---:|"]

    for w in WORKS:
        for judge in ("g6", "g56"):
            md.append(f"| {w} / {judge} | {cov_count(w, judge, BASE)} | {cov_count(w, judge, TAG)} | "
                      f"{alone_count(w, judge, BASE)} | {alone_count(w, judge, TAG)} |")

    floor_bad = VERDICT.floor(TAG, BASE)
    assert not floor_bad, floor_bad
    md += ["",
           "原逐段底线计算结果：`pass`。覆盖按同段两位评委是否均下降至少 2 颗判断，单独读按原成立段数门槛判断；全曲总数不代替逐段判断。",
           "",
           f"逐段最大下降：Op.60 {drops['op60'][0]} 为 {drops['op60'][1][0]}/{drops['op60'][1][1]} 颗，"
           f"Op.61 {drops['op61'][0]} 为 {drops['op61'][1][0]}/{drops['op61'][1][1]} 颗；没有一段两位评委都掉 2 颗以上，所以覆盖底线过。",
           "",
           f"绝对覆盖总数仍低于起点：Op.60 {cov['op60']}，Op.61 {cov['op61']}；相对盲比赢不等于绝对覆盖更多。", "",
           "## 全部正文与元数据差异", "",
           "| 作品 | 起点字数 / 条数 | 当前字数 / 条数 | 正文变化段 | 仅引用或关系变化段 |",
           "|---|---:|---:|---|---|"]

    for w in WORKS:
        a, b = g(BASE, w), g(TAG, w)
        body, meta = section_changes(w)
        md.append(f"| {w} | {chars(a)} / {item_count(a)} | {chars(b)} / {item_count(b)} | "
                  f"{', '.join(body) if body else '无'} | {', '.join(meta) if meta else '无'} |")

    for w in WORKS:
        while md and md[-1] == "":
            md.pop()
        md += ["", f"### {w}", "", f"Center：{g(TAG, w)['center']}", ""]
        md += render_pair(w)

    rows = open_rows()
    medium = [r for r in rows if r["severity"] in ("严重", "中等")]
    by_work = Counter(r["w"] for r in medium)
    by_dim = Counter((r["w"], r["goal"]) for r in medium)
    md += ["## 完整开放评审的现状", "",
           "下表逐份读取当前版已完成、已核验的评审，保留原评级和位置；有意见不等于已解决，意见是否符合标准仍看原文及输入范围审计。", "",
           "| 原始评审 | 等级 | 维度 | 位置 |", "|---|---|---|---|"]
    for row in rows:
        md.append(f"| {link(RUNS / row['rid'] / 'output.txt', row['rid'])} | {row['severity']} | {row['goal']} | {row['where']} |")

    md += ["",
           "维度 1–4 依次为单独成立、不啰嗦、人话、接得上珠子。", "",
           f"按当前十份评审（GPT 四位 + 留出 Gemini），中等以上 {len(medium)} 条：Op.60 {by_work['op60']}、Op.61 {by_work['op61']}；"
           f"按维度 Op.60 单独{by_dim[('op60','1')]}、不啰{by_dim[('op60','2')]}、人话{by_dim[('op60','3')]}、接得{by_dim[('op60','4')]}；"
           f"Op.61 单独{by_dim[('op61','1')]}、不啰{by_dim[('op61','2')]}、人话{by_dim[('op61','3')]}、接得{by_dim[('op61','4')]}。"
           f"连同轻微项共 {len(rows)} 条。", "",
           "这些意见集中在 Op.60 S06–S09、S11、S14 的重复回返，Op.61 S06–S13 的反复，以及珠子原稿/范围备注混入正文；少数句子仍像替人物整理心理。", "",
           "### 残余问题", "",
           f"- 绝对覆盖低于 `{BASE}`：Op.60 {cov['op60']}，Op.61 {cov['op61']}；逐段底线过，但总数不能当作没有下降。",
           f"- Op.60 比 `{BASE}` 多 {op60_extra} 字，不啰嗦净胜只有 {op60_lean:+d}（{complete} 票合计），是四个维度里最窄的。",
           f"- 开放评审仍有 {len(medium)} 条中等以上问题；Op.60 后半的“想要保证/怕不再被需要”和 Op.61 中段的“回不回去”仍在反复。",
           "- 没有收敛审计；只在这两首上跑过，没在别的作品上验证，评委也是迭代时用的同一批。", "",
           "## 成品与复现", ""]

    for name in ("op60_线与珠子_r78a.md", "op61_线与珠子_r78a.md",
                 "op60_只看线_r78a.md", "op61_只看线_r78a.md",
                 "integrity.json", "00_说明.md"):
        md.append(f"- {link(DELIVER / name)}")

    md += ["", "复现命令：", "", "```powershell", "python build_r78a_docs.py", "```", ""]

    path = ROOT / f"最终版本_{TAG}_vs_{BASE}.md"
    path.write_text("\n".join(md), encoding="utf-8")
    return path


def main() -> None:
    write_receipt()
    note = build_note()
    final = build_final()
    delivered = DELIVER / final.name
    delivered.write_text(final.read_text(encoding="utf-8"), encoding="utf-8")
    print("wrote", note)
    print("wrote", final)
    print("wrote", delivered)


if __name__ == "__main__":
    main()
