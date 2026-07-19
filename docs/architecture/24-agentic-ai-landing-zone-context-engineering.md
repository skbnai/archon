---
title: "Agentic AI Landing Zone: Context Engineering Layer"
doc_type: guide
domain: architecture
status: current
canonical: true
topic_id: agentic-ai-landing-zone-context-engineering
maturity: practitioner
personas: [architect, engineer, platform-engineer]
last_reviewed: 2026-07-19
covers_version: ""
supersedes: [docs/ai-foundations/agentic_ai_landing_zone_context_engineering.md]
tags: [agentic-ai, context-engineering, landing-zone, rag, knowledge-base]
sources: []
---

# Agentic AI Landing Zone: Context Engineering Layer

Context is not an afterthought — it's the primary design constraint for production agentic AI.

## Why This Matters

Agents fail not because of models, but because of context. Production systems demand systematic attention to how data is assembled, secured, optimized, and kept fresh. This guide treats **context engineering** as a first-class architecture concern, not a prompt engineering detail.

---

## The Context Lifecycle

```mermaid
graph TD
    A["Business Process / User Request<br/>What does this agent need to know?"]
    B["Context Assembly<br/>Identify required data sources<br/>Fetch data<br/>Validate freshness & permissions"]
    C["Context Compression<br/>Optimize for latency & cost<br/>Summarize if > 100KB<br/>Remove redundant fields"]
    D["Context Security<br/>Enforce access control<br/>Check user identity & permissions<br/>Redact sensitive data<br/>Log context access"]
    E["Context Injection<br/>System prompt: strategic knowledge<br/>User message: immediate data<br/>Examples: Few-shot demonstrations"]
    F["Agent Reasoning & Action<br/>Model uses context to decide next step"]
    G["Context Refresh<br/>Time-to-live TTL<br/>Trigger refresh on state changes<br/>Detect context drift"]
    
    A --> B --> C --> D --> E --> F --> G
    
    style A fill:#ffcccc
    style B fill:#fff3cd
    style C fill:#fff3cd
    style D fill:#fff3cd
    style E fill:#d4edda
    style F fill:#cfe2ff
    style G fill:#d4edda
```

The context lifecycle progresses from assembly through compression and security to injection, reasoning, and refresh.

---

## CONTEXT SOURCES & INTEGRATION PATTERNS

### Data Source Categories

**Structured Data:**
- **Databases (SQL, NoSQL)** — Customer profile, order history, transaction records
- **APIs (REST, GraphQL)** — Real-time inventory, pricing, availability
- **Data Warehouses (Snowflake, BigQuery, Redshift)** — Aggregated metrics, analytics, historical trends

**Semi-Structured Data:**
- **Document stores (JSON, XML)** — Product specifications, legal documents
- **Object storage (S3, Blob Storage)** — Customer files, contracts, image assets

**Unstructured Data:**
- **Vector stores / Knowledge bases** — Embeddings of company policies, FAQs, documentation
- **Knowledge graphs** — Entity relationships (who reports to whom, product dependencies)
- **Logs & audit trails** — Historical context (previous decisions, customer history)

**Real-Time Data:**
- **Message queues (Kafka, Pub/Sub)** — Live inventory changes, order status
- **WebSockets / Server-sent events** — Stock prices, weather, sports scores
- **External APIs (polling)** — Competitor pricing, market data

### Integration Pattern: MCP for Context

**Model Context Protocol** is the emerging standard for connecting agents to context sources.

```mermaid
graph TD
    A["Agent<br/>(running LangGraph)"]
    B["MCP Client<br/>Discovers available tools<br/>Calls: fetch_customer id=12345<br/>Validates user permissions<br/>Handles retries & errors"]
    C["MCP Server - Database<br/>Query customer_db<br/>with row-level security"]
    D["MCP Server - Knowledge<br/>Search embeddings<br/>in Pinecone/Weaviate"]
    E["MCP Server - API<br/>Call REST endpoints<br/>rate-limited"]
    F["MCP Server - File<br/>Serve documents<br/>from S3"]
    G["Response<br/>Data returned to agent<br/>Audit logged<br/>Cost tracked"]
    
    A --> B
    B --> C
    B --> D
    B --> E
    B --> F
    C --> G
    D --> G
    E --> G
    F --> G
    
    style A fill:#e3f2fd
    style B fill:#cfe2ff
    style C fill:#d4edda
    style D fill:#d4edda
    style E fill:#d4edda
    style F fill:#d4edda
    style G fill:#fff3cd
```

