---
title: "Kill Switch Architecture for Multi-Agent AI Systems"
doc_type: guide
domain: architecture
status: current
canonical: true
topic_id: kill-switch-architecture
maturity: practitioner
personas: [architect, platform-engineer, sre, security]
last_reviewed: 2026-07-19
covers_version: "as of 2026-07-14"
supersedes: ["docs/enterprise-architecture/ai-architecture/kill-switch-architecture.md"]
tags: ["kill-switch", "reliability", "safety", "governance", "emergency-shutdown"]
sources: []
---

# Kill Switch Architecture for Multi-Agent AI Systems

**Audience:** Platform engineers, AI architects, SREs, CISO/security teams, and AI governance teams responsible for emergency response.

**Purpose:** Defines the complete kill switch architecture for enterprise multi-agent AI systems — covering global, scoped, and progressive shutdown mechanisms; safe mode; circuit isolation; feature flags; emergency policy override; and the governance model for who can activate each level.

**Scope:** Emergency shutdown and containment mechanisms. For the underlying circuit breaker reliability pattern, see [Agentic AI Reliability, Observability & Governance §4.3](43-agentic-ai-reliability-observability-governance.md). For the observability that triggers kill switch activation, see [Agent Reliability Engineering](42-agent-reliability-engineering.md). For governance of kill switch authority, see [Governance Propagation Chain](55-governance-propagation-chain.md).

---

## 1. Why Kill Switches Are a First-Class Architectural Concern

Kill switches are not an afterthought — they are a fundamental trust mechanism. Regulators, enterprise risk teams, and users must have confidence that **any agent can be stopped immediately**, regardless of what it is doing, without requiring a code deployment or infrastructure change.

The EU AI Act Article 9 (risk management) requires high-risk AI systems to include "appropriate human oversight measures" including the ability to halt the system. DORA (Digital Operational Resilience Act) requires financial firms to be able to terminate AI-driven processes that pose operational risk.

**Key design principle:** Kill switches must work when the system is under load, when the normal communication paths are degraded, and when the agent is in the middle of a long-running task.

---

## 2. Kill Switch Taxonomy

### 2.1 Scope Levels

| Level | Scope | Propagation Time Target | Who Can Activate |
|-------|-------|------------------------|-----------------|
| **Global kill** | All AI agents in the enterprise | &lt; 30 seconds | CISO, CTO, On-call incident commander |
| **Platform kill** | All agents on a specific platform/region | &lt; 30 seconds | Platform Team Lead, On-call SRE |
| **Tenant kill** | All agents for a specific tenant/customer | &lt; 60 seconds | Tenant Admin, Platform Team |
| **Agent kill** | A specific named agent | &lt; 30 seconds | Platform Team, On-call SRE |
| **Tool kill** | A specific tool/MCP server across all agents | &lt; 30 seconds | Platform Team, Tool Owner |
| **Workflow kill** | A specific workflow run | &lt; 30 seconds | Platform Team, Workflow Owner |
| **Model kill** | All calls to a specific model provider or model ID | &lt; 60 seconds | Platform Team Lead |
| **Memory disable** | Disable long-term memory read/write for specified agents | &lt; 60 seconds | Platform Team, AI Governance |
| **Retrieval disable** | Disable RAG retrieval for specified agents | &lt; 60 seconds | Platform Team, AI Governance |
| **Remote agent isolation** | Block all A2A calls to/from a specific remote agent | &lt; 30 seconds | Security Team, Platform Team |

### 2.2 Mechanism Types

| Mechanism | How It Works | Propagation Speed | Use Case |
|----------|-------------|------------------|---------|
| **Feature flag** (real-time) | Centralized flag service; agents poll every 5s or use long-poll | 5–30 seconds | Planned disablement; graduated rollout |
| **Policy override** | Emergency deny rule pushed to all OPA/Cedar instances | &lt; 30 seconds | Security incident; unauthorized behavior |
| **Gateway block** | Gateway rejects all requests for the target scope | &lt; 5 seconds | Immediate containment; easiest to activate |
| **Circuit breaker open** | Circuit breaker forced-open programmatically | &lt; 5 seconds | Provider failure; quality failure |
| **Capability suspension** | Agent registry marks agent as suspended; all calls refused | &lt; 30 seconds | Agent misbehavior; compliance hold |
| **Credential revocation** | Agent's workload certificate / token revoked | &lt; 60 seconds (OCSP/CRL propagation) | Compromised agent identity |
| **Process termination** | Kill the agent process directly | Immediate | Last resort; may leave state inconsistent |

---

## 3. Kill Switch Architecture

