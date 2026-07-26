---
title: "Agentic AI Landing Zone: Multi-Agent Reference Architectures"
date_created: 2026-07-09
last_reviewed: 2026-07-10
status: current
source_type: native-md
doc_type: reference-architecture
domain: architecture
topic_id: agentic-ai-landing-zone-multiagent
supersedes: ["docs/ai-foundations/agentic_ai_landing_zone_multiagent.md"]
tags: ["ai-foundations"]
covers_version: "as of 2026-07-10"
---

# Agentic AI Landing Zone: Multi-Agent Reference Architectures

*Single agents solve narrow problems. Multi-agent systems solve complex, real-world business processes.*

---

## Why Multi-Agent?

**Business Reality (2026):**

- 73% of production agents use specialist agents (not monolithic)
- Complex workflows require collaboration (order processing, compliance review, customer service escalation)
- Different specialists (expert in returns, expert in billing, expert in escalation)
- Autonomous coordination reduces human bottlenecks

**Architecture Decision:**
> One agent does one thing well. Multiple agents divide labor.

---

## MULTI-AGENT TOPOLOGY SELECTION

### When to Use Each Pattern

```
START
  - Simple sequential flow?
    - Use SEQUENTIAL Pattern
      - One coordinator, many workers?
    - Use SUPERVISOR Pattern
      - Hierarchical breakdown (CEO → VPs → Teams)?
    - Use HIERARCHICAL Pattern
      - Agents can run in parallel on unrelated tasks?
    - Use MESH Pattern
      - Many agents, same capability, load balanced?
    - Use POOL Pattern
      - Emergent behavior, swarm intelligence needed?
     - Use SWARM Pattern
```

---

## PATTERN 1: SEQUENTIAL

**Description:** Agents execute one after another, each passing output to next.

```
User Request
    ↓
Agent A (Understands intent)
    ↓ output: structured intent
Agent B (Gathers data)
    ↓ output: customer profile + policies
Agent C (Makes decision)
    ↓ output: decision + reasoning
Agent D (Communicates)
    ↓
Response to User
```

### Sequential Workflow Example: Customer Refund Request

```
1. Intake Agent
   Input: "I want to return my order"
   Task: Understand request, extract order ID
   Output: {order_id: 98765, customer_id: 12345, request_type: "return"}

   ↓ passes to

2. Validation Agent
   Input: {order_id, customer_id, request_type}
   Task: Verify order exists, check return window, verify customer
   Output: {valid: true, return_window: "30 days", days_elapsed: 8, eligible: true}

   ↓ passes to

3. Policy Agent
   Input: {order_id, eligible: true}
   Task: Determine return shipping method, refund amount, timeline
   Output: {refund_amount: $99.99, shipping_label: "...", timeline: "5-7 days"}

   ↓ passes to

4. Communication Agent
   Input: {refund_amount, shipping_label, timeline}
   Task: Compose response to customer
   Output: "Your return is approved. Here's your shipping label: ..."

   ↓
Response to Customer
```

### Sequential Implementation (Pseudo-code)

```python
async def sequential_workflow(user_request):
    # Step 1: Intake
    intake_result = await intake_agent.run(user_request)

    # Step 2: Validation
    validation_result = await validation_agent.run(intake_result)

    if not validation_result.valid:
        return validation_result.error_message  # Early exit

    # Step 3: Policy
    policy_result = await policy_agent.run(validation_result)

    # Step 4: Communication
    response = await communication_agent.run(policy_result)

    return response
```

### When to Use Sequential

- ✅ Clear linear process (step 1 → 2 → 3)
- ✅ Each step must complete before next
- ✅ Output of one agent feeds into next
- ✅ Low concurrency needed
- ❌ Slow if many steps (latency multiplies)

### Pros & Cons

| Pros | Cons |
| ------ | ------ |
| Simple to understand | Slow (serial execution) |
| Easy to debug | Must wait for each step |
| Clear handoff points | No parallelization |
| Deterministic flow | Hard to scale |

