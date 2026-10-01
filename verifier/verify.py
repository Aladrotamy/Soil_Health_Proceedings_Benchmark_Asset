#!/usr/bin/env python3
"""Verifier of the Soil Health Proceedings benchmark asset.

Compiles a submitted project (pdfLaTeX, biber, makeindex, pdfLaTeX x2) in a
temporary copy and scores it against verifier/expected.json, which is built
from golden_solution/ by verifier/build_expected.py.

    python verifier/verify.py project_source            # report
    python verifier/verify.py project_source --json     # machine-readable
    python verifier/verify.py variants/variant_B/project_source \
        --expected variants/variant_B/verifier/expected.json

Score = gate x (sum of weights of fixed defects) / (sum of all weights).
The gate is 0 if the project fails to compile or any integrity check fails,
and 1 otherwise. Each defect is all-or-nothing: every one of its checks must
pass. Requires pdflatex, biber and makeindex on the PATH; standard library only.
"""
import argparse
import difflib
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
BUILD_EXT = (".aux", ".log", ".out", ".toc", ".lof", ".lot", ".bbl", ".blg", ".bcf",
             ".run.xml", ".idx", ".ind", ".ilg", ".synctex.gz", ".fls", ".fdb_latexmk", ".pdf")
# Tokens that would hide a defect instead of fixing it, or pull in a decoy.
FORBIDDEN = [r"\hfuzz", r"\vfuzz", r"\hbadness", r"\vbadness", r"\WarningFilter",
             r"\nocite", r"\addbibresource", r"\makeatletter", "soilhealth_draft", "data/archive"]
# Warnings present in the seeded project; any other warning breaks the gate.
SEED_WARNINGS = [r"Citation 'pittelkow2016'", r"Reference `tab:p3LER'",
                 r"There were undefined references", r"biblatex Warning: The following entry could not be found",
                 r"Overfull \\hbox"]
SITE_COLUMNS = ["site", "zone", "clay_pct", "sand_pct", "ph_initial", "soc_initial_gkg",
                "bulk_density_gcm3", "rainfall_mm", "temperature_c"]


def norm_bytes(path):
    """File bytes with CRLF folded to LF, so line endings never decide a check."""
    return open(path, "rb").read().replace(b"\r\n", b"\n")


def text(root, rel):
    p = os.path.join(root, rel)
    return norm_bytes(p).decode("utf-8") if os.path.exists(p) else ""


def strict(s):
    """Lower-case and collapse whitespace (tolerates reflowed lines)."""
    return re.sub(r"\s+", " ", s).strip().lower()


def source_files(root):
    out = []
    for d, _, fs in os.walk(root):
        for f in fs:
            rel = os.path.relpath(os.path.join(d, f), root).replace(os.sep, "/")
            if not rel.endswith(BUILD_EXT):
                out.append(rel)
    return sorted(out)


def build(root):
    """Compile a temporary copy; return (ok, log text, index text, pages)."""
    tmp = tempfile.mkdtemp(prefix="shp_verify_")
    work = os.path.join(tmp, "p")
    shutil.copytree(root, work, ignore=shutil.ignore_patterns(*["*" + e for e in BUILD_EXT]))
    steps = [["pdflatex", "-interaction=nonstopmode", "main"], ["biber", "main"],
             ["makeindex", "main"], ["pdflatex", "-interaction=nonstopmode", "main"],
             ["pdflatex", "-interaction=nonstopmode", "main"]]
    for cmd in steps:
        try:
            subprocess.run(cmd, cwd=work, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=300)
        except (OSError, subprocess.TimeoutExpired):
            pass
    log = open(os.path.join(work, "main.log"), encoding="latin-1").read() if os.path.exists(os.path.join(work, "main.log")) else ""
    ind = open(os.path.join(work, "main.ind"), encoding="utf-8", errors="replace").read() if os.path.exists(os.path.join(work, "main.ind")) else ""
    m = re.search(r"Output written on main\.pdf \((\d+) page", log)
    pages = int(m.group(1)) if m else 0
    ok = os.path.exists(os.path.join(work, "main.pdf")) and not re.search(r"^!", log, re.M)
    shutil.rmtree(tmp, ignore_errors=True)
    return ok, log, ind, pages


