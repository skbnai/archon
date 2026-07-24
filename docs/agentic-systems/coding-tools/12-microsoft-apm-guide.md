---
title: 'Microsoft APM — Zero to Mastery'
doc_type: guide
domain: agentic-systems
topic_id: microsoft-apm-guide
status: current
date_published: 2026-07-24
last_reviewed: 2026-07-24
supersedes:
  - ../knowledge-docs/docs/coding-tools/github-copilot/microsoft-apm-guide.md
tags:
  - microsoft-apm
  - github-copilot
  - package-management
---

# Microsoft APM — Zero to Mastery

**APM** — **Agent Package Manager** — Open Source · MIT License

## Agent Package Manager: Zero to Mastery

The complete guide to APM — Microsoft's open-source dependency manager for AI agents. Declare once, deploy everywhere.

- **6** Primitives
- **10+** AI Clients
- **1** Manifest File
- **∞** Packages

## 01 — What is APM?

**APM (Agent Package Manager)** is an open-source, community-driven dependency manager for AI agents — developed under the Microsoft GitHub organization and MIT-licensed. Think of it as `npm` or `pip`, but instead of managing code libraries, it manages everything an AI agent needs to be productive on your project: instructions, skills, prompts, MCP server configs, hooks, and plugins.

With one `apm.yml` manifest file, you describe every agentic dependency your project needs. Running `apm install` deploys that context to all your AI tools simultaneously — GitHub Copilot, Claude Code, Cursor, Gemini, Codex, Windsurf, and more.

```
apm.yml manifest
    ↓
apm install
    ↓
.github/ .claude/ .cursor/
    ↓
Every agent configured ✓
```

APM was created by **@danielmeppiel** and is maintained under the Microsoft GitHub org. It is MIT-licensed and fully open source.

## 02 — Why APM Exists

AI coding agents need rich context to work well — architecture standards, coding conventions, reusable prompt templates, tool integrations. But today every developer sets this up manually, locally, and inconsistently. Nothing is portable or reproducible.

APM solves this with four guarantees:

**📦 Reproducibility**: A lockfile pins exact commits. Any developer who clones your repo gets byte-identical agent configuration.

**🌐 Portability**: One manifest deploys context to Copilot, Claude, Cursor, Gemini, Codex, OpenCode, and Windsurf simultaneously.

**🔗 Transitive Deps**: Packages can depend on packages. APM resolves the full dependency tree automatically, just like npm.

**🛡️ Governance**: Policy files enforce allowed packages, MCP servers, and trust levels — from enterprise down to repo level.

## 03 — Core Concepts

APM introduces a small set of terms that map directly to familiar software packaging concepts:

**📄 apm.yml**: Your manifest. Declares the package name, version, agent dependencies, and MCP servers. Equivalent to `package.json`.

**🔒 apm.lock.yaml**: The lockfile. Pins every resolved dependency to its exact git commit hash for deterministic installs.

