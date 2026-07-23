---
doc_type: reference-architecture
domain: architecture
topic_id: mcp-a2a-protocol-deep-dive
title: "MCP & A2A Protocol Deep Dive (2026)"
date_created: 2026-07-05
last_reviewed: 2026-07-23
status: current
covers_version: "as of 2026-07-10"
aliases:
  - mcp protocol deep dive
  - a2a protocol deep dive
  - agent interoperability protocols
supersedes:
  - docs/enterprise-architecture/ai-architecture/mcp-a2a-protocol-deep-dive.md
tags:
  - enterprise-ai-architect
  - protocols
  - mcp
  - a2a
  - agentic-systems
---

# MCP & A2A Protocol Deep Dive (2026)

> **Current as of July 2026.** This guide covers the two protocols that define the agentic interoperability layer — MCP (agent↔tool) and A2A (agent↔agent) — with a focus on the **MCP 2026-07-28 revision** (stateless core, Extensions, Tasks, MCP Apps) and **A2A v1.x** (Signed Agent Cards, multi-tenancy, AP2). It is Volume 3 of the harness architecture series ([Vol 1: Harness & Orchestration](./44-ai-harness-architecture-orchestration.md); [Vol 4: Memory & Planning](./41-agent-memory-planning-architecture.md)).

---

## 1. Protocol State (July 2026)

```mermaid
graph TB
    A["Client Agent<br/>(orchestrator)"]
    B["MCP Gateway<br/>(auth, routing,<br/>rate limit)"]
    C["MCP Server<br/>(tool provider)"]
    D["Tool Execution<br/>(external system)"]
    E["Remote Agent<br/>(A2A peer)"]
    
    A -->|tools/list, tools/call| B
    B -->|request| C
    C -->|execute| D
    D -->|result| C
    C -->|response| B
    B -->|tool result| A
    
    A -->|task submit| E
    E -->|task result| A
```

**MCP agent↔tool interoperability (stateless, 2026-07-28):** Agent invokes tools via MCP gateway; A2A enables agent↔agent delegation for long-running tasks or specialized capabilities.

