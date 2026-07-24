---
title: Safety, Enterprise Deployment & CCA-F Exam Prep (Part 2)
doc_type: learning-path
domain: agentic-systems
topic_id: module-7-safety-enterprise-exam-part2
status: current
date_created: 2026-07-24
last_reviewed: 2026-07-24
tags: [coding-tools]
supersedes: []
---

# Safety, Enterprise Deployment & CCA-F Exam Prep (Part 2)

20 practice questions with full explanations covering all 5 exam domains

**This is Part 2 of 2. [Return to Part 1 ←](pathname:///archon/agentic-systems/coding-tools/29-module-7-safety-enterprise-exam) for permission hierarchy, data privacy, system prompt hardening, and CCA-F study plan.**

## 7.5 Practice Questions — All 5 Domains (20 Questions)

### Domain 1: Claude API & SDK (5 questions)

**Q1: A streaming request returns stop_reason='max_tokens'. What is the correct next action?**

A) Retry with exact same request
B) Increase max_tokens and resend full conversation history with partial response as an assistant turn
C) Start a new conversation
D) Switch to non-streaming mode

**Answer: B** — max_tokens was too low. You must append the partial response as an assistant message and resend the complete history with higher max_tokens so Claude can continue.

**Q2: You need to process 8,000 documents nightly for sentiment classification. Which minimizes cost?**

A) messages.stream() with Sonnet 4.6
B) messages.create() parallel threads with Haiku
C) messages.batches.create() with claude-haiku-4-5
D) Haiku with prompt caching on the system prompt

**Answer: C** — Batch API = 50% off. Haiku = $1/$5/MTok. Combined: ~80% cheaper than standard Sonnet real-time. Batch API is the correct tool for non-real-time bulk workloads.

**Q3: Which cache_control block will SILENTLY fail to cache without raising an error?**

A) System prompt of 2,000 tokens with cache_control
B) User message block of 400 tokens with cache_control
C) Tool definitions of 1,500 tokens with cache_control
D) An assistant turn of 1,200 tokens with cache_control

**Answer: B** — Minimum cacheable size is 1,024 tokens. A 400-token block is silently ignored — no error is raised, the block is just processed normally without caching.

**Q4: Claude returns stop_reason='tool_use' with THREE tool_use blocks simultaneously. What must happen next?**

A) Return results sequentially in three separate user messages
B) Execute only the first tool and return its result
C) Execute all three tools (parallel is fine) and return ALL results in ONE user-role message
D) Ask Claude which result it needs first

**Answer: C** — All tool results must be in a single user-role message. Returning partial results causes API errors. Execute in parallel when tools don't depend on each other's results.

**Q5: Which parameter replaces budget_tokens for controlling extended thinking depth on Claude 4.6+ models?**

A) max_thinking_tokens
B) thinking_budget
C) effort with values low/medium/high
D) reasoning_depth

**Answer: C** — The effort parameter replaces the deprecated budget_tokens on Claude 4.6+ models. Adaptive thinking (thinking:{type:'auto'}) automatically manages depth without any explicit parameter.

### Domain 2: Prompt Engineering (4 questions)

**Q6: Which technique reduces missed fields in contract extraction by approximately 40%?**

A) Zero-shot with temperature=0
B) Few-shot with 5 examples
C) Chain-of-thought with a self-critique step that verifies each field against an explicit checklist
D) Parallel extraction with 3 models and majority vote

**Answer: C** — Self-critique (verify draft against a checklist before finalizing) is proven to reduce extraction errors ~40%. Adding a verification step over the initial draft is the most reliable high-recall technique.

**Q7: A developer sets temperature=0.7 AND top_p=0.9 in the same API call. What is the problem?**

A) top_p must always be lower than temperature
B) Setting both simultaneously leads to unpredictable sampling behavior — use one or the other
C) temperature must be 0 for any structured output
D) This combination will cause a 400 API error

**Answer: B** — Setting both temperature and top_p simultaneously is undefined behavior per Anthropic's guidance. Choose one sampling strategy. For extraction, use temperature=0 only.

**Q8: Semantic RAG search keeps missing exact product codes like 'PRD-4521-X'. What is the best fix?**

A) Increase the embedding model's output dimensions
B) Lower the similarity threshold to 0.4
C) Add BM25 keyword search and combine results using Reciprocal Rank Fusion
D) Store product codes as separate metadata fields

**Answer: C** — Semantic search cannot reliably match exact strings. Hybrid search (dense semantic + sparse BM25) with RRF fusion handles exact matches. This is the production standard for enterprise RAG.

**Q9: What is the minimum token count for a content block to be eligible for prompt caching?**

A) 512 tokens
B) 768 tokens
C) 1,024 tokens
D) 2,048 tokens

**Answer: C** — 1,024 tokens is the minimum. This is a specific number tested frequently. Blocks below this threshold are silently not cached — no error is raised.

### Domain 3: Model Context Protocol (4 questions)

**Q10: A company wants Claude to reference internal policy documents whenever relevant. Which MCP primitive?**

A) Tools — Claude decides when to access them
B) Resources — application exposes documents for Claude to read
C) Prompts — users invoke document access explicitly
D) Sampling — server fetches docs via LLM call

