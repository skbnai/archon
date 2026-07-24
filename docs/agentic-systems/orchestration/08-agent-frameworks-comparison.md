---
title: "Agent Frameworks Comparison"
date_created: 2026-07-24
last_reviewed: 2026-07-24
status: current
domain: agentic-systems
topic_id: agent-frameworks-comparison
supersedes: ["docs/workflow-orchestration/08-agent-frameworks-comparison.md"]
doc_type: guide
tags: ["workflow-orchestration", "agents", "langgraph", "crewai", "pydanticai", "google-adk", "mastra"]
---

# Agent Frameworks Comparison

> **As of July 2026.** Versions: LangGraph 1.2.8, CrewAI 0.80, PydanticAI 0.0.54, Google ADK 1.0, Mastra 0.10, Microsoft Agent Framework SDK 1.0.

This guide compares the leading agent orchestration frameworks for teams building agentic systems on top of or alongside workflow orchestrators like Temporal and Camunda. It covers **LangGraph, CrewAI, PydanticAI, Google ADK, Mastra, and Microsoft Agent Framework SDK** — with guidance on state management, tool calling, multi-agent support, and Temporal integration.

---

## Framework Landscape

```mermaid
graph LR
    Control["CONTROL"] --> Flex["FLEXIBILITY"]
    
    TypeSafe["Type-safe / Structured:<br/>PydanticAI<br/>(typed I/O, validation)"]
    RoleBased["Role-based Teams:<br/>CrewAI<br/>(role + task)"]
    Explicit["Explicit Graph:<br/>LangGraph<br/>(explicit graph nodes)"]
    Managed["Managed / Azure-native:<br/>MS Agent Framework<br/>(Azure AI Foundry)"]
    Cloud["Cloud-native:<br/>Google ADK<br/>(Google APIs)"]
    FullStack["Full-stack TypeScript:<br/>Mastra<br/>(TS, full-app,<br/>built-in memory)"]
    
    Control --> TypeSafe
    Control --> RoleBased
    Control --> Explicit
    Explicit --> Managed
    Explicit --> Cloud
    Flex --> FullStack
```

No framework is universally best. The right choice depends on control flow needs, type-safety requirements, language preference, and cloud platform.

---

## LangGraph

**Best for**: Stateful multi-step agents where you need explicit control over the reasoning loop.

LangGraph 1.2.8 models agent execution as a **directed graph** — nodes are functions, edges are transitions. You can see, control, and debug exactly which nodes ran and why, unlike frameworks that hide the loop inside a black box.

```python
# pip install langgraph==1.2.8
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from langchain_anthropic import ChatAnthropic
from typing import TypedDict, Annotated
import operator

class AgentState(TypedDict):
    messages: Annotated[list, operator.add]

model = ChatAnthropic(model="claude-sonnet-4-6")
tools = [lookup_account, check_policy, draft_response]
model_with_tools = model.bind_tools(tools)
tool_node = ToolNode(tools)

def call_model(state: AgentState) -> AgentState:
    response = model_with_tools.invoke(state["messages"])
    return {"messages": [response]}

def should_continue(state: AgentState) -> str:
    last = state["messages"][-1]
    return "tools" if last.tool_calls else END

graph = StateGraph(AgentState)
graph.add_node("agent", call_model)
graph.add_node("tools", tool_node)
graph.set_entry_point("agent")
graph.add_conditional_edges("agent", should_continue)
graph.add_edge("tools", "agent")

# Compile with checkpointing (enables pause/resume)
from langgraph.checkpoint.sqlite import SqliteSaver
memory = SqliteSaver.from_conn_string(":memory:")
app = graph.compile(checkpointer=memory)

result = app.invoke(
    {"messages": [{"role": "user", "content": "Resolve billing dispute for account A-123"}]},
    config={"configurable": {"thread_id": "dispute-A-123"}},
)
```

