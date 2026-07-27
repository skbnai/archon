---
title: "AI Security Operations Center"
doc_type: guide
domain: trust
status: current
topic_id: ai-soc
last_reviewed: 2026-07-27
maturity: practitioner
supersedes: [docs/ai-security-governance/deep-mind/Part13_AI_SOC.md]
tags: [ai-security, ai-soc, deepmind, incident-response]
covers_version: "as of 2026"
---

Agent Detection and Response (ADR), AI-specific SIEM data sources, incident classification and response playbooks, AI forensics, and threat-hunting hypotheses for AI agent threats.

## Evolution of the SOC for AI Agent Threats

Traditional Security Operations Centers are optimized for detecting and responding to threats targeting human users and deterministic software systems. AI agent threats require SOC evolution in three dimensions: detection capabilities (new threat patterns), analyst skills (semantic understanding of AI behavior), and response procedures (AI-specific containment and recovery). The AI SOC is not a replacement for the traditional SOC — it is an extension that handles the AI threat surface as a specialization.

**AI SOC core requirement:** SOC analysts must be able to distinguish between an AI agent making unusual-but-authorized decisions and an AI agent that is compromised or misaligned. This requires semantic understanding of agent goals, context, and decision rationale — a capability not required in traditional SOC roles.

## AI-Specific SIEM Architecture

**SIEM data sources for AI agents:**

| Data Source | Content | Integration Method | Retention |
|---|---|---|---|
| Agent Action Logs | All tool calls, API requests, file operations | OpenTelemetry → SIEM ingest | 90 days hot / 3 years cold |
| Policy Decision Logs | All authorization decisions with context | Policy engine → SIEM | 1 year hot / 7 years cold |
| Behavioral Metrics | Anomaly scores, drift metrics, risk trajectories | Analytics platform → SIEM | 1 year hot |
| Memory Access Logs | All memory read/write operations | Memory governor → SIEM | 90 days hot / 3 years cold |
| Tool Invocation Logs | Tool calls, parameters, results metadata | Tool proxy → SIEM | 90 days hot / 3 years cold |
| Approval Gate Events | Human approval requests, decisions, reasoning | Approval workflow → SIEM | 7 years (audit record) |
| Identity Events | Token issuance, delegation, revocation, expiry | Identity broker → SIEM | 3 years |
| Circuit Breaker Events | Breaker trips, resets, incident correlation | Runtime monitor → SIEM | 3 years |

## Agent Detection and Response (ADR)

**ADR: the AI equivalent of EDR.** Endpoint Detection and Response (EDR) monitors endpoints for malicious activity and enables containment and investigation. Agent Detection and Response (ADR) is the analogous capability for AI agents: continuous monitoring, behavioral anomaly detection, automated or human-initiated containment, and forensic investigation support. ADR must be deeply integrated with the agent execution environment.

**ADR capabilities:**

| Capability | Description | Implementation |
|---|---|---|
| Continuous Behavioral Monitoring | Real-time monitoring of all agent actions against behavioral baseline | eBPF + OTel + behavioral ML model |
| Anomaly Detection | Statistical and ML-based detection of behavioral anomalies | Isolation Forest / LSTM anomaly detection on action sequences |
| Automated Containment | Circuit breaker triggers to isolate compromised agent without human delay | Runtime kill switch + capability token revocation |
| Human-Triggered Isolation | SOC analyst can quarantine agent with a single action | Incident response dashboard + kill switch API |
| Forensic Evidence Collection | Capture full agent state at time of detection | State snapshot API + reasoning trace export |
| Root Cause Analysis | Replay agent actions in a forensic environment | Action replay system in isolated sandbox |
| Threat Hunting | Proactive search for indicators of compromise in agent telemetry | SIEM query interface + threat hunting playbooks |
| Incident Timeline | Automated reconstruction of incident event sequence | Causality graph from correlated telemetry events |

## AI Incident Response Playbooks

**Incident classification:**

| Incident Type | Indicators | Severity | Response Time |
|---|---|---|---|
| Prompt Injection Detected | Injection pattern in action params; goal drift following external content retrieval | High | 15 min |
| Data Exfiltration Suspected | Anomalous data access + external API calls; volume spike | Critical | 5 min |
| Agent Identity Compromise | Token used from unexpected location; behavioral profile mismatch | Critical | 5 min |
| Memory Poisoning | Anomalous memory write; subsequent behavior change; new false belief detected | High | 30 min |
| Privilege Escalation | Permission request outside normal scope; new capability acquisition | High | 15 min |
| Goal Hijacking | Agent actions inconsistent with declared goal; semantic drift detected | High | 15 min |
| Circuit Breaker Trip | Automated containment triggered; root cause unknown | Medium-High | 30 min |
| Policy Violation | Hard constraint violation detected; unauthorized action attempted | Medium | 60 min |

## AI Forensics Procedures

**Evidence collection for AI incidents.** AI incident forensics must capture evidence beyond what traditional forensics requires. The chain of custody for AI incidents includes: prompts (the "scene of crime"), reasoning traces (the "suspect's mental state"), tool invocations (the "physical actions"), memory states (the "environment before and after"), and authorization decisions (the "access controls"). All evidence must be cryptographically verified to resist tampering claims.

| Evidence Type | Collection Method | Preservation Requirement |
|---|---|---|
| Agent state snapshot | Runtime state capture API at time of detection | Cryptographically sealed; write-once storage |
| Reasoning trace export | Full chain-of-thought export for incident window | Encrypted; access-controlled; chain of custody logged |
| Action history | SIEM query for all agent actions during incident window | Immutable SIEM export with hash verification |
| Memory state before/after | Memory governor snapshot at detection time + 24h prior | Hash-verified snapshot; diff analysis |
| Tool call logs | Full request/response logs including parameters | Immutable log export; PII protected |
| Authorization decisions | Policy engine decision log for incident window | Immutable export; includes full context |
| Communication logs | A2A and external API communication records | Immutable export with source/dest verification |

## Threat Hunting for AI Agents

**AI-specific threat hunting hypotheses:**

- **Long-tail Injection:** search for agents that retrieved external content immediately followed by unusual action sequences. Hypothesis: indirect prompt injection caused behavior change.
- **Permission Creep:** identify agents whose aggregate capability token set has grown over time without corresponding task complexity growth. Hypothesis: systematic permission accumulation.
- **Memory Anomaly Clusters:** identify memory writes that cluster around specific time periods and share semantic similarity. Hypothesis: coordinated memory poisoning campaign.
- **Cross-Agent Correlation:** identify statistically improbable correlations in actions across different agent instances. Hypothesis: cross-agent coordination or collusion.
- **Data Staging:** identify read operations across diverse data sources that aggregate toward a common external endpoint. Hypothesis: multi-stage data exfiltration in progress.
- **Goal Drift Cluster:** identify time periods where multiple agent types show simultaneous goal drift. Hypothesis: coordinated attack affecting multiple agents simultaneously.

## Related

- [AI Observability](16-ai-observability.md)
- [Enterprise Governance](18-enterprise-governance.md)
- [AI Control Series Overview](01-ai-control-series-overview.md)
