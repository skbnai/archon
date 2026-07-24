---
title: "AGUI Standards & Ecosystem Landscape: Framework Comparison (Part 3)"
date_created: 2026-07-24
last_reviewed: 2026-07-24
status: current
domain: agentic-systems
doc_type: reference-architecture
topic_id: agui-standards-landscape-part3
covers_version: "as of 2026-07-10"
---

This is part 3 of 3.

**Related:** [Part 1](../02-agui-standards-landscape.md) · [Part 2](../parts/02-agui-standards-landscape-part2.md)

---

## 5. NLWeb

NLWeb is a Microsoft open project that makes any website queryable via natural language. It uses Schema.org markup, RSS feeds, and existing semi-structured web data as a knowledge source, adds vector search and an LLM query layer, and exposes the result via natural language API. Every NLWeb instance is simultaneously an MCP server, making website content discoverable by AI agents.

**GitHub:** `nlweb-ai/NLWeb` (MIT)  
**Reference implementation:** Python  
**Vision:** "Play a similar role to HTML in the emerging agentic web"  
**Cloudflare integration:** Native NLWeb support via AutoRAG (added early 2026)

### 5.1 Architecture

```mermaid
graph TB
    Q["External Agent / User<br/>Natural language query:<br/>'What are your refund policies for software subscriptions?'"]
    Q --> QL

    subgraph QL["NLWeb Query Layer"]
        S1["1. Parse intent from natural language"]
        S2["2. Extract structured filters (Schema.org entity types)"]
        S3["3. Vector search over indexed content"]
        S4["4. LLM synthesis of relevant chunks"]
        S5["5. Return grounded answer with source citations"]
        S1 --> S2 --> S3 --> S4 --> S5
    end

    QL -- "reads from" --> VI["Vector Index<br/>(chunked site content)"]
    QL -- "reads from" --> SRC["Schema.org / RSS Source Data<br/>Existing website HTML, Schema.org JSON-LD,<br/>RSS/Atom feeds, product catalogs, docs, FAQs"]

    QL -.->|"also exposes"| MCP["MCP server endpoint<br/>tools: search_content, get_page, list_topics<br/>Every NLWeb instance is agent-discoverable;<br/>Cloudflare AutoRAG uses this pattern natively"]
```

*NLWeb architecture: a query layer parses natural-language questions, searches a vector index built from the site's existing Schema.org/RSS data, and synthesizes a grounded answer — while the same instance also exposes itself as an MCP server.*

### 5.2 Cloudflare AutoRAG Integration

Cloudflare added native NLWeb support via AutoRAG in early 2026. This allows any Cloudflare-hosted website to become an NLWeb-compatible MCP server without self-hosting infrastructure:

| Deployment Model | Setup | Scalability | Cost | Governance |
| --- | --- | --- | --- | --- |
| **Self-hosted NLWeb (Python)** | Clone repo, configure data sources, deploy | Manual scaling | Self-managed | Full control |
| **Cloudflare AutoRAG** | Enable in Cloudflare dashboard, point at content | Auto-scaling (Cloudflare edge) | Usage-based | Cloudflare data processing |
| **Azure AI Search + NLWeb adapter** | Custom integration | Enterprise-scale | Azure consumption | Azure governance |

### 5.3 NLWeb vs. Competing Approaches

| Approach | Query Type | Data Source | Setup Complexity | Agent Integration | Governance |
| --- | --- | --- | --- | --- | --- |
| **NLWeb** | Natural language | Existing website content (Schema.org/RSS) | Low (uses existing markup) | Native MCP server | Content owner controlled |
| **Custom RAG** | Natural language | Any document corpus | High (ingestion, chunking, embedding) | Requires MCP wrapper | Fully custom |
| **Azure AI Search** | Keyword + semantic | Enterprise documents | Medium (index configuration) | Requires MCP wrapper | Microsoft/enterprise |
| **Enterprise portal (SharePoint)** | Keyword | SharePoint content | Low (built-in) | Requires Copilot plugin | Microsoft 365 governance |
| **Knowledge assistant (Guru, Confluence AI)** | Natural language | Internal wiki content | Low | Vendor-specific | Vendor governed |

