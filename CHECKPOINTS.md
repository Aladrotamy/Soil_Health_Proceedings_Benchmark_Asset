# Checkpoints

All checks are pass/fail, and every check states its threshold. A milestone is complete only when every check passes.

Build sequence used for every milestone: `pdflatex main` → `biber main` → `makeindex main` → `pdflatex main` → `pdflatex main`.

## M1 — Volume Foundation

**Status:** Complete
**Snapshot:** `milestone_1_foundation/`
**Toolchain:** MiKTeX 26.5 (pdfTeX 4.27), biber 2.22, makeindex, via TeXstudio

### Work completed
- Created the project structure under `project_source/` with 8 folders: backmatter, bib, build, data, figures, frontmatter, notes, papers.
- Created the house style `soilproc.sty`: A4 two-sided page layout, T1 fonts with Latin Modern, British English, microtype, siunitx for units, booktabs, pgfplots (compat 1.18), running heads, clean blank pages (emptypage), biblatex with the biber backend (author–year), a subject index with imakeidx (makeindex run as its own step), hyperref, and subfiles for separately typeset papers.
- Defined the volume metadata macros `\volumetitle`, `\volumeshort`, `\volumenumber` and `\volumeeditor` (Rotimi Alade).
- Created the master file `main.tex` with front matter, main matter and back matter divisions.
- Created four front-matter files: title page, imprint, editor's preface, and "How This Volume Is Organised".
- Stated on the imprint that the symposium is fictional and that all papers, trials, sites and datasets are synthetic, and fixed the unit conventions (SI; t/ha dry matter; g/kg soil organic carbon; pH in water at 1:2.5).

### Pass/fail checks
| ID | Check | Threshold | Result |
|---|---|---|---|
| C1.1 | Full build sequence completes | 0 errors in `main.log`; biber and makeindex exit normally | PASS |
| C1.2 | Warnings and bad boxes in `main.log` | exactly 0 matches for `^!`, `Warning`, `Overfull`, `Underfull` | PASS (0) |
| C1.3 | Compiled page count | exactly 8 | PASS (8) |
| C1.4 | `soilproc.sty` defines `\volumetitle`, `\volumeshort`, `\volumenumber`, `\volumeeditor` | all 4 present | PASS |
| C1.5 | `soilproc.sty` loads biblatex with `backend=biber`, imakeidx with `noautomatic`, and subfiles | all 3 present | PASS |
| C1.6 | Front-matter files in `frontmatter/`: `titlepage.tex`, `imprint.tex`, `preface.tex`, `organisation.tex` | exactly 4, each `\input` once by `main.tex` | PASS |
| C1.7 | Contents lists "Editor's Preface" and "How This Volume Is Organised" | both present | PASS |
| C1.8 | Imprint states that the symposium is fictional and the data synthetic | both statements present | PASS |
| C1.9 | Title page names the editor | "Edited by Rotimi Alade" present | PASS |
| C1.10 | Pages left blank before a chapter carry no running head or page number | 0 words of text on pages 4 and 6 | PASS |
| C1.11 | Source files in `project_source/` | exactly 6 (`main.tex`, `soilproc.sty`, 4 front-matter files) | PASS (6) |
| C1.12 | Text files stored with LF line endings | 0 CRLF files | PASS (0) |


## M2 — References and Paper Framework

**Status:** Complete
**Snapshot:** `milestone_2_references/`
**Toolchain:** MiKTeX 26.5 (pdfTeX 4.27), biber 2.22, makeindex, via TeXstudio and Git Bash

### Work completed
- Created `bib/soilhealth.bib` with 18 references to published soil science, agronomy and field-experimentation literature. Every entry was checked against a publisher, library or repository record before it was added. Accented author names (Bünemann, Mäder, Kögel-Knabner, von Lützow, Schöb) are written directly in UTF-8 and processed by biber.
- Extended `soilproc.sty` with the paper layout: chapters labelled "Paper", a `paper` environment giving each paper its own reference section, a `paperabstract` environment and a `\paperkeywords` command. Enabled `useprefix` so that "von Lützow" is cited and sorted with its prefix.
- Added six contributed papers under `papers/`, each with title, short running-head title, abstract, keywords and introduction: (1) minimum dataset of soil health indicators; (2) nitrogen rate and nitrogen use efficiency in maize; (3) maize–cowpea intercropping and the land equivalent ratio; (4) tillage, residues and soil organic carbon; (5) organic amendments and carbon stabilisation; (6) design and analysis of multi-site field trials.
- Connected the papers to `main.tex` with `\subfile`, so that each paper is typeset both inside the volume and on its own. Filtered the single LaTeX warning that subfiles causes when a paper is typeset alone (package requested as `../soilproc`), using the silence package with a filter for exactly that message.
- Excluded the standalone paper PDFs from Git (`**/papers/*.pdf`); `main.pdf` remains the committed output.