### 3.1 Control Plane

Kill Switch Control Plane Orchestration

```mermaid
graph TD
    OP["OPERATOR"]
    API["KILL SWITCH API<br/>authenticated, audited"]
    ORCH["KILL SWITCH ORCHESTRATOR<br/>1. Authenticate operator<br/>2. Verify authority for scope<br/>3. Log activation + reason<br/>4. Determine propagation path<br/>5. Dispatch mechanisms<br/>6. Confirm SLA<br/>7. Alert stakeholders"]
    
    GW["Gateway<br/>Block"]
    OPA["OPA<br/>Rule"]
    FF["Feature<br/>Flag"]
    AR["Agent<br/>Registry"]
    CB["Circuit<br/>Breaker"]
    CR["Credential<br/>Revocation"]
    
    OP -->|activate| API
    API -->|scope, level, reason| ORCH
    ORCH -->|Dispatch| GW
    ORCH -->|Dispatch| OPA
    ORCH -->|Dispatch| FF
    ORCH -->|Dispatch| AR
    ORCH -->|Dispatch| CB
    ORCH -->|Dispatch| CR
```

Operator activates kill switch through authenticated API. Orchestrator authenticates operator, verifies authority, logs activation, dispatches to six propagation mechanisms, confirms within SLA targets, and alerts all stakeholders.

### 3.2 Feature Flag Kill Switch

Feature flags provide the most controllable kill switch — graduated, reversible, audited:

Kill Switch Feature Flag Hierarchy

```mermaid
graph TB
    STORE["Kill Switch Flag Store<br/>LaunchDarkly / AWS AppConfig<br/>Azure App Config / Unleash"]
    GLOBAL["Global:<br/>ai.agents.enabled = false"]
    PLATFORM["Platform:<br/>ai.platform.us-east-1.enabled = false"]
    AGENT["Agent:<br/>ai.agent.billing-agent.enabled = false"]
    TOOL["Tool:<br/>ai.tool.funds-transfer.enabled = false"]
    MODEL["Model:<br/>ai.model.claude-opus.enabled = false"]
    TENANT["Tenant:<br/>ai.tenant.acme-corp.enabled = false"]
    
    STORE --> GLOBAL
    STORE --> PLATFORM
    STORE --> AGENT
    STORE --> TOOL
    STORE --> MODEL
    STORE --> TENANT
```

**Agent implementation (required at every agent):**

```python
async def execute_agent_task(task: AgentTask) -> AgentResult:
    # Kill switch check BEFORE any work begins
    if not await feature_flags.is_enabled(f"ai.agent.{agent_id}.enabled"):
        raise AgentSuspendedError(
            code="AGENT_SUSPENDED",
            message="Agent temporarily disabled by platform governance"
        )

    # Kill switch check DURING long-running tasks (at every step boundary)
    for step in plan.steps:
        if not await feature_flags.is_enabled(f"ai.agent.{agent_id}.enabled"):
            raise AgentSuspendedMidTaskError(
                completed_steps=completed_steps,
                checkpoint=current_checkpoint
            )
        await execute_step(step)
```

**Flag polling requirement:** Agents must poll kill switch flags at intervals ≤ 5 seconds (real-time). Long-running agents must check the kill switch flag at every step boundary, not just at invocation start.

### 3.3 Gateway-Level Kill Switch

The gateway is the fastest and most reliable kill switch for inbound traffic:

**Gateway kill-switch activation and effect.**

```mermaid
graph TD
    A["Kill Switch Activation<br/>API call to Gateway Admin API"]
    B["Gateway Kill Switch Rule<br/>match: agent_id == billing-agent<br/>action: REJECT with HTTP 503<br/>reason: Agent suspended by governance - ref: INC-8821<br/>duration: until explicitly lifted"]
    C["New requests to billing-agent → rejected immediately"]
    D["In-flight requests → completed (drain) or killed (hard stop)"]
    E["User experience → 503 with governance message"]
    A --> B
    B --> C
    B --> D
    B --> E
```

**Drain vs. hard stop choice:**
- **Drain** (allow in-flight requests to complete): use for non-security incidents where graceful completion is preferred
- **Hard stop** (kill in-flight immediately): use for security incidents (prompt injection, data exfiltration in progress)

### 3.4 Policy Override Kill Switch

For scenarios where the agent bypassed the gateway (internal calls, scheduled tasks):

Emergency Policy Rule (OPA / Cedar):

```rego
# OPA: emergency deny for specific agent
package emergency.overrides

deny[msg] {
  input.agent_id == "billing-agent"
  msg := "Agent billing-agent suspended - INC-8821"
}

# This rule takes precedence over all permit rules
# Must be propagated to all OPA instances in < 30 seconds
```

