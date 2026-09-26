# Pilot One benchmark eligibility

This table records only screened candidates. Public issue text is not treated as
reproduction evidence by itself.

| Candidate | Source and size | Affected compiler | Fix / pass attribution | Historical availability | Formal compatibility | Reproduced | Reducible structure | Status |
|---|---|---|---|---|---|---|---|---|
| Yosys #1047 | `research/pilot_zero/issue1047/source.v`, 98 bytes, 5 lines | `92dde319fc603223304a64a5a49bbbe6c1ec3045` | Fix PR #1049, merged fix `349c472`; `shiftmul` in `peepopt` | Built in isolated worktree; executable reports `UNKNOWN` source SHA; ABC disabled | Historical PassWitness run blocked by old SAT markers and quoted-path behavior; imported RTLIL verifies with modern Yosys | Compiler-level: yes; formal pre/post: yes | No: 5-line testcase | `FORMALLY VERIFIED`, not reduction-eligible |
| Yosys #6085 | `research/pilot_zero/issue6085/source.v`, 78 bytes, 3 lines | `7a2bd64c93b8040d8509f4ced1366aba3e9da87e` | Public issue attributes defect to `cmp2lut`; no independently verified fixing revision used | Built in isolated worktree; executable SHA recorded | PassWitness-compatible with explicit `prep -> techmap` flow | Yes | No meaningful removable structure | `FORMALLY VERIFIED`, screened but not reduction-eligible |
| Signed FMA / PR #6231 | Existing PassWitness case study; not counted as an independent pilot benchmark | Clean and patched revisions recorded in release evidence | `arith_tree`; upstream PR remains separate | Existing release evidence | PassWitness-compatible | Previously verified | Separate case study | Not part of Pilot One corpus |

## #1047 verification result

The historical compiler emitted these actual representations:

- pre-`shiftmul`: [Verilog](out/1047-historical/pre-shiftmul.v), [RTLIL](out/1047-historical/pre-shiftmul.il)
- post-`shiftmul`: [Verilog](out/1047-historical/post-shiftmul.v), [RTLIL](out/1047-historical/post-shiftmul.il)

The modern Yosys 0.69 SAT checker loaded the historical RTLIL directly:

- pre-`shiftmul`: `PASS`
- post-`shiftmul`: `FAIL`
- witness: `w = 3'b100`, reference `y = 1`, candidate `y = 0`

The shared PassWitness proof classifier produced those verdicts from explicit
SAT markers, not from process exit codes.

The post-representation was therefore verified as functionally wrong. This is
an imported-representation verification result, not a claim that the released
PassWitness historical synthesis path supports Yosys 0.8.