MCP provides a standardized protocol connecting agents to multiple data sources through separate server implementations.

---

## CONTEXT ASSEMBLY STRATEGIES

### Strategy 1: Eager Context (Fetch Everything Upfront)

**When to use:** Low-complexity requests, small context size

```yaml
Agent: "User asks: What's my account balance?"

Context Assembly:
1. Fetch customer record (20KB)
2. Fetch account balances (5KB)
3. Fetch recent transactions (10KB)
4. Fetch payment methods (3KB)
────────────────────────
Total Context: ~38KB (small)
Latency: ~200ms (acceptable)

Prompt:
────────────────────────
System:
"You are a customer service agent. Help customers with account inquiries.
Current user: Customer ID 12345
Customer Status: Verified, Account Age: 5 years
Account Balance: $2,345.67
Last Transaction: 2026-07-09 10:30 (Amazon purchase $50.23)"

User:
"What's my account balance?"

Agent Output:
"Your account balance is $2,345.67. Your last transaction was..."
```

**Pros:**
- ✅ Simple, predictable
- ✅ No mid-conversation delays
- ✅ Full context available for reasoning

**Cons:**
- ❌ Wastes tokens on unused context
- ❌ Latency increases with data size
- ❌ Harder to keep fresh during long conversations

---

### Strategy 2: Lazy Context (Fetch On Demand)

**When to use:** Complex requests, large potential context, need for specificity

```yaml
Agent: "User asks a complex question requiring specific data lookup"

Context Assembly:
1. System prompt loaded (2KB)
2. User query injected (1KB)

Agent Decides: "I need to check transactions and account history"
    ↓
Agent calls MCP tools on demand:
    - mcp://db/fetch_transactions(account_id, date_range)
    - mcp://kb/search(query="refund policy")

Context grows dynamically: 5KB → 15KB → 25KB

Latency: ~400ms (higher, but context is fresh)
```

**Pros:**
- ✅ Only fetch what's needed
- ✅ Cost-efficient (smaller prompts)
- ✅ Can adapt to conversation flow

**Cons:**
- ❌ Introduces latency (tool calls mid-conversation)
- ❌ Harder to reason about (incomplete context initially)
- ❌ Risk of "forgotten" relevant facts

---

### Strategy 3: Hybrid Context (Smart Prefetch + On-Demand)

**Most production systems use this:**

**Agent Request:** "Customer calls with a complaint"

**Phase 1: Prefetch (Immediate, <100ms)**
- Customer record (identity, account status)
- Recent order (most likely relevant)
- Cached FAQ about common issues
- Total: ~15KB

**Phase 2: Agent Reasoning (with prefetched context)**
- "The customer is complaining about order X"
- "I need to check refund policy and shipping history"

**Phase 3: On-Demand Fetch (if needed)**
- Full order details (shipping, tracking)
- Previous refund history (patterns)
- Competitor return policies (context for decision)
- Total Context: ~35KB by end

**Latency Profile:**
- Initial response: 150ms (prefetched)
- Complex reasoning: 300-500ms (lazy context added)

---

## CONTEXT COMPRESSION: Fit More In Less

### Problem: Context Bloat

**Scenario:** Customer asks about a product.

**Naive Context Injection:**
- Product DB row (500B)
- Customer profile (1KB)
- Product category (500B)
- Customer order history (20 orders × 500B = 10KB)
- Customer support tickets (50 tickets × 2KB = 100KB)
- Product reviews (1000 reviews × 500B = 500KB)
- Competitor comparison (5KB)

**TOTAL: ~625KB**

**Cost:**
- Tokens used: 625KB / 0.75 bytes per token ≈ 833 tokens
- Input cost: 833 × $0.003 = $0.0025 per query
- Volume: 1000 queries/day = $2.50/day = $75/month
- **ANNUAL COST: $900 just for context bloat**

