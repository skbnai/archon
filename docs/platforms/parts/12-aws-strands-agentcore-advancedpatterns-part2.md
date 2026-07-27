---
title: "AWS Strands & Bedrock AgentCore — Advanced Patterns v3.0 (Part 2: Checkpointer, Code Interpreter, Browser Tool, Meta Tool)"
doc_type: guide
domain: platforms
status: draft
topic_id: aws-strands-agentcore-advancedpatterns-part2
last_reviewed: 2026-07-27
maturity: practitioner
supersedes: []
tags: [aws, agentcore, strands, hooks, hitl, checkpointer, multi-agent]
covers_version: "N/A"
---

> **Known issue:** some fenced code examples on this page were flattened during the original PDF-to-markdown conversion (lost line breaks/indentation, stray artifact characters) and need reformatting. Tracked in migration/WAVE6_BATCH1_STATUS.md (repo root).

*Part 2 of 3 of [AWS Strands & Bedrock AgentCore — Advanced Patterns v3.0](../12-aws-strands-agentcore-advancedpatterns.md). Continued in [Part 3](12-aws-strands-agentcore-advancedpatterns-part3.md).*

## Checkpointer: State Persistence & Replay

SessionManag er · DynamoDB · AgentCore Memory · Multi-Tier

#### A3.1 Why Agents Need Checkpointing

Production agents die: Lambda timeouts, container restarts, network failures. Without checkpointing, the entire conversation history, intermediate tool results, and agentic reasoning context are lost. **Checkpointing** persists agent state at every step so agents can: *resume* after crashes, *pause* for HITL approvals, *replay* historical runs for debugging, and *branch* into parallel sub-agents without memory conflicts.

|**Backend**|**What Persists / Tradeoffs**|**Best For**|
|---|---|---|
|Strands SessionManager (File)|In-process, file-backed. Session history only. No tool state.|Dev / single-user|
|Strands SessionManager (S3)|Atomic S3 writes, safe concurrent access. Session history.|Multi-instance prod|
|LangGraph DynamoDBSaver|Full graph state: node outputs, edges, pending actions.<br/>Small->DDB, large->S3.|LangGraph + full replay|
|LangGraph AgentCoreMemorySaver|Persists to AgentCore Memory API. Native integration.|AgentCore + LangGraph|
|Custom Redis/Valkey checkpointer|Sub-millisecond reads. Use for high-throughput real-time<br/>agents.|High-frequency agents|

#### A3.2 Strands Built-In SessionManager

###### `session_manager.py`

```
```

```
from strands.session import FileSessionManager, S3SessionManager
```

- `#` II `Option A: File-based (development / local testing)` IIIIIIIIIIIIIII `file_manager = FileSessionManager(`

```
    storage_dir="./sessions",  # NEVER use default /tmp — wiped on restart!
```

```
    agent_id="support-agent-v2",
```

```
)
```

`#` II `Option B: S3-based (production, multi-instance safe)` IIIIIIIIIIIII

```
s3_manager = S3SessionManager(
```

```
    bucket="my-agent-sessions",
    prefix="prod/support/",
```

```
    agent_id="support-agent-v2",
```

```
    # Atomic operations: uses S3 conditional writes to prevent race conditions
```

```
    kms_key_id="arn:aws:kms:us-east-1:123:key/abc",  # Encrypt at rest
)
# Agent with session persistence
```

```
    model="us.anthropic.claude-sonnet-4-20250514",
    system_prompt="You are a support agent.",
    tools=[...],
    session_manager=s3_manager,  # Drop-in; works with any backend
)
```

```
# First invocation: creates session
result1 = agent("Hello, my order #1234 is missing.", session_id="user-abc-session-1")
# Second invocation: automatically loads conversation history from S3
result2 = agent("What was the order ID I mentioned?", session_id="user-abc-session-1")
# Agent will correctly recall order #1234 from persisted history
```

#### A3.3 LangGraph DynamoDBSaver (Full Graph State)

###### `dynamodb_checkpointer.py`

```
pip install langgraph-checkpoint-aws
from langchain.chat_models import init_chat_model
from langgraph.prebuilt import create_react_agent
from langgraph_checkpoint_aws import DynamoDBSaver
```

