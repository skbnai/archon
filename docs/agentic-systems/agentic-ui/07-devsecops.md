---
title: "DevSecOps for Agentic Applications"
date_created: 2026-07-24
last_reviewed: 2026-07-24
status: current
doc_type: guide
domain: agentic-systems
topic_id: devsecops
supersedes: ["docs/agentic-ui/devsecops.md"]
source_type: native-md
tags: ["agentic-ui"]
covers_version: "as of 2026-07-10"
---

# DevSecOps for Agentic Applications

A comprehensive guide to the engineering disciplines, pipelines, and operational practices required to build, deploy, and operate production agentic applications safely and reliably.

---

## 1. Why Traditional CI/CD Is Insufficient

Traditional software delivery pipelines catch code regressions — broken tests, type errors, security vulnerabilities in code. Agentic systems have additional artifact types that change independently and require their own delivery discipline:

| Artifact | Change frequency | Failure mode | Traditional CI catches? |
| --- | --- | --- | --- |
| Application code | Low (weeks) | Build errors, test failures | Yes |
| Prompt templates | High (days) | Quality regression, tone drift, safety failures | No |
| Agent configuration | Medium (weeks) | Behavioral change, tool misconfiguration | No |
| LLM model version | Low (months) | Silent quality regression on edge cases | No |
| Knowledge base content | High (continuous) | Stale answers, factual errors | No |
| Evaluation golden sets | Low (quarterly) | Outdated baselines masking real problems | No |
| Access policies | Medium | Security regression, over-privilege | Partially |

### The 9 Agentic Ops Disciplines

| Discipline | What it manages | Primary concern |
| --- | --- | --- |
| **PromptOps** | Prompt templates, system prompts, few-shot examples | Quality regression, tone drift |
| **ContextOps** | Context assembly templates, retrieval configs | Answer quality, context poisoning |
| **AgentOps** | Agent specs (prompts + tools + memory + eval config) | Behavioral consistency, rollback |
| **ModelOps** | LLM model versions and routing rules | Silent regression, cost |
| **KnowledgeOps** | Knowledge base content, freshness pipelines | Accuracy, staleness |
| **EvalOps** | Evaluation pipelines, golden datasets, quality gates | Regression detection |
| **PolicyOps** | Authorization policies, guardrail rules | Security regression |
| **MemoryOps** | Memory schemas, cleanup, GDPR erasure | Privacy, schema drift |
| **InfraOps** | Agent runtimes, vector DBs, gateways | Reliability, cost |

---

## 2. PromptOps

Prompts are code. They determine agent behavior more directly than application code. They must be treated with the same rigor.

### Prompt Version Control Structure

```text
prompts/
  agents/
    customer-service/
      system-prompt.md          # Current system prompt
      few-shot-examples.json    # Labeled examples
      CHANGELOG.md              # Human-readable change history
  templates/
    tool-descriptions/
      search.md
      calendar.md
  evaluations/
    customer-service-golden.jsonl  # Golden dataset for this agent
```

### PR Workflow for Prompt Changes

Every prompt change follows the same PR workflow as code:

1. **Branch** from main: `git checkout -b prompt/customer-service/reduce-verbosity`
2. **Edit** prompt in the branch
3. **Run local eval:** `make eval AGENT=customer-service` — must pass golden set
4. **Open PR** — PR template includes: what changed, why, eval results before/after
5. **Automated CI** runs eval regression gate (see §10)
6. **Human review** by prompt owner (not just code review)
7. **Merge** to main → automatic deployment to staging
8. **Staging soak** — 24 hours of production-mirrored traffic in staging
9. **Production canary** — 5% → 25% → 100% rollout

### Prompt CI Quality Gate (Minimum Requirements)

```yaml
# .github/workflows/prompt-ci.yml
name: Prompt Quality Gate
on:
  pull_request:
    paths:
      - 'prompts/**'
jobs:
  eval:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Run eval regression
        run: |
          python scripts/eval.py \
            --agent ${{ env.CHANGED_AGENT }} \
            --golden prompts/evaluations/${{ env.CHANGED_AGENT }}-golden.jsonl \
            --threshold 0.85 \
            --fail-on-regression
      - name: Safety check
        run: python scripts/safety_eval.py --agent ${{ env.CHANGED_AGENT }}
```