**State management**: TypedDict schema, persisted via checkpointer (SQLite, Postgres, Redis). Supports pause/resume — a human approval gate can suspend the graph and resume it when approved.

**Tool handling**: LangChain tools or `ToolNode` prebuilt. Tool calling is explicit in the graph — you decide when the agent can call tools vs. when it must reason.

**Multi-agent**: Supervisor patterns with subgraphs. Each agent is a compiled subgraph; a supervisor routes between them via conditional edges.

**Temporal integration**: LangGraph runs naturally inside a Temporal activity. The compiled `app.invoke(...)` is a single function call.

**When to choose LangGraph**:

- You need explicit control over the reasoning loop
- You want pause/resume for human-in-the-loop gates
- You are building multi-agent workflows with defined handoffs
- You need to debug exactly which nodes ran and in what order

---

## CrewAI

**Best for**: Role-based teams of agents working on decomposed tasks in sequence or parallel.

CrewAI models the problem as a **crew** (team of agents) executing **tasks**. Each agent has a role, goal, and backstory. Tasks flow through the crew according to a process.

```python
# pip install crewai==0.80.0
from crewai import Agent, Task, Crew, Process
from langchain_anthropic import ChatAnthropic

claude = ChatAnthropic(model="claude-sonnet-4-6")

researcher = Agent(
    role="Senior Research Analyst",
    goal="Find accurate information about the topic and synthesize key findings",
    backstory="Expert in enterprise architecture with 10 years of distributed systems experience",
    tools=[search_tool, read_tool],
    llm=claude,
    verbose=True,
)

writer = Agent(
    role="Technical Writer",
    goal="Convert research into clear, structured architectural guidance",
    backstory="Specializes in enterprise documentation and architecture decision records",
    llm=claude,
    verbose=True,
)

research_task = Task(
    description="Research the current state of agent orchestration frameworks in 2026. Focus on production adoption, limitations, and enterprise fit.",
    agent=researcher,
    expected_output="A structured summary of framework capabilities with concrete trade-offs",
)

write_task = Task(
    description="Write an architectural comparison guide based on the research. Target audience: enterprise architects choosing a framework.",
    agent=writer,
    context=[research_task],  # writer receives researcher's output as context
    expected_output="A 2000-word comparison guide with a recommendation matrix",
)

crew = Crew(
    agents=[researcher, writer],
    tasks=[research_task, write_task],
    process=Process.sequential,
    verbose=True,
)

result = crew.kickoff()
print(result.raw)
```

**State management**: Task outputs are passed as context between tasks. Long-term memory available via `memory=True` on `Crew` — backed by ChromaDB.

**Multi-agent**: Built-in via crew composition. `Process.hierarchical` adds a manager agent that delegates and routes tasks.

**When to choose CrewAI**:

- Your problem naturally decomposes into roles (researcher, analyst, writer, reviewer)
- You want a readable, declarative team definition
- You are building content pipelines, research workflows, or report generation
- You don't need fine-grained control over the reasoning loop

---

## PydanticAI

**Best for**: Type-safe agents where the correctness of structured output matters more than flexibility.

PydanticAI wraps LLM calls with Pydantic models for input validation and output parsing. The agent is less a free-form reasoning engine and more a **typed extraction pipeline** with LLM steps.

