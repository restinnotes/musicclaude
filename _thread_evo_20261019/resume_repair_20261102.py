"""将未通过运行前检查的顾问方案交回原提出者，不擅自代改。"""
import json
from concurrent.futures import ThreadPoolExecutor

import evo
import pipe
from resume_20261102 import ROOT


def run(who):
    old = evo.output(f"resume20261102_{who}_qu")
    assert old
    spec = pipe.load_spec(ROOT / "schemes/Q15.json")
    originals = {s["prompt_file"]: spec["_texts"][s["prompt_file"]] for s in spec["steps"]}
    issue = (
        "你的运行提示词未通过泛化和标准检查：其中直接写了眼前成品的关键关系情节、相近处境例子，以及来自这批 TARGETS 的文艺句；"
        "这些不是通用方法，不能进入提示词。另有机械禁用‘这份/那点/这股’等词、每次回响必须推进、中段只能暂时不想等要求，"
        "与标准‘不机械禁词、不强造进步、允许延续’冲突。请自己重写这些部分，不让我替你综合。"
        if who == "gem" else
        "你的诊断有价值，但返回的提示词占位符全部消失：作品、段落、Center、候选数与 A4 输入标题下为空；"
        "FILE 标记也被 Markdown 转义，无法直接运行。请保留你的改法，只修复接口并返回可机器读取的格式。"
    )
    message = (
        "继续上一轮：你的方案尚未运行，运行前检查发现以下问题，请作为提出者修正。\n"
        + issue + "\n\n【你上一次的完整答复】\n" + old
        + "\n\n【原接口提示词，准确占位符以此为准】\n" + json.dumps(originals, ensure_ascii=False)
        + "\n\n【返回格式】\n只输出一个 JSON 对象，不用 Markdown，不用 FILE 标记。"
        "结构为 {\"analysis\":\"修改理由\",\"files\":{\"原文件名\":\"完整提示词字符串\"}}。"
        "只返回你改的层。A1 必须保留 {NAME}、{SECTIONS}、{CENTER}、{K}；"
        "A4 必须保留 {SECTIONS}、{CENTER}、{ROUTES}、{TARGETS}。A2 的 ROUTES 由流水线末尾附加，不必添加。"
        "不要含具体作品、眼前故事、固定心理主题或针对某段的例子。"
        "不要机械禁词、不要强制每段新进步，保持四层兼容、两首同提示词。"
    )
    rid = f"resume20261102_{who}_repair1"
    if not evo.done(rid):
        if who == "gem":
            evo.call_gemini_direct(rid, message, meta={"stage": "运行前退回", "base": "qu"})
        else:
            evo.call(rid, message, model="gpt-6-thinking", meta={"stage": "运行前退回", "base": "qu"})
    response = evo.output(rid)
    if not response:
        raise RuntimeError(f"{who} 未返回完整修正版")
    print(who, "修正版已返回", len(response), "字，待审查", flush=True)


if __name__ == "__main__":
    with ThreadPoolExecutor(max_workers=2) as executor:
        futures = [executor.submit(run, who) for who in ("gem", "g6")]
        for future in futures:
            future.result()