### Pass/fail checks
| ID | Check | Threshold | Result |
|---|---|---|---|
| C2.1 | Full build of `main.tex` completes | 0 errors; biber and makeindex exit normally | PASS |
| C2.2 | Warnings and bad boxes in `main.log` | exactly 0 matches for `^!`, `Warning:`, `Overfull`, `Underfull` | PASS (0) |
| C2.3 | Compiled page count of the volume | exactly 20 | PASS (20) |
| C2.4 | Entries in `bib/soilhealth.bib` | exactly 18: 15 with DOI, 1 with URL, 1 with ISBN, 1 identified by journal volume and pages | PASS (18) |
| C2.5 | Every bibliography entry cited at least once in the papers | 18 of 18 | PASS (18/18) |
| C2.6 | Papers in `papers/`, each connected by `\subfile` in `main.tex` | exactly 6, each `\subfile` once | PASS (6) |
| C2.7 | Each paper typeset on its own | 6 of 6 compile with 0 issues; 2 pages each | PASS (6/6) |
| C2.8 | Reference lists are per paper | 6 reference sections; each lists only the works its paper cites (4 to 7 each) | PASS |
| C2.9 | Accented names written in UTF-8 in the `.bib`, and first authors rendered correctly in the PDF | Bünemann, Mäder, Kögel-Knabner, von Lützow, Schöb present in the `.bib`; "Bünemann et al." and "von Lützow et al." printed in citations | PASS |
| C2.10 | Chapters of the main matter labelled "Paper" | "Paper 1" to "Paper 6" | PASS |
| C2.11 | Each paper has an abstract and keywords | 6 of 6 | PASS |
| C2.12 | Text files stored with LF line endings | 0 CRLF files | PASS (0) |


## M3 — Data Layer and Methods

**Status:** Complete
**Snapshot:** `milestone_3_data_methods/`
**Toolchain:** MiKTeX 26.5 (pdfTeX 4.27), biber 2.22, makeindex, Python 3.12 (standard library only)

### Work completed
- Added the seeded data generator `tools/make_trials.py` (default seed 20261001, 4 blocks; options `--seed`, `--blocks`, `--out`). It writes `data/sites.tsv` (3 fictional sites in temperate, semi-arid and humid tropical zones) and six files in `data/trials/`: one per trial (T1–T5) and `plot_register.tsv`, which lists every plot of every trial. Output uses LF line endings and fixed decimal places, so it is byte-identical on any operating system.
- Wrote out the 13 data rules with their exact conditions in `notes/data_rules.md`, and added `tools/check_data.py`, which checks every rule, reports violations per rule and exits with status 1 if any rule fails.
- Added a Materials and Methods section to each of the six papers, as separate files in `papers/methods/`, with 15 numbered equations: indicator scoring and the soil health index (Paper 1); quadratic-plateau response, agronomic efficiency and recovery efficiency (Paper 2); partial and total land equivalent ratio (Paper 3); change in soil organic carbon and the factorial model (Paper 4); carbon stock and carbon retention (Paper 5); block-design model, least significant difference and combined-site model (Paper 6).
- Added `tables/` with the sites table, typeset directly from `data/sites.tsv` with pgfplotstable, and the indicator scoring table. File paths inside papers are written relative to `papers/` and wrapped in `\subfix`, so they resolve both in the volume and when a paper is typeset alone.
- A first version of the sites table overran the text block (Overfull \hbox, 46.1 pt too wide); the table was narrowed before commit. This defect is recorded as a candidate planted defect for M6.

