---
title: "Tool Calling Orchestration"
date_created: 2026-07-24
last_reviewed: 2026-07-24
status: current
domain: agentic-systems
topic_id: tool-calling-orchestration
supersedes: ["../knowledge-docs/docs/workflow-orchestration/09-tool-calling-orchestration.md"]
doc_type: guide
tags: ["workflow-orchestration", "tool-calling", "agents", "mcp"]
---

# Tool Calling Orchestration

> **As of July 2026.** Claude claude-sonnet-4-6 tool use spec; LangGraph 1.2.8 ToolNode; MCP 1.0.

This guide explains how LLM tool calling changes orchestration fundamentals. Tool calling is a new primitive that changes what "orchestration" means — shifting from human-defined activity sequences to agent-directed capability invocation at runtime.

---

## Tool Calling as a New Primitive

In traditional workflow orchestration (Temporal, Camunda), the developer defines which activities run and in what order. The workflow engine executes that plan.

In LLM tool calling, the **LLM decides** which tools to call, in what order, with what arguments — based on its reasoning about the current context.

```
Traditional orchestration (developer-defined):
  developer: "Step 1: validate, Step 2: charge, Step 3: notify"
  engine: executes exactly those steps in order

Tool calling (LLM-directed):
  developer: "Here are 10 tools. Here is the goal."
  LLM: reasons → decides which tool → calls it → observes → reasons again
```

This is a fundamental shift. The orchestration logic moves from your code into the LLM's context window.

---

## The Agent Loop

Every tool-calling agent runs the same core loop:

```mermaid
graph TD
    A["1. REASON<br/>LLM reads context + available tools<br/>Decides: 'I need to call tool X'"]
    B["2. CALL<br/>LLM emits a tool_call with args<br/>Framework executes the real function"]
    C["3. OBSERVE<br/>Tool result added to context<br/>LLM now knows what happened"]
    D["4. DECIDE<br/>Is the goal achieved?"]
    E["Emit final answer"]
    
    A --> B
    B --> C
    C --> D
    D -->|YES| E
    D -->|NO| A
```

### Implementation with Claude

```python
import anthropic
import json

client = anthropic.Anthropic()

tools = [
    {
        "name": "get_account_balance",
        "description": "Returns the current account balance for a customer",
        "input_schema": {
            "type": "object",
            "properties": {
                "account_id": {"type": "string", "description": "The account identifier"},
            },
            "required": ["account_id"],
        },
    },
    {
        "name": "issue_refund",
        "description": "Issues a refund to a customer account",
        "input_schema": {
            "type": "object",
            "properties": {
                "account_id": {"type": "string"},
                "amount": {"type": "number", "description": "Amount to refund in USD"},
                "reason": {"type": "string"},
            },
            "required": ["account_id", "amount", "reason"],
        },
    },
]

def execute_tool(tool_name: str, tool_input: dict) -> str:
    if tool_name == "get_account_balance":
        balance = database.get_balance(tool_input["account_id"])
        return json.dumps({"balance": balance, "currency": "USD"})
    elif tool_name == "issue_refund":
        refund_id = payments.issue_refund(**tool_input)
        return json.dumps({"refund_id": refund_id, "status": "processed"})
    raise ValueError(f"Unknown tool: {tool_name}")

def run_agent(goal: str, max_iterations: int = 10) -> str:
    messages = [{"role": "user", "content": goal}]

    for iteration in range(max_iterations):
        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=4096,
            tools=tools,
            messages=messages,
        )

        # Add assistant's response to history
        messages.append({"role": "assistant", "content": response.content})

        if response.stop_reason == "end_turn":
            # Agent decided it's done
            return next(b.text for b in response.content if hasattr(b, "text"))

        if response.stop_reason == "tool_use":
            # Execute all requested tool calls
            tool_results = []
            for block in response.content:
                if block.type == "tool_use":
                    result = execute_tool(block.name, block.input)
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": result,
                    })

            # Feed results back to the agent
            messages.append({"role": "user", "content": tool_results})

    raise RuntimeError(f"Agent did not complete within {max_iterations} iterations")

result = run_agent("Check account A-123 and issue a $50 refund for the duplicate charge")
```

---

## Tool Design: The Difference That Matters

Well-designed tools are **narrow, composable, and safe to retry**. Poorly designed tools create coupling, side effects, and loops.

### Good Tool Design

