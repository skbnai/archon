---
name: graphify
description: >
  Build and query a content graph of the entire docs/ corpus to power search
  and duplicate-topic detection at a depth the fast CI similarity gate can't
  reach. Use this whenever asked to find duplicate/overlapping topics
  repo-wide, find everything related to a page or concept, see which pages
  cover a given technology, or produce a visual/searchable map of the wiki.
  Complements dedup-canonicalization + scripts/dedup_check.py (which is a
  cheap per-PR shingle gate) with a full TF-IDF + graph pass across the whole
  corpus, five edge types, and an interactive HTML explorer. Run after any
  migration wave, bulk edit, or on the weekly schedule — a stale graph gives
  false confidence, so always rebuild before trusting a cluster report.
---

# Graphify — Corpus Graph, Search & Duplicate Detection

## Why this exists alongside dedup_check.py

`scripts/dedup_check.py` (shingle overlap) is the fast, deterministic PR gate —
it stops an obvious near-duplicate from merging. It is NOT a research tool: it
doesn't tell you which existing page a NEW topic idea is closest to, doesn't
surface technology coverage, and doesn't give you anything to look at. Graphify
is the deep-analysis counterpart: build once per wave/week, then query it
cheaply as many times as needed without re-scanning the corpus.

## 1. Build the graph

```bash
python3 .claude/skills/graphify/scripts/build_graph.py --sim-threshold 0.3
```

Reads every `docs/**/*.md` directly. Produces:

- **`_meta/graph.json`** — nodes (pages, concepts from `tags`, technologies from
  `governance/technology-taxonomy.json`) and five edge types:
  - `similar_to` — TF-IDF cosine similarity (the duplication signal itself)
  - `links_to` — real markdown links (the only explicit authorial signal)
  - `part_of` — sidebar hierarchy from `sidebars.js`
  - `tagged` — frontmatter `tags` → concept nodes
  - `mentions` — body-text scan against the technology taxonomy
- **`_meta/duplicate-clusters.md`** — connected components at ≥60% similarity,
  human-readable, every pairwise score shown, generated fresh every run.

Regenerate after every migration wave and every bulk edit. **A stale graph is
worse than no graph** — a cluster report from before content changed gives
false confidence.

## 2. Query it

```bash
python3 .claude/skills/graphify/scripts/query_graph.py --related <doc_id>     # strongest connections first
python3 .claude/skills/graphify/scripts/query_graph.py --concept <tag>        # pages tagged with a concept
python3 .claude/skills/graphify/scripts/query_graph.py --tool <name>          # pages mentioning a technology
python3 .claude/skills/graphify/scripts/query_graph.py --tool list           # all tools ranked by coverage
python3 .claude/skills/graphify/scripts/query_graph.py --duplicates --min 0.6 # every duplicate-candidate cluster
```

`doc_id` = the page's path under `docs/` without `.md` (matches `topic_id`
resolution and `sidebars.js` doc ids).

## 3. Before creating ANY new page (mandatory step, ties into dedup-canonicalization)

Before asking the librarian to register a new topic:

1. `query_graph.py --concept <candidate-topic>` and `--related` against the
   single closest existing page you can find by browsing the domain hub.
2. A `similar_to` edge ≥ 60% to something already in the graph is a **stronger**
   "this probably already exists" signal than folder/taxonomy placement alone —
   it's based on actual content overlap, not naming. Treat it the same as a
   registry hit: enhance/merge instead of creating new.
3. Same-directory high similarity is often a legitimate multi-part series —
   check the cluster's member list before treating every cluster as a problem.

## 4. Interactive exploration (search UI)

```bash
python3 .claude/skills/graphify/scripts/build_explorer.py
```

Generates `_meta/knowledge-graph-explorer.html` — a force-directed, D3-based
graph you open in a browser: search by title/tag/tool, filter by similarity
threshold and domain, toggle edge types. This is the fastest way for a human
(architect, reviewer, consultant) to actually see duplication and coverage
rather than read JSON. Regenerate any time `graph.json` changes.

## 5. Section indexes (cheap per-domain lookup, avoids re-reading the corpus)

```bash
python3 .claude/skills/graphify/scripts/build_section_indexes.py
```

Writes one `docs/<domain>/_index.json` per domain: title, doc_type, tags,
word count, last_reviewed, status, and each page's top-3 similar neighbors
(pulled from `graph.json`). Answer "what exists in this domain" by reading one
~5–10KB file instead of walking the whole tree — the token-efficiency skill's
manifest-over-corpus rule, applied at the domain level. Regenerate whenever a
domain's page set changes.

## Technology taxonomy

`governance/technology-taxonomy.json` is the registry of named tools/frameworks
(LLM providers, agent frameworks, protocols, cloud AI, vector DBs, etc.), each
with aliases compiled into a match pattern. Add new tools there and rebuild the
graph to refresh `mentions` edges — this is how "which pages cover LangGraph"
stays answerable without relying on authors remembering frontmatter tags.

## Interpreting `similar_to` correctly

High similarity **across different domains/folders** → likely duplication,
route to a merge plan (dedup-canonicalization skill). High similarity **within
the same series/folder** → often expected (sequential parts, sibling
sub-topics) — verify via the cluster member list, don't auto-merge.

## Requires

`scikit-learn`, `pyyaml`, Node.js (to evaluate `sidebars.js` for hierarchy).
