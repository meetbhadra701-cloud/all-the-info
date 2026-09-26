# Reproduction

Everything here was executed on 2026-09-24. The host was Windows 11 with WSL2 Ubuntu 26.04 and Docker Desktop 29.8.0, with 8 CPUs.
All paths are relative to this folder unless stated.

## 1. Tools and exact builds (`evidence/provenance.txt`)

| Role | Build | Identity |
|---|---|---|
| Yosys, clean main ("MAIN", unpatched) | local image `muxwise-yosys-current:exp6`, binary `/build/yosys` | source `e8db64c609c7ae4574e66bbd475f5f10f36d7a31` (clean tree); binary sha256 `9733cb78b13b210476f1ce68507895685d9d086576f8446523b852e806f2f136` |
| Yosys, PR #6231 ("PATCH") | local image `muxwise-yosys-patched:exp6`, binary `/build/yosys` | source `30b851e63ff071578cda4e1e49eccd367f7881d9` (branch `exp6-fma-fix`, clean tree); binary sha256 `1632d7d70a88817a4224155aa9f8a6638f83498bf6641ed9d8413dcce5417da3` |
| TRACE | `third_party/trace_d57aa9a7/trace` (**not redistributable**; see its NOTICE) | repo `github.com/jan-kl/trace`, commit `d57aa9a7e2f87c2813bc3e8176e2fb5e5b47b43f`; git blob `76cb3f383dc52defe36adca414d0aee6dfe08ee7`; sha256 `a5c249049fa72176866a8f0286b4a24c3503775af730fc0012db575a0ea4f92d`; static x86-64 ELF |
| Oracle | `scripts/aigtool.py` (own code, Python 3.14, no dependencies) | bit-parallel AIGER evaluation against exact integer reference arithmetic |
| ABC, for `&cec` pre ≡ post (`cec_pre_post.sh`) and single-step isolation (`abc_steps.sh`) | local OSS CAD Suite, `…/muxwise-experiment-02/work/oss-cad-suite/bin/yosys-abc` (no network) | `UC Berkeley, ABC 1.01 (compiled Sep 21 2026)`; binary sha256 `da8621c9fb2fa30a7ac243c91948eb892b4e74c7c0ebc1f28a89edf556e12ad9`; bundled with Yosys `0.69+77 (9ff27d29c-dirty)`. Only ABC is used from this suite; every netlist was synthesised by the MAIN/PATCH images above (`scripts/abc_provenance.sh`) |

Both Yosys images report `Yosys 0.69+ (git sha1 e8db64c60 …)`. The patched build still prints the base commit in its version string. The two binaries have different sha256 hashes, and the only source difference is the `kernel/compressor_tree.cc` correction hunk (`evidence/provenance.txt`).

## 2. TRACE sandbox

TRACE runs only inside `trace-sandbox:d57aa9a7`, built with `scripts/trace_build_sandbox.sh`:
- Base: the **local** `alpine:3.20` image.
- Build flags: `--pull=false --network none`.
- The binary is copied in, set to mode 0555, and runs as user 65534.

`scripts/trace_run.sh` executes every run with:

```
docker run --rm --network none --read-only --cap-drop ALL --security-opt no-new-privileges \
  --pids-limit 64 --memory 14g --memory-swap 14g --cpus 1 --user 65534:65534 \
  --tmpfs /tmp:rw,noexec,nosuid,size=64m -v <this folder>:/data:ro --pull never \
  --entrypoint /bin/sh trace-sandbox:d57aa9a7 -c 'timeout -s KILL <T> /usr/bin/time -v /opt/trace/trace <args>; …'
```

Verdicts are parsed only from TRACE's `Result:` line (`Correct` / `Buggy`). A `Buggy` result includes the non-zero remainder polynomial (`SP: {N} …`). `scripts/remainder_witness.py` turns that polynomial into a concrete input and replays it on the original netlist.

Memory is taken from cgroup `memory.peak`. BusyBox `time -v` over-reports max RSS by about 4×.

## 3. Pipeline (run in this order)

Windows-side Python scripts call WSL through `wsl.exe -d Ubuntu-26.04`. Run bash scripts from WSL, or from Git Bash with `MSYS_NO_PATHCONV=1`.

**Designs, synthesis, ground truth**

1. `python scripts/gen_rtl.py` generates `rtl/*.v` and `rtl/manifest.csv`: 102 designs, each with an independent reference spec string.
2. `python scripts/flows.py` writes one Yosys script per (build, design, architecture) into `netlists/<BUILD>/*.ys`, plus `netlists/jobs_<BUILD>.txt`.
3. `bash scripts/run_synth.sh` runs every script inside the matching local Yosys image with `--network none`. Logs go to `netlists/<BUILD>/*.log` and the summary to `logs/synth_<BUILD>.csv`. The 64-bit pre-ABC netlists come from `run_synth_extra.sh`; the W = 2..6 mini MACs from `run_synth_mini.sh` (`rtl/mini/`); the W = 4..16 onset sweep from `run_synth_sweep.sh` (`rtl/sweep/`).
4. `python scripts/validate_netlists.py` writes `evidence/ground_truth.csv`: a port-order audit against the `.map` files, plus an oracle check that is exhaustive at ≤ 20 input bits and otherwise uses 4,096 corner and 16,384 random vectors. `python scripts/validate_extra.py` writes `evidence/ground_truth_extra.csv`, covering the netlists created later and every `netlists/CONTROL` file. The mini, sweep and graft sets are validated inline; the commands are in the transcript, and their outputs are `evidence/ground_truth_{mini,sweep,ctx}.csv`.

