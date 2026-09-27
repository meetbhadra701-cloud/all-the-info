# 03 — Research tree (Wave 14 + gates G1–G3 + final decision run R3)

```
P1  Accumulation hardware of hardwired linear layers when base layers are weight-independent (regime V)
│   parent: 13_FABLE_5_1 (HIST-OBS survivor)            STATUS: PROBLEM CONFIRMED — primary thesis
├── H1.1 Bit-parallel universal block patterns (UBP-g)
│   ├── Mechanism: GEN(g) per block + NEG per line + TREE(⌈n/g⌉, w) per neuron; via selects line / −line / 0
│   ├── Critical assumption: select wiring fits
│   ├── Experiment: E5 (n = 32, SKY130, ORFS PnR; A1 relaxed clock; A2 full fabric)
│   ├── Result: UBP3 DRC-clean at U = 60, global-route congestion at U = 75 (g1 routes at 75)
│   │           → ratio 1.67× (2.08× at equal U); post-route delay 1.10× g1; select WL 1.58× lower
│   └── Decision: A5 MET narrowly (1.59× on the tie-corrected basis) — WEAKENED (routability-limited), superseded by H1.2
├── H1.2 Bit-serial UBP  (evolution iteration 1)                  STATUS: SURVIVOR
│   ├── Mechanism: serial registered adders; 1-wire pattern lines; serial trees fed by shared pattern streams
│   ├── Why: bit-parallel generator depth (pre-placement 1.43× delay) and w-bit select buses
│   ├── Experiment: E6 (n = 64, real 3.0 ns clock + CTS, equal throughput)
│   ├── Result: UBP3 2.13× smaller routed area; DRC-clean at U = 75 like g1; timing met (2.08 vs 2.22 ns);
│   │           +1 cycle latency; select WL 5.8× lower; final routed netlists = numpy W@x
│   ├── Decision: A6 MET → primary thesis (12); gates G1–G3 (14)
│   └── Gates (15–19, 2026-09-27)                                 STATUS: PHYSICALLY VALIDATED — NOVELTY PROVISIONAL (19)
│       ├── G1 novelty: no identical/equivalent mechanism; likely obvious composition → MATERIALLY DOWNGRADED
│       ├── G3 competitors (hardwired W): A×T B 6.10e6 < P2 11.23e6 < A 13.84e6 < P 15.24e6; DA(K≥2) ≥ P → SURVIVES (S3)
│       ├── G2 fixed base, generic placement: B's W1/W2 unroutable on met4-met5 at U 60…8 → K2b: SUBSTANTIALLY WEAKENED
│       └── R2 structured W-blind crossbar base (bounded revision):
│           ├── GRT: all 5 W route for B at U60/52/45, P2 at U60/67, A at U60/75; A×T B 8.10e6 vs P2 14.98e6, A 14.28e6
│           ├── DRT (20 it.): B 1,167 / 881 / 416 residual (U60/52/45) — P2 and A close at every U; post hoc 64 it.: B closes at U45 only (52: 117, 60: 410)
│           ├── R2-K not fired, R2-A not granted → G2 UNRESOLVED (class then: PROMISING BUT KEY GATE UNRESOLVED)
│           └── R3 segmented line access (final layout revision; pre-registered, f7f33ba):
│               ├── 4 taps/line on a base spine, row quarters, area-neutral; W-blind placement from development matrices
│               ├── U52 (decisive): 5/5 W DRT 0 (≤ 14 it.), invariant, = numpy; A×T 9.26e6 = 1.538× vs A75, 1.612× vs P2 67 → PASS
│               ├── U60: 5/5 W DRT 0, invariant, = numpy; A×T 8.57e6 = 1.663× vs A75 → PASS
│               ├── P2-R3 (fairness, U67): valid, A×T 17.88e6 (weaker than P2); driver-sized (post hoc) 13.69e6 → B 1.478× / 1.60–1.73×
│               └── G2 CLOSED → PHYSICALLY VALIDATED — NOVELTY PROVISIONAL; robust at 60%, break-even at 52%
└── H1.3 Cross-matrix generator sharing → MERGED as a design rule into H1.1/H1.2

P2  Functional yield of hardwired weights                          STATUS: RESERVE (not executable here)
├── H2.1 Adapter-as-redundancy (rank-r SRAM adapter replaces r defective rows)
└── H2.2 Defect-benign one-hot encodings

P3  Hash-friendly full-custom CMVM                                 STATUS: KILLED (prior art)
└── H3.1 Greedy hash-maximizing pairing → = Paar-style CSE; da4ml stronger
```

