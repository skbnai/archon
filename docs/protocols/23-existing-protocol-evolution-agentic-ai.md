---
doc_type: reference-architecture
domain: protocols
topic_id: existing-protocol-evolution-agentic-ai
title: "Existing Protocol Evolution for Agentic AI (2025–2026)"
date_created: 2026-07-11
last_reviewed: 2026-07-11
status: current
supersedes:
  - docs/ai-protocols/standards/existing-protocol-evolution-agentic-ai.md
source_type: native-md
source_file: "Existing Protocol Evolution for Agentic AI Guide"
tags: ["ai-protocols", "http", "oauth", "dns", "tls", "json-rpc", "spiffe", "enterprise-architecture"]
audience: "Enterprise Architects, AI Platform Engineers, Security Architects"
---

# Existing Protocol Evolution for Agentic AI (2025–2026)

The agentic AI stack did not invent new transports from scratch. Instead, it extended, reinterpreted, and in some cases *finally activated* dormant features of protocols that have underpinned the web for decades. Understanding these changes helps architects audit existing infrastructure for agent readiness rather than assuming a greenfield build.

---

## 1. HTTP — The Biggest Change Surface

### 1.1 Server-Sent Events (SSE) as the Dominant Agent Streaming Transport

WebSockets lost the streaming debate for agents. SSE won.

| Dimension | WebSocket | SSE (HTTP) |
|---|---|---|
| Connection type | Bidirectional, full-duplex | Unidirectional server→client |
| Proxy / CDN compatibility | Breaks most reverse proxies | Works through nginx, Cloudflare, AWS ALB |
| Load balancer sticky sessions | Required or connection drops | Optional — reconnect is stateless |
| Reconnect after failure | Application code | Browser/client built-in (`EventSource`) |
| HTTP/2 multiplexing | Not applicable | Streams over a single TCP connection |
| TLS termination | Requires WSS upgrade | Standard HTTPS |

MCP, A2A, and AG-UI all converged on SSE for server-to-client streaming. Client-to-server remains plain HTTP POST. This "half-duplex over HTTP" pattern is now the agent streaming baseline.

```mermaid
sequenceDiagram
    participant Client
    participant Server
    Client->>Server: POST /messages
    Server-->>Client: GET /sse (text/event-stream)
    Server-->>Client: data: ("type":"TEXT_MESSAGE_CONTENT"...)
    Server-->>Client: data: ("type":"TOOL_CALL_START"...)
    Server-->>Client: data: ("type":"RUN_FINISHED"...)
```

### 1.2 `/.well-known/` URI Pattern for Agent Discovery

OIDC popularised `.well-known/openid-configuration` in 2014. Agents have adopted the same pattern:

| File | Purpose | Adopted by |
|---|---|---|
| `/.well-known/agent-card.json` | A2A capability manifest | A2A v1 spec |
| `/.well-known/agents.json` | Multi-agent registry at a domain | Community convention |
| `/agents.md` | Human + machine readable agent description (like robots.txt) | AAIF proposal 2026 |
| `/.well-known/openid-configuration` | OAuth discovery for agent auth | OAuth 2.1 + MCP |

DNS + HTTP become a distributed, zero-infrastructure agent registry. No central broker required.

### 1.3 HTTP 402 Payment Required — 30 Years Later

The `402 Payment Required` status code was defined in RFC 1945 (1996) with the note "reserved for future use." The agentic commerce layer has activated it.

**x402 protocol flow (Coinbase, 2025):**

```mermaid
sequenceDiagram
    participant Agent
    participant Service
    Agent->>Service: GET /paid-api
    Service-->>Agent: 402 Payment Required<br/>X-Payment-Required: (...)
    Agent->>Agent: Pay on-chain
    Agent->>Service: GET /paid-api<br/>X-Payment-Proof: &lt;signed-receipt&gt;
    Service-->>Agent: 200 OK
```

