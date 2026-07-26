---
title: "Agent Skills & Skill Registries — Complete Playbook 2026 (Part 1)"
doc_type: guide
domain: agentic-systems
status: current
topic_id: agent-skills-complete-playbook-2026
date_created: 2026-07-24
last_reviewed: 2026-07-24
supersedes:
  - docs/agentic-systems/skill/Agent_Skills_Complete_Playbook_2026.md
tags:
  - agentic-ai
  - agent-skills
  - playbook
  - coding-tools
---

# Agent Skills & Skill Registries — Complete Playbook 2026 (Part 1)

_The Complete Playbook_

Lifecycle · Best Practices · Anti-Patterns · Evaluation · A/B Testing Registries · Microsoft APM · Plugin Marketplaces · Enterprise Integration OKRs & KPIs · Security · Governance · Personas · The Road Ahead

Covering: Claude Code · GitHub Copilot · Cursor · Codex · Windsurf · Gemini CLI · Microsoft APM

---

## 01 FUNDAMENTALS — WHAT ARE AGENT SKILLS?

### What Are Agent Skills?

An **Agent Skill** is a modular, portable package of domain-specific expertise that an AI agent can discover and load on demand. Introduced by Anthropic in October 2025 and donated to the open **Agentic AI Foundation (AAIF)** under the Linux Foundation in December 2025, the standard centers on a SKILL.md file combining YAML metadata with Markdown procedural instructions. By early 2026, the standard had been adopted by Claude Code, GitHub Copilot (April 2026), Cursor, Codex, Windsurf, Gemini CLI, and over 20 other agents.

### The Three-Layer Architecture

Skills use **Progressive Disclosure** — a design philosophy that solves context window bloat. Rather than loading everything upfront, an agent traverses three layers:

#### Layer 1 — Metadata Scan

Agent reads YAML frontmatter (name, triggers, domain tags, negative_examples) to determine relevance without loading full content. Fast and cheap — runs on every task.

#### Layer 2 — Instruction Load

If relevant, the Markdown procedural body loads. Step-by-step workflow, constraints, gotchas, examples. Kept under 500 lines / 5,000 tokens per the AAIF spec.

#### Layer 3 — Resource Execution

Optional scripts, templates, reference data in Skills = portable domain expertise loaded on demand. MCP = external service calls. AGENTS.md = always-on project context. If it should happen almost every time, use AGENTS.md. If only sometimes, make it a skill.

### Canonical SKILL.md Structure

```yaml
---
name: data-pipeline-audit
version: 2.1.0
domain: data-engineering
triggers: [audit, pipeline, dbt, lineage, quality-check]
negative_examples: [frontend, UI, CSS, design, React]
author: platform-eng@acme.com
compatible_with: [claude-code, copilot, cursor, codex, windsurf]
---
## Instructions

When auditing a data pipeline, follow this sequence:

1. Identify source-to-target lineage
2. Check SLA breach patterns in run metadata
3. Run schema drift detection against registered contracts
4. Output findings as structured JSON to findings/audit-report.json

## Resources

- Read references/audit-runner.py before executing
- Load references/findings-schema.json if validation is requested
```

**280K+** Public skills Feb 2026. **73% → 85%** Routing accuracy lift with negative examples. **40%** Enterprise apps with task-specific domains in SkillsBench by end 2026. **20+** Agents supporting SKILL.md standard.

---

## 02 BEST PRACTICES FOR SKILL AUTHORSHIP

### Best Practices

Perplexity published its internal skill development manual in May 2026, revealing that _'many useful patterns for writing code become anti-patterns in skill creation.'_ The agentskills.io specification and Google ADK teams have contributed additional guidance. Below is the consolidated practitioner consensus.

### The Zen of Skills vs The Zen of Python

| Zen of Python | Zen of Skills | Implication |
|---|---|---|
| Simple is better than complex | Complexity is the feature | Skills encode the non-obvious. If it's simple, the model already knows it. Delete it. |
| If easy to explain, may be a good idea | If easy to explain, model knows it. Delete. | Skills should contain gotchas, exceptions, and institutional knowledge — not basics. |
| Special cases aren't special enough | Gotchas ARE the special cases | Edge cases and failure modes are the highest-value content in a skill. |
| Explicit is better than implicit | Trust the model's training | Don't explain what a PDF is. Jump straight to project-specific conventions. |
| Flat is better than nested | A skill is a folder, not a file | Use /references/ subdirectory for heavy content. SKILL.md is the router. |

### Top 10 Best Practices

1. **Keep SKILL.md under 5,000 tokens** — The spec recommends ≤500 lines. Every token competes with conversation history, other active skills, and system context. Focus only on what the agent wouldn't know without your skill.

2. **Write negative_examples in YAML** — Adding negative trigger examples improved routing accuracy from 73% to 85% in published benchmarks. Explicitly list what the skill should NOT activate for — as important as the positive triggers.

3. **Match specificity to task fragility** — Prescribe tightly for fragile steps (exact API parameters, security checks). Give the agent freedom for steps where creativity improves outcomes. Over-constraining flexible tasks degrades quality.

