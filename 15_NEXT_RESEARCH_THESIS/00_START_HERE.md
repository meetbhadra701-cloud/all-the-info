# 15 — Next research thesis: start here

**Decision (2026-09-28): NO NEW THESIS READY.** Four candidates were generated, screened and tested against pre-registered criteria. None survived. The strongest near-miss and the one experiment that would decide it are below.

This folder is the Phase B investigation of the transition run. UBP is closed (`../14_FABLE_5_1_SCIENTIFIC_DISCOVERY/22_UBP_PROJECT_CLOSEOUT.md`). The process followed `../SUPPORTING_ARTIFACTS/NEXT_THESIS_RESEARCH_RULES.md` and used `../SUPPORTING_ARTIFACTS/research_harness/`.

## What was done

1. **Frontier scan** (01). Twenty-six searches; access was limited to summaries and GitHub. The archive's own register (about 45 probes, TRACE, Waves 10–11) served as the exclusion set.
2. **Four candidates**, each with the full P → L → M → B → E → F → C tuple (02):
   - **XACC:** exact accumulation for bounded-scale block formats;
   - **XABFT:** threshold-free SDC detection;
   - **MR-SIGNOFF:** oracle-free metamorphic testing of open sign-off tools;
   - **LIN-CEC:** linear-algebraic CEC for XOR logic.
3. **Proximity and reflection** (03). LIN-CEC was killed as occupied, and XABFT was merged into XACC.
4. **Pre-registration** of every cheap evaluator (04 Part 1, commit `967661a`) before any data.
5. **Evaluators run** (04 Part 2). Numerics, full SKY130 physical implementation with extracted three-corner sign-off, metamorphic sign-off tests and an ABC screen.
6. **Prosecution** (05), decision (06, 07) and next experiment (08).

## Results in one table

| Candidate | Decisive test | Outcome |
|---|---|---|
| **XACC** | E1b: is IEEE-FP32 accumulation of NVFP4 GEMMs order-sensitive in practice? | **KILLED.** Order-invariant for ≥ 99.9% of outputs on every pre-registered data regime, because FP32 accumulation of NVFP4 block contributions is effectively *exact* there |
| XACC (cost; cannot revive the kill) | E2: exact vs three FP32 accumulator PEs (IEEE RNE, truncating, pipelined with two interleaved accumulators), SKY130, extracted tt/ss/ff, post-route verified | **PASS with structural headroom.** A×T_ss ratio **0.738** against the strongest FP32 design (0.929 even with one readout converter per PE). The exact PE is 23% smaller, and its loop (3.2–4.0 ns at tt) is 2.3–2.9× shorter than the FP32 loops |
| XABFT | Merged; depends on XACC's premise | **KILLED with XACC** (E3 not run; deviation D2) |
| **MR-SIGNOFF** | Metamorphic invariance of OpenRCX + OpenSTA | **KILLED.** Exactly invariant under rerun, DEF permutation and full renaming on two routed designs (13,126 and 506 nets) |
| **LIN-CEC** | Proximity (occupied), plus an ABC screen | **Killed as a thesis.** The tool gap is real (ABC `cec` / `&cec` > 70 s vs 0.02–0.23 s for GF(2) matching on CRC-32), but the method is published: engineering |

## The strongest near-miss (06)

A post-hoc diagnostic (not decisive) found a **sharp phase transition**:
- FP32 accumulation of NVFP4 block contributions is exact, hence order-free, while the within-row block-scale exponent span stays at about 9 binades or less;
- it is order-sensitive in about 100% of outputs once the span reaches about 12–13 binades (outliers of 1000× or more).

LLM "massive activations" can reach that regime unless rotations flatten them. In that regime, a 60-bit exact accumulator (E1a: the smallest exact width for NVFP4 / UE4M3) makes GEMMs bitwise order-free by construction. The pre-registered physical cost test (E2) came out **cheaper, not merely free**: 0.738× the A×T of the strongest FP32 accumulator at the slow corner, on real SKY130 layouts. The cost half of the near-miss is therefore settled at PE level.

**Missing evidence:**
1. Whether real NVFP4 recipes on real LLMs cross the transition (08). This needs model weights, which cannot be reached here.
2. Whether vendor tensor cores already accumulate NVFP4 blocks exactly (full texts blocked).
3. An array-level cost that includes accumulator storage, plus comparison against a vendor-style fused multi-term FP accumulator (not implemented here).

## Read in this order

| File | Contents |
|---|---|
| `06_PRIMARY_THESIS.md` | Why there is no primary, and the near-miss in the required final form |
| `04_CHEAP_EVALUATORS.md` | The pre-registration (Part 1) and every result (Part 2) |
| `08_NEXT_EXPERIMENT.md` | The one experiment that decides the near-miss (proposed, not started) |
| `05_PRIOR_ART_PROSECUTION.md` | Known ingredient / equivalent / obvious / distinct, per candidate |
| `01_FRONTIER.md`, `evidence/search_log.md` | The September-2026 frontier and every source |
| `02`, `03` | Candidates and proximity / reflection / ranking |
| `07_RESERVE_THESIS.md` | No reserve; LIN-CEC recorded as engineering |
| `RESEARCH_STATE.md`, `experiments/README.md` | State; how to reproduce |

## How the UBP lessons were applied

| Lesson (`../14_FABLE_5_1_SCIENTIFIC_DISCOVERY/24_LESSONS_FOR_NEXT_THESIS.md`) | Applied here |
|---|---|
| Strongest baseline from day one | XACC's physical test used three FP32 accumulators (IEEE RNE, truncating, pipelined with two interleaved accumulators) through the same flow |
| Physical costs early | Real cells, flow sizing, OpenRCX extraction, the ss corner and post-route functional verification in the first evaluator |
| Pre-register decisive tests | `967661a` precedes every result (audited) |
| Independent validation | Our own AIG simulator, exact goldens cross-checked with numpy, and mutants detected on every design |
| No rescue loops | XACC's post-hoc regime finding is recorded as a near-miss and a new study, not as a result |
| Close failed candidates cleanly | Four kills, each with its evidence |
