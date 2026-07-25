#!/usr/bin/env python3
"""
Query the graph built by build_graph.py. Five modes:

  --related <doc_id>     Every page connected to this one, by edge type,
                          strongest first. Answers "what else touches this
                          topic" and "is this a duplicate of something."

  --concept <tag>         Every page tagged with this concept (frontmatter).

  --tool <name>           Every page that mentions this technology or
                          framework in its body text. Fuzzy-matches on tool
                          name/id. Also supports --tool list to show all tool
                          nodes and page counts sorted by coverage.

  --topic <topic_id>      Resolve a governance/CANONICAL_REGISTRY.yaml
                          topic_id straight to its page and show what's
                          connected to it — the fastest "does this already
                          exist, and what's around it" check before
                          registering a new topic.

  --duplicates [--min 0.6]
                          All duplicate-candidate clusters at or above the
                          given similarity, most severe first.

Usage:
    python3 query_graph.py --related architecture/02-agent-topologies
    python3 query_graph.py --concept kubernetes
    python3 query_graph.py --tool langgraph
    python3 query_graph.py --tool list
    python3 query_graph.py --topic mcp-security
    python3 query_graph.py --duplicates --min 0.6
"""
import json
import argparse
import os
from collections import defaultdict

try:
    import yaml
except ImportError:
    yaml = None

DEDUP_EXCEPTIONS_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "..",
    "governance", "DEDUP_EXCEPTIONS.yaml",
)


def load(path):
    return json.load(open(path, encoding="utf-8"))


def load_dedup_exceptions(path=DEDUP_EXCEPTIONS_PATH):
    """Manually-reviewed similar_to pairs to exclude from --duplicates.
    See governance/DEDUP_EXCEPTIONS.yaml for the review criteria."""
    if yaml is None or not os.path.isfile(path):
        return set()
    data = yaml.safe_load(open(path, encoding="utf-8")) or {}
    pairs = set()
    for entry in data.get("exceptions", []) or []:
        pair = entry.get("pair") or []
        if len(pair) == 2:
            pairs.add(frozenset(pair))
    return pairs


def cmd_related(graph, doc_id, top):
    titles = {n["id"]: n.get("title", n["id"]) for n in graph["nodes"]}
    if doc_id not in titles:
        print(f"'{doc_id}' not found in graph. Use the doc_id form: 'domain/NN-slug' (no .md).")
        return
    hits = []
    for e in graph["edges"]:
        if e["source"] == doc_id:
            hits.append((e["target"], e["type"], e.get("tier", ""), e["weight"]))
        elif e["target"] == doc_id and e["type"] != "tagged":
            hits.append((e["source"], e["type"], e.get("tier", ""), e["weight"]))
    hits.sort(key=lambda h: -h[3])
    print(f"'{doc_id}' — {titles[doc_id]}\n")
    for target, etype, tier, weight in hits[:top]:
        label = titles.get(target, target)
        tag = f" [{tier}]" if tier else ""
        print(f"  {weight:.0%}  {etype:10s}{tag}  {target}  — {label}")
    if not hits:
        print("  No connections found above the graph's similarity threshold.")


def cmd_concept(graph, concept):
    concept_id = f"concept:{concept}"
    titles = {n["id"]: n.get("title", n["id"]) for n in graph["nodes"]}
    pages = [e["source"] for e in graph["edges"]
             if e["type"] == "tagged" and e["target"] == concept_id]
    if not pages:
        matches = [n["id"] for n in graph["nodes"]
                   if n["type"] == "concept" and concept.lower() in n["id"].lower()]
        if matches:
            print(f"No exact tag '{concept}'. Did you mean: "
                  f"{', '.join(m.replace('concept:', '') for m in matches[:10])}?")
        else:
            print(f"No pages or concepts matching '{concept}'.")
        return
    print(f"Pages tagged '{concept}' ({len(pages)}):\n")
    for p in pages:
        print(f"  {p}  — {titles.get(p, p)}")


