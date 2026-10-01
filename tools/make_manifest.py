#!/usr/bin/env python3
"""Write or check MANIFEST.sha256: the SHA-256 of every file of the asset.

    python tools/make_manifest.py           # write MANIFEST.sha256
    python tools/make_manifest.py --check   # verify every file against it

Text files are hashed with CRLF folded to LF, so a Windows checkout and a Linux
checkout give the same manifest. LaTeX build output, Python caches and the
.git folder are skipped. Standard library only.
"""
import hashlib
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SKIP_DIRS = {".git", "__pycache__"}
SKIP_EXT = (".aux", ".log", ".out", ".toc", ".lof", ".lot", ".bbl", ".blg", ".bcf", ".run.xml",
            ".idx", ".ind", ".ilg", ".synctex.gz", ".fls", ".fdb_latexmk", ".pyc")
BINARY_EXT = (".pdf", ".png", ".jpg", ".zip")
NAME = "MANIFEST.sha256"


def files():
    for d, dirs, fs in os.walk(ROOT):
        dirs[:] = sorted(x for x in dirs if x not in SKIP_DIRS)
        for f in sorted(fs):
            rel = os.path.relpath(os.path.join(d, f), ROOT).replace(os.sep, "/")
            if rel == NAME or rel.endswith(SKIP_EXT):
                continue
            # standalone paper PDFs are build output, not part of the asset
            if rel.endswith(".pdf") and "/papers/" in rel:
                continue
            yield rel


def digest(rel):
    data = open(os.path.join(ROOT, rel), "rb").read()
    if not rel.endswith(BINARY_EXT):
        data = data.replace(b"\r\n", b"\n")
    return hashlib.sha256(data).hexdigest()


def main():
    path = os.path.join(ROOT, NAME)
    if "--check" in sys.argv:
        want = dict(reversed(line.split("  ", 1)) for line in open(path, encoding="utf-8").read().splitlines() if line)
        have = set(files())
        bad = [f for f, h in want.items() if f not in have or digest(f) != h]
        new = sorted(have - set(want))
        print(f"{len(want) - len(bad)} of {len(want)} files match {NAME}; {len(new)} files not listed")
        for f in bad[:10]:
            print(f"  changed or missing: {f}")
        for f in new[:10]:
            print(f"  not listed: {f}")
        return 1 if bad or new else 0
    lines = [f"{digest(f)}  {f}" for f in files()]
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write("\n".join(lines) + "\n")
    print(f"{NAME}: {len(lines)} files")
    return 0


if __name__ == "__main__":
    sys.exit(main())
