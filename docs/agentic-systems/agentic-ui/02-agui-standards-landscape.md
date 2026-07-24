---
title: "AGUI Standards & Ecosystem Landscape"
date_created: 2026-07-24
last_reviewed: 2026-07-24
status: current
domain: agentic-systems
doc_type: guide
topic_id: agui-standards-landscape
covers_version: "as of 2026-07-10"
supersedes:
  - docs/agentic-ui/agui-standards-landscape.md
---

# AGUI Standards & Ecosystem Landscape

Principal AI Architects and AI Platform Teams will find here the authoritative technical reference for every protocol, standard, and framework in the agentic UI ecosystem as of July 2026 — including AG-UI, A2UI v0.9, MCP Apps, NLWeb, OpenAI Apps SDK, and Microsoft Agent Framework 1.0, with production code examples, a 15-framework comparison matrix, and a selection decision tree.

:::info Protocol Maturity Status — July 2026
    AG-UI: production-ready open standard. A2UI: v0.9 experimental (Google). NLWeb: production open project (Microsoft). MCP Apps: production (CopilotKit/Anthropic ecosystem). OpenAI Apps SDK: production (later standardized into MCP Apps). Microsoft Agent Framework 1.0: production-ready (released April 2026). Amazon Bedrock AgentCore AG-UI support: infrastructure-level production.

---

## 1. Protocol Layer Map

The agentic UI protocol stack as of July 2026 comprises five distinct but interoperating standards. Each operates at a different layer of the stack and solves a different problem. Understanding the boundaries between them is essential for correct architecture decisions.

```text
AGENTIC UI PROTOCOL STACK — LAYER MODEL

┌─────────────────────────────────────────────────────────────────────────┐
│  PRESENTATION  Web · Mobile · Desktop · Voice · IDE · Teams / Slack    │
│  RENDER ENGINE CopilotKit · React Native · Terminal · Custom shells    │
└──────────────────────────────┬──────────────────────────────────────────┘
                               │  AG-UI Protocol
                               │  Server→Client: HTTP + Server-Sent Events
                               │  Client→Server: HTTP POST (actions)
┌──────────────────────────────▼──────────────────────────────────────────┐
│  AG-UI — Agent-to-User-Interface Transport Protocol                    │
│  Concern: HOW events flow between agent and user interface              │
│  Events: TEXT_MESSAGE_* · TOOL_CALL_* · STATE_* · RUN_* · STEP_* ...  │
│  Capabilities: streaming · generative UI · state sync · HITL · nesting │
└──────────────────────────────┬──────────────────────────────────────────┘
                               │  A2UI JSON payload (in AG-UI CUSTOM event)
┌──────────────────────────────▼──────────────────────────────────────────┐
│  A2UI v0.9 — Agent-to-UI Surface Definition (Google)                  │
│  Concern: WHAT the UI surface looks like (declarative widget JSON)     │
│  Widget types: text · form · table · chart · card · carousel · action  │
│  Rendering: framework-agnostic, host renders natively                   │
└─────────────┬────────────────┬──────────────────┬───────────────────────┘
              │                │                  │
┌─────────────▼────┐ ┌─────────▼───────┐ ┌────────▼──────────────────────┐
│  MCP             │ │  A2A            │ │  NLWeb                        │
│  Model Context   │ │  Agent-to-Agent │ │  Conversational Web           │
│  Protocol        │ │  (Google)       │ │  (Microsoft open project)     │
│  Concern:        │ │  Concern:       │ │  Concern:                     │
│  agent ↔ tool    │ │  agent ↔ agent  │ │  agent ↔ web content          │
│  Tool routing    │ │  Task deleg.    │ │  Schema.org/RSS + vector       │
│  Auth / authz    │ │  Agent Cards    │ │  Every instance = MCP server   │
│  Rate limiting   │ │  Scoped trust   │ │  Cloudflare AutoRAG native    │
└──────────────────┘ └─────────────────┘ └───────────────────────────────┘

ORACLE OPEN AGENT SPEC — THREE-LAYER MODEL
  Tier 1  Oracle Open Agent Spec  defines WHAT capabilities an agent has
  Tier 2  AG-UI                   defines HOW transport and interaction stream
  Tier 3  A2UI                    defines WHAT the UI surface renders

RELATIONSHIP SUMMARY
  AG-UI   transport layer — does NOT replace MCP or A2A
  A2UI    surface layer — travels inside AG-UI as CUSTOM event payload
  NLWeb   instances are MCP servers; their content is agent-discoverable
  MCP Apps = MCP servers that bundle UI resource components with tools
  OpenAI Apps SDK later standardized as part of the MCP Apps pattern
```