**📁 apm_modules/**: Downloaded package cache — analogous to `node_modules/`. Never edit these directly.

**🗂️ .apm/ directory**: Your project's own agent primitives — the source code for your agent workflows. Local content always wins on collision.

**🧩 Primitives**: The six building blocks: agents, instructions, skills, prompts, hooks, and plugins.

**🏪 Marketplaces**: Curated registries (like `github/awesome-copilot`) you can search and install from with shorthand syntax.

## 04 — Installation

APM supports multiple installation methods. Choose the one that matches your environment:

**macOS / Linux — one-liner**

```bash
curl -sSL https://aka.ms/apm-unix | sh
```

**Windows — PowerShell**

```powershell
irm https://aka.ms/apm-windows | iex
```

**Homebrew (macOS/Linux)**

```bash
brew install microsoft/apm/apm
```

**Scoop (Windows)**

```powershell
scoop bucket add apm https://github.com/microsoft/scoop-apm
scoop install apm
```

**pip**

```bash
pip install apm-cli
```

**Verify installation**

```bash
apm --version
# Agent Package Manager (APM) CLI version 0.x.x
```

## 05 — Quick Start

Three commands. Three minutes. Your entire team's AI agents learn your project's standards:

1. **Initialize** — creates `apm.yml` in your repo

```bash
apm init
```

2. **Install a package** — APM downloads, resolves deps, and deploys files to all agent config dirs

```bash
apm install microsoft/apm-sample-package#v1.0.0
```

3. **Compile for Copilot** — assembles all instructions into `.github/copilot-instructions.md`

```bash
apm compile -t copilot
```

After install, APM deploys primitives to **every detected agent directory simultaneously**:

```
my-project/
|
+-- apm.yml                    # manifest (commit this)
+-- apm.lock.yaml              # lockfile (commit this)
+-- apm_modules/               # cache (gitignore)
+-- .github/                   # GitHub Copilot + Codex
|   +-- instructions/
|   +-- prompts/
+-- .claude/                   # Claude Code
|   +-- commands/
+-- .cursor/                   # Cursor
|   +-- rules/
|   +-- agents/
+-- .opencode/                 # OpenCode
+-- .gemini/                   # Gemini CLI
```

Commit `apm.yml`, `apm.lock.yaml`, and the deployed files in `.github/`. New contributors get full agent context the moment they clone — before running `apm install`.

## 06 — The apm.yml Manifest

The manifest is the single source of truth for your project's agent configuration. Here is a fully annotated example:

```yaml
# Package Identity --------------------
name: my-backend-api
version: 2.1.0
description: Node.js REST API with agent standards
author: platform-team

# Agent Dependencies ------------------
dependencies:
  apm:
    - anthropics/skills/frontend-design      # Skills from any git repo/path
    - github/awesome-copilot/plugins/context-engineering  # Plugin from marketplace
    - microsoft/apm-sample-package#v1.0.0    # Pin to specific git tag
    - github/awesome-copilot/agents/api-architect.agent.md # A specific agent file

# MCP Servers ------------------------
mcp:
  - name: io.github.github/github-mcp-server
    transport: http
  - name: io.github.modelcontextprotocol/postgres
    transport: stdio
    args: [postgresql://localhost/mydb]

# Scripts ----------------------------
scripts:
  postinstall: apm compile -t copilot
```

Always pin production dependencies to a `#tag` or commit SHA. Unpinned dependencies (latest) can break silently when upstream packages update.

## 07 — The 6 Agent Primitives

APM packages are composed of six primitive types. Each serves a distinct purpose in the agent's context window:

**🤖 Agents**: Sub-agent definitions specialized for specific tasks — e.g., an "api-architect" agent with domain expertise.

**📋 Instructions**: Rules and guidelines always present in the agent's context. Deployed to `copilot-instructions.md`, `.cursorrules`, etc.

**🛠️ Skills**: Concise how-to guides for a specific task. Follow the Agent Skills spec and are reusable across projects.

**💬 Prompts**: Reusable prompt templates for common tasks — accessibility audits, code reviews, design reviews.

**🪝 Hooks**: Scripts invoked at specific points in the agent's execution flow (pre-commit, post-tool-call, etc.).

**🔌 Plugins**: Pre-packaged bundles of skills, prompts, and MCP servers. Exportable as standard `plugin.json` files.

**Example: Writing an Instruction**

`.apm/instructions/api-standards.instructions.md`

```markdown
---
applyTo: "src/api/**/*.ts"
---

# API Design Standards

- All endpoints must return { data, error, meta } envelope format
- Use 422 Unprocessable Entity for validation errors
- Every route must have an OpenAPI JSDoc annotation
- Rate limiting headers (X-RateLimit-*) are mandatory on public routes
```

## 08 — MCP Server Management

APM is the only tool that manages MCP (Model Context Protocol) servers as versioned, policy-gated dependencies. When you add an MCP server to `apm.yml`, APM wires it into every detected client automatically.

**HTTP (remote) MCP server**

```yaml
dependencies:
  mcp:
    - name: io.github.github/github-mcp-server
      transport: http  # connects over HTTPS
```

**stdio (local Docker) MCP server**

```yaml
dependencies:
  mcp:
    - name: io.github.modelcontextprotocol/postgres
      transport: stdio
      args: ["postgresql://localhost/mydb"]
```

Every MCP server in a transitive dependency triggers an **explicit trust prompt** before installation. This is enforced automatically — no opt-in required. Policy files can pre-approve trusted servers org-wide.

## 09 — Creating Your Own Packages

Packages are just git repositories with an `apm.yml` and primitives in a `.apm/` directory. Publishing means pushing to GitHub (or any git host).

1. **Scaffold the package structure**

```bash
apm init my-team-standards
```

2. **Add primitives to `.apm/`** — instructions, skills, prompts, agents, hooks
3. **Declare any dependencies your package itself needs in `apm.yml`**
4. **Commit, tag, and push to GitHub**

```bash
git tag v1.0.0
git push origin v1.0.0
```

5. **Anyone can now install it**

```bash
apm install your-org/my-team-standards#v1.0.0
```

**Package structure**

```
my-team-standards/
|
+-- apm.yml
+-- .apm/
    +-- instructions/
    |   +-- coding-standards.instructions.md
    +-- skills/
    |   +-- deploy-to-azure.md
    +-- prompts/
    |   +-- pr-review.prompt.md
    +-- agents/
        +-- backend-specialist.agent.md
