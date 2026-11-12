---
name: p0-core-concepts
description: "The P0 constitution concepts (Center, History, Connection, Inner, Outer + the five kinds of accumulated understanding) must be carried into every Thread design, judge and schema"
metadata:
  node_type: memory
  type: feedback
  originSessionId: 7c623294-a1ea-40eb-b513-ae6588ad2c39
  modified: 2026-10-21T22:52:40.041Z
---

User (2026-10-21): "一个核心概念 center history 等 我们初版提示词里有的那些 都要记住 你这上面就似乎漏了 center？"

P0 definitions:
- **Center:** the shared trouble. What matters to the person, and what makes it hard to settle. **It does not preview the course of development or the final answer.**
- **History:** the grounds actually obtained by now. Which joys happened, which expectations were rewarded, which difficulties have surfaced, which needs remain.
- **Connection:** says the relation out loud. How one experience **explains, limits or shakes** another, or **gives a reason** for the present response.
- **Inner:** the person's situation, wants, reasons and costs, said in plain words.
- **Outer:** the same relation happening in a perceivable action or situation. In route A this is mostly carried by beads.
- **Accumulated understanding:**
  1. two demands squeezed together get separated;
  2. a method that really gave something shows what it can't handle;
  3. a reasonable choice carries a cost that can't be ignored;
  4. a full satisfaction makes what is still unsatisfied clearer;
  5. knowing more can make the trouble sharper, not solved.
- Thread is the core; the rest are tools.

**Why:** I kept designing schemas and prompts from my own vocabulary and dropped Center. My center lines also previewed the ending ("最终带着尊严与怀念走下去"), which violates P0.

**How to apply:**
- Every schema and judge must map these concepts explicitly:
  - a Center node, linked from each segment;
  - History items tagged by kind;
  - Connection relations using P0's own verbs;
  - Inner node types (wants / reasons / costs);
  - the accumulation kind on realizations.
- Check that the Center doesn't preview the route or the answer.

- 10-21 user: Centers must be typical and convincing for the piece. Derive them from the 24 A drafts' whole-piece readings: cluster them and keep only the 2–4 with the widest independent support. Don't ask for "mutually different" candidates and don't pad with fringe angles; my research-tournament Centers felt off for exactly this reason. Judges need a "does this Center fit the piece" check.
- Center FORMAT (settled in 09-21/22 dialogues, reconfirmed 10-14 and 10-19; recovered 10-21 by a Haiku search):
  - the **minimal complete relation sentence**: subject (one or more objects, as noun phrases) + predicate (how they relate), holding from early on to the end;
  - no later changes or answers; no relation-type menu; don't default to conflict, but state the conflict if there is one;
  - two bare nouns ("行动 / 内在牵动") were explicitly rejected by the user as insufficient;
  - no person/action phrasing ("他想……却……" is padding).
  - Example: "向外行动与向内牵动都要求成立，却彼此牵制。"

- Center per segment (10-21, from the 09-20/21 dialogue): every segment responds to the one Center, but it need not touch it explicitly or advance it. Each segment is 还说不清 / 正在面对 / 没在想 (no quota). The opening may be cloudy. Never force a menu like 触及/分化/加深/松动, and never use visibility words (显性/潜伏) — that is the old SHOW/HOLD/SILENT drift. Judge clause: penalize 强行挂靠 and 开头说死.

Related: [[thread-structured-output-and-advisor]], [[thread-needs-own-logic]], [[thread-spec-doc]].
