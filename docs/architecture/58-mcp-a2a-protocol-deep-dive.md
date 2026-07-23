---
title: "MCP & A2A Protocol Deep Dive (2026)"
date_created: 2026-07-05
last_reviewed: 2026-07-10
status: current
source_type: native-md
source_file: ""
tags: ["architecture", "protocols", "mcp", "a2a"]
doc_type: reference-architecture
covers_version: "as of 2026-07-10"
domain: architecture
topic_id: mcp-a2a-protocol-deep-dive
supersedes:
  - docs/enterprise-architecture/ai-architecture/mcp-a2a-protocol-deep-dive.md
---

# MCP & A2A Protocol Deep Dive (2026)

**Current as of July 2026.** This guide covers the two protocols that define the agentic interoperability layer — MCP (agent↔tool) and A2A (agent↔agent) — with a focus on the **MCP 2026-07-28 revision** (stateless core, Extensions, Tasks, MCP Apps) and **A2A v1.x** (Signed Agent Cards, multi-tenancy, AP2).

---

## 1. Protocol State (July 2026)

| | MCP | A2A |
| --- | ----- | ----- |
| **Current version** | 2025-11-25 (finalized) | v1.x (v1.0 early 2026) |
| **Incoming** | 2026-07-28 (RC locked; largest revision since launch) | Point releases on the v1 line |
| **Governance** | Linux Foundation — Agentic AI Foundation | Linux Foundation — Agentic AI Foundation (Google-donated, June 2025) |
| **Scale** | ~10⁴ public servers; ~10⁸ monthly downloads; official MCP Registry near 2,000 entries | 150+ organizations in production |
| **Positioning** | De facto agent↔**tool** layer | De facto agent↔**agent** layer — complementary, same foundation |

---

## 2. MCP 2026-07-28: The Changes to Design Against

### 2.1 Stateless Core

Protocol sessions and `Mcp-Session-Id` are **removed**; the `initialize` handshake is removed — version and capabilities travel in `_meta` per request, with `server/discover` for upfront capability fetch. Servers must survive round-robin load balancing.

**Consequence:** hidden per-connection state must become explicit, client-visible **handles/scopes**. Session semantics move fully into your harness — own them explicitly with signed, expiring session/state handles.

### 2.2 Mandatory Routing Headers

`Mcp-Method` and `Mcp-Name` are now mandatory on Streamable HTTP. Gateways can route and rate-limit on headers **without body parsing**; servers must reject header/body mismatch. This makes gateway-level governance of MCP traffic cheap at scale.

### 2.3 Extensions Framework

Reverse-DNS-identified, independently versioned extensions negotiated via capability maps. Two ship with the release:

- **Tasks** — long-running async work: a server can answer `tools/call` with a task handle; the client drives it with `tasks/get` / `tasks/update` / `tasks/cancel`. Replaces blocking waits.
- **MCP Apps** — server-shipped HTML UI rendered in sandboxed iframes, with pre-declared, cacheable, reviewable templates.

### 2.4 Client-Side Caching Standardized

`ttlMs` + `cacheScope` on list/read results. `cacheScope` exists to prevent cross-user cache leaks — in multi-tenant deployments, per-tenant `cacheScope` is mandatory.

### 2.5 Authorization Hardening & Tracing

- RFC 9207 `iss` validation, AS-bound client credentials
- **W3C Trace Context in `_meta`** — end-to-end distributed tracing through MCP hops

### 2.6 Migration Strategy

Design your client SDK wrapper to abstract both the 2025-11-25 and 2026-07-28 lifecycles during the 12-month overlap.

---

## 3. Lifecycle, Transport, Interaction Semantics

**Lifecycle:** 2025-11-25 = initialize → operation → shutdown. 2026-07-28 = per-request `_meta` self-description with capability discovery on demand.

**Transports:** stdio (local servers — subprocess); Streamable HTTP (remote — POST with optional SSE response streaming for progress/partial results).

**Streaming, progress, cancellation:** long operations emit progress notifications (progress tokens); `notifications/cancelled` propagates cancellation. Your harness must map task-level cancel → MCP cancels → Tasks-extension cancels. Untracked orphan operations are a cost *and* safety leak.

**Tool metadata:** name, JSON Schema for inputs/outputs, descriptions, annotations (read-only/destructive hints). Treat annotations as **untrusted hints, never security controls**.

---

## 4. Discovery, Registry, Versioning, Trust

**Registry-of-record doctrine.** The enterprise pattern: run a **private registry-of-record** that mirrors/allowlists external entries after security review; clients may only resolve servers through it. A registry entry carries:

```
{owner, version, risk class, auth config, tool manifest hash,
 sandbox profile, data classification, approved tenants}
```

Anything not in the registry is unsanctioned by definition.

**Versioning & rug-pull defense:** date-based spec versions + per-server semver; pin server versions in production. **Tool-manifest hash pinning** detects rug-pulls — a server silently changing tool descriptions/behavior post-approval is a documented attack class.

**Tool trust tiers:**

| Tier | Definition | Allowed use |
| ------ | ----------- | ------------- |
| **T0** | Internal first-party | Full access per policy |
| **T1** | Vetted vendor | Approved data classes, contract-backed |
| **T2** | Community | Sandboxed, read-only, no sensitive data |
| **T3** | Unvetted | Blocked |

---

## 5. MCP Security

