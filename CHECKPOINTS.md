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
