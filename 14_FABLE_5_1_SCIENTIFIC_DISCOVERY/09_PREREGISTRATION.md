# 09 — Pre-registration: E5, the physical falsifier for regime-(V) wiring

Written before any E5 data.

## Hypothesis (H1.1, physical)

Weight-independent block-pattern fabrics keep a material area advantage after place-and-route at an equal clock: **routed core area of UBP-g ≤ routed core area of the per-input fabric / 1.5**, with detailed routing DRC-clean and timing met.

## Proposed mechanism under test

- UBP-g (g ∈ {3, 4}):
  - GEN(g) per input block (all canonical signed subset sums);
  - NEG per pattern line (shared negated lines);
  - TREE(⌈n/g⌉, w_g) per row.
- Each row leaf is connected, by the top-level netlist, to one pattern line, its negation, or a tie-low. That connection is **the via program**.

## Strongest baseline

The per-input universal fabric g1_V:
- NEG(8) per input (shared);
- TREE(n, 8) per row;
- each leaf connected to x_j, −x_j or tie-low.

This is the regime-(V) status quo (HNLPU / Ankhdjet style at the adder level).

## Inputs

- n = m = 32; i.i.d. ternary W (p0 = 0.4, numpy seed 14); symmetric INT8 activations in [−127, 127].
- Generalization run: n = m = 64, only if the n = 32 result advances and the budget allows.

## Controlled variables (identical for every design)

- **Library / PDK:** SKY130 HD (ORFS container `openroad/orfs:latest`, image id `69df744e2b5c`).
- **Module synthesis:** the same Yosys + ABC script (`synth -flatten; abc -liberty -D 4000; hilomap`), with the platform's DONT_USE cells excluded.
- **No cross-module optimization:** modules are synthesized once and instantiated. ORFS consumes the netlist via `SYNTH_NETLIST_FILES` (no re-synthesis).
- **ORFS flow:** default settings except CORE_UTILIZATION and the clock.
- **Clock:** a virtual clock of **6.0 ns** for all designs (iso-clock); input and output delays 0.

## Utilization protocol

- Each design is run at CORE_UTILIZATION ∈ {30, 45, 60} % (PLACE_DENSITY at ORFS defaults).
- The **routed core area** of a design is core area at the highest U whose detailed routing finishes with 0 DRC violations and no unrouted nets, with setup timing met (WNS ≥ 0).
- If no U satisfies this, the design is "not routable in the tested range".

## Measurement (from ORFS reports / metrics)

- Core area and instance (cell) area.
- DRC violation count after detailed routing.
- Total routed wirelength.
- Setup WNS / worst path at the finish stage.

## Independent validation

1. **Module level:** every synthesized module netlist is simulated by our own AIGER simulator (Yosys → AIG) against Python integer arithmetic (64 vectors).
2. **Top level:** the assembled top netlist (modules + ties) is converted by Yosys to an AIG and simulated against numpy `W @ x` (64 vectors).
3. **Negative control:** flipping one via connection must be caught.
4. **Physical level:** the ORFS final netlist is checked equivalent to the pre-PnR netlist with Yosys/ABC `cec`, where tractable. ORFS's own LVS is not available for this flow; the equivalence check stands in for it.

## Expected distinguishing behaviour (if the mechanism works)

- UBP routes at a utilization similar to g1's, keeping most of its ~1.6–2× cell-area advantage at n = 32.
- If select wiring dominates, UBP instead fails to route at the utilizations where g1 routes, or needs a much lower U.

## Kill and advance conditions

| ID | Condition | Classification |
|---|---|---|
| K5 | routed core area(g1_V) / min_g routed core area(UBP_V) < 1.3, or no UBP variant routable in range while g1 is | Wiring erodes the (V) advantage → **H1.1 MECHANISM FALSIFIED physically** → evolve to H1.2 (bit-serial) |
| A5 | ratio ≥ 1.5, with timing met for both | H1.1 physically supported at this scale |
| (between) | 1.3 ≤ ratio < 1.5 | weak support; record, and do not claim advance |

## Known interpretation limitations (declared)

- **Placement freedom.** The placer may arrange instances freely. A structured via-ROM array (fixed straps) is more constrained, so the result is optimistic for both designs.
- **Only used connections are routed.** A via fabric needs every candidate line to *cross* every site, which a real strap array provides without routing. The route here approximates that demand only when users are spread (random W).
- **Scale and technology.** Small layers (32×32) under-amortize the generator, which is conservative for UBP. One PDK only (SKY130, 5 metal layers).
- **Combinational only;** no pipelining; tie cells for zero leaves.
- **Novelty is not tested by E5.**

## Deviation log

The first three entries were logged before any E5 routing result was known.

- **D1 (validation item 1): module-level simulation is subsumed by top-level simulation.**
  - What was done: the assembled top netlist was simulated against numpy W@x with 64 random vectors, plus a mutation control. It exercises every module instance as used; the modules were not simulated one by one.
  - Why it matters little: a module error that never shows at the top cannot change the measured function.
