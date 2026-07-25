---
doc_type: reference-architecture
domain: protocols
topic_id: agent-protocol-metadata-headers
title: "Agent Protocol Metadata, Headers & Capability Negotiation"
subtitle: "MCP · A2A · AG-UI · ANP — In-Protocol Metadata Systems (July 2026)"
date_created: 2026-07-11
last_reviewed: 2026-07-11
status: current
supersedes:
  - docs/ai-protocols/standards/agent-protocol-metadata-headers.md
source_type: native-md
source_file: "Agent Protocol Metadata, Headers & Capability Negotiation Reference"
tags: ["ai-protocols", "mcp", "a2a", "ag-ui", "anp", "metadata", "headers", "capability-negotiation"]
audience: "Enterprise Architects, AI Platform Engineers, Security Architects"
---

# Agent Protocol Metadata, Headers & Capability Negotiation

*MCP · A2A · AG-UI · ANP — In-Protocol Metadata Systems — July 2026*

This reference covers the **metadata layer within** each protocol — the fields, headers, and negotiation mechanisms that travel alongside every message. Understanding this layer is essential for observability, security hardening, progressive enhancement, and cross-protocol correlation.

---

## Part 1: MCP Metadata & Headers

### 1.1 HTTP Transport Headers

MCP's 2026-07-28 stateless spec makes these headers mandatory on every HTTP connection:

```http
# Every request
Authorization: Bearer eyJhbGciOiJSUzI1NiJ9...   # OAuth 2.1 — mandatory in 2026 spec
Content-Type: application/json
Mcp-Session-Id: sess-7f3a2b1c4d5e6f7a            # Session identity (stateless: in header, not connection)
Mcp-Version: 2026-07-28                           # Protocol version

# SSE stream responses
Content-Type: text/event-stream
Cache-Control: no-cache
Connection: keep-alive
```

**Key change from 2025 → 2026:** Sessions are now carried in `Mcp-Session-Id` header, not tied to a TCP connection. This means session state must live in the application layer (Redis, database) — the protocol itself is connectionless. An agent can reconnect from a different IP and resume the same session.

**On version mismatch:** Server returns `400 Bad Request` with a JSON body listing supported versions. Client selects the highest mutually supported version and retries.

**stdio transport:** No headers. Capability negotiation happens entirely via the `initialize` handshake (see §1.2).

### 1.2 The `initialize` Handshake — Capability Negotiation

The `initialize` exchange is how MCP implements progressive enhancement — a client and server discover what each other supports before any meaningful work begins.

**Request (client → server):**
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "initialize",
  "params": {
    "protocolVersion": "2026-07-28",
    "capabilities": {
      "roots": { "listChanged": true },
      "sampling": {}
    },
    "clientInfo": {
      "name": "claude-code",
      "version": "1.12.0"
    }
  }
}
```

**Response (server → client):**
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "protocolVersion": "2026-07-28",
    "capabilities": {
      "tools": { "listChanged": true },
      "resources": { "subscribe": true, "listChanged": true },
      "prompts": { "listChanged": true },
      "logging": {},
      "experimental": {
        "myVendor/batchTools": {}
      }
    },
    "serverInfo": {
      "name": "postgres-mcp-server",
      "version": "2.1.0"
    }
  }
}
```

**Capabilities reference:**

| Capability | Who Declares | Meaning |
|---|---|---|
| `roots` | Client | Client can expose filesystem roots to server |
| `roots.listChanged` | Client | Client sends `notifications/roots/list_changed` when roots change |
| `sampling` | Client | Client supports `sampling/createMessage` — server can request LLM completions |
| `tools` | Server | Server exposes callable tools |
| `tools.listChanged` | Server | Server sends `notifications/tools/list_changed` on tool set changes |
| `resources` | Server | Server exposes readable resources |
| `resources.subscribe` | Server | Client can subscribe to resource change notifications |
| `prompts` | Server | Server exposes prompt templates |
| `logging` | Server | Server sends structured log notifications |
| `experimental.*` | Either | Vendor-specific extensions — must be namespaced |

**Progressive enhancement in practice:** A client without `sampling` capability simply never calls `sampling/createMessage`. The server detects the missing capability and never attempts bidirectional LLM calls. No error, no fallback code needed.

