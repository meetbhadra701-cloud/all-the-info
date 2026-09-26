# Experimental matrix

This file records what was planned, what was actually executed, and why anything was trimmed.
- Results per run: `RESULTS.csv`.
- Portfolio verdicts per netlist: `evidence/portfolio_summary.csv`.
- Interpretation: `INVESTIGATION_REPORT.md`.

## 1. Designs

### 1.1 Main set (`rtl/manifest.csv`, 102 designs; `scripts/gen_rtl.py`)

Operand ports are named `a`, `b`, `c`, `d`, `e`; the output is `y`. The alphabetical, declaration, AIGER and TRACE operand orders coincide. This was audited per netlist against Yosys `-map` files (`evidence/ground_truth*.csv`, column `port_order_ok`).

| Family | Operation | Signedness | Operand widths W | Output width |
|---|---|---|---|---|
| A | `y = a*b` | u, s | 8, 12, 16, 20, 24, 32, 64 | 2W |
| B-mac | `y = a*b + c` (c has 2W bits) | u, s | 8, 12, 16, 24, 32, 64 | 2W+1 (already Y_WIDTH > A+B) |
| B-dot2 | `y = a*b + c*d` | u, s | 8, 12, 16, 24, 32, 64 | 2W+1 |
| B-dot2c | `y = a*b + c*d + e` (e has 2W bits) | u, s | 8, 12, 16, 24, 32, 64 | 2W+2 |
| C-macw | `y = a*b + c` (c has Y bits) | u, s | 4, 8, 16, 32 | Y = 2W+8 and 2W+16 |
| C-msubw | `y = c - a*b` (c has Y bits) | u, s | 4, 8, 16, 32 | Y = 2W+8 and 2W+16 |
| C-msub | `y = c - a*b` (c has 2W bits) | u, s | 4, 8, 16, 32 | 2W+1 |
| MUT | RTL semantic mutants | – | 8, 16, 32 | – |

RTL mutants, all oracle-confirmed INCORRECT:
- `signext_mac_s`: signed product zero-extended into the accumulator (incorrect sign extension);
- `trunc_mul_u`: product truncated to 2W−1 bits;
- `accum_mac_u`: accumulator carry-out dropped;
- `plus1_dot2_u`: accumulator off by one.

"Missing correction term" is the **real** defect in unpatched `arith_tree`: the Baugh–Wooley correction is not sign-extended to the accumulation width. It is present in every MAIN signed `tree*` MAC, `dot2c` and Family-C netlist except `tree_nofma`.

### 1.2 Additional sets created during the investigation

| Set | Location | Purpose |
|---|---|---|
| Mini signed MACs, W = 2..6, MAIN and PATCH, `tree` and `tree_pre` | `rtl/mini/`, `netlists/MINI_*` (`scripts/run_synth_mini.sh`) | Smallest natural instances of the phase-optimisation trigger; the real defect at small widths |
| Onset sweep: `y = a*b`, W = 4..16, u/s, `booth` / `norm` / (`booth_lp` for s) | `rtl/sweep/`, `netlists/SWEEP_MAIN` (`scripts/run_synth_sweep.sh`) | Onset of post-ABC difficulty. W = 8 and 16 files are byte-identical to the main-set netlists (synthesis is deterministic) |
| 64-bit onset (W = 40/48/56), pre-ABC | `rtl/onset64/`, `netlists/ONSET_MAIN` (`scripts/run_synth_onset64.sh`) | Where the 64-bit pre-ABC cost appears |
| ABC isolation | `netlists/ABCSTEP` (`scripts/abc_steps.sh`, local ABC), `netlists/ABCMAP` (`scripts/run_synth_abcmap.sh`), `netlists/MAIN/*booth_lp_pre*` (`scripts/run_synth_lppre.sh`) | Which ABC pass destroys verifiability |
| Derived controls | `netlists/CONTROL/` (`scripts/aigxform.py`) | `fold` (constant propagation), `buffer` (insert `AND(x, TRUE)`), `contra` (insert `AND(x, ¬x)`), `xorself` (insert `XNOR(x, x)`), `ctx` (graft the full Yosys context `XOR(AND(p,¬x), XNOR(x,x))`), and `xorout` (deliberate output mutant). Every derived netlist is oracle-checked (`evidence/ground_truth_extra.csv`, `ground_truth_ctx.csv`) |
| TRACE's own examples and gate-level mutants | `third_party/trace_d57aa9a7/example_circuits`, `netlists/BASELINE` | Baseline trust |

