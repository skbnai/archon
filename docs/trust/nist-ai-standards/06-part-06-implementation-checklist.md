---
title: "NIST AI Standards — Implementation Checklist"
doc_type: guide
domain: trust
status: current
topic_id: part-06-implementation-checklist
last_reviewed: 2026-07-28
maturity: practitioner
supersedes: [docs/nist-ai-standards/part-06-implementation-checklist.md]
tags: [checklist, implementation, banking, healthcare, government, regulated-industry]
covers_version: "as of 2026"
---

**Audience:** CISO, compliance team, security architect, project manager.

## Universal Baseline Checklist

Applicable to all organizations deploying AI systems, regardless of sector, across three phases.

**Phase 1, Foundations (Days 1-30):**

```
GOVERNANCE AND POLICY:
  □ Designate an AI Risk Owner (typically CISO or AI Ethics Officer)
  □ Draft and approve AI Acceptable Use Policy
  □ Create AI Risk Register using NIST AI 100-2 attack taxonomy
  □ Define AI risk appetite (what automation levels are acceptable?)
  □ Establish AI governance committee (CISO, Legal, CTO, Business)

INVENTORY AND CLASSIFICATION:
  □ Inventory all AI systems currently deployed
  □ Classify each AI system by risk level (EU AI Act model)
  □ Document intended use and out-of-scope use for each system
  □ Map data flows: what data enters and exits each AI system
  □ Identify all third-party AI components (APIs, models, libraries)

IMMEDIATE SECURITY CONTROLS:
  □ Enable logging for all LLM API calls (inputs, outputs, tokens)
  □ Implement rate limiting on all AI API endpoints
  □ Add PII redaction before any data is sent to external LLM APIs
  □ Require API key rotation schedule (90-day maximum)
  □ Document which AI models have access to production data
```

**Phase 2, Core Controls (Days 30-90):**

```
NIST AI 100-2 CONTROLS:
  □ Training data: document provenance for all training datasets
  □ Training data: verify no PII in training data (scan with regex/ML)
  □ Model testing: run adversarial test suite before deploying new models
  □ Prompt injection: implement input sanitization for all user-facing AI
  □ Output validation: schema enforcement or content filtering on AI outputs
  □ Rate limiting: implemented on all AI inference endpoints
  □ Model registry: all deployed models registered with version and hash

NIST AI 100-4 CONTROLS:
  □ Synthetic content policy: define when AI content must be labeled
  □ AI content labeling: implement for all AI-generated external communications
  □ Deepfake response plan: procedure for suspected deepfake incident
  □ BEC training: educate executives and finance on voice/video deepfake risk

CAISI AGENTIC AI CONTROLS (if using agentic AI):
  □ Agent identity: each agent has unique identity (managed identity or certificate)
  □ Agent permissions: document tool permissions per agent type
  □ Human approval: mandatory human approval for high-risk agentic actions
  □ Kill switch: tested emergency stop for all AI agents
  □ Audit trail: all agent actions logged with tamper protection
```

**Phase 3, Maturity (Days 90-180):**

```
ADVANCED CONTROLS:
  □ Adversarial training: fine-tuned models trained with adversarial examples
  □ Model behavior monitoring: automated drift detection operational
  □ C2PA implementation: content provenance signing for AI-generated content
  □ Inter-agent authentication: mTLS or signed messages between agents
  □ Memory integrity: cryptographic integrity protection for agent memory
  □ Red team exercise: AI-specific red team conducted against production systems

COMPLIANCE AND AUDIT:
  □ NIST AI RMF: GOVERN-MAP-MEASURE-MANAGE cycle documented and followed
  □ ISO 42001: AI management system documentation complete
  □ EU AI Act (if applicable): high-risk AI system documentation and registration
  □ Evidence package: all controls evidenced for audit
  □ Quarterly review: governance committee review of AI risk register
```

## Banking and Financial Services Checklist

Additional controls for regulated financial institutions (DORA, PCI-DSS, SOX, BSA/AML):

