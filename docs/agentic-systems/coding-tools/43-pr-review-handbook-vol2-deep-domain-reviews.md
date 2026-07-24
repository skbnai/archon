---
title: 'THE ENTERPRISE PR REVIEW PLAYBOOK (Part 1)'
doc_type: guide
domain: agentic-systems
topic_id: pr-review-handbook-vol2-deep-domain-reviews
status: current
date_created: 2026-07-24
last_reviewed: 2026-07-24
supersedes:
  - docs/coding-tools/code-review/PR_Review_Handbook_Vol2_Deep_Domain_Reviews.md
---
# THE ENTERPRISE PR REVIEW PLAYBOOK
Volume II — Deep Domain Reviews

Architecture, ADRs and RFCs, Security, Infrastructure, Databases, APIs, and Documentation — Reviewed the Way Principal Engineers Actually Read Them

A practitioner-level reference on domain-specific review discipline, grounded in published standards (OWASP Top 10:2025, SLSA, ADR/RFC practice) and engineering literature from Google, AWS, Microsoft, Stripe, Cloudflare, and the open-source security community.

Series: 5 Volumes · Volume 2 of 5 July 2026

## **Contents**

Section 3 — Architecture Review

- 3.1 What architecture review actually looks for in a diff

- 3.2 Service and API boundary changes

- 3.3 Event contracts and schema evolution

- 3.4 Database migration boundary concerns

Section 4 — Security Review

- 4.1 The OWASP Top 10:2025 lens

- 4.2 AuthN, AuthZ, and session management

4.3 AI-era attack surfaces: prompt and agent injection, MCP, A2A

4.4 Supply chain: SBOM, SLSA, Sigstore, signed commits

4.5 Manual vs. automated security checklist

Section 5 — Infrastructure Review

- 5.1 Terraform, Pulumi, CloudFormation review

- 5.2 Kubernetes, Helm, and Dockerfiles

5.3 CI/CD pipeline review (GitHub Actions, GitLab CI, ArgoCD, Flux)

5.4 Zero Trust, RBAC, cost, and autoscaling

Section 6 — Database Review

Section 7 — API Review (REST, GraphQL, gRPC, Async)

Section 8 — Documentation Review

Section 9 — ADR-Driven Development Section 10 — RFC-Driven Engineering

About This Series

## **Section 3 — Architecture Review**

Architecture review inside a PR is not a separate ceremony from code review — it is a different lens applied to the same diff. A reviewer doing architecture review is asking whether this change is consistent with decisions the organization has already made, and whether it's creating a new decision that hasn't been recorded anywhere.

### **3.1 What Architecture Review Actually Looks For**

- <sup>**ADR/RFC references**— does the PR description link to the design doc or decision record that justifies this</sup> approach? A PR introducing a new dependency direction, a new data store, or a new cross-service call pattern without a linked ADR is a signal to slow down, not a formality to skip.

- <sup>**Sequence and event-flow correctness**— for anything asynchronous, does the diff match the sequence</sup> diagram in the design doc, or has the implementation quietly diverged from what was agreed?

- <sup>**Dependency direction**— does this change introduce a dependency that violates the intended layering (e.g., a</sup> domain-layer module now importing from an infrastructure-layer module)?

- <sup>**Bounded-context integrity**— in a DDD-organized system, does this change respect the boundary of the</sup> domain that owns the data, or does it reach across a boundary to read or write another domain's internal model directly instead of going through its published interface?

- <sup>**Microservice granularity**— is this PR growing an existing service in a way that blurs its single responsibility,</sup> effectively merging two services' concerns into one deployable unit?

### **3.2 Service and API Boundary Changes**

The riskiest class of architectural change is one that alters a boundary other teams depend on without those teams being aware it happened. Reviewers at this layer check: is this API change additive or breaking; is there a deprecation window; has the change been announced to known consumers; and — critically — does the reviewer actually know who the consumers are, or is that knowledge missing entirely (a common and dangerous gap in fast-growing polyrepo organizations without a service catalog).

### **3.3 Event Contracts and Schema Evolution**

For event-driven systems (Kafka, Kinesis, Pub/Sub, or similar), the review question is whether a schema change is compatible with every consumer still running the old schema — not just the producer's own tests. Consumer-driven contract testing (e.g., Pact-style contracts) is the mechanism mature organizations use to make this checkable in CI rather than dependent on a reviewer's memory of who consumes a topic.

- <sup>Adding an optional field to an event schema is generally safe; removing or renaming a field, or changing a field's</sup> type or semantic meaning, is generally breaking and needs a versioned schema or a dual-publish transition period.

