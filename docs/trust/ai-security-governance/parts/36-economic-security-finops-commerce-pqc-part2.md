---
title: "Economic Security: Quantum-Ready Agent Security (Part 2)"
doc_type: guide
domain: trust
status: current
topic_id: economic-security-finops-commerce-pqc-part2
last_reviewed: 2026-07-27
maturity: practitioner
supersedes: [docs/ai-security-governance/security/05-Economic-Security-FinOps-Commerce-PQC.md]
tags: [ai-security, post-quantum-cryptography, nist, spiffe]
covers_version: "as of 2026"
---

NIST's finalized post-quantum cryptographic standards, the practical migration constraints for agent infrastructure, and the post-quantum agent fabric design specification.

## Why Post-Quantum Readiness Belongs in an Agentic Security Program

Post-quantum cryptography belongs in an agentic security program for a reason specific to this domain, not as a generic cryptography-hygiene item: the identity and trust infrastructure this entire program is built on — SPIFFE SVIDs, signed Agent Cards, AP2 mandates — is precisely the category of cryptographic material with long operational lifetimes and high replay/forgery value that harvest-now-decrypt-later attacks are designed to exploit. An adversary recording today's signed Agent Card exchanges or mandate signatures, intending to forge or decrypt them once cryptographically relevant quantum computers exist, is a realistic threat model for infrastructure expected to remain in service for years.

## NIST Post-Quantum Standards — Current Status

NIST finalized its first three post-quantum cryptographic standards in August 2024, concluding an eight-year evaluation process, and the regulatory and infrastructure environment has moved decisively since:

| Standard | Algorithm | Function | Status |
|---|---|---|---|
| FIPS 203 | ML-KEM (formerly Kyber) | Lattice-based key encapsulation (key exchange) | Finalized; already deployed in hybrid X25519+ML-KEM-768 configurations in production browsers and major CDNs; integrated into OpenSSL 3.5 |
| FIPS 204 | ML-DSA (formerly Dilithium) | Lattice-based digital signatures | Finalized; the primary candidate for signing agent identity credentials and payment mandates going forward |
| FIPS 205 | SLH-DSA (formerly SPHINCS+) | Hash-based digital signatures (stateless, conservative fallback) | Finalized; relies solely on hash-function security rather than lattice assumptions — recommended as a crypto-agility fallback alongside ML-DSA rather than a primary scheme, given its substantially larger signature sizes |
| HQC | Hamming Quasi-Cyclic | Alternative, non-lattice key encapsulation mechanism | Selected March 2025 as a structurally independent backup to ML-KEM; draft publication expected 2026, full standardization expected 2027 |

NIST's draft guidance (IR 8547) calls for deprecating quantum-vulnerable algorithms — RSA, ECDSA, EdDSA, DH, and ECDH — by 2030, with full retirement by 2035; the NSA has separately mandated post-quantum capability for national security systems by 2025, moving to exclusive PQC use by 2035. These are not distant timelines relative to the operational life of identity and payment infrastructure being architected now.

## Practical Constraints

Post-quantum migration is not a drop-in algorithm swap, and agent infrastructure has specific exposure to the practical constraints involved. ML-KEM operations on resource-constrained edge or embedded inference hardware run roughly two orders of magnitude slower than on server-class CPUs, and memory requirements increase two-to-fivefold compared to classical algorithms — directly relevant for any agent runtime architecture deployed to edge inference or constrained sandboxed environments rather than full server-class compute. Signature sizes also grow substantially: ML-DSA signatures run roughly 2,400-4,600 bytes and SLH-DSA signatures 7,800-49,900 bytes, versus a few hundred bytes for classical ECDSA — a material consideration for any high-frequency signing operation, such as per-task mandate signing under AP2 or per-request SPIFFE SVID issuance at agent-population scale.

Crypto-agility — the capability to rotate cryptographic algorithms quickly without a hard-coded dependency on any single scheme — is the operational property that determines whether an organization can actually respond to a future cryptanalytic break, and is explicitly identified by current research as the binding constraint, more than any single algorithm choice. Protocols and infrastructure that hard-code a specific algorithm, or that require firmware-level updates to change it, cannot pivot within any relevant response timescale.

## Post-Quantum Agent Fabric — Design Specification

**Hybrid cryptography as the default, not pure post-quantum.** Combine classical (X25519/ECDSA) and post-quantum (ML-KEM/ML-DSA) algorithms in every new identity and transport implementation, following the same hybrid pattern already in production for TLS; this hedges against both a cryptanalytic break in the new PQC algorithms (still a less battle-tested mathematical foundation) and the known vulnerability of classical algorithms to a future quantum adversary.

**PQC-ready identity substrate.** Extend the SPIFFE/SPIRE trust domain to issue hybrid-signed SVIDs as the PQC ecosystem in SPIFFE's own tooling matures, rather than waiting for a wholesale identity-infrastructure replacement once quantum risk becomes acute.

**PQC-ready payment mandates.** Track the FIDO Alliance Payments Technical Working Group's post-quantum profile for AP2 directly, and plan for ML-DSA-signed mandates as the natural successor to current classical signing schemes given the multi-year operational lifetime of payment-authorization infrastructure.

**Hybrid TLS everywhere agents communicate.** Apply hybrid X25519+ML-KEM TLS configurations to all MCP and A2A gateway transport as the default for any new gateway deployment, consistent with the pattern already standard in major browsers and CDNs.

**Crypto-agility as an explicit architecture requirement.** Any component issuing or verifying agent identity, signing Agent Cards, or signing payment mandates must support algorithm negotiation/rotation without a hard dependency baked into firmware or an unupgradable protocol version — evaluated as a first-class procurement and architecture-review criterion alongside the functional requirements for any new identity, MCP, or A2A infrastructure component.

**Where this sits on the priority list.** Post-quantum readiness is a multi-year migration, not a near-term deliverable, and should not compete for budget against identity, MCP, A2A, and governance priorities that address active, currently-exploited risk. The correct near-term action is architectural: ensure every new identity, MCP, A2A, and payment-mandate component procured or built from this point forward supports crypto-agility and hybrid algorithms, so the eventual PQC migration is a configuration change rather than a forklift replacement of infrastructure being built today.

## Related

- [Economic Security: Agent FinOps & Autonomous Commerce (Part 1)](../36-economic-security-finops-commerce-pqc.md)
- [Identity/MCP/A2A Security Blueprint](../34-identity-mcp-a2a-security-blueprint.md)
- [Identity for AI Agents](../10-identity-for-ai-agents.md)
