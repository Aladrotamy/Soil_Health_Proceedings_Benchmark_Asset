#!/usr/bin/env python3
"""Compute every result reported in the volume from the trial data.

Reads project_source/data/ and writes project_source/results/:
  p1_indicators.tsv  mean indicator values and soil health index by site and system
  p2_response.tsv    mean yield, uptake and efficiencies by site and N rate
  p2_fit.tsv         quadratic-plateau fit per site
  p3_ler.tsv         mean partial and total land equivalent ratio by site
  p4_means.tsv       mean SOC change and yield by site, tillage and residue
  p4_anova.tsv       factorial analysis of variance per site
  p5_retention.tsv   mean carbon retention by site and amendment
  p6_combined.tsv    combined analysis of variance of maize yield (trial T2)
  values.tex         the numbers quoted in the text, as \\resdef{key}{value}

The tables and figures of the volume read these files, and the text quotes
values.tex, so text, tables, figures and data cannot disagree. Standard library
only; output uses LF line endings and fixed decimals.

    python tools/compute_results.py
    python tools/compute_results.py --data variants/variant_B/data --out variants/variant_B/results
"""
import argparse
import csv
import math
import os
from collections import defaultdict

SITES = ["S1", "S2", "S3"]
DEPTH_M = 0.20

# Scoring limits of Paper 1 (tables/scoring.tex): (curve, L, O1, O2, U)
SCORING = {
    "soc_gkg": ("more", 5, None, None, 25),
    "ph_water": ("optimum", 4.5, 6.0, 7.0, 8.5),
    "p_mehlich3_mgkg": ("more", 5, None, None, 40),
    "bulk_density_gcm3": ("less", 1.10, None, None, 1.60),
    "wsa_pct": ("more", 20, None, None, 70),
    "mbc_mgkg": ("more", 50, None, None, 300),
}


# ------------------------------------------------------------------ helpers
def read(path):
    with open(path, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f, delimiter="\t"))


def write(path, header, rows):
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write("\t".join(header) + "\n")
        for r in rows:
            f.write("\t".join(str(x) for x in r) + "\n")


def mean(xs):
    xs = list(xs)
    return sum(xs) / len(xs)


def fx(x, p):
    return f"{x:.{p}f}"


def fmt_p(p):
    return "<0.001" if p < 0.001 else f"{p:.3f}"


def betacf(a, b, x):
    """Continued fraction for the incomplete beta function (Lentz)."""
    tiny, eps = 1e-300, 3e-16
    qab, qap, qam = a + b, a + 1, a - 1
    c, d = 1.0, 1 - qab * x / qap
    d = 1 / (d if abs(d) > tiny else tiny)
    h = d
    for m in range(1, 300):
        m2 = 2 * m
        aa = m * (b - m) * x / ((qam + m2) * (a + m2))
        d = 1 + aa * d
        d = 1 / (d if abs(d) > tiny else tiny)
        c = 1 + aa / c if abs(1 + aa / c) > tiny else tiny
        h *= d * c
        aa = -(a + m) * (qab + m) * x / ((a + m2) * (qap + m2))
        d = 1 + aa * d
        d = 1 / (d if abs(d) > tiny else tiny)
        c = 1 + aa / c if abs(1 + aa / c) > tiny else tiny
        dl = d * c
        h *= dl
        if abs(dl - 1) < eps:
            break
    return h


def betai(a, b, x):
    if x <= 0:
        return 0.0
    if x >= 1:
        return 1.0
    lbt = math.lgamma(a + b) - math.lgamma(a) - math.lgamma(b) + a * math.log(x) + b * math.log(1 - x)
    if x < (a + 1) / (a + b + 2):
        return math.exp(lbt) * betacf(a, b, x) / a
    return 1 - math.exp(lbt) * betacf(b, a, 1 - x) / b


def f_pvalue(f, d1, d2):
    """Upper-tail probability of the F distribution."""
    if f <= 0:
        return 1.0
    return betai(d2 / 2, d1 / 2, d2 / (d2 + d1 * f))