def cmd_tool(graph, tool_query):
    """Find pages that mention a tool. 'list' shows all tools by coverage."""
    tool_nodes = {n["id"]: n for n in graph["nodes"] if n["type"] == "tool"}
    titles = {n["id"]: n.get("title", n["id"]) for n in graph["nodes"]}

    if tool_query.lower() == "list":
        counts = defaultdict(int)
        for e in graph["edges"]:
            if e["type"] == "mentions":
                counts[e["target"]] += 1
        ranked = sorted(tool_nodes.items(), key=lambda kv: -counts.get(kv[0], 0))
        print(f"Tools in graph ({len(tool_nodes)} total), by page coverage:\n")
        for tid, tnode in ranked:
            cat = tnode.get("category", "")
            name = tnode.get("name", tid)
            print(f"  {counts.get(tid, 0):4d} pages  [{cat:18s}]  {name}")
        return

    query_norm = tool_query.lower().replace("-", "").replace(" ", "")
    matches = [
        (tid, tnode) for tid, tnode in tool_nodes.items()
        if query_norm in tid.lower().replace("-", "").replace(":", "")
        or query_norm in tnode.get("name", "").lower().replace("-", "").replace(" ", "")
    ]
    if not matches:
        all_names = [n.get("name", n["id"]) for n in tool_nodes.values()]
        print(f"No tool matching '{tool_query}'. Available: {', '.join(sorted(all_names))}")
        return

    for tid, tnode in matches:
        pages = [e["source"] for e in graph["edges"]
                 if e["type"] == "mentions" and e["target"] == tid]
        cat = tnode.get("category", "")
        desc = tnode.get("description", "")
        print(f"Tool: {tnode.get('name', tid)}  [{cat}]")
        if desc:
            print(f"      {desc}")
        print(f"      {len(pages)} page(s) mention this tool:\n")
        by_domain = defaultdict(list)
        for p in sorted(pages):
            domain = p.split("/")[0]
            by_domain[domain].append(p)
        for domain in sorted(by_domain):
            print(f"  {domain}/")
            for p in by_domain[domain]:
                print(f"    {p}  — {titles.get(p, p)}")
        print()


def cmd_topic(graph, topic_id):
    """Resolve a registry topic_id to its page and show connections."""
    matches = [n for n in graph["nodes"]
               if n.get("type") == "page" and n.get("topic_id") == topic_id]
    if not matches:
        fuzzy = [n for n in graph["nodes"]
                 if n.get("type") == "page" and topic_id.lower() in (n.get("topic_id") or "").lower()]
        if fuzzy:
            print(f"No exact topic_id '{topic_id}'. Did you mean: "
                  f"{', '.join(n['topic_id'] for n in fuzzy[:10])}?")
        else:
            print(f"No page with topic_id '{topic_id}' in the graph. "
                  f"If this is a genuinely new topic, register it via the librarian "
                  f"agent before writing — don't rely on this being empty as sole proof "
                  f"nothing similar exists; also check --related against the nearest hub page.")
        return
    for n in matches:
        print(f"topic_id '{topic_id}' -> {n['id']}  ({n.get('status','')})  — {n.get('title', n['id'])}\n")
        cmd_related(graph, n["id"], top=15)
        print()


def cmd_duplicates(graph, min_sim):
    exceptions = load_dedup_exceptions()
    edges = [
        e for e in graph["edges"]
        if e["type"] == "similar_to" and e["weight"] >= min_sim
        and frozenset((e["source"], e["target"])) not in exceptions
    ]
    parent = {}

    def find(x):
        parent.setdefault(x, x)
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(a, b):
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[ra] = rb

    for e in edges:
        union(e["source"], e["target"])

    clusters = defaultdict(set)
    for e in edges:
        clusters[find(e["source"])].add(e["source"])
        clusters[find(e["target"])].add(e["target"])

    titles = {n["id"]: n.get("title", n["id"]) for n in graph["nodes"]}
    domains = {n["id"]: n.get("domain", "") for n in graph["nodes"]}
    ranked = sorted(clusters.values(), key=lambda members: -max(
        (e["weight"] for e in edges if e["source"] in members and e["target"] in members),
        default=0))

    if exceptions:
        print(f"({len(exceptions)} manually-reviewed pair(s) suppressed via governance/DEDUP_EXCEPTIONS.yaml)\n")
    print(f"{len(ranked)} duplicate-candidate cluster(s) at >= {min_sim:.0%} similarity:\n")
    for members in ranked:
        cross_domain = len({domains.get(m, "") for m in members}) > 1
        flag = " [CROSS-DOMAIN — likely real duplication]" if cross_domain else " [same domain — check if series]"
        print(f"Cluster ({len(members)} pages){flag}:")
        for m in sorted(members):
            print(f"  {m}  — {titles.get(m, m)}")
        print()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--graph", default="_meta/graph.json")
    ap.add_argument("--related", metavar="DOC_ID")
    ap.add_argument("--concept", metavar="TAG")
    ap.add_argument("--tool", metavar="NAME_OR_list",
                     help="Find pages mentioning this tool, or 'list' to show all tools")
    ap.add_argument("--topic", metavar="TOPIC_ID", help="Resolve a registry topic_id in the graph")
    ap.add_argument("--duplicates", action="store_true")
    ap.add_argument("--min", type=float, default=0.6, help="Min similarity for --duplicates")
    ap.add_argument("--top", type=int, default=15, help="Max results for --related")
    args = ap.parse_args()

    graph = load(args.graph)

    if args.related:
        cmd_related(graph, args.related, args.top)
    elif args.concept:
        cmd_concept(graph, args.concept)
    elif args.tool:
        cmd_tool(graph, args.tool)
    elif args.topic:
        cmd_topic(graph, args.topic)
    elif args.duplicates:
        cmd_duplicates(graph, args.min)
    else:
        print("Specify one of --related, --concept, --tool, --topic, or --duplicates.")


if __name__ == "__main__":
    main()
