#!/usr/bin/env python3
"""Consolidated post-batch migration verifier.

One run replaces the ad hoc per-file sequence of validate_frontmatter.py /
wc -w / box-drawing grep / MDX-escape grep / link-resolution commands, and
emits a compact PASS/FAIL table (failures expanded) so the orchestrator
reads one report instead of raw per-command output.

Usage:
  python3 scripts/verify_migration_batch.py --wave 3
  python3 scripts/verify_migration_batch.py --pairs batch.csv
  python3 scripts/verify_migration_batch.py --wave 3 --batch-checks

--wave N       verify every MIGRATE row of that wave in migration/mapping.csv
--pairs FILE   CSV of old_path,new_path pairs (no header needed)
--old-root     old-repo root (default ../knowledge-docs)
--ratio-min    minimum output/source word ratio (default 0.90)
--batch-checks also run registry_check.py --domains, dedup_check.py --all,
               and the forbidden-filename scan (same battery as pre-push)
"""
import argparse, csv, os, re, subprocess, sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BOX = re.compile(r"[─-╿]")
FENCE = re.compile(r"^(```|~~~)")
BAD_LT = re.compile(r"<(?![A-Za-z/!])")
LINK = re.compile(r"\]\(([^)#\s]+\.md)")


def words(text):
    # Raw wc -w equivalent on both sides — do NOT strip code fences here:
    # sources and outputs must be counted identically, or pages that
    # correctly converted prose into mermaid/code blocks get false-low ratios.
    return len(text.split())


def read(path):
    with open(path, encoding="utf-8", errors="replace") as f:
        return f.read()


def strip_fences(text):
    """Yield (lineno, line) for lines outside fenced code blocks."""
    fenced = False
    for i, line in enumerate(text.splitlines(), 1):
        if FENCE.match(line.strip()):
            fenced = not fenced
            continue
        if not fenced:
            yield i, line


def part_files(new_path):
    """Find sibling part2/3 files sharing the target's base slug."""
    base = re.sub(r"^\d+-", "", os.path.splitext(os.path.basename(new_path))[0])
    d = os.path.dirname(new_path)
    found = []
    for pdir in (os.path.join(d, "parts"), os.path.join(os.path.dirname(d), "parts")):
        if os.path.isdir(pdir):
            for f in os.listdir(pdir):
                if re.match(rf"\d+-{re.escape(base)}-part\d+\.md$", f):
                    found.append(os.path.join(pdir, f))
    return found


def check_pair(old_path, new_path, old_root, ratio_min):
    errs = []
    src = os.path.join(old_root, old_path)
    if not os.path.isfile(new_path):
        return [f"target missing: {new_path}"], None
    text = read(new_path)

    # 1. frontmatter validator (reuse existing script)
    r = subprocess.run([sys.executable, os.path.join(REPO, "scripts", "validate_frontmatter.py"),
                        new_path], capture_output=True, text=True)
    if r.stdout.strip() != "OK":
        errs.append("frontmatter: " + (r.stdout + r.stderr).strip().replace("\n", "; "))

    # 2. word ratio vs source (parts summed)
    ratio = None
    if os.path.isfile(src):
        sw = words(read(src))
        nw = words(text) + sum(words(read(p)) for p in part_files(new_path))
        ratio = nw / sw if sw else 1.0
        if ratio < ratio_min:
            errs.append(f"word ratio {ratio:.2f} < {ratio_min} (src {sw}w -> {nw}w incl. parts)")
    else:
        errs.append(f"source not found: {src} (ratio unchecked)")

    # 3. box-drawing / ASCII art
    n = len(BOX.findall(text))
    if n:
        errs.append(f"{n} box-drawing char(s) — ASCII art not converted")

    # 4. MDX-unsafe '<' outside code fences
    bad = [(i, line.strip()[:80]) for i, line in strip_fences(text)
           if BAD_LT.search(line)]
    if bad:
        locs = ", ".join(str(i) for i, _ in bad[:8])
        errs.append(f"{len(bad)} MDX-unsafe '<' line(s): {locs}")

    # 5. relative .md links resolve on disk
    broken = []
    for i, line in strip_fences(text):
        for m in LINK.finditer(line):
            tgt = m.group(1)
            if tgt.startswith(("http://", "https://", "pathname://", "/")):
                continue
            if not os.path.isfile(os.path.normpath(os.path.join(os.path.dirname(new_path), tgt))):
                broken.append(f"L{i}:{tgt}")
    if broken:
        errs.append(f"{len(broken)} broken relative link(s): " + ", ".join(broken[:6]))

    return errs, ratio


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--wave", type=int)
    ap.add_argument("--pairs")
    ap.add_argument("--old-root", default=os.path.join(REPO, "..", "knowledge-docs"))
    ap.add_argument("--ratio-min", type=float, default=0.90)
    ap.add_argument("--batch-checks", action="store_true")
    args = ap.parse_args()
    os.chdir(REPO)

    pairs, domains = [], set()
    if args.wave:
        with open("migration/mapping.csv", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                if row["wave"] == str(args.wave) and row["disposition"] == "MIGRATE":
                    pairs.append((row["old_path"], row["target_path"]))
                    m = re.match(r"docs/([a-z-]+)/", row["target_path"])
                    if m:
                        domains.add(m.group(1))
    elif args.pairs:
        with open(args.pairs, encoding="utf-8") as f:
            for row in csv.reader(f):
                if len(row) >= 2 and row[1].endswith(".md"):
                    pairs.append((row[0].strip(), row[1].strip()))
                    m = re.match(r"docs/([a-z-]+)/", row[1].strip())
                    if m:
                        domains.add(m.group(1))
    else:
        ap.error("need --wave or --pairs")

    fails = 0
    for old, new in pairs:
        errs, _ = check_pair(old, new, args.old_root, args.ratio_min)
        if errs:
            fails += 1
            print(f"FAIL {new}")
            for e in errs:
                print(f"     - {e}")
    print(f"\nper-file: {len(pairs) - fails}/{len(pairs)} PASS, {fails} FAIL "
          f"(ratio_min={args.ratio_min})")

    batch_fail = 0
    if args.batch_checks:
        if domains:
            r = subprocess.run([sys.executable, "scripts/registry_check.py",
                                "--domains", ",".join(sorted(domains))])
            batch_fail |= r.returncode
        r = subprocess.run([sys.executable, "scripts/dedup_check.py", "--all", "0.55"])
        batch_fail |= r.returncode
        bad_names = []
        for root, _, files in os.walk("docs"):
            for f in files:
                if re.search(r"_v\d|_final|_copy|-old|_new", f):
                    bad_names.append(os.path.join(root, f))
        if bad_names:
            print("FAIL forbidden filenames: " + ", ".join(bad_names))
            batch_fail = 1

    sys.exit(1 if (fails or batch_fail) else 0)


if __name__ == "__main__":
    main()