def check(name, ok, detail=""):
    return {"check": name, "pass": bool(ok), "detail": detail}


def verify(root, exp):
    res = {"gate": [], "defects": {}}
    ok, log, ind, pages = build(root)
    res["gate"].append(check("G1 project compiles to a PDF with 0 errors", ok, f"{pages} pages"))

    # ------------------------------------------------------------ integrity (gate)
    files = source_files(root)
    frozen, editable = exp["frozen"], exp["editable"]
    bad = [f for f, h in frozen.items()
           if f not in files or hashlib.sha256(norm_bytes(os.path.join(root, f))).hexdigest() != h]
    res["gate"].append(check("G2 every file outside the six editable files is unchanged (SHA-256)", not bad,
                             ", ".join(bad[:5])))
    extra = [f for f in files if f not in frozen and f not in editable and f != "main.pdf"]
    res["gate"].append(check("G3 no files added", not extra, ", ".join(extra[:5])))
    sim_bad, forb = [], []
    for f, g in editable.items():
        t = text(root, f)
        ratio = difflib.SequenceMatcher(None, g["content"], t).ratio()
        if ratio < 0.90 or len(t) > 1.10 * len(g["content"]):
            sim_bad.append(f"{f} (similarity {ratio:.3f}, {len(t)} chars)")
        for tok in FORBIDDEN:
            if tok in t:
                forb.append(f"{f}: {tok}")
    res["gate"].append(check("G4 editable files stay within 10% of the golden text (similarity >= 0.90, length <= 110%)",
                             not sim_bad, "; ".join(sim_bad)))
    res["gate"].append(check("G5 no warning suppression, decoy file or extra bibliography in editable files",
                             not forb, "; ".join(forb)))
    lo, hi = exp["pages"] - 1, exp["pages"] + 1
    res["gate"].append(check(f"G6 page count within {lo}-{hi}", lo <= pages <= hi, str(pages)))
    warns = [l for l in log.splitlines() if re.search(r"Warning:|Overfull|Underfull", l)]
    new = [w for w in warns if not any(re.search(p, w) for p in SEED_WARNINGS)]
    res["gate"].append(check("G7 no warning other than those of the seeded defects", not new, "; ".join(new[:3])))

    # ------------------------------------------------------------ defects
    W = exp["weights"]
    d = {}
    sites = text(root, "tables/sites.tex")
    cols = re.search(r"columns=\{([^}]*)\}", sites)
    collist = [c.strip() for c in cols.group(1).split(",")] if cols else []
    d["D1"] = [check("no Overfull box in the log", "Overfull" not in log),
               check("all 9 site columns still typeset", collist == SITE_COLUMNS, ",".join(collist)),
               check("table still read from data/sites.tsv", "{\\subfix{../data/sites.tsv}}" in sites)]
    p4 = text(root, "papers/discussion/paper4_discussion.tex")
    allsrc = " ".join(text(root, f) for f in files if f.endswith(".tex"))
    d["D2"] = [check("no undefined citation in the log", not re.search(r"Citation .* undefined", log)),
               check("discussion cites pittelkow2015 at the same place",
                     "residue retention \\parencite{pittelkow2015}" in strict(p4)),
               check("key pittelkow2016 cited nowhere", "pittelkow2016" not in allsrc)]
    p3r = text(root, "papers/results/paper3_results.tex")
    d["D3"] = [check("no undefined reference in the log", not re.search(r"Reference .* undefined", log)),
               check("results refer to Table~\\ref{tab:p3ler}", "(table~\\ref{tab:p3ler})" in strict(p3r)
                     and "tab:p3LER" not in p3r)]
    p3d = text(root, "papers/discussion/paper3_discussion.tex")
    concl = p3d.split("\\section{Conclusion}")[-1]
    m = re.search(r"\\res\{p3-ler-S2\}\s+and\s+(\\res\{p3-ler-S3\}|[0-9]+\.[0-9]+)\s*\.", concl)
    val = m.group(1) if m else ""
    target = float(exp["values"]["p3-ler-S3"])
    okv = val == "\\res{p3-ler-S3}" or (val[:1].isdigit() and abs(float(val) - target) <= 0.005)
    wrong = exp["values"]["p3-ler-S3-wrong"]
    d["D4"] = [check(f"S3 ratio in the conclusion equals the computed value {target:.2f} (tolerance 0.005)", okv, val),
               check(f"the wrong value {wrong} is gone from the conclusion", wrong not in concl)]
    items = [l for l in ind.splitlines() if re.match(r"\s*\\item\s", l)]
    soc = [l for l in items if re.match(r"\s*\\item\s+soil organic carbon,", l, re.I)]
    d["D5"] = [check("exactly one top-level index entry for soil organic carbon", len(soc) == 1, str(len(soc))),
               check("no capitalised \\index{Soil organic carbon} in the sources", "\\index{Soil organic carbon}" not in allsrc),
               check(f"\\index{{soil organic carbon}} used exactly {exp['soc_index_count']} times",
                     allsrc.count("\\index{soil organic carbon}") == exp["soc_index_count"],
                     str(allsrc.count("\\index{soil organic carbon}")))]
    ab = text(root, "backmatter/abbreviations.tex")
    rows = re.findall(r"^\s*(\S[^&\n]*?)\s*&\s*([^\\\n]+?)\s*\\\\", ab, re.M)
    rows = [(a.strip(), b.strip()) for a, b in rows if a.strip() != "Abbreviation"]
    keys = [a for a, _ in rows]
    d["D6"] = [check("LER listed as land equivalent ratio", ("LER", "land equivalent ratio") in rows),
               check(f"exactly {exp['abbreviations']} abbreviations", len(rows) == exp["abbreviations"], str(len(rows))),
               check("list in alphabetical order", keys == sorted(keys, key=str.lower))]
    res["defects"] = {k: {"weight": W[k], "checks": v, "fixed": all(c["pass"] for c in v)} for k, v in d.items()}
    gate = all(c["pass"] for c in res["gate"])
    total = sum(W.values())
    got = sum(W[k] for k, v in res["defects"].items() if v["fixed"])
    res["gate_pass"] = gate
    res["score"] = round(got / total, 4) if gate else 0.0
    return res


def main():
    ap = argparse.ArgumentParser(description="Score a project against the golden solution.")
    ap.add_argument("project", nargs="?", default="project_source")
    ap.add_argument("--expected", default=os.path.join(HERE, "expected.json"))
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    exp = json.load(open(a.expected, encoding="utf-8"))
    r = verify(a.project, exp)
    if a.json:
        print(json.dumps(r, indent=1))
        return
    print(f"Verifying {a.project}")
    for c in r["gate"]:
        print(f"  [{'PASS' if c['pass'] else 'FAIL'}] {c['check']}" + (f"  ({c['detail']})" if c["detail"] and not c["pass"] else ""))
    for k, v in r["defects"].items():
        print(f"  {k} weight {v['weight']}: {'FIXED' if v['fixed'] else 'NOT FIXED'}")
        for c in v["checks"]:
            print(f"      [{'PASS' if c['pass'] else 'FAIL'}] {c['check']}" + (f"  ({c['detail']})" if c["detail"] else ""))
    print(f"SCORE: {r['score']:.4f}  (gate {'passed' if r['gate_pass'] else 'FAILED'})")


if __name__ == "__main__":
    main()
