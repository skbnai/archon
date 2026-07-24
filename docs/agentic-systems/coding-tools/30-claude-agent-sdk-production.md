---
title: "Claude Agent SDK — Production Reference"
domain: agentic-systems
doc_type: guide
status: current
date_created: 2026-07-24
last_reviewed: 2026-07-24
topic_id: claude-agent-sdk-production
supersedes:
  - ../knowledge-docs/docs/coding-tools/claude/claude-agent-sdk-production.md
---

# Claude Agent SDK — Production Reference

Zero-to-mastery guide for building production multi-agent systems with the Claude Agent SDK. Covers architecture decisions, every major pattern, cost controls, observability, guardrails, and responsible AI considerations.

:::note Naming history
    The Claude Agent SDK was renamed from "Claude Code SDK" in September 2025. All package names and imports in this guide reflect the current name.

---

## 1. Overview

### What the Agent SDK Is

The Claude Agent SDK is a library that runs **in your own process** and provides a structured runtime for multi-turn, tool-using, multi-agent applications built on top of the Claude Messages API. It handles the agentic loop (calling tools, processing results, continuing the conversation), session persistence, subagent spawning, and lifecycle management — without you writing that scaffolding manually.

The SDK is distinct from the raw Messages API (which you manage entirely) and from Managed Agents (a hosted REST API product where Anthropic runs the sandbox). For a model pricing reference, see [Claude Models 2026](claude-models-2026.md). For enterprise cloud deployment across AWS/GCP/Azure, see [Claude Enterprise Deployment 2026](claude-enterprise-2026.md). For MCP server development and the MCP protocol deep-dive, see [MCP Deep Guide](mcp-deep-guide.md).

### Agent SDK vs Managed Agents — Decision Matrix

| Criterion | Agent SDK | Managed Agents |
| ----------- | ----------- | ---------------- |
| **Where it runs** | Your infrastructure | Anthropic-hosted sandbox |
| **Integration style** | Python/TypeScript library | REST API calls |
| **Data residency** | Stays in your environment | Processed in Anthropic's sandbox |
| **Customisation** | Full control over tools, prompts, storage | Fixed runtime, tool allowlist |
| **Session storage** | Your Postgres/Redis | Managed automatically |
| **Billing** | Token-based (Messages API pricing) | Agent SDK credits (see §19) |
| **Network isolation** | VPC/private — no outbound required | Public HTTPS to Anthropic endpoints |
| **Best for** | Complex custom workflows, data-sensitive tasks | Rapid prototyping, light integration |

**Choose Agent SDK when:**

- Your data must not leave your infrastructure
- You need custom tools, custom state stores, or custom cost controls
- You are building multi-tenant SaaS with per-customer billing isolation
- You need circuit breakers, custom retry logic, or partial-result recovery

**Choose Managed Agents when:**

- You want zero infrastructure overhead
- You are prototyping or building internal tools with standard capability sets
- You are integrating Claude into a product that already uses Anthropic's REST APIs

### SDK vs Raw Messages API

| Capability | Raw Messages API | Agent SDK |
| ------------ | ----------------- | ----------- |
| Tool execution loop | You write it | Built-in |
| Subagent spawning | Manual | `agent.spawn_subagent()` |
| Session persistence | You manage | Automatic |
| Memory | You implement | Managed provider interface |
| Retry / backoff | You implement | Configurable `RetryConfig` |
| Cost / token budgets | You track | Built-in `CostLimit` |
| HITL checkpoints | You implement | Built-in `HumanCheckpoint` |
| MCP client | You wire up | Built-in MCP transport |

---

## 2. Installation & Setup

### Prerequisites

- Python 3.10+ (Agent SDK uses `asyncio`, `typing.TypeAlias`, and `match` statements)
- Node.js 18+ for TypeScript (uses native `fetch`, `ReadableStream`)
- `ANTHROPIC_API_KEY` set in your environment

=== "Python"

    ```bash
    pip install claude-agent-sdk
    ```

    Pin to a specific version in production:

    ```bash
    pip install "claude-agent-sdk==0.8.1"
    ```

