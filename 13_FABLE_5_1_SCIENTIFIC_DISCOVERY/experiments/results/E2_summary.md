# E2 summary (regime F, gate level) — run STOPPED before completion (see E2 deviation D3)

Delay-oriented stage (`strash; dch; map`, SKY130 HD). The behavioural baseline and every iso-delay re-map were not completed.
Valid = own AIGER simulation vs numpy passed AND ABC cec "Networks are equivalent".

## n=m=128, p0=0.33

| design | adders U | AIG ANDs | area um^2 | delay ps (mapper) | g1 area / this | valid |
|---|---|---|---|---|---|---|
| g1 | 10932 | 558121 | 2217417 | 4412 | 1.000 | yes |
| ubp2 | 7319 | 551235 | 1869482 | 5520 | 1.186 | yes |
| ubp3 | 5594 | 534357 | 1868914 | 6201 | 1.186 | yes |
| ubp4 | 5068 | 496658 | 1875014 | 5011 | 1.183 | yes |
| cbp4 | 5032 | 496621 | 1862251 | 5036 | 1.191 | yes |
| da4ml | 4148 | 428976 | 1610877 | 5268 | 1.377 | yes |

best UBP (ubp3): g1/UBP area = 1.186 with UBP slower than g1 in every case.

## n=m=128, p0=0.5

| design | adders U | AIG ANDs | area um^2 | delay ps (mapper) | g1 area / this | valid |
|---|---|---|---|---|---|---|
| g1 | 8100 | 465695 | 1930894 | 3900 | 1.000 | yes |
| ubp2 | 6148 | 478674 | 1632487 | 5169 | 1.183 | yes |
| ubp3 | 5094 | 472401 | 1652382 | 5793 | 1.169 | yes |
| ubp4 | 4866 | 456699 | 1667681 | 5229 | 1.158 | yes |
| cbp4 | 4721 | 456710 | 1669881 | 5230 | 1.156 | yes |
| da4ml | 3613 | 363763 | 1379334 | 4944 | 1.400 | yes |

best UBP (ubp2): g1/UBP area = 1.183 with UBP slower than g1 in every case.

## Registered verdicts

- K2a (g1/best-UBP < 1.3 at iso-delay for both p0): not measured at iso-delay. **Bounded inference:** at the delay-oriented stage the ratio is already 1.19 (p0=.33) and 1.18 (p0=.5), and every UBP mapping is slower than g1. Iso-delay sets D* to the slowest design's delay, and every faster design is relaxed to D*. g1 receives the most relative slack, because its delay-optimal delay (3.9–4.4 ns) is the lowest (UBP: 5.0–6.2 ns). So the iso-delay ratio is *expected*, though not guaranteed, to be at or below these values, i.e. K2a would be met (the regime-F advantage does not survive). Consistent with E1-hashed.
- K2b (behavioural baseline within 1.2x of best UBP): not evaluated (behavioural run stopped). The adder-level analogue (hashed per-input trees within 1.04–1.20x of UBP; E1-hashed) indicates yes.
