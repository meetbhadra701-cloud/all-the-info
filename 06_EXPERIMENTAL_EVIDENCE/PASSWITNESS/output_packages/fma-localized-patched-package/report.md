# PassWitness analysis report

**Verdict:** `PASS`

## Verified facts

- Yosys version recorded as Yosys 0.69+ (git sha1 e8db64c60, Release, Clang /usr/bin/clang++ 18.1.3).
- The golden RTL and synthesized candidate were independently loaded into a generated output-comparison miter.
- Formal classification is PASS based on an explicit SAT proof marker.

## Inferences

- The tested combinational input space is equivalent under the supplied flow.

## Unexecuted checks

- None recorded.

## Inputs and provenance

- RTL: `/mnt/c/Users/meetb/Downloads/passwitness/fixtures/signed_fma_bug/source.v`
- Top: `fma_impl`
- Flow: `/mnt/c/Users/meetb/Downloads/passwitness/fixtures/signed_fma_bug/synthesis.ys`
- Yosys: `Yosys 0.69+ (git sha1 e8db64c60, Release, Clang /usr/bin/clang++ 18.1.3)`
- Tool commit: `30b851e63ff071578cda4e1e49eccd367f7881d9`

## Formal result

- Status: `PASS`
- Reason: The SAT solver established the equivalence property.
- Runtime: `0.641 s`

## Stage localization

- Status: `NO_DIVERGENCE`
- Mode: `synth_arith_tree_expansion`
- Checkpoint count: `8`
- Formal check count: `9`
- Synthesis runtime: `0.726 s`
- Formal runtime: `6.005 s`
- Total localization runtime: `6.969 s`

### Checkpoint results

| # | Checkpoint | Transition | Produced | Proof | Snapshot |
|---:|---|---|---|---|---|
| 0 | `elaborated` | `elaboration` | `True` | `PASS` | `/mnt/c/Users/meetb/Downloads/passwitness/out/fma-localized-patched-package/localization/checkpoints/000_elaborated.rtlil` |
| 1 | `proc` | `proc` | `True` | `PASS` | `/mnt/c/Users/meetb/Downloads/passwitness/out/fma-localized-patched-package/localization/checkpoints/001_proc.rtlil` |
| 2 | `opt` | `opt` | `True` | `PASS` | `/mnt/c/Users/meetb/Downloads/passwitness/out/fma-localized-patched-package/localization/checkpoints/002_opt.rtlil` |
| 3 | `wreduce` | `wreduce` | `True` | `PASS` | `/mnt/c/Users/meetb/Downloads/passwitness/out/fma-localized-patched-package/localization/checkpoints/003_wreduce.rtlil` |
| 4 | `alumacc` | `alumacc` | `True` | `PASS` | `/mnt/c/Users/meetb/Downloads/passwitness/out/fma-localized-patched-package/localization/checkpoints/004_alumacc.rtlil` |
| 5 | `arith_tree` | `arith_tree` | `True` | `PASS` | `/mnt/c/Users/meetb/Downloads/passwitness/out/fma-localized-patched-package/localization/checkpoints/005_arith_tree.rtlil` |
| 6 | `techmap` | `techmap` | `True` | `PASS` | `/mnt/c/Users/meetb/Downloads/passwitness/out/fma-localized-patched-package/localization/checkpoints/006_techmap.rtlil` |
| 7 | `abc` | `abc` | `True` | `PASS` | `/mnt/c/Users/meetb/Downloads/passwitness/out/fma-localized-patched-package/localization/checkpoints/007_abc.rtlil` |

## Generated evidence

- `candidate_netlist`: `/mnt/c/Users/meetb/Downloads/passwitness/out/fma-localized-patched-package/work/candidate.v`
- `formal_log`: `/mnt/c/Users/meetb/Downloads/passwitness/out/fma-localized-patched-package/logs/formal.log`
- `formal_script`: `/mnt/c/Users/meetb/Downloads/passwitness/out/fma-localized-patched-package/work/formal.ys`
- `golden_metadata_log`: `/mnt/c/Users/meetb/Downloads/passwitness/out/fma-localized-patched-package/logs/golden-metadata.log`
- `miter`: `/mnt/c/Users/meetb/Downloads/passwitness/out/fma-localized-patched-package/work/miter.v`
- `portable_package`: `/mnt/c/Users/meetb/Downloads/passwitness/out/fma-localized-patched-package/portable`
- `synthesis_log`: `/mnt/c/Users/meetb/Downloads/passwitness/out/fma-localized-patched-package/logs/synthesis.log`
- `tool_version_log`: `/mnt/c/Users/meetb/Downloads/passwitness/out/fma-localized-patched-package/logs/tool-version.log`
