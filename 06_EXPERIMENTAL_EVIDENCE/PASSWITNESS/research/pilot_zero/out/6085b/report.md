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
- Yosys: `Yosys 0.69+ (git sha1 e8db64c60, Release, Clang /usr/bin/clang++ 18.1.3)`
- Tool commit: `e8db64c609c7ae4574e66bbd475f5f10f36d7a31`
- Yosys-reported commit: `e8db64c60`
- Executable SHA-256: `7d58111d6119006406e3ba635cb646da07abd48f248a0fc2899a8037630883c6`
- Source revision verified: `False`
- Provenance method: Yosys -V output and SHA-256 of the executable path; source checkout was not supplied

## Formal result

- Status: `NOT_EXECUTED`
- Reason: Formal check was not executed because setup failed.
- Backend: `yosys-sat`

## Errors

- Synthesis failed or did not produce a candidate netlist.

## Generated evidence

- `candidate_metadata`: `/mnt/c/Users/meetb/Downloads/passwitness/research/pilot_zero/out/6085b/work/candidate.json`
- `candidate_netlist`: `/mnt/c/Users/meetb/Downloads/passwitness/research/pilot_zero/out/6085b/work/candidate.v`
- `formal_log`: `/mnt/c/Users/meetb/Downloads/passwitness/research/pilot_zero/out/6085b/logs/formal.log`
- `golden_metadata_log`: `/mnt/c/Users/meetb/Downloads/passwitness/research/pilot_zero/out/6085b/logs/golden-metadata.log`
- `synthesis_log`: `/mnt/c/Users/meetb/Downloads/passwitness/research/pilot_zero/out/6085b/logs/synthesis.log`
- `tool_version_log`: `/mnt/c/Users/meetb/Downloads/passwitness/research/pilot_zero/out/6085b/logs/tool-version.log`