=== "TypeScript"

    ```bash
    npm install @anthropic-ai/claude-agent-sdk
    ```

    ```bash
    # or with yarn/pnpm
    yarn add @anthropic-ai/claude-agent-sdk
    pnpm add @anthropic-ai/claude-agent-sdk
    ```

### Environment Configuration

=== "Python"

    ```python
    import os
    from claude_agent_sdk import Agent

    # The SDK reads ANTHROPIC_API_KEY automatically
    # Never hardcode keys — use a secrets manager or environment injection
    assert os.environ.get("ANTHROPIC_API_KEY"), "ANTHROPIC_API_KEY must be set"

    agent = Agent(
        model="claude-sonnet-4-6",
        system="You are a senior data analyst. Be precise and cite sources.",
        max_tokens=8192,
    )
    ```

=== "TypeScript"

    ```typescript
    import { Agent } from "@anthropic-ai/claude-agent-sdk";

    // SDK reads process.env.ANTHROPIC_API_KEY automatically
    const agent = new Agent({
      model: "claude-sonnet-4-6",
      system: "You are a senior data analyst. Be precise and cite sources.",
      maxTokens: 8192,
    });
    ```

:::danger Never hardcode API keys
    Store `ANTHROPIC_API_KEY` in AWS Secrets Manager, HashiCorp Vault, or a `.env` file excluded from version control. Rotate on a 90-day schedule. Audit access logs for unexpected usage.

---

## 3. Core Concepts

### Agent

An `Agent` is a configured instance that wraps a Claude model with a system prompt, a tool set, and runtime policies (retry, cost limits, checkpoints). Agents are long-lived objects — create one per role or responsibility, not one per request.

### Session

A `Session` is a stateful conversation thread. Sessions persist context (message history, tool results, memory) across multiple turns and HTTP requests. Sessions have IDs you control; they can be resumed from any process instance as long as they share the same state store.

### Tool

A `Tool` is a callable function the agent can invoke during its reasoning loop. Tools are the agent's interface to the outside world — databases, APIs, file systems, external services. The SDK handles the serialisation/deserialisation and result injection automatically.

### Subagent

A subagent is a child agent spawned by a parent. Subagents run in isolated context windows and can use their own tool sets and models. Results are aggregated back to the parent. Subagents enable fan-out parallelism and responsibility separation.

### Skill

A skill is a reusable capability described in a `SKILL.md` file placed in `.agents/skills/`. The SDK auto-discovers skill files at startup. The model reads skill descriptions and invokes them by name when appropriate — no manual wiring required.

---

## 4. Quick Start

=== "Python"

    ```python
    import asyncio
    from claude_agent_sdk import Agent, tool

    @tool(description="Look up a product's current price. Use when asked about pricing.")
    async def get_price(product_id: str) -> dict:
        # Replace with your real data source
        prices = {"SKU-001": 29.99, "SKU-002": 49.99, "SKU-003": 9.99}
        price = prices.get(product_id)
        if price is None:
            return {"error": f"Product {product_id} not found"}
        return {"product_id": product_id, "price_usd": price, "currency": "USD"}

    agent = Agent(
        model="claude-sonnet-4-6",
        tools=[get_price],
        system="You are a helpful product pricing assistant.",
        max_tokens=4096,
    )

    async def main():
        result = await agent.run("What is the price of SKU-001 and SKU-003?")
        print(result.text)

    asyncio.run(main())
    ```

=== "TypeScript"

    ```typescript
    import { Agent, tool } from "@anthropic-ai/claude-agent-sdk";

    const getPrice = tool({
      name: "get_price",
      description: "Look up a product's current price. Use when asked about pricing.",
      parameters: {
        type: "object",
        properties: {
          productId: { type: "string", description: "The product SKU" },
        },
        required: ["productId"],
      },
      execute: async ({ productId }: { productId: string }) => {
        const prices: Record&lt;string, number&gt; = {
          "SKU-001": 29.99,
          "SKU-002": 49.99,
          "SKU-003": 9.99,
        };
        const price = prices[productId];
        if (price === undefined) {
          return { error: `Product ${productId} not found` };
        }
        return { productId, priceUsd: price, currency: "USD" };
      },
    });

    const agent = new Agent({
      model: "claude-sonnet-4-6",
      tools: [getPrice],
      system: "You are a helpful product pricing assistant.",
      maxTokens: 4096,
    });

    const result = await agent.run("What is the price of SKU-001 and SKU-003?");
    console.log(result.text);
    ```

