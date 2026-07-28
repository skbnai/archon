---
title: "RAG, Memory & Data Authorization"
doc_type: guide
domain: trust
status: current
topic_id: rag-memory-data-authorization
last_reviewed: 2026-07-27
maturity: practitioner
supersedes: [docs/ai-security-governance/policy/Vol4_RAG_Memory_Data_Authorization.md]
tags: [authorization, rag, memory, multi-tenant, dlp]
covers_version: "as of 2026"
---

Document- and chunk-level RAG authorization, the memory type taxonomy and its Cedar protections, multi-tenant data isolation defense layers, and output classification/DLP filtering.

## RAG Authorization Architecture

**Critical risk:** without RAG authorization, a user in Sales can prompt an agent to retrieve confidential M&amp;A documents from the knowledge base simply by phrasing their query to match those documents. Vector similarity search has no concept of permissions — authorization must be added as a filter layer on top.

**RAG authorization pipeline.** A user query carrying canonical claims and context first passes a retrieval-authorization check (can this user query this knowledge base at all?); the claims are mapped to a permission set (clearance level, allowed categories, tenant ID, department, geography); a pre-retrieval metadata filter is applied *before* the vector similarity search runs (`WHERE tenant_id = :tenant AND classification IN (:allowed_classes) AND geography IN (:allowed_geos)`); the vector similarity search (OpenSearch, pgvector, or Bedrock Knowledge Bases) then returns only the pre-filtered, permitted documents; a post-retrieval authorization step verifies each retrieved chunk individually against the user's clearance; only authorized chunks are injected into the LLM context; an output classification filter checks whether the response is within the user's clearance (scanning for leaked PII or classified content); and the authorized response, with source citations, is finally returned to the user.

**Document-level authorization schema.** Every document and chunk in the knowledge store carries authorization metadata that drives both the pre-retrieval filter and the post-retrieval Cedar evaluation:

```json
{
  "doc_id": "doc-m-and-a-briefing-2026-001",
  "title": "Project Phoenix M&A Briefing",
  "classification": "TOP_SECRET",
  "classification_basis": "MERGERS_ACQUISITIONS",
  "tenant_id": "bank-prod",
  "legal_entity": "BANK_UK_LTD",
  "department_owners": ["STRATEGY", "LEGAL", "C_SUITE"],
  "geography_restriction": ["GB", "IE"],
  "required_capabilities": ["can_access_ma_documents", "can_view_strategic_plans"],
  "need_to_know_list": ["emp-00001", "emp-00042", "emp-00891"],
  "embargo_until": "2026-09-01T00:00:00Z",
  "retention_class": "LEGAL_HOLD",
  "dlp_category": "CONFIDENTIAL_BUSINESS",
  "created_at": "2026-03-15T14:00:00Z",
  "source_system": "SharePoint_Legal",
  "chunks": [
    { "chunk_id": "chunk-001", "classification": "TOP_SECRET", "content_hash": "sha256:abc123..." }
  ]
}
```

**Cedar policies for RAG authorization.** Pre-retrieval permission checks whether the agent may query the knowledge base at all, scoped to its tenant and a risk ceiling:

```
permit(
  principal is BankAI::Agent, action == BankAI::Action::"QueryKnowledgeBase",
  resource is BankAI::KnowledgeBase
)
when {
  principal.delegatedFrom.capabilities.contains("can_query_knowledge_base") &&
  resource.tenantId == principal.tenantId &&
  context.riskScore < 60
};
```

Post-retrieval chunk authorization verifies tenant match, sufficient clearance, and either department ownership or an explicit need-to-know entry:

```
permit(
  principal is BankAI::Agent, action == BankAI::Action::"AccessChunk",
  resource is BankAI::DocumentChunk
)
when {
  resource.tenantId == principal.tenantId &&
  principal.delegatedFrom.clearanceLevel >= resource.classification &&
  (resource.departmentOwners.containsAny(principal.delegatedFrom.department) ||
   resource.needToKnowList.contains(principal.delegatedFrom.id))
};
```

Embargo and tenant isolation are enforced as unconditional forbids:

```
forbid(
  principal, action == BankAI::Action::"AccessChunk", resource is BankAI::DocumentChunk
)
when {
  resource has embargoUntil && context.currentTime < resource.embargoUntil
};

forbid(principal, action, resource is BankAI::DocumentChunk)
when { resource.tenantId != principal.tenantId };
```

**Vector database filtering implementation.** Modern vector databases support metadata filtering at query time. The pre-retrieval filter is constructed from the canonical claims before the similarity search executes — mapping the user's clearance level to a set of permitted classifications, and building a query filter requiring tenant match, an allowed classification, and geography match, with a should-clause covering department ownership or need-to-know membership, and a must-not clause excluding embargoed documents:

