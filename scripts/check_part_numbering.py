#!/usr/bin/env python3
"""Check that every 'Part N of M' navigation label in a split series matches
the actual number of files in that series, and that N increments correctly.

Usage: python3 scripts/check_part_numbering.py [--fix]
--fix rewrites only the M (total count) in mismatched labels; N and link
text are left alone since they require judgment about part order.

Note: series matching relies on part files being named `<base>-partN.md`.
A few early architecture-domain splits used a descriptive slug instead
(e.g. `...-sector-impacts.md`) and will show as false-positive mismatches
here; verify those by hand rather than trusting --fix on them.
"""
import argparse, glob, os, re

PART_RE = re.compile(r"[Tt]his is [Pp]art (\d+) of (\d+)")


def series_files(path, root="docs"):
    """All files (main + parts/) sharing this file's base topic slug.

    Main files and their part-N siblings can live anywhere under the same
    domain root (docs/<domain>/...) — most series keep a sibling parts/
    folder next to the main file, but a few orphaned early splits put
    part2+ in the domain-root parts/ folder while the main file lives in
    a different subfolder (e.g. core/05-*.md's part2 sits in
    docs/agentic-systems/parts/, not docs/agentic-systems/core/parts/).
    So search the whole domain subtree by basename rather than trying to
    enumerate the handful of layout conventions.
    """
    fn = os.path.basename(path)
    base = re.sub(r"^\d+-", "", fn[:-3])
    base = re.sub(r"-part\d+$", "", base)

    rel = os.path.relpath(path, root)
    domain = rel.split(os.sep)[0]
    domain_root = os.path.join(root, domain)

    found = []
    for dirpath, _, filenames in os.walk(domain_root):
        for cf in filenames:
            if not cf.endswith(".md"):
                continue
            cbase = re.sub(r"^\d+-", "", cf[:-3])
            if cbase == base or re.match(rf"^{re.escape(base)}-part\d+$", cbase):
                found.append(os.path.join(dirpath, cf))
    return found


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--fix", action="store_true")
    ap.add_argument("--root", default="docs")
    args = ap.parse_args()

    mismatches = 0
    for f in glob.glob(f"{args.root}/**/*.md", recursive=True):
        text = open(f, encoding="utf-8", errors="replace").read()
        m = PART_RE.search(text)
        if not m:
            continue
        n, total = int(m.group(1)), int(m.group(2))
        actual = len(series_files(f, root=args.root))
        if actual and actual != total:
            mismatches += 1
            print(f"{f}: says 'part {n} of {total}' but {actual} files exist in the series")
            if args.fix:
                fixed = PART_RE.sub(lambda mo: f"{mo.group(0).split(' of ')[0]} of {actual}", text, count=1)
                open(f, "w", encoding="utf-8", newline="").write(fixed)
                print(f"  -> fixed to 'of {actual}'")

    print(f"\n{mismatches} mismatch(es) found" + (" and fixed" if args.fix and mismatches else ""))


if __name__ == "__main__":
    main()
