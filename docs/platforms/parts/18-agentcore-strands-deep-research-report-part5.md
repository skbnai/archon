---
title: "Amazon Bedrock AgentCore & Strands SDK — Deep Technical Research Report (Part 5)"
doc_type: guide
domain: platforms
status: current
topic_id: agentcore-strands-deep-research-report-part5
last_reviewed: 2026-07-27
maturity: practitioner
supersedes: []
tags: [aws, agentcore, security, threat-model, production-architecture]
covers_version: "as of 2026-07-10"
---

> Continues from [Amazon Bedrock AgentCore & Strands SDK — Deep Technical Research Report](../18-agentcore-strands-deep-research-report.md), covering the complete security threat model, production architecture patterns, and the April–June 2026 release analysis.

## Part XIII — Security: Complete Threat Model

### Threat Model Overview

Agentic systems introduce a genuinely new class of attack surface distinct from traditional application security: the "exploit" can be a sentence, delivered through any content the agent reads, not just through a direct network request. This section maps each major threat class to the specific AgentCore capability designed to mitigate it, and — critically — notes where independent research shows the mitigation is partial or was found deficient.

### Prompt Injection

**Threat.** An attacker embeds instructions in content the agent will read as part of its task context — a retrieved document, a tool result, a PR title, a web page — rather than in the user's direct input. If the agent treats retrieved content with the same trust as its system instructions, it may follow the injected instruction. OWASP ranks prompt injection the #1 vulnerability in its LLM Top 10. A documented April 2026 academic/industry demonstration (Guan et al., Johns Hopkins) hijacked Claude Code, Gemini CLI, and GitHub Copilot via instructions embedded in GitHub PR titles, exfiltrating CI secrets through PR comments — illustrating the pattern is not theoretical.

**AgentCore mitigation.** Bedrock Guardrails, integrated directly into Policy/Gateway as of the April–June 2026 wave, evaluates *inputs to gateway targets* for injection attempts at the Gateway layer — structurally outside the agent's own context, so the agent cannot "reason around" a check it never sees. This is a materially stronger position than prompt-level defenses (system-prompt instructions telling the model to ignore injected commands), which remain bypassable by construction. However, Guardrails-at-Gateway defends the *tool-call boundary*; it does not prevent an already-injected instruction from influencing the agent's *reasoning or final text response* if the injected content never triggers a Gateway-mediated tool call. Defense-in-depth guidance (hidekazu-konishi.com, April 2026) recommends layering an **input guardrail with denied-topic policies** seeded with concrete jailbreak patterns (role-reassignment phrases, system-prompt-extraction phrases, encoding-based bypasses, and known indirect-injection markers) in addition to, not instead of, Gateway-layer Guardrails.

### Tool (Injection) Poisoning / MCP Poisoning

**Threat.** A malicious or compromised MCP server, or a tampered tool *description* (metadata the agent reads to decide when/how to use a tool, often invisible to the end user), redirects the agent toward unintended actions without any change to the agent's own code. Documented real-world instances in 2026 include a malicious MCP package (`postmark-mcp`) that shipped fifteen clean releases to build trust before quietly adding an exfiltration line, and large-scale scans finding hundreds of internet-exposed MCP servers with zero authentication.

**AgentCore mitigation.** Gateway's aggregation model means every MCP target an agent reaches through AgentCore should itself be a vetted, Registry-catalogued resource (once Registry's approval workflow is used as intended) rather than an ad hoc, unvetted server URL. Cedar policy evaluation happens per **tool call**, not merely per tool *description* — so even if a description is misleading, the actual invoked action, its arguments, and the calling principal are still checked against policy at the moment of execution. Registry's Approver persona and auto-approval-off-by-default posture is specifically the governance control against onboarding an unvetted or poisoned tool into the organization's shared catalog in the first place.

### Data Exfiltration

**Threat.** An agent with legitimate access to sensitive data is manipulated (via injection or a poisoned tool) into sending that data somewhere it shouldn't go — an external API, a DNS query, an unauthorized recipient.

