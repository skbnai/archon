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
---

# Stages 6–11: Design through Testing

This is Part 2 of 3. **[Back to Part 1](pathname:///archon/agentic-systems/agentic-ui/04-application-lifecycle) · [Continue to Part 3 →](pathname:///archon/agentic-systems/agentic-ui/parts/04-application-lifecycle-part3)**

## Stage 6 — Context Engineering

Design and implement the knowledge architecture that grounds the agent: what information it has access to, how it is structured, and how it is managed over time.

### Context Architecture Decision Matrix

| Context Source | Mechanism | When to Use | Maintenance |
| --- | --- | --- | --- |
| System prompt | In-context injection | Always — agent identity, scope, persona | Low — update on release |
| RAG knowledge base | Vector retrieval | Domain knowledge, policies, documents | Medium — sync on source change |
| Tool outputs | Tool call results | Real-time data (live records, APIs) | Low — tools maintain freshness |
| Conversation history | Session memory | Multi-turn reasoning | Low — managed by runtime |
| User profile | Session injection | Personalization, preferences | Low — pulled per session |
| Episodic memory | External memory store | Cross-session continuity | Medium — GC policy required |
| Entity memory | Structured knowledge graph | Key facts about users/entities | High — deduplication required |

### Prompt Engineering Strategy

- **Role definition:** First sentence specifies who the agent is, not what it does
- **Capability declaration:** Explicit list of what agent CAN do
- **Boundary declaration:** Explicit list of what agent MUST NOT do
- **Output format specification:** Structured format for any structured output
- **Uncertainty handling:** Explicit instruction for low-confidence scenarios
- **Safety instructions:** Content policy, refusal instructions, data handling
- **Tool use instructions:** When and how to use each available tool
- **Context window management:** Instructions for handling long conversations

### Context Window Budget Allocation

For a 200K context window model: system prompt (2,000–5,000), RAG retrieved chunks (20,000–40,000), tool schemas (2,000–8,000), conversation history (20,000–50,000), user message (1,000–5,000), output reservation (4,000–8,000).

### Go / No-Go Criteria

- System prompt validated against persona spec
- RAG eval baseline established (precision@k ≥ target)
- Context window budget modeled at P95 session length
- All prompts in version control
- Prompt change process documented

### Common Anti-patterns

- One giant system prompt: 5,000-token monolithic prompt with contradictory instructions
- No RAG evaluation: Adding knowledge base without measuring retrieval quality
- Static few-shot examples: Examples that don't cover actual distribution of requests
- Ignoring context freshness: RAG over stale data answers yesterday's policies with confidence

---

## Stage 7 — Agent Design

Specify the agent's full behavioral contract: what it does, how it plans, what tools it has, and how it handles edge cases.

### Agent Specification Template

- **Identity:** Name, version, role (one sentence), persona reference
- **Capabilities:** Bulleted list of specific capabilities
- **Out of Scope:** Explicit exclusions
- **Tools:** Table with tool name, purpose, input, output, side effects
- **Planning Strategy:** ReAct / plan-and-execute / hierarchical; max steps; backtracking
- **Multi-agent Topology:** Role, connected agents, handoff protocol
- **Error Handling:** Error type → response mapping
- **Evaluation Criteria:** Primary, secondary, safety metrics

### Tool Design Principles

- **Idempotent where possible:** Same input produces same side effects
- **Narrow scope:** Each tool does one thing  
- **Descriptive names:** `search_vendor_contracts` not `search`
- **Typed parameters:** JSON schema with enums and constraints
- **Structured output:** Define response schema
- **Side effect declaration:** Mark tools with side effects for HITL configuration
- **Error response standard:** Structured error with `error_code` and `message`

### Multi-agent Topology Patterns

| Topology | When to Use | Complexity |
| --- | --- | --- |
| Single agent | Simple, bounded use case | Low |
| Hierarchical (supervisor + workers) | Parallelizable sub-tasks | Medium |
| Pipeline (A → B → C) | Sequential stages with specialization | Medium |
| Collaborative (peer agents) | Independent parallel paths | High |
| Federated (cross-org) | Multi-enterprise coordination | Very High |

---

## Stage 8 — Evaluation Design

Build the measurement system before building the product. If you cannot measure quality, you cannot improve it.

### Evaluation Dimensions

| Dimension | What It Measures | Method | Target |
| --- | --- | --- | --- |
| Task completion | Does agent complete the task? | Binary / multi-point per golden case | ≥ 92% |
| Answer correctness | Is the content accurate? | Exact match / semantic similarity / LLM-as-judge | ≥ 92% |
| Citation accuracy | Are cited sources real and relevant? | Automated retrieval validation | ≥ 95% |
| Safety | Does agent refuse harmful requests? | Adversarial prompt battery | 100% refusal |
| Latency | Time to first token; total response time | P50, P95 measurement | P50 &lt; 800ms |
| Tool use correctness | Right tools called with correct parameters? | Tool call trace evaluation | ≥ 97% |
| Conversation coherence | Does agent maintain context correctly? | Multi-turn conversation evaluation | ≥ 90% |
| Calibration | Are confidence signals accurate? | Calibration curve on holdout set | ≤ 0.15 calibration error |

### Golden Dataset Construction

- **Size:** Minimum 200 cases for statistical significance
- **Coverage:** Distribution matches expected production traffic
- **Difficulty:** 40% easy, 40% medium, 20% hard/edge cases
- **Adversarial:** 10–15% adversarial prompts, refusal tests
- **Annotation:** Each case has gold answer + evaluation rubric
- **Versioning:** Versioned alongside prompts
- **Refresh cadence:** Reviewed and updated quarterly with production samples

### Safety Evaluation Scenarios (Required)

- **Prompt injection:** 20 cases indirect injection via documents/tool outputs → 100% detection and refusal
- **Jailbreak attempts:** 20 cases role-play, hypothetical framing → 100% refusal
- **Data exfiltration:** 10 cases requesting system prompt or other users' data → 100% refusal
- **Scope violation:** 20 cases clearly outside scope → ≥ 95% graceful refusal
- **PII handling:** 15 cases involving personal data → 100% compliance with rules
- **Harmful content:** 20 cases requesting illegal/biased/harmful → 100% refusal

---

## Stage 9 — Security Review

Identify, assess, and mitigate security risks before development investment is committed.

### OWASP Agentic Top 10 (ASI01–ASI10)

| ID | Vulnerability | Assessment Question | Mitigation |
| --- | --- | --- | --- |
| ASI01 | Prompt Injection | Can malicious content in documents redirect behavior? | Input sanitization; trust boundaries |
| ASI02 | Insecure Tool Execution | Can agent execute tools beyond authorized scope? | Tool-level authorization; scope enforcement |
| ASI03 | Agent Hijacking | Can attacker make agent impersonate different authority? | Strong identity; signed task manifests |
| ASI04 | Excessive Permission | Does agent have broader access than required? | Least-privilege permissions; scoped credentials |
| ASI05 | Resource Exhaustion | Can attacker cause runaway token consumption? | Token budgets; loop detection; circuit breakers |
| ASI06 | Memory Poisoning | Can attacker inject false information into memory? | Memory access control; integrity validation |
| ASI07 | Insecure Inter-agent Communication | Can messages between agents be intercepted/forged? | mTLS; signed A2A messages |
| ASI08 | Data Exfiltration via Tools | Can agent extract sensitive data via tools? | Data classification in responses; egress monitoring |
| ASI09 | Supply Chain Attack | Can malicious MCP server compromise agent? | MCP allowlist; tool output sandboxing |
| ASI10 | Insufficient Logging | Can agent actions be attributed and audited? | Structured logging of all tool calls; audit trail integrity |

### Security Architecture Review Checklist

- Authentication: OAuth 2.1 + OBO on all endpoints
- Authorization: Tool permissions enforced at runtime per identity
- Transport security: TLS 1.3 minimum
- Secrets management: No secrets in prompts, logs, or tool parameters
- Data classification: All data handled classified; flows documented
- Audit logging: All tool calls logged immutably with identity + decision
- Prompt injection: Input sanitization implemented and tested
- Rate limiting: Per-user and per-session token/call limits enforced
- Memory security: Memory store access controlled per identity
- MCP server vetting: All servers in approved registry; no arbitrary URL loading

---

## Stage 10 — Development

### Sprint Structure for Agentic Applications

Agentic apps require modified sprints because prompts iterate differently from code.

| Sprint Phase | Activities | Artifacts |
| --- | --- | --- |
| **Sprint planning** | User story prioritization + prompt hypothesis | Sprint goal + prompt experiment plan |
| **Day 1–3: Scaffold** | Agent framework setup, tool stubs, eval harness | Working agent shell |
| **Day 4–7: Prompt iteration** | Experiment with prompt variations; run eval | Eval results per variant |
| **Day 8–9: Tool implementation** | Build and unit-test each tool | Tool test suite |
| **Day 10: Integration test** | End-to-end agent test with all tools | Integration test results |
| **Sprint review** | Demo against acceptance criteria | Reviewed increment |

### Agent Unit Testing Patterns

Test that the agent calls correct tool for given intent, refuses out-of-scope requests, handles tool failure gracefully, and maintains conversation context across turns.

---

## Stage 11 — Testing

### Testing Pyramid for Agentic Applications

From base to top: eval harness (automated, regression) + unit testing (mocked LLM), integration testing (end-to-end with real LLM), UX testing (usability, accessibility), red team (manual adversarial).

### Red Team Exercise Requirements

- Prompt injection via user input: 50 cases → 0 successful injections
- Prompt injection via tool output: 20 cases → 0 successful
- Data exfiltration attempts: 20 cases → 0 successful
- Scope violation (off-topic harmful): 30 cases → ≥ 97% refusal
- Persona override attempts: 15 cases → 0 successful
- Automated jailbreak suite: 100 cases (PyRIT or Garak) → ≥ 99% refusal

### Performance Testing Requirements

- P50 time to first token (10 concurrent): &lt; 800ms
- P95 time to first token (50 concurrent): &lt; 3 seconds
- P99 total response time (100 concurrent): &lt; 30 seconds
- Throughput at SLA: Sustained load, 0 HTTP 429 errors
- Cost per interaction: 1000 sessions within ±20% of business case

---

**This is Part 2 of 3. [Back to Part 1](pathname:///archon/agentic-systems/agentic-ui/04-application-lifecycle) · [Continue to Part 3 →](pathname:///archon/agentic-systems/agentic-ui/parts/04-application-lifecycle-part3) for Deployment through Retirement.**
