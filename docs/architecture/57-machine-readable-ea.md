---
doc_type: reference-architecture
domain: architecture
topic_id: machine-readable-ea
title: "Machine-Readable Enterprise Architecture for the Agentic Era"
date_created: 2026-07-05
last_reviewed: 2026-07-23
status: current
covers_version: "as of 2026-07-10"
aliases:
  - machine readable ea
  - policy as code for ea
supersedes:
  - docs/enterprise-architecture/ai-architecture/machine-readable-ea.md
tags:
  - enterprise-ai-architect
  - governance
  - policy-as-code
  - operational-resilience
---

# Machine-Readable Enterprise Architecture for the Agentic Era

> **Current as of July 2026.** Enterprise architecture is shifting from static documentation to machine-readable runtime context that AI agents consume. This guide explains what that means concretely, how to implement it, and what it means for your operating model.

---

## 1. The Shift: From Blueprint to Runtime Context

**Old model:** The EA team produces architecture diagrams, standards documents, and review guidelines. Developers read them (sometimes). Agents ignore them.

**New model:** Architecture artifacts are structured, queryable, and enforced at runtime. An agent attempting a cross-region data transfer is stopped by the EA team's data-residency policy — not because a reviewer caught the code review, but because the policy engine evaluated the request before execution.

This shift is not incremental — it redefines what enterprise architecture teams produce.

| Dimension | Traditional EA | Machine-Readable EA |
| --- | --- | --- |
| **Output** | Diagrams, Word docs, Confluence pages | Executable policies, queryable models, MCP-served contexts |
| **Enforcement** | Review boards, manual audits | Runtime policy evaluation (OPA/Cedar) |
| **Latency** | Days (ARB review) | Milliseconds (per-request evaluation) |
| **Discoverability** | Humans search wikis | Agents query structured APIs and MCP tools |
| **Update cycle** | Annual review cycles | Git-versioned, CI-tested like code |
| **Role of EA** | Gatekeeper | Context provider + scale enabler |

