"""F7 = F6 without the formula (user 10-21: F6 headlines sound like AI; overuse of 越…越). The F4 example sentence
('越怕被丢下，就越先把人推开') seeded the pattern, so: no example, named banned patterns, ask for natural speech.
Source = the concrete C1 prose. ids: fm_F7_<thread>_r<j>.  python fmt4.py count <id>... counts formula headlines."""
import re, sys
import arts, evo, node2b, plain

F7 = ("把下面这篇文章改写成极凝练的要点，不损失原文的关键因果。保留原来的分段标题。\n"
      "每段最多三行：\n"
      "第一行加粗：像一个懂人心的朋友，用平常说话的语气，直接点破他此刻怎么了——其实在怕什么、想要什么、在骗自己什么。"
      "句子可以很平淡，长短和句式要自然变化。\n"
      "第二行以“← 因为”开头：是前面哪一段的什么导致了它（一句）。\n"
      "第三行以“→ 于是”开头：它把他推向哪里（一句）。\n"
      "这一段没有新的变化，就只写第一行。\n"
      "不要用这些套路句式：“越……越……”“不是……而是……”“X 不等于 Y／不代表”“真正的……是……”“与其……不如……”，"
      "也不要写前后对仗、像格言或金句的句子——这些读起来像 AI。不要前言、总结、过渡和修饰。只输出改写后的内容。\n\n")
PAT = {"越…越": r"越[^。！？\n，,]{0,20}[，,]?[^。！？\n]{0,6}越", "不是…而是": r"不是[^。！？\n]{0,30}而是",
       "不等于/不代表": r"不等于|不代表", "真正": r"真正", "与其": r"与其"}


def count(n):
    t = arts.clean(evo.output(n)); heads = [h for h in re.findall(r"^\*\*(.+?)\*\*\s*$", t, re.M) if not re.match(r"^[\d（(第]", h)]
    hit = sum(any(re.search(v, h) for v in PAT.values()) for h in heads)
    return len(heads), hit, {k: sum(bool(re.search(v, h)) for h in heads) for k, v in PAT.items()}


if __name__ == "__main__":
    if sys.argv[1:2] == ["count"]:
        for n in sys.argv[2:]:
            print(n, *count(n))
        sys.exit()
    jobs = []
    for w, ts in plain.THREADS.items():
        for t in ts:
            src = arts.clean(evo.output(f"pc_C1_{t}_r1"))
            for j in (1, 2):
                rid = f"fm_F7_{t}_r{j}"
                if not evo.done(rid):
                    jobs.append(node2b.job(rid, F7 + src, {"stage": "fmt4", "variant": "F7", "thread": t}))
    evo.run_parallel(jobs, 4)
