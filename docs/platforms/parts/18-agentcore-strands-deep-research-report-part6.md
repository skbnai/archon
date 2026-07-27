---
title: "Amazon Bedrock AgentCore & Strands SDK — Deep Technical Research Report (Part 6)"
doc_type: guide
domain: platforms
status: current
topic_id: agentcore-strands-deep-research-report-part6
last_reviewed: 2026-07-27
maturity: practitioner
supersedes: []
tags: [aws, agentcore, roadmap, best-practices, anti-patterns]
covers_version: "as of 2026-07-10"
---

> Continues from [Amazon Bedrock AgentCore & Strands SDK — Deep Technical Research Report](../18-agentcore-strands-deep-research-report.md), covering roadmap predictions, the adjacent AWS Continuum/Context signal, best practices, and anti-patterns.

## Part XVI — Roadmap Prediction

### Method

Predictions below are grounded exclusively in public evidence gathered for this report: AWS release notes and blogs, GA/preview timing patterns observed April–June 2026, AWS Summit/re:Invent announcements, GitHub activity in the `strands-agents` organization, and adjacent AWS platform announcements (Continuum, Context) that signal strategic direction. Each prediction carries a confidence level (**High**/**Medium**/**Low**) and its evidentiary basis. Predictions are explicitly forward-looking and unverifiable at time of writing — they are structured inference, not confirmed roadmap.

### Next 6 Months (through ~December 2026)

| Prediction | Confidence | Evidence |
|---|---|---|
| **Registry reaches GA**, adding Terraform/CloudFormation support and at least basic cross-account sharing | Medium | Registry moved preview → visible-roadmap-item within ~2 months of launch (April→June mentions of "additional connectors" at the June summit); AWS's historical pattern (Policy: preview→GA in similar-order months; Evaluations: preview→GA in ~4 months) suggests a GA push within 6–9 months of an April 2026 preview start, but no explicit GA date has been stated |
| **Payments reaches broader regional availability**, still likely preview | Medium | Four regions at May 2026 launch is narrow even by AgentCore preview standards; the partnership structure (Coinbase, Stripe) and cited Bazaar MCP server scale (10,000+ endpoints) suggest AWS intends rapid expansion, but agent-commerce is a genuinely novel risk category AWS is likely to expand cautiously |
| **Harness gains a native HTTP/MCP/A2A endpoint**, closing the API-only gap noted at preview | Medium | The gap was explicitly noted by independent reviewers at preview (April 2026); GA already added Step Functions integration and code export, both signals of AWS actively closing integration gaps quickly post-preview |
| **Policy gains additional third-party detection-signal integrations** (Check Point, Zscaler, Rubrik, Netskope, SentinelOne — all explicitly named "coming soon" by AWS) | High | Directly and explicitly stated by AWS in an official blog as a near-term commitment, not inferred |
| **Code Interpreter Sandbox-mode network isolation is hardened further**, following the DNS-exfiltration disclosure and partial fix | High | AWS already shipped one remediation (DNS exfiltration blocked) within roughly five weeks of BeyondTrust's disclosure; the Sonrai IAM-reachability finding (S3 access from Sandbox mode) remains open at time of writing and is a logical next target given the pattern of rapid response to credible external security research |

### Next 12 Months (through ~mid-2027)