4. **Use progressive reference loading** — 'Read references/error-codes.md if the API returns non-200' beats a generic 'see references/ for details.' The agent loads context on demand, not upfront.

5. **Test with SkillsBench or custom harness** — Google ADK and agentskills.io both recommend evaluating every skill against a test harness before publishing. Routing accuracy and task success rate are minimum gates.

6. **Human review for generated skills** — Auto-generated skills provide 'no benefit on average' per Perplexity's research — models cannot reliably author the procedural knowledge they benefit from consuming. Human authorship of SKILL.md content is currently non-negotiable.

7. **One workflow per skill** — A skill that tries to handle five different workflows becomes a monolith no agent can route to reliably. Write narrow, named skills. Compose them at the harness layer.

8. **Encode anti-rationalization** — Addy Osmani's production skill set includes explicit rebuttals to common engineering excuses: 'We'll fix tests after launch' paired with the counter-argument. Write down the lies your team tells itself and pair each with the rebuttal in the skill.

9. **Version semantically** — Use semver (1.0.0 → 1.1.0 for backwards-compatible instruction improvements, → 2.0.0 for trigger/scope changes). Pin versions in apm.yml lockfiles so team setups are reproducible byte-for-byte across machines.

10. **Vet OSS skills before installing** — Snyk's ToxicSkills research found 13.4% of public ClawHub skills had critical issues. Even a 30-second skim of SKILL.md catches obvious attacks. Look for environment variable references and unexplained URL fetches.

---

## 03 ANTI-PATTERNS — WHAT GOES WRONG

### Anti-Patterns in Skill Design

These are patterns that seem correct from a software engineering background but actively harm skill quality. Drawn from Perplexity's production experience, Sysdig's deployment guide, and the agentskills.io creator documentation.

| Anti-Pattern | Why It Feels Right | What Actually Happens | Fix |
|---|---|---|---|
| The Encyclopedia | Comprehensive docs are good software practice | Context window bloated; agent attends to irrelevant content; routing slows | ≤500 lines in SKILL.md; move reference material to /references/ |
| The Monolith | One file is simpler to maintain | Agent can't route to the right sub-workflow; ambiguous trigger matching | Split into narrow skills; compose at harness layer |
| The Python Tutorial | Explaining concepts ensures the agent understands | Wastes tokens on things the model already knows from training | Delete anything the model would know without your skill |
| Broad Triggers, No Negatives | More triggers = more discovery | Skill fires on irrelevant tasks; degrades other skills sharing the window | Add negative_examples; use specific trigger keywords |
| Installing Without Vetting | Open-source = community-trusted | Prompt injection, credential theft, elevated permissions | Scan SKILL.md before install; prefer registries that scan (Agensi, Tessl) |
| Static Skill, No Iteration | If it works, don't touch it | Skill decays as codebase evolves; routing drifts; quality drops silently | Monitor task success rate; A/B test updates; set staleness alerts |
| Workflow-in-AGENTS.md | Always-on context ensures agent never misses it | Every task pays the token cost even when the workflow isn't needed | Move specialized workflows to skills; keep AGENTS.md for universal context |
| Self-Generated Skills | Agent can write its own skills = automation | No measurable quality improvement over baseline per SkillsBench | Human authors write skills; agents execute them |
| Hardcoded Secrets in Resources | Convenience during development | Snyk found 280+ skills leaking API keys; instant credential theft vector | Use env var references; run secret scanning in CI before publish |
| No Exit Criteria | Natural language is self-explanatory | Agent doesn't know when it has completed the task; loops or halts early | Add explicit completion signals: 'output findings to findings/report.json and stop' |

---

## 04 SKILL REGISTRIES & PACKAGE MANAGERS

### Skill Registries

A skill registry is a centralized (or federated) catalog where skills are published, discovered, versioned, and governed. As of early 2026, the ecosystem spans public community registries, private enterprise registries, and cloud-native managed registries. The landscape evolved rapidly from simple GitHub repos to governed platforms with automated security scanning, version tracking, and IDE-native discovery.

### Registry Taxonomy

| Type | Examples | Audience | Key Features |
|---|---|---|---|
| Public Community | ClawHub, skills.sh, Tessl Registry, Agensi | OSS developers | High volume, community ratings — but highest security risk (ClawHavoc campaign) |
| Private Enterprise | SkillReg, SkillHub (iFlytek), internal GitOps | Enterprise eng teams | RBAC, audit logs, approval flows, firewall deployment, data sovereignty |
| Cloud-Native Managed | Google Cloud Agent Registry, AWS AI Registry, Cisco AI Defense | Platform/MLOps teams | MCP server integration, IAM binding, compliance frameworks, automated scanning |
| Marketplace / Curated | dotnet/skills, Cowork, Azure SRE Agent Plugins, awesome-copilot | Business users | Verified, quality-scored, cross-model reuse via AAIF standard |
| IDE-Native | VS Code Extensions, GitHub Copilot Plugin Marketplace | Individual developers | Browse/install from IDE; slash-command activation; side-by-side diff on update |

---

## 05 MICROSOFT APM & PLUGIN MARKETPLACES

