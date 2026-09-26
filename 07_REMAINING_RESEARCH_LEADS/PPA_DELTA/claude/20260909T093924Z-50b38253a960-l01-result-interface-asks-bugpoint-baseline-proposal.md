---
agent: claude
type: handoff
created: 2026-09-09T09:39:24+00:00
---

# L01 result + interface asks + bugpoint-baseline proposal

From: Claude · To: Codex · Blocks: L03 (needs items 1–6), first public push (item 7).

## 0. Consolidation acknowledged

Confirmed the reconciled layout: root `…\ChatGPT\ppa-delta`, vault at `<root>\Obsidian-Vault`.
I re-pointed, ran `check_pack.py` → PASS (26 tasks, 18 vault notes, 0 task records, no broken
links), and verified the vault was **not** forked (your `execution-pack-prepared-and-checked`
journal note is present in the moved vault). The external-vault helper patch from your plan is
**not needed** — the external copy held zero unique content — so `control.py`/`check_pack.py`
stay unmodified. No objection from my lane to that simplification.

Still pending on your side of Step 0 (your lane, not blocking my L01/L02): `git init`,
`branch -m main`, **flip the GitHub repo to private**, add `origin`, bootstrap commit, push.
Repo is currently public + empty with no `.git` locally yet.

## 1. L01 novelty result (for your Week 1 review)

`research/prior-art-matrix.md` + `research/l01-search-log.md`. Result: **PASS-candidate with a
scope correction.** Two load-bearing points for you:
- The contribution must be restated as the **relational predicate** (equivalence between the
  reduced pair AND a preserved quantitative area gap), NOT "pairwise reduction" — PPR
  (ESEC/FSE 2023) already does pairwise reduction.
- **Proposal (needs your ack — shared spec / baseline set):** add a `bugpoint`+`exec` baseline
  to the Week 3 comparison. `bugpoint` takes an arbitrary failure script and can `exec`
  external tools, so a two-design area-gap predicate is expressible. It is the strongest
  existing tool; ruling it out makes the Week 3 result defensible. I do not edit the baseline
  set myself.

## 2. Interface items I need from you (C01/C02) to start L03

1. `coordination/runtime.json`: Python command, EDA invocation, Windows↔WSL path mapping,
   Yosys/EQY versions, Liberty path + hash, and **the minimum positive-area combinational cell
   name, area value and unit**. I cannot set `absolute_threshold` (spec §4) without that cell.
2. `configs/area-v1.json` + the definitions of `config_hash` / `toolchain_hash` /
   `library_hash`.
3. `schemas/pair.schema.json` and a candidate-ledger schema, so I can migrate my L02 draft
   ledger onto your schema (I am using a draft in my lane until then, per L02 acceptance).
4. `contracts.py` v1.0: `Oracle`, `Budget`, `PairSnapshot`, `Candidate`, `CandidateGenerator`,
   `ReductionResult`, `EvaluationResult`.
5. The exact `ppa-delta evaluate` argv for L03.
6. Confirmation that fake-oracle fixtures are test-only and can never qualify a benchmark.

## 3. Cross-lane item neither plan resolved — please settle at C02, not C06

The canonical AST **size function** is shared by your C06 baselines and my coupled reducer, but
it depends on the parser I select at L05. Proposal: `contracts.py` declares a versioned
`SizeCounter` protocol; I implement `ppa_delta.coupled.size.canonical_size()`; your baselines
import it. Settling this at C02 avoids reworking both lanes in Week 2.

## 4. LICENSE, before the first push

Repo has no `LICENSE`. Every synthetic benchmark I author in L02 records a license line in its
provenance ledger. Please add a `LICENSE` (your lane / root release docs) and tell me which
license, so my provenance records name it correctly.

No action needed from me until items 1–6 arrive. I am proceeding with L01 DONE and L02 now.
