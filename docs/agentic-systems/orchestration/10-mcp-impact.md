---
title: "MCP (Model Context Protocol) Impact on Orchestration"
date_created: 2026-07-24
last_reviewed: 2026-07-24
status: current
domain: agentic-systems
topic_id: mcp-impact
supersedes: ["../knowledge-docs/docs/workflow-orchestration/10-mcp-impact.md"]
doc_type: guide
tags: ["workflow-orchestration", "mcp", "tool-discovery", "agents", "protocol"]
---

# MCP (Model Context Protocol) Impact on Orchestration

> **As of July 2026.** MCP 1.0 is stable. Python SDK 1.8; TypeScript SDK 1.10.

This guide analyzes how the Model Context Protocol (MCP) changes orchestration fundamentals — shifting tool capability from statically wired code to dynamically discovered, negotiated services. MCP is rapidly becoming the standard interface between LLM agents and the tools they use.

---

## What is MCP?

MCP is a client-server protocol for connecting LLM applications to external data sources and tools. It standardizes:

- **Tool discovery**: Agents ask an MCP server "what can you do?" at runtime
- **Capability negotiation**: Servers declare capabilities; clients choose what to use
- **Stateful tool sessions**: A session persists across multiple tool calls
- **Cancellation**: Agents can interrupt long-running tool operations

```
Without MCP (static, hardcoded):
  Agent code → hardcoded function calls → specific APIs
  Adding a tool = code change + redeploy

With MCP (dynamic, discoverable):
  Agent ←→ MCP Client ←→ MCP Server ←→ APIs
  Adding a tool = update MCP server, agent discovers it on next run
```

This is the architectural shift: tool coupling moves from **compile-time** to **runtime**.

---

## MCP Architecture

```mermaid
graph TD
    A["LLM Agent<br/>(MCP Client side)<br/><br/>1. Connect to MCP server(s)<br/>2. Call list_tools() → discover available tools<br/>3. Include discovered tools in LLM context<br/>4. When LLM requests a tool → call_tool() via MCP<br/>5. Return result to LLM"]
    
    B["MCP Protocol<br/>(JSON-RPC over stdio/HTTP/SSE)"]
    
    C["MCP Server<br/>(tool provider side)<br/><br/>Exposes: tools, resources, prompts<br/>Examples: filesystem, database, CRM, billing system<br/>Auth: OAuth 2.1, API keys, mTLS"]
    
    A -->|MCP Protocol| B
    B --> C
```

---

## Building an MCP Server

MCP servers expose tools to any compatible client. Here is a complete server for a loan management system:

```python
# pip install mcp==1.8.0
from mcp.server import FastMCP
from pydantic import BaseModel
from typing import Optional
import json

mcp = FastMCP("loan-management-server")

@mcp.tool()
async def get_loan_application(application_id: str) -> dict:
    """
    Retrieves a loan application by ID.
    Returns status, applicant info, requested amount, and current step.
    """
    application = await loan_db.get(application_id)
    if not application:
        return {"error": f"Application {application_id} not found"}
    return {
        "id": application.id,
        "status": application.status,
        "applicant_name": application.applicant_name,
        "requested_amount": application.requested_amount,
        "current_step": application.current_step,
        "created_at": application.created_at.isoformat(),
    }

@mcp.tool()
async def update_application_status(
    application_id: str,
    new_status: str,
    reason: str,
    updated_by: str,
) -> dict:
    """
    Updates a loan application status.
    Valid statuses: pending, under_review, approved, rejected, cancelled.
    Requires updated_by to be set for audit trail.
    """
    valid_statuses = {"pending", "under_review", "approved", "rejected", "cancelled"}
    if new_status not in valid_statuses:
        return {"error": f"Invalid status. Must be one of: {valid_statuses}"}

    result = await loan_db.update_status(
        application_id=application_id,
        status=new_status,
        reason=reason,
        updated_by=updated_by,
    )
    return {"success": True, "application_id": application_id, "new_status": new_status}

@mcp.resource("loan://applications/{application_id}/documents")
async def get_loan_documents(application_id: str) -> str:
    """Returns all documents attached to a loan application."""
    docs = await document_store.list(application_id)
    return json.dumps([{"name": d.name, "type": d.type, "url": d.url} for d in docs])

if __name__ == "__main__":
    mcp.run()
```

