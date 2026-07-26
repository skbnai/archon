---
title: "MCP Integration & Memory"
date_created: 2026-07-24
last_reviewed: 2026-07-24
status: current
domain: agentic-systems
doc_type: guide
topic_id: mcp-integration-and-memory
supersedes: ["docs/agentic-systems/skill/coding/08-mcp-integration-and-memory.md"]
---

# Part 11 — MCP Integration & Part 12 — Memory

## PART A: MCP Integration for Coding Agents

### 11.1 Common MCP servers in coding workflows

| Server | Typical capability exposed |
| --- | --- |
| Filesystem MCP | Sandboxed file access, sometimes used instead of a fully-native filesystem tool for extra policy control |
| Git MCP | Structured git operations, sometimes preferred over native git for auditable, policy-checked commits |
| GitHub MCP | Issues, PRs, Actions status, code search — the most heavily used external-system MCP server in this domain |
| Jira / Linear MCP | Ticket read/update — closes the loop between "what was asked" and "what the agent is doing" |
| Browser MCP | Navigate, screenshot, extract — used for visual/E2E validation and for agents researching live documentation |
| Database MCP | Query execution against dev/staging databases, typically read-only by policy default |
| Slack MCP | Notify, read thread context — used in background-agent workflows (file `09`) to report status without a human watching a terminal |
| Cloud (AWS/Azure/GCP) MCP | Provision/inspect cloud resources — high blast-radius, should default to read-only/plan-only unless explicitly elevated |
| Kubernetes MCP | Cluster inspection, sometimes apply — same elevated-risk profile as cloud MCP |
| Terraform MCP | Plan/apply IaC changes — plan should be default; apply should require explicit human approval by policy |

### 11.2 Discovery, registration, and versioning

- **Discovery**: most coding-tool MCP configuration is *static*, declared in a config file (`.mcp.json`, `config.toml` for Codex, VS Code's `mcp.json`) rather than dynamically discovered at runtime — a notable contrast with the more dynamic enterprise registry patterns (companion package file `06`). This reflects the smaller, more stable per-project tool set typical of a single repository versus an enterprise-wide capability catalog.
- **Registration**: adding a server is typically a one-time, explicit developer action (`codex mcp add`, VS Code's `Add Tools` catalog, Docker MCP's one-click catalog install) — deliberately not automatic, since MCP servers are a genuine trust boundary (file `10`).
- **Capabilities**: an MCP server advertises its available tools/resources at connection time; well-built coding-agent harnesses cap how many tools are surfaced to the model at once — community guidance explicitly warns that enabling too many MCP servers simultaneously ("if you enable too many MCP servers, Copilot chokes") degrades tool-selection accuracy, echoing the enterprise "tool overloading" anti-pattern (companion package file `07`).
- **Authentication**: increasingly handled via in-agent OAuth flows with automatic callback handling rather than manual token pasting — a maturity improvement observed broadly across 2026 tooling updates.
- **Authorization**: scoped per-server, and should be scoped further per-tool where the server supports it (read-only DB access vs. full write access being the canonical example).
- **Trust**: this is the area with the most documented incidents (file `10`) — an MCP server, once added, is generally treated as trusted infrastructure by the agent, which is exactly what attacks like "Toxic Agent Flow" (GitHub MCP exploited via issue-body content) exploit. The mitigation isn't "don't use MCP," it's per-file/per-action confirmation rather than blanket, connection-level trust.
- **Versioning**: less formalized in coding-agent MCP usage than in enterprise platforms; a good practice gap to flag for any org standardizing internal MCP servers — pin server versions in the same config file that declares the server, and treat server upgrades with the same regression-testing discipline as any dependency bump.
- **Dynamic loading**: some harnesses (Codex's MCP-server-as-a-tool pattern, where Codex CLI itself is exposed as an MCP server to a *different* orchestrating agent) show a more dynamic, composable pattern emerging — worth watching as the ecosystem matures.
- **Tool filtering**: several tools now let a developer enable only a subset of a given server's tools (Azure DevOps MCP Server's "configure a subset of available tools to control which actions agents can perform" is a direct, cited example) — this is good practice universally, not vendor-specific, and should be the default configuration stance rather than an opt-in hardening step.

## PART B: Memory Architecture

### 12.1 Memory scopes

| Scope | Typical lifetime | Example content |
| --- | --- | --- |
| **Conversation/session** | Single chat session | Current task's working state, files touched so far |
| **Workspace/repository** | Persistent, tied to the repo | Learned conventions, past decisions the agent should remember for this project specifically |
| **Developer/personal** | Persistent, tied to the individual | Personal preferences ("I prefer functional components"), independent of which repo is open |
| **Organization** | Persistent, shared across the org | Org-wide standards — the least mature of these scopes in current tooling (same "coming soon" gap noted in file `07`/`11`) |
| **Long-term** | Survives across many sessions | Distilled, durable facts (a specific auto-memory feature seen in community tooling stores "user/feedback/project notes" in a persistent directory specifically so the agent doesn't relearn the same corrections every session) |
| **Short-term/task** | Scoped to the current multi-step task only | Intermediate plan state, not meant to persist once the task completes |

### 12.2 What should be remembered

- **Corrections the developer has made more than once** — a clear signal the agent should internalize the preference rather than requiring restatement (this is precisely the value proposition of the "auto memory" pattern observed in current tooling).
- **Project-specific conventions not captured in AGENTS.md yet** — memory can function as a staging area; a repeatedly-reinforced memory item is a strong candidate for graduating into an actual, reviewed AGENTS.md entry.
- **Stable facts about the environment** (build commands, test invocation patterns) that are expensive to rediscover each session.

### 12.3 What should never be remembered

- **Secrets and credentials** — regardless of scope; a memory store is not a secrets manager and should never become a de facto one, especially given that memory files are often plaintext and sometimes inadvertently committed.
- **Sensitive user/customer data** encountered incidentally while working in a codebase that touches production-adjacent data.
- **One-off, task-specific detail with no future value** — indiscriminately persisting everything degrades future-session context quality and creates exactly the "over-retrieval" problem discussed in file `06`, just at the memory layer instead of the retrieval layer.
- **Anything the developer explicitly asked not to be retained** — should be a hard, enforced rule, not just a norm, given how easily "remember this for later" and "forget this immediately" can otherwise blur together in an unstructured memory store.

### 12.4 Governance note

Memory in coding-agent tooling today is overwhelmingly **local and unmanaged** compared to the increasingly formal memory architectures emerging in enterprise agent platforms (companion package: AWS AgentCore's episodic memory, Azure Foundry's procedural memory). For teams operating at scale, this is a gap worth closing deliberately: treat repository-scoped memory with the same review discipline as AGENTS.md (file `10`), since a poisoned or incorrect memory entry persists and compounds exactly the way a bad standing instruction does.

## Related

- [VS Code & Dev Containers Integration](23-vscode-devcontainers-integration.md) — the previous section in this series.
- [Multi-Agent Skills & Observability](25-multi-agent-and-observability.md) — the next section in this series.
