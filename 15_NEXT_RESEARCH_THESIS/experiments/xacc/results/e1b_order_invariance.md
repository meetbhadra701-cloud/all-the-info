| Data | K | FP32: outputs order-sensitive | FP32 max / median ULP spread | FP32 rel. err. (median / max) | Exact: order-sensitive | Exact = independent reference | Wrap mutant detected |
|---|---|---|---|---|---|---|---|
| gauss | 4096 | 0.0% | 0 / 0 | 2.09e-08 / 5.94e-08 | 0.0% | True | True (wrap 44 b; max |sum| 48 b) |
| student_t3 | 4096 | 0.0% | 0 / 0 | 2.09e-08 / 5.88e-08 | 0.0% | True | False (wrap 44 b; max |sum| 42 b) |
| outlier_channels | 4096 | 0.0% | 0 / 0 | 2.08e-08 / 5.86e-08 | 0.0% | True | True (wrap 44 b; max |sum| 45 b) |
| gauss | 16384 | 0.0% | 0 / 0 | 2.05e-08 / 5.86e-08 | 0.0% | True | True (wrap 46 b; max |sum| 48 b) |
| student_t3 | 16384 | 0.0% | 0 / 0 | 2.01e-08 / 5.90e-08 | 0.0% | True | False (wrap 46 b; max |sum| 40 b) |
| outlier_channels | 16384 | 0.1% | 1 / 0 | 2.11e-08 / 6.62e-08 | 0.0% | True | False (wrap 46 b; max |sum| 46 b) |
