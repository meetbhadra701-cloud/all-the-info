# 03 — Research tree (living)

```
P1  Accumulation hardware of hardwired linear layers when base layers are weight-independent (regime V)
│   parent: 13_FABLE_5_1 (HIST-OBS: survivor)
├── H1.1 Bit-parallel universal block patterns (UBP-g)
│   ├── Mechanism: GEN(g) per block + TREE(⌈n/g⌉,w) per neuron + via-selected lines
│   ├── Prior-art challenge: LUT-GEMM (ingredient); HNLPU in-neuron grouping (provisional delta)
│   ├── Evidence (HIST-OBS): adders ≈ g× (exact); cells 1.95×/2.49× at iso-delay (E3)
│   ├── Critical assumption: select wiring fits (MODEL only)
│   ├── Experiment: E5 PnR, weight-independent hierarchy-preserved fabrics, SKY130, iso-clock   ← NEXT
│   ├── Result: (pending)
│   └── Decision: (pending)
├── H1.2 Bit-serial UBP (evolution; single-wire lines; width-independent per-site cost)
│   ├── Mechanism: serial-adder generators; popcount neurons fed by shared pattern streams
│   ├── Critical assumption: no cycle penalty at iso-throughput; small serial generator overhead
│   ├── Experiment: E6 gate-level iso-throughput (then PnR if budget)   ← only if justified by E5
│   └── Result: (not started)
└── H1.3 Cross-matrix generator sharing → MERGED as a design rule into H1.1/H1.2

P2  Functional yield of hardwired weights (reserve; not executable here)
├── H2.1 Adapter-as-redundancy (rank-r SRAM adapter replaces r defective rows)
└── H2.2 Defect-benign one-hot encodings

P3  Hash-friendly full-custom CMVM
└── H3.1 greedy hash-maximizing pairing → MERGED/KILLED (= Paar-style CSE; da4ml stronger)
```

## Branch records

| Branch | Problem | Mechanism | Assumptions | Evidence | Prior art | Experiment | Result | Decision | Next question |
|---|---|---|---|---|---|---|---|---|---|
| H1.1 | P1 | bit-parallel UBP | wiring fits at g = 3 | E1 closed forms; E3 cells | LUT-GEMM; HNLPU (prov.) | E5 PnR | pending | pending | Does routed area keep ≥ 1.5×? |
| H1.2 | P1 | bit-serial UBP | width-independent per-site cost | none yet | HNLPU POPCNT (closest) | E6 | — | — | Does serialization remove the wire and width penalties? |
| H2.1 | P2 | adapter-as-redundancy | defects within rank r | none | RRAM LoRA compensation; DNN yield tolerance | none possible here | — | reserve | Defect statistics of via ROMs? |
| H3.1 | P3 | hash-friendly pairing | — | E1-hashed (HIST-OBS) | Paar; da4ml | — | — | merged/killed | — |
