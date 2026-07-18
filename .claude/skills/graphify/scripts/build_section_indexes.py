#!/usr/bin/env python3
"""
Generate one lightweight index file per top-level docs/ domain:
    docs/<domain>/_index.json

Each index lists every page in that domain with just enough metadata to
decide "do I need to open this file" without opening it: title, doc_type,
topic_id, status, tags, word count, last_reviewed, and its 3 nearest
neighbors by content similarity (pulled from _meta/graph.json if present).

This is the concrete version of the token-efficiency skill's "manifests over
corpus" rule at domain scope: instead of an agent walking every file in
docs/ (or grepping the whole tree) to answer "what already exists about X",
it reads one ~5-10KB file for the relevant domain.

Usage:
    python3 build_section_indexes.py [--docs-dir docs] [--graph _meta/graph.json]

Regenerate whenever pages are added/removed/retitled in a domain — cheap
enough (one domain's worth of file reads) to do after every migration wave
or content-refresh PR that touches that domain, not just on a schedule.
"""
import os
import re
import sys
import json
import argparse

FM_RE = re.compile(r"^---\n(.*?)\n---\n", re.DOTALL)

try:
    import yaml
except ImportError:
    yaml = None


def parse_frontmatter(text):
    m = FM_RE.match(text)
    if not m:
        return {}
    if yaml:
        try:
            return yaml.safe_load(m.group(1)) or {}
        except Exception:
            return {}
    return {}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--docs-dir", default="docs")
    ap.add_argument("--graph", default="_meta/graph.json",
                     help="If present, used to attach each page's top-3 similar "
                          "pages by content — skipped (with a warning) if missing "
                          "or stale relative to the docs tree.")
    args = ap.parse_args()

    neighbors = {}
    if os.path.exists(args.graph):
        graph_mtime = os.path.getmtime(args.graph)
        newest_doc_mtime = max(
            (os.path.getmtime(os.path.join(r, f))
             for r, _d, files in os.walk(args.docs_dir) for f in files if f.endswith(".md")),
            default=0)
        if newest_doc_mtime > graph_mtime:
            print(f"WARNING: {args.graph} is older than the newest page in {args.docs_dir}/ — "
                  f"neighbor data in the generated indexes will be stale. Re-run "
                  f"graphify's build_graph.py first for accurate neighbors.",
                  file=sys.stderr)
        graph = json.load(open(args.graph, encoding="utf-8"))
        sim_by_page = {}
        for e in graph["edges"]:
            if e["type"] != "similar_to":
                continue
            sim_by_page.setdefault(e["source"], []).append((e["target"], e["weight"]))
            sim_by_page.setdefault(e["target"], []).append((e["source"], e["weight"]))
        for page, sims in sim_by_page.items():
            sims.sort(key=lambda x: -x[1])
            neighbors[page] = sims[:3]
    else:
        print(f"No {args.graph} found — indexes will omit neighbor data. Run "
              f"graphify's build_graph.py first for the full index.",
              file=sys.stderr)

    domains = [d for d in os.listdir(args.docs_dir)
               if os.path.isdir(os.path.join(args.docs_dir, d))]

    total_written = 0
    for domain in sorted(domains):
        domain_dir = os.path.join(args.docs_dir, domain)
        entries = []
        for r, _d, files in os.walk(domain_dir):
            for f in files:
                if not f.endswith(".md"):
                    continue
                full = os.path.join(r, f)
                doc_id = os.path.relpath(full, args.docs_dir)[:-3].replace(os.sep, "/")
                text = open(full, encoding="utf-8", errors="replace").read()
                fm = parse_frontmatter(text)
                body = FM_RE.sub("", text, count=1)
                entries.append({
                    "id": doc_id,
                    "title": fm.get("title", doc_id),
                    "doc_type": fm.get("doc_type", "unknown"),
                    "topic_id": fm.get("topic_id", ""),
                    "tags": fm.get("tags") or [],
                    "word_count": len(body.split()),
                    "last_reviewed": str(fm.get("last_reviewed", "")),
                    "status": fm.get("status", ""),
                    "top_similar": [{"id": n, "score": round(s, 2)} for n, s in neighbors.get(doc_id, [])],
                })

        if not entries:
            continue

        index = {
            "domain": domain,
            "page_count": len(entries),
            "pages": sorted(entries, key=lambda e: e["id"]),
        }
        out_path = os.path.join(domain_dir, "_index.json")
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(index, f, indent=1)
        total_written += 1

    print(f"Wrote {total_written} domain index file(s) under {args.docs_dir}/*/_index.json")


if __name__ == "__main__":
    main()
