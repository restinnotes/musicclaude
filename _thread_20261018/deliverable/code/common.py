"""Shared material renderers for the Thread experiment."""
import thr

SEGLIST = "；".join(f"{s} 第{thr.mm(s)}小节 {lab}" for s, (_, lab) in thr.SEGS.items())


def bead_block(seg, with_rel=True):
    d = thr.bead(seg)
    lines = [f"### {seg} · 第 {thr.mm(seg)} 小节（{thr.SEGS[seg][1]}）｜{d.get('title')}",
             f"读者正文：{d.get('reader', '').strip()}", "体验条目："]
    for b in d["beads"]:
        cond = f"（演奏条件：{b['performance_condition']}）" if b.get("performance_condition") else ""
        lines.append(f"- {b['id']}［{b.get('role')}｜{b.get('measures')}］{b.get('text', '').strip()}{cond}")
    if with_rel and d.get("relations"):
        lines.append("条目关系：" + "；".join(f"{r.get('a')}与{r.get('b')}：{r.get('type')}" for r in d["relations"]))
    return "\n".join(lines)


def beads_text(upto=None):
    segs = list(thr.SEGS)
    if upto:
        segs = segs[:segs.index(upto) + 1]
    return "\n\n".join(bead_block(s) for s in segs)


def t_zip():
    T = thr.load_T()
    assert len(T) >= 18 and not any(x in k.lower() for k in T for x in ("muse", "sol", "opus", "grok", "gpro")), sorted(T)
    return thr.zip_of("T_research", {f"T/{k}.md": v for k, v in T.items()})


def a_zip():
    A = thr.load_A()
    assert len(A) == 24 and not any("muse" in k.lower() for k in A)
    return thr.zip_of("A_sources", {f"A/{k}.md": v for k, v in A.items()})


MAT_T = (f"附件 `T_research.zip` 的 `T/` 里有 {len(thr.load_T())} 份独立的纵向聆听研究（文件名即来源 ID：每个模型各有不查资料的 int 版与查阅资料的 web 版，各 3 份）。"
         "它们直接讨论这首曲子从头到尾在处理什么、前面怎样改变后面。")
MAT_B = ("下面是这首曲子按 PTNA／朝山冻结十四段整理的当前体验（Bead）：每段是经过精选的体验条目，标明哪些可以同时成立、哪些是不同听法、哪些是段内变化或演奏条件。"
         "它们是每个时刻当前体验的依据；Thread 只能组织它们，不能改写它们。按音乐顺序给出。")
