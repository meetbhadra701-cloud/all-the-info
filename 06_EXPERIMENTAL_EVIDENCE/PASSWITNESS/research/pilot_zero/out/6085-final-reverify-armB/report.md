# PassWitness analysis report

**Verdict:** `FAIL`

## Investigation summary

- Final design equivalence: `FAIL`
- Formal backend: `yosys-sat`
- Localization: `LOCALIZED`
- Flow fidelity: `PASS`
- First verified divergent transition: `cmp2lut`

## Verified facts

- Yosys version recorded as Yosys 0.68+post (git sha1 UNKNOWN, Release, GNU /usr/bin/c++ 13.3.0).
- Formal backend: yosys-sat.
- The golden RTL and synthesized candidate were independently loaded into a generated output-comparison miter.
- Formal classification is FAIL based on an explicit SAT proof marker.

## Inferences

- The candidate differs from the golden RTL for at least one input assignment.

## Unexecuted checks

- None recorded.

## Inputs and provenance

- RTL: `/mnt/c/Users/meetb/Downloads/passwitness/research/pilot_zero/reductions/6085-armB/minimized/source.v`
- Top: `top`
- Flow: `/mnt/c/Users/meetb/Downloads/passwitness/research/pilot_zero/issue6085/synthesis.ys`
- Yosys: `Yosys 0.68+post (git sha1 UNKNOWN, Release, GNU /usr/bin/c++ 13.3.0)`
- Executable SHA-256: `1a39da5e6e475cadb2ca66e20ac16687ec78ef222ef1f55c631feb05e5d1b9b7`
- Source revision verified: `False`
- Provenance method: Yosys -V output and SHA-256 of the executable path; source checkout was not supplied

## Formal result

- Status: `FAIL`
- Reason: The SAT solver found a model that violates output equivalence.
- Backend: `yosys-sat`
- Runtime: `0.117 s`

### Counterexample

```json
{
  "inputs": {
    "a": {
      "decimal": 0,
      "hex": "0",
      "binary": "0000"
    }
  },
  "reference_outputs": {
    "y": {
      "decimal": 1,
      "hex": "1",
      "binary": "1"
    }
  },
  "candidate_outputs": {
    "y": {
      "decimal": 0,
      "hex": "0",
      "binary": "0"
    }
  },
  "raw_model": {
    "a": {
      "decimal": 0,
      "hex": "0",
      "binary": "0000"
    },
    "candidate_y": {
      "decimal": 0,
      "hex": "0",
      "binary": "0"
    },
    "mismatch": {
      "decimal": 1,
      "hex": "1",
      "binary": "1"
    },
    "reference_y": {
      "decimal": 1,
      "hex": "1",
      "binary": "1"
    }
  }
}
```

## Stage localization

- Status: `LOCALIZED`
- Mode: `marked_explicit_flow`
- First verified divergent transition: `cmp2lut`
- Previous proven checkpoint: `prep`
- Checkpoint count: `2`
- Formal check count: `3`
- Synthesis runtime: `0.137 s`
- Formal runtime: `0.397 s`
- Total localization runtime: `1.211 s`
- Time to first verified divergence: `0.471 s`

### Checkpoint results

| # | Checkpoint | Transition | Produced | Proof | Snapshot |
|---:|---|---|---|---|---|
| 0 | `prep` | `elaboration` | `True` | `PASS` | `/mnt/c/Users/meetb/Downloads/passwitness/research/pilot_zero/out/6085-final-reverify-armB/localization/checkpoints/000_prep.rtlil` |
| 1 | `cmp2lut` | `cmp2lut` | `True` | `FAIL` | `/mnt/c/Users/meetb/Downloads/passwitness/research/pilot_zero/out/6085-final-reverify-armB/localization/checkpoints/001_cmp2lut.rtlil` |

### Failing-transition evidence

- Checkpoint: `cmp2lut`
- Counterexample JSON: `/mnt/c/Users/meetb/Downloads/passwitness/research/pilot_zero/out/6085-final-reverify-armB/localization/witnesses/001_cmp2lut.json`
- Counterexample VCD: `/mnt/c/Users/meetb/Downloads/passwitness/research/pilot_zero/out/6085-final-reverify-armB/localization/witnesses/001_cmp2lut.vcd`
- Formal log: `/mnt/c/Users/meetb/Downloads/passwitness/research/pilot_zero/out/6085-final-reverify-armB/localization/logs/001_cmp2lut.log`

### Flow fidelity

- Status: `PASS`
- Catalog: `explicit-marked-flow`
- Original command count: `2`
- Instrumented command count: `5`
- Added checkpoint commands: `2`
- Final representation comparison: `PASS`
- Original final representation: `/mnt/c/Users/meetb/Downloads/passwitness/research/pilot_zero/out/6085-final-reverify-armB/work/candidate.v`
- Instrumented final representation: `/mnt/c/Users/meetb/Downloads/passwitness/research/pilot_zero/out/6085-final-reverify-armB/localization/checkpoints/001_cmp2lut.rtlil`

### Fixed-witness replay

- Status: `CONFIRMED`
- Replay is explanatory evidence for one input and is not a formal proof.
- `failing_checkpoint`: `CONFIRMED` — Replay target failing_checkpoint produced mismatch=1; expected 1.
- `original_final`: `CONFIRMED` — Replay target original_final produced mismatch=1; expected 1.
- `previous_checkpoint`: `CONFIRMED` — Replay target previous_checkpoint produced mismatch=0; expected 0.

## Generated evidence

- `candidate_metadata`: `/mnt/c/Users/meetb/Downloads/passwitness/research/pilot_zero/out/6085-final-reverify-armB/work/candidate.json`
- `candidate_netlist`: `/mnt/c/Users/meetb/Downloads/passwitness/research/pilot_zero/out/6085-final-reverify-armB/work/candidate.v`
- `formal_log`: `/mnt/c/Users/meetb/Downloads/passwitness/research/pilot_zero/out/6085-final-reverify-armB/logs/formal.log`
- `formal_script`: `/mnt/c/Users/meetb/Downloads/passwitness/research/pilot_zero/out/6085-final-reverify-armB/work/formal.ys`
- `golden_metadata_log`: `/mnt/c/Users/meetb/Downloads/passwitness/research/pilot_zero/out/6085-final-reverify-armB/logs/golden-metadata.log`
- `miter`: `/mnt/c/Users/meetb/Downloads/passwitness/research/pilot_zero/out/6085-final-reverify-armB/work/miter.v`
- `portable_package`: `/mnt/c/Users/meetb/Downloads/passwitness/research/pilot_zero/out/6085-final-reverify-armB/portable`
- `synthesis_log`: `/mnt/c/Users/meetb/Downloads/passwitness/research/pilot_zero/out/6085-final-reverify-armB/logs/synthesis.log`
- `tool_version_log`: `/mnt/c/Users/meetb/Downloads/passwitness/research/pilot_zero/out/6085-final-reverify-armB/logs/tool-version.log`
