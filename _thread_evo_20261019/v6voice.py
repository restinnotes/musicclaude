"""DAG N08 v3 (11-01): the surface is written from the graph as a list of MEANINGS, not re-said item by item.
User: "dag 不仅是你可以加后置层 还有可能可以修改已有的层的呀 … 开放评审认为没区别 那岂不就是啥也没干".
Diagnosis: N06 defines every item as "他此刻感到什么、想要什么、怕什么、做了什么、发现了什么" (= 他＋心理动词); N05/N06/N08 ask every
segment to state its cause; every later layer (N08 old, N09b, N09c, N10c) re-says item by item with count/order fixed and
"第三人称他". The writer always has the old sentence in front of him and one slot per item, so the template survives every
pass (the model imitates what it sees). Here: one call per work, the graph is given as meaning notes per segment; the writer
re-tells each segment freely (any number of sentences, any order inside the segment), causes may show through order, voice
is a parameter. ids vo_<w>_<out>.
  VOICE=he : third person, free sentence shapes (subject may be dropped, things / time / the thought itself may lead)
  VOICE=i  : first person, he tells it himself
usage: GLOSS_TAG=d0 VOICE=he python v6voice.py <base> <out>"""
import json, os, sys
import covjudge, evo, v6fix as V
from v6gen import build, gloss_text

VOICES = {
    "he": "用第三人称讲，但不要每句都从“他”起头、再接“想/怕/觉得/明白/知道”：汉语可以省掉主语；可以从那件事、从一段时间、从一个已经发生的结果说起；念头可以直接出现（半句自问也行），不必报告成“他想……”。",
    "i": "用第一人称“我”，由他自己讲：像他事后跟一个熟朋友说起这段经历，不是写日记、不是独白表演。念头直接说出来，不要“我意识到”“我明白了”这种报告句。另一个人一律叫“对方”，不要写成“他”“她”“那个人”“人家”，不给对方定性别。",
}

P = """下面是肖邦{NAME}的一条“线”：一个人在这首曲子里经历的一件事。它会和另一批人写的听感记录（珠子）放在一起读：珠子写此刻听到、感到的样子；线讲他自己的经历，把这些听感串起来。

【线的意思】按段列出（每段标了小节和他此刻与整件事的关系），每条后面的编号是这条意思的编号。注意：这些条目是一份“意思清单”，不是写法；句子要你自己组织，不要照清单的字面一条条翻成句子。

请把这条线重新讲出来：
1. {VOICE}
2. 每段的意思都要讲到（可以合并、换顺序、换说法），不加清单里没有的事件、人物、场景、对白；可能的不改成确定的，一时的感受不写成已经成立的认识。
3. 因果靠先后自然显出来就够了：前面已经讲过的经历，用几个字提一下即可；不要每段都“原以为……可……”“因为……所以……”地解释一遍，转折词（却、可、仍、又、还是）只在真有转折时用。
4. 句子要完整、有来有去，像人说话，不要为了省字压成电报式、文言式的短句（不写“怎办”“怎活”“似觉”这类缩略）；句子有长有短；不用格言、对仗、总结句，不用成语和比喻，不写声音、画面、身体感受。标“没在想”的段，就讲他沉在什么里，不替他想道理。
5. 每段写成两到四条（一条是一两句话），全文不超过 {N} 个字。每条的 cite 写它提到的更早段落里你写出的条目编号（第 1 段是 S01-1、S01-2……）。

【Center 各部分指什么】（这层意思要守住，不能改窄或换成别的事）
{GLOSS}

【线的意思】
{NOTES}

只输出 json：
```json
{{"segments": [{{"sec": "S01", "items": [{{"text": "……", "cite": []}}]}}]}}
```"""


def notes(g, sk=None):
    L = []
    for s in g["segments"]:
        L.append(f"## {s['sec']}（{s['bars']} 小节；{s.get('relation') or ''}）")
        L += [f"- {(sk or {}).get(it['id']) or it['text']}〔{it['id']}〕" for it in s["items"]]
    return "\n".join(L)


SKEL = """下面是一条“线”的条目（方括号里是编号）。请把每一条压成“要点”：只留下意思，不留句子。
- 要点用词组和箭头写，例如「怕说破→关系会变」「刚靠近：不自在，每近一点重拿分寸」；不写主语（不出现“他”“我”），不用“却、也、又、还、越、仍、可、便、就”这类虚词和连接词，不写完整句子。
- 意思一点不能丢：原因、对象、变化都要在；原文的限定要留（一时、仿佛、一度、还说不清、可能、隐约）；一条里有几层意思就写几个要点，用“；”隔开。
- 不加原文没有的东西。

{TEXT}

只输出 json：
```json
{{"notes": [{{"id": "S01-1", "note": "……"}}]}}
```"""


def skeleton(w, base):
    """{item id: note}; ids sk_<w>_<base> (Gemini 3.8: a conversion, not a judgement)"""
    g = V.graph_of(w, base); rid = f"sk_{w}_{base}"
    if not evo.done(rid):
        evo.call_gemini_direct(rid, SKEL.format(TEXT=chr(10).join(f"[{it['id']}] {it['text']}" for s in g["segments"] for it in s["items"])), meta={"stage": "v6-skeleton"})
    return {x.get("id"): x.get("note") for x in (V.parse(rid) or {}).get("notes") or []}


def run(base, out):
    voice = os.environ.get("VOICE", "he"); writer = os.environ.get("VOICE_WRITER", "argon")
    def piece(w):
        g = V.graph_of(w, base); C = sum(len(i["text"]) for s in g["segments"] for i in s["items"])
        rid = f"vo_{w}_{out}"
        if not evo.done(rid):
            msg = P.format(NAME=covjudge.NAME[w], VOICE=VOICES[voice], N=int(C * float(os.environ.get('VOICE_LEN', '0.65')) // 100 * 100), GLOSS=gloss_text(w), NOTES=notes(g, skeleton(w, base) if os.environ.get('VOICE_SKEL') else None))
            if writer == "argon":
                evo.call_argon_direct(rid, msg, meta={"stage": "v6-voice", "voice": voice})
            elif writer == "gem":
                evo.call_gemini_direct(rid, msg, meta={"stage": "v6-voice", "voice": voice})
            else:
                evo.call(rid, msg, model=evo.G6, meta={"stage": "v6-voice", "voice": voice})
        G, kept = build(w, base, out, V.parse(rid) or {})
        T = [i["text"] for s in G["segments"] for i in s["items"]]
        print(w, out, voice, "条目", len(T), "字数", sum(map(len, T)), f"（原 {C}）", "没写出的段", kept, flush=True)
    evo.run_parallel([(w, (lambda w=w: piece(w))) for w in ("op60", "op61")], 2)


if __name__ == "__main__":
    run(sys.argv[1], sys.argv[2])
