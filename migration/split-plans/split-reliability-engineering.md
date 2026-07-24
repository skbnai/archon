# Split Plan: reliability-engineering

**Source:** docs/agentic-ui/reliability-engineering.md (8962 words)

**Split Strategy:** 3-way split at natural failure/reliability mechanism boundaries

## Split Map

| Part | Target Path | Topic ID | Source Sections | Line Range | Word Count |
|------|------------|----------|-----------------|-----------|-----------|
| 1 | docs/agentic-systems/agentic-ui/16-reliability-engineering.md | reliability-engineering | Sections 1-4 (Why Different + SLA/SLO + Fault Tolerance + Degradation) | 14-556 | ~2900 |
| 2 | docs/agentic-systems/agentic-ui/parts/16-reliability-engineering-part2.md | reliability-engineering-part2 | Sections 5-9 (Retry + Checkpoint + Saga + Conversation Recovery + Streaming) | 557-1069 | ~2980 |
| 3 | docs/agentic-systems/agentic-ui/parts/16-reliability-engineering-part3.md | reliability-engineering-part3 | Sections 10-16 (Offline + Multi-Region + Chaos + Error Budget + Scorecard + Incident Response + Anti-patterns) | 1070-1502 | ~3082 |

## Split Rationale

The reliability-engineering document covers production-grade reliability patterns for agentic applications. The split organizes by reliability concern:

**Part 1** establishes the unique challenges of agentic reliability (why traditional patterns don't work) and foundational patterns: SLA/SLO definition, circuit breaker fault tolerance, and graceful degradation ladders. This covers "what can fail and how to detect it."

**Part 2** covers recovery patterns: retry strategies with budget limits, checkpointing for resumable workflows, saga compensation for multi-step operations, conversation recovery after mid-stream failures, and streaming reliability with Last-Event-ID. This covers "how to recover when failures occur."

**Part 3** covers advanced patterns and operations: offline mode, multi-region failover, chaos engineering validation, error budget management, reliability scorecard, incident response runbooks, and 25 reliability anti-patterns to avoid. This covers "how to run reliably at scale."

Each part is self-contained while building on concepts from earlier parts.

## Supersedes

The three parts together completely supersede the original monolithic document at `docs/agentic-ui/reliability-engineering.md`.

## Verification

- Combined word count: ~2900 + ~2980 + ~3082 = ~8962 (100% word retention)
- All code examples preserved (circuit breaker implementations, retry budget, idempotency store, checkpoint schema, DLQ pattern, chaos middleware)
- All tables and matrices intact (SLI definitions, degradation levels, timeout hierarchy, compensation actions, multi-region architectures, chaos experiments)
- All diagrams converted from ASCII box-drawing to text descriptions
- All Python and TypeScript code examples included completely
- Runbook templates and checklists preserved
- 25 anti-patterns with impact assessment fully included
