#!/usr/bin/env python3
"""Propose N-way source line-range splits at heading boundaries.

Migrator dispatches require exact source line-ranges (see migration/README.md).
For sources that must split into multiple parts, this proposes boundaries at
H2 (fallback H3/H1) headings that balance word counts across parts, so plan
authors don't hand-count lines.

Usage: python3 scripts/propose_split_ranges.py <source.md> <num_parts>
Prints one `lines N-M (~W words, starts at: <heading>)` per part.
"""
import re, sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def main(path, n):
    lines = open(path, encoding="utf-8", errors="replace").read().splitlines()
    total = sum(len(l.split()) for l in lines)
    # candidate boundaries: heading lines outside code fences
    fenced = False
    heads = []  # (lineno_1idx, words_before, text)
    wsum = 0
    for i, l in enumerate(lines, 1):
        if l.strip().startswith(("```", "~~~")):
            fenced = not fenced
        if not fenced and re.match(r"^#{1,3} ", l):
            heads.append((i, wsum, l.strip()))
        wsum += len(l.split())
    if not heads:
        print(f"no headings found; single range: lines 1-{len(lines)} (~{total} words)")
        return
    # pick n-1 boundaries closest to equal word fractions, preferring H2
    bounds = []
    for k in range(1, n):
        target = total * k / n
        # prefer H2 within 15% of total words of target, else any heading
        h2 = [h for h in heads if h[2].startswith("## ")]
        pool = [h for h in (h2 or heads) if abs(h[1] - target) <= total * 0.15] or (h2 or heads)
        best = min(pool, key=lambda h: abs(h[1] - target))
        if best[0] not in [b[0] for b in bounds] and best[0] > 1:
            bounds.append(best)
    bounds = sorted(set(bounds))
    starts = [1] + [b[0] for b in bounds]
    ends = [b[0] - 1 for b in bounds] + [len(lines)]
    for idx, (s, e) in enumerate(zip(starts, ends), 1):
        w = sum(len(l.split()) for l in lines[s - 1:e])
        label = next((h[2] for h in heads if h[0] == s), "(file start)")
        print(f"part{idx}: lines {s}-{e} (~{w} words, starts at: {label[:70]})")


if __name__ == "__main__":
    main(sys.argv[1], int(sys.argv[2]))