AP2 extends this with the `PaymentMandate` pattern — the agent pre-authorises a spending envelope rather than paying per-call, which is more practical for multi-step workflows.

### 1.4 Emerging Agent HTTP Headers

No RFC yet, but these are becoming de facto standards across MCP, A2A, and platform implementations:

```http
# Agent identity
X-Agent-ID: did:web:fraud-detector.acme.com
X-Agent-Name: fraud-detector-v2

# Task / session tracking
X-Task-ID: task-7f3a2b1c-4d5e-6f7a-8b9c
Mcp-Session-Id: sess-abc123          # MCP-specific
X-Correlation-ID: trace-root-uuid

# Delegation chain (A2A multi-hop)
X-Delegation-Chain: orchestrator → planner → executor

# Capability negotiation
X-Agent-Capabilities: tools,streaming,sampling
X-Protocol-Version: mcp/2026-07-28
```

### 1.5 HTTP/3 (QUIC) for Long-Running Agent Tasks

HTTP/2 SSE breaks on network switches because TCP head-of-line blocking stalls all streams when one packet is lost. HTTP/3 over QUIC fixes this:

- **Independent streams** — packet loss in one agent stream doesn't block others
- **0-RTT reconnect** — agent reconnects in under one round trip after a network switch
- **Connection migration** — agent's IP changes (spot instance, mobile) without dropping the task
- **Built-in TLS 1.3** — no separate TLS handshake overhead

LMOS and longer-horizon IoA protocols explicitly target HTTP/3. MCP's 2026 stateless spec is HTTP/3 compatible because session state is in headers, not the connection.

### 1.6 Rate Limiting Headers for Agent Capacity Management

Agents make rapid fan-out calls (parallelising tool calls). Standard rate limit headers gain new importance:

```http
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 847
X-RateLimit-Reset: 1720742400
Retry-After: 30
```

Enterprise platforms now expose **agent-tier rate limits** — higher burst allowances than human-tier API keys, with mandatory `Retry-After` for graceful backoff.

---

## 2. OAuth 2.0 / OIDC — Agent Delegation Extensions

### 2.1 RFC 8693 Token Exchange — The Key Primitive for Agent Chains

When Orchestrator Agent delegates a task to Sub-Agent, it cannot simply pass its own token — that would give Sub-Agent excessive privilege. RFC 8693 (Token Exchange) solves this:

```mermaid
sequenceDiagram
    participant Orchestrator
    participant AuthServer
    Orchestrator->>AuthServer: POST /token<br/>grant_type=token-exchange<br/>subject_token=&lt;orchestrator-token&gt;<br/>requested_token_type=access_token<br/>scope=fraud:read<br/>actor=did:web:sub-agent.vendor.com
    AuthServer-->>Orchestrator: 200 OK<br/>access_token: &lt;scoped-delegated-token&gt;<br/>act: (sub: did:web:sub-agent.vendor.com)
```

The resulting token carries `act` (who is acting) and `may_act` (who is authorised to act), creating a cryptographically provable delegation chain through arbitrarily deep agent hierarchies.

### 2.2 Dynamic Client Registration (RFC 7591)

Traditional OAuth requires pre-registering every client. Ephemeral agents cannot be pre-registered. RFC 7591 allows an agent to register itself at runtime:

```http
POST /register
{
  "client_name": "invoice-processing-agent-prod-7f3a",
  "grant_types": ["client_credentials"],
  "token_endpoint_auth_method": "private_key_jwt",
  "jwks_uri": "https://agent.company.com/.well-known/jwks.json",
  "scope": "invoices:read invoices:approve"
}
```

Combined with short-lived tokens, this gives ephemeral agents cryptographic identities without manual provisioning.

### 2.3 New JWT Claims for Non-Human Identity

