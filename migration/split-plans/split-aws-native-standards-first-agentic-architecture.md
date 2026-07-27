# Split Plan: aws-native-standards-first-agentic-architecture

## Overview
- **Source:** `../knowledge-docs-old/docs/cloud-platforms/aws/AWS_Native_Standards_First_Agentic_Architecture.md` (7828 words)
- **Topic ID:** `aws-native-standards-first-agentic-architecture`
- **Doc Type:** guide (per source frontmatter; word cap 2600/part — kept as `guide` rather than reclassified to `reference-architecture` despite the "Reference Architecture for..." subtitle, since the source's own frontmatter already declares `doc_type: guide` and reclassifying would additionally require a validated Mermaid diagram in every resulting part)
- **Domain:** platforms
- **Note:** "PART 2 — Layered Reference Architecture" (source lines 186-620, ~2878 words) exceeds the cap alone; sub-split at its own `###` layer sub-headings (Layers 1-9) rather than the parent `##` boundary.

## Part 1: Executive Summary through Standards Map
- **Topic ID:** `aws-native-standards-first-agentic-architecture`
- **Target Path:** `docs/platforms/11-aws-native-standards-first-agentic-architecture.md`
- **Content:** Lines 1-286 of source (~2364 words)
- **Sections:** Title/role lenses, TOC, Executive Summary, PART 1 — Architecture Principles & Standards Map (design principles P1-P8, standards-to-AWS-service mapping, anti-lock-in contract), start of PART 2 layered architecture overview through Layer 1 (Client & Experience)

## Part 2: Layered Reference Architecture (Layers 2-6)
- **Topic ID:** `aws-native-standards-first-agentic-architecture-part2`
- **Target Path:** `docs/platforms/parts/11-aws-native-standards-first-agentic-architecture-part2.md`
- **Content:** Lines 287-620 of source (~2198 words)
- **Sections:** Layer 2 (API & Gateway), Layer 3 (Agent Runtime), Layer 4 (Tool & Integration/MCP), Layer 5 (Multi-Agent Coordination/A2A), Layer 6 (Memory & Knowledge)

## Part 3: Layered Architecture close, Memory/Session/Multi-Agent Design, Security & Governance
- **Topic ID:** `aws-native-standards-first-agentic-architecture-part3`
- **Target Path:** `docs/platforms/parts/11-aws-native-standards-first-agentic-architecture-part3.md`
- **Content:** Lines 621-868 of source (~2316 words)
- **Sections:** Layer 7 (Data & Storage), Layer 8 (Observability/OTel), Layer 9 (Security & Governance), PART 3 — Memory, Session & Multi-Agent Design, PART 4 start (Security, Governance & Anti-Lock-In Strategy through 4.1)

## Part 4: Governance mapping through Appendices
- **Topic ID:** `aws-native-standards-first-agentic-architecture-part4`
- **Target Path:** `docs/platforms/parts/11-aws-native-standards-first-agentic-architecture-part4.md`
- **Content:** Lines 869-1133 of source (~966 words)
- **Sections:** 4.2 Governance & Compliance Mapping, 4.3 Anti-Pattern Cross-Reference, 4.4 Portability & Exit-Strategy Design, Appendix: Service & Standards Reference, Appendix: Infrastructure-as-Code Skeleton, Closing Statement

## ASCII Art / Diagram Conversions
None — no box-drawing characters detected in source (layer diagrams are expressed as headed prose/lists, not ASCII art).

## Key Considerations
- No internal cross-links in source requiring rewrite.
- All illustrative code blocks (agent container structure, MCP tool manifest, A2A delegation flow, memory abstraction interface, OTel span attributes, IaC skeleton) preserved verbatim within their assigned part.
- Each part gets a nav-link to the next/previous (1↔2↔3↔4).