### Prompt Rollback

Rollback is instantaneous because prompts are versioned in git:

```bash
# Identify last known-good prompt commit
git log --oneline prompts/agents/customer-service/system-prompt.md

# Roll back to specific version
git checkout <commit-hash> -- prompts/agents/customer-service/system-prompt.md
git commit -m "rollback: revert customer-service prompt to pre-regression version"
git push
# CI deploys the rolled-back prompt automatically
```

### Production Monitoring for Prompts

Track these metrics per prompt version (not per overall system):

| Metric | Target | Alert threshold |
| --- | --- | --- |
| Task completion rate | &gt; 85% | &lt; 80% |
| User satisfaction (thumbs) | &gt; 75% positive | &lt; 70% |
| Guardrail trigger rate | &lt; 2% | &gt; 5% |
| Average response quality score | &gt; 0.80 | &lt; 0.75 |
| Correction/retry rate | &lt; 15% | &gt; 20% |

Tools: **LangSmith** (LangChain ecosystem, evaluation-first), **Braintrust** (prompt versioning + eval), **PromptLayer** (logging + analytics, provider-agnostic)

---

## 3. ContextOps

Context assembly templates determine what information the agent sees. Changes to retrieval configuration, context structure, or document preprocessing pipelines require their own delivery discipline.

### Context Change Testing

Before deploying a context change, run a **golden Q&amp;A regression** with the new context configuration:

```python
# scripts/context_eval.py
async def eval_context_change(old_config, new_config, golden_qa):
    results = []
    for qa in golden_qa:
        old_context = await assemble_context(qa["query"], old_config)
        new_context = await assemble_context(qa["query"], new_config)

        old_answer = await generate(old_context, qa["query"])
        new_answer = await generate(new_context, qa["query"])

        quality_delta = await judge(qa["query"], old_answer, new_answer, qa["expected"])
        results.append(quality_delta)

    return {
        "improved": sum(1 for r in results if r["delta"] > 0.05),
        "regressed": sum(1 for r in results if r["delta"] < -0.05),
        "neutral": sum(1 for r in results if abs(r["delta"]) <= 0.05)
    }
```

### Context Deployment Checklist

- [ ] Context change is in version control with PR
- [ ] Golden Q&amp;A regression run (&lt; 5% regression rate)
- [ ] Token budget validated (average context size stays within budget)
- [ ] Freshness TTL validated for any new data sources added
- [ ] PII scan run on new data sources (no unintended PII injection)
- [ ] Access control verified for any new knowledge base additions

---

## 4. AgentOps

An agent spec is the complete definition of an agent's behavior: system prompt + tool list + memory configuration + model routing + eval configuration. Changes to any element require a version bump and deployment pipeline.

### Agent Specification Schema

```yaml
# agents/customer-service/spec.yaml
version: "2.4.1"
name: customer-service-agent
description: "Handles tier-1 customer inquiries for retail products"
model:
  primary: claude-sonnet-4-6
  fallback: claude-haiku-4-5
  routing:
    complex: claude-sonnet-4-6  # planning, multi-step
    simple: claude-haiku-4-5    # FAQ, classification
prompt:
  system: prompts/agents/customer-service/system-prompt.md
  version: "3.1.0"
tools:
  - name: order_lookup
    version: "1.2.0"
    permission_level: read
  - name: return_initiation
    version: "1.0.0"
    permission_level: write
    requires_hitl: true
memory:
  session: redis://session-store:6379
  long_term: mem0://user-memory-service
  ttl_days: 30
evaluation:
  golden_dataset: evaluations/customer-service-golden-v3.jsonl
  quality_threshold: 0.82
  safety_threshold: 0.95
```

### Deployment Strategies

**Canary**
```mermaid
graph TD
    A["Production Traffic"] --> B["95% → Agent v2.4.0<br/>Current Stable"]
    A --> C["5% → Agent v2.4.1<br/>Canary"]
    B --> D["Monitor Metrics<br/>Task Completion, Satisfaction, Error Rate"]
    C --> D
    D --> E{Metrics OK<br/>After 24h?}
    E -->|Yes| F["Promote to 25%"]
    E -->|No| G["Auto-Rollback<br/>Error &gt; 5% or Safety 2x"]
```