After `initialize`, client must send `notifications/initialized` before any other messages.

### 1.3 The `_meta` Field — Per-Request Extensibility

The `_meta` field in `params` carries per-request metadata that the receiving party uses but does not act on as a command. Servers MUST pass unknown `_meta` fields through without error.

**Progress reporting (long-running tools):**
```json
{
  "jsonrpc": "2.0",
  "id": "req-42",
  "method": "tools/call",
  "params": {
    "name": "run_etl_pipeline",
    "arguments": {"dataset": "q2-2026"},
    "_meta": {
      "progressToken": "progress-req-42"
    }
  }
}
```

Server sends notifications during execution:
```json
{"jsonrpc":"2.0","method":"notifications/progress","params":{"progressToken":"progress-req-42","progress":3,"total":10,"message":"Processing partition 3/10"}}
```

**OpenTelemetry integration:**
```json
"_meta": {
  "traceId": "4bf92f3577b34da6a3ce929d0e0e4736",
  "spanId":  "00f067aa0ba902b7",
  "traceFlags": "01"
}
```

**Custom vendor metadata:**
```json
"_meta": {
  "progressToken": "tok-1",
  "acme/costCenter": "engineering-ai-platform",
  "acme/requestedBy": "fraud-detection-orchestrator"
}
```

### 1.4 Tool Metadata — Annotations

Tool `annotations` are hints that clients use to build permission UIs, cost estimates, and audit trails. They do not constrain server behaviour.

```json
{
  "name": "delete_customer_record",
  "description": "Permanently delete a customer record",
  "inputSchema": {
    "type": "object",
    "properties": {
      "customer_id": {"type": "string"}
    },
    "required": ["customer_id"]
  },
  "annotations": {
    "readOnlyHint": false,
    "destructiveHint": true,
    "idempotentHint": false,
    "openWorldHint": false
  }
}
```

| Annotation | Default | Meaning |
|---|---|---|
| `readOnlyHint` | `false` | Tool only reads; makes no writes or side effects |
| `destructiveHint` | `true` | Tool may delete or irreversibly modify data |
| `idempotentHint` | `false` | Repeated calls with same args have no additional effect |
| `openWorldHint` | `true` | Tool may contact the external internet |

**Enterprise use:** UI platforms use `destructiveHint: true` to surface confirmation prompts. Audit systems flag `destructiveHint: true` tool calls for mandatory human review in regulated workflows.

**Tool list pagination:** Large MCP servers (10k+ tools) use cursor-based pagination:
```json
{"method":"tools/list","params":{"cursor":"eyJwYWdlIjozfQ=="}}
```

### 1.5 Resource Metadata

```json
{
  "uri": "file:///data/reports/{year}/{month}.csv",
  "name": "Monthly Revenue Report",
  "description": "Revenue by product line",
  "mimeType": "text/csv",
  "annotations": {
    "audience": ["assistant"],
    "priority": 0.8
  }
}
```

**URI templates** (RFC 6570): `{year}` and `{month}` are expanded by the client when requesting specific resources.

**Annotations:**
- `audience`: `["user"]` — show in UI; `["assistant"]` — inject into context silently
- `priority`: `0.0–1.0` — controls context window priority when resources compete for space

**Subscriptions:** When server declares `resources.subscribe: true`, clients can subscribe:
```json
{"method": "resources/subscribe", "params": {"uri": "postgres://db/metrics/realtime"}}
```
Server sends `notifications/resources/updated` when the resource changes, enabling real-time agent responses to data changes.

### 1.6 Sampling Metadata — Bidirectional LLM Calls

When the server has a task that requires LLM reasoning (not just data retrieval), it can request a completion from the host model via `sampling/createMessage`:

```json
{
  "method": "sampling/createMessage",
  "params": {
    "messages": [
      {"role": "user", "content": {"type": "text", "text": "Classify this transaction: $4,200 to offshore account"}}
    ],
    "modelPreferences": {
      "hints": [{"name": "claude-opus"}],
      "costPriority": 0.2,
      "speedPriority": 0.3,
      "intelligencePriority": 0.9
    },
    "systemPrompt": "You are a fraud classification expert. Respond only with LEGITIMATE, SUSPICIOUS, or FRAUDULENT.",
    "includeContext": "thisServer",
    "maxTokens": 50
  }
}
```

