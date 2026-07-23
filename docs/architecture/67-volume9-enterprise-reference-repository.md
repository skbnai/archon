---
title: "Part A — Reference Architectures & Architecture Patterns"
doc_type: reference-architecture
domain: architecture
topic_id: volume9-enterprise-reference-repository
date_created: 2026-07-23
status: current
last_reviewed: 2026-07-23
covers_version: "N/A"
supersedes:
  - docs/enterprise-architecture/architectural-review-board/Volume9_Enterprise_Reference_Repository.md
nav_prev: docs/architecture/66-volume7-ai-native-arb-case-studies.md
nav_next: null
---

# Part A — Reference Architectures & Architecture Patterns

Enterprise Reference Repository — A curated, practitioner-grade reference library: architecture patterns, anti-patterns, decision trees, ADR examples, governance policies, and Policy-as-Code templates — calibrated for banking and financial services environments.

Enterprise Architecture Review Board Handbook · Banking & Financial Services Edition · Continuation Volume

## Using Mermaid Diagrams in Living Documentation

All diagrams can be specified in Mermaid syntax, which can be rendered directly in Confluence, GitHub/GitLab, and most modern documentation platforms. This means the diagram lives as version-controlled text alongside ADRs and architecture records, rather than as a binary image file disconnected from its source.

## Reference Architectures

### RA-01 — Event-Driven Core Banking Integration

**Problem:** Core banking platforms are typically synchronous, monolithic, and intolerant of the fan-out integration demands that a modern digital bank imposes — mobile app, open banking APIs, real-time analytics, fraud detection, regulatory reporting, all needing to react to account events in near-real-time.

**Solution:** Introduce an event streaming backbone (Apache Kafka or cloud-native equivalent) as a mediator between the core and downstream consumers. The core emits domain events (AccountDebited, LoanStatusChanged, CustomerKYCUpdated) and each consumer subscribes independently — no direct coupling between consumers, and the core is insulated from demand spikes on any downstream system.

**Trade-offs:** Gained: Decoupling; downstream scalability independent of core; natural audit trail (the event log itself is immutable); fan-out without core performance impact. Lost: Eventual consistency — consumers see events with a small lag, which is unacceptable for some use cases (e.g., real-time payment status checks by the customer must be handled with care). Avoid when: The bank has very low event volume and the integration complexity of a broker outweighs its benefits; or when regulatory requirements demand synchronous confirmation of every downstream reaction.

### RA-02 — Strangler Fig for Core Banking Modernization

**Problem:** Replacing a legacy core banking platform in a single cutover carries catastrophic operational risk. But allowing the legacy to persist indefinitely also has compounding costs.

**Solution:** The Strangler Fig pattern routes new capability requests to modern implementations while existing functionality remains on the legacy system, migrating capability-by-capability with each iteration gradually shrinking the legacy's footprint until it can be safely retired. The routing layer (often an API gateway or a specialized "façade" service) is the key architectural element.

**Trade-offs:** Gained: Risk distributed across many small increments rather than concentrated in one cutover; ability to validate each migrated capability in production before the next; legacy system provides fallback at every stage. Lost: Extended dual-running cost — the bank runs both systems in parallel for the migration duration, which can be 3-7+ years for a full core banking migration; the routing facade itself becomes a technical debt item. Avoid when: The legacy system is so deeply intertwined that clean capability boundaries cannot be established without a foundational redesign first.

### RA-03 — CQRS for Regulatory Reporting at Scale

**Problem:** Regulatory reporting in banking requires complex, time-consuming aggregations over large datasets that, if run against the transactional database, impose unacceptable performance impact on the write path — and the reporting data model is often radically different from the transactional one.

**Solution:** Command Query Responsibility Segregation (CQRS) separates the write model (transactional commands) from read models (optimized for regulatory reporting queries), with the read model updated asynchronously from the write model via the event stream from RA-01. Multiple specialized read models can coexist, each optimized for a different reporting shape.

