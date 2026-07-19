---
title: "Part 13 — Enterprise AI Security Model"
doc_type: guide
domain: strategy
topic_id: part-13-security-model
status: current
canonical: true
last_reviewed: 2026-07-19
covers_version: "as of 2026-07-14"
maturity: practitioner
personas: ["architect", "security-lead", "ciso"]
supersedes: ["docs/enterprise-ai-report/part-13-security-model.md"]
tags: ["ai-security", "zero-trust", "identity", "mcp-security", "a2a-security", "oauth", "spiffe", "encryption", "supply-chain-security"]
sources: []
---

# Part 13 — Enterprise AI Security Model

Enterprise AI requires a comprehensive security architecture spanning identity, network, data, and runtime planes. This page maps the complete AI security domain.

## AI Security Architecture Overview

<!-- TODO(diagram): Convert ASCII security model to Mermaid diagram showing identity, network, data, and runtime planes with control plane -->

AI security spans four planes plus a control plane:

- **Identity Plane:** Agent Identity, OAuth/OIDC, SPIFFE/SPIRE, Workload ID
- **Network Plane:** Zero Trust, API Gateway, mTLS, Service Mesh
- **Data Plane:** Encryption, KMS, Data Residency, Tenant Isolation
- **Runtime Plane:** Isolation, Containers, Firecracker, Sidecars
- **Control Plane:** Policy Enforcement, Admission Controllers, Audit Logging, Threat Detection, Supply Chain Security

## Security Domain Breakdown

### Zero Trust Architecture for AI

AI systems must operate under **Zero Trust** principles — never implicitly trust any request, regardless of network location.

**Zero Trust for AI means:**
- Every LLM API call must be authenticated and authorised (no anonymous access)
- Every agent action must carry a verified identity claim
- Every MCP tool call is evaluated against policy before execution
- Every data access is logged and can be audited
- Network location (internal vs. external) confers no implicit trust

### AI Identity

AI agents and AI platform components require machine identities to authenticate with services and to create auditable action trails.

**Identity models for AI:**

| Model | When to Use | Standard |
|-------|------------|----------|
| **IAM Role** | AI agents running in cloud (same-cloud resources) | AWS IAM, Azure Managed Identity, GCP Service Account |
| **OIDC Federated Identity** | Cross-cloud or cross-system agent identity | OIDC with STS |
| **SPIFFE/SPIRE** | Workload identity for containers and microservices | SPIFFE x.509 SVID |
| **OAuth 2.0 Client Credentials** | Agent-to-API authentication | OAuth 2.0 RFC 6749 |
| **mTLS** | Service-to-service (agent ↔ tool, agent ↔ MCP server) | X.509 certificates |

### MCP Security

The Model Context Protocol (MCP) introduces a new attack surface: a channel between AI agents and tool servers. MCP security requires:

- **Authentication:** MCP servers must authenticate agent identity before serving tools
- **Authorisation:** Agent may only call tools explicitly permitted by its scope
- **Input validation:** Tool inputs validated before execution (prompt injection via tool results is a key risk)
- **Output sanitisation:** Tool results validated before returning to agent
- **Rate limiting:** Tool call rate limits prevent resource exhaustion
- **Audit logging:** Every MCP tool call logged with agent identity, tool name, inputs, outputs, timestamp

### A2A Security

Agent-to-Agent (A2A) communication introduces additional risks when multiple agents collaborate.

**A2A security controls:**
- Mutual authentication between orchestrator and sub-agents
- Authorisation scoping: sub-agent inherits no more privilege than delegated
- Delegation chain audit trail (who authorised whom to do what)
- Prompt injection protection in inter-agent messages
- Agent impersonation prevention

### OAuth 2.0 and OIDC for AI

OAuth 2.0 and OIDC are the primary standards for:
- User-delegated authority to AI agents (user consents for agent to act on their behalf)
- Agent authentication to APIs and services
- Token-based authorisation with scoped permissions

**Key flows for AI:**
- **Client Credentials** — agent authenticates as itself (no user context)
- **Authorisation Code + PKCE** — user delegates authority to agent
- **On-Behalf-Of (OBO)** — agent calls downstream service on behalf of user with delegated token

### SPIFFE / SPIRE (Workload Identity)

SPIFFE (Secure Production Identity Framework for Everyone) provides a workload identity framework — each AI agent, MCP server, and platform component gets a cryptographic identity (SVID) that can be verified by any other component in the system.

**Why SPIFFE for AI agents?** Agents in containers or serverless functions don't have a stable IP or hostname. SPIFFE provides verifiable identity regardless of infrastructure.

### Secrets Management (KMS & Secrets Service)

AI systems use secrets (API keys, database credentials, model credentials) that must never appear in code, logs, or environment variables.

**Controls:**
- Secrets stored in KMS-backed secrets manager (AWS Secrets Manager, Azure Key Vault, GCP Secret Manager)
- Just-in-time injection at runtime; never persisted in app config
- Automatic rotation (API keys: 90-day rotation; mTLS certs: 1-year)
- Access to secrets gated by agent identity and policy
- Secret access audit trail

