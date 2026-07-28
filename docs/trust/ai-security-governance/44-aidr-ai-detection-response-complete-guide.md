---
title: "AIDR: AI Detection and Response — Definition, Landscape & Ecosystem"
doc_type: guide
domain: trust
status: current
topic_id: aidr-ai-detection-response-complete-guide
last_reviewed: 2026-07-27
maturity: practitioner
supersedes: [docs/ai-security-governance/security/AIDR-AI-Detection-Response-Complete-Guide.md]
tags: [aidr, ai-security, agentic-ai, detection-response, mcp-security]
covers_version: "as of 2026"
---

The security category that secures the runtime behavior of autonomous AI agents: definition, category history, academic literature, and the commercial vendor landscape.

## Executive Summary

AIDR (AI Detection and Response) is the security discipline built to monitor, detect, and respond to threats that emerge when AI agents execute tasks autonomously inside enterprise systems. It extends the detection-and-response logic that EDR applied to endpoints — and that XDR extended across the network — to the AI layer, where agents act on behalf of identities, invoke tools, access memory, and coordinate with other agents at machine speed.

The category formally crystallized in September-December 2025, driven by CrowdStrike's acquisition of Pangea and launch of Falcon AIDR, and by Zenity's dedicated AIDR platform. Palo Alto Networks (Prisma AIRS 3.0) and Cisco followed at RSAC 2026. An academic production-validated framework (ADR, arXiv 2605.17380) deployed at Uber across 7,200+ hosts validated the approach at scale.

AIDR is not a general AI framework, workflow orchestrator, or agent runtime — it is a security control plane layered above an existing agentic architecture to make agent behavior observable, policy-enforceable, and incident-recoverable.

## Terminology and Definitions

**Primary definition (dominant, 2025-2026):** AIDR is a cybersecurity capability providing continuous visibility into AI agent behavior at runtime, with automated response when that behavior poses a risk. An "AIDR Platform" is the software product category combining agent telemetry, intent analysis, behavioral baselining, policy enforcement, and automated remediation. AISPM (AI Security Posture Management) is its pre-deployment complement — configuration auditing and supply-chain scanning — where AISPM reduces static risk and AIDR enforces at runtime.

**Historical definition (legacy, 2013-present, humanitarian domain):** AIDR also refers to "Artificial Intelligence for Disaster Response," an open-source platform from the Qatar Computing Research Institute for classifying social-media crisis messages using human-plus-ML hybrid approaches. **The two definitions are completely unrelated** — this guide covers exclusively the enterprise security meaning. The humanitarian AIDR predates the security AIDR by over a decade; they share only the acronym.

**Relationship to adjacent categories:** EDR monitors endpoints (processes, file writes, network); XDR correlates across endpoint, network, identity, cloud, and email; MDR is the managed-service delivery of EDR/XDR capabilities; AIDR observes AI agent decision paths, tool invocations, and execution flow; and AISPM covers the pre-deployment posture of AI models, agents, and configurations.

## Historical Timeline

| Date | Event |
|---|---|
| 2013 | QCRI releases "Artificial Intelligence for Disaster Response" — the original, humanitarian AIDR |
| 2022-2024 | Prompt injection and jailbreak attacks proliferate; enterprise AI adoption accelerates |
| Jan 2025 | OWASP publishes the LLM Top 10 2025; prompt injection remains LLM01 for a third consecutive year |
| Mid-2025 | Enterprises deploy autonomous agents at scale via MCP and LangGraph; the attack surface becomes measurable |
| Sep 2025 | CrowdStrike acquires Pangea (~$260M), launches its Agentic Security Platform, and coins "AIDR" as the next-gen security category |
| Dec 2025 | CrowdStrike Falcon AIDR goes GA; Zenity releases a dedicated AIDR platform; OWASP publishes the Agentic Top 10 (ASI01-ASI10) |
| May 2026 | arXiv 2605.17380 publishes the first large-scale, production-validated ADR framework (Uber, 7,200+ hosts) |
| Apr 2026 | RSAC 2026: CrowdStrike, Palo Alto Networks (Prisma AIRS 3.0), and Cisco all ship agentic SOC tools; AIDR becomes a mainstream category |
| Jun 2026 | Obsidian Security extends SaaS XDR capabilities to agentic systems; market consolidation begins |
| Jul 2026 | AIDR category broadly adopted; analysts project consolidation into major security platforms |

## Definition and Origin

**Is AIDR an official standard?** AIDR is not a formal standard defined by ISO, IEEE, IETF, or NIST as of mid-2026 — it is a vendor-coined category label introduced by CrowdStrike in September 2025 and since adopted by Zenity, Obsidian Security, and others. That said, NIST AI RMF 1.0 and the forthcoming AI 600-2 implicitly require the capabilities AIDR provides (GOVERN/MEASURE/MANAGE functions); the OWASP Agentic Top 10 provides the threat taxonomy that AIDR platforms operationalize; and EU AI Act Articles 9 and 17 mandate risk management systems and post-market monitoring for high-risk AI systems — functions AIDR fulfills. There is no RFC, ISO standard, or IETF draft specifically for AIDR as a category; the academic community uses "ADR" (Agentic Detection and Response) interchangeably.

**Who introduced it?** CrowdStrike crystallized the term "AIDR" in September 2025 following the Pangea acquisition. Zenity had been building the underlying capability (agent runtime security) independently and adopted the category label once it emerged.

