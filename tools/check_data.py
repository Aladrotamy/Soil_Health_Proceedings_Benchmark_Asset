#!/usr/bin/env python3
"""Check the trial data against the fourteen rules in notes/data_rules.md.

    python tools/check_data.py                    # checks project_source/data
    python tools/check_data.py variants/variant_B/data

Prints the number of violations of each rule and exits with status 1 if any
rule fails, 0 otherwise. Only the Python standard library is used.
"""
import csv
import os
import sys
from collections import Counter, defaultdict

DEPTH_M = 0.20
TRIALS = {"t1_indicators.tsv": ("T1", "system"), "t2_nitrogen.tsv": ("T2", "n_rate_kgha"),
          "t3_intercrop.tsv": ("T3", "system"), "t4_tillage.tsv": ("T4", None),
          "t5_amendments.tsv": ("T5", "amendment")}


def read(path):
    with open(path, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f, delimiter="\t"))


def treatment(fname, r):
    if fname == "t4_tillage.tsv":
        return f"{r['tillage']}-{r['residue']}"
    if fname == "t2_nitrogen.tsv":
        return f"N{int(r['n_rate_kgha']):03d}"
    return r[TRIALS[fname][1]]


def main():
    data = sys.argv[1] if len(sys.argv) > 1 else os.path.join("project_source", "data")
    tdir = os.path.join(data, "trials")
    v = Counter()
    notes = defaultdict(list)

    def fail(rule, msg):
        v[rule] += 1
        if len(notes[rule]) < 3:
            notes[rule].append(msg)

    # R13 format, checked on the raw bytes of every file
    files = [os.path.join(data, "sites.tsv")] + \
        [os.path.join(tdir, f) for f in list(TRIALS) + ["plot_register.tsv"]]
    for p in files:
        raw = open(p, "rb").read()
        name = os.path.basename(p)
        try:
            text = raw.decode("utf-8")
        except UnicodeDecodeError:
            fail("R13", f"{name}: not UTF-8")
            continue
        if b"\r" in raw:
            fail("R13", f"{name}: CR character found")
        if not text.endswith("\n"):
            fail("R13", f"{name}: no final newline")
        lines = text.rstrip("\n").split("\n")
        width = len(lines[0].split("\t"))
        for i, line in enumerate(lines[1:], start=2):
            cells = line.split("\t")
            if len(cells) != width:
                fail("R13", f"{name} line {i}: {len(cells)} fields, header has {width}")
            if any(c == "" for c in cells):
                fail("R13", f"{name} line {i}: empty field")
            if "NA" in cells and name != "t3_intercrop.tsv":
                fail("R13", f"{name} line {i}: NA outside t3_intercrop.tsv")

    sites = {r["site"]: r for r in read(os.path.join(data, "sites.tsv"))}
    t = {f: read(os.path.join(tdir, f)) for f in TRIALS}
    reg = read(os.path.join(tdir, "plot_register.tsv"))

    # R1 sites
    try:
        if sorted(sites) != ["S1", "S2", "S3"]:
            fail("R1", f"sites are {sorted(sites)}")
        for s, r in sites.items():
            if int(r["clay_pct"]) + int(r["silt_pct"]) + int(r["sand_pct"]) != 100:
                fail("R1", f"{s}: texture does not sum to 100")
    except (KeyError, ValueError, TypeError, ZeroDivisionError) as e:
        fail("R1", f"could not be evaluated: {type(e).__name__} {e}")

    # R2 plot register
    try:
        ids = Counter(r["plot_id"] for r in reg)
        for pid, n in ids.items():
            if n > 1:
                fail("R2", f"{pid} appears {n} times in the register")
        regmap = {r["plot_id"]: r for r in reg}
        total = 0
        for f, rows in t.items():
            trial = TRIALS[f][0]
            for r in rows:
                total += 1
                g = regmap.get(r["plot_id"])
                if g is None:
                    fail("R2", f"{r['plot_id']} not in register")
                elif (g["trial"], g["site"], g["block"], g["treatment"]) != \
                        (trial, r["site"], r["block"], treatment(f, r)):
                    fail("R2", f"{r['plot_id']} differs from its register entry")
        if total != len(reg):
            fail("R2", f"register has {len(reg)} rows, trials have {total}")
    except (KeyError, ValueError, TypeError, ZeroDivisionError) as e:
        fail("R2", f"could not be evaluated: {type(e).__name__} {e}")

    # R3 complete blocks
    try:
        for f, rows in t.items():
            trts = sorted({treatment(f, r) for r in rows})
            cells = Counter((r["site"], r["block"], treatment(f, r)) for r in rows)
            for s in sites:
                blocks = sorted({r["block"] for r in rows if r["site"] == s})
                for b in blocks:
                    for tr in trts:
                        if cells[(s, b, tr)] != 1:
                            fail("R3", f"{f} {s} block {b}: {tr} x{cells[(s, b, tr)]}")
    except (KeyError, ValueError, TypeError, ZeroDivisionError) as e:
        fail("R3", f"could not be evaluated: {type(e).__name__} {e}")

    # R4-R6 soil ranges
    try:
        for r in t["t1_indicators.tsv"]:
            if not 4.5 <= float(r["ph_water"]) <= 8.5:
                fail("R4", f"{r['plot_id']} pH {r['ph_water']}")
            if not 5 <= float(r["p_mehlich3_mgkg"]) <= 80:
                fail("R6", f"{r['plot_id']} P {r['p_mehlich3_mgkg']}")
            if not 5 <= float(r["wsa_pct"]) <= 95:
                fail("R6", f"{r['plot_id']} WSA {r['wsa_pct']}")
            if not 20 <= float(r["mbc_mgkg"]) <= 900:
                fail("R6", f"{r['plot_id']} MBC {r['mbc_mgkg']}")
        for f, rows in t.items():
            for r in rows:
                for k, val in r.items():
                    if k.startswith("soc") and not 0 < float(val) <= 60:
                        fail("R5", f"{r['plot_id']} {k} {val}")
                    if k.startswith("bulk_density") and not 1.0 <= float(val) <= 1.7:
                        fail("R5", f"{r['plot_id']} {k} {val}")
        for s, r in sites.items():
            if not 1.0 <= float(r["bulk_density_gcm3"]) <= 1.7:
                fail("R5", f"{s} bulk density {r['bulk_density_gcm3']}")
    except (KeyError, ValueError, TypeError, ZeroDivisionError) as e:
        fail("R4", f"could not be evaluated: {type(e).__name__} {e}")

    # R7-R8 nitrogen
    try:
        ctrl = {(r["site"], r["block"]): float(r["grain_yield_tha"])
                for r in t["t2_nitrogen.tsv"] if int(r["n_rate_kgha"]) == 0}
        for r in t["t2_nitrogen.tsv"]:
            y = float(r["grain_yield_tha"])
            if not 0 < y <= 14:
                fail("R7", f"{r['plot_id']} yield {y}")
            if int(r["n_rate_kgha"]) > 0 and y < ctrl[(r["site"], r["block"])]:
                fail("R7", f"{r['plot_id']} yield {y} below its control")
            if float(r["n_uptake_kgha"]) < 10:
                fail("R8", f"{r['plot_id']} uptake {r['n_uptake_kgha']}")
    except (KeyError, ValueError, TypeError, ZeroDivisionError) as e:
        fail("R7", f"could not be evaluated: {type(e).__name__} {e}")

    # R9-R10 intercropping
    try:
        blk = defaultdict(dict)
        for r in t["t3_intercrop.tsv"]:
            blk[(r["site"], r["block"])][r["system"]] = r
            m, c = r["maize_yield_tha"], r["cowpea_yield_tha"]
            ok = {"SOLE_M": m != "NA" and c == "NA", "SOLE_C": m == "NA" and c != "NA",
                  "INTER": m != "NA" and c != "NA"}.get(r["system"], False)
            if not ok:
                fail("R9", f"{r['plot_id']} {r['system']} has maize={m} cowpea={c}")
        for key, d in blk.items():
            try:
                im, sm = float(d["INTER"]["maize_yield_tha"]), float(d["SOLE_M"]["maize_yield_tha"])
                ic, sc = float(d["INTER"]["cowpea_yield_tha"]), float(d["SOLE_C"]["cowpea_yield_tha"])
            except (KeyError, ValueError):
                continue
            if im >= sm or ic >= sc:
                fail("R9", f"{key}: intercrop yield not below sole yield")
            ler = im / sm + ic / sc
            if not 0.80 <= ler <= 1.60:
                fail("R10", f"{key}: LER {ler:.3f}")
    except (KeyError, ValueError, TypeError, ZeroDivisionError) as e:
        fail("R9", f"could not be evaluated: {type(e).__name__} {e}")

    # R11-R12 amendments
    try:
        ctrl_d = {}
        for r in t["t5_amendments.tsv"]:
            add = float(r["c_added_tha"])
            if r["amendment"] == "CTRL" and add != 0:
                fail("R11", f"{r['plot_id']} control has carbon added {add}")
            if r["amendment"] != "CTRL" and add != 12.0:
                fail("R11", f"{r['plot_id']} carbon added {add}, expected 12.0")
        def dstock(r):
            bd = float(sites[r["site"]]["bulk_density_gcm3"])
            return (float(r["soc_final_gkg"]) - float(r["soc_initial_gkg"])) * bd * DEPTH_M * 10
        for r in t["t5_amendments.tsv"]:
            if r["amendment"] == "CTRL":
                ctrl_d[(r["site"], r["block"])] = dstock(r)
        ret = defaultdict(list)
        for r in t["t5_amendments.tsv"]:
            if r["amendment"] != "CTRL":
                ret[r["site"]].append((dstock(r) - ctrl_d[(r["site"], r["block"])]) /
                                      float(r["c_added_tha"]))
        means = {s: sum(x) / len(x) for s, x in ret.items()}
        order = sorted(means, key=lambda s: int(sites[s]["clay_pct"]))
        for a, b in zip(order, order[1:]):
            if not means[a] < means[b]:
                fail("R12", f"retention {a} {means[a]:.3f} not below {b} {means[b]:.3f}")
    except (KeyError, ValueError, TypeError, ZeroDivisionError) as e:
        fail("R11", f"could not be evaluated: {type(e).__name__} {e}")

    # R14 apparent nitrogen recovery
    try:
        t2r = t["t2_nitrogen.tsv"]
        u0 = {(r["site"], r["block"]): float(r["n_uptake_kgha"]) for r in t2r if int(r["n_rate_kgha"]) == 0}
        groups = defaultdict(list)
        for r in t2r:
            n = int(r["n_rate_kgha"])
            if n > 0:
                groups[(r["site"], n)].append((float(r["n_uptake_kgha"]) - u0[(r["site"], r["block"])]) / n)
        for (s_, n), xs in sorted(groups.items()):
            m = sum(xs) / len(xs)
            if not 0 < m <= 1:
                fail("R14", f"{s_} N{n}: mean apparent recovery {m:.3f}")
    except (KeyError, ValueError, TypeError, ZeroDivisionError) as e:
        fail("R14", f"could not be evaluated: {type(e).__name__} {e}")

    # report
    print(f"Data rules check: {data}")
    for i in range(1, 15):
        rule = f"R{i}"
        print(f"  {rule:<4} {'PASS' if v[rule] == 0 else 'FAIL'}  violations: {v[rule]}")
        for n in notes[rule]:
            print(f"         - {n}")
    print(f"TOTAL violations: {sum(v.values())}")
    return 1 if sum(v.values()) else 0


if __name__ == "__main__":
    sys.exit(main())