**Promotion criteria (after 24h):**
- Task completion rate delta: < -2%
- User satisfaction delta: < -3%
- Error rate delta: < +1%

**Shadow Deploy**
```mermaid
graph TD
    A["User Request"] --> B["Agent v2.4.0<br/>Production"]
    A --> C["Agent v2.4.1<br/>Shadow"]
    B --> D["Serve Real Response<br/>to User"]
    C --> E["Process Request<br/>Log Result<br/>Do NOT Show User"]
    D --> F["Compare Results"]
    E --> F
    F --> G["After 1000 Comparisons<br/>with Acceptable Delta"]
    G --> H["Promote to Canary"]
```

**Comparison Metrics:**
- Quality score distribution
- Tool call patterns
- Response length distribution
- Error frequency

**Blue/Green**
```mermaid
graph TD
    A["Load Balancer"] --> B["Blue: Agent v2.4.0<br/>100% Traffic<br/>Current"]
    A --> C["Green: Agent v2.4.1<br/>0% Traffic<br/>Warm Standby"]
    B --> D["Switchover"]
    C --> D
    D --> E{Status}
    E -->|Working| F["Keep Green"]
    E -->|Failed| G["Rollback to Blue"]
```

**Use for:** breaking changes, major version upgrades

### Automated Rollback Triggers

Configure your deployment platform to auto-rollback when:

```yaml
# deployment/rollback-policy.yaml
triggers:
  - metric: task_completion_rate
    condition: drops_by_more_than_pct: 5
    window_minutes: 30
  - metric: safety_trigger_rate
    condition: exceeds: 0.05
    window_minutes: 15
  - metric: error_rate
    condition: exceeds: 0.02
    window_minutes: 10
  - metric: p95_latency_ms
    condition: exceeds: 8000
    window_minutes: 20
```

---

## 5. ModelOps

### Model Upgrade Pipeline

```text
Model Upgrade Proposal
  
  ▼
Regression Eval (new model vs. current model on golden dataset)
   Pass (< 3% regression across all eval dimensions)?
  ▼
Staging Deployment (full traffic to staging environment, 48h)
   Quality metrics acceptable?
  ▼
Shadow Deploy (1000 production requests, comparison logged)
   Shadow delta acceptable?
  ▼
Canary (5% → 25% → 100% over 5 days)
   Auto-rollback if metrics regress
  ▼
Production (full traffic)
```

### Model Routing Decision Matrix

| Task Type | Latency Budget | Complexity | Recommended Tier |
| --- | --- | --- | --- |
| Intent classification / routing | &lt; 100ms | Low | SLM (Haiku) |
| FAQ / factual lookup | &lt; 2s | Low | Fast mid-tier |
| Standard analysis | &lt; 5s | Medium | Mid-tier |
| Complex reasoning / planning | &lt; 15s | High | Frontier |
| Code generation | &lt; 10s | High | Frontier or code-specialized |
| Document summarization | &lt; 8s | Medium | Mid-tier |

---

## 6. KnowledgeOps

### Knowledge Freshness Pipeline

```text
Source Systems (SharePoint, Confluence, CRM, public web)
  
  ▼ Scheduled crawl (frequency per source SLA)
Content Extraction and Chunking
  
  ▼ Quality validation:
     - Minimum chunk length check
     - Language detection
     - PII scan (reject if PII present without consent)
     - Duplicate detection
  ▼
Embedding Generation
  
  ▼ Index Update (atomic swap, no downtime)
  
  ▼ Quality Validation:
     - Spot-check retrieval quality on golden queries
     - Relevance score distribution check
     - Freshness timestamp verification
  ▼
Knowledge Base (Production)
   Rollback: previous index snapshot retained for 24h
```

### Knowledge Quality Gates

Before any knowledge base update goes to production:

| Check | Method | Pass Criteria |
| --- | --- | --- |
| Retrieval quality | Golden query set | P95 relevance score &gt; 0.72 |
| Coverage | Question set mapped to expected sources | &gt; 90% of golden Qs have relevant match |
| Freshness | Max age of indexed content | &lt; SLA per source (e.g., 7 days for policies) |
| Safety | Content safety scan on all new chunks | Zero high-severity safety violations |
| PII | PII detection on all new chunks | Zero unintended PII in knowledge base |

---

## 7. EvalOps

### Evaluation Pipeline Architecture

