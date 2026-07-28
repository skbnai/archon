---
title: "Agentic AI Security Architecture & Multi-Layer Guardrails (2 of 2)"
doc_type: guide
domain: trust
status: current
topic_id: agentic-ai-security-guardrails-part2
last_reviewed: 2026-07-28
maturity: practitioner
supersedes: []
tags: [agentic-ai, security-architecture, vendor-implementations, compliance]
covers_version: "as of 2026-07-10"
---

Continuing from [Part 1](../04-agentic-ai-security-guardrails.md) (core doctrine, the 18-class threat catalog, threat-model method, and the 14-layer guardrail map): this part covers how Google, Microsoft, and AWS implement agentic AI security at scale, how leading consultancies frame it, real-world case studies, the compliance overlay, and the full security architecture review checklist.

## How Google Implements at Scale

Google's stack integrates cloud-native security with AI-specific controls. Threat prevention: Vertex AI Model Armor (managed guardrails for prompt injection, jailbreak classification, and toxicity filtering integrated directly into Vertex AI endpoints); Sensitive Data Protection/DLP API (output-layer PII detection and redaction before responses reach downstream systems); Cloud Armor plus Apigee (gateway-layer DDoS/rate-limiting and API management as the deterministic outer shell, with quota enforcement and allowlisted egress). Identity and isolation: Workload Identity Federation (OIDC-based agent identity without static API keys, SPIFFE/SPIRE-equivalent for GKE-hosted agents); GKE Sandbox/gVisor (user-space kernel syscall-level isolation without hardware VM overhead, microVM-equivalent blast-radius containment); Binary Authorization (signed container images enforced at deployment, supply chain integrity for agent runtimes). Detection and response: Chronicle SIEM (centralized analytics ingesting agent audit logs, tool call logs, and egress events, with behavioral analytics on action sequences); Security Command Center (an aggregated view of guardrail findings, DLP hits, and anomaly detections across the fleet); Gemini Security AI (AI-powered threat hunting within Chronicle via natural-language queries over agent behavioral logs). Google's AI security team sits within the broader Cloud Trust organization with dedicated red-team capacity for Gemini and Vertex AI agents, and external researchers can report agent-behavior findings through the Google VRP.

## How Microsoft Implements at Scale