`modelPreferences` is a soft hint — the host resolves these priorities against available models. A high `intelligencePriority` biases toward Opus/Frontier-tier models; high `speedPriority` toward Haiku/nano-tier.

---

## Part 2: A2A Metadata & Headers

### 2.1 Agent Card — The Complete Capability Manifest

Every A2A agent publishes its capability manifest at `/.well-known/agent-card.json`. This is the primary discovery and negotiation artifact.

```json
{
  "schemaVersion": "1.0",
  "name": "Fraud Detection Agent",
  "description": "Real-time transaction fraud scoring with AML screening",
  "url": "https://fraud.acme.com/a2a",
  "version": "3.2.1",
  "documentationUrl": "https://fraud.acme.com/docs",
  "capabilities": {
    "streaming": true,
    "pushNotifications": true,
    "stateTransitionHistory": true
  },
  "authentication": {
    "schemes": ["Bearer", "OAuth2"],
    "oauth2": {
      "authorizationUrl": "https://identity.acme.com/authorize",
      "tokenUrl": "https://identity.acme.com/token",
      "scopes": {"fraud:score": "Request fraud scores", "fraud:explain": "Get explanations"}
    }
  },
  "defaultInputModes": ["text", "data"],
  "defaultOutputModes": ["text", "data"],
  "skills": [
    {
      "id": "score-transaction",
      "name": "Score Transaction",
      "description": "Return a 0–100 fraud risk score with contributing factors",
      "tags": ["fraud", "risk", "aml"],
      "examples": ["Score this wire transfer for AML risk"],
      "inputModes": ["data"],
      "outputModes": ["data", "text"]
    }
  ],
  "supportsAuthenticatedExtendedCard": true
}
```

**Extended Agent Card:** When `supportsAuthenticatedExtendedCard: true`, authenticated callers can fetch `/agent-card-extended.json` which reveals internal skills, pricing, SLA commitments, and rate limits not exposed publicly.

### 2.2 Task Envelope — Full Schema

```json
{
  "id": "task-7f3a2b1c-4d5e-6f7a-8b9c-0a1b2c3d4e5f",
  "sessionId": "sess-parent-orchestration-id",
  "status": {
    "state": "working",
    "timestamp": "2026-07-11T10:23:45.123Z",
    "message": {
      "role": "agent",
      "parts": [{"type": "text", "text": "Querying AML database..."}]
    }
  },
  "history": [
    {
      "role": "user",
      "parts": [{"type": "data", "data": {"amount": 42000, "currency": "USD", "beneficiary": "ACME Corp", "account": "CH12..."}}],
      "metadata": {"correlationId": "trace-root-uuid"}
    }
  ],
  "artifacts": [],
  "metadata": {
    "priority": "HIGH",
    "requester": "did:web:orchestrator.acme.com",
    "costCenter": "compliance-team"
  }
}
```

**Task state machine:**

```mermaid
stateDiagram-v2
    submitted --> working
    working --> completed
    working --> input-required
    input-required --> working
    submitted --> cancelled
    working --> cancelled
    working --> failed
```

### 2.3 Message Parts — Multimodal Metadata

Each `Message` contains an array of typed `Part` objects:

```json
{
  "role": "agent",
  "parts": [
    {
      "type": "text",
      "text": "Transaction classified as HIGH RISK (score: 87)"
    },
    {
      "type": "data",
      "data": {
        "riskScore": 87,
        "flags": ["high-value", "new-beneficiary", "unusual-hour"],
        "amlMatch": false
      },
      "metadata": {"mimeType": "application/vnd.acme.fraud-score+json"}
    },
    {
      "type": "file",
      "file": {
        "name": "fraud-report.pdf",
        "mimeType": "application/pdf",
        "uri": "https://fraud.acme.com/reports/task-7f3a.pdf"
      }
    }
  ],
  "metadata": {"spanId": "00f067aa0ba902b7"}
}
```

### 2.4 Streaming Event Metadata (SSE)

A2A streams task updates via SSE. Each event has a type and structured payload:

