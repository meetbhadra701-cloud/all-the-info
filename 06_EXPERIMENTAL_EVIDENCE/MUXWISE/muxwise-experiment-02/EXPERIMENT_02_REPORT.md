# Experiment 02 — EDA Optimization Failure Discovery

Date: 2026-09-20  
Primary toolchain: official YosysHQ OSS CAD Suite 2026-09-21, Yosys 0.69+77, ABC 1.01  
Research-gap conclusion: **NO VIABLE NEW OPTIMIZATION GAP FOUND**

This experiment searched for consequential weaknesses in existing synthesis decisions. It did not implement a new optimization pass and does not resurrect MUXWISE.

## 1. Environment and version control

Experiment 1’s Docker image was located and left untouched. The primary Experiment 2 toolchain is newer: Yosys 0.69+77, git sha1 `9ff27d29c-dirty`, and ABC 1.01 compiled September 21, 2026. It came from the official OSS CAD Suite asset `oss-cad-suite-linux-x64-20260921.tgz`; SHA-256 and container/image provenance are in `logs/environment.txt`.

The current bundle was extracted only under this experiment’s `work/` directory. No system-wide installation was performed. No Liberty standard-cell library or OpenROAD installation was available, so all final quantitative results are generic mapped-cell counts, not physical area or timing.

Yosys 0.69 differs from Experiment 1’s 0.23: `share -force` is no longer supported, and `abc -fast` is no longer supported by the current `abc` pass. Unsupported `abc -fast` probes were excluded from the valid dataset. Final valid synthesis dataset: **136 runs**. Formal dataset: **7 checks, all PASS**.

## 2. Benchmarks and flows

Controlled synthetic designs:

- `add_chain` and `add_balanced`: eight-operand arithmetic trees at W=4, 8, 16, 32, 64.
- `mixed_left` and `mixed_grouped`: mixed add/subtraction networks at W=16, 32.
- `trim_wide` and `trim_narrow`: wide intermediates whose outputs use only low bits at W=8, 16, 32.
- `fir4` and `fir4_grouped`: signed four-tap constant-coefficient FIR datapath at W=4, 8, 16.
- `mapping_datapath`: muxed arithmetic/logic datapath at W=8, 16, 32.
- Current-Yosys resource-sharing reproduction from Experiment 1’s `multi_operator` at W=16.

External open-source sanity check:

- PicoRV32 `picorv32.v`, ISC licensed, fetched from the official GitHub repository. The exact source and license copy are in `reproducers/external/`.

Documented configurations tested:

- Normal `synth`.
- `synth -arith_tree`.
- Explicit `opt_share`, `share`, and `share -aggressive` where supported.
- Explicit `wreduce`.
- Same pre-ABC flow followed by `abc`, `abc -g simple`, and `abc -g gates`.
- Normal `synth -noshare` versus normal `synth`; this was not treated as disabling all sharing.

Every generated Yosys script is retained under `work/ys_scripts/`, and every run has a log under `logs/synthesis/`.

## 3. Formal verification

RTL alternatives were checked with Yosys equivalence. Mapped netlists were checked with a primary-output miter and `sat -prove trigger 0 -set-def-inputs`, avoiding fragile internal-name matching.

| Check class | Count | Result |
|---|---:|---|
| RTL add-chain versus balanced | 1 | PASS, W=8 |
| RTL width-trim alternative | 1 | PASS, W=8 |
| RTL FIR versus grouped sum | 1 | PASS, W=8 |
| Normal mapped add-chain versus RTL | 1 | PASS, W=4 |
| `arith_tree` mapped add-chain versus RTL | 1 | PASS, W=4, 44.16 s |
| Normal mapped FIR versus RTL | 1 | PASS, W=4 |
| `arith_tree` mapped FIR versus RTL | 1 | PASS, W=4 |

Wider arithmetic RTL proofs were not silently inferred from W=8. Structural results at larger widths are reported as synthesis observations; the formal coverage is exactly the manifest in `results/formal_manifest.csv`.

## 4. Family A — resource sharing

The current-Yosys reproduction confirms Experiment 1’s conclusion.

