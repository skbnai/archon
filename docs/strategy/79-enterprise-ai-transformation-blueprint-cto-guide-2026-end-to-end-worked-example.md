---
title: "CTO Transformation Blueprint: End-to-End Worked Example"
doc_type: guide
domain: strategy
status: current
canonical: true
topic_id: enterprise-ai-transformation-blueprint-cto-guide-2026-part4
maturity: expert
personas: ["CTOs", "Platform Architects", "Product Managers", "AI Engineers"]
last_reviewed: 2026-07-19
covers_version: "N/A"
supersedes: []
tags: ["enterprise-ai", "worked-example", "customer-support-agent", "architecture-decisions", "cost-model"]
sources: []
pagination_prev: strategy/enterprise-ai-transformation-blueprint-cto-guide-2026-failure-playbook-migration
---

A complete, production-grade customer support agent — from spec to cost model to evaluation framework to architecture decisions. Every decision is documented. This is the reference for building agents at scale.

## The Objective

Build a Level 3 customer support agent that handles Tier-1 support tickets autonomously, with HITL escalation for Tier-2 complexity.

**Production target:** Handle 60% of tickets with zero human touch; escalate 40% to humans with full context pre-loaded.

---

## Step 1: Spec-Driven Development (requirements.md)

### Objective
Resolve Tier-1 support tickets autonomously. Escalate Tier-2 with context.

### Capabilities
- Read customer account data (CRM MCP server)
- Read order history (ERP MCP server)
- Check ticket knowledge base (RAG via Pinecone MCP server)
- Create/update tickets (CRM MCP server — Tier 2, logged)
- Send templated emails (Email MCP server — Tier 2, logged, human-reviewed)
- Initiate refund ≤$50 (Payments MCP — Tier 2, logged, auto-approved)
- Escalate to human (Zendesk API — Tier 3, always human decision)

### Explicit Constraints (DO NOT)
- DO NOT issue refunds >$50 without human approval
- DO NOT delete any records
- DO NOT disclose other customers' data
- DO NOT promise outcomes you cannot verify (check before stating)

### Success Metrics
- Tier-1 resolution rate: >60% of tickets (target: 70%)
- Resolution time: &lt;2 minutes for Tier-1 (vs 8 min human average)
- CSAT delta: +0.5 or above vs human-only baseline
- Escalation quality: humans rate pre-loaded context as 'helpful' >80%
- Cost per ticket: &lt;$0.08 at scale (blended Tier-1+2 with routing)

### Failure Modes to Design Against
- Hallucinating order details not in CRM
- Processing wrong customer's data (PII boundary violations)
- Issuing duplicate refunds on retry
- Infinite escalation loops (escalated → human → reassigned → escalated)

---

## Step 2: Agent Architecture

```
TICKET ARRIVES (email / API / chat)
         ↓
INTAKE NODE: Classify tier (1 vs 2) + extract customer_id, issue_type, urgency
  Model: Claude Haiku 4.5 (structured output, Pydantic-validated)
         ↓
CONTEXT LOADING NODE: Call 3 MCP servers IN PARALLEL
  → CRM MCP: customer profile, account status, previous tickets (90 days)
  → ERP MCP: order history, shipment status, return eligibility
  → RAG MCP: top 3 KB articles for this issue_type (≤2K tokens total)
  TOTAL CONTEXT BUDGET: 4,000 tokens max
         ↓
RESOLUTION NODE: Draft response + action plan
  Model: Claude Sonnet 4.6 (reasoning, customer empathy)
  Output MUST be Pydantic-validated: {response: str, actions: List[Action]}
         ↓
ACTION TIER CHECK (deterministic, not LLM-based)
  Tier 1 (read-only): → SEND NODE → done
  Tier 2 (refund ≤$50, create ticket): → LOG → EXECUTE → SEND
  Tier 3 (refund >$50, escalate): → HITL GATE → human approval
         ↓
EVAL NODE (async after response sent):
  LLM-as-judge checks: accuracy | empathy | policy compliance | hallucination
  Score <80%: flag for human quality review
  Score <60%: alert on-call + pause agent for this issue_type
         ↓
COST GUARD: if tokens >8,000 OR cost >$0.50/ticket: alert + escalate
```

---

## Step 3: Cost Model for This Agent