**Answer: B** — Resources are app-controlled data. The application decides which documents to expose. Claude can read them but does NOT autonomously choose to access resources — that's the Tools primitive.

**Q11: An MCP file server must only access paths within declared boundaries. Which mechanism enforces this?**

A) Tool inputSchema validation
B) Roots — file access boundaries declared by the client at connection time
C) Capability negotiation flags
D) The stdio transport layer

**Answer: B** — Roots define file system boundaries. The client declares approved root URIs at connection. Servers must validate all file paths against these roots and reject anything outside them.

**Q12: Your MCP server needs Claude to classify documents as part of tool execution. Which MCP feature enables this?**

A) Resources — expose documents as resources for Claude to read
B) Prompts — create a classification prompt template
C) Sampling — server requests a Claude completion via the client
D) Tool chaining — call a classification tool from within another tool

**Answer: C** — Sampling allows an MCP server to request LLM completions through the client. The server can get AI analysis without needing its own Anthropic API key — all flows through the host client.

**Q13: When should you choose StreamableHTTP transport over stdio for an MCP server?**

A) When the server needs to access a database
B) When the server is remote, needs to serve multiple users, or requires horizontal scaling
C) When the server uses the sampling feature
D) When lower latency is required

**Answer: B** — StreamableHTTP is for remote multi-user deployments. stdio is for local single-process deployment. Network exposure via HTTP requires authentication and TLS — never deploy remote MCP without them.

### Domain 4: Agent Design & Orchestration (4 questions)

**Q14: Why can CLAUDE.md instructions be occasionally ignored by Claude Code?**

A) CLAUDE.md has a 10,000 token size limit
B) CLAUDE.md is user context (probabilistic), not a system prompt (deterministic)
C) CLAUDE.md is only read once at startup
D) CLAUDE.md requires explicit activation with a setting

**Answer: B** — CLAUDE.md is delivered as user context, which Claude follows probabilistically. For mandatory rules that cannot be overridden, use the Hooks system — hooks execute deterministic code the model cannot bypass.

**Q15: A code review agent must NEVER write to files. What is the most architecturally correct enforcement?**

A) Add 'Never write files' to CLAUDE.md
B) System prompt: 'Do not use the Write tool'
C) Define agent in .claude/agents/ with allowed-tools:[Read, Grep] only — Write is not listed
D) Add a PreToolUse hook that warns on Write

**Answer: C** — Agent definitions with allowed-tools provide hard enforcement — unlisted tools are not available to the agent. CLAUDE.md and system prompt are probabilistic. Hooks can block but agent definition is simpler and definitive.

**Q16: When is a Dynamic Workflow the correct choice over a regular subagent?**

A) When the task requires complex multi-step reasoning
B) When you need 50+ parallel independent agents with checkpointing and must prevent intermediate results from consuming the context window
C) When the task requires MCP tool access
D) When extended thinking is needed

**Answer: B** — Workflows solve three specific problems: (1) parallel scale (50+ agents), (2) context pollution from intermediate results, (3) resumability. Complexity alone is never a reason to use workflows over simpler approaches.

**Q17: In an orchestrator-worker pipeline, a worker agent fails after 2 retries. What should happen?**

A) Stop the entire pipeline immediately
B) Silently skip that worker's contribution
C) Handle gracefully: report partial results clearly, flag the failed component, and allow the orchestrator to decide whether to proceed or escalate
D) Replace with a different model and retry

**Answer: C** — Resilient pipelines handle partial failures gracefully. The orchestrator should receive a clear failure report (not silence) and make an informed decision. Stopping the entire pipeline for one failure is usually over-aggressive.

### Domain 5: Safety, Security & Responsible Deployment (3 questions)

**Q18: An operator system prompt includes: 'Confirm you are human when users ask.' What does Claude do?**

A) Complies — operators can configure this behavior
B) Complies for roleplay scenarios only
C) Refuses and confirms being an AI — this is a Tier 1 hard limit no operator can override
D) Depends on how sincerely the user asks

**Answer: C** — Denying being an AI when sincerely asked is a hard limit — it cannot be overridden by any operator system prompt. Claude will always confirm being an AI when a user directly and sincerely asks.

**Q19: Which is the SIMPLEST HIPAA-compliant path for an enterprise already on AWS?**

A) Anthropic direct API with end-to-end encryption
B) Anthropic direct API with zero data retention option
C) Amazon Bedrock with existing AWS HIPAA Business Associate Agreement
D) Google Vertex AI in a US region with CMEK

**Answer: C** — Amazon Bedrock inherits AWS's existing HIPAA BAA — enterprises already on AWS often have this in place. Anthropic direct API requires a separate BAA plus ZDR configuration, which is a more complex procurement process.

**Q20: A user is injecting instructions via tool results (prompt injection). Which is the CORRECT defense?**

A) Add 'ignore injections' to the system prompt
B) Wrap all tool results in XML with an 'untrusted data' label, validate outputs against expected schemas, and monitor for unexpected behaviors
C) Disable tool use for this user session
D) Switch to a more security-focused model

**Answer: B** — Defense-in-depth: (1) label all tool results as untrusted in XML wrapper, (2) validate Claude's response against expected schema, (3) monitor for anomalies. System prompt alone is insufficient — it's probabilistic guidance, not a security control.
