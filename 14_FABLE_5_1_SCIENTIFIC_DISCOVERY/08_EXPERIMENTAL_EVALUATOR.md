# 08 — The experimental evaluator (built this session)

## Question it answers

Does the cell-level advantage of universal block sharing (UBP-g) over the per-input universal fabric (g1) survive **physical place-and-route**, once the per-weight connections become real wires?

Cell-level results (HIST-OBS) cannot answer this. The previous session's wire model is analytic only.

## Designs (generated per W; modules are weight-independent)

| Design | Weight-independent modules (synthesized once, instantiated) | W-dependent part |
|---|---|---|
| g1 (baseline) | NEG per input (shared x → −x); TREE(n) per row | Each row leaf connects to x_j, −x_j or tie-low |
| UBP-g, g ∈ {3, 4} | GEN(g) per input block (all (3^g − 1)/2 canonical signed subset sums); NEG per pattern line; TREE(⌈n/g⌉) per row | Each row leaf connects to one pattern line, its negation, or tie-low |

**Styles:**
- **E5, bit-parallel (H1.1):** combinational; w-bit lines.
- **E6, bit-serial (H1.2):** one-wire lines; registered serial adders; T = ow cycles per word.
- The top-level netlist is the **via program**: only connections differ between W's.

## Flow (all inside the pinned container `openroad/orfs:latest`, image id `69df744e2b5c`)

1. **Module synthesis:** Yosys + ABC (`synth -flatten; [dfflibmap;] abc -liberty; hilomap`). Area-oriented, identical script for all designs. The platform's DONT_USE cells are excluded.
2. **Netlist assembly:** modules plus top are re-emitted through Yosys **without flattening or optimization** (`hierarchy; opt_clean -purge`). Synthesis can therefore never exploit W: cross-module sharing and hashing are impossible. This keeps the comparison in regime V.
3. **ORFS (SKY130 HD):** stock flow, run through detailed routing and finish.
   - The netlist is given via `SYNTH_NETLIST_FILES`, so there is no re-synthesis.
   - Defaults except CORE_UTILIZATION and the clock. OpenROAD flattens at link time; placement, repair, CTS (E6), global and detailed routing then run as usual.
4. **Utilization sweep** U ∈ {45, 60, 75} %:
   - **U_max** is the highest U whose detailed route finishes with 0 DRC violations (E6 also requires setup and hold met at 3.0 ns).
   - **Routed area** = synthesized cell area / U_max.
5. **Metrics** come from the ORFS JSON metrics:
   - `2_1_floorplan.json`: instance area, core area;
   - `5_1_grt.json`: global-route violations;
   - `5_2_route.json`: DRC errors, wirelength;
   - `6_report.json`: setup/hold WS, final std-cell area.

   The collector is `scripts/e5_collect.py`; the decision rules are pre-registered in 09.

## Independent validation (not trusting any tool's own report)

| Level | Check | Script |
|---|---|---|
| Top netlist, pre-PnR | Yosys → AIG (liberty functions) → **our** simulator vs numpy W@x. E5: 64 vectors. E6: cycle-accurate over 12 back-to-back words. | `e5_build.validate`, `e6_build.sim_seq` |
| Negative control | The same simulation against W′ (one weight's polarity flipped) must fail | the same |
| Post-PnR | The ORFS **final routed** netlist (buffers, resizing, CTS, hold fixes, ties) → AIG → our simulator vs numpy, plus the mutation control | `post_pnr_validate.py` |

## W-independence invariant (added by Amendment A2)

A regime-V fabric must have **the same cells for every W**. Functional checks cannot see a violation, because pruned logic is dead. The evaluator therefore also checks:
- **Negator instance count** in the emitted netlist equals the closed form: n for g1; Σ_blocks (3^|b| − 1)/2 for UBP.
- **ORFS `synth__design__instance__area` equals Yosys `stat -liberty`** of the full netlist. This means no dead-logic elimination happened.

**How it is enforced:**
- every top-level instance carries `keep`;
- ORFS runs with `eliminate_dead_logic` disabled (`scripts/orfs_patch/synth_odb.tcl`, mounted by `NO_DCE=1 scripts/e5_run.sh`).

## What the evaluator measures well

- The **real** place-and-route cost of the W-dependent connections: detours, congestion and DRC limits, on a real 5-metal PDK.
- **Timing repair** after placement, and CTS for the serial designs.

## Its limitations, and the direction of each bias

| Limitation | Effect | Favours |
|---|---|---|
| **Placement freedom:** cells are placed knowing W. A real regime-V chip fixes placement (base layers) and changes only upper metal. | Understates the wiring of every design: connections are placed close together | Both. Possibly UBP more, because its per-W nets span shared generators and many rows. |
| **All metal layers are used for W-dependent nets.** In regime V only the top layers are programmable. | Understates congestion | Both |
| **Only used connections are routed.** A strap-and-via ROM-style fabric needs every candidate line to pass every site. | Understates UBP's strap demand ((3^g − 1) lines per block vs 2 per input) | **UBP** |
| Random ternary W (p0 = 0.4) | Real weights may be more structured | Neutral |
| One PDK (SKY130, 5 metals, 130 nm); small layers (32, 64) | Scale trends are not measured. Small m under-amortizes the generators. | g1 (at small m) |
| Standard-cell realization | A via-ROM macro, or custom HNLPU neurons, would have different constants | Unknown |

**Interpretation rule.** Written after global-route congestion was visible for two U = 60 runs (g1_n32, ubp3_n32; no overflow in either) and before any detailed-route outcome. It only restates the limitations declared in 09.
- A **negative** result (K5/K6) is strong evidence against the mechanism: the evaluator is optimistic for UBP on the wiring axis.
- A **positive** result is necessary but not sufficient, because of the strap-demand and fixed-placement gaps. It would call for a fixed-placement, upper-metal-only ECO experiment (possible in OpenROAD, not run in this session).
