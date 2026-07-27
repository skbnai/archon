---
title: "Reference Architecture"
doc_type: guide
domain: trust
status: current
topic_id: reference-architecture
last_reviewed: 2026-07-27
maturity: practitioner
supersedes: [docs/ai-security-governance/deep-mind/Part16_Reference_Architecture.md]
tags: [ai-security, reference-architecture, deepmind, air-gapped]
covers_version: "as of 2026"
---

Production-grade reference architectures for single-agent, multi-agent, finance, healthcare, highly regulated, and air-gapped AI agent deployments.

## Architecture Taxonomy and Selection Criteria

The following reference architectures address the most common enterprise AI agent deployment patterns. Each architecture is designed to be production-deployable, not just conceptual. Selection criteria for each pattern are provided to help architects choose the appropriate baseline for their use case.

- **Pattern 1 — Single-Agent Internal Assistant:** &lt;5 integrated systems; single business unit; &lt;500 users; low-medium data sensitivity.
- **Pattern 2 — Multi-Agent Workflow Platform:** &gt;5 integrated systems; cross-functional workflows; complex task decomposition; medium-high data sensitivity.
- **Pattern 3 — Enterprise Agent Platform:** platform serving multiple BUs; diverse agent types; high scale; governance requirements.
- **Pattern 4 — Highly Regulated Environment:** financial services, healthcare, government; strict compliance; audit requirements; adversarial threat model.
- **Pattern 5 — Air-Gapped Deployment:** classified environments; no internet connectivity; on-premises only; maximum security controls.

## Pattern 1: Single-Agent Internal Assistant

**Component architecture:**

| Component | Technology | Security Config |
|---|---|---|
| Agent Framework | LangGraph / Anthropic SDK | Checkpoint enabled; interrupt on risk threshold |
| LLM Endpoint | Anthropic API / AWS Bedrock | Private endpoint; mTLS; no model logging (data residency) |
| Identity | SPIFFE SVID (short-lived) | Auto-rotate every 1 hour; revocation on session end |
| Authorization | OPA sidecar | Hard constraints + contextual ABAC; &lt;5ms P99 latency |
| Tool Execution | Isolated Lambda / Cloud Run | Per-invocation container; VPC isolation; secrets from Vault |
| Memory | PostgreSQL + pgvector | Encrypted at rest (AES-256); access control by session ID; RLS |
| Observability | Langfuse + OTel Collector | Reasoning traces encrypted; PII redaction pipeline |
| Human Approval | Slack workflow integration | SLA: 5 min for high-risk; 15 min for medium-risk |
| Audit Store | Immutable S3 / CloudWatch Logs | Object Lock (WORM); 3-year retention; encrypted |

## Pattern 2: Multi-Agent Workflow Platform

**Orchestration architecture.** Multi-agent workflow platforms require additional security architecture around inter-agent trust, shared resource governance, and workflow-level risk assessment. The orchestrator is the highest-risk component because it controls multiple agents and has broad visibility into workflow state.

| Component | Technology | Security Config |
|---|---|---|
| Orchestrator | LangGraph multi-agent / AutoGen | Minimal orchestrator permissions; cannot elevate sub-agent trust |
| Sub-Agent Pool | Specialized agents per function | Each has independent policy enforcement; own identity |
| Inter-Agent Bus | Kafka / Google Pub/Sub | mTLS; message signing; agent identity in message header |
| Shared Memory | Redis (ephemeral) + PostgreSQL (persistent) | Namespace isolation; agent-scoped read/write; no cross-namespace |
| Tool Registry | Custom registry service | Registry as single source of truth; agents cannot bypass |
| Workflow Governance | Temporal.io | Workflow audit log; step-level policy enforcement hooks |
| Risk Aggregation | Custom risk service | Aggregate risk across all agents in workflow; workflow-level circuit breaker |
| Cross-Agent Monitoring | Behavioral analytics with cross-correlation | Detect collusion patterns; correlated anomaly detection |

