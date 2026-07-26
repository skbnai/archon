---
title: "Skills vs. MCP & the Full Responsibility Stack"
doc_type: reference-architecture
domain: agentic-systems
status: current
topic_id: skills-tools-mcp-relationship
date_created: 2026-07-24
last_reviewed: 2026-07-24
supersedes:
  - docs/agentic-systems/skill/coding/04-skills-tools-mcp-relationship.md
tags:
  - agentic-systems
  - skill
  - coding-tools
  - research
---

# Part 5 — Skills vs. MCP & the Full Responsibility Stack (+ Deliverable 3)

## 5.1 The layered stack for coding agents

```mermaid
graph TD
    A["Skill<br/>(behavior: when/why/how to approach a class of task)"]
    B["Tool<br/>(built-in capability: read/write file, run terminal, git op)"]
    C["MCP Server<br/>(external system access: GitHub, Jira, DB, browser, cloud)"]
    D["IDE / Extension<br/>(UI surface, chat participant, editor commands)"]
    E["Dev Container / Sandbox<br/>(reproducible, isolated execution environment)"]
    F["Language Server<br/>(symbol/type/diagnostic ground truth)"]
    
    A -->|references| B
    B -->|OR reaches beyond built-ins via| C
    C -->|runs inside| D
    D -->|which may run inside| E
    E -->|on top of| F
```

## 5.2 What belongs in each layer

| Layer | Owns | Does NOT own |
| --- | --- | --- |
| **Skill** | Procedure, sequencing, project-specific judgment, output-format conventions | File I/O, process execution, protocol handshakes |
| **AGENTS.md/Rules** | Always-true facts and boundaries (stack, conventions, verification steps) | Deep multi-step procedures (that's a Skill's job — see file `01`) |
| **Tool** (built-in) | Filesystem, terminal, git, basic search (grep/ripgrep) — typically shipped natively by the harness | Business/procedural judgment about when to use them |
| **MCP Server** | Auth boundary + protocol framing for any *external* system: GitHub issues/PRs, Jira, Linear, databases, browsers, cloud providers, Kubernetes, Terraform | Editor UI, language-specific diagnostics |
| **IDE/Extension** | Chat UI, inline suggestions, commands, editor lifecycle hooks, workspace/task/debug APIs | Deep procedural knowledge (delegates to Skills), external system access (delegates to MCP) |
| **Language Server (LSP)** | Ground-truth symbol resolution, type info, diagnostics, go-to-definition | Anything LLM-mediated — LSP is deterministic, non-generative infrastructure that *tools* consult |
| **Dev Container/Sandbox** | Reproducible OS/dependency environment, isolation boundary | Application logic, procedural knowledge |

## 5.3 The specific chain named in the brief

```
Skill → Tool → MCP → IDE → CLI → Git → Filesystem → Terminal → Docker →
Cloud → Language Server
```

Mapped concretely:

- **Skill** references a **Tool** by name/intent in its instructions ("use the test-runner tool").
- The **Tool** is exposed by either the **IDE** (VS Code's built-in file/terminal/git tools) or the **CLI** (Claude Code's, Codex's own built-in tool set) — largely redundant implementations of the same primitives across surfaces.
- **Git** and **Filesystem** are near-universally *built-in* tools, not MCP-mediated, in every mainstream coding agent studied — this is a deliberate design choice for latency and reliability; MCP is reserved for genuinely external systems.
- **Terminal** access is likewise typically native, wrapped in a sandbox (file `10`) rather than routed through MCP.
- **Docker** and **Cloud** access is a mixed picture: some agents shell out to the `docker`/cloud CLI as a terminal command; others use a dedicated MCP server (Docker's own MCP catalog exposes 200+ verified MCP servers, explicitly positioned as the more secure and governed path versus raw shell access).
- **Language Server** sits underneath tools, not beside them — an agent's "find all references" tool is typically implemented *using* LSP under the hood, but the model never talks to the language server directly.

## 5.4 Avoiding duplication across this stack

The most common coding-assistant-specific duplication failure mode, not present in the same form in enterprise business agents: **the same primitive capability (file read, terminal exec, git diff) is reimplemented slightly differently by every IDE/CLI surface**, because each vendor ships its own built-in tool set rather than sharing one. This is a structural, largely unavoidable duplication (each harness needs its own sandboxed implementation), but it means:

- **Skills should never assume a specific tool name/signature** beyond the small set of near-universal primitives (read, write, search, run-command, git-diff) — a skill written against one vendor's exact tool name will silently fail to find that tool on another vendor's harness, defeating the entire cross-tool portability promise of SKILL.md.
- **MCP servers are the correct place to consolidate genuinely duplicated *external-system* integrations.** If three different teams each hand-roll a "call our internal deployment API" skill with embedded curl commands, that's a sign a shared internal MCP server is missing (directly analogous to the enterprise "avoid duplicate wrappers" guidance, companion package file `06`).
- **Don't build a skill to wrap a single MCP tool 1:1.** If a skill's entire content is "call the `create_pull_request` MCP tool with these arguments," that's a thin, low-value wrapper — the tool's own description (file `05`) should already carry that guidance.

## 5.5 Deliverable 3 — Responsibility Matrix

| Question | Skill | AGENTS.md/Rules | Tool | MCP Server | Extension/IDE | Language Server | Dev Container |
| --- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| Defines *when/why* to approach a task a certain way | ✅ | partial (boundaries only) | | | | | |
| States facts true on every single turn | | ✅ | | | | | |
| Executes a file read/write | | | ✅ | possible | | | |
| Executes a terminal command | | | ✅ | possible | | | |
| Reaches GitHub/Jira/a database/a browser | | | | ✅ | | | |
| Provides chat UI / inline suggestions | | | | | ✅ | | |
| Resolves symbols/types/diagnostics | | | | | | ✅ | |
| Guarantees a reproducible environment | | | | | | | ✅ |
| Isolates the agent from the host OS | | | | | | | ✅ |
| Should be code-reviewed like source | ✅ (if committed) | ✅ | n/a (harness-provided) | server config, yes | n/a | n/a | ✅ (devcontainer.json) |
| Should be portable across agent vendors | ✅ (spec-conformant) | ✅ (if AGENTS.md) | rarely | ✅ (protocol-native) | ❌ | ❌ | ✅ (devcontainer.json spec) |

## Related

- [Skill Discovery & Execution Lifecycle](19-discovery-and-execution-lifecycle.md) — the previous section in this series.
- [Tool Definitions & Instructions Engineering](21-tool-definitions-and-instructions-engineering.md) — the next section in this series.
