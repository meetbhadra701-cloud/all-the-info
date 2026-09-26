### Family A — `y = a*b` (portfolio over six configurations, plus the longer/uncontended reruns; best outcome, solving configuration, TRACE time)

Unsigned `booth_pre` (raw) crashes TRACE at every width (constant-fan-in AND); the folded copy is the same function.

| netlist | W=8 | W=12 | W=16 | W=20 | W=24 | W=32 | W=64 |
|---|---|---|---|---|---|---|---|
| unsigned · default synth (post-ABC) | PASS (idx, <1 s) | PASS (idx, <1 s) | PASS (idx, 23 s) | TIMEOUT ×6 (≤180 s) | TIMEOUT ×6 (≤240 s) | TIMEOUT ×6 (≤300 s) | – |
| unsigned · synth -booth (post-ABC) | TIMEOUT ×7 (≤1800 s) | TIMEOUT ×6 (≤90 s) | PASS (dyn, 1 s) | PASS (dyn, 3 s) | PASS (dyn, 6 s) | PASS (dyn, 21 s) | PASS (dyn, 260 s) |
| unsigned · default, pre-ABC | PASS (dyn, <1 s) | – | PASS (dyn, <1 s) | – | – | PASS (dyn, 11 s) | PASS (dyn, 264 s) |
| unsigned · booth, pre-ABC, const-folded | PASS (dyn, <1 s) | – | PASS (dyn, <1 s) | – | – | PASS (dyn, 23 s) | PASS (dyn, 294 s) |
| signed · default synth (post-ABC) | PASS (idx, <1 s) | PASS (dyn, <1 s) | PASS (dyn, 1 s) | PASS (dyn, 2 s) | PASS (dyn, 16 s) | PASS (dyn, 15 s) | PASS (dyn, 162 s) |
| signed · synth -booth (post-ABC) | PASS (dyn, <1 s) | PASS (dyn, <1 s) | PASS (dyn, <1 s) | PASS (dyn, 3 s) | PASS (dyn, 5 s) | PASS (dyn, 25 s) | PASS (dyn, 270 s) |
| signed · booth -lowpower (post-ABC) | TIMEOUT ×7 (≤1800 s) | – | TIMEOUT ×6 (≤120 s) | – | – | TIMEOUT ×2 (≤300 s) | – |
| signed · default, pre-ABC | PASS (dyn, <1 s) | – | PASS (dyn, <1 s) | – | – | PASS (dyn, 15 s) | PASS (dyn, 152 s) |
| signed · booth, pre-ABC | PASS (dyn, <1 s) | – | PASS (dyn, <1 s) | – | – | PASS (dyn, 23 s) | PASS (dyn, 467 s) |

### Family B — fused arithmetic (MAIN = unpatched; PATCH = PR #6231; portfolio plus longer/uncontended reruns)

MAIN signed `a*b+c` trees (except `-no-fma`) are INCORRECT by the oracle (the real Yosys defect): FAIL is the correct outcome there. Signed `dot2` is excluded: `-dot=2 -s` ignores `-s` (every run a FALSE_FAIL; `dotspec` stage).