```

Use `apm pack` to bundle your package into a distributable `.tar.gz` archive — useful for air-gapped environments or Claude Code plugin marketplaces.

## 10 — AI Client Compatibility

APM supports two integration levels. Native clients get the full primitive set; compiled clients receive a unified instructions file.

| Client | Support Level | Config Deployed To |
|--------|---|---|
| GitHub Copilot | ✓ Native | `.github/instructions/, prompts/, agents/` |
| Claude Code | ✓ Native | `.claude/commands/` |
| Cursor | ✓ Native | `.cursor/rules/, agents/` |
| OpenCode | ✓ Native | `.opencode/agents/, commands/` |
| Gemini CLI | ✓ Native | `.gemini/commands/` |
| Windsurf | ✓ Native | `.windsurf/` |
| Codex CLI | ⟳ Compiled | `AGENTS.md` via `apm compile` |
| Gemini (compile) | ⟳ Compiled | `GEMINI.md` via `apm compile` |

Run `apm compile -t codex` to generate `AGENTS.md` for compiled targets. This aggregates all instructions into a single file each tool can consume.

## 11 — Security & Policy

APM has a security-first design with protections applied by default — no configuration required:

- **✓ Content hash pinning** — `apm.lock.yaml` records SHA hashes for every file. Tampering is detected on any subsequent install.
- **✓ Hidden Unicode scan** — every install automatically scans for invisible Unicode characters (prompt injection vectors). Packages with critical findings are blocked.
- **✓ MCP trust prompts** — transitive MCP servers are gated behind explicit trust confirmation before touching disk.
- **✓ Policy enforcement** — `apm-policy.yml` lets organizations define allowed packages, blocked sources, and MCP allowlists. Policy is enforced at install time.
- **✓ Tighten-only inheritance** — policy flows enterprise → org → repo. Child policies can only be more restrictive, never more permissive.

**Example apm-policy.yml**

```yaml
# Org-level policy — enforced on all repos
version: 1
allow:
  sources:
    - github.com/my-org/**
    - github.com/microsoft/apm-sample-package
deny:
  mcp:
    - *.untrusted-domain.com
require:
  pinned-versions: true  # block floating refs
```

## 12 — CI/CD Integration

Use `microsoft/apm-action` to install and validate agent dependencies in GitHub Actions — zero configuration required.

**Basic install in CI**

```yaml
jobs:
  agent-setup:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: microsoft/apm-action@v1
        with:
          compile: 'true'  # generate AGENTS.md after install
```

**Pack and publish a plugin bundle**

```yaml
steps:
  - uses: actions/checkout@v4
  - uses: microsoft/apm-action@v1
    id: pack
    with:
      pack: 'true'
      bundle-format: 'plugin'  # for Claude Code plugin marketplace
  - uses: actions/upload-artifact@v4
    with:
      name: agent-bundle
      path: ${{ steps.pack.outputs.bundle-path }}
```

The action installs APM CLI, reads your `apm.yml`, runs `apm install`, and blocks on any hidden-Unicode findings — all in one step. No manual APM setup required in CI.

## 13 — Enterprise Features

APM ships with an enterprise-grade governance layer covering the full org hierarchy:

**🏢 Org-wide Packages**: Publish internal packages to your org's git host. Developers install with the same `apm install org/package` syntax.

**🔏 Private Packages**: APM supports GitLab, Bitbucket, Azure DevOps, Gitea, Gogs, and GitHub Enterprise as package hosts. Authentication via PAT or OIDC.

**🛰️ Registry Proxy**: Air-gapped environments can run a registry proxy that mirrors approved packages internally, blocking direct public access.

**📊 Audit & Rulesets**: GitHub Rulesets integration lets platform teams enforce `apm-policy.yml` compliance at the repo level via branch protection rules.

**Three enterprise adoption ramps**

```
Consumer ramp   → Install community packages, run apm install, commit lockfile
Producer ramp   → Package your team's standards, share across repos
Governance ramp → Add policy files, CI gating, registry proxy for air-gap
```

## 14 — CLI Quick Reference

All major commands:

```bash
# Project setup ------------------------------------
apm init [name]                               # create apm.yml in current dir
apm install                                   # install all deps from apm.yml
apm install org/repo#tag                      # install + pin a specific package
apm install pkg@marketplace                   # install from a marketplace shorthand
apm update                                    # update all deps to latest
apm update org/repo                           # update a specific package

# Compilation --------------------------------------
apm compile                                   # compile instructions for all targets
apm compile -t copilot                        # compile only for GitHub Copilot
apm compile -t codex                          # generate AGENTS.md

# Package authoring --------------------------------
apm pack                                      # bundle into .tar.gz
apm pack -o build --format plugin             # Claude Code plugin format

# Marketplace --------------------------------------
apm marketplace add github/awesome-copilot    # add marketplace source
apm marketplace list                          # list available marketplaces
apm search "terraform@awesome-copilot"        # search packages
apm marketplace browse awesome-copilot        # browse marketplace

# Context generation -----------------------------------------------
agentrc                                       # auto-generate instructions from codebase
```

**agentrc** is APM's companion tool that analyzes your actual codebase — architecture, conventions, build commands — and generates high-quality `.instructions.md` files automatically. Start there before writing instructions by hand.

---

Built from the official [microsoft.github.io/apm](https://microsoft.github.io/apm/) documentation & [github.com/microsoft/apm](https://github.com/microsoft/apm)

MIT License · microsoft/apm · May 2026
