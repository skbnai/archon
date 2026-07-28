---
title: "Enterprise Agent Operating Model & Maturity Model"
doc_type: guide
domain: trust
status: current
topic_id: operating-model-maturity-roadmap
last_reviewed: 2026-07-27
maturity: practitioner
supersedes: [docs/ai-security-governance/security/06-Operating-Model-Maturity-Roadmap.md]
tags: [ai-security, operating-model, maturity-model, raci]
covers_version: "as of 2026"
---

The five-function agent operating model with RACI and KPIs, and a five-level enterprise agent maturity model for honest self-assessment.

## Who Builds It, Who Runs It

A complete reference architecture answers "what does a secure, governed agentic AI ecosystem look like." The harder organizational question is who builds it, who runs it, how success is measured, and in what order an enterprise should actually do this work given finite budget and finite people — the operating model, a maturity model for self-assessment, security review checklists, and an implementation roadmap.

## Enterprise Agent Operating Model

No single team owns agentic AI security end to end, and attempting to build one monolithic team is a common and costly early mistake. The operating model distributes accountability across five functions, deliberately mirroring how mature organizations already split traditional cybersecurity, cloud platform engineering, and data governance — because reporting agentic AI risk through entirely new, parallel structures tends to isolate it from the rest of the enterprise's risk management muscle rather than integrating with it.

**The five functions:**

| Function | Primary Mandate | Reports Into / Coordinates With |
|---|---|---|
| AI Governance Board | Sets policy, approves autonomy-level thresholds, owns the framework crosswalk, and is the final escalation point for risk acceptance decisions on individual agents | Chaired by the AI CISO; includes Legal, Compliance, Enterprise Architecture, and business-unit risk owners |
| AI Security Office | Owns the architecture and policy: identity substrate, MCP/A2A gateways, governance fabric, supply-chain controls | Reports to the AI CISO; works day-to-day with Platform Engineering on implementation |
| Agent Operations Team | Day-to-day agent lifecycle management: registration, provisioning, autonomy-level changes, retirement — operationalizing the Agent Registry | Reports to the AI Platform Architect; accountable for the Agent Registry's accuracy |
| Platform Engineering Team | Builds and operates the runtime, gateways, and mesh infrastructure | Reports to the AI Platform Architect; the engineering counterpart to the AI Security Office's policy |
| AI SOC | Continuous monitoring, detection, and incident response, including operating the kill-switch framework | Reports to the AI CISO, typically integrated into or co-located with the existing enterprise SOC |
| Red Team | Adversarial testing, feeding purple-team findings back into the AI SOC's detection logic | Reports to the AI CISO, organizationally independent from the AI Security Office to preserve adversarial objectivity |

**RACI — core program activities** (R = Responsible, A = Accountable, C = Consulted, I = Informed):

| Activity | AI Gov. Board | AI Security Office | Agent Ops | Platform Eng. | AI SOC | Red Team |
|---|---|---|---|---|---|---|
| Approve new agent autonomy level &ge;L3 | A | C | R | I | I | I |
| Define identity & MCP/A2A policy | C | A/R | I | C | I | I |
| Build & operate gateways and mesh | I | C | I | A/R | C | I |
| Maintain Agent Registry | I | C | A/R | I | C | I |
| Monitor & triage security incidents | I | C | C | C | A/R | I |
| Execute kill switch | I | C | C | C | A/R | I |
| Conduct red/purple team exercises | I | C | I | C | C | A/R |
| Regulatory filing / incident reporting | A | C | I | I | R | I |
| Quarterly risk reporting to board | A/R | C | I | I | C | I |

**KPIs:**

| KPI | Target Direction | Primary Source |
|---|---|---|
| % of active agents with complete Agent Registry entries | Toward 100% | Agent Registry audit |
| % of agents with standing (non-ephemeral) credentials | Toward 0% | Identity substrate audit |
| Mean time to detect (MTTD) an ASI-mapped incident | Down | AI SOC |
| Mean time to contain (MTTC) via kill switch | Down | AI SOC incident logs |
| Goal conformance rate (fleet average) | Up | Agent Reliability Engineering |
| % of red-team findings with a corresponding purple-team detection pattern shipped | Toward 100% | Purple Team tracking |
| % of MCP servers / A2A peers passing gateway validation on first registration attempt | Track trend, not a target direction in isolation | MCP/A2A gateway logs |
| Framework crosswalk coverage (regulations with current, evidenced control mapping) | Toward 100% | AI Governance Board |

## Enterprise Agent Maturity Model

Use this model for honest self-assessment, not for marketing the program internally. Most enterprises deploying agents in production today, including ones with significant AI investment, sit at Level 1 or the early part of Level 2 — current research on the state of agent identity is consistent on this point: authentication is largely solved with static credentials, while authorization, lifecycle management, and governance are not.

| Level | Designation | Characteristic State | Identity Pattern | Governance Pattern |
|---|---|---|---|---|
| 1 | Ad Hoc | Agents deployed by individual teams with no central inventory; security is whatever the deploying team happened to implement | Static API keys, shared service accounts | No central registry; no formal autonomy-level concept |
| 2 | Aware | A central team has visibility into most agents and has begun applying baseline controls, but enforcement is inconsistent across business units | Mix of static credentials and early workload-identity pilots | Agent Registry exists but is incomplete; manual, periodic review |
| 3 | Managed | Identity substrate (SPIFFE or equivalent) and MCP/A2A gateways are deployed organization-wide; the Agent Registry is the authoritative source of truth; autonomy levels are assigned and enforced | Ephemeral, workload-identity-issued credentials as the default | Framework crosswalk operating; AI Governance Board meets on a regular cadence |
| 4 | Measured | Agent Reliability Engineering SLIs/SLOs are operating; the AI SOC correlates across all seven monitored surfaces; kill-switch and FinOps circuit breakers are unified and tested | Trust-score-informed dynamic authorization layered on identity | Purple-team loop closed; KPIs reported quarterly to the board with trend data, not point-in-time snapshots |
| 5 | Optimizing | Post-quantum-ready identity and payment infrastructure; agent trust extends to verified external counterparties via decentralized identity/verifiable credentials; the program contributes back to industry standards bodies | Hybrid classical/PQC credentials; verifiable-credential-based external trust | Governance model anticipates regulatory change rather than reacting to it; the enterprise is a reference case other organizations benchmark against rather than only consuming |

## Related

- [Enterprise Agent Operating Model: Checklists, Interview Guide & Roadmap (Part 2)](parts/37-operating-model-maturity-roadmap-part2.md) — production readiness checklists, an architect interview guide, and a 24-month implementation roadmap
- [Enterprise Governance](18-enterprise-governance.md)
- [Foundations & Reference Architecture](33-foundations-reference-architecture.md)
