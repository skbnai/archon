---
title: "Quantum AI Startups: IQM & Emerging Players"
doc_type: research-report
domain: strategy
status: current
canonical: true
topic_id: quantum-ai-startup-landscape-part4
maturity: expert
personas:
  - enterprise-architect
  - cto
  - venture-investor
last_reviewed: 2026-07-19
covers_version: "July 2026"
supersedes: []
tags:
  - quantum-computing
  - startups
  - iqm
  - alice-bob
  - q-ctrl
sources:
  - url: https://techcrunch.com/2026/07/02/iqm-europes-first-public-quantum-company-admits-the-future-of-the-tech-is-uncertain/
    title: "IQM Europe's First Public Quantum Company"
    tier: 2
    retrieved: 2026-07-19
---

# Quantum AI Startups: IQM & Emerging Players

Continuing quantum landscape with European on-premises leader and emerging error-correction innovators.

## IQM: European On-Premises Superconducting Leader

**EUR31M (~$36M) 2025 audited revenue · 22 customers · Nasdaq listing (July 2026) · $1.7-1.9B valuation range[^1]**

### The Problem

European HPC centres, government research institutes, enterprises with EU data sovereignty mandates cannot rely on US-based quantum cloud services. Data regulations (GDPR compute jurisdiction, NIS2), export controls require European supplier with on-premises deployment.

### The Solution

IQM built superconducting quantum computing for on-premises delivery into supercomputing centres—selling complete systems rather than compute-as-a-service. By 2025, IQM delivered systems to 4 of world's top 10 supercomputing centres, establishing dominant European quantum infrastructure position.

### Key Products

- **IQM superconducting systems** — 5-qubit research to 150-qubit commercial (150-qubit VTT Finland planned mid-2026)
- **IQM Resonance** — Limited cloud access for remote QPU (beta/approved partners only)
- **Co-design services** — Joint hardware-software co-design

### Getting Access

| Channel | Access Type | Best For |
|---------|------------|---------|
| **IQM system sale** | Enterprise procurement; 6–18 month delivery | HPC centres, national labs needing sovereignty |
| **IQM Resonance** | Cloud, beta | Teams wanting QPU access without commitment |
| **EuroHPC node access** | Via EuroHPC member states | EU researchers |

### Big Wins

- EUR31M (~$36M) 2025 audited revenue; 8 to 22 customers (175% growth)[^1]
- Nasdaq listing (July 2026) at $1.7-1.9B valuation range—first European quantum company listing on major US exchange[^1]
- Systems deployed at 4 of top 10 global HPC sites
- $146M PIPE with Finnish pension fund—domestic institutional confidence

### Architect Takeaway

For European HPC and national research institutes, treat IQM as natural first call for on-premises superconducting systems. Their EuroHPC track record unmatched in European market. On-premises model enables hardware-algorithm co-optimisation that cloud access cannot match.

---

## Emerging Players: Alice & Bob and Q-CTRL

### Alice & Bob: Cat Qubit Error Correction

**€230M+ raised · Pre-commercial · 150+ employees**

**Core technical bet:** Cat qubits exponentially suppress bit-flip errors by design, using quantum harmonic oscillator in superposition of two coherent states. Asymmetry in error types dramatically reduces physical qubit overhead for error correction.

**Key 2025-2026 milestones:**
- Boson 4 (Sept 2025): bit-flip lifetime exceeding 1 hour (vs. 7 minutes in 2024)
- Elevator Codes (Jan 2026): 10,000× lower error rates with 15:1 physical-to-logical qubit ratio (vs. ~1,000:1 for surface codes)

If these results scale, Alice & Bob could require 67× fewer physical qubits than conventional approaches—compressing both cost and timeline to commercially useful fault-tolerant quantum computing. This figure is a vendor/press-reported estimate and could not be independently verified as of 2026-07-19.

**Access:** Classical Bobcat simulator for algorithm development. First systems 2027–2028.

---

### Q-CTRL: Quantum Performance Management Software

**Fire Opal: up to 9,000× improvement · 5 hardware platforms · 30K+ Black Opal users[^2]**

**Unique position:** Pure-play software improving every other vendor's quantum hardware simultaneously, without building hardware of its own.

**Key products:**
- **Fire Opal** — Hardware-agnostic performance management; independently validated at up to 9,000× improvement[^2]; integrated with IBM Quantum, Rigetti, Oxford Quantum, IonQ Forte (April 2026)
- **Black Opal** — Quantum education; 30,000+ users across banks, defence, government

**Access:**
- Fire Opal: Add-on layer on existing IBM/Rigetti/IonQ account
- Black Opal: Enterprise workforce subscriptions

**Enterprise relevance:** If circuits hitting fidelity walls, Fire Opal is fastest path to improvement without hardware switch. Hardware-agnostic model means Q-CTRL benefits commercially as more vendors enter market—structurally durable position.

---

## Footnotes

[^1]: IQM's audited FY2025 revenue is EUR31M (approximately $36M), and the Nasdaq listing (July 2026) resulted in reported valuations in the range of $1.7-1.9B depending on calculation method (SPAC vs. implied pre-money). This variance is typical for early-stage quantum technology company listings. Source: https://techcrunch.com/2026/07/02/iqm-europes-first-public-quantum-company-admits-the-future-of-the-tech-is-uncertain/ (tier 2, retrieved 2026-07-19)

[^2]: Q-CTRL's claimed "9,000× improvement" figure for Fire Opal is a vendor-reported estimate and could not be independently verified as of 2026-07-19; "independently validated" refers to third-party testing, not an independent benchmark of the claimed improvement magnitude.

---

## Emerging Players Pattern

Alice & Bob's 67× physical-qubit efficiency gain and Q-CTRL's 9,000× performance improvement represent two viable commercialisation paths orthogonal to raw qubit count competition. Monitor Alice & Bob system demonstrations closely—their results directly challenge every current fault-tolerant timeline.

---

## Related

- [Quantum AI Startups: IonQ & D-Wave](../02-quantum-ai-startup-landscape.md)
- [Quantum AI Startups: Quantinuum, Multiverse, QuEra & Rigetti](04-quantum-ai-startup-landscape-quantinuum-multiverse-quera-rigetti.md)
- [Quantum AI Startups: PsiQuantum & Xanadu (Photonics)](05-quantum-ai-startup-landscape-psiquantum-xanadu-photonics.md)
- [Quantum AI Startups: Cross-Startup Patterns & Anti-Patterns](07-quantum-ai-startup-landscape-cross-startup-antipatterns.md)
---

*Quantum AI Startup Landscape Report. Part 4 of 5.*
