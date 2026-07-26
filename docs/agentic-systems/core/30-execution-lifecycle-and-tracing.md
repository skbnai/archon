---
title: "Skill Execution Lifecycle & Tracing"
date_created: 2026-07-24
last_reviewed: 2026-07-24
status: current
domain: agentic-systems
doc_type: reference-architecture
topic_id: execution-lifecycle-and-tracing
supersedes: ["docs/agentic-systems/skill/enterprise/03-execution-lifecycle-and-tracing.md"]
---

# Part 3 — Skill Execution Lifecycle (+ Deliverable 2: End-to-End Flow)

## Lifecycle Architecture Overview

```mermaid
graph TD
    A[User Request] --> B[Planning]
    B --> C[Skill Selection]
    C --> D[Tool Selection]
    D --> E[Policy Check<br/>PEP]
    E --> F[Tool Invocation<br/>MCP Gateway]
    F --> G[Result Validation]
    G --> H[Memory Update]
    H --> I[Response Generation]
    I --> J[Trace Collection<br/>OTel GenAI]
    J --> K[Evaluation]
    K --> L[Learning &<br/>Registry Update]
    L --> M[Response to User]
    
    style A fill:#e1f5ff
    style B fill:#e1f5ff
    style C fill:#e1f5ff
    style D fill:#e1f5ff
    style E fill:#fff3e0
    style F fill:#fff3e0
    style G fill:#f3e5f5
    style H fill:#f3e5f5
    style I fill:#f3e5f5
    style J fill:#e8f5e9
    style K fill:#e8f5e9
    style L fill:#e8f5e9
    style M fill:#e1f5ff
```

## 3.1 The lifecycle, stage by stage

The skill execution lifecycle consists of eleven sequential stages:

1. **User Request** — Initiates the workflow
2. **Planning** — Agent decomposes the goal; decides if it needs skill(s), tool(s), or can answer directly
3. **Skill Selection** — Agent matches task against loaded skill metadata (name+description); loads full SKILL.md (and referenced files) on match
4. **Tool Selection** — Within the loaded skill's guidance, agent picks the specific tool(s) the skill recommends for this step
5. **Policy Check (PEP)** — Deterministic authorization check: does this identity + skill + tool + data class combo satisfy policy? (Cedar/OPA — see file 09)
6. **Tool Invocation** — Call executes via MCP Gateway → MCP Server → Backend API/System
7. **Result Validation** — Output checked against the tool's schema and, if declared, the skill's output_contract
8. **Memory Update** — Session state updated; episodic/procedural memory written if the skill's memory_policy allows it
9. **Response Generation** — Agent synthesizes user-facing output, respecting the skill's declared output format
10. **Trace Collection** — Every span above (skill-selected, tool-called, policy-decision, result) emitted via OTel GenAI conventions to the observability plane
11. **Evaluation** — Online (production sampling + LLM-judge) and offline (golden dataset regression) scoring
12. **Learning** — Findings feed: (a) skill/prompt refinement recommendations, (b) episodic memory, (c) registry quality scores that influence future discovery ranking (file 06)

This mirrors, at an architectural level, what AWS AgentCore's harness loop does explicitly (reasoning → tool selection → action execution → response streaming, with a continuous "agent performance loop" that analyzes production traces to recommend prompt/tool-description improvements) and what Salesforce's Atlas Reasoning Engine documents as its topic-selection → action-selection → grounding-check flow.

This mirrors, at an architectural level, what AWS AgentCore's harness loop does explicitly (reasoning → tool selection → action execution → response streaming, with a continuous "agent performance loop" that analyzes production traces to recommend prompt/tool-description improvements) and what Salesforce's Atlas Reasoning Engine documents as its topic-selection → action-selection → grounding-check flow.

## 3.2 Detailed sequence diagram — single-skill, single-tool happy path