`#` II `Production DynamoDB checkpointer` IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII `checkpointer = DynamoDBSaver( table_name="agent-checkpoints", region_name="us-east-1", ttl_seconds=86400 * 7,            # 7-day auto-expiry enable_checkpoint_compression=True, # Gzip compression s3_offload_config={               # Large checkpoints (>350KB)` -> `S3 "bucket_name": "agent-checkpoint-offload" } ) # IAM policy required: # dynamodb:GetItem, PutItem, Query, BatchGetItem, BatchWriteItem # s3:GetObject, PutObject (for large payloads) # Create agent graph with checkpointing llm = init_chat_model("us.anthropic.claude-sonnet-4-20250514", model_provider="bedrock_converse") agent_graph = create_react_agent(llm, tools=[...], checkpointer=checkpointer) #` II `Invoke with thread_id for session tracking` IIIIIIIIIIIIIIIIIIIIIIII `config = {"configurable": {"thread_id": "user-abc-thread-1"}} result1 = agent_graph.invoke( {"messages": [{"role":"user","content":"Start a complex multi-step analysis"}]}, config=config ) #` II `HITL pause: agent interrupted mid-execution` IIIIIIIIIIIIIIIIIIIIIII `# Check for pending interrupt if "__interrupt__" in result1: print(f"Human approval needed: {result1['__interrupt__']}") # ... notify human ... # Resume after approval: result2 = agent_graph.invoke( {"resume": {"decision": "APPROVED"}}, config=config  # Same thread_id = same checkpoint )`

```
llm = init_chat_model("us.anthropic.claude-sonnet-4-20250514", model_provider="bedrock_converse")
agent_graph = create_react_agent(llm, tools=[...], checkpointer=checkpointer)
```

`#` II `Replay: list all checkpoints for a session` IIIIIIIIIIIIIIIIIIIIIIII `history = list(agent_graph.get_state_history(config)) for snapshot in history: print(f"Step {snapshot.metadata.get('step')}: {snapshot.next} | {snapshot.created_at}")`

`#` II `Time-travel: re-run from a specific checkpoint` IIIIIIIIIIIIIIIIIIII `past_config = {"configurable": {"thread_id": "user-abc-thread-1",`

```
                                 "checkpoint_id": history[3].config["configurable"]["checkpoint_id"
]}}
```

```
replay_result = agent_graph.invoke(
    {"messages": [{"role":"user","content":"What did you conclude in step 3?"}]},
    config=past_config
)
```

#### A3.4 AgentCoreMemorySaver for LangGraph

###### `agentcore_memorysaver.py`

`from langgraph_checkpoint_aws import AgentCoreMemorySaver, AgentCoreMemoryStore from langchain.chat_models import init_chat_model from langgraph.prebuilt import create_react_agent from langchain_core.runnables import RunnableConfig from langchain_core.messages import HumanMessage import uuid MEMORY_ID = "mem-abc123"   # AgentCore Memory resource ID REGION    = "us-west-2" #` II `Short-term checkpointer: full session state per turn` IIIIIIIIIIIII `checkpointer = AgentCoreMemorySaver(MEMORY_ID, region_name=REGION)`

`#` II `Long-term store: semantic insight extraction` IIIIIIIIIIIIIIIIIIIIIII `store = AgentCoreMemoryStore(MEMORY_ID, region_name=REGION) # Pre-model hook: save human messages + retrieve long-term memories def pre_model_hook(state, config: RunnableConfig, *, store): actor_id  = config["configurable"]["actor_id"] thread_id = config["configurable"]["thread_id"] namespace = (actor_id, thread_id)`

```
    # Persist message to long-term store for background extraction
    for msg in reversed(state.get("messages", [])):
        if isinstance(msg, HumanMessage):
```

`store.put(namespace, str(uuid.uuid4()), {"message": msg.content}) break # Retrieve relevant memories to inject into context memories = store.search(namespace, query=state["messages"][-1].content, limit=3) if memories: memory_context = "\n".join(m.value.get("insight","") for m in memories) system_inject = f"\n\nRelevant context from past sessions:\n{memory_context}" # Inject into system message return {"messages": [{"role":"system","content":system_inject}]+state["messages"]} return state llm = init_chat_model("us.anthropic.claude-sonnet-4-20250514", model_provider="bedrock_converse") agent = create_react_agent(llm, tools=[...], checkpointer=checkpointer, pre_model_hook=pre_model_hook, store=store) #` II `Invoke with actor_id (user) + thread_id (conversation)` IIIIIIIIIII