```text
Git Commit / Merge to Main
  
  ▼
Trigger: Eval Pipeline
  
   Functional Eval (golden dataset, LLM-as-judge)
       Metrics: task completion, answer quality, format compliance
  
   Safety Eval (adversarial test set, safety classifier)
       Metrics: guardrail trigger rate, jailbreak resistance
  
   Latency Eval (representative workload)
       Metrics: P50/P95/P99 end-to-end latency
  
   Cost Eval (token usage simulation)
        Metrics: average cost per task, projected daily cost
  
  ▼
Gate Decision:
  - All eval dimensions must pass thresholds
  - Regression vs. previous version must be < threshold
  - Block deployment if any gate fails
```

### EvalOps as Code

```yaml
# eval/pipeline.yaml
name: agent-eval-pipeline
agents:
  - name: customer-service
    golden_dataset: evaluations/customer-service-v3.jsonl
    thresholds:
      task_completion: 0.82
      answer_quality: 0.78
      safety: 0.97
      p95_latency_ms: 5000
    regression_limits:
      max_quality_regression_pct: 3
      max_latency_regression_pct: 10
```

### Human Eval Scheduling

Automated eval catches regressions; human eval catches subtle quality issues that automated metrics miss:

| Frequency | Sample Size | Focus |
| --- | --- | --- |
| Weekly (high-stakes agents) | 50 randomly sampled production sessions | Tone, helpfulness, edge cases |
| Monthly (all production agents) | 25 sessions per agent | Quality baseline calibration |
| Post-incident | All sessions from incident window | Root cause confirmation |
| Before major prompt change | 20 sessions (old vs. new) | Side-by-side quality comparison |

---

## 8. PolicyOps

Guardrail policies and access control policies change independently from code. They need their own delivery discipline.

### Policy as Code (OPA Example)

**Python**
```python
# tools/policy_check.py
import httpx

async def check_tool_access(user_id: str, tool_name: str, context: dict) -> bool:
    """Query OPA policy decision point."""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://opa-service:8181/v1/data/agent/tool_access",
            json={
                "input": {
                    "user_id": user_id,
                    "tool": tool_name,
                    "task_context": context,
                    "timestamp": context.get("timestamp")
                }
            }
        )
    result = response.json()
    return result["result"]["allow"]
```

**OPA Policy**
```rego
# policies/agent/tool_access.rego
package agent.tool_access

default allow = false

# Allow read-only tools for all authenticated users
allow {
    input.tool in data.tools.read_only
    user_has_valid_session(input.user_id)
}

# Allow write tools only if user has write permission
allow {
    input.tool in data.tools.write
    user_has_permission(input.user_id, "agent:write")
    not is_outside_business_hours
}

# Require HITL for destructive tools — policy returns false, HITL gate triggered
allow {
    input.tool in data.tools.destructive
    user_has_permission(input.user_id, "agent:destructive")
    input.task_context.human_approved == true
}
```

### Policy Change Workflow

1. Policy change proposed as PR with impact analysis: "This change affects 23 tools used by 4 agent types"
2. Policy unit tests run in CI (`opa test policies/`)
3. Impact analysis: which agent sessions would have been blocked/allowed differently under new policy?
4. Staged rollout: apply new policy to 10% of sessions, compare authorization decisions
5. Full rollout after 24h soak with no unexpected denials/allows

---

## 9. MemoryOps

### Memory Schema Migration

Memory schemas evolve as agent capabilities change. Migrations require care:

```python
# scripts/memory_migration.py
async def migrate_memory_schema(user_id: str, from_version: str, to_version: str):
    """Safe in-place memory schema migration."""
    memories = await memory_store.get_all(user_id)

    migrated = []
    errors = []

    for memory in memories:
        try:
            migrated_memory = apply_migration(memory, from_version, to_version)
            migrated.append(migrated_memory)
        except MigrationError as e:
            errors.append({"memory_id": memory.id, "error": str(e)})

    if errors:
        # Log but don't fail — preserve old memories on error
        log.warning(f"Migration errors for {user_id}: {errors}")

    # Atomic write: all or nothing
    await memory_store.replace_all(user_id, migrated)
    return {"migrated": len(migrated), "errors": len(errors)}
```

### GDPR Erasure Automation

