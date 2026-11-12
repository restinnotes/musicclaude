---
name: thread-node-no-beads
description: 10-21 user — in the main DAG the Thread node sees NO bead information at all (not even a bead-derived Center); beads enter only at the later align/assemble nodes
metadata:
  type: feedback
---

User (2026-10-21): the layered DAG is: segmentation → [beads] and [Thread written with zero bead input] → align → assemble (inject beads) → compress. Deriving the Center from beads injects beads before the Thread. That makes it a completely different path, with a different DAG that no longer needs the later injection. That path is secondary. Do route A (no beads at node 2) first.

**Why:** the layering (line and beads produced independently, then joined) is the point of the DAG; passing beads in early collapses it.

**How to apply:** Optimize node 2 with no bead-derived inputs: P0 + segmentation, centers the model proposes itself, a tournament, and so on. Report bead-informed variants only as a separate alternative path, never as "the" Thread. Related: [[thread-staging]], [[thread-needs-own-logic]].
