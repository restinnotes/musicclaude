"""Op.60 'happiness' Center, round 4: round 3's '眼前的幸福与无法留住幸福的忧伤始终并存' was the widest consensus
(13/24 drafts, B0's theme) but failed acceptance: static predicate ('并存') -> development 4.5, only 57% of segments
explained naturally. Redo the predicate only: say how the two act on each other (no default conflict).
Then the same content tests in one comparison with the accepted '对亲密的投入与自我克制始终相互牵制'.
usage: python center_v4_op60.py gen | pool | spec | fit | report"""
import json, sys
import center_v3, centersel, evo

P = ("为船歌 Op.60 改写一个 Center。Center 是一条“线”围绕的那件人的事，写成“最小完整关系句”：主语是一个或几个对象，用名词直接点出事物本身；"
     "谓语说清它们之间的一个关系，从曲子较早处成立到结尾。\n"
     "原意（24 份独立文章里最多的一类理解，13 份）：一个人正在享受真实的温柔、亲密或美好，却越珍惜越清楚它不能永久存在，幸福本身就带着舍不得和隐痛。\n"
     "上一版：“眼前的幸福与无法留住幸福的忧伤始终并存。”它的问题：谓语“始终并存”是静态的，只说两样东西同时在，没说它们怎样作用于对方，"
     "所以线很难从它展开出前后的变化。\n"
     "请只改谓语：说清这两样东西怎样作用于对方（例如一方怎样改变另一方的分量、意义或滋味），不要为了戏剧性默认写成冲突；"
     "不写后来才出现的变化、认识或结局；不用比喻和画面道具（手、心跳、影子、水面……）；不出现人称（他、我、人）和心理动词（想、怕、舍不得）；"
     "不用“越……越……”；全句不超过 25 个汉字。\n"
     "给 3 种写法，再选一种。只输出一个 ```json 代码块：{\"options\": [\"…\", \"…\", \"…\"], \"center\": \"选中的一句\"}")

centersel.OUT = evo.ROOT / "evaluations" / "centersel_v4"

if __name__ == "__main__":
    ph = sys.argv[1]
    if ph == "gen":
        j = evo.parse_json(evo.call("cv4_op60", P, prompt_text=P, meta={"stage": "center_v4"}))
        (evo.ROOT / "evaluations" / "centers" / "v4_op60.json").write_text(json.dumps(j, ensure_ascii=False, indent=1), encoding="utf-8")
        for o in j["options"]:
            print(o, center_v3.form_check(o) or "形式无问题")
        print("选中:", j["center"], center_v3.form_check(j["center"]) or "形式无问题")
    elif ph == "pool":
        j = json.loads((evo.ROOT / "evaluations" / "centers" / "v4_op60.json").read_text(encoding="utf-8"))
        centersel.OUT.mkdir(parents=True, exist_ok=True)
        p = [{"id": "H4", "center": j["center"], "src": "幸福·新谓语"},
             {"id": "H3", "center": "眼前的幸福与无法留住幸福的忧伤始终并存。", "src": "幸福·上一版"},
             {"id": "V2", "center": "对亲密的投入与自我克制始终相互牵制。", "src": "已通过"}]
        (centersel.OUT / "pool_op60.json").write_text(json.dumps(p, ensure_ascii=False, indent=1), encoding="utf-8")
        (centersel.OUT / "pool_op61.json").write_text("[]", encoding="utf-8")
        print(p)
    else:
        orig = evo.call
        evo.call = lambda rid, *a, **k: orig("v4" + rid, *a, **k)
        orig_out = evo.output
        evo.output = lambda rid: orig_out("v4" + rid) if rid.startswith(("csp_", "cfit_")) else orig_out(rid)
        body = open("centersel.py", encoding="utf-8").read().split('if __name__ == "__main__":')[1].replace("\n    ", "\n")
        body = body.replace('for w in ("op60", "op61"):', 'for w in ("op60",):')
        sys.argv = [sys.argv[0], ph]
        exec(body, {**vars(centersel), "sys": sys})
