---
title: "Evaluation, Reusability & Deduplication"
date_created: 2026-07-24
last_reviewed: 2026-07-24
status: current
domain: agentic-systems
doc_type: guide
topic_id: evaluation-reusability-deduplication
supersedes: ["docs/agentic-systems/skill/coding/11-evaluation-reusability-deduplication.md"]
---

# Part 17 — Evaluation · Part 18 — Skill Reusability · Part 19 — Preventing Duplication

## PART A: Evaluation

### 17.1 What to measure

| Dimension | Metric | Notes specific to coding agents |
| --- | --- | --- |
| Correct skill selection | % of tasks where the matching skill actually loaded | Directly measurable via the `skill_selected` trace event (file `09`) |
| Correct tool selection | % of tasks using the "right" tool (structured tool vs. raw terminal, file `06`) | A raw-terminal call where a structured tool existed is a specific, flaggable anti-pattern |
| Correct repository retrieval | Precision/recall of files retrieved vs. files actually relevant | Over-retrieval (file `06`) is measurable as "files loaded but never referenced in the final diff" |
| **Compilation success** | % of agent-produced changes that build without error | The most basic, universally-applicable coding-specific bar |
| **Unit test success** | % of changes where the existing test suite still passes | Standard regression bar |
| **Integration test success** | % passing broader, cross-component tests | Higher bar, especially relevant for multi-file/multi-service changes |
| Security findings | Vulnerabilities introduced per N lines of agent-generated code | Directly relevant given independent research (Veracode, cited in file `10`'s broader literature) found agent-generated code security pass rates flat around ~55% even as raw coding-benchmark scores improved — a genuine, unresolved gap between "compiles and passes tests" and "is secure" |
| Latency | Time from request to validated response | Matters heavily for interactive (non-background) agent use |
| Cost | Token usage + API cost per resolved task | Token efficiency varies substantially by harness — differences of several-fold between agents on the same task have been publicly reported |
| Developer satisfaction | Survey/qualitative | Stack Overflow's own 2025 survey data (cited in the broader literature) shows adoption climbing while trust metrics simultaneously eroded — satisfaction and raw benchmark performance are not the same signal and both should be tracked |
| **Acceptance rate** | % of agent-proposed diffs merged without substantial human rewrite | The most direct proxy for "is this actually saving time" |
| Regression testing | Golden-task suite pass rate over time, per skill/tool/prompt version | Same discipline as the enterprise case (companion package file `08`) |

### 17.2 Benchmark suites relevant to coding agents specifically

Public, standardized benchmarks give a useful (if imperfect) external reference point distinct from any org's internal golden-task suite:

- **SWE-bench (Verified / Pro)**: resolves real GitHub issues end-to-end; a widely cited comparative benchmark across agent+model pairs.
- **Terminal-Bench**: tests an agent driving a terminal end-to-end on realistic tasks — a good proxy specifically for CLI-first agents.

**Important methodological note, directly relevant to any org running its own evaluation program**: published benchmark scores are properties of the *agent-plus-model pairing*, not the model alone — the same underlying model scores differently depending on the surrounding harness/scaffolding (context management, tool design, retry strategy). Evaluate the combination you actually intend to deploy, not just the model in isolation.

### 17.3 Human review

Automated metrics (compile/test pass, benchmark scores) catch correctness regressions but systematically under-detect: code that "works" but is stylistically inconsistent with the codebase, architecturally sound-but-locally-suboptimal choices, and security issues that don't manifest as test failures. Scope human review to sampled, high-risk, or low-confidence-score agent output rather than attempting full manual review of every agent-authored change — full manual review defeats the productivity purpose of the tooling in the first place.

---

## PART B: Skill Reusability

### 18.1 Sharing mechanisms observed

| Mechanism | Scope | Maturity |
| --- | --- | --- |
| Repository-committed skills (`.github/skills/`, `.agents/skills/`) | Team, via git | Mature, widely used |
| Personal/global skills (`~/.copilot/skills/`, etc.) | Individual developer, cross-project | Mature, widely used |
| Organization catalog | Org-wide | Announced/roadmap on multiple platforms, not broadly shipped |
| Extension/plugin marketplace | Public or curated | Mature but **unverified** by the platform in most cases (GitHub's own explicit warning, file `10`) |
| Community skill directories (Agensi, awesome-copilot, ClawHub-equivalents) | Public | Large catalogs (hundreds to low-thousands of skills), variable quality, security risk as documented in file `10` |
| Git repositories as skill sources | Public or private | `gh skill` installs directly from a repo reference, with provenance tracking |
| Package registries | — | Not yet a dominant distribution mechanism for coding skills specifically, unlike, say, npm for code libraries |

### 18.2 Version compatibility and migration

- **Cross-tool compatibility is generally strong** for the SKILL.md core (`name`/`description`/body); vendor-specific frontmatter extensions are safely ignored by hosts that don't recognize them (file `02`) — this is a genuinely good, spec-driven property, not something teams need to work hard to preserve.
- **Migration between tools' native rule formats is the harder problem** — `.cursorrules` → `.clinerules` → `AGENTS.md` migrations are common enough that dedicated community tooling exists (`intellectronica/ruler` distributes one canonical instructions source to many tool-specific formats). The clear long-term recommendation, echoed across multiple sources: **standardize on AGENTS.md as the canonical always-loaded file** where the target tools support it, and treat vendor-specific files as thin, generated overlays rather than independently authored sources of truth.
- **Deprecation**: no formalized mechanism observed; practically handled the same way as any repo file removal — grep for references, remove, and communicate via the normal PR process.

---

## PART C: Preventing Duplication

### 19.1 Why this problem is structurally worse for coding-assistant skills than for enterprise skills

In the enterprise case (companion package file `06`), a central platform team can enforce a registry admission gate. In the coding-assistant case, **any individual developer can author and commit a skill or rules file with zero central review**, and the natural failure mode — observed repeatedly across the sources reviewed — is five near-identical instruction files per repository (`.cursorrules`, `CLAUDE.md`, `.windsurfrules`, `.clinerules/base.md`, `AGENTS.md`), each maintained independently and drifting out of sync.

### 19.2 Concrete anti-duplication practices

| Practice | What it prevents |
| --- | --- |
| **Single canonical source + generated/symlinked overlays** (the sync-script or `ruler`-style pattern from section 18.2) | The five-near-identical-files problem directly |
| **Standardize on AGENTS.md as the primary always-loaded file** wherever supported | Reduces the number of files that need to exist at all, rather than just keeping duplicates in sync |
| **Naming conventions for skills** (`domain-verb-noun`, e.g., `github-issues`, `webapp-testing`) | Reduces accidental near-duplicate skill creation by making existing coverage more discoverable by name alone |
| **A lightweight internal skill catalog/index** (even a wiki page or README-of-skills, absent a real registry) | Gives developers something to check before authoring a new skill — the single highest-leverage low-effort fix available today, given the absence of mature org-catalog tooling |
| **Ownership metadata** (`metadata.owner`, file `02`) | Creates accountability that makes forking less tempting than asking the existing owner to extend their skill |
| **Dependency awareness** (`dependencies.tools`, file `02`) | Surfaces at authoring time whether a needed MCP server/tool already exists, reducing duplicate MCP server wrappers |
| **Periodic audit** (grep across the org's repos for skill directories, diff for near-identical content) | A manual but effective substitute for the automated similarity-gate the enterprise registry pattern provides natively (companion package file `06`) |

### 19.3 What NOT to duplicate — the checklist

- **Tool wrappers**: if two skills both essentially say "call this MCP tool with these arguments," that's a sign the *tool's own description* (file `05`) should carry that guidance instead, eliminating the need for either skill.
- **MCP servers**: one GitHub MCP server per org, not one per team reinventing a thinner version of the same integration.
- **Instructions/prompts**: the single-canonical-source pattern above.
- **Slash commands**: overlapping slash commands across tools for the same underlying procedure should point to the same underlying skill content, not separately maintained near-duplicates.
- **Capability definitions generally**: the same discipline as the enterprise case — before authoring, search first (file `18`'s catalog mechanisms); author only when a genuine gap is confirmed.
