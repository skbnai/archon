---
title: "AIDLC TOGAF Artifacts: Artifact Cross-Reference"
doc_type: guide
domain: architecture
status: current
canonical: true
topic_id: aidlc-artifacts-togaf-migration-to-ea-part3
maturity: expert
personas: [architect, governance, manager]
last_reviewed: 2026-07-19
covers_version: ""
supersedes: []
tags: [aidlc, enterprise-architecture, togaf, adm, ai-first, governance, templates, reference]
sources: []
---

# AIDLC TOGAF Artifacts: Artifact Cross-Reference

Part 3 of 3 — continues from [Part 2: Change Management & Cross-Cutting Artifacts (Phase H)](./08-aidlc-artifacts-togaf-change-management-cross-cutting.md).

Cross-reference guides mapping TOGAF ADM phases to artifacts and mapping AIDLC phases to output artifacts.

**Audience:** Enterprise Architects, Chief Technology Officers, Governance Leaders, AI Governance Council Members

**Coverage:** Artifact Cross-Reference by ADM Phase · Artifact Cross-Reference by AIDLC Phase

**As of:** 2026

---

## Artifact Cross-Reference by ADM Phase

| **ADM Phase** | **Artifact Templates in This Library** |
|---|---|
| PRE — Preliminary | EAFC-001 EA Framework Charter, AGP-001 AI Governance Principles, ESR-001 Stakeholder Register |
| A — Architecture Vision | SAW-001 Statement of Architecture Work, ACA-001 AI Capability Assessment, AVD-001 Architecture Vision |
| B — Business Architecture | ACM-001 AI Capability Map, HATB-001 Human-AI Task Boundary Map, AOM-001 AI Operating Model, WIA-001 Workforce Impact Analysis |
| C1 — Data Architecture | DAB-001 Data Architecture Blueprint, DM-001 Data Mesh Domain Design, VDA-001 Vector DB Architecture, FLS-001 Feature Store Lineage Spec |
| C2 — Application Architecture | LLMG-001 LLM Gateway Architecture, AOB-001 Agent Orchestration Blueprint, CSD-001 Copilot Stack Design, ASAP-001 Agent-Safe API Pattern |
| D — Technology Architecture | AIB-001 AI Infrastructure Blueprint, MPD-001 MLOps Platform Design, ZTA-001 Zero Trust AI Architecture, FAOD-001 FinOps for AI Design |
| E/F — Opportunities &amp; Migration | AUP-001 AI Use Case Portfolio, ARTA-001 AI-Readiness Transition Architecture, ARM-001 Architecture Roadmap |
| G — Implementation Governance | ACC-001 Architecture Compliance Checklist, ASRF-001 AI System Registration Form, ARB-001 ARB Decision Log |
| H — Change Management | ACR-001 Architecture Change Request, APR-001 AI Portfolio Review Report, AIM-001 Architecture Impact Model |
| EA — Cross-Cutting | EADR-001 EA Architecture Decision Record, AABR-EA-001 Agent Boundary Register, ASI-EA-001 AI System Inventory, RAIMP-001 RAI Maturity Programme |

## Artifact Cross-Reference Summary

| **AIDLC Phase** | **Key Inputs** | **Key Output Artifacts** |
|---|---|---|
| Phase 1: Discovery | AUC-001 Use Case Charter | BVC-001 Business Value Canvas, RCS-001 Risk Classification, ESO-001 Sponsor Sign-off |
| Phase 2: Feasibility | AUC-001, BVC-001, RCS-001 | FR-001 Feasibility Report, RR-001 Risk Register, FRIA-001, TPRM-001, COM-001 |
| Phase 3: Data Strategy | RR-001, COM-001, FR-001 | DS-001 Data Sheet, PIA-001, DLM-001 (init), BB-001 Bias Baseline, DPA-001 |
| Phase 4: Architecture | DS-001, RCS-001, COM-001, FRIA-001 | ADR-001 Architecture Decisions, CAP-001 Constitutional AI Policy, MCD-001 Model Card (Draft), ATM-001 Threat Model, EXD-001 Explainability Design |
| Phase 5: Development | ADR-001, CAP-001, DS-001, COM-001 | ETR-001 Experiment Tracking, TRL-001 Training Logs, BMR-001 Bias Mitigation, CAL-001 Code Audit, MRE-001 Model Registry |
| Phase 6: Evaluation | MRE-001, CAP-001, MCD-001, BB-001 | RTR-001 Red Team Report, FER-001 Fairness Eval, PBR-001 Performance Benchmark, CCA-001 Constitutional Audit, MCF-001 Final Model Card, SPT-001 Security Test |
| Phase 7: Deployment | MCF-001, RTR-001, CCA-001, Governance Approval | DRB-001 Deployment Runbook, IRP-001 Incident Response, ALC-001 Audit Log Config, UDD-001 User Disclosure, RMD-001 Monitoring Dashboard |
| Phase 8: Monitor &amp; Retire | Runtime data, DRB-001, ALC-001, COM-001 | MMR-001 Monthly Report, DAL-001 Drift Alert Log, QAR-001 Quarterly Audit, RCL-001 Regulatory Change Log, MSP-001 Sunset Plan |
| EA (Cross-Phase) | All phase artifacts + Business Strategy + Regulatory Frameworks | ASI-001 AI System Inventory, ACM-001 AI Capability Map, AABR-001 Agent Boundary Register, EADR-001 EA Architecture Decisions, DLM-001 Data Lineage Map (full) |

---

## Related

- [../04-aidlc-artifacts-togaf-migration-to-ea.md](../04-aidlc-artifacts-togaf-migration-to-ea.md) — Part 1: Opportunities, Migration &amp; Implementation Governance (Phase E-G)
- [./08-aidlc-artifacts-togaf-change-management-cross-cutting.md](./08-aidlc-artifacts-togaf-change-management-cross-cutting.md) — Part 2: Change Management &amp; Cross-Cutting Artifacts (Phase H)
- [../01-aidlc-artifacts-discovery-to-model.md](../01-aidlc-artifacts-discovery-to-model.md) — AIDLC Phases 1–4 artifact templates
- [../02-aidlc-artifacts-development-to-retirement.md](../02-aidlc-artifacts-development-to-retirement.md) — AIDLC Phases 5–8 artifact templates
- [../03-aidlc-artifacts-togaf-foundation-to-technology.md](../03-aidlc-artifacts-togaf-foundation-to-technology.md) — TOGAF ADM Preliminary through Technology phases

## Sources

None currently documented.