| Flow | Cells | Muxes | Arithmetic operators |
|---|---:|---:|---:|
| Early | 16 | 6 | 10 |
| `opt_share` | 16 | 10 | 6 |
| `share` | 16 | 6 | 10 |
| `share -aggressive` | 24 | 14 | 10 |
| `synth -noshare` | 642 | 137 | 0 |
| Normal `synth` | 642 | 137 | 0 |

`opt_share` recognized four common-operand opportunities. Default `share` considered only two cells and made no change. Aggressive SAT-based sharing removed operator cells but introduced equality/mux control overhead. Normal synthesis and `-noshare` converged to the same mapped structure.

**Disposition:** stop. No residual final implementation difference was found in this family.

## 5. Family B — arithmetic structure optimization

The current `arith_tree` pass creates a real, measurable, family-sensitive final mapped difference.

### Add-chain family

Counts are generic mapped cells. `delta` is `arith_tree - normal`.

| Width | Normal | `-arith_tree` | Delta | Signature equal? |
|---:|---:|---:|---:|:---:|
| 4 | 133 | 133 | 0 | No |
| 8 | 273 | 275 | +2 | No |
| 16 | 567 | 560 | -7 | No |
| 32 | 1151 | 1151 | 0 | No |
| 64 | 2361 | 2355 | -6 | No |

### Mixed arithmetic and FIR families

| Family | Width | Normal | `-arith_tree` | Delta |
|---|---:|---:|---:|---:|
| Mixed add/sub | 16 | 412 | 423 | +11 |
| Mixed add/sub | 32 | 836 | 888 | +52 |
| FIR4 | 4 | 145 | 151 | +6 |
| FIR4 | 8 | 270 | 330 | +60 |
| FIR4 | 16 | 518 | 716 | +198 |

The result reproduces across related circuits: `arith_tree` is slightly beneficial for some pure add-chain widths but consistently harmful for the tested mixed arithmetic and FIR family. The final structures differ, not merely RTLIL names or intermediate operator counts. The W=4 mapped add and FIR variants passed miter/SAT equivalence.

### Open-source datapath check

PicoRV32 normal synthesis and `synth -arith_tree` both produced **9,171 cells** with identical name-independent structural signatures. This is negative evidence against treating the synthetic arithmetic result as universal.

**Finding retained:** F-AT-01, a current-version technical observation. It is not promoted as a new research opportunity because `-arith_tree` is already a documented Yosys configuration, and the default flow already chooses a different implementation.

## 6. Family C — bit-width optimization

At W=8, 16, and 32, `trim_wide` and `trim_narrow` had different early structural signatures. However:

- Early generic cell counts were both 3: two `$add` cells and one `$mul` cell.
- Explicit `wreduce` made no observable change in this setup.
- Normal synthesis mapped both to identical final cell counts and structural signatures: 204, 830, and 3253 cells for W=8, 16, and 32 respectively.
- The W=8 RTL alternatives passed formal equivalence.

**Disposition:** not a surviving finding. The width-related difference disappears in the normal downstream flow.

## 7. Family D — logic mapping sensitivity

The documented ABC gate-set restrictions produced final differences in `mapping_datapath`:

| Width | Default ABC | `abc -g simple` | `abc -g gates` |
|---:|---:|---:|---:|
| 8 | 178 | 198 | 207 |
| 16 | 378 | 474 | 432 |
| 32 | 776 | 844 | 889 |

These are legitimate mapped differences, but they are expected consequences of documented gate-type restrictions. They are not evidence of a missing optimization algorithm. No Liberty area or timing claim is made.

## 8. Surviving finding record

### F-AT-01

**Optimization family:** Arithmetic structure optimization.

**Exact trigger:** Compare `synth -top TOP` with documented `synth -top TOP -arith_tree` on add chains, mixed add/sub networks, and a FIR datapath.

**Observed behavior:** The optional arithmetic-tree pass changes final mapped connectivity. It reduces generic mapped cells for add-chain W=16 and W=64, is neutral at W=4 and W=32, and increases cells for all tested mixed arithmetic and FIR widths.

**Expected or alternative behavior:** A structure-aware arithmetic optimization would ideally not make a family-dependent decision without regard to downstream cost. Here the alternative is real and functionally equivalent, but the behavior is already exposed as a documented pass configuration.

