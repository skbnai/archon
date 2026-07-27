---
title: "AWS Strands & Bedrock AgentCore Production Builder Journey Kit"
doc_type: guide
domain: platforms
status: draft
topic_id: aws-strands-agentcore-builder-journey-kit
last_reviewed: 2026-07-27
maturity: practitioner
supersedes: [docs/cloud-platforms/aws/AWS_Strands_AgentCore_Builder_Journey_Kit.md]
tags: [aws, agentcore, strands, mcp, observability, compliance, production]
covers_version: "N/A"
---

> **Known issue:** some fenced code examples on this page were flattened during the original PDF-to-markdown conversion (lost line breaks/indentation, stray artifact characters) and need reformatting. Tracked in migration/WAVE6_BATCH1_STATUS.md (repo root).

# AWS STRANDS & BEDROCK AGENTCORE PRODUCTION BUILDER JOURNEY KIT
From Zero to Production · Multi-Agent · MCP · A2A · Auth · RAI · Observability · Compliance

|**12 Chapters**|**100+ Patterns**<br/>**50+ Snippets**<br/>**Enterprise Grade**|
|---|---|
|**Version**|1.0 — March 2026|
|**Scope**|AWS Strands SDK · AgentCore Runtime · Gateway · Identity · Memory · Observability · Policy|
|**Audience**|AI Architects · Platform Engineers · ML Engineers · Security Architects|
|**Status**|GA — Validated against AgentCore GA (Oct 2025) and Strands 0.1.x+|

Builder Journey Kit

### **TABLE OF CONTENTS**

### **CHAPTER 1 — Foundation & Architecture**

1.1 What is AWS Strands Agents SDK

1.2 What is Amazon Bedrock AgentCore

- 1.3 AgentCore Service Taxonomy

- 1.4 Strands Architecture Deep-Dive

1.5 Key Concepts: Sessions, MicroVM Isolation, Versioning

### **CHAPTER 2 — Your First Agent**

2.1 Installing the SDK & Toolkit

2.2 Hello-World Agent with Strands

2.3 Custom Tools & Decorators

2.4 Deploying with Starter Toolkit

2.5 Invoking via AWS SDK

### **CHAPTER 3 — AgentCore Runtime In Depth**

3.1 Runtime Architecture & MicroVM Isolation

3.2 Deployment Modes: direct_code_deploy vs Container

3.3 Custom FastAPI Agent Pattern

3.4 AG-UI & A2A Protocol Support

3.5 Session Management & Long-Running Tasks

### **CHAPTER 4 — AgentCore Memory**

4.1 Short-Term (In-Session) Memory

4.2 Long-Term Memory: Extraction & Retrieval

4.3 Memory Namespacing & Tenant Isolation

### **CHAPTER 5 — AgentCore Gateway & MCP**

5.1 Gateway Core Concepts

5.2 Target Types: OpenAPI, Lambda, Smithy, Remote MCP

5.3 Inbound & Outbound Authorization

5.4 Semantic Tool Discovery

5.5 API Gateway MCP Proxy Integration

5.6 Deploying Gateway on Fargate & OpenShift

### **CHAPTER 6 — Identity, Auth & Trust Layers**

6.1 AgentCore Identity Overview

6.2 Inbound: IAM SigV4, OAuth 2.1, Cognito

6.3 Outbound: M2M, API Key, OAuth Credential Providers

- 6.4 MCP Proxy for AWS (SigV4 Bridge)

- 6.5 Cross-Tenant A2A Trust (JWT Federation)

- 6.6 Policy Engine: Action-Level Authorization

### **CHAPTER 7 — Multi-Agent Patterns**

7.1 Supervisor / Sub-Agent Pattern

7.2 Agent-as-Tool Pattern

7.3 A2A Protocol: Cross-Runtime Communication

7.4 A2A Cross-Tenant (Inter-Organization)

- 7.5 Agent Swarm & Mesh Topologies