```python
# pip install pydantic-ai==0.0.54
from pydantic_ai import Agent
from pydantic import BaseModel, Field
from typing import Optional

class LoanDecision(BaseModel):
    approved: bool
    credit_score_used: int = Field(ge=300, le=850)
    debt_to_income_ratio: float = Field(ge=0.0, le=1.0)
    reason: str
    suggested_rate: Optional[float] = Field(default=None, ge=0.01, le=0.30)
    conditions: list[str] = Field(default_factory=list)

loan_agent = Agent(
    "claude-sonnet-4-6",
    result_type=LoanDecision,
    system_prompt=(
        "You are a loan underwriting agent for a regulated financial institution. "
        "Analyze the application data provided via tools and return a structured underwriting decision. "
        "You must use the credit score and income tools before making a decision."
    ),
)

@loan_agent.tool
async def get_credit_score(ctx, applicant_id: str) -> int:
    """Fetches credit score from bureau. Returns integer 300-850."""
    return await credit_bureau_client.fetch_score(applicant_id)

@loan_agent.tool
async def get_income_verification(ctx, applicant_id: str) -> dict:
    """Returns verified annual income and employment status."""
    return await income_verifier.fetch(applicant_id)

@loan_agent.tool
async def get_existing_debts(ctx, applicant_id: str) -> list[dict]:
    """Returns list of current debt obligations with monthly payments."""
    return await debt_registry.fetch(applicant_id)

async def underwrite(applicant_id: str) -> LoanDecision:
    result = await loan_agent.run(f"Underwrite loan application for applicant {applicant_id}")
    return result.data  # LoanDecision — fully typed and validated

decision = asyncio.run(underwrite("APP-456"))
assert isinstance(decision.approved, bool)  # always — Pydantic guarantees it
```

**State management**: Stateless by design — each run is independent. Pass context explicitly as tool return values.

**Testing**: Straightforward to unit test — mock tools, assert on typed output. No hidden state to account for.

**When to choose PydanticAI**:

- Structured output correctness is critical (finance, compliance, healthcare, legal)
- You need to validate LLM output against a business schema before acting
- You want simple, testable agents without orchestration overhead
- Regulatory requirements demand auditable, predictable outputs

---

## Google ADK

**Best for**: Google Cloud-native workloads, and systems that use Vertex AI, Google Search, or BigQuery.

Google Agent Development Kit (ADK) 1.0 is designed around Google's agent ecosystem — tight integration with Vertex AI models, Google Search grounding, and the Agent-to-Agent (A2A) protocol.

```python
# pip install google-adk==1.0.0
from google.adk.agents import Agent
from google.adk.tools import google_search, code_execution
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner

root_agent = Agent(
    name="research_agent",
    model="gemini-2.0-flash",  # or claude via Vertex AI
    description="Researches topics using Google Search and summarizes findings",
    instruction="""
    You are a research agent. When given a topic:
    1. Search for current information using the search tool
    2. Synthesize findings into a structured summary
    3. Include sources for all factual claims
    """,
    tools=[google_search, code_execution],
)

# Multi-agent: ADK uses sub-agents natively
coordinator = Agent(
    name="coordinator",
    model="gemini-2.0-flash",
    description="Coordinates research and analysis tasks",
    instruction="Delegate research to sub-agents and synthesize results",
    sub_agents=[root_agent, analysis_agent],
)

session_service = InMemorySessionService()
runner = Runner(
    agent=coordinator,
    app_name="research_app",
    session_service=session_service,
)

import asyncio
from google.genai import types

async def run_research(query: str) -> str:
    session = await session_service.create_session(app_name="research_app", user_id="user-1")
    content = types.Content(role="user", parts=[types.Part(text=query)])
    events = runner.run_async(user_id="user-1", session_id=session.id, new_message=content)

    async for event in events:
        if event.is_final_response():
            return event.content.parts[0].text

result = asyncio.run(run_research("Latest enterprise orchestration trends 2026"))
```

**State management**: Session-based. `InMemorySessionService` for development; `VertexAiSessionService` for production (backed by Spanner).

**A2A protocol**: ADK implements Google's A2A protocol natively — agents discover each other via `.well-known/agent.json` endpoints and communicate via structured messages.

**When to choose Google ADK**:

- You are on Google Cloud (Vertex AI, BigQuery, GKE)
- You need Google Search grounding out of the box
- You want A2A protocol compliance for multi-agent interoperability
- Your team is building with Gemini models

---

## Mastra

**Best for**: TypeScript teams building full-stack agentic applications with built-in memory and workflow support.

