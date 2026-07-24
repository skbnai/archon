---
status: current
title: "GitHub Copilot Zero to Hero"
date_created: 2026-07-07
doc_type: guide
domain: agentic-systems
topic_id: github-copilot-zero-to-hero
tags: ["coding-tools", "github-copilot"]
last_reviewed: 2026-07-24
covers_version: "as of 2026-07-10"
supersedes:
  - docs/coding-tools/github-copilot/github-copilot-zero-to-hero.md
---

## Why This Matters

GitHub Copilot transforms how developers write code — from a code-completion tool to a full agentic development platform. Whether you're new to AI-assisted development or scaling Copilot across an enterprise, understanding its capabilities, models, governance, and best practices is essential for maximizing productivity while controlling costs.

# GitHub Copilot: Zero to Hero

The complete guide — from first suggestion to enterprise-scale AI-assisted development. Audience: developers new to Copilot through enterprise power users and platform engineers.

---

## Table of Contents

1. [What Is GitHub Copilot?](#1-what-is-github-copilot)
2. [Plans Comparison](#2-plans-comparison)
3. [Setup and Installation](#3-setup-and-installation)
4. [Model Selection](#4-model-selection)
5. [Code Completion](#5-code-completion)
6. [Chat Interface](pathname:///archon/agentic-systems/coding-tools/parts/11-github-copilot-zero-to-hero-part2#6-chat-interface)
7. [Agent Mode](pathname:///archon/agentic-systems/coding-tools/parts/11-github-copilot-zero-to-hero-part2#7-agent-mode)
8. [MCP Integration](pathname:///archon/agentic-systems/coding-tools/parts/11-github-copilot-zero-to-hero-part2#8-mcp-integration)
9. [Copilot Code Review](pathname:///archon/agentic-systems/coding-tools/parts/11-github-copilot-zero-to-hero-part2#9-copilot-code-review)
10. [Copilot Coding Agent](pathname:///archon/agentic-systems/coding-tools/parts/11-github-copilot-zero-to-hero-part2#10-copilot-coding-agent)
11. [AI Credits Billing](pathname:///archon/agentic-systems/coding-tools/parts/11-github-copilot-zero-to-hero-part2#11-ai-credits-billing)
12. [Enterprise Features](pathname:///archon/agentic-systems/coding-tools/parts/11-github-copilot-zero-to-hero-part3#12-enterprise-features)
13. [Parallelism](pathname:///archon/agentic-systems/coding-tools/parts/11-github-copilot-zero-to-hero-part3#13-parallelism)
14. [Token and Cost Optimization](pathname:///archon/agentic-systems/coding-tools/parts/11-github-copilot-zero-to-hero-part3#14-token-and-cost-optimization)
15. [Guardrails](pathname:///archon/agentic-systems/coding-tools/parts/11-github-copilot-zero-to-hero-part3#15-guardrails)
16. [Explainability](pathname:///archon/agentic-systems/coding-tools/parts/11-github-copilot-zero-to-hero-part3#16-explainability)
17. [Human-in-the-Loop (HITL)](pathname:///archon/agentic-systems/coding-tools/parts/11-github-copilot-zero-to-hero-part3#17-human-in-the-loop-hitl)
18. [RAI and Compliance](pathname:///archon/agentic-systems/coding-tools/parts/11-github-copilot-zero-to-hero-part4#18-rai-and-compliance)
19. [Best Practices](pathname:///archon/agentic-systems/coding-tools/parts/11-github-copilot-zero-to-hero-part4#19-best-practices)
20. [Antipatterns](pathname:///archon/agentic-systems/coding-tools/parts/11-github-copilot-zero-to-hero-part4#20-antipatterns)
21. [Keyboard Shortcuts](pathname:///archon/agentic-systems/coding-tools/parts/11-github-copilot-zero-to-hero-part4#21-keyboard-shortcuts)
22. [Troubleshooting](pathname:///archon/agentic-systems/coding-tools/parts/11-github-copilot-zero-to-hero-part4#22-troubleshooting)

---

## 1. What Is GitHub Copilot?

GitHub Copilot is an AI pair programmer embedded directly in your development environment. It started as an inline code-completion tool in 2021 and has evolved into a full agentic development platform — capable of reading your codebase, planning work, implementing changes across multiple files, running terminal commands, reviewing pull requests, and autonomously resolving GitHub issues.

**Core value proposition:**

- **Inline completions**: ghost-text suggestions as you type, from single lines to whole functions.
- **Chat interface**: conversational AI for code explanation, debugging, and generation.
- **Agent mode**: autonomous multi-step task execution — reads files, proposes edits, runs commands, monitors output, self-corrects.
- **Code review**: agentic PR review that traverses cross-file dependencies before commenting.
- **Coding agent**: assign a GitHub issue to copilot and receive an implemented PR.

**What Copilot is NOT:**

- A replacement for code review or engineering judgment.
- Guaranteed-correct output — all suggestions require human validation.
- A search engine — it generates, it does not retrieve verified documentation.

---

## 2. Plans Comparison

### Overview Table

| Plan | Price | Best For | AI Credits | Key Features |
|---|---|---|---|---|
| Free | $0 | Individuals exploring Copilot | 2,000 completions/month | Inline completions, limited chat, no agent mode |
| Pro | $10/user/month | Individual developers | Unlimited completions, 300 premium requests/month | All completions, chat, agent mode, code review |
| Business | $19/user/month | Teams and organizations | 1,900 credits/user/month pooled | Pro features + admin console, policy controls, audit logs |
| Enterprise | $39/user/month | Large enterprises | 3,900 credits/user/month pooled | Business features + codebase indexing, fine-tuned models, IP indemnification, DPA |

### Feature Matrix

| Feature | Free | Pro | Business | Enterprise |
|---|---|---|---|---|
| Inline code completions | Limited | Unlimited | Unlimited | Unlimited |
| Multi-model selection (GPT-4o, Claude, Gemini) | No | Yes | Yes | Yes |
| Chat in IDE | Limited | Yes | Yes | Yes |
| Agent mode | No | Yes | Yes | Yes |
| Coding agent (issue → PR) | No | Yes | Yes | Yes |
| Agentic code review | No | Yes | Yes | Yes |
| MCP server support | No | Yes | Yes | Yes |
| GitHub.com Copilot chat | No | Yes | Yes | Yes |
| Admin console + seat management | No | No | Yes | Yes |
| Organization policy controls | No | No | Yes | Yes |
| Audit logs | No | No | Yes | Yes |
| Codebase indexing (knowledge base) | No | No | No | Yes |
| Fine-tuned custom models | No | No | No | Yes |
| IP indemnification | No | No | Yes | Yes |
| Data processing agreement (DPA) | No | No | Partial | Full |
| SSO/SCIM provisioning | No | No | Yes | Yes |
| Enterprise MCP admin (allow-list + audit) | No | No | No | Yes |

**AI Credits (from June 1, 2026)**

- Business: $19/user/month subscription includes 1,900 credits/user/month (1 credit = $0.01 USD).
- Enterprise: $39/user/month includes 3,900 credits/user/month.
- Credits pool at the enterprise level: 100 Business users = 190,000 shared credits/month.
- Premium features (agent mode, code review, coding agent) consume credits beyond the base completion quota.

---

## 3. Setup and Installation

### VS Code Extension

Install via VS Code Extensions marketplace. Search for "GitHub Copilot" (publisher: GitHub). Install both GitHub Copilot (completions + chat) and GitHub Copilot Chat (included in recent versions).

Alternatively, via command line:
```bash
code --install-extension GitHub.copilot
code --install-extension GitHub.copilot-chat
```

After installation, the VS Code bottom status bar shows the Copilot icon. Click the icon to "Sign in to GitHub" and authorize in your browser. Open a code file and start typing — ghost text suggestions appear.

### JetBrains Plugin

1. Open any JetBrains IDE (IntelliJ IDEA, PyCharm, GoLand, WebStorm, Rider).
2. File → Settings (Preferences on macOS) → Plugins → Marketplace.
3. Search "GitHub Copilot" → Install → Restart IDE.
4. Tools → GitHub Copilot → Login to GitHub.

### GitHub.com Copilot Chat

No installation required. Navigate to github.com and click the Copilot icon in the top navigation bar (available on Pro/Business/Enterprise plans). Supports chat with cross-repository context.

### GitHub Copilot App

The Copilot App is an agent-native desktop experience separate from IDE extensions — designed for managing coding agents, reviewing agent-authored PRs, and interacting with Copilot outside the editor context. Install from copilot.github.com.

### Codespaces / Dev Containers

Copilot is pre-configured in GitHub Codespaces for repos with Copilot-enabled organizations. To add to a devcontainer, include this in .devcontainer/devcontainer.json:

```json
{
  "customizations": {
    "vscode": {
      "extensions": [
        "GitHub.copilot",
        "GitHub.copilot-chat"
      ]
    }
  }
}
```

---

## 4. Model Selection

GitHub Copilot supports multiple AI models. Model selection is available in VS Code, JetBrains, and GitHub.com chat on Pro/Business/Enterprise plans.

| Model | Provider | Strengths | Best Use |
| --- | --- | --- | --- |
| GPT-4o | OpenAI | Fast, broad knowledge, excellent for completions | Default for inline completions, quick chat queries |
| Claude Sonnet 4.6 | Anthropic | Strong reasoning, long-context, code quality | Complex multi-file refactors, architecture questions |
| Claude Sonnet 5 | Anthropic | Latest Claude, improved code generation | Agent mode tasks, complex problem-solving |
| Gemini models | Google | Google ecosystem integration, multimodal | GCP-related tasks, Android development |

### When to Use Which Model

**GPT-4o**
- Inline completions (speed matters most).
- Quick questions: "What does this function do?"
- Simple code generation (single-file, well-scoped).
- Most cost-efficient for high-volume completion tasks.

**Claude Sonnet**
- Agent mode tasks spanning multiple files.
- Architecture and design discussions.
- Long-context analysis (large codebases, lengthy documents).
- Security code review requiring deep reasoning.
- When you need the model to explain its reasoning clearly.

**Gemini**
- Google Cloud Platform infrastructure tasks.
- Android/Flutter development.
- Multimodal tasks (e.g., analyzing screenshots of UI).

To switch models in VS Code, click the model selector in the Copilot Chat panel (dropdown at the top) and select the model. For agent mode, the model selector appears in the agent mode panel.

**Cost implication:** Premium models (Claude, Gemini) consume more AI Credits per request than GPT-4o. For high-volume environments, use GPT-4o for completions and reserve premium models for complex chat and agent tasks.

---

## 5. Code Completion

### How It Works

Copilot analyzes the code in your open files and the cursor position, sending context to the model, and returns inline ghost text suggestions. You see them as gray text; pressing Tab accepts.

### Inline Suggestions

```python
# Type the function signature — Copilot suggests the body:
def calculate_compound_interest(principal: float, rate: float, years: int) -> float:
    # Copilot ghost text appears here:
    # return principal * (1 + rate) ** years
```

### Multi-Line Completions

Copilot can complete entire blocks, classes, or functions. Write a descriptive comment, then let Copilot generate:

```python
# Parse a JWT token, verify the signature with a JWKS endpoint,
# extract the user_id claim, and return it or raise AuthError

def extract_user_id_from_token(token: str, jwks_url: str) -> str:
    # Copilot generates the full implementation
```

### Ghost Text Navigation

| Action | Shortcut (VS Code) |
| --- | --- |
| Accept suggestion | Tab |
| Dismiss suggestion | Escape |
| See next suggestion | Alt+] (Windows/Linux) / Option+] (macOS) |
| See previous suggestion | Alt+[ / Option+[ |
| Accept word-by-word | Ctrl+Right (Windows/Linux) / Cmd+Right (macOS) |
| Open completions panel | Ctrl+Enter |

### Getting Better Completions

- **Write clear comments** before the code you want — comments are high-signal context.
- **Keep related files open** — Copilot uses open tabs as context (especially in VS Code).
- **Name variables and functions descriptively** — get_user_by_email gives far more context than get_u.
- **Use a copilot-instructions.md** — project-level conventions that guide all suggestions (see Section 12).

---

## Related Links

- [GitHub Copilot Zero to Hero Part 2](parts/11-github-copilot-zero-to-hero-part2.md) — Chat Interface, Agent Mode, MCP Integration, Code Review, Coding Agent, Billing
- [GitHub Copilot Zero to Hero Part 3](parts/11-github-copilot-zero-to-hero-part3.md) — Enterprise Features, Parallelism, Token Optimization, Guardrails, Explainability, HITL
- [GitHub Copilot Zero to Hero Part 4](parts/11-github-copilot-zero-to-hero-part4.md) — RAI and Compliance, Best Practices, Antipatterns, Keyboard Shortcuts, Troubleshooting