| netlist | W=8 | W=12 | W=16 | W=24 | W=32 | W=64 |
|---|---|---|---|---|---|---|
| MAIN a*b+c u · default (post-ABC) | PASS (idx, <1 s) | PASS (idx, 1 s) | PASS (ipc, 16 s) | TIMEOUT ×6 (≤240 s) | TIMEOUT ×6 (≤300 s) | – |
| MAIN a*b+c u · default, pre-ABC | PASS (dyn, <1 s) | – | PASS (dyn, <1 s) | – | PASS (dyn, 8 s) | PASS (dyn, 348 s) |
| MAIN a*b+c u · arith_tree (post-ABC) | PASS (idx, <1 s) | PASS (ipc, <1 s) | PASS (idx, t=n/a) | PASS (ipc, 16 s) | PASS (ipc, 269 s) | TIMEOUT ×1 (≤900 s) |
| MAIN a*b+c u · arith_tree, pre-ABC | PASS (dyn, <1 s) | – | PASS (dyn, 1 s) | – | PASS (dyn, 9 s) | PASS (dyn, 188 s) |
| MAIN a*b+c u · arith_tree -no-fma | PASS (idx, <1 s) | – | PASS (ipc, 17 s) | – | – | – |
| MAIN a*b+c u · arith_tree -strategy fa | PASS (idx, <1 s) | – | PASS (idx, 6 s) | – | – | – |
| MAIN a*b+c u · arith_tree -final ripple | PASS (idx, <1 s) | – | PASS (idx, 7 s) | – | – | – |
| MAIN a*b+c s · default (post-ABC) | PASS (idx, 1092 s) | PASS (dyn, <1 s) | PASS (dyn, 2 s) | PASS (dyn, 15 s) | PASS (dyn, 20 s) | – |
| MAIN a*b+c s · default, pre-ABC | PASS (dyn, <1 s) | – | PASS (dyn, <1 s) | – | PASS (dyn, 13 s) | – |
| MAIN a*b+c s · arith_tree (post-ABC) | FAIL (igsm, <1 s) | FAIL (igsm, <1 s) | FAIL (ipc, <1 s) | FAIL (igsm, 2 s) | FAIL (idx, 10 s) | TIMEOUT ×1 (≤900 s) |
| MAIN a*b+c s · arith_tree, pre-ABC | FAIL (igs, <1 s) | – | FAIL (dyn, <1 s) | – | FAIL (dyn, 9 s) | FAIL (dyn, 209 s) |
| MAIN a*b+c s · arith_tree -no-fma | TIMEOUT ×6 (≤60 s) | – | PASS (dyn, 2 s) | – | – | – |
| MAIN a*b+c s · arith_tree -strategy fa | FAIL (idx, <1 s) | – | FAIL (idx, <1 s) | – | – | – |
| MAIN a*b+c s · arith_tree -final ripple | FAIL (igsm, <1 s) | – | FAIL (igsm, <1 s) | – | – | – |
| PATCH a*b+c s · arith_tree (post-ABC) | PASS (dyn, <1 s) | PASS (ipc, <1 s) | PASS (dyn, <1 s) | PASS (ipc, 2 s) | PASS (dyn, 63 s) | TIMEOUT ×1 (≤900 s) |
| PATCH a*b+c s · arith_tree, pre-ABC | **FALSE_FAIL** ×2, TIMEOUT ×4 | – | PASS (dyn, <1 s) | – | PASS (dyn, 8 s) | PASS (dyn, 217 s) |
| PATCH a*b+c s · arith_tree -strategy fa | PASS (dyn, 21 s) | – | PASS (dyn, 5 s) | – | – | – |
| PATCH a*b+c s · arith_tree -final ripple | PASS (dyn, <1 s) | – | PASS (dyn, <1 s) | – | – | – |
| MAIN a*b+c*d u · default (post-ABC) | PASS (idx, 9 s) | TIMEOUT ×6 (≤90 s) | TIMEOUT ×6 (≤120 s) | TIMEOUT ×6 (≤240 s) | TIMEOUT ×2 (≤300 s) | – |
| MAIN a*b+c*d u · default, pre-ABC | PASS (dyn, <1 s) | – | PASS (dyn, 2 s) | – | PASS (dyn, 32 s) | – |
| MAIN a*b+c*d u · arith_tree (post-ABC) | PASS (idx, <1 s) | PASS (ipc, 32 s) | TIMEOUT ×6 (≤120 s) | TIMEOUT ×6 (≤240 s) | TIMEOUT ×2 (≤300 s) | – |
| MAIN a*b+c*d u · arith_tree, pre-ABC | PASS (dyn, <1 s) | – | PASS (dyn, 2 s) | – | PASS (dyn, 29 s) | PASS (dyn, 308 s) |
| MAIN a*b+c*d u · arith_tree -no-fma | PASS (idx, 13 s) | – | TIMEOUT ×6 (≤120 s) | – | – | – |
| MAIN a*b+c*d u · arith_tree -strategy fa | PASS (idx, 2 s) | – | TIMEOUT ×6 (≤120 s) | – | – | – |
| MAIN a*b+c*d u · arith_tree -final ripple | PASS (idx, <1 s) | – | TIMEOUT ×6 (≤120 s) | – | – | – |

