---
title: "Security Architecture"
domain: agentic-systems
doc_type: reference-architecture
topic_id: agent-skills-security-architecture
status: current
supersedes:
  - "docs/agentic-systems/skill/enterprise/09-security-architecture.md"
date_created: 2026-07-24
last_reviewed: 2026-07-24
---

# Part 12 — Security (+ Deliverable 8: Security Architecture)

## 9.1 The threat model has changed the governance conversation

Two peer-reviewed-style frameworks now anchor enterprise agent security discussions, both published in the December 2025–March 2026 window:

- **OWASP Top 10 for Agentic Applications (ASI01–ASI10)**: agent-level risks — Goal Hijack, Tool Misuse & Exploitation, Identity & Privilege Abuse, Agentic Supply Chain Compromise, Unexpected Code Execution, Memory & Context Poisoning, Insecure Inter-Agent Communication, Cascading Agent Failures, Human-Agent Trust Exploitation, Rogue Agents.
- **OWASP Agentic Skills Top 10 (AST10)**: skill-content-layer risks specifically — because a Skill's natural-language instructions can direct malicious behavior (e.g., exfiltrate a file via the system's default HTTP client) **without any code signature a traditional scanner would catch**. AST10 was directly motivated by a real Q1 2026 incident in which a major public skill marketplace was systematically poisoned — five of its seven most-downloaded skills at peak infection were confirmed malware — and by Snyk research finding a meaningful share of critical skill issues invisible to simple pattern matching.

The unifying concept both frameworks converge on is the **"Lethal Trifecta"** (Simon Willison / Palo Alto Networks framing, now widely cited): a skill or agent is especially dangerous when it simultaneously has (1) access to private data, (2) exposure to untrusted content, and (3) the ability to communicate externally. Most production agent deployments today satisfy all three conditions simultaneously — which is precisely why deterministic, non-model-side controls are non-negotiable.

## 9.2 Where authorization checks belong — the enforcement boundary principle

**Core principle, stated by essentially every platform reviewed in some form: model-side guardrails are probabilistic and cannot be the sole enforcement point. A deterministic boundary must sit between the agent and whatever it is reaching.**

```
Skill layer:         states POLICY IN PROSE (what should happen) — advisory only,
                      NOT an enforcement boundary. The model can misread or be
                      manipulated around prose instructions (prompt injection).

Tool layer:           can perform SCHEMA validation (types, enums, required
                      fields) — necessary, not sufficient for authorization.

MCP Server layer:     SHOULD enforce per-connection auth boundary — this is
                      where OAuth 2.1 + RFC 9728 (Protected Resource Metadata)
                      + RFC 8707 (Resource Indicators, token-binding to the
                      specific server) are now MUST per the current MCP spec.

Policy Enforcement    THIS is the deterministic, mandatory checkpoint —
Point (PEP) —         evaluates identity + skill + tool + resource + context
Gateway/Cedar/OPA:    against policy BEFORE the tool call is allowed to execute.
                      Not bypassable by prompt content.

Backend API layer:    defense in depth — enforces its own authz independent
                      of whether the agent/gateway got it right, exactly as
                      it would for a human-driven client.
```

This is precisely how AWS AgentCore's guardrail model works in production: developers set boundaries "using plain language to control which tools agents can use and what actions they're allowed to perform," and AgentCore **automatically converts that natural-language policy into Cedar** — the enforcement itself is deterministic Cedar evaluation, not the natural-language statement. The natural-language authoring step is a *developer experience* improvement; the actual security boundary is the compiled, deterministic policy.

## 9.3 Identity architecture

