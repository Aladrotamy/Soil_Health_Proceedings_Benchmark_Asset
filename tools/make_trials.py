#!/usr/bin/env python3
"""Generate the synthetic trial data of the Soil Health Proceedings asset.

Every value in project_source/data/ is produced by this script. The same seed
and block count always give byte-identical files (LF line endings, fixed
decimal places), on any operating system. Only the Python standard library is
used.

    python tools/make_trials.py                       # seed 20261001, 4 blocks
    python tools/make_trials.py --seed 7 --blocks 5 --out variants/x/data

The rules the data must obey are written out in notes/data_rules.md and are
checked by tools/check_data.py.
"""
import argparse
import os
import random

# ------------------------------------------------------------------ sites
# Three fictional sites, one per climatic zone. Texture and baseline soil
# properties are fixed; only plot-level variation is random.
SITES = [
    # id,  zone,             clay, silt, sand, pH0, SOC0 g/kg, BD g/cm3, rain mm, temp C
    ("S1", "temperate",       28,   40,   32,  6.4,  18.0,      1.32,      780,    10.5),
    ("S2", "semi-arid",       14,   22,   64,  7.6,   7.5,      1.48,      480,    24.0),
    ("S3", "humid tropical",  36,   24,   40,  5.4,  14.0,      1.25,     1450,    26.5),
]

# Site-specific crop response parameters (maize).
# ymax: attainable yield t/ha; y0: unfertilised yield t/ha; nopt: N rate at
# which the quadratic response reaches its plateau, kg/ha.
MAIZE = {"S1": (9.6, 4.2, 150), "S2": (5.4, 2.1, 110), "S3": (7.8, 2.9, 135)}
N_RATES = [0, 40, 80, 120, 160]
DEPTH_M = 0.20          # sampling depth for carbon stocks
YEARS = 5               # duration of the long-term trials


def rnd(x, places):
    """Round and format with a fixed number of decimals (stable text)."""
    return f"{x:.{places}f}"


def write_tsv(path, header, rows):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write("\t".join(header) + "\n")
        for r in rows:
            f.write("\t".join(str(v) for v in r) + "\n")