## 2. Architectures (`scripts/flows.py`)

| Tag | Flow | Purpose |
|---|---|---|
| `norm` | `synth -top top` | Yosys default lowering: `alumacc` → `$macc_v2` → `maccmap`, `$alu` → Brent–Kung `$lcu`, then ABC |
| `booth` | `synth -top top -booth` | radix-4 Booth: Bewick architecture for unsigned; the "pre-encoded low-power" architecture (IEEE Access 2020) for signed |
| `tree` | `synth -top top -arith_tree` | 4:2 compressor carry-save tree, FMA fusion, one final adder |
| `*_pre` | the same flows with `-noabc` | pre-ABC netlist (the stage-wise reference) |
| `tree_nofma`, `tree_fa`, `tree_ripple`, `booth_lp` | explicit replicas of `synth` with one option changed | cause isolation |
| `norm_rep`, `tree_rep` | explicit replicas of the default flows | proves the replicas are faithful (byte-identical to `synth`) |

Builds:
- `MAIN` = clean main `e8db64c6` (unpatched).
- `PATCH` = PR #6231 `30b851e6`.

Only `compressor_tree.cc` differs between them (`evidence/provenance.txt`).

## 3. TRACE invocation

- **Modes:** `-mul`, `-mac` (template `F(2n+1) = A(n)·B(n) + S(2n)`), `-dot=2`, `-add`, `-gen`. Add `-s` for two's complement.
- **Template fit:**
  - `a*b + c*d + e`, `c − a*b` and any accumulator wider than 2W+1 have no template. They are marked `template_fit=NO` and classed UNSUPPORTED.
  - Signed `dot2` fits the documented `-dot=2 -s` invocation, but TRACE ignores `-s` there (R5 in `PRIOR_ART_PROSECUTION.md`).