| Prediction | Confidence | Evidence |
|---|---|---|
| **A Policy Studio / visual policy-authoring console** emerges, building on the existing NL2Cedar neuro-symbolic pipeline | Medium | The natural-language-to-Cedar pipeline and Cedar Analysis are already GA-quality building blocks; AWS has a strong historical pattern (IAM Access Analyzer, Verified Permissions console) of eventually wrapping policy-as-code capabilities in a visual authoring layer once the underlying engine matures |
| **Native multi-agent orchestration at the AgentCore platform level** (beyond Strands' SDK-level Graph/Swarm and Gateway's A2A passthrough) — e.g., a managed "Orchestrator" service | Medium | S&P Global Market Intelligence's public case study explicitly cited struggling to orchestrate complex multi-agent workflows and needing a unified memory layer, which AgentCore Memory partially addressed; the *orchestration* half of that gap (not just shared memory) remains a plausible next platform-level service, especially given AWS Context's knowledge-graph direction as adjacent infrastructure |
| **Registry federation** (cross-account, possibly cross-region) ships | Low-Medium | Explicitly named as a preview-stage gap by AWS's own early adopters; federation is architecturally harder than the GA items above and typically lags initial GA by 2+ release cycles in comparable AWS catalog services (e.g., cross-account Resource Access Manager patterns took multiple years to mature for other AWS catalogs) |
| **Compliance Packs** (pre-built Cedar policy + Guardrails bundles mapped to specific regulatory frameworks — HIPAA, PCI-DSS, FedRAMP) | Medium | Consistent with AWS's stated positioning ("stay aligned with numerous AWS compliance programs") and the general AWS pattern of shipping compliance-program-mapped configuration bundles (e.g., Config Conformance Packs) once a policy engine matures; no explicit AgentCore-specific announcement found |
| **Evaluation Studio** (a dedicated, richer authoring/comparison UI for custom evaluators, closing the gap with Phoenix/Braintrust's evaluation-first UX) | Medium | Evaluations and Optimization both reached GA within the report window and are clearly an active investment area; independent observability-landscape analysis explicitly frames evaluation-platform depth as AWS's current relative weak point versus Phoenix/Braintrust, which is the kind of competitive gap AWS has historically closed within 12–18 months once identified |
| **Cost Optimizer** (automated right-sizing recommendations for warm pools, memory strategy selection, model routing) | Medium | The Optimization service's existing "recommendations" capability already analyzes production traces to suggest prompt/tool-description fixes; extending the same trace-mining approach to cost (not just quality) is a natural, low-lift extension of infrastructure AWS has already built |

### Next 24 Months (through ~mid-2028)

| Prediction | Confidence | Evidence |
|---|---|---|
| **Enterprise Agent Marketplace** (cross-organization, not just cross-account within one enterprise) reaches meaningful adoption | Medium | Explicitly named as a roadmap item at re:Invent 2025 ("a marketplace where teams can publish or subscribe to reusable agent capabilities"); the AWS Marketplace "AI Agents & Tools" solution page already exists as of early 2026 for partner-published offerings, but a genuine AgentCore-native, Registry-integrated marketplace (vs. today's general AWS Marketplace listing mechanism) is a larger integration lift likely to land later in this window |
| **Agent Lifecycle Manager** (a unified deprecation/promotion/rollback console spanning Registry + Harness/Runtime versioning) | Medium-High | The individual building blocks (Registry lifecycle states, Runtime/Harness immutable versioning with named-endpoint rollback) already exist independently; unifying them into one lifecycle-management surface is a coherent, low-novelty integration of existing primitives rather than new invention |
| **Visual Agent Builder** (no-code/low-code agent construction UI, likely harness-backed) | Low-Medium | AWS's overall product philosophy across this report — CLI-first, code-exportable, "export to Strands code" as an explicit design principle at Harness GA — suggests AWS is more likely to keep deepening the code-first/config-first Harness path than to invest heavily in a separate no-code builder; Bedrock's existing (separate, older) visual Agent Builder for classic Bedrock Agents suggests appetite exists, but AgentCore's stated positioning has been consistently code/config-first to date |
| **Governance dashboards** unifying Policy decisions, Registry approval workflows, and Payments spend across an entire organization into one executive-facing view | Medium | A direct, logical extension of AWS Continuum's demonstrated "learn mode → enforce mode" staged-trust UX pattern (already shipping for code-vulnerability remediation as of June 2026) applied to the agent-governance domain; AWS has explicitly signaled cross-product coherence around "trust ladders" as a company-wide theme at the June 2026 summit |
| **AgentCore Payments reaches GA** with expanded regional coverage and additional wallet/rail partners beyond Coinbase/Stripe | Medium | Novel risk category makes a cautious, multi-quarter preview-to-GA timeline likely rather than a fast-track; 24 months is a conservative but reasonably confident window given the partnership investment already made |
| **Deeper convergence with AWS Context** (the identity-aware enterprise knowledge graph previewed June 2026) as a native AgentCore Memory/Gateway data source | Medium | Context and AgentCore Memory address adjacent but distinct problems (organization-wide business knowledge vs. per-agent conversational memory); AWS's own framing at the June summit positioned Context as available "to every agent across an organization," which logically implies an AgentCore integration path even though none was explicitly announced within the report window |

## Part XVII — Adjacent Roadmap Signal: AWS Continuum and AWS Context

Though not AgentCore services themselves, both were previewed at the same June 17, 2026 AWS Summit New York event alongside AgentCore enhancements, by the same leadership (VP of Agentic AI Swami Sivasubramanian, Chief AI and Technology Officer Matt Wood), and are directly relevant to any AgentCore roadmap forecast because they reveal AWS's company-wide thesis for the next investment cycle: **trust, not raw capability, is the bottleneck to enterprise agent adoption.**

**AWS Continuum** is an AI-native security service for autonomous code-vulnerability discovery, prioritization, validation, and remediation. Architecturally, it demonstrates the **staged-trust pattern** independent analysis expects AWS to generalize across its agent portfolio: it launches in "learn mode" (every recommendation surfaces with full reasoning and an audit trail; no autonomous action), and organizations promote specific finding *categories* to "enforce mode" individually as confidence is earned — never an all-or-nothing autonomy switch. Exploit validation happens inside isolated sandboxes before any fix is proposed, filtering false positives that would otherwise generate noisy remediation PRs. This launched partly in direct response to internally-reported incidents where AI-generated code changes caused AWS's own production outages in February 2026, which is itself a useful, independently-reported data point on the real-world failure modes agentic systems produce at scale.

**AWS Context** auto-builds an identity-aware knowledge graph from an organization's databases, documents, and chat history, making it queryable and discoverable by every agent across the organization, with access itself scoped by the querying identity's existing permissions (so an agent cannot surface information via Context that the underlying identity wouldn't otherwise be authorized to see). AWS's own framing positions Context as solving the fourth-generation problem in the agent-infrastructure stack — after compute (Runtime), tools (Gateway), and governance (Policy/Registry) comes *business knowledge* — and independent analysis (TechTarget, June 2026) notes AWS is arriving at this "context layer" concept after several other vendors had already begun shipping similar knowledge-graph offerings, making AWS a fast-follower on this specific capability rather than a first-mover.

**Why this matters for the AgentCore roadmap specifically:** both services validate the predictions in Part XVI that emphasize *staged, auditable autonomy* (Governance dashboards, Compliance Packs) and *deeper business-context integration* (the Context-to-Memory convergence prediction) as the most evidence-backed near-term investment areas, rather than raw capability expansion.

## Part XVIII — Best Practices

### Runtime and Harness

- Externalize any state an MCP server or long-running agent needs to survive a microVM recycle — never rely on in-process RAM as a correctness mechanism, only as a latency optimization.
- Use named endpoints (dev/staging/prod) rather than always deploying to DEFAULT, to get zero-downtime rollback via endpoint repointing rather than redeployment.
- Right-size warm pools against measured traffic patterns rather than either accepting cold-start latency or over-provisioning a static pool.
- Start new projects on Harness for speed; explicitly plan the "export to Strands code" exit ramp before configuration complexity outgrows what Harness exposes, rather than discovering the ceiling mid-project.
- Disable Strands hot-reload in any container destined for Runtime or Harness — treat it as strictly local/dev tooling.

### Gateway and Policy

- Always start a new Policy engine in **LOG_ONLY** and validate against real production traffic before flipping to **ENFORCE**.
- Treat natural-language-generated Cedar as a draft requiring human review against the actual Gateway schema, never as production-ready output on first generation.
- Use REQUEST interceptors for anything dynamic (token exchange, external context lookups); use Cedar for anything expressible as a static rule over the resulting context — do not conflate the two responsibilities.
- Scope every execution-role trust policy with `aws:SourceArn`/`aws:SourceAccount` conditions bound to the specific Gateway/Runtime ARN, without exception.
- Do not remove IAM-layer scoping under the assumption that Policy supersedes it — the two layers answer different questions and both must be independently correct.

### Identity

- Prefer OBO token exchange over raw token passthrough wherever the downstream service supports it — it preserves both user and agent identity for fine-grained downstream authorization without a re-consent prompt.
- Register callback URLs per workload identity explicitly; never widen the whitelist beyond what a specific agent's OAuth flows actually require.
- For genuinely multi-cloud agent estates, evaluate a dedicated cross-cloud identity-federation layer early — do not assume AgentCore Identity alone will unify identity across AWS, Azure AI Foundry, and Vertex AI.

### Memory

- Match memory strategy to retrieval contract, not to strategy name popularity — Semantic is not automatically the right default; a travel-preference use case wants User Preference, a workflow-audit use case wants Episodic.
- Set short-term event-expiry deliberately per use case rather than accepting a default; regulated data may need materially shorter retention than the 30-day Harness-GA default.
- Rely on namespace-based (`actorId`-keyed) isolation as the multi-tenant boundary, not application-layer filtering after retrieval.

### Code Interpreter and Browser

- Treat "Sandbox" network mode as *reduced*, not *zero*, network exposure — DNS-tunneling-class exfiltration was independently demonstrated and only partially remediated by AWS at time of writing (the underlying IAM-role-reachability finding from Sonrai remains open).
- Use VPC-only network mode for any Code Interpreter session touching sensitive data, and pair it with a tightly-scoped, dedicated execution role — never a role shared with other AgentCore primitives.
- Enable full session replay and CloudTrail logging on Browser sessions handling any authenticated or sensitive web interaction, treating it as an auditable action a human may need to review after the fact.

### Observability

- Default to CloudWatch for infrastructure health, cost, and compliance audit; layer Phoenix (or an equivalent OTEL-compatible platform) for trace-level debugging and evaluation-driven development — treat this as additive instrumentation, not a fork.
- Use Optimization/failure-insights' continuous monitoring specifically to catch **silent** behavioral failures (no error signal, wrong or subtly-degraded output) — the class of bug that infrastructure metrics alone will never surface.

## Part XIX — Anti-Patterns

- **Treating Policy as a replacement for IAM**, rather than a complementary layer — removes an independent line of defense.
- **Relying on session-ID stickiness for MCP protocol-level correctness** — it is a routing optimization, not a durability guarantee, and will break under real scaling events.
- **Assuming Registry preview auto-catalogs deployed Runtime agents** — it does not; registration is a manual, explicit step teams must build into their deployment pipeline themselves.
- **Assuming "Sandbox" network mode in Code Interpreter means zero egress** — independently disproven; DNS-based exfiltration was demonstrated, and IAM-role reachability from within Sandbox mode is a separate, still-open finding.
- **Leaving Strands hot-reload enabled in a production container** — turns a convenience feature into an unsandboxed arbitrary-code-execution surface.
- **Widening OAuth callback-URL whitelists broadly "to be safe"** — inverts the actual security property the whitelist exists to provide.
- **Deploying multi-region without an explicit state-replication plan for Memory and Registry** — neither replicates natively cross-region; assuming otherwise produces a DR plan that fails exactly when it's needed.
- **Skipping the LOG_ONLY validation phase before ENFORCE** — the single most commonly cited practitioner mistake across the Policy adoption write-ups reviewed for this report; it converts a legitimate business call into an outage.
- **Treating a single quote/estimate from AWS marketing (spend caps, "15× performance," auto-learning claims) as independently verified fact** — several such figures at the June 2026 summit were explicitly flagged by independent analysts as vendor-stated and awaiting third-party verification; architects should distinguish AWS-documented behavior from AWS-marketed claims when making dependency decisions.

## Related

- [Deep Research Report](../18-agentcore-strands-deep-research-report.md) — executive summary, platform foundations, Runtime, Gateway
- [Deep Research Report (Part 5)](18-agentcore-strands-deep-research-report-part5.md) — Security threat model, production architecture, release analysis
- [Deep Research Report (Part 7)](18-agentcore-strands-deep-research-report-part7.md) — Production readiness checklist, cost optimization, security hardening, resilience mechanisms