**Trade-offs:** Gained: Read model can be independently scaled; report queries no longer compete with payment processing for database resources; read models can be purpose-built for regulatory report schemas. Lost: Eventual consistency on the read side (reports reflect data as of last event, not necessarily real-time); operational complexity of maintaining read model synchronization. Avoid when: Reports must reflect exact-to-the-second transactional state.

### RA-04 — Saga Pattern for Distributed Payment Flows

**Problem:** A payment initiation in a modern banking architecture typically spans multiple services (authorization, fraud check, AML screening, ledger posting, notification) with no single database that all services share. A failure in any step must not leave the system in a partially-completed state that can't be reconciled.

**Solution:** The Saga pattern manages a distributed multi-step transaction as a sequence of local transactions, each of which publishes an event consumed by the next step. If any step fails, compensating transactions are executed in reverse to undo prior steps' effects — preserving data consistency without a distributed transaction coordinator.

### RA-05 — API Gateway with Backend-for-Frontend (BFF) for Omnichannel Banking

**Problem:** Mobile banking, web banking, branch systems, and open-banking third-party channels all consume overlapping but not identical data, at different payload sizes, with different latency tolerances and authentication requirements.

**Solution:** An API gateway handles cross-cutting concerns (authentication, rate limiting, SSL termination) while channel-specific Backend-for-Frontend services handle the composition, transformation, and aggregation each channel needs — the mobile BFF returns a lightweight, mobile-optimized payload; the web BFF returns a richer dataset; the open-banking BFF enforces regulatory protocol requirements.

### RA-06 — Zero-Trust Network Architecture for Payment Processing Environments

**Problem:** Traditional perimeter-based security assumes that traffic inside the network boundary is trustworthy — a model that has been demonstrated repeatedly as insufficient.

**Solution:** Zero-trust treats every connection request as potentially hostile regardless of origin, requiring explicit verification (identity, device posture, intent) for every access request, minimum-privilege authorization scoped to the specific action requested, and continuous monitoring of in-session behavior.

### RA-07 — AI Model Gateway / Router Pattern

**Problem:** An enterprise banking organization deploying AI features across multiple products faces vendor concentration risk, cost optimization opportunities, and resilience requirements.

**Solution:** A model gateway sits between consuming services and AI model providers, handling routing, rate limiting, cost tracking, provider failover, and response caching. A routing policy engine directs queries based on complexity, cost envelope, latency requirements, and data-sensitivity classification.

### RA-08 — Customer 360 Data Product

**Problem:** Customer data in a typical large bank is fragmented across dozens of systems with no single, curated, authoritative view.

**Solution:** A Customer 360 data product aggregates, reconciles, and exposes a curated, versioned, SLA-backed customer view as a reusable data product rather than a point-to-point integration. Ownership, quality, and freshness are explicit.

### RA-09 — Agentic AI with Human-in-the-Loop for KYC Remediation

**Problem:** KYC (Know Your Customer) remediation — identifying and resolving gaps in customer due diligence records — is a labor-intensive process typically handled by operations teams manually reviewing thousands of records. It is highly repetitive, yet the consequences of errors are severe.

**Solution:** An AI agent handles the high-volume, well-defined portion of the remediation workflow (identifying gaps, retrieving available data, drafting outreach to customers, pre-populating forms) with human reviewers handling exception cases and final authorization decisions. The agent specification explicitly defines the boundary: agent acts autonomously up to drafting/staging; human approves before any customer-facing action or record modification.

## Architecture Pattern Catalog

Fifteen core patterns covering resilience, distribution, data, observability, and AI:

**AP-01 Circuit Breaker** — Prevents cascading failure when a downstream service is degraded. Trade-off: Adds false-positive risk.

**AP-02 Bulkhead** — Isolates resource pools so failure in one consumer doesn't exhaust resources for others. Trade-off: Adds resource overhead.

**AP-03 Retry with Exponential Backoff** — Recovers from transient failures without overloading the failing service. Trade-off: Retry storms under correlated failure.

