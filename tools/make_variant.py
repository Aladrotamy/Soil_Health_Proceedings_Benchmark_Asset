#!/usr/bin/env python3
"""Build a complete variant of the asset under variants/<name>/.

A variant is a full second task: its own golden solution, its own seeded start
state with the six defects, its own verifier expectations and its own oracle
run. Two axes can be varied:

  data    --seed N --blocks B   regenerate every data file, recompute every
                                result; tables, figures and quoted values in
                                the text follow automatically
  layout  --layout NAME         change paper size, font size and sides

    python tools/make_variant.py --name variant_B --seed 118 --blocks 5
    python tools/make_variant.py --name variant_C --layout letter12

A data variant is accepted only if all 14 data rules (tools/check_data.py)
and all qualitative claims of the text (tools/check_claims.py) hold for the
new data. Every variant is accepted only if its golden solution compiles with
0 warnings, its start state scores 0, its golden solution scores 1 and the
oracle passes every case. Writes variants/<name>/VARIANT.md.
"""
import argparse
import os
import re
import shutil
import subprocess
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "verifier"))
from defects import defects  # noqa: E402
from verify import build, verify  # noqa: E402

LAYOUTS = {
    # name: (document class options, geometry options)
    "a4-11pt": ("11pt,a4paper,twoside,openright",
                "a4paper,inner=28mm,outer=24mm,top=28mm,bottom=30mm,headsep=8mm"),
    "letter12": ("12pt,letterpaper,oneside,openany",
                 "letterpaper,left=25mm,right=25mm,top=25mm,bottom=28mm,headsep=8mm,headheight=15pt"),
}


def run(cmd):
    r = subprocess.run([sys.executable] + cmd, cwd=ROOT, capture_output=True, text=True)
    if r.returncode:
        sys.exit(f"failed: {' '.join(cmd)}\n{r.stdout}\n{r.stderr}")
    return r.stdout


def sub(path, old, new):
    s = open(path, encoding="utf-8").read()
    if old not in s:
        sys.exit(f"text not found in {path}: {old!r}")
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(s.replace(old, new, 1))


def main():
    ap = argparse.ArgumentParser(description="Build a variant of the asset.")
    ap.add_argument("--name", required=True)
    ap.add_argument("--seed", type=int)
    ap.add_argument("--blocks", type=int)
    ap.add_argument("--layout", default="a4-11pt", choices=sorted(LAYOUTS))
    a = ap.parse_args()
    out = os.path.join(ROOT, "variants", a.name)
    gold = os.path.join(out, "golden_solution")
    seed = os.path.join(out, "project_source")
    shutil.rmtree(out, ignore_errors=True)
    shutil.copytree(os.path.join(ROOT, "golden_solution"), gold,
                    ignore=shutil.ignore_patterns("*.pdf", "*.aux", "*.log", "*.bbl", "*.bcf", "*.blg",
                                                  "*.idx", "*.ind", "*.ilg", "*.out", "*.toc", "*.run.xml"))
    log = []

    # ------------------------------------------------------------ data axis
    if a.seed is not None or a.blocks is not None:
        sd, bl = a.seed if a.seed is not None else 20261001, a.blocks or 4
        run(["tools/make_trials.py", "--seed", str(sd), "--blocks", str(bl), "--out", os.path.join(gold, "data")])
        log.append(run(["tools/check_data.py", os.path.join(gold, "data")]).strip().splitlines()[-1])
        run(["tools/compute_results.py", "--data", os.path.join(gold, "data"), "--out", os.path.join(gold, "results")])
        log.append(run(["tools/check_claims.py", os.path.join(gold, "results")]).strip().splitlines()[-1])

    # ------------------------------------------------------------ layout axis
    if a.layout != "a4-11pt":
        cls, geo = LAYOUTS[a.layout]
        sub(os.path.join(gold, "main.tex"), "[" + LAYOUTS["a4-11pt"][0] + "]{book}", f"[{cls}]{{book}}")
        sub(os.path.join(gold, "soilproc.sty"), "[" + LAYOUTS["a4-11pt"][1] + "]{geometry}", f"[{geo}]{{geometry}}")
        if "oneside" in cls:
            # one-sided pages have no even/odd distinction in the running heads
            sub(os.path.join(gold, "soilproc.sty"), "\\fancyhead[LE]{", "\\fancyhead[L]{")
            sub(os.path.join(gold, "soilproc.sty"), "\\fancyhead[RO]{", "\\fancyhead[R]{")

    # ------------------------------------------------------------ golden must be clean
    ok, blog, _, pages = build(gold)
    issues = len(re.findall(r"^!|Warning:|Overfull|Underfull", blog, re.M))
    if not ok or issues:
        sys.exit(f"golden solution of {a.name} does not compile cleanly ({issues} issues)")
    log.append(f"golden solution: 0 issues, {pages} pages")

    # ------------------------------------------------------------ start state = golden + six defects
    shutil.copytree(gold, seed)
    vals = dict(re.findall(r"\\resdef\{([^}]*)\}\{(.*)\}", open(os.path.join(gold, "results", "values.tex"), encoding="utf-8").read()))
    for d, (f, good, bad) in defects(vals).items():
        sub(os.path.join(seed, f), good, bad)
    exp_path = os.path.join(out, "verifier", "expected.json")
    log.append(run(["verifier/build_expected.py", "--golden", gold, "--out", exp_path]).strip())
    import json
    exp = json.load(open(exp_path, encoding="utf-8"))
    s0, s1 = verify(seed, exp)["score"], verify(gold, exp)["score"]
    if s0 != 0 or s1 != 1:
        sys.exit(f"{a.name}: start state scores {s0}, golden scores {s1}")
    log.append(f"start state scores {s0:.4f}; golden solution scores {s1:.4f}")
    r = subprocess.run([sys.executable, "verifier/run_oracle.py", "--root", out], cwd=ROOT,
                       capture_output=True, text=True)
    log.append(r.stdout.strip().splitlines()[-1])
    if r.returncode:
        sys.exit(f"{a.name}: oracle failed\n{r.stdout}")

    with open(os.path.join(out, "VARIANT.md"), "w", encoding="utf-8", newline="\n") as f:
        f.write(f"# {a.name}\n\nBuilt by `tools/make_variant.py` with:\n\n")
        f.write(f"- data: seed {a.seed if a.seed is not None else 'unchanged (20261001)'}, "
                f"blocks {a.blocks if a.blocks else 'unchanged (4)'}\n")
        f.write(f"- layout: {a.layout} (document class options `{LAYOUTS[a.layout][0]}`)\n")
        f.write(f"- computed land equivalent ratio of S3 (defect D4): {exp['values']['p3-ler-S3']}; "
                f"seeded wrong value {exp['values']['p3-ler-S3-wrong']}\n\n## Acceptance\n\n")
        f.write("\n".join(f"- {line}" for line in log) + "\n")
    print("\n".join(log))


if __name__ == "__main__":
    main()
