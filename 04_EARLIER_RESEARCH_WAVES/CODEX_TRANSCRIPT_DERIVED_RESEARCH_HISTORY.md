# Earlier research history recovered from Codex session records

This file records findings whose original reports were not present as ordinary local files but whose final-session messages were recoverable from the local Codex backup database. They are transcript-derived summaries, not substitutes for the missing source artifacts. Thread IDs are included for provenance.

## Wave 3: physical-design and ECO evidence

### Wave 3A — incremental versus full ECO order

Thread `01a0a7b6-1fc2-70d0-900e-aa37fdd5905e` reported a controlled ranking experiment over 20 valid one-cell-upsize candidates, with 40 primary and 24 seed-control observations. Incremental-versus-full ECO rankings were weak and seed-sensitive: WNS Spearman 0.142 / Kendall 0.096 with 74 reversals and zero top-five overlap; TNS 0.247 / 0.158 with 80 reversals and one top-five overlap; wirelength -0.334 / -0.211 with 115 reversals and zero top-five overlap; vias 0.354 / 0.263 with 67 reversals and two top-five overlaps; displacement 0.504 / 0.357 with 57 reversals and two top-five overlaps. A persistent C05>C06 reversal under incremental but the opposite under full was observed across seeds. This supports a history-dependent ranking effect, but the local package lacks the original scripts and complete raw data.

### Wave 3B/3C — real-synthesis and actual-netlist bridges

Threads `01a0a803-2588-7b33-a0a6-d0e855d4c58d` and `01a0a805-3af7-71e2-ae8b-25f7ed1c2471` investigated whether a real synthesis/physical-design bridge could turn abstract optimization into an evidence-backed contribution. The original final reports were not recovered locally. Treat the existence and broad direction as transcript evidence only; do not claim a completed publication-grade result without the missing artifacts.

## Wave 4: physical memory and retiming directions

Threads `01a0a926-a2bf-7841-a472-039dff4e12bf` and `01a0a938-2de5-75b1-8216-8eea006cf04e` covered banked-memory topologies and temporal retiming/composition. The original reports were not recovered locally. Later transcript evidence indicates the recurring issue: implementation-visible behavior and timing/physical effects can be real, while the proposed general scientific mechanism is already covered or lacks a clean independent oracle.

## Wave 5: memory mapping, power recovery, and hardware-security attacks

### Wave 5B — memory semantic contract and physical mapping

Threads `01a0ae39-d389-75d2-9330-701c7485cec5` and `01a0a99b-540c-7d33-9e3a-a09db01d33f6` reported a fixed 16x128 memory study. The transcript gives the following concrete observations: NEW+WHOLE_WORD and OLD+NATIVE_GRANULARITY each mapped to one RAM; NEW+NATIVE_GRANULARITY mapped to zero RAM with 2072 LUTs and 2064 FFs; eight depth-2 post-map checks passed; all pre-memory-libmap `$mem_v2` cells had WR_PORTS=1; native masks were represented as one 16-bit enable vector; OLD/native mapped to SB_RAM40_4K, while NEW/native and UNDEFINED/native fell back to FF/LUT because of an unregistered-read structural reason. A constructive witness using one explicit SB_RAM40_4K plus 39 LUT4 and 33 DFFE passed 524,288 transitions and a 262,144 depth-128 mapped address/mask sweep with zero failures.

The transcript also records an important qualification: an older canonical witness had a mask-encoding inconsistency (byte-enable mask versus forwarding all 16 bits) and was excluded from equivalence. The safest interpretation is a mapper emulation/composition or engineering-contract gap, not a confirmed new semantic theory.

### Wave 5B Assassin — resource cliff

Thread `01a0b0d3-9c53-7c61-b6fd-730a317ed3e5` concluded that the resource cliff was explained by ordinary register retiming plus incomplete memory-inference recognition, not a new mathematical notion. The malformed canonical witness was excluded from equivalence for the mask inconsistency described above.

### Wave 5C — power recovery to electrical legality

Thread `01a0a99d-1b4e-7b01-9851-9160fa32250d` reported a corrected harness with fixed DEF/placement/library/RC and only the create_clock period varied. It observed max-cap values changing from approximately 23.03 versus 60.65 before recovery to approximately 70.24 versus the same limit after recovery, with max slew below 0.1985. This is evidence of a real electrical-legality seam in the tested setup, but not evidence of a novel general method; the original report and full harness were not recovered.

## Wave 6: formal verification, HLS, and cross-stage guarantees

### Wave 6A-C — L2S liveness witness extraction

Thread `01a0a1cd-213e-7b83-9e85-e73a3d6bf931` reported that the baseline L2S witness passed, equivalent-latch elimination and XOR state reparameterization passed the full witness obligations, and a negative control caught a liveness failure. The interpretation was that the existing composition already suffices for the tested transformations; no separate novel witness mechanism was established.

### Wave 6C-B — CODO

Thread `01a0b1d8-1d76-7030-8417-a1daef22189d` reported that CODO built 71/71 and that a GPT2 public flow ran, but the exact paper A→B→C→D ping-pong case was not present in the artifact/paper/history. The result was classified INCONCLUSIVE. The original dossier was not recovered locally.

### Wave 6C-C — EagerlyElastic × LSQ

The locally recovered dossier is `WAVE_6C_C/WAVE 6C-C — EAGERLYELASTIC × LSQ FRONTIER DOSSIER.md`. Its official artifact/source zip is in `SUPPORTING_ARTIFACTS/WAVE_6C_C/`. The transcript record identifies the official Zenodo artifact `10.5281/zenodo.18033076` and Dynamatic commit `7d33a780b8907cd395065dc8a283836a3563418a`. The baseline flow was identified, but the original reproduction environment lacked a usable container runtime; no end-to-end execution was completed. Classification: BASELINE NOT REPRODUCED.

### Wave 6D-A — MaskedHLSVerif

Thread `01a0b2e9-bad6-7bf0-aea8-f32182effad7` reported that baseline reproduction stopped before A/B experiments. The identified references were MaskedHLS_LP commit `51c36d602028c2b763cc8ce439a0f17e240f8d5e`, the MaskedHLSVerif paper dated 2026-03-19, and REBECCA commit `09c93f8994ca09352e967221c4c407d060e8ea99`. Missing Vitis HLS 2022.2, Yosys, C++, Icarus, Python packages, and wrapper support prevented a completed experiment. Classification: INCONCLUSIVE.
