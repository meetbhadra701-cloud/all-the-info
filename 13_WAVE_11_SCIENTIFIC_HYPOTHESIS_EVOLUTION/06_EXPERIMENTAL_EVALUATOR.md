# 06 — Experimental evaluator for H1.6 (designed before any H1.6 data)

## Reference implementations

| Role | Implementation | Why |
|---|---|---|
| Strongest in-library heuristic | mockturtle **emap** (same commit `420f027`; single-output cells, the same 47-gate ASAP7 genlib as W10) | Won most iso-delay comparisons in W10 D1. |
| Strongest external heuristic | ABC **`&nf -p`** (yosys-abc in the ORFS image), with `-R` for relaxation | The standard open-source standard-cell mapper. |
| Closest exact-area implementation | ABC **`&nf -p -a`** ("SAT-based area-oriented mapping, experimental") | The closest possible implementation of the occupied principle. It must be beaten or matched, not ignored. |
| Heuristic whose space is solved exactly | mockturtle **`map`** (initial operators) | Its cut-match space can be dumped exactly from `mapping.hpp`, so "optimum over the same space" is well defined. |
| Post-mapping Boolean resynthesis | ASP-DAC'25 engine / mfs3 | Bar for the research-development stage, not the first experiment. Availability in local mockturtle/ABC is UNVERIFIED. |

## Scientific objectives (what exactly is measured)

- **A1 (headroom).** H = [A_map(D) − A*(D)] / A_map(D).
  - A*(D) is the exact minimum cell area over **map's own cut-match space** (same cuts, matches, phases, inverters and delay model), subject to worst arrival ≤ D.
  - Reported with its relation to emap and `&nf`: A*(D) / min(A_emap(D), A_nf(D)).
- **A2 (concentration).** Capture ratio C(ε) = [A_map(D) − A*_ε(D)] / [A_map(D) − A*(D)].
  - A*_ε is the exact minimum when each (node, phase) may only use candidates whose area flow is ≤ (1 + ε) × that node's best candidate area flow, plus the heuristic's own choice.
  - Area flows come from `map`'s final state.
  - ε ∈ {0, 0.05, 0.20}.
- **A3 (reduction).** R(ε) = the restricted candidate count ÷ the full candidate count.
- **Two delay points per circuit:**
  - D0 = `map`'s own delay-optimal delay (with load-independent delays, `map`'s delay pass is exact over its space);
  - D1 = 1.10 × D0.

## Measurement

- All areas and delays are recomputed from the **netlist** by the Wave 10 independent evaluator `c1_eval.py`: its own genlib parser and its own STA with pin delay = max(rise, fall). The solver's objective value and the mapper's self-report are never used for comparison.
- A solver result counts only if its reconstructed netlist's independently computed delay is ≤ D (+0.01 ps tolerance).

## Correctness

Every netlist, whether heuristic or exact, is checked in three ways:
1. `c1_eval.py` simulation of the cell netlist against the **original** AIG (4096 patterns, own simulator);
2. ABC `cec` of `c1_eval`'s own BLIF translation against the original AIG, where only the literal "Networks are equivalent" counts as PASS;
3. the solver's model is re-checked against the dumped space in Python before netlist emission (every chosen match's leaves are available in the right phase; arrivals are consistent).

**Negative control.** One deliberately mutated solver solution must be rejected by checks 1 and 2.

## Comparison: algorithm, not configuration

- The heuristic baselines get the **same D** through their own knobs:
  - `map`/emap: `required_time = D`;
  - ABC: `-R ⌊100(D/D_nfp − 1)⌋`.
  This way any headroom is not just the relaxation that W10 exposed.
- The exact model's space is *exactly* `map`'s space, dumped from the mapper after its own passes. Any gap between A_map and A* is therefore attributable to covering decisions, not to cuts, library or structure.

## Solver outcomes and how they are read (fail-closed)

| Outcome | Reading |
|---|---|
| Z3 `sat` with optimum, netlist validated | A* established for that instance |
| Solver timeout / `unknown` | **no verdict** (never read as "no headroom") |
| Solver answer whose netlist fails validation | modelling error; the instance is excluded and reported |

## Generalization (first experiment vs later)

- **First experiment.** Small circuits where whole-circuit exact search is plausible, from two families:
  - control/random logic: EPFL `ctrl`, `router`, `int2float`, `cavlc`, `dec`, `priority`, `i2c`;
  - ISCAS85: `c432`, `c499`, `c880`, `c1355`, `c1908`.

  These use the same compress2 pre-processed AIGs as Wave 10 (`12_…/experiments/inputs/c1/c2/`).
- **Research-development stage (only if the first experiment passes).**
  - The ambiguity-restricted solver runs on circuits too large for whole-circuit search (EPFL arithmetic, IWLS05).
  - It is compared against emap, `&nf -p -a`, satlut-style windows and ASP-DAC'25 resubstitution, at matched D and reported runtime.

## Failure: what invalidates the central hypothesis

These conditions are fixed here, before any data exists (see `07_INITIAL_EXPERIMENT.md`):

| Test | Condition | Classification |
|---|---|---|
| A1 kill | Median H < 2% over the solved instances (both D points) | PROBLEM INVALIDATED within the mapper's covering space |
| A2 / A3 kill | A1 holds, but median C(0.05) < 50%, or median R(0.05) > 50% | MECHANISM INVALIDATED |
| Relevance kill | A* is not below the best heuristic of emap / `&nf -p` / `&nf -p -a` at the same D on most solved instances | covering-level headroom in `map`'s space does not beat the state of the art; the lever is the space (emap's), not the algorithm |
