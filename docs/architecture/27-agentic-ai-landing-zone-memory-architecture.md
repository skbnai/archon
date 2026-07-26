---
title: "Agentic AI Landing Zone: Memory Architecture (Tier 3)"
date_created: 2026-07-09
last_reviewed: 2026-07-10
status: current
source_type: native-md
doc_type: reference-architecture
domain: architecture
topic_id: agentic-ai-landing-zone-memory-architecture
maturity: practitioner
personas: [architect, platform-engineer, ai-engineer]
tags: ["ai-foundations", "agentic-ai", "memory-systems"]
supersedes: ["docs/ai-foundations/agentic_ai_landing_zone_memory_architecture.md"]
covers_version: "as of 2026-07-10"
---

# Agentic AI Landing Zone: Memory Architecture (Tier 3)

*Agents without memory are stuck in the present. Agents with well-designed memory become intelligent, adaptive, and trustworthy.*

---

## THE MEMORY PROBLEM

**Challenge:** Agents process each request in isolation.

```
Request 1: "What's my account balance?"
    ↓ Agent processes, generates response
    ✅ Response: "$2,345.67"
    - Memory: NONE

Request 2 (5 minutes later): "Has anything changed?"
    ↓ Agent has no memory of Request 1
    ❌ Response: "I don't know what your previous balance was"
    - Memory: NONE

User Frustration: 😤 "I just told you this!"
```

**Solution:** Systematic memory architecture that stores, retrieves, and manages agent intelligence across time.

---

## MEMORY TYPES: The Pyramid

**Agent Memory Architecture (Top-to-Bottom):**

```mermaid
graph TD
    A["ORGANIZATIONAL MEMORY<br/>Enterprise knowledge<br/>policies, history<br/>Shared across all agents"]
    B["SEMANTIC MEMORY<br/>Facts & relationships<br/>what we know<br/>Persistent, reusable"]
    C["EPISODIC MEMORY<br/>Experiences & events<br/>what happened<br/>Time-bound, contextual"]
    D["CONVERSATION MEMORY<br/>Current session<br/>what we said<br/>Short-term, operational"]
    E["WORKING MEMORY<br/>Current reasoning<br/>what we're thinking<br/>Ephemeral, task-specific"]
    
    A --> B
    B --> C
    C --> D
    D --> E
    
    style A fill:#f0e6ff
    style B fill:#e6d5ff
    style C fill:#dcc4ff
    style D fill:#d1b3ff
    style E fill:#c7a2ff
```

**Memory Hierarchy:** Organizational (enterprise-wide) → Semantic (factual) → Episodic (experiential) → Conversation (session) → Working (immediate reasoning)

---

## LAYER 1: WORKING MEMORY

**Purpose:** Immediate, ephemeral storage during active reasoning.

**What it stores:**

- Current task state
- Intermediate reasoning steps
- Active variables and computations
- Transient context from current request

**Characteristics:**

- ⏱️ **Lifetime**: Duration of single request/interaction
- 💾 **Storage**: In-memory (RAM)
- 🔄 **Scope**: Single agent instance
- 🗑️ **Cleanup**: Automatic (garbage collected after request)

**Example:**

```
User Request: "Can I return my order?"

Working Memory Contents (during processing):
- order_id: "98765"
- customer_id: "12345"
- current_step: "checking_return_eligibility"
- days_since_purchase: 8
- return_window_days: 30
- is_eligible: true
- reasoning_chain: [
  "Fetched order",
  "Calculated days since purchase",
  "Checked against 30-day window",
  "Determined eligible=true"
  ]
- confidence_score: 0.94

Request ends → Working memory discarded
```

**Implementation:**

```python
class WorkingMemory:
    """Ephemeral memory for current reasoning"""
    def __init__(self):
        self.state = {}
        self.reasoning_steps = []

    def set(self, key, value):
        self.state[key] = value

    def get(self, key):
        return self.state.get(key)

    def add_reasoning_step(self, step):
        self.reasoning_steps.append(step)

    def clear(self):
        """Auto-called at end of request"""
        self.state = {}
        self.reasoning_steps = []
```