```python
# Narrow: does one thing, returns structured data
{
    "name": "get_customer_profile",
    "description": "Returns customer profile data. Does NOT modify any data.",
    "input_schema": {
        "type": "object",
        "properties": {
            "customer_id": {"type": "string"},
            "fields": {
                "type": "array",
                "items": {"type": "string", "enum": ["name", "email", "account_tier", "since"]},
                "description": "Which fields to return. Defaults to all.",
            },
        },
        "required": ["customer_id"],
    },
}

# Idempotent: safe to call multiple times
{
    "name": "send_notification",
    "description": "Sends a notification. Uses idempotency_key to prevent duplicates.",
    "input_schema": {
        "type": "object",
        "properties": {
            "recipient_id": {"type": "string"},
            "message": {"type": "string"},
            "idempotency_key": {"type": "string", "description": "Unique key to prevent duplicate sends"},
        },
        "required": ["recipient_id", "message", "idempotency_key"],
    },
}
```

### Anti-Pattern: God Tool

```python
# BAD: does too much, causes hallucination risk
{
    "name": "handle_customer_issue",
    "description": "Handles any customer issue end-to-end",
    "input_schema": {
        "type": "object",
        "properties": {
            "issue_type": {"type": "string"},
            "action": {"type": "string"},  # anything the LLM imagines
        },
    },
}
```

Wide tools invite the LLM to hallucinate argument values. Narrow tools constrain what the LLM can do — which is a feature, not a limitation.

---

## Tool Discovery: Static vs Dynamic

### Static Tool Registry

All tools defined at startup. Simple, fast, predictable.

```python
TOOL_REGISTRY = {
    "get_balance": get_balance_function,
    "issue_refund": issue_refund_function,
    "lookup_policy": lookup_policy_function,
}

def get_tools_for_agent(agent_role: str) -> list[dict]:
    """Return only the tools this agent is authorized to use."""
    permissions = RBAC.get_tools(agent_role)
    return [tool_schema for name, tool_schema in tool_schemas.items() if name in permissions]
```

### Dynamic Tool Discovery (MCP)

Tools discovered at runtime from MCP servers. The agent queries what's available before deciding what to call. See [MCP Impact](./mcp-impact) for full details.

```python
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def get_available_tools(server_params: StdioServerParameters) -> list:
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools = await session.list_tools()
            return tools.tools  # dynamically available capabilities
```

---

## Preventing Infinite Loops

Without safeguards, agents can enter reasoning loops: the LLM calls a tool, gets a result that doesn't satisfy it, calls another tool, gets another result, and so on indefinitely.

```python
class AgentExecutor:
    def __init__(self, max_iterations: int = 15, max_tokens_total: int = 100_000):
        self.max_iterations = max_iterations
        self.max_tokens_total = max_tokens_total
        self.iteration_count = 0
        self.tokens_used = 0

    def check_limits(self, response_usage) -> None:
        self.iteration_count += 1
        self.tokens_used += response_usage.input_tokens + response_usage.output_tokens

        if self.iteration_count >= self.max_iterations:
            raise RuntimeError(
                f"Agent exceeded {self.max_iterations} iterations — possible reasoning loop"
            )
        if self.tokens_used >= self.max_tokens_total:
            raise RuntimeError(
                f"Agent exceeded {self.max_tokens_total} tokens — likely runaway"
            )

    def detect_tool_repeat(self, tool_calls: list, history: list) -> bool:
        """Detect if agent is calling the same tool with the same args repeatedly."""
        recent_calls = [c for step in history[-3:] for c in step.get("tool_calls", [])]
        for call in tool_calls:
            matching = [c for c in recent_calls if c["name"] == call["name"] and c["args"] == call["args"]]
            if len(matching) >= 2:
                return True  # Same call seen 3+ times in last 3 rounds
        return False
```

---

## Tool Output Validation

Never pass raw tool output directly back to the LLM without validation. Malformed tool responses can confuse the agent or enable prompt injection.

```python
import re
from typing import Any

def sanitize_tool_output(tool_name: str, raw_output: Any) -> str:
    """Validate and sanitize tool output before feeding back to LLM."""

    if raw_output is None:
        return json.dumps({"error": "Tool returned no data"})

    # Convert to JSON string if not already
    if not isinstance(raw_output, str):
        try:
            output = json.dumps(raw_output, default=str)
        except (TypeError, ValueError) as e:
            return json.dumps({"error": f"Tool output not serializable: {e}"})
    else:
        output = raw_output

    # Enforce size limit — large outputs bloat the context window
    if len(output) > 8_000:
        output = output[:8_000] + "... [truncated]"

    # Detect prompt injection patterns in tool responses
    injection_patterns = [
        r"ignore previous instructions",
        r"you are now",
        r"new system prompt",
    ]
    for pattern in injection_patterns:
        if re.search(pattern, output, re.IGNORECASE):
            return json.dumps({"error": "Tool output contained potentially unsafe content and was blocked"})

    return output
```