---

## 5. Tool Use

### Custom Tool Definition

=== "Python"

    ```python
    from claude_agent_sdk import tool
    from pathlib import Path

    @tool(
        description=(
            "Query the analytics database. Use for revenue, user counts, and "
            "event data. Accepts read-only SQL SELECT queries only."
        )
    )
    async def query_analytics(
        sql: str,
        database: str = "production",
    ) -> list[dict]:
        """
        sql: A SQL SELECT statement. Must not modify data.
        database: Target database — 'production' or 'staging'.
        """
        if not sql.strip().upper().startswith("SELECT"):
            raise ValueError("Only SELECT queries are permitted")
        async with db_pool.acquire() as conn:
            rows = await conn.fetch(sql)
            return [dict(r) for r in rows]
    ```

=== "TypeScript"

    ```typescript
    import { tool } from "@anthropic-ai/claude-agent-sdk";

    const queryAnalytics = tool({
      name: "query_analytics",
      description:
        "Query the analytics database. Use for revenue, user counts, and event data. "
        + "Accepts read-only SQL SELECT queries only.",
      parameters: {
        type: "object",
        properties: {
          sql: { type: "string", description: "A SQL SELECT statement" },
          database: {
            type: "string",
            enum: ["production", "staging"],
            description: "Target database",
            default: "production",
          },
        },
        required: ["sql"],
      },
      execute: async ({ sql, database = "production" }) => {
        if (!sql.trim().toUpperCase().startsWith("SELECT")) {
          throw new Error("Only SELECT queries are permitted");
        }
        return await db.query(sql, database);
      },
    });
    ```

### Tool Security Boundaries

Always sandbox tool access. Path traversal, SQL injection, and command injection are the most common attack vectors against agentic systems.

```python
from pathlib import Path

@tool(description="Read file contents from the project sandbox directory")
async def read_file(path: str) -> str:
    base = Path("/var/projects/sandbox").resolve()
    target = (base / path).resolve()
    if not str(target).startswith(str(base)):
        raise ValueError(f"Path traversal attempt blocked: {path!r}")
    if not target.is_file():
        raise FileNotFoundError(f"File not found: {path!r}")
    return target.read_text(encoding="utf-8")


@tool(description="Execute a shell command in the project sandbox")
async def run_command(command: str) -> dict:
    BLOCKED_PATTERNS = ["rm -rf", "sudo", "curl", "wget", "&gt; /dev/sd", "mkfs"]
    for pattern in BLOCKED_PATTERNS:
        if pattern in command:
            raise ValueError(f"Blocked command pattern: {pattern!r}")
    proc = await asyncio.create_subprocess_shell(
        command,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
        cwd="/var/projects/sandbox",
        env={"PATH": "/usr/bin:/bin"},  # Minimal environment
    )
    stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=30.0)
    return {
        "exit_code": proc.returncode,
        "stdout": stdout.decode()[:10_000],  # Truncate to 10K chars
        "stderr": stderr.decode()[:2_000],
    }
```

### Built-In Tools

The Agent SDK ships with eight built-in tools you can enable by name:

| Built-in Tool | Description | Governance Note |
| --------------- | ------------- | ----------------- |
| `file_editor` | Read, write, edit files | Require HITL for writes outside sandbox |
| `bash` | Execute shell commands | Block network access; apply allow-list |
| `web_search` | Search the web | Log queries; apply content filtering |
| `web_fetch` | Fetch a URL | Block internal IP ranges; rate-limit |
| `human_checkpoint` | Pause for human approval | Use for all irreversible actions |
| `spawn_subagent` | Create a child agent | Set concurrency limits |
| `session_manager` | Load/save session state | Requires configured state store |
| `mcp_client` | Connect to MCP servers | Apply per-server allow-lists |

