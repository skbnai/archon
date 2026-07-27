---
title: "AWS Strands & Bedrock AgentCore — Advanced Patterns v3.0"
doc_type: guide
domain: platforms
status: draft
topic_id: aws-strands-agentcore-advancedpatterns
last_reviewed: 2026-07-27
maturity: practitioner
supersedes: [docs/cloud-platforms/aws/AWS_Strands_AgentCore_AdvancedPatterns_v3.md]
tags: [aws, agentcore, strands, hooks, hitl, checkpointer, multi-agent]
covers_version: "N/A"
---

> **Known issue:** some fenced code examples on this page were flattened during the original PDF-to-markdown conversion (lost line breaks/indentation, stray artifact characters) and need reformatting. Tracked in migration/WAVE6_BATCH1_STATUS.md (repo root).

### AWS STRANDS & BEDROCK AGENTCORE

# AWS Strands & Bedrock AgentCore — Advanced Patterns v3.0
**Hooks · HITL · Checkpointer · Code Interpreter · Browser Agent · Meta Tool · Expert Patterns**

|**Vol 3 of 3**|**Expert Patterns**<br/>**Production Grade**|**March 2026**|
|---|---|---|
|**Volume**|3 of 3 — Advanced Patterns & Expert Implementations||
|**Prereqs**|Builder Journey Kit v1.0 + Delta Supplement v2.0||
|**Focus**|Hooks · HITL · Checkpointer Replay · Code Interpreter · Browser|· Meta Tool · Expert Patterns|
|**Status**|March 28, 2026 — Production Validated||

Advanced Patterns Volume

#### TABLE OF CONTENTS

##### CHAPTER A1 — Strands Hooks: Full Lifecycle System

A1.1 Hook Architecture: Events, Registry, Providers

A1.2 Full Event Inventory & Lifecycle Map

A1.3 Production Hook Patterns: Observability, Cost, PII

A1.4 retry_model & retry_tool: Conditional Re-execution

A1.5 Composing Multiple Hook Providers

##### CHAPTER A2 — HITL: Human-in-the-Loop Implementation

A2.1 The Two HITL Patterns in Strands

A2.2 Pattern 1: BeforeToolCallEvent Hook Interrupt

A2.3 Pattern 2: ToolContext.interrupt() from Inside @tool

A2.4 Async HITL: SQS/SNS Approval Workflows

A2.5 Resuming Agent Execution After Interrupt

A2.6 Max-Iteration Circuit Breaker & Deadlock Prevention

##### CHAPTER A3 — Checkpointer: State Persistence & Replay

A3.1 Why Agents Need Checkpointing (vs LangGraph model)

A3.2 Strands Built-In SessionManager (File, S3)

A3.3 LangGraph DynamoDBSaver + AgentCore Memory Backend

A3.4 AgentCoreMemorySaver + AgentCoreMemoryStore

A3.5 Multi-Tier Memory Orchestrator Pattern

A3.6 Replay: Time-Travel Debugging with Checkpoint History

##### CHAPTER A4 — AgentCore Code Interpreter

A4.1 Architecture: Secure Sandbox Execution A4.2 Default (Isolated) vs Custom (Public Network) Mode A4.3 Integration with Strands: built-in vs custom tool A4.4 File I/O, Visualization, and Multi-Language Support A4.5 Data Analysis Agent Pattern

##### CHAPTER A5 — AgentCore Browser Tool

A5.1 Browser Tool Architecture & Security Model A5.2 Integration with Strands Agent

A5.3 Browser-Based Data Extraction Patterns A5.4 Nova Act for Legacy System Automation

##### CHAPTER A6 — Meta Tool Pattern (Advanced)

A6.1 What Is the Meta Tool Pattern and Why Use It A6.2 Implementing create_skill_agent_tool (Reference)

A6.3 Dynamic Tool Registration at Runtime A6.4 Meta Tool + AgentCore Gateway: Unified Discovery

A6.5 Token-Budget-Aware Tool Routing