### **CHAPTER 8 — Observability, Tracing & Evaluation**

8.1 AgentCore Native Observability (CloudWatch + OTEL)

8.2 Arize Phoenix: Self-Hosted LLM Observability

8.3 Instrumenting Strands with OpenInference

8.4 AgentCore Evaluations (Preview)

- 8.5 Strands Eval Framework

- 8.6 LLM-as-Judge & Prompt Playground

### **CHAPTER 9 — RAI, PII & Compliance**

9.1 Responsible AI (RAI) Framework on AWS

9.2 Bedrock Guardrails: Content, PII, Grounding

9.3 AgentCore Policy: Action-Level Enforcement

9.4 Data Residency, Encryption & VPC Controls

9.5 Regulatory Compliance (SOC 2, HIPAA, GDPR)

### **CHAPTER 10 — LaaS Integration (URL-Based)**

10.1 What is LaaS and Why It Matters

10.2 Exposing Agents as REST Endpoints

10.3 Integrating External LLMs via URL

10.4 End-to-End LaaS Architecture

### **CHAPTER 11 — Best Practices & Anti-Patterns**

11.1 Architecture Best Practices

11.2 Security Anti-Patterns to Avoid

11.3 Operational Anti-Patterns

### **CHAPTER 12 — End-to-End Production Blueprint**

12.1 Reference Architecture Diagram

12.2 IaC Terraform Skeleton

12.3 CI/CD Pipeline Design

###### 12.4 Production Checklist

##### **CHAPTER 1**

## **Foundation & Architecture**

Core Concepts · Service Taxonomy · Design Philosophy

### **1.1 What is AWS Strands Agents SDK**

**Strands Agents** is AWS's open-source, model-first Python SDK for building production-grade AI agents. It abstracts away orchestration complexity by letting the foundation model plan, select tools, and iterate — the developer simply declares *what* tools are available, not *how* to orchestrate them. Strands was open-sourced in May 2025 and is the recommended native framework for AgentCore.

###### **Key design pillars:**

###### I **BEST PRACTICE**

Strands is **model-agnostic** — it works with Claude, Nova, GPT-4, Gemini, Llama, and any Bedrock or LiteLLM-compatible endpoint, not just Bedrock models.

- **Model-first reasoning** : the LLM drives planning; tools are just functions.

- **Minimal boilerplate** : @tool decorator turns any Python function into an agent capability.

- **Multi-agent native** : agents-as-tools, A2A executor, swarm primitives built-in.

- **AgentCore first-class** : BedrockAgentCoreApp wraps any agent in 3 lines.

- **OpenTelemetry natively** : OTEL hooks for trace_attributes, session IDs, user IDs.

### **1.2 What is Amazon Bedrock AgentCore**

Amazon Bedrock AgentCore (GA October 2025) is a fully managed, enterprise-grade platform for deploying and operating AI agents at scale. It provides the infrastructure layer that developers would otherwise spend months building: session isolation, memory, identity controls, tool integration, observability, evaluations, and policy enforcement — all as composable services.

|**Service**|**Description**|
|---|---|
|Runtime|Serverless, MicroVM-isolated compute for agents. Supports MCP & A2A. Up to 8h tasks.|
|Memory|Short-term (per session) + Long-term (cross-session) memory primitives.|
|Gateway|Fully managed MCP server. Converts APIs, Lambda, OpenAPI->MCP tools. OAuth/IAM auth.|
|Identity|Inbound & outbound credential management. OAuth 2.1, Cognito, IAM SigV4, API Keys.|
|Policy|Real-time action-level authorization. Intercepts every tool call before execution.|
|Observability|OTEL-based tracing, CloudWatch dashboards, audit logs. Framework-agnostic.|
|Evaluations|Continuous quality scoring, LLM-as-judge, production monitoring. (Preview)|

Browser Managed headless browser tool for web-based tasks. Code Interp. Secure sandboxed code execution environment for agents.

