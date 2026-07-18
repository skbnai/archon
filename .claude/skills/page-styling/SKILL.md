---
name: page-styling
description: >
  Use whenever writing, migrating, or polishing any wiki page — or the sidebar
  itself — so it reads and renders at professional publication grade. Covers
  voice, heading structure, tables, metric/stat callouts, buttons/CTAs, and
  Docusaurus/MDX presentation components (admonitions, tabs, cards, collapsible
  sections), plus sidebar.js authoring standards. Apply together with
  doc-standards (which governs frontmatter/types) — doc-standards decides WHAT
  the page is, this skill decides HOW it and the surrounding navigation read
  and look. Component snippets: ./components-reference.md (load only when
  needed). Full sidebar spec: governance/SIDEBAR_GUIDE.md.
---

# Professional Page Styling

## Voice & tone

- Write like a distinguished architect briefing a peer: confident, precise,
  prescriptive. Prefer "Route pricing to a deterministic engine; the agent
  orchestrates it" over "it may be advisable to consider…".
- Active voice, present tense, second person for guides ("you configure…").
- No hype words (revolutionary, game-changing, cutting-edge), no filler
  ("in today's fast-paced world"), no emoji in body text.
- One idea per paragraph; paragraphs ≤ 4 sentences. Sentences ≤ 25 words on
  average.
- Define an acronym at first use per page, then use the acronym.

## Page opening (every page, all types)

1. H1 = frontmatter title (Docusaurus renders it; don't duplicate).
2. First paragraph = the "so what": what this page covers and why the reader
   cares — 2–3 sentences, no heading above it.
3. For guide/runbook/reference-architecture: a `:::info At a glance` admonition
   with 3–5 bullets (scope, prerequisites, outcome, covers_version if set).

## Structure & scannability

- Heading depth ≤ H3. Headings are descriptive claims where possible
  ("Stateless transports break sampling" beats "Transport considerations").
- A reader skimming only headings + admonitions must get the argument.
- Tables for comparisons (≥3 items × ≥2 attributes); prose for reasoning.
  Never use tables for page layout.
- Lists only when order or enumeration matters; 3–7 items; parallel grammar.
- Bold for key terms at first definition only — never for whole sentences.

## Docusaurus components — when to use what

| Component | Use for | Rule |
|---|---|---|
| `:::note` | Context worth knowing | ≤ 2 per page |
| `:::tip` | Practitioner shortcut | ≤ 2 per page |
| `:::warning` | Foot-guns, breaking changes | Whenever one exists |
| `:::danger` | Irreversible/security-critical | Sparingly; never decorative |
| `Tabs` | Same task, per-cloud/per-language variants | Tab labels = product names |
| `<details>` | Long optional material (full configs, transcripts) | Summary line must say what's inside |
| Code blocks | Always with language + `title="filename"` when it's a file | Runnable or clearly marked pseudo |

Total admonitions ≤ 5 per page — more means the body is disorganized.
Exact snippets: see ./components-reference.md.

## Visual rhythm

- Something non-prose (diagram, table, admonition, code) at least every
  ~500 words; never two identical component types back-to-back.
- Mermaid per diagram-standards skill; caption line under every diagram.
- Section separators: headings only, never `---` rules inside a page body.

## Page closing (in order)

1. `## Related` — 2–5 canonical links with a 3–6 word reason each
   ("— threat model behind these controls").
2. `## Sources` — per research-grounding, when the page carries grounded claims.
Never end on an admonition or a bare table.

## Tables

- Use for comparisons (≥3 items × ≥2 attributes) — never for page layout or
  to fake a diagram.
- ≤ 6 columns; if more, split into two tables or switch to prose. Header
  row in Title Case; body cells sentence case.
- Right-align numeric/metric columns (Docusaurus/MDX tables support
  `:---:`/`---:` alignment markers) so figures scan vertically.
- One measurable claim per cell — no bundled "12 (up from 8, +50%)"; put the
  delta in its own column instead.
- Every table needs a one-line takeaway sentence immediately after it — a
  table alone doesn't argue a point.

## Metrics & stat callouts

Use a stat row for headline numbers a reader should absorb in one glance
(maturity scores, coverage %, SLA figures, cost deltas) — not for routine
data that belongs in a table.

```mdx
<div className="stat-row">
  <div className="stat"><span className="stat-value">5.5/10</span><span className="stat-label">Platform maturity</span></div>
  <div className="stat"><span className="stat-value">33/40</span><span className="stat-label">Lifecycle domains covered</span></div>
</div>
```
(CSS in `src/css/custom.css` — see `governance/DOCUSAURUS_SETUP.md`.)

Rules: 2–4 stats per row, never more (it stops being scannable); every stat
must be sourced (grounded number, not a vibe); pair each with a ≤4-word label,
not a full sentence.

## Buttons & calls-to-action

MDX has no native button; use a styled link, sparingly — one primary CTA per
page maximum (e.g., hub pages linking to a flagship asset or learning path).

```mdx
<a className="button button--primary button--lg" href="/learning-paths/solution-architect">
  Start the Solution Architect path →
</a>
```

Don't use buttons for ordinary in-body navigation — that's what inline links
and the Related section are for. Reserve buttons for hub/landing pages and
the homepage persona tiles.

## Sidebar (`sidebars.js`)

Governed by `governance/SIDEBAR_GUIDE.md` — read it before editing
`sidebars.js`. Summary:
- Sidebar structure mirrors `governance/TAXONOMY.md` domains exactly — one
  top-level category per domain, in the fixed order given there. Never let
  the sidebar and the taxonomy drift apart.
- Curate manually (explicit `items` lists in reading order) for every
  published category; `autogenerated` is allowed only inside `migration/`
  staging, never in a domain a reader will see.
- Category `label` = domain display name from TAXONOMY.md; `link.type: doc`
  points at that domain's hub `index.md` so clicking the category itself
  is useful, not just expandable.
- Collapsed by default except the current domain; `collapsible: true` always.
- No emoji in sidebar labels; if icons are wanted, use the theme's
  `customProps.icon` mechanism, not inline emoji characters.

## Migration polish checklist (old-repo content)

- Strip: box-drawing characters, layout tables, ALL-CAPS headings, `**bold**`
  used as fake headings, stray `//` lines, "Part N" phrasing in prose.
- Convert: ASCII diagrams → Mermaid; inline code crushed into table cells →
  proper fenced blocks; long parenthetical asides → footnotes or cut.
- Rewrite converted-PDF prose that reads like slide bullets into full sentences.
