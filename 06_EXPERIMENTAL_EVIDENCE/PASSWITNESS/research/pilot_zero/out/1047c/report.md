# PassWitness analysis report

**Verdict:** `PASS`

## Investigation summary

- Final design equivalence: `PASS`
- Formal backend: `yosys-sat`
- Localization: `NOT_EXECUTED`
- Flow fidelity: `NOT_EXECUTED`
- First verified divergent transition: `none`

## Verified facts

- Yosys version recorded as Yosys 0.69+ (git sha1 e8db64c60, Release, Clang /usr/bin/clang++ 18.1.3).
- Formal backend: yosys-sat.
- The golden RTL and synthesized candidate were independently loaded into a generated output-comparison miter.
- Formal classification is PASS based on an explicit SAT proof marker.

## Inferences

- The tested combinational input space is equivalent under the supplied flow.

## Unexecuted checks

- None recorded.

## Inputs and provenance

- RTL: `/mnt/c/Users/meetb/Downloads/passwitness/research/pilot_zero/issue1047/source.v`
- Top: `top`
- Flow: `/mnt/c/Users/meetb/Downloads/passwitness/research/pilot_zero/issue1047/synthesis.ys`
- Yosys: `Yosys 0.69+ (git sha1 e8db64c60, Release, Clang /usr/bin/clang++ 18.1.3)`
- Tool commit: `e8db64c609c7ae4574e66bbd475f5f10f36d7a31`
- Yosys-reported commit: `e8db64c60`
- Executable SHA-256: `7d58111d6119006406e3ba635cb646da07abd48f248a0fc2899a8037630883c6`
- Source revision verified: `False`
- Provenance method: Yosys -V output and SHA-256 of the executable path; source checkout was not supplied

## Formal result

- Status: `PASS`
- Reason: The SAT solver established the equivalence property.
- Backend: `yosys-sat`
- Runtime: `0.647 s`

## Generated evidence

- `candidate_metadata`: `/mnt/c/Users/meetb/Downloads/passwitness/research/pilot_zero/out/1047c/work/candidate.json`
- `candidate_netlist`: `/mnt/c/Users/meetb/Downloads/passwitness/research/pilot_zero/out/1047c/work/candidate.v`
- `formal_log`: `/mnt/c/Users/meetb/Downloads/passwitness/research/pilot_zero/out/1047c/logs/formal.log`
- `formal_script`: `/mnt/c/Users/meetb/Downloads/passwitness/research/pilot_zero/out/1047c/work/formal.ys`
- `golden_metadata_log`: `/mnt/c/Users/meetb/Downloads/passwitness/research/pilot_zero/out/1047c/logs/golden-metadata.log`
- `miter`: `/mnt/c/Users/meetb/Downloads/passwitness/research/pilot_zero/out/1047c/work/miter.v`
- `synthesis_log`: `/mnt/c/Users/meetb/Downloads/passwitness/research/pilot_zero/out/1047c/logs/synthesis.log`
- `tool_version_log`: `/mnt/c/Users/meetb/Downloads/passwitness/research/pilot_zero/out/1047c/logs/tool-version.log`
