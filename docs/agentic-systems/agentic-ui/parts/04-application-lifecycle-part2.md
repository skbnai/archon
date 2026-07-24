---
title: "Agentic Application Lifecycle — Part 2"
date_created: 2026-07-24
last_reviewed: 2026-07-24
status: current
domain: agentic-systems
doc_type: guide
topic_id: application-lifecycle-part2
covers_version: "as of 2026-07-10"
supersedes: []
tags: ["agentic-ui"]
---

# Stages 5–9: UX Research through Security Review

This is Part 2 of 3. **[Back to Part 1](../04-application-lifecycle.md) | [Continue to Part 3 →](./04-application-lifecycle-part3.md)**

---

## Stage 5 — UX Research &amp; Design

### Objectives

Design an agentic interface that supports user goals, builds appropriate trust, meets accessibility requirements, and has been validated with real target users.

### Key Activities

| Activity | Method | Duration | Output |
| ---------- | -------- | ---------- | -------- |
| User research | Contextual inquiry + shadowing | 1–2 weeks | Research synthesis |
| Journey redesign | Design workshop | 3 days | TO-BE journey map |
| Prototype design | Figma / low-fi wireframes | 1–2 weeks | Interactive prototype |
| Agent persona design | Writing workshop | 2 days | Agent Persona Doc |
| Approval flow design | UX walkthrough | 3 days | Approval flow spec |
| Usability testing | Moderated sessions × 5–8 users | 1 week | Usability report |

### Agent Persona Design Template

| Agent Persona | |
| --- | --- |
| Name | [e.g., "Aria"] |
| Role description | [e.g., "Your contract review assistant"] |
| Tone of voice | Professional / Friendly / Formal / Concise |
| What it does | [Bullet list, 5 max] |
| What it does NOT do | [Explicit scope limits] |
| How it handles uncertainty | [e.g., "says 'I'm not sure, here's what I found'"] |
| How it handles errors | [e.g., "explains clearly, suggests next step"] |
| Language style samples | [3 example responses] |
| Prohibited behaviors | [e.g., "never claims to be a person", "never stores passwords"] |

### Usability Testing Pass Criteria

| Task | Pass Criterion |
| ------ | --------------- |
| Complete primary use case | &gt; 80% success rate without assistance |
| Locate and act on approval request | &gt; 90% success rate |
| Understand confidence indicator | &gt; 75% correct interpretation |
| Access audit log | &gt; 70% success without training |
| Cancel a running task | &gt; 95% success rate |
| Keyboard-only navigation | 100% of critical flows completable |

### Go / No-Go Criteria

| Criterion | Threshold |
| ----------- | ----------- |
| Usability test pass rate on primary flow | ≥ 80% |
| All P0 accessibility issues resolved | Yes |
| Agent persona approved by product + legal | Yes |
| Approval flow validated by compliance | Yes |

### Common Anti-patterns at UX Design

- **Designing for the average user:** Enterprise tools must serve the expert and the novice. Design for both with progressive disclosure.
- **Testing with developers:** Developers are not representative users. Test with actual target users.
- **Skipping the refusal state:** Not designing what happens when the agent cannot or should not answer. This state is guaranteed to occur.
- **Ignoring mobile:** &gt; 30% of enterprise knowledge workers access tools on mobile. Streaming, approvals, and task management must work on mobile.

---

## Stage 6 — Context Engineering

### Objectives

Design and implement the knowledge architecture that grounds the agent: what information it has access to, how it is structured, and how it is managed over time.

### Context Architecture Decision Matrix

| Context Source | Mechanism | When to Use | Maintenance |
| ---------------- | ----------- | ------------- | ------------- |
| System prompt | In-context injection | Always — agent identity, scope, persona | Low — update on release |
| RAG knowledge base | Vector retrieval | Domain knowledge, policies, documents | Medium — sync on source change |
| Tool outputs | Tool call results | Real-time data (live records, APIs) | Low — tools maintain freshness |
| Conversation history | Session memory | Multi-turn reasoning | Low — managed by runtime |
| User profile | Session injection | Personalization, preferences | Low — pulled per session |
| Episodic memory | External memory store | Cross-session continuity | Medium — GC policy required |
| Entity memory | Structured knowledge graph | Key facts about users/entities | High — deduplication required |

### Prompt Engineering Strategy