def clamp(x, lo, hi):
    return max(lo, min(hi, x))


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--seed", type=int, default=20261001)
    ap.add_argument("--blocks", type=int, default=4)
    ap.add_argument("--out", default=os.path.join("project_source", "data"))
    a = ap.parse_args()
    rng = random.Random(a.seed)
    g = rng.normalvariate
    blocks = list(range(1, a.blocks + 1))
    out = a.out
    register = []   # plot_id, trial, site, block, plot_in_block, treatment

    def plots(trial, site, treatments):
        """Randomise treatments within each block (RCBD) and register plots."""
        result = []
        for b in blocks:
            order = treatments[:]
            rng.shuffle(order)
            for pos, t in enumerate(order, start=1):
                pid = f"{trial}-{site}-B{b}-P{pos:02d}"
                register.append((pid, trial, site, b, pos, t))
                result.append((pid, b, t))
        return result

    # ------------------------------------------------------------ sites.tsv
    write_tsv(os.path.join(out, "sites.tsv"),
              ["site", "zone", "clay_pct", "silt_pct", "sand_pct", "ph_initial",
               "soc_initial_gkg", "bulk_density_gcm3", "rainfall_mm", "temperature_c"],
              [(s[0], s[1], s[2], s[3], s[4], rnd(s[5], 1), rnd(s[6], 1), rnd(s[7], 2),
                s[8], rnd(s[9], 1)) for s in SITES])

    # ------------------------------------------------------------ T1 soil health indicators
    systems = {"CONV": (0.00, 0.00), "CONS": (0.10, 0.08), "INTG": (0.18, 0.14)}
    rows = []
    for s in SITES:
        sid, _, clay, _, _, ph0, soc0, bd0, _, _ = s
        for pid, b, t in plots("T1", sid, list(systems)):
            c_gain, agg_gain = systems[t]
            soc = soc0 * (1 + c_gain) * (1 + g(0, 0.04))
            ph = clamp(ph0 + (0.15 if t == "INTG" else 0.0) + g(0, 0.08), 4.5, 8.5)
            p = clamp(22 + 0.9 * soc + (6 if t == "INTG" else 0) + g(0, 3), 5, 80)
            bd = clamp(bd0 - 0.6 * c_gain * 0.5 + g(0, 0.02), 1.0, 1.7)
            wsa = clamp(28 + 1.1 * clay * 0.5 + 100 * agg_gain + g(0, 3), 5, 95)
            mbc = clamp(9 * soc + 60 * c_gain * 10 + g(0, 12), 20, 900)
            rows.append((pid, sid, b, t, rnd(soc, 1), rnd(ph, 2), rnd(p, 1),
                         rnd(bd, 2), rnd(wsa, 1), rnd(mbc, 0)))
    write_tsv(os.path.join(out, "trials", "t1_indicators.tsv"),
              ["plot_id", "site", "block", "system", "soc_gkg", "ph_water",
               "p_mehlich3_mgkg", "bulk_density_gcm3", "wsa_pct", "mbc_mgkg"], rows)

    # ------------------------------------------------------------ T2 nitrogen rate
    rows = []
    for s in SITES:
        sid = s[0]
        ymax, y0, nopt = MAIZE[sid]
        block_eff = {b: g(0, 0.25) for b in blocks}
        trt = [f"N{n:03d}" for n in N_RATES]
        recs = plots("T2", sid, trt)
        base = {}
        for pid, b, t in recs:
            n = int(t[1:])
            x = min(n, nopt)
            y = y0 + (ymax - y0) * (2 * x / nopt - (x / nopt) ** 2)
            y = y + block_eff[b] + g(0, 0.35)
            if n == 0:
                base[b] = y
            rows.append([pid, sid, b, n, y])
        # rule R7: a fertilised plot never yields below the control of its block
        for r in rows:
            if r[1] == sid and r[3] > 0:
                r[4] = max(r[4], base[r[2]] + 0.10)
        for r in rows:
            if r[1] == sid:
                uptake = 10 * r[4] + 0.12 * r[3] + g(0, 3)
                r.append(max(uptake, 10))
    rows = [(pid, sid, b, n, rnd(y, 2), rnd(u, 1)) for pid, sid, b, n, y, u in rows]
    write_tsv(os.path.join(out, "trials", "t2_nitrogen.tsv"),
              ["plot_id", "site", "block", "n_rate_kgha", "grain_yield_tha", "n_uptake_kgha"],
              rows)

    # ------------------------------------------------------------ T3 intercropping
    rows = []
    for s in SITES:
        sid = s[0]
        sole_m = {"S1": 8.4, "S2": 4.6, "S3": 6.9}[sid]
        sole_c = {"S1": 1.6, "S2": 1.2, "S3": 1.9}[sid]
        pm, pc = {"S1": (0.74, 0.52), "S2": (0.70, 0.60), "S3": (0.78, 0.55)}[sid]
        recs = plots("T3", sid, ["SOLE_M", "SOLE_C", "INTER"])
        byblock = {}
        for pid, b, t in recs:
            byblock.setdefault(b, {})[t] = pid
        for b in blocks:
            m = sole_m * (1 + g(0, 0.05))
            c = sole_c * (1 + g(0, 0.06))
            im = m * clamp(pm + g(0, 0.03), 0.5, 0.95)
            ic = c * clamp(pc + g(0, 0.03), 0.3, 0.9)
            rows.append((byblock[b]["SOLE_M"], sid, b, "SOLE_M", rnd(m, 2), "NA"))
            rows.append((byblock[b]["SOLE_C"], sid, b, "SOLE_C", "NA", rnd(c, 2)))
            rows.append((byblock[b]["INTER"], sid, b, "INTER", rnd(im, 2), rnd(ic, 2)))
    write_tsv(os.path.join(out, "trials", "t3_intercrop.tsv"),
              ["plot_id", "site", "block", "system", "maize_yield_tha", "cowpea_yield_tha"],
              rows)

    # ------------------------------------------------------------ T4 tillage x residue
    rows = []
    for s in SITES:
        sid, _, clay, _, _, _, soc0, _, rain, _ = s
        dry = rain < 600
        recs = plots("T4", sid, ["CT-R0", "CT-R1", "NT-R0", "NT-R1"])
        for pid, b, t in recs:
            till, res = t.split("-")
            dsoc = -0.02 * YEARS * 0.2 + (0.035 if till == "NT" else 0) \
                + (0.045 if res == "R1" else 0) + (0.02 if t == "NT-R1" else 0)
            si = soc0 * (1 + g(0, 0.03))
            sf = si * (1 + dsoc + g(0, 0.012))
            ybase = MAIZE[sid][0] * 0.82
            ypen = -0.09 if (till == "NT" and res == "R0") else (-0.03 if till == "NT" else 0)
            if dry and t == "NT-R1":
                ypen = 0.07
            y = ybase * (1 + ypen + (0.02 if res == "R1" else 0) + g(0, 0.06))
            rows.append((pid, sid, b, till, res, rnd(si, 1), rnd(sf, 1), rnd(y, 2)))
    write_tsv(os.path.join(out, "trials", "t4_tillage.tsv"),
              ["plot_id", "site", "block", "tillage", "residue", "soc_initial_gkg",
               "soc_final_gkg", "grain_yield_tha"], rows)

    # ------------------------------------------------------------ T5 organic amendments
    rows = []
    c_added = 12.0   # t C/ha added in total over the trial, equal for every amendment
    for s in SITES:
        sid, _, clay, _, _, _, soc0, bd0, _, _ = s
        base_ret = 0.06 + 0.0045 * clay       # retention rises with clay content
        kind = {"CTRL": 0.0, "MANURE": 1.00, "COMPOST": 1.25, "RESIDUE": 0.70}
        recs = plots("T5", sid, list(kind))
        for pid, b, t in recs:
            si = soc0 * (1 + g(0, 0.03))
            stock_i = si * bd0 * DEPTH_M * 10          # t C/ha
            drift = -0.015 * stock_i                   # slow loss without inputs
            add = 0.0 if t == "CTRL" else c_added
            ret = 0.0 if t == "CTRL" else clamp(base_ret * kind[t] + g(0, 0.012), 0.02, 0.45)
            stock_f = stock_i + drift + ret * add + g(0, 0.15)
            sf = stock_f / (bd0 * DEPTH_M * 10)
            rows.append((pid, sid, b, t, rnd(add, 1), rnd(si, 1), rnd(sf, 1)))
    write_tsv(os.path.join(out, "trials", "t5_amendments.tsv"),
              ["plot_id", "site", "block", "amendment", "c_added_tha", "soc_initial_gkg",
               "soc_final_gkg"], rows)

    # ------------------------------------------------------------ plot register (Paper 6)
    write_tsv(os.path.join(out, "trials", "plot_register.tsv"),
              ["plot_id", "trial", "site", "block", "plot_in_block", "treatment"],
              sorted(register))


if __name__ == "__main__":
    main()