### Onset sweep (`y = a*b`, W = 4..16, 60 s per configuration)

| netlist | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 | 13 | 14 | 15 | 16 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| A_mul_u norm | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| A_mul_u booth | ✓ | ✓ | ✓ | ✓ | ⏱ | ⏱ | ⏱ | ✓ | ⏱ | ✓ | ✓ | ✓ | ✓ |
| A_mul_s norm | ✓ | ✓ | ✓ | ✓ | ✓ | ⏱ | ✓ | ✓ | ✓ | ⏱ | ✓ | ✓ | ✓ |
| A_mul_s booth | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| A_mul_s booth_lp | ✓ | ✓ | ✓ | ⏱ | ⏱ | ⏱ | ⏱ | ⏱ | ⏱ | ⏱ | ⏱ | ⏱ | ⏱ |

✓ = proved by at least one of the configurations run; ⏱ = every configuration timed out.

### Stage-wise certification: TRACE on the pre-ABC netlist + ABC `&cec` pre ≡ post

| design (build) | W | TRACE on pre-ABC netlist | `&cec` pre≡post | TRACE directly on post-ABC |
|---|---|---|---|---|
| A_mul_s_w8 booth_lp (MAIN) | 8 | PASS (dyn, <1 s) | PASS (1.0 s) | TIMEOUT ×7 (≤1800 s) |
| A_mul_s_w16 booth (MAIN) | 16 | PASS (dyn, <1 s) | PASS (0.5 s) | PASS (dyn, <1 s) |
| A_mul_s_w16 booth_lp (MAIN) | 16 | PASS (idx, <1 s) | PASS (1.3 s) | TIMEOUT ×6 (≤120 s) |
| A_mul_s_w16 norm (MAIN) | 16 | PASS (dyn, <1 s) | PASS (0.5 s) | PASS (dyn, 1 s) |
| A_mul_u_w16 booth (MAIN) | 16 | PASS (dyn, <1 s) | PASS (1.2 s) | PASS (dyn, 1 s) |
| A_mul_u_w16 norm (MAIN) | 16 | PASS (dyn, <1 s) | PASS (0.6 s) | PASS (idx, 23 s) |
| B_dot2_u_w16 norm (MAIN) | 16 | PASS (dyn, 2 s) | PASS (0.7 s) | TIMEOUT ×6 (≤120 s) |
| B_dot2_u_w16 tree (MAIN) | 16 | PASS (dyn, 2 s) | PASS (0.3 s) | TIMEOUT ×6 (≤120 s) |
| B_mac_s_w16 tree (PATCH) | 16 | PASS (dyn, <1 s) | PASS (0.3 s) | PASS (dyn, <1 s) |
| B_mac_u_w16 norm (MAIN) | 16 | PASS (dyn, <1 s) | PASS (0.3 s) | PASS (ipc, 16 s) |
| B_mac_u_w16 tree (MAIN) | 16 | PASS (dyn, 1 s) | PASS (0.2 s) | PASS (idx, t=n/a) |
| A_mul_s_w32 booth (MAIN) | 32 | PASS (dyn, 23 s) | PASS (1.6 s) | PASS (dyn, 25 s) |
| A_mul_s_w32 booth_lp (MAIN) | 32 | PASS (dyn, 10 s) | PASS (49.3 s) | TIMEOUT ×2 (≤300 s) |
| A_mul_s_w32 norm (MAIN) | 32 | PASS (dyn, 15 s) | PASS (1.2 s) | PASS (dyn, 15 s) |
| A_mul_u_w32 booth (MAIN) | 32 | PASS (dyn, 23 s) | PASS (0.8 s) | PASS (dyn, 21 s) |
| A_mul_u_w32 norm (MAIN) | 32 | PASS (dyn, 11 s) | PASS (1.5 s) | TIMEOUT ×6 (≤300 s) |
| B_dot2_u_w32 norm (MAIN) | 32 | PASS (dyn, 32 s) | PASS (44.2 s) | TIMEOUT ×2 (≤300 s) |
| B_dot2_u_w32 tree (MAIN) | 32 | PASS (dyn, 29 s) | PASS (4.4 s) | TIMEOUT ×2 (≤300 s) |
| B_mac_s_w32 tree (PATCH) | 32 | PASS (dyn, 8 s) | PASS (0.5 s) | PASS (dyn, 63 s) |
| B_mac_u_w32 norm (MAIN) | 32 | PASS (dyn, 8 s) | PASS (0.5 s) | TIMEOUT ×6 (≤300 s) |
| B_mac_u_w32 tree (MAIN) | 32 | PASS (dyn, 9 s) | PASS (0.4 s) | PASS (ipc, 269 s) |
| A_mul_s_w64 booth (MAIN) | 64 | PASS (dyn, 467 s) | PASS (28.5 s) | PASS (dyn, 270 s) |
| A_mul_s_w64 norm (MAIN) | 64 | PASS (dyn, 152 s) | PASS (126.5 s) | PASS (dyn, 162 s) |
| A_mul_u_w64 booth (MAIN) | 64 | PASS (dyn, 294 s) | PASS (48.0 s) | PASS (dyn, 260 s) |
| A_mul_u_w64 norm (MAIN) | 64 | PASS (dyn, 264 s) | PASS (46.3 s) | – |
| B_dot2_u_w64 norm (MAIN) | 64 | – | no netlist (synthesis timeout) | – |
| B_dot2_u_w64 tree (MAIN) | 64 | PASS (dyn, 308 s) | PASS (662.4 s) | – |
| B_mac_s_w64 tree (PATCH) | 64 | PASS (dyn, 217 s) | PASS (3.7 s) | TIMEOUT ×1 (≤900 s) |
| B_mac_u_w64 norm (MAIN) | 64 | PASS (dyn, 348 s) | PASS (4.5 s) | – |
| B_mac_u_w64 tree (MAIN) | 64 | PASS (dyn, 188 s) | PASS (5.4 s) | TIMEOUT ×1 (≤900 s) |