### Pass/fail checks
| ID | Check | Threshold | Result |
|---|---|---|---|
| C3.1 | Full build of `main.tex` completes | 0 errors; biber and makeindex exit normally | PASS |
| C3.2 | Warnings and bad boxes in `main.log` | exactly 0 matches for `^!`, `Warning:`, `Overfull`, `Underfull` | PASS (0) |
| C3.3 | Compiled page count of the volume | exactly 28 | PASS (28) |
| C3.4 | Each paper typeset on its own | 6 of 6 with 0 issues; pages 3, 3, 2, 2, 3, 3 | PASS (6/6) |
| C3.5 | Data rules R1–R13 on the committed data | 13 of 13 PASS; 0 violations | PASS (0) |
| C3.6 | Rows per data file (4 blocks) | sites 3; T1 36; T2 60; T3 36; T4 48; T5 48; register 228 | PASS |
| C3.7 | Reproducibility: regenerating with the default seed gives identical files | SHA-256 prefixes identical on Linux and on Windows (MiKTeX machine): sites `350f855fd546`, register `668c940f92f4`, T1 `b93b68b5a067`, T2 `714beec3ce7b`, T3 `148ae9ca7fd3`, T4 `6c6e1eaa1c96`, T5 `b13bbf8d62cf` | PASS (7/7) |
| C3.8 | Generator robustness across seeds and block counts | 40 of 40 combinations (10 seeds × 3–6 blocks) pass all 13 rules | PASS (40/40) |
| C3.9 | Checker detects planted errors | a fertilised yield set below its control fails R7; a CR line ending and a short row fail R13 | PASS |
| C3.10 | Methods files in `papers/methods/`, each input once by its paper | exactly 6 | PASS (6) |
| C3.11 | Numbered equations in the methods | exactly 15, each with an `eq:` label | PASS (15) |
| C3.12 | Each methods section names its data file | 6 of 6 | PASS (6/6) |
| C3.13 | Sites table typeset from `data/sites.tsv` | 3 rows; values identical to the data file | PASS |
| C3.14 | Text files stored with LF line endings | 0 CRLF files | PASS (0) |


## M4 — Results

**Status:** Complete (committed in two parts)
**Snapshot:** `milestone_4_results/`
**Toolchain:** MiKTeX 26.5 (pdfTeX 4.27), biber 2.22, makeindex, Python 3.12 (standard library only)

### Work completed
- **Part 1.** Added `tools/compute_results.py`, which computes every reported result from the data and writes it to `results/`: eight summary files, four figure files and `values.tex` (148 values). It computes the soil health index with a block-design analysis of variance, the quadratic-plateau fit and agronomic optimum rate, agronomic and recovery efficiency of nitrogen, land equivalent ratios, the tillage × residue factorial analysis of variance, carbon retention, and the combined-site analysis of variance with the least significant difference. P values are computed with a standard-library implementation of the F distribution.
- Increased plot-to-plot variation in trials T2 and T4 to realistic levels (part 1), and corrected the nitrogen uptake model so that apparent recovery falls between 0.34 and 0.72 (part 2); an earlier model gave a mean recovery of 1.04, which is not physically plausible. Added data rule R14 (0 < mean apparent recovery ≤ 1 at every site and rate) so that the error cannot return.
- **Part 2.** Added a Results section to each paper in `papers/results/`. Every number in the text is quoted from `results/values.tex` with `\res{key}`; an undefined key prints **??** and raises a warning.
- Added seven result tables in `tables/`, each typeset from a `results/*.tsv` file with pgfplotstable, and five figures in `figures/`, drawn with pgfplots from the results files at compile time; the fitted response curves of Figure 2.1 take their coefficients from `values.tex`.
- Extended `soilproc.sty` with the result macros, common table and figure styles, and a float barrier so that each paper's tables and figures are placed before its references.