Microsoft integrates Azure security services with its Responsible AI principles. Threat prevention: Azure AI Content Safety Prompt Shield (a dedicated indirect-injection classifier trained specifically on instructions embedded in retrieved documents and tool results — the hardest guardrail problem to solve deterministically); Azure Content Safety (a multi-modal toxicity/harm/policy-violation classifier for both inputs and outputs, with FP/FN tracking via the Azure AI Foundry evaluation hub); Azure API Management (gateway-layer rate limiting, IP allowlisting, JWT validation, and egress control for agent-to-external-system traffic). Identity and isolation: Entra Agent ID/Workload Identity (Microsoft's managed AI agent identity, federated credentials eliminating static secrets, audience-scoped short-TTL tokens); Azure Confidential Computing (hardware TEEs for agent runtimes processing regulated data, enclave-level isolation for the most sensitive workloads); Azure Policy (infrastructure-layer guardrail enforcement, deny policies for non-compliant configurations like public endpoint exposure or unencrypted storage). Detection and response: Microsoft Defender for Cloud AI Threat Protection (real-time detection of prompt injection, anomalous tool usage, and exfiltration patterns); Microsoft Sentinel (SIEM with pre-built agent security incident playbooks and automated identity-revocation/session-termination response); Purview Information Protection (data lineage from source systems through agent context into outputs, with legal hold for the agent evidence store). Microsoft's Responsible AI team maintains the AI red team (AIRT) which specifically attacks Copilot and Azure AI agent deployments, with findings feeding guardrail updates — and the Security Copilot product itself operates on the same architecture it defends.

## How AWS Implements at Scale

AWS centers its agentic AI security on Bedrock Guardrails and the broader AWS security fabric. Threat prevention: Amazon Bedrock Guardrails (six control types — content filters with configurable severity, topic deny lists, word filters, PII detection/redaction across 20+ entity types, grounding checks for RAG answer faithfulness, and sensitive information filters combining regex and ML patterns); AWS WAF plus CloudFront (a deterministic outer shell for rate limiting, geo-blocking, and IP allowlisting before requests reach agent infrastructure); Amazon Macie (DLP scanning of S3 buckets used as agent knowledge and evidence stores). Identity and isolation: AWS Nitro Enclaves (isolated compute for agent runtimes processing regulated data, no persistent storage, no operator access, attested via the Nitro Attestation Document); IAM roles for service accounts/IRSA (short-lived credentials bound to Kubernetes service accounts, SPIFFE/SVID-equivalent for EKS-hosted agents); Amazon Inspector (automated vulnerability scanning of agent container images and the AI-BOM tracking model/SDK/MCP package versions per deployment). Detection and response: Amazon GuardDuty (runtime threat detection for unusual API call patterns, credential exfiltration signals, and cross-account activity from agent roles); AWS Security Hub (aggregated findings across GuardDuty, Inspector, and Macie with agent-specific custom insights); CloudWatch Logs plus Contributor Insights (tool audit logging at scale with anomaly detection and behavioral delta alerting on tool-call frequency). Amazon's AI Security Center of Excellence maintains the threat model for all Bedrock services and publishes a shared responsibility model explicitly extending traditional compute responsibility to include prompt integrity, tool manifest integrity, and memory provenance as customer responsibilities.

## How Top Consultancies Frame AI Security

Accenture's "Responsible AI Shield" is a five-layer model: Perimeter (API gateway controls, authentication, rate limiting), Behavioral (guardrail classifiers and policy engines per request), Identity (agent workload identity, delegation chain integrity), Data (provenance tracking, DLP, residency enforcement), and Audit (immutable logs, evidence store, regulatory reporting) — their engagements typically open with a 4-week AI threat-model workshop producing a prioritized risk register mapped to the client's existing ISO 27001 control framework with AI-specific extensions.

McKinsey's AI Security Maturity Model runs four stages: Level 1 Reactive (basic content filters, manual incident response, security bolted on after deployment); Level 2 Proactive (systematic threat modeling, automated guardrails, security in the design process); Level 3 Embedded (security-by-design, continuous adversarial testing in CI, behavioral monitoring as business-as-usual); Level 4 Adaptive (self-improving defenses, red-team findings automatically feeding guardrail updates, AI-assisted threat hunting) — McKinsey's research finds most enterprises deploying agentic AI in 2025-2026 enter at Level 1 and need 12-18 months to reach Level 3.

Deloitte's AI Trust Model treats AI security as a trust assurance problem across four dimensions: Technical trust (guardrails, testing, security architecture), Process trust (change management, incident response, audit trails), Regulatory trust (compliance mapping, evidence generation, regulator engagement), and Stakeholder trust (explainability, human oversight, escalation paths) — emphasizing that in regulated industries, the audit trail and regulatory evidence package matter as much as the technical controls themselves.

Across finance and healthcare, the Big Four's common engagement pattern runs seven steps: AI-BOM creation (inventory all model/SDK/prompt-template/fine-tuning-dataset versions); trust boundary mapping (a formal diagram of every agent-to-system and agent-to-agent data flow); a threat model workshop (STRIDE plus the OWASP agentic taxonomy applied per boundary); control gap analysis (current versus target state, a prioritized remediation roadmap); guardrail architecture design (a layer map tailored to the specific agent workflow); a red-team exercise (adversarial testing against the deployed system); and audit readiness (an evidence package mapping controls to regulatory requirements).

## Real-World Big Wins

JPMorgan Chase expanded its COIN (contract review AI) program into a multi-agent system handling loan servicing, compliance checking, and trade processing. The security architecture that enabled regulatory approval: egress control as an invariant (agents cannot reach external networks, all external calls route through a proxied allowlisted gateway); hallucination containment (schema validation plus reference-validity checks before any financial record mutation, with saga compensation for rollback); and audit completeness (every action logged with the full actor chain — a non-negotiable OCC requirement). The architecture let JPMorgan demonstrate to regulators that even in a worst-case injection attack, no agent could authorize a transaction outside its bounded decision scope.

Salesforce's Agentforce platform (using Anthropic's Claude via the Einstein Trust Layer) implements the core principles above directly: the Einstein Trust Layer enforces zero data retention, PII masking, prompt-injection defense, toxicity scoring, and geo-aware routing before any prompt leaves Salesforce's environment; zero-data-retention routes LLM calls through Salesforce infrastructure under contractual no-training commitments with per-region data residency; every action logs to the Einstein Activity Platform with full actor-chain capture via a customer-accessible audit API; and Agentforce achieved FedRAMP High authorization in 2025, unlocking federal and public-sector procurement — the trust layer is the primary enterprise sales differentiator enabling deployment into financial services, healthcare, and government contexts that would otherwise reject agentic AI.