```
AI GOVERNANCE (FINANCIAL):
  □ AI Model Risk Management (MRM) policy per OCC 2011-12 / SR 11-7
    - Pre-deployment validation of all AI models
    - Ongoing monitoring with defined performance thresholds
    - Annual model inventory review
    - Independent validation for high-risk models
  □ DORA compliance: AI systems included in ICT risk management framework
  □ DORA: AI model providers (Anthropic, OpenAI) assessed as critical ICT third parties
  □ AI in AML/BSA: document AI model role in suspicious activity detection
  □ Fair lending: AI credit decisions tested for disparate impact

SYNTHETIC CONTENT (FINANCIAL):
  □ BEC deepfake protocol: out-of-band verification for wire transfer authorization
    - Video call is NOT sufficient for authorization
    - Require callback to known phone number + dual approval
  □ Voice biometric: liveness detection for phone banking AI authentication
  □ Document verification: AI-assisted KYC must include deepfake detection
  □ C2PA: implement for all official communications (investor relations, filings)

FRAUD DETECTION AI:
  □ Model evasion testing: quarterly adversarial testing against fraud AI
  □ Explainability: fraud model decisions must be explainable for regulatory inquiry
  □ Fairness testing: fraud models tested for demographic disparate impact quarterly
  □ Model poisoning defense: fraud feedback loops monitored for systematic bias injection

AI SOC (FINANCIAL):
  □ SOC AI classified as critical ICT function under DORA
  □ Fallback procedures documented for AI SOC unavailability
  □ AI-assisted incident reporting: DORA Article 17 reporting templates
  □ Major incident definition includes AI-caused security failures
  □ Concentration risk: AI provider dependency assessed; contingency plan if provider unavailable
```

## Healthcare Checklist

Additional controls for HIPAA, FDA AI/ML, EU MDR:

```
AI GOVERNANCE (HEALTHCARE):
  □ PHI protection: AI systems processing PHI must have BAA with all AI vendors
  □ Minimum necessary: AI prompts contain minimum PHI required
  □ De-identification: PHI de-identified before AI training (HIPAA Safe Harbor or Expert)
  □ AI in clinical decisions: FDA SaMD classification for clinical AI (if applicable)
  □ Bias testing: clinical AI tested on diverse patient populations

SYNTHETIC CONTENT (HEALTHCARE):
  □ Synthetic medical images: detection pipeline for AI-generated radiology images
  □ Medical deepfake: provider authentication not solely relying on video
  □ EHR integrity: AI-generated clinical notes labeled as AI-assisted
  □ Research data: AI-generated synthetic datasets labeled; not mixed with real patient data

AI-SPECIFIC HIPAA CONTROLS:
  □ Access controls: AI agents subject to same HIPAA access controls as humans
  □ Audit controls: AI access to PHI logged (same as human access logs)
  □ Person authentication: multi-factor for human-AI collaborative decision systems
  □ Transmission security: PHI never in plain-text to AI APIs; always encrypted in transit

PATIENT SAFETY:
  □ Clinical AI: human-in-the-loop for all clinical decision recommendations
  □ Drug interactions: AI not sole check for dangerous drug combinations
  □ Dosing: AI dosing recommendations require pharmacist/physician approval
  □ Alert fatigue: AI-generated clinical alerts calibrated for sensitivity vs. fatigue
```

## Government / Public Sector Checklist

Additional controls for FISMA, FedRAMP, NIST SP 800-53, E.O. 14110:

```
AI GOVERNANCE (GOVERNMENT):
  □ Executive Order 14110: AI in federal agencies — inventory, risk management, safety
  □ NIST AI RMF: adopted as primary AI governance framework
  □ AI Impact Assessment: completed for all high-impact AI systems
  □ Explainability: AI decisions affecting individuals must be explainable
  □ Human review: mandatory for AI decisions with significant individual impact

FedRAMP FOR AI:
  □ AI platforms used: confirm FedRAMP authorization status
    - Azure OpenAI: FedRAMP High authorized (Azure Government)
    - AWS Bedrock: FedRAMP High authorized (GovCloud)
    - Google Vertex AI: FedRAMP Moderate authorized
  □ Data classification: AI must not process data above its authorization level
  □ Government-specific: confirm no training on government data by provider

NIST SP 800-53 FOR AI:
  □ SA-11(10): AI developer security testing (adversarial testing)
  □ SA-15(11): Requirements for AI system trustworthiness
  □ SI-20: Information tagging (label AI-generated content)
  □ SC-28(3): Sensitive system isolation for AI processing classified data
  □ AU-12: Audit record generation for all AI system actions

SYNTHETIC CONTENT (GOVERNMENT):
  □ Official communications: AI-generated content labeled in all official communications
  □ Disinformation defense: program for detecting AI-generated election-related content
  □ C2PA: government agencies implement for press releases and official media
  □ Procurement: require C2PA attestation for AI-generated deliverables from contractors
```

