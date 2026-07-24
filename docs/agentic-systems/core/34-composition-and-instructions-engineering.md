---
title: "Skill Composition & Instructions Engineering"
domain: agentic-systems
doc_type: guide
topic_id: composition-and-instructions-engineering
status: current
supersedes:
  - "docs/agentic-systems/skill/enterprise/07-composition-and-instructions-engineering.md"
date_created: 2026-07-24
last_reviewed: 2026-07-24
---

# Part 7 — Skill Composition & Part 9 — Instructions Engineering

## PART A: Skill Composition Patterns

### 7.1 Composition topology options

**(a) Single Skill:** One skill with its own tools.

**(b) Composite Skill:** Skill A delegates to sub-skills B and C, which it references.

**(c) Hierarchical / Supervisor:** Supervisor skill routes to Domain Skills 1, 2, and 3.

- **Single Skill**: one coherent procedure, own tools. Default choice; prefer this unless composition is clearly justified.
- **Composite Skill**: a skill whose instructions explicitly delegate part of the procedure to another named skill ("apply the `refund-eligibility-check` skill before proceeding"). Useful when a sub-procedure is genuinely reused by multiple parent skills (eligibility checks, PII redaction, tone/style guides).
- **Nested/Hierarchical**: multiple levels of delegation — a domain skill delegates to a narrower sub-skill for an edge case. Keep depth shallow (2–3 levels); deep nesting reintroduces the context-bloat and debuggability problems Skills were meant to solve.
- **Planner/Supervisor Skills**: a top-level skill whose entire job is decomposition and routing — it holds almost no domain procedure itself, just the judgment for which domain skill(s) to invoke and in what order. This is the skill-layer analogue of Salesforce's orchestrator/specialist agent pattern and SAP's "Joule orchestrator delegates subtasks... to partner agents" model — except here the delegation target is another *skill* within the same agent rather than a separate *agent* over A2A.
- **Domain Skills**: owned by a business domain team (finance, HR, supply chain); the natural unit of ownership and versioning in most enterprise registries.
- **Shared/Reusable Skills**: cross-cutting concerns (tone-of-voice, PII-handling, citation format, escalation boilerplate) factored out so domain skills reference them rather than re-stating them — directly addressing the "duplicated prompts" anti-pattern (file `11`).

### 7.2 When should a Skill invoke another Skill vs. invoke Tools directly?

| Situation | Choice |
| --- | --- |
| The sub-procedure is itself reused by ≥2 parent skills | Invoke the shared sub-skill |
| The sub-procedure is only ever used in this one context | Inline it as a step in this skill's own instructions; don't over-decompose |
| The sub-procedure has its own distinct owner/compliance surface (e.g., a KYC check owned by Legal) | Invoke as a separate skill — this gives Legal independent versioning/audit control over just that piece |
| The next action is a single, unambiguous, atomic operation | Invoke the Tool directly; wrapping a single tool call in a "skill" adds indirection with no benefit (see anti-patterns, file `11`) |
| The task genuinely spans systems/teams that operate independent agents | Don't use skill-to-skill delegation at all — use A2A to a peer agent (file `04`) |

### 7.3 Trade-offs

- **Reuse vs. blast radius**: a shared sub-skill used by 50 parent skills is high-leverage but also a high-blast-radius single point of failure — treat it with the change-management rigor of a shared library, including a deprecation window (file `10`), not an internal implementation detail.
- **Debuggability**: every layer of nesting makes a production trace harder to read for a human responder. Cap nesting depth as a house style rule, and make sure trace visualization (file `08`) explicitly bundles repeated/nested spans rather than flattening everything into noise — this is precisely the UX problem AWS AgentCore's trace-tree tooling addresses (bundling repeated spans, adding default agent span filters to reduce infrastructure noise).
- **Latency**: each skill-load or sub-skill invocation is a context-window round trip. For latency-sensitive interactive agents, prefer inlining small, stable sub-procedures over dynamic sub-skill loading; reserve dynamic composition for less latency-sensitive or background/batch agents.

---

## PART B: Instructions Engineering

### 7.4 What belongs inside a skill's instructions

