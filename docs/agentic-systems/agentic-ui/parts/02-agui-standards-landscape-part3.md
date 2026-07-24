---
title: "AGUI Standards & Ecosystem Landscape — Part 3"
date_created: 2026-07-24
last_reviewed: 2026-07-24
status: current
domain: agentic-systems
doc_type: guide
topic_id: agui-standards-landscape-part3
covers_version: "as of 2026-07-10"
supersedes: []
---

# OpenAI Apps SDK, Microsoft Agent Framework, and Production Deployment

This is Part 3 of 3. **[Back to Part 1](pathname:///archon/agentic-systems/agentic-ui/02-agui-standards-landscape) · [Back to Part 2](pathname:///archon/agentic-systems/agentic-ui/parts/02-agui-standards-landscape-part2)**

## 6. OpenAI Apps SDK

The OpenAI Apps SDK was an early standardization of the MCP Apps pattern, using JSON-RPC 2.0 over the browser's `postMessage` API as the transport layer between the host application and the AI-powered app component. It remains in production use but organizations should plan migration to the MCP Apps standard for future projects.

### 6.1 Architecture

An OpenAI App runs in an iFrame sandbox with strict Content Security Policy isolation. The app component is a React or Web Component that uses the `openai/apps-sdk-ui` library for standard UI components. Communication with the host application occurs via `postMessage` using JSON-RPC 2.0 format. The host bridge receives tool-input notifications from the app, delivers tool results after user approval, and enforces CSP.

### 6.2 JSON-RPC 2.0 Transport

The SDK defines JSON-RPC 2.0 methods for bidirectional communication. `ui/render` requests rendering of a component. `ui/notifications/tool-input` delivers user-approved tool arguments to the app. `tools/execute` requests tool execution from the host. `tools/result` delivers execution results back to the app. `user/approve` and `user/reject` signal user approval or rejection of a tool call.

### 6.3 Card UI Model

OpenAI Apps SDK cards support a title, rich text body, up to two primary actions, and metadata key-value pairs. The two-action limit was a deliberate UX constraint to avoid decision paralysis on approval cards. This constraint is more restrictive than A2UI's richer widget catalog.

### 6.4 Approval Flow

When an agent proposes a tool call, the host receives the arguments. The host delivers arguments to the app via `ui/notifications/tool-input`. The app renders an approval card with the proposed arguments. The user approves or rejects in the card UI. The app notifies the host of the decision. The host either executes the tool (approve) or cancels (reject). The host delivers the result back to the app via `tools/result`.

### 6.5 Relationship to MCP Apps

The OpenAI Apps SDK pattern (tool + UI bundle in a sandboxed component, approval gate required) was the precursor to MCP Apps. MCP Apps improvements include protocol standardization across vendors (not OpenAI-specific), native AG-UI integration (no postMessage bridge required), richer widget catalog (A2UI) versus fixed card schema, and centralized enterprise MCP registry support. Organizations using OpenAI Apps SDK should plan migration to MCP Apps when it reaches full production maturity.

---

## 7. Microsoft Agent Framework 1.0

Microsoft Agent Framework 1.0 was released in April 2026 as a production-ready multi-agent orchestration framework for Python and .NET. It includes first-party AG-UI integration via the `HttpAgent` endpoint pattern.

### 7.1 Core Capabilities

The framework supports multi-agent orchestration, multi-provider model support (Azure OpenAI, OpenAI, Anthropic, Bedrock), AG-UI transport with SSE streaming, HITL interrupt support, Azure managed identity authentication, OpenTelemetry integration, and enterprise SLA through Azure support.

### 7.2 AG-UI Integration Pattern

A React frontend using CopilotKit communicates with an HttpAgent endpoint via AG-UI SSE streams. The HttpAgent endpoint maps CopilotKit messages to Agent Framework internal messages and maps Agent Framework events back to AG-UI events. It handles HITL pause/approve/reject via the `/agent/action` endpoint. The Agent Orchestrator coordinates multiple specialized agents (Research, Analysis, Report Writing, etc.) that execute in parallel or sequence. Results are aggregated and streamed back to the frontend.

### 7.3 Azure Deployment Targets

Microsoft Agent Framework runs on multiple Azure compute options. Azure App Service is suitable for simple HTTP agent endpoints. Azure Container Apps works well for microservices architectures with ingress controller support. Azure Kubernetes Service (AKS) handles high-scale enterprise deployments with HPA auto-scaling. Azure Functions works for event-driven agent triggers but Premium plan is recommended for SSE support.

### 7.4 Code Example

An Agent Framework implementation defines specialized agents with `run()` methods that receive an `AgentRunContext`. Agents emit steps, call tools, and return results. An OrchestratorAgent delegates to sub-agents and merges their outputs. An `HttpAgentEndpoint` maps this to a FastAPI router with AG-UI adapter and authentication.

---

## 8. Framework Comparison Matrix

The following matrix covers 15 frameworks and protocols relevant to enterprise agentic UI architecture. Enterprise Readiness (L1–L5) is assessed across production deployments, enterprise SLA, governance tooling, security certifications, and multi-tenant support.

| Framework / Protocol | Protocol | Frontend Framework | Backend Framework | Streaming | Generative UI | HITL Support | MCP Compatible | A2A Compatible | Enterprise Readiness | License | Maturity |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| **AG-UI** | AG-UI (own) | Any | Any | Native (SSE) | Yes (static + A2UI) | Native (pause/approve/edit/retry) | Complementary | Complementary | L4 | Apache 2.0 | Production |
| **CopilotKit** | AG-UI | React (primary) | Any AG-UI backend | AG-UI stream | Yes (component registry + A2UI) | Yes (useCopilotAction render) | Yes (MCPAppsMiddleware) | Via orchestrator | L4 | MIT | Production |
| **A2UI** | Carried in AG-UI | Host-rendered | AG-UI backend | Via AG-UI | Native (is the spec) | Via AG-UI | No | No | L2 (v0.9 experimental) | Google | Experimental |
| **NLWeb** | MCP (as server) | N/A (query API) | Python | No | No | No | Native (IS MCP server) | No | L3 | MIT | Production |
| **OpenAI Apps SDK** | JSON-RPC 2.0/postMessage | React | OpenAI platform | No (postMessage) | Card UI | Yes (approval gate) | Evolving → MCP Apps | No | L3 | MIT | Production |
| **Microsoft Agent Framework 1.0** | AG-UI (HttpAgent) | CopilotKit (via AG-UI) | Python, .NET | AG-UI SSE | Via AG-UI + A2UI | AG-UI HITL | Yes | Yes (A2A) | L5 | MIT | Production (Apr 2026) |
| **Vercel AI SDK** | Streaming (custom) | React/Next.js | Node.js | Yes (RSC + stream) | React Server Components | Partial (no standard) | Partial | No | L3 | Apache 2.0 | Production |
| **LangGraph** | AG-UI (1st party) | CopilotKit (via AG-UI) | Python, JS | AG-UI native | Via AG-UI | Via AG-UI | Yes | Yes | L4 | MIT | Production |
| **Semantic Kernel** | AG-UI (planned) | .NET/Python | .NET, Python | Partial | Partial (plugin UI) | Manual implementation | Yes | Partial | L4 | MIT | Production |
| **AutoGen / AG2** | AG-UI (1st party) | CopilotKit (via AG-UI) | Python | AG-UI native | Via AG-UI | Via AG-UI | Yes | Yes | L3 | MIT | Production |
| **CrewAI** | AG-UI (1st party) | CopilotKit (via AG-UI) | Python | AG-UI native | Via AG-UI | Via AG-UI | Yes | Yes | L3 | MIT | Production |
| **Agno** | AG-UI (1st party) | CopilotKit (via AG-UI) | Python | AG-UI native | Via AG-UI | Via AG-UI | Yes | No | L2 | Apache 2.0 | Beta |
| **Mastra** | AG-UI (1st party) | CopilotKit (via AG-UI) | TypeScript | AG-UI native | Via AG-UI | Via AG-UI | Yes | No | L2 | Apache 2.0 | Beta |
| **PydanticAI** | AG-UI (1st party) | CopilotKit (via AG-UI) | Python | AG-UI native | Via AG-UI | Via AG-UI | Yes | No | L3 | MIT | Production |
| **Google ADK** | AG-UI (1st party) + A2UI | Any (via AG-UI) | Python | AG-UI native | A2UI native | Via AG-UI | Yes | Yes (A2A native) | L4 | Apache 2.0 | Production |

Enterprise Readiness Scale: L1 (Proof of concept only), L2 (Experimental/early adopter), L3 (Production-ready, limited enterprise features), L4 (Production-ready, enterprise features including SLA and multi-tenant support), L5 (Enterprise-grade, certified, full lifecycle support).

---

## 9. Decision Tree: Which Protocol or Framework Should I Choose?

Start with the question: Do you need to stream agent output to a user interface in real time? If no, consider batch/async agent patterns. If yes, does the interface need dynamic UI components? If no, use AG-UI with TEXT_MESSAGE streaming only (LangGraph, CrewAI, or PydanticAI work well). If yes, is the UI surface determined by the agent at runtime? If no, use a static component registry in AG-UI CUSTOM events. If yes, consider A2UI (v0.9 experimental) or A2UI with explicit version pinning.

Given that AG-UI is confirmed, what is your primary backend ecosystem? Python-only suggests LangGraph, CrewAI, PydanticAI, or Agno. .NET/C# suggests Microsoft Agent Framework 1.0 or Semantic Kernel. TypeScript/Node.js suggests Mastra or Vercel AI SDK. Multi-language suggests Microsoft Agent Framework 1.0 (Python + .NET). Cloud-managed suggests AWS Bedrock AgentCore.

What are your HITL requirements? Formal approval workflow with named approver suggests CopilotKit with useCopilotAction render or Microsoft Agent Framework 1.0 HITL tools. Simple yes/no approval works with any AG-UI framework. No HITL needed means any AG-UI framework.

Do you need MCP tool integration? Tools with bundled UI suggest CopilotKit MCPAppsMiddleware. Tools without UI suggest any MCP-compatible backend (LangGraph, Mastra, PydanticAI). No MCP means direct tool calling in your chosen framework.

Enterprise readiness requirements? L5 (Azure SLA, certified, .NET + Python) suggests Microsoft Agent Framework 1.0. L4 (production, multi-tenant, governance tooling) suggests LangGraph + CopilotKit + AG-UI or Google ADK + A2UI. L3 (production, basic enterprise) suggests PydanticAI, CrewAI, or AutoGen. L2 (beta, growing projects) suggests Agno or Mastra.

Special cases: Making website content agent-queryable? Use NLWeb. Cloudflare-hosted content? Use Cloudflare AutoRAG. OpenAI platform existing investment? Use OpenAI Apps SDK but plan migration to MCP Apps.

---

## 10. Production Considerations

### 10.1 Operational Requirements Checklist

Before deploying any agentic UI system to production, ensure:

**Transport:** TLS 1.3 on all AG-UI connections, mutual TLS for backend-to-agent connections, connection timeout configured for idle SSE, SSE reconnection logic in client, WebSocket fallback for SSE-blocking environments.

**Authentication:** Short-lived JWTs with audience binding, OBO flow configured for enterprise tool access, API key rotation policy, rate limiting per user per tenant.

**Reliability:** AG-UI server behind load balancer with sticky sessions, run state persisted to durable storage (not in-memory only), interrupt handler does not leak resources on cancellation, TOOL_CALL_RESULT retry on transient failures.

**Observability:** OTel spans on every AG-UI event with trace ID propagation, run_id and thread_id in all log lines, metrics for events/second, HITL approval rate, run duration, and error rate, append-only audit log with tool call args plus user identity plus decision.

**Security:** CUSTOM event payload validated against JSON Schema, MCP App UI resources sandboxed (CSP iframe), tool call args sanitized before execution, output guardrails on TEXT_MESSAGE stream (PII scrubbing, safety checks).

**Testing:** AG-UI conformance test suite against all event types, load test with 100 concurrent SSE streams, chaos test covering mid-stream tool failure, SSE disconnect, and timeout, HITL approval latency test for P99 round-trip time.

For detailed guidance on observability beyond this checklist, see the companion guide on OTel GenAI semantic conventions and burn rate dashboards. For security hardening beyond this page, see the Agentic AI Security & Identity guide and its OWASP ASI mapping.

---

## Conclusion

The agentic UI ecosystem in July 2026 is mature and feature-rich, with multiple standards and frameworks addressing different organizational needs. AG-UI has emerged as the standard transport protocol, with A2UI providing a declarative UI surface specification. MCP Apps standardizes the bundling of tools with UI components. Organization must select frameworks based on backend ecosystem, enterprise readiness requirements, and HITL complexity.

For most organizations, the combination of LangGraph + CopilotKit + AG-UI provides the best balance of production-readiness, flexibility, and ecosystem maturity. For organizations with .NET requirements or multi-language needs, Microsoft Agent Framework 1.0 is the only L5-grade option. For organizations requiring maximum agent control and want to avoid component registry dependencies, A2UI provides a path forward, though v0.9 remains experimental.

**This is Part 3 of 3. [Back to Part 1](pathname:///archon/agentic-systems/agentic-ui/02-agui-standards-landscape) · [Back to Part 2](pathname:///archon/agentic-systems/agentic-ui/parts/02-agui-standards-landscape-part2)**
