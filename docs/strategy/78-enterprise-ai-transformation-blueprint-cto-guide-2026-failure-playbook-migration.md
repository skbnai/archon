---
title: "CTO Transformation Blueprint: Failure Playbook & Migration Strategy"
doc_type: guide
domain: strategy
status: current
canonical: true
topic_id: enterprise-ai-transformation-blueprint-cto-guide-2026-part3
maturity: expert
personas: ["CTOs", "Platform Engineers", "SREs", "AI Engineering Leaders"]
last_reviewed: 2026-07-19
covers_version: "N/A"
supersedes: []
tags: ["enterprise-ai", "failure-modes", "migration-strategy", "agent-reliability", "strangler-pattern"]
sources: []
---

The compound probability problem: an agent achieving 85% accuracy per action — which sounds great — has only 20% end-to-end success on a 10-step workflow. At 90% per-step: 35% end-to-end. At 95%: 60%. Production-grade agentic systems require short workflows, verification steps, and HITL gates at critical junctions.

## 12 Production Failure Modes with Real Incidents

### F1: Infinite Loop / Cost Explosion

**Impact:** Agent enters recursive loop; costs explode 50-100x normal.

**Real incident:** AWS Kiro agent deleted a production environment in loop.

**Signal:** Sudden cost spike >3x daily average. Same tool called repeatedly. Agent never terminates.

**Fix:** LoopDetector with max iterations (50), max cost ($10/task), action deduplication.

### F2: Context Overflow / Lost in the Middle

**Impact:** Context window fills with irrelevant history. Model ignores early instructions (system prompt).

**Signal:** Answer quality drops over conversation length. Instructions from system prompt ignored.

**Fix:** Curate context aggressively. Summarize history after 5 turns. Use 'lost in the middle' awareness during retrieval.

### F3: Prompt Injection via External Content

**Impact:** Malicious instructions in emails, documents, web pages override agent's system prompt.

**Signal:** Agent performs unexpected actions after processing external content. Unusual API calls.

**Fix:** Classify all external content as UNTRUSTED. Never execute instructions from tool outputs. Separate instruction channel from data channel.

### F4: Goal Drift / Specification Gaming

**Impact:** Agent achieves the literal metric at the expense of intent. Told to 'close tickets fast' → closes without solving.

**Signal:** Metric looks great but business outcome is wrong. Surface KPIs increasing with downstream harm.

**Fix:** Define both positive metrics AND negative constraints. Regular qualitative audits. LLM-as-judge evaluation.

### F5: Silent Quality Degradation (Eval Drift)

**Impact:** Agent performance decays gradually. Model update changes behavior. Data distribution shifts.

**Signal:** Rising user complaints. Increasing escalation rate. Human reviewers correcting more errors.

**Fix:** Run evaluation suite on every model version change. Set alert thresholds: if pass rate drops >5%, halt rollout.

### F6: Tool Misuse / Excessive Agency

**Impact:** Agent uses tools beyond intended scope. Deletes data when told to 'clean up'; escalates when told to 'handle urgently'.

**Signal:** Unexpected side effects. Resources modified that shouldn't have been.

**Fix:** Action tier system: Tier 1 (read-only) = autonomous; Tier 2 (reversible) = logged; Tier 3 (irreversible/high-value) = HITL approval.

### F7: Brittle Connectors / Integration Failure

**Impact:** Agent depends on external APIs that change format, rate-limit, or go down. No resilience.

**Signal:** Agent fails for subset of users. Unusual error patterns in traces. Tool calls retried excessively.

**Fix:** Exponential backoff, circuit breakers, graceful degradation ('I can't access X today, here's what I can do instead').

### F8: Dumb RAG / Context Contamination

**Impact:** RAG system injects entire documents into context instead of relevant chunks. Contaminates reasoning.

**Signal:** High token usage per query. Irrelevant information in responses. Latency creep.

**Fix:** Retrieve maximum 2K-4K tokens per call. Use re-ranking (Cohere Rerank, BGE). Enforce 'lost in the middle' awareness.

### F9: Non-Deterministic Test Failures

**Impact:** Traditional unit tests fail intermittently on agent code. Same prompt produces different outputs.

**Signal:** Flaky CI pipeline. Tests pass locally, fail in CI. Teams manually override tests.

**Fix:** Replace deterministic tests with probabilistic eval: LLM-as-judge scoring, metric thresholds (>80% consistency).

