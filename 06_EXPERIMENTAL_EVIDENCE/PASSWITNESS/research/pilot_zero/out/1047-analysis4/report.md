# PassWitness analysis report

**Verdict:** `SETUP_ERROR`

## Investigation summary

- Final design equivalence: `SETUP_ERROR`
- Formal backend: `yosys-sat`
- Localization: `UNSUPPORTED`
- Flow fidelity: `UNSUPPORTED`
- First verified divergent transition: `none`

## Verified facts

- Yosys version recorded as Yosys 0.8+0 (git sha1 UNKNOWN, clang 18.1.3 -fPIC -Os).
- Formal backend: yosys-sat.
- The golden RTL and synthesized candidate were independently loaded into a generated output-comparison miter.
- Formal classification is SETUP_ERROR based on an explicit SAT proof marker.

## Inferences

- No inference was recorded.

## Unexecuted checks

- A trustworthy functional verdict.

## Inputs and provenance

- RTL: `/mnt/c/Users/meetb/Downloads/passwitness/research/pilot_zero/issue1047/source.v`
- Top: `top`
- Flow: `/mnt/c/Users/meetb/Downloads/passwitness/research/pilot_zero/issue1047/synthesis.ys`
- Yosys: `Yosys 0.8+0 (git sha1 UNKNOWN, clang 18.1.3 -fPIC -Os)`
- Executable SHA-256: `175317e8eaa2684621d4e707f36d476151fdc6b080713dc7bdc730a0e7b8e640`
- Source revision verified: `False`
- Provenance method: Yosys -V output and SHA-256 of the executable path; source checkout was not supplied

## Formal result

- Status: `SETUP_ERROR`
- Reason: The formal check did not complete with a trustworthy proof result.
- Backend: `yosys-sat`
- Runtime: `0.620 s`

## Stage localization

- Status: `UNSUPPORTED`
- Mode: `unsupported`
- Checkpoint count: `0`
- Formal check count: `0`
- Synthesis runtime: `0.000 s`
- Formal runtime: `0.000 s`
- Total localization runtime: `0.019 s`

### Flow fidelity

- Status: `UNSUPPORTED`
- Catalog: `explicit flow`
- Original command count: `2`
- Instrumented command count: `0`
- Added checkpoint commands: `0`
- Original final representation: `/mnt/c/Users/meetb/Downloads/passwitness/research/pilot_zero/out/1047-analysis4/work/candidate.v`
- Instrumented final representation: `None`

### Localization caveats

- Localization supports either the exact `synth -top TOP -arith_tree` flow or a flow with at least two `# passwitness-stage: NAME` blocks.

## Generated evidence

- `candidate_metadata`: `/mnt/c/Users/meetb/Downloads/passwitness/research/pilot_zero/out/1047-analysis4/work/candidate.json`
- `candidate_netlist`: `/mnt/c/Users/meetb/Downloads/passwitness/research/pilot_zero/out/1047-analysis4/work/candidate.v`
- `formal_log`: `/mnt/c/Users/meetb/Downloads/passwitness/research/pilot_zero/out/1047-analysis4/logs/formal.log`
- `formal_script`: `/mnt/c/Users/meetb/Downloads/passwitness/research/pilot_zero/out/1047-analysis4/work/formal.ys`
- `golden_metadata_log`: `/mnt/c/Users/meetb/Downloads/passwitness/research/pilot_zero/out/1047-analysis4/logs/golden-metadata.log`
- `miter`: `/mnt/c/Users/meetb/Downloads/passwitness/research/pilot_zero/out/1047-analysis4/work/miter.v`
- `synthesis_log`: `/mnt/c/Users/meetb/Downloads/passwitness/research/pilot_zero/out/1047-analysis4/logs/synthesis.log`
- `tool_version_log`: `/mnt/c/Users/meetb/Downloads/passwitness/research/pilot_zero/out/1047-analysis4/logs/tool-version.log`
