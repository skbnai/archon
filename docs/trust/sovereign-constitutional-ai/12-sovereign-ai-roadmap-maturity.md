---
title: "Roadmap, Maturity & Standards Canon (1 of 4)"
doc_type: guide
domain: trust
status: current
topic_id: sovereign-ai-roadmap-maturity
last_reviewed: 2026-07-28
maturity: practitioner
supersedes: [docs/sovereign-constitutional-ai/sovereign-ai-roadmap-maturity.md]
tags: [sovereign-constitutional-ai, maturity-model, compliance, trust-framework]
covers_version: "as of 2026-07-10"
---

**Audience:** Chief AI Officers, principal AI governance architects, AI governance leads, enterprise architects. **Purpose:** AI governance maturity model, board reporting framework, compliance and trust frameworks, a 24-month learning roadmap, a Principal AI Governance Architect interview guide, and the complete standards/books/tools canon. This part covers the maturity model, compliance framework, and trust framework; [Part 2](parts/12-sovereign-ai-roadmap-maturity-part2.md) covers the learning roadmap and interview guide (strategic and technical patterns); [Part 3](parts/12-sovereign-ai-roadmap-maturity-part3.md) covers the regulatory and behavioral interview patterns; [Part 4](parts/12-sovereign-ai-roadmap-maturity-part4.md) covers the remaining interview patterns, scoring rubric, and the standards canon.

## AI Governance Maturity Model

Five levels: Level 1 Ad Hoc (no formal governance, case-by-case decisions, no risk register — shadow AI everywhere, no accountability chain, purely reactive); Level 2 Developing (basic policies documented, AI register being built, roles assigned — an acceptable use policy exists, an RAI Champion is named, basic model cards exist); Level 3 Defined (a formal operating model, policy-as-code implemented, fairness monitoring active — the AI Governance Council is operational, an ARB approval gate exists, fairness reports run monthly); Level 4 Managed (metrics-driven governance, continuous compliance monitoring, constitutional AI deployed — a live constitutional classifier, quarterly kill switch tests, quarterly board AI briefings); Level 5 Optimizing (proactive governance, continuous improvement, democratic participation in the constitution — ISO 42001 certified, EU AI Act conformity assessed, a public AI register, CCAI input incorporated).

Maturity is scored 0-4 across eight dimensions, summing to a level: AI Strategy (no strategy → informal vision → documented → enterprise-aligned → AI-native board commitment); Governance Structure (none → named CAIO → Governance Council → full 6-layer model → board-integrated with external advisory); Risk Management (no register → basic → tiered → continuous monitoring → predictive); RAI/Constitutional (none → principles stated → office plus model cards → constitutional enforcement live → CCAI/democratic participation); Audit & Assurance (none → self-assessment → internal audit → three lines of defense → ISO 42001 certified); Policy-as-Code (manual review only → some OPA/Cedar → constitutional policies live → full control library → constitutional traceability); Agent Governance (no policy → basic policy → L0-L5 taxonomy applied → kill switches tested → sovereign agent fabric); Sovereign AI (fully dependent → data residency only → sovereign infra for Tier 1 → sovereign model → full stack sovereign). Total score out of 32 maps to level: 0-8 is Level 1, 9-15 is Level 2, 16-22 is Level 3, 23-28 is Level 4, 29-32 is Level 5.

## AI Compliance Framework