---

## LAYER 2: CONVERSATION MEMORY

**Purpose:** Store messages within a session/conversation.

**What it stores:**

- User messages
- Agent responses
- Multi-turn dialogue history
- Session context

**Characteristics:**

- ⏱️ **Lifetime**: Single session (30 min - 1 day)
- 💾 **Storage**: In-memory cache or temp DB
- 🔄 **Scope**: Single conversation thread
- 🗑️ **Cleanup**: After session ends or TTL expires

**Variants:**

```
CONVERSATION WINDOW (Last N turns):
- Keep only last 5 exchanges
- Older messages summarized or discarded
- Example: Chat interface (last 10 messages visible)

FULL CONVERSATION HISTORY:
- Store all messages in session
- Index for search/retrieval
- Example: Support ticket (all interactions recorded)

SUMMARIZED CONVERSATION:
- Store key points, decisions, unresolved items
- Discard full text after N hours
- Example: "Customer asked about refunds, decided to wait"
```

**Example:**

```
Session: customer_12345_session_789

Message 1:
- User: "Hi, I want to return my order"
- Agent: "I'd be happy to help! What's your order number?"

Message 2:
- User: "Order 98765"
- Agent: "Great! Your order qualifies for return..."

Message 3:
- User: "What about shipping?"
- Agent: "We'll provide a prepaid label..."

Current agent can recall entire conversation
(After session ends → Store as episodic memory if needed)
```

**Implementation:**

```python
class ConversationMemory:
    def __init__(self, session_id, ttl_minutes=30):
        self.session_id = session_id
        self.messages = []
        self.created_at = datetime.now()
        self.ttl = ttl_minutes

    def add_message(self, role: str, content: str):
        self.messages.append({
            "role": role,  # "user" or "agent"
            "content": content,
            "timestamp": datetime.now()
        })

    def get_conversation_context(self):
        """Return formatted history for LLM context"""
        return "\n".join([
            f"{m['role']}: {m['content']}"
            for m in self.messages
        ])

    def is_expired(self):
        age_minutes = (datetime.now() - self.created_at).total_seconds() / 60
        return age_minutes > self.ttl

    def summarize(self):
        """Optional: Summarize and archive"""
        return {
            "session_id": self.session_id,
            "duration": datetime.now() - self.created_at,
            "message_count": len(self.messages),
            "key_topics": extract_topics(self.messages),
            "outcome": determine_outcome(self.messages)
        }
```

---

## LAYER 3: EPISODIC MEMORY

**Purpose:** Store specific events and experiences for retrieval.

**What it stores:**

- Past interactions (resolved support tickets)
- Historical decisions and their outcomes
- Customer behavior patterns
- Contextual events and circumstances

**Characteristics:**

- ⏱️ **Lifetime**: Months to years (retention varies)
- 💾 **Storage**: Database (PostgreSQL, Cosmos DB, etc.)
- 🔄 **Scope**: Specific to agent/user/domain
- 🔍 **Retrieval**: Query, search, semantic similarity
- 🔐 **Security**: Access controls, PII redaction

**Example: Customer Service Agent**

```
EPISODIC MEMORY STORE:

Episode 1: Customer 12345 returned item successfully
- Date: 2026-06-15
- Order: 98765
- Reason: Item damaged
- Resolution: Approved return, refund issued
- Processing time: 4 days
- Outcome: ✅ Successful

Episode 2: Customer 12345 complained about shipping
- Date: 2026-05-20
- Issue: Late delivery (5 days)
- Escalation: Human review needed
- Compensation: Free express shipping on next order
- Outcome: ✅ Resolved, customer satisfied

Episode 3: Customer 12345 asked about bulk discount
- Date: 2026-04-10
- Request: 10% discount for 5+ units
- Response: Policy requires 20+ units
- Customer reaction: Accepted explanation
- Outcome: ✅ Friendly decline

AGENT RETRIEVAL:
When customer 12345 calls again:
- Retrieve similar past episodes
- "This customer has been pleasant in past"
- "Resolved successfully before"
- "Had shipping issues once, now happy"
- Agent: More personalized, faster resolution
```