##### CHAPTER A7 — Expert Patterns & Specialised Implementations

A7.1 AgentCore Memory Branching (Parallel Agent Graphs)

A7.2 Structured Output with @tool + Pydantic Contracts

A7.3 Context Engineering: Hierarchical Memory Architecture

A7.4 Import-Agent: Migrating Bedrock Agents to Strands

A7.5 Claude Code as Remote A2A Sub-Agent

A7.6 Circuit Breaker & Retry Wrapper Tool Pattern

A7.7 Prompt Injection Defence: Multi-Layer Canary Pattern

A7.8 Cost-Aware Model Routing at Tool Dispatch

###### I **CHAPTER A1**

## Strands Hooks: Full Lifecycle System

Events · Registry · Retry · Composable Providers

#### A1.1 Hook Architecture

Strands Hooks are a **composable, type-safe extensibility mechanism** built into the agent loop. Unlike callback_handler (fire-and-forget kwargs dict), Hooks use **strongly-typed event objects** , support multiple subscribers per event, and allow *modifying agent behaviour* — not just observing it. Hooks are the foundation of Steering, HITL, cost tracking, PII scrubbing, and retry logic.

- A **HookProvider** class implements register_hooks(registry) to subscribe.

- A **HookRegistry** maps event types -> callback lists; manages execution ordering.

- Cleanup events (EndRequest, AfterModel, AfterTool) use **reverse callback ordering** .

- retry_model=True / retry=True on event objects trigger re-execution.

#### A1.2 Full Event Inventory & Lifecycle Map

|**Event**|**Purpose / What You Can Do**|**Frequency**|
|---|---|---|
|AgentInitializedEvent|After agent fully constructed. Setup, DB pool init, warm-up.|Once|
|StartRequestEvent|Before any model/tool execution on new request. Request-level<br/>setup, logging, auth check.|Per request|
|EndRequestEvent|After request completes (success or error). Cleanup, state persist.<br/>REVERSE order.|Per request|
|MessageAddedEvent|When user message, assistant response, or tool result added to<br/>history.|Per message|
|BeforeModelCallEvent|Before LLM invocation. Modify prompt, inject context, token-budget<br/>check.|Per LLM call|
|AfterModelCallEvent|After LLM response. Validate output, set retry_model=True to retry.|Per LLM call|
|BeforeToolCallEvent|Before tool execution. Intercept args, fire HITL interrupt, cancel tool.|Per tool call|
|AfterToolCallEvent|After tool execution. Validate result, set retry=True to re-run tool.|Per tool call|

#### A1.3 Production Hook Patterns

###### `hooks_production.py`

```
from strands.hooks import (
    HookProvider, HookRegistry,
    AgentInitializedEvent, StartRequestEvent, EndRequestEvent,
```

```
    MessageAddedEvent, BeforeModelCallEvent, AfterModelCallEvent,
    BeforeToolCallEvent, AfterToolCallEvent,
)
```

```
import time, logging, re
log = logging.getLogger(__name__)
```

`#` II `Hook 1: Observability — token cost + latency per request` IIIIIIIII `class ObservabilityHook(HookProvider): def register_hooks(self, registry: HookRegistry, **kw): registry.add_callback(StartRequestEvent,    self._start) registry.add_callback(BeforeModelCallEvent, self._before_llm) registry.add_callback(AfterModelCallEvent,  self._after_llm) registry.add_callback(EndRequestEvent,       self._end)`

```
    def _start(self, event: StartRequestEvent):
        self._t0 = time.perf_counter()
```

```
        self._tokens_in = self._tokens_out = 0
```

```
    def _before_llm(self, event: BeforeModelCallEvent):
```

```
        self._llm_t0 = time.perf_counter()
```

```
    def _after_llm(self, event: AfterModelCallEvent):
```

```
        llm_ms = (time.perf_counter() - self._llm_t0) * 1000
```

```
        if event.stop_response and hasattr(event.stop_response, "usage"):
```

```
            u = event.stop_response.usage
```

