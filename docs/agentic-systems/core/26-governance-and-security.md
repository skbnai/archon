---
title: "Governance & Security"
date_created: 2026-07-24
last_reviewed: 2026-07-24
status: current
domain: agentic-systems
doc_type: guide
topic_id: governance-and-security
supersedes: ["docs/agentic-systems/skill/coding/10-governance-and-security.md"]
---

# Part 15 — Governance & Part 16 — Security

## PART A: Governance

### 15.1 Why governance lags here compared to enterprise agent platforms

The most consistent theme across this entire research package: **individual developers, not a central platform team, author most coding-agent Skills and instruction files today**, and organization-level distribution/governance features are explicitly marked "coming soon" on more than one major platform as of mid-2026. This is a structural gap, not an oversight — coding-assistant tooling grew bottom-up from individual developer productivity, while enterprise business-agent platforms (companion package) grew top-down from IT/platform teams from day one. Any organization serious about this needs to build the governance layer itself today, ahead of vendor tooling catching up.

### 15.2 Approval and publishing

| Stage | Practice observed | Gap to close for org use |
| --- | --- | --- |
| **Authoring** | Individual developer writes a `SKILL.md`, commits it to `.github/skills/` | Goes through the same PR review as any other repo change *if the team enforces that* — not automatic |
| **Marketplace publishing** | `gh skill` supports publish with validation (`--dry-run` checks against the Agent Skills spec, tag protection, secret scanning, code scanning) | Genuine, useful tooling — but marketplace skills are explicitly documented as **not verified by GitHub**, with an explicit warning that skills "may contain prompt injections, hidden instructions, or malicious scripts" |
| **Organization Skills** | Announced roadmap item on more than one platform, not yet broadly shipped | Until available, the practical substitute is a shared, org-owned git repository of skills that individual repos reference/clone from — treat it with the same access control and review rigor as a shared library |
| **Versioning** | Ad hoc — most skills have no formal version field in practice, despite the schema supporting one (file `02`) | Adopt `metadata.version` as an org policy requirement, not just a nice-to-have field |
| **Ownership** | Rarely tracked formally at the individual-developer level | Require `metadata.owner` for any skill committed to a shared/org repo |
| **Retirement** | No formal deprecation mechanism observed in current tooling | Handle via the same PR-based removal process as any dead code, with a grep-for-references check first |

### 15.3 Security review, prompt review, dependency review

Given the security findings in Part B below, these three review types should be treated as **mandatory gates**, not optional best practice, for any skill or rules file sourced from outside the immediate authoring team:

1. **Security review**: does the skill's bundled scripts do anything beyond what the description implies? Does it request network egress, credential access, or destructive operations not obviously justified by its stated purpose?
2. **Prompt review**: does the instruction text contain anything that reads as an attempt to override safety behavior, suppress confirmation prompts, or instruct the agent to hide its actions from the user ("don't mention this to the user" is a documented, named red flag pattern from real malicious-skill research)?
3. **Dependency review**: does the skill declare MCP tool dependencies (file `02`) that themselves need independent trust evaluation? A skill is only as trustworthy as every MCP server it silently assumes access to.

---

## PART B: Security

### 16.1 The threat is proven, not theoretical — a concrete CVE/incident catalog

This is the area where coding-assistant-specific research has moved fastest and produced the most concrete, named findings. A representative (non-exhaustive) sample from systematic 2025–2026 security research:

| Vulnerability class | Example CVE(s) / named finding | Mechanism |
| --- | --- | --- |
| **Rules File Backdoor** | AIShellJack framework: 314 payloads across 70 MITRE ATT&CK techniques, 41–84% success rate | A malicious `.cursorrules`/`.clinerules`/`copilot-instructions.md` committed to a repo instructs the agent to run attacker code; survives forking — every downstream clone inherits it |
| **README/instruction-file injection** | Documented by Pillar Security and Cloud Security Alliance research | Instructions hidden in README or other repo-committed prose, styled to look like normal documentation to a human reviewer while parsing as instructions to the agent |
| **Filename-based injection** | Tenable TRA-2025-53; CVE-2025-36730 (Windsurf) | A crafted *filename* itself carries injected instructions, appended into the agent's prompt during normal file listing |
| **Toxic Agent Flow (MCP-mediated)** | Documented exploitation of GitHub MCP servers | A GitHub issue body contains hidden instructions; agent processes it via an MCP server holding broad repo-access tokens, exfiltrating data via a crafted PR or encoded response |
| **Auto-approval tampering** | CVE-2025-53773 / CVE-2025-62222 (GitHub Copilot) | Prompt injection tricks the agent into modifying its own settings (`.vscode/settings.json`) to enable auto-approval of further tool calls, achieving RCE without further user interaction |
| **MCP server RCE** | CVE-2025-49150 (Cursor) | Remote code execution via MCP configuration/tool-call handling |
| **Data exfiltration via agent tooling** | CVE-2025-58335 (Junie), CVE-2025-53097 (Roo Code — credential theft) | Agent tricked into reading and transmitting sensitive local files/credentials |
| **Command injection** | CVE-2025-61260 (Codex CLI) | Crafted input leads to unintended shell command execution |
| **Environment/config hijack** | Documented Claude Code repository-environment-config exploit | A malicious repo-committed environment variable (`ANTHROPIC_BASE_URL`) silently redirects all of the agent's API traffic — including the developer's own API key, in plaintext — to an attacker-controlled server |
| **Malicious published skills** | Snyk study: 3,984 skills scanned across major public registries, 13.4% contained critical issues (credential theft, backdoor installation, data exfiltration); 91% of confirmed-malicious skills combined prompt injection with traditional malware | Same class of supply-chain risk as the enterprise-side OWASP AST10 findings (companion package file `09`), specifically instantiated in coding-skill marketplaces |