- **D2 (validation item 4): the physical-level check is simulation-based, not formal `cec`.**
  - What is done: the ORFS **final routed** netlist (6_final.v) is converted by Yosys and simulated by our AIG simulator against numpy (64 vectors), plus a mutation control. Script: `scripts/post_pnr_validate.py`.
  - This is weaker than formal equivalence. It does catch any functional corruption by buffering, resizing or tie handling on the tested vectors.
- **D3 (negative-control form):** the mutation control flips the polarity of one nonzero weight in the *reference* (W → W′), rather than editing the netlist. Detecting W′ ≠ netlist is equivalent to detecting a one-via change in the netlist against W.
- **D4 (scheduling): runs are ordered U = 60, then U = 75, then U = 45** (the last only for designs that fail at 60). This does not change the definition of U_max over {45, 60, 75}.

## Amendment A1 — written after the 8×8 smoke build (module timing only) and BEFORE any n = 32 place-and-route data

**What the smoke build showed** (OpenSTA on Yosys/ABC-mapped SKY130 modules):
- Module delays are far above the ABC load-independent model used in the previous session's E3: NEG8 0.99 ns; GEN3 3.59 ns; TREE(8, 8) 3.40 ns.
- The UBP3 combinational path at 8×8 (8.1 ns) already exceeds the pre-registered 6.0 ns clock; g1's is 4.4 ns.

**Methodological defects this exposes:**
- (a) The pre-registered iso-clock would make E5 measure **timing repair**, not wiring. That confounds the question E5 exists to answer.
- (b) Budgeting module delays from pre-placement STA is unreliable, because post-placement repair and sizing change delays.

**Amended protocol (the original above is preserved):**
- **Synthesis:** every module is synthesized area-oriented (Yosys `abc -liberty`, no `-D`), with identical settings for all designs.
- **Clock:** a relaxed 20 ns virtual clock for all designs, so no timing repair is needed and WNS gives the natural delay.
- **Utilization sweep:** {45, 60, 75} % (the 30% point is dropped; 75 is added to find routability limits).
- **Routed area:** cell area / U_max, where U_max is the highest utilization with detailed routing at 0 DRC violations.
- **The iso-delay question** (a combinational delay penalty from generator/negator carry chains) is reported **separately** as natural post-route delay per design. It is not folded into the area ratio. Pipelining the generator stage, the realistic mitigation for throughput designs, is discussed and not tested.
- **K5 and A5 thresholds are unchanged** (1.3 / 1.5), now applied to cell area / U_max.
- **New reported (non-decisive) metric:** the delay ratio UBP / g1.

---

# E6 — pre-registration: evolution iteration 1 (H1.2, bit-serial)

Written before any n = 64 bit-serial data. The only prior data were the 8×8 smoke build: validation and module areas.

## Why an evolution iteration exists (what failed, what was learned)

- **What the E5 build revealed.** In bit-parallel combinational realizations, the generator's chained carry-propagate adders and the line negators sit **on the critical path**.
  - With OpenSTA on SKY130: UBP3's logic path is 9.37 ns vs g1's 6.57 ns at n = 32, a 1.43× delay penalty.
  - The previous session's ABC-model iso-delay (E3) understated this.
- **H1.1 has a second risk:** its select buses are (3^g − 1)/2 × w bits per site.
- **Technical change (H1.2):** make the fabric bit-serial.
  - Every generator step, negator and tree node is a 1-bit serial adder with registered sum and carry. The generator latency becomes pipeline latency (cycles), not clock period.
  - Lines become single wires, cutting select wiring w×.
  - Throughput is identical by construction: one output word every T = ow cycles in both fabrics.
- **Why it addresses the failure:** the clock period is set by one serial-adder stage for both designs. The delay penalty turns into a small latency difference (cycles), which throughput designs tolerate.

## Hypothesis

At an equal clock (3.0 ns) and equal throughput, bit-serial UBP-g fabrics have **routed area ≤ bit-serial g1 routed area / 1.5**, with detailed routing DRC-clean and setup timing met.

## Designs and inputs

- n = m = 64; the same W generator as E5 (seed 14, p0 = 0.4); symmetric INT8 streams, LSB first, sign-extended, T = ow cycles per word.
- **g1:** a shared serial negator per input line, plus STREE(n) per row.
- **UBP-g (g ∈ {3, 4}):** SGEN(g) per block (all canonical patterns, aligned), plus a shared serial negator per pattern line, plus STREE(⌈n/g⌉) per row.
- Zero leaves are tied low.

## Controlled variables

- The same Yosys/ABC area-oriented synthesis (plus `dfflibmap`) for every module; modules synthesized once and instantiated.
- ORFS defaults, SKY130 HD, a real clock on port `clk` (3.0 ns), CTS included.
- Utilization protocol as in Amendment A1: {45, 60, 75} %, with routed area = synthesized cell area / U_max.