**Implementation:**

```python
class EpisodicMemory:
    def __init__(self, db_connection):
        self.db = db_connection

    def store_episode(self, episode: dict):
        """Store an event/experience"""
        episode["timestamp"] = datetime.now()
        episode["embedding"] = embed_text(episode["description"])
        self.db.insert("episodic_memory", episode)

    def retrieve_similar_episodes(self, query: str, limit=5):
        """Find similar past experiences"""
        query_embedding = embed_text(query)
        similar = self.db.similarity_search(
            "episodic_memory",
            query_embedding,
            limit=limit
        )
        return similar

    def retrieve_customer_history(self, customer_id: str):
        """Get all episodes for a customer"""
        return self.db.query(
            "SELECT * FROM episodic_memory WHERE customer_id = ?",
            [customer_id],
            order_by="timestamp DESC"
        )

    def extract_patterns(self, customer_id: str):
        """Analyze episodes to find patterns"""
        episodes = self.retrieve_customer_history(customer_id)
        return {
            "avg_issue_resolution_time": avg([
                e["resolution_time"] for e in episodes
            ]),
            "common_issues": mode([e["issue_type"] for e in episodes]),
            "satisfaction_trend": trend([e["satisfaction"] for e in episodes]),
            "risk_score": calculate_risk(episodes)
        }
```

---

## LAYER 4: SEMANTIC MEMORY

**Purpose:** Store facts, relationships, and knowledge.

**What it stores:**

- Company policies and procedures
- Product information
- Customer preferences and segments
- Entity relationships (who knows whom, what depends on what)
- Facts and rules

**Characteristics:**

- ⏱️ **Lifetime**: Persistent (months to years)
- 💾 **Storage**: Knowledge graphs (Neo4j), vector DBs (Pinecone), or documents
- 🔄 **Scope**: Shared across multiple agents
- 🧠 **Encoding**: Embeddings (semantic similarity) or structured (graphs)
- 🔄 **Update**: Batched or real-time, depending on freshness requirements

**Examples:**

```
SEMANTIC FACTS (Knowledge Graph):

Products:
- iPhone 15 Pro
  - Price: $999
  - Warranty: 1 year
  - Color options: [Black, Silver, Gold, Purple]
  - Related: [iPhone 15, iPhone 15 Max]
  - iPad Air
   - Price: $599
   - Warranty: 1 year
   - Bundle offers: [Apple Pencil, Magic Keyboard]

Policies:
- Return Policy
  - Window: 30 days
  - Condition: Unopened/unused
  - Exceptions: [Electronics, Accessories]
  - Refund method: Original payment
  - Warranty Policy
   - Coverage: Manufacturing defects
   - Duration: 1 year
   - Claim process: [Contact support, Provide proof, Ship to warehouse]

Relationships:
- Customer 12345 → Tier: Gold Member
- Gold Member → Benefits: [Free shipping, Extended warranty]
- Customer 12345 → Previous orders: [Order 98765, Order 98764, ...]
- Order 98765 → Product: iPhone 15 Pro
```

**Vector-Based Semantic Memory:**

```
Query: "Can I return my phone after 30 days?"

Embedding the question:
- Vector: [0.234, -0.145, 0.892, ..., 0.567]

Semantic search in knowledge base:
- "30-day return policy" → Similarity: 0.98 ✓
- "Return window 30 days for phones" → Similarity: 0.96 ✓
- "Can't return damaged items" → Similarity: 0.78 ⚠️
- "Warranty covers phone defects" → Similarity: 0.45 ✗

Result: "No, return window is 30 days. You're at day 31."
```

**Implementation:**

