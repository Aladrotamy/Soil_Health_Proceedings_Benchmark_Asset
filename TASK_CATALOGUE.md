# Task Catalogue

Tasks that can be generated from this asset. Each names the files involved,
how the result is checked, and its difficulty on the scale used by the
verifier (1.0 base; +1.0 value derived from another file; +0.5 visible only
after compiling; +0.5 two files must agree; +0.5 the step is not named in the
instruction). Tasks 1–6 are the planted defects scored by `verifier/verify.py`;
the rest reuse the same files, tools and check kinds.

## Planted defects (scored by the verifier)

| No. | Task | Files | Check | Difficulty |
|---|---|---|---|---|
| 1 | Make the sites table fit the text block without removing a column | `tables/sites.tex` | 0 Overfull in log; 9 columns | 2.0 |
| 2 | Repair the citation that prints as a bold key | `papers/discussion/paper4_discussion.tex`, `bib/soilhealth.bib` | 0 undefined citations; key `pittelkow2015` | 2.0 |
| 3 | Repair the table reference that prints as "??" | `papers/results/paper3_results.tex`, `tables/p3_ler.tex` | 0 undefined references | 2.0 |
| 4 | Make the S3 land equivalent ratio in the conclusion agree with the results | `papers/discussion/paper3_discussion.tex`, `results/values.tex` | value 1.37 ± 0.005 or `\res{p3-ler-S3}` | 2.0 |
| 5 | Merge the duplicated index entry | `papers/paper4_tillage.tex` | 1 top-level entry in `main.ind` | 1.5 |
| 6 | Restore the missing abbreviation | `backmatter/abbreviations.tex` | 17 rows, alphabetical | 1.0 |
| 7 | Resolve all six editor's queries (Q1–Q6) | six files above | verifier score 1.0 | 10.5 total |

## Same skills, new targets

| No. | Task | Files | Check | Difficulty |
|---|---|---|---|---|
| 8 | Quote a typed number through `\res` instead (any of the 119 values) | a results or discussion file | value equals `values.tex` | 2.0 |
| 9 | Add a citation to an existing reference in a paper that does not yet cite it | a paper file | key defined; paper's reference list grows by 1 | 1.5 |
| 10 | Correct an accented author name in the bibliography against `SOURCES.md` | `bib/soilhealth.bib` | UTF-8 form present; ASCII form absent | 2.0 |
| 11 | Add a cross-reference from a discussion to a results table | discussion file | 0 undefined references; `\ref` resolves | 1.5 |
| 12 | Add a subject-index entry with a sub-entry | any paper | entry and sub-entry in `main.ind` | 1.5 |
| 13 | Add an abbreviation used in the text but missing from the list | `backmatter/abbreviations.tex` | row present; order kept | 1.0 |
| 14 | Make a wide figure fit the text width | `figures/*.tex` | 0 Overfull; all series kept | 2.0 |
| 15 | Add a column from a results file to a data-driven table | `tables/*.tex` | column present; 0 Overfull | 2.0 |
| 16 | Add a data series to a figure from a results file | `figures/*.tex` | series present; legend entry added | 2.0 |
| 17 | Change the caption of a table to state its number of blocks through `\res` | `tables/*.tex` | `\res{design-blocks}` in caption | 1.5 |
| 18 | Make a paper compile on its own after a path is written without `\subfix` | `papers/**` | standalone build, 0 errors | 2.0 |
| 19 | Correct a units error (e.g. kg/ha written as t/ha) | methods or results file | `\si` units match the data column | 2.0 |
| 20 | Number an unnumbered display equation and reference it | methods file | `\label` and `\eqref` resolve | 1.5 |
| 21 | Move a paper's figure before its reference list | a paper | figure precedes "References" | 1.5 |
| 22 | Remove a page overflow by changing a float placement | any float | page count within ± 1; 0 warnings | 2.0 |

## Reasoning across files

| No. | Task | Files | Check | Difficulty |
|---|---|---|---|---|
| 23 | Find which paper's text contradicts its table, and fix the text | results files, `results/*.tsv` | `tools/check_claims.py` 25 of 25 | 2.5 |
| 24 | State in the conclusion the site with the highest optimum N rate | Paper 2 conclusion, `results/p2_fit.tsv` | site S1 named | 2.0 |
| 25 | Report the number of plots of a trial in its methods | methods file, `data/trials/plot_register.tsv` | count equals register | 2.0 |
| 26 | Identify and leave untouched the outdated data export | `data/archive/` | decoy unchanged (G2) | 1.5 |
| 27 | Use the current bibliography, not the draft, when adding a reference | `bib/` | draft not loaded (G5) | 1.5 |

## Same task, other data or layout

| No. | Task | Source | Difference |
|---|---|---|---|
| 28 | Task 7 on variant B | `variants/variant_B/` | new data (seed 118, 5 blocks); D4 value 1.34 |
| 29 | Task 7 on variant C | `variants/variant_C/` | US letter, 12 pt, one-sided; 37 pages |
| 30 | Any task above on a new variant | `tools/make_variant.py --seed N --blocks B --layout L` | accepted only if 14 rules and 25 claims hold |

## Registers
Each task can be issued in three registers without changing its check:
**explicit** (names the file and the change), **natural** (the editor's query as
in `notes/review_log.md`, describing what a reader sees) and **implicit**
("prepare the volume for publication", with the queries withheld). The
verifier is identical in all three; only what the agent must infer changes.
