---
title: "AI Solution Lifecycle Deliverables by Role (Part 2 of 3): Security, RAI/Governance, Solution, Distinguished, Data & Platform Architect Deep-Dives"
doc_type: guide
domain: architecture
topic_id: ai-solution-lifecycle-deliverables-part2
date_created: 2026-07-07
last_reviewed: 2026-07-10
status: current
supersedes: []
source_type: native-md
tags: ["enterprise-architecture", "process", "architect-roles"]
covers_version: "as of 2026-07-10"
---

:::info Part 2 of 3
This is the second part of a three-part guide. Start with [Part 1](/archon/architecture/74-ai-solution-lifecycle-deliverables) (Lifecycle, Roles, Matrix & Enterprise Architect) and continue with [Part 3](/archon/architecture/parts/29-ai-solution-lifecycle-deliverables-part3) (Use Case Walk-throughs & Architect's Checklist).
:::

---

## 4.2 Security Architect

**Incubation:** The Security Architect creates a Preliminary Threat Model, identifying attack surface, key threat actors, and critical risks at concept stage. This informs AI Safety Level classification. The stub outlines asset inventory (model weights, training data, API endpoints, agent tool access), top threat actors (external attacker with prompt injection and model exfiltration, malicious insider with training data poisoning, third-party vendor with supply chain risk), and critical risks.

**RFP / Vendor Selection:** The Security Architect defines Security RFP Requirements — mandatory security criteria for vendor evaluation. Mandatory criteria include SOC 2 Type II (or equivalent) report, ISO 27001 certification, penetration test results from the last 12 months, documented and audited data residency controls, customer-managed encryption keys (BYOK), customer-retained audit logs that the vendor cannot delete, contractual service termination / kill switch guarantee, and vulnerability disclosure program. Preferred criteria include EU AI Act conformity assessment, OWASP LLM Top 10 self-assessment, bug bounty program, and zero-trust architecture.

**Design & Build:** The Security Architect creates a comprehensive Security Architecture Document covering full threat model, guardrail architecture, identity and access model, network controls, and incident response. A Guardrail Specification documents all guardrail layers: constitutional classifier parameters, Open Policy Agent / Cedar policies, tool sandbox configuration, input/output filters.

**Operate & Scale:** The Security Architect maintains a Security Monitoring Dashboard tracking prompt injection attempts, anomalous agent behavior, authentication failures, policy violations, and kill switch tests. Quarterly penetration testing scopes AI-specific attack vectors per OWASP LLM Top 10 and prompt injection scenarios.

**Retire / Decommission:** The Security Architect develops a Secure Wipe Plan documenting secure deletion of model weights, training data, and inference logs, with certificates of destruction for regulated data.

---

## 4.3 RAI / Governance Lead

**Incubation:** The RAI Lead conducts an AI Impact Assessment v0 (preliminary), an early-stage assessment of potential harms and benefits informing go/no-go decision. The assessment covers purpose and scope, EU AI Act classification (prohibited, high-risk under Annex III, limited risk, or minimal risk), affected groups and vulnerable populations, key potential harms with probability and severity ratings, key potential benefits, preliminary fairness risks, and recommendation.

**RFP / Vendor Selection:** The RAI Lead defines RAI Evaluation Criteria for RFP, scoring vendors on constitutional / RAI capabilities (built-in constitutional AI, fairness tools; 25% weight), explainability support (SHAP/LIME APIs, model cards; 20%), fairness evaluation tooling (AIF360 integration, bias reports; 20%), privacy-preserving techniques (differential privacy, federated learning; 15%), and audit trail and compliance (immutable logging, regulatory reporting; 20%).

**Design & Build:** The RAI Lead ratifies an AI Constitution — the constitutional document for the system (see Constitutional AI Engineering resources for templates). A Model Card documents system-level documentation: intended use, performance metrics, fairness evaluation results, known limitations, recommended uses and misuses. The RAI Lead also creates a Bias Monitoring Playbook defining metrics, thresholds, alert escalation, and remediation for each fairness metric in production.

**Operate & Scale:** The RAI Lead produces a Monthly Fairness Report (automated plus human-reviewed) including demographic parity, equalized odds, individual fairness checks, and trend analysis. An Annual Ethics Audit provides comprehensive review of constitutional compliance, fairness performance, incident history, and governance adherence.

**Retire / Decommission:** The RAI Lead ensures Responsible Retirement Checklist compliance: data deleted with dignity (no continued processing), affected users notified, regulatory obligations met, lessons learned documented.

---

## 4.4 Solution Architect

**Incubation:** The Solution Architect conducts a Feasibility Study, assessing technical feasibility: Can we build this? What are the technical risks? What dependencies exist?

**RFP / Vendor Selection:** The Solution Architect creates a Vendor Functional Comparison, side-by-side comparison of vendor capabilities against functional requirements, including PoC results if conducted.

**Design & Build:** The Solution Architect develops a Solution Design Document (SDD) covering full technical design: component architecture, integration design, data flow, API contracts, infrastructure design, and test strategy.

**Operate & Scale:** The Solution Architect maintains a Production Runbook with step-by-step operational procedures: startup, shutdown, incident response, escalation, and common failure scenarios with resolutions. Quarterly Capacity Reviews track usage trends, performance headroom, scaling recommendations, and cost optimization.

**Retire / Decommission:** The Solution Architect prepares a Handover to Decommission Pack documenting each component: what it does, dependencies, data it holds, shutdown procedure, and contacts.

---

## 4.5 Distinguished / Principal Architect

**Incubation:** The Distinguished Architect produces a Technical Vision — a three to five page technical narrative describing the future state and rationale for the chosen technical direction, not a detailed design document but a strategic vision.

**RFP / Vendor Selection:** The Distinguished Architect creates Architecture Decision Records (ADRs) capturing key architectural decisions with rationale and alternatives considered. An ADR includes status, context (why this decision is needed), decision (which option is chosen), rationale (benefits, compliance reasons, fallback considerations), consequences (positive and negative), and mitigation strategies.

**Design & Build:** The Distinguished Architect conducts Design Authority Review, acting as gatekeeper for the Solution Design Document: technical correctness, pattern alignment, risk coverage, security adequacy.

**Operate & Scale:** The Distinguished Architect performs Post-Implementation Review at 90 days and annually: what did we learn? What would we do differently? What patterns should be adopted or retired?

**Retire / Decommission:** The Distinguished Architect captures lessons learned in an Innovation Brief, documenting patterns for future systems: what worked, what didn't, what should become standard.

---

## 4.6 Data Architect

**Incubation:** The Data Architect maps the Data Landscape Assessment: What data does this system need? Where does it live? What is its classification? What are the sovereignty requirements?

**RFP / Vendor Selection:** The Data Architect defines Data RFP Requirements covering data residency guarantees, data lineage support, data portability, personally identifiable information handling, and retention controls.

**Design & Build:** The Data Architect formalizes a Data Contract specifying data flowing into and out of the AI system: schema, classification, service level agreement, lineage, owner, residency. Example: A loan underwriting agent requires applicant profile data classified as PERSONAL_FINANCIAL, residency in EU, schema per applicant_v2.json, personally identifiable fields including name, date of birth, national ID, address, purpose for credit assessment, retention for 7 years per Supervisory Review 11-7. Outputs include credit decision (same classification and residency), with explanation and SHAP values required per EU AI Act. Lineage tracks source from core banking applicants, transformations for PII masking and feature engineering, and model version at decision.

The Data Architect also designs Data Lineage, mapping end-to-end lineage from source system to AI training data to model to decision output.

**Operate & Scale:** The Data Architect maintains a Data Quality SLA Dashboard monitoring data freshness, schema compliance, personally identifiable information leakage alerts, and lineage breaks. An Annual Data Residency Audit verifies all AI data remains within required jurisdictions and generates evidence for regulatory inspection.

**Retire / Decommission:** The Data Architect creates a Data Deletion / Purge Plan specifying which data to delete, in what order, by when, with what verification, generating certificates of deletion for regulated data classes.

---

## 4.7 Platform / MLOps Architect

**Incubation:** The MLOps Architect conducts a Platform Readiness Assessment: Does the existing AI platform support this initiative? What gaps need addressing?

**RFP / Vendor Selection:** The MLOps Architect defines MLOps Platform RFP Requirements covering model registry, CI/CD for models, evaluation gate framework, drift detection, and cost controls.

**Design & Build:** The MLOps Architect designs an AI Landing Zone covering sovereign AI landing zone elements: model registry, evaluation pipeline, inference infrastructure, governance integrations (policy engine, audit ledger, constitution registry).

The MLOps Architect also creates an Eval Gate Framework defining automated evaluation gates models must pass before promotion to each environment. Example: Staging to production gates include Fairness gate (demographic parity gap threshold 0.05, BLOCK on fail), Performance gate (task accuracy threshold 0.90, BLOCK), Constitutional gate (constitutional violation rate threshold 0.001, BLOCK), and Latency gate (p99 latency 2000ms, WARN on fail).

**Operate & Scale:** The MLOps Architect implements a Model Drift + Retraining Pipeline monitoring Population Stability Index, prediction drift, and data drift; triggering automated retraining or alerts. An AI FinOps Dashboard tracks cost per inference, cost per model version, cost trend, and optimization opportunities.

**Retire / Decommission:** The MLOps Architect creates a Model Archival Plan for secure archival of model weights, training data, and evaluation results with defined retention periods, ensuring regulatory reconstruction capability.