```
id: evt-001
event: task_status_update
data: {"id":"task-7f3a","status":{"state":"working","timestamp":"2026-07-11T10:23:46.200Z"}}

id: evt-002
event: task_artifact_update
data: {
  "id": "task-7f3a",
  "artifact": {
    "index": 0,
    "name": "fraud-score",
    "parts": [{"type":"data","data":{"riskScore":87}}],
    "append": false,
    "lastChunk": true
  }
}
```

`append: true` + `lastChunk: false` = streaming a large artifact in chunks. `lastChunk: true` signals completion.

### 2.5 Push Notification Metadata

```json
{
  "id": "task-7f3a",
  "pushNotification": {
    "url": "https://orchestrator.acme.com/webhooks/a2a",
    "token": "webhook-secret-hmac-key",
    "authentication": {
      "schemes": ["Bearer"],
      "credentials": "webhook-bearer-token"
    }
  }
}
```

Webhook payloads include `X-A2A-Signature: hmac-sha256=...` for verification. Prevents replay via `X-A2A-Timestamp` with 5-minute skew tolerance.

---

## Part 3: AG-UI Event Metadata

### 3.1 Base Event — Every Event's Shared Context

Every AG-UI event carries this base envelope:

```typescript
interface BaseEvent {
  type: EventType;          // Discriminated union — one of the types below
  timestamp?: number;       // Unix ms — for ordering and latency measurement
  rawResponse?: unknown;    // Framework debug data (stripped in production)
}
```

Run-level context is carried in the SSE stream headers and the RUN_STARTED event:

```json
{
  "type": "RUN_STARTED",
  "timestamp": 1720742400123,
  "thread_id": "thread-conversations-uuid",
  "run_id": "run-7f3a2b1c",
  "agent_name": "fraud-orchestrator"
}
```

### 3.2 Complete Event Type Taxonomy

**Lifecycle events:**
```
RUN_STARTED    → run_id, thread_id, agent_name
RUN_FINISHED   → (inherits base) — signals normal completion
RUN_ERROR      → message: string, code?: string
```

**Message streaming events (text arrives token by token):**
```
TEXT_MESSAGE_START    → message_id, role: "user"|"assistant"
TEXT_MESSAGE_CONTENT  → message_id, delta: string   ← token chunk
TEXT_MESSAGE_END      → message_id
```

**Tool call events (parallel calls tracked by tool_call_id):**
```
TOOL_CALL_START   → tool_call_id, tool_call_name, parent_message_id
TOOL_CALL_ARGS    → tool_call_id, delta: string   ← streaming JSON args
TOOL_CALL_END     → tool_call_id
TOOL_CALL_RESULT  → tool_call_id, content: string | ContentBlock[]
```

**Agentic step events:**
```
STEP_STARTED  → step_name, step_type: "thinking"|"tool"|"agent-handoff"
STEP_FINISHED → step_name
STEP_ERROR    → step_name, message, code
```

**State synchronisation:**
```
STATE_SNAPSHOT → snapshot: object   ← full state, sent on connect/reconnect
STATE_DELTA    → delta: JSONPatch   ← RFC 6902 patch operations
```

**Human-in-the-loop:**
```
MESSAGES_SNAPSHOT → messages: Message[]   ← paused, awaiting human input
```

**Extensibility:**
```
CUSTOM → name: string, value: unknown
```

:::warning CUSTOM Event Security Risk
The `CUSTOM` event is the AG-UI extensibility escape hatch. Its `value` field is arbitrary JSON from the agent. In 2026, prompt injection attacks have targeted CUSTOM event handlers — malicious tool results instructing the agent to emit CUSTOM events that trigger privileged frontend actions. Always validate CUSTOM event names against an allowlist; never execute code from CUSTOM event payloads.
:::

### 3.3 Tool Call Metadata Chaining

Multiple tool calls run in parallel. `tool_call_id` is the correlation anchor:

```
TOOL_CALL_START   tool_call_id="tc-1"  tool_call_name="search_web"  parent_message_id="msg-5"
TOOL_CALL_START   tool_call_id="tc-2"  tool_call_name="query_db"    parent_message_id="msg-5"
TOOL_CALL_ARGS    tool_call_id="tc-1"  delta='{"q":'
TOOL_CALL_ARGS    tool_call_id="tc-2"  delta='{"table":'
TOOL_CALL_ARGS    tool_call_id="tc-1"  delta='"AAPL"}'
TOOL_CALL_ARGS    tool_call_id="tc-2"  delta='"transactions"}'
TOOL_CALL_END     tool_call_id="tc-1"
TOOL_CALL_END     tool_call_id="tc-2"
TOOL_CALL_RESULT  tool_call_id="tc-1"  content="Apple Inc. stock: $192.34"
TOOL_CALL_RESULT  tool_call_id="tc-2"  content=[{"amount":42000,...}]
```

### 3.4 State Delta — RFC 6902 JSON Patch

`STATE_DELTA` carries incremental state changes as JSON Patch operations:

```json
{
  "type": "STATE_DELTA",
  "delta": [
    {"op": "replace", "path": "/status", "value": "processing"},
    {"op": "add", "path": "/results/-", "value": {"score": 87, "flag": "suspicious"}},
    {"op": "remove", "path": "/pendingItems/0"}
  ]
}
```

React/Vue frontends apply these patches to their state store for reactive UI updates. `STATE_SNAPSHOT` is sent on initial connect and after reconnect to re-establish full state.

---

## Part 4: ANP Metadata (DID / JSON-LD Layer)

### 4.1 DID Document Metadata

```json
{
  "@context": [
    "https://www.w3.org/ns/did/v1",
    "https://w3id.org/security/suites/ed25519-2020/v1"
  ],
  "id": "did:web:fraud-detector.acme.com",
  "verificationMethod": [
    {
      "id": "did:web:fraud-detector.acme.com#key-1",
      "type": "Ed25519VerificationKey2020",
      "controller": "did:web:fraud-detector.acme.com",
      "publicKeyMultibase": "z6MkhaXgBZDvotDkL5257faiztiGiC2QtKLGpbnnEGta2doK"
    }
  ],
  "authentication": ["did:web:fraud-detector.acme.com#key-1"],
  "assertionMethod": ["did:web:fraud-detector.acme.com#key-1"],
  "keyAgreement": [
    {
      "id": "did:web:fraud-detector.acme.com#key-agreement-1",
      "type": "X25519KeyAgreementKey2020",
      "publicKeyMultibase": "z6LSbysY2xFMRpGMhb7tFTLMpeuPRaqaWM1yECx2AtzE3KCc"
    }
  ],
  "service": [
    {
      "id": "did:web:fraud-detector.acme.com#agent-discovery",
      "type": "AgentDiscovery",
      "serviceEndpoint": "https://fraud-detector.acme.com/agent/discover"
    },
    {
      "id": "did:web:fraud-detector.acme.com#messaging",
      "type": "DIDCommMessaging",
      "serviceEndpoint": "https://fraud-detector.acme.com/agent/message"
    }
  ],
  "updated": "2026-07-11T00:00:00Z",
  "versionId": "42"
}
```

**Key purpose separation:**
- `authentication` key → proves "I am this DID"
- `assertionMethod` key → signs Verifiable Credentials
- `keyAgreement` key (X25519) → ECDH key for encrypted DIDComm messages

### 4.2 DIDComm v2 Message Metadata

```json
{
  "id": "msg-7f3a2b1c-4d5e-6f7a",
  "type": "https://agent-protocol.ai/protocols/fraud-check/1.0/request",
  "from": "did:web:orchestrator.acme.com",
  "to": ["did:web:fraud-detector.acme.com"],
  "created_time": 1720742400,
  "expires_time": 1720742700,
  "thid": "thread-orchestration-session-uuid",
  "pthid": "parent-thread-top-level-task-uuid",
  "body": {
    "transaction": {"amount": 42000, "currency": "USD", "beneficiary": "ACME Corp"}
  },
  "attachments": [
    {
      "id": "att-1",
      "media_type": "application/pdf",
      "data": {"base64": "..."},
      "description": "Supporting documentation"
    }
  ]
}
```

**Metadata fields:**