## Branch records

| Branch | Problem | Mechanism | Assumptions | Evidence | Prior art | Experiment | Result | Decision | Next question |
|---|---|---|---|---|---|---|---|---|---|
| H1.1 | P1 | bit-parallel UBP | select buses fit | E1 closed forms; E3 cells; **E5 PnR** | LUT-GEMM (runtime); HNLPU (g = 1, provisional) | E5 | 1.67×; loses one utilization step to congestion; 1.10× delay | weakened; superseded | none (use H1.2) |
| H1.2 | P1 | bit-serial UBP | 1-wire lines route like g1 (hardwired); lines reachable from all rows (fixed base) | **E6, G3, G2, R2, R3 PnR** | HNLPU POPCNT; TENET/T-MAC (runtime); segmented channel routing (layout principle); G1: likely obvious composition | E6, G3, G2, R2, R3 | hardwired: 2.13× area, 1.84× A×T vs P2; fixed base: generic collapse; R2 GRT only; **R3: 5/5 W DRC-clean at 52% and 60%, 1.54× / 1.66× vs A75** (driver-sized P2-R3: 1.48× / 1.60–1.73×) | **PHYSICALLY VALIDATED — NOVELTY PROVISIONAL** | Paper-scale plan (19 §H): driver closure for all designs, real weights, scale, advanced node, energy, novelty full texts |
| H2.1 | P2 | adapter-as-redundancy | defects within rank r | none | RRAM LoRA compensation | none possible here | — | reserve | Via-ROM defect statistics? |
| H3.1 | P3 | hash-friendly pairing | — | E1-hashed (HIST-OBS) | Paar; da4ml | — | — | killed | — |

## Amendments and deviations affecting the tree

| ID | What happened | Effect |
|---|---|---|
| A1 | Relaxed E5 clock | Removes the timing-repair confound |
| A2 | W-dependent pruning removed; UBP runs repeated on full fabrics | Pruned runs superseded; they overstated E5 ubp3 by 4% and ubp4 by up to 27% |
| D6.1 | E6 top-level flip-flops emitted as cells | Format fix only |
| D-G3.1 | P re-run at 5.0 ns (unpipelined P cannot pack at 3.0 ns) | Metric uses achieved period; unaffected |
| D-G2.1 | P2 base built alongside A as G2 baseline | Same programmable structure as A |
| D-G2.2 | Base PDN = met1 rails only (via-stack/strap shorts) | Equal for all designs; IR out of scope |
| R2 | Structured W-blind crossbar placement of via sites/taps (pre-registered bounded revision) | Removes generic-placement collapse; B's DRT still unclosed |
| R3 | Segmented line taps: 4 per line on a base spine, row quarters (pre-registered final revision) | Closes B's DRT at 52% and 60% for all 5 W; G2 passes |
| D-R3.1 | `r3_build.py` generalized to build the pre-registered P2-R3 point | Implementation only |
| D-R3.2–3 | Routed-parasitic timing check (post hoc) | 52% at break-even (1.495× vs A); 60% robust (1.673×) |
| D-R3.4 | Spine-driver sizing sensitivity, STA only (post hoc) | Driver-sized P2-R3 is strongest: B 1.478× (52%), 1.60–1.73× (60%). Stated as the standing qualification |
