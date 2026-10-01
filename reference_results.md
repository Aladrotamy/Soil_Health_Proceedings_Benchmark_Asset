# Reference Results

Values of the golden solution of the main asset (seed 20261001, 4 blocks, 228
plots), computed by `tools/compute_results.py` and quoted in the volume through
`results/values.tex`. Tolerances state how far a recomputed value may differ
before it counts as wrong; they cover rounding to the printed number of
decimals only, since regeneration is byte-identical.

## Build

| Quantity | Value | Tolerance |
|---|---|---|
| Pages of the volume | 41 | ± 1 (verifier G6) |
| Errors, warnings, overfull and underfull boxes in `main.log` | 0 | exact |
| Papers typeset on their own | 6 of 6, pages 5, 5, 4, 5, 4, 4 | exact |
| References cited | 18 of 18 in `bib/soilhealth.bib` | exact |
| Index | 43 `\index` commands, 29 distinct entries | exact |
| Abbreviations | 17 | exact |

## Data

| Quantity | Value | Tolerance |
|---|---|---|
| Data rules R1–R14 | 14 of 14 pass, 0 violations | exact |
| Text claims | 25 of 25 hold | exact |
| Plots in the register | 228 (T1 36, T2 60, T3 36, T4 48, T5 48) | exact |

## Results

| Paper | Quantity | S1 | S2 | S3 | Tolerance |
|---|---|---|---|---|---|
| 1 | Soil health index, CONV | 0.682 | 0.342 | 0.566 | ± 0.0005 |
| 1 | Soil health index, INTG | 0.880 | 0.502 | 0.790 | ± 0.0005 |
| 2 | Agronomic optimum N rate (kg/ha) | 143 | 125 | 137 | ± 0.5 |
| 2 | Plateau yield (t/ha) | 9.83 | 5.69 | 7.72 | ± 0.005 |
| 2 | R² of the quadratic-plateau fit | 0.976 | 0.931 | 0.982 | ± 0.0005 |
| 3 | Total land equivalent ratio | 1.23 | 1.28 | **1.37** | ± 0.005 (D4) |
| 4 | ΔSOC, CT-R0 (g/kg) | −0.35 | −0.20 | −0.42 | ± 0.005 |
| 4 | ΔSOC, NT-R1 (g/kg) | 1.50 | 0.62 | 1.10 | ± 0.005 |
| 5 | Mean carbon retention | 0.183 | 0.117 | 0.215 | ± 0.0005 |

Combined analysis of variance of maize yield, trial T2 (Paper 6): F(site) =
228.36, F(nitrogen) = 615.15, F(site × nitrogen) = 7.58, F(blocks within
sites) = 3.80, all P < 0.05; 36 residual degrees of freedom; t₀.₀₂₅ = 2.028;
least significant difference 0.40 t/ha. Tolerance ± 0.005 on each printed value.

## Verification

| Quantity | Value |
|---|---|
| Start state (`project_source/`) | score 0.0000 |
| Golden solution | score 1.0000 |
| Prefix scores D1 … D1–D5 | 0.1905, 0.3810, 0.5714, 0.7619, 0.9048 |
| Oracle | 21 of 21 cases, on Linux and on Windows |

## Variants

| Variant | Parameters | Pages | S3 land equivalent ratio (D4 seeded as) | Oracle |
|---|---|---|---|---|
| B | seed 118, 5 blocks (285 plots) | 41 | 1.34 (1.29) | 21 of 21 |
| C | US letter, 12 pt, one-sided | 37 | 1.37 (1.32) | 21 of 21 |

The data, results and model are synthetic and demonstrative. They must not be
presented as evidence about real soils, crops or farming systems.