**The unifying root cause, stated plainly by the research literature**: these are not model failures in the traditional sense — they are **trust-boundary failures**. The agent treats repository-supplied text (a rules file, a filename, an issue body, an environment variable) as if it were a trusted instruction from the developer, when it is actually untrusted, attacker-reachable content. This is exactly the same "Lethal Trifecta" pattern documented in the enterprise package (companion file `09`): access to private data (credentials, local files) + exposure to untrusted content (the repo itself) + ability to communicate externally (network egress) — and a huge share of real-world coding-agent deployments satisfy all three simultaneously by default.

### 16.2 Sandboxing — the dominant, converging mitigation

Every major agent studied now ships some form of default or strongly-recommended isolation:

| Agent | Default sandbox mechanism |
| --- | --- |
| OpenAI Codex CLI | Default-on; Seatbelt (macOS), Landlock + seccomp (Linux), restricted tokens (Windows); modes: read-only, workspace-write, danger-full-access |
| Anthropic Claude Code | Sandboxed bash tool via `@anthropic-ai/sandbox-runtime` (Seatbelt/bubblewrap + a network-filtering proxy); cloud sessions run in full microVMs |
| Google Gemini CLI / Antigravity | Seatbelt (macOS) or Docker/Podman containers via a declared sandbox Dockerfile |
| Cursor, Devin, other cloud-hosted agents | Per-task hosted sandbox/VM (Devin explicitly uses dedicated cloud VMs per task) |
| Replit Agent | Runs inside a Replit-managed VM/container |

**Measured impact**: Anthropic reports that sandboxing reduces permission-prompt volume by roughly 84% — a meaningful usability improvement, not just a security one, because fewer prompts means less "approval fatigue" and less reflexive, un-scrutinized clicking of "Allow."

**The important caveat, repeatedly emphasized in the source material**: sandboxing protects the *host machine*. It does not, by itself, prevent a compromised/malicious repository from exfiltrating whatever credentials and data *are* accessible from inside the sandbox (a real, documented gap: `--dangerously-skip-permissions`-style flags inside a devcontainer still expose anything mounted or forwarded into that container, including the agent's own API credentials). The concrete, documented anti-pattern here: the Cursor IDE incident where an agent deleted 70 files despite an explicit "DO NOT RUN ANYTHING" instruction in the prompt — demonstrating that **text-based restriction inside the prompt is not a reliable control**; the deterministic, out-of-band sandbox/permission boundary is.

### 16.3 A layered security architecture for coding agents

```mermaid
graph TD
    A["LAYER 1: Untrusted Input Boundary<br/>Repository content never auto-executed<br/>rules files, README, filenames, issues, env vars"]
    B["LAYER 2: Skill/Rules Review Gate<br/>Security + Prompt Review<br/>before auto-load"]
    C["LAYER 3: OS/Container-level Sandbox<br/>Seatbelt/Landlock/bubblewrap/microVM<br/>Deterministic protection"]
    D["LAYER 4: Network Egress Allowlist<br/>Only model API, package registries, git host<br/>Blocks exfiltration"]
    E["LAYER 5: Approval Gates for High-Risk Actions<br/>Force-push, destructive commands, auto-approval changes,<br/>secrets access, unpinned installs"]
    
    A --> B --> C --> D --> E
    
    style A fill:#ffebee
    style B fill:#fff3e0
    style C fill:#e8f5e9
    style D fill:#e3f2fd
    style E fill:#f3e5f5
```

The layered security architecture for coding agents consists of five key control layers:

1. **Untrusted Input Boundary** — Repository content (rules files, README, filenames, issue bodies, env vars) is treated as untrusted by default — never auto-executed or auto-trusted without review, regardless of how "normal" it looks to a human reviewer.

2. **Skill/Rules Review Gate** — Externally-sourced or first-time-seen skills/rules files must pass security + prompt review before being allowed to auto-load (as described in Part A, section 15.3).

3. **OS/Container-level Sandbox** — Seatbelt/Landlock/bubblewrap/microVM provides deterministic, prompt-independent protection that safeguards the host regardless of what the model is tricked into attempting.

4. **Network Egress Allowlist** — Restrict outbound connectivity to only the model API, package registries, and git host — blocks exfiltration even if the sandbox itself is compromised.

5. **Approval Gates for High-Risk Actions** — Force-push, destructive shell commands, auto-approval-setting changes, secrets access, and package installs from unpinned sources require explicit, per-action human confirmation outside of fully-isolated, disposable environments.

### 16.4 Least privilege and permission prompts

- **Read-only-by-default for anything with a write mode**: database MCP servers, cloud MCP servers, and terminal tools should default to the least-privileged mode (Codex CLI's own default posture is the clearest vendor-endorsed example) and require explicit elevation.
- **Human-in-the-loop checkpoints are a design requirement, not a UX inconvenience** — every long-horizon agent studied (Devin, GitHub Copilot Workspace) surfaces a plan and asks for approval before destructive actions specifically because unattended, high-autonomy operation without checkpoints is where the worst documented incidents originate.
- **Approval fatigue is a real, named failure mode** — the fix is not "prompt less" but "sandbox more, so that fewer prompts are actually necessary because the blast radius of an unreviewed action is already contained."

## Related

- [Multi-Agent Skills & Observability](25-multi-agent-and-observability.md) — the previous section in this series.
- [Evaluation, Reusability & Deduplication](27-evaluation-reusability-deduplication.md) — the next section in this series.