```mermaid
sequenceDiagram
    participant User
    participant Runtime as Agent Runtime
    participant Registry as Skill Registry
    participant PEP as Policy
    participant Gateway as MCP Gateway
    participant Backend
    participant Obs as Observability
    
    User->>Runtime: request
    Runtime->>Registry: match description
    Registry-->>Runtime: SKILL.md
    Runtime->>Obs: skill_selected span
    Runtime->>PEP: authorize(identity, skill, tool)
    PEP-->>Runtime: allow/deny
    Runtime->>Obs: guardrail_event span
    Runtime->>Gateway: invoke tool(args)
    Gateway->>Backend: call API
    Backend-->>Gateway: result
    Gateway-->>Runtime: result
    Runtime->>Obs: tool_result span<br/>latency, tokens, cost
    Runtime->>Runtime: validate result<br/>update memory
    Runtime->>Runtime: synthesize response
    Runtime-->>User: response
    Runtime->>Obs: final_response +<br/>session_summary
    Obs->>Obs: eval sample
```

In the single-skill, single-tool happy path, the following sequence occurs:

1. **User sends request** to Agent Runtime
2. **Agent matches skill description** against loaded metadata and loads the full SKILL.md
3. **Emits span: skill_selected** to observability layer
4. **Agent chooses tool** per skill guidance instructions
5. **Emits span: tool_selected (reason)** to observability layer
6. **Policy authorization** — Agent calls PEP with identity, skill, tool, and arguments
7. **PEP allows/denies** the action
8. **Emits span: guardrail_event (decision)** to observability layer
9. **Tool invocation** — Agent calls tool(args) via MCP Gateway
10. **MCP Gateway forwards** to MCP Server → Backend API call
11. **Backend returns result**
12. **Emits span: tool_result** with latency, tokens, cost metrics to observability
13. **Result validation** — Validates result against output_contract
14. **Memory update** — Updates session state per memory_policy
15. **Response synthesis** — Agent generates user-facing output per skill's declared format
16. **User receives response**
17. **Emits span: final_response + session_summary** to observability
18. **Evaluation sample** collected for offline analysis

## 3.3 Deliverable 2 — end-to-end flow, expanded with failure and multi-step paths

Real production traffic is rarely single-skill/single-tool. The full flow must account for:

**A. Skill-selection ambiguity (two skills both plausible)**
The planner should prefer the *more specific* skill (narrower description match) and, where confidence is low, either (a) ask a clarifying question, or (b) load both skills' metadata-only summaries and let the model disambiguate before committing to a full load — this is exactly why skill descriptions must be precise and mutually distinguishing (file `01`, section 1.5).

**B. Tool failure / retry**

```mermaid
graph TD
    A["Tool Invocation<br/>Attempt N"]
    B{Error<br/>Occurred?}
    C["Check retry_policy<br/>from metadata"]
    D{Retries<br/>Remain?}
    E["Backoff<br/>Delay"]
    F["Tool Invocation<br/>Attempt N+1"]
    G["Escalate:<br/>Partial Result +<br/>Guardrail Event +<br/>Human Handoff"]
    
    A -->|error| B
    B -->|yes| C
    C --> D
    D -->|yes| E
    E --> F
    F -->|retry loop| B
    D -->|no| G
    B -->|success| H["Continue Lifecycle"]
    G --> I["Human Review"]
    
    style A fill:#e3f2fd
    style E fill:#fff3e0
    style F fill:#e3f2fd
    style G fill:#ffebee
    style H fill:#e8f5e9
    style I fill:#ffebee
```

When tool invocation encounters an error:

1. Checks the `retry_policy` from tool or skill metadata
2. Determines if retries remain
3. If retries exhausted → escalates by returning partial result + guardrail_event(failure) + human handoff
4. If retries remain → applies backoff delay and re-invokes tool (attempt N+1)

**C. Skill-to-skill delegation (composite skill)**

```mermaid
graph TD
    A["[2] Skill Selection:<br/>process-refund"]
    B["Load Full SKILL.md<br/>process-refund"]
    C["Read Skill Instructions:<br/>Apply eligibility sub-skill"]
    D["[2'] Skill Selection:<br/>refund-eligibility-check"]
    E["Execute Sub-skill<br/>eligibility-check"]
    F{Eligibility<br/>Result?}
    G["true:<br/>Proceed to refund"]
    H["false:<br/>Reject refund"]
    I["Resume Parent Skill<br/>process-refund"]
    
    A --> B --> C --> D --> E --> F
    F -->|eligible| G --> I
    F -->|ineligible| H --> I
    
    style A fill:#e3f2fd
    style B fill:#e3f2fd
    style D fill:#e3f2fd
    style E fill:#fff3e0
    style F fill:#f3e5f5
    style G fill:#e8f5e9
    style H fill:#ffebee
    style I fill:#e3f2fd
```