```python
from claude_agent_sdk import Agent, BuiltinTools

agent = Agent(
    model="claude-sonnet-4-6",
    builtin_tools=[
        BuiltinTools.WEB_SEARCH,
        BuiltinTools.WEB_FETCH,
        BuiltinTools.FILE_EDITOR,
    ],
    system="You are a research assistant. Search the web and synthesize findings.",
)
```

### Human-in-the-Loop Checkpoints

HITL checkpoints are built into the SDK and pause agent execution pending human approval. Use them for any action that is irreversible, high-cost, or externally visible.

```python
from claude_agent_sdk import Agent, HumanCheckpoint, CheckpointResult

agent = Agent(
    model="claude-sonnet-4-6",
    tools=[deploy_tool, send_email_tool, delete_records_tool],
    checkpoints=[
        HumanCheckpoint(
            trigger="before_tool_call",
            tool_names=["deploy_tool", "delete_records_tool"],
            prompt_template=(
                "Agent wants to call `{tool_name}` with arguments:\n"
                "```json\n{arguments}\n```\n"
                "Approve? (yes/no/modify)"
            ),
            timeout_seconds=300,   # 5-minute approval window
            on_timeout="reject",   # Reject if no response
        ),
        HumanCheckpoint(
            trigger="before_tool_call",
            tool_names=["send_email_tool"],
            prompt_template="Agent wants to send an email to {to}. Preview:\n{body}\nApprove?",
            timeout_seconds=120,
        ),
    ],
)

async def run_with_approval(prompt: str, approver_channel):
    async def approval_handler(checkpoint_event):
        # Send the approval request to a Slack channel, UI, or webhook
        await approver_channel.send(checkpoint_event.prompt)
        response = await approver_channel.wait_for_response(
            timeout=checkpoint_event.timeout_seconds
        )
        if response.text.lower() == "yes":
            return CheckpointResult.APPROVE
        elif response.text.lower().startswith("modify"):
            return CheckpointResult.modify(response.modified_args)
        return CheckpointResult.REJECT

    result = await agent.run(prompt, checkpoint_handler=approval_handler)
    return result
```

:::warning HITL is not optional for production
    Any agent action that modifies external state — sending emails, writing to databases, calling payment APIs, deploying code — must have a HITL checkpoint or be designed to be fully reversible. Document which actions are covered and which are not in your system design.

---

## 6. Multi-Agent Patterns

### Fan-Out Parallelism (Map-Reduce)

Distribute independent work across concurrent subagents, then aggregate results.

```python
import asyncio
from claude_agent_sdk import Agent

# Specialised analyst agent (uses cheaper model for sub-tasks)
analyst = Agent(
    model="claude-haiku-4-5",  # Cost-efficient for parallel sub-tasks
    tools=[query_analytics, format_report],
    system="You are a regional sales analyst. Analyse the data provided and return structured JSON.",
    max_tokens=2048,
)

# Orchestrating agent
orchestrator = Agent(
    model="claude-sonnet-4-6",
    system="You synthesise regional reports into executive summaries.",
    max_tokens=8192,
)

async def analyse_all_regions(regions: list[str], quarter: str) -> str:
    # MAP: spawn one subagent per region in parallel
    tasks = [
        analyst.run(
            f"Analyse sales performance for region '{region}' in {quarter}. "
            "Return JSON with: total_revenue, growth_pct, top_3_products, anomalies."
        )
        for region in regions
    ]

    # Collect with bounded concurrency to avoid rate limits
    semaphore = asyncio.Semaphore(5)  # Max 5 concurrent API calls

    async def bounded_run(task):
        async with semaphore:
            return await task

    regional_results = await asyncio.gather(*[bounded_run(t) for t in tasks])

    # REDUCE: orchestrator synthesises
    summary_prompt = (
        f"Synthesise these {len(regions)} regional reports for {quarter} into a "
        "CEO-level executive summary with key insights and recommended actions:\n\n"
        + "\n\n---\n\n".join(
            f"**{region}**:\n{result.text}"
            for region, result in zip(regions, regional_results)
        )
    )
    summary = await orchestrator.run(summary_prompt)
    return summary.text


# Usage
regions = ["APAC", "EMEA", "AMER-North", "AMER-South", "MEA"]
report = asyncio.run(analyse_all_regions(regions, "Q2-2026"))
```