def score(key, x):
    curve, L, o1, o2, U = SCORING[key]
    if curve == "more":
        return min(1, max(0, (x - L) / (U - L)))
    if curve == "less":
        return 1 - min(1, max(0, (x - L) / (U - L)))
    if x <= L or x >= U:
        return 0.0
    if x < o1:
        return (x - L) / (o1 - L)
    if x <= o2:
        return 1.0
    return (U - x) / (U - o2)


def solve3(m, v):
    """Solve a 3x3 linear system by Gaussian elimination."""
    a = [row[:] + [v[i]] for i, row in enumerate(m)]
    for i in range(3):
        piv = max(range(i, 3), key=lambda r: abs(a[r][i]))
        a[i], a[piv] = a[piv], a[i]
        for r in range(3):
            if r != i:
                f = a[r][i] / a[i][i]
                a[r] = [x - f * y for x, y in zip(a[r], a[i])]
    return [a[i][3] / a[i][i] for i in range(3)]


def anova_rcbd(cells):
    """cells: {(treatment, block): y}. Returns df, MSE, F and P of treatments."""
    trts = sorted({t for t, _ in cells})
    blks = sorted({b for _, b in cells})
    t, r = len(trts), len(blks)
    g = mean(cells.values())
    sst = r * sum((mean(cells[(i, j)] for j in blks) - g) ** 2 for i in trts)
    ssb = t * sum((mean(cells[(i, j)] for i in trts) - g) ** 2 for j in blks)
    sstot = sum((y - g) ** 2 for y in cells.values())
    sse = sstot - sst - ssb
    dft, dfb, dfe = t - 1, r - 1, (t - 1) * (r - 1)
    mse = sse / dfe
    f = (sst / dft) / mse
    return {"dft": dft, "dfe": dfe, "mse": mse, "F": f, "P": f_pvalue(f, dft, dfe)}


