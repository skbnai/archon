---
name: diagram-standards
description: >
  Use whenever a page describes an architecture, flow, topology, sequence, or
  lifecycle. Converts prose/ASCII descriptions into versioned Mermaid diagrams
  with C4-style conventions. Also use during migration when old pages contain
  ASCII art or broken converted-PDF layout tables.
---

# Diagram Standards

- All diagrams are Mermaid in fenced ```mermaid blocks — versioned & diffable.
  Never binary images for architecture; never ASCII art.
- Vocabulary:
  - System context / containers → `graph TB` with C4 conventions
    (Person, System, Container; boundaries as subgraphs).
  - Interactions over time (agent↔tool↔MCP↔model) → `sequenceDiagram`.
  - Lifecycles/state (agent runtime, doc status) → `stateDiagram-v2`.
  - Decision guidance → `flowchart` with diamond decision nodes.
- One idea per diagram; ≤ ~15 nodes. Split rather than cram.
- Every diagram: a title line and a 1–2 sentence caption below it.
- Label edges with protocol/artifact (e.g., `-- MCP tools/call -->`),
  not vague arrows.
- Migration duty: when a source page contains ASCII layouts or converted-PDF
  table-diagrams, REPLACE them with Mermaid; do not carry them over.

## Mandatory verification (do not skip — this rule has been ignored before)

"No ASCII art" is not satisfied by eyeballing the page. Before marking any
migrated/written file done, run:

```
grep -cP '[\x{2500}-\x{257F}]' path/to/file.md
```

The count MUST be 0. If it isn't, convert what's left — including small
"minor" trees, org-charts, or phase/step sequences using `├── └── │ → ↓`.
There is no size or complexity exception: a 4-node tree gets the same
Mermaid treatment as a 15-node one (split it if it's actually >15 nodes).
"Not a real diagram, just an indented list" is not a valid reason to keep
box-drawing characters — convert it to a small `graph TD` instead.
