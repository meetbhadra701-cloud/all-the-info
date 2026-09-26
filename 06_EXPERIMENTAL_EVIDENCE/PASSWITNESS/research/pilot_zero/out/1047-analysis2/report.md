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

- RTL: `/mnt/c/Users/meetb/Downloads/passwitness/research/pilot_zero/issue1047/source.v`
- Top: `top`
- Flow: `/mnt/c/Users/meetb/Downloads/passwitness/research/pilot_zero/issue1047/synthesis.ys`
- Yosys: `Yosys 0.8+0 (git sha1 UNKNOWN, clang 18.1.3 -fPIC -Os)`
- Executable SHA-256: `158d4cc84110d1161bb9ead286986f51412d5175ea6692b12608c69472339de1`
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

- Golden-reference elaboration failed; no trustworthy port metadata was produced.

## Generated evidence

- `formal_log`: `/mnt/c/Users/meetb/Downloads/passwitness/research/pilot_zero/out/1047-analysis2/logs/formal.log`
- `golden_metadata_log`: `/mnt/c/Users/meetb/Downloads/passwitness/research/pilot_zero/out/1047-analysis2/logs/golden-metadata.log`
- `synthesis_log`: `/mnt/c/Users/meetb/Downloads/passwitness/research/pilot_zero/out/1047-analysis2/logs/synthesis.log`
- `tool_version_log`: `/mnt/c/Users/meetb/Downloads/passwitness/research/pilot_zero/out/1047-analysis2/logs/tool-version.log`