### Compression Techniques

#### 1. Summarization (Reduce Volume)

**BEFORE (customer history):**
- Order 1: 2026-06-15, $150, delivered
- Order 2: 2026-06-08, $45, delivered
- Order 3: 2026-06-01, $200, delivered
- Order 4: 2026-05-25, $30, returned
- Order 5: 2026-05-18, $175, delivered
- ... (20 orders total) ...

**AFTER (one-line summary):**
- Customer has 20 orders, avg $120, 85% delivery success, 1 return history
- Most recent: $150 delivered 2026-06-15

**SAVINGS:** From 10KB → 200 bytes (98% reduction)

#### 2. Prioritization (Keep High-Signal)

**CUSTOMER SUPPORT TICKETS (50 total):**

**Keep:**
- Last 5 tickets (most relevant, time-ordered)
- Any "UNRESOLVED" tickets
- Total: ~8 tickets → 16KB

**Discard:**
- Resolved tickets from 6+ months ago
- Duplicate/similar issues
- Low-severity tickets
- Total: ~42 tickets → 80KB saved

**Context: 100KB → 20KB (80% reduction)**

#### 3. Semantic Filtering (Extract Meaning)

**PRODUCT REVIEWS (1000 total):**

**Naive:** Include all reviews (500KB)

**Smart: Extract themes**
- Positive themes: "Easy setup (20%)", "Great quality (45%)"
- Negative themes: "Slow shipping (15%)", "Fragile packaging (10%)"
- Neutral: "Gray color available"
- Score: 4.2/5 from 1000 reviews

**Semantic Summary: 2KB (vs 500KB)**

### Compression Rules of Thumb

| Data Type | Compression Strategy | Max Size | Example |
| ----------- | --------------------- | ---------- | --------- |
| Customer profile | Keep current, discard archived | 1KB | Name, ID, status, account age |
| Order history | Summarize, keep last 5 | 2KB | "20 orders, avg $120, 85% success" |
| Support history | Last 3 unresolved tickets | 5KB | Recent issues, last resolution |
| Product info | Full spec, drop reviews | 2KB | Features, price, inventory |
| Knowledge base hits | Top 3 documents, not all 100 | 3KB | Top FAQ answers by relevance |
| **TOTAL TARGET** | | **~15KB** | Most requests should fit here |

---

## CONTEXT SECURITY: Enforce Access Control

### Context Access Control Flow

```mermaid
graph TD
    A["Agent Request for Context<br/>Give me customer order history<br/>for customer_id=12345"]
    B["1. AUTHENTICATE<br/>Who is making this request?<br/>Result: agent-token with permissions"]
    C["2. AUTHORIZE<br/>Does agent have permission?<br/>Is customer_id in scope?<br/>Result: ALLOW or DENY"]
    D["3. ROW-LEVEL SECURITY<br/>Filter orders where user_id = 12345<br/>Exclude other customers<br/>Result: Only relevant rows"]
    E["4. COLUMN-LEVEL SECURITY<br/>Include: order_id, amount, date, status<br/>Exclude: credit_card, internal_cost<br/>Mask: ssn"]
    F["5. LOG & AUDIT<br/>Log: agent_id, timestamp, data_accessed<br/>Classification: PII accessed<br/>Compliance: 7-year retention"]
    G["6. RETURN TO AGENT<br/>Safe, filtered context ready for LLM"]
    
    A --> B --> C --> D --> E --> F --> G
    
    style A fill:#ffcccc
    style B fill:#fff3cd
    style C fill:#fff3cd
    style D fill:#d4edda
    style E fill:#d4edda
    style F fill:#cfe2ff
    style G fill:#d4edda
```

Context security flows through six stages: authentication, authorization, row and column filtering, audit logging, and finally safe injection into the LLM.

### Sensitive Data Patterns

**Automatic detection & masking:**