| Concept | Purpose | Implementation examples |
| --- | --- | --- |
| **Agent identity** | The agent itself is a first-class identity, not an anonymous process | Entra Agent ID (Azure), AgentCore Identity, dedicated integration users (Salesforce's explicit guidance: never clone the running user's own profile onto the agent's service identity) |
| **On-Behalf-Of (OBO) / delegation** | Agent acts with a *scoped subset* of the requesting human's permissions, not the agent's own broad service identity | OAuth 2.1 token exchange patterns; MCP's Resource Indicators (RFC 8707) bind a token to the specific downstream server it was issued for, preventing token replay against an unintended resource |
| **Service identity** | For autonomous, non-human-triggered agent runs (scheduled, event-driven) | Dedicated service principal per agent, least-privilege scoped, never shared across agents |
| **Cross-agent identity (A2A)** | A remote agent must be able to verify *which* agent it's talking to | Signed Agent Cards (A2A v1.0 requirement) |

**Salesforce's own architecture review guidance is a good general-purpose warning, not Salesforce-specific**: the default temptation is to give the agent's running identity everything the cloning human user can do; that "works on day one" and fails the first time a creative or malicious user probes it. The agent's identity should hold only the minimum object/field/action access its *published* skills actually require — determined from the `permission_manifest` metadata (file `02`), not from convenience.

## 9.4 Policy engines

| Engine | Model | Where it fits |
| --- | --- | --- |
| **Cedar** (AWS, open-source) | Explicit allow/deny policy language, verifiable via automated reasoning | Natural PEP choice on AWS; increasingly used standalone given its formal-verification properties |
| **OPA / Rego** (CNCF) | General-purpose policy-as-code, widely adopted across Kubernetes/cloud-native stacks | Good default when the enterprise already runs OPA for other authorization surfaces — reuse rather than introduce a second policy language |
| **RBAC** | Role-based — coarse-grained, easy to reason about | Baseline for discovery filtering (file `06`) and simple deployments |
| **ABAC / context-aware authorization** | Attribute-based — supports rules like "agents can only access customer data during business hours" | Needed once policies depend on runtime context (time, data sensitivity, session risk score), not just static role |

## 9.5 Secrets and least privilege

- **Never place credentials in skill instructions or in the model's context window.** Tool/MCP-layer credential injection (the gateway holds and injects the secret; the model only ever sees a reference/handle) is the only acceptable pattern.
- **Short-lived, task-scoped credentials** over long-lived static keys — directly addresses ASI03 (Identity & Privilege Abuse) mitigation guidance around avoiding cached long-lived secrets in agent memory.
- **Permission manifests are declarative and enforced, not aspirational.** A skill declaring `tools: [orders.cancel_order]` in its manifest should be *structurally incapable* of invoking `payments.refund` even if a prompt-injected instruction tries to steer it there — enforcement happens at the PEP, independent of what the model "decides" to attempt.

## 9.6 Skill-specific supply-chain security (Deliverable 8 core content)

Mitigations mapped to the OWASP AST10 risk classes surfaced in research:

| Risk | Mitigation |
| --- | --- |
| Unsigned/tampered skill content | Require `content_hash` + cryptographic signature (e.g., ed25519) before a skill is loadable in any non-dev environment (file `02` schema) |
| Registry poisoning (malicious skill published to a marketplace) | Mandatory security review before certification (file `10`); automated scanning tuned for *natural-language* attack patterns, not just code signatures, since regex/pattern-matching alone misses a meaningful share of malicious instructions |
| Sandbox escape via bundled scripts | Execute skill-bundled scripts in an isolated sandbox (microVM/container) with no default host filesystem/network access — never assume "it's just a script" is safe by default |
| Excess permission (skill can do more than it needs) | Enforce `permission_manifest` as a hard ceiling, not documentation; default-deny anything not explicitly declared |
| Prompt injection via untrusted content processed *by* a skill (e.g., a skill that reads emails/documents) | Treat all content a skill retrieves as untrusted input, structurally separate from trusted instructions; apply the same discipline as SQL-injection defense — never let retrieved content be interpreted as new instructions without explicit, bounded parsing |
| Dynamic runtime composition risk (agent discovers and loads new skills mid-session) | Discovery must be policy-filtered (file `06`) *and* the loaded skill must pass the same signature/certification check as a statically registered one — dynamic loading is not an exemption from governance |

## 9.7 Deliverable 8 — consolidated security architecture diagram

```mermaid
graph TD
    A["IDENTITY LAYER<br/>Human user --OBO/delegation--&gt; Agent Identity<br/>--scoped token--&gt; downstream systems<br/>Agent identity is least-privilege,<br/>never a clone of the human's access"]
    B["SKILL SUPPLY-CHAIN GATE<br/>Signature verify → permission_manifest review<br/>→ security scan → human review<br/>→ certified"]
    C["RUNTIME POLICY ENFORCEMENT POINT<br/>Identity + skill + tool + resource + context<br/>→ Cedar/OPA decision<br/>Deterministic, non-bypassable"]
    D["MCP AUTH BOUNDARY<br/>OAuth 2.1 + RFC 9728 + RFC 8707<br/>Per connected system<br/>Token bound to this server only"]
    E["BACKEND SYSTEM<br/>Defense-in-depth authz<br/>Independent of above"]
    F["Sandbox isolation wraps skill-bundled<br/>script execution at every layer.<br/>Content from external sources is<br/>never treated as trusted instruction."]
    
    A --> B --> C --> D --> E
    F -.->|wraps| C
    F -.->|wraps| D
    
    style A fill:#e1f5ff
    style B fill:#fff3e0
    style C fill:#ffe0b2
    style D fill:#fff3e0
    style E fill:#f3e5f5
    style F fill:#ffccbc
```
