# E1 — pre-registration

Written 2026-09-25. At this point only the infrastructure smoke tests on c17 and ctrl had been run. Those runs were not used to choose any threshold.

**HYPOTHESIS (necessary assumptions of H1.6).**
- **A1:** at a fixed delay bound D, the minimum-area cover over mockturtle `map`'s *own* cut-match space is materially smaller than `map`'s heuristic cover.
- **A2:** most of that headroom is reachable by changing only near-tie decisions (ε-restricted candidates).
- **A3:** the ε-restricted space is a small fraction of the full space.

**EXPERIMENTAL INPUT.** The Wave 10 compress2 AIGs (`12_…/experiments/inputs/c1/c2/*.aig`) for these circuits: ctrl, router, int2float, dec, cavlc, priority, i2c, c432, c499, c880, c1355, c1908. A circuit is attempted only while solver budgets allow.

**BASELINE.**
- `map` itself, with `required_time = D`;
- **emap** at `required_time = D`;
- ABC `&nf -p` and `&nf -p -a`, both with `-R ⌊100(D/D_nfp − 1)⌋`.

**PROPOSED CHANGE (a controlled approximation of the mechanism, not the mechanism).** Exact covering over the dumped space: full, and ε-restricted with ε ∈ {0, 0.05, 0.20}. Solver: z3 4.15.5 νZ (weighted MaxSAT objective; pseudo-Boolean exactly-one; timing as guarded difference constraints). The OSS CAD Suite binary runs inside the network-off container.

**CONTROLLED VARIABLES.**
- The same AIG, cut set, matches, library, delay model and D for every method.
- The heuristic's dump is taken at the same `required_time` as the comparison point.

**D POINTS.** D0 = `map`'s delay-optimal delay (+0.001 ps float tolerance) and D1 = 1.10 × D0.

**OBSERVABLES** (all areas and delays recomputed by the Wave 10 independent evaluator from the netlists):
- A_map(D), A_emap(D), A_nf(D), A_nfa(D);
- UB(D) = the smallest validated exact-model area at D;
- LB = the proven minimum area with **no** delay constraint over the same space (pure MaxSAT). This is a valid lower bound at every D;
- A*_ε(D);
- the candidate counts.

**Verdict logic (fail-closed; a timeout is never evidence).**

| Condition | Reading |
|---|---|
| (A_map − LB) / A_map < 2% | headroom **proven** < 2% at every D on that circuit |
| (A_map − UB(D)) / A_map ≥ 2%, UB netlist validated | headroom **demonstrated** ≥ 2% at D |
| anything else | UNRESOLVED for that circuit / D |

