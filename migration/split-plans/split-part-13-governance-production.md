# Split Plan: part-13-governance-production

## Overview
Source file `../knowledge-docs/docs/multimodal-ai/part-13-governance-production.md` (5981 words) split into 2 parts to fit within reference-architecture doc_type word cap.

## Split Strategy
Logical split at "A.R.T. Framework Applied to Multimodal Governance & Production" section to separate foundational governance concepts from advanced framework application.

## Part 1: 13-part-13-governance-production.md
**Topic ID:** part-13-governance-production
**Word Count:** 5,376 words
**Doc Type:** reference-architecture
**Sections:**
- Enterprise AI Governance Framework (pillars: accountability, transparency, control, audit)
- Governance Operating Model (4 defined roles)
- Policy-as-Code for Multimodal AI (OPA Rego examples, Cedar, ABAC vs RBAC)
- Approval Workflows and Human-in-the-Loop Governance (change approval, inference approval tiers, SLA management)
- Policy-as-Code Implementation (OPA policies, Cedar alternatives, testing)
- Audit Logging and Chain of Custody (what to log, immutable logs, retention requirements)
- Risk Scoring and Kill Switches (risk scoring components, automated thresholds, kill switch architecture)
- Production Engineering (streaming inference, batch inference, edge inference, air-gapped environments)
- GPU Infrastructure and Scheduling (GPU selection, CUDA memory, multi-GPU inference, autoscaling, fractional GPU/MIG)
- Large Media Processing Architecture (100-hour video archives, state recovery, distributed inference frameworks, queue architecture)
- Caching Architecture (embedding cache, inference cache, KV cache, CDN-level caching)

**Includes:** Enterprise governance framework mermaid diagram

## Part 2: 13-part-13-governance-production-part2.md
**Topic ID:** part-13-governance-production-part2
**Word Count:** 721 words
**Doc Type:** reference-architecture
**Sections:**
- Governance Approval Workflow (complete flowchart with risk tiers)
- Production Batch Processing Architecture (detailed system diagram with error handling)
- A.R.T. Framework Applied to Multimodal Governance & Production (Risk pillar, Tenacity pillar, Agility pillar implementation)
- Related References (links to A.R.T. Framework, observability, compliance, security, cloud platform guides)

**Includes:** A.R.T. Framework pillars mermaid diagram

## Metadata
- **Source:** ../knowledge-docs/docs/multimodal-ai/part-13-governance-production.md
- **Original Word Count:** 5,981 words
- **Combined Word Count:** 6,097 words
- **Retention Ratio:** 102.0%
- **Date Created:** 2026-07-24
- **Frontmatter:** Properly formatted with topic_id, domain, doc_type (reference-architecture with mermaid diagrams), supersedes, last_reviewed
- **Mermaid Diagrams:** 2 required architecture diagrams included (governance framework, A.R.T. pillars)

## Navigation Links
- Part 1 links to Part 2 via split nav link at end
- Part 2 links back to Part 1 via split nav link at end
- Format: `pathname:///archon/agentic-systems/multimodal/<subpath>`