### Pass/fail checks
| ID | Check | Threshold | Result |
|---|---|---|---|
| C4.1 | Full build of `main.tex` completes | 0 errors; biber and makeindex exit normally | PASS |
| C4.2 | Warnings and bad boxes in `main.log`, including undefined result keys | exactly 0 matches for `^!`, `Warning:`, `Overfull`, `Underfull` | PASS (0) |
| C4.3 | Compiled page count of the volume | exactly 34 | PASS (34) |
| C4.4 | Each paper typeset on its own | 6 of 6 with 0 issues; pages 5, 4, 3, 4, 3, 3 | PASS (6/6) |
| C4.5 | Data rules R1–R14 | 14 of 14 PASS; 0 violations | PASS (0) |
| C4.6 | Generator robustness across seeds and block counts | 40 of 40 combinations pass all 14 rules | PASS (40/40) |
| C4.7 | Reproducibility of data and results | SHA-256 prefixes identical on Linux and Windows: T2 `6732d536f5da`, T4 `172c71a8f1ca`, `values.tex` `9b992b1ae447` (other data files unchanged from M3) | PASS |
| C4.8 | P values of the F distribution | match SciPy within 1 × 10⁻⁶ in 6 of 6 test cases | PASS (6/6) |
| C4.9 | Factorial analysis of variance | F ratios match an independent least-squares fit to 2 decimal places (site S2, grain yield) | PASS |
| C4.10 | Files in `results/` | exactly 13: 8 summary TSV, 4 figure TSV, `values.tex` with 148 values | PASS (13) |
| C4.11 | Numbers in the Results sections | all quoted by `\res` (100 uses); 0 occurrences of "??" in the PDF | PASS |
| C4.12 | Result tables typeset from `results/*.tsv` | exactly 7 | PASS (7) |
| C4.13 | Figures drawn by pgfplots from `results/` | exactly 5; 6 curve coefficients read with `\resnum` | PASS (5) |
| C4.14 | Each paper's tables and figures appear before its references | 6 of 6 | PASS (6/6) |
| C4.15 | Text files stored with LF line endings | 0 CRLF files | PASS (0) |


## M5 — Discussion, Abbreviations and Index

**Status:** Complete
**Snapshot:** `milestone_5_discussion/`
**Toolchain:** MiKTeX 26.5 (pdfTeX 4.27), biber 2.22, makeindex, Python 3.12

### Work completed
- Added a Discussion and a Conclusion to each paper, as separate files in `papers/discussion/`. Each discussion interprets its results against the literature already cited in the volume and states its limitations (for example, texture confounded with climate across the three sites of Paper 5); no new references were added. Each conclusion restates its key results through `\res`, so they remain traceable to the data.
- Corrected a draft claim that the semi-arid site was the warmest (the data show the humid tropical site is warmer; the text now says "driest"), and replaced the clay percentages typed in Paper 5 with values from `data/sites.tsv` (`\res{site-clay-…}`).
- Added the List of Abbreviations (`backmatter/abbreviations.tex`, 17 entries) and a subject index built with makeindex: 43 `\index` commands for 29 distinct entries, including sub-entries.
- Filtered the reminder that imakeidx always prints when loaded with `noautomatic` (the build sequence runs makeindex as its own step); the filter is documented in `main.tex`.
- Tested on Overleaf (pdfLaTeX, TeX Live 2026). The free plan stopped both the full volume and a single paper with a compile timeout before a PDF was produced, reporting 0 errors and 0 warnings up to that point. A full Overleaf compile is pending access to an account with a longer compile limit (check C5.13).

### Pass/fail checks
| ID | Check | Threshold | Result |
|---|---|---|---|
| C5.1 | Full build of `main.tex` completes | 0 errors; biber and makeindex exit normally | PASS |
| C5.2 | Warnings and bad boxes in `main.log` | exactly 0 matches for `^!`, `Warning:`, `Overfull`, `Underfull`; exactly 2 documented warning filters in `main.tex` | PASS (0) |
| C5.3 | Compiled page count of the volume | exactly 41 | PASS (41) |
| C5.4 | Each paper typeset on its own | 6 of 6 with 0 issues; pages 5, 5, 4, 5, 4, 4 | PASS (6/6) |
| C5.5 | Discussion files in `papers/discussion/`, each input once by its paper | exactly 6; each contains one Discussion and one Conclusion section | PASS (6) |
| C5.6 | Every conclusion quotes its key results from `values.tex` | 6 of 6 conclusions use `\res`; 119 `\res` uses in the papers in total | PASS |
| C5.7 | References | still exactly 18 cited keys, all defined in `bib/soilhealth.bib`; 0 new references | PASS (18) |
| C5.8 | List of Abbreviations | exactly 17 entries; each abbreviation appears in the text, tables or figures | PASS (17/17) |
| C5.9 | Subject index | 43 `\index` commands, 29 distinct entries; makeindex reports 0 warnings | PASS |
| C5.10 | Reproducibility of the computed values | `values.tex` SHA-256 prefix `d607777b1569` identical on Linux and Windows | PASS |
| C5.11 | Undefined result values | 0 occurrences of "??" in the PDF | PASS (0) |
| C5.12 | Text files stored with LF line endings | 0 CRLF files | PASS (0) |
| C5.13 | Full compile on Overleaf | PDF produced with 0 errors | OPEN — free-plan timeout; awaiting an account with a longer compile limit |