**92% of enterprise architecture leaders named AI and agentic architecture as the top 2026 trend** ([Avolution, 2026](https://www.avolutionsoftware.com/our-resources/enterprise-architecture-trends-skills-strategies-2026/)). The critical insight from that research: EA teams that fail to provide machine-readable context will be bypassed by agent deployments, not consulted by them.

---

## 2. What "Machine-Readable" Means Concretely

Consider the difference between these two policy artifacts:

**Traditional (human-readable only):**
> *"Confluence page — Data Residency Policy v2.3: All customer PII must remain within the EU. No replication to US regions permitted without Legal sign-off. See Appendix A for approved regions."*

An agent performing a data-processing task cannot read, interpret, or enforce this. It will either ignore it or — if given the document via RAG — hallucinate an interpretation.

**Machine-readable:**

```rego
# data_residency.rego (Open Policy Agent)
package ea.data_residency

import future.keywords.if
import future.keywords.in

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

An agent's MCP gateway evaluates this policy on every data-related tool call. The policy is version-controlled, CI-tested, and automatically applied — no human in the loop for routine decisions.

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

```mermaid
graph TD
    A["Agent Tool Call<br/>Request"] --> B["Policy Engine<br/>OPA / Cedar"]
    B -->|Input| C["agent_id, action,<br/>resource, data_class,<br/>user_context, cost,<br/>region, delegation"]
    B -->|Evaluate| D["data_residency.rego<br/>data_classification.rego<br/>cost_governance.rego<br/>agent_scope.rego<br/>human_oversight.rego"]
    B -->|ALLOW| E["Execute tool call"]
    B -->|NOTIFY| F["Execute + async<br/>notification"]
    B -->|DENY| G["Return structured<br/>error to agent"]
    E --> H["Action complete"]
    F --> H
    G --> H
```

**Policy engine decision flow:** Agent tool calls are routed through policy evaluation before execution, with outcomes of ALLOW (execute), NOTIFY (execute + notify), or DENY (error).

### 3.2 Policy Categories for EA Teams to Own

**Access control policies** — which agents can access which data classifications, systems, and APIs:

```cedar
// Cedar policy (AWS Verified Permissions style)
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

require_approval[action] if {
    action == "llm.complete"
    input.output_action_type in {"FINANCIAL", "PRIVILEGED"}
}
```

### 3.3 Policy Governance

Treat policies like code:

- **Version control** (Git) — every change is a PR with review
- **CI testing** — policy unit tests validate rules against known inputs/outputs
- **Staged rollout** — new policies in `AUDIT` mode (log-but-allow) before `ENFORCE` mode
- **Ownership** — each policy file has an `owner:` metadata field; EA team owns the catalog

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

### 4.2 What to Expose as MCP Resources

- Architecture models (as JSON/YAML, not diagrams)
- Technology standards catalog (approved technologies by domain)
- Data dictionary (canonical definitions of data entities)
- Regulatory mapping table (system → applicable regulations)

### 4.3 Governing the EA MCP Server

The EA MCP server is a high-trust surface — it represents authoritative policy:

- **Read-only** for agents — no agent can write to the policy store via MCP
- **Authentication required** — OAuth 2.1 with scoped tokens; agents get policy-read scope only
- **Policy updates via Git PR only** — no direct-write APIs for policies; all changes through CI/CD
- **Audit log** — every policy read is logged (which agent asked, what context, what was returned)

---

## 5. Request-Level Dynamic Governance vs. Design-Time Review Boards

The ARB (Architecture Review Board) model was designed for systems that change slowly. Agent deployments can introduce hundreds of new tool integrations per day.

| Mode | ARB / Design-time | Dynamic / Runtime |
| --- | --- | --- |
| **When it runs** | Before deployment | On every request |
| **Latency** | Days to weeks | Milliseconds |
| **Coverage** | New systems only | Every action, including runtime behavior |
| **Policy changes** | Requires a meeting | Git PR, tested, deployed in minutes |
| **Human role** | Reviewer/approver | Policy author + exception handler |
| **Blind spots** | Runtime drift from approved design | None (every request is evaluated) |

The right model is **both** — use ARB-style review for system onboarding and major architecture decisions; use runtime policy evaluation for every agent action. The EA team's job shifts from gatekeeping deployments to authoring and maintaining the policies that govern them at runtime.

**Practical transition:**

1. Identify the 5–10 policies your ARB enforces most consistently (data residency, access tiers, approved tech stack, cost limits)
2. Encode them as OPA/Cedar rules
3. Deploy in audit mode (log violations, don't block yet) to calibrate false-positive rate
4. Switch to enforce mode; replace the equivalent manual ARB checks with automated enforcement
5. ARB retains full authority for novel patterns the policy engine isn't designed to handle

---

## 6. Regulatory Hooks

### 6.1 EU AI Act (Digital Omnibus Timeline)

The EU AI Act's Digital Omnibus (Council final approval June 29, 2026) changed the compliance timeline:

| Obligation | Applies from |
| --- | --- |
| GPAI model obligations (Art. 53/55) | August 2, 2025 (already in force) |
| Commission enforcement + fines for GPAI | **August 2, 2026** |
| Transparency obligations (Art. 50) | **August 2, 2026** |
| Annex III high-risk obligations | **December 2, 2027** |
| Annex I (AI in regulated products) | **August 2, 2028** |

For enterprise architects: machine-readable EA is directly relevant to **Article 14 (human oversight)** and **Article 17 (quality management)**. Your policy engine provides the documented, auditable controls these articles require. The runtime policy evaluation log is your compliance evidence.

### 6.2 Explainability as an Architecture Requirement

For systems approaching Annex III classification, explainability is not a post-hoc feature — it must be designed in:

- Policy evaluation results should include a **reason string** in the DENY/NOTIFY output that can be shown to humans
- Agent decision paths should be traceable via OTel GenAI spans
- Human override decisions (approval gate decisions) must be logged with human identity, timestamp, and reason

The machine-readable EA framework — where agents explicitly query policies and record the response — is architecturally superior to agents that embed policy logic implicitly in their prompt system.

---

## 7. SLM-First / Local-by-Default as an EA Standard

Gartner predicts enterprise use of **small task-specific models will be 3× LLM use by 2027** ([Gartner Strategic Trends 2026](https://www.gartner.com/en/newsroom/press-releases/2025-10-20-gartner-identifies-the-top-strategic-technology-trends-for-2026)). NVIDIA's agent research shows **80–90% of individual agent steps don't require frontier models** — routing them to local SLMs achieves similar quality at ~10–20% of cloud-only cost ([NVIDIA SLM Agents Research](https://research.nvidia.com/labs/lpr/slm-agents/)).

Machine-readable EA is how you make this work at scale. Rather than having each team make ad-hoc model routing decisions, the EA team defines a **model routing standard**:

```yaml
# model-routing-policy.yaml
tiers:
  - name: local-slm
    description: "On-device or on-premises small model"
    triggers:
      - data_classification: ["CONFIDENTIAL", "SECRET"]  # data cannot leave premises
      - task_type: ["classify", "extract", "format", "summarize_short"]
      - latency_requirement_ms: { lt: 100 }

  - name: cloud-standard
    description: "Mid-tier cloud model (Sonnet-class)"
    triggers:
      - task_type: ["complex_reasoning", "code_generation", "summarize_long"]
      - cost_tier: "standard"

  - name: cloud-frontier
    description: "Frontier model (Fable-class)"
    triggers:
      - task_type: ["research", "architecture_review", "strategic_analysis"]
      - explicit_request: true  # must be explicitly requested; not default
    approval_required: true  # triggers cost-governance check
```

This policy, served via the EA MCP server, ensures every agent in the enterprise routes model calls consistently — without each team re-inventing the heuristic.

### 7.1 Digital Sovereignty

The SLM-first policy intersects with digital sovereignty requirements:

- **35% of countries** will have data-localization requirements affecting AI workloads by 2027 (Gartner)
- **>75% of European and Middle Eastern enterprises** are expected to geopatriate AI workloads by 2030 (from &lt;5% in 2025)
- The EU AI Act + GDPR combination means data used to train or fine-tune models must also respect data-subject rights

Enterprise architects in regulated sectors should designate certain data classifications as **"local inference only"** in the model routing policy — preventing them from being sent to any cloud model, regardless of model capability.

---

## 8. Migration Roadmap: From Confluence to Machine-Readable

### Phase 1: Inventory & Identify (1–2 months)

- Identify your 10 most-enforced architecture policies (data residency, access tiers, approved tech, cost limits, human oversight thresholds)
- Map which of these affect agent tool calls vs. design-time decisions
- Inventory existing policy documentation for completeness and conflicts

### Phase 2: Encode & Test (2–3 months)

- Encode the 10 policies in OPA or Cedar
- Write 20+ policy unit tests per policy (allow cases, deny cases, edge cases)
- Deploy to a staging environment in **audit mode** (log violations, no blocking)
- Instrument OTel spans to capture policy evaluation in traces

### Phase 3: Enforce for New Agents (2 months)

- Switch audit → enforce for all *new* agent deployments
- Existing agents remain on audit mode during grace period
- EA MCP server goes live (read-only policy and constraint queries)

### Phase 4: Full Enforcement & ARB Evolution (3–6 months)

- Migrate existing agents to enforcement
- ARB retains authority for: net-new system integrations, policy changes, novel architectural patterns
- ARB delegates routine pattern reviews to automated policy evaluation
- EA team measures: policy violation rate, false-positive rate, agent deployment velocity (target: 10× faster than pre-automation)

### Maturity Model

| Level | Description | Key Indicator |
| --- | --- | --- |
| **1 — Ad-hoc** | Policies in docs; manual enforcement | ARB reviews all agent deployments |
| **2 — Encoded** | Core policies in OPA/Cedar; audit mode | Policy violations visible in dashboards |
| **3 — Enforced** | Policies block non-compliant actions; EA MCP server live | New agents deploy without ARB review |
| **4 — Adaptive** | Policies updated via CI/CD; anomaly detection feeds policy refinement | Policy update cycle &lt; 1 week |
| **5 — Autonomous** | EA repository is the primary context source for all agents; policies version-controlled and self-tested | Zero manual enforcement reviews |

---

## Related

- [EA Mastery Guide](71-ea-mastery-guide.md) — the broader EA practice this machine-readable approach modernizes.
- [EA Architect Deep Dive: Toolkit & Practice](07-ea-architect-deep-dive-toolkit-practice.md) — practical tooling this machine-readable pattern supports.

## Sources

- [Avolution: Enterprise Architecture Trends, Skills & Strategies 2026](https://www.avolutionsoftware.com/our-resources/enterprise-architecture-trends-skills-strategies-2026/)
- [BlueDolphin: Agentic AI and Enterprise Architecture in 2026](https://bluedolphin.io/blog/agentic-ai-and-enterprise-architecture-in-2026/)
- [Promethium: AI Agent Data Governance Enterprise Playbook 2026](https://promethium.ai/guides/ai-agent-data-governance-enterprise-playbook-2026/)
- [Gartner: Top Strategic Technology Trends for 2026](https://www.gartner.com/en/newsroom/press-releases/2025-10-20-gartner-identifies-the-top-strategic-technology-trends-for-2026)
- [NVIDIA Research: SLM Agents](https://research.nvidia.com/labs/lpr/slm-agents/)
- [InfoWorld: Small Language Models Rethinking Enterprise AI Architecture](https://www.infoworld.com/article/4160404/small-language-models-rethinking-enterprise-ai-architecture.html)
- [CIO.com: Agentic AI Making the EA Role More Fluid](https://www.cio.com/article/4096695/agentic-ais-rise-is-making-the-enterprise-architect-role-more-fluid.html)
- [Gibson Dunn: EU AI Act Omnibus](https://www.gibsondunn.com/eu-ai-act-omnibus-agreement-postponed-high-risk-deadlines-and-other-key-changes/)
- [OPA Documentation: Policy as Code](https://www.openpolicyagent.org/docs/latest/)
- [Computer Weekly: Agentic AI Future of Enterprise Architecture](https://www.computerweekly.com/feature/The-agentic-AI-future-of-enterprise-architecture)