**AP-04 Idempotency Keys** — Makes payment and state-changing operations safe to retry without double-processing. Trade-off: Requires idempotency store with appropriate retention.

**AP-05 Outbox Pattern** — Guarantees exactly-once event publishing even when the event broker is temporarily unavailable. Trade-off: Polling overhead.

**AP-06 Event Sourcing** — Preserves the full history of state changes as an immutable event log — strong audit trail. Trade-off: Query complexity; eventual consistency.

**AP-07 Sidecar** — Attaches operational concerns (logging, mTLS, configuration) to service instances without modifying service code. Trade-off: Adds per-instance resource overhead.

**AP-08 API Versioning via Content Negotiation** — Allows API evolution without breaking existing consumers. Trade-off: Multiple active versions create maintenance burden.

**AP-09 Data Mesh / Domain Ownership** — Shifts data product ownership to domain teams, improving quality accountability. Trade-off: Federated ownership increases data governance coordination cost.

**AP-10 RBAC + ABAC Hybrid Authorization** — Role-based access for coarse-grained control, attribute-based for fine-grained. Trade-off: Policy complexity grows quickly.

**AP-11 Feature Flags / Dark Launching** — Decouples deployment from release; enables gradual rollout and instant rollback. Trade-off: Technical debt accumulates if flags are not cleaned up.

**AP-12 Prompt Caching** — Reduces LLM API cost for calls sharing a common system prompt. Trade-off: Only effective when prompt prefix is stable.

**AP-13 RAG (Retrieval-Augmented Generation)** — Grounds LLM responses in enterprise knowledge without fine-tuning. Trade-off: Retrieval quality ceiling determines answer quality; hallucination risk.

**AP-14 Competing Consumers** — Scales event/message processing horizontally. Trade-off: Message ordering not guaranteed; requires idempotent processing.

**AP-15 Transactional Outbox + Inbox** — Implements reliable exactly-once message delivery end-to-end. Trade-off: Two additional tables and polling overhead.

## Anti-Pattern Catalog

Fifteen named failure modes with root causes and remedies:

**ANT-01 Distributed Monolith** — Services deployed separately but share a database or call each other synchronously for every operation. Remedy: Proper bounded context decomposition before deployment decomposition.

**ANT-02 Chatty Microservices** — A single business operation requires 15+ synchronous inter-service calls. Remedy: Event choreography or aggregate coarser-grained services.

**ANT-03 Shared Mutable Database** — Multiple services write to a single shared schema. Remedy: Each service owns its data and exposes it through a defined interface.

**ANT-04 God Service** — One service has accumulated so many responsibilities that it is functionally a monolith deployed as a "service." Remedy: Apply strangler fig to decompose.

**ANT-05 Callback Hell / Event Spaghetti** — Event flow is so complex and non-obvious that no single person can trace a business process end-to-end through the events. Remedy: Explicit event catalog with choreography diagrams and fitness functions.

**ANT-06 Accidental Eventual Consistency** — A system is built as eventually consistent because the team used an event broker, not because eventual consistency was a deliberate design choice. Remedy: Establish the consistency model required per use case.

**ANT-07 The Mega-ADR** — An Architecture Decision Record covering dozens of choices in one document — so large it's never read and never updated. Remedy: Each decision gets its own ADR, cross-referenced.

**ANT-08 Security Through Obscurity** — API endpoints "protected" by not being documented, with no actual authentication or authorization enforcement. Remedy: Zero-trust and explicit auth enforcement on every endpoint.

**ANT-09 Snowflake Infrastructure** — Each deployment environment is hand-configured uniquely. Remedy: Infrastructure-as-code with strict environment parity enforcement.

**ANT-10 Vendor-Mediated Integration** — Two internal systems integrated through a third-party vendor's platform that neither team controls. Remedy: Event-driven direct integration or explicit vendor-dependency risk management.

