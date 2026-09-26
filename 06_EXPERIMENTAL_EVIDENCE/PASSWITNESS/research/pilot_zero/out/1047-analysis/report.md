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

- Yosys is unavailable or did not return a version string.

## Generated evidence

- `formal_log`: `/mnt/c/Users/meetb/Downloads/passwitness/research/pilot_zero/out/1047-analysis/logs/formal.log`
- `synthesis_log`: `/mnt/c/Users/meetb/Downloads/passwitness/research/pilot_zero/out/1047-analysis/logs/synthesis.log`
- `tool_version_log`: `/mnt/c/Users/meetb/Downloads/passwitness/research/pilot_zero/out/1047-analysis/logs/tool-version.log`
