---
title: "AWS-Native, Standards-First Agentic Platform Architecture (Part 4: Governance Mapping, Anti-Patterns, Appendices)"
doc_type: guide
domain: platforms
status: current
topic_id: aws-native-standards-first-agentic-architecture-part4
last_reviewed: 2026-07-27
maturity: practitioner
supersedes: []
tags: [aws, agentcore, strands, reference-architecture, standards, mcp, a2a]
covers_version: "N/A"
---

*Part 4 of 4 of [AWS-Native, Standards-First Agentic Platform Architecture](../11-aws-native-standards-first-agentic-architecture.md).*

## Appendix: Service & Standards Reference

### A.1 Complete AWS Service Inventory

|**Layer**|**AWS Service**|**Open Standard Interface**|**Primary Role**|
|---|---|---|---|
|1. Client|API Gateway (WebSocket/HTTP streaming)|AG-UI|Event stream adapter to clients|
|2. API/Gateway|Amazon API Gateway (HTTP API)|OpenAPI 3.1|Synchronous REST contracts|
|2. API/Gateway|AWS AppSync Events / EventBridge|AsyncAPI 3.0|Event-driven contracts|
|2. API/Gateway|Amazon Cognito|OIDC / OAuth2|Identity provider|
|3. Agent<br>Runtime|Amazon Bedrock AgentCore Runtime|A2A (via Strands)|Agent hosting, checkpointing,<br>scaling|
|3. Agent<br>Runtime|Strands Agents 1.0|A2A, OTel-native|Agent orchestration framework|
|3. Agent<br>Runtime|Amazon Bedrock|(model API)|Foundation model access|
|3. Agent<br>Runtime|Amazon Bedrock Guardrails|(policy config)|Content safety, PII redaction|
|4. Tools|Amazon Bedrock AgentCore Gateway|MCP|Tool exposure from Lambda/APIs|
|4. Tools|AWS Lambda|(implementation)|Tool execution|
|5. Multi-Agent|Amazon Bedrock AgentCore Runtime (per agent)|A2A|Specialist agent hosting|
|6. Memory|Amazon Bedrock AgentCore Memory|(provider-agnostic adapter)|Short & long-term memory|
|7. Data|Aurora PostgreSQL Serverless v2 (+pgvector)|SQL / pgvector|Conversations, metadata, vectors|
|7. Data|Amazon S3|S3 API / CloudEvents (audit)|Artifacts, documents, audit archive|
|7. Data|Amazon OpenSearch Service|OpenSearch API|Full-text & hybrid search|
|7. Data|Amazon Neptune (optional)|Gremlin / openCypher|Knowledge graph (Graph RAG)|
|7. Data|Amazon ElastiCache (Redis OSS)|Redis protocol|Session cache|
|8. Observability|AWS Distro for OpenTelemetry (ADOT)|OpenTelemetry / OTLP|Trace/metric/log collection|
|8. Observability|Amazon CloudWatch, AWS X-Ray|(default export target)|Default telemetry backend|
|9. Security|AWS IAM|(policy engine)|Authorization|
|9. Security|AWS KMS|(encryption)|Encryption key management|
|9. Security|AWS Step Functions|(orchestration)|Deletion cascade, long workflows|
|9. Security|AWS CloudTrail + EventBridge|CloudEvents|Audit logging|

### A.2 Standards Quick Reference

|**Standard**|**Governing Body / Origin**|**Maturity (as of mid-2026)**|**Role in This Architecture**|
|---|---|---|---|
|MCP (Model Context<br>Protocol)|Anthropic (open-sourced)|Production, broad ecosystem<br>adoption|Tool/data access contract (Layer<br>4)|

|**Standard**|**Governing Body / Origin**|**Maturity (as of mid-2026)**|**Role in This Architecture**|
|---|---|---|---|
|A2A (Agent2Agent)|Google, contributed to Linux<br>Foundation|Production; 150+ org adoption,<br>AWS/Azure/GCP support|Agent coordination contract<br>(Layer 5)|
|AG-UI|CopilotKit|Production, growing adoption|Agent-to-frontend event protocol<br>(Layer 1)|
|OpenTelemetry|CNCF|Production, industry standard|Observability instrumentation<br>(Layer 8)|
|OpenAPI 3.1|OpenAPI Initiative / Linux<br>Foundation|Production, industry standard|Synchronous API contracts<br>(Layer 2)|
|AsyncAPI 3.0|AsyncAPI Initiative / Linux<br>Foundation|Production, growing adoption|Event-driven API contracts<br>(Layer 2)|
|CloudEvents|CNCF|Production, industry standard|Audit/event format (Layer 7/9)|
|OIDC / OAuth 2.0|OpenID Foundation / IETF|Production, ubiquitous|Identity (Layer 2/9)|

