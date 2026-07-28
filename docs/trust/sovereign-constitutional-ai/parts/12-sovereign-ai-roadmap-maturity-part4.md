---
title: "Roadmap, Maturity & Standards Canon (4 of 4)"
doc_type: guide
domain: trust
status: current
topic_id: sovereign-ai-roadmap-maturity-part4
last_reviewed: 2026-07-28
maturity: practitioner
supersedes: []
tags: [sovereign-constitutional-ai, interview-guide, standards-canon, certifications]
covers_version: "as of 2026-07-10"
---

Continuing from [Part 3](12-sovereign-ai-roadmap-maturity-part3.md) (regulatory and behavioral interview patterns): this part covers the whiteboard design challenges, crisis simulation and emerging-topics patterns, the hiring scoring rubric, and the complete standards/regulations/certifications/books/tools canon.

## Pattern 5: Whiteboard / Design Challenge

Live architecture exercises for Principal/Distinguished final rounds. **Challenge 1:** "Design the agent governance fabric for a financial services firm running 200 agents across 15 business units. 45 minutes." Evaluators look for: starting from problem constraints (regulatory, scale, operational); identifying the five registries and their relationships; a policy deployment pipeline showing how constitutional changes propagate to 200 agents; kill switch architecture with a clear SLA for stopping one or all agents; audit ledger design supporting cross-agent search for a regulatory inquiry; and exception handling for an agent offline during a governance update.

**Challenge 2:** "A new EU regulation requires all AI systems to generate a human-readable explanation of any decision within 24 hours of a request. Redesign your audit and explainability architecture to meet this. 30 minutes." Evaluators look for: SHAP value storage at decision time rather than recomputed on request; a natural-language explanation generation pipeline; SLA design (a 24-hour external requirement driving an internal 4-hour SLA to leave room for human review); the EU's 24-official-language multilingual requirement; a citizen-accessible plain-language interface; and edge cases — what if the model has since been updated, or SHAP values weren't stored for older decisions.

## Pattern 6: Scenario / Crisis Simulation

