# PassWitness analysis report

**Verdict:** `FAIL`

## Verified facts

- Yosys version recorded as Yosys 0.69+ (git sha1 e8db64c60, Release, Clang /usr/bin/clang++ 18.1.3).
- The golden RTL and synthesized candidate were independently loaded into a generated output-comparison miter.
- Formal classification is FAIL based on an explicit SAT proof marker.

## Inferences

- The candidate differs from the golden RTL for at least one input assignment.

## Unexecuted checks

- None recorded.

## Inputs and provenance

- RTL: `/mnt/c/Users/meetb/Downloads/passwitness/fixtures/signed_fma_bug/source.v`
- Top: `fma_impl`
- Flow: `/mnt/c/Users/meetb/Downloads/passwitness/fixtures/signed_fma_bug/synthesis.ys`
- Yosys: `Yosys 0.69+ (git sha1 e8db64c60, Release, Clang /usr/bin/clang++ 18.1.3)`
- Tool commit: `e8db64c609c7ae4574e66bbd475f5f10f36d7a31`

## Formal result

- Status: `FAIL`
- Reason: The SAT solver found a model that violates output equivalence.
- Runtime: `0.759 s`

### Counterexample

```json
{
  "inputs": {
    "a": {
      "decimal": 1,
      "hex": "1",
      "binary": "0001"
    },
    "b": {
      "decimal": 12,
      "hex": "c",
      "binary": "1100"
    }
  },
  "reference_outputs": {
    "y": {
      "decimal": 11,
      "hex": "b",
      "binary": "00000000000000001011"
    }
  },
  "candidate_outputs": {
    "y": {
      "decimal": 139,
      "hex": "8b",
      "binary": "00000000000010001011"
    }
  },
  "raw_model": {
    "a": {
      "decimal": 1,
      "hex": "1",
      "binary": "0001"
    },
    "b": {
      "decimal": 12,
      "hex": "c",
      "binary": "1100"
    },
    "candidate_y": {
      "decimal": 139,
      "hex": "8b",
      "binary": "00000000000010001011"
    },
    "mismatch": {
      "decimal": 1,
      "hex": "1",
      "binary": "1"
    },
    "reference_y": {
      "decimal": 11,
      "hex": "b",
      "binary": "00000000000000001011"
    }
  }
}
```

## Stage localization

- Status: `LOCALIZED`
- Mode: `synth_arith_tree_expansion`
- First verified divergent transition: `arith_tree`
- Previous proven checkpoint: `alumacc`
- Checkpoint count: `8`
- Formal check count: `9`
- Synthesis runtime: `0.806 s`
- Formal runtime: `6.107 s`
- Total localization runtime: `7.282 s`

### Checkpoint results

| # | Checkpoint | Transition | Produced | Proof | Snapshot |
|---:|---|---|---|---|---|
| 0 | `elaborated` | `elaboration` | `True` | `PASS` | `/mnt/c/Users/meetb/Downloads/passwitness/out/fma-localized-clean-package/localization/checkpoints/000_elaborated.rtlil` |
| 1 | `proc` | `proc` | `True` | `PASS` | `/mnt/c/Users/meetb/Downloads/passwitness/out/fma-localized-clean-package/localization/checkpoints/001_proc.rtlil` |
| 2 | `opt` | `opt` | `True` | `PASS` | `/mnt/c/Users/meetb/Downloads/passwitness/out/fma-localized-clean-package/localization/checkpoints/002_opt.rtlil` |
| 3 | `wreduce` | `wreduce` | `True` | `PASS` | `/mnt/c/Users/meetb/Downloads/passwitness/out/fma-localized-clean-package/localization/checkpoints/003_wreduce.rtlil` |
| 4 | `alumacc` | `alumacc` | `True` | `PASS` | `/mnt/c/Users/meetb/Downloads/passwitness/out/fma-localized-clean-package/localization/checkpoints/004_alumacc.rtlil` |
| 5 | `arith_tree` | `arith_tree` | `True` | `FAIL` | `/mnt/c/Users/meetb/Downloads/passwitness/out/fma-localized-clean-package/localization/checkpoints/005_arith_tree.rtlil` |
| 6 | `techmap` | `techmap` | `True` | `FAIL` | `/mnt/c/Users/meetb/Downloads/passwitness/out/fma-localized-clean-package/localization/checkpoints/006_techmap.rtlil` |
| 7 | `abc` | `abc` | `True` | `FAIL` | `/mnt/c/Users/meetb/Downloads/passwitness/out/fma-localized-clean-package/localization/checkpoints/007_abc.rtlil` |

## Generated evidence

- `candidate_netlist`: `/mnt/c/Users/meetb/Downloads/passwitness/out/fma-localized-clean-package/work/candidate.v`
- `formal_log`: `/mnt/c/Users/meetb/Downloads/passwitness/out/fma-localized-clean-package/logs/formal.log`
- `formal_script`: `/mnt/c/Users/meetb/Downloads/passwitness/out/fma-localized-clean-package/work/formal.ys`
- `golden_metadata_log`: `/mnt/c/Users/meetb/Downloads/passwitness/out/fma-localized-clean-package/logs/golden-metadata.log`
- `miter`: `/mnt/c/Users/meetb/Downloads/passwitness/out/fma-localized-clean-package/work/miter.v`
- `portable_package`: `/mnt/c/Users/meetb/Downloads/passwitness/out/fma-localized-clean-package/portable`
- `synthesis_log`: `/mnt/c/Users/meetb/Downloads/passwitness/out/fma-localized-clean-package/logs/synthesis.log`
- `tool_version_log`: `/mnt/c/Users/meetb/Downloads/passwitness/out/fma-localized-clean-package/logs/tool-version.log`