### Phase-optimisation defect: natural netlists and mutants (P PASS, F FAIL, FF FALSE_FAIL, FP FALSE_PASS, t TIMEOUT)

Mutants `…y{MSB}xor{lit}`: lit = sign bit of c (even literal) gives exactly `a*b + zext(c)`; odd literal = its complement; `xor1` = unconditional MSB flip. `_folded` = constant-folded (pattern removed).

| netlist (oracle) | `-dyn -p -c` | `-dyn -p` | `-igs -p -c` | `-igs -p` | `-idx -p -c` | `-dyn -c` | `-dyn` | `-igs -c` | `-igs` | `-idx -c` | `-idx` | `-idx -p` |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| CONTROL/MUTX_PATCH_B_mac_s_w3__tree_pre__y6xor24 (INCO) | **FP** | **FP** | **FP** |  | F | F | F | F |  | F |  |  |
| CONTROL/MUTX_PATCH_B_mac_s_w3__tree_pre__y6xor25 (INCO) | F | F | F |  | F | F | F | F |  | F |  |  |
| CONTROL/MUTX_PATCH_B_mac_s_w4__tree_pre__y8xor32 (INCO) | F | **FP** | **FP** |  | F | F | F | F |  | F |  |  |
| CONTROL/MUTX_PATCH_B_mac_s_w4__tree_pre__y8xor33 (INCO) | F | F | F |  | F | F | F | F |  | F |  |  |
| CONTROL/MUTX_PATCH_B_mac_s_w8__tree_pre__y16xor1 (INCO) | F | F | F | F |  | F | F | F | F |  |  |  |
| CONTROL/MUTX_PATCH_B_mac_s_w8__tree_pre__y16xor64 (INCO) | **FP** | **FP** | **FP** | **FP** |  | F | F | F | F |  |  |  |
| CONTROL/MUTX_PATCH_B_mac_s_w8__tree_pre__y16xor65 (INCO) | F | F | F | F |  | F | F | F | F |  |  |  |
| CONTROL/MUTX_PATCH_B_mac_s_w8__tree_pre_folded__y16xor1 (INCO) | F | F | F | F |  | F | F | F | F |  |  |  |
| CONTROL/MUTX_PATCH_B_mac_s_w8__tree_pre_folded__y16xor64 (INCO) | F | F | F | F |  | F | F | F | F |  |  |  |
| CONTROL/MUTX_PATCH_B_mac_s_w8__tree_pre_folded__y16xor65 (INCO) | F | F | F | F |  | F | F | F | F |  |  |  |
| CONTROL/PATCH_B_mac_s_w8__tree_pre_folded (CORR) | P |  | P |  |  |  |  |  |  |  |  |  |
| MAIN/B_mac_u_w8__tree_pre (CORR) |  | P |  |  |  | P | P |  |  |  |  |  |
| MINI_MAIN/B_mac_s_w2__tree_pre (INCO) | F | F | F |  | F | F | F | F |  | F |  |  |
| MINI_MAIN/B_mac_s_w3__tree_pre (INCO) | F | F | F |  | F | F | F | F |  | F |  |  |
| MINI_MAIN/B_mac_s_w4__tree_pre (INCO) | F | F | F |  | F | F | F | F |  | F |  |  |
| MINI_MAIN/B_mac_s_w5__tree_pre (INCO) | F | F | F |  | F | F | F | F |  | F |  |  |
| MINI_MAIN/B_mac_s_w6__tree_pre (INCO) | F | F | F |  | F | F | F | F |  | F |  |  |
| MINI_PATCH/B_mac_s_w2__tree_pre (CORR) | P | P | P |  | P | P | P | P |  | P |  |  |
| MINI_PATCH/B_mac_s_w3__tree_pre (CORR) | **FF** | P | **FF** |  | P | P | P | P |  | P |  |  |
| MINI_PATCH/B_mac_s_w4__tree_pre (CORR) | P | **FF** | **FF** |  | P | P | P | P |  | P |  |  |
| MINI_PATCH/B_mac_s_w5__tree_pre (CORR) | P | P | P |  | P | P | P | P |  | P |  |  |
| MINI_PATCH/B_mac_s_w6__tree_pre (CORR) | P | P | P |  | P | P | P | P |  | P |  |  |
| PATCH/B_mac_s_w16__tree_pre (CORR) | P |  | **FF** |  |  |  |  |  |  |  |  |  |
| PATCH/B_mac_s_w8__tree_pre (CORR) |  | **FF** |  | **FF** |  | P | P | P | P | t | t | t |
| REPRO/mac_s_w3_patched_noabc_CORRECT (CORR) | **FF** |  |  |  |  | P |  |  |  |  |  |  |
| REPRO/mac_s_w3_zext_addend_mutant_INCORRECT (INCO) | **FP** |  |  |  |  | F |  |  |  |  |  |  |

