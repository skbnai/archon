---
title: "AgentCore Memory Architecture Guide (Part 3)"
doc_type: guide
domain: platforms
status: current
topic_id: agentcore-memory-architecture-guide-part3
last_reviewed: 2026-07-27
maturity: practitioner
supersedes: []
tags: [aws, agentcore, gdpr, security, terraform]
covers_version: "v3.0, June 2026"
---

> Continues from [AgentCore Memory Architecture Guide](../15-agentcore-memory-architecture-guide.md) and [Part 2](15-agentcore-memory-architecture-guide-part2.md), covering token optimisation, Strands best practices, EU banking/GDPR compliance, the security/threat model, cost optimisation, the PoC-to-production journey, evaluation, and Terraform IaC.

## Memory & Token Optimisation Strategies

65% of enterprise AI failures in 2025 were caused by context drift — not context exhaustion (Zylos Research, Feb 2026). The optimisation strategies below address both cost and quality.

| Strategy | Technique | Cost Reduction | Implementation |
|---|---|---|---|
| Prompt caching | `CacheConfig(strategy='auto')` in BedrockModel | 30-70% input | One-line change. Stable prefix cached across requests. |
| Batch write | `batch_size=10+` in SessionManager | 90% API calls | Buffer messages; flush on session close. Free optimisation. |
| Retrieval caching | 15-min cache keyed on actor_id | 70-90% LTM calls | Invalidate on memory write for actor. Redis or ElastiCache. |
| Context compaction (70% rule) | ACON framework or Strands built-in | 26-54% tokens | Trigger at 70% context window. Summarise early turns. |
| Tiered retrieval | 900-token budget across 5 tiers | Noise reduction | Tier 1: identity 50t. Tier 2: session 200t. Tier 3: prefs 300t. |
| Session-end consolidation | EventBridge trigger post-session | Avoids per-msg | Never consolidate per-message. EventBridge is the trigger. |
| Envelope KMS encryption | One data key per session | KMS API calls | Encrypt DEK per session, reuse for all events in session. |

## Strands Framework Best Practices

### Mandatory Hooks

**`PIIRedactionHook`** (`MessageAddedEvent`, before write) — fires before any storage, applying Comprehend + Presidio. A GDPR Art. 25 architectural requirement.

```python
class PIIRedactionHook:
    def on_message_added(self, event):
        if event.message.role in ('user', 'assistant'):
            event.message.content = self.redactor.redact(event.message.content)
        return event
```

**`MemoryRetrievalHook`** (`MessageAddedEvent`, on user message, before model call) — semantic search over LTM, injecting top-K records plus session context into the system prompt within a 900-token budget.

```python
class MemoryRetrievalHook:
    def on_message_added(self, event):
        if event.message.role == 'user':
            # Check cache first (15-min TTL keyed on actor_id)
            records = self.cache.get(self.actor_id) or \
                self.memory.retrieve_memory_records(
                    memoryId=self.memory_id,
                    namespace=f'/actors/{self.actor_id}/',
                    text=event.message.content,
                    maxResults=5,
                )
            event.agent.system_prompt = self._format(records) + event.agent.system_prompt
```

**`MemoryPersistenceHook`** (`AfterInvocationEvent`) — persists the interaction, handles checkpointing, and updates the DynamoDB catalog with `last_updated_at` and preview text.

```python
class MemoryPersistenceHook:
    def after_invocation(self, event):
        self.session.flush_if_threshold_reached()  # batch_size flush
        self.dynamo.update_item(  # update sidebar catalog
            Key={'actor_id': self.actor_id, 'session_id': self.session_id},
            UpdateExpression='SET last_updated_at=:t, preview_text=:p',
            ExpressionAttributeValues={':t': int(time.time()), ':p': preview},
        )
```

**`ConsentCheckHook`** (`StartAgentCycleEvent`) — validates the GDPR lawful basis before any read or write. Mandatory for EU banking.

```python
class ConsentCheckHook:
    def on_start_agent_cycle(self, event):
        if not self.consent.has_valid_basis(event.context['actor_id'], 'memory'):
            event.context['memory_enabled'] = False
            logger.audit(f'Memory disabled: no GDPR basis')
```

### Sub-Agent Skills

| Skill | Access | Purpose | Mandatory? |
|---|---|---|---|
| memory_write | Writer only | Wraps put_events. PII check + consent + namespace scope enforced. | YES |
| memory_read | Reader roles | Wraps RetrieveMemoryRecords. actor_id = IdP auth only. | YES |
| memory_delete | DPO Admin only | Art. 17 erasure: deletes events + records + all namespaces. | YES |
| memory_search | Reader roles | Semantic search. Top-K with scores. Query logged for audit. | YES |
| session_list | Agent self-call | ListEvents for STM replay on resume (Scenario B). | Recommended |
| session_close | Agent self-call | Flush batch, trigger EventBridge consolidation, update DDB catalog. | Recommended |