Recommended structure (expands on file `02`'s anatomy section with authoring guidance):

1. **Role** — who the agent is being asked to "be" for this task (tone, authority level, audience).
2. **Objectives** — the concrete success criteria, stated as outcomes, not just actions.
3. **Boundaries** — explicit scope limits ("do not process refunds over $500 without escalation").
4. **Business policies** — the actual rules, ideally cited to a source of truth rather than restated from memory (link to the policy doc; skills drift out of sync with policy otherwise).
5. **Decision trees** — where branching logic exists, prefer an actual if/then structure in the prose (or, for compliance-critical branches, delegate to a deterministic workflow engine — file `01`, §1.4).
6. **Reasoning hints** — guidance on *how* to think through ambiguous cases, not just what to do in clear-cut ones.
7. **Guardrails** — hard stops, forbidden actions, PII handling rules.
8. **Escalation rules** — exact conditions that trigger human handoff, and what context must be passed along.
9. **Compliance requirements** — regulatory citations, retention rules, disclosure requirements specific to the domain.
10. **Output formatting** — exact expected shape (especially where downstream systems or UI components parse the response).
11. **Termination conditions** — when the skill's procedure is "done" (important for multi-turn or long-running skills to avoid open-ended looping).
12. **Fallback / recovery behavior** — what to do when a tool fails, when information is missing, when the user's request doesn't cleanly match any branch.
13. **Clarification rules** — when to ask the user a question vs. proceed with a reasonable default.
14. **Tool usage policy** — which tools are preferred over which for overlapping capabilities, and why (the exact "use the Email Reset action if... otherwise use..." pattern from Salesforce's context-engineering guidance).
15. **Memory policy** — what should/shouldn't be written to persistent memory (ties to `memory_policy` metadata, file `02`).
16. **Human approval triggers** — restated in prose even though also declared in metadata, so the instruction is visible to the model at reasoning time, not just enforced structurally.

### 7.5 Anti-patterns in instruction design

| Anti-pattern | Why it hurts | Fix |
| --- | --- | --- |
| **Very long prompts** | Degrades instruction-following, increases cost/latency, buries the important rules among the trivial | Use progressive disclosure — move edge cases to `references/*.md`, keep the core SKILL.md lean |
| **Hidden business logic** | A rule embedded three paragraphs deep in prose is invisible to auditors and easy to silently violate | Extract compliance-critical logic into a deterministic workflow/tool with an explicit contract, referenced (not restated) by the skill |
| **Conflicting instructions** | Two skills (or two sections of one skill) state contradictory rules; the model resolves the conflict unpredictably | Registry-level lint check for overlapping scope + contradictory keywords; require a single owner per policy domain |
| **Tool overloading** | Skill lists 30 tools "just in case," diluting the model's ability to pick correctly | Curate the tool set per skill tightly; use Tool Search / dynamic tool selection (Azure Foundry's Toolbox tool search, which intelligently selects the right tools per task instead of surfacing every tool to the model) for large catalogs |
| **Duplicated prompts** | Same escalation boilerplate copy-pasted across 20 skills | Factor into a shared sub-skill (§7.1) |
| **Prompt drift** | Skill instructions and the actual backend/policy diverge over time because nobody re-validates | Tie skill review cadence to policy-change events, not just calendar time; include skills in the same change-control process as the policies they encode |
| **Instruction sprawl** | Skill accretes ad hoc exception after ad hoc exception until nobody can predict its behavior | Enforce the "one paragraph description" test (file `01`, §1.5) as a periodic re-certification gate, not just an initial-authoring gate |

### 7.6 Practical authoring workflow (the pattern that works in production)

1. **Start with evaluation, not authoring.** Run representative tasks against the agent without the skill; catalog specific, concrete gaps.
2. **Author the smallest skill that closes the observed gap.** Resist the urge to anticipate every future edge case up front.
3. **Structure for scale from the start** — assume the SKILL.md will eventually need a `references/` split, and organize headings accordingly even while the file is still small.
4. **Observe real trajectories.** Watch how the agent actually uses the skill in production/staging — overreliance on one section, unexpected tool choices, and misfires are the signal for the next revision, not intuition alone.
5. **Treat the name and description as the highest-leverage two fields in the whole document** — they are the only thing evaluated at every single turn (via the system-prompt-level metadata), long before the rest of the content is ever loaded.