### Causal graft of the six-gate Yosys context into unrelated correct netlists (`ctx`, 55 graft positions)

| source netlist | grafts | `-dyn -p -c` FF / P / t | `-igs -p -c` FF / P / t | `-dyn -p` FF / P / t | `-dyn -c` FF / P / t |
|---|---|---|---|---|---|
| A_mul_s_w8__norm_pre | 9 | 1 / 8 / 0 | 7 / 2 / 0 | 0 / 9 / 0 | 0 / 9 / 0 |
| B_mac_u_w8__tree_pre | 16 | 6 / 10 / 0 | 15 / 1 / 0 | 0 / 16 / 0 | 0 / 16 / 0 |
| PATCH_B_mac_s_w5__tree_pre | 11 | 4 / 7 / 0 | 9 / 2 / 0 | 1 / 10 / 0 | 0 / 11 / 0 |
| PATCH_B_mac_s_w8__tree_pre_folded | 19 | 7 / 11 / 1 | 15 / 3 / 1 | 2 / 15 / 2 | 0 / 19 / 0 |

### Which ABC step destroys verifiability? One ABC step applied to the pre-ABC netlist (`-dyn -p -c` and `-idx -p -c`; ✓ = proved by either)

`yosysnomap` = Yosys's default ABC script without the final technology mapping: `&fraig -x; scorr; dc2; dretime; strash; &dch -f`.