| | MCP | A2A |
| --- | ----- | ----- |
| **Current version** | 2025-11-25 (finalized) | v1.x (v1.0 early 2026) |
| **Incoming** | 2026-07-28 (RC locked 2026-05-21; finalizes this month) — largest revision since launch | Point releases on the v1 line |
| **Governance** | Linux Foundation — Agentic AI Foundation | Linux Foundation — Agentic AI Foundation (Google-donated, June 2025; IBM's ACP merged in Aug 2025) |
| **Scale** | ~10⁴ public servers; SDKs at ~10⁸ monthly downloads; official MCP Registry near 2,000 entries within months of launch | 150+ organizations in production (Microsoft, AWS, Google, Salesforce, SAP, ServiceNow, Deutsche Bank) |
| **Positioning** | De facto agent↔**tool** layer | De facto agent↔**agent** layer — complementary, same foundation |

---

## 2. MCP 2026-07-28: The Changes to Design Against

The 2026-07-28 release is the largest revision since MCP launched. Six changes matter architecturally:

### 2.1 Stateless Core

Protocol sessions and `Mcp-Session-Id` are **removed**; the `initialize` handshake is removed — version and capabilities travel in `_meta` per request, with `server/discover` for upfront capability fetch. Servers must survive round-robin load balancing; a remote MCP server that previously needed sticky sessions and a shared session store can now run behind a plain HTTP load balancer.

**Consequence:** hidden per-connection state must become explicit, client-visible **handles/scopes**. And since the protocol no longer owns sessions, *session semantics move fully into your harness* — own them explicitly with signed, expiring session/state handles (see [Vol 1 §2, Session Manager](./44-ai-harness-architecture-orchestration.md)).

### 2.2 Mandatory Routing Headers

`Mcp-Method` and `Mcp-Name` are now mandatory on Streamable HTTP. Gateways can route and rate-limit on headers **without body parsing**; servers must reject header/body mismatch (an integrity check). This is what makes gateway-level governance of MCP traffic cheap at scale.

### 2.3 Extensions Framework

Reverse-DNS-identified, independently versioned extensions negotiated via capability maps. Two ship with the release:

- **Tasks** — long-running async work: a server can answer `tools/call` with a task handle; the client drives it with `tasks/get` / `tasks/update` / `tasks/cancel`. Replaces blocking waits. Task creation is server-directed: the client advertises the extension, the server decides when a call runs as a task.
- **MCP Apps** — server-shipped HTML UI rendered in sandboxed iframes, with **pre-declared, cacheable, reviewable templates**. Tools declare UI templates ahead of time so hosts can prefetch, cache, and security-review them before anything runs.

### 2.4 Deprecations (annotation-only, ≥12-month window)

| Deprecated | Migrate to |
| ----------- | ----------- |
| **Sampling** (server borrows client's LLM) | Direct provider calls via your AI gateway |
| **Roots** | Explicit tool params / resource URIs |
| **Logging** | OpenTelemetry |

Design your client SDK wrapper to abstract both the 2025-11-25 and 2026-07-28 lifecycles during the 12-month overlap.

### 2.5 Client-Side Caching Standardized

`ttlMs` + `cacheScope` on list/read results. `cacheScope` exists to prevent cross-user cache leaks — in multi-tenant deployments, per-tenant `cacheScope` is mandatory, not optional.

### 2.6 Authorization Hardening & Tracing

- RFC 9207 `iss` validation, AS-bound client credentials, declared `application_type` in Dynamic Client Registration.
- **W3C Trace Context in `_meta`** (traceparent/tracestate/baggage) — end-to-end distributed tracing through MCP hops is now spec-level, closing the observability gap across the agent → gateway → server chain.

---

## 3. Lifecycle, Transport, Interaction Semantics

**Lifecycle:** 2025-11-25 = initialize → operation → shutdown. 2026-07-28 = per-request `_meta` self-description with capability discovery on demand.

**Transports:** stdio (local servers — subprocess); Streamable HTTP (remote — POST with optional SSE response streaming for progress/partial results).

**Streaming, progress, cancellation:** long operations emit progress notifications (progress tokens); `notifications/cancelled` propagates cancellation. Your harness must map task-level cancel → in-flight MCP cancels → Tasks-extension cancels. Untracked orphan operations are a cost *and* safety leak.

**Tool metadata:** name, JSON Schema for inputs/outputs, descriptions, annotations (read-only/destructive hints). Treat annotations as **untrusted hints, never security controls**. Precise schemas materially improve model call accuracy; over-strict validation becomes its own DoS.

**Resources / Prompts / Elicitation:** resources = addressable context (URI, subscribable); prompts = server-provided templates; elicitation = server requests structured user input mid-operation (form/url modes) — powerful for HITL but a phishing surface: hosts must render origin clearly.

---

## 4. Discovery, Registry, Versioning, Trust

**Registry-of-record doctrine.** The enterprise pattern: run a **private registry-of-record** that mirrors/allowlists external entries after security review; clients may only resolve servers through it. A registry entry carries:

```
{owner, version, risk class, auth config, tool manifest hash,
 sandbox profile, data classification, approved tenants}
```

Anything not in the registry is unsanctioned by definition. This mirrors the consensus pattern reported from production MCP-gateway operators (Uber's platform team, running tens of thousands of agent executions weekly through an internal MCP gateway, at the April 2026 AAIF MCP Dev Summit): one gateway for identity, policy, redaction, audit; one registry as source of truth.

**Versioning & rug-pull defense:** date-based spec versions + per-server semver; pin server versions in production. **Tool-manifest hash pinning** detects rug-pulls — a server silently changing tool descriptions/behavior post-approval is a documented attack class. Re-review on any manifest change.

**Tool trust tiers:**

| Tier | Definition | Allowed use |
| ------ | ----------- | ------------- |
| **T0** | Internal first-party | Full access per policy |
| **T1** | Vetted vendor | Approved data classes, contract-backed |
| **T2** | Community | Sandboxed, read-only, no sensitive data |
| **T3** | Unvetted | Blocked |

---

## 5. MCP Security

For the full threat catalog and treatment stages, see [Security Architecture & Guardrails](../trust/04-agentic-ai-security-guardrails.md). The MCP-specific surfaces:

**Prompt injection — three vectors:** (a) **tool descriptions** (malicious instructions in the manifest read into context), (b) **tool results** (retrieved content carrying instructions — indirect injection), (c) **rug-pull updates**. Controls: manifest review + hash pinning; result screening at the tool gateway; provenance-tag tool output as untrusted data; least privilege so a hijacked call can't matter; and the **"lethal trifecta" rule** — never combine private-data access + untrusted content + external egress in one agent context without approval gates.

**Confused deputy / token theft:** enforce RFC 8707 audience binding, no token passthrough, per-server OAuth clients.

**Stateless-world risks:** state handles must be unguessable, user-bound, expiring, and server-validated per use. Replaying a handle pasted into a ticket must fail.

**MCP Apps threat surface:** server-controlled HTML in the host (IDE) → XSS, UI mimicry of native auth prompts, clickjacking. Controls: template pre-declaration + review + caching, strict iframe sandboxing/CSP, **no credential entry into server-rendered UI ever**, endpoint-level monitoring (network gateways cannot see this surface).

**Tasks DoS:** cheap-to-create/expensive-to-run async tasks → per-principal task quotas, cost-based admission, orphan reaping.

**Sandboxing:** local servers in containers/microVMs with read-only FS, no ambient creds, egress allowlist; remote servers behind your MCP gateway.

### Deployment Topologies

| Topology | Trust profile | Guidance |
| ---------- | -------------- | ---------- |
| **Local (stdio)** | = host-level code execution | Dev/desktop only; signed packages; deny in server-side prod |
| **Remote (HTTP)** | Network boundary; OAuth | Default for production |
| **Enterprise/private** | Behind gateway; workforce IdP; private registry | Standard for internal systems of record |
| **Shared/public SaaS MCP** | Vendor-operated (e.g., official vendor servers) | Contract + tier review; audience-bound tokens |
| **Multi-tenant MCP** | One server, many tenants | Tenant claim in token → row/namespace isolation server-side; per-tenant `cacheScope`; pen-test tenant bleed explicitly |

---

## 6. A2A Deep Dive

### 6.1 Core Model

**Agent Card:** JSON self-description at a well-known URL — identity, endpoint(s), capability advertisement (skills with descriptions/modalities), auth requirements (OAuth/API key/mTLS schemes), streaming support, version. **Signed Agent Cards** (v1.0) add a cryptographic signature verifying domain-owner issuance — the control against card forgery/redirection attacks. Verification is mandatory in zero-trust postures.

**Task lifecycle:** client agent submits a task → states: `submitted → working → input-required → completed/failed/cancelled`. **Messages** carry conversational turns; **Artifacts** carry typed outputs. Long-running tasks stream state via SSE or push notifications; tasks are addressable (`get`/`cancel`/`resubscribe`) — this is what makes cross-agent work *governable* rather than chat.

**Negotiation:** modality and capability negotiation per task (text/file/structured data); version negotiation at connect (guaranteed v0.3→v1.0 migration path).

**Delegation:** the remote agent is **opaque by design** — you delegate outcomes, not implementations. Consequence: contracts (SLOs, data-handling terms, risk class) attach to the *card/skill*, and your platform enforces them at the A2A edge.

### 6.2 Discovery, Trust, Federation

**Discovery:** well-known URI on the agent's domain; enterprise catalog/registry of approved cards (internal "agent directory"); private marketplace patterns emerging. Same registry-of-record doctrine as MCP.

**Trust establishment sequence:**

1. Verify card signature
2. mTLS / OAuth per the card's declared scheme, with your STS-issued, audience-bound tokens
3. Check catalog entitlement (is this counterparty approved for this data class / this tenant?)
4. Runtime DLP on egress payloads

Identity here is *organizational* trust, distinct from intra-platform workload identity ([Agentic AI Security & Identity](../trust/05-agentic-ai-security-identity.md)).

**Cross-org federation:** treat each partner as a separate trust domain — SPIFFE or OIDC federation for workload trust; contractual allowlist of skills; **artifact-only exchange** (no raw internal context); asymmetric disclosure (send minimum necessary); per-partner audit streams.

**Failure & recovery across org boundaries:** tasks are durable references — after a network partition, reconcile by polling `tasks/get` rather than resubmitting; resubmission only with the same idempotency semantics; cancellation is best-effort → design compensations for "cancel arrived too late." You cannot roll back inside the partner — compensations run on your side.

---

## 7. MCP vs. A2A: Decision Table

| Question | MCP | A2A |
| ---------- | ----- | ----- |
| **Unit of interaction** | Tool call / resource read | Task with lifecycle |
| **Counterparty** | Deterministic capability | Autonomous (opaque) agent |
| **Typical latency** | ms–s (Tasks ext. for longer) | s–days |
| **Trust artifact** | Registry entry + manifest hash | Signed Agent Card + contract |
| **Use when** | You want *this specific action* done | You want *this outcome* achieved by a peer |

---

## 8. Enterprise Protocol Adoption Lifecycle

| Stage | MCP actions | A2A actions | Exit criteria |
| ------- | ------------ | ------------- | --------------- |
| **1. Evaluate** | Inventory candidate servers; classify by trust tier (T0–T3); threat-model | Identify internal/external agent counterparties; review card schemas | Protocol fit confirmed vs. decision table |
| **2. Pilot** | 1–2 T0/T1 servers behind a gateway in sandboxed domain; stdio denied server-side | Internal-only A2A between two owned agents; unsigned cards acceptable inside one trust domain | Telemetry + policy enforcement demonstrated end-to-end |
| **3. Private registry** | Stand up registry-of-record; manifest hash pinning; allowlist mirroring; CI re-review on manifest change | Governed agent catalog; card signing required for anything crossing a domain | Nothing resolvable outside the registry |
| **4. Production** | Gateway mandatory (route on Mcp-Method/Mcp-Name); per-tenant cacheScope; Tasks quotas; version pinning | Signed cards verified; entitlement checks per call; DLP on egress; idempotent task submission | SLOs + audit + kill-switch tested |
| **5. Federation** | Vendor SaaS MCP servers under contract + tier review | Cross-org A2A with SPIFFE/OIDC federation, skill allowlists, artifact-only exchange, per-partner audit | Partner trust domains contractually and technically bounded |
| **6. Continuous governance** | Registry diff alerts; deprecation migration (Sampling/Roots/Logging by mid-2027); spec-version upgrades | Card rotation/re-signing; contract renewal gates; counterparty reviews | Quarterly re-certification cadence |

---

## 9. How Industry Implements

**Microsoft** — Copilot Studio's A2A support went GA in April 2026; Azure AI Foundry and Microsoft Agent Framework (.NET) ship A2A v1 support, making cross-platform agent communication a framework primitive rather than custom plumbing.

**AWS** — Bedrock AgentCore Runtime hosts A2A agents and fronts tools through its MCP-compatible Gateway; the AgentCore service decomposition (Runtime/Memory/Gateway) is the managed-harness reference implementation.

**Google** — Donated A2A to the Linux Foundation (June 2025); Google ADK and the Gemini Enterprise Agent Platform implement both protocols; the Linux Foundation reports 150+ organizations in production within the first year, including enterprise deployments at Deutsche Bank.

**Salesforce** — Agentforce exposes every custom agent as an A2A endpoint; partner agents can be invoked directly from Flow — A2A as the integration surface for an entire SaaS ecosystem.

**SAP & ServiceNow** — SAP Joule uses A2A to connect SAP's enterprise agents to external orchestrators; ServiceNow is among the production adopter cohort — the "system-of-record agents as A2A counterparties" pattern.

**Gateway/registry ecosystem** — The MCP Registry reached ~2,000 server entries within months of launch. Production operators converge on the same architecture: an MCP gateway in front of every registered server as the point of discovery, authentication, RBAC, and request-level tracing — the surface where MCP Apps content is screened and Task lifecycles are bounded. Uber's platform team (tens of thousands of agent executions weekly through their internal gateway) publicly frames gateways and registries as doing "most of the real work."

**Payments** — **AP2 (Agent Payments Protocol)** ships as a formal A2A extension for cryptographically-evidenced agent commerce (see the broader agent interoperability landscape for the payments architecture).

---

## 10. Architect's Checklist

- [ ] Client SDK wrapper abstracts 2025-11-25 and 2026-07-28 MCP lifecycles during the overlap window
- [ ] Migration plans filed for Sampling → AI gateway, Roots → explicit params, Logging → OTel
- [ ] Private MCP registry-of-record with manifest hash pinning; re-review triggered on manifest change
- [ ] Trust tiers T0–T3 assigned to every server; tier gates data-class access
- [ ] Per-tenant `cacheScope` everywhere; tenant-bleed pen test scheduled
- [ ] State handles: unguessable, user-bound, expiring, validated per use
- [ ] Tasks extension: per-principal quotas, cost-based admission, orphan reaping
- [ ] MCP Apps: template review pipeline, iframe sandbox/CSP, no-credential-entry rule
- [ ] A2A: card signature verification mandatory; entitlement check per call; DLP on egress
- [ ] Cross-org: artifact-only exchange, idempotent submission, compensation paths for late cancels
- [ ] Harness maps task-level cancel → MCP `notifications/cancelled` → Tasks cancels → A2A `tasks/cancel`

---

## Sources

- [MCP Blog — The 2026-07-28 Specification Release Candidate](https://blog.modelcontextprotocol.io/posts/2026-07-28-release-candidate/)
- [WorkOS — Everything your team needs to know about MCP in 2026](https://workos.com/blog/everything-your-team-needs-to-know-about-mcp-in-2026)
- [TrueFoundry — Governing MCP Apps and Tasks at the Gateway](https://www.truefoundry.com/blog/mcp-apps-tasks-gateway-governance)
- [A2A Protocol — Announcing Version 1.0](https://a2a-protocol.org/latest/announcing-1.0/)
- [Linux Foundation — A2A Protocol Surpasses 150 Organizations](https://www.linuxfoundation.org/press/a2a-protocol-surpasses-150-organizations-lands-in-major-cloud-platforms-and-sees-enterprise-production-use-in-first-year)
- [Microsoft — A2A v1 in Microsoft Agent Framework for .NET](https://devblogs.microsoft.com/agent-framework/a2a-v1-is-here-cross-platform-agent-communication-in-microsoft-agent-framework-for-net/)
- [Stellagent — A2A Protocol: 150+ Organizations in One Year](https://stellagent.ai/insights/a2a-protocol-google-agent-to-agent)
- [Digital Applied — MCP Dev Summit 2026 Readout](https://www.digitalapplied.com/blog/mcp-dev-summit-2026-readout-protocol-roadmap-analysis)
- Volume 3, *Multi-Agent AI Harness Architecture (2026) — Production Reference Guide*
