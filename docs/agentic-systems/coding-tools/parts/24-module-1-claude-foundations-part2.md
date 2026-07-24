---
title: Claude Foundations & Ecosystem Overview (Part 2)
doc_type: learning-path
domain: agentic-systems
topic_id: module-1-claude-foundations-part2
status: current
date_created: 2026-07-24
last_reviewed: 2026-07-24
tags: [coding-tools]
supersedes: []
---

# Claude Foundations & Ecosystem Overview (Part 2)

Continuation: token economics, safety philosophy, deployment channels, and CCA-F certification pathway

**This is Part 2 of 2. [Return to Part 1 ←](pathname:///archon/agentic-systems/coding-tools/24-module-1-claude-foundations) for Claude model families, product suite overview, plans, and API pricing.**

## 1.6 Token Economics & Context Windows

Tokens are the fundamental unit of measurement for all Claude API interactions. A token is roughly 4 characters or 0.75 words in English. Different languages have different token densities — code, JSON, and non-Latin scripts often tokenize differently.

| Unit | Equivalence |
|------|------------|
| **1 token** | ~4 characters or ~0.75 words in English text |
| **1,000 tokens** | ~750 words — about 3 pages of double-spaced text |
| **Max context (Opus/Sonnet 4.6+)** | 1,000,000 tokens — ~750,000 words, ~2,000 pages |
| **Max context (Haiku 4.5)** | 200,000 tokens — ~150,000 words, ~500 pages |
| **Max output (Opus 4.6/4.7/4.8)** | 128,000 tokens — extended with output-300k-2026-03-24 beta to 300K |
| **Max output (Sonnet 4.6)** | 64,000 tokens; 300K with beta header |
| **Max output (Haiku 4.5)** | 8,192 tokens standard |
| **Token counting API** | Use /v1/messages/count_tokens to pre-calculate before billing |
| **Context auto-compaction** | Claude Code compacts context at ~75-92% capacity — summarizes history |
| **Cache minimum** | 1,024 tokens minimum to be eligible for prompt caching |
| **Thinking tokens** | Extended thinking tokens count toward max_tokens but previous thinking blocks are stripped |

### Context Window Strategy for Architects

| Scenario | Architectural Recommendation |
|----------|------------------------------|
| **Static system prompt** | Mark with cache_control: ephemeral — free cache refresh after 5 min, ~90% discount on hits |
| **Large reference document** | Chunk it — or cache the document in the context for repeated queries |
| **Long conversation history** | Implement server-side summarization at ~70% capacity; never rely on auto-compaction for API apps |
| **RAG retrieved chunks** | Inject at the end of the user message — after the static cached content |
| **Multi-modal inputs** | Images cost ~1,600 tokens each regardless of image size; PDFs counted per page |
| **Measuring actual usage** | Always log response.usage.input_tokens + output_tokens for cost tracking |

## 1.7 Constitutional AI & Safety Philosophy

Constitutional AI (CAI) is Anthropic's training methodology that embeds safety behaviors directly into the model rather than applying them as post-hoc filters. Understanding CAI is essential for Domain 5 of the CCA-F exam and for designing compliant enterprise applications.

### How Constitutional AI Works

| Phase | Description |
|-------|------------|
| 1. RLHF (Base) | Standard reinforcement learning from human feedback to create a capable base model |
| 2. Constitution | A set of principles ('the constitution') defining what makes Claude's responses good or bad |
| 3. AI Feedback (RLAIF) | Claude critiques its own outputs against the constitution — no human labeling needed at scale |
| 4. Revision | Claude revises responses based on its own constitutional critique |
| 5. Fine-tuning | The revised outputs train the final model — safety behaviors are intrinsic, not a filter |

### The Three-Tier Permission System

Claude's behavior is governed by a three-tier system. Each tier can only operate within the bounds set by the tier above it:

| Tier | Authority Level | What They Control |
|------|-----------------|------------------|
| **TIER 1 — Anthropic (Training)** | Highest authority | Sets absolute limits via Constitutional AI |
| **TIER 2 — Operators (System Prompt)** | Middle authority | Can adjust Claude's default behaviors |
| **TIER 3 — Users (Chat Messages)** | Lowest authority | Can adjust behaviors within operator-set bounds |

### Hard Limits (Cannot Be Overridden at Any Tier)

- Generating sexual content involving minors (CSAM) — absolute, no exceptions
- Providing meaningful technical uplift for creating CBRN (chemical, biological, radiological, nuclear) weapons
- Creating functional cyberweapons or malware designed to cause significant damage
- Denying being an AI when a user sincerely and directly asks
- Taking actions that undermine the ability of humans to oversee and correct AI systems
- Assisting attempts to seize unprecedented societal control

### Adjustable Default Behaviors (Operator-Configurable)

Many behaviors are default ON or OFF but can be adjusted by operators:

- Default ON — operators CAN turn off: Using crude/profane language; providing extremely blunt feedback without diplomatic softening
- Default OFF — operators CAN turn on: Accepting roleplay scenarios involving illegal activities (for research/training purposes only)

## 1.8 Responsible Scaling Policy (RSP)

The Responsible Scaling Policy establishes the framework by which Anthropic decides when to train and deploy increasingly powerful models. It defines AI Safety Levels (ASL) that trigger specific safety requirements. Enterprise architects should understand this because it explains why certain capabilities are gated or restricted.

| Level | Threshold | Implications |
|-------|-----------|-------------|
| **ASL-1** | Current commercial models | No extraordinary risks identified. Standard deployment permitted. |
| **ASL-2** | Models approaching serious uplift for CBRN or cyberweapons | Enhanced evaluations required. Standard deployment with monitoring. |
| **ASL-3** | Models capable of serious CBRN uplift or autonomous replication | Strict security controls required before deployment. Not yet reached. |
| **ASL-4** | Models posing catastrophic risk | Full capability control protocols required. Theoretical at this stage. |

**Enterprise Implication:** The RSP means that Anthropic proactively withholds certain capabilities if safety evaluations are not met — even if those capabilities are technically achievable. For example, Claude Mythos Preview (the most advanced frontier model) is restricted to trusted organizations via Project Glasswing due to cybersecurity concerns.

## 1.9 Deployment Channels: Direct API, Bedrock, Vertex

Enterprise architects must choose the right deployment channel based on infrastructure, compliance, data residency, and operational requirements. Each channel offers different SLAs, IAM integrations, and data isolation guarantees.

| Feature | Direct Anthropic API | Amazon Bedrock | Google Vertex AI |
|---------|-------------------|-----------------|-----------------|
| **Authentication** | ANTHROPIC_API_KEY | AWS IAM roles + Cognito | GCP service accounts + OAuth |
| **Network isolation** | Internet (TLS) | VPC endpoint + PrivateLink | VPC Service Controls |
| **Data residency** | Anthropic infrastructure | Your AWS account + region | Your GCP project + region |
| **Anthropic access to data** | Logging per retention policy | None — your VPC | None — your GCP project |
| **Compliance certs** | SOC 2 Type II | HIPAA, SOC 2, FedRAMP | HIPAA, SOC 2, ISO 27001 |
| **Cost model** | Per-token billing | Per-token + Bedrock inference markup | Per-token + Vertex markup |
| **Prompt caching** | Full support | Full support | Full support |
| **Batch API** | Yes | Yes (Batch Inference) | Yes (Batch predictions) |
| **Extended thinking** | Yes | Yes (beta headers) | Yes (beta headers) |
| **Rate limits** | Anthropic tiers | Bedrock service quotas | Vertex quotas |
| **Best for** | Startups, speed to market | AWS-native enterprise | GCP-native enterprise |

### Bedrock SDK Pattern — Python

```python
import boto3, json

bedrock = boto3.client('bedrock-runtime', region_name='us-east-1')

response = bedrock.invoke_model(
    modelId='anthropic.claude-sonnet-4-6-20251101-v1:0',
    body=json.dumps({
        'anthropic_version': 'bedrock-2023-05-31',
        'max_tokens': 1024,
        'messages': [{'role': 'user', 'content': 'Hello from Bedrock'}]
    })
)

result = json.loads(response['body'].read())
print(result['content'][0]['text'])
```

## 1.10 CCA-F Certification Pathway

The Claude Certified Architect — Foundations (CCA-F) is Anthropic's official certification for practitioners who design and build production Claude applications. It was launched in late 2025 through Anthropic Academy on the Skilljar platform.

| Parameter | Value |
|-----------|-------|
| **Exam Code** | CCA-F |
| **Questions** | 60 multiple-choice |
| **Duration** | 120 minutes |
| **Passing Score** | 720 / 1,000 (approximately 72% — weighted by domain) |
| **Proctoring** | Online via Skilljar — webcam + screen share required |
| **Retake Policy** | 14-day waiting period after a failed attempt |
| **Validity** | 2 years from pass date |
| **Prerequisites (recommended)** | 3–6 months hands-on Claude development experience |
| **Target Candidate** | Solution architect designing/shipping production Claude applications |
| **Platform** | anthropic.skilljar.com — Anthropic Academy |

### Exam Domain Weights — Know These Cold

| Domain | Topic | Weight | Study Strategy |
|--------|-------|--------|-----------------|
| **Domain 1** | Claude API & SDK Integration | 22% | Priority 1 — most questions; master Messages API, streaming, tool use, caching |
| **Domain 2** | Prompt Engineering & Optimization | 20% | Priority 2 — XML tags, few-shot, chain-of-thought, extended thinking, RAG |
| **Domain 3** | Model Context Protocol (MCP) | 18% | Priority 3 — hardest for most; tools/resources/prompts primitives, transport |
| **Domain 4** | Agent Design & Orchestration | 22% | Priority 1 — tied with Domain 1; CLAUDE.md, Skills, Subagents, multi-agent |
| **Domain 5** | Safety, Security & Responsible Deployment | 18% | Priority 3 — frequently underestimated; hard limits, privacy, hardening, RSP |

### Recommended Skilljar Course Completion Order

| # | Course | Level | Why It Matters |
|---|--------|-------|-----------------|
| 1 | Claude 101 | Beginner | Start here — core features, projects, file uploads, everyday Claude usage |
| 2 | Building with the Claude API | Intermediate | Most important course — covers full API from auth to agents |
| 3 | Claude in Amazon Bedrock | Intermediate | AWS-specific deployment, IAM, VPC, RAG on Bedrock |
| 4 | Introduction to Model Context Protocol | Intermediate | Three MCP primitives, Python SDK, MCP Inspector |
| 5 | MCP: Advanced Topics | Advanced | Sampling, transport layers, roots, production scaling |
| 6 | Claude Code in Action | Intermediate | Agentic coding, CLAUDE.md, GitHub workflows, thinking modes |
| 7 | Introduction to Agent Skills | Intermediate | SKILL.md frontmatter, description writing, distribution |
| 8 | Introduction to Subagents | Intermediate | Isolated contexts, delegation, structured outputs, limits |
