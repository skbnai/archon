---
title: "NIST AI Standards — Future Trends & Standards Evolution"
doc_type: guide
domain: trust
status: current
topic_id: part-07-future-trends
last_reviewed: 2026-07-28
maturity: practitioner
supersedes: [docs/nist-ai-standards/part-07-future-trends.md]
tags: [future-trends, emerging-threats, standards-evolution, frontier-ai, quantum, regulation]
covers_version: "as of 2026"
---

**Audience:** AI security researcher, CISO, standards practitioner, AI architect.

## Emerging Threat Landscape (2026-2030)

**AI-native attacks (next generation).** Current adversarial ML attacks require significant expertise; by 2028, AI will automate attack generation:

```
Adversarial ML as a Service (AMLaaS): non-expert attackers query an API that
generates optimized adversarial examples for a target model in seconds, not
days — under $100 for a complete evasion attack on a commercial ML API.

Multi-objective attacks: today's attacks optimize for a single objective
(misclassify); future attacks will simultaneously evade the ML classifier,
bypass rule-based filters, avoid detection signatures, minimize perturbation
(steganographic), and transfer across multiple models at once.

Adaptive attacks: continuously updated, learning from partial feedback on
whether they were detected — self-improving adversarial perturbation,
resembling APT tradecraft: persistent, adaptive, targeted.
```

**Foundation model attacks (2026-2028).** Universal adversarial suffixes (Zou et al. 2023 — a suffix appended to any prompt bypasses alignment) are mostly patched in major commercial models today, but new suffixes surface periodically and open-source models stay vulnerable. Many-shot jailbreaking (Anthropic 2024 — in-context examples bypass safety) is patched in major models but smaller models remain exposed, and growing 1M+ token context windows will make monitoring harder. Indirect injection at scale is shifting from targeted documents/emails today toward poisoned data in widely-used datasets (Wikipedia, arXiv, GitHub) — any AI trained on or using these becomes systematically vulnerable, affecting millions of deployments at once. Model architecture attacks (gradient attacks on attention mechanisms, token embedding space manipulation, multi-head attention manipulation) remain largely theoretical but may become practical with greater model access.

**Multimodal attack expansion.** Image-plus-text combined attacks embed a trigger in an image that hijacks AI text analysis when combined with specific text. Audio-visual sync attacks pair deepfake audio/video with adversarial perturbations that defeat both human inspection and deepfake detectors — proof-of-concept today, expected in production by 2027+. Cross-modal transfer causes an adversarial image perturbation to manipulate a text response (e.g., an image sent to customer service AI causing an injected text reply). Physical-world adversarial attacks use adversarial patches on physical objects (QR codes, stickers, clothing) to defeat vision systems, including security cameras.

## Standards Evolution Roadmap

| Standard | Status | Expected | Focus |
|---------|--------|----------|-------|
| NIST AI 100-1 | Published | 2023 | AI Trustworthiness |
| NIST AI 100-2 | Published | March 2024 | Adversarial ML |
| NIST AI 100-3 | In development | 2025-2026 | AI Technology Resilience |
| NIST AI 100-4 | Published | May 2024 | Synthetic Content |
| NIST AI 100-5 | Planned | 2026 | Agentic AI (formal) |
| NIST AI 100-6 | Planned | 2027 | AI in Critical Infrastructure |
| NIST SP 800-220 | In development | 2026 | AI Security for Enterprises |
| NIST AI RMF 2.0 | Expected | 2026-2027 | Updated risk management |

International standards are converging: ISO/IEC JTC1 SC42 has published ISO 42001 (AI Management Systems, 2023) and ISO 24028/24029 (Trustworthiness/Robustness), with ISO 42005 (AI Risk Management) in development for 2025 and ISO 42006 (AI Evaluation) planned for 2026. IEC 63278 (AI for Cybersecurity — covering AI-powered IDS/IPS and AI-assisted incident response) is expected 2026-2027. IEEE is developing 2941 (AI API Standard), P3119 (AI Testing Standard), and the P7000 series (Ethical AI). The convergence pattern: the EU AI Act adopts ISO 42001 as a conformance standard, NIST AI RMF and ISO 42001 gain interoperability guidance in 2026, the G7 Hiroshima Process drives an international AI code of conduct, and the US-EU AI Safety Institute collaboration produces joint standards.

EU AI Act enforcement: the Act entered into force August 2024; prohibited AI (Article 5 — social scoring, real-time biometric surveillance in public) became enforceable February 2025; General Purpose AI obligations (Articles 51-56, registration and transparency, with enhanced safety/cybersecurity obligations for systemic-risk GPAI) became enforceable August 2025; high-risk AI (Annex III) became enforceable **August 2026**, requiring risk management, data governance, technical documentation, logging, transparency, human oversight, accuracy, and cybersecurity, with penalties up to €30M or 6% of global turnover; notified bodies and standardization continue updating through 2027-2030.

## Quantum Computing Impact on AI Security

