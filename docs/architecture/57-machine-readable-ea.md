---
title: "Machine-Readable Enterprise Architecture for the Agentic Era"
date_created: 2026-07-05
last_reviewed: 2026-07-10
status: current
source_type: native-md
source_file: ""
tags: ["architecture", "governance", "policy-as-code"]
doc_type: reference-architecture
covers_version: "as of 2026-07-10"
domain: architecture
topic_id: machine-readable-ea
supersedes:
  - docs/enterprise-architecture/ai-architecture/machine-readable-ea.md
---

# Machine-Readable Enterprise Architecture for the Agentic Era

**Current as of July 2026.** Enterprise architecture is shifting from static documentation to machine-readable runtime context that AI agents consume. This guide explains what that means concretely, how to implement it, and what it means for your operating model.

---

## 1. The Shift: From Blueprint to Runtime Context

**Old model:** The EA team produces architecture diagrams, standards documents, and review guidelines. Developers read them (sometimes). Agents ignore them.

**New model:** Architecture artifacts are structured, queryable, and enforced at runtime. An agent attempting a cross-region data transfer is stopped by the EA team's data-residency policy — not because a reviewer caught the code review, but because the policy engine evaluated the request before execution.

| Dimension | Traditional EA | Machine-Readable EA |
| --- | --- | --- |
| **Output** | Diagrams, Word docs, Confluence pages | Executable policies, queryable models, MCP-served contexts |
| **Enforcement** | Review boards, manual audits | Runtime policy evaluation (OPA/Cedar) |
| **Latency** | Days (ARB review) | Milliseconds (per-request evaluation) |
| **Discoverability** | Humans search wikis | Agents query structured APIs and MCP tools |
| **Update cycle** | Annual review cycles | Git-versioned, CI-tested like code |
| **Role of EA** | Gatekeeper | Context provider + scale enabler |

---

## 2. What "Machine-Readable" Means Concretely

**Traditional (human-readable only):**
"All customer PII must remain within the EU. No replication to US regions permitted without Legal sign-off."

An agent performing a data-processing task cannot read, interpret, or enforce this.

**Machine-readable (Open Policy Agent):**

```rego
package ea.data_residency

deny[msg] if {
    input.action == "data.replicate"
    input.data.classification in {"PII", "CONFIDENTIAL"}
    not input.destination.region in allowed_eu_regions
    msg := sprintf("Data residency violation: %v cannot be replicated to %v",
                   [input.data.classification, input.destination.region])
}

allowed_eu_regions := {
    "eu-central-1",   # Frankfurt
    "eu-west-1",      # Dublin
    "eu-west-3",      # Paris
    "eu-north-1",     # Stockholm
}
```

An agent's MCP gateway evaluates this policy on every data-related tool call. The policy is version-controlled, CI-tested, and automatically applied.

### 2.1 The Four Artifacts to Structurize

| Artifact | Traditional form | Machine-readable form |
| --- | --- | --- |
| **Policies** | Word doc / Confluence | OPA Rego / Cedar policies, evaluated per-request |
| **Constraints** | Architecture principles doc | Typed constraint objects queryable via API or MCP |
| **Dependencies** | Architecture diagrams | Machine-readable service catalog (Backstage, ServiceNow, custom) |
| **Data lineage** | Data flow diagrams | Automated lineage graphs (dbt, Apache Atlas, OpenLineage) |

---

## 3. Policy-as-Code for Agents

### 3.1 The Policy Engine Pattern

Every agent gateway should route requests through a policy engine before execution:

```
Agent Tool Call Request
        │
        ▼
  Policy Engine (OPA / Cedar)
        │
        ├── Input: {agent_id, action, resource, data_classification,
        │           user_context, estimated_cost, region, delegation_depth}
        │
        ├── Policies evaluated:
        │    ├── data_residency.rego
        │    ├── data_classification.rego
        │    ├── cost_governance.rego
        │    ├── agent_scope.rego
        │    └── human_oversight.rego
        │
        ├── ALLOW → execute tool call
        ├── NOTIFY → execute + async notification
        └── DENY → return structured error to agent
```

