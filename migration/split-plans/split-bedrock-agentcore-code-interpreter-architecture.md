# Split Plan: Bedrock AgentCore Code Interpreter Architecture

**Source:** `/workspace/knowledge-docs/docs/cloud-platforms/aws/bedrock-agentcore-code-interpreter-architecture.md` (~11,558 words, `source_type: native-md`, 11 numbered sections + an unnumbered ADR appendix)

**Reason:** Word count exceeds guide doc_type cap (2600 words hard cap); 5-way split used (same approach as the AgentCore Memory Architecture Guide).

## Split Boundary

**Part 1 (Main):** `docs/platforms/19-bedrock-agentcore-code-interpreter-architecture.md`
- Source: Sections 1–2 (Executive Summary, Architecture Deep Dive)
- Content: problem statement, strategic decision to use Code Interpreter as the compute primitive, capability/technology-stack tables, risk-adjusted architecture posture; the logical architecture (orchestration/sandbox/memory/persistence planes), the 9-step ReAct tool-invocation lifecycle, the session-based execution model, and the Strands framework agent-definition pattern

**Part 2 (Supplementary):** `docs/platforms/parts/19-bedrock-agentcore-code-interpreter-architecture-part2.md`
- Source: Section 3 (Code Interpreter + Memory Design)
- Content: the 4-tier memory architecture (L0 in-context through L3 long-term), the `CodeInterpreterStateManager` checkpoint/rehydration class, data lineage tracking, the long-term memory write policy with conflict resolution, the PII detection/redaction pipeline, and memory summarization for large datasets

**Part 3 (Supplementary):** `docs/platforms/parts/19-bedrock-agentcore-code-interpreter-architecture-part3.md`
- Source: Sections 4–5 (Security & Compliance, Multi-Agent Patterns)
- Content: the threat model table, the `CodeValidationHook` AST-scanning class, Bedrock Guardrails configuration, IAM least-privilege policy, GDPR compliance posture; the Writer → Validator pipeline (`MultiAgentCodeInterpreterPipeline`), shared-memory coordination with optimistic locking, and the async execution model

**Part 4 (Supplementary):** `docs/platforms/parts/19-bedrock-agentcore-code-interpreter-architecture-part4.md`
- Source: Sections 6–7 (Cost & Performance Optimization, Implementation: Code + Terraform)
- Content: cost drivers table, the `ComputationCache` result-caching class, the `LargeDatasetHandler` chunking class; the full `banking_analyst_agent.py` reference implementation (tools, hooks, agent construction, an example generated analysis script) and the complete Terraform `main.tf` (KMS, S3, DynamoDB, OpenSearch Serverless, IAM, CloudWatch, Bedrock Guardrail, Step Functions, VPC, alarms, outputs)

**Part 5 (Supplementary):** `docs/platforms/parts/19-bedrock-agentcore-code-interpreter-architecture-part5.md`
- Source: Sections 8–11 (Best Practices & Guardrails, Risks & Trade-offs, Project Roadmap, Evaluation Framework) + the unnumbered ADR appendix
- Content: the tool-selection decision tree, the `RetryOrchestrator` retry/fallback strategy, memory policy summary; when-not-to-use guidance, key failure modes, scaling constraints; the 3-phase project roadmap, developer onboarding, and governance/RACI model; the `AgentEvaluationPipeline` automated evaluation class and key metrics dashboard; and the four Architecture Decision Records (Code Interpreter vs SageMaker Processing, OpenSearch Serverless vs RDS pgvector, DynamoDB conditional writes vs distributed locks, Writer → Validator vs single agent)

## Source-quality notes

This is a `source_type: native-md` document — already clean, well-formed markdown (unlike the PDF-converted K8s Handbook and AgentCore Memory Architecture Guide sources). Migration was primarily splitting + diagram conversion + light editing; all Python and Terraform code blocks were preserved near-verbatim.

- Two ASCII box-drawing architecture diagrams in Part 1 (Logical Architecture, Runtime Tool-Invocation Lifecycle) were converted to Mermaid `graph TB` and `flowchart TD` diagrams respectively.
- One ASCII box-drawing diagram in Part 2 (4-tier Memory Architecture Layers) was converted to a Mermaid `graph TB` diagram.
- Two ASCII box-drawing diagrams in Part 3 (Writer → Validator Pipeline, Async Execution Model) were converted to Mermaid `flowchart TD` and `flowchart LR` diagrams respectively.
- One ASCII decision-tree diagram in Part 5 (Tool Selection Policy, using `├── └── │` characters) was converted to a Mermaid `flowchart TD` with diamond decision nodes; the accompanying USE/AVOID bullet lists (previously marked with `✓`/`✗` glyphs) were kept as plain bullet lists.
- All `# ─── Section Name ───` box-drawing comment dividers inside Python and Terraform code blocks (Part 4's `banking_analyst_agent.py` and `main.tf`, Part 5's example code) were converted to plain ASCII `# --- Section Name ---` dividers — box-drawing characters are zero-tolerance even inside code comments.
- Bare `<`/`>` comparison operators in Part 5's tables (e.g. "&lt;100ms", "&gt;92%") were escaped as HTML entities to avoid MDX parsing errors.

## Navigation

- Each part ends with a pointer to the next/adjacent parts; Parts 2–5 also link back to Part 1.
- Topic ID: all five parts share the `bedrock-agentcore-code-interpreter-architecture` topic family.
- Part 1 is canonical (`topic_id: bedrock-agentcore-code-interpreter-architecture`, carries `supersedes: [docs/cloud-platforms/aws/bedrock-agentcore-code-interpreter-architecture.md]`).
- Parts 2–5 use `topic_id: bedrock-agentcore-code-interpreter-architecture-part{2,3,4,5}`, all `supersedes: []`.