```json
{
  "sub": "did:web:fraud-detector.acme.com",
  "iss": "https://identity.acme.com",
  "aud": "https://payments-api.acme.com",
  "iat": 1720742400,
  "exp": 1720746000,
  "agent_type": "orchestrator",
  "agent_version": "2.1.0",
  "delegation_depth": 1,
  "act": {
    "sub": "did:web:sub-agent.vendor.com"
  },
  "agent_capabilities": ["tools", "sampling", "streaming"]
}
```

:::tip MCP 2026 Mandate
The MCP 2026-07-28 stateless spec mandates OAuth 2.1 + PKCE for all HTTP transport connections. `Authorization: Bearer &lt;token&gt;` is no longer optional.
:::

### 2.4 Pushed Authorization Requests (PAR, RFC 9126)

In standard OAuth, parameters travel in the redirect URL (visible in browser history, logs). PAR pushes them server-side first:

```http
POST /as/par
client_id=agent-client
code_challenge=S256...
scope=payments:authorise
response_type=code

<-- 201 Created
{"request_uri": "urn:ietf:params:oauth:request_uri:abc123", "expires_in": 90}
```

The redirect URL carries only the opaque `request_uri`. Prevents parameter tampering in agent OAuth flows.

---

## 3. DNS — From Name Resolution to Agent Discovery

### 3.1 DNS TXT Records for Agent Capabilities

Following the pattern of SPF (`v=spf1`), DKIM, and BIMI, ANP proposes TXT records for agent capability advertisement:

```
_agent.acme.com.  IN  TXT  "v=agent1; did=did:web:acme.com; caps=tool,delegate,pay; endpoint=https://agent.acme.com"
_agent._tcp.acme.com.  IN  SRV  0 0 443 agent.acme.com.
```

This makes any DNS-resolvable domain an agent-discoverable entity without a central registry.

### 3.2 DHT for Decentralised Discovery

ANP's peer-to-peer mode uses **Kademlia DHT** (the algorithm behind BitTorrent and IPFS) for agent discovery without central infrastructure:

```
Node joins DHT → announces DID and capabilities
Other node wants fraud-detection capability:
  → hashes capability URI → finds responsible DHT bucket
  → retrieves agent endpoints from bucket
  → establishes DIDComm encrypted channel directly
```

| Approach | Infrastructure | Latency | Trust Model |
|---|---|---|---|
| `/.well-known/` HTTP | None | ~50ms | HTTPS PKI |
| DNS TXT | DNS zone admin | ~10ms | DNS DNSSEC |
| DHT (ANP) | None (P2P) | ~200ms | DID cryptography |
| Central Registry (AAIF) | Registry operator | ~50ms | Registry governance |

---

## 4. TLS → mTLS + SPIFFE/SPIRE

### 4.1 Why TLS Alone Is Insufficient

Standard TLS authenticates only the **server**. In agent-to-agent communication, both parties must prove identity. An agent calling another agent over plain TLS cannot cryptographically verify it is talking to the correct agent (not a MITM or rogue agent).

**mTLS (mutual TLS)** requires both client and server to present X.509 certificates. Both are verified before any data flows.

### 4.2 SPIFFE — Workload Identity for Ephemeral Agents

Traditional X.509 certificates bind identity to a hostname or IP. Agents are ephemeral — they run on spot instances, auto-scale, migrate across nodes. SPIFFE binds identity to the **workload** (what the process is), not where it runs.

**SPIFFE URI format:**
```
spiffe://acme.com/agent/fraud-detector/prod
spiffe://acme.com/agent/orchestrator/ns/payments
```

**SVID (SPIFFE Verifiable Identity Document) — two forms:**

1. **X.509-SVID**: Standard X.509 cert with SPIFFE URI in the SAN field. Used for mTLS.
2. **JWT-SVID**: Short-lived JWT (TTL 5min) with SPIFFE URI as `sub`. Used for API auth.

**SPIRE** is the control plane: it issues, rotates, and revokes SVIDs automatically. Agents get identity without human-provisioned certificates.

