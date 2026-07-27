---
title: "AWS-Native, Standards-First Agentic Platform Architecture (Part 2: Layers 2-6)"
doc_type: guide
domain: platforms
status: current
topic_id: aws-native-standards-first-agentic-architecture-part2
last_reviewed: 2026-07-27
maturity: practitioner
supersedes: []
tags: [aws, agentcore, strands, reference-architecture, standards, mcp, a2a]
covers_version: "N/A"
---

*Part 2 of 4 of [AWS-Native, Standards-First Agentic Platform Architecture](../11-aws-native-standards-first-agentic-architecture.md). Continued in [Part 3](11-aws-native-standards-first-agentic-architecture-part3.md).*

### 2.4 Layer 3: Agent Runtime (AgentCore + Strands)

This is the heart of the platform. Amazon Bedrock AgentCore Runtime provides the managed, serverless execution environment—session isolation, checkpointing, scaling to thousands of concurrent invocations. Strands Agents 1.0 (Apache 2.0, AWS open-source) provides the agent loop, multi-agent orchestration primitives, and native OpenTelemetry + A2A support.

#### Why AgentCore Runtime

- Framework-agnostic by design—AgentCore documentation explicitly supports Strands, LangGraph, CrewAI, and custom frameworks packaged as containers; choosing Strands is a recommendation, not a requirement imposed by the runtime.

- Managed checkpointing and recovery: agents resume from interruption without custom durable-execution code (directly addresses anti-pattern AP-07, Missing Checkpointing, from prior research).

- Session isolation per invocation: each conversation/session runs in an isolated execution context, addressing cross-tenant leakage risk (AP-15) at the runtime level.

#### Why Strands Agents 1.0

- Model-agnostic: works with Anthropic, OpenAI, Meta Llama, and self-hosted models via Bedrock or direct API—no architectural dependency on a single model provider.

- Native multi-agent orchestration (as of v1.0, May 2026) including A2A protocol support and a remote session manager—directly enables Layer 5 (Section 2.6) without bespoke glue code.

- Native OpenTelemetry instrumentation—Layer 8 observability (Section 2.9) is populated automatically, not bolted on.

- Open source (Apache 2.0) with broad industry contribution (Accenture, Anthropic, Meta, PwC, Langfuse, mem0.ai, Tavily)—reduces single-vendor risk in the framework layer itself, distinct from the runtime layer.

**AWS NATIVE:** Agent packaging pattern: each Strands agent (orchestrator and specialists) is packaged as a container image with a standard entrypoint. AgentCore Runtime hosts the container; the container itself has zero AgentCore-specific imports beyond a thin runtime adapter shim. This shim is the only file that would need to change to run the same container on, e.g., self-managed Fargate with an open-source A2A server.

#### Agent container structure (illustrative)

```
agent-orchestrator/
```

```
+-- Dockerfile
```

```
+-- pyproject.toml                # strands-agents, opentelemetry-* deps
```

```
+-- src/
```

- `|   +-- main.py                   # entrypoint; AgentCore runtime adapter`

- `|   +-- agent.py                  # Strands Agent definition (model, prompt, tools)`

- `|   +-- tools/`

- `|   |   +-- mcp_client.py         # MCP client config (Layer 4)`

- `|   +-- a2a/`

- `|   |   +-- delegate.py           # A2A client for sub-agent calls (Layer 5)`

- `|   +-- memory/`

- `|   |   +-- memory_adapter.py     # provider-agnostic memory interface (Layer 6)`

- `|   +-- observability/`

- `|       +-- otel_setup.py         # OTel SDK init, ADOT exporter config`

- `+-- runtime_adapter/`

- `+-- agentcore_shim.py          # &lt;- ONLY AgentCore-specific file`

### 2.5 Layer 4: Tool & Integration (MCP)

Every capability an agent can invoke—AWS service calls, internal microservices, third-party SaaS integrations—is exposed as an MCP tool server. Amazon Bedrock AgentCore Gateway is the primary mechanism for converting existing AWS resources (Lambda functions, OpenAPI-described APIs) into MCP-compliant tool servers without rewriting them.

- **AgentCore Gateway** ingests an OpenAPI spec or Lambda function ARN and produces an MCP server exposing

- each operation as a tool—this is the bridge between Layer 2's OpenAPI contracts and Layer 3's tool-calling agents.

• **Third-party MCP servers** (e.g., a CRM, a ticketing system, a code-search tool) are connected directly—AgentCore Gateway can proxy/aggregate multiple MCP servers behind one endpoint, but agents can also connect to external MCP servers directly via Strands' MCP client support.