---

## Connecting an Agent to MCP

The agent discovers tools dynamically and includes them in the LLM context:

```python
# pip install mcp==1.8.0 anthropic==0.40.0
import asyncio
import anthropic
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def run_agent_with_mcp(goal: str) -> str:
    server_params = StdioServerParameters(
        command="python",
        args=["loan_mcp_server.py"],
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            # Discover tools at runtime — no hardcoding needed
            tools_response = await session.list_tools()

            # Convert MCP tool format to Anthropic tool format
            anthropic_tools = [
                {
                    "name": tool.name,
                    "description": tool.description,
                    "input_schema": tool.inputSchema,
                }
                for tool in tools_response.tools
            ]

            client = anthropic.Anthropic()
            messages = [{"role": "user", "content": goal}]

            while True:
                response = client.messages.create(
                    model="claude-sonnet-4-6",
                    max_tokens=4096,
                    tools=anthropic_tools,  # dynamically discovered
                    messages=messages,
                )

                messages.append({"role": "assistant", "content": response.content})

                if response.stop_reason == "end_turn":
                    return next(b.text for b in response.content if hasattr(b, "text"))

                if response.stop_reason == "tool_use":
                    tool_results = []
                    for block in response.content:
                        if block.type == "tool_use":
                            # Call through MCP session — not a direct function call
                            result = await session.call_tool(block.name, block.input)
                            tool_results.append({
                                "type": "tool_result",
                                "tool_use_id": block.id,
                                "content": result.content[0].text if result.content else "No output",
                            })
                    messages.append({"role": "user", "content": tool_results})

result = asyncio.run(run_agent_with_mcp("Review application APP-123 and flag it for underwriting"))
```

---

## Capability Negotiation

MCP servers advertise capabilities during initialization. Clients choose which to use:

```python
async with ClientSession(read, write) as session:
    init_result = await session.initialize()

    # Server tells client what it supports
    server_capabilities = init_result.capabilities

    supports_resources = server_capabilities.resources is not None
    supports_prompts = server_capabilities.prompts is not None
    supports_tools = server_capabilities.tools is not None
    supports_logging = server_capabilities.logging is not None

    print(f"Server capabilities: resources={supports_resources}, tools={supports_tools}")

    # Only call list_resources() if server supports it
    if supports_resources:
        resources = await session.list_resources()

    if supports_tools:
        tools = await session.list_tools()
```

This means agents can safely connect to any MCP server without knowing its capabilities in advance — true plug-and-play tool extensibility.

---

## MCP Security Architecture

MCP opens tool access to any connected client. Security requires defense at multiple layers:

### Authentication

```python
# MCP server with OAuth 2.1 token validation
from mcp.server import FastMCP
from mcp.server.auth import BearerAuthProvider
import jwt

def validate_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=["RS256"])
        if payload.get("scope") not in ["loan:read", "loan:write", "loan:admin"]:
            raise ValueError("Insufficient scope")
        return payload
    except jwt.ExpiredSignatureError:
        raise ValueError("Token expired")

auth = BearerAuthProvider(validate_token=validate_token)
mcp = FastMCP("loan-management-server", auth=auth)
```

### Tool-Level Authorization

```python
from mcp.server import Context

@mcp.tool()
async def update_application_status(
    application_id: str,
    new_status: str,
    reason: str,
    ctx: Context,  # MCP injects request context
) -> dict:
    # Check that caller has write scope
    caller_scope = ctx.client_info.get("scope", "")
    if "loan:write" not in caller_scope:
        return {"error": "Insufficient permissions — loan:write scope required"}

    # Log every write for audit
    await audit_log.record(
        action="update_application_status",
        actor=ctx.client_info.get("sub"),
        resource=application_id,
        change={"new_status": new_status, "reason": reason},
    )

    return await loan_db.update_status(application_id, new_status, reason)
```

### Preventing Prompt Injection via Tool Responses

Tool responses flow back into the LLM context. A malicious data source could inject instructions:

```python
import re

INJECTION_PATTERNS = [
    r"ignore (?:all )?(?:previous|prior) instructions",
    r"you are now",
    r"new (?:system )?prompt",
    r"forget (?:everything|all)",
]

def sanitize_mcp_response(content: str) -> str:
    for pattern in INJECTION_PATTERNS:
        if re.search(pattern, content, re.IGNORECASE):
            return "[Response blocked: potential injection attempt detected]"
    return content[:8000] if len(content) > 8000 else content
```

---

## MCP in Temporal Workflows

MCP servers are long-lived processes. Temporal activities can connect to them per-invocation:

```python
from temporalio import activity
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

@activity.defn
async def run_mcp_agent_activity(goal: str, mcp_server_url: str) -> str:
    server_params = StdioServerParameters(command="python", args=[mcp_server_url])

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools = await session.list_tools()

            # Run the full agent loop within this activity
            return await execute_agent_loop(goal, tools, session)
```

**Pattern**: MCP session lifetime = Temporal activity lifetime. The session opens when the activity starts and closes when it ends. This keeps connections short-lived and avoids resource leaks.

---

## Impact on Orchestration Patterns

| Before MCP | With MCP |
| --- | --- |
| Tools hardcoded in agent code | Tools discovered at runtime from servers |
| Adding tools requires redeploy | Adding tools requires updating MCP server only |
| Tool auth per-function | Tool auth centralized in MCP server |
| Observability per-tool | Observability at MCP protocol layer |
| Single-provider tools | Any client can use any compliant server |

MCP does not replace Temporal or LangGraph — it standardizes the tool interface layer below them. A LangGraph agent still owns the reasoning loop; MCP standardizes how it invokes capabilities.

---

## MCP Server Registry Pattern

At scale, an enterprise runs many MCP servers — one per domain or capability. A **server registry** helps agents discover the right server for a given task.

```python
# Central registry: maps capability categories to MCP server endpoints
MCP_SERVER_REGISTRY = {
    "loan_management": {
        "command": "python",
        "args": ["servers/loan_mcp_server.py"],
        "capabilities": ["get_loan_application", "update_application_status", "list_documents"],
        "auth_scope": "loan:read loan:write",
    },
    "compliance": {
        "command": "python",
        "args": ["servers/compliance_mcp_server.py"],
        "capabilities": ["run_aml_check", "verify_sanctions", "check_pep_list"],
        "auth_scope": "compliance:read",
    },
    "communications": {
        "command": "python",
        "args": ["servers/comms_mcp_server.py"],
        "capabilities": ["send_email", "send_sms", "log_interaction"],
        "auth_scope": "comms:write",
    },
}

async def get_tools_for_agent_role(role: str) -> list:
    """Aggregate tools from all MCP servers the agent role is authorized to use."""
    authorized_servers = ROLE_SERVER_MAP.get(role, [])
    all_tools = []

    for server_name in authorized_servers:
        server_config = MCP_SERVER_REGISTRY[server_name]
        server_params = StdioServerParameters(
            command=server_config["command"],
            args=server_config["args"],
        )
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                tools = await session.list_tools()
                all_tools.extend(tools.tools)

    return all_tools
```

---

## Performance Considerations

MCP adds latency at tool discovery time. Profile before and after introducing MCP:

| Operation | Without MCP | With MCP (stdio) | With MCP (HTTP) |
| --- | --- | --- | --- |
| Tool discovery | 0ms (hardcoded) | 50–100ms (startup) | 20–50ms (cached) |
| Tool invocation | Direct function call | +5–15ms IPC overhead | +10–30ms HTTP overhead |
| Session initialization | N/A | 100–300ms (once per session) | 50–150ms |

**Optimization**: Cache tool lists per server. Re-initialize sessions only when servers restart. Use stdio for local servers, HTTP/SSE only for remote or cloud-hosted servers.

---

## Related

[Tool Calling Orchestration](./09-tool-calling-orchestration.md) · [Agent Frameworks Comparison](./08-agent-frameworks-comparison.md) · [Security Architecture](./17-workflow-orchestration-security-architecture.md) · [A2A Orchestration Patterns](./11-a2a-orchestration-patterns.md)
