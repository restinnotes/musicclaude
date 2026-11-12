"""Return the second Gemini proposal's preflight failures to its author, once."""
import json
from pathlib import Path

import evo
import mg_schedule

ROOT = Path(__file__).resolve().parent
RID = "resume20261102_gem_preflight3"


def main():
    mg_schedule.check()
    folder = evo.RUNS / RID
    folder.mkdir(exist_ok=True)
    frozen = folder / "prepared_input.txt"
    if not frozen.exists():
        prior = json.loads((ROOT / "evaluations/v6fix/resume20261102_gem_candidate_feedback2.parsed.json").read_text(encoding="utf-8"))
        message = (
            "你第二版的实际运行提示词未通过 I03，尚未试跑。请作为提出者最后修正一次；不能让我替你改或混合方案。"
            "若无法给出符合标准的通用方案，请直接放弃。\n"
            "【运行前发现】\n"
            "1. A1/A4 仍把眼前失败情节写成禁令和例子：事先约定、预设相处何时必须结束、行程安排、结局现实动作。"
            "即使写成反例也不泛化。诊断可以引用眼前故事，可运行提示词不得含这些例子。\n"
            "2. 将所有 Thread 定义为独自经历、纯粹内在，且要求核心矛盾贯穿始终、终局态度只能留到最后，"
            "擅自收窄了标准。标准禁止新编事实推动，不要求每件事都是独处心路，也不预定中途不能出现已成立的认识或结尾必须落定。\n"
            "3. A4 规定一段多条必须是不同时序的念头推进，与标准允许同段多种感受共存、允许延续冲突。"
            "也不应将没有外部动作变成写作资格。\n"
            "请更换任务定义或删去会收窄任务的安排，而不是增加更多禁止条款。保留你真正有价值的改法，"
            "不要只把上述情节换成同义词，也不要预定每段进步、强度增加或只有情绪起伏。\n"
            "【用户标准】\n" + (ROOT / "标准.md").read_text(encoding="utf-8")
            + "\n【你的第二版完整答复】\n" + json.dumps(prior, ensure_ascii=False)
            + "\n【硬约束】\n两首同一套通用提示词；不改分段、A稿、珠子、Center；不手改正文；"
            "A1/A2 不见珠子，A3 不改，A4 才见去画面情节的 TARGETS；允许联网。"
            "保留四步接口、原占位符与 JSON 输出字段。"
            "只输出 JSON：{\"decision\":\"放弃或改了再试\",\"analysis\":\"诊断与取舍\","
            "\"files\":{\"R26G_A1.txt\":\"完整提示词\",\"R26G_A2.txt\":\"完整提示词\",\"R26G_A4.txt\":\"完整提示词\"}}。"
            "只返回确实修改的层。A1 保留 {NAME} {SECTIONS} {CENTER} {K}，A4 保留 {SECTIONS} {CENTER} {ROUTES} {TARGETS}。"
        )
        frozen.write_text(message, encoding="utf-8")
    message = frozen.read_text(encoding="utf-8")
    print("第三次运行前退回", "输入字数", len(message), flush=True)
    if not evo.done(RID):
        evo.call_gemini_direct(RID, message, meta={"stage": "I03泛化/标准退回", "base": "qu"})
    response = evo.output(RID)
    if not response:
        if not mg_schedule.status().get("cooling"):
            mg_schedule.fail(RID, "Gemini运行前修正未完整返回")
        raise SystemExit("基础设施失败，按共享状态记录的故障分类和截止恢复")
    (ROOT / "evaluations/v6fix" / f"{RID}.md").write_text(response, encoding="utf-8")
    print("已返回，仍须人工检查，不自动运行", flush=True)


if __name__ == "__main__":
    main()
