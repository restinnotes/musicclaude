"""接续已批准的迭代：以 qu 为基准，先把完整材料交回顾问。"""
import json
import re
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import evo
import pipe
import v6fix as V
from advisor_followup import meas_text

ROOT = Path(__file__).resolve().parent
BASE = "qu"


def material():
    spec = pipe.load_spec(ROOT / "schemes/Q15.json")
    rules = (ROOT / "迭代准则.md").read_text(encoding="utf-8")
    rules = rules[rules.index("## 二、迭代范围和硬约束"):rules.index("## 三、流程")]
    prompts = "\n\n".join(
        f"=====FILE: {step['prompt_file']}=====\n{spec['_texts'][step['prompt_file']]}"
        for step in spec["steps"]
    )
    lines = "\n\n".join(f"【{w}】\n{V.view(V.graph_of(w, BASE), center=True)}" for w in ("op60", "op61"))
    history = (ROOT / "试验记录.md").read_text(encoding="utf-8")
    message = (
        "用户已看过上一轮，确认迭代流程可行，要求继续。现在主线是 Q15/qu，不再是 m6w。\n"
        "你是上一轮的方案顾问，现在把实际成品、开放评审和失败记录交回，请判断怎么继续。\n"
        "优先换掉导致问题的写法，而不是继续堆禁止条款；可以改经历骨架、选路或写线层，不增加修补成品的层。\n"
        "本次请给一套最值得实际试跑的方案，保持四步接口、占位符和 JSON 输出结构兼容。\n"
        "诊断可以引用眼前作品；可运行提示词绝不能包含具体作品、段号、人物情节或针对某一处毛病的例子。\n"
        "不改分段、A稿、珠子、Center，不手改成品，两首同一套提示词；每段2–4条、每条一句，保留引用与关系标签。\n\n"
        "【标准】\n" + (ROOT / "标准.md").read_text(encoding="utf-8")
        + "\n【硬约束】\n" + rules
        + "\n【实际运行的四层提示词】\n" + prompts
        + "\n【实际成品】\n" + lines
        + "\n【测量及逐段理由、开放评审】\n" + meas_text(BASE, "qo")
        + "\n【实验历史，避免重走失败路线】\n" + history[-24000:]
        + "\n【本轮任务】\n"
        "先判断关键转折缺前因、后半篇绕圈、替人物概括心理分别来自哪层，哪些评审意见不应照办。\n"
        "然后给出一套完整改法；未改的层不要输出。输出‘结论：改了再试’或‘结论：放弃’。\n"
        "如改了再试，逐个输出修改后的完整提示词，文件名仍用原文件名，严格采用格式：\n"
        "=====FILE: Q15_A4.txt=====\n（完整提示词）\n=====END=====\n"
        "如果修改上游层，文件名分别是 Q6_A1.txt、Q6_A2.txt、Q6_A3.txt。不得输出任何其他文件。"
    )
    print("材料核对", {"作品数": 2, "提示词层数": len(spec["steps"]), "材料字数": len(message)}, flush=True)
    assert all(len(V.graph_of(w, BASE)["segments"]) > 0 for w in ("op60", "op61"))
    return message


def advise(who, message):
    rid = f"resume20261102_{who}_qu"
    if not evo.done(rid):
        if who == "gem":
            evo.call_gemini_direct(rid, message, meta={"stage": "接续顾问", "base": BASE})
        else:
            evo.call(rid, message, model=V.JUDGES[who], meta={"stage": "接续顾问", "base": BASE})
    response = evo.output(rid)
    if not response:
        raise RuntimeError(f"{who} 未完成，未生成候选")
    (V.OUT / f"{rid}.md").write_text(response, encoding="utf-8")
    files = re.findall(r"=====FILE:\s*(\S+?)\s*=====\s*\n(.*?)\n=====END=====", response, re.S)
    allowed = {s["prompt_file"] for s in pipe.load_spec(ROOT / "schemes/Q15.json")["steps"]}
    if any(name not in allowed for name, _ in files):
        raise RuntimeError(f"{who} 输出未授权文件名")
    if len({name for name, _ in files}) != len(files):
        raise RuntimeError(f"{who} 输出重复文件")
    print(who, "顾问已完成", "候选文件", [name for name, _ in files], "请先人工检查再运行", flush=True)


if __name__ == "__main__":
    message = material()
    with ThreadPoolExecutor(max_workers=2) as pool:
        futures = [pool.submit(advise, who, message) for who in ("gem", "g6")]
        for future in futures:
            future.result()