### **1.3 Strands Architecture Deep-Dive**

###### **The Strands agentic loop follows the ReAct (Reason + Act) pattern enhanced with native retry, reflection, and tool-composition primitives:**

1. **User message** -> Agent receives input with system prompt + tool registry

2. **LLM planning** -> Model selects tool(s), generates tool_use blocks

3. **Tool execution** -> Strands dispatches to @tool functions (sync or async)

4. **Reflection** -> Results fed back; model decides: done or continue loop

5. **Guardrail check** -> Bedrock Guardrails filters input/output if configured

6. **Response** -> Final message + OTEL spans emitted

###### II **NOTE**

Strands agents can also be **composed** : an agent can be registered as a tool of another agent (supervisor pattern), or exposed as an A2A executor that another runtime can call via the A2A protocol.

### **1.4 Key Concepts: Sessions, MicroVM Isolation, Versioning**

###### **AgentCore Runtime provisions a dedicated MicroVM per user session. Each MicroVM has isolated CPU, memory, and filesystem — preventing cross-session data contamination. This is the fundamental security primitive underpinning multi-tenant agent deployments.**

- **Session ID** : unique identifier (UUID) per conversation. Passed in invocation payload.

- **Runtime Endpoint** : ARN-addressed. The DEFAULT endpoint always points to latest version.

- **Versioning** : immutable versions created on each deploy. Endpoints reference specific versions.

- **Session timeout** : configurable idle and max-duration timeouts per runtime.

##### **CHAPTER 2**

## **Your First Agent**

Installation · Hello World · Tools · Deploy · Invoke

### **2.1 Installing the SDK & Toolkit**

Install all required packages into a Python 3.11+ virtual environment:

###### **requirements.txt / setup**

```
# Create and activate virtual environment
python3 -m venv .venv && source .venv/bin/activate
# Core SDK packages
pip install strands-agents          # Strands core
pip install strands-agents-tools    # Built-in tools (file, browser, etc.)
pip install bedrock-agentcore       # AgentCore Runtime SDK
pip install bedrock-agentcore-starter-toolkit  # CLI deploy tool
# Observability (Phoenix)
pip install arize-phoenix-otel openinference-instrumentation-strands
```

- `# Optional: evaluation pip install strands-agents[evaluation]`

### **2.2 Hello-World Agent with Strands**

###### **my_agent.py**

```
# my_agent.py
from strands import Agent, tool
from bedrock_agentcore import BedrockAgentCoreApp
```

`#` II `AgentCore app wrapper` IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII `app = BedrockAgentCoreApp()`

`#` II `Custom tool (any Python function decorated with @tool)` IIIIIIIIIIIII `@tool def get_weather(city: str) -> str: """Returns current weather for a given city.""" # In production: call a real weather API return f"Weather in {city}: 28°C, sunny" #` II `Agent with system prompt, model, and tools` IIIIIIIIIIIIIIIIIIIIIIII `agent = Agent( model="us.anthropic.claude-sonnet-4-20250514",  # or any Bedrock model system_prompt="You are a helpful travel assistant.", tools=[get_weather], # Optional: Bedrock Guardrails # guardrail_id="abc123", guardrail_version="1", ) #` II `AgentCore entrypoint (called per invocation)` IIIIIIIIIIIIIIIIIIIIII `@app.entrypoint`

```
def invoke(payload, context):
```

```
    user_message = payload.get("prompt", "Hello!")
    result = agent(user_message)
    return {"result": result.message}
if __name__ == "__main__":
    app.run()  # Local dev server on :8080
```

###### I **BEST PRACTICE**

The **context** object injected by AgentCore contains: context.session_id, context.agent_runtime_id, context.user_id (from inbound auth token). Always log these for full trace correlation.

### **2.3 Custom Tools & Decorators**

###### **tools.py**

```
from strands import tool
from pydantic import BaseModel
```