**Propagation mechanism:** OPA bundle update pushed to all OPA sidecar instances via bundle server. Each sidecar polls every 5–10 seconds (configurable). Target: &lt; 30 seconds global propagation.

### 3.5 Capability Suspension in Agent Registry

Suspending an agent in the central registry prevents new dispatches:

```json
{
  "agent_id": "billing-agent",
  "status": "suspended",
  "suspension_reason": "INC-8821: anomalous billing lookups detected",
  "suspended_at": "2026-07-14T15:30:00Z",
  "suspended_by": "platform-oncall@acme.com",
  "review_scheduled": "2026-07-14T17:00:00Z"
}
```

All components that dispatch work to agents (Planner, Supervisor, A2A gateway) must check agent registry status before dispatching. A suspended agent receives no new tasks.

---

## 4. Safe Mode

Safe mode is a degraded operating state that maintains basic functionality while disabling AI-powered features. It is activated when AI systems must be suspended but the underlying service must remain available.

| Normal Mode | Safe Mode |
|---|---|
| Agent answers questions | Fallback to knowledge base search |
| Agent routes to specialist | Fixed routing rules (no ML) |
| Agent drafts emails | Email drafting disabled |
| Agent processes claims | Claims queued for human review |
| Agent monitors for anomalies | Rule-based alerting only |
| Agent interprets contracts | Contract review routed to legal team |

### Safe Mode Activation Playbook

```
Trigger: Global kill switch activated for AI agents

1. Gateway switches to safe-mode ruleset:
   - All AI-agent endpoints → fallback handler
   - Fallback handler serves static/rule-based responses

2. UI displays safe-mode banner:
   - "AI features temporarily unavailable. Using assisted mode."

3. Work queue accumulates:
   - Unprocessed AI tasks enter a durable queue
   - Queue monitored for SLA breaches
   - Human review team notified of queue depth

4. Communications:
   - Users notified via status page
   - Account teams notified if enterprise customers affected

5. AI reactivation:
   - Requires: root cause identified + resolved
   - Requires: sign-off from: Platform Lead + AI Governance + (CISO if security incident)
   - Reactivation is gradual (canary first, then full rollout)
```

---

## 5. Progressive Shutdown

Progressive shutdown reduces blast radius by stopping in a controlled sequence:

```
Step 1: Feature flag → disable new task acceptance
        (agent finishes current tasks; accepts no new ones)
        Wait: 30 seconds

Step 2: Gateway kill → reject new requests
        (belt-and-suspenders; catches requests that bypassed flag check)
        Wait: 30 seconds for drain

Step 3: Cancel in-flight tasks
        (send cancellation signal to all active task IDs)
        Wait: 60 seconds for graceful cancellation

Step 4: Force-terminate remaining tasks
        (checkpoint state; kill processes)
        Wait: 10 seconds

Step 5: Suspend agent registry entry
        (prevent any future dispatch)
        Immediate

Step 6: Revoke credentials (if security incident)
        (revoke SPIFFE SVID / OAuth tokens)
        OCSP propagation: < 60 seconds
```

For **security incidents** (compromised agent, active data exfiltration), skip Steps 1–4 and go directly to Steps 5–6 + gateway hard block.

---

## 6. Remote Agent Isolation (A2A)

When a remote agent (connected via A2A) is suspected of malicious behavior or has been compromised:

| Local Action | Effect |
|---|---|
| 1. Block outbound A2A to remote agent (gateway rule: drop A2A calls to remote-agent-id) | No new tasks sent to remote agent |
| 2. Invalidate cached remote agent card (agent registry: mark as BLOCKED) | Local agents no longer discover remote agent |
| 3. Revoke trust for remote agent's certificate/JWT issuer | All in-flight A2A responses rejected (SPIFFE trust bundle updated) |
| 4. Notify remote org (A2A protocol: send agent-status notification) | Remote org can investigate their side |
| 5. Audit: log all recent interactions with the remote agent | Compliance + forensics |

---

## 7. Circuit Isolation

Circuit isolation prevents a failing component from cascading failures to other components:

Circuit Breaker State Transition: Normal to Isolated