### 1.1 Protocol Responsibility Matrix

| Concern | AG-UI | A2UI | MCP | A2A | NLWeb | MCP Apps |
| --- | --- | --- | --- | --- | --- | --- |
| Text streaming | Primary | No | No | No | No | No |
| Generative UI rendering | Carries payload | Primary definition | No | No | No | Renders alongside tool |
| Tool invocation (backend) | Event emission | No | Primary | No | No | Yes (bundled) |
| Tool invocation (frontend) | Primary | No | No | No | No | Yes |
| State synchronization | Primary | No | No | No | No | No |
| Agent-to-agent delegation | No | No | No | Primary | No | No |
| Human-in-the-loop | Primary | Via A2UI forms | No | No | No | Via approval gate |
| Web content querying | No | No | Via NLWeb MCP | No | Primary | No |
| Authentication / authorization | Transport-level | No | Primary | Scoped | MCP-inherited | Primary |
| Nested agent composition | Primary | No | No | Complementary | No | No |

---

## 2. AG-UI Deep Dive

AG-UI (Agent-User Interface Protocol) is an open, lightweight, event-based protocol that standardizes communication between AI agents and user-facing applications. It builds atop HTTP and WebSockets as an abstraction layer, handling the complexities of streaming intermediate agent work, nondeterministic execution behavior, and mixed structured/unstructured I/O.

**GitHub:** `ag-ui-protocol/ag-ui` (Apache 2.0)  
**First-party backend integrations:** LangGraph, CrewAI, Microsoft Agent Framework 1.0, Google ADK, AWS Strands, Bedrock AgentCore, Mastra, PydanticAI, Agno, LlamaIndex, AG2  
**In-progress backends:** OpenAI Agent SDK, Cloudflare Agents  
**First-party client:** CopilotKit  
**Additional clients:** React Native, Terminal clients  
**Additional SDKs:** Kotlin, Golang, Dart, Java, Rust; .NET and Nim in progress

### 2.1 Event Taxonomy

AG-UI communication is entirely event-driven. The server emits a stream of typed events; the client renders incrementally as events arrive. Every event carries a `type` field that determines how it is processed.

| Event Type | Direction | Purpose | Carries |
| --- | --- | --- | --- |
| `RUN_STARTED` | Server → Client | Signals that an agent run has begun | `run_id`, `thread_id`, metadata |
| `RUN_FINISHED` | Server → Client | Signals successful run completion | `run_id`, final status, timing |
| `RUN_ERROR` | Server → Client | Signals agent run failure | `run_id`, error code, message, retry hint |
| `STEP_STARTED` | Server → Client | A named agent step has begun | `step_name`, `step_id`, description |
| `STEP_FINISHED` | Server → Client | A named agent step has completed | `step_id`, duration, result summary |
| `TEXT_MESSAGE_START` | Server → Client | A new text message stream has started | `message_id`, role |
| `TEXT_MESSAGE_CONTENT` | Server → Client | Incremental text token delivery | `message_id`, `delta` (string) |
| `TEXT_MESSAGE_END` | Server → Client | Text message stream complete | `message_id`, full message summary |
| `TOOL_CALL_START` | Server → Client | Agent is about to call a tool | `tool_call_id`, `tool_name`, pause hint |
| `TOOL_CALL_ARGS` | Server → Client | Streaming tool call arguments | `tool_call_id`, `delta` (JSON string) |
| `TOOL_CALL_END` | Server → Client | Tool call arguments complete | `tool_call_id`, full args |
| `TOOL_CALL_RESULT` | Server → Client | Tool execution result | `tool_call_id`, result, error |
| `STATE_SNAPSHOT` | Server → Client | Full state store snapshot | Typed state object |
| `STATE_DELTA` | Server → Client | Incremental state update (JSON Patch RFC 6902) | `delta` (JSON Patch operations array) |
| `MESSAGES_SNAPSHOT` | Server → Client | Full conversation history snapshot | Messages array |
| `RAW` | Server → Client | Pass-through of raw backend data | Arbitrary payload (for debugging / custom use) |
| `CUSTOM` | Server → Client | Protocol extension point | Typed payload including A2UI surface definitions |