• **Tool governance:** AgentCore Gateway's IAM integration means tool access is scoped per-agent (or per-session) using standard AWS IAM policies—an agent's MCP tool list is the intersection of 'tools the gateway knows about' and 'tools this agent's IAM role permits'.

• **Idempotency (addresses AP-13):** state-changing MCP tools (create/update/delete operations) are designed with idempotency-key parameters from the OpenAPI spec stage—Lambda implementations check a DynamoDB idempotency table before executing side effects.

#### MCP tool manifest example

```
{
  "name": "create_support_ticket",
```

```
  "description": "Create a ticket in the support system",
```

- `"inputSchema": {`

```
    "type": "object",
```

```
    "properties": {
```

```
      "title": {"type": "string"},
```

```
      "description": {"type": "string"},
      "priority": {"type": "string", "enum": ["low","medium","high"]},
```

```
      "idempotency_key": {
```

```
        "type": "string",
        "description": "Client-generated UUID; required for safe retries"
      }
    },
    "required": ["title", "description", "idempotency_key"]
  }
}
```

- `// Backed by: AgentCore Gateway -> Lambda -> DynamoDB idempotency check`

- `//            -> Ticketing system API (OpenAPI-described)`

### 2.6 Layer 5: Multi-Agent Coordination (A2A)

Strands 1.0's native A2A support means every agent—orchestrator or specialist—is an A2A-addressable endpoint by default. Multi-agent coordination (manager/planner/research/coding/reviewer patterns from prior research) is implemented as A2A task delegation between Strands agents, each independently hosted on AgentCore Runtime.

- **Discovery:** agents publish A2A 'agent cards' (capability descriptions) to an internal registry (can be as simple as a

- DynamoDB table or as rich as a dedicated A2A registry service); the orchestrator discovers specialist agents by capability, not by hardcoded endpoint.

- **Cross-framework interoperability:** because A2A is the coordination contract, a specialist agent built on LangGraph,

- CrewAI, or the Claude Agent SDK can be delegated to identically—as long as it exposes an A2A task endpoint. This directly satisfies the requirement to avoid framework lock-in at the multi-agent layer.

- **Cross-organization patterns:** A2A's HTTP-based transport and task lifecycle (synchronous, streaming, or

- async-with-notification) support delegating to agents outside the platform entirely—a partner's agent, a different business unit's agent mesh—using the same protocol as internal delegation.

- **Context compaction (addresses prior research finding A.6):** sub-agents return compact A2A task results

- (structured summaries) to the orchestrator rather than raw tool output, keeping the orchestrator's context window focused on decision-making.

#### A2A task delegation flow (Strands orchestrator -> specialist)

`1. Orchestrator agent (Strands, AgentCore Runtime) receives user request`

`2. Orchestrator's planning step identifies need for "financial analysis"`

`3. Orchestrator queries agent registry for capability="financial-analysis"`

- `-> resolves to Specialist Agent X (A2A endpoint, also on AgentCore Runtime,`

- `OR a different team's agent on a different runtime entirely)`

`4. Orchestrator sends A2A task request:`

- `POST https://specialist-x.internal/a2a/tasks`

- `{ "input": {...}, "context_id": "<conversation_id>",`

- `"callback": "<orchestrator A2A endpoint>" }`

`5. Specialist Agent X executes (own AgentCore session, own memory,`

- `own OTel trace span linked via traceparent header)`

`6. Specialist returns A2A task result (structured summary, not raw data)`

`7. Orchestrator incorporates result into its own context (compacted)`

`8. OTel trace shows: orchestrator span -> A2A call span -> specialist span`

- `-> specialist's internal tool-call spans (full trace, Section 2.9)`

### 2.7 Layer 6: Memory & Knowledge

Amazon Bedrock AgentCore Memory provides both short-term (session/working) memory and long-term (semantic, episodic) memory as managed services. Per Principle P3, agents access memory exclusively through an internal abstraction layer—the memory taxonomy from prior research (working, episodic, semantic, procedural, project, organizational, agent) maps onto AgentCore Memory's primitives plus supplementary stores where needed.

