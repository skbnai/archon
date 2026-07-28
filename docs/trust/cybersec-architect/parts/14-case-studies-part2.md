---
title: "Cybersecurity Architect Part 14: Industry Case Studies (2 of 2)"
doc_type: guide
domain: trust
status: current
topic_id: case-studies-part2
last_reviewed: 2026-07-28
maturity: practitioner
supersedes: []
tags: [cybersec-architect, manufacturing, telecommunications, energy, pharmaceuticals, aviation]
covers_version: "as of 2026"
---

Continuing the ten industry profiles from [Part 1](../14-case-studies.md) (Financial Services, Healthcare, Government, Defense, Retail): this part covers Manufacturing, Telecommunications, Energy & Utilities, Pharmaceuticals, and Aviation.

## Manufacturing

Priorities: Operational Technology / ICS security, safety of AI in industrial control systems, intellectual property protection (design files, process data), and supply-chain security. Drivers: IEC 62443 (OT security standard for industrial automation), NIS2 (manufacturers classified as important entities in the EU), the NIST CSF applied to OT environments, and the EU Cyber Resilience Act (connected product security). AI adoption: predictive maintenance, vision-based quality inspection, production optimization, AI-assisted design and engineering, and autonomous robotics.

| Scenario | Threat | Impact |
| --- | --- | --- |
| OT ransomware | Encrypt industrial control systems | Production shutdown; safety incident |
| AI quality inspection poisoning | Defeat vision inspection, ship defects | Product recall; safety liability |
| IP theft via AI | AI tools used to exfiltrate design files | Competitive harm; trade secret loss |
| Robot hijacking | AI-controlled robot reprogrammed for harm | Worker safety incident |

Recommended patterns: strict IT/OT network separation, with AI systems for OT never bridging to the IT network without dedicated controls; secure AI for quality inspection with model integrity verification and anomaly detection on vision outputs; and IP data governance treating CAD/design files as restricted with DLP controls.

## Telecommunications

Priorities: network infrastructure protection, subscriber data privacy, 5G network security (including AI in RAN and core), lawful interception compliance, and DDoS resilience. Drivers: NIS2 (telcos as essential entities under stringent requirements), GDPR (subscriber CDRs and location data are personal data), ETSI/3GPP 5G security standards for AI in 5G networks, and lawful-interception compliance for AI-powered communications analysis. AI adoption: network traffic optimization and capacity planning, AI-driven 5G RAN beam management and interference mitigation, fraud detection (toll fraud, SIM swap, subscription fraud), churn prediction and personalized offers, and NOC automation.

| Scenario | Threat | Impact |
| --- | --- | --- |
| AI network management compromise | Compromise AI managing the core network | Service disruption at scale |
| SS7/Diameter attacks enhanced by AI | AI-assisted protocol exploitation for tracking | Privacy breach; national security |
| AI-assisted telecom fraud | LLM-powered scam calls/SMS at scale | Subscriber harm; brand damage |
| CDR exfiltration via AI | AI accesses subscriber records without authorization | GDPR breach; regulatory fine |

## Energy & Utilities

Priorities: critical national infrastructure (CNI) protection, OT/SCADA security for the power grid, pipelines, and water systems, AI safety in automated control, and insider threat prevention. Drivers: NERC CIP (North American power grid cybersecurity standards), NIS2 (energy as an essential sector), the EU Cybersecurity Act (critical infrastructure requirements), and IEC 62351 (security for power system communications). AI adoption: grid optimization and load balancing, predictive maintenance for turbines/transformers/pipelines, smart meter analytics, demand forecasting, and autonomous substations.

| Scenario | Threat | Impact |
| --- | --- | --- |
| AI grid management attack | Compromise AI controlling power distribution | Regional power outage |
| AI sensor spoofing | False readings fed to AI health monitoring | Undetected infrastructure failure |
| Ransomware on AI control systems | Encrypt OT AI platforms | Grid instability; shutdown |
| Deepfake in crisis communication | Fake executive communication during an outage | Panic; stock manipulation |

## Pharmaceuticals

Priorities: clinical trial data integrity, drug development IP protection, regulatory submission security (FDA, EMA), and manufacturing quality system integrity. Drivers: FDA 21 CFR Part 11 (electronic records and signatures in regulated environments), ICH E9(R1) (statistical principles for clinical trials, applicable to AI-assisted analysis), the EMA's 2025 AI in Clinical Trials guidance, and GDPR/HIPAA for patient data in trials. AI adoption spans drug discovery (molecular generation, protein structure prediction), clinical trial design and patient selection, AI-assisted clinical data analysis, adverse event detection and pharmacovigilance, and manufacturing quality control — each carrying the same trial-integrity and IP-protection stakes as the regulatory drivers above, with AI systems requiring the same validation rigor as any GxP-regulated process.

## Aviation

Priorities: safety-critical systems integrity (DO-178C, DO-254), Air Traffic Control system protection, passenger data protection, and avionics software supply-chain integrity. Drivers: the EASA AI Roadmap 2.0 (framework and safety assurance for AI in aviation), emerging FAA AI certification guidance for type-certified aircraft systems, the ICAO Cybersecurity framework, and GDPR for passenger PII in airline AI systems. AI adoption: flight operations (fuel optimization, route planning, weather routing), AI-assisted ATC (traffic flow management, conflict detection), predictive maintenance via aircraft health monitoring, passenger experience personalization, and AI-assisted safety hazard analysis.

| Scenario | Threat | Impact |
| --- | --- | --- |
| AI ATC manipulation | Compromise AI supporting ATC decisions | Aviation safety incident |
| AI maintenance system poisoning | False predictions, undetected fault | Safety incident; disruption |
| Passenger data AI breach | AI reservation system exposes PII at scale | GDPR breach; passenger harm |
| AI avionics supply chain compromise | Malicious AI component in aircraft software | Safety-critical compromise |

Recommended patterns: extending DO-178C/DO-254 safety assurance to AI components in airborne systems; air-gapped AI for ATC and other safety-critical systems; AI model determinism requirements for certified applications, since some AI approaches are structurally incompatible with airworthiness standards; and architecturally separating safety-critical AI from operational AI systems.

## Related

- [Cybersecurity Architect Part 14: Industry Case Studies (1 of 2)](../14-case-studies.md)
- [Cybersecurity Architect Part 15: Emerging Trends](../15-emerging-trends.md)
- [Cybersecurity Architect Part 8: AI Governance](../08-ai-governance.md)