## EU Banking, GDPR & Regulatory Compliance

| GDPR Article | Obligation | AgentCore Implementation |
|---|---|---|
| Art. 5 — Minimisation | Store only memory relevant to lawful purpose. | Minimum strategies. Aggressive TTLs. DPO quarterly review. |
| Art. 6 — Lawful Basis | Each memory type needs documented legal basis. | ConsentCheckHook validates per actor_id. Document in consent_config.py. |
| Art. 17 — Right to Erasure | Delete all customer data within 30 days on request. | memory_delete skill: cascades events + LTM records + S3 archive + DDB catalog. |
| Art. 22 — Automated Decisions | Decisions using automated processing require human review. | Episodic → credit/fraud must log reasoning + provide human review path. |
| Art. 25 — Privacy by Design | Privacy embedded architecturally — not as an audit layer. | PIIRedactionHook fires BEFORE put_events. Architecture-level, not optional. |
| Art. 32 — Security | Technical measures to protect personal data. | CMK + VPC + PrivateLink + MFA + CloudTrail. All mandatory. |
| Art. 35 — DPIA | Impact assessment before high-risk AI deployment. | GDPR_DPIA.md with DPO sign-off — production gate before go-live. |

| Regulation | Memory-Specific Control |
|---|---|
| DORA Art. 6 | VPC + PrivateLink. Memory access in CloudTrail. ICT risk register entry. |
| DORA Art. 11 | Cross-region backup plan. S3 replication for session archive. |
| EBA ML §4.3 | AgentCore Observability trace IDs on every memory-influenced decision. |
| EBA ML §5.1 | Quarterly fairness audit on episodic memory patterns across demographic groups. |
| MiFID II Art. 25 | Suitability memory in Semantic strategy. Immutable metadata. 5-year TTL minimum. STRICTLY_CONSISTENT. |
| 5AMLD | KYC Semantic memories. 7-year retention. S3 WORM. Object Lock COMPLIANCE mode. |

## Security, Policy & Threat Model

| Attack Vector | Description | Mitigation |
|---|---|---|
| Memory Injection (event write) | Crafted input survives PII redaction and plants false memories. | Input validation Lambda + adversarial detector. Quarterly test. |
| Persistence Hijack (consolidation) | Malicious event extracted as 'preference', replayed as trusted. | Schema allowlist on extracted records. Validate entity types. |
| Cross-session Leak (actor_id derivation) | actor_id collision — reading another user's memories. | actor_id = Cognito sub ONLY. IAM namespace condition key enforced. |
| Prompt Override (retrieval injection) | User prompt forces the agent to output raw memories verbatim. | System prompt rule + Bedrock Guardrails output filter. |
| Tool Surface Poison (pre-write) | Tool output poisoned before memory write. | Tool output sanitisation hook. Schema validation. |

| Layer | Encryption Key | Key Management | Required for EU Banking? |
|---|---|---|---|
| Events (STM) | Customer-managed KMS (CMK) | Rotate 90d; eu-central-1 only | MANDATORY |
| Memory Records (LTM) | CMK + encryption context | `context={customer_id, namespace}` | MANDATORY |
| In-Transit | TLS 1.3 | Enforced by PrivateLink endpoint | MANDATORY |
| CloudWatch Logs | CMK log group encryption | Separate key from data key | MANDATORY |
| S3 WORM Archive | SSE-KMS + Object Lock | COMPLIANCE mode — 7-year lock | MANDATORY (AML) |
| Session Storage | S3-backed encryption | SSE-S3 or SSE-KMS | SSE-KMS recommended |

## Cost Analysis & Optimisation

**Anti-patterns to avoid:** `batch_size=1` (multiplies API costs 5-15x); 365-day STM retention on all memory types; per-message consolidation (never do this); no retrieval cache (re-fetching LTM every turn); a cold start on every session (no warm pool); no SUMMARIZATION strategy (Scenario C becomes impossible); not tagging `session_id` as a STRICTLY_CONSISTENT key.

**Best practices to follow:** `batch_size=10+` (90% fewer API requests); tiered TTL (30d STM, 1yr LTM preferences); a session-end EventBridge trigger for consolidation; a 15-min retrieval cache keyed on actor_id; a warm pool that heartbeats sessions past the idle timeout; SUMMARIZATION always on with an S3 archive on close; STRICTLY_CONSISTENT `session_id` on all LTM records.

## Project Journey — PoC to Production

**Phase 1 — Memory + Sidebar PoC (Weeks 1-4)**