```
config = {"configurable": {"actor_id": "user-123", "thread_id": "conv-abc"}}
```

```
result = agent.invoke({"messages":[{"role":"user","content":"Summarize my preferences"}]}, config)
```

#### A3.5 Multi-Tier Memory Orchestrator (Expert Pattern)

For complex agents needing three distinct memory tiers, implement a unified orchestrator that routes reads/writes across the appropriate backend:

###### `multi_tier_memory.py`

```
from dataclasses import dataclass, field
from typing import List, Dict, Any, Tuple
import json, boto3
@dataclass
class MultiTierMemoryOrchestrator:
    """Unified interface across: in-process (fast), DynamoDB (session), AgentCore (long-term)."""
    session_id:   str
    actor_id:     str
    dynamo_table: str = "agent-checkpoints"
    memory_id:    str = "mem-abc123"
    _hot_cache:   Dict = field(default_factory=dict, init=False)   # L1: in-memory
    _dynamo:      Any  = field(default=None, init=False)           # L2: DynamoDB
    _agentcore:   Any  = field(default=None, init=False)           # L3: AgentCore Memory
    def __post_init__(self):
        self._dynamo    = boto3.client("dynamodb", region_name="us-east-1")
        from langgraph_checkpoint_aws import AgentCoreMemoryStore
        self._agentcore = AgentCoreMemoryStore(self.memory_id, region_name="us-east-1")
    # L1: Fast in-process cache (current execution only)
    def hot_put(self, key: str, value: Any):
        self._hot_cache[key] = value
    def hot_get(self, key: str) -> Any:
        return self._hot_cache.get(key)
    # L2: DynamoDB session store (survives restarts within session TTL)
    def session_put(self, key: str, value: Any, ttl_hours: int = 24):
        import time
        self._dynamo.put_item(TableName=self.dynamo_table, Item={
            "PK": {"S": f"SESSION#{self.session_id}"},
            "SK": {"S": key},
            "data": {"S": json.dumps(value)},
            "ttl": {"N": str(int(time.time()) + ttl_hours * 3600)}
        })
    def session_get(self, key: str) -> Any:
        resp = self._dynamo.get_item(
            TableName=self.dynamo_table,
            Key={"PK":{"S":f"SESSION#{self.session_id}"},"SK":{"S":key}}
        )
        if "Item" in resp: return json.loads(resp["Item"]["data"]["S"])
        return None
    # L3: AgentCore Memory (long-term cross-session, semantically searched)
    def long_put(self, content: str, namespace_suffix: str = "preferences"):
        ns = (self.actor_id, namespace_suffix)
        import uuid
```

```
        self._agentcore.put(ns, str(uuid.uuid4()), {"content": content})
```

```
    def long_search(self, query: str, namespace_suffix: str = "preferences", top_k=5) -> List[str]:
        ns = (self.actor_id, namespace_suffix)
        results = self._agentcore.search(ns, query=query, limit=top_k)
        return [r.value.get("content","") for r in results]
    def get_hierarchical_context(self, query: str) -> Dict:
        return {
            "hot_cache": dict(self._hot_cache),
            "session": self.session_get("recent_tools"),
            "long_term": self.long_search(query),
        }
```

II **CHAPTER A4**

Secure

## AgentCore Code Interpreter

Sandbox · Isolated vs Public · Data Analysis Agents

#### A4.1 Architecture & Security Model

AgentCore Code Interpreter provides a **fully managed, sandboxed execution environment** for agent-generated code. Each session gets a dedicated container with isolated filesystem, CPU, and memory. Two network modes: **ISOLATED** (default, no internet) for sensitive data, and **PUBLIC** for agents that need live API calls or package installation.

- Supports Python, JavaScript, TypeScript execution.

- Persistent filesystem within a session: write files, read them in next code block.

- Returns: stdout, stderr, return value, generated files (charts, CSVs, documents).

- VPC-connectable for access to internal data sources.

#### A4.2 Default vs Custom Code Interpreter

###### `code_interp_isolated.py`

```
from strands_tools.code_interpreter import AgentCoreCodeInterpreter
```

`#` II `Mode A: Default isolated sandbox (no internet, max security)` IIIII `code_interp = AgentCoreCodeInterpreter()  # ISOLATED network by default`

