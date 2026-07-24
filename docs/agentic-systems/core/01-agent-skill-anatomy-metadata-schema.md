---
title: "Skill Anatomy & Metadata Schema"
date_created: 2026-07-24
last_reviewed: 2026-07-24
status: current
domain: agentic-systems
doc_type: guide
topic_id: agent-skill-anatomy-metadata-schema
supersedes: ["docs/agentic-systems/skill/enterprise/02-skill-anatomy-and-metadata-schema.md"]
covers_version: "as of mid-2026"
tags: ["agentic-systems", "skill", "enterprise", "research"]
---

# Part 2 — Skill Anatomy & Metadata Schema

> **Shared chapter.** The internal structure of a skill — the `SKILL.md` layout, folder anatomy (`references/`, `scripts/`, `templates/`, `evals/`), and the full metadata schema — is identical for enterprise and coding-assistant skills, because both build on the same open Agent Skills spec.
>
> The canonical version of this chapter lives in the coding-assistant skills series (not yet migrated to this wiki).

This chapter covers:

- **Physical structure** — the required `SKILL.md` plus optional `references/`, `scripts/`, `templates/`, and recommended `evals/` folders.
- **Metadata schema (Deliverable 4)** — every frontmatter field, which are required vs optional, and validation rules.
- **Progressive disclosure** — how metadata, instructions, and reference files load at different times to protect the context window.

Then continue this series with [Part 3 — Execution Lifecycle & Tracing](30-execution-lifecycle-and-tracing.md).