## Independent validation

- The full top netlist is exported by Yosys (liberty cell functions) to a sequential AIG. Our own cycle-accurate simulator checks 12 back-to-back words against numpy W@x at the design's latency.
- One-connection mutation control.

## Kill and advance conditions

| ID | Condition | Classification |
|---|---|---|
| K6 | g1 / best UBP routed-area ratio < 1.3, or no UBP variant DRC-clean with timing met where g1 is | H1.2 falsified. Together with E5 this decides the mechanism class. |
| A6 | ratio ≥ 1.5, timing met for both | H1.2 supported at this scale |

**Also reported:** latency (cycles) of each design, and wirelength.

## Known limitations

- Placement freedom (as in E5).
- Random W.
- One size (64) and one PDK.
- The negator-per-line structure is kept for both designs. The complement-line + via-programmed constant-correction refinement, which would help both, is not tested.

## Amendment A2 (E5 and E6): weight-dependent pruning removed

A2 is a genuine methodological defect, found and fixed **before any corrected-run data**.

### What was found (23:45–00:05 UTC, after these runs finished)

- **Runs finished at that point:** E5 g1/ubp3 at U = 60; E6 ubp3/ubp4 at U = 60.
- **First source of pruning:** the netlist emission (`hierarchy; opt_clean -purge`) removed every negator instance whose output no row used.
  - E5 ubp3: 35 of 134 removed. E5 ubp4: 223 of 320. E6 ubp4: 156 of 640.
- **Second source of pruning:** ORFS's `synth_odb.tcl` runs `eliminate_dead_logic` after flattening. That removed generator logic feeding pattern lines no row selects.
  - E5 ubp3: 180 instances. E5 ubp4: 2,722. E6 ubp3: 190. E6 ubp4: 1,719.
  - g1: 0 in every run.

### Why this is a defect, not a result

- In regime V the base layers, i.e. the whole universal fabric, are **weight-independent**. Hardware for an unused line still exists on silicon.
- Pruning it per W is exactly the weight-specific optimization the hypothesis is not allowed to use.
- It understated UBP area: about 4% (E5 ubp3), 27% (E5 ubp4), 1.5% (E6 ubp3), 18% (E6 ubp4). The bias favours UBP.
- The pre-registration's own stated intent was "modules are synthesized once and instantiated; no cross-module optimization".

### Fix

1. **Emission:** every top-level instance gets `keep` (`setattr -set keep 1 top/t:*`), so negator instances are never removed. The rebuilt netlists hold the full fabric.
   - 134 / 320 / 274 / 640 negators, checked against the closed-form count.
   - Re-validated against numpy with the mutation control.
   - Script: `scripts/reemit_a2.py`; builders patched the same way.
2. **ORFS:** `eliminate_dead_logic` is disabled through a mounted copy of `synth_odb.tcl` (`scripts/orfs_patch/`). Nothing else in the flow changes.
3. **The g1 runs are kept as they are:** its netlists were already full fabrics (32 / 64 negators) and `eliminate_dead_logic` removed 0 instances. The patched and unpatched flows are therefore identical for g1.
4. **Area basis made precise.** "Synthesized cell area" = ORFS `synth__design__instance__area` (`1_synth.json`), i.e. the netlist as handed to ORFS.
   - It is taken **before** floorplan's `repair_tie_fanout`. That step splits each zero-leaf tie into one cell per load: +6,810 cells in g1 vs +430 in ubp3 at n = 32. This is an artifact that inflates g1: in a via fabric, zero is a ground connection.
   - Floorplan, final, and final-minus-ties areas are reported as sensitivity bases.

### Unchanged

The K5/A5 and K6/A6 thresholds, the utilization protocol, and the clocks.

### Preserved

The pruned runs' logs, netlists and summaries: `results/E*/pruned_A1_runs/`, `results/E*_pruned_A1_summary.md`. They are reported, not used for decisions.

### Known consequence

At U = 60, ubp3's actual cell load differs only slightly from the pruned run (1.5–4%). ubp4's differs a lot.

## E6 deviation log

- **D6.1 (netlist format; before any E6 PnR data): the top-level start-delay and alignment flip-flops were re-emitted as explicit `sky130_fd_sc_hd__dfxtp_1` instances.**
  - What happened: the first E6 ORFS launch failed at stage 1 for all six jobs (OpenSTA `STA-0171` syntax error). The top module still held behavioural `always @(posedge clk)` registers, which Yosys's Verilog backend writes with a `reg … = 0` initializer.
  - The fix: the same D flip-flops are instantiated as library cells, i.e. the cell `dfflibmap` would pick. Function, latency and every module are unchanged.
  - The build was re-run, and validation plus the mutation control were re-checked on the new netlist before PnR.
- **D6.2:** D1–D4 of E5 apply to E6 as well. The physical-level check uses the sequential simulator on 6_final.v (12 back-to-back words).
