# Prompt versions

All templates take {WORK_SHORT} and {SEG} from works/<work>/segmentation.json (seg.py). P0 rendered with seg style
`orig` is byte-identical to the user's P0. Style `ranges` renders explicit closed bar ranges (fixes the "117 is a bar" misreading).

| version | change vs P0 (one variable each) | hypothesis (failure mechanism) |
|---|---|---|
| P0 | — (user's original) | baseline |
| P1 | + pacing paragraph: not every segment needs a new insight; let experience dwell; no habitual insight/"still not enough" endings | P0's list of "理解的内容" examples is read as a per-segment quota → every section ends in a declared realization (F7/F2) |
| P2 | + private comparison of candidate "难以安顿的事" against this piece's own events before writing | all samples collapse onto one generic center (water flows / happiness can't be kept), a template not derived from the music (F6) |
| P3 | + each segment's feeling starts from an audible event in that segment, then why it feels so given history | reasons drift into story logic detached from the music; music descriptions become decoration |
| M1 | GPT-6 mutation (run mut_m1_1, plan 1): rewrite the "理解的内容" examples into a non-quota definition; closing allows dwelling | F7 quota |
| M2 | GPT-6 mutation (mut_m1_2, plan 2): Connection/Inner may show relations through experience, explain only when needed; closing rewritten + "只输出文章正文" | F3 author-explains, F2 |
| M3 | GPT-6 mutation (mut_m1_2, plan 3): Center emerges through experience, not an opening thesis; examples framed as possibilities; closing rewritten + "只输出文章正文" | F2 thesis-first |
| P0o | P0 + "只输出文章正文。" only | ablation: is M2/M3's gain just the output-only line? |
| Q1 | M3 + M2's Connection/Inner + "理解要足够清楚，但不必把每件事都解释出来" | combine the two best mutations |

Segment clause styles: `orig` (user's list incl. right edge), `note` (orig + "最后一个数只是全曲结束的边界，不是一个小节；全曲共N小节"),
`ranges` (explicit closed ranges). J2+J3: ranges clearly worse (6 samples, all 3 judges); note ≈ orig and removes the 117 misreading.
| Q2 | Q1 + P1's pacing paragraph | F7 still the top FP for the Q1 family (J4) |
| R1 | GPT-6 mutation of Q1 (mut_m2_2 plan 1): drop the five example bullets; "understanding may arrive late"; closing no longer says "不断得到更准确的理解" | F7 |
| R2 | GPT-6 mutation of Q1 (mut_m2_1 plan 2): reasoning may stay implicit, but the concrete grounds of a key turn may not be omitted | F3 (reported change instead of shown change) |
| R3 | GPT-6 mutation of Q1 (mut_m2_2 plan 3): the trouble is made of specific conditions and later events may change the trouble itself | F6 template themes |
| P0g | P0 + one line: emotion reasons come from what happens in this segment's music plus prior experience; do not invent events, dialogue or objects to drive emotion | user 10-20: invented plot = wrong (B) |
Material D3s = D3 with a one-paragraph note: string the beads (relations between them), do not retell them in order | user 10-20: bead copying = wrong (C) |

## Round E1 (10-20, behavior-steering batch; see exp.py)
Bases: C4 = P0 + bead-derived Center #4 + D3; C6 = P0 + Center #6 + D3; PD = P0 + D3.
Variants (one change each): X1 last line "让读者在经历中感到……而不是听你解释"; X2 first-person monologue; X3 no-explaining rule
(+ let earlier things return concretely); X6 whisper-to-listener; X7 ≤150 字/段; X4 plan→write two-stage; X8 critique→redraft.
Hypothesis: P0's last line ("合理化…即为什么…") drives the explanatory essay voice found in every source.

## Round E2/E3 (10-21)
E2 = X2 (first-person monologue) combined with X3 (no explaining) and/or X6' (each segment starts from the sound heard now), plus X2 written by GPT-5.6 / Gemini.
My reading: C6 + X2X3X6 best so far (concrete first-person body experience, almost no explanation, line carried by experience); Gemini X2 vivid but occasionally overwrought; PD + X2 drifts into invented memories.
E3 = X2X3X6 over all six bead-derived centers + PD, written by GPT-6 and Gemini (2 each).