```mermaid
sequenceDiagram
    participant Agent Pod
    participant SPIRE Agent
    participant SPIRE Server
    Agent Pod->>SPIRE Agent: attestation request
    SPIRE Agent->>SPIRE Server: attestation
    SPIRE Server-->>SPIRE Agent: X.509-SVID
    SPIRE Agent-->>Agent Pod: X.509-SVID
    Agent Pod->>Agent Pod: Certificate rotates every ~1 hour automatically
    Agent Pod->>Agent Pod: Use SVID for mTLS with other agents
```

:::warning Zero Trust Implication
With SPIFFE/mTLS, network location (VPC, subnet, firewall zone) conveys no implicit trust. An agent inside the perimeter calling another agent inside the perimeter still must prove SPIFFE identity. This is the correct posture for lateral movement resistance.
:::

---

## 5. JSON-RPC 2.0 — The Universal Agent RPC Wire Format

The JSON-RPC 2.0 spec was published in 2010 and sat largely dormant in most enterprise stacks. MCP, A2A, and several emerging protocols all chose it as the wire format for three reasons:

1. **Transport-agnostic** — identical message format over HTTP, stdio, WebSocket
2. **Bidirectional** — supports both request/response and server-initiated notifications
3. **Zero build step** — plain JSON, no Protobuf compilation, no IDL toolchain

**Standard message structure:**
```json
// Request
{"jsonrpc":"2.0","id":"req-1","method":"tools/call","params":{"name":"search","arguments":{"q":"AAPL"}}}

// Response
{"jsonrpc":"2.0","id":"req-1","result":{"content":[{"type":"text","text":"Apple Inc..."}]}}

// Server notification (no id — no response expected)
{"jsonrpc":"2.0","method":"notifications/progress","params":{"progressToken":"tok-1","progress":45,"total":100}}
```

**Agent-specific extensions emerging across MCP/A2A:**

| Extension | Purpose |
|---|---|
| `_meta` field in params | Carry trace IDs, progress tokens, vendor extensions |
| Batch requests `[...]` | Fan out multiple tool calls in one HTTP round trip |
| Notification-only messages | Task status updates, resource change events |
| Error codes -32xxx + agent-specific 4xxx | Standardising agent error taxonomy |

---

## 6. OpenAPI — Extended for Agent Capabilities

### 6.1 MCP Tool Definitions — OpenAPI-Influenced Schema

MCP tool definitions use JSON Schema (the same schema system OpenAPI 3.1 uses) for parameter validation:

```json
{
  "name": "get_stock_price",
  "description": "Retrieve real-time stock price for a ticker symbol",
  "inputSchema": {
    "type": "object",
    "properties": {
      "ticker": {"type": "string", "description": "Stock ticker, e.g. AAPL"},
      "currency": {"type": "string", "enum": ["USD","EUR","GBP"], "default": "USD"}
    },
    "required": ["ticker"]
  },
  "annotations": {
    "readOnlyHint": true,
    "idempotentHint": true
  }
}
```

### 6.2 `x-agent-card` OpenAPI Extension

API providers are adding `x-agent-card` to their OpenAPI specs linking to the A2A manifest:

```yaml
info:
  title: Payments API
  x-agent-card: https://api.acme.com/.well-known/agent-card.json
  x-mcp-server: https://api.acme.com/mcp
```

### 6.3 AsyncAPI for Agent Event-Driven Patterns

AsyncAPI 3.0 is being used to describe agent event streams — particularly for AG-UI SSE events and A2A task notifications:

```yaml
asyncapi: 3.0.0
info:
  title: Agent Event Stream
channels:
  agentEvents:
    address: /sse/agent-stream
    messages:
      TextMessageContent:
        payload:
          type: object
          properties:
            type: {const: TEXT_MESSAGE_CONTENT}
            message_id: {type: string}
            delta: {type: string}
```

---

## 7. gRPC / Protobuf

### 7.1 Why gRPC Appears in IoA Protocols