```python
class SemanticMemory:
    def __init__(self, vector_db, knowledge_graph_db):
        self.vector_db = vector_db  # Pinecone, Weaviate
        self.kg_db = knowledge_graph_db  # Neo4j

    def store_fact(self, fact: str, metadata: dict):
        """Store fact with embedding"""
        embedding = embed_text(fact)
        self.vector_db.upsert({
            "id": metadata["id"],
            "text": fact,
            "embedding": embedding,
            "metadata": metadata
        })

    def retrieve_fact(self, query: str, threshold=0.8):
        """Search for relevant facts"""
        query_embedding = embed_text(query)
        results = self.vector_db.query(
            query_embedding,
            top_k=5,
            threshold=threshold
        )
        return results

    def get_entity_relationships(self, entity_id: str):
        """Retrieve entity from knowledge graph"""
        return self.kg_db.query(
            f"MATCH (n {{id: '{entity_id}'}}) "
            f"RETURN n, relationships(n)"
        )

    def update_policy(self, policy_id: str, new_policy: dict):
        """Update fact in knowledge base"""
        self.vector_db.upsert({
            "id": policy_id,
            "text": new_policy["text"],
            "embedding": embed_text(new_policy["text"]),
            "metadata": {"updated_at": datetime.now()}
        })
```

---

## LAYER 5: ORGANIZATIONAL MEMORY

**Purpose:** Shared knowledge across all agents and the organization.

**What it stores:**

- Company knowledge base (procedures, best practices)
- Training data and examples
- Historical decisions and precedents
- Aggregate insights and trends
- Lessons learned and playbooks

**Characteristics:**

- ⏱️ **Lifetime**: Permanent
- 💾 **Storage**: Central repository (Wiki, Confluence, custom DB)
- 🔄 **Scope**: Shared across organization
- 👥 **Contributors**: Humans + agents (both can add to it)
- 📊 **Analytics**: Can be analyzed for patterns

**Example: Customer Service Playbook**

```
ORGANIZATIONAL MEMORY:

Playbook: Handling High-Value Customer Complaints

Context:
- Applies to: Orders > $1,000
- Created: 2026-01-15
- Updated: 2026-06-20
- Owner: Customer Service Leadership

Steps:
- Step 1: Acknowledge emotion ("I understand your frustration")
- Step 2: Take ownership ("I'll personally handle this")
- Step 3: Escalate authority
  - Agent can approve: Up to $500 credit
  - Manager can approve: Up to $2,000 credit
  - Director can approve: Up to $10,000 credit
- Step 4: Follow up within 24 hours
- Step 5: Document for future reference

Success Rate:
- Customer retention: 87% (vs 45% without playbook)
- Issue resolution time: 4.2 hours (vs 8.1 hours)
- Customer satisfaction: 4.7/5 (vs 2.1/5)

Lessons Learned:
- Acknowledge emotion first (increases retention by 15%)
- Faster authority delegation improves outcomes (20% better)
- 24-hour follow-up critical (prevents 70% of escalations)
```

**Uses:**

```
Agent accessing organizational memory:

Agent A (New, 1 month old):
- "I don't know how to handle this high-value complaint"
   - Retrieves playbook from organizational memory
   - Follows steps exactly
   - Achieves 87% retention rate (matches experienced team)

Agent B (Experienced, 3 years old):
- "I see a pattern we haven't seen before"
   - Documents new case + solution
   - Adds to organizational memory
   - All other agents now benefit from this learning
```

---

## MEMORY LIFECYCLE & GOVERNANCE

### Storage Tiers

| Layer | Storage Type | Retention | Query Time | Cost |
|---|---|---|---|---|
| Working | RAM | 5 min | &lt; 1ms | ✓✓ (free) |
| Conversation | Cache / Temp DB | 24 hours | &lt; 100ms | ✓ (cheap) |
| Episodic | Production DB | 7 years | &lt; 500ms | $$ (medium) |
| Semantic | Vector DB | Permanent | &lt; 200ms | $$ (medium) |
| Organizational | Central Repo | Permanent | &lt; 1s | $$ (medium) |

### Memory Hygiene

**What to delete (privacy/compliance):**

- ✅ PII after retention period (GDPR: 7 years)
- ✅ Financial data (older than 7 years)
- ✅ Deleted customer data (right to erasure)
- ✅ Sensitive credentials (never store)

**What to keep:**

- ✅ Anonymized patterns (for learning)
- ✅ Aggregated statistics (trends, insights)
- ✅ Business decisions (compliance trail)
- ✅ Playbooks and lessons learned