- <sup>Schema registries (Confluent Schema Registry, AWS Glue Schema Registry) that enforce compatibility modes</sup> (backward, forward, full) at the CI/publish level turn this from a review-time judgment call into an automated gate — the more mature pattern.

### **3.4 Database Migration Boundary Concerns**

Architecture review and database review overlap heavily here: a schema migration that looks correct in isolation can still be an architectural regression if it couples two services to the same physical schema, re-introducing the tight coupling that a service boundary was meant to remove in the first place. See Section 6 for migration mechanics.

## **Section 4 — Security Review**

Security review operates on two tracks simultaneously: automated scanning that runs on every PR regardless of content, and targeted human review triggered by risk signals (auth changes, new external inputs, new dependencies, new data stores touching regulated data). The OWASP Top 10:2025 release reorganized the landscape in ways that materially change what a security reviewer should be looking for versus the prior 2021 edition.

### **4.1 The OWASP Top 10:2025 Lens**

#### **OWASP Top 10:2025 — What Changed and Why It Matters to Reviewers**

|**Category**|**Reviewer Implication**|
|---|---|
|A01 — Broken Access Control|Still #1. Now absorbs Server-Side Request Forgery (SSRF), which was<br/>previously its own category — reflecting that SSRF is fundamentally an<br/>access-control failure (the server accessing a resource it shouldn't on the<br/>attacker's behalf).|
|A02 — Security Misconfiguration|Jumped from #5 to #2, now affecting a measurably larger share of tested<br/>applications — a direct consequence of the shift to cloud-native,<br/>config-heavy infrastructure where a single wrong IAM policy or open<br/>bucket is catastrophic.|
|A03 — Software Supply Chain<br/>Failures|New top-3 category, expanding the old "vulnerable components" category<br/>to the full pipeline: compromised dependencies, tampered build steps,<br/>stolen signing keys, and over-permissive CI/CD integrations. Ranked #1<br/>by over half of practitioners surveyed for the standard.|
|A04 — Cryptographic Failures|Dropped from #2 to #4 as baseline TLS/crypto hygiene has improved<br/>industry-wide, but remains a hard blocker whenever a reviewer sees<br/>custom cryptography or a legacy cipher suite.|
|A05 — Injection|Fell from #3 to #5 — still critical, but no longer the dominant category as<br/>parameterized queries and modern ORMs have closed off much of the<br/>easy surface.|
|A10 — Mishandling of Exceptional<br/>Conditions (new)|A new category covering improper error handling, logic errors, and<br/>fail-open conditions — the class of bug where a system's behavior under<br/>failure is itself the vulnerability, not a component the system depends on.|

*Source: OWASP Top 10:2025 official release (owasp.org/Top10/2025). The 2025 edition also flags, as a forward-looking "next steps" item rather than a ranked category, the risk of unreviewed AI-generated code being merged without a human fully understanding its logic.*

### **4.2 AuthN, AuthZ, and Session Management**

- <sup>Every new endpoint: is authorization checked at the resource level, not just "is the user logged in"? The most</sup> common real-world finding is an endpoint that checks authentication but not whether *this* authenticated user is allowed to act on *this specific* resource — classic broken object-level authorization.

- <sup>Token handling: are JWTs validated for signature, issuer, audience, and expiry on every use, not just decoded</sup> and trusted?

- <sup>Session fixation and rotation: does a privilege change (e.g., login, password reset) rotate the session identifier?</sup>

- <sup>RBAC/ABAC model correctness: does a new role or permission actually map to the intended resource scope, or</sup> does it accidentally grant broader access than described in the PR?

- <sup>Multi-tenancy isolation: for shared-infrastructure SaaS systems, is tenant ID enforced at the query layer (not just</sup> the application layer), so a bug elsewhere in the code cannot leak cross-tenant data?

### **4.3 AI-Era Attack Surfaces**

- <sup>**Prompt injection**— user-controlled or externally-fetched text that enters a system prompt or tool-calling</sup> context without clear delimiting; a reviewer should be able to point to exactly where trusted instructions end and untrusted content begins.

- <sup>**Agent injection**— the multi-step analog of prompt injection, where a malicious instruction embedded in a</sup> document, webpage, or tool result causes an agent to take an unintended action later in its reasoning chain, not just produce bad text.

- <sup>**MCP (Model Context Protocol) security**— does a newly integrated MCP server request more tool scope than</sup> the task needs; is the server's identity and provenance verified before granting it access to sensitive tools or data?

