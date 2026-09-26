# TRACE `-p` (phase optimisation) soundness defect: minimal reproduction

TRACE commit `d57aa9a7` (binary sha256 `a5c249…4f92d`) was run in the hardened sandbox (`scripts/trace_run.sh`). All four runs are logged in `logs/trace/repro__*.log`.

## Files

| File | What it is | Independent oracle (`scripts/aigtool.py check`, exhaustive: 12 inputs, 4,096 vectors) |
|---|---|---|
| `mac_s_w3_patched_noabc_CORRECT.aig` / `.aag` | Unmodified Yosys output from PR #6231 (`30b851e6`, image `muxwise-yosys-patched:exp6`), `synth -top top -arith_tree -noabc; aigmap; opt_clean; write_aiger` of `y = a*b + c` with signed `a[2:0]`, `b[2:0]`, `c[5:0]` and `y[6:0]` (`rtl/mini/B_mac_s_w3.v`). 144 ANDs. sha256 `928704f3…15ef` | `mac:sss:3,3,6:7` → **CORRECT**, 0 / 4,096 mismatches |
| `mac_s_w3_zext_addend_mutant_INCORRECT.aig` / `.aag` | The same netlist with `y[6] ^= c[5]` (3 extra ANDs; `scripts/aigxform.py xorout … 6 24`). This is exactly `y = a*b + zext(c)`, the signed addend zero-extended: a textbook sign-extension bug. sha256 `4f814a9c…0e03` | `mac:sss:3,3,6:7` → **INCORRECT**, 2,048 / 4,096 mismatches (first: a=0, b=0, c=0x20 → got 0x20, expected 0x60). `mac:ssu:3,3,6:7` → 0 mismatches, so it computes a*b + zext(c) exactly |

The trigger in the correct netlist is gates 280 and 282, both `AND(¬c[5], c[5])` (literals 25, 24). They are combined as
`NOR(280, 282)` = `XNOR(c5, c5)` (= 1), which is XORed with `AND(p, ¬c5)`.

## Observed (TRACE `-mac -s … -no-steps`)

| Netlist | `-dyn -p -c` (paper's best configuration) | `-dyn -c` (no phase optimisation) |
|---|---|---|
| correct | `Result: Buggy`, `SP: {2} -64 + 64i24` → **FALSE_FAIL** | `Result: Correct` |
| mutant (wrong) | `Result: Correct` → **FALSE_PASS** | `Result: Buggy`, `SP: {1} -64n24` (valid; the witness replays) |

With `-p`, TRACE's remainder is off by ±2^6·c5 (mod 2^7) relative to the true remainder. The mutant's true error is exactly ∓2^6·c5, so the two cancel.

The same happens at W = 4 and W = 8 (`y8 ^= c7`, `y16 ^= c15`) and under `-dyn -p`, `-igs -p -c` and `-igs -p` (`evidence/trace_mini_results.csv`, `evidence/trace_phaseopt_probe_results.csv`).

## Controls (see INVESTIGATION_REPORT.md §7)

- **Constant folding.** `scripts/aigxform.py fold` removes `AND(x, ¬x)`. It returns the correct 8-bit netlist to `Correct` under all configurations and makes all 8-bit mutants `Buggy` under all 8 configurations.
- **Grafts.** The six-gate context `NOT XOR(AND(p,¬x)', XNOR(x,x))` was grafted at 55 gate positions in four unrelated correct netlists (`scripts/aigxform.py ctx`). Many grafts give spurious remainders of the form 2^k·x under `-p` configurations; under `-dyn -c`, none do (`evidence/trace_ctx_results.csv`).
- **Isolated patterns.** `AND(x, ¬x)` alone, or `XNOR(x, x)` alone, inserted at an output does not trigger the defect.

## Reproduce

```
python scripts/trace_batch.py evidence/jobs_repro.csv evidence/trace_repro_results.csv 1
python scripts/aigtool.py check evidence/trace_phaseopt_minimal_repro/mac_s_w3_zext_addend_mutant_INCORRECT.aig mac:sss:3,3,6:7
```

## Workarounds

- Use structural hashing or constant folding before TRACE (ABC `strash`, or `aigxform.py fold`).
- Or run without `-p`.

Post-ABC netlists never contain the pattern, because ABC strashes them.

## Reporting

This package is suitable for a bug report to the TRACE authors. The report should be sent by the user; nothing has been sent.
