# Asset Metadata

## Owner
Rotimi Alade

## What this is
An Overleaf/LaTeX benchmark asset built around a multi-paper conference
proceedings volume on soil health and sustainable crop production. An agent
receives the volume with six planted defects (`project_source/`), reads the
editor's queries in `notes/review_log.md`, and must return the volume to the
state of `golden_solution/` working only in the editor. `verifier/verify.py`
compiles the result and scores it.

## Milestones
1. Volume foundation
2. References and paper framework
3. Data layer and methods
4. Results
5. Discussion, abbreviations and index
6. Verification layer
7. Variants and documentation

Each milestone's pass/fail checks, with explicit thresholds, are in `CHECKPOINTS.md`.

## Planted defects

| ID | Defect | File | Visible in | Weight |
|---|---|---|---|---|
| D1 | Sites table overruns the margin (Overfull \hbox, 46.1 pt); all 9 columns must stay | `tables/sites.tex` | compile log only | 2.0 |
| D2 | Citation key `pittelkow2016` not in the bibliography | `papers/discussion/paper4_discussion.tex` | compile log; bold key in PDF | 2.0 |
| D3 | `\ref{tab:p3LER}` does not match the label `tab:p3ler` | `papers/results/paper3_results.tex` | "??" in PDF | 2.0 |
| D4 | Land equivalent ratio of S3 typed as 1.32; computed value 1.37 | `papers/discussion/paper3_discussion.tex` | comparison with Table 3.1 | 2.0 |
| D5 | `\index{Soil organic carbon}` splits the index entry | `papers/paper4_tillage.tex` | compiled index only | 1.5 |
| D6 | LER missing from the List of Abbreviations | `backmatter/abbreviations.tex` | back matter | 1.0 |

Weights follow difficulty: 1.0 base, +1.0 when the correct value must be
derived from another file, +0.5 when the defect shows only after compiling,
+0.5 when two files must agree. All six defects are defined once in
`verifier/defects.py`.

## Decoys
- `data/archive/t2_nitrogen_2025_export.tsv` — an outdated export of trial T2 from a different seed, with an older column name. Not read by the volume.
- `bib/soilhealth_draft.bib` — a superseded bibliography with ASCII-stripped author names and the key `pittelkow2016`, which would appear to fix D2. Not loaded by the volume.

Both must remain unchanged and unused; the verifier gives 0 if either is edited, named in an edited file, or loaded.

## Data rules
The 14 rules the data must obey are written out with their exact conditions in
[`project_source/notes/data_rules.md`](project_source/notes/data_rules.md) and
checked by `tools/check_data.py`. Examples: R7, every fertilised plot yields at
least as much as the unfertilised plot of its block; R10, every block's land
equivalent ratio lies between 0.80 and 1.60; R12, carbon retention rises with
clay content across sites; R14, mean apparent nitrogen recovery lies in (0, 1].

## Text claims
The 25 qualitative statements made in the text (for example, "the tillage ×
residue interaction on soil carbon was significant at S1 and S3 but not at S2")
are encoded as tests in `tools/check_claims.py`. A data variant is accepted only
if all 25 hold.

## Room to vary

| Axis | How to vary | Demonstrated by | What changes for the agent |
|---|---|---|---|
| Dataset (values and size) | `tools/make_variant.py --seed N --blocks B` | `variants/variant_B/` (seed 118, 5 blocks, 285 plots) | every table, figure and quoted value; the correct value for D4 (1.34 in variant B, seeded as 1.29) |
| Page layout | `tools/make_variant.py --layout NAME` (`a4-11pt`, `letter12`) | `variants/variant_C/` (US letter, 12 pt, one-sided, 37 pages) | page breaks, float positions and the overflow that D1 must fix |
| Which defects are planted | edit the list in `verifier/defects.py`; weights in `verifier/build_expected.py` | 21 oracle cases, including every prefix of D1–D6 | the subset of queries in the review log and the maximum score |
| Defect position and wording | change a defect's golden and seeded text in `verifier/defects.py` | the oracle's alternative-fix cases | the file and line the agent must find |
| Task register | rewrite `task_brief.md` or the review log in another voice; the verifier is unchanged | `TASK_CATALOGUE.md` (explicit, implicit and natural registers) | how much the agent must infer |
| Scope of the task | single paper typeset alone (`papers/paperN_*.tex`) or the whole volume | standalone builds checked in C2.7–C5.4 | size of the context the agent must hold |

A seed is accepted only if all 14 data rules and all 25 claims hold; of 400
seeds tried with five blocks, seed 118 was the first to qualify, so the text's
claims are specific rather than vague.

## Overleaf note
On Overleaf's free plan, the full volume and a single paper both stop with a
compile timeout before a PDF is produced (0 errors reported). The volume
compiles with 0 warnings under MiKTeX 26.5 and TeX Live 2023.
