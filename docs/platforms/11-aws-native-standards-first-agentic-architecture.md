---
title: "AWS-Native, Standards-First Agentic Platform Architecture"
doc_type: guide
domain: platforms
status: current
topic_id: aws-native-standards-first-agentic-architecture
last_reviewed: 2026-07-27
maturity: practitioner
supersedes: [docs/cloud-platforms/aws/AWS_Native_Standards_First_Agentic_Architecture.md]
tags: [aws, agentcore, strands, reference-architecture, standards, mcp, a2a]
covers_version: "N/A"
---

# AWS-NATIVE, STANDARDS-FIRST AGENTIC PLATFORM ARCHITECTURE

Reference Architecture for Conversational AI, Agent Memory, and Multi-Agent Systems on Amazon Bedrock AgentCore + Strands

Interoperable via MCP, A2A, AG-UI, OpenTelemetry, OpenAPI & AsyncAPI

**AGENTCORE STRANDS 1.0**

**MCP**

**A2A AG-UI**

**OTEL**

###### ROLE LENSES APPLIED:

Enterprise Architecture . AWS AI/ML . Platform Engineering . Security Architecture . Agentic Systems

## 9

## 7

**15**

**2**

Architecture Layers

Open Standards

Anti-Patterns Mapped

Medium Lock-In Points

->  Part 1: Architecture Principles & Standards Map

- ->  Part 2: Layered Reference Architecture (AWS Services)

->  Part 3: Memory, Session & Multi-Agent Design

->  Part 4: Security, Governance & Anti-Lock-In Strategy

Reference Architecture  .  June 2026  .  Confidential

Principal Architecture Group

## TABLE OF CONTENTS

|**Executive Summary**|**3**|
|---|---|
|**Part 1: Architecture Principles & Standards Map**|**4**|
|1.1 Design Principles|4|
|1.2 Standards-to-AWS-Service Mapping|5|
|1.3 The Anti-Lock-In Contract|6|
|**Part 2: Layered Reference Architecture**|**7**|
|2.1 Architecture Overview Diagram|7|
|2.2 Layer 1: Client & Experience (AG-UI)|8|
|2.3 Layer 2: API & Gateway (OpenAPI/AsyncAPI)|8|
|2.4 Layer 3: Agent Runtime (AgentCore + Strands)|9|
|2.5 Layer 4: Tool & Integration (MCP)|10|
|2.6 Layer 5: Multi-Agent Coordination (A2A)|11|
|2.7 Layer 6: Memory & Knowledge|12|
|2.8 Layer 7: Data & Storage|13|
|2.9 Layer 8: Observability (OpenTelemetry)|14|
|2.10 Layer 9: Security & Governance|15|
|**Part 3: Memory, Session & Multi-Agent Design**|**16**|
|3.1 Conversation & Session Persistence on AWS|16|
|3.2 Memory Architecture with AgentCore Memory|17|
|3.3 Multi-Agent Topology with Strands + A2A|18|
|3.4 Agent Recovery & Durable Execution|19|
|**Part 4: Security, Governance & Anti-Lock-In Strategy**|**20**|
|4.1 Identity, Auth & Tenant Isolation|20|
|4.2 Governance & Compliance Mapping|20|
|4.3 Anti-Pattern Cross-Reference|21|
|4.4 Portability & Exit-Strategy Design|22|
|**Appendix: Service & Standards Reference Tables**|**23**|
|**Appendix: Infrastructure-as-Code Skeleton**|**25**|

## Executive Summary

This document specifies a reference architecture for a production-grade conversational AI and multi-agent platform that is AWS-native by default but standards-first by design. Amazon Bedrock AgentCore provides the managed runtime, memory, gateway, and observability substrate; Strands Agents (1.0) provides the agent orchestration framework. Every external boundary of the system—client communication, tool access, agent-to-agent coordination, API contracts, and telemetry—is implemented against an open standard (AG-UI, MCP, A2A, OpenAPI, AsyncAPI, OpenTelemetry) so that AWS-specific services can be replaced without rewriting the agents, tools, or client applications that depend on them.

### Architectural Thesis