The regulatory landscape as of July 2026: the EU AI Act (prohibitions since Aug 2024, GPAI since Aug 2026, High-Risk from Dec 2027/Aug 2028 — risk classification, conformity assessment, transparency, human oversight); GDPR Art. 22 (since 2018 — right to human review, explanation, opt-out for automated decisions); DORA (EU financial, since Jan 2025 — ICT risk, incident reporting, resilience testing); the NIST AI RMF (US federal plus voluntary adoption, since Jan 2023 — GOVERN/MAP/MEASURE/MANAGE); SR 11-7 (US banking, applies to AI since 2011 — model risk management, documentation, validation); the EU MDR for AI (EU healthcare, since 2024 — SaMD classification, clinical evidence); FDA SaMD guidance (US healthcare, since 2021 — predetermined change control, real-world performance); ISO 42001:2023 (international — an AI management system standard); ISO/IEC 23894:2023 (international — AI risk management); China's AI regulation (since 2023 — algorithmic recommendation, generative AI, deep synthesis); and India's PDPB plus AI policy guidance (since 2023).

Controls map across frameworks: AI Risk Classification (EU AI Act Art. 6/9; NIST MAP 1.1; ISO 42001 Cl. 6.1; SR 11-7 §4); AI Impact Assessment (EU AI Act Art. 9; GDPR DPIA Art. 35; NIST MAP 5.1; ISO Cl. 8.4; SR 11-7 §4); Model Documentation (EU AI Act Art. 11/Annex IV; NIST GOVERN 6.1; ISO Cl. 8.5; SR 11-7 §4); Human Oversight (EU AI Act Art. 14; GDPR Art. 22; NIST GOVERN 5.2; ISO Cl. 8.6; SR 11-7 §5); Transparency/Explanation (EU AI Act Art. 13; GDPR Art. 22; NIST GOVERN 6.2; ISO Cl. 9.1; SR 11-7 §4); Fairness Monitoring (EU AI Act Art. 10; NIST MEASURE 2.5; ISO Cl. 9.1; SR 11-7 §5); Audit Trail (EU AI Act Art. 12; NIST MEASURE 4.1; ISO Cl. 9.2; SR 11-7 §5); Incident Reporting (EU AI Act Art. 73; GDPR Art. 33; NIST MANAGE 4.1; ISO Cl. 10.2; SR 11-7 §5); Kill Switch (EU AI Act Art. 14; NIST MANAGE 3.2; ISO Cl. 8.6).

## AI Trust Framework

AI trust is multidimensional and earned through demonstrated behavior, not declared by the deployer, across four dimensions:

```
TECHNICAL TRUST (can we verify the system works as claimed?)
- Performance: does it perform within stated metrics?
- Robustness: does it hold up under adversarial conditions?
- Reliability: is uptime and SLA commitment met?
- Explainability: can decisions be understood and verified?

ETHICAL TRUST (does the system act in accordance with stated values?)
- Fairness: does it treat all groups equitably?
- Honesty: does it not deceive users or operators?
- Constitutional compliance: does it follow its stated constitution?
- Privacy: does it protect personal data as committed?

GOVERNANCE TRUST (is the organization accountable?)
- Transparency: are AI systems disclosed and documented?
- Accountability: are named humans responsible?
- Auditability: can governance be independently verified?
- Democratic legitimacy: are affected parties represented?

SOVEREIGN TRUST (is control maintained?)
- Data sovereignty: data stays in-jurisdiction
- Infrastructure sovereignty: no foreign control point
- Governance sovereignty: kill switch without vendor
- Constitutional sovereignty: enterprise sets its own AI values
```

Each dimension needs evidence and a measurement cadence: Performance via model card benchmarks and production metrics (monthly report); Robustness via red-team results and adversarial pass rate (quarterly security review); Fairness via demographic parity gap and equalized odds (monthly dashboard); Constitutional via violation rate (real-time dashboard); Auditability via ledger coverage and explanation capability (annual audit); Sovereign via an infrastructure sovereignty score and kill switch drill results (quarterly review).

## Related

- [Roadmap, Maturity & Standards Canon (2 of 4)](parts/12-sovereign-ai-roadmap-maturity-part2.md)
- [Sovereign Constitutional AI Part 3: AI Governance Operating Model](03-ai-governance-operating-model.md)
- [Sovereign Constitutional AI Foundations (1 of 2)](11-sovereign-ai-foundations.md)