| pre-ABC source | strash | balance | rewrite | refactor | dc2 | resyn2 | fraig | dch | yosysnomap | full `synth` (post-ABC) |
|---|---|---|---|---|---|---|---|---|---|---|
| A_mul_s_w8 booth_lp_pre | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ⏱ | ⏱ | ⏱ | ⏱ |
| A_mul_u_w8 booth_pre_folded | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ⏱ | ⏱ | ⏱ |
| B_dot2_u_w16 norm_pre | ✓ 1 s | ✓ 1 s | ✓ 1 s | ✓ 1 s | ✓ 1 s | ✓ 3 s | ✓ 2 s | ✓ 2 s | ⏱ | ⏱ |

### Does the ABC target gate library matter? (`synth … -noabc; abc -g <lib>; aigmap`; `default` is byte-identical to the real post-ABC netlist)

| design | g_aig | g_gates | g_simple | default |
|---|---|---|---|---|
| A_mul_s_w8 booth_lp | ⏱ | ⏱ | ⏱ | ⏱ |
| A_mul_u_w12 booth | ⏱ | ⏱ | ⏱ | ⏱ |
| A_mul_u_w20 norm | ⏱ | ⏱ | ⏱ | ⏱ |
| A_mul_u_w8 booth | ⏱ | ⏱ | ⏱ | ⏱ |
| B_dot2_u_w16 norm | ⏱ | ⏱ | ⏱ | ⏱ |

### Onset of 64-bit pre-ABC cost (`-dyn -p -c`; W = 64 from `stage2_pre` under contention and `long64` uncontended)

| netlist | W=32 | W=40 | W=48 | W=56 | W=64 (900 s, contended) | W=64 (3600 s, uncontended) |
|---|---|---|---|---|---|---|
| B_mac_u norm_pre | ✓ 8 s | ✓ 31 s | ⏱ | ✓ 346 s | ⏱ | ✓ 348 s |
| B_mac_u tree_pre | ✓ 9 s | ✓ 12 s | ✓ 37 s | ✓ 60 s | ✓ 188 s | – |
| B_dot2_u tree_pre | ✓ 29 s | ✓ 47 s | ✓ 119 s | ✓ 252 s | ⏱ | ✓ 308 s |

### Signed low-power Booth before ABC (`booth -lowpower`, no ABC)

| W | raw pre-ABC netlist | constant-folded copy | post-ABC (portfolio) | `&cec` pre ≡ post |
|---|---|---|---|---|
| 8 | ERROR (segfault) | ✓ | ⏱ | PASS (1.0 s) |
| 16 | ERROR (segfault) | ✓ | ⏱ | PASS (1.3 s) |
| 32 | ERROR (segfault) | ✓ 10 s | ⏱ | PASS (49.3 s) |

### Longer or uncontended reruns of TIMEOUT results