- AgentCore CLI deploy (`agentcore create`) in eu-central-1; Memory Resource with SUMMARIZATION strategy only.
- All 4 mandatory hooks (Consent stubbed for PoC); a DynamoDB conversations table with the actor_id/session_id schema; a sidebar UI that lists sessions and resumes on click (Scenario A/B only).
- **Milestone:** synthetic data only (zero real PII); the agent maintains context and the DynamoDB session catalog serves the sidebar; validate warm resume &lt;200ms and cold start &lt;3s.

**Phase 2 — STM Expiry Resume + LTM (Weeks 5-8)**

- Add USER_PREFERENCE + SEMANTIC strategies; wire `actor_id` = Cognito sub; add the STRICTLY_CONSISTENT `session_id` metadata key on all strategies; implement Scenario B (STM replay) and Scenario C (LTM-only resume).
- S3 session archive (EventBridge → Lambda → S3 on session close); a PII redaction Lambda (Comprehend + domain patterns); right-to-erasure cascade delete across all 4 data layers.
- **Milestone:** Scenario C (expired STM) reconstruction works end-to-end.

**Phase 3 — Multi-Agent + Policy (Weeks 9-12)**

- Hub & Spoke namespace hierarchy; IAM writer/reader/DPO-admin roles; AgentCore Policy with Cedar namespace access rules; a warm pool that pre-warms microVMs to cut cold start latency; a session browser with search, fork, rename, and label.
- **Milestone:** a 100-concurrent-agent performance test on a shared Memory Resource; a multi-agent workflow with governed shared memory.

**Phase 4 — Episodic + EU Banking Hardening (Weeks 13-16)**

- Episodic memory on high-value workflow agents (with a fairness audit plan); a DPIA sign-off by the DPO as a production gate; CMK + VPC + PrivateLink for all AgentCore endpoints; an S3 WORM archive (Object Lock COMPLIANCE, 7-year AML retention).
- **Milestone:** DPO-approved, pen-tested, GDPR-compliant production. AgentCore Evaluations covering all 9 memory metrics plus the resume quality metric; a SAR drill (right-to-erasure end-to-end across all 4 data layers); a penetration test covering memory injection, cross-session leak, and STM replay attacks.

## Evaluation Framework

| Metric | Definition | Target | Alert Threshold |
|---|---|---|---|
| Memory Retrieval Relevance | Cosine similarity: retrieved memory vs current query | >0.85 | &lt;0.75 — tune retrieval |
| PII Leakage Rate | % of memory reads with unredacted PII in output | 0.00% | >0% — CRITICAL, page DPO |
| Cross-Session Recall | % of correctly recalled preferences from prior session | above 90% | &lt;80% — review extraction |
| Memory Staleness Rate | % of retrieved memories older than TTL threshold | below 5% | >10% — run TTL purge |
| Namespace Isolation | % of out-of-scope access attempts blocked | 100% | &lt;100% — CRITICAL, audit IAM |
| Erasure Completeness | After Art. 17: 0 memories retrievable for actor_id | 100% | &lt;100% — CRITICAL, GDPR breach |
| Scenario C Resume Quality | Semantic similarity: LTM-reconstructed context vs original STM | above 0.80 | &lt;0.70 — tune summarization strategy |
| Cold Start Latency p99 | New microVM provision to first agent response | &lt;3s | >5s — warm pool undersized |
| Episodic Bias Score | Fairness delta across demographic groups in decisions | Delta &lt;5% | Delta >10% — suspend episodic |

## Terraform IaC Reference

### Memory Resource with Strictly Consistent Metadata

```hcl
resource "aws_bedrockagentcore_memory" "banking_memory" {
  name                   = "${var.project}-${var.env}-memory"
  event_expiry_duration  = var.event_retention_days  # 30 default, 90 for loans
  encryption_key_arn     = aws_kms_key.memory_cmk.arn

  memory_strategies {
    summarization_memory_strategy { name = "ConversationSummary" }
  }

  # Add indexed_keys for strictly consistent metadata (May 2026)
  indexed_keys = [
    { name = "session_id", extraction_type = "STRICTLY_CONSISTENT" },
    { name = "actor_id",   extraction_type = "STRICTLY_CONSISTENT" },
    { name = "tenant_id",  extraction_type = "STRICTLY_CONSISTENT" },
  ]

  tags = { DataClass = "RESTRICTED", GDPRScope = "true", RetentionOwner = "DPO" }
}
```

### DynamoDB Session Catalog