---

## PATTERN 2: SUPERVISOR (Orchestrator Pattern)

**Description:** One "supervisor" agent coordinates multiple specialist agents, deciding which to call.

```mermaid
graph LR
    User["User<br/>Request"]
    Supervisor["Supervisor<br/>Agent"]
    AgentA["Specialist A<br/>Returns"]
    AgentB["Specialist B<br/>Billing"]
    AgentC["Specialist C<br/>Technical"]
    
    User --> Supervisor
    Supervisor --> AgentA
    Supervisor --> AgentB
    Supervisor --> AgentC
    
    style Supervisor fill:#fff4e6
    style AgentA fill:#f0f0f0
    style AgentB fill:#f0f0f0
    style AgentC fill:#f0f0f0
```

Supervisor: "This is a billing question → call Billing Agent"

### Supervisor Example: Customer Service Hub

```
User: "I was overcharged on my order, and my tracking isn't updating"

Supervisor Analysis:
- Identified issues: 2 (overcharge + tracking)
- Required agents:
  - Billing Agent (for overcharge)
  - Logistics Agent (for tracking)
- Decision: Call both in parallel

Parallel Execution:
- Billing Agent
  - Checks order: $99.99 charged, should be $79.99
  - Finds duplicate charge
  - Output: "Issue found: $20 duplicate. Refund processing."
  - Logistics Agent
   - Checks tracking system
   - Finds package stuck in facility
   - Output: "Stuck in Denver facility. Investigating."

Supervisor Synthesis:
- Combines: "Your refund is being processed ($20).
             Your package is stuck but moving today."
- Escalates: "I'm escalating the logistics issue to our ops team."

Response to User:
- Clear, addressed both problems, escalation initiated
```

### Supervisor Implementation

```python
class SupervisorAgent:
    def __init__(self):
        self.specialists = {
            "billing": BillingAgent(),
            "returns": ReturnsAgent(),
            "logistics": LogisticsAgent(),
            "technical": TechnicalAgent(),
        }

    async def route_and_execute(self, user_request, context):
        # Step 1: Analyze request
        analysis = await self.analyze(user_request, context)
        # Output: {issues: ["billing", "logistics"], priority: ["billing"]}

        # Step 2: Route to specialists
        tasks = []
        for issue in analysis.issues:
            specialist = self.specialists[issue]
            task = specialist.handle(user_request, context)
            tasks.append(task)

        # Step 3: Parallel execution
        results = await asyncio.gather(*tasks)

        # Step 4: Synthesize results
        response = await self.synthesize(results, analysis)

        return response
```

### When to Use Supervisor

- ✅ Multiple independent specialists
- ✅ Supervisor can parallelize work
- ✅ Dynamic routing (different specialists for different requests)
- ✅ Clear separation of concerns
- ❌ Supervisor becomes bottleneck if too many specialists
- ❌ Harder to handle cross-domain issues

### Pros & Cons

| Pros | Cons |
| ------ | ------ |
| Parallel specialist execution | Supervisor can become complex |
| Clear specialization | Harder for specialists to coordinate |
| Good for diverse problems | May miss cross-domain patterns |
| Scales with specialists | Requires well-defined interfaces |

---

## PATTERN 3: HIERARCHICAL

**Description:** Agents organized in hierarchy. High-level agents delegate to lower-level agents.

```
CEO Agent
    - VP Sales Agent
      - Account Manager Agent
      - Upsell Agent
          - VP Operations Agent
      - Order Processing Agent
      - Fulfillment Agent
          - VP Support Agent
        - Tier 1 Support Agent
        - Tier 2 Support Agent
```

### Hierarchical Example: Order Processing

