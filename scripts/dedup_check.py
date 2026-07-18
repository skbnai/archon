#!/usr/bin/env python3
"""Shingle-based near-duplicate detector.
Usage: dedup_check.py <file> [threshold]   -> compares vs all docs/**/*.md
       dedup_check.py --all [threshold]    -> pairwise report for CI
Exit 1 on any pair >= threshold (default 0.55)."""
import sys, re, itertools, pathlib

def shingles(path, k=8):
    txt = pathlib.Path(path).read_text(encoding="utf-8", errors="ignore")
    txt = re.sub(r"^---\n.*?\n---\n", "", txt, flags=re.S)      # drop frontmatter
    words = re.findall(r"[a-z0-9]+", txt.lower())
    return {" ".join(words[i:i+k]) for i in range(max(0, len(words)-k+1))}

def jac(a, b):
    if not a or not b: return 0.0
    return len(a & b) / len(a | b)

def main():
    thr = 0.55
    args = sys.argv[1:]
    if args and re.match(r"^0?\.\d+$", args[-1]): thr = float(args.pop())
    files = sorted(str(p) for p in pathlib.Path("docs").rglob("*.md"))
    sh = {}
    bad = []
    if args and args[0] != "--all":
        target = args[0]
        st = shingles(target)
        for f in files:
            if pathlib.Path(f).resolve() == pathlib.Path(target).resolve(): continue
            s = jac(st, shingles(f))
            if s >= thr: bad.append((target, f, s))
    else:
        for f in files: sh[f] = shingles(f)
        for a, b in itertools.combinations(files, 2):
            s = jac(sh[a], sh[b])
            if s >= thr: bad.append((a, b, s))
    for a, b, s in sorted(bad, key=lambda x: -x[2]):
        print(f"DUPLICATE {s:.0%}: {a} <-> {b}")
    if bad:
        print(f"\n{len(bad)} pair(s) over threshold {thr}. Merge per "
              f"dedup-canonicalization skill; do not ship both.")
        sys.exit(1)
    print("dedup: clean")

if __name__ == "__main__":
    main()