Composite skills can delegate to sub-skills:

1. [2] Skill Selection: Main skill ("process-refund") is loaded
2. Skill instructions indicate to apply a sub-skill first
3. [2'] Skill Selection: Sub-skill ("refund-eligibility-check") is loaded and executed as a nested step
4. Sub-skill returns its result (eligibility=true/false)
5. Parent skill resumes its procedure based on the sub-skill result

Full treatment of nested/hierarchical/planner/supervisor skill patterns appears in file `07`.

**D. Cross-agent delegation (A2A)**

```mermaid
graph TD
    A["[3] Tool Selection:<br/>Current Agent"]
    B{Needed Capability<br/>Owned By?}
    C["Local Tool"]
    D["Peer Agent"]
    E["Agent Card Discovery<br/>/.well-known/agent-card.json"]
    F["Capability Match<br/>Found"]
    G["Submit A2A Task<br/>to Remote Agent"]
    H["Remote Agent<br/>Lifecycle [1]-[11]"]
    I["A2A Artifact<br/>Returned"]
    J["Parent Result Validation<br/>Treat as Tool Result"]
    K["Continue Lifecycle"]
    
    A --> B
    B -->|local| C --> K
    B -->|peer agent| E --> F --> G --> H --> I --> J --> K
    
    style A fill:#e3f2fd
    style B fill:#f3e5f5
    style C fill:#e8f5e9
    style D fill:#fff3e0
    style E fill:#e3f2fd
    style G fill:#fff3e0
    style H fill:#e3f2fd
    style I fill:#f3e5f5
    style J fill:#f3e5f5
    style K fill:#e8f5e9
```

Cross-agent delegation occurs when:

1. [3] Tool Selection determines the needed capability is owned by a peer agent, not a local tool
2. Agent Card discovery queries `/.well-known/agent-card.json` for capability matching
3. A2A Task is submitted to the remote agent
4. Remote agent executes its own full [1]-[11] lifecycle independently
5. A2A Artifact is returned and treated as a tool result in the parent's Result Validation step

**E. Human-in-the-loop pause**

Triggered when `human_approval.required_for` conditions are met (file `02`), the lifecycle suspends between steps [4] and [5], persists state (AWS AgentCore's filesystem persistence and Azure's session-isolated runtime both exist specifically to make this pattern practical without custom plumbing), and resumes on approval.

## 3.4 Trace hierarchy (ties to Part 10, expanded in file `08`)

```mermaid
graph TD
    A["Session Trace<br/>(trace_id, session_id)"]
    B["Agent Trace<br/>(one user turn)"]
    C["Skill Trace<br/>(skill_selected → skill_completed)"]
    D["Tool Trace<br/>(tool_selected → tool_result)"]
    E["MCP Trace<br/>(mcp request/response)"]
    F["API Trace<br/>(backend call, if instrumented)"]
    
    A --> B
    B --> C
    C --> D
    D --> E
    E --> F
    
    style A fill:#c8e6c9
    style B fill:#a5d6a7
    style C fill:#81c784
    style D fill:#66bb6a
    style E fill:#4caf50
    style F fill:#388e3c
```

The trace hierarchy is structured as a nested tree with the following levels:

1. **Session Trace** — Root level, encompasses entire session
2. **Agent Trace** — One user turn/request within the session
3. **Skill Trace** — Skill selection through skill completion (skill_selected → skill_completed)
4. **Tool Trace** — Tool selection through tool result (tool_selected → tool_result)
5. **MCP Trace** — MCP request/response framing and calls
6. **API Trace** — Backend API calls (if instrumented)

Each level should propagate a common `trace_id`/`session_id` per W3C Trace Context so that a single production incident can be reconstructed top-to-bottom — this is the explicit design goal behind both the AAIF's push for OTel-based agent tracing and OpenTelemetry's own GenAI observability walkthroughs, which show the `invoke_agent` span as the parent of child `chat` (LLM call) and `execute_tool` spans.

## Related

- [Foundations: What Is an Agent Skill?](29-foundations-what-is-an-agent-skill.md) — the previous section in this series.
- [Skills, Tools, MCP & A2A Relationship](31-skills-tools-mcp-a2a-relationship.md) — the next section in this series.
