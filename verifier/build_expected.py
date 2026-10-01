#!/usr/bin/env python3
"""Build verifier/expected.json from golden_solution/.

    python verifier/build_expected.py
    python verifier/build_expected.py --golden variants/variant_B/golden_solution \
        --out variants/variant_B/verifier/expected.json

Records the SHA-256 of every file that must stay unchanged, the golden text
of the six editable files, the golden page count, the defect weights and the
reference values the defect checks compare against.
"""
import hashlib
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from verify import build, norm_bytes, source_files  # noqa: E402

from defects import wrong_ler  # noqa: E402
EDITABLE = ["tables/sites.tex", "papers/discussion/paper4_discussion.tex",
            "papers/results/paper3_results.tex", "papers/discussion/paper3_discussion.tex",
            "papers/paper4_tillage.tex", "backmatter/abbreviations.tex"]
# Weight = difficulty: 1.0 base, +1.0 value derived from another file,
# +0.5 defect visible only after compiling, +0.5 two files must agree.
WEIGHTS = {"D1": 2.0,   # overflow: compile-only (+0.5), two constraints to keep (+0.5)
           "D2": 2.0,   # citation key: compile-only (+0.5), checked against the .bib (+0.5)
           "D3": 2.0,   # cross-reference: compile-only (+0.5), checked against the table file (+0.5)
           "D4": 2.0,   # wrong value: derived from the results (+1.0)
           "D5": 1.5,   # index: compile-only (+0.5)
           "D6": 1.0}   # abbreviation: direct edit


def main():
    import argparse
    ap = argparse.ArgumentParser(description="Build expected.json from a golden solution.")
    ap.add_argument("--golden", default=os.path.join(HERE, "..", "golden_solution"))
    ap.add_argument("--out", default=os.path.join(HERE, "expected.json"))
    a = ap.parse_args()
    GOLDEN = a.golden
    files = source_files(GOLDEN)
    ok, log, ind, pages = build(GOLDEN)
    if not ok:
        sys.exit("golden solution does not compile")
    vals = dict(re.findall(r"\\resdef\{([^}]*)\}\{([^}]*)\}",
                           norm_bytes(os.path.join(GOLDEN, "results", "values.tex")).decode()))
    allsrc = " ".join(norm_bytes(os.path.join(GOLDEN, f)).decode() for f in files if f.endswith(".tex"))
    ab = norm_bytes(os.path.join(GOLDEN, "backmatter", "abbreviations.tex")).decode()
    exp = {
        "frozen": {f: hashlib.sha256(norm_bytes(os.path.join(GOLDEN, f))).hexdigest()
                   for f in files if f not in EDITABLE},
        "editable": {f: {"content": norm_bytes(os.path.join(GOLDEN, f)).decode()} for f in EDITABLE},
        "pages": pages,
        "weights": WEIGHTS,
        "values": {"p3-ler-S3": vals["p3-ler-S3"], "p3-ler-S3-wrong": wrong_ler(vals["p3-ler-S3"])},
        "soc_index_count": allsrc.count("\\index{soil organic carbon}"),
        "abbreviations": len(re.findall(r"^\s*\S[^&\n]*&[^\n]*\\\\", ab, re.M)) - 1,
    }
    os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
    with open(a.out, "w", encoding="utf-8", newline="\n") as f:
        json.dump(exp, f, indent=1, ensure_ascii=False, sort_keys=True)
        f.write("\n")
    print(f"expected.json: {len(exp['frozen'])} frozen files, {len(EDITABLE)} editable, "
          f"{pages} pages, {exp['abbreviations']} abbreviations, "
          f"soil organic carbon indexed {exp['soc_index_count']} times")


if __name__ == "__main__":
    main()