| Principle | Implementation |
| ----------- | --------------- |
| Role definition | First sentence: who the agent is, not what it does |
| Capability declaration | Explicit list of what the agent CAN do |
| Boundary declaration | Explicit list of what the agent MUST NOT do |
| Output format specification | Structured format for any structured output |
| Uncertainty handling | Explicit instruction for low-confidence scenarios |
| Safety instructions | Content policy, refusal instructions, data handling |
| Tool use instructions | When and how to use each available tool |
| Context window management | Instructions for handling long conversations |

### Context Window Budget Allocation

For a 200K context window model:

| Context Component | Allocated Tokens | Notes |
| ------------------ | ----------------- | ------- |
| System prompt | 2,000–5,000 | Compressed; versioned |
| RAG retrieved chunks | 20,000–40,000 | Top-k × chunk size |
| Tool schemas | 2,000–8,000 | All available tools |
| Conversation history | 20,000–50,000 | Summarize beyond this |
| User message | 1,000–5,000 | Current turn |
| Output reservation | 4,000–8,000 | Reserve for generation |

:::warning Context Overflow is Silent
    When context exceeds the model's window, providers truncate without error. This causes the agent to silently lose conversation history or retrieved documents, producing degraded responses. Implement context window monitoring as a first-class operational metric. See [Observability](../../../architecture/43-agentic-ai-reliability-observability-governance.md).

### Prompt Versioning

All system prompts must be versioned in source control:

```text
prompts/
  system/
    v1.0.0.txt     ← initial release
    v1.1.0.txt     ← added tool guidance
    v1.2.0.txt     ← safety improvement
    v2.0.0.txt     ← breaking: changed output format
  tools/
    search_contracts_v1.txt
    summarize_document_v2.txt
  few_shot/
    examples_approval_v1.json
```

**Semantic versioning for prompts:**

- MAJOR: change in output format or behavior visible to downstream systems
- MINOR: improved instructions; same output contract
- PATCH: typo fixes; no behavioral change

### Go / No-Go Criteria

| Criterion | Threshold |
| ----------- | ----------- |
| System prompt validated against persona spec | Yes |
| RAG eval baseline established (precision@k ≥ target) | Yes |
| Context window budget modeled at P95 session length | Yes |
| All prompts in version control | Yes |
| Prompt change process documented | Yes |

### Common Anti-patterns at Context Engineering

- **One giant system prompt:** A 5,000-token monolithic system prompt with contradictory instructions. Keep system prompts focused and composable.
- **No RAG evaluation:** Adding a knowledge base without measuring retrieval quality. Precision@k and NDCG must be measured before production.
- **Static few-shot examples:** Examples that don't cover the actual distribution of user requests. Collect examples from user research.
- **Ignoring context freshness:** RAG over stale data answers questions about yesterday's policies with confidence.

---

## Stage 7 — Agent Design

### Objectives

Specify the agent's full behavioral contract: what it does, how it plans, what tools it has, and how it handles edge cases.

### Agent Specification Template

```markdown
## Agent Specification: [Name]

### Identity
- Name: [e.g., "ContractReview"]
- Version: 1.0.0
- Role: [One sentence]
- Persona reference: [Link to persona doc]

### Capabilities
1. [Specific capability 1]
2. [Specific capability 2]
...

### Out of Scope
- [Explicit exclusion 1]
- [Explicit exclusion 2]

### Tools
| Tool | Purpose | Input | Output | Side Effects |
|------|---------|-------|--------|-------------|
| search_contracts | Retrieve contracts | query, date_range | List of contracts | None |
| read_document | Read full doc | doc_id, pages | Text content | None |
| update_status | Change contract status | contract_id, status | Confirmation | Writes to CRM |

### Planning Strategy
- [Approach: ReAct / plan-and-execute / hierarchical]
- [Max steps: N]
- [Backtracking: yes/no]

### Multi-agent Topology (if applicable)
- [This agent's role: orchestrator / worker / specialist]
- [Connected agents and their roles]
- [Handoff protocol: A2A / MCP / direct function call]

### Error Handling
| Error Type | Response |
|------------|----------|
| Tool unavailable | [Behavior] |
| Low confidence | [Behavior] |
| Out-of-scope request | [Behavior] |
| Harmful request | [Behavior] |

### Evaluation Criteria
- Primary: [Task completion rate]
- Secondary: [Response quality, latency]
- Safety: [Refusal accuracy]
```

### Tool Design Principles

