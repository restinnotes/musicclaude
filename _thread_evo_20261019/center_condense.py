"""Center condensing (user 10-21: Centers still wordy; an unclear core trouble will mislead every later step).
P0: Center = what matters to him + what makes it hard to settle; no route, no answer. Here: one sentence <=30 chars,
'matters' <=12 chars, 'hard' <=20 chars; no 3-item lists, no 越…越, no abstract words; meaning must not drift.
GPT-6 gives 3 phrasings per candidate and picks one (orchestrator does not write candidates).
ids: ccd -> evaluations/centersel/pool_<w>.json (condensed 'center', original kept as 'center_long')"""
import json, sys
import centersel, evo

P = ("下面是几首肖邦作品的候选 Center（一条“线”围绕的那件人的事）。它们太啰嗦，会误导后面的写作。请把每个候选压成最精炼、最清楚的一句：\n"
     "- 只说两件事：什么对他重要（matters，不超过 12 字）；是什么使它难以安顿（hard，不超过 20 字）。合成一句 center，不超过 30 字。\n"
     "- 抓住那一个核心矛盾，不要并列三四样东西（如“伤感、迟疑和旧日记忆”），不要“越……越……”，不要抽象词（归属、安顿、边界、张力），用人话。\n"
     "- 不预告发展路线和最后的答案；不改变原意，不换成新的角度。\n"
     "每个候选先给 3 种写法，再选出最好的一种，并说明它是否偏离原意（drift：无／轻微／明显）。\n"
     "只输出一个 ```json 代码块：{\"items\": [{\"id\": \"…\", \"options\": [\"…\", \"…\", \"…\"], \"center\": \"选中的一句\", \"matters\": \"…\", \"hard\": \"…\", \"drift\": \"无\"}]}\n\n候选：\n")

if __name__ == "__main__":
    pools = {w: centersel.pool(w) for w in ("op60", "op61")}
    msg = P + "\n".join(f"{w}:{c['id']}（{'船歌 Op.60' if w == 'op60' else '幻想波兰舞曲 Op.61'}）：{c['center']}" for w, p in pools.items() for c in p)
    r = evo.call("ccd", msg, prompt_text=P, meta={"stage": "center_condense"})
    got = {x["id"]: x for x in evo.parse_json(r)["items"]}
    centersel.OUT.mkdir(parents=True, exist_ok=True)
    for w, p in pools.items():
        for c in p:
            x = got.get(f"{w}:{c['id']}")
            if x:
                c.update(center_long=c["center"], center=x["center"], matters=x.get("matters"), hard=x.get("hard"), drift=x.get("drift"), options=x.get("options"))
            print(w, c["id"], f"[{len(c['center'])}字|偏离:{c.get('drift')}]", c["center"])
        (centersel.OUT / f"pool_{w}.json").write_text(json.dumps(p, ensure_ascii=False, indent=1), encoding="utf-8")
