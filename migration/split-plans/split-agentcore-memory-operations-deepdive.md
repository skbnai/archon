# Split Plan: AgentCore Memory Operations Deep Dive

**Source:** `/workspace/knowledge-docs/docs/cloud-platforms/aws/AgentCore_Memory_Operations_DeepDive.md` (3645 words)

**Reason:** Word count exceeds guide doc_type cap (2000 words)

## Split Boundary

**Part 1 (Main):** `docs/platforms/17-agentcore-memory-operations-deepdive.md`
- Source lines: 1–195
- Sections: 1 (Metadata Options), 2 (Streaming Use Case), 3 (Batch Use Case)
- Content: CreateEvent metadata fields, ListEvents filters, Kinesis real-time delivery architecture, BatchCreate/Update/Delete APIs, payload types, consumer patterns
- Target word count: ~1400 words

**Part 2 (Supplementary):** `docs/platforms/parts/17-agentcore-memory-operations-deepdive-part2.md`
- Source lines: 196–500
- Sections: 4 (Issues & Fixes by Phase), 5 (Unit Testing), 6 (Evaluation & Retirement), 7 (Cleanup Strategies)
- Content: PoC-to-production troubleshooting, mock patterns and test matrix, PII/isolation/erasure tests, strategy health evaluation, shadow evaluation, retirement patterns, TTL sweep, GDPR erasure workflows
- Target word count: ~2245 words

## Mapping

| Section | Part | Title |
|---------|------|-------|
| 1 | 1 | Metadata Options — Events, Records & Retrieval Filters |
| 2 | 1 | Streaming Use Case — Kinesis Real-Time Change Notifications |
| 3 | 1 | Batch Use Case — BatchCreate / Update / Delete Memory Records |
| 4 | 2 | Issues, Root Causes & Fixes — By Development Phase |
| 5 | 2 | Unit Testing — Mocks, Test Matrix & Full Test Code |
| 6 | 2 | Evaluation Metrics, Retirement Criteria & Strategy Switching |
| 7 | 2 | Cleanup Strategies — Namespace Purge, TTL, Erasure & Scheduler |

## Navigation

- Part 1 ends with: "See Part 2 (docs/platforms/parts/17-agentcore-memory-operations-deepdive-part2.md) for production operations: troubleshooting, unit testing patterns, evaluation metrics, and cleanup strategies..."
- Part 2 begins with: "Continuation from Part 1 (Sections 1–3). Covers production operations: troubleshooting by phase, comprehensive test patterns, strategy evaluation, and cleanup workflows."
- Topic ID: Both parts share `agentcore-memory-operations-deepdive`
- Part 1 is canonical (`topic_id: agentcore-memory-operations-deepdive`)
- Part 2 uses `topic_id: agentcore-memory-operations-deepdive-part2` and `supersedes: []`