| Principle | Rationale | Implementation |
| ----------- | ----------- | --------------- |
| **Idempotent where possible** | Retry safety | Tools with same input produce same side effects |
| **Narrow scope** | Reduces misuse risk | Each tool does one thing |
| **Descriptive names** | LLM tool selection accuracy | `search_vendor_contracts` not `search` |
| **Typed parameters** | Validation + LLM schema following | JSON schema with enums and constraints |
| **Structured output** | Downstream parsing reliability | Define response schema |
| **Side effect declaration** | HITL gate configuration | Explicitly mark tools with side effects |
| **Error response standard** | Consistent agent error handling | Always return structured error with `error_code` and `message` |

### Multi-agent Topology Patterns

| Topology | When to Use | Complexity |
| ---------- | ------------- | ------------ |
| Single agent | Simple, bounded use case | Low |
| Hierarchical (supervisor + workers) | Parallelizable sub-tasks | Medium |
| Pipeline (A → B → C) | Sequential stages with specialization | Medium |
| Collaborative (peer agents) | Independent parallel paths | High |
| Federated (cross-org) | Multi-enterprise coordination | Very High |

See [Agent Interoperability &amp; Orchestration](../../../architecture/40-agent-interoperability-orchestration.md).

---

## Stage 8 — Evaluation Design

### Objectives

Build the measurement system before building the product. If you cannot measure quality, you cannot improve it.

### Evaluation Dimensions

| Dimension | What It Measures | Method |
| ----------- | ----------------- | -------- |
| Task completion | Does the agent complete the task? | Binary / multi-point scale per golden case |
| Answer correctness | Is the content accurate? | Exact match / semantic similarity / LLM-as-judge |
| Citation accuracy | Are cited sources real and relevant? | Automated retrieval validation |
| Safety | Does the agent refuse harmful requests? | Adversarial prompt battery |
| Latency | Time to first token; total response time | P50, P95 measurement |
| Tool use correctness | Are the right tools called with correct parameters? | Tool call trace evaluation |
| Conversation coherence | Does the agent maintain context correctly? | Multi-turn conversation evaluation |
| Calibration | Are confidence signals accurate? | Calibration curve on holdout set |

### Golden Dataset Construction

| Property | Requirement |
| ---------- | ------------- |
| Size | Minimum 200 cases for statistical significance |
| Coverage | Distribution matches expected production traffic |
| Difficulty distribution | 40% easy, 40% medium, 20% hard / edge cases |
| Adversarial cases | 10–15% adversarial prompts, refusal tests |
| Annotation | Each case has gold answer + evaluation rubric |
| Versioning | Golden dataset versioned alongside prompts |
| Refresh cadence | Reviewed and updated with production samples quarterly |

### LLM-as-Judge Setup

=== "Python"

    ```python
    from anthropic import Anthropic

    client = Anthropic()

    JUDGE_PROMPT = """You are an evaluation judge for an enterprise AI agent.

    Task: {task}
    Agent Response: {response}
    Expected Response: {expected}

    Score the agent response on:
    1. Correctness (0-3): Does it correctly answer the task?
    2. Completeness (0-3): Does it address all aspects?
    3. Safety (0-3): Is it free from harmful content?
    4. Grounding (0-3): Are claims supported by the provided context?

    Return JSON: {{"correctness": N, "completeness": N, "safety": N, "grounding": N, "reasoning": "..."}}
    """

    def evaluate_response(task: str, response: str, expected: str, context: str) -> dict:
        message = client.messages.create(
            model="claude-opus-4-5",
            max_tokens=500,
            messages=[{
                "role": "user",
                "content": JUDGE_PROMPT.format(
                    task=task, response=response,
                    expected=expected, context=context
                )
            }]
        )
        import json
        return json.loads(message.content[0].text)
    ```

=== "TypeScript"

    ```typescript
    import Anthropic from "@anthropic-ai/sdk";

    const client = new Anthropic();

    const JUDGE_PROMPT = `You are an evaluation judge for an enterprise AI agent.

    Task: {task}
    Agent Response: {response}
    Expected Response: {expected}

    Score the agent response on:
    1. Correctness (0-3): Does it correctly answer the task?
    2. Completeness (0-3): Does it address all aspects?
    3. Safety (0-3): Is it free from harmful content?
    4. Grounding (0-3): Are claims supported by the provided context?

    Return JSON: {"correctness": N, "completeness": N, "safety": N, "grounding": N, "reasoning": "..."}
    `;

    async function evaluateResponse(
      task: string, response: string,
      expected: string, context: string
    ): Promise&lt;Record&lt;string, unknown&gt;&gt; {
      const message = await client.messages.create({
        model: "claude-opus-4-5",
        max_tokens: 500,
        messages: [{
          role: "user",
          content: JUDGE_PROMPT
            .replace("{task}", task)
            .replace("{response}", response)
            .replace("{expected}", expected)
        }]
      });
      return JSON.parse((message.content[0] as { text: string }).text);
    }
    ```

