"""Rewrite the shortlisted Centers into the historical Center format (09-21/22, reconfirmed 10-14/10-19):
the minimal complete relation sentence — subject (one or more objects, noun phrases) + predicate (how they relate),
holding from early on to the end; no person/action wording, not two bare nouns, no relation menu, no default conflict,
no later change or answer. GPT-6 gives 3 options per Center and picks one. -> evaluations/centers/sel_<w>.json"""
import json
import centersel, evo

SHORT = {"op60": ["A1", "A2", "R1"], "op61": ["DD", "A3", "A1"]}
P = ("下面是两首肖邦作品的几个候选 Center（一条“线”围绕的那件人的事）。请把每个改写成“最小完整关系句”：\n"
     "- 主语是一个或几个对象，用具体的名词短语（不要“他想……却……”这种人称和动作，那是多余的）；\n"
     "- 谓语说清这几个对象之间究竟怎样相关；关系从曲子较早处就成立，一直到结尾都成立；\n"
     "- 不只是两个名词并列（如“行动 / 内在牵动”不合格，因为没说怎样相关）；\n"
     "- 不要预设关系类型，不要为了戏剧性默认写成冲突；但如果原意确实是冲突或牵制，就写明；\n"
     "- 不写后来才出现的变化、认识、解决或结局；不写成问句；不用抽象词堆砌（归属、安顿、边界、张力）；尽量短。\n"
     "- 保持原意，不要换成新的角度。\n"
     "参考格式（只示范格式，与这两首无关的内容请勿套用）：“向外行动与向内牵动都要求成立，却彼此牵制。”\n"
     "每个先给 3 种写法，再选最好的一种。只输出一个 ```json 代码块：{\"items\": [{\"id\": \"…\", \"options\": [\"…\", \"…\", \"…\"], \"center\": \"选中的一句\"}]}\n\n候选：\n")

if __name__ == "__main__":
    lines = []
    pools = {w: {c["id"]: c for c in json.loads((centersel.OUT / f"pool_{w}.json").read_text(encoding="utf-8"))} for w in SHORT}
    for w, ids in SHORT.items():
        for i in ids:
            c = pools[w][i]
            lines.append(f"{w}:{i}（{'船歌 Op.60' if w == 'op60' else '幻想波兰舞曲 Op.61'}）：{c['center']}（较长的原意：{c.get('center_long', c['center'])}）")
    r = evo.call("crf", P + "\n".join(lines), prompt_text=P, meta={"stage": "center_relform"})
    got = {x["id"]: x for x in evo.parse_json(r)["items"]}
    for w, ids in SHORT.items():
        out = []
        for i in ids:
            c = dict(pools[w][i]); x = got[f"{w}:{i}"]
            c.update(center_sentence=c["center"], center=x["center"], relform_options=x.get("options")); out.append(c)
            print(w, i, x["center"], "|", " / ".join(x.get("options", [])))
        (evo.ROOT / "evaluations" / "centers" / f"sel_{w}.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
