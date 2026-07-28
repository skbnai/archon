---
title: "NIST AI Standards — Cross-Framework Control Mappings"
doc_type: guide
domain: trust
status: current
topic_id: part-05-control-mappings
last_reviewed: 2026-07-28
maturity: practitioner
supersedes: [docs/nist-ai-standards/part-05-control-mappings.md]
tags: [control-mapping, nist-csf, iso-42001, owasp-llm, eu-ai-act, mitre-atlas]
covers_version: "as of 2026"
---

**Audience:** CISO, compliance team, security architect.

## NIST AI 100-2 to NIST CSF 2.0

| AI 100-2 Attack | AI 100-2 Mitigation | NIST CSF 2.0 Function | CSF Subcategory |
|----------------|--------------------|-----------------------|-----------------|
| Data Poisoning | Training data provenance | PROTECT | PR.DS-10 (data integrity) |
| Data Poisoning | Anomaly detection on training data | DETECT | DE.CM-01 (monitoring) |
| Backdoor Attack | Behavioral baseline testing | DETECT | DE.CM-09 (AI testing) |
| Backdoor Attack | Model supply chain verification | PROTECT | PR.PS-04 (platform security) |
| Evasion Attack | Adversarial training | PROTECT | PR.IR-01 (incident resilience) |
| Evasion Attack | Input preprocessing | PROTECT | PR.DS-10 |
| Model Extraction | Rate limiting | PROTECT | PR.AA-05 (least privilege) |
| Model Extraction | Output perturbation | PROTECT | PR.DS-02 (data in transit) |
| Membership Inference | Differential privacy | PROTECT | PR.DS-01 (data at rest) |
| Prompt Injection | Input sanitization | PROTECT | PR.DS-10 |
| Prompt Injection | Output monitoring | DETECT | DE.AE-06 (AI adversarial activity) |

## NIST AI 100-4 to NIST CSF 2.0

| AI 100-4 Risk | AI 100-4 Control | NIST CSF 2.0 | CSF Subcategory |
|--------------|-----------------|--------------|-----------------|
| Deepfake fraud | Multi-factor verification | PROTECT | PR.AA-02 (authentication) |
| Deepfake fraud | C2PA provenance | IDENTIFY | ID.AM-03 (data flows) |
| Synthetic phishing at scale | AI email detection | DETECT | DE.CM-01 |
| Disinformation | Content provenance tracking | GOVERN | GV.OC-03 (legal requirements) |
| Synthetic training data | Data provenance | PROTECT | PR.DS-01 |

## CAISI to NIST CSF 2.0

| CAISI Risk | CAISI Control | NIST CSF 2.0 | CSF Subcategory |
|-----------|--------------|--------------|-----------------|
| Agent impersonation | Cryptographic agent identity | PROTECT | PR.AA-01 (identity management) |
| Tool abuse | Least-privilege tool sets | PROTECT | PR.AA-05 |
| Memory poisoning | Memory integrity signatures | PROTECT | PR.DS-10 |
| Orchestrator compromise | Authorization chains | PROTECT | PR.AA-03 (authorization) |
| Agent behavior drift | Behavioral monitoring | DETECT | DE.AE-06 |

## OWASP LLM Top 10 to NIST AI 100-2

| OWASP LLM Risk | OWASP ID | NIST AI 100-2 Section | Shared Mitigations |
|---------------|----------|----------------------|-------------------|
| Prompt Injection | LLM01 | §2.5, §5.2 | Input sanitization, privilege separation |
| Insecure Output Handling | LLM02 | §5.4 | Output validation, schema enforcement |
| Training Data Poisoning | LLM03 | §3.1-3.2 | Data provenance, anomaly detection |
| Model Denial of Service | LLM04 | §4.3 (availability) | Rate limiting, circuit breakers |
| Supply Chain Vulns | LLM05 | §3.3-3.4 | Model SBOM, hash verification |
| Sensitive Info Disclosure | LLM06 | §4.4 (membership inference) | Differential privacy, output filtering |
| Insecure Plugin Design | LLM07 | §5.3 (tool abuse) | Least privilege, OPA |
| Excessive Agency | LLM08 | CAISI §3 | Permission scoping, human approval |
| Overreliance | LLM09 | AI 100-2 §6 (calibration) | Confidence calibration, explainability |
| Model Theft | LLM10 | §4.1 (extraction) | Rate limiting, watermarking |

## MITRE ATLAS to NIST AI 100-2