Mastra is a TypeScript-first framework designed to ship complete agent applications — not just the LLM reasoning layer. It includes built-in memory, workflows (similar to LangGraph), integrations, and an eval framework.

```typescript
// npm install @mastra/core@0.10
import { Mastra, Agent, createTool } from "@mastra/core";
import Anthropic from "@anthropic-ai/sdk";
import { z } from "zod";

const getLoanStatus = createTool({
  id: "get-loan-status",
  description: "Retrieves the current status of a loan application",
  inputSchema: z.object({ applicationId: z.string() }),
  outputSchema: z.object({
    status: z.enum(["pending", "approved", "rejected", "under_review"]),
    amount: z.number(),
    applicantName: z.string(),
  }),
  execute: async ({ context }) => {
    return await loanDatabase.getApplication(context.applicationId);
  },
});

const loanAgent = new Agent({
  name: "Loan Agent",
  instructions: `You are a loan servicing agent. Help customers understand
    their loan application status and answer questions about the process.`,
  model: {
    provider: "ANTHROPIC",
    toolChoice: "auto",
    name: "claude-sonnet-4-6",
  },
  tools: { getLoanStatus },
});

export const mastra = new Mastra({
  agents: { loanAgent },
});

// Use in a Next.js API route, Express handler, etc.
const agent = mastra.getAgent("loanAgent");
const response = await agent.generate(
  "What is the status of my application APP-123?",
  { threadId: "customer-session-456" }  // built-in memory across turns
);
console.log(response.text);
```

**State management**: Built-in memory via `threadId` — conversations persist across requests without external setup. Backed by Postgres or LibSQL.

**Workflows**: Mastra has a first-class workflow primitive (similar to LangGraph graphs) for multi-step agent pipelines with branching, parallel steps, and retry.

**Multi-agent**: Supported via agent handoffs in workflows. One agent can invoke another as a step.

**When to choose Mastra**:

- Your team works in TypeScript and prefers a Node.js ecosystem
- You are building a full application (API + agent + UI) not just the agent layer
- You want memory management out of the box without configuring vector stores
- You need to ship quickly with sensible defaults

---

## Microsoft Agent Framework SDK

**Best for**: Microsoft Azure and Microsoft 365 ecosystems — enterprises already invested in Azure AI Foundry, Entra ID, and Microsoft 365 infrastructure.

Microsoft Agent Framework SDK (part of Azure AI Foundry, GA 2025) is Microsoft's **production-grade, managed agent development SDK** — positioned as the enterprise path distinct from the research-oriented AutoGen and the lower-level Semantic Kernel integration toolkit. It provides a standardised way to build, host, and orchestrate agents on Azure with native integration to Azure AI services, Microsoft Entra ID, and Microsoft 365 Copilot extensibility.

**Positioning vs. other Microsoft offerings:**

- **Semantic Kernel**: Lower-level AI integration SDK for building plugins/skills; useful as a building block but not a complete agent framework
- **AutoGen (AG2)**: Multi-agent research framework for AI-to-AI conversation patterns; not recommended for production enterprise agents
- **Microsoft Agent Framework SDK**: The recommended production path — managed hosting, enterprise auth, compliance controls, M365 integration

