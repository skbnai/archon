---
title: 'THE ENTERPRISE PR REVIEW PLAYBOOK (Part 2)'
doc_type: guide
domain: agentic-systems
topic_id: pr-review-handbook-vol4-agentic-review-architecture-part2
status: current
date_created: 2026-07-24
last_reviewed: 2026-07-24
supersedes: []
---


**This is Part 2 of 2. [Back to Part 1 ←](pathname:///archon/agentic-systems/coding-tools/45-pr-review-handbook-vol4-agentic-review-architecture) for the beginning.**
|**Decision criteria**|Does this change have adequate test coverage of its new or modified behavior,<br/>particularly failure paths?|
|**Output**|Coverage delta plus specific untested branches, cited by file and line.|
|**Confidence score**|High for coverage-delta measurement; lower for judging whether coverage is meaningfully<br/>testing behavior versus just executing lines.|
|**Escalation path**|Advisory only by default; can be configured to block merge below an org-defined<br/>coverage floor.|

#### **Compliance Reviewer Agent**

|**Inputs**|PR diff, data-classification tags on touched fields, applicable regulatory scope (e.g., PCI,<br/>HIPAA, GDPR) for the service.|
|---|---|
|**Context**|Current compliance posture and any open remediation items for this service.|
|**Knowledge sources**<br/>**/ Tools**|Data-classification scanner, policy-as-code engine (e.g., OPA/Rego-style rule evaluation).|
|**Memory**|Prior compliance findings and their resolution for this repository.|
|**Policies**|PII/regulated data must be encrypted, access-logged, and retained per its classification's<br/>policy.|
|**Decision criteria**|Does this change touch regulated data in a way that violates an applicable compliance<br/>policy?|
|**Output**|Findings mapped to the specific regulatory clause or internal policy violated.|
|**Confidence score**|High for policy-as-code deterministic checks; lower for novel data-handling patterns not<br/>covered by existing rules.|
|**Escalation path**|Any finding touching regulated data escalates to a human compliance officer; this agent<br/>never has auto-approval authority.|

#### **Observability Reviewer Agent**

|**Inputs**|PR diff, existing instrumentation coverage for the touched service.|
|---|---|
|**Context**|Standard telemetry conventions (metric naming, trace-span conventions) for the<br/>organization.|
|**Knowledge sources**<br/>**/ Tools**|Instrumentation-coverage linter, dashboard/alert-config diff checker.|
|**Memory**|None beyond current repository state.|
|**Policies**|Every new externally-facing endpoint emits standard request/latency/error metrics and<br/>trace spans by default (Volume 1, Section 2.7–2.8).|
|**Decision criteria**|Will this change be visible in existing dashboards and alerting, or does it introduce an<br/>observability blind spot?|
|**Output**|Findings listing specific missing instrumentation, mapped to the org's standard telemetry<br/>schema.|
|**Confidence score**|High — instrumentation presence/absence is mechanically checkable against a known<br/>convention.|
|**Escalation path**|Advisory only; does not block, but is weighted heavily in the SRE/platform composite<br/>score (Section 16.3).|

#### **AI Safety Reviewer Agent**

|**Inputs**|PR diff for any prompt, agent configuration, or tool-permission change.|
|---|---|
|**Context**|Existing eval suite results for touched prompts/agents; prior incident history for this agent.|

|**Knowledge sources**<br/>**/ Tools**|Eval harness execution, prompt-injection test suite, tool-scope diff analyzer.|
|---|---|
|**Memory**|Prior AI-safety findings and their resolution for this agent/prompt.|
|**Policies**|No consequential/destructive tool granted without a human-approval gate (Volume 3,<br/>Section 14.6); hard iteration/cost caps required on every agent loop.|
|**Decision criteria**|Does this change expand an agent's tool scope, remove a safety check, or lack eval<br/>coverage for a prompt modification?|
|**Output**|Findings citing the specific eval regression, missing gate, or scope expansion.|
|**Confidence score**|High for structural findings (missing iteration cap, missing approval gate on a destructive<br/>tool); lower for eval-score regression severity judgment.|
|**Escalation path**|Any removal of an existing human-approval gate, or any new destructive tool grant, blocks<br/>auto-merge unconditionally and escalates to the AI Architect role (Volume 1, Section<br/>2.12).|

#### **Cost Reviewer Agent**

|**Inputs**|IaC diff, autoscaling configuration diff, projected traffic change if stated in the PR.|
|---|---|
|**Context**|Current spend baseline per service/environment; org-wide cost anomaly thresholds.|
|**Knowledge sources**<br/>**/ Tools**|Cost-estimation tool, autoscaling-ceiling checker.|
|**Memory**|Historical cost anomalies traced to specific infra patterns.|
|**Policies**|Every autoscaling configuration has an explicit, bounded maximum (Volume 2, Section<br/>5.4).|
|**Decision criteria**|Does this change introduce unbounded cost exposure (missing autoscale ceiling,<br/>oversized default resource request)?|
|**Output**|Projected monthly cost delta with the specific configuration driving it.|
|**Confidence score**|Moderate — cost projections are estimates, not guarantees, and should be presented with<br/>that caveat.|
|**Escalation path**|Any missing autoscale ceiling escalates to platform engineering; large projected cost<br/>deltas escalate to the requesting team's engineering manager.|

#### **Governance Reviewer Agent**

|**Inputs**|Full set of findings from all other agents for this PR.|
|---|---|
|**Context**|Organization's review policy configuration (which findings block, which are advisory, per<br/>repo/team).|
|**Knowledge sources**<br/>**/ Tools**|Policy engine (evaluates the aggregate finding set against configured rules).|
|**Memory**|None beyond the current PR's aggregate finding set.|
|**Policies**|The org's codified merge policy — e.g., "any Critical Security finding blocks; any two or<br/>more High findings from different agents requires a second human approval."|

|**Decision criteria**|Given the aggregate finding set, does this PR meet the organization's configured bar for<br/>auto-eligible merge, or does it require human review, and at what level?|
|---|---|
|**Output**|A single routing decision: auto-eligible, standard human review, or escalated review (with<br/>the triggering findings cited).|
|**Confidence score**|This agent does not have its own confidence score — it is a deterministic policy evaluator<br/>over other agents' outputs, not a judgment-forming agent itself.|
|**Escalation path**|By definition, this agent's output *is* the escalation routing for the whole pipeline; it has no<br/>further escalation path of its own beyond the configured governance board (Section 17).|

#### **Enterprise Standards Reviewer Agent**

|**Inputs**|PR diff, applicable enterprise reference architecture and coding-standard documents.|
|---|---|
|**Context**|Which enterprise standards apply to this repository/domain (not every repo is in scope for<br/>every standard).|
|**Knowledge sources**<br/>**/ Tools**|Enterprise standards document search (MCP resource), pattern-conformance linter.|
|**Memory**|Prior standards exceptions granted for this repository, to avoid re-flagging an<br/>already-approved deviation.|
|**Policies**|Conformance to published enterprise patterns, or an explicit, time-boxed, owned<br/>exception on record (Volume 1, Section 2.5).|
|**Decision criteria**|Does this change conform to an existing enterprise standard, or does it introduce an<br/>undocumented deviation?|
|**Output**|Findings citing the specific standard and the specific deviation.|
|**Confidence score**|High for deterministic pattern-matching against documented standards; lower for<br/>judgment calls about whether a standard actually applies to this case.|
|**Escalation path**|Any undocumented deviation from a mandatory (not advisory) enterprise standard<br/>escalates to the Enterprise Architecture review board (Section 17.1).|

## **Section 16 — Multi-Agent Review Workflow**

### **16.1 The Protocol Layer: MCP and A2A**

By mid-2026 the protocol landscape for exactly this kind of multi-agent system has consolidated around two complementary, non-competing standards, both now under open, vendor-neutral governance.

#### **The Two-Layer Protocol Stack**

|**Protocol**|**Origin**|**What It Solves**|**Role in This Pipeline**|
|---|---|---|---|
|MCP (Model Context<br/>Protocol)|Anthropic, released Nov.<br/>2024|How a single agent accesses tools and<br/>data — a reviewer agent's connection<br/>to its SAST scanner, its ADR repository,<br/>its SBOM generator. Reported at<br/>roughly 97 million downloads and<br/>adopted across Anthropic, OpenAI,<br/>Google, and Microsoft tooling by early<br/>2026.|Every specialist agent's<br/>individual toolset in this<br/>pipeline (Section 15.2)<br/>is exposed via MCP.|
|A2A (Agent2Agent)|Google, released April<br/>2025; donated to Linux<br/>Foundation mid-2025|How independent agents — potentially<br/>built by different teams or vendors —<br/>discover each other's capabilities, hand<br/>off tasks, and coordinate, using<br/>structured "Agent Cards" for capability<br/>discovery and defined task-lifecycle<br/>states (submitted, working, completed,<br/>failed). Reported production-grade<br/>enterprise adoption and 150+<br/>supporting organizations by April 2026.|The orchestrator agent's<br/>delegation to each<br/>specialist reviewer<br/>agent, and any<br/>cross-agent finding<br/>hand-off (e.g., the<br/>Architecture Reviewer<br/>flagging something for<br/>the Security Reviewer to<br/>examine further), runs<br/>over A2A.|

The mental model that recurs consistently across current practitioner guidance: **MCP is how an agent uses its tools; A2A is how agents work with each other.** Neither protocol, on its own, answers who is allowed to do what or how an organization knows when something went wrong — that is the governance layer this section and Section 17 build on top of the protocol layer.

### **16.2 Reference Architecture**

*Rendered as Mermaid source below; paste into any Mermaid-compatible renderer (GitHub Markdown, mermaid.live, or a docs site) to view as a diagram. boxes represent A2A-addressable agents; arrows into each box represent its MCP tool connections, omitted here for width.*

### **16.3 Orchestration, Voting, and Conflict Resolution**

- <sup>**Parallel dispatch, bounded timeout**— the orchestrator dispatches to all applicable specialist agents in</sup> parallel (not sequentially), with a hard per-agent timeout; an agent that doesn't return within its budget is treated as "no finding, flagged as incomplete" rather than blocking the whole pipeline indefinitely.

- <sup>**Reviewer voting on overlapping findings**— when two agents flag the same code region for different reasons</sup> (e.g., Performance and Data both flag the same migration), the finding bus surfaces both rather than deduplicating them away, since they represent genuinely independent concerns even when co-located.

- <sup>**Conflict resolution when agents disagree**— if the Architecture Reviewer approves a pattern the Enterprise</sup> Standards Reviewer flags as a deviation, this is not silently resolved by either agent; it routes to a human at the intersection of both domains (typically the Enterprise Architect role, Volume 1 Section 2.5), since the disagreement itself is the signal, not noise to be averaged away.

- <sup>**Weighted composite scoring**— the Governance Reviewer Agent's policy engine, not any individual specialist,</sup> computes the final routing decision, using configured weights per finding severity and agent domain rather than a simple majority vote — a single Critical Security finding should outweigh five Low Documentation findings, and the policy engine encodes that explicitly rather than leaving it to an implicit voting scheme.

### **16.4 Confidence Scoring and Evidence Collection**

Every specialist agent's finding carries a confidence score, but — following the verification-pass pattern already emerging in production tools (Volume 3, Section 14.4) — confidence is not self-reported by the finding-generating agent alone. A separate verification step re-checks each candidate finding against actual code behavior (running the referenced test, re-evaluating the referenced policy rule, re-executing the referenced query plan) before the finding is finalized, specifically to counter the hallucination risk documented in Volume 3, Section 14.5. Every finding in the evidence store carries: the specific artifact it cites (file:line, policy clause, CVE ID), the tool or check that produced it, and the verification step's pass/fail result — nothing reaches a human or the policy engine as a bare assertion.

### **16.5 Human Approval Gates**

This is the single most important governance mechanism in the entire pipeline, and the direct structural fix for the incident pattern described in Volume 3, Section 14.6 (an agent taking a destructive action without human sign-off).

- <sup>**Gates are enforced in the permission model, not the prompt.**An agent should be technically incapable of</sup> executing a gated action — the credential or tool scope simply isn't available to it — rather than merely instructed not to. A prompt-level instruction is a suggestion; a missing credential is a guarantee.

- <sup>**The gated-action list is explicit and enumerated, not inferred.**Destructive infra operations, database</sup> migrations against production, merging a PR, granting a new tool/permission to another agent, and anything touching regulated data are the baseline set; individual organizations extend this list but should never shrink it via an agent's own judgment.

- <sup>**Auto-eligible PRs still pass through a lightweight human confirmation**, not a fully unattended merge — the</sup> reference architecture in 16.2 shows even the "auto-eligible" path terminating in a human final-confirm step, reflecting that no tool surveyed in Volume 3 recommends or implements fully unattended merging in production use today.

- <sup>**Escalation is a first-class output, not a failure mode.**An agent routing a decision to a human is the system</sup> working as designed, not the system failing to be autonomous enough — measuring "percentage auto-resolved" as a success metric in isolation creates exactly the pressure that erodes this safeguard over time.

### **16.6 Traceability, Audit Logs, and the Policy Engine**

- <sup>Every finding, every agent decision, every human override, and every escalation is written to an append-only</sup> audit log — the agentic-review analog of the ADR's append-only, superseded-not-edited discipline from Volume 2, Section 9.3.

- <sup>The policy engine (the Governance Reviewer Agent's rule set) is itself version-controlled and reviewed with the</sup> same rigor as production code — a change to "what blocks a merge" is at least as consequential as the code changes it's gating, and should go through this same review discipline.

- <sup>Audit logs should be queryable for after-the-fact analysis: which agent's findings correlate with actual production</sup> incidents, which agents produce the highest false-positive rate, and which escalation paths are triggered most often — the data that lets an organization tune the pipeline the same way vendors tune their tools using the thumbs-up/down signal described in Volume 3.

## **Section 17 — Enterprise Review Governance**

### **17.1 Change Advisory Boards and Architecture Review Boards**

#### **Governance Boards and Their Relationship to Agentic Review**

|**Board**|**Function**|**Integration Point**|
|---|---|---|
|Change Advisory Board<br/>(CAB)|Reviews and approves high-risk production<br/>changes, typically at a cadence (weekly, or<br/>on-demand for urgent changes) separate from<br/>individual PR review — the governance layer<br/>above PR review, not a replacement for it.|Escalated-review PRs from the reference<br/>architecture (16.2) that trip a defined<br/>blast-radius or risk threshold route here<br/>rather than merging on standard PR<br/>approval alone.|
|Architecture Review<br/>Board (ARB)|Reviews architecturally significant decisions —<br/>typically RFC-stage, before implementation<br/>(Volume 2, Section 10) — and adjudicates the<br/>Enterprise Standards / Architecture Reviewer<br/>agents' escalations described in Section 16.3.|Agent-flagged undocumented deviations<br/>from mandatory enterprise standards,<br/>and disagreements between specialist<br/>agents at an architectural boundary, land<br/>here.|
|Security Review Board|Adjudicates accepted-risk exceptions for<br/>security findings that a team wants to ship<br/>despite a flagged issue — the human authority<br/>the Security Reviewer Agent's unconditional<br/>escalation (Section 15.2) ultimately reports to.|Any Critical/High security finding a team<br/>wants to override rather than fix goes<br/>through this board, not a single engineer's<br/>judgment call.|
|Production Readiness<br/>Review (PRR)|A one-time gate before a new service first<br/>reaches production, checking the full breadth of<br/>Volume 1–2 concerns (ownership, on-call<br/>readiness, SLOs, rollback, security posture) in<br/>one sitting rather than piecemeal across many<br/>PRs.|The Platform, SRE, Security, and<br/>Observability Reviewer agents' outputs<br/>can be aggregated into a PRR checklist<br/>automatically, though the review itself<br/>remains a human sign-off event.|
|Operational Readiness<br/>Review (ORR)|A recurring or pre-major-change version of the<br/>PRR, re-validating operational readiness<br/>(updated runbooks, current on-call rotation,<br/>load-tested capacity) before a significant<br/>change or seasonal traffic event.|Similar aggregation role as the PRR, run<br/>periodically rather than once.|

### **17.2 Production and Operational Readiness Reviews**

These are the highest-altitude review gates in the whole pipeline, and — deliberately — the ones least amenable to full automation. A PRR is checking whether an organization, not just a codebase, is ready: is there a named owner for 2am pages, does the on-call rotation actually have runbook access, has the team actually load-tested at expected scale rather than just configuring an autoscaler and hoping. Agentic review agents can pre-populate the checklist (which reduces the human meeting from an hour of discovery to minutes of confirmation) but the human sign-off itself should not be automated away, since a PRR's actual function is organizational accountability, not just technical verification.

### **17.3 How Governance Boards Integrate with Agentic Review**

The design principle that ties Sections 15–17 together: **agentic review agents feed governance boards; they do not replace them.** An agent can pre-screen, aggregate evidence, flag conflicts, and route escalations with far more consistency and speed than a human doing the same triage manually — but the actual authority to accept risk, override a finding, or certify organizational readiness remains with a named human or board, exactly the same non-negotiable boundary Volume 3, Section 14.7 established for individual review tools, now extended to the full multi-agent pipeline. The audit trail from Section 16.6 is what makes this workable at scale: a governance board reviewing an escalated PR sees the full evidence chain an agent assembled, rather than starting its own investigation from zero.

## **About This Series**

This is Volume 4 of a five-part Enterprise PR Review Playbook. Volume 1 covers workflow, ownership models, and role-based human review playbooks. Volume 2 covers deep domain review. Volume 3 covers AI-assisted review tools available today and their benchmarked strengths and failure modes. Volume 5 collects case studies, master checklists, review scorecards, and a review maturity model that spans all four preceding volumes.

*Generated as a synthesized practitioner reference. The agent-protocol ecosystem (MCP, A2A, and adjacent standards) is evolving rapidly; adoption figures and governance details reflect publicly reported status as of mid-2026 and should be re-verified against current protocol documentation before architecture decisions are finalized.*