```yaml
Patterns Detected Automatically:
├─ Credit cards: 16-digit numbers → "****-****-****-1234"
├─ SSN: XXX-XX-#### → "***-**-1234"
├─ Email: user@company.com → "u***@c***.com"
├─ Phone: 1-555-1234 → "1-555-****"
├─ API keys: sk_live_... → "[REDACTED]"
└─ Passwords: any field named "password" → "[REDACTED]"

Custom Rules (organization-specific):
├─ Financial data: Only show to agents in "Finance" domain
├─ Medical: Only show to healthcare agents
├─ Internal IP addresses: Mask from external-facing agents
└─ [Your rules here]
```

---

## CONTEXT FRESHNESS: TTL & Invalidation

### Time-to-Live (TTL) Strategy

```yaml
CONTEXT TYPE → TTL

Customer Profile:
  - If accessed today: 24-hour TTL (unlikely to change)
  - Last accessed: 2026-07-09T10:30Z
  - Expires: 2026-07-10T10:30Z
  └─ Refresh trigger: Account status change event

Inventory / Stock:
  - Real-time data: 5-minute TTL
  - Last accessed: 2026-07-09T16:45:00Z
  - Expires: 2026-07-09T16:50:00Z
  └─ Refresh trigger: Inventory update event (webhook)

Pricing / Exchange Rates:
  - Hourly: 60-minute TTL
  - Daily: 24-hour TTL

FAQs / Policies:
  - Stable: 7-day TTL (rarely change)
  - Last updated: 2026-07-02
  - Expires: 2026-07-09 (refresh on update)
  └─ Refresh trigger: Policy document changed
```

### Smart Invalidation (Event-Driven)

Instead of waiting for TTL, invalidate on events:

```
Data Source (e.g., Customer DB)
    ↓ publishes event
"Customer 12345 status changed: active → suspended"
    ↓
Event Bus (Kafka, Event Hub, Pub/Sub)
    ↓
Cache Invalidation Service
    ├─ Remove: customer_12345 from cache
    ├─ Notify: any agents with cached context for this customer
    └─ Log: context invalidation event
    ↓
Next request: Agent refetches fresh context
```

---

## CONTEXT BUDGET: Cost & Latency Constraints

### Define Context Budgets

```yaml
Customer Service Agent:
  max_input_tokens: 2000       # Context can't exceed this
  max_context_size_kb: 8       # Physical limit (~8KB)
  max_fetch_latency_ms: 200    # Context assembly deadline
  cost_budget_per_query: $0.05 # Max cost for context + inference

  Breakdown:
  ├─ Context tokens: 1000 (~$0.003)
  ├─ Model reasoning: 800 (~$0.006)
  ├─ MCP tool calls: 1-3 (~$0.01)
  └─ TOTAL: ~$0.02 per query (within budget)

Financial Analysis Agent:
  max_input_tokens: 4000       # Can use more context
  max_context_size_kb: 25      # Larger budget for complex analysis
  max_fetch_latency_ms: 500    # OK to wait longer
  cost_budget_per_query: $0.15 # Higher-value queries
```

### Context Budget Violations

**What happens if context exceeds budget?**

```
Agent attempts to load 50KB of customer history

Context Budget: 8KB max
Actual Size: 50KB
Status: OVER BUDGET

Fallback Strategy:
1. Compress: Summarize to 8KB
2. If still over: Prioritize (recent + unresolved only)
3. If still over: Reject expensive context, use defaults
4. Alert: Monitor if this happens repeatedly

Log:
├─ Timestamp: 2026-07-09T16:45:30Z
├─ Agent: customer-service-v2.4
├─ Requested: 50KB
├─ Budget: 8KB
├─ Action: Compressed to 7.2KB
└─ Cost Impact: Saved $0.02 but reduced context quality
```

---

## CONTEXT DRIFT: When Context Goes Stale

### Detection & Recovery

```yaml
Long-running agent (multi-turn conversation):

Turn 1 (14:00):
  Context: Customer order status = "In Transit"

Turn 5 (14:15): [15 minutes later]
  Agent references: "Your order is in transit"

BUT: Order delivered in the meantime!
  Real status (14:15): "Delivered"

PROBLEM: Context drifted! Agent is misinformed.

SOLUTION:
├─ Detect: Check TTL on context
│  └─ If context older than 5 minutes, refresh
│  
├─ Refresh: Refetch order status
│  └─ New status: "Delivered"
│  
├─ Update: Inject fresh context
│  └─ System: "Updated information: Your order was delivered at 14:05"
│  
└─ Correct: Agent now has accurate information
```