|**Memory Type**|**Primary Store**|**Access Pattern**|**Notes**|
|---|---|---|---|
|Working / Session|AgentCore Memory (short-term)|Read/write via memory adapter, scoped<br/>to session ID|Auto-managed lifecycle tied to<br/>AgentCore Runtime session|
|Episodic|AgentCore Memory (long-term) +<br/>Aurora (pgvector)|Semantic search via adapter;<br/>embeddings in pgvector for hybrid search|Provenance tag (Section 3.2)<br/>stored alongside each record|
|Semantic (user facts)|AgentCore Memory (long-term)|Extracted async post-conversation;<br/>conflict-checked on write|TTL + importance score fields<br/>per prior-research best practice<br/>D.1|
|Procedural|S3 (versioned) + Aurora metadata|Agent playbooks/prompts retrieved by<br/>orchestrator at session start|Versioned like artifacts; not part<br/>of AgentCore Memory|
|Project / Org|Aurora + OpenSearch (full-text) +<br/>S3 (documents)|Project-scoped retrieval; shared across<br/>conversations in a project|Maps to 'Projects' construct from<br/>prior research Part 10|
|Knowledge Graph|Amazon Neptune (optional, Graph<br/>RAG)|Entity/relationship traversal combined<br/>with vector search|Added when multi-hop retrieval<br/>quality (Part A.3, prior research)<br/>justifies the investment|

#### Memory abstraction interface (illustrative)

```
class MemoryProvider(Protocol):
```

- `# Provider-agnostic interface. AgentCore Memory is the default`

- `# implementation; mem0/Letta/custom Postgres implementations satisfy`

- `# the same interface for swap-out (Section 1.3).`

```
    async def write(self, record: MemoryRecord) -> str:
```

- `# record includes: content, type (episodic|semantic|procedural),`

- `# provenance (user_stated|agent_inferred|tool_derived),`

- `# importance_score, valid_from, valid_until (optional) ...`

```
    async def search(self, query: str, scope: MemoryScope,
                      top_k: int = 5) -> list[MemoryRecord]:
        # scope = session | project | user | org
        ...
```

```
    async def check_conflicts(self, record: MemoryRecord) -> list[MemoryRecord]:
```

- `# Retrieve potentially-contradictory existing records`

- `# before write (mitigates AP-11, No Conflict Resolution) ...`

```
# Default binding:
```

```
provider: MemoryProvider = AgentCoreMemoryAdapter(memory_id=...)
```

- `# Swap-out binding (no agent code changes required):`

- `# provider: MemoryProvider = Mem0Adapter(config=...)`

- `# provider: MemoryProvider = PostgresPgvectorAdapter(dsn=...)`

**DECISION:** This abstraction is the single most important anti-lock-in mechanism for memory (Section 1.3). It costs one interface definition and a thin adapter; it buys the ability to migrate memory infrastructure—driven by cost, capability, or compliance—without touching agent logic.

### 2.8 Layer 7: Data & Storage

Storage selections follow the storage taxonomy established in prior research (Part 1, Section 1.1): relational for metadata/transactions, document/object for content, vector for semantic search, graph for relationships, event log for audit/CQRS.

|**Storage Need**|**AWS Service**|**Standard/Format**|**Portability Note**|
|---|---|---|---|
|Conversation & message<br/>metadata|Aurora PostgreSQL (Serverless<br/>v2)|Standard SQL schema (per prior<br/>research Part 1.2)|pg_dump/restore to any<br/>Postgres-compatible target|
|Vector embeddings|Aurora PostgreSQL + pgvector<br/>extension|pgvector (open-source extension)|Standard pgvector; portable to<br/>any Postgres with the<br/>extension|
|Large artifacts (code, docs,<br/>images)|Amazon S3|Content-addressable, versioned<br/>objects|S3 API is a de facto standard;<br/>S3-compatible APIs (MinIO,<br/>R2) available everywhere|
|Full-text & hybrid search|Amazon OpenSearch Service|OpenSearch (Apache 2.0,<br/>Elasticsearch-API-compatible fork)|OpenSearch is itself<br/>open-source; self-hostable|
|Knowledge graph (optional)|Amazon Neptune|Gremlin / openCypher (open query<br/>languages)|Query language portable to<br/>Neo4j, JanusGraph, etc.|
|Event log / audit trail|Amazon EventBridge -> S3<br/>(WORM)|CloudEvents-formatted events<br/>(CNCF standard)|CloudEvents format is<br/>broker-agnostic|
|Session cache (hot path)|Amazon ElastiCache (Redis<br/>OSS)|Redis protocol (open-source)|Standard Redis; portable to<br/>any Redis-compatible cache|

**PRINCIPLE:** Every storage choice in this layer uses either an open-source engine (Postgres, OpenSearch, Redis) run as a managed AWS service, or an open data format (CloudEvents, Gremlin/openCypher) on a proprietary engine (Neptune). This is the practical version of 'standards-first': pay AWS for operational convenience, but never for a proprietary data format you cannot extract.