```
            self._tokens_in  += getattr(u, "inputTokens",  0)
            self._tokens_out += getattr(u, "outputTokens", 0)
        log.info(f"LLM call: {llm_ms:.0f}ms")
```

```
    def _end(self, event: EndRequestEvent):
```

```
        total_ms = (time.perf_counter() - self._t0) * 1000
```

```
        log.info(f"Request: {total_ms:.0f}ms | in={self._tokens_in} out={self._tokens_out}")
```

`#` II `Hook 2: PII Scrubber — redact before storage` IIIIIIIIIIIIIIIIIIIIII `class PIIScrubHook(HookProvider):`

```
    _PII_PATTERNS = [
```

```
        (re.compile(r'\b\d{3}-\d{2}-\d{4}\b'), "[SSN]"),          # SSN
```

```
        (re.compile(r'\b4[0-9]{12}(?:[0-9]{3})?\b'), "[CARD]"),      # Visa
```

```
        (re.compile(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+'), "[EMAIL]"),  # Email
```

```
    ]
    def register_hooks(self, registry: HookRegistry, **kw):
        registry.add_callback(MessageAddedEvent, self._scrub_message)
```

```
    def _scrub_message(self, event: MessageAddedEvent):
        msg = event.message
```

```
        if isinstance(msg.get("content"), str):
```

```
            content = msg["content"]
```

```
            for pattern, replacement in self._PII_PATTERNS:
```

```
                content = pattern.sub(replacement, content)
```

```
            msg["content"] = content  # Mutate in-place before persistence
```

`#` II `Hook 3: retry_model on low-quality response` IIIIIIIIIIIIIIIIIIIIIII `class QualityRetryHook(HookProvider):`

```
    def __init__(self, max_retries=2):
```

```
        self._retries = {}; self._max = max_retries
```

```
    def register_hooks(self, registry: HookRegistry, **kw):
        registry.add_callback(AfterModelCallEvent, self._check_quality)
    def _check_quality(self, event: AfterModelCallEvent):
```

`if not event.stop_response: return content = str(event.stop_response.content) session = id(event)  # Use event id as proxy for session key retries = self._retries.get(session, 0) if retries &lt; self._max and len(content) &lt; 50 and "sorry" in content.lower(): self._retries[session] = retries + 1 event.retry_model = True   #` &lt;- `Discard response, re-invoke model log.warning(f"Low-quality response, retry {retries+1}/{self._max}") #` II `Wire all hooks into agent` IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII `agent = Agent( model="us.anthropic.claude-sonnet-4-20250514", system_prompt="You are a production assistant.", tools=[...], hooks=[ObservabilityHook(), PIIScrubHook(), QualityRetryHook()], )`

###### II **WARNING**

**retry_model vs retry (tool)** : event.retry_model=True on AfterModelCallEvent discards the LLM response and re-calls the model — streaming events already emitted are NOT recalled. event.retry=True on AfterToolCallEvent re-runs the tool. Implement idempotent tools before enabling tool retry.

I **CHAPTER A2**

## Human-in-the-Loop (HITL)

Hook Interrupt · ToolContext · Async SQS · Deadlock Prevention

#### A2.1 The Two HITL Patterns in Strands

Strands provides two built-in mechanisms for pausing agent execution to request human approval. Both ultimately pause the **agentic loop** and surface an **interrupt object** in the agent result for the caller to handle. The distinction is *where* the interruption is initiated:

- **Pattern 1 — Hook interrupt** : Initiated in a HookProvider.BeforeToolCallEvent callback. Agent code stays

- clean; interrupt logic is externalized.

- **Pattern 2 — ToolContext interrupt** : Initiated inside a @tool function using ToolContext.interrupt(). Useful

- when mid-execution data determines approval need.

#### A2.2 Pattern 1: Hook-Based HITL Interrupt

###### `hitl_hook_pattern.py`

```
from strands import Agent, tool
from strands.hooks import BeforeToolCallEvent, HookProvider, HookRegistry
from typing import Any
```