### DAG Orchestration

When tasks have dependencies, model them as a directed acyclic graph (DAG). Each stage consumes outputs from prior stages.

```python
import asyncio
from claude_agent_sdk import Agent
from dataclasses import dataclass

@dataclass
class PipelineResult:
    research: str
    critique: str
    recommendations: str
    final_report: str

# Each agent is specialised for its stage
research_agent = Agent(
    model="claude-sonnet-4-6",
    tools=[web_search, web_fetch, read_file],
    system="You are a researcher. Find facts, cite sources, and summarise findings.",
)
critique_agent = Agent(
    model="claude-sonnet-4-6",
    system="You are a critical reviewer. Identify gaps, biases, and unsupported claims.",
)
strategy_agent = Agent(
    model="claude-sonnet-4-6",
    system="You are a strategy consultant. Turn research and critique into actionable recommendations.",
)
writer_agent = Agent(
    model="claude-fable",  # Creative, polished prose
    system="You are a technical writer. Produce clear, compelling executive reports.",
)

async def research_pipeline(topic: str) -> PipelineResult:
    # Stage 1 — Research (no dependencies)
    research_result = await research_agent.run(
        f"Research '{topic}': gather key facts, statistics, and primary sources."
    )

    # Stage 2 — Critique (depends on Stage 1)
    critique_result = await critique_agent.run(
        f"Critically review this research on '{topic}':\n\n{research_result.text}\n\n"
        "Identify: gaps, unsupported claims, alternative interpretations, missing data."
    )

    # Stage 3 — Recommendations (depends on Stages 1 + 2, can run after Stage 2)
    recommendations_result = await strategy_agent.run(
        f"Topic: {topic}\n\nResearch:\n{research_result.text}\n\n"
        f"Critique:\n{critique_result.text}\n\n"
        "Produce 5 specific, evidence-backed strategic recommendations."
    )

    # Stage 4 — Final report (depends on all prior stages)
    final_result = await writer_agent.run(
        f"Write an executive report on '{topic}' incorporating:\n\n"
        f"Research: {research_result.text}\n\n"
        f"Critique: {critique_result.text}\n\n"
        f"Recommendations: {recommendations_result.text}\n\n"
        "Format: executive summary (200 words), findings, analysis, recommendations, next steps."
    )

    return PipelineResult(
        research=research_result.text,
        critique=critique_result.text,
        recommendations=recommendations_result.text,
        final_report=final_result.text,
    )
```

### Adversarial Verification (Red Team + Blue Team)

Use a critic agent to challenge the primary agent's output. A synthesiser resolves conflicts and produces the most accurate result. This pattern is especially valuable for financial analysis, security assessments, and medical information.

