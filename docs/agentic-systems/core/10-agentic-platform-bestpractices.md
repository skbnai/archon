---
title: "Enterprise Agentic Platform Best Practices"
date_created: 2026-07-24
last_reviewed: 2026-07-24
status: current
domain: agentic-systems
doc_type: guide
topic_id: agentic-platform-bestpractices
supersedes:
  - ../knowledge-docs/docs/agentic-systems/platform/agentic_platform_bestpractices.md
---

**This is Part 1 of 3. [Continue with Part 2 →](pathname:///archon/agentic-systems/core/parts/10-agentic-platform-bestpractices-part2) for multitenancy, MCP, and ADFS. [Part 3 →](pathname:///archon/agentic-systems/core/parts/10-agentic-platform-bestpractices-part3) covers observability, governance, and roadmap.**

**ENTERPRISE AGENTIC PLATFORM — Best Practices, Antipatterns & Implementation Guide**
*Strands Agents · AgentCore · MCP · ADFS/FT Rights · Multitenancy · Langfuse*

| Document Type | Best Practices & Antipatterns Guide |
| --- | --- |
| Companion To | Enterprise Agentic Platform Architecture v1.0 |
| Version | 1.0 — Based on Research to March 2026 |
| Classification | INTERNAL — RESTRICTED |
| Coverage | Strands Agents SDK, AgentCore GA, MCP, ADFS, Multitenancy, Langfuse |

# Enterprise Agentic Platform Best Practices
## 1. Executive Summary & Research Findings

This document consolidates research-backed best practices and antipatterns for implementing the Enterprise Agentic Platform. It covers five major capability layers: Strands Agents SDK (open-sourced by AWS in May 2025, 14M+ downloads), Amazon Bedrock AgentCore (GA October 2025), MCP tool integration, ADFS/FT Rights authentication propagation, and Langfuse observability. It also introduces the multitenancy model specific to a financial-services use case where multiple business divisions or external clients share platform infrastructure.

Key research findings that affect the architecture design:

- AgentCore reached General Availability in October 2025 with full VPC, PrivateLink, CloudFormation support — moving from the preview architecture assumed in the companion document to production-grade infrastructure.
- AgentCore Identity now natively supports Microsoft Entra ID (ADFS/Azure AD) as an identity provider, enabling direct IDP integration for agent authentication without custom BFF token bridging.
- AgentCore Gateway now includes built-in multitenancy interceptors, fine-grained tool access control, and identity propagation — this significantly changes how FT rights can be enforced.
- Strands Agents SDK ships with native OpenTelemetry (OTEL) support (via pip install strands-agents[otel]) and integrates directly with Langfuse via OTEL export, enabling zero-code-change observability.
- AgentCore Runtime provides microVM-level session isolation (Firecracker), meaning each user session gets dedicated CPU, memory, and filesystem — this is the correct multitenancy model for financial services.
- Strands Agent SOPs (Standard Operating Procedures) provide a natural-language workflow specification format that can encode FT rights requirements directly into agent behaviour contracts.

## 2. Strands Agents SDK — Best Practices & Antipatterns

## 2.1 Core Design Principles

:::note

Strands Agents is a model-driven SDK where the LLM does the planning — not the developer. The correct mental model is: define model + tools + prompt, then trust the model to reason about what to call and when. Fighting this model-driven approach by over-constraining the agent loop leads to brittle systems.

:::

### 2.1.1 Agent Initialisation

:::tip[✅ Best Practice]

Define agents using the three-component pattern: model provider (Bedrock Claude), a focused system prompt, and a bounded set of tools. Prefer small, highly-focused agents over large agents with many tools. An agent with 20+ tools is a smell — use sub-agents instead.

:::

:::danger[❌ Antipattern]

Passing every available tool to a single agent. Strands documentation explicitly notes that models cannot accurately select from very large toolsets (6000+ tools example). Use semantic tool retrieval (the retrieve tool with knowledge base) to dynamically surface relevant tools, or decompose into specialist agents.

:::

```python
# ✅  CORRECT: Focused agent with bounded toolset
from strands import Agent
from strands.models import BedrockModel

customer_agent = Agent(
    model=BedrockModel(model_id="anthropic.claude-sonnet-4-20250514"),
    system_prompt=CUSTOMER_AGENT_SOP,   # see Section 2.3 for SOPs
    tools=[get_customer_profile, get_account_summary, get_recent_transactions],  # bounded FT scope: only CUST_VIEW tools
)

# ❌  WRONG: Mega-agent with all tools
god_agent = Agent(
    model=...,
    tools=[*customer_tools, *trading_tools, *reporting_tools, *admin_tools],  # model cannot reason correctly over 40+ tools
)
```

### 2.1.2 Context Window Management

:::tip[✅ Best Practice]

Implement a ConversationManager to control history growth. For long-running financial workflows, use a sliding window (keep last N turns) plus a structured summary of earlier context. Store summaries in DynamoDB, not in the LLM context window.

:::

:::danger[❌ Antipattern]

Accumulating the full conversation history indefinitely. In multi-step financial agent workflows (e.g., trade analysis), the context window can overflow after 10-20 turns, causing silent truncation and loss of earlier FT context claims. Strands' ConversationManager's reduce_context hook must be implemented.

:::

```python
# ✅  CORRECT: Custom ConversationManager with FT-aware summarisation
from strands.agent.conversation_manager import ConversationManager

class BankConversationManager(ConversationManager):
    def __init__(self, max_turns=15, dynamo_table=None):
        self.max_turns = max_turns
        self.dynamo = dynamo_table

    def apply_management(self, messages):
        # Keep last max_turns, summarise older turns
        if len(messages) > self.max_turns:
            summary = self._summarise(messages[:-self.max_turns])
            self.dynamo.put_item(Item={'session_id': ..., 'summary': summary})
            return messages[-self.max_turns:]
        return messages

    def reduce_context(self, messages):
        # Called when token limit exceeded — hard-trim to last 8 turns
        return messages[-8:]
```

### 2.1.3 Error Handling & Resilience

:::tip[✅ Best Practice]

Wrap all agent invocations in retry logic with exponential backoff. Set explicit max_iterations on the agent loop. Define a graceful fallback that returns a structured error response to the calling API rather than propagating exceptions.

:::

:::danger[❌ Antipattern]

Relying on the agent to self-terminate gracefully. Without max_iterations limits, runaway agents can loop indefinitely on ambiguous tasks — consuming tokens and budget. Strands does not enforce a loop limit by default; the application code must.

:::

```python
# ✅  CORRECT: Bounded agent invocation with budget guard
import asyncio
from strands import Agent

async def invoke_agent_safely(agent: Agent, prompt: str, max_tokens: int = 8000) -> dict:
    try:
        response = await asyncio.wait_for(
            agent.invoke_async(prompt, max_iterations=15),
            timeout=90.0  # hard wall-clock timeout
        )
        if response.token_count > max_tokens:
            raise BudgetExceededError(f'Agent used {response.token_count} tokens')
        return response
    except asyncio.TimeoutError:
        return {'error': 'AGENT_TIMEOUT', 'retryable': True}
    except Exception as e:
        log_to_langfuse(span_id=..., error=str(e))
        return {'error': 'AGENT_FAILURE', 'message': str(e)}
```

## 2.2 Multi-Agent Patterns

:::note

Strands supports four multi-agent collaboration patterns: Agents-as-Tools (hierarchical), Swarms (peer mesh), Graphs (deterministic topology via GraphBuilder), and Workflows (pipeline/DAG). Choose the pattern based on your dependency structure and risk profile.

:::

### 2.2.1 Pattern Selection Guide

| Pattern | Description | Best For (Bank Context) | Watch Out For |
| --- | --- | --- | --- |
| Agents-as-Tools | Supervisor calls specialist agents as tools | FT-scoped delegation; supervisor enforces rights before delegating | Latency in deep hierarchies; each hop adds 200-500ms |
| Swarm / Mesh | Agents communicate peer-to-peer via agent_graph | Parallel research, redundancy, consensus for ambiguous decisions | Hard to enforce FT rights across peer calls; audit trail complexity |
| GraphBuilder (DAG) | Typed handoffs, deterministic topology | Regulated workflows (trade approval chains, compliance checks) | Requires upfront workflow design; less flexible than ReAct |
| Workflow Pipeline | Sequential stages: plan → execute → synthesise | ReWOO for complex multi-step financial analysis | No dynamic replanning; brittle if intermediate steps fail |

:::tip[✅ Best Practice]

For the bank's agentic platform, use Agents-as-Tools (supervisor-worker) for most workflows. The supervisor agent enforces FT rights before delegating to specialist agents. Use GraphBuilder for regulated workflows (trade submission, compliance sign-off) where deterministic step ordering is required.

:::

:::danger[❌ Antipattern]

Using Swarm pattern for actions that modify state (write operations). In a Swarm, agents communicate asynchronously and there is no coordinator to prevent duplicate writes or conflicting state mutations. Swarms are appropriate for read-heavy research tasks, not for workflows that submit transactions.

:::

### 2.2.2 Supervisor Agent FT Enforcement Pattern

```python
# ✅  CORRECT: Supervisor checks FT rights before delegating
from strands import Agent, tool

@tool
def delegate_to_portfolio_agent(task: str, user_ft_rights: list) -> str:
    """Delegate portfolio analysis to specialist agent. Requires FT:PORTFOLIO_READ in user_ft_rights."""
    if "FT:PORTFOLIO_READ" not in user_ft_rights:
        return "ACCESS_DENIED: FT:PORTFOLIO_READ required for portfolio operations"
    # Only create sub-agent if FT check passes
    portfolio_agent = Agent(model=..., tools=portfolio_tools)
    return portfolio_agent(task)

# Supervisor receives enriched context from API gateway
supervisor = Agent(
    model=...,
    tools=[delegate_to_portfolio_agent, delegate_to_customer_agent],
    system_prompt=f'User FT rights: {ft_rights_from_jwt}. Check rights before delegation.'
)
```

## 2.3 Strands Agent SOPs (Standard Operating Procedures)

:::note

Strands Agent SOPs, released as open source in late 2025, allow agent workflows to be defined in structured natural-language markdown with RFC 2119 constraints (MUST, SHOULD, MAY). For a regulated bank, SOPs can encode compliance requirements and FT rights checks directly into the agent's instruction set.

:::

:::tip[✅ Best Practice]

Use Agent SOPs as the system_prompt for each specialist agent. Include explicit FT rights requirements in the SOP's preconditions section. This creates a human-readable, auditable specification of what the agent is permitted to do — critical for regulatory review.

:::

:::danger[❌ Antipattern]

Embedding business rules, FT requirements, and compliance constraints in ad-hoc natural language system prompts that are scattered across codebase and not version-controlled. SOPs provide a standardised, parameterisable format that can be reviewed by compliance teams without reading Python code.

:::

```python
# ✅  CORRECT: SOP as system prompt (stored in version-controlled markdown)
PORTFOLIO_AGENT_SOP = '''
# Portfolio Analysis Agent SOP

## Preconditions
- The calling user MUST have FT:PORTFOLIO_READ in their ft_rights claim
- The agent MUST NOT access customer PII unless FT:SENSITIVE_DATA is also present
- The agent MUST log all data access actions to the audit span

## Steps
1. MUST validate the portfolio_id belongs to the authenticated customer
2. SHOULD retrieve the current holdings using the get_portfolio tool
3. MAY calculate derived metrics (P&L, risk score) using the analytics tool
4. MUST NOT expose raw account numbers in the final response

## Postconditions
- The response MUST include a data_accessed_at timestamp
- All tool calls MUST be traceable in Langfuse with ft_context metadata
'''

portfolio_agent = Agent(model=..., tools=[...], system_prompt=PORTFOLIO_AGENT_SOP)
```

## 2.4 Strands AgentOps — Observability

:::note

Strands Agents ships with native OpenTelemetry (OTEL) instrumentation. Installing strands-agents[otel] enables automatic span export without code changes. The bank's self-hosted Langfuse instance accepts OTEL/OTLP spans directly, creating a zero-code observability pipeline from agent execution to Langfuse dashboards.

:::

### 2.4.1 OTEL Integration with Langfuse

:::tip[✅ Best Practice]

Configure Strands' OTEL exporter to target the self-hosted Langfuse OTLP endpoint within the VPC. This ensures all agent traces, including FT rights context in span metadata, remain within the EU AWS environment. Use the @observe() decorator from the Langfuse SDK to add bank-specific attributes (ft_rights, tenant_id, session_id).

:::

```python
# requirements.txt:
#   strands-agents[otel]
#   langfuse

# -- Environment variables (set via AWS Secrets Manager / ECS Task Definition) --
# OTEL_EXPORTER_OTLP_ENDPOINT=http://langfuse-internal.vpc:4318/api/public/otel
# OTEL_EXPORTER_OTLP_HEADERS=Authorization=Basic <base64(pk:sk)>
# OTEL_SERVICE_NAME=agentic-platform-{env}
# OTEL_TRACES_SAMPLER=always_on

# -- Agent code — no changes required for basic tracing --
from strands import Agent
from langfuse.decorators import observe, langfuse_context

@observe(name='supervisor_agent_invoke')
async def invoke_supervisor(user_prompt: str, enriched_ctx: dict):
    # Add bank-specific span attributes
    langfuse_context.update_current_observation(
        metadata={
            'ft_rights': enriched_ctx.get('ft_rights', []),
            'tenant_id': enriched_ctx.get('tenant_id'),
            'session_id': enriched_ctx.get('session_id'),
            'user_upn':  enriched_ctx.get('upn'),  # pseudonymised in Langfuse
        }
    )
    return await supervisor_agent.invoke_async(user_prompt)
```

:::danger[❌ Antipattern]

Logging raw PII (customer names, account numbers, UPNs) into Langfuse trace metadata. GDPR Art.25 requires privacy by design. Use Langfuse's field masking configuration and pseudonymise UPNs before trace ingestion. Set data retention policies (90 days for full traces, 1 year for aggregates).

:::

### 2.4.2 Key Metrics to Instrument

| Metric | Strands Instrumentation Point | Bank-Specific Alert |
| --- | --- | --- |
| Agent loop iterations | agent.metrics.iteration_count | Alert if &gt; 12 iterations (runaway agent risk) |
| Total token usage per session | agent.metrics.total_tokens | Alert if &gt; 50k tokens (budget governance) |
| Tool call latency (p99) | OTEL span duration on tool calls | Alert if MCP tool &gt; 5s (circuit breaker candidate) |
| FT rights denial rate | Custom span attribute: ft_check_result | Alert if &gt; 0.5% (misconfiguration indicator) |
| Agent timeout rate | Error span type: AGENT_TIMEOUT | Alert if &gt; 0.1% in any 5-minute window |
| Conversation manager reduce_context events | Custom counter in ConversationManager | Alert if &gt; 5% of sessions hit context limit |
| Sub-agent delegation depth | Custom span attribute: delegation_depth | Alert if depth &gt; 3 (latency and cost risk) |

## 2.5 Strands Skills (Pre-built Tools)

:::note

The strands-agents-tools package provides 20+ pre-built tools including file operations, shell integration, memory (Mem0, Bedrock Knowledge Bases, MongoDB), web infrastructure (Tavily, Exa), HTTP client, and browser automation. For a bank, the dynamic MCP client tool must NEVER be enabled in production — it allows agents to connect to arbitrary external MCP servers at runtime.

:::

:::tip[✅ Best Practice]

Use strands_tools pre-built tools only for non-sensitive capabilities (calculator, current_time, HTTP GET to internal APIs). For all bank data access, implement custom @tool functions that include FT rights validation. Register tools per-agent based on the agent's FT scope.

:::

:::danger[❌ Antipattern]

Enabling the Dynamic MCP Client tool (strands_tools.mcp) in production. The Dynamic MCP Client allows the agent to connect to ANY external MCP server specified in the prompt. In a financial services context, this creates a prompt injection vector where malicious input could direct the agent to exfiltrate data to attacker-controlled MCP servers.

:::

| Tool | Usage Recommendation |
| --- | --- |
| calculator | Safe — use for financial calculations |
| current_time | Safe — date/time context for transactions |
| http_request | Use only with allowlist of internal API endpoints |
| file_read / file_write | Prohibited — use S3-backed document MCP instead |
| shell | Prohibited — never enable in production agents |
| browser | Use only via AgentCore Browser Tool (isolated microVM) |
| python_repl | Prohibited — use AgentCore Code Interpreter instead |
| mcp (Dynamic MCP Client) | PROHIBITED — allows arbitrary external server connection |
| memory (Mem0/Knowledge Bases) | Approved — use with tenant-scoped namespaces |
| retrieve | Approved — use with FT-scoped OpenSearch indices |

## 3. Amazon Bedrock AgentCore — Best Practices

## 3.1 AgentCore Runtime — Session Isolation

:::note

AgentCore Runtime GA (October 2025) uses Firecracker microVMs to provide complete CPU, memory, and filesystem isolation per session. Each session runs in a dedicated microVM that is completely sanitised after termination. This is the correct isolation model for a multi-tenant financial services platform.

:::

:::tip[✅ Best Practice]

Map one AgentCore Runtime session to one user's conversation context. Use the user's sub claim from the enriched JWT as the actor_id and generate a unique runtimeSessionId per conversation. Store the session_id → user mapping in DynamoDB with TTL, as AgentCore does not enforce session-to-user mappings itself.

:::

:::danger[❌ Antipattern]

Reusing a single AgentCore Runtime session across multiple users to save cold-start latency. Even though session state is accessible within a session, cross-user session reuse can leak conversation state. The microVM isolation only works if session IDs are kept per-user.

:::

```python
# ✅  CORRECT: Per-user session management (BFF layer)
import boto3, hashlib, time

def get_or_create_session(user_sub: str, conversation_id: str) -> str:
    '''Map user + conversation to an AgentCore session ID.'''
    # Deterministic session ID from user + conversation (no DB lookup needed)
    session_id = hashlib.sha256(
        f"{user_sub}:{conversation_id}".encode()
    ).hexdigest()[:32]
    # Record session-user mapping in DynamoDB for audit trail
    dynamo.put_item(
        TableName='agent-sessions',
        Item={
            'session_id': session_id,
            'user_sub': user_sub,
            'created_at': int(time.time()),
            'ttl': int(time.time()) + 1800  # 30 min session TTL
        },
        ConditionExpression='attribute_not_exists(session_id)'
    )
    return session_id
```

## 3.2 AgentCore Gateway — FT Rights with Interceptors

:::note

AgentCore Gateway (GA October 2025) supports Lambda-based request interceptors that can enforce fine-grained access control, implement multitenancy, and propagate user identity to downstream MCP tools. This is the correct place to enforce FT rights in the AgentCore deployment model.

:::

:::tip[✅ Best Practice]

Implement an AgentCore Gateway interceptor that extracts the enriched context JWT from the request, validates the FT rights claim, and either forwards the tool call (with identity-propagated headers) or returns a 403 with a structured error code. The interceptor runs before the MCP server receives the call.

:::

```python
# ✅  CORRECT: AgentCore Gateway interceptor for FT rights enforcement
import json, jwt, boto3
from functools import lru_cache

# Tool → required FT rights mapping
TOOL_FT_MAP = {
    'get_customer_profile':   ['FT:CUST_VIEW'],
    'get_portfolio':          ['FT:CUST_VIEW', 'FT:PORTFOLIO_READ'],
    'submit_trade_order':     ['FT:CUST_VIEW', 'FT:TRADE_SUBMIT'],
    'export_report':          ['FT:REPORT_EXPORT'],
}

@lru_cache(maxsize=1024)
def get_jwks() -> dict:
    # Cached JWKS from BFF — refreshed by background job
    return secrets_manager.get_secret_value(SecretId='bff-jwks')['SecretString']

def lambda_handler(event, context):
    tool_name = event.get('toolName')
    auth_header = event.get('headers', {}).get('X-Enriched-Context', '')
    # Validate enriched context token
    try:
        claims = jwt.decode(auth_header, get_jwks(), algorithms=['RS256'])
        ft_rights = claims.get('ft_rights', [])
    except jwt.ExpiredSignatureError:
        return {'action': 'DENY', 'statusCode': 401, 'message': 'TOKEN_EXPIRED'}
    # Check FT rights for the requested tool
    required = TOOL_FT_MAP.get(tool_name, [])
    if not all(ft in ft_rights for ft in required):
        missing = [ft for ft in required if ft not in ft_rights]
        return {
            'action': 'DENY',
            'statusCode': 403,
            'message': f'MISSING_FT_RIGHTS: {missing}',
            'auditContext': {'user': claims['upn'], 'tool': tool_name}
        }
    # Enrich forwarded request with user identity
    return {
        'action': 'ALLOW',
        'additionalHeaders': {
            'X-User-UPN': claims['upn'],
            'X-Tenant-ID': claims.get('tenant_id', 'default'),
            'X-FT-Rights': ','.join(ft_rights),
        }
    }
```

## 3.3 AgentCore Identity — ADFS Integration

:::tip[✅ Best Practice]

Use AgentCore Identity's native Microsoft Entra ID / ADFS integration to handle agent-level token validation. AgentCore Identity supports bearer token forwarding from OIDC providers, meaning the enriched context JWT issued by the BFF can be validated directly at the AgentCore layer without a separate JWKS fetch per call.

:::

:::danger[❌ Antipattern]

Implementing a custom token validation middleware inside the agent code. Token validation logic inside the agent loop creates a maintenance burden and security risk if the validation library has vulnerabilities. Delegate token validation to the AgentCore Identity layer or the API Gateway authoriser.

:::

## 3.4 AgentCore Memory — Tenant-Scoped Design

:::tip[✅ Best Practice]

Scope all AgentCore Memory operations using the actor_id (derived from the user's sub claim) and namespace (derived from tenant_id). This prevents cross-tenant memory contamination. For long-term memory, apply FT rights filtering — a user with FT:PORTFOLIO_READ should only retrieve portfolio-related memories.

:::

:::danger[❌ Antipattern]

Storing sensitive financial data (account balances, positions, PII) in AgentCore Memory as raw text. Memory stores should contain only sanitised summaries. Use field-level encryption (KMS) for any memory items that contain regulated data. Implement a memory TTL aligned with data retention policies.

:::

```python
# ✅  CORRECT: FT-scoped, tenant-aware memory storage
from bedrock_agentcore import AgentCoreMemory

memory_client = AgentCoreMemory()

async def store_interaction_summary(user_sub: str, tenant_id: str, ft_rights: list, summary: str):
    # Namespace isolates memory per tenant
    namespace = f'tenant:{tenant_id}:user:{user_sub}'
    # Only store summary, never raw financial data
    sanitised = sanitise_pii(summary)  # remove names, account numbers
    await memory_client.store(
        actor_id=user_sub,
        namespace=namespace,
        content=sanitised,
        metadata={
            'ft_rights_at_store': ft_rights,   # for retrieval filtering
            'tenant_id': tenant_id,
            'stored_at': datetime.utcnow().isoformat()
        }
    )
```

---

**This is Part 1 of 3. [Continue with Part 2 →](pathname:///archon/agentic-systems/core/parts/10-agentic-platform-bestpractices-part2) for multitenancy, MCP, and ADFS. [Part 3 →](pathname:///archon/agentic-systems/core/parts/10-agentic-platform-bestpractices-part3) covers observability, governance, and roadmap.**