## Telecom Sector Checklist

```
AI GOVERNANCE (TELECOM):
  □ Network AI: AI in routing/provisioning documented with fallback procedures
  □ 5G AI/ML: O-RAN AI components secured per NIST AI 100-2
  □ Fraud detection AI: tested quarterly for model drift and evasion
  □ Customer-facing AI: transparency disclosure (TCPA, GDPR as applicable)

SYNTHETIC CONTENT (TELECOM):
  □ Call center deepfake: agent authentication not solely voice biometric
  □ Vishing defense: customer education on AI voice cloning risks
  □ CLI spoofing + AI voice: combined attack defense procedures
  □ SIM swap: AI-assisted fraud detection for SIM swap attacks

NETWORK SECURITY AI:
  □ NOC AI: intrusion detection AI tested for adversarial evasion
  □ SS7/Diameter anomaly AI: tested against known telecom attack patterns
  □ DDoS AI: tested against adversarial traffic crafted to evade detection
  □ Supply chain: network equipment AI firmware integrity verification
```

## Implementation Tracking Template

```python
IMPLEMENTATION_TRACKER = {
    "organization": "ACME Corp",
    "assessment_date": "2026-07-16",
    "sector": "banking",
    "applicable_frameworks": ["nist_ai_100_2", "nist_ai_100_4", "caisi", "eu_ai_act", "dora"],
    "controls": {
        "AI-C-001": {"status": "implemented",
            "evidence": "docs/controls/AI-C-001-training-data-provenance.pdf",
            "implementation_date": "2026-05-15", "owner": "ML Engineering",
            "next_review": "2026-11-15"},
        "AI-C-002": {"status": "in_progress", "target_date": "2026-08-31", "owner": "Red Team",
            "blockers": ["Need GPU environment for adversarial testing"]},
        "AI-C-003": {"status": "not_started", "priority": "HIGH",
            "reason_for_delay": "Pending OPA deployment approval", "target_date": "2026-09-30"},
    },
    "summary": {
        "total_controls": 10, "implemented": 4, "in_progress": 3, "not_started": 3,
        "coverage_pct": 40,
        "critical_gaps": ["AI-C-003 (Agent Least Privilege)", "AI-C-008 (Inter-Agent Auth)"],
    },
}

def generate_implementation_report(tracker: dict) -> str:
    """Generate executive implementation status report."""
    summary = tracker["summary"]
    return f"""
AI STANDARDS IMPLEMENTATION STATUS REPORT
Organization: {tracker['organization']}
Date: {tracker['assessment_date']}

OVERALL PROGRESS:
  Total Controls Required: {summary['total_controls']}
  Implemented: {summary['implemented']} ({summary['coverage_pct']}%)
  In Progress: {summary['in_progress']}
  Not Started: {summary['not_started']}

CRITICAL GAPS:
{chr(10).join(f"  - {gap}" for gap in summary['critical_gaps'])}

RECOMMENDED IMMEDIATE ACTIONS:
  1. Prioritize Agent Least Privilege (OPA deployment) — blocks CAISI compliance
  2. Activate Inter-Agent Authentication — required for CAISI and ISO 42001
  3. Complete adversarial testing program — EU AI Act Art. 15 requirement
"""
```

## Related

- [NIST AI Standards Part 5: Control Mappings](05-part-05-control-mappings.md)
- [NIST AI Standards Part 4: Enterprise Architecture](04-part-04-enterprise-architecture.md)
- [NIST AI Standards Part 7: Future Trends](07-part-07-future-trends.md)