**ANT-11 Prompt Injection Blindness** — An AI agent processes external input without sanitization or sandboxing. Remedy: Explicit input sanitization, agent tool permission scoping, and output validation.

**ANT-12 Model Monoculture** — Enterprise-wide AI deployment entirely dependent on a single model provider with no fallback. Remedy: AI Model Gateway with multi-provider routing and tested failover.

**ANT-13 Unbounded Agent Autonomy** — An AI agent deployed with write access to production systems and no explicit scope-of-action limits. Remedy: Explicit tool permission scoping and human-in-the-loop gates.

**ANT-14 The Living Dead System** — A system officially classified as "in decommission" for 3+ years that never actually gets decommissioned. Remedy: Retirement Checklist with dependency verification; ARB gate requiring decommission sign-off.

**ANT-15 Cost-Blind Architecture** — Architecture designed for technical elegance without modeling the economics at scale. Remedy: Mandatory cost-at-scale projection as part of the ARB submission.

## ADR Examples

**ADR-001 — ADOPT APACHE KAFKA AS ENTERPRISE EVENT STREAMING BACKBONE**

Date: [Date]. Status: Accepted. Deciders: Chief Architect, Domain Architects, CTO Council.

Context: The enterprise currently uses point-to-point synchronous integration between core banking, mobile banking, fraud detection, and regulatory reporting systems. This creates tight coupling, limits downstream system scale independence.

Decision: We will adopt Apache Kafka (managed via cloud provider MSK / Confluent Cloud) as the enterprise event streaming backbone for domain events. All teams producing or consuming domain events will do so through this backbone rather than point-to-point.

Options considered: Option A: Kafka/Confluent Cloud — strong ecosystem, proven at banking scale, managed offering reduces operational burden. Selected. Option B: Cloud-native — lower operational overhead, tighter cloud integration, but higher vendor lock-in risk. Option C: RabbitMQ — mature, simpler, but lacks Kafka's log retention/replay model.

Consequences positive: Decoupling of core banking from downstream consumers; replay capability for new consumers; durable audit log; scales downstream systems independently.

Consequences negative: Kafka operational expertise required; introduces eventual consistency that teams must design for explicitly; a new critical infrastructure component requiring high-availability design and operational runbooks.

Compliance notes: Event data at rest will be encrypted; PII in events must be tokenized per Data Governance policy; event retention periods set per regulatory requirement by topic classification.

**ADR-002 — USE CQRS FOR REGULATORY REPORTING READ MODELS**

Context: Regulatory reporting queries against the transactional database are causing performance degradation during month-end/quarter-end processing windows.

Decision: Implement CQRS with purpose-built read models for the three highest-volume regulatory report types (LCR, NSFR, and AML transaction monitoring feeds). Read models will be maintained via consumption of domain events from the Kafka backbone.

Consequences positive: Zero contention with transactional write path; read models optimized for their specific report schema; can independently scale report-generation infrastructure.

Consequences negative: Eventual consistency — reports reflect data as of last event processing, with SLA lag. Reconciliation process required for end-of-day regulatory submissions. Additional operational complexity for read model rebuild on schema change.

**ADR-003 — AGENT SPECIFICATION: KYC REMEDIATION AGENT SCOPE OF AUTONOMY**

Context: The KYC Remediation Agent requires a formally documented scope of autonomy as a governance prerequisite for ARB and AI Governance Board approval.

Decision — Permitted autonomous actions: Read-only access to customer record system to identify KYC gaps. Cross-reference external data sources (credit bureau, sanctions lists) for gap resolution candidates. Draft remediation action items and customer outreach messages (staging only, not sending). Categorize customers into remediation priority tiers.

Decision — Requires human approval before execution: Any customer-facing communication. Any write to the customer record system. Any recommendation to exit a customer relationship. Any case above defined complexity threshold (agent confidence score below 0.75).

Consequences: Human review remains in the critical path for all consequential actions, preserving regulatory accountability. Agent delivers value through throughput improvement on the screening and preparation steps, which represent approximately 70% of current operations team time per case.