```python
from claude_agent_sdk import Agent

analyst_agent = Agent(
    model="claude-sonnet-4-6",
    tools=[query_analytics, read_file],
    system=(
        "You are a senior financial analyst. Produce rigorous analysis backed by data. "
        "State confidence levels and acknowledge uncertainty."
    ),
)

critic_agent = Agent(
    model="claude-sonnet-4-6",
    system=(
        "You are an adversarial reviewer (red team). Your job is to find flaws: "
        "unsupported claims, logical errors, missing considerations, cherry-picked data, "
        "and alternative interpretations that contradict the analysis. Be thorough."
    ),
)

synthesiser_agent = Agent(
    model="claude-sonnet-4-6",
    system=(
        "You are an impartial arbitrator. Given an analysis and a critique, "
        "produce the most accurate, balanced, and well-supported conclusion. "
        "Acknowledge genuine uncertainty rather than false confidence."
    ),
)

async def verified_analysis(data: str, question: str) -> dict:
    # Blue team: primary analysis
    primary = await analyst_agent.run(
        f"Question: {question}\n\nData:\n{data}\n\nProvide detailed analysis."
    )

    # Red team: adversarial critique
    critique = await critic_agent.run(
        f"Question: {question}\n\n"
        f"Analysis to challenge:\n{primary.text}\n\n"
        "Find every flaw, gap, and alternative interpretation."
    )

    # Synthesis: arbitrated conclusion
    final = await synthesiser_agent.run(
        f"Question: {question}\n\n"
        f"Original analysis:\n{primary.text}\n\n"
        f"Adversarial critique:\n{critique.text}\n\n"
        "Produce the most accurate conclusion, incorporating valid critiques."
    )

    return {
        "analysis": primary.text,
        "critique": critique.text,
        "verified_conclusion": final.text,
        "confidence": "high" if "significant flaw" not in critique.text.lower() else "medium",
    }
```

### Tournament Evaluation

Generate N candidate solutions in parallel, then use a judge to select the best. Effective for code generation, document drafting, and algorithm design.

```python
import asyncio
from claude_agent_sdk import Agent

solver_agent = Agent(
    model="claude-sonnet-4-6",
    tools=[write_code, run_tests],
    system="You are an expert software engineer. Solve the given problem.",
)

judge_agent = Agent(
    model="claude-sonnet-4-6",
    tools=[run_tests, analyse_code],
    system=(
        "You are a code reviewer and judge. Evaluate candidate solutions on: "
        "correctness, performance, readability, edge-case handling, and maintainability. "
        "Select the best and explain your reasoning."
    ),
)

async def tournament_solve(problem: str, n_candidates: int = 3) -> dict:
    # Generate N candidates in parallel with a different seed prompt each time
    seed_variants = [
        f"{problem}\n\nApproach this from the angle of: {approach}"
        for approach in [
            "optimising for performance",
            "optimising for readability and maintainability",
            "minimising code complexity",
        ][:n_candidates]
    ]

    candidates = await asyncio.gather(*[
        solver_agent.run(variant) for variant in seed_variants
    ])

    # Build evaluation prompt
    evaluation_prompt = (
        f"Problem:\n{problem}\n\n"
        "Evaluate these candidate solutions and select the best:\n\n"
        + "\n\n---\n\n".join(
            f"### Candidate {i + 1}\n{c.text}"
            for i, c in enumerate(candidates)
        )
        + "\n\nProvide: winner (1/2/3), detailed reasoning, and any improvements."
    )

    verdict = await judge_agent.run(evaluation_prompt)

    return {
        "candidates": [c.text for c in candidates],
        "verdict": verdict.text,
        "token_cost": sum(c.usage.total_tokens for c in candidates) + verdict.usage.total_tokens,
    }
```

---

## 7. Skills

### What Are Skills

Skills are reusable, model-discoverable capabilities described in Markdown files. The SDK auto-discovers all `SKILL.md` files in the `.agents/skills/` directory at agent startup. The model reads skill descriptions and invokes them by name when the task calls for it — no explicit tool call wiring required.

Skills are best for higher-level workflows that combine multiple tools, or for domain expertise the agent should apply automatically.

### Directory Structure

```
.claude/
  skills/
    data-analysis.md
    report-writer.md
    security-reviewer.md
    onboarding.md
```

### Creating a SKILL.md