## Vertical-Specific Architectures

### Finance Agent Architecture

Finance agents require the most stringent security controls due to the combination of high-value targets, strict regulatory requirements (SOX, PCI DSS, Basel III), and the potential for direct financial loss from unauthorized actions.

- **Financial Action Limits:** every financial action has a hard dollar limit enforced by the policy engine; limits are defined by transaction type and require human approval above threshold.
- **Four-Eyes Principle:** all financial transactions above defined thresholds require approval from two separate humans, implemented as dual-signature in the approval workflow.
- **Real-Time Fraud Detection:** every agent-initiated financial transaction is submitted to a fraud detection service before execution; block and alert if the fraud score exceeds threshold.
- **Complete Audit Trail:** every financial action retains agent identity, delegating user, business justification, full action parameters, approval chain, and timestamp — retained 7 years minimum.
- **Market Data Isolation:** agent access to market data through a rate-limited, type-safe proxy; raw websocket access prohibited.
- **Sandbox Testing:** all new finance agent capabilities must pass identical scenarios in a production-mirrored sandbox before deployment.

### Healthcare Agent Architecture

- **PHI Access Controls:** all PHI access requires a patient consent check, treating relationship verification, the minimum necessary principle, and BAA compliance for the agent framework provider.
- **De-identification Pipeline:** PHI de-identified before entering model context using the Safe Harbor or Expert Determination method; re-identification prohibited.
- **Prescriptive Action Restrictions:** agents cannot prescribe medications, diagnose conditions, or recommend treatments; these actions require human clinician review.
- **Audit for HIPAA:** full audit trail of all PHI access; the access log includes the reason for access; available for patient request within 60 days.

### Highly Regulated Environment Architecture

For highly regulated environments (financial services, healthcare, government), the baseline security architecture is supplemented with:

- **Hardware Security Modules (HSMs):** all cryptographic operations performed by HSMs; keys never leave the HSM boundary.
- **Confidential Computing:** agent execution in Intel TDX or AMD SEV-SNP confidential VMs; memory encrypted even from the cloud provider.
- **Zero-Knowledge Audit:** audit records structured to provide compliance evidence without exposing sensitive agent context.
- **Formal Approval Workflows:** all high-risk agent deployments require formal risk acceptance sign-off at SVP level minimum.
- **Regulatory Sandbox:** all new agent capabilities tested in a regulatory sandbox environment mirroring production controls.
- **Compliance Automated Reporting:** monthly automated compliance reports generated from telemetry data; no manual data collection.

## Air-Gapped Deployment Architecture

Air-gapped deployments require all AI capabilities — models, tools, knowledge bases, and governance services — to operate without internet connectivity. This creates specific challenges for model currency, threat intelligence updates, and certificate management.

| Challenge | Air-Gapped Solution |
|---|---|
| Model access | On-premises model serving (Ollama, vLLM, llama.cpp) with locally hosted open-weight models |
| Model updates | Manual update process with offline verification; cryptographically signed model packages delivered via secure physical media |
| Threat intelligence | Periodic offline updates to MITRE ATLAS signatures; manual review of security advisories |
| Certificate management | Internal PKI with offline root CA; online intermediate CAs within the air-gapped network |
| Tool connectivity | All tools must operate against internal systems only; external API proxy with data diode for approved one-way feeds |
| Observability | Internal ELK stack or Grafana; no external telemetry export; local behavioral analytics models |
| Identity federation | Internal SPIFFE/SPIRE deployment with no external trust federation; local identity broker |
| Policy updates | Policy changes go through formal change management; digitally signed policy packages |

## Related

- [Cloud Implementation Comparison](19-cloud-implementation-comparison.md)
- [Best Practices & Anti-Patterns](21-best-practices-anti-patterns.md)
- [AI Control Series Overview](01-ai-control-series-overview.md)
