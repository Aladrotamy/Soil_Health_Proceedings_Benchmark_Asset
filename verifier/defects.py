#!/usr/bin/env python3
"""The six planted defects, defined once and used by every tool.

Each defect is a text substitution in one file: the golden text and the
seeded (defective) text. tools/make_variant.py applies them to a variant's
golden solution to build its start state; verifier/run_oracle.py undoes them
to build its test submissions. D4 depends on the data: the seeded value is the
computed value minus 0.05.
"""


def wrong_ler(correct):
    return f"{float(correct) - 0.05:.2f}"


def defects(values):
    """values: dict of results/values.tex. Returns {id: (file, golden, seeded)}."""
    correct = values["p3-ler-S3"]
    return {
        "D1": ("tables/sites.tex",
               "  \\centering\\footnotesize\n  \\setlength{\\tabcolsep}{4pt}\n",
               "  \\centering\\small\n"),
        "D2": ("papers/discussion/paper4_discussion.tex",
               "with residue retention \\parencite{pittelkow2015}.",
               "with residue retention \\parencite{pittelkow2016}."),
        "D3": ("papers/results/paper3_results.tex",
               "(Table~\\ref{tab:p3ler})", "(Table~\\ref{tab:p3LER})"),
        "D4": ("papers/discussion/paper3_discussion.tex",
               "\\res{p3-ler-S3}. Maize contributed", f"{wrong_ler(correct)}. Maize contributed"),
        "D5": ("papers/paper4_tillage.tex",
               "topsoil organic carbon\\index{soil organic carbon}",
               "topsoil organic carbon\\index{Soil organic carbon}"),
        "D6": ("backmatter/abbreviations.tex",
               "  LER      & land equivalent ratio \\\\\n", ""),
    }
