---
title: "Enterprise Workflows & Comparative Analysis"
date_created: 2026-07-24
last_reviewed: 2026-07-24
status: current
domain: agentic-systems
doc_type: guide
topic_id: enterprise-workflows-comparative-analysis-and-patterns
supersedes: ["docs/agentic-systems/skill/coding/12-enterprise-workflows-comparative-analysis-and-patterns.md"]
---

# Part 20 — Enterprise Development Workflows · Part 21 — Comparative Analysis (+ Deliverables 1 & 10)

## PART A: How Skills Support Enterprise Development Workflows

| Workflow | How Skills/AGENTS.md/context engineering apply |
| --- | --- |
| **Greenfield development** | Lower skill dependency (less existing convention to encode); AGENTS.md scaffolding and templates (file `01`, section 1.5) matter more than deep procedural skills early on |
| **Legacy modernization** | High skill value — encode migration-specific procedures (e.g., a specific ORM-to-ORM migration pattern) as a dedicated skill; repository context engineering (file `06`, especially ADRs) is critical to avoid the agent "fixing" deliberate legacy workarounds |
| **Bug fixing** | Debugging-methodology skills (root-cause-first, reproduce-before-fix) show measurable value; testing-agent separation (file `09`) reduces the risk of a fix that only satisfies the bug's literal symptom |
| **Feature development** | The default case most tooling optimizes for; benefits most directly from well-scoped, single-purpose skills (webapp-testing, code-review, etc.) |
| **Architecture reviews** | Best served by repository context engineering (ADRs, architecture docs, file `06`) more than by skills per se — this is a retrieval/grounding problem, not a procedural one |
| **Code review** | A dedicated review-agent role (file `09`) plus a code-review skill/checklist; independence from the implementing agent is the key design choice |
| **Refactoring** | Requires the highest validation bar (broad regression testing, file `17`) since success is defined as "no behavior change," which automated tests alone can only partially verify |
| **Documentation** | Often folded into the coding agent's output-format requirement (skill instructions specifying doc updates as part of the deliverable) rather than a fully separate agent |
| **Migration** | Same pattern as legacy modernization — a dedicated, narrowly-scoped skill per migration type, retired once the migration completes (file `18`, deprecation) |
| **Testing** | Dedicated testing skills/agents, file `09`, `05` |
| **CI/CD** | Validation lifecycle stage (file `03`) should integrate with, not duplicate, existing CI observability (file `09`) |
| **DevSecOps** | Security-agent role plus mandatory security review gates on skills themselves (file `10`) — the discipline applies both to what the agent produces and to the agent's own tooling |
| **Infrastructure as Code** | Terraform/cloud/Kubernetes tools should default to plan-only with explicit approval for apply (file `10`, section 16.4) |
| **Cloud engineering / Platform engineering** | Dev Container and MCP server standardization (file `07`, `08`) is itself a platform-engineering deliverable — treat "the org's standard agent environment" as a product |
| **SRE** | Background/async agents (Devin-style) triaging incidents and proposing rollback PRs is an emerging, higher-autonomy pattern requiring the tightest approval gates of any workflow in this list |
| **Data engineering / AI engineering** | Notebook APIs (file `07`) and data-specific tool descriptions (query safety, PII handling) become first-class concerns |

## PART B: Comparative Analysis

*Reflects publicly documented capability as of mid-2026 — this category changed vendor structure multiple times during the research window itself (Windsurf into Devin, Continue.dev into Cursor, Gemini CLI into Antigravity); verify current state before procurement.*

### Comparison table