```
CEO Agent
  Role: Route customer request to appropriate VP

  User: "I placed an order 3 days ago. It hasn't shipped yet."

  - Delegates to: VP Operations Agent
      Role: Handle operational issues

      - Analyzes: Issue is about order status + shipping
      - Delegates to: Tier 1 Support Agent
        Role: Handle standard inquiries
                - Checks order status: Shows "processing"
        - Checks current date: 3 days is normal for processing
        - Standard response: "Your order is being processed..."
                  - If complaint or edge case → Escalate to Tier 2
              - (If Tier 1 escalates) Delegates to: Tier 2 Support Agent
          Role: Handle complex/escalated issues

          - Deep investigation: Order flagged for manual review (fraud check)
          - Explanation: "Security review in progress, ships tomorrow"
          - Compensation: "Free express shipping as apology"
          - Resolution: Issue resolved
```

### Hierarchical Implementation

```python
class HierarchicalAgent:
    def __init__(self, role, level, delegates_to=None):
        self.role = role
        self.level = level  # CEO=0, VP=1, Manager=2, IC=3
        self.delegates_to = delegates_to or []

    async def handle(self, request, context):
        # Level 1: Try to handle at this level
        if self.can_handle(request):
            return await self.execute(request, context)

        # Level 2: Find appropriate delegate
        for delegate in self.delegates_to:
            if delegate.can_handle(request):
                return await delegate.handle(request, context)

        # Level 3: Escalate up the chain
        return await self.escalate(request, context)

    def can_handle(self, request):
        # Does this agent's role match request domain?
        return request.domain in self.responsibilities

    async def escalate(self, request, context):
        # Pass to higher level (parent)
        return await self.parent.handle(request, context)
```

### When to Use Hierarchical

- ✅ Clear organizational structure
- ✅ Different expertise at different levels
- ✅ Natural escalation paths
- ✅ Support tiers (Tier 1 → 2 → 3)
- ❌ Latency from multiple hops
- ❌ Requires clear responsibility boundaries

### Pros & Cons

| Pros | Cons |
| ------ | ------ |
| Maps to org structure | Slow escalation |
| Clear authority levels | Potential bottlenecks at top |
| Supports tier system | Rigid structure |
| Familiar to humans | Hard to cross-level communication |

---

## PATTERN 4: MESH (Peer-to-Peer)

**Description:** Agents are peers. Each can call any other agent directly.

```
Agent A ←→ Agent B
  ↓ ↖       ↓ ↖
  ↓   ↖   ↙   ↖
  ↓     ↙       ↖
Agent C ←→ Agent D

Each agent can communicate with any other agent.
```

### Mesh Example: Supply Chain Optimization

```
Demand Planner Agent: "We need 1000 units by Friday"
    - Calls Supplier Agent: "Can you deliver 500 by Friday?"
      - Supplier: "Yes, $50/unit"
          - Calls Inventory Agent: "How many in stock?"
      - Inventory: "200 units"
          - Calls Finance Agent: "Is $50K budget available?"
        - Finance: "Yes"

Supply Planner Agent: "Need 500 units from Supplier + 200 from Inventory"
    - Calls Supplier Agent: "Confirm order for 500"
    - Calls Inventory Agent: "Reserve 200 units"
    - Calls Logistics Agent: "Arrange delivery for 700 units"

Logistics Agent: "Confirmed delivery Friday"
    - Calls Customer Agent: "Notify customer: arriving Friday"

Each agent maintains state:
- Demand: 1000 needed
- Inventory: 200 reserved
- Suppliers: 500 ordered
- Logistics: 700 units in transit
- Customer: Notified of Friday arrival
```

### Mesh Implementation

```python
class MeshAgent:
    def __init__(self, agent_id):
        self.agent_id = agent_id
        self.peers = {}  # Dict of peer agents
        self.state = {}  # Local state

    async def call_peer(self, peer_id, action, params):
        # Direct peer-to-peer call
        peer = self.peers[peer_id]
        result = await peer.handle(action, params)
        return result

    async def handle(self, request):
        # This agent's work
        result = await self.execute(request)

        # Potentially call other peers
        if result.needs_inventory_check:
            inventory = await self.call_peer(
                "inventory_agent",
                "check_stock",
                {"product": result.product_id}
            )

        return result

    def register_peer(self, agent_id, agent):
        # Discover and register peers
        self.peers[agent_id] = agent
```