**Choose NLWeb when:**

- The organization has an existing public-facing website with Schema.org markup or RSS
- The goal is to make existing web content queryable by AI agents without rebuilding the knowledge base
- Low-friction agent integration (every NLWeb instance is already an MCP server) is a priority
- The Cloudflare AutoRAG deployment model is acceptable for the data classification

**Choose Custom RAG when:**

- The knowledge base contains proprietary enterprise documents not suitable for a public-facing NLWeb instance
- Fine-grained access control per document/chunk is required
- The organization requires specific embedding models or retrieval strategies
- Compliance requirements prohibit processing through third-party infrastructure (Cloudflare)

**Do not use NLWeb when:**

- The content is classified or subject to regulatory data residency requirements
- The content is not already in a semi-structured form (Schema.org, RSS, HTML)
- Real-time data (stock prices, live inventory) is required — NLWeb is search-based, not live-query

### 5.4 Governance Considerations

:::warning Public Exposure Risk
    Every NLWeb instance is, by design, publicly queryable as an MCP server. This makes previously navigational-only website content fully extractable by any agent that discovers the MCP endpoint. Organizations must review their website content against data classification policies before enabling NLWeb.

| Governance Concern | Mitigation |
| --- | --- |
| Unintended data exposure | Audit all content indexed by NLWeb before enabling; use `noindex` meta tags for excluded content |
| Rate limit abuse | Implement per-caller rate limiting at the MCP server layer |
| Data freshness | Configure crawl/re-index frequency; stale content may produce incorrect agent responses |
| Competitive intelligence extraction | NLWeb makes structured extraction trivial; ensure no proprietary information is on the indexed website |
| PII in web content | Scan website content for PII before indexing; NLWeb does not automatically redact |

---

## 6. OpenAI Apps SDK

The OpenAI Apps SDK was an early standardization of the MCP Apps pattern, using JSON-RPC 2.0 over the browser's `postMessage` API as the transport layer between the host application and the AI-powered app component.

### 6.1 Architecture

```mermaid
graph TB
    subgraph Host["Browser Host Application"]
        subgraph Frame["iFrame sandbox (CSP-isolated)"]
            Comp["OpenAI App Component (React/Web Component)<br/>Uses openai/apps-sdk-ui: Button, Card, Input, Layout"]
        end
        Bridge["Host Bridge<br/>Receives tool-input notifications from app<br/>Delivers tool results after user approval<br/>Enforces content security policy"]
    end
    Frame -- "postMessage (JSON-RPC 2.0)" --> Bridge
```

*OpenAI Apps SDK architecture: the app component runs inside a CSP-isolated iframe and communicates with the host bridge exclusively via JSON-RPC 2.0 over `postMessage`.*

### 6.2 JSON-RPC 2.0 Transport

| Method | Direction | Purpose |
| --- | --- | --- |
| `ui/render` | App → Host | Request rendering of a UI component |
| `ui/notifications/tool-input` | Host → App | Deliver user-approved tool arguments |
| `tools/execute` | App → Host | Request tool execution |
| `tools/result` | Host → App | Deliver tool execution result |
| `user/approve` | Host → App | Signal user approval of a tool call |
| `user/reject` | Host → App | Signal user rejection |

### 6.3 Card UI Model

OpenAI Apps SDK cards support:

- **Title** — string
- **Body** — rich text or structured data
- **Up to two primary actions:** each action is either a conversation turn or a tool call
- **Metadata** — key-value pairs displayed below card body

The two-action limit was a deliberate UX constraint: avoid decision paralysis on approval cards.

### 6.4 Approval Flow