```markdown
# Skill: Data Analysis

## Description
Perform quantitative analysis on tabular data: descriptive statistics,
trend detection, outlier identification, and correlation analysis.

## When to invoke
- User asks to "analyse data", "find trends", or "generate a report"
- User provides a CSV, database table name, or query result
- User asks about patterns, anomalies, or relationships in data

## Capabilities
- Descriptive statistics (mean, median, std dev, percentiles)
- Correlation and regression analysis
- Outlier detection (IQR and z-score methods)
- Time-series trend analysis
- Export results as JSON or formatted Markdown tables

## Tools used
- `query_analytics` — fetch data from the database
- `run_python` — execute analysis code
- `write_file` — save results to disk

## Output format
Return a structured report with:
1. Executive summary (3 sentences max)
2. Key findings (bullet list)
3. Supporting statistics (table)
4. Recommended next steps

## Example invocation
"Analyse sales data for Q2-2026 and identify the top 5 anomalies."
```

### Model Invocation

```python
from claude_agent_sdk import Agent, load_skills

# Auto-discover skills from .agents/skills/
skills = load_skills(skills_dir=".agents/skills")

agent = Agent(
    model="claude-sonnet-4-6",
    tools=[query_analytics, run_python, write_file],
    skills=skills,
    system=(
        "You are a senior data analyst. Use your available skills when appropriate. "
        "Always invoke the Data Analysis skill for any quantitative analysis task."
    ),
)

# Agent will automatically invoke the 'data-analysis' skill
result = await agent.run(
    "Look at our Q2 revenue data and tell me if there are any anomalies."
)
```

---

## 8. Sessions

### Persistent Context

Sessions maintain conversation history, tool results, and agent memory across multiple HTTP requests or process restarts. Without a durable state store, context is lost when the process exits.

=== "Python (Postgres)"

    ```python
    from claude_agent_sdk import Agent
    from claude_agent_sdk.stores import PostgresStateStore

    store = PostgresStateStore(
        dsn="postgresql://user:pass@host/db",
        table_prefix="agent_",  # Creates: agent_sessions, agent_memory
    )

    agent = Agent(
        model="claude-sonnet-4-6",
        tools=[query_analytics, write_report],
        state_store=store,
    )
    ```

=== "Python (Redis)"

    ```python
    from claude_agent_sdk.stores import RedisStateStore

    store = RedisStateStore(
        url="redis://localhost:6379",
        ttl_seconds=86400,  # Sessions expire after 24h of inactivity
        prefix="agent:",
    )
    ```

=== "TypeScript (Postgres)"

    ```typescript
    import { Agent } from "@anthropic-ai/claude-agent-sdk";
    import { PostgresStateStore } from "@anthropic-ai/claude-agent-sdk/stores";

    const store = new PostgresStateStore({
      connectionString: process.env.DATABASE_URL!,
      tablePrefix: "agent_",
    });

    const agent = new Agent({
      model: "claude-sonnet-4-6",
      tools: [queryAnalytics, writeReport],
      stateStore: store,
    });
    ```

### Session Management Across Requests

```python
import fastapi
from claude_agent_sdk import Agent

app = fastapi.FastAPI()

@app.post("/chat/{session_id}")
async def chat(session_id: str, body: ChatRequest, user: User = Depends(get_user)):
    # Load existing session (creates new if not found)
    session = await agent.load_session(
        session_id=f"user-{user.id}-{session_id}",
        metadata={"user_id": user.id, "created_by": user.email},
    )

    result = await session.continue_(body.message)

    return {
        "response": result.text,
        "session_id": session_id,
        "turn_count": session.turn_count,
        "tokens_used": result.usage.total_tokens,
    }

@app.delete("/chat/{session_id}")
async def delete_session(session_id: str, user: User = Depends(get_user)):
    await agent.delete_session(f"user-{user.id}-{session_id}")
    return {"deleted": True}

@app.get("/chat/{session_id}/history")
async def get_history(session_id: str, user: User = Depends(get_user)):
    session = await agent.load_session(f"user-{user.id}-{session_id}")
    log = await session.export_log()
    # Audit log — strip tool results if they contain PII
    return {
        "turns": [
            {"role": t.role, "preview": t.content[:200], "timestamp": t.timestamp}
            for t in log.turns
        ]
    }
```

### Session Isolation