| Step | Model | Tokens/ticket | Cost/ticket | Notes |
|---|---|---|---|---|
| Intake/Classification | Claude Haiku 4.5 | ~1K | $0.0008 | Cached system prompt saves 80% |
| Context loading (MCP calls) | No LLM — parallel API | No tokens | $0.001–0.003 | API latency, not token cost |
| Resolution drafting | Claude Sonnet 4.6 | ~4.5K | $0.020 | 4K context window enforced |
| Async eval (LLM-as-judge) | Claude Haiku 4.5 | ~1.1K | $0.0012 | Runs async, doesn't block |
| **Subtotal API cost** | — | ~6.6K | **$0.023/ticket** | Target: &lt;$0.08 blended |
| **LLMOps multiplier (2.8x)** | Infra, obs, guardrails | — | **$0.064/ticket** | Multiply API cost × 2.8 |
| **TOTAL at 1K tickets/day** | — | — | **$64/day = $1,920/month** | Break even vs 1 agent FTE |
| **TOTAL at 10K tickets/day** | — | — | **$640/day = $19.2K/month** | Break even vs 12 agent FTEs |

---

## Step 4: Evaluation Framework

| Eval Type | What It Measures | How | Threshold |
|---|---|---|---|
| **Accuracy** | Did agent retrieve correct account/order data? | Compare stated facts vs CRM ground truth. Automated. | >99% (errors are customer trust events) |
| **Resolution Quality (LLM-as-judge)** | Was response helpful, empathetic, policy-compliant? | Claude Sonnet grades on 4 dimensions, structured JSON | >80% score; flag &lt;60% |
| **Hallucination detection** | Did agent invent information not in CRM/ERP/KB? | Check every factual claim vs retrieved context | Zero tolerance for factual errors |
| **PII boundary** | Did response include another customer's data? | Automated: scan for customer IDs, emails not matching ticket customer | Zero violations |
| **Action accuracy** | Did agent perform the right action (correct tier, approval)? | Audit log: every action logged with ticket ID, action type, value | >99% correct tier classification |
| **Cost per ticket** | Is blended cost within budget? | Portkey tracks per-trace costs; Vantage alerts if 7-day avg exceeds $0.10 | &lt;$0.10 per ticket blended |
| **Escalation quality** | Did humans find pre-loaded context helpful? | CSAT from human agents rating context at handoff | >80% 'helpful' rating |

---

## Step 5: Key Architecture Decisions (ADRs)

### ADR-001: Parallel MCP Calls, Not Sequential

**Decision:** Parallel MCP calls reduce context loading latency to 2s regardless of number of sources.

**Rationale:** Sequential context loading adds 2-3s per call. Parallel calls with 2s timeout is much faster.

**Tradeoff:** More complex error handling — mitigated by graceful degradation (proceed with partial context, note missing data in response).

### ADR-002: Pydantic-Validated Outputs Everywhere

**Decision:** Every LLM output MUST conform to a defined Pydantic schema. Output schema violations trigger immediate fallback to human.

**Rationale:** Schema drift is the #1 cause of silent agent failures in production.

### ADR-003: Haiku for Classification, Sonnet for Resolution

**Decision:** Use Haiku 4.5 for classification (cheap, structured), Sonnet 4.6 for resolution (reasoning).

**Rationale:** Classification requires structured output, not reasoning. Haiku at 90% quality of Sonnet for classification tasks at 10% the cost. Saves ~70% on intake costs alone.

### ADR-004: Async Evaluation (Not Blocking)

**Decision:** Run LLM-as-judge asynchronously after response sent.

**Rationale:** Synchronous eval blocks response delivery, adds 3-5s latency. Async doesn't block. Tradeoff: can't block bad response before delivery — mitigated by strict Pydantic validation and guardrails.

### ADR-005: 4,000-Token Context Hard Cap

**Decision:** Enforce 4K context budget. Priority: (1) current ticket, (2) customer account, (3) last 3 orders, (4) top 2 KB articles. Truncate RAG if >2K tokens.

**Rationale:** 'Lost in the middle' quality degradation begins at 40% of context window fill. 4K cap prevents this.

---

## Related

- [CTO Transformation Blueprint: Maturity Model & Reference Architectures](34-enterprise-ai-transformation-blueprint-cto-guide-2026.md)
- [CTO Transformation Blueprint: FinOps & Security Threat Model](77-enterprise-ai-transformation-blueprint-cto-guide-2026-finops-security-threat-model.md)
- [CTO Transformation Blueprint: Failure Playbook & Migration Strategy](78-enterprise-ai-transformation-blueprint-cto-guide-2026-failure-playbook-migration.md)

## Sources

- Zylos Research — LLM quality degradation over context length (Feb 2026)
- Portkey — Agent cost tracking best practices
- OpenAI / Anthropic — Pydantic integration guides
- LangGraph documentation — Agent architecture patterns