```mermaid
sequenceDiagram
    participant Agent
    participant Host
    participant App as App Component
    participant User

    Agent->>Host: propose tool call
    Host->>App: deliver args via ui/notifications/tool-input
    App->>User: render approval card with proposed args
    User->>App: approve or reject
    App->>Host: notify of user decision
    Host->>Host: execute tool (approve) or cancel (reject)
    Host->>App: deliver result via tools/result
```

*OpenAI Apps SDK approval flow: the host mediates every step between the agent's tool proposal and the app component's approval card, only executing after explicit user approval.*

### 6.5 Relationship to MCP Apps

The OpenAI Apps SDK pattern (tool + UI bundle in a sandboxed component, approval gate required) was the precursor to the MCP Apps specification. Organizations using the OpenAI Apps SDK should plan migration to the MCP Apps standard when it reaches full production maturity, as MCP Apps provides:

- Protocol standardization across vendors (not OpenAI-specific)
- Native AG-UI integration (no postMessage bridge required)
- Richer widget catalog (A2UI) vs. fixed card schema
- Centralized enterprise MCP registry support

---

## 7. Microsoft Agent Framework 1.0

Microsoft Agent Framework 1.0 was released in April 2026 as a production-ready multi-agent orchestration framework for Python and .NET. It includes first-party AG-UI integration via the `HttpAgent` endpoint pattern.

### 7.1 Core Capabilities

| Capability | Python SDK | .NET SDK |
| --- | --- | --- |
| Multi-agent orchestration | Yes | Yes |
| Multi-provider model support | Yes (Azure OpenAI, OpenAI, Anthropic, Bedrock) | Yes |
| AG-UI transport (HttpAgent) | Yes | Yes |
| SSE streaming | Yes | Yes |
| HITL interrupt support | Yes | Yes |
| Azure managed identity | Yes | Yes |
| OpenTelemetry integration | Yes | Yes |
| Enterprise SLA | Yes (Azure support) | Yes |

### 7.2 AG-UI Integration Pattern

```mermaid
graph TB
    FE["React Frontend (CopilotKit)<br/>&lt;CopilotKit runtimeUrl='/api/copilotkit'&gt;"]
    FE -- "AG-UI (SSE stream)" --> EP

    EP["HttpAgent Endpoint (Microsoft Agent Framework 1.0)<br/>Maps CopilotKit messages ↔ Agent Framework messages<br/>Maps Agent Framework events → AG-UI events<br/>Handles HITL pause/approve/reject via action endpoint"]
    EP -- "Internal agent bus" --> ORCH

    subgraph ORCH["Agent Orchestrator (Agent Framework 1.0)"]
        R[Research Agent]
        A[Analysis Agent]
        W[Report Writing Agent]
    end
```

*Microsoft Agent Framework 1.0 integration: a CopilotKit frontend streams over AG-UI to an HttpAgent endpoint, which translates between CopilotKit and Agent Framework message formats and routes to a multi-agent orchestrator.*

### 7.3 Azure Deployment Targets

| Target | Use Case | AG-UI Connectivity | Scale |
| --- | --- | --- | --- |
| **Azure App Service** | Simple HTTP agent endpoint | Direct HTTPS + SSE | Up to 10 concurrent runs per instance |
| **Azure Container Apps** | Microservices architecture | Ingress controller + SSE | Auto-scale to zero; KEDA event-driven |
| **Azure Kubernetes Service (AKS)** | High-scale enterprise | Nginx ingress + SSE | Unlimited with HPA; best for >100 concurrent |
| **Azure Functions** | Event-driven agent triggers | HTTP trigger + SSE | Cold start latency; use Premium plan for SSE |

### 7.4 Code Example: Agent Framework with AG-UI