## M6 — Verification Layer

**Status:** Complete
**Snapshot:** `milestone_6_verification/` (the seeded start state)
**Toolchain:** MiKTeX 26.5 (pdfTeX 4.27), biber 2.22, makeindex, Python 3.12 (standard library only)

### Work completed
- Added `golden_solution/`, the correct finished project (70 files including its compiled `main.pdf`), with the decoys and the review log present and unchanged.
- Turned `project_source/` into the task's start state with six planted defects, each a different skill:

| ID | Defect | Where | Visible in | Weight |
|---|---|---|---|---|
| D1 | Sites table overruns the margin (Overfull \hbox, 46.1 pt too wide); all 9 columns must be kept | `tables/sites.tex` | compile log only | 2.0 |
| D2 | Citation key `pittelkow2016` does not exist in the bibliography | `papers/discussion/paper4_discussion.tex` | compile log, bold key in PDF | 2.0 |
| D3 | `\ref{tab:p3LER}` does not match the label `tab:p3ler` | `papers/results/paper3_results.tex` | "??" in PDF | 2.0 |
| D4 | Land equivalent ratio of S3 typed as 1.32; the computed value is 1.37 | `papers/discussion/paper3_discussion.tex` | comparison with Table 3.1 | 2.0 |
| D5 | `\index{Soil organic carbon}` splits the index entry in two | `papers/paper4_tillage.tex` | compiled index only | 1.5 |
| D6 | LER missing from the List of Abbreviations | `backmatter/abbreviations.tex` | back matter | 1.0 |

- Added two decoys, which must remain unchanged and unused: `data/archive/t2_nitrogen_2025_export.tsv` (an outdated export of trial T2 from a different seed, with an older column name) and `bib/soilhealth_draft.bib` (a superseded bibliography with ASCII-stripped names and the key `pittelkow2016`, which would appear to fix D2).
- Added `notes/review_log.md`: six editor's queries describing each symptom as a reader would see it, without prescribing the fix.
- Added `verifier/verify.py`, `verifier/build_expected.py` and `verifier/expected.json`. The verifier compiles a submission in a temporary copy and applies 7 gate checks (compiles with 0 errors; 64 frozen files match their SHA-256; no files added; each editable file keeps similarity ≥ 0.90 to the golden text and length ≤ 110 %; no warning suppression, extra bibliography or decoy path; page count 40–42; no warning other than the seeded ones) and 16 defect checks. Score = gate × (weights of fixed defects) / 10.5. File comparisons fold CRLF to LF, so line endings never decide a check.
- Added `verifier/run_oracle.py`, which scores 21 constructed submissions against their requirements, and `verifier/oracle_report.txt`.

### Pass/fail checks
| ID | Check | Threshold | Result |
|---|---|---|---|
| C6.1 | Golden solution builds | 0 errors, 0 warnings, 41 pages | PASS |
| C6.2 | Seeded start state shows each defect | Overfull 46.1 pt; undefined citation `pittelkow2016`; undefined reference `tab:p3LER`; 2 top-level index entries for soil organic carbon; 16 abbreviations | PASS (6/6) |
| C6.3 | `expected.json` reproducible | SHA-256 prefix `fac1755afcaf` identical when rebuilt on Linux (TeX Live 2023) and Windows (MiKTeX 26.5) | PASS |
| C6.4 | Null: untouched start state | score exactly 0 | PASS (0.0000) |
| C6.5 | Golden solution | score exactly 1 | PASS (1.0000) |
| C6.6 | Monotone: defects fixed in order D1–D5 | scores strictly increase: 0.1905, 0.3810, 0.5714, 0.7619, 0.9048 | PASS |
| C6.7 | Alternative valid fixes | 4 of 4 score exactly 1 (`\resizebox`, narrower `\tabcolsep`, smaller font, value typed as 1.37) | PASS (4/4) |
| C6.8 | Adversarial submissions | 10 of 10 score below 1; 7 of them exactly 0 (warning hidden with `\hfuzz`, `.bib` key renamed, label renamed, decoy edited, decoy named, instruction pasted, file added) | PASS (10/10) |
| C6.9 | Oracle on both systems | 21 of 21 cases meet their requirement on Linux and on Windows, with identical scores | PASS (21/21) |
| C6.10 | Data rules on golden and start state | 14 of 14 pass on both | PASS |
| C6.11 | Text files stored with LF line endings | 0 CRLF files | PASS (0) |