### 2.9 Layer 8: Observability (OpenTelemetry)

Every component—AG-UI adapter, API Gateway/Lambda, Strands agents, MCP tool calls, A2A delegations, memory adapter calls—emits OpenTelemetry traces, metrics, and logs using OTel semantic conventions for generative AI (gen_ai.* attributes). The AWS Distro for OpenTelemetry (ADOT) Collector is the default export path; this is purely an export destination choice, not an instrumentation choice.

- **Trace correlation across protocol boundaries:** traceparent (W3C Trace Context) headers propagate through

- AG-UI events, A2A task requests, and MCP tool calls—a single user request produces one trace spanning the orchestrator, every delegated specialist agent, and every tool invocation, regardless of which AWS service or external system handled each span.

- **Strands' native instrumentation** emits spans for the agent loop (model invocation, tool selection, tool execution)

- automatically—this directly populates the 'tool trace persistence' data model from prior research Part 6 without custom instrumentation code.

- **Sampling policy (addresses AP-06, Trace Explosion):** ADOT Collector applies tail-based sampling—100%

- retention for traces containing errors or exceeding a latency threshold, 1-5% sampling for fully successful traces—configured once at the collector, not per-service.

- **Export targets:** ADOT Collector ships traces to AWS X-Ray and CloudWatch by default; metrics to CloudWatch; logs

- to CloudWatch Logs. Re-pointing to Honeycomb, Datadog, Grafana Cloud, or self-hosted Jaeger/Prometheus/Loki is an ADOT Collector configuration change (OTLP exporter endpoint + credentials)—zero application code changes.

#### OTel resource & span attributes (gen_ai semantic conventions)

```
# Span: agent invocation
gen_ai.system = "strands"
gen_ai.agent.name = "orchestrator"
gen_ai.request.model = "anthropic.claude-sonnet-4-6"
gen_ai.operation.name = "chat"
session.id = "<conversation_id>"
enduser.id = "<user_id>"          # hashed/pseudonymized per Section 4.1
tenant.id = "<workspace_id>"       # critical for AP-15 mitigation
```

```
# Child span: MCP tool call
gen_ai.tool.name = "create_support_ticket"
gen_ai.tool.call.id = "<idempotency_key>"
```

```
# Child span: A2A delegation
peer.service = "specialist-financial-analysis"
a2a.task.id = "<task_id>"
traceparent = "00-<trace_id>-<span_id>-01"   # propagated to specialist
```

### 2.10 Layer 9: Security & Governance

Security is enforced at every layer boundary using AWS IAM as the policy engine, but the policies themselves encode standards-defined identities (OIDC subjects, A2A agent identities, MCP tool scopes)—so the *rules* are portable even though the *enforcement engine* is AWS-specific.

- **Identity:** Amazon Cognito issues OIDC tokens; AgentCore Runtime sessions, A2A task requests, and MCP tool calls

- all carry the originating user's OIDC subject claim through the entire call chain—every span in Layer 8 can be attributed to a user and tenant.

- **Tenant isolation:** every Aurora query, OpenSearch query, and AgentCore Memory call is scoped by tenant_id at the

- query level (not post-filtered)—directly mitigating AP-15 (Cross-Tenant Query Without Scoping). IAM policies additionally enforce resource-level tenant boundaries for S3 and DynamoDB.

• **Encryption:** AWS KMS customer-managed keys (CMKs), one per tenant for regulated workloads, encrypt Aurora, S3, and AgentCore Memory at rest. CMK rotation and per-tenant key isolation support both GDPR/CCPA requirements and customer-managed-key compliance demands.

• **Audit trail:** every state-changing action (memory write, tool call with side effects, agent run completion) emits a CloudEvents-formatted audit event to EventBridge, archived to an S3 bucket with Object Lock (WORM) for immutability—satisfying the 'immutable audit log' requirement from prior research Part 13.

- **Deletion cascade (addresses AP-14):** a single 'delete tenant/user data' Step Functions workflow orchestrates

deletion across Aurora, S3, OpenSearch, AgentCore Memory, and Neptune—triggered by a DeletionRequest record (per prior research data model) and tracked to completion with SLA monitoring.

**AWS NATIVE:** Guardrails: Amazon Bedrock Guardrails (content filtering, PII redaction, topic restrictions) are applied at the model-invocation layer within Strands agents. Guardrail policies are configuration, not code—but the

*outcomes* (what gets filtered, what gets redacted) should be specified in a portable policy format (e.g., a YAML policy document) so the same governance intent could be re-implemented against another provider's moderation layer if needed.

##### PART 3
