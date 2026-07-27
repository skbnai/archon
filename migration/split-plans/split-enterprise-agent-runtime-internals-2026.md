# Split Plan: Enterprise AI Agent Runtime Internals: AWS, Azure & GCP (2026)

**Source:** `/workspace/knowledge-docs/docs/cloud-platforms/enterprise-agent-runtime-internals-2026.md` (~13,750 words body excluding the source's table of contents and claim-classification key, `source_type: native-md`, 24 numbered sections)

**Reason:** Word count exceeds the guide doc_type cap (2600 words hard cap); a 7-way split was used, grouping sections by comparative theme (runtime/isolation, lifecycle/session/durability, memory/MCP/mesh, execution pipeline/auth, zero-trust/guardrails/policy, networking/observability/multi-tenancy, comparative tables/references).

## Split Boundary

**Part 1 (Main):** `docs/platforms/23-enterprise-agent-runtime-internals-2026.md`
- Source: Section 1 (Executive Summary) + Section 2 (Runtime Architecture) + Section 3 (Compute Isolation)
- Content: the three-vendor thesis and architectural-philosophy summary; per-vendor runtime architecture (AWS AgentCore/ECS-Fargate, Azure AI Foundry/ACA, GCP Vertex AI Agent Engine/Cloud Run) with the three vendor architecture diagrams; the compute isolation stack for each vendor (Nitro/Firecracker, Hyper-V/Confidential Containers, gVisor/Borg)

**Part 2:** `docs/platforms/parts/23-enterprise-agent-runtime-internals-2026-part2.md`
- Source: Section 4 (Runtime Lifecycle) + Section 5 (Session Management) + Section 6 (Long-Running Agents & Durable Execution) + Section 7 (Failure Recovery)
- Content: the three per-vendor session-lifecycle sequence diagrams; session type taxonomy, persistence stores, sticky sessions, cross-region failover; durable-execution mechanisms (Step Functions, Durable Functions, Cloud Workflows/Temporal) and the orchestrator comparison table; failure classification/response, retry/circuit-breaker patterns, and the saga-pattern compensation diagram

**Part 3:** `docs/platforms/parts/23-enterprise-agent-runtime-internals-2026-part3.md`
- Source: Section 8 (Memory Architecture) + Section 9 (MCP Runtime Integration) + Section 10 (Sidecars and Service Mesh)
- Content: memory type taxonomy and per-vendor memory deep dives; MCP integration architecture per vendor (including the AWS Gateway tool-call sequence diagram) and the MCP comparison table; per-vendor sidecar/service-mesh composition diagrams (Fargate multi-container, ACA + Dapr, Cloud Run platform-layer proxy) and the service-mesh comparison table

**Part 4:** `docs/platforms/parts/23-enterprise-agent-runtime-internals-2026-part4.md`
- Source: Section 11 (Request Execution Pipeline) + Section 12 (Authentication) + Section 13 (Authorization)
- Content: the full 14-step request-execution pipeline for each vendor (converted from bracket-numbered ASCII blocks to markdown ordered lists); per-vendor authentication stacks and the authentication comparison table; per-vendor authorization models (Cedar+IAM, Azure RBAC+Conditional Access, IAM Conditions+VPC Service Controls) with example policy code

**Part 5:** `docs/platforms/parts/23-enterprise-agent-runtime-internals-2026-part5.md`
- Source: Section 14 (Zero Trust Implementation) + Section 15 (Service-to-Service Trust) + Section 16 (Guardrails Placement) + Section 17 (Middleware and Interceptors) + Section 18 (Policy Engine)
- Content: the zero-trust principle comparison table and SPIFFE/SPIRE status; the three per-vendor credential-chain diagrams and the no-credential-architecture summary; the three per-vendor guardrails-pipeline diagrams and the guardrails comparison table; per-vendor middleware/extension-point tables; per-vendor policy-engine deep dives (Cedar, Azure Policy+OPA, IAM Conditions+OPA) with example policy code

**Part 6:** `docs/platforms/parts/23-enterprise-agent-runtime-internals-2026-part6.md`
- Source: Section 19 (Networking Internals) + Section 20 (Observability Architecture) + Section 21 (Multi-Tenancy Strategy)
- Content: the three per-vendor traffic-flow diagrams, service discovery mechanisms, and latency-engineering targets table; per-vendor observability stacks (traces/metrics/logs/AI-specific) and the observability comparison table; multi-tenancy isolation boundaries, shared-vs-dedicated resource breakdown, and cross-tenant data-leakage prevention controls

**Part 7:** `docs/platforms/parts/23-enterprise-agent-runtime-internals-2026-part7.md`
- Source: Section 22 (Comparative Analysis Tables) + Section 23 (Documented vs Inferred Analysis) + Section 24 (References)
- Content: the four cross-cutting comparison tables (runtime implementation, security architecture, MCP integration, strengths/weaknesses); the per-vendor documented-vs-inferred claim breakdown; the report's full source bibliography, with the source's old-repo "Related Guides" cross-links resolved to their already-migrated new-repo canonical paths (or omitted where not yet migrated)

## Source-quality notes

This is a `source_type: native-md` document — already clean, well-formed markdown. Migration was primarily splitting + diagram conversion; all JSON/Cedar/Python code blocks were preserved verbatim.

- Nine ASCII box-drawing diagrams were converted to Mermaid: three vendor runtime-architecture diagrams (Part 1, `graph TB`), three per-vendor session-lifecycle sequence diagrams (Part 2, `sequenceDiagram`), one MCP tool-call sequence diagram (Part 3, `sequenceDiagram`), and three per-vendor sidecar/service-mesh composition diagrams (Part 3, `graph TB`).
- Three additional box-drawing diagrams were converted in Part 5: the three per-vendor service-to-service credential-chain diagrams (`flowchart TD`).
- Three per-vendor guardrails-pipeline ASCII trees (using `├──`/`│`/`└──`) were converted to Mermaid `flowchart TD` diagrams in Part 5.
- One saga-pattern compensation diagram (using `→`/`↑` arrows, not box-drawing characters, but still an ASCII layout per the diagram-standards migration duty) was converted to a Mermaid `flowchart LR` in Part 2.
- Three per-vendor traffic-flow diagrams (using `→` arrow chains) were converted to Mermaid `flowchart LR` diagrams in Part 6.
- The three per-vendor 14-step "Full Pipeline" numbered blocks (Part 4) were plain bracket-numbered lists inside generic code fences with no box-drawing characters; converted to markdown ordered lists for readability rather than forced into diagrams, since they are linear prose sequences rather than spatial layouts.
- Checkmark/question-mark glyphs (✅/❓, not box-drawing-range characters) in the Section 23 documented-vs-inferred lists were dropped in favor of plain bullet lists, consistent with earlier de-glyphing done elsewhere in this migration wave.
- Bare `<`/`>` comparison operators in Part 6's latency table (e.g. "&lt;5ms") were escaped as HTML entities to avoid MDX parsing errors.
- No content-loss (heading-then-nothing) artifacts were found; every section retained its full body text.

## Navigation

- Each part ends with a pointer to the adjacent parts; Parts 2–7 also link back to Part 1.
- Topic ID: all seven parts share the `enterprise-agent-runtime-internals-2026` topic family.
- Part 1 is canonical (`topic_id: enterprise-agent-runtime-internals-2026`, carries `supersedes: [docs/cloud-platforms/enterprise-agent-runtime-internals-2026.md]`).
- Parts 2–7 use `topic_id: enterprise-agent-runtime-internals-2026-part{2..7}`, all `supersedes: []`.