```python
def build_rag_filter(canonical_claims: dict) -> dict:
    user = canonical_claims["principal"]
    org = canonical_claims["organization"]
    clearance_map = {
        "L1": ["PUBLIC"],
        "L2": ["PUBLIC", "INTERNAL"],
        "L3": ["PUBLIC", "INTERNAL", "CONFIDENTIAL"],
        "L4": ["PUBLIC", "INTERNAL", "CONFIDENTIAL", "SECRET"],
        "L5": ["PUBLIC", "INTERNAL", "CONFIDENTIAL", "SECRET", "TOP_SECRET"],
    }
    clearance = user.get("clearance_level", "L2")
    allowed_classifications = clearance_map.get(clearance, ["PUBLIC"])
    return {
        "bool": {
            "must": [
                {"term": {"tenant_id": org["tenant_id"]}},
                {"terms": {"classification": allowed_classifications}},
                {"terms": {"geography_restriction": [org["geography"], "GLOBAL"]}},
            ],
            "should": [
                {"terms": {"department_owners": [org["department"]]}},
                {"term": {"need_to_know_list": user["id"]}},
            ],
            "minimum_should_match": 1,
            "must_not": [{"range": {"embargo_until": {"gte": "now"}}}],
        }
    }
```

## Memory Authorization Architecture

AI agents use multiple types of memory, each with different authorization requirements. An agent must never access another user's memory without explicit authorization.

**Memory type taxonomy and authorization model:**

| Memory Type | Scope | Authorization Model | Cedar Policy |
|---|---|---|---|
| Working Memory (in-context) | Current conversation window | Owned by session — no cross-session access; the agent may only hold context from its own authorized sources | Implicit — scope is session-bound |
| Episodic Memory (short-term) | Recent interactions for this user-agent pair | Private to the user; the agent can read its own episodic memory only. A manager may have read access with an explicit capability | `principal.userId == memory.ownerId` |
| Long-term Memory (semantic) | Learned patterns, user preferences | User-scoped; cannot be shared without explicit consent; tenant-isolated | `memory.tenantId == principal.tenantId AND memory.ownerId == principal.userId` |
| Shared Memory (team/project) | Project context shared across users | Shared within a defined group; group membership checked via Cedar; no cross-group access | `principal.projectMemberships contains memory.projectId` |
| Organizational Memory (enterprise KB) | Company-wide knowledge base | Full RAG authorization applies; classification and capability-based | Full RAG policy stack |

**Cedar policies for memory protection.** Agents may read memory they own or, with an explicit manager capability, memory owned by their team:

```
permit(
  principal is BankAI::Agent, action == BankAI::Action::"ReadMemory",
  resource is BankAI::MemoryRecord
)
when {
  (resource.ownerId == principal.delegatedFrom.id && resource.tenantId == principal.tenantId) ||
  (principal.delegatedFrom.capabilities.contains("can_read_team_memory") &&
   resource.teamId == principal.delegatedFrom.teamId)
};
```

Memory writes are scoped strictly to the agent's own delegating user and to non-organizational memory scopes:

```
permit(
  principal is BankAI::Agent, action == BankAI::Action::"WriteMemory",
  resource is BankAI::MemoryRecord
)
when {
  resource.ownerId == principal.delegatedFrom.id &&
  resource.tenantId == principal.tenantId &&
  context.memoryScope in ["WORKING", "EPISODIC", "PERSONAL_SEMANTIC"]
};
```

Shared project memory requires explicit project membership, and cross-tenant memory access is an unconditional hard block:

```
permit(
  principal is BankAI::Agent, action == BankAI::Action::"ReadMemory",
  resource is BankAI::MemoryRecord
)
when {
  resource.memoryType == "SHARED_PROJECT" &&
  principal.delegatedFrom.projectMemberships.contains(resource.projectId) &&
  resource.tenantId == principal.tenantId
};

forbid(principal, action, resource is BankAI::MemoryRecord)
when { resource.tenantId != principal.tenantId };
```

**Memory protection implementation:**

| Memory Storage | Authorization Control | Implementation |
|---|---|---|
| DynamoDB (working/episodic) | Partition key `userId#tenantId`; IAM policy restricts the agent role to its own partition | DynamoDB condition expressions + Cedar post-read verify |
| OpenSearch (semantic memory) | Index-per-tenant pattern; OpenSearch security plugin (row-level security) | Pre-query filter + Cedar chunk authorization |
| Redis ElastiCache (working context) | Key prefix `tenant:user:session`; no cross-key access in the agent role | Redis AUTH + namespace isolation |
| S3 (long-term memory snapshots) | Object key `tenant/user-id/memory/`; IAM boundary restricts the agent | S3 resource policy + Cedar evaluation on read |
| RDS PostgreSQL (shared memory) | Row-level security policies (Postgres RLS) + Cedar post-read filter | Postgres RLS + Cedar authorization |