The thesis is straightforward: AWS services should sit *behind* standard protocol boundaries, never define them. AgentCore Runtime hosts agents, but agents are invoked via A2A-compliant task requests. AgentCore Gateway exposes tools, but those tools are described via MCP. AgentCore Memory persists state, but the memory access pattern is abstracted so an alternative memory provider (mem0, Letta, a self-hosted store) could be substituted. This is not a hedge against AWS—it is the pattern that makes the platform composable, auditable, and resilient to both vendor and protocol churn.

### Key Architectural Decisions

|**Concern**|**Primary Choice**|**Rationale**|
|---|---|---|
|Runtime|Amazon Bedrock AgentCore Runtime<br/>(primary)|Managed, serverless, checkpointed agent execution with session isolation;<br/>framework-agnostic so Strands is a choice, not a constraint.|
|Agent Framework|Strands Agents 1.0<br/>(Python/TypeScript)|AWS-built, open-source (Apache 2.0), model-agnostic, native A2A + OTel<br/>support; multi-agent orchestration as of 1.0 (May 2026).|
|Tool Access|MCP via AgentCore Gateway|Every tool—AWS-native or third-party—exposed as an MCP server; agents<br/>and IDEs consume identical tool definitions.|
|Agent<br/>Coordination|A2A Protocol|Cross-agent and cross-vendor task delegation; AgentCore Runtime agents<br/>are A2A-addressable endpoints.|
|Client Interface|AG-UI Protocol|Event-driven, bidirectional agent-to-frontend streaming; decouples UI<br/>framework from agent runtime.|
|API Contracts|OpenAPI 3.1 + AsyncAPI 3.0|Synchronous tool/service APIs documented in OpenAPI; event-driven and<br/>streaming interfaces in AsyncAPI.|
|Observability|OpenTelemetry -> AWS Distro for OTel<br/>(ADOT)|Vendor-neutral instrumentation; AWS collector as default export target,<br/>swappable for Honeycomb/Datadog/Grafana.|
|Memory|AgentCore Memory + abstraction layer|Short-term (session) and long-term (semantic/episodic) memory via managed<br/>service, accessed through a provider-agnostic interface.|

**INFO:** Reading guide: Part 1 establishes principles and the standards-to-service mapping that everything else derives from. Part 2 walks the architecture layer by layer with concrete AWS service choices. Part 3 details memory, session persistence, and multi-agent design—the hardest problems identified in prior research. Part 4 covers security, governance, and the specific mechanisms that prevent lock-in from becoming a liability.

##### PART 1

## Architecture Principles & Standards Map

*Eight principles govern every decision in this architecture. They are written as testable constraints, not aspirations.*

### 1.1 Design Principles

#### P1 — Protocols at the boundary, services behind it

Every external interface (client, tool, agent-to-agent, telemetry) is defined by an open standard. AWS services implement one side of that interface; they never become the interface itself. Test: could a non-AWS implementation of this component be swapped in by changing configuration, not code, at the consuming layer?

#### P2 — AWS-native is the default, not the constraint

Where AWS offers a managed service that implements a standard well (AgentCore Runtime for agent hosting, AgentCore Gateway for MCP), use it—operational simplicity matters. But the choice is justified by standards compliance plus operational fit, not by AWS being the only option considered.

#### P3 — Memory and conversation state are portable by construction

Conversation, session, and long-term memory records are stored in formats and schemas that do not depend on a single vendor's proprietary memory API. AgentCore Memory is the primary store, accessed through an internal abstraction that could be re-pointed at another provider (Section 3.2).

#### P4 — Every agent is independently addressable and replaceable

Agents are A2A endpoints first, AgentCore Runtime workloads second. A specialized agent built on a different framework (LangGraph, CrewAI, Claude Agent SDK) can participate in the same multi-agent system as long as it exposes an A2A-compliant interface.

#### P5 — Observability is structural, not bolted on

OpenTelemetry instrumentation is present from the first agent, exported through ADOT to a vendor-neutral pipeline. Trace, span, and log correlation IDs flow through A2A and MCP calls so a single request can be reconstructed end-to-end regardless of which AWS service or external agent handled which step.

#### P6 — Governance is encoded in infrastructure, not policy documents