```python
# pip install azure-ai-projects azure-ai-inference azure-identity
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import (
    AgentDefinition,
    BingGroundingTool,
    FunctionTool,
    ThreadMessage,
)
from azure.identity import DefaultAzureCredential

# Authenticate using Entra ID (managed identity in production)
credential = DefaultAzureCredential()
client = AIProjectClient(
    endpoint="https://<foundry-endpoint>.azure.com",
    credential=credential,
)

# Define tools — functions + Microsoft-native connectors
def get_customer_account(customer_id: str) -> dict:
    """Retrieves customer account details from CRM."""
    return crm_client.get_account(customer_id)

def update_account_status(customer_id: str, status: str) -> bool:
    """Updates customer account status. Requires Entra ID role: CRM.Write."""
    return crm_client.update_status(customer_id, status)

# Create agent with Azure AI Foundry — managed, persisted, version-controlled
agent = client.agents.create_agent(
    model="gpt-4o",  # or any Azure AI model: claude via Azure, Llama, Mistral
    name="customer-service-agent",
    instructions="""
    You are a customer service agent for enterprise accounts.
    Retrieve account details before taking any action.
    Always confirm before updating account status.
    Log every action taken for compliance audit trail.
    """,
    tools=[
        FunctionTool(functions=[get_customer_account, update_account_status]),
        BingGroundingTool(),  # Microsoft-native grounding
    ],
)

# Create a thread (conversation session)
thread = client.agents.create_thread()

# Add a user message
client.agents.create_message(
    thread_id=thread.id,
    role="user",
    content="Review account C-8832 and flag it if their last payment was over 90 days ago.",
)

# Run the agent
run = client.agents.create_and_process_run(
    thread_id=thread.id,
    agent_id=agent.id,
)

# Retrieve the response
messages = client.agents.list_messages(thread_id=thread.id)
for msg in messages.data:
    if msg.role == "assistant":
        print(msg.content[0].text.value)
```

**Enterprise capabilities built in:**

| Capability | Implementation |
| --- | --- |
| **Identity & access** | Microsoft Entra ID integration; agent identity is an Entra service principal; function tools can enforce Entra roles |
| **Audit trail** | All agent runs logged to Azure Monitor; queryable via Log Analytics |
| **Compliance** | Azure compliance controls (GDPR, HIPAA, FedRAMP) inherited; data residency enforced by Azure region |
| **Multi-model** | Azure AI Foundry supports OpenAI, Azure OpenAI, Meta Llama, Mistral, Cohere — agent can use any approved model |
| **Knowledge grounding** | Bing Grounding Tool; Azure AI Search connector; SharePoint connector |
| **M365 integration** | Agents deployable as Copilot extensions; native Teams integration |
| **Vector store** | Azure AI Search as managed vector store; no external vector DB required |
| **Streaming** | Server-sent events streaming natively supported |
| **Monitoring** | Azure AI Foundry tracing; OpenTelemetry-compatible spans |

**Multi-agent coordination:**

```python
# Microsoft Agent Framework supports multi-agent patterns via Connected Agents
# Each agent is a separate Foundry agent; the orchestrator delegates via tool calls

# Orchestrator agent definition
orchestrator = client.agents.create_agent(
    model="gpt-4o",
    name="orchestrator",
    instructions="Coordinate specialist agents to complete complex tasks.",
    tools=[
        # Sub-agents exposed as tools to the orchestrator
        ConnectedAgentTool(agent_id=research_agent.id, name="research"),
        ConnectedAgentTool(agent_id=analysis_agent.id, name="analysis"),
        ConnectedAgentTool(agent_id=writer_agent.id, name="write"),
    ],
)
```

**State management**: Thread-based session state persisted in Azure AI Foundry (Cosmos DB backend). Threads survive agent restarts and can be resumed. Long-term memory via Azure AI Search vector index.

**Temporal integration**: Agent runs are synchronous within a Temporal activity; use `create_and_process_run()` with polling for long-running tasks. Temporal owns the workflow durability; Foundry agent owns the reasoning.

```python
from temporalio import activity

@activity.defn
async def run_foundry_agent(customer_id: str, task: str) -> str:
    thread = client.agents.create_thread()
    client.agents.create_message(thread_id=thread.id, role="user", content=task)
    run = client.agents.create_and_process_run(
        thread_id=thread.id, agent_id=agent.id
    )
    msgs = client.agents.list_messages(thread_id=thread.id)
    return msgs.data[0].content[0].text.value
```

**When to choose Microsoft Agent Framework SDK:**

