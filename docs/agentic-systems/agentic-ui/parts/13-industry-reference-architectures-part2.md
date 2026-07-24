---
title: "Industry Reference Architectures for Agentic Applications — Part 2 of 2: Government, Telecom, Knowledge Management, and Life Sciences"
date_created: 2026-07-24
last_reviewed: 2026-07-24
status: current
doc_type: guide
domain: agentic-systems
topic_id: industry-reference-architectures-part2
supersedes: []
source_type: native-md
tags: ["agentic-ui"]
covers_version: "as of 2026-07-10"
---

# Industry Reference Architectures for Agentic Applications — Part 2 of 2

Government & Public Sector, Telecommunications, Knowledge Management & Enterprise Search, and Life Sciences & Pharmaceuticals, plus cross-industry patterns.

**This is Part 2 of 2.** Part 2 covers the remaining 4 industry verticals (Government, Telecom, Knowledge Management, Life Sciences) and cross-cutting UX patterns observed across all domains. See [Part 1: Financial Services, Healthcare, Insurance, Retail, Manufacturing, and Developer Platforms](pathname:///archon/agentic-systems/agentic-ui/13-industry-reference-architectures) for the first 6 verticals.

---

## 7. Government & Public Sector

### Top Use Cases

| Use Case | Expected Value | HITL Requirement |
| --- | --- | --- |
| Citizen services portal | 35-45% reduction in call center volume; 24/7 service | Required for eligibility determinations affecting benefits |
| Benefits eligibility assistant | Faster, more consistent eligibility determinations | Mandatory; EU AI Act Art. 22 and similar |
| Policy research agent | 40-50% reduction in policy research time for staff | Advisory only for research; required for policy recommendations |

### Architecture

```text
Citizen / Government Staff Member
  
  
AG-UI Frontend (Accessible, Multi-language)
   AI disclosure: "You are talking to an AI assistant"
   Language selector (accessibility requirement)
   High contrast / large text mode
   Human escalation always visible
   Decision explanation for any AI-assisted determination
  
  
Agent Runtime
   Policy document retrieval
   Eligibility rule engine
   Case management tools
   Translation tools
  
  
Government Systems
   Salesforce Government Cloud
   ServiceNow (IT/citizen service management)
   Microsoft Azure Government / GovCloud
   Legacy mainframe connectors (common in public sector)
```

### UX Considerations

**Transparency and accountability are statutory requirements:**

- Citizens must be informed at the start of every interaction that they are talking to an AI
- Every eligibility determination must include a plain-language explanation of how the decision was made
- Human review option must be prominently accessible — not buried in a menu
- No impersonation of human government officials

**Multi-language and accessibility are legal requirements, not enhancements:**

- Section 508 (US) / EN 301 549 (EU) compliance is mandatory
- Language support: minimum in official national/regional languages; additional based on population served
- WCAG 2.1 AA at minimum; AAA for high-stakes services
- Screen reader compatibility for every UI component including streaming agent responses

**Sovereign AI considerations for classified tiers:**

- Public-facing (Unclassified): commercial cloud permitted
- Sensitive (CUI / IL2): FedRAMP High, GovCloud required (US); restricted cloud only
- Classified (IL4/IL5/IL6): on-premises or government-specific cloud required; no commercial LLM providers

### Regulatory Constraints

| Regulation | Requirement |
| --- | --- |
| EU AI Act Art. 50 | Disclosure that citizen is interacting with AI; right to human review of consequential decisions |
| Section 508 / WCAG (US/EU) | Full accessibility for digital services |
| APA (US Administrative Procedure Act) | AI-assisted determinations must be explainable and challengeable |
| FedRAMP (US) | Cloud security authorization required for federal deployments |
| GDPR Art. 22 (EU) | No automated decision-making affecting legal rights without human review option |

---

## 8. Telecommunications

### Top Use Cases

| Use Case | Expected Value | HITL Requirement |
| --- | --- | --- |
| NOC agentic assistant | 25-35% faster mean time to resolve network incidents | Required for changes to live network configuration |
| Customer service automation | 40-55% reduction in average handle time | Required for account-level financial exceptions |
| Network anomaly detection | 20-30% improvement in anomaly detection accuracy | Required before automated remediation |

### Architecture

```text
NOC Engineer / Customer Service Rep
  
  
AG-UI Frontend
   Real-time network health dashboard integration
   Alert stream with severity tiers
   HITL gate for network change approvals
   Runbook auto-generation
   On-call escalation integration (PagerDuty, ServiceNow)
  
  
Agent Runtime
   Network telemetry retrieval
   Log analysis tools
   Network configuration read tools
   Change management tools [HITL — network changes]
   Customer account tools
  
  
Telecom Systems
   Network Management System (Nokia NetAct, Ericsson ENM)
   ServiceNow (ITSM)
   Salesforce (CRM)
   OSS/BSS stacks
```

### UX Considerations

**24/7 operations require always-on agent availability.** NOC agents face:

- Sub-second alert display (delayed alerts in a network NOC have direct customer impact)
- Multiple simultaneous incidents (agent must handle parallel problem streams)
- Runbook generation on demand: "Show me the runbook for this BGP alarm type"
- Shift handover mode: summarize all open incidents and in-progress actions for the incoming engineer

**Human escalation is always one click away.** In high-severity incidents, the agent assists but a human decides:

- "Take action" requires explicit human approval for any network config change
- Emergency override: human can instantly suspend agent actions for all affected devices
- Audio alert for P1 incidents even when UI is in background

### Regulatory Constraints

| Regulation | Requirement |
| --- | --- |
| CALEA (US) | Lawful intercept access; agent must not interfere with interception systems |
| CPNI (US) | Customer proprietary network information — strict access controls; no CPNI in shared LLM context |
| GDPR (EU) | Customer data in network logs; consent and retention requirements |
| NIS2 Directive (EU) | Critical infrastructure security; incident reporting within 24 hours |

---

## 9. Knowledge Management & Enterprise Search

### Top Use Cases

| Use Case | Expected Value | HITL Requirement |
| --- | --- | --- |
| Enterprise search copilot | 35-50% reduction in time-to-answer for knowledge workers | Not required for search/retrieval; required for creating/publishing content |
| Document intelligence agent | 40-60% reduction in document review time | Required for decisions based on document analysis |
| SharePoint/Confluence copilot | 25-35% increase in knowledge base utilization | Not required for reading; required for content updates |

### Architecture

```text
Knowledge Worker
  
  
AG-UI Frontend (embedded in M365/SharePoint/Confluence)
   NLWeb interface for internal portal
   Source attribution on every answer
   Document viewer with relevant section highlighted
   Access-controlled results (user sees only permitted content)
   Content creation assistance with review workflow
  
  
Agent Runtime
   Enterprise search (Elastic, SharePoint Search, Vertex Search)
   Document retrieval tools
   Content creation tools
   Knowledge graph traversal
  
  
Knowledge Repositories
   SharePoint / OneDrive
   Confluence / Jira
   Box / Google Drive
   Internal databases and wikis
```

### UX Considerations

**Source attribution is the single most important trust signal.** Knowledge workers need to:

- See exactly which document each answer fragment came from
- One click to the exact page/section in the source document
- Freshness indicator on every source: "Last updated: March 2026"
- "Show me more like this" to explore the source document neighborhood

**Access control is surfaced to users:** The agent only shows results the user has permission to see. When a relevant document exists but user doesn't have access, the agent says "There is a relevant document you don't have access to — contact [document owner] to request access." This is better than silently omitting results.

**NLWeb integration:** Internal portals built on NLWeb expose structured content via natural language queries. Agent navigates internal knowledge with the same natural language interface as external web — but with full enterprise access control.

---

## 10. Life Sciences & Pharmaceuticals

### Top Use Cases

| Use Case | Expected Value | HITL Requirement |
| --- | --- | --- |
| Clinical trial assistance | 20-30% reduction in protocol development time | Mandatory for protocol approval |
| Regulatory submission (FDA/EMA) | 30-40% reduction in submission preparation time | Mandatory; all AI-generated content requires human review and signature |
| Drug discovery literature review | 50-60% reduction in literature review time | Advisory; human researcher validates all findings |

### Architecture

```text
Regulatory Affairs Specialist / Research Scientist / Clinical Trial Manager
  
  
AG-UI Frontend
   Document collaboration with AI suggestions
   Version-controlled AI-generated vs. human content tracking
   Electronic signature workflow (21 CFR Part 11 compliant)
   Regulatory checklist (FDA/EMA requirements)
   Audit trail for every AI contribution
  
  
Agent Runtime
   Literature retrieval (PubMed, ClinicalTrials.gov)
   Regulatory guidance retrieval (FDA, EMA databases)
   Document generation tools
   Statistical analysis assistance
  
  
Life Sciences Systems
   Veeva Vault (regulatory content management)
   MedDRA (medical terminology)
   CTMS (Clinical Trial Management System)
   EDC (Electronic Data Capture)
```

### UX Considerations

**Every AI-generated element must be distinguishable and traceable.** Regulatory submissions require:

- Clear visual distinction between AI-generated and human-authored content in every document
- AI contribution attribution: "AI-assisted — reviewed and approved by [name, date, signature]"
- Version control on every AI-assisted document showing change history
- Electronic signatures (21 CFR Part 11 compliant) on all documents containing AI-generated content

**Explainability for regulatory context:** Every AI-generated claim in a regulatory document must link to the supporting evidence:

- Every efficacy statement links to the clinical data source
- Every safety claim links to the adverse event data
- Regulatory guidance references link to the exact FDA/EMA guidance section

### Regulatory Constraints

| Regulation | Requirement |
| --- | --- |
| 21 CFR Part 11 (US FDA) | Electronic records and signatures for AI-assisted documents; audit trail; computer system validation |
| EU Clinical Trials Regulation | Clinical trial data integrity; AI contributions must be documented and auditable |
| ICH E6(R3) | Good Clinical Practice — data integrity requirements apply to AI-generated content |
| EU AI Act (High-risk) | Pharma AI systems likely classified as high-risk; human oversight, technical documentation required |
| GDPR | Patient data in clinical trials; consent and pseudonymization requirements |

---

## Cross-Industry Patterns

Regardless of industry, five UX patterns appear consistently in successful agentic deployments:

| Pattern | When | Why |
| --- | --- | --- |
| Source attribution | Every factual claim | Builds trust; enables verification; satisfies audit requirements |
| Explicit HITL for irreversible actions | Deletes, sends, executes, publishes | Risk management; regulatory compliance; user confidence |
| Progressive disclosure | All complex outputs | Reduce cognitive load; surface summary first, details on demand |
| Graceful degradation messaging | Any component failure | Maintain user trust even when system is degraded |
| Human escalation path | Every agent interaction | Non-negotiable for regulated industries; best practice for all |

---

## Related Pages

- [Part 1: Financial Services, Healthcare, Insurance, Retail, Manufacturing, and Developer Platforms](pathname:///archon/agentic-systems/agentic-ui/13-industry-reference-architectures) — Sections 1–6
- [Security Architecture](security-architecture.md) — Enterprise security controls across industries
- [Agent UX Patterns](agent-ux-patterns.md) — Human oversight models (HITL/HOTL/HOOL)
- [Governance](governance.md) — Compliance and governance frameworks
- [Enterprise Reference Architecture](enterprise-reference-architecture.md) — Backend platform architecture
