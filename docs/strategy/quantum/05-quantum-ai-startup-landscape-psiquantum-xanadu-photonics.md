---
title: "Quantum AI Startups: PsiQuantum & Xanadu (Photonics)"
doc_type: research-report
domain: strategy
status: current
canonical: true
topic_id: quantum-ai-startup-landscape-part3
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
  - psiquantum
  - xanadu
  - photonics
sources:
  - url: https://www.psiquantum.com/news-import/psiquantum-1b-fundraise
    title: "PsiQuantum $1B Series E Fundraise"
    tier: 1
    retrieved: 2026-07-19
  - url: https://www.sec.gov/Archives/edgar/data/0002097163/000121390026042080/ea0285152-20f_xanadu.htm
    title: "Xanadu 20-F SEC Filing"
    tier: 1
    retrieved: 2026-07-19
---

# Quantum AI Startups: PsiQuantum & Xanadu (Photonics)

Continuing from parts 1-2 (IonQ, D-Wave, Quantinuum, Multiverse, QuEra, Rigetti), this section covers the photonic modality leaders betting that semiconductor manufacturing will be the path to millions of qubits.

## PsiQuantum: Silicon Photonics & Fault-Tolerant Infrastructure Bet

**$1B Series E (Sept 2025) · $7B valuation · Led by BlackRock/Temasek/Baillie Gifford · ~$2.3B total raised · ~$1B Australia government deal · Pre-commercial[^1]**

### The Problem

Current qubit modalities requiring cryogenic cooling—superconducting, trapped-ion, neutral atom—face a fundamental scaling ceiling. Millions of physical qubits cannot be built by stacking more cryostats.

### The Solution

Photons don't interact with their environment like electrons. Photonic qubits can operate at room temperature. More critically, photonic chips manufactured using silicon photonics on industry-standard full-size wafers means the path to millions of qubits runs through existing semiconductor supply chains.

### Key Technology

- **Omega chipset** (Feb 2025) — Purpose-built photonic quantum computing chipset at GlobalFoundries; single-photon sources, superconducting detectors, optical switches; commercial semiconductor yields
- **Fusion-Based Quantum Computing (FBQC)** — Modular architecture enabling scale-up without connectivity constraints
- **GlobalFoundries partnership** — Production at GF Fotonix; industry-standard wafers; yields matching semiconductors

### Getting Access

**PsiQuantum is NOT yet commercially accessible** — no cloud service, developer API, or hardware preview as of July 2026.

| Channel | Access Type | Status |
|---------|------------|--------|
| **Government/strategic** | Direct relationship | Active — ~$1B Australian/Queensland investment |
| **US government/DARPA** | Partnership-based research | Active |
| **Public developer access** | None yet | Follow psiquantum.com for announcements |

### Big Wins

- $1B Series E (Sept 2025) funding at $7B valuation—one of largest quantum rounds in history[^1]
- Omega chipset demonstrated all components required for fault-tolerant photonic computing
- Australian government ~$1B commitment—largest single government quantum hardware infrastructure investment globally

### Architect Takeaway

Track Omega chipset production yields at GlobalFoundries as leading indicator for photonic modality timeline to accessible systems. If yields match classical semiconductor yields, timeline to photonic quantum access compresses significantly.

---

## Xanadu: Networked Photonic Computing & PennyLane Ecosystem

**$4.6M 2025 revenue[^2] · $2.8M Q1 2026 · $276M cash (post-SPAC-close, Mar 2026)[^3] vs. $16.2M FY2025 year-end[^3] · XNDU (public) · PennyLane: 35K users**

### The Problem

Existing quantum hardware requires specialized cryogenic infrastructure. Algorithms written for IBM don't run on IonQ without rewriting, creating vendor lock-in from day one.

### The Solution

Two-track strategy: build photonic quantum hardware operating at room temperature, and grow PennyLane as hardware-agnostic QML standard.

### Key Products

- **Aurora** (Jan 2025) — World's first networked, modular photonic quantum computer: 12 qubits across 4 racks, 35 photonic chips, 13 km fiber optics; room temperature operation; cross-rack entanglement demonstrated
- **PennyLane** (open source) — Hardware-agnostic quantum ML framework; 35,000 users, 200,000 monthly downloads; runs on IBM, Google, AWS Braket, IonQ, Rigetti, QuEra, Xanadu backends
- **Strawberry Fields** — Photonic quantum programming library

### Getting Access

| Channel | Access Type | Best For |
|---------|------------|---------|
| **PennyLane** | Free, open source | First entry point for ALL QML work |
| **Xanadu Cloud** | Account registration; simulator free, hardware by request | Direct access to photonic platform |
| **AWS Braket (Borealis)** | Pay-per-task; Gaussian Boson Sampling | Photonic GBS experiments |

### Big Wins

- Aurora is first demonstration of networked, modular photonic quantum computing
- PennyLane ecosystem with 35,000 users—durable competitive moat independent of hardware competition
- Public listing (2026) with $272.5M cash runway
- DARPA Stage B benchmarking results provide independent validation

### Architect Takeaway

Use PennyLane as default QML starting point regardless of eventual hardware vendor choice—decouples algorithm development from hardware commitment. Monitor DARPA Stage B results as independent validation of photonic performance.

---

## Cross-Photonic Pattern: Semiconductor Manufacturing Is the Unlocking Constraint

Both PsiQuantum and Xanadu converge on shared thesis: path to millions of qubits runs through semiconductor fabs, not cryogenic engineering. If fab yields match classical semiconductor yields, timeline to commercially accessible photonic quantum computing compresses significantly within 18-24 months.

**Architect Takeaway:** Track Omega chipset yields at GlobalFoundries and Aurora network scaling results as primary leading indicators for photonic QC timeline.

---

## Footnotes

[^1]: PsiQuantum raised $1B Series E funding in September 2025 at a $7B valuation, led by BlackRock, Temasek, and Baillie Gifford, bringing total raised to date to approximately $2.3B. Source: https://www.psiquantum.com/news-import/psiquantum-1b-fundraise (tier 1, retrieved 2026-07-19)

[^2]: Xanadu reported $4.6M 2025 revenue. Source: https://www.sec.gov/Archives/edgar/data/0002097163/000121390026042080/ea0285152-20f_xanadu.htm (tier 1, retrieved 2026-07-19)

[^3]: Xanadu reported $276M cash immediately post-SPAC-close (March 2026) versus $16.2M cash at FY2025 year-end (pre-listing); these are not directly comparable figures reflecting the timing of the public listing. Source: https://www.sec.gov/Archives/edgar/data/0002097163/000121390026042080/ea0285152-20f_xanadu.htm (tier 1, retrieved 2026-07-19)

---

## Related

- [Quantum AI Startups: IonQ & D-Wave](../02-quantum-ai-startup-landscape.md)
- [Quantum AI Startups: Quantinuum, Multiverse, QuEra & Rigetti](04-quantum-ai-startup-landscape-quantinuum-multiverse-quera-rigetti.md)
- [Quantum AI Startups: IQM & Emerging Players](06-quantum-ai-startup-landscape-iqm-emerging-players.md)
---

*Quantum AI Startup Landscape Report. Part 3 of 5.*