```
```

```
    model=BedrockModel(model_id="us.amazon.nova-pro-v1:0"),
```

```
    system_prompt="""You are a data analysis assistant.
    Validate every numerical answer by writing and executing Python code.
    Always show calculations and results.""",
```

```
    tools=[code_interp.code_interpreter],  # Expose as @tool
)
```

```
result = agent("What is the compound interest on $10,000 at 7% over 15 years, compounded monthly?")
```

```
# Agent writes Python, executes it, returns verified numeric answer
```

###### `code_interp_public.py`

```
from bedrock_agentcore.tools.code_interpreter_client import CodeInterpreter
from strands import Agent, tool
```

```
```

- `#` II `Mode B: Custom interpreter with PUBLIC network access` IIIIIIIIIIIII

- `# Use when agent needs: pip install, external APIs, live data ci_client = CodeInterpreter(region="us-east-1")`

- `# Provision a custom interpreter resource (in console or via API) ci_client.start(identifier="YOUR_CODE_INTERPRETER_ID")  # PUBLIC network mode`

```
@tool
```

`def execute_python_with_internet(code: str) -> str: """Execute Python code with full internet access and package installation. Use for: live data fetching, pip install, API calls. NEVER use for processing confidential/PII data.""" response = ci_client.invoke("executeCode", { "code": code, "language": "python", "timeout": 30,  # seconds }) result_parts = [] for event in response["stream"]: if "result" in event: result_parts.append(str(event["result"])) if "error"  in event: result_parts.append(f"ERROR: {event['error']}") return "\n".join(result_parts) agent = Agent( model=BedrockModel(model_id="us.amazon.nova-pro-v1:0"), system_prompt="You can install packages and access live data to answer questions.", tools=[execute_python_with_internet], ) result = agent("What is Amazon's stock price right now? Calculate its P/E ratio if EPS is $58.") # Agent: pip install yfinance` -> `fetch live AMZN` -> `calculate` -> `return`

#### A4.3 Data Analysis Agent Pattern

###### `data_analysis_agent.py`

```
from strands_tools.code_interpreter import AgentCoreCodeInterpreter
```

`# Full data analysis agent: upload CSV` -> `analyze` -> `visualise` -> `export code_interp = AgentCoreCodeInterpreter() analysis_agent = Agent( model=BedrockModel(model_id="us.amazon.nova-pro-v1:0"), system_prompt="""You are a senior data analyst. When given data: (1) explore shape/dtypes, (2) check for missing values,`

```
    (3) compute key statistics, (4) create appropriate visualizations,
```

```
    (5) identify trends/anomalies, (6) summarize findings in plain English.
    Always use pandas, matplotlib, seaborn. Save charts as PNG files.""",
    tools=[code_interp.code_interpreter],
)
# Agent receives CSV path, does full analysis autonomously
report = analysis_agent("""
    Analyze the sales data in /uploads/sales_q1_2026.csv.
    Identify the top 5 products by revenue, show monthly trends,
    flag any anomalies, and export a summary report as PDF.
""")
```

```
# Agent generates: matplotlib charts, pandas analysis, PDF summary — all in sandbox
# Retrieve generated files from sandbox session filesystem
output_files = code_interp.list_files()  # Returns generated chart PNGs, PDF
print(report.message)
```

###### II **WARNING**

**Code Interpreter security rules** : (1) Always use ISOLATED mode for data containing PII or business-sensitive content. (2) Never pass raw user input directly as code to execute — always have the LLM generate the code which is then reviewed by Guardrails before execution. (3) Apply a timeout (30s default) to prevent runaway computations.

I **CHAPTER A5**

## AgentCore Browser Tool

Managed Browser · Web Automation · Data Extraction · Nova Act

#### A5.1 Browser Tool Architecture

AgentCore Browser Tool provides a **cloud-managed headless browser** runtime that agents can control to navigate websites, fill forms, extract data, and complete multi-step web tasks — all within a secure sandbox with enterprise-grade isolation. No Selenium/Playwright infrastructure to manage; it scales automatically and provides session-level isolation between users.

- Navigate arbitrary URLs including SPAs requiring JavaScript rendering.

- Multi-step form completion, authentication flows, file downloads/uploads.

- Screenshots at any point for visual debugging or multimodal agent input.

- VPC connectivity for accessing internal web applications.