**Formal evidence:** Seven final checks passed. In particular, W=4 normal and arithmetic-tree mapped add/FIR outputs passed miter/SAT equivalence. RTL alternatives passed at W=8.

**Structural evidence:** Name-independent connectivity signatures differ for synthetic arithmetic cases. PicoRV32 signatures are identical under both flows.

**Quantitative evidence:** Add-chain counts `(normal, arith_tree)` are `(133,133)`, `(273,275)`, `(567,560)`, `(1151,1151)`, and `(2361,2355)` for W=4, 8, 16, 32, 64. Mixed add/sub is 412 versus 423 at W=16 and 836 versus 888 at W=32. FIR is 145 versus 151, 270 versus 330, and 518 versus 716 at W=4, 8, 16.

**Affected tool/version:** Yosys 0.69+77 and ABC 1.01 from the official current OSS CAD Suite bundle.

**Current-version status:** Reproduced in the current bundle; not a 0.23-only result.

**Existing built-in alternatives:** `synth -arith_tree`, normal `synth`, `arith_tree -strategy`, and `arith_tree -final` are documented controls. Default synthesis already avoids this particular harmful setting on the tested FIR/mixed families.

**Strongest reason this is not a new research opportunity:** The behavior is a documented, user-selectable synthesis policy, not an unaddressed capability. The experiment found no timing or physical-area consequence and no evidence that a new optimizer is needed to perform a missing transformation.

**Next experiment required:** Only if this policy question remains interesting, run both configurations through a fixed Liberty/OpenROAD flow with timing constraints on a larger arithmetic benchmark set. That is validation work, not evidence yet of a new algorithmic gap.

## 9. Exact questions

**Q1. Which optimization families were tested?** Resource sharing, arithmetic structure optimization, bit-width reduction, and ABC logic-mapping sensitivity.

**Q2. How many controlled experiments completed?** 136 valid Yosys synthesis runs, 7 formal checks, and 2 PicoRV32 current-flow runs. Unsupported `abc -fast` probes were excluded from the valid count.

**Q3. Which comparisons produced identical final implementations?** Resource-sharing normal versus `-noshare`; wide versus narrow width-trim designs after normal synthesis; normal versus explicit pre-ABC default mapping; and PicoRV32 normal versus `-arith_tree`.

**Q4. Which produced different final implementations?** `-arith_tree` versus default on synthetic add/mixed/FIR circuits, and documented `abc -g simple`/`-g gates` restrictions versus default ABC.

**Q5. Which differences were actually meaningful?** The arithmetic-tree differences were the strongest: they survived final mapping and repeated across related circuit families. They remain generic-cell observations, not physical PPA results.

**Q6. Did any finding reproduce across multiple related circuits?** Yes. F-AT-01 reproduced across five add-chain widths, two mixed-arithmetic widths, and three FIR widths. Its direction was family-sensitive, not universal.

**Q7. Which findings disappeared after applying existing built-in optimization passes?** Resource-sharing differences and width-trim differences disappeared in normal synthesis. The basic arithmetic source-tree differences also disappeared under default synthesis; only the explicit `-arith_tree` policy produced a different final map.

**Q8. Which findings remain in the current Yosys version, if tested?** F-AT-01 remains as a documented configuration sensitivity in Yosys 0.69+77. It is not evidence of a missing transformation.

**Q9. What would require physical-design validation?** Any claim about area, routed delay, congestion, critical-path impact, or select-arrival sensitivity. No Liberty or OpenROAD flow was available here.

**Q10. Is there evidence of a problem that could justify developing a new EDA algorithm?** No. There is one reproducible technical behavior worth measuring physically, but it is already exposed by documented built-in controls. The experiment found no viable new optimization gap.

## 10. Finding ranking

1. **F-AT-01 — arithmetic-tree configuration sensitivity:** strongest evidence; current-version, reproduced across related synthetic families, survives final mapping, formally checked at small width. Not a new algorithmic opportunity because the control already exists.
2. **ABC gate-set sensitivity:** reproducible across widths, but expected behavior from documented restrictions and not a failure.
3. **Width-reduction intermediate difference:** structurally observable before mapping, but eliminated downstream; not a surviving finding.
4. **Resource-sharing alternatives:** recognized by built-in passes and converged in normal synthesis; no surviving gap.