Four intersections matter for 2028-2035: cryptographic AI model protection (model weights currently protected by AES-256/RSA-2048 signing; Shor's algorithm breaks RSA once a cryptographically relevant quantum computer exists, estimated 2030-2035 — migrate model signing to NIST PQC now, CRYSTALS-Kyber/CRYSTALS-Dilithium); quantum-enhanced adversarial attacks (quantum optimization could find adversarial examples faster than classical gradient-step methods, though quantum ML hardware isn't yet practical); quantum ML models (quantum neural networks may carry different attack surfaces, with adversarial examples that may not transfer from classical models, requiring dedicated defense research); and quantum-resistant AI (today's classical-bit-operation models need a post-quantum-secure design, with "harvest now, decrypt later" attacks on AI training data a key present-day concern). Immediate action: migrate AI model signing and authentication to the finalized NIST PQC standards (FIPS 203, 204, 205 — finalized August 2024).

## Frontier AI Safety Standards

AI safety (alignment) asks whether AI pursues intended goals without unintended harm — the domain of goal misspecification, reward hacking, and instrumental convergence, led by organizations like Anthropic, DeepMind, and OpenAI safety teams. AI security (adversarial) asks whether systems withstand deliberate attack — evasion, injection, extraction, poisoning — led by NIST, CAISI, MITRE, and academic research. The two converge fully in agentic AI, where "can an attacker manipulate this agent" and "could this agent cause unintended harm even without attack" become the same governance question. Joint standards development includes a UK AI Safety Institute plus NIST joint evaluation framework, Anthropic's Responsible Scaling Policy influencing NIST standards, OpenAI's Preparedness Framework informing regulatory guidance, and EU AI Office systemic risk assessment for frontier models.

Expected NIST AI safety standards 2026-2028: NIST AI 100-5 (Agentic AI Security, expected 2026 — formal guidance for autonomous agents, tool-use security standards, multi-agent system security architecture, human oversight requirements by autonomy level); NIST SP 800-220 (AI in Enterprise Security, expected 2026 — SP 800-53 extensions for AI-specific controls, FedRAMP implications, federal deployment guidance); and a planned AI Safety Evaluations Standard (standard evaluation methodology for frontier AI safety, aligned with the UK AISI evaluation framework, red teaming requirements for high-capability models, and disclosure requirements for dangerous capabilities).

## Future Control Priorities

Security control categories that don't formally exist yet but are coming: AI-to-AI authentication standards (no formal standard today for how agents authenticate each other; expect PKI-based agent identity certificates similar to TLS for websites, via IETF/NIST); AI behavioral contracts (no formal specification for expected agent behavior today; expect machine-readable behavioral specifications, following initiatives like an "Agent Behavior Spec" and formal verification, enabling automated compliance testing); an AI model liability framework (today it's unclear who is liable when an agent causes harm; expect a regulatory framework assigning liability across AI action chains, making audit trail requirements legally mandated, via EU AI Act Article 65+ and NIST policy work); continuous AI testing standards (no standardized ongoing-testing methodology today; expect a NIST AI 100-X on evaluation and testing cadence, enabling monthly adversarial evaluation against standardized test suites); and AI incident response standards (NIST SP 800-61 doesn't cover AI-specific incidents today; expect an SP 800-61r3 update addressing what to do when SOC AI is compromised and what disclosure is required).

Enterprise preparation: now (2026), establish AI governance ahead of regulation, implement NIST AI 100-2 controls before they become legally required by 2027-2028, build immutable audit trails ahead of their EU AI Act-driven spread, and start PQC migration planning for model signing and AI API authentication. By 2027, implement agent cryptographic identity, begin behavioral specification work, deploy synthetic content detection ahead of mandate, and participate in standards development via NIST/ISO/IETF comment processes. By 2028, complete PQC migration for AI authentication, have a tested AI incident response capability, run automated compliance testing against published standards, and fold AI behavioral audits into the annual security program. Organizations implementing NIST AI 100-2/100-4/CAISI controls now will have the strongest posture once these become mandatory through the EU AI Act, the NIST AI RMF (already adopted across US federal agencies), ISO 42001, and pending sector-specific regulation — early movers gain institutional knowledge before compliance pressure, influence over standard development, competitive differentiation in regulated markets, and lower retroactive compliance cost.

## Standards Watch List

| Source | Resource | Update Frequency |
|--------|---------|-----------------|
| NIST | csrc.nist.gov/projects/ai | Monthly |
| CAISI | nist.gov/artificial-intelligence | Quarterly |
| MITRE | atlas.mitre.org | Monthly |
| OWASP | owasp.org/www-project-top-10-for-large-language-model-applications | Quarterly |
| EU AI Office | digital-strategy.ec.europa.eu/ai | Monthly |
| UK AISI | gov.uk/government/organisations/ai-safety-institute | Monthly |
| Anthropic | anthropic.com/research | Ongoing |
| IAPP | iapp.org/resources/article/ai-governance-frameworks | Quarterly |

## Related

- [NIST AI Standards Part 6: Implementation Checklist](06-part-06-implementation-checklist.md)
- [NIST AI Standards Part 1: NIST AI 100-2 Adversarial ML](01-part-01-nist-ai-100-2-adversarial-ml.md)
- [NIST AI Standards Part 3: CAISI Agentic AI Security](03-part-03-caisi-agentic-ai.md)
