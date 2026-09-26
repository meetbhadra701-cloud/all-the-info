# 00 — Executive summary (Wave 10: experimental-first discovery)

**Bottom line.**
- **No candidate advances to research development.**
- Two decisive, pre-registered experiments were run to completion:
  - **C1 (MappingEvolve, LLM-evolved technology mapping): KILLED.**
  - **C6 (OpenROAD search-based resynthesis): KILLED.**
- C2 (GT2N multi-Vt usage) is ENGINEERING ONLY.
- C4 (Dynamatic MILP) and C5 (emap in OpenROAD) are UNRESOLVED, blocked by tooling or licences.
- C3 and six further screening candidates were killed as occupied.
- Nothing was fabricated to produce a survivor.

Evidence labels: OBSERVED (we ran it), PAPER, INFERRED, UNVERIFIED. All third-party code ran in a network-off container, and no LLM API was called.

## Prior conclusions accepted

- Investigation 11 (TRACE/Yosys) stays **ENGINEERING ONLY** and was not reopened.
- Waves 8/9 are not recoverable locally (their `RECOVERY_NOTE.md` files).
- The handoff and both Opus reports were internalized. Session 1's audit finding shaped the method: execution finds things that desk review misses, and occupation happens faster than one research cycle.

## C1 — the decisive experiment of this wave (details: 04 §2–6)

**Object.** MappingEvolve (arXiv 2604.26591; MIT artifact @308f5cc). Its claim: LLM-evolved mockturtle mapping operators give "10.04% area reduction versus ABC and 7.93% versus mockturtle" on EPFL, with 0 equivalence failures.

**Documented case reproduced first (OBSERVED).**
- The ISCAS85 rewards of all three released evolved mappers match `reward.json` exactly.
- The paper's EPFL table reproduces 20/20 for mockturtle and 20/20 for GPT-5 it29.
- The DeepSeek column is reproduced by *no* released DeepSeek operator state (all 5 distinct states scanned; best 3/20, which is the initial mapper). That is a provenance gap.

**Decisive experiment D1.** Pre-registered, 53 circuits × 35 configurations = 1,855 netlists. Every netlist was independently re-timed, simulated against the original AIG, and CEC'd from our own translation. All pass.

| geomean A_evolved / A_best-baseline at the evolved mapper's own delay | GPT-5 it29 | DeepSeek it24 | Qwen it20 |
|---|---|---|---|
| EPFL-20 (the paper's suite) | 1.050 (5/20 wins) | 1.044 (3/20) | 1.075 (1/20) |
| IWLS05-22 (held out) | 1.073 (3/22) | 1.076 (3/22) | 1.108 (1/22) |

The kill condition (≥ 0.99) is met for all three. The best baseline is usually mockturtle's own `emap`, from the same library and commit, which the paper did not compare against.

**What the headline actually was.**
- Against ABC, GPT-5's EPFL area gain is *entirely* delay relaxation: 0.9496 = 0.9537 (relaxation) × 0.9957 (operator).
- Current `&nf` defaults give 5.2% *less* area than the paper's ABC column, at identical delays on 17/20 circuits. Against current `&nf`, the "10.04%" becomes 5.1%.

**Cause isolation (D2, pre-registered).**
- One evolved *delay-round* acceptance rule is necessary and sufficient for GPT-5's whole effect. Grafted onto the initial operators alone, it reproduces GPT-5 within 0.13%. Removing it restores the initial mapper within 0.25%.
- The two area-round edits are inert.
- The rule's non-relaxation part (≈3.6% at iso-delay) is real, but smaller than what emap already delivers.

**Contribution test (03).** It fails for A–E. Iso-delay evaluation, the stronger baseline and multi-objective LLM evolution (MEoH, AAAI'25) are all established.

## C6 — the next candidate after C1 died (details: 04 §7)

**Object.** OpenROAD mainline `resynth_annealing` / `resynth_genetic`: SA/GA search over ABC scripts for worst slack. The published example is AES/ASAP7 WNS −30.92 → +20.59 ps, with no baseline.

**Result (OBSERVED, placed ORFS asap7/aes, defaults).** All 8 search runs made timing **worse than doing nothing**.
- Start: −29.38 ps.
- `resynth_annealing` (5 seeds): −88.8 to −141.2 ps. `resynth_genetic` (3 seeds): −117.1 to −123.5 ps.
- Standard `repair_timing -setup` reaches −5.5 ps in 5 s.
- Running annealing before repair leaves the result 10.3 ps worse than repair alone.
- The tool applies its best-found script even when it is worse than the untouched netlist.
- All 19 treated netlists are functionally equivalent: the commands are correct but harmful by default.

The published example used an unplaced test netlist. It is **not reproduced** in the analogous unplaced setting on our AES netlist: 3/3 seeds end 3.6–21.1 ps *worse* than their −59.3 ps start, against the blog's +51.5 ps gain. **KILLED on F1**; the residual is an engineering bug report.

## Engineering findings (not contributions; nothing has been sent anywhere)

1. **MappingEvolve critique package.** Iso-delay tables, the emap baseline, the ABC-baseline discrepancy and the DeepSeek-column provenance gap. It could go to the authors if you choose.
2. **OpenROAD rmp.** Search-based resynthesis regresses placed designs and lacks a do-no-harm check. This is an issue you could file.
3. **ABC (ORFS image).** `&nf -D` is a no-op, and `&nf -R` is inert on div/hyp/sqrt.
4. **mockturtle `map`/`emap`.** 2.5× / 1.7× ABC's inverter count on IWLS05 (vga_lcd ≈ 10×). This matters now that emap is entering OpenROAD.
5. **ORFS.** `kepler-formal` LEC SIGILLs on non-AVX-512 CPUs, so flows need `LEC_CHECK=0`.

## What this wave says about the search (recommendation)

- Experimental-first discovery worked *as a method*. Both decisive experiments produced crisp, reproducible, pre-registered verdicts within a day, and C1 recovered the exact published numbers before overturning the claim.
- What execution keeps finding in recent, fast-moving claims is **evaluation defects with known remedies**, not open technical problems. That is the third consecutive session with this pattern.
- **Recommendation:** if the goal stays "a publishable contribution", the only direction this wave left genuinely untested is **evolving from the strongest mapper (emap) with iso-delay/Pareto selection** (05 §"What would be required"). It needs your authorization for LLM API spend. Everything else examined is occupied or blocked.
- Alternatively, the critique and reproduction packages above are concrete, low-cost outputs with community value. They are engineering, not research.