- Full audit log of all browser actions for compliance.

#### A5.2 Integration with Strands

###### `browser_agent.py`

```
from bedrock_agentcore.tools.browser import BrowserTool, BrowserConfig
```

`#` II `Initialize managed browser tool` IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII `browser = BrowserTool( region="us-east-1", config=BrowserConfig( viewport={"width": 1920, "height": 1080}, user_agent="Mozilla/5.0 (compatible; AgentBot/1.0)", timeout_ms=30_000, screenshot_on_error=True,   # Auto-capture on failures ) ) #` II `Strands agent with browser capability` IIIIIIIIIIIIIIIIIIIIIIIIIIII `web_agent = Agent(`

```
    model=BedrockModel(model_id="us.anthropic.claude-sonnet-4-20250514"),
    system_prompt="""You are a web research agent.
    Use the browser to navigate websites and extract structured data.
    Always screenshot before and after complex interactions.
    If a page requires login, use the provided credentials tool first.""",
    tools=[
        browser.navigate,        # Navigate to URL
        browser.click,           # Click element by selector or description
```

```
        browser.type_text,       # Type into form fields
```

`browser.screenshot,      # Take screenshot` -> `returns base64 image browser.extract_content, # Extract text/data from current page browser.scroll,          # Scroll page browser.wait_for,        # Wait for element/condition ], ) #` II `Example: Multi-step web task` IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII `result = web_agent(""" Go to https://finance.yahoo.com/quote/AMZN. Extract the current stock price, P/E ratio, and 52-week range. Then navigate to the News tab and return the titles of the 5 latest articles. """)`

#### A5.3 Browser-Based Data Extraction Pattern

###### `browser_extraction.py`

`from strands import Agent, tool from bedrock_agentcore.tools.browser import BrowserTool import json browser = BrowserTool(region="us-east-1") #` II `Custom extraction tool: structured scraping with schema` IIIIIIIIIII `@tool def extract_product_catalog(url: str, max_products: int = 50) -> list: """Extract structured product catalog from e-commerce URL. Returns: list of {name, price, rating, sku, availability}.""" browser.navigate(url) browser.wait_for(".product-grid", timeout=10) # Let agent describe what it sees, extract structured data content = browser.extract_content( selector=".product-card", schema={ "name":         ".product-title", "price":        ".price-current", "rating":       ".star-rating[data-value]", "sku":          "[data-sku]", "availability": ".stock-status", }, max_items=max_products ) return content #` II `Agent uses browser for competitive pricing research` IIIIIIIIIIIIIII `pricing_agent = Agent( model="us.anthropic.claude-sonnet-4-20250514", system_prompt="""You are a competitive intelligence agent. Extract pricing data from competitor sites and produce comparison reports.""", tools=[extract_product_catalog, browser.navigate, browser.screenshot], )`

```
result = pricing_agent("Compare pricing for industrial pumps across these 3 competitors: [URLs]")
```

#### A5.4 Nova Act for Legacy System Automation

Amazon Nova Act extends browser automation to **legacy systems** that lack APIs — ERP portals, mainframe web wrappers, aged internal tools:

###### `nova_act_erp.py`

`# Nova Act: browser automation for systems without APIs # Available via: pip install amazon-nova-act-sdk from nova_act import NovaAct from strands import Agent, tool #` II `Wrap Nova Act as a Strands tool` IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII `@tool def automate_erp_portal(task: str, portal_url: str) -> dict: """Automate tasks in legacy ERP portal using visual AI navigation. Use for: data entry, form submission, report extraction in legacy systems.""" with NovaAct( starting_page=portal_url, headless=True,             # Server-side, no display needed logs_directory="/tmp/nova-act-logs", ) as nova: result = nova.act(task)    # Natural language instruction` -> `actions return { "success": result.succeeded, "output": result.response, "steps_taken": len(result.actions_taken), } #` II `Agent uses Nova Act for ERP data entry` IIIIIIIIIIIIIIIIIIIIIIIIIIII `erp_agent = Agent( model="us.anthropic.claude-sonnet-4-20250514", system_prompt="You automate data entry into legacy ERP systems.", tools=[automate_erp_portal], ) result = erp_agent( "Enter the following 50 purchase orders into SAP portal at https://erp.internal/sap: " + json.dumps(purchase_orders[:50]) )`

I **CHAPTER A6**