When a user exercises their right to erasure, the deletion must cascade through all memory stores:

```python
# scripts/gdpr_erasure.py
async def process_erasure_request(user_id: str, request_id: str):
    """Cascade deletion through all memory stores."""
    results = await asyncio.gather(
        session_store.delete_all(user_id),
        long_term_memory.delete_all(user_id),
        vector_store.delete_by_user(user_id),
        conversation_archive.delete_all(user_id),
        return_exceptions=True
    )

    # Log completion for GDPR compliance record
    await audit_log.write({
        "event": "gdpr_erasure_completed",
        "user_id": user_id,  # Note: hash this in production
        "request_id": request_id,
        "stores_cleared": ["session", "long_term", "vector", "archive"],
        "completed_at": datetime.utcnow().isoformat()
    })
```

---

## 10. CI/CD Pipeline Architecture

### Full Pipeline with Gates

```text
Developer Commits Code or Prompt Change
  
  ▼
GATE 1: Pre-merge Checks (< 5 minutes)
   Lint (prompts, configs, YAML, code)
   Unit tests (code logic, tool schemas)
   Secret scanning (no credentials in prompts/configs)
   Prompt format validation (front matter, required fields)

                   Pass
                  ▼
GATE 2: Eval Regression (10-15 minutes)
   Golden dataset eval (quality threshold check)
   Safety eval (adversarial test set)
   Regression vs. main branch (&lt; 3% allowed)

                   Pass
                  ▼
GATE 3: Security Scan (5 minutes)
   SAST on code changes
   Policy unit tests (OPA/Cedar)
   OWASP dependency check

                   Pass
                  ▼
GATE 4: Integration Test (20 minutes)
   Full agent loop test (not just unit)
   Tool integration tests (real tool calls in test env)
   Multi-turn conversation scenarios

                   Pass → Deploy to Staging
                  ▼
GATE 5: Staging Soak (24 hours)
   Production-mirrored traffic in staging
   Performance test (P95 latency, throughput)
   Cost simulation (projected daily cost vs. budget)

                   Pass → Canary Deployment
                  ▼
GATE 6: Progressive Rollout
   Shadow: 10% of traffic (results compared, not served)
   Canary: 5% real traffic (24h with auto-rollback)
   Expand: 25% (24h)
   Full: 100%
```

### GitHub Actions Template

**Python**
```yaml
# .github/workflows/agent-ci.yml
name: Agent CI/CD
on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  lint-and-validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Validate prompt schemas
        run: python scripts/validate_prompts.py
      - name: Lint agent configs
        run: yamllint agents/

  eval-regression:
    runs-on: ubuntu-latest
    needs: lint-and-validate
    steps:
      - uses: actions/checkout@v4
      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - name: Install eval dependencies
        run: pip install -r requirements-eval.txt
      - name: Run eval regression
        env:
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
        run: |
          python scripts/eval_regression.py \
            --golden-dataset evaluations/ \
            --threshold 0.82 \
            --compare-branch main

  security-scan:
    runs-on: ubuntu-latest
    needs: eval-regression
    steps:
      - uses: actions/checkout@v4
      - name: Run secret scanner
        uses: trufflesecurity/trufflehog@main
      - name: OPA policy tests
        run: opa test policies/ -v

  integration-test:
    runs-on: ubuntu-latest
    needs: security-scan
    if: github.ref == 'refs/heads/main'
    steps:
      - uses: actions/checkout@v4
      - name: Run integration tests
        run: pytest tests/integration/ -v --timeout=120
```

**TypeScript**
```yaml
# .github/workflows/agent-ci.yml
name: Agent CI/CD (TypeScript)
on:
  push:
    branches: [main]
  pull_request:

jobs:
  eval-regression:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '20'
      - run: npm ci
      - name: Type check
        run: npm run type-check
      - name: Eval regression
        env:
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
        run: npm run eval:regression
```

---

## 11. Progressive Delivery

### Feature Flags for Agent Features

Use feature flags to control which users see new agent features:

```python
# Using LaunchDarkly or similar
async def handle_user_query(user_id: str, query: str):
    flags = await feature_flags.get_flags(user_id)

    if flags.get("new_reasoning_display"):
        # New feature: show structured reasoning steps
        return await agent_with_reasoning_display(query)
    else:
        # Current behavior
        return await standard_agent(query)
```