**AgentCore mitigation.** Cedar policy can restrict which tools/destinations a given principal may reach and under what data conditions (the geography/data-residency pattern documented in Part IV is a direct instance of this). RESPONSE interceptors can redact sensitive fields from tool results before they re-enter the agent's context. Guardrails specifically screens for sensitive-data exposure at the Gateway boundary. **However**, the independently-documented Code Interpreter Sandbox-mode DNS gap (Part IX) is a concrete, real-world instance where a documented isolation boundary against exfiltration was weaker than advertised — the corrective control (VPC-only network mode plus least-privilege IAM roles specifically for the interpreter) should be treated as a required hardening step, not an optional one, for any workload where exfiltration risk matters.

### Cross-Agent Attacks (Multi-Agent Trust Boundaries)

**Threat.** In a Graph/Swarm/supervisor-worker topology, a compromised or manipulated specialist agent could attempt to escalate privilege, access another user's data, or feed poisoned output back up the chain to the supervisor, which may trust it uncritically.

**AgentCore mitigation.** Identity propagation (Part VII) means a specialist agent's downstream tool calls are still evaluated against the *original user's* identity claims, not an elevated system identity — a compromised specialist cannot gain access the original user didn't have, regardless of how many hops deep it sits. Each agent in the chain, if deployed as a separate Runtime, gets its own microVM-isolated execution boundary and its own workload identity, so a compromise of one specialist agent's process does not directly grant code-level access to a sibling agent's memory or filesystem.

### Privilege Escalation / Confused Deputy

**Threat.** A shared, over-broadly-trusted execution role lets an unrelated AgentCore resource (in the same or a different account) assume permissions intended for a specific Gateway or Runtime.

**AgentCore mitigation.** As detailed in Part VII, this is directly guarded against via `aws:SourceArn`/`aws:SourceAccount` conditions scoped to the specific resource ARN in every execution-role trust policy AWS's own samples ship. This is a **configuration responsibility**, not an automatic platform guarantee — omitting the condition (a documented, easy-to-miss mistake) reopens the confused-deputy path via the shared `bedrock-agentcore.amazonaws.com` service principal.

### Replay Attacks and Token Theft

**Threat.** A captured OAuth authorization code or bearer token is replayed by an attacker to impersonate a legitimate agent or user session.

**AgentCore mitigation.** Session-binding mechanisms in the 3LO callback flow (Part VII, DeepWiki-documented) tie the authorization code's completion to a whitelisted, pre-registered callback URL per workload identity, structurally preventing redirect hijacking. Token Vault-issued credentials are short-lived and scoped; the Workload Access Token pattern means raw user tokens are never forwarded downstream to third-party resource servers, limiting the blast radius of any single token's theft.

### Secret Management

**Threat.** Long-lived credentials embedded in agent code, container images, or environment variables.

**AgentCore mitigation.** The Token Vault is the sanctioned pattern precisely to eliminate this class of risk — credentials for downstream resources are fetched at invocation time via `@requires_access_token`/`@requires_api_key` decorators (in Strands-on-AgentCore code) rather than hard-coded, and are encrypted at rest and in transit.

### Runtime, Browser, and Code Interpreter Isolation — Summary Assessment

All three compute-hosting primitives (Runtime, Browser, Code Interpreter) share the Firecracker-microVM-per-session isolation model, which independent security researchers (BeyondTrust: *"we applaud AWS for providing strong isolation properties of a full KVM-based VM"*) rate favorably relative to "agent as a service" competitors offering weaker container-only isolation. The documented weak point is specifically **network policy within an otherwise well-isolated VM boundary** (the Sandbox-mode DNS gap) and **IAM-permission scoping independent of network isolation** (the Sonrai S3-reachability finding) — not the VM isolation boundary itself, which held up under scrutiny. The practical takeaway for a threat model: trust the hardware-level session isolation; **do not** trust "Sandbox" network-mode naming alone to mean zero egress, and always pair network-mode hardening with least-privilege IAM scoping on the specific execution role.

## Part XIV — Production Architecture

### Network Connectivity Patterns

AWS's own networking blog (May 2026) documents four progressively hardened patterns for AgentCore Runtime; the same patterns generalize to Gateway and Browser/Code Interpreter:

1. **Public endpoint, public egress (default).** Fastest to stand up; both inbound and outbound traffic traverse the internet. Appropriate only for prototyping or genuinely public-facing agents with no sensitive backend access.
2. **VPC egress via ENI, public ingress.** AgentCore provisions ENIs in customer-specified subnets so the agent can reach private resources (RDS, internal APIs, on-prem via Direct Connect/VPN) — but the agent's own inbound endpoint remains internet-reachable.
3. **PrivateLink ingress + VPC egress, public ingress blocked.** A resource-based policy condition (`aws:SourceVpce`/`aws:SourceVpc`) rejects any request not arriving via the customer's own VPC endpoint; combined with pattern 2's egress, this fully removes the public internet from both directions of agent traffic — except for OAuth IdP round-trips and Gateway-to-external-MCP-server calls, which still require internet egress unless those specific targets are themselves reachable via PrivateLink or a private connectivity path.
4. **Full isolation — no IGW/NAT.** Every AWS service call (ECR image pulls, CloudWatch Logs, X-Ray, Bedrock) routes through its own VPC endpoint; no traffic enters or leaves the VPC through the public internet under any circumstance. This is the correct target state for the highest-sensitivity workloads (regulated PII/PHI/financial data) and is explicitly called out by AWS as providing the highest level of network isolation available on the platform.

Three distinct PrivateLink endpoint types exist and must be provisioned separately: the **data plane** endpoint (`bedrock-agentcore`) for Runtime/Memory/Identity/built-in-tools invocation, the **control plane** endpoint (`bedrock-agentcore-control`) for Runtime/Memory management operations, and the dedicated **Gateway** endpoint (`bedrock-agentcore.gateway`).

### Multi-Account and Multi-Region Patterns

- **Single account.** Simplest; appropriate for a single team or early-stage adoption. All AgentCore resources (Runtime, Gateway, Registry, Policy engines) live in one account, one region.
- **Multi-account (recommended enterprise pattern).** A platform/security account owns shared Gateway targets, Registry catalogs, and Policy engine templates; workload accounts own their own Runtime/Harness deployments and consume the platform account's governed catalog via cross-account IAM roles. As documented in Part V, **Registry currently has no native cross-account federation** (April 2026 preview state) — this pattern today requires custom cross-account IAM role assumption and manual catalog synchronization rather than a native federation feature, a real operational gap worth planning around explicitly rather than assuming away.
- **Multi-region.** AgentCore Runtime, Gateway, Policy, and Identity are regional services; a genuinely multi-region deployment requires independently provisioned resources per region, with cross-region replication of Memory data and Registry catalogs handled at the application/IaC layer (there is no documented native cross-region Memory or Registry replication as of June 2026).

### Disaster Recovery: Active-Active vs. Active-Passive

- **Active-passive.** A standby region holds provisioned-but-idle Runtime/Gateway/Policy resources, with Route 53 or Global Accelerator failover redirecting traffic on primary-region failure. Memory and Registry state require an explicit replication mechanism (e.g., DynamoDB Global Tables if state has been externalized there, or scheduled Registry-record export/import) since neither service natively replicates cross-region.
- **Active-active.** Both regions serve live traffic; session affinity becomes region-scoped (a session started in one region should not expect its microVM state to be reachable from the other), which pushes any genuinely cross-region session continuity requirement onto an externalized state store with its own cross-region replication (DynamoDB Global Tables, Aurora Global Database, or a cross-region cache).
- The consumption-based, serverless nature of Runtime/Gateway/Harness means a standby region's *idle* cost is materially lower than a comparable EC2/EKS active-passive DR posture — no idle compute capacity needs to be paid for beyond Memory storage and any pre-warmed session pool a team chooses to maintain (Part III).

### Hybrid Cloud

VPC connectivity plus Direct Connect/VPN lets AgentCore Runtime, Browser, and Code Interpreter reach on-premises systems as if they were private VPC resources, without exposing those systems to the public internet. The identity-federation limitation noted in Part VII (no native cross-cloud agent-identity unification with Azure/GCP) is the primary architectural gap for genuinely hybrid or multi-cloud agent estates; a third-party identity-federation layer, or a deliberate choice to run cloud-specific agent fleets per provider with governed hand-offs at defined boundaries, are the two practical mitigations as of mid-2026.

## Part XV — Release Analysis: April–June 2026

### Chronological Timeline