### Encryption

| Data State | Encryption Standard | Key Management |
|-----------|---------------------|---------------|
| Data at rest (vector DB, knowledge store, logs) | AES-256 | Customer-managed keys (CMK) via KMS |
| Data in transit (all API calls) | TLS 1.3 | Certificate Authority |
| Agent-to-tool (MCP) | mTLS | SPIFFE-issued SVID |
| LLM API calls | TLS 1.3 | Vendor-managed |
| Training/fine-tuning data | AES-256 | CMK |
| Model weights (proprietary) | AES-256 | CMK with HSM |

### Data Residency & Tenant Isolation

**Data Residency:**
- Define data classification tiers: Restricted (never leaves region), Sensitive (approved regions only), Internal (any enterprise region)
- Configure LLM API calls to enforce data residency (Azure OpenAI in-region, Bedrock with VPC endpoint)
- Log storage and vector databases deployed within approved regions
- Audit log exports to compliant regional storage

**Tenant Isolation:**
- In multi-tenant AI platforms, each tenant's data must be isolated
- Namespace-level isolation in vector databases
- Separate encryption keys per tenant (KMS with per-tenant CMK)
- Network isolation: separate VPCs or network policies per tenant
- Agent identity scoped to tenant namespace

### Runtime Isolation

AI agents executing code (code interpreter, tool execution) require strong runtime isolation.

| Isolation Technology | Strength | Use Case |
|---------------------|----------|----------|
| **Containers (Docker, containerd)** | Moderate | Standard agent isolation |
| **Firecracker microVMs** | High | Code interpreter, untrusted code execution |
| **gVisor** | High | Syscall filtering for agent containers |
| **Kata Containers** | High | VM-level isolation with container interface |
| **Process isolation (seccomp, AppArmor)** | Moderate | Supplementary controls within containers |

### Policy Enforcement

Runtime policy enforcement ensures every agent action is evaluated against policy before execution.

**Implementation:**
- **Open Policy Agent (OPA)** with Rego policies: declarative, version-controlled, auditable
- **Admission Controllers** (Kubernetes): validate agent deployment configs before admission
- **API Gateway policies**: rate limits, authentication, authorisation enforced at the gateway

**Policy examples:**
- Agent X may only call CRM API read endpoints (no write)
- No agent may send emails to external domains without human approval
- Cost-exceeding operations require HITL approval
- Data tagged "Restricted" may not be sent to external LLM APIs

### Audit Logging

Every AI action must be logged for security investigation, compliance, and governance purposes.

**Minimum audit log fields for AI actions:**

```
timestamp, agent_id, user_id, action_type, tool_name,
tool_inputs_hash, tool_output_hash, policy_decision,
session_id, trace_id, cost_tokens, latency_ms
```

**Log retention:** Minimum 90 days online; 7 years archive (regulated industries).

### Threat Detection

AI-specific threat detection monitors for:
- Unusual agent behaviour (tool call patterns deviating from baseline)
- Prompt injection attempts (patterns in inputs targeting system prompt override)
- Data exfiltration via AI (large output volumes, unusual retrieval patterns)
- Credential abuse (agent using credentials outside normal scope)
- Supply chain tampering (model or tool integrity check failures)

### AI Supply Chain Security

The AI supply chain includes: base model weights, fine-tuning datasets, Python dependencies, MCP tool code, third-party LLM APIs.

**Controls:**
- **AI SBOM** (Software Bill of Materials for AI): document every model, dataset, framework
- Model provenance verification: cryptographic hash of model weights at onboarding
- Dependency scanning: Python packages in AI workloads scanned for known vulnerabilities
- MCP tool code review: tool servers reviewed and approved before use by agents
- Vendor security assessment: LLM API providers assessed annually

## Authoritative Guides

Comprehensive AI security guidance is available in the **AI Security Governance**, **Cybersecurity Architecture**, and **AI Protocols** domains. Consult specialised guides for:

- Complete AI security architecture and reference implementation
- Identity, MCP, and A2A security blueprints
- AI supply chain security and SBOM management
- Policy engine design and OPA/Rego implementation
- Threat detection and response for AI systems
- Red teaming and adversarial testing methodologies

## Related

- [Part 6 — Governance](16-part-06-governance.md) — Security governance
- [Part 8 — Organizational Roles](18-part-08-organizational-roles.md) — AI Security Engineer role
- [Part 9 — Operating Processes](19-part-09-operating-processes.md) — Security incident response
- [Part 10 — Service Catalog](20-part-10-service-catalog.md) — AI Identity Service, Policy Engine, Guardrail Service
- [Part 12 — Responsible AI](22-part-12-responsible-ai.md) — OWASP LLM Top 10, MITRE ATLAS

## Sources

[No external sources for this page.]