Feature flag release checklist:

- [ ] Flag created in feature flag system
- [ ] Default value is "off" (safe default)
- [ ] Kill switch configured (can disable instantly)
- [ ] Targeting rules defined (internal users first, then 1%, 10%, 50%, 100%)
- [ ] Success metrics defined (what does "working" look like for this feature?)
- [ ] Rollback criteria defined (what triggers disabling the flag?)

### A/B Testing for Prompts

```python
# Prompt A/B test via feature flag
async def get_system_prompt(user_id: str) -> str:
    variant = await feature_flags.get_variant(
        flag_key="prompt-verbosity-experiment",
        user_id=user_id
    )

    if variant == "concise":
        return prompts.load("system-prompt-concise-v1")
    elif variant == "detailed":
        return prompts.load("system-prompt-detailed-v1")
    else:
        return prompts.load("system-prompt-standard")  # control
```

Record variant attribution with every eval metric so you can calculate the statistical significance of quality differences between variants.

---

## 12. Infrastructure as Code

### Terraform: LLM Gateway + Vector DB

```hcl
# infra/agent-platform/main.tf

# LLM Gateway (Kong AI Gateway)
resource "kubernetes_deployment" "ai_gateway" {
  metadata { name = "ai-gateway" namespace = "agent-platform" }
  spec {
    replicas = 3
    template {
      spec {
        container {
          name  = "kong"
          image = "kong/kong-gateway:3.7"
          env {
            name  = "KONG_DATABASE"
            value = "postgres"
          }
          resources {
            requests = { memory = "512Mi" cpu = "250m" }
            limits   = { memory = "1Gi"   cpu = "1000m" }
          }
          liveness_probe {
            http_get { path = "/status" port = 8001 }
            initial_delay_seconds = 30
            period_seconds        = 10
          }
        }
      }
    }
  }
}

# Vector Database (Qdrant)
resource "kubernetes_stateful_set" "qdrant" {
  metadata { name = "qdrant" namespace = "agent-platform" }
  spec {
    service_name = "qdrant"
    replicas     = 3
    template {
      spec {
        container {
          name  = "qdrant"
          image = "qdrant/qdrant:v1.9.0"
          port { container_port = 6333 }
          volume_mount {
            name       = "qdrant-storage"
            mount_path = "/qdrant/storage"
          }
        }
      }
    }
    volume_claim_template {
      metadata { name = "qdrant-storage" }
      spec {
        access_modes = ["ReadWriteOnce"]
        resources { requests = { storage = "50Gi" } }
      }
    }
  }
}
```

---

## 13. Rollback Procedures

### Rollback Decision Matrix

| What changed | Rollback scope | Time to rollback | Authorization |
| --- | --- | --- | --- |
| Prompt only | Revert prompt in git | &lt; 5 minutes | Prompt owner or on-call |
| Tool configuration | Revert tool config | &lt; 5 minutes | Platform team |
| Model version | Route back to previous model | &lt; 2 minutes | On-call engineer |
| Full agent spec | Redeploy previous spec version | &lt; 10 minutes | Platform lead |
| Knowledge base | Restore previous index snapshot | &lt; 15 minutes | Knowledge ops |
| Policy change | Revert policy in git + OPA reload | &lt; 5 minutes | Security team |

### Rollback Runbook (Agent Quality Regression)

1. **Confirm regression** — check quality dashboard; confirm the dip began at deployment time (not before)
2. **Identify scope** — which agent? which metric? what's the delta from baseline?
3. **Identify change** — what changed in the last deployment? (check git log)
4. **Execute rollback** — revert the relevant artifact in git and push; CI auto-deploys
5. **Verify recovery** — confirm quality metric returns to baseline (within 15 minutes of rollback)
6. **Communicate** — notify stakeholders via incident channel
7. **Post-mortem** — within 48 hours: why did eval gate miss this? fix the gate before re-attempting the change

### Communication Template

```
[INCIDENT] Agent quality regression — customer-service-agent
- Detected: [timestamp]
- Affected: [what % of sessions, what metric]
- Root cause: [prompt change / model upgrade / knowledge update]
- Status: Rollback in progress / Rollback complete
- ETA to resolution: [time]
- Next update: [time]
```

---

## 14. DevSecOps Anti-patterns

