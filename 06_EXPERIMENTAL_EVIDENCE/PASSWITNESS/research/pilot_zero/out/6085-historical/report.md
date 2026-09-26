# PassWitness analysis report

**Verdict:** `SETUP_ERROR`

## Investigation summary

- Final design equivalence: `NOT_EXECUTED`
- Formal backend: `yosys-sat`
- Localization: `NOT_EXECUTED`
- Flow fidelity: `NOT_EXECUTED`
- First verified divergent transition: `none`

## Verified facts

- No completed checks were recorded.

## Inferences

- No inference was recorded.

## Unexecuted checks

- Formal equivalence.

## Inputs and provenance

- RTL: `/mnt/c/Users/meetb/Downloads/passwitness/research/pilot_zero/issue6085/source.v`
- Top: `top`
- Flow: `/mnt/c/Users/meetb/Downloads/passwitness/research/pilot_zero/issue6085/synthesis.ys`
- Yosys: `Yosys 0.68+post (git sha1 UNKNOWN, Release, GNU /usr/bin/c++ 13.3.0)`
- Executable SHA-256: `1a39da5e6e475cadb2ca66e20ac16687ec78ef222ef1f55c631feb05e5d1b9b7`
- Source revision verified: `False`
- Provenance method: Yosys -V output and SHA-256 of the executable path; source checkout was not supplied

## Formal result

- Status: `NOT_EXECUTED`
- Reason: Formal check was not executed because setup failed.
- Backend: `yosys-sat`

## Stage localization

- Status: `NOT_EXECUTED`
- Mode: `unknown`
- Checkpoint count: `0`
- Formal check count: `0`
- Synthesis runtime: `0.000 s`
- Formal runtime: `0.000 s`
- Total localization runtime: `0.000 s`

### Fixed-witness replay

- Status: `UNCONFIRMED`
- Replay is explanatory evidence for one input and is not a formal proof.

## Errors

- Synthesis failed or did not produce a candidate netlist.

## Generated evidence

- `candidate_metadata`: `/mnt/c/Users/meetb/Downloads/passwitness/research/pilot_zero/out/6085-historical/work/candidate.json`
- `candidate_netlist`: `/mnt/c/Users/meetb/Downloads/passwitness/research/pilot_zero/out/6085-historical/work/candidate.v`
- `formal_log`: `/mnt/c/Users/meetb/Downloads/passwitness/research/pilot_zero/out/6085-historical/logs/formal.log`
- `golden_metadata_log`: `/mnt/c/Users/meetb/Downloads/passwitness/research/pilot_zero/out/6085-historical/logs/golden-metadata.log`
- `synthesis_log`: `/mnt/c/Users/meetb/Downloads/passwitness/research/pilot_zero/out/6085-historical/logs/synthesis.log`
- `tool_version_log`: `/mnt/c/Users/meetb/Downloads/passwitness/research/pilot_zero/out/6085-historical/logs/tool-version.log`
