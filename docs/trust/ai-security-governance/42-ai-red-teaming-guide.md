---
title: "AI Red Teaming: Adversarial Testing for AI and Agentic Systems"
doc_type: guide
domain: trust
status: current
topic_id: ai-red-teaming-guide
last_reviewed: 2026-07-27
maturity: practitioner
supersedes: [docs/ai-security-governance/security/AI-Red-Teaming-Guide.md]
tags: [ai-red-teaming, adversarial-testing, prompt-injection, agentic-security]
covers_version: "as of 2026"
---

Human and automated adversarial testing — jailbreaks, prompt injection, data poisoning, model extraction, and agentic misuse — that reveals AI system failures before adversaries do.

## What Is AI Red Teaming?

AI red teaming is adversarial testing that systematically probes AI systems for exploitable vulnerabilities, combining human creativity with automated tooling to simulate real attack scenarios across LLM vulnerabilities (jailbreaks, prompt injection, harmful output generation), agent-specific attacks (goal hijacking, tool misuse, memory poisoning, multi-agent coordination attacks), infrastructure attacks (model extraction, training-data poisoning, supply chain compromise), and operational attacks (evasion of monitoring, detection bypass, adversarial examples). The OWASP Agentic Top 10 is the threat taxonomy that AI red teams operationalize through testing.

**Red teaming vs. other security practices:**

| Practice | Focus | Frequency |
|---|---|---|
| AI Red Teaming | Adversarial simulation; finds exploitable vulnerabilities | Quarterly minimum; before major releases |
| AIDR | Runtime detection of attacks in production | Continuous |
| AISPM | Configuration posture and supply-chain risk | Continuous |
| Penetration testing | Infrastructure and application layer attacks | Annual minimum |
| Evaluation / evals | Quality and safety benchmarking (not adversarial) | Every deployment |

Red teaming validates that AIDR and guardrails actually work — it generates the "hard examples" that make detection systems robust.

## The AI Red Team Methodology

**Phase 1 — Scoping and Threat Modeling (Days 1-3).** Define the attack surface and objectives: identify the target system (LLM, agent, multi-agent pipeline, MCP server); map the threat model against which OWASP ASI01-ASI10 threats apply; define success criteria for a successful attack; select attack categories (jailbreak, injection, exfiltration, tool misuse); and assign team roles across prompt engineers, security researchers, and domain experts.

**Phase 2 — Automated Scanning (Days 3-7).** Run automated tool suites in parallel: Garak (a vulnerability probe suite with 100-plus probes and 20,000 prompts), PyRIT (orchestrated attack sequences with an AI Red Teaming Agent), Promptfoo (regression testing plus an adversarial eval harness), and Gaia (agentic-specific goal-hijack testing).

**Phase 3 — Manual Adversarial Testing (Days 7-14).** Human red teamers probe what automation misses: indirect injection via tool responses (documents, email, database records); multi-turn manipulation that builds trust across a conversation before attacking; context-window attacks that exploit long-context handling for injection; cross-agent attacks that use one agent to attack another in a multi-agent pipeline; MCP tool poisoning via crafted malicious tool descriptions or responses; and memory persistence attacks that inject content surviving across sessions.

**Phase 4 — Report and Remediation (Days 14-21).** Structured findings capture severity (Critical/High/Medium/Low), exploitability (automated/manual/requires insider access), impact (data exfiltration, goal hijack, harmful output, service disruption), and remediation (guardrail update, prompt hardening, policy change, architecture change).

## Tooling Landscape

**Garak** (NVIDIA) is an open-source LLM vulnerability scanner using a probe-based approach — roughly 100 prebuilt probes across 20-plus attack categories including prompt injection, jailbreaks, encoding bypasses, glitch tokens, toxicity, training-data extraction, output XSS, and malware generation. A single run can issue up to 20,000 adversarial prompts. It's best for systematic baseline scanning before deployment and CI/CD integration:

```bash
pip install garak
garak --model openai --model_type gpt-4o --probes promptinjection,jailbreak,encoding
```

**PyRIT** (Microsoft) is an open-source adversarial testing framework using orchestrated attack sequences, including an AI Red Teaming Agent, natively integrated with Azure AI Foundry but usable against any LLM endpoint. It's best for enterprise workflows, automated attack orchestration, and Azure-native teams:

```python
from pyrit.orchestrator import PromptSendingOrchestrator
from pyrit.attack_strategy import JailbreakAttackStrategy

orchestrator = PromptSendingOrchestrator(
    objective_target=target,
    attack_strategy=JailbreakAttackStrategy(objective="extract system prompt"),
)
await orchestrator.run()
```