| Field | Purpose |
|---|---|
| `id` | Globally unique message ID — replay prevention anchor |
| `type` | Protocol URI — determines how the recipient handles the message |
| `from` / `to` | DID-based identity (not IP/hostname) |
| `created_time` / `expires_time` | Replay protection — messages older than 5min (configurable) are rejected |
| `thid` | Thread ID — groups related messages in a conversation |
| `pthid` | Parent thread ID — links sub-conversations to parent workflows |

### 4.3 Verifiable Credential — Agent Capability Proof

```json
{
  "@context": [
    "https://www.w3.org/2018/credentials/v1",
    "https://agent-protocol.ai/context/agent-capabilities/v1"
  ],
  "type": ["VerifiableCredential", "AgentCapabilityCredential"],
  "issuer": "did:web:trust-registry.acme.com",
  "issuanceDate": "2026-07-01T00:00:00Z",
  "expirationDate": "2026-10-01T00:00:00Z",
  "credentialSubject": {
    "id": "did:web:fraud-detector.acme.com",
    "capabilities": ["fraud:score", "aml:screen"],
    "complianceCertifications": ["ISO-27001", "PCI-DSS-Level-1"],
    "maxTransactionValue": 1000000,
    "regulatoryJurisdictions": ["EU", "UK", "US"]
  },
  "proof": {
    "type": "Ed25519Signature2020",
    "created": "2026-07-01T00:00:00Z",
    "verificationMethod": "did:web:trust-registry.acme.com#key-1",
    "proofPurpose": "assertionMethod",
    "proofValue": "z5vgY..."
  }
}
```

An agent presents this VC instead of querying a central registry. The receiving agent verifies the cryptographic proof independently — zero round trips to a registry during operation.

### 4.4 Meta-Protocol Negotiation Metadata

```json
// ProtocolPropose — sent by initiating agent
{
  "type": "https://didcomm.org/protocols/meta-protocol/1.0/propose",
  "body": {
    "protocols": [
      {"uri": "https://agent-protocol.ai/protocols/fraud-check/2.0", "priority": 1},
      {"uri": "https://agent-protocol.ai/protocols/fraud-check/1.0", "priority": 2}
    ]
  }
}

// ProtocolAccept — sent by responding agent
{
  "type": "https://didcomm.org/protocols/meta-protocol/1.0/accept",
  "body": {
    "protocol": "https://agent-protocol.ai/protocols/fraud-check/2.0"
  }
}
```

This is ANP's forward compatibility mechanism — new protocol versions can be proposed and negotiated at runtime without breaking older agents that only know older versions.

---

## Part 5: Cross-Protocol Metadata Patterns

### 5.1 W3C Trace Context — End-to-End Correlation

The `traceparent` header propagates a single trace through every protocol boundary:

```
traceparent: 00-{traceId}-{parentSpanId}-{flags}
traceparent: 00-4bf92f3577b34da6a3ce929d0e0e4736-00f067aa0ba902b7-01
             ^^ version   ^^ 16-byte traceId (128-bit)    ^^ flags (sampled=1)
                                                ^^ 8-byte spanId
```

**Full trace through the agent stack:**

```mermaid
graph TD
    A["HTTP request<br/>traceparent: 00-abc...01"] --> B["MCP tool/call<br/>_meta.traceId: abc..., _meta.spanId: 001..."]
    B --> C["span: gen_ai.client.operation"]
    C --> D["A2A task delegation<br/>X-Trace-Id: abc..., X-Parent-Span: 001..."]
    D --> E["span: a2a.task.delegate"]
    E --> F["MCP tool/call inside sub-agent<br/>_meta.traceId: abc..."]
    F --> G["span: gen_ai.client.operation"]
    E --> H["AG-UI event<br/>timestamp links to span timeline"]
    H --> I["TOOL_CALL_RESULT → tool_call_id links to OTel span"]
```

All spans share the same `traceId`. OpenTelemetry's `gen_ai.*` semantic conventions define the span attributes:

```
gen_ai.system = "anthropic"
gen_ai.operation.name = "chat"
gen_ai.request.model = "claude-sonnet-4-6"
gen_ai.request.max_tokens = 4096
gen_ai.usage.input_tokens = 1234
gen_ai.usage.output_tokens = 456
```