**Is it open source?** The category spans both commercial and open approaches: commercial platforms include CrowdStrike Falcon AIDR, Zenity Defend, and Palo Alto Prisma AIRS (all proprietary); ADR-Bench (Uber, arXiv 2605.17380) is an open benchmark dataset for the research community; and supporting open standards — OpenTelemetry GenAI semantic conventions, the OWASP threat taxonomy — are used within most AIDR implementations regardless of vendor.

## Literature Survey

**ADR: An Agentic Detection System for Enterprise Agentic AI Security** (arXiv 2605.17380, May 2026, Uber Research) is the first production-validated enterprise framework for securing MCP-based AI agents. Its three-component architecture — an ADR Sensor for telemetry, an ADR Explorer for red-teaming, and an ADR Detector using two-tier detection — combines high-fidelity agent telemetry capture, systematic adversarial testing, and fast-triage plus context-aware LLM reasoning. In production it achieved 97.2% precision for credential detection across 7,200+ hosts and 10,000+ daily agent sessions; on ADR-Bench (302 tasks, 17 techniques) it reached 67% attack detection with zero false positives; on AgentDojo (93 tasks) it reached 100% attack detection with 3 false alarms. Its strength is production validation at scale with an open benchmark; its limitation is that it's MCP-specific, with limited evaluation of non-tool-calling agent architectures.

**AgentSOC: A Multi-Layer Agentic AI Framework for Security Operations Automation** (arXiv 2604.20134, April 2026) targets multi-agent SOC automation for threat detection and response, using an orchestrator plus specialist agents for triage, investigation, and remediation, built on LangGraph orchestration and MITRE ATT&CK-aligned threat modeling.

**Perspectives on a Reliability Monitoring Framework for Agentic AI Systems** (arXiv 2511.09178, November 2025) addresses reliability and behavioral monitoring for autonomous AI systems, and establishes the behavioral-baseline methodology used across AIDR platforms.

**Threat research sources** feeding these frameworks include the OWASP Agentic Top 10 (ASI01-ASI10 threat taxonomy), the OWASP LLM Top 10 (where prompt injection remains the top threat), MITRE ATLAS (an AI-specific adversarial TTP matrix), MCP-SandboxScan (arXiv 2601.01241, WASM-based secure MCP tool execution), and MCP Pitfall Lab (arXiv 2604.21477, multi-vector attacks on MCP tool servers). Research clusters into seven categories: agent runtime security, prompt injection defense, multi-agent security, identity and Zero Trust, MCP security, AI SOC, and governance/compliance — each anchored by the papers and standards above.

## Vendor Landscape

**CrowdStrike — Falcon AIDR** reached GA in December 2025 following the Pangea acquisition. It's a unified platform covering data, models, agents, identities, infrastructure, and prompt interactions, claiming 99% detection efficacy for prompt attacks at 30ms or less latency, tracking 180+ prompt injection techniques, providing shadow AI discovery across SaaS and cloud, and integrating Microsoft Defender telemetry into Falcon's next-gen SIEM.

**Zenity — Zenity Defend (AIDR)** is a specialist vendor that coined its own AIDR definition independently, built on three-layer runtime monitoring (execution monitoring, intent analysis, runtime response). It provides full execution graph mapping across decision chains, tool invocations, and control flow; intent-aware threat detection including indirect injection via RAG documents; build-time to runtime correlation; coverage of six threat vectors (prompt injection, data exfiltration, privilege escalation, multi-agent attacks, memory poisoning, tool misuse); and real-time PII/PHI/financial data classification.

**Palo Alto Networks — Prisma AIRS 3.0** extends the existing Prisma platform to agent workloads, providing agent discovery, action auditing, and governance enforcement, with 2026 additions including Unit 42 Frontier AI Defense services and AI-agent runtime protection announced at RSAC 2026.

**Expanding vendors:** Cisco announced AI-agent runtime protection at RSAC 2026 with limited public detail; Obsidian Security extends its SaaS XDR to agentic systems, focused on SaaS agent behavior; Microsoft's Security Copilot plus Sentinel provides indirect AIDR via an AI-augmented SOC without explicit AIDR branding; AWS's GuardDuty plus Bedrock security controls and Google's Vertex AI security plus Security Command Center are platform-native but not branded as AIDR; and IBM's QRadar AI plus watsonx security is an AI-augmented SIEM rather than a dedicated AIDR product.

**Vendor evaluation matrix** (1-5 scale):

| Criterion | CrowdStrike | Zenity | Palo Alto |
|---|---|---|---|
| Agent telemetry depth | 5 | 5 | 4 |
| Prompt injection detection | 5 | 5 | 4 |
| MCP-aware detection | 4 | 5 | 3 |
| Enterprise integration | 5 | 3 | 5 |
| Shadow AI discovery | 5 | 4 | 5 |
| Open telemetry support | 3 | 4 | 3 |
| Time to value | 3 | 4 | 3 |

## Related

- [AIDR: Architecture & Threat Model (Part 2)](parts/44-aidr-ai-detection-response-complete-guide-part2.md) — the open-source ecosystem, three-layer architecture, and the OWASP Agentic Top 10 threat mapping
- [AI TRiSM Complete Guide](43-ai-trism-complete-guide.md)
- [AISPM: AI Security Posture Management](45-aispm-ai-security-posture-management.md)
