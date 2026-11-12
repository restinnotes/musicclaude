"""Center v3 (user 10-21: the 6 relation sentences were wordy, Op.61's three were one Center, Op.60-3 weak; redo and
self-accept before showing). Inputs: consensus clusters from the 24 A drafts, selection-test results, historical
candidates for these pieces. GPT-6 proposes only truly distinct Centers (1-3 per work), minimal relation sentences.
Acceptance: form check (script) + specificity/fit tests (centersel) + my reading.
usage: python center_v3.py gen <round> | check <round>"""
import json, re, sys
import centersel, evo

HIST = {"op60": ["对亲密的投入和对控制的维持都要求成立，并长期互相牵制。", "同一份亲密的温柔与严肃分量持续并存。"],
        "op61": ["向外行动与向内牵动都要求成立，却彼此牵制。"]}
P = ("任务：为{WORK}确定 Center。Center 是一条“线”围绕的那件人的事，要写成“最小完整关系句”：\n"
     "- 主语：一个或几个对象，用名词直接点出事物本身（例如幸福、时间、深情、克制、行动、梦）——“具体”是指说得出它究竟是什么，不是用比喻或画面；"
     "不要用身体或场景道具来比喻（手、心跳、脚步、门、水面、影子……），它们会把画面和情节带进后面的写作；不出现人称（他、我、人、两人）和心理动词（想、怕、舍不得……）；\n"
     "- 谓语：说清这几个对象之间的一个关系（可以是“都要求成立，却彼此牵制”这样的复合谓语，但只说一个关系）；这个关系从曲子较早处成立，一直到结尾都成立；\n"
     "- 语域：像下面 C 里的历史候选那样——直接说出事物本身和它们的关系，既不用比喻和画面，也不堆砌空的抽象词；可以用“对……的投入”“……这件事”“向外行动”“梦与回忆”这类直白的说法；\n"
     "- 尽可能短：全句不超过 25 个汉字；不并列三样东西；不用“越……越……”；不用空的抽象词（归属、安顿、边界、张力）；\n"
     "- 不写后来才出现的变化、认识、解决或结局；不写成问句；不要为了戏剧性默认冲突，但原意是冲突就写明。\n"
     "依据（不要换成新奇角度，要贴着这些材料里最有说服力的理解）：\n"
     "A. 24 份独立文章对这首曲子的中心理解，聚类后的结果：\n{CLUSTERS}\n"
     "B. 上一轮检验（只看一句话能否认出是这首曲子 / 逐段能否自然解释 / 综合说服力）：\n{TESTS}\n"
     "C. 以前为这首曲子讨论过的候选（可以采用、改进或否定）：\n{HIST}\n"
     "只给出彼此真正不同的 Center（1–3 个；同一个矛盾换个角度或换个说法，算同一个，只留最好的一种）。每个先给 3 种写法，再选一种。\n"
     "只输出一个 ```json 代码块：{\"centers\": [{\"options\": [\"…\", \"…\", \"…\"], \"center\": \"选中的一句\", \"distinct_because\": \"它和其他候选的根本区别\", \"basis\": \"依据 A/B/C 的哪部分\"}]}")
BAD = {"人称/心理动词": r"他|(?<!自)我|想|怕|舍不得|希望|渴望|的人", "画面道具": r"手|心跳|脚步|指尖|微笑|门|水面|眼泪|背影|影子|情话|两人|散场|唇|脊背", "越…越": r"越.{0,12}越", "结局词": r"最终|终于|学会|最后|走出", "问句": r"？|\?"}


def form_check(c):
    s = c.rstrip("。.")
    issues = [k for k, v in BAD.items() if re.search(v, s)]
    if len(s) > 27:
        issues.append(f"长度{len(s)}")
    if s.count("、") >= 2:
        issues.append("并列三项")
    if len(re.findall(r"[，,；;]", s)) > 1:
        issues.append("多个分句")
    return issues


if __name__ == "__main__":
    ph, rnd = sys.argv[1], sys.argv[2]
    for w in ("op60", "op61"):
        if ph == "gen":
            A = json.loads((evo.ROOT / "evaluations" / "centers" / f"A_{w}.json").read_text(encoding="utf-8"))
            cl = "\n".join(f"- （{c['n']} 份）{c['summary']}" for c in A["clusters"])
            tests = (centersel.OUT / f"{w}.md").read_text(encoding="utf-8")
            msg = P.replace("{WORK}", "船歌 Op.60" if w == "op60" else "幻想波兰舞曲 Op.61").replace("{CLUSTERS}", cl).replace("{TESTS}", tests).replace("{HIST}", "\n".join(f"- {h}" for h in HIST[w]))
            r = evo.call(f"cv3_{rnd}_{w}", msg, prompt_text=P, meta={"stage": "center_v3"})
            j = evo.parse_json(r)
            (evo.ROOT / "evaluations" / "centers" / f"v3_{rnd}_{w}.json").write_text(json.dumps(j, ensure_ascii=False, indent=1), encoding="utf-8")
        j = json.loads((evo.ROOT / "evaluations" / "centers" / f"v3_{rnd}_{w}.json").read_text(encoding="utf-8"))
        for k, c in enumerate(j["centers"], 1):
            print(w, k, f"[{len(c['center'].rstrip('。'))}字]", c["center"], "| 形式问题:", form_check(c["center"]) or "无", "| 选项:", " / ".join(f"{o}{form_check(o) or ''}" for o in c["options"]))
            print("    区别:", c.get("distinct_because"))