| stage | netlist | configuration | budget | outcome | TRACE time | cgroup peak MiB |
|---|---|---|---|---|---|---|
| calib | A_mul_u_w32 norm | `-idx -p -c` | 1800 s | TIMEOUT | – | 6282.2 |
| calib | B_dot2_u_w16 norm | `-dyn -p -c` | 1800 s | TIMEOUT | – | 1966.6 |
| long64 | B_mac_u_w64 norm_pre | `-dyn -p -c` | 3600 s | PASS | 348 s | 176.5 |
| long64 | B_dot2_u_w64 tree_pre | `-dyn -p -c` | 3600 s | PASS | 308 s | 288.2 |
| long | A_mul_u_w8 booth | `-dyn -p -c` | 1800 s | TIMEOUT | – | 628.9 |
| long | A_mul_s_w8 booth_lp | `-dyn -p -c` | 1800 s | TIMEOUT | – | 1608.1 |
| long | B_mac_s_w8 norm | `-idx -p -c` | 1800 s | PASS | 1092 s | 783.9 |
| long | MUT_accum_mac_u_w8 tree | `-dyn -p -c` | 900 s | TIMEOUT | – | 626.4 |
| long | MUT_signext_mac_s_w8 norm | `-dyn -p -c` | 900 s | TIMEOUT | – | 225.8 |
| long | MUT_trunc_mul_u_w8 norm | `-idx -p -c` | 900 s | TIMEOUT | – | 926.7 |

### Class totals per stage (`RESULTS.csv`)

| stage | PASS | FAIL | FALSE_FAIL | FALSE_FAIL? | FALSE_PASS | TIMEOUT | UNSUPPORTED | ERROR | UNKNOWN | runs |
|---|---|---|---|---|---|---|---|---|---|---|
| abcmap | 0 | 0 | 0 | 0 | 0 | 40 | 0 | 0 | 0 | 40 |
| baseline | 17 | 6 | 0 | 0 | 0 | 5 | 1 | 0 | 0 | 29 |
| calib | 0 | 0 | 0 | 0 | 0 | 2 | 0 | 0 | 0 | 2 |
| contra | 27 | 0 | 3 | 0 | 0 | 12 | 0 | 0 | 0 | 42 |
| ctrlcrash | 2 | 0 | 0 | 0 | 0 | 0 | 0 | 3 | 0 | 5 |
| ctx | 149 | 0 | 67 | 0 | 0 | 4 | 0 | 0 | 0 | 220 |
| diag1 | 4 | 0 | 1 | 0 | 0 | 4 | 0 | 1 | 0 | 10 |
| dotspec | 3 | 1 | 1 | 0 | 0 | 2 | 0 | 0 | 0 | 7 |
| isolation | 46 | 0 | 0 | 0 | 0 | 23 | 0 | 6 | 0 | 75 |
| long | 1 | 0 | 0 | 0 | 0 | 5 | 0 | 0 | 0 | 6 |
| long64 | 2 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 2 |
| mini | 43 | 74 | 4 | 0 | 5 | 6 | 0 | 0 | 0 | 132 |
| phaseopt_probe | 19 | 44 | 0 | 0 | 4 | 5 | 0 | 0 | 0 | 72 |
| portfolio_w32 | 70 | 56 | 2 | 0 | 0 | 280 | 0 | 0 | 0 | 408 |
| repro | 1 | 1 | 1 | 0 | 1 | 0 | 0 | 0 | 0 | 4 |
| stage1 | 1 | 0 | 0 | 0 | 0 | 2 | 0 | 0 | 0 | 3 |
| stage2_pre | 18 | 3 | 0 | 0 | 0 | 21 | 0 | 0 | 0 | 42 |
| sweep | 71 | 0 | 0 | 0 | 0 | 33 | 0 | 0 | 0 | 104 |
| unsupported_probe | 0 | 0 | 0 | 0 | 0 | 0 | 5 | 0 | 0 | 5 |
| w64post | 3 | 0 | 0 | 0 | 0 | 3 | 0 | 0 | 0 | 6 |
| **all** | 477 | 185 | 79 | 0 | 10 | 447 | 6 | 10 | 0 | 1214 |

