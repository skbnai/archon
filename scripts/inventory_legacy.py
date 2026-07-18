#!/usr/bin/env python3
"""Stage-01 inventory of the old knowledge-docs repo.

Walks <root>/docs/**/*.md, extracts lightweight metadata (no content
rewriting), infers a governance/DOC_TYPES.md doc_type via filename/heading
heuristics, and clusters near-duplicates via shingle-jaccard similarity
(logic mirrors scripts/dedup_check.py, but at a looser threshold suited to
casting a wide net for merge-plan review).

Usage: inventory_legacy.py [--root ../knowledge-docs-old] [--threshold 0.45]
                            [--out migration/inventory.csv]
"""
import argparse
import csv
import itertools
import re
import sys
from pathlib import Path

FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---\n", re.S)
MERMAID_RE = re.compile(r"^```mermaid\b", re.M | re.I)
BOX_CHAR_RE = re.compile(r"[─-╿▀-▟■-◿]")
ASCII_BOX_LINE_RE = re.compile(r"^\s*\+[-=+]{3,}\+\s*$", re.M)
H1_RE = re.compile(r"^#\s+(.+)$", re.M)

PART_VOL_RE = re.compile(r"(?i)(?:^|[_\-])(?:part|vol)[_\-]?\d+")
RESEARCH_KEYWORDS = ("report", "research", "study", "whitepaper", "assessment", "deep_dive", "deep-dive")
ANTI_PATTERN_RE = re.compile(r"(?i)anti[_-]?pattern")
REFERENCE_ARCH_RE = re.compile(r"(?i)reference[_-]?architecture")
QUESTION_MARK_DENSITY_MIN = 8
CITATION_MARKER_RE = re.compile(r"(?i)\b(?:VERIFIED|INFERRED)\b\s*[—:-]")
CITATION_MARKER_MIN = 5

# old-repo doc_type (their taxonomy) -> governance/DOC_TYPES.md fallback
OLD_DOC_TYPE_FALLBACK = {
    "guide": "guide",
    "multi-part-series": "guide",
    "research-report": "research-report",
    "interview-questions": "career",
    "workshop-transcript": "guide",
    "handbook-volume": "guide",
    "certification": "checklist",
    "narrative-case-study": "case-study",
    "architecture-whitepaper": "research-report",
    "research-guide": "research-report",
    "reference": "concept",
    "study-guide": "guide",
    "research-series-index": "hub",
    "research": "research-report",
    "handbook-index": "hub",
    "architecture-guide": "guide",
}

KNOWN_DUP_FAMILIES = [
    (re.compile(r"(?i)ai[_-]?agent[_-]?evaluation[_-]?framework|evaluation-framework"), "known-dup:eval-framework"),
    (re.compile(r"(?i)eu[_-]?bank"), "known-dup:eu-bank-copilot"),
    (re.compile(r"(?i)aidlc_artifact_reference_library"), "known-dup:aidlc-artifact-library"),
    (re.compile(r"(?i)mental_model"), "known-dup:mental-models-encyclopedia"),
    (re.compile(r"(?i)apex_ea_final"), "known-dup:apex-ea"),
    (re.compile(r"(?i)enterprise_ai_architect_deep_dive"), "known-dup:ea-deep-dive"),
]

QUANTUM_ZERO_TO_MASTERY_RE = re.compile(r"(?i)zero[_-]?to[_-]?mastery")

TOPIC_OVERLAP_KEYWORDS = [
    (re.compile(r"(?i)security"), "topic-overlap:security"),
    (re.compile(r"(?i)finops"), "topic-overlap:finops"),
    (re.compile(r"(?i)\bmcp\b"), "topic-overlap:mcp"),
    (re.compile(r"(?i)memory"), "topic-overlap:memory"),
    (re.compile(r"(?i)observab"), "topic-overlap:observability"),
    (re.compile(r"(?i)anti[_-]?pattern"), "topic-overlap:anti-patterns"),
    (re.compile(r"(?i)glossary"), "topic-overlap:glossaries"),
    (re.compile(r"(?i)interview|questionnaire"), "topic-overlap:interview-content"),
]

CONVERTED_SOURCE_TYPES = {"converted-pdf", "pdf-converted", "converted-html", "converted-docx"}


def parse_frontmatter(text):
    m = FRONTMATTER_RE.match(text)
    if not m:
        return {}, text
    fm_text = m.group(1)
    body = text[m.end():]
    fm = {}
    for line in fm_text.splitlines():
        line = line.rstrip()
        km = re.match(r'^([A-Za-z_][A-Za-z0-9_]*):\s*(.*)$', line)
        if not km:
            continue
        key, val = km.group(1), km.group(2).strip()
        val = val.strip('"').strip("'")
        if key not in fm:  # first occurrence wins (top-level scalar keys)
            fm[key] = val
    return fm, body


def infer_title(fm, body, stem):
    if fm.get("title"):
        return fm["title"]
    hm = H1_RE.search(body)
    if hm:
        return hm.group(1).strip()
    return stem.replace("_", " ").replace("-", " ")


