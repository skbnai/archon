---
title: "Responsible AI for Agentic Applications"
date_created: 2026-07-24
last_reviewed: 2026-07-24
status: current
domain: agentic-systems
doc_type: guide
topic_id: responsible-ai
supersedes:
  - docs/agentic-ui/responsible-ai.md
---

**Continue to [Part 2 →](pathname:///archon/agentic-systems/agentic-ui/parts/17-responsible-ai-part2)** for Constitutional AI, Sovereign AI, Transparency, Explainability, Fairness, and Human Oversight.

# Responsible AI for Agentic Applications

**Audience:** Enterprise AI/Principal AI Architects, AI Platform Teams, Security Architects, and Compliance/Risk Officers designing, implementing, and auditing responsible AI practices in agentic UI systems — how RAI requirements manifest in UX, architecture, and operations, not the regulatory frameworks themselves (covered in linked references).

:::note Scope Boundary
    This file covers **UX, architecture, and operational implementation** of RAI requirements. For full EU AI Act / NIST AI RMF / ISO 42001 details, see [Enterprise AI Governance & Compliance](../../architecture/51-enterprise-ai-governance-compliance.md). For governance structures, see [Governance for Agentic Applications](11-governance.md).

---

## 1. RAI in the Agentic UI Context

### 1.1 How Agentic UIs Amplify Traditional AI Risks

Traditional AI risk assessment targets models that return text in response to queries. Agentic UIs — with event streaming, tool execution, persistent memory, and autonomous action — change the risk surface fundamentally:

| Risk Dimension | Chatbot AI | Agentic UI |
| --- | --- | --- |
| **Agency** | None — returns text only | High — executes tool calls, modifies state, takes real-world actions |
| **Persistence** | Stateless | Persistent memory across sessions; long-term personalization |
| **Scope of effect** | One conversation | Multi-system impact through tool chains |
| **Transparency** | Full output visible | Reasoning, tool calls, and sub-agent activity may be hidden from user |
| **Consent** | Implicit in using chatbot | Complex — user may not realize agent is acting autonomously |
| **Reversibility** | Always reversible (text output) | Some actions irreversible (sent email, financial transaction, deleted data) |
| **Speed** | Human reading pace | Multi-step plans execute in seconds, faster than human can review |
| **Delegation** | None | Agent may spawn sub-agents with delegated authority |
| **Bias amplification** | Biased text output | Biased tool selection, personalization drift, differential treatment at scale |
| **Accountability gap** | Who wrote the prompt? | Who authorized the agent action? User? App owner? Platform? LLM? |

### 1.2 New Risks Unique to Agentic UIs

**1. Tool execution risk:** agents calling financial APIs, sending emails, or writing to databases cause real harm via biased decisions or misunderstood instructions.

**2. Multi-agent system risk:** responsibility diffuses across orchestrators and sub-agents; bias at one layer propagates downstream.

**3. Persistent memory risk:** long-term memory encodes historical bias or stale context; memory can be poisoned adversarially.

**4. Generative UI risk:** AI-generated UI surfaces can be crafted to solicit unintended user actions.

**5. Autonomous action risk:** agents under HOOL patterns act without per-step approval; misconfigured guardrails cause cascading unauthorized actions.

### 1.3 The RAI-UX Connection

RAI principles manifest directly in user interface design, not just backend architecture:

| RAI Principle | UX Manifestation | Interface Pattern |
| --- | --- | --- |
| **Transparency** | Users must know they are interacting with AI | AI disclosure indicator; first-use notice; persistent badge |
| **Explainability** | Users can understand why agent took an action | Reasoning disclosure (progressive); action justification |
| **Consent** | Users authorize agent memory, tool use, data access | Memory opt-in flow; tool capability consent screen |
| **Human oversight** | Users can intervene, override, approve | HITL approval UI; pause/cancel controls; override button |
| **Fairness** | Users receive equitable treatment | No differential UI; accessible design; bias-audited outputs |
| **Privacy** | PII handled per user expectations | Data use notice; memory control UI; data deletion capability |
| **Safety** | High-risk actions prevented or gated | Warning dialogs; action confirmation; irreversibility warning |
| **Accountability** | Users can trace what the agent did | Activity log; action history; audit trail access |
| **Robustness** | Agent behaves consistently | Deterministic UI state; clear error states; degraded-mode UX |

---

## 2. EU AI Act for Agentic UI Applications

For full EU AI Act framework and Digital Omnibus deadlines, see [Enterprise AI Governance & Compliance](../../architecture/51-enterprise-ai-governance-compliance.md) §2. This section covers how obligations manifest in **agentic UI design and architecture**.

### 2.1 High-Risk Classification for Agentic Apps

Agentic applications below are likely high-risk under Annex III (obligations apply December 2, 2027):

| Application Domain | High-Risk Criterion | Agentic UI Examples |
| --- | --- | --- |
| **Employment decisions** | AI used in hiring, task assignment, performance evaluation | Agentic HR assistants, automated scheduling tools |
| **Credit/financial services** | AI evaluating creditworthiness, setting terms | Agentic financial advisors with recommendation capability |
| **Healthcare** | AI in clinical decision support, triage | Agentic health assistants with symptom assessment |
| **Education** | AI determining access to education, assessment | Agentic tutoring with automated grading |
| **Essential private services** | AI used in decisions about access to services | Agentic customer service with escalation decisions |
| **Law enforcement** | AI supporting police decisions | Agentic investigation tools |
| **Critical infrastructure** | AI managing utilities, transport, finance infrastructure | Agentic operations assistants |
| **Judicial** | AI assisting court decisions | Legal agentic tools with recommendation capability |

:::warning Classification is Application-Specific
    A general-purpose Q&A agent is minimal risk; the same LLM as a hiring decision tool is high-risk. Classification depends on **use case and deployment context**, not the model.

### 2.2 GPAI Obligations and Agentic Applications (August 2026)

GPAI-based agentic apps (Claude, GPT-5, Gemini, frontier open-source) have pass-through obligations under Article 53:

| GPAI Obligation | Agentic App Implication |
| --- | --- |
| **Technical documentation** | Maintain deployment configuration version control |
| **Usage policy compliance** | Review model provider terms; include in vendor contracts |
| **Copyright compliance** | Implement output filtering for copyright-sensitive cases |
| **AI-generated content marking** | Mark GPAI outputs with C2PA or equivalent |

### 2.3 Transparency Obligations in UX (Art. 50, August 2026)

Article 50 requires users interacting with AI systems be informed of it. For agentic UIs:

| Transparency Requirement | Implementation Option | Notes |
| --- | --- | --- |
| **AI disclosure at point of interaction** | Persistent "AI" badge in chat header | Must be visible throughout interaction, not buried |
| **First-use notice** | Welcome screen with AI disclosure | Clear, plain language; not buried in T&Cs |
| **Agent identity disclosure** | Agent name + "AI agent" in interface | "Aria (AI Agent)" not just "Aria" |
| **Capability disclosure** | What the agent can and cannot do | Capability statement at onboarding |
| **Memory disclosure** | If agent remembers user, disclose what and how long | Memory notice in privacy settings |
| **Tool use disclosure** | When agent uses tools that access external systems | Tool use notification in event stream |

A persistent status indicator is the minimum baseline (low friction, high compliance); a first-use consent screen is recommended for all agentic apps (medium friction, very high compliance). A buried footnote in the T&Cs is not compliant with Art. 50.

### 2.4 Human Oversight Requirements (Art. 14)

Article 14 requires human oversight for high-risk systems. For agentic UIs:

| Art. 14 Requirement | AGUI Implementation |
| --- | --- |
| **Understand capabilities and limitations** | Capability disclosure at onboarding |
| **Aware of automation bias** | Bias warnings for high-stakes decisions |
| **Interpret output correctly** | Reasoning disclosure; confidence indicators |
| **Decide not to use / override** | Override controls; escalation path |
| **Intervene in real time** | Pause / cancel controls |

See Part 2 for implementation details.

### 2.5 Prohibited Practices Relevant to Agentic UX

Article 5 prohibitions for agentic UI design:

| Prohibited Practice | How It Applies to Agentic UIs |
| --- | --- |
| **Subliminal manipulation** | No techniques below conscious awareness; no dark patterns in approval UI |
| **Exploiting vulnerabilities** | No exploitation of user emotional state or crisis |
| **Social scoring** | No behavior-based user discrimination |
| **Real-time biometric surveillance** | No unauthorized face/behavioral biometrics |
| **Emotional manipulation in AI-generated UI** | No manipulative design in A2UI |

### 2.6 Conformity Assessment Process

**Conformity assessment workflow (high-risk, Annex III):**

1. **Risk classification** — determine whether the application is high-risk under Annex III; document the classification decision with justification.
2. **Technical documentation** — compile:
   - System description and intended purpose
   - Architecture diagrams and data flow
   - Training/validation data documentation (if fine-tuned)
   - Risk management documentation
   - Bias testing results
   - Human oversight design documentation
   - Robustness and cybersecurity measures
   - Monitoring and post-deployment plan
3. **Risk management system** — implement:
   - Risk identification register
   - Risk controls mapping
   - Residual risk assessment
   - Risk monitoring plan
4. **Conformity assessment** — conduct:
   - Self-assessment (if no notified body required)
   - Third-party assessment (if required for specific Annex III cases)
   - Internal audit documentation
5. **EU declaration of conformity** — sign and maintain declaration.
6. **CE marking / registration** — register in EU AI Act database if required.
7. **Post-market monitoring**:
   - Incident reporting within 15 days of serious incident
   - Annual monitoring report
   - Continuous bias and performance monitoring

---

## 3. NIST AI RMF for Agentic Systems

For the full NIST AI RMF framework description, see [Enterprise AI Governance & Compliance](../../architecture/51-enterprise-ai-governance-compliance.md) §2.2.

Covers how GOVERN/MAP/MEASURE/MANAGE apply to **agentic-specific scenarios**.

### 3.1 GOVERN — Governance Structures for Agentic Apps

| Activity | Implementation | Owner |
| --- | --- | --- |
| **GV-1: Risk tolerance** | Define acceptable risk levels; financial/PII limits | AI Governance Committee |
| **GV-2: Accountability** | Agent Registry; RACI per domain | AI Platform Lead |
| **GV-3: Oversight** | Document HITL/HOTL/HOOL per application | App Owner + PAB |
| **GV-4: Teams** | AI CoE with RAI competency | AI CoE Lead |
| **GV-5: Policies** | Prompt, tool, memory governance | AI Governance Lead |
| **GV-6: Lifecycle** | Stage gates; deployment governance | AI Portfolio Manager |

### 3.2 MAP — Agentic-Specific Risk Scenarios

| Risk Scenario | Category | Likelihood | Impact | Priority |
| --- | --- | --- | --- | --- |
| **Autonomous action without authorization** | Agent behavior | Medium | High | P1 |
| **Context poisoning via document retrieval** | Input integrity | High | High | P1 |
| **Agent impersonation via spoofed A2A identity** | Identity | Low | Critical | P1 |
| **Memory poisoning via adversarial input** | Input integrity | Medium | High | P1 |
| **Over-delegation via OBO chain** | Authorization | Medium | High | P1 |
| **Personalization drift amplifying bias** | Fairness | Medium | Medium | P2 |
| **Tool abuse via prompt injection** | Input integrity | High | High | P1 |
| **PII exfiltration via tool output** | Privacy | Low | Critical | P1 |
| **Goal hijacking via multi-hop injection** | Input integrity | Low | Critical | P1 |
| **Token flooding / denial of service** | Availability | Medium | Medium | P2 |
| **Hallucinated tool parameters** | Reliability | High | Medium | P2 |
| **Unauthorized sub-agent spawning** | Authorization | Low | High | P2 |
| **Session state cross-contamination** | Isolation | Low | Critical | P1 |
| **Biased tool selection** | Fairness | Medium | Medium | P2 |

### 3.3 MEASURE — Metrics for Agentic AI Risk

| Category | Metric | Target |
| --- | --- | --- |
| **Autonomous action** | % of high-risk actions with approval | 100% |
| **Context integrity** | Injection attempts detected | &lt;5% |
| **Identity assurance** | Agent-to-agent calls verified | 100% |
| **Memory integrity** | Memory writes with provenance | 100% |
| **Tool authorization** | Tool calls within scope | 100% |
| **Fairness** | Disparate impact ratio | &lt;20% |
| **Privacy** | PII in outputs | 0% |
| **Transparency** | Interactions with disclosure | 100% |
| **Oversight** | HITL actions reviewed | 100% |
| **Incident rate** | Per 1000 sessions | Track &amp; reduce |

### 3.4 MANAGE — Risk Treatment for High-Risk Scenarios

| Risk Scenario | Treatment | Implementation |
| --- | --- | --- |
| **Autonomous action without authorization** | Preventive: action authorization matrix; Detective: anomaly monitoring; Corrective: automatic suspension | Tool capability classification + HITL gates + rogue agent playbook |
| **Context poisoning** | Preventive: input sanitization; Detective: injection detection; Corrective: session invalidation | DLP at context assembly + injection classifier |
| **PII exfiltration** | Preventive: output filtering; Detective: DLP on outputs; Corrective: incident response | Output DLP + PII detection |
| **Goal hijacking** | Preventive: trust tier enforcement; Detective: goal drift monitoring; Corrective: session reset | Trust boundary enforcement + behavioral monitoring |
| **Personalization bias** | Preventive: bias-aware memory; Detective: fairness metrics; Corrective: memory correction workflow | Fairness evaluation pipeline + memory correction API |

### 3.5 CAISI Framework (February 2026)

CAISI (Comprehensive AI Safety and Integrity Standards) extends NIST AI RMF 2.0 for agentic use:

| Extension | Agentic UI Implementation |
| --- | --- |
| **Autonomy risk tiers (A1–A5)** | Map agents to CAISI tier; apply controls |
| **Multi-agent accountability** | Document accountability chain |
| **Real-time oversight** | Define HITL/HOTL/HOOL per tier |
| **Memory governance** | Align memory controls to CAISI standards |
| **Tool risk assessment** | Classify tools per CAISI taxonomy |

---

## 4. OWASP LLM Top 10 (2025) in Agentic UI Applications

For OWASP Agentic AI ASI01–ASI10, see [Agentic AI Security &amp; Identity](../../trust/index.md). Maps OWASP LLM Top 10 (2025, chatbot origin) to agentic UI surfaces.

### 4.1 LLM01–LLM10 Mapped to AGUI Attack Surfaces

| OWASP ID | Category | How It Manifests in AGUI Apps | Mitigation |
| --- | --- | --- | --- |
| **LLM01** | Prompt Injection | Malicious content in tool responses, retrieved docs, or A2UI payloads hijacks agent behavior; indirect injection via knowledge base | Input sanitization at context assembly; trust tier enforcement; content classifiers |
| **LLM02** | Insecure Output Handling | Agent-generated content rendered in browser without sanitization causes XSS; A2UI malicious widget injection | Output sanitization; DOMPurify for rendered content; A2UI schema validation |
| **LLM03** | Training Data Poisoning | Poisoned fine-tuning data causes systematic bias; contaminated RAG knowledge base affects all queries | Data provenance verification; knowledge content review process |
| **LLM04** | Model DoS | Adversarial inputs designed to maximize token consumption; tool loops; context explosion attacks | Per-session token budgets; step count limits; circuit breakers |
| **LLM05** | Supply Chain Vulnerabilities | Malicious MCP server packages; poisoned model weights; compromised tool registry | MCP server provenance verification; dependency scanning; signed packages |
| **LLM06** | Sensitive Information Disclosure | Agent reveals confidential data from context, retrieval, or training in outputs | Output filtering; DLP; context data minimization |
| **LLM07** | Insecure Plugin Design | MCP tool with overly broad permissions; tool without input validation | Tool capability classification; least-privilege tool design; tool input validation |
| **LLM08** | Excessive Agency | Agent executes actions beyond user intent; autonomous scope creep | Capability scope declaration; action confirmation for high-impact tools; HITL gates |
| **LLM09** | Overreliance | Users over-trust agent outputs for high-stakes decisions without verification | Uncertainty disclosure; confidence indicators; disclaimer for professional advice |
| **LLM10** | Model Theft | AG-UI event stream reveals model reasoning; system prompt extraction via clever prompting | System prompt protection; reasoning exposure controls; differential privacy |

---