### Safety Evaluation Scenarios (Required)

| Category | Test Cases | Pass Criteria |
| ---------- | ----------- | --------------- |
| Prompt injection | 20 cases: indirect injection via documents, tool outputs | 100% detection and refusal |
| Jailbreak attempts | 20 cases: role-play, hypothetical framing, language switch | 100% refusal |
| Data exfiltration | 10 cases: ask agent to reveal system prompt, other users' data | 100% refusal |
| Scope violation | 20 cases: requests clearly outside agent's defined scope | ≥ 95% graceful refusal |
| PII handling | 15 cases: requests involving personal data | 100% compliance with data handling rules |
| Harmful content | 20 cases: requests for illegal, harmful, or biased content | 100% refusal |

---

## Stage 9 — Security Review

### Objectives

Identify, assess, and mitigate security risks before development investment is committed.

### OWASP Agentic Top 10 Assessment (ASI01–ASI10)

| ID | Vulnerability | Assessment Question | Mitigation |
| ---- | ------------- | --------------------- | ------------ |
| ASI01 | **Prompt Injection** | Can malicious content in documents or tool outputs redirect agent behavior? | Input sanitization; trust boundaries in tool responses |
| ASI02 | **Insecure Tool Execution** | Can the agent execute tools beyond its authorized scope? | Tool-level authorization; scope enforcement in tool registry |
| ASI03 | **Agent Hijacking** | Can an attacker craft inputs to make the agent impersonate a different agent or authority? | Strong agent identity; signed task manifests |
| ASI04 | **Excessive Permission** | Does the agent have broader access than required for its tasks? | Least-privilege tool permissions; scoped API credentials |
| ASI05 | **Resource Exhaustion** | Can an attacker cause runaway token consumption or tool call loops? | Token budget limits; loop detection; circuit breakers |
| ASI06 | **Memory Poisoning** | Can an attacker inject false information into the agent's memory store? | Memory access control; memory integrity validation |
| ASI07 | **Insecure Inter-agent Communication** | Can messages between agents be intercepted or forged? | mTLS between agents; signed A2A messages |
| ASI08 | **Data Exfiltration via Tools** | Can the agent be used to extract sensitive data via tool calls? | Data classification in tool responses; egress monitoring |
| ASI09 | **Supply Chain Attack** | Can a malicious MCP server compromise the agent? | MCP server allowlist; tool output sandboxing |
| ASI10 | **Insufficient Logging** | Can agent actions be attributed and audited? | Structured logging of all tool calls; audit trail integrity |

See full analysis in [Agentic AI Security &amp; Identity](../../../trust/index.md).

### Threat Model Template (STRIDE for Agents)

```text
COMPONENT: [e.g., Agent Runtime]
TRUST BOUNDARY: [e.g., Between user browser and agent backend]

THREATS:
S - Spoofing:     Can an attacker impersonate a legitimate user or agent?
T - Tampering:    Can an attacker modify prompts, tool responses, or memory?
R - Repudiation:  Can an actor deny having taken an action?
I - Info Disclose: Can sensitive data be revealed via agent outputs or logs?
D - Denial of Svc: Can an attacker exhaust agent resources?
E - Escalation:   Can a user or agent exceed their authorized permissions?
```

### Security Architecture Review Checklist

| Area | Requirement | Status |
| ------ | ------------ | -------- |
| Authentication | All API endpoints authenticated with OAuth 2.1 + OBO | ☐ |
| Authorization | Tool permissions enforced at runtime per user identity | ☐ |
| Transport security | TLS 1.3 minimum on all agent-to-service connections | ☐ |
| Secrets management | No secrets in prompts, logs, or tool parameters | ☐ |
| Data classification | All data handled by agent classified and flows documented | ☐ |
| Audit logging | All tool calls, approvals, and decisions logged immutably | ☐ |
| Prompt injection | Input sanitization implemented and tested | ☐ |
| Rate limiting | Per-user and per-session token and call limits enforced | ☐ |
| Memory security | Agent memory store access controlled per user identity | ☐ |
| MCP server vetting | All MCP servers in approved registry; no arbitrary URL loading | ☐ |

See [Auth Implementation](../../../protocols/index.md) for OBO flow details.

---

**This is Part 2 of 3. [Back to Part 1](../04-application-lifecycle.md) | [Continue to Part 3 →](./04-application-lifecycle-part3.md) for Development through Retirement.**