**TRACE runs**

5. `bash scripts/trace_build_sandbox.sh` builds the TRACE sandbox image.
6. Baseline on TRACE's own examples: `python scripts/trace_batch.py evidence/jobs_baseline.csv evidence/trace_baseline_results.csv 3`.
7. Diagnostics and controls, each run as `python scripts/trace_batch.py evidence/jobs_<X>.csv evidence/trace_<X>_results.csv <par>`, for X in:
   - `diag1`, `ctrl_crash`, `dotspec`, `unsupported_probe`;
   - `contra`, `phaseopt_probe`, `mini`, `ctx`, `repro`;
   - `long` (uses the optional `mem` column);
   - `sweep`.
8. Portfolio for Families A/B and MUT at W ≤ 32: `python scripts/make_portfolio_jobs.py`, then `python scripts/trace_portfolio.py evidence/jobs_portfolio_w32b.csv evidence/trace_portfolio_w32_results.csv 5`. It was resumed with `jobs_portfolio_w32c.csv` (see `EXPERIMENTAL_MATRIX.md` §5; resuming re-parses complete logs).
9. Stage-wise check, pre-ABC half: `python scripts/make_stage2_jobs.py`, then `python scripts/trace_portfolio.py evidence/jobs_stage2_pre.csv evidence/trace_stage2_pre_results.csv 3`. ABC half: `bash scripts/cec_pre_post.sh` (local ABC from the OSS CAD Suite; `evidence/cec_pre_post.csv`).

**Cause isolation and onset**

- `bash scripts/run_synth_lppre.sh` synthesises the pre-ABC low-power Booth. `bash scripts/run_synth_onset64.sh` synthesises W = 40/48/56. `bash scripts/run_synth_abcmap.sh` produces the gate-library variants; the `default` variant is byte-identical to the main post-ABC netlist.
- `bash scripts/abc_steps.sh <pre-ABC aig>…` applies single ABC steps with the local ABC.
- Then run `python scripts/trace_batch.py` on `evidence/jobs_{isolation,abcmap,long64,calib,w64post}.csv`.
- `bash scripts/diag_traj_batch.sh` records polynomial-size trajectories (`logs/diag/*.traj.csv`).

**Replay and classification**

10. `python scripts/replay_all.py` replays every `Buggy` verdict. It writes `counterexamples/<job_id>.json` and `evidence/witness_summary.csv`.
11. `python scripts/classify.py` writes `RESULTS.csv` (one row per run) and `evidence/portfolio_summary.csv` (one row per netlist and mode).
12. `python scripts/finalize.py` runs steps 10–11, then `replay_false_pass.py` (the oracle counterexample for every FALSE_PASS) and `make_tables.py` (`evidence/report_tables.md`), and splices the tables into `INVESTIGATION_REPORT.md`.

## 4. Deviations and known limitations of the harness

- **Absolute paths.** Scripts assume this folder's absolute path in `trace_batch.py` (`WSL_RUN`), `cec_pre_post.sh` (the ABC path inside the Codex OSS CAD Suite) and `record_provenance.sh`. Adjust them if the folder moves.
- **Contention.** Up to 11 TRACE containers shared 8 CPUs at times. See `EXPERIMENTAL_MATRIX.md` §6.
- **WSL clock and host sleep.** The WSL clock lagged the host by about 7 h 25 min until it resynchronised at about 11:28 PDT, so log timestamps before that are low by that amount. The host also slept again later. The 21 runs whose wall time exceeds their budget by more than 60 s are flagged in `RESULTS.csv` (`timing_note`); their verdicts are unaffected, because TRACE was bounded by the in-container `timeout`.
- **Lost CEC row.** The first `cec_pre_post.sh` run lost one row, `MAIN A_mul_u_w16 booth`, to concurrent appends on the Windows filesystem. That row was re-run alone (PASS, 1.2 s), and the script now writes one file per row.
- **Oracle strength.** The oracle is exhaustive only up to 20 input bits. Above that, "CORRECT" means no mismatch in about 20,000 corner and random vectors, which is not a proof. `INVESTIGATION_REPORT.md` states where a conclusion depends on it.
- **No redistribution.** The TRACE binary and its example circuits are not redistributable (no license in the repository). `third_party/trace_d57aa9a7/` must not be shared.
