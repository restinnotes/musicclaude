"""Create P/Q descriptions by extracting literal text from the unchanged reference."""
import ast
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TEMP = Path(__file__).resolve().parent
source = (ROOT / "schemes.py").read_text(encoding="utf-8")
tree = ast.parse(source)
constants = {}
notes = {}
for node in tree.body:
    if isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
        if node.targets[0].id in {"CENTER_IN", "P_A2_C_NEW"}:
            constants[node.targets[0].id] = ast.literal_eval(node.value)
    if isinstance(node, ast.FunctionDef) and node.name in {"run_P", "run_Q"}:
        for call in ast.walk(node):
            if isinstance(call, ast.Call) and isinstance(call.func, ast.Name) and call.func.id == "save":
                notes[node.name[-1]] = ast.literal_eval(call.args[3])


def literal(text):
    return {"text": text}


def step(sid, filename, replace, after=None, append=None):
    item = {"id": sid, "prompt_file": filename + ".txt", "replace": replace, "model": "g6"}
    if after is not None:
        item["after"] = after
    if append is not None:
        item["append"] = append
    return item


center_before, center_after = constants["CENTER_IN"].split("{CENTER}")
new_before, new_after = constants["P_A2_C_NEW"].split("{CENTER}")
p_a2 = (ROOT / "schemes/P_A2.txt").read_text(encoding="utf-8")
p = {
    "name": "P", "note": notes["P"],
    "edits": [{"prompt_file": "P_A2.txt", "old": p_a2[p_a2.index("七、Center"):p_a2.index("八、语言")],
               "new": [literal(new_before), "CENTER", literal(new_after)]}],
    "steps": [
        step("A0", "P_A0", {
            "{WORK_INFO}": "WORK_INFO",
            "{SEGMENTS}": ["SEGMENTS", literal(center_before), "CENTER", literal(center_after)],
            "{INDEPENDENT_MUSIC_CONTEXT}": literal("（无）")}),
        step("A1", "P_A1", {
            "{CANDIDATES_JSON}": "step:A0", "{BEADS_JSON}": "BEADS_TEXT", "{SEGMENTS}": "SEGMENTS"}),
        step("A2", "P_A2", {
            "{WORK_INFO}": "WORK_INFO", "{SEGMENTS}": "SEGMENTS",
            "{CANDIDATES_JSON}": "step:A0", "{COVERAGE_PLAN_JSON}": "step:A1"}),
    ], "final": "A2",
}
q = {
    "name": "Q", "note": notes["Q"],
    "steps": [
        step("A1", "Q_A1", {"{NAME}": "WORK_INFO", "{SECTIONS}": "SEGMENTS", "{K}": literal("3")}),
        step("A2", "Q_A2", {"{ROUTES}": "step:A1"}, append="\n\n【候选路线】\n{ROUTES}"),
        step("A3", "Q_A3", {"{SEGMENTS}": "SEGMENTS", "{BEADS_TEXT}": "BEADS_TEXT"},
             after=["A1"], append="\n\n【段落】\n{SEGMENTS}\n\n【珠子】\n{BEADS_TEXT}"),
        step("A4", "Q_A4", {"{SECTIONS}": "SEGMENTS",
             "{ROUTES}": ["step:A1", literal("\n\n【宏观评审结果】\n"), "step:A2"],
             "{TARGETS}": "step:A3"}),
    ], "final": "A4",
}
for name, spec in [("P", p), ("Q", q)]:
    target = ROOT / "schemes" / f"{name}.json"
    with target.open("x", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(spec, ensure_ascii=False, indent=2) + "\n")
    print("created", target)

protected = list(ROOT.glob("*.py")) + list((ROOT / "schemes").glob("*.txt"))
protected += [ROOT / "evaluations/v6fix" / f"{w}_m6w.json" for w in ("op60", "op61")]
protected += list((ROOT / "runs").glob("scpa_*/prompt.txt")) + list((ROOT / "runs").glob("scqa_*/prompt.txt"))
snapshot = {str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest()
            for path in protected if path.name != "pipe.py"}
(TEMP / "protected_before.json").write_text(json.dumps(snapshot, ensure_ascii=False, indent=2), encoding="utf-8")
with (TEMP / "log.md").open("x", encoding="utf-8", newline="\n") as handle:
    handle.write("""# pipe.py 实施及离线验证日志（2026-11-02）

- 授权范围：仅新增 pipe.py、schemes/P.json、schemes/Q.json、schemes/README_pipe.md，以及本目录内验证产物。已有 codex_log.txt / codex_prompt.md 不改。
- 所有文本通过 Python 显式 UTF-8 或 PowerShell -Encoding UTF8 读取。初次 PowerShell 管道向 Python 标准输入传脚本时附带 BOM，Python 报 SyntaxError，未产生写入；后续改用脚本文件或 python -c。
- 读取 ROOT 各父目录、schemes、_codex 及本目录的适用 AGENTS.md；未发现附加指令文件。
- 参考实现：schemes.py 的 work_info/segments/run_P/run_Q/call/save；v6fix.JUDGES/parse/tidy/view；covjudge.bead_text；evo.done/call/run_parallel。
- P：A0 → A1 → A2；A2 在内存替换七、Center 整段。所有原文及注释来自源码 AST / 原始提示词，未改动提示词文件。
- Q：A1 → A2、A3 并行 → A4。A3 虽不读取 A1 输出，仍显式 after A1 以复现原流程。step: 引用自动增加数据依赖。
- 模型核对：schemes.py 唯一 call 包装函数固定 model=evo.G6；因此 P/Q 所有 model 均为 g6。Q 的 GPT-5.6 标签指顾问来源，不代表实际生成模型。通用执行器支持 g56，严格映射 V.JUDGES。
- 调用边界：仅传 model 和原样 stage 元数据；不传 cli_args、web、推理参数，不修改路由、保温、watchdog 或任务计划。
- SAMPLE 规则：输入 TAG=pa、SAMPLE=2 时，运行 id 为 scpa_op60_A0_s2，成品 TAG 为 pas2；避免把 s2 重复加进运行 id。
- 已有真实 prompt.txt 含 evo 路由追加的 NO_WEB 段落；验证分别报告渲染正文直接比较及按现有路由追加后比较，绝不修改新脚本正文来掩盖这项差异。
- 当前仅发现 P 的 A0、Q 的 A1 各两首作品的真实 prompt.txt；未发现它们的 output.txt。
- 保护快照记录已有根目录 Python 源码、7 份提示词、2 份参考成品和现有 pa/qa prompt.txt 的 SHA-256；验证后再次核对。

后续离线验证明细见本日志追加内容及 results.json。
""")