| Date | Release | Significance |
|---|---|---|
| **March 3, 2026** | **Policy** reaches GA | Deterministic, Cedar-based, Gateway-enforced authorization becomes a production-ready control, not a preview feature |
| **March 31, 2026** | **Evaluations** reaches GA | 13 built-in evaluators; continuous quality monitoring becomes standard, integrated with CloudWatch |
| **~April 2026** | **Registry** enters public preview | Governance catalog for agents/tools/skills; four-persona IAM model; five regions; free during preview |
| **April 22, 2026** | **Harness** enters public preview | Two-API-call agent definition; Strands-powered; no orchestration code required |
| **April 28, 2026** | AWS "What's Next" event | Managed harness (preview), AgentCore CLI (IaC-governed deployment, CDK at launch, Terraform later in 2026), AgentCore skills for coding assistants |
| **~May 2026** | **Optimization** (recommendations + failure insights) reaches GA | Production-trace-driven prompt/tool-description recommendations; silent-failure pattern mining across sessions |
| **May 7, 2026** | **Payments** enters preview | Agent-autonomous transacting via x402 protocol; Coinbase CDP and Stripe Privy wallet connections; four regions |
| **~May–June 2026** | Gateway: Runtime-as-target GA | Gateway can front a Runtime agent directly as an HTTP target with API-schema-driven Guardrails application |
| **June 1, 2026** | AWS blog: Policy + Lambda interceptor composability patterns | Formalizes the three-pattern design guidance (policy-only, interceptor-only, combined) for production security architecture |
| **June 17, 2026** | AWS Summit New York — **AWS Continuum** and **AWS Context** previewed | Adjacent (non-AgentCore) platform services signaling AWS's "trust ladder" investment direction (see Part XVII) |
| **June 18, 2026** | **Harness** reaches GA | Multi-model mid-session switching; auto-provisioned managed memory; A/B testing; Step Functions integration; export to Strands code |
| **Ongoing (June 2026)** | Runtime quota increases | Active sessions per account raised to 5,000 (us-east-1/us-west-2) / 2,500 (other regions); `InvokeAgentRuntime` rate raised from 25 to 200 TPS per agent per account |

### Feature-Level Deep Dives

**Policy GA — Migration Guidance.** Teams that built custom in-agent-code authorization logic before Policy's GA should migrate incrementally: stand up a Policy engine in **LOG_ONLY** mode alongside existing controls, validate that Cedar decisions match the legacy logic's expected outcomes against real traffic, then cut over to **ENFORCE** and only *then* remove the legacy in-code checks. Removing in-code checks before ENFORCE validation is complete leaves a window with no authorization at all.

**Harness GA — Migration Guidance.** Teams that built early prototypes directly on Runtime with hand-written Strands orchestration should evaluate whether Harness's configuration-only model now covers their use case — the GA "export to Strands code" feature is explicitly designed to make this a **two-way**, not one-way, decision: start on Harness for speed, export to full Strands/Runtime control if and when the configuration surface becomes limiting, rather than needing to choose irreversibly at project start.

**Registry Preview — Adoption Guidance.** Given the documented preview-stage limitations (Part V), the responsible adoption pattern in June 2026 is: use Registry now for the low-risk, high-value use case it already supports well — a build-time, human-governed catalog of *internal* skills and vetted MCP tools within a single account — while explicitly not yet depending on it for cross-account federation or IaC-managed provisioning, both of which are roadmap items rather than current capabilities.

**Payments Preview — Risk Framing.** Payments is explicitly preview-only and should not be treated as a production payment rail. AWS's own design channels risk through **deterministic, infrastructure-layer spend limits** (set at the session level) rather than trusting the agent's own reasoning to self-limit spend — consistent with the platform's overall philosophy (enforcement outside the agent's reasoning, not inside it). The Coinbase x402 Bazaar MCP server integration (10,000+ payable endpoints) previews a genuinely new category of agent-to-service commerce, but four-region availability and preview status mean production dependence should wait for GA and a second look at independent security research once broader adoption produces a research target.

## Related

- [Deep Research Report](../18-agentcore-strands-deep-research-report.md) — executive summary, platform foundations, Runtime, Gateway
- [Deep Research Report (Part 4)](18-agentcore-strands-deep-research-report-part4.md) — Strands Agents SDK deep dive, Observability
- [Deep Research Report (Part 6)](18-agentcore-strands-deep-research-report-part6.md) — Roadmap prediction, adjacent roadmap signal, best practices, anti-patterns
