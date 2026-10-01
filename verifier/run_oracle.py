#!/usr/bin/env python3
"""Oracle: prove that the verifier scores the right things.

Builds many submissions from project_source/ (the seeded start state) and
golden_solution/, scores each with verifier/verify.py and compares the score
with its required outcome:

  1. null         the untouched start state scores exactly 0
  2. golden       the golden solution scores exactly 1
  3. monotone     fixing the defects one at a time never lowers the score
  4. alternatives other valid fixes also score exactly 1
  5. adversarial  wrong or shortcut submissions score below 1 (most score 0)

    python verifier/run_oracle.py          # writes verifier/oracle_report.txt

Exits with status 1 if any outcome differs from its requirement.
"""
import json
import os
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
sys.path.insert(0, HERE)
from verify import verify  # noqa: E402

SEED = os.path.join(ROOT, "project_source")
GOLD = os.path.join(ROOT, "golden_solution")
DEFECT_FILES = {"D1": "tables/sites.tex", "D2": "papers/discussion/paper4_discussion.tex",
                "D3": "papers/results/paper3_results.tex", "D4": "papers/discussion/paper3_discussion.tex",
                "D5": "papers/paper4_tillage.tex", "D6": "backmatter/abbreviations.tex"}


def state(fixed, edits=None):
    """Copy of the seed with the golden version of the given defect files,
    then the given text edits {file: (old, new)} applied."""
    tmp = tempfile.mkdtemp(prefix="shp_oracle_")
    work = os.path.join(tmp, "p")
    shutil.copytree(SEED, work)
    for d in fixed:
        shutil.copy(os.path.join(GOLD, DEFECT_FILES[d]), os.path.join(work, DEFECT_FILES[d]))
    for f, (old, new) in (edits or {}).items():
        p = os.path.join(work, f)
        s = open(p, encoding="utf-8").read() if os.path.exists(p) else ""
        if old is None:
            s = s + new
        else:
            assert old in s, (f, old)
            s = s.replace(old, new, 1)
        with open(p, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(s)
    return tmp, work


ALL = ["D1", "D2", "D3", "D4", "D5", "D6"]
GOLD_SITES = "  \\centering\\footnotesize\n  \\setlength{\\tabcolsep}{4pt}\n"
SEED_SITES = "  \\centering\\small\n"
CASES = [
    # name, fixed defects, edits, requirement
    ("null: untouched start state", [], None, "== 0"),
    ("golden: golden solution files", ALL, None, "== 1"),
    ("prefix 1: D1", ["D1"], None, "monotone"),
    ("prefix 2: D1-D2", ALL[:2], None, "monotone"),
    ("prefix 3: D1-D3", ALL[:3], None, "monotone"),
    ("prefix 4: D1-D4", ALL[:4], None, "monotone"),
    ("prefix 5: D1-D5", ALL[:5], None, "monotone"),
    ("alt D1: \\resizebox to the text width", ALL[1:], {"tables/sites.tex": (
        "  \\pgfplotstabletypeset[", "  \\resizebox{\\linewidth}{!}{\\pgfplotstabletypeset[")}, "== 1*"),
    ("alt D1: narrower column separation only", ALL[1:], {"tables/sites.tex": (
        SEED_SITES, "  \\centering\\small\n  \\setlength{\\tabcolsep}{2pt}\n")}, "== 1"),
    ("alt D1: smaller font only", ALL[1:], {"tables/sites.tex": (
        SEED_SITES, "  \\centering\\scriptsize\n")}, "== 1"),
    ("alt D4: correct value typed as 1.37", ["D1", "D2", "D3", "D5", "D6"], {
        "papers/discussion/paper3_discussion.tex": ("1.32. Maize", "1.37. Maize")}, "== 1"),
    ("adv drop_last: every fix except D6", ALL[:5], None, "< 1"),
    ("adv drop_columns: table fitted by deleting columns", ALL[1:], {"tables/sites.tex": (
        "columns={site,zone,clay_pct,sand_pct,ph_initial,", "columns={site,zone,clay_pct,ph_initial,")}, "< 1"),
    ("adv hide_overflow: \\hfuzz instead of a fix", ALL[1:], {"tables/sites.tex": (
        SEED_SITES, "  \\centering\\small\\hfuzz=60pt\n")}, "== 0"),
    ("adv bib_edit: rename the .bib key to pittelkow2016", ["D1", "D3", "D4", "D5", "D6"], {
        "bib/soilhealth.bib": ("@article{pittelkow2015,", "@article{pittelkow2016,")}, "== 0"),
    ("adv label_edit: rename the table label to tab:p3LER", ["D1", "D2", "D4", "D5", "D6"], {
        "tables/p3_ler.tex": ("\\label{tab:p3ler}", "\\label{tab:p3LER}")}, "== 0"),
    ("adv decoy_edit: change the archived export", ALL, {
        "data/archive/t2_nitrogen_2025_export.tsv": (None, "T2-S9-B9-P99\tS9\t9\t0\t0.00\t0.0\n")}, "== 0"),
    ("adv decoy_cite: wrong value 1.32 kept, draft bibliography named", ["D1", "D2", "D3", "D5", "D6"], {
        "papers/discussion/paper3_discussion.tex": ("1.32. Maize", "1.32 (see bib/soilhealth_draft.bib). Maize")}, "== 0"),
    ("adv index_delete: delete the capitalised index entry", ["D1", "D2", "D3", "D4", "D6"], {
        "papers/paper4_tillage.tex": ("\\index{Soil organic carbon}", "")}, "< 1"),
    ("adv paste_instruction: queries pasted after \\end{document}", ALL, {
        "main.tex": (None, "\nQ1 table of sites runs past the margin. Q4 land equivalent ratio 1.37.\n")}, "== 0"),
    ("adv add_file: fixes placed in a new file", ALL, {
        "papers/fixes.tex": (None, "% fixes\n")}, "== 0"),
]


def main():
    rows, fails, prev = [], 0, -1.0
    for name, fixed, edits, req in CASES:
        tmp, work = state(fixed, edits)
        if name.startswith("alt D1: \\resizebox"):
            # close the \resizebox brace after the table data
            p = os.path.join(work, "tables/sites.tex")
            s = open(p, encoding="utf-8").read().replace("{\\subfix{../data/sites.tsv}}", "{\\subfix{../data/sites.tsv}}}", 1)
            open(p, "w", encoding="utf-8", newline="\n").write(s)
            req = "== 1"
        r = verify(work, json.load(open(os.path.join(HERE, "expected.json"), encoding="utf-8")))
        shutil.rmtree(tmp, ignore_errors=True)
        sc = r["score"]
        if req == "== 0":
            ok = sc == 0
        elif req == "== 1":
            ok = sc == 1
        elif req == "< 1":
            ok = sc < 1
        else:
            ok = sc >= prev and 0 < sc < 1
        if name.startswith(("null", "prefix", "golden")):
            prev = sc if name.startswith(("null", "prefix")) else prev
        fails += not ok
        fixed_d = "".join(k[1] for k, v in r["defects"].items() if v["fixed"]) or "-"
        rows.append(f"{'PASS' if ok else 'FAIL'}  {sc:6.4f}  req {req:<8}  gate {'ok  ' if r['gate_pass'] else 'FAIL'}  fixed {fixed_d:<6}  {name}")
        print(rows[-1], flush=True)
    rows.append(f"{len(CASES) - fails} of {len(CASES)} oracle cases meet their requirement")
    print(rows[-1])
    with open(os.path.join(HERE, "oracle_report.txt"), "w", encoding="utf-8", newline="\n") as f:
        f.write("Oracle report -- python verifier/run_oracle.py\n")
        f.write("columns: result, score, requirement, gate, defects fixed, case\n\n")
        f.write("\n".join(rows) + "\n")
    sys.exit(1 if fails else 0)


if __name__ == "__main__":
    main()
