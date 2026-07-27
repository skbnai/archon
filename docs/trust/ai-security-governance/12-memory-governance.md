---
title: "Memory Governance"
doc_type: guide
domain: trust
status: current
topic_id: memory-governance
last_reviewed: 2026-07-27
maturity: practitioner
supersedes: [docs/ai-security-governance/deep-mind/Part08_Memory_Governance.md]
tags: [ai-security, memory-governance, deepmind, gdpr]
covers_version: "as of 2026"
---

Memory lifecycle management, classification, access control, integrity verification, retention policies, poisoning detection, and regulatory compliance for enterprise AI agent memory.

## Memory as a Regulated Enterprise Asset

Agent memory is not merely a technical implementation detail — it is a regulated enterprise asset with legal, compliance, and security implications that match or exceed those of traditional data stores. Memory systems contain: user personal data (GDPR/CCPA scope), business decision context (SOX/financial regulations scope), confidential business information (IP and trade secret scope), and potentially privileged communications (legal privilege considerations). Treating memory as an afterthought is a critical enterprise risk.

**Regulatory reality check:** Under GDPR Article 17 (Right to Erasure), if an agent's episodic memory contains PII about a data subject, that subject can demand deletion of that memory. This requires memory systems to support granular, attributable deletion capabilities — not just bulk purge. Memory governance is therefore a legal requirement, not merely a security best practice.

## Memory Type Taxonomy

**Working memory** is the agent's active context window — the information in scope for the current reasoning step. It is ephemeral by nature, existing only for the duration of an inference call. However, working memory is the primary vector for prompt injection because it directly influences model outputs. Governance focuses on controlling what enters working memory from external sources.

**Working memory controls:**

- Content classification: all items entering working memory tagged with trust level and data classification.
- Size limits: enforce maximum context size to prevent context flooding attacks.
- Content filtering: scan for injection patterns before inclusion in working memory.
- Source attribution: every item in context tagged with its origin for audit purposes.
- Sensitive data masking: PII and secrets detected and masked before entering model context.

**Long-term memory systems:**

| Type | Content | Storage | Scope | Access Control | Retention |
|---|---|---|---|---|---|
| Episodic Memory | Records of specific past interactions and events | Vector DB + structured metadata | Agent instance | ABAC by agent instance + data classification | 90 days default; configurable |
| Semantic Memory | Factual knowledge and learned concepts | Vector DB (dedicated namespace) | Agent type | Agent type read; human write only | Aligned with knowledge validity period |
| Procedural Memory | How-to knowledge, workflows, learned strategies | Structured DB with versioning | Agent type | Agent type read; ops team write | Version-controlled; indefinite |
| Organizational Memory | Shared enterprise knowledge across agents | Enterprise knowledge graph | Organization | Strict ABAC by data classification | Indefinite with periodic review |
| User Context Memory | Preferences and history for individual users | Encrypted user-scoped store | User session | User consent required; strict access | User-defined or regulatory max |

## Memory Access Control Architecture

**Memory authorization model.** Memory access control must be enforced by a Memory Governor — a dedicated service that intermediates all memory reads and writes. The agent never accesses memory directly; all memory operations go through the Governor, which applies ABAC policies based on the agent's identity, task scope, and the classification of the memory content.

| Operation | Authorization Required | Additional Controls |
|---|---|---|
| Read working memory | Task identity token | None (ephemeral) |
| Read own session memory | Session identity token matching memory's session ID | Anomaly alert if reading old sessions |
| Read own episodic memory | Agent type identity + data classification check | Rate limiting; audit log |
| Read org shared memory | Agent type identity + ABAC policy evaluation | Data classification enforcement; audit |
| Write session memory | Session identity token | Content scanning before write |
| Write episodic memory | Agent type identity + content safety check | Human approval for sensitive content |
| Write org shared memory | Human principal approval required | Content review workflow; versioning |
| Delete any memory | Human approval + compliance check | Retention policy verification; audit trail |

## Memory Integrity and Provenance

**Content integrity verification.** Memory content can be tampered with at rest (database compromise), in transit (MITM), or through authorized but malicious writes (memory poisoning by a compromised agent). Integrity verification must detect all three attack vectors.

- **Write-time Hashing:** SHA-256 hash of each memory entry computed and stored alongside content; any modification invalidates the hash.
- **Merkle Tree Integrity:** memory collections organized in Merkle trees; a single hash covers the entire collection; efficient tamper detection.
- **Digital Signatures:** sensitive memory entries signed by the agent's private key at write time; the signature is verifiable by any reader.
- **Read-time Verification:** the Memory Governor verifies hash/signature on every read; tampered entries are returned as null with an alert.
- **Provenance Chain:** each memory entry carries: writing agent identity, delegating human identity, task ID, timestamp, and parent memory ID if derived.

**Memory poisoning detection** operates at write time, retrieval time, and through periodic batch analysis. Write-time detection prevents obviously malicious content from entering memory. Retrieval-time detection identifies poisoned content before it influences the agent. Batch analysis detects slow, gradual poisoning campaigns that evade per-write detection.

| Detection Layer | Method | Timing | Latency |
|---|---|---|---|
| Write-time semantic scan | Classify content for injection patterns, factual anomalies | Synchronous pre-write | 50-200ms |
| Write-time drift check | Compare against existing memory distribution; flag outliers | Synchronous pre-write | 100ms |
| Retrieval-time consistency | Verify retrieved content is consistent with cross-references | Synchronous on retrieval | 20-100ms |
| Batch statistical analysis | Analyze memory corpus for coordinated poisoning campaigns | Async daily/weekly batch | Hours |
| Ground truth comparison | Periodically verify memory facts against authoritative sources | Async weekly | Hours |
| Agent behavior correlation | Correlate memory content changes with agent behavior changes | Async real-time | Minutes |

## Memory Lifecycle and Retention

**Memory lifecycle stages:**

1. **Creation:** memory entry written; hash computed; provenance recorded; classification assigned.
2. **Active Use:** entry retrieved and used in agent context; access logged; integrity verified on each access.
3. **Review:** periodic content review for accuracy, relevance, and compliance; human review for sensitive entries.
4. **Archival:** entries past the active use period moved to cold storage; retrieval still possible but slower.
5. **Deletion:** cryptographic deletion (key rotation) for sensitive entries; standard deletion for others; audit record preserved.

**Regulatory retention mapping:**

| Regulation | Scope | Retention Requirement | Memory Implication |
|---|---|---|---|
| GDPR (EU) | EU personal data | Minimum necessary duration; Right to Erasure | PII memory must be attributable and deletable per data subject |
| CCPA/CPRA (California) | California resident PII | Right to delete; data minimization | Same as GDPR; US state law additive |
| SOX (US) | Financial records | 7 years minimum | Financial decision context memory retained 7 years in immutable store |
| HIPAA (US) | Health information | 6 years from creation | Any PHI in agent memory subject to HIPAA retention and security rules |
| ISO 27001 | Business records | Organization-defined | Memory retention policy must be documented and audited |
| EU AI Act | High-risk AI decisions | Defined per risk category | Decision context and reasoning traces for high-risk agents must be retained |

## Related

- [AI Authorization Architecture](11-ai-authorization.md)
- [Tool Governance](13-tool-governance.md)
- [AI Control Series Overview](01-ai-control-series-overview.md)