| ATLAS Technique | ATLAS ID | AI 100-2 Attack Category | Mitigation Cross-Reference |
|----------------|----------|--------------------------|--------------------------|
| Backdoor ML Model | AML.T0018 | Poisoning — backdoor | Behavioral baseline, Neural Cleanse |
| Publish Poisoned Datasets | AML.T0019 | Poisoning — data | Data provenance, curated sources |
| Poison Training Data | AML.T0020 | Poisoning — data | Access controls, anomaly detection |
| Evade ML Model | AML.T0031 | Evasion | Adversarial training, ensemble |
| Model Inference API Access | AML.T0040 | Extraction (probing) | Rate limiting, output perturbation |
| Craft Adversarial Data | AML.T0043 | Evasion | Input preprocessing |
| LLM Prompt Injection | AML.T0057 | Prompt injection | Input sanitization |
| LLM Jailbreak | AML.T0058 | Jailbreak | Constitutional AI, monitoring |

## EU AI Act to NIST AI 100-2 / 100-4 / CAISI

| EU AI Act Article | Requirement | Relevant Standard | Control Implementation |
|------------------|-------------|------------------|----------------------|
| Art. 9 — Risk Management | Risk management system for AI | NIST AI RMF (GOVERN) | Quarterly AI risk review, AI Risk Register |
| Art. 10 — Data Governance | Training data quality and governance | AI 100-2 §3 (Poisoning mitigations) | Training data provenance, bias testing |
| Art. 11 — Technical Documentation | Model cards and architecture docs | AI 100-2 §6 (Model cards) | Model card for all production AI |
| Art. 12 — Record Keeping | Automatic logging of AI operations | CAISI (Audit trail) | Immutable audit trail, Langfuse tracing |
| Art. 13 — Transparency | Users informed of AI use | AI 100-4 §4 (Watermarking, C2PA) | AI content labeling, C2PA provenance |
| Art. 14 — Human Oversight | Human intervention capability | CAISI (Kill switch) | Per-agent kill switch, approval gates |
| Art. 15 — Accuracy, Robustness | Performance and security testing | AI 100-2 §4, §6 | Adversarial testing, drift detection |

## ISO/IEC 42001 to NIST AI Standards

| ISO 42001 Clause | Requirement | NIST Standard | Implementation |
|----------------|-------------|---------------|----------------|
| 4.2 — AI System Context | Understand AI trustworthiness properties | AI 100-1 (7 properties) | Trustworthiness assessment per property |
| 6.1.2 — AI Risk Assessment | Identify AI-specific risks | AI 100-2 (attack taxonomy) | Use AI 100-2 taxonomy for risk register |
| 8.4 — AI Impact Assessment | Pre-deployment impact analysis | CAISI (agent risk assessment) | Structured impact assessment template |
| 9.1 — Monitoring | Track AI performance over time | AI 100-2 (drift detection) | Automated monitoring pipeline |
| A.2.2 — Impact Assessment | Assess before deployment | AI 100-2, CAISI | Combined adversarial + agency risk assessment |
| A.5.1 — Transparency | Explain AI decisions | AI 100-4 (provenance) | Decision explanation + C2PA for content |
| A.5.3 — Human Oversight | Human control mechanisms | CAISI (human authority) | Kill switches, approval gates |
| A.7.4 — Robustness Testing | Security testing of AI | AI 100-2 (adversarial testing) | Monthly adversarial evaluation |

## Consolidated Control Library

Ten controls anchor the mapping, each cross-referenced to its supporting standards, implementation, test, and owner:

```python
NIST_AI_CONTROL_LIBRARY = {
    "AI-C-001": {"name": "Training Data Provenance",
        "description": "Cryptographically sign all training data; track source and lineage",
        "standards": ["AI-100-2 §3.1", "ISO-42001 A.3.3", "NIST-CSF PR.DS-10"],
        "implementation": "Git-versioned data pipeline with SHA-256 hash of each dataset",
        "test": "Monthly: verify hash of training datasets against manifest",
        "owner": "AI/ML Engineering"},
    "AI-C-002": {"name": "Adversarial Input Testing",
        "description": "Monthly red team exercises using ATLAS techniques against production AI",
        "standards": ["AI-100-2 §6.2", "MITRE-ATLAS", "EU-AI-Act Art.15"],
        "implementation": "Automated adversarial test suite (FGSM, PGD, prompt injection)",
        "test": "Pass rate: >90% of adversarial inputs detected or handled correctly",
        "owner": "Red Team / AI Security"},
    "AI-C-003": {"name": "Agent Least Privilege",
        "description": "Each AI agent has minimum necessary tool permissions for its role",
        "standards": ["CAISI §3", "OWASP-LLM08", "NIST-CSF PR.AA-05"],
        "implementation": "OPA policy engine; task-scoped JIT permissions",
        "test": "Quarterly: verify no agent has permissions beyond role definition",
        "owner": "Platform Engineering / IAM"},
    "AI-C-004": {"name": "Content Provenance (C2PA)",
        "description": "All AI-generated enterprise content signed with C2PA manifest",
        "standards": ["AI-100-4 §4", "EU-AI-Act Art.13"],
        "implementation": "C2PA signing pipeline for AI content before distribution",
        "test": "Monthly: verify C2PA signing rate for published AI content",
        "owner": "Communications / Content Team"},
    "AI-C-005": {"name": "Model Behavior Monitoring",
        "description": "Continuous monitoring of AI model accuracy and behavioral drift",
        "standards": ["AI-100-2 §6.5", "ISO-42001 9.1", "NIST-CSF DE.CM-09"],
        "implementation": "Langfuse + Grafana dashboard; weekly accuracy evaluation",
        "test": "Automated: alert if accuracy drops >5% from baseline",
        "owner": "MLOps / AI Operations"},
    "AI-C-006": {"name": "Prompt Injection Defense",
        "description": "Input sanitization, instruction hierarchy, output monitoring for injections",
        "standards": ["AI-100-2 §5.2", "OWASP-LLM01", "CAISI §2"],
        "implementation": "PromptInjectionDefense class; data boundary tags; anomaly detection",
        "test": "Monthly: 20 injection test cases; pass rate >95%",
        "owner": "AI Security / Application Security"},
    "AI-C-007": {"name": "Synthetic Content Detection",
        "description": "AI text, image, and deepfake detection in enterprise communication channels",
        "standards": ["AI-100-4 §3", "NIST-CSF DE.CM-01"],
        "implementation": "Ensemble detectors in email gateway; video call deepfake alert",
        "test": "Quarterly: benchmark against new generation models",
        "owner": "SOC / Email Security"},
    "AI-C-008": {"name": "Inter-Agent Authentication",
        "description": "Cryptographic authentication for all agent-to-agent communication",
        "standards": ["CAISI §4", "NIST-CSF PR.AA-02"],
        "implementation": "mTLS + signed JWT; no implicit trust on claimed identity",
        "test": "Annual: penetration test simulating agent impersonation",
        "owner": "Platform Engineering"},
    "AI-C-009": {"name": "AI Human Override",
        "description": "Human can override, pause, or terminate any AI agent at any time",
        "standards": ["CAISI §5", "EU-AI-Act Art.14", "ISO-42001 A.5.3"],
        "implementation": "Per-agent kill switch; approval gates for high-risk actions",
        "test": "Quarterly: test kill switch activation and recovery",
        "owner": "SOC Manager / CISO"},
    "AI-C-010": {"name": "AI Audit Trail",
        "description": "Immutable, cryptographically signed record of all AI actions",
        "standards": ["CAISI §4", "EU-AI-Act Art.12", "NIST-CSF PR.DS-10"],
        "implementation": "WORM storage for AI action logs; HMAC signing per entry",
        "test": "Monthly: integrity check on audit trail; attempt tamper detection",
        "owner": "Platform Engineering / Compliance"},
}
```

## Gap Analysis Template

```python
def perform_ai_controls_gap_analysis(organization, current_controls, applicable_standards) -> dict:
    """Identify gaps between current controls and required controls."""
    standard_control_map = {
        "nist_csf_2_0": ["AI-C-001", "AI-C-002", "AI-C-005", "AI-C-009", "AI-C-010"],
        "eu_ai_act_high_risk": list(NIST_AI_CONTROL_LIBRARY.keys()),  # All controls
        "iso_42001": ["AI-C-001", "AI-C-002", "AI-C-004", "AI-C-005", "AI-C-009"],
        "owasp_llm_top10": ["AI-C-003", "AI-C-006", "AI-C-007"],
        "caisi_agentic": ["AI-C-003", "AI-C-006", "AI-C-008", "AI-C-009", "AI-C-010"],
    }
    required_controls = set()
    for standard in applicable_standards:
        required_controls.update(standard_control_map.get(standard, []))

    implemented = set(current_controls)
    gaps = required_controls - implemented

    gap_details = []
    for control_id in gaps:
        control = NIST_AI_CONTROL_LIBRARY.get(control_id, {})
        gap_details.append({
            "control_id": control_id,
            "name": control.get("name"),
            "standards_requiring": [s for s in applicable_standards
                                   if control_id in standard_control_map.get(s, [])],
            "owner": control.get("owner"),
            "implementation": control.get("implementation"),
        })

    return {
        "organization": organization,
        "applicable_standards": applicable_standards,
        "required_controls": len(required_controls),
        "implemented_controls": len(implemented & required_controls),
        "gaps_count": len(gaps),
        "coverage_pct": (len(implemented & required_controls) / len(required_controls)) * 100,
        "gaps": sorted(gap_details, key=lambda x: len(x["standards_requiring"]), reverse=True),
    }
```

## Related

- [NIST AI Standards Part 1: NIST AI 100-2 Adversarial ML](01-part-01-nist-ai-100-2-adversarial-ml.md)
- [NIST AI Standards Part 6: Implementation Checklist](06-part-06-implementation-checklist.md)
- [NIST AI Standards Part 3: CAISI Agentic AI Security](03-part-03-caisi-agentic-ai.md)