```mermaid
graph TD
    NORMAL["NORMAL STATE<br/>Circuit: CLOSED"]
    AA1["Agent A"]
    AB1["Agent B"]
    AC1["Agent C"]
    TX1["Tool X<br/>healthy"]
    
    FAILING["TOOL X FAILING<br/>error rate > 50%"]
    
    OPEN["CIRCUIT ISOLATION<br/>Circuit: OPEN"]
    AA2["Agent A"]
    AB2["Agent B"]
    AC2["Agent C"]
    FB1["Fallback<br/>Response"]
    TX2["Tool X<br/>isolated"]
    
    SUBGRAPH1["<b>Normal Operation</b>"]
    NORMAL --> AA1
    NORMAL --> AB1
    NORMAL --> AC1
    AA1 --> TX1
    AB1 --> TX1
    AC1 --> TX1
    
    SUBGRAPH2["<b>Isolation Activated</b>"]
    FAILING -.-> OPEN
    OPEN --> AA2
    OPEN --> AB2
    OPEN --> AC2
    AA2 --> FB1
    AB2 --> FB1
    AC2 --> FB1
    TX2 --> |"Recovery:<br/>after 60s<br/>half-open probe"|TX1
```

During normal operation, agents call Tool X directly (circuit closed). When Tool X fails (>50% error rate), circuit opens: agents receive fallback responses instead, Tool X isolation prevents cascading failure, and after 60 seconds a half-open probe tests recovery.

### Isolation Scope Matrix

| Failing Component | What Gets Isolated | Fallback |
|------------------|-------------------|---------|
| Model provider (Claude) | All calls to that provider | Fallback to alternate provider |
| Vector store | All RAG retrieval | Direct context (no retrieval) |
| MCP server | That server's tools | Disable tools; agent works without them |
| Policy engine | Policy enforcement | Default-deny until engine recovers |
| Memory service | Long-term memory access | Session memory only |
| Remote agent | That A2A connection | Local agent handles task (degraded quality) |

---

## 8. Emergency Policy Override

During a security incident, the normal policy evaluation may need to be bypassed for an emergency override:

### 8.1 Emergency Deny Override

Supersedes all existing permit policies for the duration of the incident:

```python
# Emergency override structure
{
    "type": "emergency_deny",
    "scope": {
        "agent_ids": ["billing-agent", "funds-agent"],
        "action_classes": ["financial:write", "funds:transfer"]
    },
    "reason": "INC-8821: Suspected unauthorized access via prompt injection",
    "activated_by": "security-oncall@acme.com",
    "activated_at": "2026-07-14T15:30:00Z",
    "valid_until": "2026-07-14T17:30:00Z",  # Auto-expires; requires renewal
    "requires_review_by": "CISO"
}
```

**Auto-expiry:** Emergency overrides must auto-expire. Indefinite emergency overrides become permanent policy by default, which is a governance failure. Default TTL: 2 hours; renewal requires explicit re-authorization.

### 8.2 Human Approval Override

For actions that were previously automated, require human approval for the duration of the incident:

```
Under emergency conditions:
  All agent actions class "HIGH" → route to HITL queue
  All agent actions class "CRITICAL" → require CISO sign-off
  Automated financial actions → suspended; queue for treasury team review
```

---

## 9. Governance Model

### 9.1 Authority Matrix

| Kill Switch Level | Minimum Authority | CISO Must Approve? | Time Limit |
|---|---|---|---|
| Global kill | CISO or CTO | Yes (or is activating) | 2 hours; review required |
| Platform kill | Platform Team Lead | No (notify within 15 min) | 4 hours |
| Tenant kill | Tenant Admin or Platform Team | No (notify within 30 min) | 8 hours |
| Agent kill | On-call SRE | No (notify within 30 min) | 24 hours |
| Tool kill | Tool Owner or On-call SRE | No | 24 hours |
| Model kill | Platform Team Lead | No (notify within 1 hour) | 8 hours |
| Memory disable | Platform Team or AI Governance | No | 24 hours |
| Remote agent isolation | Security Team or On-call SRE | If cross-org security incident: yes | 24 hours |

### 9.2 Audit Requirements

Every kill switch activation must produce a mandatory audit record:

```json
{
  "event_type": "kill_switch_activated",
  "event_id": "ks-2026-0714-001",
  "timestamp": "2026-07-14T15:30:00.123Z",
  "scope": "agent",
  "target": "billing-agent",
  "level": "agent_kill",
  "activated_by": {
    "identity": "platform-oncall@acme.com",
    "authentication_method": "OIDC + MFA",
    "ip_address": "10.0.1.45"
  },
  "reason": "Anomalous billing lookup rate: 10000 lookups/min vs normal 50/min",
  "incident_id": "INC-8821",
  "propagation_confirmed_at": "2026-07-14T15:30:28.000Z",
  "propagation_time_seconds": 28,
  "sla_met": true,
  "notifications_sent": ["platform-team@acme.com", "ai-governance@acme.com"],
  "auto_expires_at": "2026-07-14T17:30:00Z"
}
```

