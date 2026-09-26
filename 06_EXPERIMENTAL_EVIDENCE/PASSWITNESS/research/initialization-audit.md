# Verismith seed 6762640716476645086 initialization audit

This is research evidence only. The PassWitness release and Yosys PR #6231 were not modified.

## Inputs and provenance

| Artifact | Identity |
|---|---|
| Original generated RTL | `seed-6762640716476645086/fuzz-output/fuzz_1/yosys_3333e002/rtl.v`, 1,412 lines, 60,261 bytes, SHA-256 `ee5597011923be4939d7f7a82887dcb3afe544770e354f141aaab2af8347b730` |
| Affected compiler source claim | Yosys `3333e002b1c6a05e73bdc94844cbe74288771dd0` |
| Affected executable | `yosys-3333e002-bin`, SHA-256 `916dc3d905e3c74ebcd885abe7615e4e000eea2105145e5a2004e59357011f8a`; reports `Yosys 0.8+`, source checkout was built without Git metadata |
| Raw historical elaboration | `raw-historical-elaborated.il`, SHA-256 `17963711faa7a525941d51e819f91f8c5923f10ecebb7a9c5a430eaf563b5928` |
| Raw historical post-synthesis RTLIL | `raw-historical-synth.il`, SHA-256 `85f2eeda0acc43aeeedeba83fa7dcec37068057627cedf79d6f0f99a8ebaa96e` |
| Raw historical Verilog output | `synth.v`, SHA-256 `6e3051334e64123c697ed2f0233c59059b8b4d009bfae36ee870a06151adc3ad` |
| Corrected control executed | `yosys-0.8-bin`, reports Yosys `0.8` / source SHA `5706e908...`, executable SHA-256 `502b9ff42553f00b26af1b35dedf0ae04dc24a9f54cbaf7f040cf8972ca73716` |

The affected flow was executed as `read_verilog -sv rtl.v; hierarchy -top top; synth; write_verilog -noattr synth.v`. The raw historical RTLIL was emitted with that same compiler using its `write_ilang` backend. `ilang` is the historical spelling of the RTLIL text format.

## Reg93 evidence

Current Yosys elaboration identifies `modinst271.reg93` as a signed 22-bit register with source initialization `22'0000000000000000000000`. The source declaration is `rtl.v:112`; its clocked assignment is at `rtl.v:177`.

The affected historical post-synthesis RTLIL contains:

```text
attribute \init 22'xxxxxxxxxxxxx000000000
wire width 22 \reg93
```

The corresponding historical Verilog contains `reg93_reg[8] = 1'hx`; the lower eight bits are zero and the X bit is sign-extended through the upper bits. The corrected Yosys 0.8 output contains a defined zero initialization for the corresponding state and the current SAT checker proves `modinst271.reg93[8] = 0`.

The historical compiler's internal property is therefore reproduced: source initialization is zero, while the affected synthesized representation has an X-valued initial state.

## Observability checks

The hierarchy warning says that `top.modinst271.y` is 443 bits while `top.wire270` is 22 bits. The elaborated JSON maps the direct `reg93` output bits to `module88.y[442:440]`; those high bits are discarded by the 22-bit connection. The actual top-level slice associated with the surviving `wire270` signal is `top.y[254:240]` (wire bits 2 through 16).

Evidence for the observable contract:

- Direct SAT miter, source versus historical output slice `y[254:240]`, one frame with `-set-init-undef`: `SUCCESS`.
- The same slice, two sequential frames: `SUCCESS`.
- Fixed-input simulation: source and historical top-level `y` and `y[254:240]` agree at the initial sample, while the internal `reg93` VCD values differ (`0` versus `xxxxxxxxxxxxx000000000`-style X state).
- The source and historical internal `reg93` values agree after the first clock transition for the fixed-input simulation.

The SAT proof used `miter -equiv` and `sat ... -prove trigger 0`; setting `trigger` to 1 would ask for the opposite property and was not used as evidence.

## RTLIL import fidelity

Modern Yosys `read_rtlil` imported `raw-historical-synth.il` successfully and re-emitted the relevant `reg93` width, source location, and `\init` value unchanged. Imported representation: `modern-import-raw-historical-synth.il`, SHA-256 `f212cdae2cd9a56101a29e314ea57ae65b7e0429ddb12d0d1340090fc74a3d37`. Parsing success is not treated as a proof; the relevant attributes and connectivity were inspected after import.

## Fix attribution

The public Yosys issue identifies development build `09467bb9` as affected and official Yosys 0.8 as correct. The historical fixing commit is `33738c174560c718723b6c860af002d1a8a91cea`, “Fix handling of partial init attributes in write_verilog, fixes #997”. The executed Yosys 0.8 control is a corrected behavioral control, not a claim that its 2018 source revision is the fixing commit.

## Disposition

**B. FULL HISTORICAL SEED: INTERNAL DEFECT VERIFIED, OUTPUT CONSEQUENCE UNRESOLVED**

The full seed reproduces the initialization corruption internally, with raw historical RTLIL and an independent modern SAT check of the affected state. It does not currently provide a trustworthy top-level numeric or X-valued counterexample attributable to `reg93`: the formally checked top-level slice passes, and fixed-input simulation agrees at the output. The large seed must not be reported as a verified top-level miscompilation until a different observable consequence is established.
