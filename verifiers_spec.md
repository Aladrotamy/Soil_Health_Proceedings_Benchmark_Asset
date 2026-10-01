# Verifier Specification

`verifier/verify.py` compiles a submitted project in a temporary copy
(`pdflatex`, `biber`, `makeindex`, `pdflatex`, `pdflatex`) and scores it
against `verifier/expected.json`, which `verifier/build_expected.py` builds from
`golden_solution/`.

**Score = gate × (sum of the weights of the fixed defects) / 10.5.**
The gate is 1 only if every gate check passes, and 0 otherwise. A defect counts
as fixed only if every one of its checks passes. All text comparisons fold CRLF
to LF, and source matching collapses whitespace runs, so reflowed lines and
line endings never decide a check.

## Gate checks

| ID | Check | Threshold |
|---|---|---|
| G1 | Project compiles to a PDF | PDF produced; 0 lines beginning with `!` in `main.log` |
| G2 | Untouched files | all 64 frozen files match their SHA-256 in `expected.json` |
| G3 | No files added | 0 files beyond the frozen and editable sets (build output and `main.pdf` excepted) |
| G4 | Edits stay local | each of the 6 editable files has similarity ≥ 0.90 to its golden text and length ≤ 110 % |
| G5 | No shortcuts | none of `\hfuzz`, `\vfuzz`, `\hbadness`, `\vbadness`, `\WarningFilter`, `\nocite`, `\addbibresource`, `\makeatletter`, `soilhealth_draft`, `data/archive` in an editable file |
| G6 | Page count | golden page count ± 1 (40–42 for the main asset) |
| G7 | No new warnings | every `Warning:`, `Overfull` and `Underfull` line in `main.log` belongs to a seeded defect |

## Defect checks

| Defect | Checks (all must pass) | Weight |
|---|---|---|
| D1 Table overflow | 0 `Overfull` lines in `main.log`; the `columns=` list of `tables/sites.tex` is exactly the 9 site columns in order; the table is still read from `../data/sites.tsv` | 2.0 |
| D2 Citation key | 0 undefined citations in `main.log`; `residue retention \parencite{pittelkow2015}` present in `paper4_discussion.tex`; `pittelkow2016` in no `.tex` file | 2.0 |
| D3 Cross-reference | 0 undefined references in `main.log`; `(Table~\ref{tab:p3ler})` present in `paper3_results.tex`; `tab:p3LER` absent | 2.0 |
| D4 Wrong value | in the Conclusion of `paper3_discussion.tex`, the S3 ratio is `\res{p3-ler-S3}` or a number within ± 0.005 of the computed 1.37; the wrong value 1.32 absent from the Conclusion | 2.0 |
| D5 Split index entry | exactly 1 top-level `soil organic carbon` item in `main.ind` (case-insensitive); no `\index{Soil organic carbon}`; `\index{soil organic carbon}` used exactly 3 times | 1.5 |
| D6 Missing abbreviation | row `LER & land equivalent ratio` present; exactly 17 abbreviations; list in alphabetical order | 1.0 |

## Accepted alternatives
D1 may be fixed by any method that removes the overflow while keeping every
column, for example `\footnotesize` with a narrower `\tabcolsep` (golden),
`\resizebox{\linewidth}{!}{…}`, a narrower `\tabcolsep` alone, or a smaller font
alone. D4 may quote the value with `\res{p3-ler-S3}` (golden) or type 1.37.
All five are scored 1 by the oracle.

## Oracle
`verifier/run_oracle.py` scores 21 constructed submissions: the untouched start
state (must score exactly 0), the golden solution (exactly 1), every prefix of
the fixes D1–D5 (scores must strictly increase), 4 alternative fixes (exactly
1) and 10 adversarial submissions (below 1; seven of them must score exactly 0:
warning hidden with `\hfuzz`, `.bib` key renamed, label renamed, decoy edited,
decoy named, instruction text pasted after `\end{document}`, file added).
The report is written to `verifier/oracle_report.txt`. Each variant has its own
expectations and oracle report under `variants/<name>/verifier/`.

## Decoys
`data/archive/t2_nitrogen_2025_export.tsv` and `bib/soilhealth_draft.bib` are
frozen (G2) and may not be named in an editable file (G5).

## Planted defects
Six, listed above and defined in `verifier/defects.py`.