## Appendix: Infrastructure-as-Code Skeleton

Illustrative module structure organized by architectural layer (per the portability principle in Section 4.4)—each module's interface is defined in standards terms, with AWS resources as the implementation.

```
infrastructure/
```

```
+-- modules/
```

```
|   +-- layer1-client/              # AG-UI adapter
```

```
|   |   +-- main.tf                 # API Gateway WS + Lambda adapter
```

```
|   |   +-- variables.tf            # inputs: agentcore_runtime_endpoint
```

```
|   |   +-- outputs.tf              # outputs: ag_ui_websocket_url
|   |
```

```
|   +-- layer2-api-gateway/         # OpenAPI/AsyncAPI contracts
```

```
|   |   +-- main.tf                 # API Gateway from openapi.yaml
```

```
|   |   +-- openapi.yaml             # <- source of truth
```

```
|   |   +-- asyncapi.yaml            # <- source of truth
```

```
|   |   +-- cognito.tf
|   |
```

```
|   +-- layer3-agent-runtime/        # AgentCore + Strands
```

```
|   |   +-- main.tf                  # AgentCore Runtime resources
```

```
|   |   +-- agents/
```

```
|   |   |   +-- orchestrator/        # Strands agent container build
```

```
|   |   |   +-- planner/
```

```
|   |   |   +-- research/
```

```
|   |   |   +-- coding/
```

```
|   |   |   +-- reviewer/
```

```
|   |   +-- variables.tf             # inputs: mcp_gateway_endpoint,
```

```
|   |                                 #         memory_provider_config,
```

```
|   |                                 #         a2a_registry_endpoint
|   |
```

```
|   +-- layer4-tools-mcp/            # AgentCore Gateway (MCP)
```

```
|   |   +-- main.tf
```

```
|   |   +-- tool-manifests/           # <- portable MCP tool definitions
```

```
|   |   |   +-- create_support_ticket.json
```

```
|   |   |   +-- ...
```

```
|   |   +-- lambda-implementations/
|   |
```

```
|   +-- layer5-multiagent-a2a/        # A2A registry
```

```
|   |   +-- main.tf                   # DynamoDB-backed agent registry
|   |   +-- agent-cards/              # <- portable A2A agent cards
|   |
```

```
|   +-- layer6-memory/                # Memory abstraction
```

```
|   |   +-- main.tf                   # AgentCore Memory resources
```

```
|   |   +-- adapters/
```

```
|   |   |   +-- agentcore_adapter.py  # default
```

```
|   |   |   +-- mem0_adapter.py       # swap-out, tested in CI
```

- `|   |   |   +-- postgres_adapter.py   # swap-out, used in local dev |   |   +-- schema/`

```
|   |       +-- memory_record.json    # <- portable schema (Section 3.2)
|   |
```

```
|   +-- layer7-data/                  # Aurora, S3, OpenSearch, Neptune
|   |   +-- aurora.tf
```

```
|   |   +-- s3.tf
```

```
|   |   +-- opensearch.tf
```

```
|   |   +-- neptune.tf                # optional
|   |
|   +-- layer8-observability/         # ADOT Collector config
|   |   +-- main.tf
|   |   +-- adot-collector-config.yaml  # <- exporter swap point
|   |
```

```
|   +-- layer9-security/              # IAM, KMS, Step Functions, audit
```

```
|       +-- iam.tf
```

```
|       +-- kms.tf
```

```
|       +-- deletion-cascade.tf       # Step Functions workflow
```

```
|       +-- audit-pipeline.tf
|
+-- environments/
```

```
|   +-- dev/
```

```
|   +-- staging/
|   +-- prod/
|
+-- ci/
    +-- memory-adapter-portability-test.yml  # exercises 2+ adapters
```

**PRINCIPLE:** This module layout is the operational expression of Principle P1 (protocols at the boundary). Each module's variables.tf/outputs.tf define inputs and outputs in terms of standard interfaces (endpoints, manifests, schemas)—the .tf resource blocks inside are the only AWS-specific content, and they are the only thing that changes if a layer's implementation is later replaced.

### Closing Statement

This architecture deliberately chooses AWS AgentCore and Strands as the path of least resistance for an AWS-native deployment—both are well-supported, actively developed (Strands 1.0 shipped May 2026 with multi-agent and A2A support), and genuinely reduce operational burden. The standards-first framing is not a rejection of that choice; it is the discipline that ensures the choice remains a choice. Every interface that matters—what a client sees, what a tool looks like, how agents talk to each other, how telemetry is structured, how memory is accessed—is defined by an open standard first, with AWS providing one (very good) implementation of each. Twelve months from now, if a component needs to change—for cost, capability, regulatory, or strategic reasons—the change should be localized to one layer, validated against an interface that was true from day one.
