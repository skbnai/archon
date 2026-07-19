---
title: "Part 12 — Responsible AI"
doc_type: guide
domain: strategy
topic_id: part-12-responsible-ai
status: current
canonical: true
last_reviewed: 2026-07-19
covers_version: "as of 2026-07-14"
maturity: practitioner
personas: ["architect", "governance-lead", "ethics-officer"]
supersedes: ["docs/enterprise-ai-report/part-12-responsible-ai.md"]
tags: ["responsible-ai", "fairness", "transparency", "explainability", "bias", "privacy", "safety", "eu-ai-act", "nist-ai-rmf", "iso-42001", "owasp-llm"]
sources: []
---

# Part 12 — Responsible AI

Responsible AI integrates fairness, transparency, privacy, safety, and human oversight into every AI system. This page maps the responsible AI framework and regulatory standards.

## Responsible AI Dimensions

Responsible AI spans eight key dimensions:

- **Fairness:** Bias detection, fairness metrics, demographic parity testing
- **Transparency:** Model cards, decision logging, disclosure of AI use
- **Explainability:** Chain-of-thought for LLMs, citation attribution in RAG
- **Privacy:** PII detection/redaction, data minimisation, right to erasure
- **Security:** Threat modeling, adversarial testing (see Part 13)
- **Grounding:** RAG for factual grounding, citation, hallucination measurement
- **Safety:** Content moderation, harmful content filtering, constitutional constraints
- **Human Oversight:** HITL/HOTL/HOOL patterns, human recourse, override capability

## Regulatory Standards

### EU AI Act (2024–2026)

The EU AI Act introduces a risk-based regulatory framework for AI systems. All enterprises operating in the EU or offering AI-powered products/services to EU residents must comply.

| Risk Level | Definition | Requirements |
|-----------|------------|---------|
| **Unacceptable Risk** | Banned systems (social scoring, real-time biometric surveillance) | Prohibited — cannot deploy |
| **High Risk** | Credit scoring, recruitment AI, medical diagnostic AI, critical infrastructure | Conformity assessment, registration, documentation, human oversight |
| **Limited Risk** | Chatbots, deepfakes | Disclose AI use to users |
| **Minimal Risk** | Spam filters, AI games | Voluntary code of practice |

**Key compliance requirements for High Risk AI:**
- Risk management system documented
- Data governance (training data quality, bias mitigation)
- Technical documentation (model card equivalent)
- Logging and traceability
- Transparency for users
- Human oversight mechanism
- Accuracy and robustness standards
- Post-market monitoring

### NIST AI RMF (Risk Management Framework)

The US National Institute of Standards and Technology AI Risk Management Framework provides a structured approach to identifying, assessing, and managing AI risks. It is technology-agnostic and voluntary.

**Four core functions:**
1. **Govern** — Establish AI risk governance structures, policies, and culture
2. **Map** — Identify AI risks in context (technical, operational, societal)
3. **Measure** — Analyse and assess risk impact and likelihood
4. **Manage** — Prioritise and implement risk treatments; monitor effectiveness

### ISO 42001 (AI Management Systems)

The first international standard for AI management systems — analogous to ISO 27001 for information security. Provides a framework for organisations to demonstrate responsible AI governance.

**Key clauses cover:** Organisational context, AI policy, planning objectives, impact assessment, system lifecycle management, performance evaluation, monitoring, and audit.

### ISO 23894 (AI Risk Management)

Provides guidance on AI risk management, complementing NIST AI RMF and aligned with ISO 31000 enterprise risk management.

### OWASP LLM Top 10

The OWASP Top 10 for LLM Applications identifies the most critical security risks for GenAI systems: prompt injection, insecure output handling, training data poisoning, model denial of service, supply chain vulnerabilities, sensitive information disclosure, insecure plugin/tool design, excessive agency, overreliance, and model theft.

### MITRE ATLAS

ATLAS (Adversarial Threat Landscape for Artificial-Intelligence Systems) is the AI equivalent of MITRE ATT&CK. It documents adversarial techniques, tactics, and case studies specifically for AI/ML systems.

Key ATLAS tactics: Reconnaissance, Resource Development, Initial Access, ML Attack Staging, Exfiltration, Impact.

## Implementation Playbook

### Step 1: RAI Governance Structure

Appoint a Responsible AI Officer. Form a cross-functional Responsible AI Council. Define the enterprise AI ethics principles (typically 6–8 principles covering the dimensions above).

### Step 2: Risk Classification

Classify every AI use case against EU AI Act risk levels and internal risk criteria. High-risk AI requires full conformity assessment.

### Step 3: Bias & Fairness Assessment

For every AI system affecting people:
- Identify protected characteristics (age, gender, race, disability, etc.)
- Measure outcome disparities across groups
- Apply fairness metrics: demographic parity, equalised odds, individual fairness
- Document findings in the model card / AI system card

### Step 4: Transparency & Explainability

- Publish AI disclosure to users (EU AI Act transparency obligation for limited risk)
- Implement chain-of-thought or citation-based explainability for consequential decisions
- Maintain decision logs for regulatory audit purposes
- Enable human recourse mechanism (users can challenge AI decisions)

### Step 5: Human Oversight Implementation

Design AI systems with appropriate human oversight:
- **HITL** (Human-in-the-Loop): human must approve before action
- **HOTL** (Human-on-the-Loop): human monitors; can override in real-time
- **HOOL** (Human-out-of-the-Loop): fully autonomous; human reviews retrospectively

Choose oversight level based on risk class (High Risk requires HITL).

### Step 6: Continuous Monitoring & Improvement

- Monitor for bias drift (fairness metrics can degrade as data distributions shift)
- Track hallucination rates and grounding quality
- Run quarterly RAI reviews; annual external RAI audits
- Incorporate RAI findings into continuous improvement cycle

## RAI Metrics Dashboard

| Metric | Target | Alert Threshold |
|--------|--------|-----------------|
| Hallucination rate (RAG systems) | &lt;1% | >2% |
| PII leakage incidents | 0 | Any occurrence |
| Bias delta (max outcome gap across groups) | &lt;5% | >10% |
| HITL escalation rate | Appropriate per use case | >30% |
| User challenge / recourse rate | &lt;1% | >3% |
| High-risk AI use cases with current conformity assessment | 100% | &lt;100% |
| RAI incident rate | 0 high severity | Any high severity |

## Authoritative Guides

Comprehensive RAI guidance is available in the **AI Security Governance** and **Sovereign Constitutional AI** domains. Consult specialised guides for:

- Responsible AI implementation and governance models
- Fairness, transparency, and explainability techniques
- Constitutional AI engineering for safety
- OWASP LLM Top 10 mitigation strategies
- MITRE ATLAS adversarial testing
- Model cards and system cards guidance

## Related

- [Part 6 — Governance](16-part-06-governance.md) — Responsible AI governance roles and operating model
- [Part 8 — Organizational Roles](18-part-08-organizational-roles.md) — RAI Officer, AI Auditor, AI Risk Officer roles
- [Part 9 — Operating Processes](19-part-09-operating-processes.md) — Red teaming, hallucination handling processes
- [Part 13 — Security Model](23-part-13-security-model.md) — Security controls (OWASP LLM Top 10, MITRE ATLAS)

## Sources

[No external sources for this page.]
