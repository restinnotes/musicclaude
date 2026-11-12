"""10-29 (user: "就只需要让他通读这篇对话记录 然后根据最后的继续审查zip包就行 不要加太多提示词"). Before calling the user,
gpt3 (gpt-6 and 5.6, max) reads the user's ChatGPT review conversation (reviews/) and, continuing from its last part, reviews
this round's zip. Both "大致通过" -> call the user; otherwise keep working on what they point at.
ids: gate_<tag>_g6 / gate_<tag>_g56.  usage: python gate_review.py <tag> <zip> -> reviews/交付前评定_<tag>.md"""
import glob, sys
import evo, node2b

CHAT = sorted(glob.glob(str(evo.ROOT / "reviews" / "chatgpt-*.md")))[-1]      # newest export the user gave
ASK = ("附件一是我和 ChatGPT 关于这个项目的对话记录，请从头到尾通读，尤其是最后对上一个包的评审。"
       "附件二是这一轮新出的包。请接着对话最后的思路审查这个包，说清楚：上次指出的问题修好了没有，有没有新问题，能不能交给我。"
       "不必完美，大致过关就行。最后单独一行写“结论：大致通过”或“结论：不通过”。")


def main(tag, zp):
    jobs = [(rid, (lambda rid=rid, w=w: evo.call(rid, ASK, prompt_text=ASK, model=evo.G6 if w == "g6" else evo.G56,
                                                    meta={"stage": "gate", "attach": [CHAT, zp]})))
            for w in ("g6", "g56") for rid in [f"gate_{tag}_{w}"] if not evo.done(rid)]
    evo.run_parallel(jobs, 2)
    out, ok = [f"# 交付前评定：{tag}", "", f"对话记录：{CHAT}", f"包：{zp}", ""], []
    for w in ("g6", "g56"):
        r = evo.output(f"gate_{tag}_{w}") or "（没有返回）"
        ok.append("结论：大致通过" in r.replace(" ", ""))
        out += [f"## {'gpt-6' if w == 'g6' else 'gpt-5.6'}", "", r, ""]
    (evo.ROOT / "reviews" / f"交付前评定_{tag}.md").write_text("\n".join(out), encoding="utf-8")
    print("两位都大致通过" if all(ok) else f"没过：{ok}", flush=True)


if __name__ == "__main__":
    main(*sys.argv[1:3])
