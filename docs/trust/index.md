---
title: "Trust Hub"
doc_type: hub
domain: trust
status: current
canonical: true
topic_id: hub-trust
maturity: foundational
personas: [architect, security]
last_reviewed: 2026-07-27
covers_version: "as of 2026-07-27"
supersedes: []
sources: []
tags: [hub, trust]
---
import SectionProgress from '@site/src/components/SectionProgress';

Deploying an agent without a threat model means deploying a system nobody
has actually tested against failure. This hub covers the controls that make
agentic AI trustworthy in production: threat modeling, identity and
guardrails, governance frameworks, and the compliance and SOC processes that
operate them continuously.

<SectionProgress domain="trust" />

## Scope

- **AI Control & security architecture** — DeepMind-style control roadmaps, runtime security, identity for AI agents, tool/memory/reasoning governance, multi-agent security, AI observability
- **Policy & authorization** — policy-as-code (OPA, Cedar), agent/tool/MCP authorization, RAG/memory/data authorization, cloud federation patterns
- **AI security field guides** — foundations and reference architecture, identity/MCP/A2A security blueprints, red teaming, AI-BOM, model/system cards, AI-TRiSM, AISPM, AIDR
- **Enterprise cyber security architecture** — the 15-part evolution/domains/identity/cloud/governance/investment/patterns handbook for CISOs and enterprise security architects
- **AI SOC operations** — SOC operating model and maturity, agentic SOC architecture, automation playbooks, SOAR platforms, observability, FinOps, implementation roadmap
- **NIST AI standards & CAISI** — adversarial ML (AI 100-2), synthetic content (AI 100-4), agentic AI security, control mappings, implementation checklists
- **Sovereign & Constitutional AI** — sovereign AI foundations, constitutional AI engineering, RAI operating model, AI alignment/control, AI risk taxonomy, AI safety framework, assurance/audit architecture, constitutional agent architecture, policy-as-code, democratic AI, roadmap & maturity
- Standalone guides: A2A security & governance, agent communication identity gateway, agentic AI security guardrails/identity, air-gapped/sovereign infrastructure

## AI Security Is a Three-Layer Problem

1. **Identity & Credentials** — Who is this agent? Who authorized it? What can it access? (SPIFFE/SPIRE, IETF AIMS, Entra Agent ID, OAuth 2.1/PKCE)
2. **Behavioral & Architectural** — Can a compromised agent cause unacceptable harm? (Guardrail pipelines, egress control, blast-radius isolation, HITL gates)
3. **Governance & Compliance** — Are AI systems auditable, accountable, and regulation-compliant? (NIST AI RMF, EU AI Act, ISO 42001, RAI frameworks, AI SOC)

## Regulatory Framework Map (2026)

| Framework | Type | Key dates | Obligations |
|---|---|---|---|
| **EU AI Act** | Mandatory law (EU) | Art. 50 + GPAI enforcement: Aug 2, 2026; Annex III high-risk: Dec 2, 2027 | Risk classification, GPAI docs, transparency, human oversight |
| **NIST AI RMF 1.0** | Voluntary (US) | Current; AI 600-1 (Jul 2024); CAISI agent standards (Feb 2026) | GOVERN / MAP / MEASURE / MANAGE |
| **ISO/IEC 42001:2023** | Certifiable standard | ISO 42006:2025 published; 350+ orgs certified (Apr 2026) | AI management system, 38 controls |
| **OWASP Agentic Top 10** | Industry | 2026, 100+ contributors | ASI01–ASI10 threat taxonomy |
| **DORA (EU Financial)** | Mandatory law (EU) | In force January 2025 | ICT risk management extends to AI systems |

## Related

- [Protocols Hub](../protocols/index.md) — the identity/auth model these controls sit on top of.
- [Operations Hub](../operations/index.md) — where the AI SOC meets observability.