#### Event Ordering Guarantees

- Events within a single run arrive in causal order (TCP-ordered SSE stream)
- `TOOL_CALL_START` always precedes `TOOL_CALL_ARGS` for the same `tool_call_id`
- `TOOL_CALL_ARGS` events stream incrementally; `TOOL_CALL_END` marks completion
- `STATE_DELTA` events are applied in order; each produces a new consistent state
- `RUN_ERROR` may arrive at any point; client must handle it from any state

### 2.2 Transport Architecture

AG-UI operates over HTTP and Server-Sent Events for request-response patterns. The client initiates a request to `/agent/run` with messages and state; the server responds with a streaming event sequence. For bidirectional requirements like collaborative workspaces, WebSocket transport is supported.

The transport model ensures that complex interactions like human-in-the-loop approval gates can be handled through explicit action endpoints: when an agent pauses for approval, the client displays an interface and posts back to `/agent/action` with the user's decision. The server then resumes the agent run.

State is synchronized through snapshots and deltas. The agent emits `STATE_SNAPSHOT` to initialize or fully replace the client state store, and `STATE_DELTA` for incremental updates using JSON Patch format. This allows the client to maintain a consistent view of shared state even across reconnections.

### 2.3 State Synchronization Model

AG-UI implements an event-sourced state synchronization model. The state store is a typed key-value structure. The agent emits `STATE_SNAPSHOT` to initialize state and `STATE_DELTA` for incremental updates. Deltas use JSON Patch (RFC 6902) format, allowing fine-grained updates like replacing a single field or appending to a list without transmitting the entire state.

Client-to-server state writes are handled separately. When the client needs to update state (e.g., user preference changes), it posts to `/agent/action` with an action containing the state path and value. The server applies the update, validates it, and confirms by re-emitting a `STATE_DELTA` event. This pattern supports optimistic UI updates with server-authoritative conflict resolution.

### 2.4 Tool Lifecycle

AG-UI distinguishes two categories of tools based on execution location and authorization model:

Backend tools execute in the agent runtime and carry the agent's authorization credentials. These tools can access protected resources and cause side effects. Frontend tools execute in the browser or mobile client and use the user's browser credentials. Frontend tools are typically used for user-facing operations like camera access or clipboard manipulation.

Both tool categories support human-in-the-loop gates. When a tool is marked `hitl: true` in a `TOOL_CALL_START` event, the client pauses execution and displays an approval UI. The user reviews the proposed arguments and decides whether to approve, reject, or modify the call. Only after the user's decision does the agent proceed or replan.

### 2.5 Generative UI Modes

AG-UI supports two distinct modes for generating dynamic UI:

In static or typed mode, the agent selects from a pre-registered component schema and returns structured JSON matching that schema. The client has a component registry that maps component names to React or native components. The agent's job is simply to select the right component and populate its props. This mode is predictable and requires no runtime code generation.

In declarative or dynamic mode, the agent emits a full A2UI JSON surface definition that describes the entire widget tree. The client renders this tree using its native components without requiring any component registry. The agent has full control over the UI surface on a per-request basis, enabling truly adaptive UI. This mode is more powerful but requires the client to validate and render arbitrary widget structures.

### 2.6 HITL Interrupts

AG-UI's HITL model supports five distinct interrupt types, each corresponding to a user decision point:

The `pause` type halts execution when a tool call is marked for human review. The client displays the tool's arguments and waits for the user to approve, edit the arguments, request a retry with a different strategy, or escalate to a human agent. The `approve` type executes the tool with the original arguments. The `edit` type allows the user to modify arguments before execution. The `retry` type asks the agent to replan the current step with different logic or different context. The `escalate` type transfers the conversation to a human agent and records the escalation context for the human to review.

### 2.7 Nested Agent Composition

AG-UI supports nested agent composition where a parent agent can delegate to child agents. Each child agent opens its own AG-UI sub-stream with independently scoped state. The parent agent receives state snapshots from each child and can merge results before writing to the parent state. This pattern enables multi-agent systems where tasks are decomposed and delegated to specialized agents while maintaining a unified UX and audit trail.

### 2.8 Middleware Architecture

AG-UI backends typically implement a standard middleware chain. Authentication middleware validates the incoming bearer token or mTLS cert. Rate limiting middleware enforces per-user and per-tenant request limits. Context middleware assembles context: conversation history, user preferences, memory stores. Policy middleware evaluates authorization rules against the request. The agent runner executes the actual agent logic. Guardrail middleware filters outbound events for PII, safety, and policy compliance. Observability middleware attaches OpenTelemetry spans for tracing and metrics. Finally, the SSE serializer formats the events as a streaming response.

CopilotKit's MCPAppsMiddleware integrates between the agent runner and guardrail layers. When an agent calls an MCP App tool, the middleware intercepts the `TOOL_CALL_START` event, resolves the UI resource from the MCP registry, and emits a `CUSTOM` event with the A2UI surface definition before the tool result is processed.

### 2.9 Security Model

AG-UI requires TLS 1.3 for all connections. Authentication is enforced via bearer tokens or API keys in the Authorization header; enterprise deployments use short-lived JWTs with audience binding and OBO (on-behalf-of) flows for delegated identity. Event stream integrity is preserved by the TLS layer; additional message-level HMAC signing can be added for high-assurance contexts.

State store access is agent-authoritative: the client reads state but cannot initiate writes directly. Writes must go through the agent via `/agent/action` and the agent is responsible for validation. Tool calls carry the agent's authorization token; tool APIs must validate this token. CUSTOM events carrying A2UI surfaces or third-party payloads must be validated against JSON Schema before rendering. Output guardrails should filter tool results before they reach the TEXT_MESSAGE stream to prevent prompt injection attacks. Rate limiting is enforced at the middleware layer on a per-user and per-tenant basis. Audit logging captures all AG-UI events with OTel correlation IDs for later analysis.

A significant security risk exists when malicious MCP servers or compromised tool APIs inject arbitrary CUSTOM events into the stream. These events could carry fake approval buttons or UI elements designed to trick the user. Organizations must maintain an allowlist of trusted MCP servers, sandbox UI components in iframes with strict CSP policies, and validate all CUSTOM event payloads against registered schemas before rendering.

### 2.10 Code Examples

AG-UI can be implemented in any backend language. The Python example demonstrates a minimal FastAPI server using sse-starlette for streaming. The `/agent/run` endpoint receives a POST request with messages and state, yields a series of AG-UI events formatted as SSE data lines, and streams them back to the client.

The TypeScript example shows the same pattern with Express. Both examples include a tool call lifecycle with HITL pause, token generation, and result handling. A real implementation would add proper error handling, circuit breakers, and observability instrumentation.

### 2.11 CopilotKit React Frontend Integration

CopilotKit provides a React library that abstracts away AG-UI stream handling. Applications wrap their components in a `<CopilotKit>` provider pointing at an AG-UI backend. The `useCopilotReadable` hook exposes app state to the agent. The `useCopilotAction` hook registers frontend-callable tools and specifies a `render` function for HITL UI. When the agent triggers this action, the render function displays the approval panel, and the `handler` is called only after the user approves.

This is Part 1 of 3. **[Continue with Part 2 →](pathname:///archon/agentic-systems/agentic-ui/parts/02-agui-standards-landscape-part2) to explore A2UI, MCP Apps, and NLWeb.**