=== "Python"

    ```python
    # Microsoft Agent Framework 1.0 + AG-UI HttpAgent
    # pip install microsoft-agent-framework copilotkit-runtime

    from microsoft_agent_framework import (
        AgentApplication, Agent, HttpAgentEndpoint, AgentRunContext
    )
    from microsoft_agent_framework.ag_ui import AGUIAdapter
    from opentelemetry import trace

    tracer = trace.get_tracer("my-agent")

    # Define a specialized agent
    class ResearchAgent(Agent):
        name = "research_agent"
        description = "Searches internal knowledge base and external sources"

        async def run(self, ctx: AgentRunContext) -> str:
            with tracer.start_as_current_span("research_agent.run"):
                # Access AG-UI streaming context
                await ctx.emit_step("research", "Searching knowledge base")
                results = await ctx.call_tool("search_kb", query=ctx.goal)
                await ctx.emit_step_complete("research", f"Found {len(results)} results")
                return "\n".join(r["summary"] for r in results)

    # Orchestrator agent
    class OrchestratorAgent(Agent):
        name = "orchestrator"
        sub_agents = [ResearchAgent()]

        async def run(self, ctx: AgentRunContext) -> str:
            # Delegate to research agent via A2A
            research_result = await ctx.delegate(
                agent="research_agent",
                goal=ctx.goal,
                scoped_state={"session_id": ctx.session_id}
            )
            # Continue with analysis...
            return f"Analysis based on: {research_result}"

    # Create AG-UI-compatible HTTP endpoint
    app = AgentApplication()
    app.register(OrchestratorAgent())

    endpoint = HttpAgentEndpoint(
        app=app,
        adapter=AGUIAdapter(),
        hitl_tools=["write_report", "send_email"],  # tools requiring approval
        auth_provider="azure_managed_identity"
    )

    # Mount as FastAPI endpoint
    from fastapi import FastAPI
    api = FastAPI()
    api.include_router(endpoint.router, prefix="/agent")

    # Deploy with: uvicorn main:api --host 0.0.0.0 --port 8080
    ```

---

## 8. Framework Comparison Matrix

The following matrix covers 15 frameworks and protocols relevant to enterprise agentic UI architecture. Enterprise Readiness (L1–L5) is assessed across: production deployments, enterprise SLA, governance tooling, security certifications, and multi-tenant support.

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

**Enterprise Readiness Scale:**  
L1 = Proof of concept only · L2 = Experimental / early adopter · L3 = Production-ready, limited enterprise features · L4 = Production-ready, enterprise features (SLA, governance, multi-tenant) · L5 = Enterprise-grade, certified, full lifecycle support

---

## 9. Decision Tree: Which Protocol or Framework Should I Choose?

```mermaid
flowchart TD
    START([Start]) --> Q1{Stream agent output<br/>to a UI in real time?}
    Q1 -->|No| BATCH["Consider batch/async agent<br/>pattern; AG-UI not required"]
    Q1 -->|Yes| Q2{Interface needs<br/>dynamic UI components?}
    Q2 -->|No| TXT["AG-UI with TEXT_MESSAGE<br/>streaming only —<br/>LangGraph, CrewAI, or PydanticAI"]
    Q2 -->|Yes| Q3{UI surface determined<br/>by the agent at runtime?}
    Q3 -->|Yes| A2UI["Consider A2UI (v0.9 experimental)"]
    Q3 -->|No| STATIC["Static component registry in<br/>AG-UI CUSTOM events (typed generative UI)"]

    A2UI --> Q4
    STATIC --> Q4
    TXT --> Q4
    Q4{Primary backend ecosystem?}
    Q4 -->|Python only| E1["LangGraph, CrewAI, PydanticAI, Agno"]
    Q4 -->|".NET / C#"| E2["Microsoft Agent Framework 1.0, Semantic Kernel"]
    Q4 -->|TypeScript/Node.js| E3["Mastra, Vercel AI SDK (partial AG-UI)"]
    Q4 -->|Multi-language| E4["Microsoft Agent Framework 1.0 (Python + .NET)"]
    Q4 -->|Cloud-managed| E5["AWS Bedrock AgentCore (AG-UI native)"]

    E1 & E2 & E3 & E4 & E5 --> Q5
    Q5{HITL requirements?}
    Q5 -->|Formal approval workflow| H1["CopilotKit + AG-UI useCopilotAction;<br/>Microsoft Agent Framework 1.0 HITL tools"]
    Q5 -->|Simple yes/no approval| H2["Any AG-UI framework with<br/>TOOL_CALL_START hitl:true"]
    Q5 -->|No HITL needed| H3["Any AG-UI framework;<br/>HOTL monitoring via OTel"]

    H1 & H2 & H3 --> Q6
    Q6{MCP tool integration needed?}
    Q6 -->|Tools with bundled UI| M1["CopilotKit MCPAppsMiddleware;<br/>register tools on MCP App servers"]
    Q6 -->|Tools without bundled UI| M2["Any MCP-compatible AG-UI backend —<br/>LangGraph, Mastra, PydanticAI"]
    Q6 -->|No| M3["Direct tool calling in chosen framework"]

    M1 & M2 & M3 --> Q7
    Q7{Enterprise readiness level?}
    Q7 -->|L5: Azure SLA, certified| R1["Microsoft Agent Framework 1.0"]
    Q7 -->|L4: production, multi-tenant| R2["LangGraph + CopilotKit + AG-UI;<br/>Google ADK + A2UI"]
    Q7 -->|L3: production, basic| R3["PydanticAI, CrewAI, AutoGen/AG2"]
    Q7 -->|L2: beta, growing| R4["Agno, Mastra"]
```