### 9.3 Reactivation Protocol

Reactivation requires explicit process, not just removing the kill switch:

```
1. Root cause documented (incident ticket)
2. Mitigation implemented (code fix, policy update, or containment measure)
3. Testing completed (eval suite passing; chaos test of the specific failure scenario)
4. Sign-off obtained:
   - For security incident: CISO + Platform Lead
   - For quality incident: AI Governance + Platform Lead
   - For operational incident: Platform Lead + On-call SRE
5. Canary reactivation: 5% of traffic → monitor for 30 min
6. Full reactivation if canary passes
7. Post-mortem completed within 24 hours of reactivation
```

---

## 10. Kill Switch Testing

Kill switches that are never tested will fail when needed. Test on a quarterly schedule:

| Test | What It Validates | How Often |
|------|------------------|-----------|
| **Feature flag propagation** | Flag change propagates to all agents in &lt; 30s | Monthly |
| **Gateway block** | New requests blocked within 5s; in-flight drained within 60s | Monthly |
| **Policy override** | Emergency deny propagates to all OPA instances in &lt; 30s | Quarterly |
| **Agent registry suspension** | Suspended agent receives no new dispatches | Monthly |
| **Safe mode switchover** | Safe mode activates within 60s of activation | Quarterly |
| **Progressive shutdown** | Full progressive shutdown completes in &lt; 5 minutes | Quarterly |
| **Remote agent isolation** | A2A calls to isolated remote agent fail in &lt; 30s | Quarterly |
| **Reactivation process** | Reactivation flow can be completed in &lt; 2 hours from approval | Quarterly |

Test results are logged and reviewed by AI Governance. Tests are not optional — untested kill switches are not kill switches.

---

## 11. Kill Switch Runbook

### 11.1 Security Incident (Compromised Agent)

```
TRIGGER: Agent exhibiting anomalous behavior (prompt injection, data exfiltration pattern)

T+0:00  On-call SRE detects anomaly via AI SOC alert
T+0:02  Confirm: is this a genuine compromise? (check causal trace)
T+0:05  Activate agent kill switch (gateway hard block + policy override)
T+0:06  Confirm kill switch propagation (< 30s SLA)
T+0:07  Notify CISO + Platform Lead
T+0:10  Preserve forensic state (snapshot agent state, recent trace data)
T+0:15  Identify blast radius (what data was accessed? what actions were taken?)
T+0:30  Notify affected tenants/users if data accessed
T+1:00  Incident Review begins (root cause)
T+4:00  Mitigation implemented
T+4:30  CISO reviews reactivation request
T+5:00  Canary reactivation (5% traffic)
T+5:30  Full reactivation (if canary clean)
T+24h   Post-mortem published
```

### 11.2 Quality Degradation (Agent Producing Wrong Outputs)

```
TRIGGER: Judge pass rate drops below 70% (automated alert)

T+0:00  Alert fires on AI SOC dashboard
T+0:05  On-call SRE investigates (is it agent? model? prompt?)
T+0:10  Activate agent kill switch (feature flag first; gradual)
T+0:15  Notify Platform Lead + AI Governance
T+0:30  Root cause investigation begins
T+1:00  Mitigation: fix identified (prompt rollback? model pin? code fix?)
T+2:00  Fix deployed to canary
T+2:30  Canary eval suite passes
T+3:00  Canary reactivation (5% → 20% → 100% over 30 min)
T+4:00  Platform Lead signs off on full reactivation
T+24h   Post-mortem published
```

---

## Further Reading

- [Agentic AI Reliability, Observability & Governance §4.3](43-agentic-ai-reliability-observability-governance.md) — circuit breaker and kill switch patterns
- [Agent Reliability Engineering §5 & §6](42-agent-reliability-engineering.md) — chaos testing kill switches; incident runbooks
- [Governance Propagation Chain](55-governance-propagation-chain.md) — emergency policy override architecture
- [End-to-End Traceability Guide](46-end-to-end-traceability-guide.md) — forensic investigation after kill switch activation
- [Drift Detection Guide](45-drift-detection-guide.md) — detecting quality degradation that triggers kill switches
- [AIDR: AI Detection and Response](pathname:///archon/trust/ai-security-governance/aidr-ai-detection-response-complete-guide) — SOC response when kill switch is triggered
- [AI SOC](pathname:///archon/trust/ai-security-governance/ai-soc) — AI security operations
- [AI TRiSM Complete Guide](pathname:///archon/trust/ai-security-governance/ai-trism-complete-guide) — trust, risk, and security management
