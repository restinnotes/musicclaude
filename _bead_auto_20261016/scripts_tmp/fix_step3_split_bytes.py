# -*- coding: utf-8 -*-
"""Fix STEP3 review split: A prompt exceeded the gpt2 native byte cap
(A failed pre-submit at 67,003B httpB; B PASSED at 60,111B -> cap sits in
60k..67k). Byte size, not codepoint count, is the binding gate.
Self-consistent carve of the EXISTING on-disk prompt A:
  1. split A into [preamble | case blocks | tail] at structural markers;
  2. move case blocks from the tail of A into a NEW prompt C (same preamble,
     same output-spec tail) until A <= 59,500 bytes on disk;
  3. minimally reword the part-count strings (1/2 -> 1/3, 3/3);
  4. hard-verify written byte sizes; B is never touched.
Union check: moved cases existed only in A, so A/B/C verdict sets stay
disjoint and cover all cases.
"""
import os, re, sys
sys.stdout.reconfigure(encoding="utf-8")

D = r"D:\musicclaude\_bead_auto_20261016\out\STEP3_inputs"
A_P = os.path.join(D, "STEP3_review_prompt_A.txt")
B_P = os.path.join(D, "STEP3_review_prompt_B.txt")
C_P = os.path.join(D, "STEP3_review_prompt_C.txt")
BUDGET = 59500
TAIL_MARK = "输出（只能输出一个"
HEAD_MARK = "===== "

txt = open(A_P, encoding="utf-8").read()
if not os.path.isfile(B_P):
    print("B prompt missing — nothing to preserve"); sys.exit(3)

# ---- carve ----
ti = txt.index(TAIL_MARK)
tail = txt[ti:]
head_zone = txt[:ti]
ci = head_zone.index(HEAD_MARK)
preamble, rest = head_zone[:ci], head_zone[ci:]
blocks = []
pos = 0
while True:
    nxt = rest.find(HEAD_MARK, pos + len(HEAD_MARK))
    if nxt < 0:
        blocks.append(rest[pos:])
        break
    blocks.append(rest[pos:nxt])
    pos = nxt
n0 = len(blocks)

# ---- move tail blocks until under budget ----
def total_bytes(blocks, preamble, tail):
    return len((preamble + "".join(blocks) + tail).encode("utf-8"))

moved = []
while total_bytes(blocks, preamble, tail) > BUDGET:
    moved.insert(0, blocks.pop())
    if not blocks:
        print("A emptied — corpus too big for one lane"); sys.exit(4)

# ---- part-count rewording (own scaffold strings, not A-pool text) ----
def reword(s, n):
    s = s.replace("分片 1/2", "分片 %d/3" % n)
    s = s.replace("两个分片互不重叠", "三个分片互不重叠")
    s = s.replace("另一片不知情", "其他分片不知情")
    return s

preA, preC = reword(preamble, 1), reword(preamble, 3)
outA = preA + "".join(blocks) + tail
outC = preC + "".join(moved) + tail
bA = len(outA.encode("utf-8")); bC = len(outC.encode("utf-8"))
if bA > BUDGET or bC > BUDGET:
    print("post-check over budget: A=%d C=%d" % (bA, bC)); sys.exit(5)

open(A_P, "w", encoding="utf-8").write(outA)
open(C_P, "w", encoding="utf-8").write(outC)

# ---- verify on disk ----
for p, tag in ((A_P, "A"), (C_P, "C"), (B_P, "B")):
    b = len(open(p, "rb").read())
    print("%s bytes=%d" % (tag, b))
print("cases: A=%d moved_to_C=%d (from %d)" % (len(blocks), len(moved), n0))
print("C case ids: " + ", ".join(x.split("\n", 1)[0][:40] for x in moved)[:500])
# B untouched marker
print("B raw still present:", os.path.isfile(os.path.join(D, "step3_review_raw_B.json")))