**Prompt injection — three vectors:** (a) tool descriptions (malicious instructions in the manifest read into context), (b) tool results (retrieved content carrying instructions — indirect injection), (c) rug-pull updates. Controls: manifest review + hash pinning; result screening at the tool gateway; provenance-tag tool output as untrusted data; and the **"lethal trifecta" rule** — never combine private-data access + untrusted content + external egress in one agent context without approval gates.

**Confused deputy / token theft:** enforce RFC 8707 audience binding, no token passthrough, per-server OAuth clients.

**Stateless-world risks:** state handles must be unguessable, user-bound, expiring, and server-validated per use. Replaying a handle pasted into a ticket must fail.

**MCP Apps threat surface:** server-controlled HTML in the host (IDE) → XSS, UI mimicry of native auth prompts, clickjacking. Controls: template pre-declaration + review + caching, strict iframe sandboxing/CSP, **no credential entry into server-rendered UI ever**.

**Tasks DoS:** cheap-to-create/expensive-to-run async tasks → per-principal task quotas, cost-based admission, orphan reaping.

**Sandboxing:** local servers in containers/microVMs with read-only FS, no ambient creds, egress allowlist; remote servers behind your MCP gateway.

### Deployment Topologies

| Topology | Trust profile | Guidance |
| ---------- | -------------- | ---------- |
| **Local (stdio)** | = host-level code execution | Dev/desktop only; deny in server-side prod |
| **Remote (HTTP)** | Network boundary; OAuth | Default for production |
| **Enterprise/private** | Behind gateway; workforce IdP; private registry | Standard for internal systems of record |
| **Multi-tenant MCP** | One server, many tenants | Per-tenant `cacheScope`; pen-test tenant bleed explicitly |

---

## 6. A2A Deep Dive

### 6.1 Core Model

**Agent Card:** JSON self-description at a well-known URL — identity, endpoint(s), capability advertisement (skills with descriptions/modalities), auth requirements (OAuth/API key/mTLS schemes), streaming support, version. **Signed Agent Cards** (v1.0) add a cryptographic signature verifying domain-owner issuance.

**Task lifecycle:** client agent submits a task → states: `submitted → working → input-required → completed/failed/cancelled`. **Messages** carry conversational turns; **Artifacts** carry typed outputs. Long-running tasks stream state via SSE or push notifications.

**Negotiation:** modality and capability negotiation per task (text/file/structured data); version negotiation at connect (guaranteed v0.3→v1.0 migration path).

**Delegation:** the remote agent is **opaque by design** — you delegate outcomes, not implementations. Consequence: contracts (SLOs, data-handling terms, risk class) attach to the card/skill.

### 6.2 Discovery, Trust, Federation

**Discovery:** well-known URI on the agent's domain; enterprise catalog/registry of approved cards (internal "agent directory"); private marketplace patterns emerging. Same registry-of-record doctrine as MCP.

**Trust establishment sequence:**

1. Verify card signature
2. mTLS / OAuth per the card's declared scheme, with your STS-issued, audience-bound tokens
3. Check catalog entitlement (is this counterparty approved for this data class / this tenant?)
4. Runtime DLP on egress payloads

**Cross-org federation:** treat each partner as a separate trust domain — SPIFFE or OIDC federation for workload trust; contractual allowlist of skills; **artifact-only exchange** (no raw internal context); asymmetric disclosure (send minimum necessary); per-partner audit streams.

**Failure & recovery across org boundaries:** tasks are durable references — after a network partition, reconcile by polling `tasks/get` rather than resubmitting. Resubmission only with the same idempotency semantics. Cancellation is best-effort.

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
| **3. Private registry** | Stand up registry-of-record; manifest hash pinning; allowlist mirroring | Governed agent catalog; card signing required for anything crossing a domain | Nothing resolvable outside the registry |
| **4. Production** | Gateway mandatory (route on Mcp-Method/Mcp-Name); per-tenant cacheScope; Tasks quotas; version pinning | Signed cards verified; entitlement checks per call; DLP on egress; idempotent task submission | SLOs + audit + kill-switch tested |
| **5. Federation** | Vendor SaaS MCP servers under contract + tier review | Cross-org A2A with SPIFFE/OIDC federation, skill allowlists, artifact-only exchange | Partner trust domains contractually and technically bounded |

---

## 9. How Industry Implements

**Microsoft** — Copilot Studio's A2A support went GA in April 2026; Azure AI Foundry and Microsoft Agent Framework (.NET) ship A2A v1 support.

**AWS** — Bedrock AgentCore Runtime hosts A2A agents and fronts tools through its MCP-compatible Gateway.

**Google** — Donated A2A to the Linux Foundation (June 2025); Google ADK and the Gemini Enterprise Agent Platform implement both protocols.

**Salesforce** — Agentforce exposes every custom agent as an A2A endpoint; partner agents can be invoked directly from Flow.

**SAP & ServiceNow** — SAP Joule uses A2A to connect enterprise agents; ServiceNow is among the production adopter cohort.

**Gateway/registry ecosystem** — The MCP Registry reached ~2,000 server entries within months of launch. Production operators converge on the same architecture: an MCP gateway in front of every registered server as the point of discovery, authentication, RBAC, and request-level tracing.

**Payments** — **AP2 (Agent Payments Protocol)** ships as a formal A2A extension for cryptographically-evidenced agent commerce.

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