ServiceNow holds FedRAMP High authorization for its platform, and Moveworks (its conversational/agentic front-door product) achieved FedRAMP Moderate authorization in February 2026 for federal agency and defense contractor deployment. The enabling architecture: zero-data-retention contracts with all underlying LLM providers, a complete immutable-storage audit log for federal customers, mandatory HITL gating for any workflow step touching access control changes, and geo-aware routing for data residency. This demonstrates the guardrail architecture in this guide isn't just best practice — it's the architectural prerequisite for operating agentic AI in the most security-sensitive environments.

## Compliance Overlay

The NIST AI RMF's Map/Measure/Manage/Govern functions map to architect action: map each threat class to a Manage-function control, and use the risk register as the Measure artifact. ISO 42001 AIMS (Clause 6.1 AI risk assessment, Clause 8.4 AI system operation, Annex A AI-specific controls) requires aligning guardrail telemetry to Annex A controls A.6.1-A.6.3 for AI risk treatment. ISO 27001 Annex A (especially A.8 Technology controls for the AI-extended threat surface) maps AI-BOM, dependency scanning, and registry controls to A.8.7, A.8.20, and A.8.22. The EU AI Act's GPAI provisions (transparency obligations and systemic risk assessment, in force since Aug 2, 2025) require model provider transparency documentation — GPAI obligations apply to model providers, not deployers, but deployers must still verify compliance. The EU AI Act's High-Risk provisions (risk management system, technical documentation, logging, human oversight, robustness — Annex III applying Dec 2, 2027) treat guardrail audit telemetry as the logging requirement and human approval gates as the oversight requirement. NIST IR 8596 (draft 2026, agentic-AI-specific guidance) should be followed as a compliance vocabulary for US federal agency engagements.

## Security Architecture Review Checklist

Cross-keyed to the [Agentic AI Security & Identity](../05-agentic-ai-security-identity.md) checklist (which covers identity):

- [ ] **G1** — Deterministic outer shell defined: input, output, and egress have deterministic rules before probabilistic classifiers
- [ ] **G2** — Probabilistic controls measured: FP/FN rates tracked as SLOs, never the sole control for an unacceptable outcome
- [ ] **G3** — All guardrails emit telemetry: fired/passed/latency metrics on every evaluation, no silent guardrails
- [ ] **G4** — Guardrails are individually toggleable: a feature flag per layer, disabling one without affecting others
- [ ] **G5** — Guardrails tested in CI: an adversarial fixture suite regression-tested on each PR
- [ ] **G6** — Threat model covers all 18 classes: the risk register maps each class to controls with no gaps
- [ ] **G7** — Egress is allowlisted, not blocked: default-deny with an explicit allowlist, not default-allow with a blocklist
- [ ] **G8** — Lethal-trifecta separation enforced: private data, untrusted content, and egress never co-resident in one agent context
- [ ] **G9** — Memory writes are gated and provenance-tagged: no agent writes without an ACL check and provenance label
- [ ] **G10** — HITL approval shows the raw action, not prose: the UI presents the actual tool call and diff, not an agent summary
- [ ] **G11** — AI-BOM maintained and scanned: model/SDK/MCP package versions tracked with CI dependency scanning
- [ ] **G12** — Sandbox provides microVM-level isolation: agent-executed code runs in gVisor/Firecracker or equivalent, no host mounts
- [ ] **G13** — Incident response tested: kill switches reachable under 1 minute, an emergency shutdown sequence documented and drilled
- [ ] **G14** — Red-team on quarterly cadence: human adversarial testing with findings tracked in the risk register
- [ ] **G15** — Compliance evidence auto-generated: audit telemetry maps to regulatory requirements without manual collection

## Related

- [Agentic AI Security Architecture & Guardrails (1 of 2)](../04-agentic-ai-security-guardrails.md)
- [Agentic AI Security & Identity](../05-agentic-ai-security-identity.md)
- [Agent Communication, Identity & AI Gateway](../03-agent-communication-identity-gateway.md)