| Dimension | Claude Code / Claude Desktop | GitHub Copilot (Agent Mode) | Cursor | OpenAI Codex CLI | Antigravity CLI (f/k/a Gemini CLI) | Devin | Amp (Sourcegraph) | JetBrains Junie |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Skill packaging | SKILL.md (origin implementation) | SKILL.md (adopted Apr 2026) | SKILL.md-compatible + native `.mdc` rules | SKILL.md + plugin manifest (`agents/openai.yaml`) | Emerging under Antigravity's new harness | Not skill-packaged in the SKILL.md sense — procedural knowledge largely implicit/model-driven | SKILL.md-compatible | Native, less skill-marketplace-oriented |
| Always-loaded context | CLAUDE.md | `.github/copilot-instructions.md`, `*.instructions.md` (glob-scoped) | `.cursor/rules/*.mdc`, AGENTS.md | AGENTS.md (native, "intentionally simpler than CLAUDE.md") | GEMINI.md (legacy) / Antigravity-native equivalent | AGENTS.md (nearest-file-in-tree) | AGENTS.md (falls back to CLAUDE.md if absent) | — |
| MCP support | Native, mature | Native | Native | Native, TOML-configured; can itself run *as* an MCP server | Native | Native | Native | Native |
| Sandbox default | Seatbelt/bubblewrap + network proxy; microVM for cloud sessions | Host-dependent; VS Code-mediated | Hosted VM per background task | Default-on: Seatbelt/Landlock+seccomp/restricted tokens | Seatbelt/Docker-Podman | Dedicated cloud VM per task | Host-dependent | Host-dependent |
| Deployment surfaces | CLI, Desktop, VS Code ext, web | VS Code, GitHub.com, CLI, cloud agent | IDE (fork), CLI (Jan 2026) | CLI, VS Code ext, Desktop (macOS) | CLI, desktop app | Cloud-only, browser/terminal/editor in its own env | CLI, VS Code/JetBrains/Neovim/Zed | IntelliJ-family IDEs |
| Standout strength | Deepest documentation/ecosystem maturity, largest context window tier available | Tightest GitHub-native integration (issues/PRs/Actions) | Best-regarded interactive IDE UX | Strongest published benchmark ceiling (Terminal-Bench) at time of writing, token-efficient | Async multi-agent workflows, large context window | Fullest end-to-end autonomy (plans, codes, tests, deploys unsupervised) | Deepest code-search/graph grounding for large/legacy codebases | Tightest native JetBrains IDE integration |
| Notable 2026 landscape event | Fable/Mythos export-control suspension (unrelated to Claude Code itself, but same vendor) | Moved to usage-based billing June 2026 | Acquired Continue.dev | ~4M weekly active users reported April 2026 | Replaced Gemini CLI at I/O 2026; old product sunset June 18, 2026 | Absorbed Windsurf into Devin Desktop | Spun out from Sourcegraph as standalone company | — |

### Strengths/weaknesses synthesis