- **Portfolio** (`scripts/trace_portfolio.py`):
  - Configurations, in order: `-dyn -p -c` (the paper's best), `-idx -p -c`, `-ipc -p -c`, `-igs -p -c`, `-ips -p -c`, `-igsm -p -c`.
  - Expected-correct netlists stop at the first `Correct`. Expected-incorrect netlists run every configuration, so that any `Correct` (a false pass) is caught.
  - Per-configuration timeouts: W ≤ 8: 60 s; W = 12: 90 s; W = 16: 120 s; W = 20: 180 s; W = 24: 240 s; W = 32: 300 s; W = 64: 900 s.
- **Memory:** 14 GiB cgroup limit, except `jobs_long.csv`, which uses 5 GiB (column `mem`).

## 4. Stages as executed

| Stage (`evidence/jobs_*.csv` → `trace_*_results.csv`) | Runs | What it tests |
|---|---|---|
| `baseline` | 29 | TRACE's own examples, including the paper's 64-bit WT_KS and behavioural MAC-64; wrong-mode, wrong-sign and gate mutants; `-gen`; default configuration |
| `stage1` (single configuration, 900 s) | 3 of 75 planned | Abandoned after three runs: single-configuration results were not a fair capability test (see `diag1`). The three completed runs are kept. Four runs still in flight when Stage 1 was stopped left header-only logs, now in `logs/trace/aborted_stage1/` and unused |
| `diag1` | 10 | Configuration sweep on the 8-bit Yosys multipliers; pre-ABC and Booth variants |
| `ctrlcrash` | 5 | Constant-fan-in crash, controlled both ways (`buffer` / `fold`) |
| `dotspec` | 7 | Signed versus unsigned DOT specification |
| `unsupported_probe` (60 s) | 5 | Representative template-misfit runs: `macw`, `msub`, `msubw` and `dot2c`, including a patched signed wide tree |
| `portfolio_w32` | `jobs_portfolio_w32b.csv`, 128 netlists; resumed with `jobs_portfolio_w32c.csv` (§5) | Families A and B plus MUT at W = 8..32 (see §5 for trims) |
| `stage2_pre` | 22 netlists (portfolio) | Pre-ABC half of the stage-wise check: B `norm_pre` at W = 8..32, `tree_pre` at W = 32, and every W = 64 pre-ABC netlist, including folded unsigned Booth and MAIN/PATCH signed trees |
| `cec_pre_post` (`scripts/cec_pre_post.sh`, ABC `&cec`) | 29 pairs + 1 missing netlist | ABC half of the stage-wise check. 26 pairs at W = 16/32/64, plus the signed low-power Booth at W = 8/16/32, added during isolation; all PASS |
| `contra` | 42 | `-p` / `-c` ablation on the patched pre-ABC signed MAC; folded control; single `AND(x,¬x)` insertions |
| `phaseopt_probe` (`jobs_xorself` + `jobs_mutx`) | 72 | Isolated `XNOR(x,x)` insertions, and the false-pass probe: MSB ⊕ c_msb mutants of the natural and folded netlists × 8 configurations |
| `mini` | 132 | W = 2..6 MAIN/PATCH trees × 8 configurations; W = 3/4 false-pass mutants |
| `ctx` | 220 | Causal graft of the six-gate Yosys context at 55 positions in 4 unrelated correct netlists × 4 configurations |
| `repro` | 4 | Minimal reproduction package (`evidence/trace_phaseopt_minimal_repro/`) |
| `long` | 6 | Longer budgets (900–1,800 s, 5 GiB) for key TIMEOUT claims |
| `sweep` | 104 | Onset sweep W = 4..16 (60 s; `-dyn -p -c` and `-idx -p -c` for Booth; `-idx -p -c` for `norm`) |
| `w64post` | 6 | Direct post-ABC TRACE at W = 64 with the paper's best configuration (trim 5) |
| `isolation` | 75 | Three sets. (a) **ABC-step isolation**: nine single ABC steps (`strash`, `balance`, `rewrite`, `refactor`, `dc2`, `resyn2`, `fraig`, `&dch`, and Yosys's script without mapping) applied to pre-ABC unsigned Booth W = 8 (folded), signed low-power Booth W = 8 and dot2 W = 16 (`scripts/abc_steps.sh`, `netlists/ABCSTEP/`). (b) **Pre-ABC signed low-power Booth**, raw and folded, W = 8/16/32. (c) **64-bit onset**: MAC (default and tree) and dot tree at W = 40/48/56 |
| `abcmap` | 40 | **Gate-library isolation**: `synth … -noabc; abc -g aig|gates|simple|<default>; aigmap`. The `default` replicas are byte-identical to the real post-ABC netlists (`netlists/ABCMAP/`) |
| `long64` | 2 | 64-bit pre-ABC default MAC and dot tree, 3,600 s, uncontended |
| `calib` | 2 | Uncontended 1,800 s reruns of two post-ABC TIMEOUT×6 results: unsigned default multiplier W = 32, unsigned dot2 W = 16 |

Every `Buggy` verdict is replayed by `scripts/replay_all.py` (`counterexamples/*.json`, `evidence/witness_summary.csv`).

## 5. Trims, with reasons

1. **Stage 1** (one configuration, 900 s per netlist) was replaced by the portfolio after `diag1`. The configuration alone changed verdicts: `-dyn` stalls where `-idx` proves in 2 s. Reporting single-configuration TIMEOUTs as tool limits would have been unfair to TRACE.
2. **Template misfits** (60 netlists in Family C, plus `dot2c`) were not run exhaustively through TRACE. Five representative probes establish TRACE's raw behaviour; running the rest adds no information about TRACE's algorithm. They are UNSUPPORTED by construction.
3. **Signed `dot2`** was dropped from the portfolio (`w32` → `w32b`) after `dotspec` showed that `-dot=2 -s` ignores `-s`: every signed dot run is a guaranteed false `Buggy` (R5).
4. **Portfolio reprioritisation** (`jobs_portfolio_w32c.csv`). After W = 16, the run was stopped and resumed. Resumption re-parses every completed configuration log and re-runs only incomplete ones; 5 in-flight logs were re-run. The new order is W = 32 before W = 20/24. At W = 32, the budget was cut to two configurations only where all six had timed out at W = 16:
   - `A_mul_s booth_lp`, `B_dot2_u norm` and `B_dot2_u tree` run with `-dyn -p -c;-ipc -p -c`;
   - the W = 32 RTL mutants run with `-dyn -p -c;-idx -p -c`.
5. **W = 64 post-ABC** netlists were not put through the portfolio. The post-ABC difficulty is already established at W ≤ 16 and is non-monotone in W. The W = 64 question that matters for the decision is whether the stage-wise route (pre-ABC TRACE plus `&cec`) holds at 64 bits, and `stage2_pre` and `cec_pre_post` answer it. Six direct post-ABC W = 64 runs (`w64post`, `-dyn -p -c` only, 900 s) record TRACE's stand-alone behaviour there: signed default multiplier, signed Booth, unsigned Booth, and the patched, unpatched and unsigned MAC trees.
6. **`B_dot2_u_w64 norm`**: Yosys synthesis timed out after 3,600 s, so the netlist does not exist (`SYNTH_TIMEOUT`).

## 6. Resource and timing caveats

- **Contention.** Up to 11 TRACE containers shared 8 CPUs at times (the portfolio plus side batches). Wall-clock budgets are therefore conservative. A TIMEOUT near the boundary may reflect contention. Conclusions rely on results far from the budget, or on consistent patterns across configurations and widths, or on the `long` reruns.
- **Host sleep and the WSL clock.** The host slept at least twice while runs were in flight: during a usage pause before about 11:28 PDT, and again around 17:45–21:15 PDT on 2026-09-24. The WSL2 VM clock lagged the host by about 7 h 25 min until it resynchronised at about 11:28.
  - Log timestamps before that moment are low by that amount.
  - 21 runs have wall times more than 60 s over budget, from the clock jump, the second sleep, or Docker start/teardown stalls under load. Their `wall_s` (and, for runs spanning the jump, TRACE's own "Elapsed time") are unreliable. They are flagged in `RESULTS.csv` (`timing_note`) and excluded from reported solve times.
  - Verdicts are unaffected: the in-container `timeout` counts sleep intervals, so a TIMEOUT still means the full budget.
  - Under the heaviest load, a few runs also show wall times far above their budget because the Docker client or container teardown stalled. For example, one 120 s run took 18 minutes between START and END. TRACE's own runtime is still capped by the in-container `timeout` (exit 137). Every row with wall time more than 60 s over budget is flagged in `RESULTS.csv` (`timing_note`) and excluded from reported solve times.
- **Oracle strength.** The oracle is exhaustive up to 20 input bits. Above that, "CORRECT" means no mismatch in 4,096 corner plus 16,384 random vectors.
  - The oracle and TRACE disagree only where TRACE is demonstrably wrong: the FALSE_PASS runs, where the oracle's mismatch is replayed, and the FALSE_FAIL runs, where TRACE's remainder is shown invalid.
  - Every oracle-CORRECT netlist that TRACE proves is independently confirmed. No oracle-INCORRECT netlist is proved by TRACE outside the `-p` defect.