---

## MEMORY ACCESS CONTROL

**Who can access what?**

```
Agent A (Customer Service, limited authority):
- Can read: Own conversation history, customer profile, policies
- Can write: Conversation history, episodic memory (own interactions)
- Cannot read: Other agents' episodic memories, confidential payroll

Agent B (Compliance, high authority):
- Can read: All episodic memories (for compliance auditing)
- Can write: Organizational policies, compliance playbooks
- Cannot write: Customer conversation history (data isolation)

Human Analyst:
- Can read: Anonymized aggregated data, trends
- Can read/write: Playbooks, training materials
- Cannot read: Individual customer conversations (privacy)
```

---

## MEMORY COSTS & OPTIMIZATION

### Cost Breakdown (Annual, for 1M conversations/month)

```
Conversation Memory (temp storage):
- 1M conversations × 5KB avg = 5TB/month
   - Cost: $100/month = $1,200/year

Episodic Memory (7-year retention):
- 1M conversations × 2KB stored = 2TB/month
   - Cost: $150/month = $1,800/year

Semantic Memory (vector store):
- 1M embeddings × 1.5KB = 1.5TB
   - Cost: $50/month = $600/year

Organizational Memory (central repo):
- Policies, playbooks, training = 100GB
   - Cost: $5/month = $60/year

**TOTAL MEMORY COST: ~$3,660/year**
(Small compared to model inference)
```

### Optimization Strategies

**Compression:**

- ✅ Summarize old conversations (after 30 days)
- ✅ Archive episodic memory (move to cold storage after 2 years)
- ✅ Prune semantic memory (remove unused facts)

**Partitioning:**

- ✅ Separate by customer (faster queries)
- ✅ Separate by agent type (only agents that need it)
- ✅ Separate by time period (hot recent, cold historical)

**Deduplication:**

- ✅ Remove duplicate facts (single source of truth)
- ✅ Consolidate similar episodes
- ✅ Remove outdated policies

---

## IMPLEMENTATION CHECKLIST

```
Working Memory:
- [ ] In-memory storage (dict/cache)
- [ ] Auto-cleanup after request
- [ ] Logging for debugging

Conversation Memory:
- [ ] Database schema designed
- [ ] TTL configured (30 min - 1 day)
- [ ] Summarization logic (optional)
- [ ] Indexing for queries

Episodic Memory:
- [ ] Production database (PostgreSQL, etc.)
- [ ] Embeddings generated (for similarity search)
- [ ] Retention policy (7 years for compliance)
- [ ] Access controls (who can see what)
- [ ] PII redaction rules

Semantic Memory:
- [ ] Vector database (Pinecone, Weaviate, etc.)
- [ ] Knowledge graph (Neo4j, optional)
- [ ] Embedding model selected (OpenAI, Anthropic, local)
- [ ] Facts populated (policies, products, relationships)
- [ ] Update process (batch or real-time)

Organizational Memory:
- [ ] Central repository (Wiki, Confluence, custom)
- [ ] Playbooks documented
- [ ] Access controls (who can contribute)
- [ ] Version control (for playbook evolution)
- [ ] Search/retrieval interface

Governance:
- [ ] Retention policies documented
- [ ] PII handling guidelines
- [ ] Access control matrix
- [ ] Audit logging (who accessed what)
- [ ] Compliance review (GDPR, CCPA, etc.)
```

## Related

- [Agent Memory & Planning Architecture](41-agent-memory-planning-architecture.md) — deeper technical dive on the memory patterns summarized here.
- [Agentic AI Landing Zone Architecture](22-agentic-ai-landing-zone-architecture.md) — the base landing zone this memory tier belongs to.
- [Data & Knowledge Hub](../data-knowledge/index.md) — the RAG and long-term memory backends this tier relies on.

---

**Next Tier 3 Document:** Agent Identity & Trust Architecture  
**Related:** Context Engineering (how agents get data into working/conversation memory)  
**Estimated Full Tier 3:** 5 documents, ~8,000 lines, ready by midnight