---

## Tool Authorization

Not every agent should be able to call every tool. Implement least-privilege access.

```python
from enum import Enum
from functools import wraps

class ToolPermission(Enum):
    READ_ONLY = "read_only"
    WRITE = "write"
    FINANCIAL = "financial"
    ADMIN = "admin"

TOOL_PERMISSIONS: dict[str, set[ToolPermission]] = {
    "get_account_balance": {ToolPermission.READ_ONLY},
    "lookup_policy": {ToolPermission.READ_ONLY},
    "send_notification": {ToolPermission.WRITE},
    "issue_refund": {ToolPermission.FINANCIAL},
    "delete_account": {ToolPermission.ADMIN},
}

def authorized_tools_for(agent_role: str) -> list[str]:
    role_permissions = ROLE_PERMISSION_MAP[agent_role]
    return [
        tool for tool, required in TOOL_PERMISSIONS.items()
        if required.issubset(role_permissions)
    ]

# Customer support agent only gets read + write
support_tools = authorized_tools_for("customer_support")
# ["get_account_balance", "lookup_policy", "send_notification"]
# NOT: issue_refund, delete_account
```

---

## Tool Calling vs Temporal Activities: Key Differences

| Aspect | Temporal Activity | LLM Tool Call |
| --- | --- | --- |
| **Invocation decision** | Developer (in workflow code) | LLM (via reasoning) |
| **Retry on failure** | Same activity, same args | Different tool/args if LLM decides |
| **State persistence** | Event log | Conversation history |
| **Idempotency** | Required for retry | Required for any write tool |
| **Authorization** | Workflow-level | Tool-level, per invocation |
| **Observability** | Temporal Web UI timeline | LangSmith / custom trace |
| **Cost** | Function execution cost only | LLM tokens + function cost |

**Use Temporal activities for**: Guaranteed execution, long-running steps, compliance audit trails.  
**Use LLM tool calls for**: Adaptive decisions about *what* to do, *when* to do it.

**Combine them**: Temporal activity wraps the entire agent run, and inside, the agent calls tools freely.

---

## Tool Versioning

Tools evolve — new parameters get added, return schemas change, deprecated fields are removed. Without versioning, tool changes break running agents silently.

```python
from dataclasses import dataclass

@dataclass
class ToolVersion:
    tool_name: str
    version: str                   # "2.1.0"
    schema: dict                   # JSON Schema for inputs
    return_schema: dict            # JSON Schema for outputs
    deprecated_at: str | None      # ISO date or None
    replacement: str | None        # tool name of the replacement

TOOL_REGISTRY: dict[str, list[ToolVersion]] = {
    "get_account_info": [
        ToolVersion("get_account_info", "1.0.0", schema_v1, return_v1, deprecated_at="2026-01-01", replacement="get_account_profile"),
        ToolVersion("get_account_info", "2.0.0", schema_v2, return_v2, deprecated_at=None, replacement=None),
    ],
}

def get_tool_for_agent(tool_name: str, agent_version_constraint: str = "latest") -> ToolVersion:
    """Resolve the correct tool version for an agent — never use deprecated tools for new agents."""
    versions = TOOL_REGISTRY.get(tool_name, [])
    active = [v for v in versions if v.deprecated_at is None]

    if not active:
        raise ValueError(f"Tool '{tool_name}' has no active versions — all deprecated")

    # Return latest active version (sorted by semver)
    return sorted(active, key=lambda v: tuple(int(x) for x in v.version.split(".")))[-1]
```

**Practice**: Pin agent prompts to tool versions the same way you pin prompt versions. When a tool releases a breaking change (MAJOR version), audit all agents that use it before deploying.

---

## Related

[MCP Impact](./mcp-impact) · [Agent Frameworks Comparison](./agent-frameworks-comparison) · [Durable Execution vs Cognitive Execution](./durable-vs-cognitive-execution) · [Reliability Playbook](./reliability-playbook)