### Refresh Triggers

```yaml
AUTOMATIC (Time-based):
├─ Every N minutes (configurable per data type)
└─ Example: Inventory refreshes every 5 min

EVENT-TRIGGERED (Data-driven):
├─ On order status change
├─ On customer account change
├─ On inventory update
└─ Published as events to Message Queue

MANUAL (User-initiated):
├─ User says: "That's no longer true, check again"
├─ Agent detects contradiction in user feedback
└─ Triggers immediate context refresh
```

---

## CONTEXT ORCHESTRATION: Putting It All Together

### Reference Implementation (Pseudo-code)

```python
class ContextOrchestrator:
    """
    Manages context lifecycle for agents.
    Handles: fetching, compression, security, freshness, budgeting.
    """

    def __init__(self, agent_id, budget_kb=8, ttl_seconds=300):
        self.agent_id = agent_id
        self.budget_kb = budget_kb
        self.ttl_seconds = ttl_seconds
        self.cache = {}

    def assemble_context(self, user_query, user_id):
        """Assemble context for a user query."""

        # Step 1: Determine what context is needed
        required_sources = self.identify_sources(user_query)

        # Step 2: Fetch from each source (with MCP calls)
        context_items = {}
        for source in required_sources:
            data = self.fetch_with_security(
                source=source,
                user_id=user_id,
                agent_id=self.agent_id
            )
            context_items[source] = data

        # Step 3: Compress if exceeding budget
        compressed = self.compress(
            items=context_items,
            max_size_kb=self.budget_kb
        )

        # Step 4: Cache for later use
        self.cache[user_id] = {
            'context': compressed,
            'timestamp': now(),
            'ttl': self.ttl_seconds
        }

        return compressed

    def fetch_with_security(self, source, user_id, agent_id):
        """Fetch with access control and auditing."""

        # Check permissions
        if not self.can_access(agent_id, source, user_id):
            raise PermissionError(f"Agent {agent_id} cannot access {source}")

        # Fetch data
        data = self.call_mcp(source, user_id)

        # Apply row/column security
        data = self.apply_security_filters(data, user_id)

        # Log for audit
        self.audit_log(agent_id, source, user_id, len(data))

        return data

    def compress(self, items, max_size_kb):
        """Compress context to fit budget."""

        total_size = sum(len(v) for v in items.values())

        if total_size <= max_size_kb * 1024:
            return items  # Already under budget

        # Prioritize high-signal data
        prioritized = self.prioritize(items)

        # Summarize if needed
        if total_size > max_size_kb * 1024 * 1.5:
            prioritized = self.summarize(prioritized)

        return prioritized

    def is_context_fresh(self, user_id):
        """Check if cached context is still valid."""

        if user_id not in self.cache:
            return False

        cached = self.cache[user_id]
        age = now() - cached['timestamp']

        if age > cached['ttl']:
            return False  # Expired

        # Check for invalidation events
        if self.has_invalidation_event(user_id):
            return False

        return True
```

---

## Before Deploying Agents at Scale

Before deploying agents at scale, decide:

1. **Default Context Strategy**: Eager? Lazy? Hybrid?
2. **Context Budget**: How many KB per request? What's your cost tolerance?
3. **Data Sources**: Which systems will agents access? (DBs, APIs, knowledge bases)
4. **Freshness Requirements**: Which data must be real-time? Which can be cached?
5. **Security Model**: How to enforce row/column-level security?
6. **Compression Rules**: When to summarize? How aggressively?
7. **Monitoring**: How to detect context drift, bloat, or access violations?

---

## Related

- [Agentic AI Landing Zone: Platform Layer](29-agentic-ai-landing-zone-platform-layer.md)
- [Agentic AI Landing Zone: Business Layer](23-agentic-ai-landing-zone-business-layer.md)
- [Agentic AI Landing Zone: Visual Guide](32-agentic-ai-landing-zone-visual-guide.md)

---

**Document Status:** Current (July 2026)  
**Owner:** Platform Engineering  
**Audience:** Architects, engineers deploying production agents
