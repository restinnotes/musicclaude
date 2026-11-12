"""I12/I13: return invalid candidates to their authors; prepare locally before calls.

Usage: python resume_feedback_20261102.py --prepare
       python resume_feedback_20261102.py --run g6|gem
Returned proposals remain for human/agent review; this script never promotes a line.
"""
import argparse
import json
from pathlib import Path

import evo
import mg_schedule
import pipe
import v6fix as V

ROOT = Path(__file__).resolve().parent
FEEDBACK = {
    "gem": ("R26G", "r26g", "Op.60 从第一段起新增了事先确定暂别的安排，之后不断用对方的回应推动转折，结尾又让两人实际分开。"
            "这些外部事实不来自既有输入，也不因在第一段先写出就自动合规。它绕过旧稿缺前因的问题，却引入了新编安排和事件。"),
    "g6": ("R26T", "r26t", "Op.61 后半段靠‘眼下要处理的事情’‘把该处理的事做了’‘事情过后’完成主要转折，"
           "这个未交代的事件并无输入依据。前半段又出现先压住怀念、发现不管用、换一种办法的心理算账。"
           "请判断自己的方案是否回到已失败的办法试验链，以及怎样保留真实经历的发展而不借含糊事件完成论证。"),
}


def prepare(who):
    name, tag, issue = FEEDBACK[who]
    spec = pipe.load_spec(ROOT / f"schemes/{name}.json")
    prompts = {step["prompt_file"]: spec["_texts"][step["prompt_file"]] for step in spec["steps"]}
    lines = {work: V.view(V.graph_of(work, tag), center=True) for work in ("op60", "op61")}
    raw = {}
    for prefix in ("cov2", "al2", "tr2", "v6b2"):
        for work in ("op60", "op61"):
            for judge in ("g6", "g56"):
                rid = f"{prefix}_{work}_{judge}_{tag}" + ("_vsqu" if prefix == "v6b2" else "")
                if evo.done(rid):
                    raw[rid] = evo.output(rid)
    rules = (ROOT / "迭代准则.md").read_text(encoding="utf-8")
    rules = rules[rules.index("## 二、迭代范围和硬约束"):rules.index("## 三、流程")]
    message = (
        "这是你上一套实际运行方案的反馈，按 I12/I13 交回提出者。主线仍为 Q15/qu，本候选没有收下。\n"
        "测量因基础设施问题中断，以下只有已完整返回的原始结果；不能把未测项说成通过或失败。"
        "但正文已经出现硬约束问题，因此先处理它，不耗费更多评审把违规候选测到底。\n"
        "【通读发现，供你诊断】\n" + issue
        + "\n这些句子只用于诊断，不得把眼前人物、情节或段号写进可运行提示词。"
        "请自行判断该放弃还是改了再试；若改，优先更换造成问题的任务定义，不叠具体禁令，也不机械禁词或强制每段进步。\n"
        "【标准】\n" + (ROOT / "标准.md").read_text(encoding="utf-8")
        + "\n【硬约束】\n" + rules
        + "\n【你的实际运行提示词】\n" + json.dumps(prompts, ensure_ascii=False)
        + "\n【两首完整成品】\n" + json.dumps(lines, ensure_ascii=False)
        + "\n【已完成的原始测量，未出现的项均缺失】\n" + json.dumps(raw, ensure_ascii=False)
        + "\n【实验历史】\n" + (ROOT / "试验记录.md").read_text(encoding="utf-8")[-20000:]
        + "\n【输出】\n只输出 JSON 对象：{\"decision\":\"放弃或改了再试\",\"analysis\":\"诊断与取舍\","
        "\"files\":{\"原提示词文件名\":\"修改后完整提示词\"}}。未改的层不要返回。"
        "保持当前四步接口和占位符；A1 保留 {NAME} {SECTIONS} {CENTER} {K}；"
        "A4 保留 {SECTIONS} {CENTER} {ROUTES} {TARGETS}。A2 的候选路线在模板末尾附加。"
        "A3 不改；两首同一套通用提示词。返回方案不会自动运行，先查泛化性和标准。"
    )
    rid = f"resume20261102_{who}_candidate_feedback2"
    folder = evo.RUNS / rid
    folder.mkdir(exist_ok=True)
    path = folder / "prepared_input.txt"
    if path.exists() and path.read_text(encoding="utf-8") != message:
        raise RuntimeError("已冻结的反馈输入发生变化，请先审查并使用新的 run_id")
    path.write_text(message, encoding="utf-8")
    print(who, "候选", tag, "作品", len(lines), "提示词", len(prompts), "完整测量", len(raw), "输入字数", len(message), flush=True)
    assert len(lines) == 2 and len(prompts) == 4 and all(lines.values())
    return rid, message


def run(who):
    mg_schedule.check()
    rid = f"resume20261102_{who}_candidate_feedback2"
    frozen = evo.RUNS / rid / "prepared_input.txt"
    if frozen.exists():
        message = frozen.read_text(encoding="utf-8")
        print(who, "使用已冻结输入", len(message), "字", flush=True)
    else:
        rid, message = prepare(who)
    if not evo.done(rid):
        if who == "gem":
            evo.call_gemini_direct(rid, message, meta={"stage": "I12/I13候选反馈", "base": "qu"})
        else:
            evo.call(rid, message, model=V.JUDGES[who], meta={"stage": "I12/I13候选反馈", "base": "qu"})
    response = evo.output(rid)
    if not response:
        # GPT route persists its own failure. A direct Gemini failure must also cool down.
        if not mg_schedule.status().get("cooling"):
            mg_schedule.fail(rid, "顾问调用未完整返回")
        raise SystemExit("未完成；保留原始输入，按共享状态记录的故障分类和截止恢复")
    destination = V.OUT / f"{rid}.md"
    destination.write_text(response, encoding="utf-8")
    print("顾问已返回，待审查：", destination, flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--prepare", action="store_true")
    parser.add_argument("--run", choices=tuple(FEEDBACK))
    args = parser.parse_args()
    if args.prepare:
        for who in FEEDBACK:
            prepare(who)
    elif args.run:
        run(args.run)
    else:
        parser.error("choose --prepare or --run")