# ------------------------------------------------------------------ main
def main():
    ap = argparse.ArgumentParser(description="Compute the results of the volume.")
    ap.add_argument("--data", default=os.path.join("project_source", "data"))
    ap.add_argument("--out", default=os.path.join("project_source", "results"))
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    T = os.path.join(a.data, "trials")
    sites = {r["site"]: r for r in read(os.path.join(a.data, "sites.tsv"))}
    val = {}   # values quoted in the text

    # ---------------------------------------------------------- Paper 1
    t1 = read(os.path.join(T, "t1_indicators.tsv"))
    keys = list(SCORING)
    rows, shi_site = [], defaultdict(dict)
    for s in SITES:
        for sysname in ["CONV", "CONS", "INTG"]:
            rr = [r for r in t1 if r["site"] == s and r["system"] == sysname]
            means = [mean(float(r[k]) for r in rr) for k in keys]
            shi = mean(mean(score(k, float(r[k])) for k in keys) for r in rr)
            shi_site[s][sysname] = shi
            rows.append([s, sysname, fx(means[0], 1), fx(means[1], 2), fx(means[2], 1),
                         fx(means[3], 2), fx(means[4], 1), fx(means[5], 0), fx(shi, 3)])
    write(os.path.join(a.out, "p1_indicators.tsv"),
          ["site", "system", "soc", "ph", "p", "bd", "wsa", "mbc", "shi"], rows)
    for s in SITES:
        for k, v in shi_site[s].items():
            val[f"p1-shi-{s}-{k}"] = fx(v, 3)
        cells = {(r["system"], r["block"]): mean(score(k, float(r[k])) for k in keys)
                 for r in t1 if r["site"] == s}
        an = anova_rcbd(cells)
        val[f"p1-F-{s}"], val[f"p1-P-{s}"] = fx(an["F"], 2), fmt_p(an["P"])
    allshi = [v for s in SITES for v in shi_site[s].values()]
    val["p1-shi-min"], val["p1-shi-max"] = fx(min(allshi), 3), fx(max(allshi), 3)

    # ---------------------------------------------------------- Paper 2
    t2 = read(os.path.join(T, "t2_nitrogen.tsv"))
    rates = sorted({int(r["n_rate_kgha"]) for r in t2})
    rows, fits = [], []
    for s in SITES:
        rr = [r for r in t2 if r["site"] == s]
        ctrl = {r["block"]: r for r in rr if int(r["n_rate_kgha"]) == 0}
        for n in rates:
            x = [r for r in rr if int(r["n_rate_kgha"]) == n]
            y = mean(float(r["grain_yield_tha"]) for r in x)
            u = mean(float(r["n_uptake_kgha"]) for r in x)
            if n:
                ae = mean(1000 * (float(r["grain_yield_tha"]) - float(ctrl[r["block"]]["grain_yield_tha"])) / n for r in x)
                re_ = mean((float(r["n_uptake_kgha"]) - float(ctrl[r["block"]]["n_uptake_kgha"])) / n for r in x)
                rows.append([s, n, fx(y, 2), fx(u, 1), fx(ae, 1), fx(re_, 2)])
            else:
                rows.append([s, n, fx(y, 2), fx(u, 1), "NA", "NA"])
            val[f"p2-yield-{s}-N{n}"] = fx(y, 2)
        # quadratic fit Y = a + bN + cN^2 by least squares on plot values
        xs = [float(r["n_rate_kgha"]) for r in rr]
        ys = [float(r["grain_yield_tha"]) for r in rr]
        S = [[sum(x ** (i + j) for x in xs) for j in range(3)] for i in range(3)]
        v = [sum(y * x ** i for x, y in zip(xs, ys)) for i in range(3)]
        c0, c1, c2 = solve3(S, v)
        nopt = -c1 / (2 * c2) if c2 < 0 else max(rates)
        nopt = min(nopt, max(rates))
        ypl = c0 + c1 * nopt + c2 * nopt ** 2
        ssr = sum((y - (c0 + c1 * x + c2 * x * x)) ** 2 for x, y in zip(xs, ys))
        sst = sum((y - mean(ys)) ** 2 for y in ys)
        r2 = 1 - ssr / sst
        fits.append([s, fx(c0, 4), fx(c1, 6), fx(c2, 8), fx(nopt, 0), fx(ypl, 2), fx(r2, 3)])
        val[f"p2-nopt-{s}"], val[f"p2-yplat-{s}"], val[f"p2-rsq-{s}"] = fx(nopt, 0), fx(ypl, 2), fx(r2, 3)
        ae40 = [r for r in rows if r[0] == s and r[1] == 40][0][4]
        ae160 = [r for r in rows if r[0] == s and r[1] == 160][0][4]
        val[f"p2-ae40-{s}"], val[f"p2-ae160-{s}"] = ae40, ae160
    write(os.path.join(a.out, "p2_response.tsv"),
          ["site", "n_rate", "yield", "uptake", "ae", "re"], rows)
    write(os.path.join(a.out, "p2_fit.tsv"),
          ["site", "a", "b", "c", "nopt", "yplat", "rsq"], fits)

    # ---------------------------------------------------------- Paper 3
    t3 = read(os.path.join(T, "t3_intercrop.tsv"))
    rows = []
    for s in SITES:
        blk = defaultdict(dict)
        for r in t3:
            if r["site"] == s:
                blk[r["block"]][r["system"]] = r
        lm = [float(d["INTER"]["maize_yield_tha"]) / float(d["SOLE_M"]["maize_yield_tha"]) for d in blk.values()]
        lc = [float(d["INTER"]["cowpea_yield_tha"]) / float(d["SOLE_C"]["cowpea_yield_tha"]) for d in blk.values()]
        tot = [x + y for x, y in zip(lm, lc)]
        rows.append([s, fx(mean(lm), 2), fx(mean(lc), 2), fx(mean(tot), 2), fx(min(tot), 2), fx(max(tot), 2)])
        val[f"p3-ler-{s}"], val[f"p3-lerm-{s}"], val[f"p3-lerc-{s}"] = fx(mean(tot), 2), fx(mean(lm), 2), fx(mean(lc), 2)
    write(os.path.join(a.out, "p3_ler.tsv"),
          ["site", "ler_maize", "ler_cowpea", "ler_total", "ler_min", "ler_max"], rows)

    # ---------------------------------------------------------- Paper 4
    t4 = read(os.path.join(T, "t4_tillage.tsv"))
    rows, arows = [], []
    for s in SITES:
        rr = [r for r in t4 if r["site"] == s]
        for tl in ["CT", "NT"]:
            for rs in ["R0", "R1"]:
                x = [r for r in rr if r["tillage"] == tl and r["residue"] == rs]
                ds = mean(float(r["soc_final_gkg"]) - float(r["soc_initial_gkg"]) for r in x)
                y = mean(float(r["grain_yield_tha"]) for r in x)
                rows.append([s, tl, rs, fx(ds, 2), fx(y, 2)])
                val[f"p4-dsoc-{s}-{tl}{rs}"], val[f"p4-yield-{s}-{tl}{rs}"] = fx(ds, 2), fx(y, 2)
        for resp, fn in [("dsoc", lambda r: float(r["soc_final_gkg"]) - float(r["soc_initial_gkg"])),
                         ("yield", lambda r: float(r["grain_yield_tha"]))]:
            ys = {(r["tillage"], r["residue"], r["block"]): fn(r) for r in rr}
            blks = sorted({k[2] for k in ys})
            g = mean(ys.values())
            m_t = {tl: mean(v for k, v in ys.items() if k[0] == tl) for tl in ["CT", "NT"]}
            m_r = {rs: mean(v for k, v in ys.items() if k[1] == rs) for rs in ["R0", "R1"]}
            m_b = {b: mean(v for k, v in ys.items() if k[2] == b) for b in blks}
            m_tr = {(tl, rs): mean(v for k, v in ys.items() if k[:2] == (tl, rs)) for tl in m_t for rs in m_r}
            nb = len(blks)
            ss_t = 2 * nb * sum((m - g) ** 2 for m in m_t.values())
            ss_r = 2 * nb * sum((m - g) ** 2 for m in m_r.values())
            ss_tr = nb * sum((m_tr[(tl, rs)] - m_t[tl] - m_r[rs] + g) ** 2 for tl in m_t for rs in m_r)
            ss_b = 4 * sum((m - g) ** 2 for m in m_b.values())
            ss_tot = sum((v - g) ** 2 for v in ys.values())
            ss_e = ss_tot - ss_t - ss_r - ss_tr - ss_b
            df_e = 3 * (nb - 1)
            mse = ss_e / df_e
            for src, ss in [("tillage", ss_t), ("residue", ss_r), ("interaction", ss_tr)]:
                f = ss / mse
                p = f_pvalue(f, 1, df_e)
                arows.append([s, resp, src, 1, df_e, fx(f, 2), fmt_p(p)])
                val[f"p4-{resp}-{src}-F-{s}"], val[f"p4-{resp}-{src}-P-{s}"] = fx(f, 2), fmt_p(p)
    write(os.path.join(a.out, "p4_means.tsv"), ["site", "tillage", "residue", "dsoc", "yield"], rows)
    write(os.path.join(a.out, "p4_anova.tsv"), ["site", "response", "source", "df1", "df2", "F", "P"], arows)

    # ---------------------------------------------------------- Paper 5
    t5 = read(os.path.join(T, "t5_amendments.tsv"))
    def dstock(r):
        bd = float(sites[r["site"]]["bulk_density_gcm3"])
        return (float(r["soc_final_gkg"]) - float(r["soc_initial_gkg"])) * bd * DEPTH_M * 10
    ctrl = {(r["site"], r["block"]): dstock(r) for r in t5 if r["amendment"] == "CTRL"}
    rows = []
    for s in SITES:
        per = []
        for am in ["MANURE", "COMPOST", "RESIDUE"]:
            x = [r for r in t5 if r["site"] == s and r["amendment"] == am]
            ret = mean((dstock(r) - ctrl[(s, r["block"])]) / float(r["c_added_tha"]) for r in x)
            per.append(ret)
            rows.append([s, sites[s]["clay_pct"], am, fx(ret, 3)])
            val[f"p5-ret-{s}-{am}"] = fx(ret, 3)
        val[f"p5-ret-{s}"] = fx(mean(per), 3)
    write(os.path.join(a.out, "p5_retention.tsv"), ["site", "clay", "amendment", "retention"], rows)

    # ---------------------------------------------------------- Paper 6
    # combined analysis of maize yield in trial T2 across the three sites
    y = {(r["site"], int(r["n_rate_kgha"]), r["block"]): float(r["grain_yield_tha"]) for r in t2}
    blks = sorted({k[2] for k in y})
    nb, ns, nt = len(blks), len(SITES), len(rates)
    g = mean(y.values())
    m_s = {s: mean(v for k, v in y.items() if k[0] == s) for s in SITES}
    m_n = {n: mean(v for k, v in y.items() if k[1] == n) for n in rates}
    m_sn = {(s, n): mean(v for k, v in y.items() if k[:2] == (s, n)) for s in SITES for n in rates}
    m_sb = {(s, b): mean(v for k, v in y.items() if (k[0], k[2]) == (s, b)) for s in SITES for b in blks}
    ss_s = nt * nb * sum((m - g) ** 2 for m in m_s.values())
    ss_bs = nt * sum((m_sb[(s, b)] - m_s[s]) ** 2 for s in SITES for b in blks)
    ss_n = ns * nb * sum((m - g) ** 2 for m in m_n.values())
    ss_sn = nb * sum((m_sn[(s, n)] - m_s[s] - m_n[n] + g) ** 2 for s in SITES for n in rates)
    ss_tot = sum((v - g) ** 2 for v in y.values())
    ss_e = ss_tot - ss_s - ss_bs - ss_n - ss_sn
    df = {"site": ns - 1, "block(site)": ns * (nb - 1), "nitrogen": nt - 1,
          "site x nitrogen": (ns - 1) * (nt - 1), "error": ns * (nb - 1) * (nt - 1)}
    ss = {"site": ss_s, "block(site)": ss_bs, "nitrogen": ss_n, "site x nitrogen": ss_sn, "error": ss_e}
    mse = ss_e / df["error"]
    rows = []
    for src in ["site", "block(site)", "nitrogen", "site x nitrogen", "error"]:
        ms = ss[src] / df[src]
        if src == "error":
            rows.append([src, df[src], fx(ss[src], 2), fx(ms, 3), "NA", "NA"])
        else:
            # site is tested against blocks within sites; the other terms against error
            den, dfd = (ss_bs / df["block(site)"], df["block(site)"]) if src == "site" else (mse, df["error"])
            f = ms / den
            p = f_pvalue(f, df[src], dfd)
            rows.append([src, df[src], fx(ss[src], 2), fx(ms, 3), fx(f, 2), fmt_p(p)])
            key = src.replace(" x ", "x").replace("(", "").replace(")", "")
            val[f"p6-F-{key}"], val[f"p6-P-{key}"] = fx(f, 2), fmt_p(p)
    write(os.path.join(a.out, "p6_combined.tsv"), ["source", "df", "ss", "ms", "F", "P"], rows)
    val["p6-df-error"] = str(df["error"])
    # two-sided 5 % t quantile, found by bisection on F(1, df) = t^2
    lo, hi = 0.0, 50.0
    for _ in range(200):
        mid = (lo + hi) / 2
        if f_pvalue(mid, 1, df["error"]) > 0.05:
            lo = mid
        else:
            hi = mid
    tcrit = math.sqrt((lo + hi) / 2)
    lsd = tcrit * math.sqrt(2 * mse / nb)
    val["p6-lsd"], val["p6-tcrit"] = fx(lsd, 2), fx(tcrit, 3)

    with open(os.path.join(a.out, "values.tex"), "w", encoding="utf-8", newline="\n") as f:
        f.write("% values.tex -- generated by tools/compute_results.py; do not edit by hand.\n")
        f.write("% Each value is quoted in the text as \\res{key}.\n")
        for k in sorted(val):
            f.write(f"\\resdef{{{k}}}{{{val[k]}}}\n")


if __name__ == "__main__":
    main()
