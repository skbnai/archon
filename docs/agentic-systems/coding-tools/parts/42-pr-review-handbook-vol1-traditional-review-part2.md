---
title: 'THE ENTERPRISE PR REVIEW PLAYBOOK (Part 2)'
doc_type: guide
domain: agentic-systems
topic_id: pr-review-handbook-vol1-traditional-review-part2
status: current
date_created: 2026-07-24
last_reviewed: 2026-07-24
supersedes: []
---

**This is Part 2 of 3. [Back to Part 1 ←](pathname:///archon/agentic-systems/coding-tools/42-pr-review-handbook-vol1-traditional-review) | [Continue to Part 3 →](pathname:///archon/agentic-systems/coding-tools/parts/42-pr-review-handbook-vol1-traditional-review-part3)**
|**Common comments**|"This is fine as a one-off, but if we're about to do this five more times, we should<br/>build the shared primitive now." "This needs an ADR before it merges, not after."|
|**Anti-patterns they flag**|Reviewing everything at this level of scrutiny, which does not scale and signals a<br/>breakdown of trust in staff/senior review; being the bottleneck on changes that<br/>don't need this altitude of review.|

#### **2.5 Enterprise Architect**

|**What they review**|Alignment with enterprise reference architecture and business-capability model;<br/>whether the change respects bounded-context and domain boundaries (in the<br/>DDD sense); future extensibility against the multi-year roadmap; compliance with<br/>published enterprise standards; ADR traceability.|
|---|---|
|**What they deliberately**<br/>**ignore**|Implementation-level code quality — that is delegated to engineering review.|
|**Questions they ask**|"Does this belong to the domain that owns it, or is it leaking a capability across a<br/>bounded context?" "Is there an existing enterprise pattern for this, and if not,<br/>should one be created?" "Does this align to an approved ADR, and if not, why<br/>not?"|
|**Approval criteria**|The change fits the target-state architecture, or there is an explicit, time-boxed<br/>exception recorded (with an owner and a remediation plan) if it doesn't.|
|**Common comments**|"This duplicates a capability that already exists in the Customer domain — can we<br/>reuse it instead of building a parallel model?" "This needs to go through the<br/>architecture review board before merge."|
|**Anti-patterns they flag**|Architecture review as a rubber-stamp committee with no teeth; enterprise<br/>standards so rigid they get routinely bypassed, which erodes the review's<br/>legitimacy entirely.|

#### **2.6 Security Architect**

|**What they review**|AuthN/AuthZ correctness; OWASP Top 10 classes (injection, SSRF, XSS, CSRF,<br/>broken access control); secrets and credential handling; encryption in transit and<br/>at rest; PII handling and data classification; RBAC/ABAC model correctness;<br/>multi-tenancy isolation; trust-boundary crossings; supply-chain risk (dependency<br/>provenance, SBOM, signed artifacts).|
|---|---|
|**What they deliberately**<br/>**ignore**|Business logic correctness unrelated to a security control; UI/UX decisions.|
|**Questions they ask**|"What is the trust boundary here, and does this change cross it?" "If this input is<br/>attacker-controlled, what happens?" "Is this secret ever logged, cached, or<br/>returned in an error message?" "Does this new dependency introduce a<br/>supply-chain risk we haven't accepted before?"|
|**Approval criteria**|No new class of vulnerability is introduced; any new trust boundary is explicitly<br/>modeled and least-privilege is preserved; secrets never appear in code, logs, or<br/>version control.|
|**Common comments**|"This endpoint is missing an authorization check — anyone with a valid session,<br/>not just the resource owner, can call this." "This dependency was published two<br/>days ago with no history — hold until it has more provenance."|
|**Anti-patterns they flag**|Security review that happens only at the end, after architecture is locked in,<br/>forcing an expensive rework; treating every finding as blocking regardless of<br/>actual exploitability, which trains engineers to route around security review<br/>entirely.|

#### **2.7 Platform Engineer**

|**What they review**|Deployment safety (containers, Helm charts, Kubernetes manifests, Terraform);<br/>resource requests/limits; backward compatibility of infra changes; feature-flag<br/>hygiene; observability wiring (is this new service emitting metrics/logs/traces by<br/>default); golden-path conformance.|
|---|---|
|**What they deliberately**<br/>**ignore**|Application-level business logic — platform review is about the substrate the code<br/>runs on, not what the code does.|
|**Questions they ask**|"Does this have resource limits, or will it starve its neighbors?" "Is this<br/>rollback-safe if the deploy needs to be reverted mid-rollout?" "Does this follow the<br/>golden path, or is it a bespoke deployment pattern we'll have to support forever?"|
|**Approval criteria**|The change deploys safely, is observable by default, and doesn't introduce a<br/>one-off infrastructure pattern that platform engineering will be asked to maintain<br/>indefinitely.|
|**Common comments**|"This Helm chart has no resource limits set — that's how one bad deploy takes<br/>down the node." "Can this use the shared logging sidecar instead of a custom log<br/>shipper?"|
|**Anti-patterns they flag**|Approving infra changes without checking rollback behavior; allowing bespoke,<br/>unsupported deployment patterns to proliferate because saying no is friction in the<br/>moment.|

#### **2.8 Site Reliability Engineer (SRE)**

|**What they review**|SLI/SLO impact; timeout and retry configuration; idempotency of operations that<br/>may be retried; rate limiting and backpressure; circuit-breaker presence on<br/>external calls; rollback plan; chaos/failure-mode readiness; whether the change is<br/>safe to deploy during business hours.|
|---|---|
|**What they deliberately**<br/>**ignore**|Code style; whether the abstraction is elegant, so long as it's operationally safe.|
|**Questions they ask**|"What happens when this dependency is slow or down?" "Is this operation<br/>idempotent if the client retries?" "What's the blast radius if this is wrong, and how<br/>fast can we roll it back?" "Does this add load to a system that's already near its<br/>SLO budget?"|
|**Approval criteria**|The change has a bounded, understood failure mode; retries are capped and<br/>jittered; rollback is fast and tested, not theoretical.|
|**Common comments**|"This external call has no timeout — a hung dependency will hang every caller."<br/>"This retry loop has no backoff and will hammer the downstream service during an<br/>incident."|
|**Anti-patterns they flag**|No rollback plan ("we'll just fix forward"); retries without backoff or jitter, which turn<br/>a minor blip into a self-inflicted DDoS ("retry storm"); deploying a risky change on<br/>a Friday afternoon with nobody available to respond.|

#### **2.9 QA Engineer**

|**What they review**|Testability of the change; presence and quality of integration tests, not just unit<br/>tests; regression risk against existing behavior; edge cases the author didn't<br/>consider; contract-test coverage for consumer-facing interfaces.|
|---|---|
|**What they deliberately**<br/>**ignore**|Internal implementation detail that has no externally observable behavior.|
|**Questions they ask**|"How would I test this if I had to do it manually?" "What's the smallest input that<br/>breaks this?" "Does this change any documented contract, and if so, is there a<br/>contract test for it?"|
|**Approval criteria**|The change is verifiable — there's a way to know, mechanically, whether it's<br/>working — and the tests actually exercise the failure paths, not just the happy<br/>path.|
|**Common comments**|"This only tests the success case — what does the API return on a malformed<br/>request?" "This will regress the behavior tested in [existing test], which now needs<br/>updating or is silently broken."|
|**Anti-patterns they flag**|Tests that assert on implementation detail rather than behavior, which break on<br/>every refactor and get deleted rather than fixed; non-deterministic ("flaky") tests<br/>tolerated because "that test is always flaky," which erodes trust in the entire suite.|

#### **2.10 Data Engineer**

|**What they review**|Schema evolution safety (additive vs. breaking); data-contract compliance for<br/>downstream consumers; lineage impact; backfill strategy for historical data;<br/>partitioning and volume implications.|
|---|---|
|**What they deliberately**<br/>**ignore**|Application-layer business logic that doesn't touch the data model.|
|**Questions they ask**|"Is this schema change backward-compatible for consumers still on the old<br/>contract?" "Does this need a backfill, and if so, what's the plan and the cost?"<br/>"Does this break anything downstream in the lineage graph?"|
|**Approval criteria**|The schema change is additive or has an explicit, communicated deprecation<br/>window; backfill (if needed) is planned and sized, not left as a surprise for whoever<br/>runs the migration.|
|**Common comments**|"This renames a column that three downstream pipelines depend on — this needs<br/>a dual-write period, not a hard cutover." "What's the expected row count for this<br/>backfill, and has anyone estimated the runtime?"|
|**Anti-patterns they flag**|Breaking schema changes shipped without notifying consumers; backfills run<br/>against production without a dry run or a rollback plan; silently changing the<br/>meaning of an existing field instead of adding a new one.|

#### **2.11 AI Engineer**

|**What they review**|Prompt quality and versioning; guardrail and content-filter coverage; model routing<br/>logic (cost/latency/capability tradeoffs); temperature and sampling parameter<br/>appropriateness for the task; structured-output schema enforcement; hallucination<br/>and grounding risk; evaluation coverage for the specific change; RAG retrieval<br/>quality; conversational memory handling; token cost per request at expected<br/>volume; latency budget.|
|---|---|
|**What they deliberately**<br/>**ignore**|Whether the underlying model architecture is state-of-the-art — that's a<br/>model-selection decision, not a PR-level one.|
|**Questions they ask**|"What happens when the model returns something outside the expected<br/>schema?" "Is there an eval suite that would have caught a regression in this<br/>prompt change?" "What's the cost per request at expected traffic, and does that<br/>scale linearly with a bad actor sending long inputs?" "Is user data that shouldn't be<br/>retained ending up in a memory store?"|
|**Approval criteria**|The change has eval coverage showing it doesn't regress quality on the existing<br/>benchmark set; structured outputs are validated against a schema rather than<br/>trusted as-is; failure modes (malformed output, refusal, timeout) are handled<br/>explicitly.|
|**Common comments**|"This prompt change wasn't run against the eval suite — we don't know if it<br/>regresses the existing golden set." "There's no fallback if the model returns invalid<br/>JSON here." "This will blow the latency budget for the synchronous request path<br/>— should this be async?"|
|**Anti-patterns they flag**|Shipping a prompt tweak with no eval run ("it looked better on three examples");<br/>trusting raw model output without schema validation; unbounded conversation<br/>memory that grows context and cost without limit; no fallback behavior when the<br/>model call fails or times out.|

#### **2.12 AI Architect**

|**What they review**|Agent and tool-orchestration design; memory strategy (what persists, what<br/>doesn't, and why); evaluation framework coverage at the system level, not just the<br/>prompt level; human-approval checkpoints for consequential actions; multi-agent<br/>communication protocol and failure isolation; context-engineering discipline (what<br/>enters the context window and why); prompt/version governance across the whole<br/>agent, not one prompt.|
|---|---|
|**What they deliberately**<br/>**ignore**|Individual prompt wording, which is delegated to the AI engineer role.|
|**Questions they ask**|"What happens if this agent gets into a loop — is there a hard iteration cap?"<br/>"Which actions require human approval before execution, and is that enforced in<br/>code, not just documented?" "If one agent in a multi-agent system produces a bad<br/>output, does it poison the others, or is there isolation?" "How is context window<br/>growth bounded over a long-running session?"|
|**Approval criteria**|The system has bounded failure modes: agents cannot loop indefinitely, cannot<br/>take irreversible consequential actions without an explicit approval gate, and<br/>degrade gracefully rather than cascading failure across a multi-agent pipeline.|
|**Common comments**|"This tool call has no rate limit and no maximum-iteration cap — an agent stuck in<br/>a retry loop could rack up unbounded cost or take unbounded action." "This action<br/>(deleting data, sending money, emailing a customer) needs a human-in-the-loop<br/>gate, not just a confidence threshold."|
|**Anti-patterns they flag**|Infinite agent loops with no hard iteration ceiling; context explosion from<br/>unbounded memory or tool-output accumulation, driving both cost and quality<br/>degradation; consequential actions (financial, destructive, externally visible) gated<br/>only by a soft confidence score rather than a hard human checkpoint; silent<br/>memory leakage of one user's context into another's session.|

## **Section 12 — Review Anti-Patterns Catalog**

These patterns recur across companies, tech stacks, and review tools. They are grouped by where in the pipeline they tend to originate.

### **12.1 Process Anti-Patterns**

- <sup>**LGTM without review**— approval given because the reviewer trusts the author, not because they read the diff;</sup> erodes the entire signal value of "approved."

- <sup>**Giant PRs**— changes too large to hold in working memory get either rubber-stamped or reviewed so slowly</sup> that the author has moved on to unrelated work by the time comments arrive.

- <sup>**Missing ADR**— an architecturally significant decision made silently inside a PR, with no record of the</sup> alternatives considered or why this one won, leaving future engineers to reverse-engineer intent from a diff.

- <sup>**No rollback plan**— "we'll fix forward" as a strategy, discovered to be inadequate only during an actual incident.</sup>

- <sup>**Hidden breaking changes**— a change that is technically backward-compatible in the code but breaks an</sup> implicit contract (timing, ordering, error format) that consumers depend on.

- <sup>**Architecture drift**— many individually-reasonable PRs that, in aggregate, move the system away from its</sup> documented target architecture with nobody noticing until a much larger remediation is required.

### **12.2 Code-Level Anti-Patterns**

- <sup>**Business logic duplication**— reimplementing a rule that already exists elsewhere, creating two sources of</sup> truth that will inevitably drift.

- <sup>**Magic constants**— unexplained numeric or string literals that encode a business rule with no record of why</sup> that value was chosen.

- <sup>**Over-engineering**— building for a scale or flexibility requirement that doesn't exist yet, at the cost of</sup> present-day readability.

- <sup>**Premature optimization**— complexity introduced for a performance problem that hasn't been measured or</sup> demonstrated.

- <sup>**Non-deterministic tests**— flaky tests tolerated rather than fixed or deleted, which teaches the team to ignore</sup> CI failures generally.

### **12.3 AI-Era Anti-Patterns**

- <sup>**Prompt copied from a chat session**— a prompt that worked in an interactive session, shipped into a</sup> production system without adaptation for adversarial input, cost at scale, or failure handling.

- <sup>**Hardcoded secrets in AI configuration**— API keys embedded directly in prompt templates or agent</sup> configuration files rather than a secrets manager.

- <sup>**Prompt injection surface left open**— user-controlled text concatenated directly into a system prompt or</sup> tool-calling context with no delimiting or sanitization.

- <sup>**Unsafe tool grants**— an agent given a tool with broader permissions than the task requires "in case it's useful</sup> later."

- <sup>**Infinite agent loops**— no hard cap on iterations, tool calls, or cost for an autonomous agent loop.</sup>

- <sup>**Context explosion**— unbounded accumulation of tool output or conversation history into the context window,</sup> degrading both quality and cost predictably over a long session.

- <sup>**Token waste**— redundant context re-sent on every call instead of cached or summarized.</sup>

- <sup>**Memory leakage**— one user's or session's context appearing in another's due to a shared or improperly</sup> scoped memory store.

- <sup>**Silent failures**— an agent or model call that fails and is swallowed rather than surfaced, producing a</sup> confidently wrong result with no error signal.

## **Section 13 — PR Metrics: DORA, SPACE, and Review Health**

### **13.1 DORA Metrics**

The DORA (DevOps Research and Assessment) program, now part of Google Cloud, established four metrics that correlate with high-performing engineering organizations. PR review discipline is a primary lever on two of the four:

#### **DORA Metrics and Their Relationship to Review**

|**Review Question**|**Why It Matters**|
|---|---|
|Deployment frequency|How often an organization successfully releases to production. Small,<br/>frequently-reviewed PRs are a direct enabler; large infrequent PRs are a direct<br/>inhibitor.|
|Lead time for changes|Time from code committed to code running in production. Review latency is<br/>typically the single largest component of lead time in organizations that have<br/>already automated build and deploy.|
|Change failure rate|Percentage of deployments causing a failure in production. This is where<br/>review depth (not just speed) matters — a review culture optimized purely for<br/>throughput tends to raise this metric even as it improves the first two.|
|Time to restore service|How long it takes to recover from a production failure. Influenced by review<br/>discipline around rollback plans and observability wiring, not by review speed.|