### 5.2 Correlation ID Mapping Across Protocols

| Protocol | Correlation Anchor | Scope |
|---|---|---|
| MCP | `_meta.progressToken` | Single tool call |
| MCP | HTTP `Mcp-Session-Id` | Session (multiple calls) |
| A2A | `task.id` | Single task |
| A2A | `task.sessionId` | Multi-task session |
| AG-UI | `run_id` | Single agent run |
| AG-UI | `thread_id` | Conversation thread |
| ANP | `thid` (DIDComm thread ID) | Conversation thread |
| ANP | `pthid` (parent thread ID) | Parent workflow |
| HTTP | `traceparent` / `tracestate` | Full distributed trace |

**Cross-protocol strategy:** Assign one root UUID per user-facing operation. Propagate it as:
- `_meta.correlationId` in MCP
- `task.metadata.correlationId` in A2A
- `tracestate: root=&lt;uuid&gt;` in HTTP headers
- `thid` in ANP (or embed in `body`)

### 5.3 Idempotency Metadata

Agents retry on failure. Without idempotency keys, payments execute twice, emails send twice.

**MCP:** `idempotentHint: true` on the tool definition signals the client that retries are safe.

**A2A:** Task `id` is the idempotency key. Resubmitting the same task `id` returns the existing task state rather than creating a new one.

**HTTP:** `Idempotency-Key` header (Stripe convention, widely adopted):
```http
POST /api/agent/tools/execute
Idempotency-Key: task-7f3a-tool-payment-attempt-1
```

**ANP:** DIDComm message `id` is globally unique. Receiving agents deduplicate by `id` within the `expires_time` window.

### 5.4 Minimum Audit Trail Metadata

For EU AI Act, PCI DSS, HIPAA compliance, every agent action must produce an audit record containing:

```json
{
  "auditId": "aud-uuid",
  "timestamp": "2026-07-11T10:23:45.123Z",
  "who": {
    "agentId": "did:web:fraud-detector.acme.com",
    "agentVersion": "3.2.1",
    "delegatedBy": "did:web:orchestrator.acme.com",
    "onBehalfOf": "user-upn@company.com"
  },
  "what": {
    "protocol": "MCP",
    "operation": "tools/call",
    "tool": "query_fraud_database",
    "input": {"transactionId": "txn-abc123"},
    "inputHash": "sha256:3f7a..."
  },
  "why": {
    "taskId": "task-7f3a",
    "correlationId": "trace-root-uuid",
    "businessReason": "AML compliance check"
  },
  "outcome": {
    "status": "success",
    "outputHash": "sha256:9c2b...",
    "durationMs": 234
  },
  "traceContext": {
    "traceId": "4bf92f3577b34da6a3ce929d0e0e4736",
    "spanId": "00f067aa0ba902b7"
  }
}
```

The `inputHash` / `outputHash` fields are SHA-256 hashes of the actual data — the audit log proves what was sent/received without storing sensitive data in plain text. PCI DSS requires 7 years retention for AP2/UCP payment audit records.

---

## Quick Reference

### Metadata Field Lookup

| Goal | MCP | A2A | AG-UI | ANP |
|---|---|---|---|---|
| Trace a request | `_meta.traceId` | `task.metadata` | `run_id` | `thid` |
| Link to parent | `Mcp-Session-Id` | `task.sessionId` | `thread_id` | `pthid` |
| Report progress | `_meta.progressToken` | Task state SSE | `STEP_*` events | N/A |
| Declare version | `initialize.protocolVersion` | Agent Card `version` | N/A | VC `issuanceDate` |
| Prove identity | `Authorization: Bearer` | `Authorization: Bearer` | (session scoped) | DID + VC proof |
| Extend metadata | `_meta.*` + `experimental.*` | `task.metadata` | `CUSTOM` event | DIDComm `body.*` |
| Ensure idempotency | `idempotentHint` | Task `id` reuse | N/A | Message `id` |

---

**Related:** [Existing Protocol Evolution for Agentic AI](./23-existing-protocol-evolution-agentic-ai.md) · [Emerging Protocols Beyond MCP & A2A](./index.md) · [MCP Deep Research 2026](./13-mcp-deep-research-2026.md)