```python
# Each tenant gets isolated sessions — no cross-tenant data leakage
async def run_for_tenant(tenant_id: str, user_id: str, prompt: str):
    session_id = f"tenant:{tenant_id}:user:{user_id}"
    session = await agent.load_session(
        session_id=session_id,
        metadata={"tenant_id": tenant_id, "user_id": user_id},
    )
    return await session.continue_(prompt)
```

---

## 9. Subagents

### Delegation

Spawn a subagent when you need a specialised capability, isolated context, or a different model without polluting the parent's conversation history.

```python
from claude_agent_sdk import Agent

orchestrator = Agent(
    model="claude-sonnet-4-6",
    system="You coordinate specialised agents to complete complex tasks.",
)

async def generate_and_review_code(requirement: str) -> dict:
    # Delegate code generation to a subagent with coding tools
    code_result = await orchestrator.spawn_subagent(
        task=f"Write Python code to: {requirement}",
        model="claude-sonnet-4-6",
        tools=[write_file, run_tests, read_file],
        system="You are an expert Python developer. Write clean, tested code.",
        max_tokens=4096,
    )

    # Delegate security review to a separate subagent
    security_result = await orchestrator.spawn_subagent(
        task=(
            f"Perform a security review of this Python code:\n\n{code_result.text}\n\n"
            "Look for: injection flaws, hardcoded secrets, insecure deserialization, "
            "path traversal, and missing input validation."
        ),
        model="claude-sonnet-4-6",
        tools=[analyse_code],
        system="You are an application security engineer specialising in Python.",
        max_tokens=2048,
    )

    return {
        "code": code_result.text,
        "security_review": security_result.text,
        "total_tokens": code_result.usage.total_tokens + security_result.usage.total_tokens,
    }
```

### Context Isolation

Subagents do not inherit the parent's conversation history. Pass only the context the subagent needs — this reduces token costs and prevents information leakage between tasks.

```python
async def process_documents(documents: list[dict]) -> list[dict]:
    """
    Each document gets its own subagent with isolated context.
    No cross-contamination of sensitive information between documents.
    """
    async def process_one(doc: dict) -> dict:
        result = await orchestrator.spawn_subagent(
            task=f"Summarise this document in 3 bullet points:\n\n{doc['content']}",
            model="claude-haiku-4-5",  # Cheapest model for simple summarisation
            max_tokens=512,
            # Context is only this document — not the full document set
        )
        return {"doc_id": doc["id"], "summary": result.text}

    # Process up to 10 documents concurrently
    semaphore = asyncio.Semaphore(10)

    async def bounded(doc):
        async with semaphore:
            return await process_one(doc)

    return await asyncio.gather(*[bounded(d) for d in documents])
```

### Result Aggregation

```python
from claude_agent_sdk import Agent
from pydantic import BaseModel

class RegionReport(BaseModel):
    region: str
    revenue_usd: float
    growth_pct: float
    top_product: str
    risk_flags: list[str]

async def aggregate_reports(regions: list[str]) -> dict:
    # Spawn subagents with structured output schemas
    tasks = [
        orchestrator.spawn_subagent(
            task=f"Analyse Q2-2026 data for region: {region}",
            model="claude-haiku-4-5",
            output_schema=RegionReport,
        )
        for region in regions
    ]
    results = await asyncio.gather(*tasks)

    reports = [r.output for r in results]  # Each r.output is a validated RegionReport

    # Sort by revenue, flag high-risk regions
    sorted_reports = sorted(reports, key=lambda r: r.revenue_usd, reverse=True)
    high_risk = [r for r in reports if r.risk_flags]

    return {
        "top_region": sorted_reports[0].region,
        "total_revenue": sum(r.revenue_usd for r in reports),
        "high_risk_regions": [r.region for r in high_risk],
        "reports": [r.dict() for r in sorted_reports],
    }
```

---

**This is Part 1 of 3. [Continue with Part 2 →](pathname:///archon/agentic-systems/coding-tools/parts/30-claude-agent-sdk-production-part2) for Production Patterns and Observability, or [skip to Part 3 →](pathname:///archon/agentic-systems/coding-tools/parts/30-claude-agent-sdk-production-part3) for Best Practices and Testing.**