*Protocol/framework selection decision tree: from streaming and dynamic-UI needs, through backend ecosystem, HITL model, MCP integration, to enterprise readiness tier.*

**Special cases:** making website content agent-queryable → NLWeb; Cloudflare-hosted content → Cloudflare AutoRAG (NLWeb pattern); existing OpenAI platform investment → OpenAI Apps SDK, then plan migration to MCP Apps.

---

## 10. Production Considerations

### 10.1 Operational Requirements Checklist

**Transport**
- [ ] TLS 1.3 on all AG-UI connections
- [ ] Mutual TLS for backend-to-agent connections
- [ ] Connection timeout configured (idle SSE connections)
- [ ] SSE reconnection logic in client (EventSource retry)
- [ ] WebSocket fallback for environments blocking SSE

**Authentication**
- [ ] Short-lived JWTs with audience binding
- [ ] OBO flow configured for enterprise tool access
- [ ] API key rotation policy
- [ ] Rate limiting per user per tenant

**Reliability**
- [ ] AG-UI server behind load balancer with sticky sessions (SSE)
- [ ] Run state persisted to durable storage (not in-memory only)
- [ ] Interrupt handler does not leak resources on cancellation
- [ ] TOOL_CALL_RESULT retry on transient tool failures

**Observability**
- [ ] OTel spans on every AG-UI event (trace ID propagated)
- [ ] run_id and thread_id in all log lines
- [ ] Metrics: events/second, HITL approval rate, run duration, error rate
- [ ] Audit log: append-only, tool call args + user identity + decision

**Security**
- [ ] CUSTOM event payload validated against JSON Schema
- [ ] MCP App UI resources sandboxed (CSP iframe)
- [ ] Tool call args sanitized before execution
- [ ] Output guardrails on TEXT_MESSAGE stream (PII, safety)

**Testing**
- [ ] AG-UI conformance test suite against all event types
- [ ] Load test: 100 concurrent SSE streams
- [ ] Chaos test: mid-stream tool failure, SSE disconnect, timeout
- [ ] HITL approval latency test (P99 approval round-trip)

:::tip Cross-Reference: Observability
    For OTel span schema specific to AG-UI events (run spans, step spans, tool call spans), see [Reliability, Observability & Governance](../../../architecture/43-agentic-ai-reliability-observability-governance.md). For security hardening beyond this page, see [Agentic AI Security & Identity](pathname:///archon/trust/agentic-ai-security-identity) OWASP ASI mapping.