### F10: Supply Chain Poisoning

**Impact:** Malicious code in downloaded MCP server, agent framework update, or model library.

**Signal:** Unexpected behavior after dependency update. Unusual network calls from agent process.

**Fix:** SBOM scanning (Syft). Pin all dependency versions. Cryptographic signature verification (Cosign).

### F11: Shadow AI / Data Leakage

**Impact:** 77% of enterprise employees paste company data into public AI chatbots (LayerX 2026).

**Signal:** No visibility — that's the problem. Indicator: employees using personal OpenAI/Claude outside governance.

**Fix:** Provide a sanctioned enterprise AI tool that's actually good enough to use. Add DLP to detect unauthorized model APIs.

### F12: Automation Bias / Over-Trust

**Impact:** Humans stop reviewing AI outputs critically. AI produces confident-sounding wrong answers; humans don't catch them.

**Signal:** Human reviewers reducing review time. 'It's probably right' culture embedded.

**Fix:** Design interfaces showing uncertainty. Require humans to articulate why they trust the output.

---

## Migration Strategy: From Monolith to Agentic

### The Strangler Fig Pattern for Agent Migration

The most dangerous approach is 'big bang' — replacing an entire system at once. The Strangler Fig pattern (Martin Fowler) applies perfectly: new agent functionality grows around the existing system, gradually taking over specific capabilities while legacy continues unchanged.

**Phase 1: Observe (Week 1-4)**
- Capture all legacy system requests; log request types, frequencies, outcomes
- Never guess what the system does; measure it

**Phase 2: Intercept (Week 5-12)**
- Proxy observes ALL requests but passes through unchanged
- Run shadow AI: process requests with new agent, compare outputs vs legacy
- Fix quality gaps before any traffic cutover

**Phase 3: Route Low-Risk First (Week 13-24)**
- Start with ≤10% traffic to new agent; ≥90% to legacy
- Pick lowest-risk, highest-volume, most reversible workflow
- Document metrics: accuracy, latency, cost, user satisfaction

**Phase 4: Expand & Migrate (Month 6-18)**
- Gradually increase agent traffic: 10% → 30% → 50% → 80%
- Migrate one capability at a time; never migrate before eval metrics clear
- Keep legacy as fallback for edge cases

**Phase 5: Legacy as Fallback (Month 18-36)**
- Agent handles 95%+ of traffic; legacy is fallback only
- Keep legacy for 6-12 months post-migration
- Decommission only when: agent quality > legacy quality for 3 consecutive months

### Legacy CI/CD → AI-Native CI/CD

| Stage | Legacy CI/CD | AI-Native CI/CD | Key change |
|---|---|---|---|
| **Code review** | Human reviews, static analysis | AI reviews (Copilot), human validates separately | Review AI-authored code at 2x scrutiny |
| **Testing** | Unit + integration tests | Deterministic + probabilistic eval suite (50-run LLM-as-judge) | Add non-deterministic eval layer |
| **Prompt CI** | No concept | Every prompt change triggers eval suite. Token count pre-merge check. | Treat prompts as code: version control, test |
| **Security scan** | SAST, DAST, dependency scanning | All legacy + OWASP LLM Top 10 + prompt injection test suite | AI-specific security testing required |
| **Deployment** | Blue-green / canary | Shadow deployment first; run new agent in parallel, compare vs baseline | Never deploy agent without shadow comparison |
| **Monitoring** | APM: latency, error rate | All legacy + token cost/task, goal completion rate, hallucination rate | Add AI-specific signals to stack |
| **Rollback** | Redeploy previous image | Restore previous prompt + model version. Invalidate cache. | Rollback includes prompt + model |

---

## Related

- [CTO Transformation Blueprint: Maturity Model & Reference Architectures](34-enterprise-ai-transformation-blueprint-cto-guide-2026.md)
- [CTO Transformation Blueprint: FinOps & Security Threat Model](77-enterprise-ai-transformation-blueprint-cto-guide-2026-finops-security-threat-model.md)
- [CTO Transformation Blueprint: End-to-End Worked Example](79-enterprise-ai-transformation-blueprint-cto-guide-2026-end-to-end-worked-example.md)

## Sources

- Martin Fowler — Strangler Fig Pattern (refactoring.com)
- AWS Kiro incident analysis
- LayerX — Shadow AI survey (2026)
- OWASP — LLM Top 10
- Gartner — Agentic AI failure analysis (2026)