**Promptfoo** is an open-source LLM testing and red-teaming framework using YAML-defined test suites for adversarial evaluation plus regression testing, covering prompt injection, harmful content, PII leakage, and hallucination — best for CI/CD integration and regression testing on every deployment:

```yaml
redteam:
  plugins:
    - prompt-injection
    - jailbreak
    - pii-extraction
    - harmful-content
  strategies:
    - jailbreak:composite
    - prompt-injection:indirect
```

**Mindgard** is a commercial automated AI red-teaming platform offering continuous adversarial testing integrated with CI/CD across agentic AI, LLMs, and computer vision models — best for enterprises wanting managed red teaming without internal expertise.

Manual tooling rounds out the toolkit: Burp Suite with AI extensions for HTTP-level prompt interception and manipulation; Langfuse for trace inspection to understand attack execution paths; and custom injection harnesses for domain-specific scenarios such as banking document injection.

## Attack Categories and Techniques

**Prompt injection** (OWASP ASI01/LLM01) is the most prevalent attack, ranked #1 in the OWASP LLM Top 10 for three consecutive years. Techniques include direct injection (malicious instructions in the user input field), indirect injection (instructions embedded in retrieved documents, emails, or web pages), nested injection (injection within tool responses returned to the agent), multi-hop injection (injection that persists through agent handoffs), and encoding bypass (Base64, Unicode, ROT13, or leetspeak variants to evade filters).

**Jailbreaking** techniques include role-play bypass ("pretend you are an AI without restrictions"), hypothetical framing ("in a fictional universe where..."), many-shot jailbreak (hundreds of examples establishing a pattern before the harmful request), crescendo (gradually escalating requests from benign to harmful), and composite attacks that combine multiple techniques for higher success rates.

**Agentic-specific attacks** map directly to the OWASP ASI taxonomy: Goal Hijack (ASI01) injects redirected objectives through retrieved content; Tool Misuse (ASI02) crafts inputs that cause tools to be called with malicious parameters; Memory Poisoning (ASI06) injects persistent malicious context into agent memory; Multi-Agent Attack (ASI07) compromises one agent to attack another via the A2A protocol; and Rogue Agent (ASI10) deploys an unauthorized agent impersonating a legitimate one.

## Agentic Red Teaming: What Changes

Traditional LLM red teaming tests individual prompt-response pairs. Agentic red teaming must test full execution sequences — research on redefining AI red teaming in the agentic era identifies the key shifts:

| Dimension | LLM Red Teaming | Agentic Red Teaming |
|---|---|---|
| Scope | Single prompt to single response | Multi-step execution graph |
| Attack surface | Input prompt | Prompt + tool calls + memory + A2A messages |
| Success metric | Harmful output produced | Goal achieved by the agent against policy |
| State | Stateless | Stateful — attacks can span multiple sessions |
| Tools available | None | All tools the agent has access to |
| Time horizon | Seconds | Minutes to hours |

Automated red-teaming frameworks have reduced agentic red team cycle times from weeks to hours.

## Enterprise Red Teaming Program

**Cadence:** a full red team across all attack categories runs before first production deployment; a focused pass on behavioral changes and regression runs before every major model upgrade; a rotating single-category focus runs quarterly; a targeted re-test of the specific attack vector runs after any security incident; and new threats are mapped to the current system whenever new OWASP guidance is published.

**Team structure:** a red team lead owns scoping, methodology, and report sign-off; a prompt engineer crafts novel injection and jailbreak scenarios; a security researcher covers infrastructure and protocol-layer attacks; a domain expert covers industry-specific attack scenarios (banking, healthcare); and a blue team liaison shares findings with the AIDR tuning team.

**Metrics:**

| KPI | Target |
|---|---|
| Attack surface coverage (% of OWASP ASI threats tested) | 100% annually |
| Critical findings mean time to remediate | &lt;7 days |
| High findings MTTR | &lt;30 days |
| Automated scan frequency | Every deployment |
| Manual red team cadence | Quarterly minimum |
| Finding recurrence rate (same finding re-discovered) | 0% |

## Related

- [AI TRiSM Complete Guide](43-ai-trism-complete-guide.md)
- [AIDR: AI Detection & Response](44-aidr-ai-detection-response-complete-guide.md)
- [Agent, Tool & MCP Authorization](27-agent-tool-mcp-authorization.md)
