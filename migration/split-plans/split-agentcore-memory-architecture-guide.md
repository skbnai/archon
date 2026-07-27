# Split Plan: AgentCore Memory Architecture Guide

**Source:** `/workspace/knowledge-docs/docs/cloud-platforms/aws/AgentCore_Memory_Architecture_Guide.md` (~8,820 words body, 18 numbered sections + 4 appendices)

**Reason:** Word count exceeds guide doc_type cap (2600 words hard cap); 4-way split used (same approach as K8s Handbook Parts 1, 4, and 12).

## Split Boundary

**Part 1 (Main):** `docs/platforms/15-agentcore-memory-architecture-guide.md`
- Source: Sections 1–5 through §5.1 (What's New Release Timeline, Executive Summary, AgentCore Architecture Core Concepts, Memory Types Complete Taxonomy, Conversation History Sidebar Architecture intro + "How Claude/ChatGPT Build Their Sidebars")
- Content: the 2025–2026 AgentCore release timeline, the executive summary dimension table, the memory resource/events/namespace model and five design principles, the microVM session lifecycle (Feb 2026 stateful runtime), the memory lifecycle flow, short-term/long-term/episodic memory and persistent session storage, the retention period decision matrix, and the sidebar architecture framing (how Claude/ChatGPT build sidebars)
- Note: §5.2–5.4 (Three Layers of Session State, Reimagining the Sidebar on AgentCore, Session Browser reference architecture) were moved to the start of Part 2 to keep Part 1 under the word cap (initial draft measured 2997 counted words; moving these three subsections, 621 source words, brought it to 2562)

**Part 2 (Supplementary):** `docs/platforms/parts/15-agentcore-memory-architecture-guide-part2.md`
- Source: Section 5 continued (§5.2–5.4: Three Layers of Session State, Reimagining the Sidebar on AWS AgentCore, Session Browser reference architecture) + Sections 6–10 (Session Resume — The Full Lifecycle, Multi-Agent Memory Patterns, Memory Processors & Extractors, Framework Comparison, Memory & Token Optimisation Strategies)
- Content: the three layers of session state and the complete AWS sidebar reference architecture (DynamoDB session catalog schema), the four session-resume scenarios (warm start, idle-timeout-STM-alive, cold reconstruction, both-unavailable) and the resume decision tree, multi-agent memory pattern trade-offs (isolated namespace, shared pub/sub, multi-write hub-and-spoke, transaction ledger), memory processors/extractors, a framework comparison, and token/memory optimisation strategies

**Part 3 (Supplementary):** `docs/platforms/parts/15-agentcore-memory-architecture-guide-part3.md`
- Source: Section 10 (Memory & Token Optimisation Strategies, moved from the end of Part 2 to stay under cap) + Sections 11–18 (Strands Framework Best Practices, EU Banking/GDPR/Regulatory Compliance, Security/Policy/Threat Model, Cost Analysis & Optimisation, Project Journey PoC to Production, Evaluation Framework, Terraform IaC Reference, Risks/Recommendations/Decision Guide)
- Content: memory/token optimisation strategies, the four mandatory Strands hooks (PII redaction, memory retrieval, memory persistence, consent check) and sub-agent skills, EU banking/GDPR compliance requirements, the security/threat model, cost anti-patterns and best practices, the four-phase PoC-to-production journey, the evaluation framework, a Terraform IaC reference, and final risk/recommendation guidance
- Note: Part 2's initial draft measured 2760 counted words; the Memory & Token Optimisation Strategies section (205 source words) was moved here to bring Part 2 to 2571

**Part 4 (Supplementary):** `docs/platforms/parts/15-agentcore-memory-architecture-guide-part4.md`
- Source: Appendices A–D (Complete Resume Orchestrator, Session Catalog API, Warm Pool & Session Close Workflow, Complete Test Suite)
- Content: the full Python resume orchestrator covering all four resume scenarios, Lambda handlers for the session catalog API (list/create/fork/delete with GDPR Art. 17 cascade), the warm-pool heartbeat and EventBridge session-close workflow, and the test suite (resume scenarios, PII redaction zero-tolerance tests, namespace isolation tests, resume quality metric)

## Source-quality notes (converted-pdf artifacts fixed during migration)

- This source has a distinct and more severe PDF-conversion artifact than the K8s Handbook: several section headings were scrambled by the PDF's font-kerning/text-extraction pass, splitting words across stray bold/underline markup — e.g. `Executive Summar** **<u>y</u>` (→ "Executive Summary"), `Memor T es — Com lete Taxonom** **<u>y yp p y</u>` (→ "Memory Types — Complete Taxonomy"), `Multi-A ent Memor Patterns` (→ "Multi-Agent Memory Patterns"), `Memor Processors & Extractors` (→ "Memory Processors & Extractors"), `Memor & Token O timisation Strate ies` (→ "Memory & Token Optimisation Strategies"), `Cost Anal sis & O timisation` (→ "Cost Analysis & Optimisation"). All headings were reconstructed to their evident intended text; no new claims were introduced, only de-scrambling of letters that were clearly split by the extraction pass (confirmed against the parallel, correctly-spelled Table of Contents entries earlier in the same source document).
- Numerous flattened multi-line JSON/Terraform/Python/DynamoDB-schema blocks reconstructed into properly line-broken fenced blocks throughout all four parts.
- Several tables were reconstructed from a PDF-conversion pattern where the header row appears as plain bold text immediately above a table missing its own header (e.g. Section 3.3's MicroVM lifecycle table, Section 3.4's memory lifecycle flow numbered steps) — merged into clean tables or ordered lists per the evident structure.
- No content-loss (heading-then-nothing) artifacts were found; all sections and appendices retained their body text.
- Appendix A's `_scenario_b`/`_scenario_c`/`_scenario_d` methods were the most severely mangled code in the source: the PDF conversion mixed inline backtick-wrapped code fragments with runs of stray capital "I" characters (e.g. `IIIIIIIIIIIIIIIII`) standing in for corrupted scenario-comment dividers, and multiple Python function bodies were concatenated onto single run-on lines. Reconstructed as three separate, properly indented methods with the evident logic preserved (verified against the parallel, correctly-formatted `SessionStatusDetector`/`WarmPool`/Lambda-handler code elsewhere in the same appendix set, which used consistent naming and control flow that made the intended structure of the mangled sections unambiguous) — no new logic was invented, only re-formatted.

## Navigation

- Each part ends with a pointer to the next; Parts 2–4 also link back to Part 1.
- Topic ID: all four parts share the `agentcore-memory-architecture-guide` topic family.
- Part 1 is canonical (`topic_id: agentcore-memory-architecture-guide`).
- Parts 2–4 use `topic_id: agentcore-memory-architecture-guide-part{2,3,4}`, all `supersedes: []` (Part 1 carries the supersedes entry).