- Your enterprise is Azure-first with Entra ID and Microsoft 365
- You need compliance-ready agents (GDPR, HIPAA, FedRAMP) without bespoke compliance engineering
- You want to deploy agents as Microsoft 365 Copilot extensions
- Your team needs managed infrastructure (no vector DB ops, no model hosting ops)
- Enterprise procurement prefers Microsoft's unified SLA and support model
- You need built-in Entra ID role-based access control for agent tool permissions

---

## Comparison Matrix

| Feature | LangGraph | CrewAI | PydanticAI | Google ADK | Mastra | **MS Agent Framework** |
| --- | --- | --- | --- | --- | --- | --- |
| **Language** | Python | Python | Python | Python | TypeScript | Python / .NET |
| **Control model** | Explicit graph | Role + task | Typed pipeline | Session + agent | Workflow + agent | Thread + managed run |
| **State / memory** | Checkpoints | Task context | Stateless | Session service | Built-in (threadId) | Thread (Cosmos DB) |
| **Type safety** | Medium | Low | High | Medium | High (TypeScript) | Medium |
| **Multi-agent** | Excellent | Good | Minimal | Excellent (A2A) | Good | Good (Connected Agents) |
| **Temporal integration** | Natural | As activity | As activity | As activity | Via TS SDK | As activity |
| **Production maturity** | High | Medium | Growing | High (GCP) | Growing | High (Azure) |
| **Cloud native** | No | No | No | GCP | No | Azure |
| **Built-in memory** | Via checkpointer | Via ChromaDB | No | Via session service | Yes | Yes (Foundry) |
| **Enterprise auth (IdP)** | Manual | Manual | Manual | GCP IAM | Manual | **Entra ID native** |
| **Compliance controls** | Manual | Manual | Manual | GCP compliance | Manual | **Azure compliance** |
| **M365 / Copilot integration** | No | No | No | No | No | **Yes** |
| **Managed infrastructure** | No | No | No | Partially | No | **Yes** |

---

## Decision Guide

```
Is your team TypeScript / Node.js?
  YES → Mastra
  NO  ↓

Are you Azure-first with Entra ID / Microsoft 365?
  YES → Microsoft Agent Framework SDK
  NO  ↓

Are you on Google Cloud with Vertex AI / Gemini?
  YES → Google ADK
  NO  ↓

Do you need type-safe, validated structured output?
  YES → PydanticAI
  NO  ↓

Is your problem decomposable into roles/teams?
  YES → CrewAI
  NO  ↓

Default choice for stateful, controllable agents:
  → LangGraph
```

---

## Integrating with Temporal

All frameworks can run as a Temporal activity — Temporal owns durability, the framework owns reasoning:

```python
from temporalio import activity
from datetime import timedelta

@activity.defn
async def run_langgraph_agent(input_data: dict) -> dict:
    from langgraph.checkpoint.sqlite import SqliteSaver

    memory = SqliteSaver.from_conn_string(":memory:")
    app = build_graph().compile(checkpointer=memory)

    result = await app.ainvoke(
        {"messages": [{"role": "user", "content": input_data["goal"]}]},
        config={"configurable": {"thread_id": input_data["run_id"]}},
    )
    return {"result": result["messages"][-1].content}

# In Temporal workflow:
# agent_result = await workflow.execute_activity(
#     run_langgraph_agent,
#     {"goal": "...", "run_id": workflow.info().workflow_id},
#     start_to_close_timeout=timedelta(minutes=5),
# )
```

Temporal handles: guaranteed execution, retries, audit trail, long-running coordination.  
The agent framework handles: reasoning, tool selection, and adaptive behavior within a bounded step.

---

## Related

[Durable Execution vs Cognitive Execution](./06-durable-vs-cognitive-execution.md) · [Tool Calling Orchestration](./09-tool-calling-orchestration.md) · [A2A Orchestration Patterns](./11-a2a-orchestration-patterns.md) · [AI Coding Orchestrators](./07-ai-coding-orchestrators.md)