**KILL CONDITIONS.**
- **A1 kill (PROBLEM INVALIDATED within `map`'s covering space):** headroom is proven < 2% on the majority of circuits where a verdict exists, and demonstrated ≥ 2% on none.
- **A2 / A3 kill (MECHANISM INVALIDATED):** on the circuits with demonstrated headroom, the ε = 0.05 restriction captures < 50% of the best demonstrated improvement, or keeps > 50% of the candidates.
- **Relevance kill:** where headroom is demonstrated, UB(D) is not below min(A_emap, A_nf, A_nfa) at D on most such circuits.

**ADVANCE CONDITION.** A1 demonstrated (≥ 2%) on at least half of the circuits with a verdict; A2 and A3 not killed; and UB(D) below the best heuristic (emap / `&nf` / `&nf -a`) on at least half of the circuits with demonstrated headroom.

**INDEPENDENT VALIDATION.** Every netlist, whether heuristic or solver-derived, gets:
- the Wave 10 `c1_eval.py` STA plus 4096-pattern simulation against the **original** AIG;
- ABC `cec` of its own BLIF against the original AIG.

A solver solution counts only if its independent delay is ≤ D + 0.01 ps and both checks pass. A mutated-netlist negative control is run once.

## Deviation log

(empty at registration)

**Entries written 2026-09-25, before any Phase A run (the real E1 runs) was launched.**

1. **Model bug found in infrastructure tests.** The first z3 no-timing lower bound on ctrl returned 2.00. That value is invalid: the model allowed `v[n,0] ∧ v[n,1]`, a node whose two phases are inverters of each other. That is a combinational cycle that computes nothing.
   - Fix: the constraint `¬(v[n,0] ∧ v[n,1])`, plus a Python acyclicity re-check of every solver model.
   - The cyclic netlist was moved to `outputs/e1/superseded/`.
   - No threshold changed.
2. **Evaluator copy.** The Wave 10 evaluator loops forever on a cyclic netlist. E1 therefore uses a copy, `scripts/c1_eval_w11.py`, whose only change is a fail-closed combinational-cycle guard (checked by normalized diff). The Wave 10 original is unmodified.
3. **Solver substitution.** z3 4.15.5 νZ could not solve even the smallest real instance, ctrl (7,345 candidates):
   - full timed model: `unknown` at 300 s;
   - with `smt.arith.solver=1`: `unknown` at 105.6 s, and the ε = 0.05 model `unknown` at 1.4 s, so that setting is unusable;
   - no-timing MaxSAT: `unknown` at 600 s.

   The same model is therefore solved with **OR-tools CP-SAT 9.14**. The binary is `/opt/or-tools/bin/sat_runner` (md5 `358d567c2bf14e88f18aebb631024127`), which ships inside the `openroad/orfs` image and runs network-off. The model is in exact integer units (×100; every asap7 area and pin delay has at most 2 decimals). `scripts/e1_exact.py` (z3) is kept unchanged as the record of the z3 attempts. The CP-SAT version is `scripts/e1_cpsat.py`, with the shared code in `scripts/e1_model.py`.
4. **Model-fidelity control (added).** For every dump, `map`'s own final cover is rebuilt from the dump, following `finalize_cover()`:
   - it must reproduce the mapper's reported area and delay under the model;
   - it must pass the independent evaluator.

   ctrl: model 6.92 / 103.17 = mapper = evaluator, sim and CEC PASS. c17: 0.53 / 42.66, same checks.

   This cover is also given to CP-SAT as a solution hint, so a full-space upper bound is normally ≤ A_map. "UB = A_map" means no improvement was found.
5. **Lower bound.** The registered LB is the no-timing MaxSAT optimum; it is run as `lb:D0`. CP-SAT also returns a proven bound for the *timed* model at D (`best_objective_bound`). That bound is a valid lower bound on the minimum area at D over the same space, and at least as tight as the no-timing one. Both are recorded, and a "proven < 2%" verdict names which bound it uses. Both are **solver claims** (no independent proof checking). Upper bounds, by contrast, are independently validated netlists.
6. **Budgets and parallelism,** fixed now:
   - full model: 600 s at each D;
   - no-timing LB: 300 s;
   - ε-restricted models: 300 s;
   - 4 CP-SAT workers, `random_seed:1`;
   - two lanes in parallel, each container with 4 CPUs and 6 GB.

   Multi-worker CP-SAT is not deterministic, so reruns can give different bounds within a budget.
7. **Disclosure: results seen before the budgets were fixed.** Smoke runs on ctrl were observed first:
   - 120 s full at D0 without a hint: UB 6.80, bound 6.57;
   - 20 s runs with the hint: full D0 6.73, full D1 6.57;
   - ε = 0.05 in 10 s: D0 6.89 and D1 6.69, both OPTIMAL.

   No threshold, circuit, D point or ε value was changed after seeing them. They are kept in `outputs/e1/cpsat_test/`, `outputs/e1/smoke_run/` and `results/e1_smoke_run/`, and are **not used for any verdict**. ctrl is re-run under the real budgets.
8. **D points, as registered:**
   - D0 = `map`'s delay + 0.001 ps;
   - D1 = 1.10 × D0;
   - the integer model uses ⌊100·D⌋, which never gives more slack than D.

   A D1 dump is taken with `map` at `required_time = D1`.
9. **Baselines, as registered:**
   - `&nf -R` is computed against `&nf -p`'s own evaluated delay;
   - a baseline counts at D only if its independently evaluated delay is ≤ D + 0.01 ps.
10. **Phase B (ε models)** runs after Phase A, ε = 0.05 first (the value the A2/A3 kill uses), then ε = 0 and 0.20 as the budget allows. Any ε run that is not done is reported as not run.
11. **Aggregation rules, fixed in `scripts/e1_analyze.py`** after Phase A launched but **before any Phase A result was read**. The registration left these implicit.
    - **Units.** The unit is the (circuit, D) pair.
      - A circuit is DEMONSTRATED if it is demonstrated at any D.
      - It is PROVEN_BELOW_2 if proven at every D.
      - Otherwise it is UNRESOLVED.
    - **Kill and advance** are applied at the circuit level. Pair-level counts are reported alongside. If the two disagree, the more conservative reading is taken.
    - **UB(D)** is the smallest validated area among the exact-model solutions at D. An ε-model solution is a valid full-space upper bound.
    - **LB(D)** is the larger of two solver-proven bounds:
      - the timed full-model bound at D;
      - the no-timing bound, which counts at D1 only if the D1 dump has exactly the same candidate set as the D0 dump.
    - **Relevance** (UB(D) strictly below the best baseline that meets D): killed if "not below" holds on more than half of the demonstrated circuits.
    - **A2 capture** = (A_map − A_ε)/(A_map − UB_full) at demonstrated pairs. The kill uses the ε model's proven bound, so a "< 50%" capture is proven rather than an artifact of the ε run's timeout. A2 is killed if the capture is proven below 50% on a majority of the demonstrated pairs that have an ε = 0.05 run.
    - **A3** is killed if the ε = 0.05 model keeps more than 50% of the candidates on a majority of those pairs.
12. **Negative control, run once as registered.** The source was the validated ctrl CP-SAT solution from the infrastructure test (area 6.80, delay 103.17; simulation AGREE, cec PASS).
    - **M1b:** the first AND2x2 was replaced by OR2x4 → SIM_MISMATCH, cec NEQ.
    - **M2:** A1 and B were swapped on the first AO21x1 → SIM_MISMATCH, cec NEQ.
    - **First M1 attempt (discarded):** it used `OR2x2`, which is not in asap7.genlib. The evaluator raised a KeyError and printed no verdict line, so fail-closed it counts as not validated. That attempt is not counted as a control.

    Logs: `logs/e1_negctrl.log`, `logs/e1_negctrl2.log`.
13. **Aborted first Phase A launch (container CPU limit).** Phase A was first launched at about 23:10 UTC.
    - **What went wrong:** the Windows-side `CPUS=4 MEM=6g` settings never reached WSL. Windows environment variables are not forwarded unless listed in `WSLENV`. Both containers therefore ran at the wrapper default of **2 CPUs**, with 4 CP-SAT workers each.
    - **How it was caught:** `docker stats` showed about 199% CPU per container, about 7 minutes in. That was **before any exact-model record was written**.
    - **Action:** both containers were killed. Their partial records (map, heuristic-control, emap and `&nf` baselines for ctrl and router) were moved unread to `outputs/e1/superseded/phaseA_2cpu_aborted/`.
    - **Relaunch:** Phase A was relaunched from scratch with the limits set inside WSL (`wsl.exe … -- env CPUS=4 MEM=6g bash w11_docker.sh …`), and the setting was checked with `docker stats`.
    - **Also affected:** the earlier infrastructure test `e1_cpsat_test` (launched with `CPUS=7`) also ran on 2 CPUs. It is a smoke test and is not used for any verdict.
14. **`06`'s median-form kill conditions are reported alongside.** `06_EXPERIMENTAL_EVALUATOR.md` states its kills as medians over *solved* instances:
    - median H < 2%;
    - median C(0.05) < 50%;
    - median R(0.05) > 50%.

    Where the exact optimum is not proven, `e1_analyze.py` computes these as sound brackets:
    - H is bounded as H_lo = (A_map − UB)/A_map ≤ H ≤ H_hi = (A_map − LB)/A_map;
    - C(0.05) has an upper bound from the ε model's proven bound;
    - R is measured directly.

    This was added after the relaunch, before any Phase A result was read. The pre-registration's LB/UB verdict table (above) remains the operative rule. If the two readings disagree, both are reported and the decision takes the more conservative one.