### Microsoft APM — Agent Package Manager

Microsoft's **Agent Package Manager (APM)**, open-sourced under the Microsoft GitHub org (MIT license), is the npm equivalent for AI agent dependencies. One **apm.yml** manifest declares every primitive — skills, prompts, instructions, plugins, MCP servers — and apm install reproduces the exact same agent setup across GitHub Copilot, Claude Code, Cursor, OpenCode, Codex, Gemini, and Windsurf. The lockfile (apm.lock.yaml) pins the resolved tree the way package-lock.json does for npm.

```yaml
# apm.yml — declare once, deploy everywhere
skills:
- source: github.com/dotnet/skills
  plugin: dotnet-agent-skills
  ref: v2.1.0
- source: github.com/addyosmani/agent-skills
  plugin: engineering-lifecycle
  ref: stable
- source: github.com/myorg/internal-skills
  plugin: data-pipeline-audit
  ref: main
mcp_servers:
- name: github
  url: https://api.githubcopilot.com/mcp/
- name: internal-db
  url: https://mcp.internal.myorg.com/
  trust: explicit
  policy: .github/apm-policy.yml # org-level policy enforced at install time
```

### Key APM Features

**One Manifest, Every Harness** — Copilot, Claude, Cursor, OpenCode, Codex, Gemini, Windsurf — all configured in one command. No manual per-agent setup. A fresh clone reproduces the same setup byte-for-byte.

**Transitive Dependency Resolution** — Packages can depend on packages. APM resolves the full dependency tree, pins content hashes, and gates transitive MCP servers behind explicit trust prompts. Tighten-only inheritance: enterprise → org → repo.

**Marketplace Integration** — Register any GitHub repo as a marketplace. Browse with /plugin marketplace browse. Install with /plugin install @marketplace. Name collision prevention via @MARKETPLACE scoping.

**Security at Install Time** — Every install scans for hidden Unicode, pins content hashes, and gates transitive MCP servers. apm-policy.yml enforced at install including transitives. No opt-in required — security is the default.

---

## 06 SKILL LIFECYCLE — END-TO-END

### The Complete Skill Lifecycle

A skill is not a static artifact — it is a product with a full lifecycle from need identification through retirement. Organizations that treat skills like software assets (versioning, testing, deprecation) consistently outperform those that treat them as static prompt files. Uber's two-tier governance model (200 curated core + 300 experimental) is the reference implementation.

| Stage | Key Activities | Owners | Gates & Outputs |
|---|---|---|---|
| 1. Discovery | Identify workflow pain points. Audit registry for existing skills — 80% reuse target. Gap analysis against team workflows. | Process owners, Platform eng | Skill brief, use-case doc, registry search report |
| 2. Design | Define trigger conditions, scope, and negative_examples. Threat model for security risks. Draft resource requirements. Determine if AGENTS.md is more appropriate. | Skill author, Security, Domain SME | SKILL.md draft v0.1, resource manifest |
| 3. Build & Test | Write SKILL.md + /references/ scripts. Unit-test against SkillsBench or custom harness. Routing accuracy check: ≥85% with negative examples. Shadow-mode execution. | Skill author, Engineer | v0.x package, test report, routing score |
| 4. Review & Approve | Security scan: OWASP AST10 + Snyk semantic scan. Peer review of SKILL.md content. Compliance sign-off. Registry approval gate (approval SLA ≤5 days). | Security, Compliance, Skill committee | Approved v1.0, scan report, approval record |
| 5. Publish | Semantic version tag. Namespace assignment. RBAC permissions set. SHA-256 hash pinned. Discovery metadata indexed in registry. apm.yml / apm.lock.yaml updated. | Platform eng, Registry admin | Live registry entry, lockfile update, Slack/email announce |
| 6. Monitor | Track: task success rate, latency P95, token cost per invocation, error patterns, routing precision. Alert thresholds: error_rate >5%, TSR drop >10%. | Platform eng, Product | Weekly telemetry report, alerting dashboard |
| 7. A/B Test & Iterate | Challenger version built. 70/30 traffic split (champion/challenger). Minimum 200 samples at 95% confidence. Shadow mode first. Winner promoted, loser archived. | Skill author, Data science | A/B test report, v1.x update, rollout record |
| 8. Deprecate & Retire | Usage drops below threshold for 30 days. Flag as deprecated with migration guide. Notify all dependents (identified via registry dependency graph). Archive after 60 days. | Platform eng, Skill owner | Deprecation notice, archived version, migration guide |

---

**This is Part 1 of 2. [Continue with Part 2 →](pathname:///archon/agentic-systems/parts/16-agent-skills-complete-playbook-2026-part2) for Evaluation Frameworks, A/B Testing, Enterprise Integration, OKRs & KPIs, Governance & Security, and The Road Ahead.**

## Related

- [Agent Skills for AI Coding Assistants — Executive Summary & Reference Architecture](15-executive-summary-and-reference-architecture.md) — the previous section in this series.
- [Foundations: What Is a Coding Skill?](18-foundations-what-is-a-coding-skill.md) — the next section in this series.