Tenant isolation, data residency, deletion cascades, and audit logging are implemented as infrastructure constraints (IAM policies, resource tagging, automated pipelines)—not as procedures that depend on engineers remembering to follow them.

#### P7 — Durability is assumed for any multi-step agent task

Any agent workflow involving more than one tool call or external side effect runs under AgentCore Runtime's checkpointing, with idempotency keys on state-changing tool calls. 'It might fail partway through' is a default assumption, not an edge case.

#### P8 — Anti-patterns from prior research are design constraints

The fifteen anti-patterns catalogued in prior research (context window dependence, unlimited memory growth, missing checkpointing, cross-tenant query leakage, etc.) map directly to specific mitigations in this architecture (Section 4.3). Each is a named constraint with an owner, not a general caution.

### 1.2 Standards-to-AWS-Service Mapping

This is the master cross-reference: for each open standard, which AWS service implements the AWS-native path, what the standard guarantees regardless of implementation, and what the swap-out path looks like if the AWS service is later replaced.

|**Standard**|**AWS-Native Implementation**|**What the Standard Guarantees**|**Swap-Out Path**|
|---|---|---|---|
|MCP (Model<br/>Context Protocol)|AgentCore Gateway exposes<br/>Lambda functions, APIs, and AWS<br/>services as MCP tool servers|Tool definitions, schemas, and<br/>invocation semantics are identical for<br/>any MCP client (Claude, IDE agents,<br/>Strands agents)|Point agents at any MCP-compliant<br/>gateway (self-hosted, Anthropic's<br/>reference implementation,<br/>third-party); tool contracts<br/>unchanged|
|A2A (Agent2Agent<br/>Protocol)|AgentCore Runtime agents (via<br/>Strands 1.0) expose A2A task<br/>endpoints natively|Any A2A-compliant agent—regardless<br/>of framework or host—can be<br/>discovered and delegated to|Replace AgentCore-hosted agents<br/>with agents on other runtimes<br/>(self-hosted, other clouds); A2A task<br/>contracts unchanged|
|AG-UI (Agent-UI<br/>Protocol)|Client applications connect to<br/>AgentCore Runtime via an<br/>AG-UI-compliant gateway layer (API<br/>Gateway + Lambda adapter)|Frontend frameworks (React, custom<br/>clients) consume a standard event<br/>stream regardless of backend agent<br/>implementation|Swap the agent backend (different<br/>AgentCore agent, different<br/>framework entirely) without frontend<br/>changes|
|OpenTelemetry|ADOT (AWS Distro for<br/>OpenTelemetry) Collector, with<br/>Strands' native OTel<br/>instrumentation|Traces, metrics, and logs use OTel<br/>semantic conventions; correlation IDs<br/>are vendor-neutral|Re-point the ADOT collector's<br/>exporter from CloudWatch/X-Ray to<br/>Honeycomb, Datadog, Grafana<br/>Cloud, or self-hosted Jaeger|
|OpenAPI 3.1|API Gateway REST/HTTP APIs<br/>defined via OpenAPI specs;<br/>AgentCore Gateway tool definitions<br/>derived from OpenAPI where<br/>applicable|Synchronous service contracts are<br/>machine-readable and<br/>codegen-compatible across any API<br/>gateway|Import the same OpenAPI spec into<br/>another API gateway (Kong, Apigee,<br/>self-hosted)|
|AsyncAPI 3.0|EventBridge, SQS, and AppSync<br/>Events (for streaming) document<br/>event contracts via AsyncAPI|Event-driven and streaming contracts<br/>(agent status updates, async task<br/>completion) are documented<br/>independent of the broker|Re-implement the event contract on<br/>Kafka, NATS, or another broker<br/>using the same AsyncAPI spec|
|MCP Memory<br/>Extensions /<br/>Provider-agnostic<br/>memory API|AgentCore Memory (short-term<br/>session + long-term<br/>semantic/episodic stores)|Internal memory abstraction layer<br/>presents a consistent read/write/search<br/>interface to agents regardless of<br/>backing store|Re-point the abstraction layer at<br/>mem0, Letta, or a custom<br/>Postgres+pgvector store; agent code<br/>unchanged|

### 1.3 The Anti-Lock-In Contract

Lock-in is not binary—it is a spectrum of switching cost. This architecture does not pretend switching away from AWS is free; it ensures the switching cost is proportional to genuine value received (operational simplicity, managed scaling, integrated security) rather than artificial cost imposed by proprietary interfaces. The contract below states, for each major AWS service used, what would need to change to replace it.

|**AWS Service**|**Lock-In**<br/>**Level**|**Replacement Path**|**What Changes**|
|---|---|---|---|
|Amazon Bedrock AgentCore<br/>Runtime|Medium|Re-host agent containers on another<br/>A2A-compliant runtime (self-managed ECS/EKS +<br/>open-source A2A server, or another cloud's agent<br/>runtime). Strands agent code is<br/>unchanged—Strands is framework-agnostic and<br/>runs anywhere.|Checkpointing/recovery semantics<br/>must be re-implemented (e.g., via<br/>Temporal or LangGraph persistence)<br/>since AgentCore's managed<br/>checkpointing is proprietary.|
|Amazon Bedrock AgentCore<br/>Gateway|Low|Any MCP-compliant gateway can replace it. Tool<br/>definitions (MCP schemas) are portable by design.|Re-point MCP client configuration;<br/>no agent code changes.|
|Amazon Bedrock AgentCore<br/>Memory|Medium|Re-point the internal memory abstraction layer at<br/>mem0, Letta, or self-hosted<br/>Postgres+pgvector/OpenSearch.|Bulk export/migration of existing<br/>memory records required;<br/>abstraction layer interface<br/>unchanged so agent code is<br/>unaffected.|
|Amazon Bedrock (model<br/>access)|Low|Strands is model-agnostic; swap the model<br/>provider configuration (Anthropic direct, OpenAI,<br/>self-hosted via SageMaker/Bedrock Marketplace).|Prompt tuning may be needed<br/>across model families; no<br/>architectural change.|
|Amazon API Gateway /<br/>AppSync|Low|Any API gateway that can host<br/>OpenAPI/AsyncAPI-defined routes and an AG-UI<br/>adapter.|Re-deploy gateway configuration<br/>from IaC; client-facing contracts<br/>(AG-UI, OpenAPI) unchanged.|
|Amazon CloudWatch / X-Ray<br/>(via ADOT)|Very Low|Re-point ADOT Collector exporter configuration to<br/>any OTLP-compatible backend.|No code change; configuration-only<br/>switch.|
|Amazon DynamoDB / Aurora<br/>(conversation store)|Medium|Schema is standard relational/document design<br/>(per prior research data models); export and<br/>re-import to PostgreSQL, CockroachDB, or another<br/>store.|Migration effort proportional to data<br/>volume; no architectural redesign<br/>needed since schema was designed<br/>store-agnostic.|

**DECISION:** Net assessment: the highest lock-in points (AgentCore Runtime's managed checkpointing, AgentCore Memory's storage format) are also the components delivering the most operational value—this is an acceptable, deliberate trade rather than an oversight. The architecture ensures these are the *only* two components with non-trivial switching cost, isolated behind the abstraction layers described in Sections 2.4 and 3.2.

##### PART 2

## Layered Reference Architecture

*Nine layers, each with a standards-defined interface and a primary AWS implementation. Layers communicate only through their declared standard—no layer reaches into another layer's internals.*

### 2.1 Architecture Overview

```
|  LAYER 1: CLIENT & EXPERIENCE                                       |
|  Web / Mobile / IDE clients  <--AG-UI (event stream)-->             |
```

```
                              |
```

```
                  AG-UI Gateway Adapter (API Gateway + Lambda)
                              |
```

```
|  LAYER 2: API & GATEWAY                                              |
|  Amazon API Gateway (OpenAPI 3.1)  +  AppSync Events (AsyncAPI 3.0)  |
|  Amazon Cognito (OIDC / OAuth2)                                      |
                              |
```

```
|  LAYER 3: AGENT RUNTIME                                              |
|  Amazon Bedrock AgentCore Runtime                                    |
|  Strands Agents 1.0 (orchestrator + specialist agents)               |
|  - A2A endpoint per agent        - OTel auto-instrumentation         |
        |                     |                        |
   (MCP)|                (A2A)|                  (Memory API)|
        v                     v                        v
```

```
+================+   +==================+    +========================+
| LAYER 4: TOOLS |   | LAYER 5: MULTI-  |    | LAYER 6: MEMORY &      |
| AgentCore      |   | AGENT COORD.     |    | KNOWLEDGE              |
| Gateway (MCP)  |   | A2A Protocol     |    | AgentCore Memory       |
| -> Lambda      |   | -> Strands agents|    | + abstraction layer    |
| -> 3rd-party   |   | -> external A2A  |    | -> short-term (session)|
|    MCP servers |   |    agents (any   |    | -> long-term (semantic,|
| -> AWS APIs    |   |    framework)    |    |    episodic, KG)       |
+================+   +==================+    +========================+
        |                     |                        |
|  LAYER 7: DATA & STORAGE                                             |
|  Aurora PostgreSQL (pgvector) | DynamoDB | S3 | OpenSearch | Neptune |
                              |
```

```
|  LAYER 8: OBSERVABILITY                                              |
|  OpenTelemetry SDK -> ADOT Collector -> CloudWatch / X-Ray /         |
|  (swappable: Honeycomb, Datadog, Grafana, Jaeger)                    |
                              |
```

```
|  LAYER 9: SECURITY & GOVERNANCE                                      |
|  IAM + Cognito + KMS + Resource Tags + Audit Log (immutable S3/QLDB) |
```

Layers 4, 5, and 6 are peers, not a stack—the agent runtime calls each independently via its respective protocol. This is the key structural decision: tools (MCP), other agents (A2A), and memory are three distinct integration surfaces, each governed by a different standard, each independently swappable.

### 2.2 Layer 1: Client & Experience (AG-UI)

AG-UI (CopilotKit, open protocol since early 2025) standardizes bidirectional, event-driven communication between agents and frontends—agent state updates, streaming tokens, tool-call visibility, and human-in-the-loop interrupts all flow over a single typed event stream.

• **AWS implementation:** An AG-UI adapter (Lambda behind API Gateway WebSocket or HTTP/2 streaming) translates between AgentCore Runtime's native streaming response format and AG-UI event types (RUN_STARTED, TEXT_MESSAGE_CONTENT, TOOL_CALL_START, STATE_DELTA, etc.).

- **Why not expose AgentCore's native protocol directly:** doing so would couple every client (web, mobile, IDE

- plugin, third-party integration) to AWS-specific message formats. The AG-UI adapter is a thin, stateless translation layer—cheap to maintain, and it means any AG-UI-compatible frontend component library works unmodified.

- **Human-in-the-loop:** AG-UI's interrupt/resume event types map directly onto AgentCore Runtime's

- checkpoint/resume primitives (Section 3.4)—an approval request pauses the agent, the checkpoint persists, and resumption is a normal AG-UI resume event.

### 2.3 Layer 2: API & Gateway (OpenAPI / AsyncAPI)

All synchronous request/response contracts (auth, conversation CRUD, artifact retrieval) are defined in OpenAPI 3.1. All asynchronous contracts (agent run status events, long-task completion notifications, streaming progress) are defined in AsyncAPI 3.0. Both specs are checked into source control and drive code generation for client SDKs.

- **Amazon API Gateway (HTTP API)** hosts the OpenAPI-defined synchronous routes; the spec is uploaded as the API

- Gateway definition source, keeping the gateway configuration and the contract in lock-step.

- **Amazon Cognito** issues OAuth2/OIDC tokens validated by API Gateway authorizers—standard JWT validation,

- portable to any OIDC-compliant identity provider (Auth0, Okta, Keycloak) by reconfiguring the authorizer, not rewriting the API.

- **AWS AppSync Events** (or EventBridge + WebSocket API) implements the AsyncAPI-defined event channels for

- agent status streaming when AG-UI's own transport isn't used directly by a consumer (e.g., backend-to-backend integrations).

- **Why this matters:** a partner integrating via API never needs to know AgentCore exists. They consume

- OpenAPI/AsyncAPI specs—identical to specs a non-AWS implementation would publish.

*Part 1 of 4. Continued in [Part 2](parts/11-aws-native-standards-first-agentic-architecture-part2.md).*