`#` II `Define sensitive tools` IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII `@tool`

```
def send_email(to: str, subject: str, body: str) -> str:
    """Send an email to a recipient."""
```

```
    return f"Email sent to {to}"
```

```
@tool
```

```
def delete_records(table: str, filter_expr: str) -> str:
    """Delete database records matching filter."""
```

```
    return f"Deleted records from {table} where {filter_expr}"
```

```
@tool
```

```
def transfer_funds(account_from: str, account_to: str, amount: float) -> str:
    """Transfer funds between accounts."""
```

```
    return f"Transferred ${amount} from {account_from} to {account_to}"
```

`#` II `HITL Hook: intercept specific tools` IIIIIIIIIIIIIIIIIIIIIIIIIIIIIII `class ApprovalHook(HookProvider):`

```
    SENSITIVE_TOOLS = {"send_email", "delete_records", "transfer_funds"}
    HIGH_VALUE_THRESHOLD = 10_000.0
```

```
    def register_hooks(self, registry: HookRegistry, **kw: Any) -> None:
        registry.add_callback(BeforeToolCallEvent, self._review_action)
```

```
    def _review_action(self, event: BeforeToolCallEvent) -> None:
        tool_name = event.tool_use["name"]
```

```
        tool_input = event.tool_use["input"]
```

```
        if tool_name not in self.SENSITIVE_TOOLS:
            return  # Not sensitive — proceed immediately
        # Build rich context for the human reviewer
        reason = {
            "tool": tool_name,
            "input": tool_input,
            "risk_level": self._assess_risk(tool_name, tool_input),
            "agent_reasoning": "Agent determined this action is necessary",
        }
        # PAUSE execution — return interrupt object to caller
        decision = event.interrupt(
            f"approval-{tool_name}",  # Unique interrupt name (must be unique per tool call)
            reason=reason,            # JSON-serializable context for reviewer
        )
        # Resume handling based on human decision
        if decision == "APPROVE":
            pass  # Proceed — event.cancel_tool not set
        elif decision == "MODIFY":
            # Human can provide modified args
            event.tool_use["input"] = decision_data.get("modified_input", tool_input)
        else:
            event.cancel_tool = f"Action cancelled by human reviewer. Reason: {decision}"
    def _assess_risk(self, tool: str, inp: dict) -> str:
        if tool == "transfer_funds" and float(inp.get("amount", 0)) > self.HIGH_VALUE_THRESHOLD:
            return "HIGH"
        if tool == "delete_records": return "HIGH"
        return "MEDIUM"
    system_prompt="You are a financial operations agent.",
    tools=[send_email, delete_records, transfer_funds],
    hooks=[ApprovalHook()],
    callback_handler=None,  # Disable streaming output for cleaner HITL flow
)
```

#### A2.3 Pattern 2: ToolContext.interrupt() Inside @tool

###### `hitl_toolcontext.py`

```
from strands import Agent, tool
from strands.types import ToolContext
@tool
def deploy_infrastructure(stack_name: str, environment: str, *, tool_context: ToolContext) -> str:
    """Deploy CloudFormation stack to environment."""
    # Mid-execution decision: prod deployments always need approval
    if environment == "production":
        # Gather deployment-time context
        preview = generate_change_set(stack_name)
        risk_assessment = {
            "stack": stack_name,
            "environment": environment,
            "changes": preview["changes"],
```

```
            "estimated_downtime": preview.get("downtime_min", 0),
            "affected_resources": len(preview["changes"])
        }
        # Request human approval from inside the tool
        approval = tool_context.interrupt(
            "prod-deploy-approval",
            reason=risk_assessment
        )
        if approval != "APPROVED":
            return f"Deployment cancelled: {approval}"
    # Proceed with deployment
    return execute_deployment(stack_name, environment)
```

#### A2.4 Async HITL: SQS/SNS Approval Workflow

For long-running workflows where human approval may take minutes or hours, implement an async HITL pattern: pause agent, persist interrupt state to DynamoDB, send SNS notification, resume when webhook callback arrives:

###### `async_hitl_sqs.py`

`#` II `Producer: invoke agent, detect interrupt, persist state` IIIIIIIII `import boto3, json, uuid def invoke_with_hitl(prompt: str, session_id: str): result = agent(prompt, callback_handler=None) if result.stop_reason == "interrupt": # Persist interrupt state for later resumption interrupt_id = str(uuid.uuid4()) dynamodb = boto3.client("dynamodb", region_name="us-east-1") dynamodb.put_item( TableName="agent-hitl-state", Item={ "interrupt_id": {"S": interrupt_id}, "session_id":   {"S": session_id}, "agent_messages": {"S": json.dumps(result.message)}, "interrupts":   {"S": json.dumps(result.interrupts)}, "ttl":          {"N": str(int(time.time()) + 86400)},  # 24h TTL } ) # Notify human reviewer via SNS` -> `email/Slack sns = boto3.client("sns", region_name="us-east-1") for interrupt in result.interrupts: sns.publish( TopicArn=APPROVAL_TOPIC_ARN, Subject=f"Agent approval required: {interrupt['name']}", Message=json.dumps({ "interrupt_id": interrupt_id, "session_id": session_id, "action_required": interrupt["reason"], "approve_url": f"https://api.example.com/approve/{interrupt_id}/APPROVE", "reject_url":  f"https://api.example.com/approve/{interrupt_id}/REJECT", })`

`) return {"status": "pending_approval", "interrupt_id": interrupt_id} return {"status": "complete", "result": result.message} #` II `Consumer: webhook resumes agent with human decision` IIIIIIIIIIIIIII `def resume_agent(interrupt_id: str, decision: str): # Load persisted state item = dynamodb.get_item(TableName="agent-hitl-state", Key={"interrupt_id": {"S": interrupt_id}})["Item"] session_id   = item["session_id"]["S"] interrupts   = json.loads(item["interrupts"]["S"]) # Build interrupt responses responses = [{"interruptResponse": {"interruptId": i["id"], "response": decision}} for i in interrupts] # Resume agent with the human decision result = agent( None,  # No new user message — continue from interrupt session_id=session_id, interrupt_responses=responses, ) return result.message`

#### A2.5 HITL Circuit Breaker & Max-Iteration Guard

###### `circuit_breaker.py`

`# Prevent infinite HITL loops and runaway agent loops from strands import Agent from strands.hooks import HookProvider, HookRegistry, StartRequestEvent, BeforeToolCallEvent class CircuitBreakerHook(HookProvider): """Prevents: (1) infinite approval loops, (2) runaway tool call loops.""" def __init__(self, max_iterations=20, max_hitl_per_session=5): self._tool_calls = 0 self._hitl_count = 0 self._max_iter   = max_iterations self._max_hitl   = max_hitl_per_session def register_hooks(self, registry: HookRegistry, **kw): registry.add_callback(StartRequestEvent,  self._reset) registry.add_callback(BeforeToolCallEvent, self._check) def _reset(self, event: StartRequestEvent): self._tool_calls = 0  # Reset per request (not per session) def _check(self, event: BeforeToolCallEvent): self._tool_calls += 1 # Circuit breaker: too many tool calls` -> `force stop if self._tool_calls > self._max_iter: event.cancel_tool = ( f"CIRCUIT BREAKER: Exceeded {self._max_iter} tool calls. " "Stopping to prevent infinite loop. Please refine the task." ) # Setting force_stop on agent would be cleaner; cancel_tool is the hook-accessible path # HITL guard: if already approved many times, require escalation if self._hitl_count >= self._max_hitl:`

```
            event.cancel_tool = (
```

```
                f"HITL LIMIT: {self._max_hitl} approvals already granted in this session. "
```

```
                "Further actions require manager escalation."
```

```
            )
```

###### I **CHAPTER A3**

*Part 1 of 3. Continued in [Part 2](parts/12-aws-strands-agentcore-advancedpatterns-part2.md).*
