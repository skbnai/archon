---
title: "Claude Architect Foundations: Best Practices & Anti-Patterns Guide — Part 3"
date: 2026-07-24
last_reviewed: 2026-07-24
status: current
domain: agentic-systems
topic_id: claude-best-practices-part3
doc_type: guide
supersedes: []
tags: ["coding-tools", "claude", "validation", "context-management"]
---

**This is Part 3 of 3. [Part 1 ←](pathname:///archon/agentic-systems/coding-tools/32-claude-best-practices) | [Part 2 ←](pathname:///archon/agentic-systems/coding-tools/parts/32-claude-best-practices-part2)**

## **4.4  Retry Loops & Validation**

Retrying a failed request is only correct if the failure is transient (timeout, rate-limit, service error). Retrying on semantic failures (wrong output format, hallucination, misunderstanding) trains the model to ignore errors — you'll get identical wrong output on every retry.

| ✅  BEST PRACTICE | ❌  ANTIPATTERN |
| --- | --- |
| Classify failures: transient (retry with backoff), semantic (refine prompt, escalate, or request user clarification), infrastructure (fail immediately). | Blanket retry all failures. Semantic failures never resolve on retry — you just loop until you hit the retry limit. |
| For semantic failures, modify the prompt between retries: add more examples, clarify the misunderstood requirement, or add validation checks. | Retry identical request. Each attempt produces identical wrong output since nothing changed in the prompt. |
| Use exponential backoff for transient failures (2s, 4s, 8s...) with a max cap (never >60s between retries). Prevents thundering herds and respects service limits. | Retry immediately on failure or use fixed backoff. Immediate retries often fail again; fixed intervals don't adapt to service load. |
| Set max retry attempts to 3–5. Beyond that, treat the failure as a hard error and escalate. | Allowing unlimited retries. Compounds token waste and operational cost. |

## **4.5  Batch API and Message Batches**

Batch API processes requests asynchronously at a 50% cost discount with a 24-hour SLA. Message Batches is the Batch API's Claude-native wrapper. Use Batch for non-urgent jobs; use synchronous API for anything developers wait for.

| ✅  BEST PRACTICE | ❌  ANTIPATTERN |
| --- | --- |
| Use Batch API for: nightly reports, weekly audits, non-urgent report generation, scheduled content analysis. 24-hour SLA is acceptable. | Using Batch for real-time features or pre-merge checks. Developer experience suffers with 24-hour delays. |
| Use synchronous API for: pre-merge blocking checks, live customer support, real-time analysis, anything a human waits for. | Switching all API calls to Batch for cost savings, regardless of SLA impact on users. Cost optimization breaks the feature. |
| When using Batch, set stop_reason checking for each request individually — don't assume all requests either succeeded or failed. | Assuming if one request succeeded, all succeeded. Process Batch results element by element with individual error handling. |
| Pre-process input files and validate their format BEFORE submitting to Batch. Catch validation errors immediately rather than discovering them in the overnight results. | Submitting unvalidated input to Batch. Invalid data sits in processing queue for 24 hours before returning errors. |

## **4.6  Context Window Management**

Every API call has a context window: tokens in (prompt + conversation history + tools) + tokens out (response). The model trades off breadth and depth within the window. Context engineering is optimizing the trade-off.

| ✅  BEST PRACTICE | ❌  ANTIPATTERN |
| --- | --- |
| Include all task-relevant facts in the prompt (exact thresholds, policy constraints, user preferences) rather than expecting the model to infer them. | Expecting the model to remember 'always check before deploying' without explicitly stating the policy in the current prompt. |
| Summarize conversation history after 20–25 turns and reset the window to keep recent turns sharp. Too much history = diluted attention. | Keeping 50+ turn conversations active. Context dilutes — recent information competes with stale information for model attention. |
| When context fills unexpectedly (rare long user inputs), summarize and restart rather than waiting for the next turn to fill the window. Proactive management is more reliable. | Waiting for the context-full error and then scrambling to summarize. Reactive response usually results in losing recent findings. |
| Put critical constraints (financial thresholds, identity verification requirements) in system prompt, not conversation history. | Putting business-critical constraints in conversation history where they can be superseded by user inputs. |

---

## **Domain 5 — Context Management & Reliability  (15%)**

Context management is the discipline of preserving facts, provenance, and reasoning across multi-step processes. Unreliable context creates hallucinations (fabricated facts), attribution (misremembered sources), and decision errors (forgetting constraints between steps).

## **5.1  Persistent Facts Blocks**

A facts block is structured, machine-readable data at the top of a conversation that both Claude and humans can understand at a glance. It survives across turns without corruption. It's the answer to 'how do you prevent Claude from forgetting critical information.'

| ✅  BEST PRACTICE | ❌  ANTIPATTERN |
| --- | --- |
| Use YAML-formatted facts blocks at conversation start to capture: customer constraints, domain-specific rules, prior findings, approval thresholds. | Embedding facts in prose conversation. They dilute, get forgotten, and become contradicted by later statements. |
| Review and refresh facts blocks at each turn start. If facts grow beyond 20 items, archive older facts and keep current session facts prominent. | Creating a facts block once at conversation start and never updating it as new information arrives. Blocks grow stale. |
| Use this structure: KEY: VALUE pairs with clear metadata (source, expiry date, confidence). Examples: CUSTOMER_BUDGET: $50K (approved 2026-07-20), IDENTITY_VERIFIED: true. | Free-form fact descriptions. Parse-ability matters — structured data is more reliable than natural language. |

## **5.2  Lost-in-the-Middle Mitigation**

Large context windows improve breadth but reduce depth: information in the middle of a long context gets lower attention than information at the start or end. This isn't a prompt bug — it's model architecture. Mitigations: (1) retrieve only the most relevant subset, (2) repeat critical information at the end, (3) use smaller, focused context windows.

| ✅  BEST PRACTICE | ❌  ANTIPATTERN |
| --- | --- |
| Use retrieval (vector search, keyword filtering) to surface only the most relevant context. Don't pass entire document collections. | Passing 50 documents for the model to search through internally. The model may miss relevant information in the middle. |
| When context is necessary, repeat critical facts at the end of the prompt immediately before the task instruction. | Stating facts at the prompt start assuming they'll be retained equally through all processing. They won't. |
| For long multi-document analysis, break into smaller focused passes: pass 5 documents, synthesize findings, then move to the next 5. | Passing 50 documents in one context window and asking for synthesis. Diluted attention produces incomplete synthesis. |
| Use citation anchors (line numbers, section headings) so Claude can point you to source information. Verify sources programmatically. | Asking for facts without citation anchors. Cannot verify where information came from; easy to hallucinate sources. |

## **5.3  Escalation Triggers**

Define explicit conditions where a system escalates to human review. Escalation criteria must be measurable and independent of sentiment or mood. Over-escalating trains humans to second-guess automation; under-escalating leaves real issues unaddressed.

| ✅  BEST PRACTICE | ❌  ANTIPATTERN |
| --- | --- |
| Define escalation criteria by objective condition, not subjective interpretation. 'Escalate if: customer explicitly requests human review' is measurable. | Using frustration level, sentiment score, or politeness as escalation signals. Different humans have different patience; signals are inconsistent. |
| When confidence falls below a threshold, escalate rather than guess. Calibrate thresholds based on actual false-positive rates in production. | Setting confidence thresholds without validating them against ground truth. Guess thresholds produce poor escalation calibration. |
| For edge cases where policy is silent, always escalate to a human decision-maker rather than inventing a policy interpretation. | Improvising policy interpretation for edge cases. Embeds judgment errors into the system; humans discover them post-facto when correcting errors. |

## **5.4  Structured Error Propagation**

Errors bubble up through layers: ML layer (model made a wrong prediction), tool layer (API returned unexpected data), application layer (business logic constraint violated). Each layer must communicate errors in a structured way so upstream handlers can respond appropriately.

| ✅  BEST PRACTICE | ❌  ANTIPATTERN |
| --- | --- |
| Return errors with structured fields: error_category (transient/validation/business/permission), is_retryable, error_code, explanation, suggested_action. | Returning a string error message. Upstream code can't distinguish retriable from non-retriable errors without parsing prose. |
| For ML errors, include the model's confidence scores or error signals so downstream code can decide whether to retry, escalate, or override. | Treating all ML outputs as equally reliable. Confidence scores inform better escalation decisions than binary pass/fail. |
| For business constraint violations, include which constraint was violated and what the conflicting values were. | Returning 'Constraint violated' with no detail. End users can't understand what went wrong or how to fix it. |
| Preserve the original exception chain (what went wrong at each layer) so debugging doesn't require recreating the failure. | Swallowing original errors and returning a generic wrapper. Makes root-cause diagnosis impossible for bugs. |

## **5.5  Provenance Preservation**

Provenance is the chain of custody for a piece of information: where it came from, how it was processed, who verified it. Lost provenance means 'this fact is correct, but I don't know why I believe it' — dangerous for high-stakes decisions.

| ✅  BEST PRACTICE | ❌  ANTIPATTERN |
| --- | --- |
| Every fact passed between agents should carry metadata: source document, extraction method, confidence, timestamp of verification. | Passing facts as bare strings. Later users don't know if a fact came from a user input, a search result, or was hallucinated. |
| When synthesizing information across sources, explicitly list which sources contributed to each conclusion. | Merging information from multiple sources without attribution. Contradictions can't be traced to source disagreements. |
| Use citation anchors (exact quotes with source references) instead of paraphrased facts for high-stakes information. | Paraphrasing facts for 'clarity.' Introduces transformation errors; receivers can't verify against original. |
| For customer-facing outputs, distinguish between facts verified by the system vs. facts provided by the customer vs. facts inferred from patterns. | Presenting all information identically regardless of confidence source. Customers can't assess reliability. |

---

## **QUICK REFERENCE: The 8 Rules**

### **Architecture**
1. **Agentic Loops** — Always check stop_reason for 'end_turn' vs 'tool_use'. Accumulate tool results in conversation history. Set MAX_ITERATIONS cap. Detect runaway loops (repeated identical calls).

2. **Multi-Agent Orchestration** — Use hub-and-spoke topology. Coordinator is single source of truth. Subagents are isolated (no shared context). Coordinator Task decomposition determines coverage quality.

### **Configuration**
3. **Configuration Hierarchy** — .mcp.json (project, shared, version-controlled) · CLAUDE.md (project, shared, version-controlled) · ~/.claude.json (user, personal, not shared). Audit active MCP servers; deactivate unused ones.

4. **Rules & Commands** — Use .claude/rules/ with path globs for conditional rule loading. Slash commands in .claude/commands/ for team workflows. Skills with context: fork for large intermediate outputs.

### **Prompting**
5. **Explicit Criteria** — Define measurable review categories, escalation criteria, and validation rules. Avoid vague terms ('thoroughly', 'carefully'). Few-shot examples beat prose instructions for consistency.

6. **Structured Output** — Use tool_use with JSON schema for extraction. Schema validates structure; add application-level semantic validation for business logic. Mark schema fields optional when data may be missing.

### **Reliability**
7. **Context Management** — Use persistent facts blocks (YAML) for critical constraints. Repeat facts at prompt end to overcome lost-in-the-middle. Retrieve only relevant context; don't pass everything.

8. **Error Handling** — Classify failures (transient/validation/business). Retry only transient failures with exponential backoff. For semantic failures, refine prompts between retries. Escalate when confidence falls below thresholds.

---

## **Exam-Focused Summary**

| Domain | Focus Area | Key Metric |
| --- | --- | --- |
| 1 (27%) | Stop_reason handling · Multi-agent topology · Hooks for determinism · Session management | Loop termination + MAX_ITERATIONS |
| 2 (18%) | Tool descriptions (primary selection mechanism) · MCP configuration hierarchy · Least-privilege distribution | Description quality drives selection |
| 3 (20%) | CLAUDE.md hierarchy · Path-scoped rules · Plan mode vs direct execution | Hub-and-spoke coordinator first |
| 4 (20%) | Explicit criteria over vague instructions · Few-shot examples · Structured output via tool_use · Context window management | Measurable criteria + examples |
| 5 (15%) | Persistent facts blocks · Lost-in-the-middle mitigation · Escalation criteria · Provenance preservation | Citation anchors + metadata |

---

**Completed: 3-part guide. [Part 1](pathname:///archon/agentic-systems/coding-tools/32-claude-best-practices) | [Part 2](pathname:///archon/agentic-systems/coding-tools/parts/32-claude-best-practices-part2) | Part 3 — Ready for study.**
