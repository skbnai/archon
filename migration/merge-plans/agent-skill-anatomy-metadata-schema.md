# Merge Plan: agent-skill-anatomy-metadata-schema

## Cluster

| old_path | words | last_reviewed | source_type | disposition |
|---|---|---|---|---|
| docs/agentic-systems/skill/coding/02-skill-anatomy-and-metadata-schema.md | 1209 | 2026-07-10 | native-md | MERGE-INTO (ascii_art_suspected=True) |
| docs/agentic-systems/skill/enterprise/02-skill-anatomy-and-metadata-schema.md | 146 | 2026-07-12 | native-md | MIGRATE |

- target canonical path: `docs/agentic-systems/core/01-agent-skill-anatomy-metadata-schema.md`
- domain: agentic-systems
- wave: 3
- topic_id: `agent-skill-anatomy-metadata-schema` — already registered in `governance/CANONICAL_REGISTRY.yaml` (line 1635), canonical path matches, `supersedes:` already lists the coding old-path. No librarian action needed for the parent topic.

## Survivor

**Flag for reviewer — disagreement with mapping.csv's stated rationale.** Both files are now read in full. The enterprise file at `docs/agentic-systems/skill/enterprise/02-skill-anatomy-and-metadata-schema.md` is **not** a broader canonical treatment — it is a one-paragraph stub/redirect. Its entire body reads: "Shared chapter... **The canonical version of this chapter lives in the coding series**" followed by a link to the coding file and three one-line bullet summaries of what the coding file covers. It contains zero original schema content, zero tables, zero examples — it explicitly defers authority to the file mapping.csv labels as the loser. mapping.csv's rationale ("enterprise scope is the broader canonical") does not hold up against the actual text; "enterprise scope" appears nowhere as a differentiator — the topic (SKILL.md anatomy + metadata schema) is scope-identical across both series by the enterprise file's own admission ("identical for enterprise and coding-assistant skills, because both build on the same open Agent Skills spec").

Applying recency > completeness > structure:
- **Recency**: enterprise 2026-07-12 vs coding 2026-07-10 — enterprise wins by 2 days, the only axis favoring it.
- **Completeness**: coding has the entire substantive payload (physical structure, full frontmatter field tables across 5 vendors, instructions-body structure, mandatory/optional summary table, full Deliverable-4 YAML schema). Enterprise has none of it — completeness overwhelmingly favors coding.
- **Structure**: coding has real H2/H3 structure (2.1–2.5) with tables and a fenced schema block. Enterprise has no heading structure below H1, just a blockquote and a bullet list — structure favors coding.

Per the stated priority order (recency first), the letter of the tie-break still nominally favors enterprise, which is consistent with mapping.csv picking it. But this is a case where a stub's higher `last_reviewed` date is a weak signal — the enterprise file was plausibly last "reviewed" only to confirm it should still point at the coding chapter, not because new content was added to it. **Recommend the reviewer double-check whether mapping.csv's rationale text should be corrected** (it currently justifies the pick with a claim — "enterprise scope is the broader canonical" — that is factually false for this specific chapter, even though the pick itself is defensible on the pure recency rule). I am not overruling mapping.csv: survivor remains as recorded —

**Survivor = `docs/agentic-systems/skill/enterprise/02-skill-anatomy-and-metadata-schema.md`** (146 words, reviewed 2026-07-12) — but functionally the survivor supplies only the frontmatter/shell and framing sentence; essentially all body content must be pulled from the loser.

## Unique-Content Map

Loser (`docs/agentic-systems/skill/coding/02-skill-anatomy-and-metadata-schema.md`, `ascii_art_suspected=True`) content absent from the survivor — this is effectively the entire loser, since the survivor is a pointer stub:

1. §2.1 Physical structure: full directory tree (`SKILL.md` required; `references/`, `scripts/`, `templates/` optional; `evals/` recommended) — this is the ASCII art to convert (see Transform Notes).
2. GitHub's own worked example: `github-issues/` skill next to `code-review/` skill, each with its own `SKILL.md` + `templates/` subfolder.
3. §2.2 spec-baseline table: `name` (required, lowercase-hyphenated, ≤64 chars) and `description` (required, ≤1024 chars, must state both WHAT and WHEN — weak triggering if "what"-only).
4. §2.2 vendor-extension table: `license`, `argument-hint`, `user-invokable`, `disable-model-invocation` (GitHub Copilot); `context: fork` (Claude Code); `globs` (Cursor `.mdc`, adjacent-but-distinct concept); `interface.*` fields, `policy.allow_implicit_invocation`, `dependencies.tools`, `default_prompt` (OpenAI Codex).
5. Cross-tool portability note: empirically confirmed that unrecognized vendor fields are silently ignored, not fatal — the mechanism that makes "one skill, every agent" work.
6. §2.2 enterprise/team governance overlay table: `owner`, `version` (semver), `repo_scope`, `security_reviewed` (bool+date+reviewer, tied to Rules-File-Backdoor-class attacks), `provenance` (source_repo/ref/tree_sha, precedented by GitHub's `gh skill` CLI).
7. §2.3 Instructions-body recommended structure (8 parts): purpose restatement, preconditions/required context, procedure (cites TDD-style explicit staging), file/language filters, constraints/safety ("never" statements), examples/non-examples, output-format expectations, references to bundled files (execute vs. read ambiguity called out).
8. §2.4 Mandatory-vs-optional summary table spanning spec baseline, invocation control, presentation, dependencies, org governance, and security categories.
9. §2.5 Deliverable 4 — full reusable YAML metadata schema (union superset: spec fields, `interface`, `policy`, `dependencies.tools`, `metadata` block with `owner`/`version`/`repo_scope`/`provenance`/`security_reviewed`/`evaluation`).
10. Closing design principle: the union schema is intentionally a superset so any host reads only the subset it recognizes, with `metadata.*` as the collision-free namespace for org governance fields.
11. Note: the survivor's own bullet list claims the (coding) canonical also covers "progressive disclosure — how metadata, instructions, and reference files load at different times." No such section actually exists in the loser body (§2.1–2.5) — likely lives in a different part of the series. Flag this as a possible dangling cross-reference for the reviewer; do not fabricate a progressive-disclosure section to satisfy it.

## Target Structure

Outline for `docs/agentic-systems/core/01-agent-skill-anatomy-metadata-schema.md` (survivor frontmatter/title shell + loser body, renumbered as flat H2/H3 since the multi-part-series framing doesn't carry over to the `core/` folder):

```
# Agent Skill Anatomy & Metadata Schema

<1-paragraph why-this-matters, adapted from survivor's framing
 sentence: shared structure across enterprise and coding-assistant
 skills, both built on the same open Agent Skills spec>

## Physical structure
  ### Folder layout
  ### Vendor example (GitHub github-issues/ + code-review/)

## SKILL.md frontmatter schema
  ### Spec-baseline fields (name, description)
  ### Vendor extensions (GitHub Copilot, Claude Code, Cursor, OpenAI Codex)
  ### Cross-tool portability
  ### Enterprise/team governance overlay

## Instructions body structure
  (8-part recommended structure)

## Mandatory vs. optional fields (summary table)

## Reusable metadata schema (YAML)

## Related
## Sources
```

Word count estimate: survivor contributes ~40 words (intent framing only, its bullet summary and "read the canonical chapter for" pointer are dropped since content is now inline); loser contributes ~1150 words of body content net of its own frontmatter/H1. **Total merged estimate ≈ 1200 words** — comfortably under the ~2,000-word limit. No split needed, no new child pages, no additional `topic_id` required.

## Transform Notes

- **diagram-standards**: the loser's §2.1 ASCII directory tree (`my-skill/` with `SKILL.md`, `references/`, `scripts/`, `templates/`, `evals/` and inline REQUIRED/OPTIONAL/RECOMMENDED annotations) must be converted to a Mermaid diagram (flowchart or simple tree) per the diagram-standards skill. This is the only `ascii_art_suspected=True` content in the cluster.
- **Links needing rewrite**: loser's internal series link `../coding/02-skill-anatomy-and-metadata-schema.md` — dropped entirely (self-referential series pointer, meaningless once merged). Loser has no other outbound links. Survivor's two internal links must be rewritten or dropped: (a) the link to the (now-merged) coding chapter — drop, content is now on this same page; (b) `./03-execution-lifecycle-and-tracing.md` ("Then continue this series with Part 3...") — this points to an old-repo sibling; check mapping.csv for that file's new-repo target and rewrite as a `## Related` link if it has a MIGRATE row, otherwise drop.
- Survivor's `series_index`, `series_part`, `series_name`, `series_total` frontmatter fields do not carry over — target uses standard doc-standards frontmatter (`doc_type`, `topic_id`, `domain`, etc.), not `multi-part-series` shell fields.

## Doc Type & Template

**doc_type: concept**, template `.claude/skills/doc-standards/templates/concept.md`.

Rationale: this page documents the anatomy and metadata schema of an artifact (a Skill package) — not a deployed system's containers/components, so `reference-architecture` (C4 diagram, components & responsibilities, operational SLOs, industry variations) is a poor fit and would force irrelevant sections. `concept` fits directly: "The core idea" = what a Skill package is and why the schema exists; "How it works" = physical structure + frontmatter schema + instructions-body structure + mandatory/optional table + full YAML schema; "When to use it / when not" = portability note (safe to add vendor-specific fields; unrecognized ones are ignored) and the org-governance overlay guidance (when `owner`/`security_reviewed`/`provenance` should be mandatory vs. optional). The converted Mermaid folder-structure diagram is embedded under "How it works" per diagram-standards; a concept page may include a diagram, it just isn't required to satisfy the architecture-diagram mandate the way `reference-architecture` is.
