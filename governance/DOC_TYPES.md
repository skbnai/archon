# Document Type Taxonomy

Every page declares exactly one `doc_type`. Type drives template, review depth,
and freshness SLA.

| doc_type | Purpose | Freshness SLA | Special requirements |
|---|---|---|---|
| concept | Explain one idea | 365d | ≤1,200 words |
| guide | How to do X | 180d | Prereqs + steps + verification |
| reference-architecture | Blueprint | 180d | Mermaid diagram required; trade-offs section; ≤6,000 words (higher ceiling — these are deep technical blueprints; still split into a series if a source genuinely exceeds it) |
| pattern | Reusable solution | 365d | Context/Forces/Solution/Consequences |
| anti-pattern | Named failure mode | 365d | Symptoms/Why it happens/Remedy |
| decision | ADR | on change | ADR template; status proposed/accepted/superseded |
| runbook | Operational procedure | 90d | Preconditions/steps/rollback |
| checklist | Gate/review list | 180d | Scoreable items |
| research-report | Grounded deep research | 90d | `sources` required (tier-1 majority), `covers_version` |
| case-study | Applied example | 365d | Fictionalization note if synthetic |
| learning-path | Persona journey | 180d | Ordered links + outcomes per stage |
| hub | Domain/topic index | 90d | Links only canonical pages; curated, not auto |
| template-asset | Downloadable deliverable | 365d | Link to editable format |
| glossary | Term definitions | 180d | One unified glossary only |

Frontmatter schema (all types) lives in `.claude/skills/doc-standards/SKILL.md`;
enforced by `scripts/validate_frontmatter.py` via PostToolUse hook and CI.