- <sup>**A2A (agent-to-agent) trust boundaries**— when one agent's output becomes another agent's input, is that</sup> boundary treated as untrusted external input (validated, scoped) or implicitly trusted because "it's our own system"? The latter is the mistake reviewers should catch.

### **4.4 Supply Chain: SBOM, SLSA, Sigstore, Signed Commits**

Software supply chain review has become one of the highest-leverage areas of security review, driven by a string of high-profile 2025 incidents — a self-propagating npm worm that compromised hundreds of downstream packages by harvesting maintainer credentials, and a compromised GitHub Action that was pinned by tag rather than commit SHA, silently pulling malicious code into tens of thousands of repositories the moment its tag was overwritten.

#### **Supply-Chain Controls a Reviewer Should Expect to See**

|**Control**|**What It Provides**|
|---|---|
|SBOM (Software Bill of Materials)|An inventory of every component in a build — the "ingredient list."<br/>Reviewers should expect a signed SBOM (CycloneDX or SPDX format)<br/>generated as part of every release build, not reconstructed after the fact.|
|SLSA (Supply-chain Levels for<br/>Software Artifacts)|A framework, originally developed inside Google and now under the<br/>OpenSSF, defining build-integrity levels. Level 2 (hosted build service,<br/>signed provenance) is the realistic near-term target for most production<br/>software; Level 3 (hermetic, isolated builds with non-falsifiable<br/>provenance) is the bar for regulated or high-risk components.|

|**Control**|**What It Provides**|
|---|---|
|Sigstore (cosign, Fulcio, Rekor)|The standard open-source toolchain for keyless artifact signing: Fulcio<br/>issues short-lived certificates tied to an OIDC identity, Cosign signs the<br/>artifact, and Rekor records the signing event in an immutable transparency<br/>log — removing the operational burden of managing long-lived signing<br/>keys.|
|Pinning by commit SHA, not tag|The single highest-leverage low-cost control after the 2025<br/>compromised-GitHub-Action incidents: a tag can be silently repointed by a<br/>compromised maintainer account; a commit SHA cannot.|

*Sources: SLSA specification (slsa.dev), Sigstore project documentation, OWASP Top 10:2025 A03 category writeup.*

### **4.5 Manual vs. Automated Security Checklist**

#### **Manual Checklist (Human Judgment Required)**

- <sup>Does this endpoint check resource-level authorization, not just authentication?</sup>

- <sup>Is every secret pulled from a secrets manager, never hardcoded or logged?</sup>

- <sup>Is user input that reaches a shell, SQL query, or template engine parameterized or escaped?</sup>

- <sup>Does a new external call have a defined trust boundary and input validation at that boundary?</sup>

- <sup>Is PII classified and handled according to its classification (encryption, retention, access logging)?</sup>

- <sup>For a new dependency: is it from a vetted source, pinned to a specific version, and does its provenance check</sup> out (not typosquatting an established package)?

#### **Automated Checklist (Should Never Depend on a Human Remembering)**

- <sup>SAST (static analysis) findings on the diff, surfaced inline in the review tool.</sup>

- <sup>Secret-scanning pre-commit and pre-merge, blocking on any match.</sup>

- <sup>Dependency / SCA scanning against known-vulnerability databases (NVD, OSV.dev).</sup>

- <sup>DAST or fuzz testing against staging environments for externally-facing endpoints.</sup>

- <sup>SBOM generation and signature verification as a required CI step, not optional tooling.</sup>

- <sup>License scanning to catch copyleft-incompatible dependencies before they ship.</sup>

## **Section 5 — Infrastructure Review**

### **5.1 Terraform, Pulumi, CloudFormation Review**

- <sup>**Plan output review, not just diff review**— the actual risk in an IaC PR is often invisible in the code diff and</sup> only visible in the `terraform plan` output (e.g., a change that looks like a rename in code but is actually a destroy-and-recreate at the provider level).

- <sup>**State and blast radius**— does this change affect a shared module used by multiple environments, meaning a</sup> single merge could quietly change production and staging simultaneously?

- <sup>**Least-privilege IAM**— is a new IAM policy scoped to specific resources and actions, or does it use a wildcard</sup> (`*`) that will be flagged in every future security audit?

- <sup>**Secrets in state**— does this introduce a resource whose sensitive output (a generated password, a private</sup> key) will be stored in plaintext in Terraform state unless explicitly marked sensitive and the backend encrypted?

**This is Part 1 of 2. [Continue with Part 2 →](pathname:///archon/agentic-systems/coding-tools/parts/43-pr-review-handbook-vol2-deep-domain-reviews-part2) for continued content.**