`#` II `Simple string input` IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII `@tool def lookup_order(order_id: str) -> dict: """Retrieves order details by order ID.""" return {"id": order_id, "status": "SHIPPED", "eta": "2026-04-01"} #` II `Structured Pydantic input` IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII `class BookingRequest(BaseModel): hotel: str check_in: str guests: int @tool def book_hotel(request: BookingRequest) -> str: """Books a hotel room for specified dates.""" return f"Booked {request.hotel} for {request.guests} guests from {request.check_in}" #` II `Async tool` IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII `@tool async def fetch_live_rate(currency_pair: str) -> float: """Fetches live FX rate for a currency pair.""" import asyncio await asyncio.sleep(0)  # Non-blocking I/O call return 1.0823`

### **2.4 Deploying with Starter Toolkit**

###### **CLI**

```
# Step 1: Configure (one-time setup)
```

```
agentcore configure --entrypoint my_agent.py
```

- `# Prompts: IAM role auto-create, ECR repo, deployment mode (default: direct_code_deploy)`

- `# Step 2: Deploy (direct_code_deploy — no Docker needed)`

```
agentcore deploy --mode direct_code_deploy
```

- `# Output: AgentCore Runtime ARN + DEFAULT endpoint ARN`

- `# Step 3: Check status`

```
agentcore status
```

```
# Step 4: Tail logs
```

```
aws logs tail /aws/bedrock-agentcore/runtimes/<RUNTIME_ID>-DEFAULT --follow
# Container deploy (when you need custom OS dependencies)
agentcore deploy --mode container_deploy  # Uses CodeBuild, no local Docker
```

### **2.5 Invoking via AWS SDK**

###### **invoke.py**

```
import boto3, json
client = boto3.client("bedrock-agentcore", region_name="us-east-1")
# Synchronous invoke
response = client.invoke_agent_runtime(
    agentRuntimeEndpointArn="arn:aws:bedrock-agentcore:...:agent-runtime/ID/DEFAULT",
    sessionId="user-session-abc123",
    qualifier="DEFAULT",
    payload=json.dumps({"prompt": "What is the weather in Mumbai?"})
)
result = json.loads(response["output"].read())
print(result["result"])
```

##### **CHAPTER 3**

## **AgentCore Runtime In Depth**

MicroVM · Deployment Modes · Custom Agents · Protocols

### **3.1 Runtime Architecture & MicroVM Isolation**

Each AgentCore Runtime is a named, versioned compute entity. When invoked, Runtime provisions a **MicroVM** (Firecracker-based) per session. The MicroVM lifecycle is tied to the session: created on first invocation, destroyed on session end. Key properties:

- Isolated CPU, memory, and filesystem per session — no shared state between users.

- Network egress can be scoped via VPC configuration and security groups.

- Supports long-running tasks up to 8 hours with async checkpointing.

- Bi-directional streaming via SSE or WebSocket for voice/real-time agents.

### **3.2 Deployment Modes**

|**Mode**|**Description**|**Use Case**|
|---|---|---|
|direct_code_deploy|Python source + requirements.txt uploaded to S3. No Docker.<br/>Fastest iteration.|Dev, simple agents|
|container_deploy|Docker image built by CodeBuild, pushed to ECR. Full OS<br/>control.|Prod, custom deps, GPU|
|custom|Bring your own container registry / image URI.|Enterprise / air-gap|

### **3.3 Custom FastAPI Agent (Full HTTP Control)**

When you need full control over the HTTP interface (custom routes, streaming endpoints, middleware), deploy a **FastAPI** agent that satisfies AgentCore's contract:

###### **custom_agent/main.py**

```
# custom_agent/main.py  — FastAPI + Strands + AgentCore contract
from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
import uvicorn, json
app = FastAPI()
agent = Agent(model="us.anthropic.claude-sonnet-4-20250514",
               system_prompt="You are a financial analysis assistant.")
# AgentCore Runtime requires POST /invocations
@app.post("/invocations")
async def invoke(request: Request):
```