LMOS (Eclipse Foundation) uses gRPC rather than HTTP+JSON-RPC for its runtime layer:

- **Typed streaming** — Protobuf IDL enforces schema at compile time, not runtime
- **Bidirectional streaming** — true full-duplex, needed for the IoA "agent operating system" model
- **Performance** — ~3–10× less bandwidth than JSON for high-frequency agent telemetry

```protobuf
service AgentRuntime {
  rpc ExecuteTask(TaskRequest) returns (stream TaskEvent) {}
  rpc RegisterAgent(AgentManifest) returns (RegistrationResponse) {}
  rpc StreamCapabilities(CapabilityQuery) returns (stream CapabilityUpdate) {}
}
```

### 7.2 gRPC vs. SSE for Agent Workloads

| | gRPC | SSE (HTTP) |
|---|---|---|
| Browser support | Requires grpc-web proxy | Native |
| Load balancer compatibility | Needs HTTP/2 ALB | Works on any |
| Schema enforcement | Compile-time (Protobuf) | Runtime (JSON Schema) |
| Adoption in agent ecosystem | LMOS only | MCP, A2A, AG-UI |
| Best for | Internal IoA runtimes | Public-facing agent APIs |

---

## 8. Content Negotiation — JSON-LD for Semantic Agents

### 8.1 From `application/json` to `application/ld+json`

Plain JSON is schema-less from a semantic perspective — a field called `"action"` means whatever the API author intended. JSON-LD binds field names to globally unambiguous IRIs:

```json
{
  "@context": "https://schema.org/",
  "@type": "SearchAction",
  "query": "AAPL stock price",
  "result": {
    "@type": "FinancialProduct",
    "name": "Apple Inc.",
    "tickerSymbol": "AAPL"
  }
}
```

Any agent that understands `schema.org/SearchAction` can interpret this without custom per-vendor schemas. HTTP `Accept: application/ld+json` triggers semantic responses.

### 8.2 ANP's JSON-LD Capability Registry

ANP uses JSON-LD for agent capability declarations, enabling semantic discovery:

```json
{
  "@context": ["https://www.w3.org/ns/did/v1", "https://agent-protocol.ai/context/v1"],
  "@type": "AgentCapability",
  "id": "https://acme.com/agents/fraud-detector#capability-1",
  "capability": "schema:ReviewAction",
  "inputType": "schema:FinancialTransaction",
  "outputType": "schema:Review",
  "maxResponseTime": "PT5S"
}
```

### 8.3 CBOR — Binary JSON-LD for Constrained Agents

**CBOR (Concise Binary Object Representation, RFC 8949)** is being adopted for agent payloads where bandwidth matters — IoT-adjacent agents, edge deployments, high-frequency tool calls:

- Semantically equivalent to JSON but 30–50% smaller
- Full JSON-LD context support
- Native support in ANP for P2P agent messages over constrained networks

---

## 9. WebRTC — Multimodal Agent Communication

A2A's modality-agnostic design (`defaultInputModes: ["text","audio","video"]`) requires a real-time transport for audio/video. WebRTC fills that gap:

- **DTLS-SRTP** — encrypted audio/video between agent and user
- **Data Channels** — structured JSON alongside media (tool calls during a voice session)
- **ICE/STUN/TURN** — NAT traversal for agents behind enterprise firewalls

**Voice agent architecture:**
```
User --WebRTC audio------------------------------------------> Voice Agent
      <-- AG-UI SSE (transcript + state) ---------
      ---- HTTP POST (text actions) ------------->
```

AG-UI's `TEXT_MESSAGE_*` events carry real-time transcription. WebRTC carries the raw audio stream. The same agent can serve text-channel and voice-channel clients simultaneously.

---

## 10. Emerging Conventions

### 10.1 `agents.md` / `agents.txt` (robots.txt for Agents)

The AAIF is standardising a root-level file declaring how agents should interact with a domain:

```markdown
# agents.md
Agent: *
Allow: /api/public/
Disallow: /admin/
MCP-Server: https://api.acme.com/mcp
A2A-Agent-Card: https://api.acme.com/.well-known/agent-card.json
Rate-Limit: 100/minute
Require-Auth: Bearer
```

### 10.2 W3C Trace Context — Cross-Protocol Correlation

`traceparent` and `tracestate` headers propagate distributed traces through agent hops:

```http
traceparent: 00-4bf92f3577b34da6a3ce929d0e0e4736-00f067aa0ba902b7-01
tracestate: acme=rr:1,vendor=xyz
```

Every MCP tool call, A2A task delegation, and AG-UI event carries the same `traceparent`. OpenTelemetry's `gen_ai.*` semantic conventions map these to LLM spans:

```
traceparent root
  |-- gen_ai.client.operation (LLM call)
       |-- mcp.tool.call: search_web
       |-- a2a.task.delegate: fraud-check-agent
       |    |-- mcp.tool.call: query_fraud_db
       |-- ag_ui.event: TOOL_CALL_RESULT
```

### 10.3 `Idempotency-Key` Header for Safe Agent Retry

Agents retry on failure. Without idempotency, a payment or email agent might execute twice. The `Idempotency-Key` pattern (from Stripe, now broadly adopted) prevents this:

```http
POST /api/payments
Idempotency-Key: agent-task-7f3a-payment-attempt-1
```

The server caches the response against the key. Retries return the cached response without re-executing.

---

## Summary: The Protocol Evolution Map

| Existing Protocol | What Changed for Agents | Why It Matters |
|---|---|---|
| HTTP | SSE streaming · /.well-known/ discovery · 402 payment handshake · agent headers · HTTP/3 for long-running tasks | Agent streaming + discovery without new infra |
| OAuth 2.0/OIDC | RFC 8693 delegation chains · Dynamic client registration · New non-human identity JWT claims | Scoped trust across agent hierarchies |
| DNS | TXT capability records · DHT-based P2P discovery | Zero-infra agent discovery at scale |
| TLS | mTLS as default (not optional) · SPIFFE workload identity · SPIRE automated certificate lifecycle | Both parties prove identity; ephemeral agents get certs |
| JSON-RPC 2.0 | Adopted as universal agent RPC format · _meta extension field added · Notification pattern for events | Single wire format across all transports |
| OpenAPI | x-agent-card extension · Tool schema via JSON Schema · AsyncAPI for event streams | Existing API docs describe agent caps |
| gRPC/Protobuf | LMOS IoA runtime streaming · Bidirectional agent-to-agent RPC | Typed, efficient streaming for IoA |
| Content-Type | JSON-LD semantic negotiation · CBOR binary for constrained agents | Cross-vendor schema interoperability |
| WebRTC | Voice/video agent channels · DTLS-SRTP encryption | Multimodal A2A agents |
| Conventions | agents.md (robots.txt for agents) · W3C traceparent propagation · Idempotency-Key for safe retry | Ecosystem hygiene: observability, safety, discovery |

:::info Key Insight
None of these changes required a new transport layer. The "agentic web" runs on HTTP/1.1, HTTP/2, and HTTP/3 — the same stack enterprises already operate. The changes are in **semantics** (what headers mean, what URIs declare, what claims flow in tokens) rather than in the underlying plumbing.
:::

---

## Related

- [Protocols Hub](index.md) — the full protocol landscape this evolution history sits within.
- [Agent Protocol Metadata, Headers & Capability Negotiation](17-agent-protocol-metadata-headers.md) — how these evolved protocols express metadata and capability negotiation.
- [Emerging AI Agent Protocols Overview](21-emerging-protocols-overview.md) — the newer protocols built on top of this evolved foundation.
- [MCP & A2A Protocol Deep Dive](../architecture/58-mcp-a2a-protocol-deep-dive.md) — the architecture-side deep dive on how these protocols are actually implemented in systems.