## M7 — Variants and Documentation

**Status:** Complete
**Snapshot:** the repository at this commit (variants under `variants/`)
**Toolchain:** MiKTeX 26.5 (pdfTeX 4.27), biber 2.22, makeindex, Python 3.12 (standard library only)

### Work completed
- Added `tools/check_claims.py`, which encodes the 25 qualitative statements of the text as tests on the computed results. It found one overstated sentence in Paper 2 ("recovery followed the same pattern"), now corrected to what the data support.
- Replaced 17 places where the text assumed four blocks with values from the data (`\res{design-blocks}`, `\res{p1-df-error}`, `\res{p4-df-error}`), and moved an index command that sat inside the word "blocks".
- Defined the six defects once in `verifier/defects.py`; the seeded value of D4 is derived from the data (computed value − 0.05). The verifier, expected-values builder and oracle now accept a variant's paths. Because the wording changes altered file fingerprints, `verifier/expected.json` was rebuilt: SHA-256 prefix `f9268cdb9f60` (M6: `fac1755afcaf`).
- Added `tools/make_variant.py` and built two complete variants, each accepted only if its data obey all 14 rules and all 25 claims, its golden solution compiles with 0 warnings, its start state scores 0, its golden solution scores 1 and its oracle passes all 21 cases.
- Added `README.md`, `ASSET.md` (with a complete room-to-vary table and a direct link to the data rules), `task_brief.md`, `verifiers_spec.md`, `reference_results.md`, `SOURCES.md`, `TASK_CATALOGUE.md` (30 tasks in three registers), `requirements.pdf` (from `docs/requirements.tex`), and `tools/make_manifest.py` with `MANIFEST.sha256`.

### Pass/fail checks
| ID | Check | Threshold | Result |
|---|---|---|---|
| C7.1 | Text claims on the main data | 25 of 25 hold | PASS (25/25) |
| C7.2 | Main asset after the wording changes | golden 0 issues, 41 pages; start state score 0.0000; golden score 1.0000; oracle 21 of 21 | PASS |
| C7.3 | `verifier/expected.json` reproducible | SHA-256 prefix `f9268cdb9f60` identical on Linux and Windows | PASS |
| C7.4 | Variant B (seed 118, 5 blocks, 285 plots) | 14 of 14 rules; 25 of 25 claims; golden 0 issues, 41 pages; start state 0, golden 1; oracle 21 of 21 | PASS |
| C7.5 | Variant C (US letter, 12 pt, one-sided) | golden 0 issues, 37 pages; D1 still overflows; start state 0, golden 1; oracle 21 of 21 | PASS |
| C7.6 | Variants reproducible | `expected.json` prefixes identical on Linux and Windows: B `0528a7b89047`, C `b514d8fd90d5` | PASS (2/2) |
| C7.7 | D4 follows the data | variant B: computed 1.34, seeded 1.29; main and variant C: computed 1.37, seeded 1.32 | PASS |
| C7.8 | Seed acceptance is selective | of 400 seeds tried with 5 blocks, the first to satisfy all rules and claims is 118 | PASS |
| C7.9 | Required documents present | `requirements.pdf`, `task_brief.md`, `verifiers_spec.md`, `reference_results.md`, `ASSET.md`, `README.md`, `SOURCES.md`, `TASK_CATALOGUE.md` | PASS (8/8) |
| C7.10 | `requirements.pdf` builds | 0 errors, 0 warnings, 0 overfull boxes; 2 pages | PASS |
| C7.11 | `SOURCES.md` covers the bibliography | 18 of 18 entries, each with its verification record and the papers that cite it | PASS (18/18) |
| C7.12 | Manifest | `python tools/make_manifest.py --check`: every file matches, 0 unlisted | PASS |
| C7.13 | Text files stored with LF line endings | 0 CRLF files | PASS (0) |
