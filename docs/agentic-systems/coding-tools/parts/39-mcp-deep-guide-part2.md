---
title: "MCP Deep Guide — Enterprise Deployment & Operations (Part 2)"
date_created: 2026-07-24
last_reviewed: 2026-07-24
status: current
domain: agentic-systems
doc_type: guide
topic_id: mcp-deep-guide-part2
supersedes: []
covers_version: "as of 2026-07-10"
---

# MCP Deep Guide — Enterprise Deployment & Operations (Part 2)

**This is Part 2 of 2. [Back to Part 1 ←](pathname:///archon/agentic-systems/coding-tools/39-mcp-deep-guide) for protocol fundamentals, architecture, building servers, and OAuth 2.1.**

---

## 11. Enterprise MCP

### Admin Controls and Allow-Lists

Enterprise deployments restrict which MCP servers each team or individual can access. This is managed centrally by the IT/Security team.

**Claude Code enterprise settings (`/etc/claude/settings.json` or MDM-deployed):**

```json
{
  "mcp": {
    "allowedServers": [
      "company-tools",
      "github",
      "postgres-analytics"
    ],
    "blockedServers": ["*"],
    "requireApprovalFor": ["write_database", "send_email", "deploy"],
    "auditLogEndpoint": "https://audit.company.internal/mcp-events"
  }
}
```

### Okta / Entra ID Provisioning

Group-based MCP server assignment, managed through your IdP:

```yaml
# Okta MCP Application Assignment (IT-managed)
mcp_application_config:
  okta_domain: "company.okta.com"
  app_name: "Claude Code MCP Servers"

  group_assignments:
    - group: "Engineering"
      servers:
        - name: "github"
          scopes: ["repo:read", "pr:write", "issue:write"]
        - name: "postgres-analytics"
          scopes: ["readonly"]
        - name: "company-tools"
          scopes: ["query_analytics", "search_knowledge_base", "run_code"]

    - group: "Sales"
      servers:
        - name: "salesforce"
          scopes: ["opportunities:read", "contacts:read"]
        - name: "slack"
          scopes: ["messages:write"]
        - name: "company-tools"
          scopes: ["search_knowledge_base", "get_employee_info"]

    - group: "IT-Admins"
      servers: "*"   # Full access to all approved servers
      scopes: "*"
```

### Audit Logging

Every tool call must be logged with sufficient detail to reconstruct what happened and who triggered it.

```python
@mcp.middleware
async def enterprise_audit_middleware(message, call_next):
    start = time.monotonic()
    result = None
    error = None

    try:
        result = await call_next(message)
        return result
    except Exception as exc:
        error = exc
        raise
    finally:
        duration_ms = round((time.monotonic() - start) * 1000)
        method = getattr(message, "method", "unknown")
        tool_name = None
        arguments_summary = None

        if method == "tools/call":
            tool_name = getattr(message.params, "name", None)
            raw_args = getattr(message.params, "arguments", {})
            # Redact sensitive fields before logging
            arguments_summary = {
                k: "***REDACTED***" if any(s in k.lower() for s in ("key", "token", "secret", "password"))
                else str(v)[:200]
                for k, v in (raw_args or {}).items()
            }

        await audit_sink.write({
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "event_type": "mcp_tool_call",
            "server_name": "company-tools",
            "method": method,
            "tool_name": tool_name,
            "user_id": getattr(getattr(message, "_meta", None), "user_id", None),
            "session_id": getattr(getattr(message, "_meta", None), "session_id", None),
            "duration_ms": duration_ms,
            "success": error is None,
            "error": str(error) if error else None,
            "arguments_summary": arguments_summary,
        })
```

### Rate Limiting and Quotas

```python
@mcp.middleware
async def quota_middleware(message, call_next):
    if getattr(message, "method", None) != "tools/call":
        return await call_next(message)

    user_id = getattr(getattr(message, "_meta", None), "user_id", "anonymous")
    tool_name = message.params.name

    # Per-user daily quota
    daily_key = f"quota:user:{user_id}:day:{date.today()}"
    daily_count = await redis.incr(daily_key)
    await redis.expire(daily_key, 86400)

    if daily_count > 1000:
        raise PermissionError(f"Daily tool call quota exceeded for user {user_id}")

    # Per-tool rate limit
    rate_key = f"rate:user:{user_id}:tool:{tool_name}:minute"
    rate_count = await redis.incr(rate_key)
    await redis.expire(rate_key, 60)

    tool_limits = {
        "query_analytics": 60,
        "run_code": 10,
        "send_email": 5,
    }
    limit = tool_limits.get(tool_name, 100)
    if rate_count > limit:
        raise PermissionError(
            f"Rate limit exceeded: {tool_name} allows {limit} calls/minute"
        )

    return await call_next(message)
```

---

## 12. Ecosystem

### Scale

As of July 2026:

- **19,831+ MCP servers** indexed across public registries
- **97 million monthly SDK downloads** (Python + TypeScript combined)
- Supported by all major AI hosts: Claude, Claude Code, Cursor, Windsurf, Zed, Continue, and others

### Registries

| Registry | URL | Focus |
| ---------- | ----- | ------- |
| Glama | glama.ai/mcp | Quality-reviewed, curated |
| MCP.so | mcp.so | Community directory, searchable |
| npm (`@modelcontextprotocol/`) | npmjs.com | Official TypeScript servers |
| PyPI (`mcp-server-*`) | pypi.org | Official Python servers |

### Curated Server List (Development & Enterprise)

**Development:**

| Package | Install | Provides |
| --------- | --------- | --------- |
| `@modelcontextprotocol/server-github` | `npx` | GitHub repos, PRs, issues, actions |
| `@modelcontextprotocol/server-filesystem` | `npx` | Local file system (configurable roots) |
| `@modelcontextprotocol/server-git` | `npx` | Git operations |
| `mcp-server-docker` | `pip` | Docker container management |

**Data & Databases:**

| Package | Install | Provides |
| --------- | --------- | --------- |
| `@modelcontextprotocol/server-postgres` | `npx` | PostgreSQL queries |
| `@modelcontextprotocol/server-sqlite` | `npx` | SQLite |
| `mcp-server-bigquery` | `pip` | BigQuery |
| `mcp-server-snowflake` | `pip` | Snowflake |

**Productivity:**

| Package | Install | Provides |
| --------- | --------- | --------- |
| `@modelcontextprotocol/server-slack` | `npx` | Slack messages, channels, DMs |
| `mcp-server-jira` | `pip` | Jira tickets, sprints |
| `mcp-server-notion` | `pip` | Notion databases and pages |
| `@modelcontextprotocol/server-google-drive` | `npx` | Google Drive files |

---

## 13. MCP Inspector

The MCP Inspector is the official development and debugging tool for MCP servers. It provides a browser UI to test every primitive without writing client code.

### Launch

```bash
# Test a Python server
npx @modelcontextprotocol/inspector python -m my_mcp_server

# Test a TypeScript server (compiled)
npx @modelcontextprotocol/inspector node dist/server.js

# Test a server with environment variables
npx @modelcontextprotocol/inspector \
  --env DATABASE_URL=postgres://localhost/dev \
  --env HR_API_TOKEN=test-token \
  python -m company_mcp_server
```

### Inspector Capabilities

- **Tools tab** — list all registered tools, inspect their JSON schemas, call them with test inputs, view raw responses
- **Resources tab** — list and read all resources, view raw content and MIME type
- **Prompts tab** — list prompts, fill arguments, preview generated message content
- **History** — full JSON-RPC request/response log for every interaction
- **Protocol** — display the raw JSON-RPC messages (useful for debugging schema issues)

### Debugging Common Issues

```bash
# Server not loading tools → check Python import errors
npx @modelcontextprotocol/inspector python -m my_server 2>&1 | head -50

# Tool returns unexpected output → inspect raw response in History tab

# Auth errors on remote server → check Authorization header in Inspector settings

# Slow tool responses → check History tab for timing data

# Claude Code not seeing server → check /mcp command output in Claude Code
/mcp

# Enable verbose MCP protocol logging in Claude Code
CLAUDE_MCP_DEBUG=1 claude
```

---

## 14. Best Practices

1. **Write tool descriptions from the model's perspective** — the description is how the model decides whether to call the tool. Answer "when should I use this?" not just "what does this do?"

2. **Return structured JSON from tools** — the model reasons over structured data far more reliably than prose. Use consistent schemas with explicit field names and types.

3. **Separate reads from writes** — design read tools (queries, lookups) as clearly distinct from write tools (creates, updates, deletes). Never combine them in one tool with a flag parameter.

4. **Implement idempotency for write tools** — write tools must be safe to retry. Use database-level idempotency keys or upsert semantics. Document which tools are idempotent and which are not.

5. **Use Streamable HTTP for all new remote servers** — SSE is deprecated in the 2025-11-25 spec. All new remote server implementations must use Streamable HTTP.

6. **Design for statelessness from day one** — even if you do not deploy under the 2026-07-28 RC today, designing stateless servers means zero migration effort later. Externalise all state to Redis or Postgres.

7. **Implement OAuth 2.1 with PKCE on all HTTP servers** — this is mandated by the 2025-11-25 spec. Bearer token-only authentication without OAuth is a compliance violation for new servers.

8. **Propagate W3C Trace Context** — extract `traceparent` from `_meta` on every request and inject it into downstream HTTP calls. This is essential for diagnosing multi-hop failures in production.

9. **Cap tool result size** — return at most 10,000–50,000 characters from any tool call. Large responses fill the context window and leave no room for reasoning. Paginate or summarise large datasets.

10. **Set a maximum connection and request timeout** — HTTP servers must set a request timeout (e.g., 30 seconds) to prevent slow client connections from exhausting server resources.

11. **Test with MCP Inspector before deploying** — validate every tool, resource, and prompt manually in the Inspector before writing client integration code. This catches schema errors early.

12. **Version your server and maintain a deprecation log** — the 2026-07-28 RC formalises deprecation policy. Follow it: mark deprecated tools with `deprecated_since`, keep them for 12+ months, log changes in a CHANGELOG.

---

## 15. Antipatterns

1. **Using SSE for new remote servers** — SSE is deprecated in the 2025-11-25 spec. New servers must use Streamable HTTP. Existing SSE servers should migrate.

2. **Returning large unstructured blobs from tools** — a tool that returns 100KB of raw log text gives the model nothing to reason over and wastes context tokens. Structure results; truncate or summarise large outputs.

3. **Not implementing idempotency for write tools** — if a network blip causes a retry, a non-idempotent write tool (e.g., `send_email`) will execute twice. Use idempotency keys.

4. **Skipping input validation at tool boundaries** — tool arguments come from an AI model, not a type-safe calling convention. Validate every argument: type, length, format, and value range. Never trust the model to send valid inputs.

5. **Exposing all tools to all users** — capability scoping is a security requirement, not an optimisation. Use dynamic tool lists based on authenticated identity and OAuth scopes.

6. **Storing session state in the MCP server process** — this breaks horizontal scaling and violates the stateless requirement in the 2026-07-28 RC. All state must be in an external shared store.

7. **Long-running synchronous operations in tool handlers** — a tool that runs for 5 minutes blocks the event loop (or the HTTP connection). Use the Tasks extension for long-running work.

8. **Not logging tool calls for audit** — in regulated industries, every tool invocation is an auditable event. If you cannot reconstruct "what did the AI do with this user's data?", you have a compliance gap.

9. **Not implementing OAuth 2.1 for remote HTTP servers** — bearer-token-only authentication without OAuth is a spec violation for HTTP servers under the 2025-11-25 spec and exposes your server to CSRF and token theft.

10. **Writing tool descriptions that say "what" but not "when"** — "This tool queries the database" is insufficient. The model needs "Use when asked about user counts, revenue, or event metrics" to make correct tool selection decisions.

11. **Returning Python exceptions as raw exception text** — catching `Exception` and returning `str(e)` may expose internal stack traces, database connection strings, or file paths to the model context. Return structured error objects with safe, user-facing messages.

12. **Building a monolithic server with 50+ tools** — a server with too many tools forces the model to reason over a large tool list, increasing the chance of incorrect selection. Split large tool sets into domain-specific servers.

---

## 16. Guardrails

### Input Validation at Tool Boundaries

```python
import re
from typing import Any

def validate_sql(sql: str) -> str:
    """Validate and sanitise an SQL query before execution."""
    sql = sql.strip()
    if len(sql) > 10_000:
        raise ValueError("SQL exceeds 10,000 character limit")
    if not sql.upper().startswith("SELECT"):
        raise ValueError("Only SELECT statements are permitted")
    # Block dangerous patterns
    BLOCKED = [r"\bDROP\b", r"\bDELETE\b", r"\bTRUNCATE\b", r"\bUPDATE\b",
               r"\bINSERT\b", r"\bEXEC\b", r"\bxp_\w+", r"--", r"/\*"]
    for pattern in BLOCKED:
        if re.search(pattern, sql, re.IGNORECASE):
            raise ValueError(f"SQL contains blocked pattern: {pattern}")
    return sql

def validate_url(url: str) -> str:
    """Validate a URL before fetching."""
    import ipaddress
    from urllib.parse import urlparse
    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https"):
        raise ValueError(f"Only http/https URLs are permitted, got: {parsed.scheme}")
    host = parsed.hostname or ""
    # Block SSRF: internal IP ranges
    try:
        ip = ipaddress.ip_address(host)
        if ip.is_private or ip.is_loopback or ip.is_link_local:
            raise ValueError(f"Requests to private IP ranges are blocked: {host}")
    except ValueError:
        pass  # Not an IP — hostname is OK
    # Block known internal hostnames
    BLOCKED_HOSTS = {"localhost", "metadata.google.internal", "169.254.169.254"}
    if host.lower() in BLOCKED_HOSTS:
        raise ValueError(f"Requests to host {host!r} are blocked")
    return url
```

### Output Sanitisation

```python
import bleach

def sanitise_html_output(raw_html: str) -> str:
    """Strip dangerous HTML from tool output before returning to client."""
    allowed_tags = ["p", "br", "b", "i", "ul", "ol", "li", "table", "tr", "td", "th", "pre", "code"]
    allowed_attrs = {"*": ["class"]}
    return bleach.clean(raw_html, tags=allowed_tags, attributes=allowed_attrs, strip=True)

def redact_secrets(text: str) -> str:
    """Redact secret-like values from tool output."""
    patterns = [
        (r"(?i)(api[_-]?key|token|secret|password|apikey)\s*[:=]\s*['\"]?([A-Za-z0-9+/=._-]{16,})['\"]?",
         r"\1: ***REDACTED***"),
        (r"(?i)(Bearer\s+)([A-Za-z0-9._-]{20,})", r"\1***REDACTED***"),
        (r"postgresql://[^@]+@", "postgresql://***REDACTED***@"),
    ]
    for pattern, replacement in patterns:
        text = re.sub(pattern, replacement, text)
    return text
```

---

## 17. Governance

### Who Can Install MCP Servers

| Context | Governance Model |
| --------- | ----------------- |
| Individual developer (Claude Code personal) | Self-serve; user accepts responsibility |
| Team (Claude Code Teams) | Team admin approves server additions |
| Enterprise (Claude for Enterprise) | Central IT/Security allow-list; IdP group assignment |
| CI/CD pipelines | Platform team controls; pinned server versions only |

**Recommended enterprise approval process:**

1. Developer or team proposes a new MCP server (GitHub PR to central config repo)
2. Security review: validate the server's code, permissions requested, and data access scope
3. IT admin adds to group allow-list in Okta/Entra ID assignment
4. Monitoring: all tool calls from this server flow to the enterprise audit log
5. Quarterly access review: remove unused servers and over-permissioned scopes

### Audit Trails

A complete MCP audit trail must capture:

- **Who** — authenticated user identity (from OAuth JWT `sub` or `email` claim)
- **When** — UTC timestamp with millisecond precision
- **What** — tool name and redacted arguments
- **Which server** — MCP server name and version
- **Outcome** — success/failure, error type if failed
- **Duration** — end-to-end latency in milliseconds
- **Trace ID** — W3C `traceparent` for cross-system correlation

### Versioning Policy

Follow the MCP 2026-07-28 RC deprecation policy for your own servers:

```python
# Annotate deprecated tools
@mcp.tool(deprecated_since="2026-06-01", replacement="query_analytics_v2")
async def query_analytics(sql: str) -> list[dict]:
    """DEPRECATED: Use query_analytics_v2 instead. Removed after 2027-06-01."""
    return await _query_analytics_impl(sql)

@mcp.tool()
async def query_analytics_v2(
    sql: str,
    timeout_ms: int = 5000,
    max_rows: int = 1000,
) -> dict:
    """
    Query the analytics database. Enhanced version with timeout and row limit controls.
    Use when asked about user counts, revenue, or event data.
    """
    ...
```

---

## 18. Performance

### Caching Strategy with ttlMs

Design your tool list for caching. Tools whose definitions do not change frequently should declare a long `ttlMs` (and `global` scope) so clients do not re-fetch on every session.

```python
# Static lookup tools → long global TTL
@mcp.tool(cache={"ttl_ms": 3_600_000, "scope": "global"})  # 1 hour
async def get_supported_currencies() -> list[str]:
    """List all supported currency codes. Use when validating currency inputs."""
    return await forex_api.get_supported_currencies()

# User-specific data → short session TTL
@mcp.tool(cache={"ttl_ms": 60_000, "scope": "session"})  # 1 minute, per session
async def get_my_permissions() -> list[str]:
    """List the permissions of the currently authenticated user."""
    return await auth_service.get_user_permissions(ctx.auth.user_id)

# Real-time data → no caching
@mcp.tool()
async def get_current_price(symbol: str) -> dict:
    """Get the live stock price for a ticker symbol."""
    return await market_data.get_price(symbol)
```

### Connection Pooling for stdio

For stdio servers that connect to databases, create the connection pool at server startup, not per-request:

```python
import asyncpg
from fastmcp import FastMCP

mcp = FastMCP("analytics-server")
_pool: asyncpg.Pool | None = None

async def get_pool() -> asyncpg.Pool:
    global _pool
    if _pool is None:
        _pool = await asyncpg.create_pool(
            dsn=os.environ["DATABASE_URL"],
            min_size=2,
            max_size=10,
            command_timeout=30,
        )
    return _pool

@mcp.tool()
async def query(sql: str) -> list[dict]:
    """Execute a read-only query."""
    pool = await get_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch(sql + " LIMIT 1000")
        return [dict(r) for r in rows]

# Cleanup on shutdown
import atexit

async def shutdown():
    if _pool:
        await _pool.close()
```

### Load Balancing for HTTP Servers

With stateless MCP (2026-07-28 RC), HTTP servers scale horizontally behind a standard load balancer:

```nginx
# nginx.conf — stateless MCP server cluster
upstream mcp_cluster {
    server mcp-server-1:3000;
    server mcp-server-2:3000;
    server mcp-server-3:3000;
    # Round-robin by default — no sticky sessions needed
}

server {
    listen 443 ssl;
    server_name mcp.company.internal;

    location /mcp {
        proxy_pass http://mcp_cluster;
        proxy_set_header Mcp-Method $http_mcp_method;  # Preserve routing header
        proxy_set_header Authorization $http_authorization;
        proxy_set_header traceparent $http_traceparent;  # Propagate trace context
        proxy_read_timeout 60s;
        proxy_connect_timeout 5s;
    }
}
```

---

## 19. Testing MCP Servers

### Unit Tests

```python
import pytest
import pytest_asyncio
from fastmcp.testing import MCPTestClient

@pytest.fixture
async def client():
    """Create an in-process test client — no network, no subprocess."""
    return MCPTestClient(mcp)  # mcp is the FastMCP instance

async def test_query_analytics_select_only(client):
    result = await client.call_tool("query_analytics", {"sql": "SELECT count(*) FROM users"})
    assert isinstance(result, list)
    assert len(result) >= 0

async def test_query_analytics_blocks_delete(client):
    result = await client.call_tool(
        "query_analytics",
        {"sql": "DELETE FROM users WHERE id = 1"},
    )
    assert "error" in result[0] or "Only SELECT" in str(result)

async def test_get_employee_info_invalid_format(client):
    result = await client.call_tool("get_employee_info", {"employee_id": "INVALID"})
    assert "error" in result
    assert "Invalid employee ID format" in result["error"]

async def test_resource_org_chart(client):
    content = await client.read_resource("hr://org-chart")
    data = json.loads(content)
    assert "employees" in data or "nodes" in data  # Validate structure

async def test_prompt_onboarding_checklist(client):
    result = await client.get_prompt("onboarding_checklist", {
        "role": "Senior Backend Engineer",
        "start_date": "2026-08-01",
    })
    assert "30" in result
    assert "60" in result
    assert "90" in result
```

### Integration Tests with Claude

```python
import anthropic

async def test_tool_selection():
    """Verify Claude selects the correct tool for a given user query."""
    ac = anthropic.Anthropic()

    # Fetch tool definitions from the running MCP server
    async with MCPTestClient(mcp) as client:
        tools = await client.list_tools_as_anthropic_format()

    response = ac.messages.create(
        model="claude-haiku-4-5",
        max_tokens=256,
        tools=tools,
        messages=[{
            "role": "user",
            "content": "How many active users do we have?",
        }],
    )

    # Claude must call query_analytics for this question
    tool_uses = [b for b in response.content if b.type == "tool_use"]
    assert len(tool_uses) >= 1
    assert tool_uses[0].name == "query_analytics"
    assert "SELECT" in tool_uses[0].input.get("sql", "").upper()

async def test_tool_result_is_usable():
    """Verify Claude can reason over the tool's return value."""
    ac = anthropic.Anthropic()

    async with MCPTestClient(mcp) as client:
        tools = await client.list_tools_as_anthropic_format()

    response = ac.messages.create(
        model="claude-haiku-4-5",
        max_tokens=512,
        tools=tools,
        messages=[{
            "role": "user",
            "content": "What department does employee E001 work in?",
        }],
    )

    tool_call = next(b for b in response.content if b.type == "tool_use")
    assert tool_call.name == "get_employee_info"
    assert tool_call.input.get("employee_id") == "E001"
```

### Stress Testing

```python
import asyncio, statistics, time
from fastmcp.testing import MCPTestClient

async def stress_test_tool(tool_name: str, arguments: dict, n: int = 200, concurrency: int = 20):
    semaphore = asyncio.Semaphore(concurrency)
    latencies = []
    errors = []

    async def single_call(i: int):
        async with semaphore:
            async with MCPTestClient(mcp) as client:
                start = time.monotonic()
                try:
                    await client.call_tool(tool_name, arguments)
                    latencies.append((time.monotonic() - start) * 1000)
                except Exception as e:
                    errors.append({"index": i, "error": str(e)})

    await asyncio.gather(*[single_call(i) for i in range(n)])

    return {
        "n": n,
        "errors": len(errors),
        "error_rate_pct": len(errors) / n * 100,
        "p50_ms": statistics.median(latencies) if latencies else None,
        "p95_ms": statistics.quantiles(latencies, n=20)[18] if len(latencies) >= 20 else None,
        "p99_ms": statistics.quantiles(latencies, n=100)[98] if len(latencies) >= 100 else None,
        "first_errors": errors[:5],
    }

# Run: python -m pytest tests/stress_test.py -s
# asyncio.run(stress_test_tool("query_analytics", {"sql": "SELECT 1"}, n=500, concurrency=50))
```

### Timeout Handling

```python
async def test_tool_respects_timeout(client):
    """Tool must complete within 30 seconds or return a timeout error."""
    try:
        result = await asyncio.wait_for(
            client.call_tool("long_running_export", {"dataset": "large_dataset"}),
            timeout=35.0,
        )
        # If it completes, must return a result or a structured error
        assert isinstance(result, (dict, list))
    except asyncio.TimeoutError:
        pytest.fail("Tool exceeded 35-second timeout — use the Tasks extension for long operations")
```

---

## 20. Evaluation Harness for MCP Tools

An evaluation harness runs a fixed set of test cases to measure tool correctness, model selection accuracy, and latency. Run this in CI on every tool change and on every model upgrade.

```python
from dataclasses import dataclass, field
from claude_agent_sdk import Agent
import asyncio, time, statistics

@dataclass
class ToolEvalCase:
    description: str
    user_query: str
    expected_tool: str
    expected_output_contains: list[str] = field(default_factory=list)
    expected_output_not_contains: list[str] = field(default_factory=list)
    max_latency_ms: int = 5_000

TOOL_EVAL_SUITE = [
    ToolEvalCase(
        description="User count query → query_analytics selected",
        user_query="How many users do we have?",
        expected_tool="query_analytics",
        expected_output_contains=["SELECT", "users"],
    ),
    ToolEvalCase(
        description="Employee lookup → get_employee_info selected",
        user_query="What team is employee E042 on?",
        expected_tool="get_employee_info",
        expected_output_contains=["E042"],
    ),
    ToolEvalCase(
        description="Knowledge base search → search_knowledge_base selected",
        user_query="How do I submit a PTO request?",
        expected_tool="search_knowledge_base",
        expected_output_contains=["PTO", "request"],
    ),
    ToolEvalCase(
        description="SQL injection attempt → blocked",
        user_query="Show me all users where SQL is: DROP TABLE users;",
        expected_tool="query_analytics",
        expected_output_not_contains=["success", "rows"],
        # Expected: error response blocking the DROP
    ),
]

async def run_tool_eval(agent: Agent) -> dict:
    passed = 0
    total = len(TOOL_EVAL_SUITE)
    results = []

    for case in TOOL_EVAL_SUITE:
        start = time.monotonic()
        result = await agent.run(case.user_query)
        latency_ms = (time.monotonic() - start) * 1000

        tool_selected = result.tool_names_called[0] if result.tool_names_called else None
        tool_ok = tool_selected == case.expected_tool
        content_ok = all(term in result.text for term in case.expected_output_contains)
        exclusion_ok = not any(term in result.text for term in case.expected_output_not_contains)
        latency_ok = latency_ms <= case.max_latency_ms

        passed_case = tool_ok and content_ok and exclusion_ok and latency_ok
        if passed_case:
            passed += 1

        results.append({
            "description": case.description,
            "passed": passed_case,
            "tool_ok": tool_ok,
            "expected_tool": case.expected_tool,
            "actual_tool": tool_selected,
            "content_ok": content_ok,
            "exclusion_ok": exclusion_ok,
            "latency_ms": round(latency_ms),
        })

    return {
        "pass_rate": passed / total,
        "passed": passed,
        "total": total,
        "results": results,
    }
```

**Latency benchmarks:**

| Tool Type | Expected p50 | Expected p95 | Alert if |
| ----------- | ------------- | ------------- | --------- |
| Sync DB query | less than 200ms | less than 800ms | p95 greater than 2s |
| External API call | less than 500ms | less than 2,000ms | p95 greater than 5s |
| Vector search | less than 300ms | less than 1,000ms | p95 greater than 3s |
| Code execution | less than 5,000ms | less than 15,000ms | p95 greater than 25s |
| Long-running (Task) | N/A (async) | N/A (async) | Task queue greater than 10 |

---

## Quick Reference: MCP Debugging Checklist

```bash
# 1. Inspect the server directly
npx @modelcontextprotocol/inspector python -m my_mcp_server

# 2. Check Claude Code server status
/mcp

# 3. View server process logs
tail -f ~/.claude/logs/mcp-*.log

# 4. Enable protocol-level debug logging
CLAUDE_MCP_DEBUG=1 claude

# 5. Test a specific tool via curl (Streamable HTTP servers)
curl -X POST https://mcp.company.internal/mcp \
  -H "Content-Type: application/json" \
  -H "Mcp-Method: tools/call" \
  -H "Authorization: Bearer $MCP_TOKEN" \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"get_employee_info","arguments":{"employee_id":"E001"}}}'
```

**Common issues and fixes:**

| Symptom | Likely Cause | Fix |
| --------- | ------------- | ----- |
| Server not appearing in `/mcp` | `command` path not on PATH | Use absolute path in `mcpServers` config |
| Tool calls failing silently | Server process crashing | Check `~/.claude/logs/mcp-*.log` |
| Auth errors on remote server | Token expired or missing | Refresh token; check `Authorization` header in Inspector |
| Slow tool responses | No connection pooling | Create pool at startup; see §18 |
| JSON-RPC parse errors | Server writing non-JSON to stdout | Redirect all logging to stderr; only protocol messages to stdout |
| `tools/list` returns empty | `@mcp.tool()` not imported | Ensure all tool modules are imported before `mcp.run()` |
