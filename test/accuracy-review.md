# Three-scan accuracy and robustness report

The three reference sets supplied by the user are evaluation labels. They are not injected into predictions. No fourth test was available. Physical circumference labels are not yet supplied.

| Test | Reference little/ring/middle/index | Current result | Correct |
|---|---|---|---|
| Test N1 | 6 / 8 / 10 / 10 | 8 / 6 / 8 / 10 | 1/4 |
| Test N2 | 8 / 10 / 10 / 10 | 8 / 10 / 10 / 12 | 3/4 |
| Test N3 | 6 / 8 / 8 / 8 | 6 / 6 / 6 / 10 | 1/4 |

The original pipeline matches 5/12 product sizes. The stability update retains those estimates, so accuracy remains 5/12. It does not claim improved physical sizing accuracy.

## Evidence

- The original photos are not black. Card calibration is about 5.55, 5.98 and 6.05 pixels/mm respectively.
- Finger-only edge crops in edge-comparison.jpg show selected endpoints generally close to the visible skin outline. There is no evidence that a single image-scale adjustment would resolve all labels.
- N1 and N2 little-finger widths are 17.74 and 17.67 mm, yet reference sizes are 6 and 8. A simple monotonic width-only model cannot robustly separate these nearly identical widths into those labels.
- Reprocessing a smaller version of the same N2 image changes the middle-finger result from 10 to 12. N3 little changes from 6 to outside the table. These are processing/boundary sensitivities, not physical finger changes.
- Mean absolute deviations describe agreement between neighboring samples, not accuracy against measured circumference. High quality percentages cannot validate a wrong shape assumption.

## Implemented robustness change

Each full analysis now compares a second, 85%-scale image when reference resolution remains sufficient. A stock-size disagreement, more than 0.75 mm circumference difference, or failed comparison marks the result unstable and caps image quality at 50%. The original full-resolution estimate remains visible, alongside a retry notice. Full comparison values are saved with each finger trace. The threshold is an engineering sensitivity check, not a calibrated error bound.

## Accuracy solution

A photo of visible width needs a validated circumference mapping learned against actual circumferences, or an additional measurement that observes finger depth. The existing local calibration pipeline accepts actual circumference labels and validates on held-out people. Twelve product labels across these scans are not enough to establish a deployable model. circumference-reference.csv provides a worksheet for recording true circumferences and stable person IDs; do not enter a stock-size midpoint as if it were a physical measurement. More independent people and repeat captures are needed before enabling a validated calibration model.

Reference: https://fengx.io/work/ring-sizer-sub-millimeter-finger-measurement-via-computer-vision/ describes a calibrated measurement pipeline; its reported errors and coefficients are not evidence of accuracy for this app.