## Multi-Tenant Data Isolation

Multi-tenant AI deployments must guarantee that one tenant's agents, tools, knowledge, and memory can never interact with another tenant's data — this requires defense-in-depth across the IAM, data, and Cedar policy layers.

**Tenant isolation defense layers:**

| Layer | Isolation Mechanism | Enforced By |
|---|---|---|
| IAM / AWS Identity | ECS task roles scoped to tenant-specific resources | IAM policies, resource tags |
| Network | VPC per tenant or subnet isolation with NACLs | VPC, Security Groups, NACLs |
| Data Storage | Partition-per-tenant (DynamoDB, OpenSearch index, S3 prefix) | Storage configuration + IAM |
| Cedar Policy | Mandatory forbid: `resource.tenantId != principal.tenantId` | Cedar AVP (always evaluated) |
| Vector Search | Pre-query metadata filter: `tenant_id = :tenant` | RAG retrieval layer |
| Memory | Key namespace `tenant:userId` — no cross-namespace access | Storage key design + IAM |
| API Gateway | Custom domain per tenant with tenant claim validation | API GW + Lambda Authorizer |
| Audit Logs | CloudTrail + per-tenant log group isolation | CloudWatch Log Groups |
| Encryption | Per-tenant KMS keys for data at rest | AWS KMS, CMK per tenant |

**Tenant isolation Cedar pattern.** This policy must be the first evaluated: Cedar's forbid-unless pattern guarantees isolation even if another permit policy would otherwise allow access, because a matching forbid always overrides any permit:

```
// Forbid all cross-tenant access to any resource
forbid(principal, action, resource)
when {
  resource has tenantId &&
  principal has tenantId &&
  resource.tenantId != principal.tenantId
};

// For agents, also check the delegated user's tenant
forbid(principal is BankAI::Agent, action, resource)
when {
  resource has tenantId &&
  principal.delegatedFrom has tenantId &&
  resource.tenantId != principal.delegatedFrom.tenantId
};
```

Cedar evaluates all applicable policies for a request, and a single forbid overrides every permit — these tenant-isolation forbids always win.

## Output Classification and Filtering

Authorization does not end when a tool executes or a document is retrieved. The output must be classified and filtered before being returned to the user or injected into the next agent step, preventing data leakage through the LLM generation layer itself.

**Output classification pipeline.** The raw LLM response is passed through automated classification (AWS Macie patterns for PII detection, Bedrock Guardrails content policy, and a custom classifier for CONFIDENTIAL/SECRET material), producing a result such as `{PII: false, class: INTERNAL}`. Cedar then evaluates whether this user can receive output of this classification from this agent, returning `ALLOW`/`DENY` with optional redaction obligations. If obligated, redaction/filtering runs — PII is replaced with `[REDACTED]`, over-clearance content strips classified references, and cross-tenant references are removed. A final DLP scan (Amazon Macie or custom patterns) blocks the response outright if sensitive patterns are detected. The output classification and its content hash are written to the audit log (CloudTrail plus a DynamoDB audit record), and only then is the filtered, classified response returned to the user.

**Data sensitivity classification model:**

| Level | Label | Examples | Agent Policy |
|---|---|---|---|
| L0 | PUBLIC | Marketing docs, public web content | All agents may retrieve and return |
| L1 | INTERNAL | Internal memos, process docs | Authenticated users only, no external channels |
| L2 | CONFIDENTIAL | Customer data, contracts, budgets | Capability required, MFA, logged |
| L3 | SECRET | M&amp;A details, legal strategy, key material | Need-to-know list, MFA, approval, DLP active |
| L4 | TOP_SECRET | Board-level strategy, regulator confidential | Explicit person list only, dual approval, offline audit |

**Best practice — Bedrock Guardrails integration.** Amazon Bedrock Guardrails provide a native output-filtering layer that can be configured with Cedar policy decisions as context. When Cedar returns an obligation to redact PII, Bedrock Guardrails can apply the redaction pattern to the LLM output in a single integrated call, eliminating the need to post-process raw LLM output in application code.

## Related

- [AWS/Entra Federation Patterns](30-4b-aws-entra-federation-patterns.md)
- [Agent Authorization Deep Dive](28-3b-agent-authorization-deep-dive.md)
- [AWS Implementation & Governance](31-aws-implementation-governance.md)
