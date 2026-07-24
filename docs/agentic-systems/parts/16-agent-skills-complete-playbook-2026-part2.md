---
title: "Agent Skills & Skill Registries — Complete Playbook 2026 (Part 2)"
doc_type: guide
domain: agentic-systems
status: current
topic_id: agent-skills-complete-playbook-2026-part2
date_created: 2026-07-24
last_reviewed: 2026-07-24
supersedes: []
tags:
  - agentic-ai
  - agent-skills
  - playbook
  - coding-tools
---

# Agent Skills & Skill Registries — Complete Playbook 2026 (Part 2)

**This is Part 2 of 2. [Return to Part 1 →](pathname:///archon/agentic-systems/core/16-agent-skills-complete-playbook-2026) for Fundamentals, Best Practices, Anti-Patterns, Registries, Microsoft APM, and Skill Lifecycle.**

---

## 07 EVALUATION FRAMEWORKS & BENCHMARKS

### Core Evaluation Dimensions

**Task Success Rate (TSR)** — Did the skill complete the assigned task end-to-end? Measured with deterministic verifiers (pass/fail tests) or LLM-as-judge for open-ended outputs. Primary metric for all skills. Target: ≥85% for curated skills.

**Routing Precision & Recall** — Was the correct skill selected? Precision = correct selections / total selections. Recall = correct selections / tasks where skill was appropriate. Target: ≥85% precision with negative_examples in YAML.

**Token Cost Efficiency** — Tokens consumed per successful task completion. At Uber, AI-related costs rose 6× since 2024 — making token cost optimization its own engineering discipline. Track QoQ and set per-task budgets.

**Long-Horizon Persistence** — Can the agent maintain goal focus across many steps without drifting or looping? Terminal-Bench caps at 100 episodes. Persistence failure before that cap is the failure mode measured.

**Plan Quality** — Does the agent decompose the task into logical steps? Does it adapt when obstacles appear? Measured via step-trace analysis and plan deviation metrics in tools like Langfuse and Langsmith.

**Output Quality (Human)** — For creative or judgment-intensive skills, human panels rate output on correctness, completeness, tone, and usefulness (1–5 scale). Run on a 10% sample. Blind review prevents evaluator bias.

### Benchmark Reference

| Benchmark | Measures | Method | Key Result 2026 |
|---|---|---|---|
| SkillsBench | Skill efficacy: vanilla vs self-generated vs curated | 84 tasks × 11 domains × 3 conditions; deterministic verifiers + trajectory logs | Curated skills ~81% TSR vs ~48% baseline — the definitive skills benchmark |
| SWE-bench Verified | Software engineering: resolving real GitHub issues | Pass@1 on test suites from popular OSS repos | Claude 3.5 Sonnet ~49%; best agents now approaching 60% |
| Terminal-Bench | Raw agentic capability on terminal/shell tasks | Hard-subset: 44 tasks; 100-episode cap; 24hr timeout; 3-repeat average | Primary harness comparison benchmark for code agents in 2026 |
| AgentBench | Multi-environment LLM agent performance | 8 distinct interactive environments; collaborative and solo tasks | Multi-dimensional; identifies cross-domain capability gaps |
| MLE-Bench | ML engineering end-to-end autonomy | Offline Kaggle competitions; graded against human-level submissions | Best setup (o1-preview + AIDE) achieved bronze medal in 16.9% of competitions |
| BrowseComp | Web-based information retrieval and navigation | Multi-turn browser interaction; structured query validation | Tests persistence and tool-use in open-web environments |

### SkillsBench Task Success Rate by Condition

No Skills (Baseline): **48%**
Self-Generated Skills: **67%**
Expert-Curated Skills: **81%**

### Evaluation Stack

| Tool | Category | Primary Use |
|---|---|---|
| Langfuse | Tracing & Observability | Full trajectory logging; skill invocation traces; latency per step |
| Langsmith | Evaluation | LLM-as-judge pipelines; dataset management; regression testing |
| Braintrust | LLM Evals | Experiment tracking; scoring functions; human annotation workflow |
| Promptfoo | Prompt Regression | Automated prompt comparison; CI integration; redteam testing |
| Harbor Framework | Containerized Envs | Isolated deterministic execution environments for benchmark runs |
| Helicone | Cost Tracking | Token cost per skill; cost-per-outcome dashboards; budget alerting |
| SkillAttack | Red Teaming | Automated adversarial testing of skill security via attack path refinement |

---

## 08 A/B TESTING AGENT SKILLS

### A/B Testing Agent Skills

Skill A/B testing is more complex than web A/B testing because agent tasks are long-horizon, non-deterministic, and hard to assign a single numeric outcome. Best-practice frameworks treat it as controlled experiment + shadow deployment + human evaluation panels in combination.

```yaml
# Skill A/B Test Configuration
experiment_id: pipeline-audit-v2-vs-v1
champion: data-pipeline-audit@1.4.2 # 70% traffic
challenger: data-pipeline-audit@2.0.0 # 30% traffic
success_metrics:
  primary: task_success_rate
  secondary: [tokens_per_task, latency_p95, human_rating]
  guardrails: [error_rate_lt_5pct, zero_security_violations]
min_sample_size: 200
confidence: 0.95
max_duration: 14d
evaluation:
  automated: deterministic_verifier + llm_judge
  human_panel: 10% sample, blind review
  shadow_first: true # run challenger silently before live split
```

### A/B Testing Design Principles

**Isolate One Variable** — Test the skill body change alone. Don't simultaneously change the model, harness, or tool set. You'll be unable to attribute the performance signal to any single cause.

**Stratified Sampling** — Ensure both variants see the same distribution of task complexity, user types, and domain contexts. Simple random routing can create imbalanced groups for rare edge cases.

**Shadow Mode First** — Run the challenger in shadow mode (execute but don't serve output to users) before splitting live traffic. Identify obvious failures before real-world exposure.

**Guardrail Metrics** — Define hard-stop conditions: error_rate >5%, any security violation, latency >2× baseline. Auto-rollback the challenger regardless of primary metric performance.

**Long-Horizon Checkpointing** — For multi-step tasks, measure success at each checkpoint (plan → execute → validate → output). A skill that excels at step 1 but degrades at step 4 needs a different fix than one that fails at step 1.

**Multi-Armed Bandits** — For high-traffic skill slots, MAB algorithms dynamically shift traffic toward the better-performing variant mid-experiment — reducing regret while maintaining statistical signal.

### What to A/B Test

| Test Dimension | Variant Examples | Primary Metric |
|---|---|---|
| Instruction style | Prescriptive step-by-step vs principle-based guidance | Task success rate |
| Negative examples | 0 vs 3 vs 10 negative trigger examples in YAML | Routing accuracy |
| Resource strategy | Link-only references vs inline script execution | Latency + success rate |
| Skill granularity | Monolithic SKILL.md vs split into sub-skills | Token cost per task |
| Output format | Free text vs structured JSON vs templated report | Human rating + usability |
| Trigger metadata | Broad domain tags vs narrow specific keywords | Routing precision & recall |
| Instruction length | Minimal (100 lines) vs comprehensive (400 lines) | TSR vs token cost tradeoff |

---

## 09 ENTERPRISE SYSTEM INTEGRATION

### Integrating Skills with Enterprise Systems

As of 2026, AI agents with skills have achieved 40% integration rate in enterprise applications. SAP Joule, Salesforce Agentforce, Microsoft Dynamics 365 Copilot, IBM watsonx Orchestrate, and ServiceNow AI Agents all support skill-like capability packages with varying governance models. The integration pattern differs significantly depending on your existing technology stack.

### Platform Integration Matrix

| Platform | Skill Mechanism | Best For | Integration Friction |
|---|---|---|---|
| IBM watsonx Orchestrate | 150+ pre-built skill catalog; SAP/Salesforce/ServiceNow connectors; SKILL.md via watsonx SDK | Large regulated enterprises; auditability non-negotiable | Low (for SAP/SFDC); longer procurement cycles |
| Salesforce Agentforce 360 | Agent builder with native skill authoring; Agentforce 360 unified deploy/observe | CRM-native workflows; customer-facing automation | Low for SFDC-native; MuleSoft required for external systems |
| ServiceNow AI Agents | AI Control Tower; CMDB-grounded context; cross-system Workflow Data Fabric | ITSM governance; IT service operations | Medium; 'massive operating model change, not software install' (ServiceNow docs) |
| Microsoft Copilot / Azure | APM skills; .NET plugin marketplace; Azure SRE Agent Plugins; SKILL.md native | Microsoft 365 / Azure-first orgs; developer tooling | Very low for M365/Azure; custom work for non-Microsoft systems |
| Google Vertex AI / ADK | Agent Development Kit (ADK) with SkillToolset; Google Cloud Agent Registry | GCP-native teams; multi-modal agent requirements | Low for GCP; usage-based pricing complexity at scale |
| NVIDIA Agent Toolkit | OpenShell runtime; cuOpt optimization skill library; Nemotron reasoning | 17+ enterprise ISVs (Adobe, SAP, Siemens, Palantir); GPU-accelerated reasoning | High initial setup; powerful for specialized inference workloads |

### CI/CD Integration Pattern — Post-CI Skill Execution

Skills can trigger post-CI to generate documentation, run security audits, update wikis, or notify downstream systems. The pattern works across GitHub Actions, GitLab CI, Jenkins, and Azure Pipelines.

```yaml
# .github/workflows/post-ci-skills.yml
on:
  workflow_run:
    workflows: ['CI']
    types: [completed]
    branches: [main]
jobs:
  run-skills:
    if: ${{ github.event.workflow_run.conclusion == 'success' }}
    steps:
      - uses: actions/checkout@v4
      - run: apm install # install all skills from apm.yml lockfile
      - run: python .github/scripts/run_skill.py docs-generator
      - run: python .github/scripts/run_skill.py security-audit
      - name: Commit outputs
        run: |
          git add docs/ wiki/ security/
          git diff --staged --quiet || \
          git commit -m 'ci: auto-update [skip ci]' && git push
```

### APM Integration with GitHub Actions Security

When Copilot Cloud Agent triggers workflows, it operates without access to organization secrets by default (as of May 2026). Secrets must be explicitly scoped to the Copilot environment. Use fine-grained PATs with minimal permissions rather than broad org secrets — this aligns with the least-privilege principle from the OWASP AST10 governance framework.

---

## 10 OKRs & KPI REFERENCE LIBRARY

### OKRs & KPIs for Agent Skills Programs

The failure mode in most agent programs is measuring the wrong thing — tracking invocation counts or token consumption instead of business outcomes. Every skill should tie to an OKR that a business leader owns, with KPIs that an engineer can instrument from day one.

### Executive OKR Framework

| OBJECTIVE | KEY RESULTS | OWNER |
|---|---|---|
| **O1: Accelerate developer velocity** | • ≥50% of code reviews AI-assisted by Q3 • PR cycle time reduced 40% • Bug escape rate unchanged or lower • Skill adoption: ≥84% of devs (Uber benchmark) | VP Engineering |
| **O2: Automate high-volume workflows** | • 3 business-critical workflows fully agent-handled by Q2 • Manual processing time reduced 60% • Agent error rate ≤ human baseline | COO / Head of Ops |
| **O3: Build a governed skill registry** | • 100 approved skills in core registry by H1 • 80% of agent tasks resolved without new skills • Mean time to publish ≤5 days | Platform Eng Lead |
| **O4: Achieve measurable skill quality** | • ≥95% task success rate on curated set • Zero P0 security incidents from skills • Every skill A/B tested within 90 days of launch | Head of AI Platform |
| **O5: Positive ROI on agent investment** | • Cost per automated task ≤ 30% of manual • Token cost per task decreasing QoQ • Productivity value quantified in board report | CFO / AI Sponsor |

### KPI Reference Library

**Skill Quality:** TSR ≥85%, Routing Precision ≥85%, Skill Regression ≤5%, JSON Parse Success ≥98%

**Operational:** Latency P95 within Baseline + 20%, Token Cost decreasing QoQ, Skill Reuse ≥80%, Error Rate ≤5%

**Developer Experience:** Time to Publish ≤5 days, Developer Adoption ≥50% at 6 months, Skill NPS ≥35, Manual Override ≤15%

**Business Impact:** Hours Automated per week tracked, Error Rate vs Human ≤1.0× parity, Cost per Outcome ≤30% of manual, Skill ROI >200% at 12 months

**Governance & Security:** Zero P0 security incidents, Audit Coverage 100%, Scan Pass Rate 100%, Staleness Rate ≤10%

---

## 11 PERSONAS & ROLES

A healthy skill program involves multiple personas with distinct needs. Key personas: **Skill Author** (publish fast, see adoption), **Platform Engineer** (reliability, versioning, cost control), **Security Engineer** (prevent injection, audit trails), **Process Owner** (automate workflows, prove ROI), **End User** (consistent, transparent outputs), **AI Program Sponsor** (ROI proof, competitive positioning), **Registry Admin** (curated registry, governance), **AI Evaluator** (quality measurement, A/B experiments).

---

## 12 GOVERNANCE, SECURITY & OWASP AST10

### Security, Governance & OWASP AST10

The rapid growth of public skill registries has created serious security risks. Snyk's ToxicSkills audit (Feb 2026) of 3,984 skills found 534 (13.4%) with critical issues. Mobb.ai's audit of 22,511 skills across four registries found 140,963 total issues. The ClawHavoc campaign in Feb 2026 saw 341 malicious skills in ClawHub. Traditional SAST tools miss nearly all of these because the attack vector is natural language, not code.

### Why Classic SAST Fails — and the Dual-Layer Solution

Skills are hybrid artifacts. You need traditional code analysis for executable components (bundled scripts, YAML parsers) AND language understanding to catch prompt injection and natural language malware. Snyk's agent-scan engine combines multiple LLM-based judges with deterministic rules. 91% of verified malware combined language jailbreaks with executable payloads — single-layer scanners miss most real attacks.

| Scan Layer | Mechanism | Catches |
|---|---|---|
| L1: Deterministic / Pattern | Regex + SAST rules on YAML headers and bundled scripts | Hardcoded secrets, unsafe syscalls, curl\|bash patterns, base64 drops, typosquatting |
| L2: Semantic / LLM Judge | Multi-model LLM judges evaluating natural language instructions | Prompt injection, toxic flows (data access + untrusted source + external comms), intent vs behaviour divergence, social engineering patterns |
| L3: Human Review | Mandatory for disagreements between L1/L2; 10% sample for curated registries | Novel attack patterns not yet in training data; ambiguous instructions |
| Runtime Sandbox | Containerized execution: seccomp, AppArmor, Firecracker VMs | Blast radius limitation even if static scan misses a malicious skill |

### Five-Layer Governance Framework

| Control Layer | Mechanism | Tooling |
|---|---|---|
| Identity | Every agent has a signed identity; Agent Personas scope privilege sets; IAM binding to skill invocation rights | Cequence Agent Personas, AWS IAM, Google Cloud IAM |
| Supply Chain | Automated SAST on all SKILL.md files before registry publish; VirusTotal integration; content-addressable SHA-256 hashing | Snyk, Cisco skill-scanner, OWASP AST10 scanner |
| Runtime Isolation | Containerized skill execution; sandboxed script runners; network egress controls per skill namespace | Harbor Framework, Docker sandboxes, Firecracker VMs |
| Audit | Immutable audit logs per invocation; full trajectory capture; compliance reporting to SOC2 / GDPR standards | Langfuse, AWS CloudTrail, Splunk |
| Access Control | RBAC by namespace; per-skill permission matrix; human approval gates for sensitive/irreversible actions | SkillHub RBAC, APM apm-policy.yml, Azure SRE Agent Plugins |

### OWASP AST10 — Top 10 Agentic Skill Risks

| # | Risk | Example Attack |
|---|---|---|
| AST1 | Skill supply chain poisoning | Malicious skill published to public registry; installs via typosquatting |
| AST2 | Prompt injection at skill layer | Skill instructions override agent's system prompt or safety filters |
| AST3 | Credential/secret exposure | API keys or PII hardcoded in SKILL.md resource files |
| AST4 | Privilege escalation | Skill grants agent elevated permissions beyond task scope |
| AST5 | Toxic flow exploitation | Skill combines data access + untrusted source + external comms |
| AST6 | YAML parser exploitation | Malformed YAML in SKILL.md triggers RCE in agent's parser |
| AST7 | Unauthorized invocation | Skill called without RBAC check; bypasses permission boundary |
| AST8 | Data exfiltration via skill | Skill reads SSH keys / env vars and POST to attacker URL |
| AST9 | Skill staleness exploitation | Outdated skill with known vuln kept active due to no deprecation process |
| AST10 | Social engineering via skill | Skill manipulates agent self-perception to disable safety measures |

---

## 13 THE ROAD AHEAD

### What's Next for Agent Skills

**Cross-Model Skill Portability** — The AAIF standard means a skill designed for Claude runs on Copilot, Codex, or Gemini without modification. The 'Agentic Web' is the next inflection — value lives in portable skills, not locked-in models.

**Self-Adapting Skills** — Skills that update their own instruction bodies based on aggregated feedback signals, closing the loop between evaluation telemetry and skill content — without human authorship at every iteration. Currently experimental.

**Federated Skill Networks** — Cross-company skill sharing (with IP controls) for industry-standard workflows: healthcare EDI, financial reporting, legal discovery. Common enough to share; specific enough to need skills.

**Skill Marketplace Economics** — Skill authors earning revenue per successful invocation — the 'Agentic App Store.' Micro-payments per task completion for third-party skill publishers. Early models emerging in 2026.

**Agent Engineers** — Uber's CTO envisions AI systems that handle coding, testing, and deployment supervised by other AI. Human skill authors shift to defining intent, constraints, and evaluation criteria — not writing SKILL.md content line by line.

**Enterprise Skill Compliance** — GDPR, SOX, and sector-specific regulations will require skills to carry compliance metadata. Audit trails per invocation will become regulatory baseline, not best practice. Skills will need jurisdiction-aware routing.

### STRATEGIC IMPERATIVE

The competitive advantage in 2026 comes from **infrastructure, not intelligence**. The model is increasingly a commodity. The skill registry, harness, evaluation pipeline, and governance framework — built and iterated over months — create structural moats that a model upgrade alone cannot overcome. The organizations investing in skill infrastructure today will be the ones setting the benchmark numbers that others cite next year.