```
    body = await request.json()
```

```
    session_id = request.headers.get("X-Amzn-Bedrock-AgentCore-Session-Id", "default")
    result = agent(body.get("prompt", ""))
```

```
    return {"result": result.message, "session_id": session_id}
```

```
# Health check required by Runtime
@app.get("/ping")
def ping(): return {"status": "ok"}
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
```

### **3.4 AG-UI Protocol Support**

###### **agui_agent.py**

```
# AG-UI: Zero-boilerplate agent UI protocol (SSE + WebSocket)
from bedrock_agentcore.runtime import serve_ag_ui, AGUIApp
```

```
from ag_ui.core import RunAgentInput, RunStartedEvent, TextMessageStartEvent,
  TextMessageContentEvent, TextMessageEndEvent, RunFinishedEvent
```

- `# Option A: One-liner for framework agents with .run() serve_ag_ui(my_strands_agent)`

- `# Option B: Full control agui_app = AGUIApp() @agui_app.entrypoint async def my_agent(input_data: RunAgentInput):`

```
    yield RunStartedEvent(thread_id=input_data.thread_id, run_id=input_data.run_id)
    msg_id = "msg-001"
```

```
    yield TextMessageStartEvent(message_id=msg_id, role="assistant")
```

```
    async for chunk in agent.stream_async(input_data.messages[-1].content):
        yield TextMessageContentEvent(message_id=msg_id, delta=chunk)
    yield TextMessageEndEvent(message_id=msg_id)
    yield RunFinishedEvent(thread_id=input_data.thread_id, run_id=input_data.run_id)
```

##### **CHAPTER 4**

## **AgentCore Memory**

Short-Term · Long-Term · Tenant Isolation

### **4.1 Short-Term (In-Session) Memory**

Short-term memory scopes context to a single session ID. The AgentCore SDK automatically manages the conversation buffer — no manual context stitching needed:

###### **short_term_memory.py**

```
from bedrock_agentcore import BedrockAgentCoreApp
from bedrock_agentcore.memory import MemoryClient
app = BedrockAgentCoreApp(
    memory_id="mem-abc123",          # AgentCore Memory resource ID
    memory_strategy="SESSION"        # Scoped to session_id
)
```

```
@app.entrypoint
def invoke(payload, context):
```

```
    # context.session_id is automatically used as the memory namespace
    agent = Agent(model="...", system_prompt="...")
    return {"result": agent(payload["prompt"]).message}
```

### **4.2 Long-Term Memory**

Long-term memory persists *extracted insights* — preferences, facts, summaries — across sessions. AgentCore Memory uses semantic search to inject relevant context:

###### **long_term_memory.py**

```
from bedrock_agentcore.memory import MemoryClient, ExtractionConfig
memory = MemoryClient(memory_id="mem-abc123")
```

```
# Store extracted facts after agent interaction
memory.put_memory(
    namespace=f"user/{user_id}/preferences",
    content="User prefers vegetarian restaurants with outdoor seating.",
    memory_strategy="SEMANTIC"
)
# Retrieve relevant memories at agent startup
relevant = memory.get_relevant_memories(
    namespace=f"user/{user_id}/preferences",
    query=payload["prompt"],
    top_k=5
)
# Inject into system prompt
system_prompt = f"""You are a helpful concierge.
User preferences:\n{chr(10).join(m['content'] for m in relevant)}"""
agent = Agent(model="...", system_prompt=system_prompt)
```

###### II **WARNING**

Always namespace memories by user_id or tenant_id to prevent cross-user memory leakage. Never store raw PII in memory — apply redaction before calling put_memory().

##### **CHAPTER 5**

*Part 1 of 3. Continued in [Part 2](parts/13-aws-strands-agentcore-builder-journey-kit-part2.md).*