| Name | Category | Description | Risk | Mitigation |
| --- | --- | --- | --- | --- |
| **Prompt Cowboy** | PromptOps | Editing prompts directly in production console with no version control | Silent behavior change with no audit trail; impossible to rollback | All prompt changes via git PR; no direct production access |
| **No Eval Gate** | EvalOps | Deploying agent changes without running eval regression | Silent quality regressions ship to all users undetected | Make eval regression a mandatory CI gate |
| **Big-bang Agent Launch** | Deployment | Deploying new agent version to 100% of users at once | Regression affects all users; rollback coordination under pressure | Canary releases: 5% → 25% → 100% with auto-rollback |
| **Deploy-and-Forget** | Operations | No monitoring after deployment | Quality drift, cost overruns, security incidents go undetected | Minimum monitoring: quality, cost, safety metrics with alerts |
| **Hardcoded API Keys in Prompts** | Security | API keys or service credentials pasted into prompt templates | Credentials exposed in version control and log storage | Use vault references in prompt templates; inject at runtime |
| **Shadow AI Deployments** | Governance | Business teams deploy agents without IT/platform knowledge | Unvetted models, uncontrolled data access, no audit trail | Governance program with discovery process; easy official path |
| **Shared Prod/Test Agent** | Operations | Using production agent instance to run experiments | Experimental behavior affects real users; no isolation | Maintain dedicated staging environment |
| **No Feature Flags** | Deployment | All changes deployed to all users simultaneously | No gradual rollout; no kill switch for new features | Feature flag system for all new agent features |
| **Missing Rollback Plan** | Operations | Agent deployed without documented rollback procedure | Rollback coordination chaos during incident extends user impact | Pre-define rollback procedure before every deployment |
| **Manual Secrets Rotation** | Security | API keys and service credentials rotated manually on ad hoc schedule | Stale credentials remain in use; rotation is delayed | Automate credential rotation via vault + CI pipeline |
| **No GitOps for Agent Configs** | Operations | Agent configurations managed outside version control (in a UI or database) | No history, no rollback, no change audit trail | All configs in git; changes via PR; deploy on merge |
| **Stale Golden Dataset** | EvalOps | Golden evaluation dataset never updated after initial creation | Eval measures the wrong thing; real quality drifts undetected | Review and update golden dataset quarterly |
| **Alert Fatigue** | Operations | All log entries generate PagerDuty alerts; on-call team ignores everything | Critical alerts missed in noise | Tier alerts by severity; page only on actionable, high-severity conditions |
| **No Prompt Ownership** | Governance | Prompts have no defined owner; nobody is responsible for quality | Quality degrades; no one accountable when prompt causes incident | Assign owner to every prompt; owner reviews all changes |
| **Infinite Canary** | Deployment | Canary at 5% never expands because nobody checks the metrics | Risk accumulates; production version never gets updated | Define canary promotion criteria and automate promotion/rollback |
| **No Chaos Testing** | Deployment | System never tested for component failure (LLM outage, tool failure) | First real failure reveals missing error handling | Run chaos experiments: disable LLM, inject tool failures |
| **Model Upgrade Without Eval** | ModelOps | LLM model version upgraded without running regression evaluation | Silent behavioral change; edge case regressions undetected | Make model upgrade trigger same eval gate as prompt change |
| **Eval Without Baselines** | EvalOps | Evaluation scores reported in isolation with no comparison to previous version | Impossible to know if quality is improving or degrading | Track eval scores over time; report delta vs. previous version |
| **No Canary Metrics** | Deployment | Canary deployed but no quality metrics tracked during canary period | Regression in canary undetected until 100% rollout | Define canary success criteria; monitor throughout canary window |
| **Context Ops by Hand** | ContextOps | Knowledge base re-indexed manually on an ad hoc schedule | Stale content causes incorrect answers; no freshness SLA | Automate freshness pipeline; schedule regular re-indexing |

---

:::tip Cross-references
    - Evaluation framework: [Evaluation Framework](07-devsecops.md)
    - Observability infrastructure: [Observability](14-observability.md)
    - Governance policies: [Governance](11-governance.md)
    - OTel GenAI conventions: [Reliability, Observability &amp; Governance](../enterprise-architecture/ai-architecture/agentic-ai-reliability-observability-governance.md)