```hcl
resource "aws_dynamodb_table" "sessions" {
  name         = "${var.project}-conversations"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "actor_id"
  range_key    = "session_id"

  attribute { name = "actor_id",         type = "S" }
  attribute { name = "session_id",       type = "S" }
  attribute { name = "last_updated_at",  type = "N" }

  global_secondary_index {
    name            = "actor-time-index"  # sidebar sort order
    hash_key        = "actor_id"
    range_key       = "last_updated_at"
    projection_type = "ALL"
  }

  server_side_encryption {
    enabled     = true
    kms_key_arn = aws_kms_key.sessions_cmk.arn
  }

  tags = { GDPRScope = "true", DataClass = "RESTRICTED" }
}
```

### KMS CMK + IAM + VPC (abbreviated)

```hcl
resource "aws_kms_key" "memory_cmk" {
  enable_key_rotation     = true  # 90-day rotation
  multi_region            = false  # single EU region (GDPR)
  deletion_window_in_days = 30
}

# Writer IAM: namespace-scoped to users/*
# Action = ["bedrock-agentcore:PutMemoryEvents"]
# Condition = { StringLike = { "bedrock-agentcore:namespace" = "users/*" }}

# DPO Admin IAM: delete only, EU regions only
# Action = ["bedrock-agentcore:DeleteMemory", "bedrock-agentcore:DeleteMemoryNamespace"]
# Condition = { StringEquals = { "aws:RequestedRegion" = ["eu-central-1","eu-west-1"] }}

# VPC PrivateLink endpoint
# service_name = "com.amazonaws.eu-central-1.bedrock-agentcore-memory"
# vpc_endpoint_type = "Interface"
# private_dns_enabled = true
```

## Risks, Recommendations & Decision Guide

| Risk | Severity | Mitigation | Owner |
|---|---|---|---|
| PII leakage to vector store | CRITICAL | PIIRedactionHook before every put_events. Macie scan. | Engineering |
| Cross-tenant actor_id collision | CRITICAL | Cognito sub as actor_id. IAM namespace condition. | Security |
| Missing right-to-erasure | CRITICAL | Cascade delete: STM + LTM + S3 + DDB. SAR drill. | DPO |
| STM expiry with no LTM config | HIGH | Always enable SUMMARIZATION. S3 archive on close. | Engineering |
| session_id not STRICTLY_CONSISTENT | HIGH | Required for Scenario C resume reliability (May 2026). | Engineering |
| Cross-EU region data flow | HIGH | Disable cross-region inference. SCP at org level. | Cloud Arch |
| Memory injection attack | HIGH | Input validation hook. Adversarial detector quarterly. | Security |
| Episodic bias drift | HIGH | Quarterly EBA fairness audit on episodic patterns. | MLOps |
| Cold start latency (>3s) | MEDIUM | Warm pool: heartbeat idle sessions past idle timeout. | Engineering |
| Context drift beyond 30K tokens | MEDIUM | 70% compaction trigger. Strands built-in compaction. | Engineering |
| Cost overrun from batch_size=1 | MEDIUM | batch_size>=10 enforced. Session-end consolidation. | Engineering |

### Final Recommendations

- **SUMMARIZATION strategy is the minimum viable memory config.** Without it, Scenario C (expired STM resume) degrades to Scenario D. One strategy costs almost nothing at session end.
- **STRICTLY_CONSISTENT session_id metadata is mandatory from May 2026.** This is what makes session-scoped LTM retrieval deterministic. Without it, Scenario C relies on semantic matching only, which is unreliable.
- **Build the DynamoDB session catalog from day one.** It is the sidebar's backbone and costs almost nothing. Without it, users cannot browse their conversation history and the resume infrastructure has no session registry.
- **Export a compressed S3 session archive on every session close.** This is the final fallback for Scenario D. A 45-minute conversation compresses to 2–5 KB; the cost over 10,000 sessions is cents.
- **Pre-warm microVMs for high-traffic conversation bots.** Cold starts are 10–15x slower than warm. A heartbeat pool sized to handle peak concurrency delivers sub-300ms latency for 90%+ of resume requests.
- **PIIRedactionHook is non-negotiable.** Implement it before any real user data enters the system — the single highest-impact control.
- **actor_id from IdP only.** This is the root cause of every reported cross-tenant memory leak.
- **batch_size=10 is free.** No quality trade-off, no architecture change — set it on day one.

## Related

- [AgentCore Memory Architecture Guide](../15-agentcore-memory-architecture-guide.md) — Part 1: release timeline, executive summary, architecture core concepts, memory types taxonomy
- [AgentCore Memory Architecture Guide (Part 2)](15-agentcore-memory-architecture-guide-part2.md) — sidebar reference architecture, session resume lifecycle, multi-agent memory patterns, memory processors, framework comparison
- [AgentCore Memory Architecture Guide (Part 4)](15-agentcore-memory-architecture-guide-part4.md) — complete resume orchestrator, session catalog API, warm pool/session close workflow, test suite