### When to Use Mesh

- ✅ All agents have similar authority
- ✅ Complex interdependencies
- ✅ Dynamic collaboration patterns
- ✅ No clear hierarchy
- ❌ Can become chaotic (difficult to debug)
- ❌ Hard to enforce coordination
- ❌ Risk of infinite loops

### Pros & Cons

| Pros | Cons |
| ------ | ------ |
| Flexible | Chaotic |
| No bottlenecks | Hard to trace execution |
| Direct communication | Potential infinite loops |
| Emergent behavior | Difficult debugging |

---

## PATTERN 5: POOL (Replicated Workers)

**Description:** Multiple identical agents, load-balanced for parallel execution.

```mermaid
graph LR
    User["User<br/>Requests"]
    LB["Load Balancer"]
    AgentA["Agent A<br/>Invoice Processor"]
    AgentB["Agent B<br/>Invoice Processor"]
    AgentC["Agent C<br/>Invoice Processor"]
    
    User --> LB
    LB --> AgentA
    LB --> AgentB
    LB --> AgentC
    
    style LB fill:#fff4e6
    style AgentA fill:#e6f3ff
    style AgentB fill:#e6f3ff
    style AgentC fill:#e6f3ff
```

User requests distributed across pool of identical agents.

### Pool Example: Invoice Processing

```
Incoming invoices: 10,000/day

Without Pool:
- Single Invoice Agent
   - Processes 1 invoice/second
   - Total time: 10,000 seconds ≈ 2.8 hours
   - Latency: Invoice sits 90+ minutes before processing

With Pool (3 agents):
- Agent A: processes invoices 1-3,333
- Agent B: processes invoices 3,334-6,666
- Agent C: processes invoices 6,667-10,000

  - Total time: 10,000 / 3 ≈ 3,333 seconds ≈ 55 minutes (3x faster)
  - Latency: Invoice processed within ~2 minutes

With Auto-Scaling Pool:
- Monitor queue depth
- If queue > 1,000: spin up more agents
- If queue < 100: scale down to save cost
- Result: Consistent latency, cost-optimized
```

### Pool Implementation

```python
class AgentPool:
    def __init__(self, agent_class, pool_size=3):
        self.agents = [agent_class(f"agent_{i}") for i in range(pool_size)]
        self.queue = asyncio.Queue()

    async def add_task(self, task):
        # Queue incoming task
        await self.queue.put(task)

    async def run(self):
        # Each agent processes from shared queue
        tasks = [
            self.worker(agent)
            for agent in self.agents
        ]
        await asyncio.gather(*tasks)

    async def worker(self, agent):
        while True:
            task = await self.queue.get()
            try:
                result = await agent.execute(task)
                await self.publish_result(result)
            finally:
                self.queue.task_done()

    async def auto_scale(self):
        # Monitor queue depth, adjust pool size
        while True:
            queue_depth = self.queue.qsize()
            if queue_depth > 1000:
                # Spin up new agent
                self.add_agent()
            elif queue_depth < 100 and len(self.agents) > 3:
                # Scale down
                self.remove_agent()
            await asyncio.sleep(60)
```

### When to Use Pool

- ✅ Many identical tasks
- ✅ Throughput-focused (not latency)
- ✅ Stateless agents
- ✅ Easy horizontal scaling
- ❌ All agents must be identical
- ❌ Not suitable for complex coordination

### Pros & Cons

| Pros | Cons |
| ------ | ------ |
| Simple scaling | All agents identical |
| High throughput | No specialization |
| Cost-effective | Stateless only |
| Load balanced | Not for complex workflows |

---

## PATTERN 6: SWARM (Emergent Collective)

**Description:** Many simple agents with local rules, exhibiting emergent collective behavior.