### 3.2 Policy Categories for EA Teams to Own

**Access control policies** — which agents can access which data classifications, systems, and APIs:

```cedar
permit(
    principal is Agent,
    action in [Action::"tool.call"],
    resource is CRMDatabase
) when {
    principal.cleared_data_tiers.contains("INTERNAL") &&
    context.data_classification in ["INTERNAL", "PUBLIC"]
};
```

**Cost governance policies** — per-agent, per-task, per-day spending limits:

```rego
deny[msg] if {
    input.action == "llm.complete"
    input.agent_daily_spend_usd + estimated_cost > agent_daily_limit
    msg := "Daily token budget exceeded"
}
```

**Human oversight policies** — which action classes require human approval:

```rego
require_approval[action] if {
    action in {"bank.transfer", "data.delete", "email.send", "access.grant"}
}
```

### 3.3 Policy Governance

Treat policies like code: Version control (Git) · CI testing · Staged rollout (AUDIT mode before ENFORCE) · Ownership metadata — each policy file has an `owner:` field; EA team owns the catalog.

---

## 4. The EA Repository via MCP

The most practical near-term change: **expose your architecture repository as an MCP server** so agents and developers can query it programmatically.

### 4.1 What to Expose as MCP Tools

| MCP Tool | What it returns | Agents use it to |
| --- | --- | --- |
| `get_data_classification(system_name)` | Data classification level + handling rules | Determine appropriate encryption, logging, residency before tool calls |
| `get_approved_regions(data_type)` | List of approved cloud regions | Validate resource placement |
| `get_dependency_graph(service_name)` | Upstream/downstream dependencies | Assess blast radius of a change |
| `get_applicable_standards(sector, data_type)` | Applicable regulatory/internal standards | Compliance-aware decisions |
| `check_policy(action, context)` | Allow / Deny / Notify + reason | Pre-flight check before executing an action |
| `get_adr(adr_id)` | Architecture Decision Record | Context for technical choices |

### 4.2 Governing the EA MCP Server

The EA MCP server is a high-trust surface — it represents authoritative policy:

- **Read-only** for agents — no agent can write to the policy store via MCP
- **Authentication required** — OAuth 2.1 with scoped tokens; agents get policy-read scope only
- **Policy updates via Git PR only** — no direct-write APIs for policies
- **Audit log** — every policy read is logged (which agent asked, what context, what was returned)

---

## 5. Request-Level Dynamic Governance vs. Design-Time Review Boards

| Mode | ARB / Design-time | Dynamic / Runtime |
| --- | --- | --- |
| **When it runs** | Before deployment | On every request |
| **Latency** | Days to weeks | Milliseconds |
| **Coverage** | New systems only | Every action, including runtime behavior |
| **Policy changes** | Requires a meeting | Git PR, tested, deployed in minutes |
| **Human role** | Reviewer/approver | Policy author + exception handler |
| **Blind spots** | Runtime drift from approved design | None (every request is evaluated) |

The right model is **both** — use ARB-style review for system onboarding and major architecture decisions; use runtime policy evaluation for every agent action.

**Practical transition:**

