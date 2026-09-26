# 07 — Final research decision

## Classification

**RESEARCH THESIS READY FOR INITIAL PROTOTYPE, scoped to regime (V) (metal/via-programmable, weight-independent base layers) and conditional on a one-day full-text novelty check that this environment could not perform.**

- **The thesis** (`05_…`): in hardwired inference silicon whose base layers must be identical for every model, universal block-pattern generators (UBP-g) share accumulation *across neurons*. What that buys for ternary/binary layers:
  - ≈ g× fewer accumulation adders than today's per-input fabrics (exact and W-independent);
  - **1.95× (n = 128) and 2.49× (n = 1024) smaller cell area at iso-delay** (E3, measured on SKY130);
  - about 2× including select wiring at g = 3 (model applied to the measured cells).
- **Proof:** the fabric meets a programmable-port lower bound with equality (Theorem 1).
- **The condition:** the full texts of HNLPU (ASPLOS'26), Ankhdjet (2608.26206) and 2604.25183 must not already contain cross-neuron block sharing under metal-only programmability.

**Explicitly NOT claimed (killed during the session):**
- any advantage in full-custom silicon (regime F);
- any advantage for 4-bit/FP4 weights.

## What changed during the session, and why it matters

- **The first experiments looked stronger than they were.** E1 showed 1.8–3.7× fewer adders than "per-input" trees in full-custom silicon.
- **The gate-level run (E2) exposed the problem:** a 2× adder cut became only 1.17–1.19× area.
- **Hypotheses tested in turn:**
  1. Yosys `alumacc` absorbing shared sums: ruled out by a controlled test.
  2. **Structural hashing:** Yosys `opt_merge` / ABC `strash` automatically merge partial sums that recur across rows of plain per-input trees. **Confirmed** (E1-hashed, n = 64–1024): hashed per-input trees come within 1.07–1.20× of UBP.
- **Consequence.** E1's full-custom baseline was weak, which is exactly the Wave 10 failure mode. The claim was withdrawn for (F) and re-tested where it can hold. In regime (V) no weight-specific hashing or CSE can exist, because the base layers cannot know W. That is E3, pre-registered after the diagnosis and before its data. It passed.

## Evidence summary

| Claim | Status |
|---|---|
| (V) adders: g1_V/UBP_V = 2.62 / 3.17 / 3.54 / 3.88 at n = 64 / 128 / 256 / 1024 | **Exact closed form, W-independent** |
| (V) cell area at iso-delay: 1.55 / 1.81 / **1.95** (n = 128; g = 2 / 3 / 4); 1.65 / 2.06 / **2.49** (n = 1024) | **OBSERVED (E3)**: 14/14 components valid (own AIG simulation + ABC `cec`); the baseline gets the delay slack |
| (V) including select wiring: g = 3 → 1.81× (n = 128), 2.06× (n = 1024) at 0.46 and 0.92 µm pitch; g = 4 → 1.8–2.24× or 1.0–1.14× | **MODEL** on measured cells |
| Price of universality: UBP needs 1.22–1.37× more adders than da4ml (weight-specific, not usable in V) | **OBSERVED** (n ≤ 256) |
| Universality itself costs 1–4% (UBP vs CBP) | **OBSERVED** |
| (F): UBP vs hashed per-input 1.04–1.20×; da4ml better than both | **OBSERVED**, so **(F) claim withdrawn** |
| Ternary ≈ 3× at g = 3 with 4.3 lines/input; binary ≈ 4× at g = 4 with 2 lines/input; int4 wire-bound | **Closed forms + line counts** |

## Final scientific review (Part XVIII)

1. **Could this be done by changing an existing parameter?**
   - Not in the existing (V) designs. HNLPU groups within a neuron and Taalas pre-multiplies per input; adopting UBP adds a generator array and changes neuron leaf counts and routing.
   - In runtime LUT-GEMM designs, the block size is a parameter. The honest core of the novelty risk: "set G large and replace the mux with a via". The defence is the changed cost regime, the port-optimality result, and the measured (V) gains.
2. **Could a stronger baseline already produce the effect?**
   - In (F), yes. Tool hashing nearly does, and da4ml does better, so (F) is withdrawn.
   - In (V), the strongest *applicable* baseline is the per-input universal fabric, which UBP beats at iso-delay by 1.95–2.49× in cell area.
3. **Is the novelty merely a new benchmark?** No. It is a construction, a bound, a regime result and measurements.
4. **Is the mechanism different from existing algorithms?**
   - The mathematics is Four Russians / LUT-GEMM (a known ingredient).
   - The complete contribution (cross-neuron sharing in weight-independent base layers, port-optimal, with the regime's optimal g) is not described in any retrieved source. Absence of search results is not proof.
5. **Would it matter if nobody used our software?** Yes. The fabric construction and Theorem 1 are tool-independent.
6. **Does it generalize beyond one example?**
   - The (V) adder ratio holds for every W.
   - The (V) cell-area ratio does not depend on W at all, since the components are W-independent. It is measured at two sizes on one library (SKY130).
   - Wiring is modelled. ASAP7/advanced nodes are not tested.
7. **Correctness guarantee without proof?** Exactness holds by construction and is checked per instance at three levels. Theorem 1 is proven.
8. **Improvement without an appropriate baseline?** Not any more. The weak (F) baseline was caught and corrected; the (V) baseline is the status-quo universal fabric at iso-delay.
9. **Hypothesis confused with result?** Wiring-inclusive numbers are labelled MODEL throughout.
10. **Would an expert find an obvious stronger prior method?** Possibly inside HNLPU's full text (its bit-serial POPCNT neurons), Taalas HC2 (proprietary), or via-programmable structured-ASIC DSP work. This is the one-day check.
11. **What result would make us abandon it?**
    - Post-PnR area(UBP_V, g = 3) > area(g1_V)/1.3 in both arithmetic styles;
    - or a full text describing the same cross-neuron construction under metal-only programmability.

## What to implement first (exact next steps)

1. **Novelty check (1 day).** Read the HNLPU Sea-of-Neurons / neuron microarchitecture sections, Ankhdjet's macro, and 2604.25183's design space. This requires allowing arxiv.org and dl.acm.org in the environment's network settings.
2. **Falsifying PnR experiment (1–2 weeks).** OpenROAD/ORFS on SKY130 (+ ASAP7): a 256×256 via-programmable macro in which every candidate line is physically present in the programmable metal layers.
   - Compare g1_V vs UBP3_V vs UBP4_V at equal clock.
   - Measure area, wirelength, congestion and power.
3. **Bit-serial variant** (HNLPU's arithmetic style), where the model predicts about 3× at g = 3–4.
4. **Integration** into Ankhdjet's open SKY130 macro for an A/B at equal metal-only programmability; possible open-shuttle test vehicle.
5. **Real BitNet-b1.58 layers.** They matter only for the (F) side comparisons; the (V) result is W-independent.

## Blockers encountered (precise)

- **Egress policy:** arxiv.org, dl.acm.org, ieeexplore.ieee.org, semanticscholar.org, openreview.net, huggingface.co and several personal sites are denied (HTTP 403 from the policy gateway). This blocks the full-text novelty check and real checkpoints. It is fixable in the environment's network settings.
- **GitHub release downloads** outside the session's repository scope are refused. Worked around with a native ABC build plus YoWASP Yosys.
- **Budget:** PnR was not attempted in this session. It is the first prototype task.