**Q17:** "It's 3am. An automated alert says your L3 trading support agent has made 800 transactions in 90 minutes — 10x normal rate. On-call alerts you. Walk me through your response." A strong answer moves in minutes: 0-5 (invoke the L4 system-level kill switch immediately, target under 30 seconds per the L3 SLA; confirm the audit ledger is live and pull the last 800 transactions); 5-15 (triage whether transactions are valid market orders, fraudulent, or test data; check for a malformed instruction/prompt injection; check for a recursive self-call loop; confirm exchange acknowledgment of all 800); 15-30 (escalate to CRO and CISO for financial exposure plus potential security incident; engage exchange emergency contacts; confirm whether the constitutional classifier fired); hour 1 (root cause across instruction loop, injection attack, or unusual market-condition behavior; regulatory notification if material, e.g. DORA's 4-hour significant-incident reporting window). Post-incident: add a hard transaction rate cap in Cedar, add a circuit-breaker loop-detection pattern to the agent runtime, and add "transaction volume anomaly" as a constitutional escalation trigger.

**Q18:** "A civil society organization has published a report claiming your bank's AI lending system discriminates against minority applicants. The press is calling. You have 2 hours before a public statement is needed. What's your governance response?" A strong answer gathers facts before speaking (hour 0-30: pull 12 months of demographic parity reports, determine whether the claim is narrow or broad, compare methodologies if published, and have Legal hold off on anything admitting liability before facts are confirmed), convenes governance review (hour 30-60: RAIO and CRO meet; if disparity is confirmed, acknowledge immediately with what was found and what's being done; if not confirmed, prepare a methodology explanation and offer an NDA-audit to the organization), and issues a transparent, factual, action-oriented statement (hour 60-120: never claim "our AI doesn't discriminate" without data — cite the specific monitored metric; commit to an independent audit if there's any internal data uncertainty, and to engagement with the organization). The structural response: this should trigger a constitution review adding an external civil society audit right, and a move to publishing demographic performance data quarterly so future reports carry no surprise element.

## Pattern 7: Emerging Topics (2026 Frontier)

**Q19:** "How would you govern agentic AI systems operating at L4 autonomy — supervised autonomous — in a regulated enterprise?" A strong answer covers board-level (not just RAIO) approval, an external audit requirement, real-time human monitoring dashboards, a sovereign infrastructure requirement, formal constitutional certification (not just enforcement), a kill switch SLA under 30 seconds, and continuous external red-teaming.

**Q20:** "What does the Digital Omnibus 2026 change for enterprises already EU AI Act compliant?" The Digital Omnibus amendment adjusted some conformity assessment requirements for SMEs and introduced proportionality provisions; for large enterprises already conformity-assessed, the substantive change is minimal, with some reporting timeline adjustments. The more significant 2026 development is the High-Risk provisions entering enforcement for most systems from August 2026 — enterprises preparing since 2024 are now in live compliance mode.

**Q21:** "How do you design AI governance for a system that uses agentic AI for both internal operations and as a product sold to other enterprises?" A strong answer covers two-tier governance: internal deployer obligations plus product provider obligations under EU AI Act Art. 25; customer constitutional governance requirements; API-level constitutional enforcement for product API consumers; a product model card and conformity documentation; and customer audit rights.

## Scoring Rubric (for Hiring Panels)

Score 5, Exceptional: the design is complete, constraints are handled, tradeoffs are explicit, the candidate defends under pushback, and adds insights the interviewer hadn't considered. Score 4, Strong: the design is sound, key elements present, most follow-ups handled. Score 3, Adequate: the framework is correct with some gaps, direct questions handled but follow-ups cause struggle. Score 2, Developing: concepts are known but the candidate cannot design or implement, following frameworks without deviating from them. Score 1, Insufficient: conceptual knowledge only, no design or implementation experience. Minimum bar for Principal AI Governance Architect: score 4 on technical architecture (Q5-Q8), score 4 on regulatory depth (Q9-Q11), score 3 on behavioral (Q12-Q14). Minimum bar for Distinguished Architect / Chief AI Governance Officer: score 5 on at least three technical questions, score 4+ on the whiteboard challenge, and strong organizational complexity handling (Q16).

## Standards, Regulations, Certifications, Books, Tools Canon

Must-know standards: ISO 42001:2023 (AI Management System, the ISO 27001 equivalent for AI); ISO/IEC 23894:2023 (AI Risk Management); ISO/IEC 42006:2025 (AI Governance, emerging); NIST AI RMF 1.0 (2023) plus the AI 600-1 GenAI Profile (2024); the IEEE P7000 series (ethics in autonomous and intelligent systems); OECD AI Principles (2019, 2024 update). Must-know regulations: the EU AI Act (2024) plus its Digital Omnibus Amendment (2026); GDPR Arts. 5/6/22; DORA; SR 11-7; FDA SaMD guidance; the UK's pro-innovation regulatory approach; and China's Generative AI Regulation (2023) plus Algorithm Recommendation Regulation (2022).

Certifications worth pursuing: ISO 42001 Lead Implementer and Lead Auditor (advanced, AI management/audit); CISA and CRISC (ISACA, professional, IT/AI audit and risk); CIPP/E, CIPP/US, and CIPM (IAPP, professional, privacy); AWS Certified AI Practitioner (foundation); Microsoft AI-102 (intermediate, Azure AI); Google Professional ML Engineer (intermediate, ML in production); TOGAF 10 (professional, enterprise architecture foundation).

Essential reading spans four categories. AI governance and ethics: "The Alignment Problem" (Christian, 2020), "Weapons of Math Destruction" (O'Neil, 2016), "Atlas of AI" (Crawford, 2021), "Human Compatible" (Russell, 2019), "Power and Progress" (Acemoglu & Johnson, 2023). AI safety and alignment (technical): "Artificial Intelligence Safety and Security" (ed. Yampolskiy, 2018), "AI Safety Gridworlds" (Leike et al., 2017), "Constitutional AI" (Bai et al., 2022), "Collective Constitutional AI" (Ganguli et al., 2023). Enterprise AI governance: "Trustworthy AI" (Ammanath, 2022), the NIST AI RMF Playbook, "Responsible AI: Best Practices for Creating Trustworthy AI Systems" (Masood, 2024). Policy and law: "The Age of Surveillance Capitalism" (Zuboff, 2019), "Automating Inequality" (Eubanks, 2018), and assorted AI-and-law review collections.

Key research papers: Bai et al.'s Constitutional AI (Anthropic, 2022); Ganguli et al.'s Collective Constitutional AI (Anthropic, 2023); NIST AI 600-1 GenAI Risks (2024); the MIT AI Risk Repository (Slattery et al., 2024); DeepMind's Frontier Safety Framework (2024); the OWASP LLM Top 10 (2023, 2025 update) and Agentic AI Top 10 (2026); and the Anthropic Model Specification (2024).

Communities and organizations to follow: Partnership on AI (multi-stakeholder governance), the AI Now Institute (social implications), the Center for AI Safety, the Future of Life Institute (existential risk), the Ada Lovelace Institute (democratic AI), OECD.AI (global policy), GovAI/Centre for the Governance of AI (research), the UK AI Safety Institute (model evaluation), and IEEE SA AI Ethics (standards development).

Core tooling: AI Fairness 360 and Fairlearn for bias detection and mitigation; SHAP and LIME for explainability; OPA and Cedar for policy-as-code enforcement; OpenFGA for agent delegation authorization; MLflow for model versioning and lineage; Presidio for PII detection and anonymization; Garak for LLM vulnerability scanning; HELM for holistic model evaluation; RAGAS for RAG pipeline quality; deepeval for LLM application testing; and the Adversarial Robustness Toolbox for defense against adversarial attacks.

## Related

- [Roadmap, Maturity & Standards Canon (1 of 4)](../12-sovereign-ai-roadmap-maturity.md)
- [Roadmap, Maturity & Standards Canon (3 of 4)](12-sovereign-ai-roadmap-maturity-part3.md)
- [Sovereign Constitutional AI Part 7: Constitutional AI Engineering](../07-constitutional-ai-engineering.md)
