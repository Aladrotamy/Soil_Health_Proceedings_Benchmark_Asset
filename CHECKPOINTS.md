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