def infer_doc_type(rel_path, stem, fm, body):
    low_path = rel_path.lower()
    low_stem = stem.lower()

    if low_stem == "index":
        return "hub"
    if "template" in low_path:
        return "template-asset"
    if "cheatsheet" in low_stem:
        return "checklist"
    if low_stem.startswith("case_") or "case-study" in low_path or "case_study" in low_stem:
        return "case-study"
    if ANTI_PATTERN_RE.search(low_stem):
        return "anti-pattern"
    if REFERENCE_ARCH_RE.search(low_stem):
        return "reference-architecture"
    if "question" in low_stem:
        return "career"
    if "interview" in low_path and body.count("?") >= QUESTION_MARK_DENSITY_MIN:
        return "career"

    heavily_cited = len(CITATION_MARKER_RE.findall(body)) >= CITATION_MARKER_MIN

    if PART_VOL_RE.search(stem):
        if any(k in low_path for k in RESEARCH_KEYWORDS) or heavily_cited:
            return "research-report"
        return "guide"
    if heavily_cited:
        return "research-report"

    old_type = fm.get("doc_type", "").lower()
    return OLD_DOC_TYPE_FALLBACK.get(old_type, "guide")


def build_notes(rel_path, stem):
    notes = []
    for regex, tag in KNOWN_DUP_FAMILIES:
        if regex.search(stem) or regex.search(rel_path):
            notes.append(tag)
    if "quantum" in rel_path.lower() and QUANTUM_ZERO_TO_MASTERY_RE.search(stem):
        notes.append("known-dup:quantum-zero-to-mastery")
    for regex, tag in TOPIC_OVERLAP_KEYWORDS:
        if regex.search(rel_path):
            notes.append(tag)
    return ";".join(dict.fromkeys(notes))  # dedupe, keep order


def shingles(body, k=8):
    words = re.findall(r"[a-z0-9]+", body.lower())
    return {" ".join(words[i:i + k]) for i in range(max(0, len(words) - k + 1))}


def jaccard(a, b):
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


class UnionFind:
    def __init__(self, n):
        self.parent = list(range(n))

    def find(self, x):
        while self.parent[x] != x:
            self.parent[x] = self.parent[self.parent[x]]
            x = self.parent[x]
        return x

    def union(self, a, b):
        ra, rb = self.find(a), self.find(b)
        if ra != rb:
            self.parent[ra] = rb


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default="../knowledge-docs-old")
    ap.add_argument("--threshold", type=float, default=0.45)
    ap.add_argument("--out", default="migration/inventory.csv")
    args = ap.parse_args()

    root = Path(args.root)
    docs_root = root / "docs"
    if not docs_root.is_dir():
        print(f"error: {docs_root} not found", file=sys.stderr)
        sys.exit(1)

    files = sorted(docs_root.rglob("*.md"))
    rows = []
    shingle_sets = []

    for f in files:
        rel_path = f.relative_to(root).as_posix()  # e.g. docs/foo/bar.md
        parts = f.relative_to(docs_root).parts
        old_section = parts[0] if len(parts) > 1 else "root"
        stem = f.stem

        raw = f.read_text(encoding="utf-8", errors="ignore")
        fm, body = parse_frontmatter(raw)
        has_frontmatter = bool(fm) or bool(FRONTMATTER_RE.match(raw))

        words = len(re.findall(r"\S+", body))
        title = infer_title(fm, body, stem)
        last_reviewed = fm.get("last_reviewed", "")
        source_type = fm.get("source_type", "")
        status_field = fm.get("status", "")
        mermaid_count = len(MERMAID_RE.findall(body))

        ascii_art_suspected = bool(
            BOX_CHAR_RE.search(body) or ASCII_BOX_LINE_RE.search(body)
        )

        inferred_doc_type = infer_doc_type(rel_path, stem, fm, body)
        notes = build_notes(rel_path, stem)

        rows.append({
            "old_path": rel_path,
            "old_section": old_section,
            "title": title,
            "words": words,
            "has_frontmatter": has_frontmatter,
            "last_reviewed": last_reviewed,
            "source_type": source_type,
            "status_field": status_field,
            "mermaid_count": mermaid_count,
            "ascii_art_suspected": ascii_art_suspected,
            "inferred_doc_type": inferred_doc_type,
            "dup_cluster": "",
            "notes": notes,
        })
        shingle_sets.append(shingles(body))

    # --- pairwise shingle clustering ---
    n = len(rows)
    sizes = [len(s) for s in shingle_sets]
    uf = UnionFind(n)
    pair_count = 0
    for i, j in itertools.combinations(range(n), 2):
        si, sj = sizes[i], sizes[j]
        if si == 0 or sj == 0:
            continue
        bound = min(si, sj) / max(si, sj)
        if bound < args.threshold:
            continue
        sim = jaccard(shingle_sets[i], shingle_sets[j])
        if sim >= args.threshold:
            uf.union(i, j)
            pair_count += 1

    groups = {}
    for idx in range(n):
        root_idx = uf.find(idx)
        groups.setdefault(root_idx, []).append(idx)

    clusters = [members for members in groups.values() if len(members) > 1]
    clusters.sort(key=lambda m: -len(m))
    for cluster_no, members in enumerate(clusters, start=1):
        cid = f"cluster-{cluster_no:03d}"
        for idx in members:
            rows[idx]["dup_cluster"] = cid

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = ["old_path", "old_section", "title", "words", "has_frontmatter",
                  "last_reviewed", "source_type", "status_field", "mermaid_count",
                  "ascii_art_suspected", "inferred_doc_type", "dup_cluster", "notes"]
    with out_path.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)

    print(f"scanned {n} files, {pair_count} pair(s) >= {args.threshold} jaccard, "
          f"{len(clusters)} cluster(s) -> {out_path}")


if __name__ == "__main__":
    main()
