---
title: "AI Fluency Cheat Sheet"
doc_type: guide
domain: agentic-systems
topic_id: cheatsheet-4-ai-fluency
status: current
date_created: 2026-07-24
last_reviewed: 2026-07-24
supersedes:
  - docs/coding-tools/claude/Cheatsheet_4_AI_Fluency.md
---

# AI Fluency Cheat Sheet

Large Language Models - Tokens - Context - Capabilities &amp; Limitations - Production Patterns

**ALL DOMAINS - FOUNDATIONAL**

## LLM Architecture Fundamentals

- **Transformer:** Architecture underlying all modern LLMs. Self-attention allows parallel processing and long-range dependencies.
- **Token:** Unit of text (≈¾ of a word). Models think in tokens, not words. "Claude" = 1 token. "Anthropic" = 2-3 tokens.
- **Context window:** Maximum tokens the model can "see" at once (input + output). Everything outside is invisible to the model.
- **Inference:** Running the model to generate output. Each forward pass predicts the next token probabilistically.
- **Temperature:** Controls randomness. 0 = deterministic (always most likely). 1 = more creative. Production: usually 0-0.3 for consistency.
- **Hallucination:** Model generates plausible-sounding but incorrect information. Common with: rare facts, specific numbers, citations.
- **System prompt:** Instructions sent before user message. Sets context, persona, constraints. High influence on behavior.
- **Few-shot:** Including examples in the prompt to guide model behavior. More examples = more consistent output format.

## Context Window Management

### Context = What the model can "see"

- **Input tokens:** System prompt + conversation history + tool results + user message
- **Output tokens:** Generated response + tool call parameters (counted separately)
- **Window limit:** Total input + output must fit. Exceeding truncates or errors.
- **Lost = invisible:** Content outside window is completely inaccessible — model cannot reason about it

### Strategies for Long Content

- **Chunking:** Break document into segments. Process each chunk. Re-assemble results.
- **Summarization:** Compress earlier conversation/docs into summaries to free space
- **RAG:** Retrieval-augmented generation — retrieve only relevant chunks via search
- **Selective retention:** Keep relevant turns, prune resolved subtopics from history

### 3 Context Challenges (Exam Key)

- 📄 **Long documents**
- 💬 **Multi-turn conversations**
- 🤝 **Multi-agent handoffs**

**✓ Context poisoning:** stale/incorrect info from earlier turns contaminating current reasoning → prune proactively

## Model Capabilities

### Strong At

- Reasoning — multi-step logic, inference
- Code — generation, review, debugging, refactoring
- Summarization — compressing long content
- Structured extraction — pulling data from text
- Translation — natural and programming languages
- Following instructions — schemas, formats, rules
- Role-following — maintaining context across turns
- Tool use — calling tools based on descriptions

### Key Strengths for Production

- Consistent with explicit schemas
- Good at self-evaluation of format
- Effective at decomposing complex tasks

## Model Limitations

### Known Weaknesses

- Hallucination — invents plausible but wrong facts
- Knowledge cutoff — no real-time information
- Math precision — unreliable for exact arithmetic
- No persistent memory — each call is stateless
- Context window cap — hard limit on input size
- Inconsistency — same prompt can yield different outputs
- Sycophancy — may agree with user even when wrong
- Prompt sensitivity — small wording changes affect output

### Production Mitigations

- Schema validation to catch format errors
- Human-in-the-loop for high-stakes decisions
- Self-evaluation patterns (format/completeness only)
- Deterministic hooks for guaranteed compliance

## Production Reliability Patterns

- **Structured output:** JSON schemas + validation prevent format errors in downstream systems
- **Human-in-loop:** Pause at high-stakes decision points for human approval
- **Self-evaluation:** Agent checks own output — use for FORMAT/COMPLETENESS, not fact accuracy
- **Hooks:** Deterministic compliance — guaranteed, not probabilistic like prompts
- **Retry logic:** Exponential backoff for tool failures; don't retry infinitely
- **Graceful degradation:** When tool fails, have fallback behavior defined
- **Context validation:** Inject stale-data checks; inform resumed sessions of changes

**⚠️ Self-evaluation cannot verify FACTS — only format/structure completeness**

## Token Economics &amp; Practical Estimates

### Token Approximations

- 1 token ≈¾ of an English word
- 1000 tokens ≈750 words / ~1.5 pages
- Code token use ≈ 1 token per ≈5 chars
- Non-English: Typically more tokens per word

### Context Window Impact

- **Long history:** Eats input budget → summarize or truncate
- **Tool results:** Each result added to history — can grow fast
- **System prompt:** Counts against input — keep concise

### Cost Optimization

- Shorter system prompts
- Summarize long histories
- Return only needed fields from tools
- Limit output with explicit instructions
- Use appropriate model tier for task

### Quality Optimization

- More examples = better format adherence
- Detailed schemas = fewer format errors
- Explicit constraints = fewer edge-case failures
- Step-by-step &gt; one-shot for complex tasks

## Mental Models for Production AI

### The Right Way to Think About LLMs

- **LLMs are probabilistic, not deterministic** — same input can produce different output. Design systems to handle this.
- **LLMs predict "what comes next" based on training** — they don't "know" facts the way a database does.
- **LLMs follow patterns in descriptions** — tool descriptions, schemas, and examples are code, not documentation.

### Key Production Principles

- Validate output against schemas — don't trust format blindly
- Use hooks for compliance guarantees — not prompt instructions
- Context window = working memory — manage it actively
- Model has NO memory between API calls — you must pass history
- Temperature 0 ≠ perfectly consistent — still probabilistic
- Evaluate with real production examples — not toy cases

### Exam Perspective

- 6+ months prod experience expected
- Understand capabilities AND limitations
- Design for reliability in uncertainty

## Related

- [MCP Cheat Sheet](17-cheatsheet-3-mcp.md) — the previous section in this series.
- [Prompt Engineering Cheat Sheet](19-cheatsheet-5-prompt-engineering.md) — the next section in this series.
