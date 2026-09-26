# 07 — Final research decision

## Classification

**RESEARCH THESIS READY FOR INITIAL PROTOTYPE, conditional on a one-day full-text novelty check that this environment could not perform.**

- **The thesis** (`05_…`): in metal/via-programmable hardwired inference silicon, universal block-pattern generators (UBP-g) share accumulation *across neurons* while keeping every base layer weight-independent.
- **What it gives, for ternary/binary layers:**
  - exactly about g× fewer accumulation adders than today's per-input fabrics (the ratio is independent of W);
  - it is provably port-optimal (Theorem 1);
  - it measures within 1.22–1.37× of the strongest weight-specific CSE (da4ml), which cannot be used in that regime at all.
- **The condition:** the HNLPU (ASPLOS'26), Ankhdjet (2608.26206) and 2604.25183 full texts must not already contain cross-neuron block sharing under metal-only programmability. arXiv/ACM/IEEE were blocked for this session.

## What was actually accomplished

1. **Archive map** (`01_…`). Includes the Wave 11 data nobody had closed out: the covering headroom over the best heuristic is about 2–3% on half the circuits, so the thread was not continued.
2. **A technology-shift-driven problem selection** (`02_…`). Model-specific silicon (Taalas HC1 → AMD acquisition Aug 2026; HNLPU ASPLOS'26; BitROM; Ankhdjet) creates a new constraint, *weight-independent base layers*. That constraint disables the classical tool, weight-specific CSE.
3. **Hypotheses** with competing mechanisms, and their review (`03_…`, `04_…`). Three ideas were rejected as occupied: the block-precompute principle, generic CSE, and via-programmable model silicon as a concept.
4. **A mechanism with a proof** (`05_…` §8): port and adder lower bounds for any via-programmable fabric. UBP meets the port bound with equality.
5. **Pre-registered experiments** with fail-closed independent checking (`06_…`):
   - **E1:** adder counts vs per-input sharing and vs da4ml, n = 64 … 4096, 3 seeds.
   - **E2:** Yosys → AIG → native ABC on SKY130 at iso-delay.
   - Wire model: labelled as a model.
6. **Two engineering by-products:**
   - the da4ml 0.6.0 input-layout hazard;
   - YoWASP Yosys's silent in-process ABC exit.

   Neither was sent anywhere.

## Evidence summary (see 06 for tables)

| Claim | Status |
|---|---|
| Regime-(V) adder ratio g1_V / UBP_V = 2.62 / 3.17 / 3.54 at n = 64 / 128 / 256 (→ ≈ g for large m) | **Exact closed form, W-independent** |
| Full-custom per-input vs UBP, adders: 1.78 → 2.12 → 2.40 (p0 = 0.33, n = 64 → 256); 1.47 → 1.66 (p0 = 0.5) | **OBSERVED**, 3 seeds, every construction independently checked |
| UBP within 1.22–1.37× of da4ml; weight-specific block patterns (CBP) within 1.21–1.31× | **OBSERVED** at n ≤ 128. da4ml exceeds 600 s at n = 256 (under load; D2) |
| Universality itself costs 1–4% (UBP vs CBP) | **OBSERVED** |
| Gate-level area at iso-delay (SKY130) | **E2: see `results/E2_summary.md`** (patched below when complete) |
| Area gain including select wiring: bit-parallel ≈ 1.7–2.3× (g = 2–3); bit-serial ≈ 3× (g = 3–4) | **MODEL only.** The main open risk. |
| 4-bit/FP4: no useful gain (value-domain blocks are wire-bound; digit planes revert to about one leaf per site) | **MODEL/INFERRED.** Scope limit. |

## Final scientific review (Part XVIII questions)

1. **Could this be done by changing an existing parameter?**
   - Not in the (V) designs that exist. HNLPU groups within a neuron and Taalas pre-multiplies per input; adopting UBP adds generator arrays and changes neuron leaf counts and routing.
   - In *runtime* LUT architectures, G is a parameter. The objection "just set G large and replace the mux with a via" is the honest core of the novelty risk (§15 of 05). The defence is the changed cost regime plus the optimality result, not a new principle.
2. **Could a stronger baseline already produce the effect?**
   - In full-custom (F), yes: da4ml gets 22–37% fewer adders than UBP.
   - In (V), da4ml is inapplicable by definition. The strongest applicable baseline (per-input/in-neuron) is beaten by about g× in adders.
3. **Is the novelty merely a new benchmark?** No. It is a construction, a bound, and measurements. No benchmark is proposed.
4. **Is the mechanism different from existing algorithms?**
   - The mathematics is Four Russians/LUT-GEMM (a known ingredient).
   - The *complete contribution* is different: cross-neuron sharing in a weight-independent fabric, a provable port-optimality, and a regime-specific optimum g set by row count and wiring. No retrieved source describes it. That is not proof of absence.
5. **Would it matter if nobody used our software?** Yes. The construction and the bound are implementation-independent design knowledge.
6. **Does the insight generalize beyond one example?**
   - The (V) ratio is exact for all W.
   - The (F) comparisons use i.i.d. ternary only: real checkpoints were blocked.
   - E2 uses one matrix per p0.
   - Wiring is modelled, not measured.
   - Scope is ternary/binary, not 4-bit.
7. **Are we promising a correctness guarantee without a proof?**
   - Exactness holds by construction and is checked per instance: numeric at two levels, plus ABC `cec`.
   - Universality holds by construction, since all patterns are present.
   - Theorem 1 is proven in 05 §8.
8. **Are we promising an improvement without an appropriate baseline?** No. The (V) status quo and the strongest (F) method are both included, and comparisons are at iso-delay (E2).
9. **Have we confused a hypothesis with a result?** The wire-level gains are labelled MODEL throughout. Area including wiring is a hypothesis until PnR.
10. **Would an expert find an obvious stronger prior method?**
    - Possibly inside HNLPU's full text (its bit-serial POPCNT neurons could share inputs across neurons), or in Taalas HC2 (proprietary).
    - Possibly in structured-ASIC DSP literature (via-programmable constant-coefficient filters). Not found in searches, which is not proof.
11. **What result would make us abandon it?** Either of the §13 conditions:
    - post-PnR area(UBP_V) > area(g1_V)/1.3 in both arithmetic styles;
    - a full text showing the same construction.

## What to implement first (exact next steps)

1. **Novelty check (1 day).** Read HNLPU §§ on the Sea-of-Neurons / neuron microarchitecture, Ankhdjet's macro description, and 2604.25183's design space. Allow arxiv.org and dl.acm.org in the environment's network settings. Decide: continue, or narrow to "bound + measurement".
2. **Bit-serial generator** (`hwlayer.py` → sequential RTL):
   - shared serial pattern generators;
   - per-neuron serial adder/popcount trees;
   - an explicit via-select netlist in which every candidate line is physically present.
3. **Falsifying experiment:** OpenROAD/ORFS place-and-route of 256×256 macros on SKY130 (and ASAP7): g1_V vs UBP_V (g = 2, 3, 4), in bit-parallel and bit-serial styles, at equal clock. Measure area, wirelength, congestion and power.
4. **Real weights:** BitNet-b1.58-2B4T layers for the (F) comparison with da4ml and CBP. This needs huggingface.co.

## Blockers encountered (precise)

- **Egress policy:** arxiv.org, dl.acm.org, ieeexplore.ieee.org, semanticscholar.org, openreview.net, huggingface.co and personal sites are denied. This blocks the full-text novelty check and real checkpoints. It is fixable in the environment's network settings.
- **GitHub release downloads** (OSS CAD Suite) are outside the session's repository scope. Worked around with a native ABC build plus YoWASP Yosys.
- **Budget:** PnR (ORFS container) was not attempted, to stay within the advisory budget. It is the first prototype task.
