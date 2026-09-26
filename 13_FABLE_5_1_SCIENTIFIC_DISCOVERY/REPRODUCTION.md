# Reproduction

Everything here ran on a 4-CPU / 15 GB Linux container (kernel 6.18, x86-64, gcc 13.3). No commercial tools, no GPU, no paid APIs.

## Tool versions (OBSERVED)

| Tool | Version / provenance | Integrity |
|---|---|---|
| Python | 3.11.15 | — |
| numpy | 2.4.6 | — |
| da4ml | 0.6.0 (PyPI wheel `da4ml-0.6.0-cp311-…manylinux_2_28_x86_64.whl`) | sha256 of the downloaded wheel is recorded in `evidence/` at the first commit of results |
| Yosys | 0.69 via YoWASP (PyPI `yowasp-yosys 0.69.0.0.post1233`, git sha1 9f75ca1f9). **ABC does not run inside YoWASP** (it exits silently), so ABC is native. | — |
| ABC | berkeley-abc master `ab2139ee0c418f54136deb4e8e89eeea3b87efc8`, built here with `make -j3 ABC_USE_NO_READLINE=1 abc` | binary md5 `f72a1da82220d6fdd0ded02dcd5a0e06` |
| Liberty | SKY130 HD `sky130_fd_sc_hd__tt_025C_1v80.lib` from The-OpenROAD-Project/OpenROAD-flow-scripts `master`, `flow/platforms/sky130hd/lib/` | md5 `12a1d61fcd2982fc8ba63993919c8ff8` |

## Commands

```bash
pip install da4ml==0.6.0 yowasp-yosys==0.69.0.0.post1233 numpy
git clone --depth 1 https://github.com/berkeley-abc/abc.git /tmp/abc_src   # then: git checkout ab2139e
make -C /tmp/abc_src -j3 ABC_USE_NO_READLINE=1 abc

cd 13_FABLE_5_1_SCIENTIFIC_DISCOVERY/experiments
python3 scripts/e1_run.py results/E1_ternary.jsonl          # E1 (adder counts; da4ml capped at 600 s per instance)
python3 scripts/e1_analyze.py results/E1_ternary.jsonl > results/E1_summary.md
python3 scripts/e2_run.py results/E2_p33 128 0.33 & python3 scripts/e2_run.py results/E2_p50 128 0.5   # E2 (Yosys -> AIG -> native ABC, iso-delay)
python3 scripts/e2_analyze.py results/E2_p33/E2_results.json results/E2_p50/E2_results.json > results/E2_summary.md
python3 scripts/wire_model.py > results/wire_model.txt      # analytic regime-V model (MODEL, not measurement)
python3 scripts/e1_hashed.py > results/E1_hashed.md         # strong (F) baseline: structurally hashed per-input trees
python3 scripts/e3_run.py results/E3                          # E3: regime-V components (TREE/GEN/NEG), iso-delay, SKY130
python3 scripts/e3_analyze.py results/E3/E3_results.json > results/E3_summary.md   # + model-adjusted table appended in-session
```

## Correctness checks built into the scripts (fail closed)

1. **Construction level (`hwlayer.py`).**
   - Every circuit is an explicit two-input add/sub op list.
   - It is executed by our own vectorised integer evaluator on random 8-bit vectors and compared with numpy `W @ x`.
   - da4ml circuits are translated from da4ml's op list by our own translator and are never executed by da4ml.
   - Negative controls: a flipped op sign, a flipped output sign, and two mutated da4ml ops. All are rejected.
2. **RTL/AIG level (`e2_run.py`).**
   - Yosys elaborates our Verilog to an AIG.
   - Our own ASCII-AIGER simulator checks the AIG against numpy on 64 vectors.
   - Negative control: a flipped weight is rejected.
3. **Mapped level.** ABC `cec` of every mapped netlist against its own AIG. Only the literal "Networks are equivalent" counts.

## Seeds

- E1 uses `numpy.random.default_rng(1000*seed + int(100*p0) + n)` with seeds {0, 1, 2}.
- E2 uses the same generator with seed 0, so the E2 matrices are exactly E1's seed-0 matrices.

## Known environment limits

- The egress policy blocks arxiv.org, dl.acm.org, ieeexplore.ieee.org, semanticscholar.org, openreview.net and huggingface.co. So there are no full-text papers and no real checkpoints; all weights are i.i.d. ternary.
- GitHub release assets outside this session's repository scope are refused, which is why OSS CAD Suite was not used.
