#!/usr/bin/env python3
"""Check every qualitative claim made in the text against the computed results.

The Results, Discussion and Conclusion sections state some findings in words
("the interaction was significant at S1 and S3 but not at S2"). Each such
statement is encoded here as a test on results/, so that text and data cannot
disagree, and so that a variant built from new data is accepted only if every
claim still holds.

    python tools/check_claims.py                         # project_source/results
    python tools/check_claims.py variants/variant_B/golden_solution/results

Exits with status 1 if any claim fails. Standard library only.
"""
import csv
import os
import re
import sys

SITES = ["S1", "S2", "S3"]


def read(d, f):
    with open(os.path.join(d, f), encoding="utf-8", newline="") as h:
        return list(csv.DictReader(h, delimiter="\t"))


def pv(s):
    """P value from a table cell: '<0.001' -> 0.0005."""
    return 0.0005 if s.startswith("<") else float(s)


def textp(s):
    """P value from its text form in values.tex: '\\ensuremath{P=0.039}'."""
    return 0.0005 if "<" in s else float(re.search(r"[0-9.]+", s.split("=")[-1]).group())


def claims(d):
    p1 = {(r["site"], r["system"]): r for r in read(d, "p1_indicators.tsv")}
    p2 = {(r["site"], int(r["n_rate"])): r for r in read(d, "p2_response.tsv")}
    fit = {r["site"]: r for r in read(d, "p2_fit.tsv")}
    p3 = {r["site"]: r for r in read(d, "p3_ler.tsv")}
    p4 = {(r["site"], r["tillage"] + r["residue"]): r for r in read(d, "p4_means.tsv")}
    a4 = {(r["site"], r["response"], r["source"]): pv(r["P"]) for r in read(d, "p4_anova.tsv")}
    p5 = {(r["site"], r["amendment"]): float(r["retention"]) for r in read(d, "p5_retention.tsv")}
    p6 = {r["source"]: r for r in read(d, "p6_combined.tsv")}
    vals = dict(re.findall(r"\\resdef\{([^}]*)\}\{(.*)\}", open(os.path.join(d, "values.tex"), encoding="utf-8").read()))
    f = lambda r, k: float(r[k])
    sy = ["CONV", "CONS", "INTG"]
    return list({
        # Paper 1
        "P1 integrated system highest and conventional lowest in SOC, WSA and MBC at every site":
            all(f(p1[(s, "CONV")], k) < f(p1[(s, "CONS")], k) < f(p1[(s, "INTG")], k)
                for s in SITES for k in ["soc", "wsa", "mbc"]),
        "P1 bulk density lowest under the integrated system at every site":
            all(f(p1[(s, "INTG")], "bd") < min(f(p1[(s, "CONV")], "bd"), f(p1[(s, "CONS")], "bd")) for s in SITES),
        "P1 soil health index CONV < CONS < INTG at every site":
            all(f(p1[(s, "CONV")], "shi") < f(p1[(s, "CONS")], "shi") < f(p1[(s, "INTG")], "shi") for s in SITES),
        "P1 semi-arid site S2 lowest index under every system":
            all(f(p1[("S2", x)], "shi") < min(f(p1[("S1", x)], "shi"), f(p1[("S3", x)], "shi")) for x in sy),
        "P1 effect of system on the index significant at every site (P < 0.05)":
            all(textp(vals[f"p1-P-{s}"]) < 0.05 for s in SITES),
        # Paper 2
        "P2 mean yield rises from 0 to 120 kg N/ha at every site":
            all(f(p2[(s, 0)], "yield") < f(p2[(s, 40)], "yield") < f(p2[(s, 80)], "yield") < f(p2[(s, 120)], "yield")
                for s in SITES),
        "P2 160 kg N/ha adds less than 0.3 t/ha over 120 kg N/ha":
            all(f(p2[(s, 160)], "yield") - f(p2[(s, 120)], "yield") < 0.3 for s in SITES),
        "P2 response well described (R2 > 0.90 at every site)": all(f(fit[s], "rsq") > 0.90 for s in SITES),
        "P2 optimum rate highest at S1 and lowest at S2":
            f(fit["S1"], "nopt") > f(fit["S3"], "nopt") > f(fit["S2"], "nopt"),
        "P2 agronomic efficiency declines with every increase in rate":
            all(f(p2[(s, 40)], "ae") > f(p2[(s, 80)], "ae") > f(p2[(s, 120)], "ae") > f(p2[(s, 160)], "ae")
                for s in SITES),
        "P2 apparent recovery lower at 160 than at 40 kg N/ha at every site":
            all(f(p2[(s, 160)], "re") < f(p2[(s, 40)], "re") for s in SITES),
        # Paper 3
        "P3 total LER above 1 at every site": all(f(p3[s], "ler_total") > 1 for s in SITES),
        "P3 maize partial ratio larger than cowpea at every site":
            all(f(p3[s], "ler_maize") > f(p3[s], "ler_cowpea") for s in SITES),
        "P3 LER highest at S3 and lowest at S1":
            f(p3["S1"], "ler_total") < f(p3["S2"], "ler_total") < f(p3["S3"], "ler_total"),
        "P3 highest LER where maize keeps the largest share":
            max(SITES, key=lambda s: f(p3[s], "ler_total")) == max(SITES, key=lambda s: f(p3[s], "ler_maize")),
        # Paper 4
        "P4 SOC falls under CT-R0 and rises under every other combination":
            all(f(p4[(s, "CTR0")], "dsoc") < 0 < min(f(p4[(s, t)], "dsoc") for t in ["CTR1", "NTR0", "NTR1"])
                for s in SITES),
        "P4 largest SOC gain under NT-R1 at every site":
            all(max(["CTR0", "CTR1", "NTR0", "NTR1"], key=lambda t: f(p4[(s, t)], "dsoc")) == "NTR1" for s in SITES),
        "P4 both main effects on SOC significant at every site":
            all(a4[(s, "dsoc", x)] < 0.05 for s in SITES for x in ["tillage", "residue"]),
        "P4 tillage x residue on SOC significant at S1 and S3, not at S2":
            a4[("S1", "dsoc", "interaction")] < 0.05 and a4[("S3", "dsoc", "interaction")] < 0.05
            and a4[("S2", "dsoc", "interaction")] >= 0.05,
        "P4 at S1 no-till lowers yield (P < 0.05), NT-R0 below CT-R0":
            a4[("S1", "yield", "tillage")] < 0.05 and f(p4[("S1", "NTR0")], "yield") < f(p4[("S1", "CTR0")], "yield"),
        "P4 at S2 interaction on yield significant; NT-R1 highest and NT-R0 lowest":
            a4[("S2", "yield", "interaction")] < 0.05
            and max(["CTR0", "CTR1", "NTR0", "NTR1"], key=lambda t: f(p4[("S2", t)], "yield")) == "NTR1"
            and min(["CTR0", "CTR1", "NTR0", "NTR1"], key=lambda t: f(p4[("S2", t)], "yield")) == "NTR0",
        "P4 at S3 neither tillage nor residues significant for yield":
            a4[("S3", "yield", "tillage")] >= 0.05 and a4[("S3", "yield", "residue")] >= 0.05,
        # Paper 5
        "P5 compost > manure > residue retention at every site":
            all(p5[(s, "COMPOST")] > p5[(s, "MANURE")] > p5[(s, "RESIDUE")] for s in SITES),
        "P5 only a modest fraction retained (every mean below 0.5)": all(v < 0.5 for v in p5.values()),
        # Paper 6
        "P6 site, nitrogen, site x nitrogen and blocks within sites all significant":
            all(pv(p6[k]["P"]) < 0.05 for k in ["site", "nitrogen", "site x nitrogen", "block(site)"]),
    }.items())


def main():
    d = sys.argv[1] if len(sys.argv) > 1 else os.path.join("project_source", "results")
    rows = list(claims(d))
    for name, ok in rows:
        print(f"  {'PASS' if ok else 'FAIL'}  {name}")
    bad = sum(not ok for _, ok in rows)
    print(f"Claims: {len(rows) - bad} of {len(rows)} hold")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