```
Individual Agent Rules:
- Follow the leader (when leader is moving)
- Stay close to neighbors (within 10 units)
- Avoid collisions
- Move toward objective

Emergent Behavior (no central controller):
- Coordinated movement (appears choreographed)
- Adapts to obstacles (flows around)
- Self-organizing (no top-down command)
- Resilient (if one agent fails, swarm continues)
```

### Swarm Example: Market Research Agents

```
Mission: Gather competitive intelligence across 100 markets

Swarm of 50 Research Agents:
- Local Rules:
  - "Search your assigned market for price changes"
  - "If you find interesting pattern, share with neighbors"
  - "If neighbor found something valuable, investigate too"
  - "Report daily to collective"
  - Emergent Behavior:
  - Agents concentrate on high-signal markets (no central assignment)
  - Interesting patterns replicate (viral behavior)
  - Redundancy handles failures (if agent fails, others continue)
  - Collective intelligence > sum of parts
  - Results:
   - Comprehensive coverage (all 100 markets touched)
   - Deep dives on anomalies (swarm converges on changes)
   - Adaptability (as market shifts, swarm redistributes)
   - Resilience (90% effectiveness even with 20% failure rate)
```

### When to Use Swarm

- ✅ Exploration problems (find patterns in large space)
- ✅ Emergent behavior desired
- ✅ Robustness required
- ✅ Decentralized better than centralized
- ❌ Hard to predict exact behavior
- ❌ Debugging difficult
- ❌ Overkill for simple coordination

### Pros & Cons

| Pros | Cons |
| ------ | ------ |
| Emergence | Unpredictable |
| Resilient | Hard to debug |
| Adapts dynamically | Not for deterministic workflows |
| Handles complexity | Over-engineered for simple tasks |

---

## CHOOSING YOUR PATTERN: Decision Framework

```
Is the workflow linear?
- YES → SEQUENTIAL
- NO
        - Is there one coordinator?
     - YES → SUPERVISOR
     - NO
            - Is there a hierarchy (org structure)?
       - YES → HIERARCHICAL
       - NO
                - Are all agents identical?
         - YES → POOL
         - NO
                    - Need emergent behavior?
           - YES → SWARM
           - NO → MESH
```

---

## HYBRID ARCHITECTURES: Combining Patterns

**Real-world systems rarely use one pattern alone.**

### Example: Customer Service Platform

```
Layer 1: SUPERVISOR (top)
- Supervisor routes to specialists:
  - Returns Specialist (HIERARCHICAL: Tier 1 → Tier 2)
  - Billing Specialist (SEQUENTIAL: Validate → Check Policy → Refund)
  - Technical Specialist (MESH: Coordinates with Ops agents)
  Layer 2: POOL (parallelization)
- If request matches pattern (e.g., "simple return"):
  - Route to pool of simple return processors (identical, load-balanced)
  Layer 3: SWARM (exploration)
- For complex, novel requests:
   - Swarm of research agents explores solution space
```

**Result:** Combines simplicity (supervisor) with speed (pool), handles complexity (hierarchical), explores novel cases (swarm).

---

## TODO: Multi-Agent Strategy for Your Organization

Before deploying multi-agent systems:

1. **Identify Workflows**: Which business processes require multiple agents?
2. **Select Pattern**: For each workflow, choose best pattern
3. **Test Locally**: Build & test pattern in dev environment
4. **Measure Performance**: Cost, latency, quality vs. single-agent baseline
5. **Scale Gradually**: Deploy to staging, then production with canary

---

**Related Documents:**

- Agent Platform Layer: Lifecycle & Registry
- Enterprise Agent Reference Architectures
- Agentic AI Security

---

**Document Status:** DRAFT (July 2026)
**Owner:** Platform Architecture
**Audience:** Architects designing agent systems

## Related

- [Multi-Agent Topology Patterns](59-multi-agent-topology-patterns.md) — the topology patterns this reference architecture implements.
- [Agentic AI Landing Zone Architecture](22-agentic-ai-landing-zone-architecture.md) — the base landing zone this multi-agent design extends.

