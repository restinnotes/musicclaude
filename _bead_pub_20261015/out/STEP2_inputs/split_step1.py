# -*- coding: utf-8 -*-
"""机械拆分 STEP1_response_raw.md 为 7 个来源独立文件 + 任务指令正文。
只做机械切分，不改一字（除文件头尾空白处理），UTF-8 无 BOM。
用法: python -I split_step1.py
"""
import re, hashlib, sys

SRC = r"D:\musicclaude\_bead_pub_20261015\out\STEP1_response_raw.md"
OUTDIR = r"D:\musicclaude\_bead_pub_20261015\out\STEP2_inputs\attach"
TASK = r"D:\musicclaude\_bead_pub_20261015\out\STEP2_inputs\STEP2_via_attach.txt"

with open(SRC, "rb") as f:
    raw = f.read()
text = raw.decode("utf-8-sig")

heads = ["### S1", "### S2", "### S3", "### S4", "### S5", "### S6", "### S7"]
idx = []
for h in heads:
    p = text.find(h)
    if p < 0:
        print("MISSING HEAD: " + h, file=sys.stderr)
        sys.exit(1)
    idx.append(p)

# S7 结束于 "## 二、" 之前
end7 = text.find("## 二、")
if end7 < 0:
    print("MISSING SECTION 二", file=sys.stderr)
    sys.exit(1)

import os
os.makedirs(OUTDIR, exist_ok=True)
names = ["S1.md", "S2.md", "S3.md", "S4.md", "S5.md", "S6.md", "S7.md"]
for i, nm in enumerate(names):
    s = idx[i]
    e = idx[i + 1] if i < 6 else end7
    chunk = text[s:e].strip("\r\n") + "\n"
    p = os.path.join(OUTDIR, nm)
    with open(p, "w", encoding="utf-8", newline="\n") as f:
        f.write(chunk)
    h = hashlib.sha256(chunk.encode("utf-8")).hexdigest()
    print(nm, len(chunk.encode("utf-8")), h)

task = """【通用提示词：整理已有结构来源的层级，不独立分句】

作品：肖邦《船歌》升F大调 Op.60（单首作品，无乐章划分）
Chopin – Barcarolle in F-sharp major, Op. 60

7个来源见附件S1-S7（S1=Rink 1988，S2=朝山奈津子/PTNA 2008，S3=Gerling 2014，S4=Damschroder 2015，S5=Kopp 2014，S6=Aziz 2015，S7=Chaffin等 2024）。请按附件原文逐来源整理。

用户已经明确指定的分段层级/来源（如无则为 NONE）：NONE（用户未指定采用哪套）
历史实验切点（只用于提取完成后的对照，可以为空）：历史对照（仅对照，绝不得作为采用依据，不得修改文献边界）：run102历史实验九段切点 1-3/4-16/17-34/35-39/40-61/62-77/78-83/84-102/103-116，仅用于STEP2文献提取完成后的对照比较，不得作为候选结构采用依据，不得据此修改任何文献来源的边界。另EXAMPLE_来源层级说明.md中的旧五段1-34/35-71/72-83/84-102/103-116为反面例子（系既往自合并产物，非文献结论），明确禁止冒充文献结论，禁止将其写成任何来源的文献分段。

你只负责解释不同**已有来源**为什么粗细不同，并提供一份有原文证据的分段选择。你不能阅读谱面、播放录音、自己做曲式/听觉判断、创造第三套切点。

- 如果一个来源明确提供“大部—主题—局部小段”的层级，忠实列出每一级及对应边界。不要把“同一大部”擅自解释成“一次自然换气”。
- 多来源分歧时，优先说明是同一段的不同**层级**，还是明确边界冲突。没有证据就不宣称同义或优越。
- 选择供 Bead Pool 使用的层级必须引用某份**确实存在的**来源划分（或用户指定的历史方案），不能把不同层级混合拼造一套然后宣称来自某论文。
- 不得以“越粗越完整、避免5小节碎珠”为由，抹除来源中明确存在的独立过渡段；也不得因为条目多就全都升为 Bead。
- 不能为了用户偏好“九段左右”凑出九段。若明确文献只有5段或14段，则呈现5段/14段及它们的层级，必要时交用户选。
- 作品、乐章各自的实际分段数可以不同；原始来源没有的内容必须明确标 NOT_SUPPORTED。
- 首次测试如有两份不同粒度，**先停在这里把两套完整表交用户看**，确认选哪套才生成 A Pool 和 Bead。

输出要求：
1. 来源对照表（7来源各自的层级与边界，忠实原文）；
2. 可直接采用的候选结构（每套都指向具体来源原文，不得拼造）；
3. 小节编号冲突说明；
4. 是否已有用户授权采用一套（本轮为 NONE，未授权）；
5. 结构映射 JSON（每套候选的来源依据与边界映射）；
6. 最后一行给出 READY_FOR_POOL=true 或 READY_FOR_POOL=false。无明确采用依据时 `READY_FOR_POOL=false` 并停机；不得由 Claude 以主观“听觉上五段更好”自行宣布结构通过。

补充说明：dramatic/assertive/single-story 的写作风格不是缺陷，不得因此扣分或否定任何来源。
"""
with open(TASK, "w", encoding="utf-8", newline="\n") as f:
    f.write(task)
print("TASK", len(task.encode("utf-8")), hashlib.sha256(task.encode("utf-8")).hexdigest())