1. Identify the 5–10 policies your ARB enforces most consistently
2. Encode them as OPA/Cedar rules
3. Deploy in audit mode (log violations, don't block yet)
4. Switch to enforce mode; replace equivalent manual ARB checks
5. ARB retains authority for novel patterns the policy engine isn't designed to handle

---

## 6. Regulatory Hooks

### 6.1 EU AI Act (Digital Omnibus Timeline)

The EU AI Act's Digital Omnibus changed the compliance timeline:

| Obligation | Applies from |
| --- | --- |
| GPAI model obligations (Art. 53/55) | August 2, 2025 (already in force) |
| Commission enforcement + fines for GPAI | **August 2, 2026** |
| Transparency obligations (Art. 50) | **August 2, 2026** |
| Annex III high-risk obligations | **December 2, 2027** |

For enterprise architects: machine-readable EA is directly relevant to **Article 14 (human oversight)** and **Article 17 (quality management)**. Your policy engine provides the documented, auditable controls these articles require.

### 6.2 Explainability as an Architecture Requirement

For systems approaching high-risk classification, explainability must be designed in:

- Policy evaluation results should include a **reason string** in the DENY/NOTIFY output that can be shown to humans
- Agent decision paths should be traceable via OTel GenAI spans
- Human override decisions (approval gate decisions) must be logged with human identity, timestamp, and reason

---

## 7. SLM-First / Local-by-Default as an EA Standard

Gartner predicts enterprise use of **small task-specific models will be 3× LLM use by 2027**. Rather than having each team make ad-hoc model routing decisions, the EA team defines a **model routing standard**:

```yaml
tiers:
  - name: local-slm
    description: "On-device or on-premises small model"
    triggers:
      - data_classification: ["CONFIDENTIAL", "SECRET"]
      - task_type: ["classify", "extract", "format", "summarize_short"]
      - latency_requirement_ms: { lt: 100 }

  - name: cloud-standard
    description: "Mid-tier cloud model (Sonnet-class)"
    triggers:
      - task_type: ["complex_reasoning", "code_generation"]
      - cost_tier: "standard"

  - name: cloud-frontier
    description: "Frontier model"
    triggers:
      - task_type: ["research", "architecture_review", "strategic_analysis"]
      - explicit_request: true
    approval_required: true
```

This policy, served via the EA MCP server, ensures every agent in the enterprise routes model calls consistently.

### 7.1 Digital Sovereignty

The SLM-first policy intersects with digital sovereignty requirements. Enterprise architects in regulated sectors should designate certain data classifications as **"local inference only"** in the model routing policy — preventing them from being sent to any cloud model, regardless of model capability.

---

## 8. Migration Roadmap: From Confluence to Machine-Readable

### Phase 1: Inventory & Identify (1–2 months)

- Identify your 10 most-enforced architecture policies
- Map which affect agent tool calls vs. design-time decisions
- Inventory existing policy documentation for completeness and conflicts

### Phase 2: Encode & Test (2–3 months)

- Encode the 10 policies in OPA or Cedar
- Write 20+ policy unit tests per policy
- Deploy to staging environment in **audit mode** (log violations, no blocking)

### Phase 3: Enforce for New Agents (2 months)

- Switch audit → enforce for all *new* agent deployments
- Existing agents remain on audit mode during grace period
- EA MCP server goes live (read-only policy and constraint queries)

### Phase 4: Full Enforcement & ARB Evolution (3–6 months)

- Migrate existing agents to enforcement
- ARB retains authority for novel patterns
- ARB delegates routine pattern reviews to automated policy evaluation

### Maturity Model

| Level | Description | Key Indicator |
| --- | --- | --- |
| **1 — Ad-hoc** | Policies in docs; manual enforcement | ARB reviews all agent deployments |
| **2 — Encoded** | Core policies in OPA/Cedar; audit mode | Policy violations visible in dashboards |
| **3 — Enforced** | Policies block non-compliant actions; EA MCP server live | New agents deploy without ARB review |
| **4 — Adaptive** | Policies updated via CI/CD; anomaly detection feeds policy refinement | Policy update cycle < 1 week |
| **5 — Autonomous** | EA repository is the primary context source for all agents; policies version-controlled and self-tested | Zero manual enforcement reviews |

---

## Further Reading

- OPA Documentation: Policy as Code
- Cedar Policy Language (AWS Verified Permissions)
- OpenTelemetry GenAI Conventions
- Backstage Service Catalog
- Digital Omnibus: EU AI Act enforcement timeline
