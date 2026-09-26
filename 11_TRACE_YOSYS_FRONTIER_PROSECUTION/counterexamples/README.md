# Counterexamples: every TRACE `Buggy` verdict, replayed independently

There is one JSON file per `Buggy` verdict, named after the TRACE job id. The logs are in `../logs/trace/<job_id>.log`. They are written by `scripts/replay_all.py`, which runs `scripts/remainder_witness.py` once per verdict. The summary is `../evidence/witness_summary.csv`.

## Procedure

1. Parse TRACE's remainder `SP: {N} c1·m1 + …`. Variables `nK` are AIGER literals: primary inputs, or internal AND nodes that TRACE left unsubstituted. Variables `iK` are undocumented and appear only with `-p`; they are evaluated as the complement of node K. That reading is the one under which every `iK` remainder on an incorrect netlist replays as a real mismatch. The identity reading is also recorded, and a remainder is called invalid only if neither reading yields a replayable mismatch.
2. Search for an input at which the remainder is non-zero modulo 2^(output width). The search is exhaustive when the netlist has ≤ 20 inputs; otherwise it uses structured candidates plus 20,000 random vectors.
3. Replay that input on the netlist with the independent evaluator (`scripts/aigtool.py`) and compare against exact integer arithmetic for the template TRACE was asked to check (`template_spec`).

## Fields

| Field | Meaning |
|---|---|
| `template_spec` | The specification TRACE checked, rebuilt from its arguments. For example, `mac:sss:8,8,16:17` is signed `a*b + c` with widths 8, 8, 16 and a 17-bit output |
| `witness_complement` / `witness_identity` | Results under each reading of `iK`: the input vector, operands, netlist output, reference, and the remainder value at that point |
| `overall: WITNESS_CONFIRMED` | A real mismatch against the checked template. The class is FAIL, or UNSUPPORTED where the template is not the design intent |
| `overall: REMAINDER_INVALID` | The remainder is non-zero somewhere, but the netlist matches the template there, or (exhaustive search) the remainder is zero everywhere. TRACE's `Buggy` does not describe any mismatch: FALSE_FAIL evidence |
| `overall: NO_WITNESS_FOUND` | Non-exhaustive search found no non-zero point. One case: an `-igsm` remainder on an incorrect netlist, i.e. the verdict is right but the remainder is wrong |

Note on the prompt's use of "counterexample": TRACE itself never outputs a counterexample. Every concrete input in these files was *derived* from TRACE's remainder by this procedure and checked by the independent evaluator.