- **Editor-embedded tools (Cursor, Windsurf-now-Devin, Continue-now-Cursor, JetBrains Junie)** win on moment-to-moment authoring UX and tightest IDE integration (file `07`'s LSP/Task/Debug API advantages are most fully realized here), but are more exposed to the rules-file-injection class of attack precisely because they auto-load repo-committed configuration by default for convenience.
- **CLI-first tools (Claude Code, Codex CLI)** win on scriptability, CI/headless integration, and — per the sandboxing comparison above — tend to have the most mature, default-on isolation, likely because their target use case (long unattended runs) forced the security investment earlier.
- **Fully autonomous cloud agents (Devin, GitHub Copilot's cloud/coding agent, Replit Agent)** win on "delegate an entire task and walk away" workflows, at the cost of requiring the most trust and the most robust approval-gate design, since there is no human watching in real time.
- **Code-search-grounded tools (Amp, Sourcegraph's own graph search)** win specifically on large/legacy codebase comprehension, where retrieval quality (file `06`) matters more than raw generation quality.
- **No single tool wins on governance/organization-wide skill management** — this remains the shared, unresolved gap across the entire category (file `10`, `19`).

## Deliverable 1 — Vendor-Neutral Reference Architecture (recap)

See file `00`, section 3 for the full diagram. In one sentence: **an always-loaded context plane (AGENTS.md/rules) plus an on-demand skill plane, both feeding a tool/MCP layer that executes inside a sandboxed/dev-container environment, with repository context retrieval and observability wrapping the whole loop.**

## Deliverable 10 — Design Patterns, Anti-Patterns, Migration Strategies, and Future Trends

### Patterns

1. **AGENTS.md as router**: always-loaded file explicitly tells the agent when to reach for which skill (file `01`, `05`) — empirically validated to roughly 26-point pass-rate improvement (53%→79%) over unguided skill discovery.
2. **Single canonical instruction source + generated overlays**: solves the five-file-duplication problem (file `19`) without waiting for org-catalog tooling to mature.
3. **Dev Container as security boundary, not just reproducibility tool**: run high-autonomy agents only inside isolated, network-egress-limited containers (file `07`, `10`).
4. **Separate implementer/reviewer/tester agent roles** for anything above trivial complexity (file `09`) — mirrors why human code review isn't done by the PR's own author.
5. **Structured tools over raw terminal invocation** wherever a structured tool exists (file `05`, `06`) — better safety enforcement, better output parsing, better agent reasoning.

### Anti-patterns

1. **Auto-loading unreviewed, externally-sourced skills/rules files** — the single highest-frequency root cause across the CVE catalog in file `10`.
2. **Cramming deep procedural knowledge into an always-loaded file** instead of a skill — burns tokens every turn for content only occasionally needed.
3. **Five divergent instruction files per repo**, unsynced (file `19`).
4. **Unbounded fix-retry loops** on validation failure with no escalation bound (file `03`).
5. **Trusting text-based prompt restrictions as a security control** — the documented Cursor 70-file-deletion incident (file `10`) despite an explicit "DO NOT" instruction is the canonical cautionary example.
6. **Enabling too many MCP servers/tools simultaneously**, degrading tool-selection accuracy (file `08`).
7. **Treating agent-authored code telemetry as a separate silo** from normal CI/PR observability (file `09`).

### Migration strategies

- Consolidate legacy tool-specific rule files (`.cursorrules`, `.windsurfrules`, `.clinerules`) toward **AGENTS.md** as the primary always-loaded source, keeping thin, generated tool-specific files only where a tool genuinely lacks AGENTS.md support (file `19`, section 18.2).
- When migrating between agent vendors entirely (as forced by events like the Gemini CLI → Antigravity or Windsurf → Devin consolidations), the SKILL.md and AGENTS.md portability properties (file `01`, `02`) mean **skill and always-loaded-context investment survives the migration**; only vendor-specific frontmatter fields and MCP configuration syntax need to be redone.
- Treat any single-vendor-specific investment (a vendor's proprietary memory feature, a vendor-only plugin format) as higher migration risk and budget for it accordingly, given the demonstrated pace of vendor consolidation in this category.

### Future trends worth tracking

- **Organization-level skill/rule distribution** maturing from "coming soon" to shipped, closing the governance gap that is today the clearest weakness of the whole ecosystem relative to enterprise business-agent platforms (companion package).
- **Formal quality/security scoring for public skill marketplaces**, analogous to the enterprise-side SkillsBench development (companion package file `06`) — early, narrower precedents already exist (`gh skill`'s spec-validation `--dry-run`, security-audited marketplaces like the ones referenced in file `18`) and are likely to broaden.
- **Convergence toward AGENTS.md + SKILL.md as the durable, cross-vendor standards**, with individual vendors competing on harness quality, sandboxing, and IDE integration rather than on proprietary instruction formats — the clearest strategic signal from this entire research window is that betting on open standards over any single vendor's proprietary format is the lower-risk long-term choice.
- **Security tooling catching up to the attack research** — expect skill/rules-file scanning (semantic, not just pattern-matching, given documented evasion of simple regex scanners) to become a standard CI check, the coding-agent-specific analogue of the enterprise AST10 mitigations (companion package file `09`).
