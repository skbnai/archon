---
title: "AgentCore Memory — Gaps, Extensions & 2026 Research"
doc_type: guide
domain: platforms
status: current
topic_id: agentcore-memory-gaps-extensions-2026
last_reviewed: 2026-07-27
maturity: practitioner
supersedes:
  - docs/cloud-platforms/aws/AgentCore_Memory_Gaps_Extensions_2026.md
tags:
  - aws
  - bedrock
  - agentcore
  - strands
  - memory
covers_version: "N/A"
---

# AgentCore Memory — Gaps, Extensions & 2026 Research

FileSessionManager · Conversation Managers · Custom Strategy Wiring · Structured Extraction · Graph Memory · Emerging Research 2025-2026

This supplement fills gaps left by the main AWS AgentCore Memory Architecture Guide: the Strands SDK's own lightweight session-persistence layer (distinct from AgentCore Memory), the built-in conversation managers that trim message history, and the infrastructure required to wire a custom extraction strategy.

| Topic | Coverage in This Document |
| --- | --- |
| FileSessionManager | When to use, backends, vs AgentCore Memory, wiring code |
| Conversation Managers | Sliding window, summarising, null — config & prompt customisation |
| Custom Strategy Wiring | Built-in overrides, self-managed Lambda pipeline, SNS/S3 trigger |
| Structured Extraction | Entity schema, Pydantic wiring, prompt changes, namespace design |
| Graph Memory | Graphiti/Zep, MAGMA, integration patterns with AgentCore |
| 2025-2026 Research | MemOS, Nemori, sleep-time compute, MAGMA, HyperGraphRAG, Hindsight |

*Supplement to: AWS AgentCore Memory Architecture Guide v2.0 (April 2026)*

## 1. FileSessionManager — The Missing Chapter

### 1.1 What the Source Document Omitted

The Architecture Guide covers AgentCore Memory exhaustively but makes no mention of the Strands SDK's own built-in session persistence layer: **FileSessionManager** and **S3SessionManager**. These are *not* the same as AgentCore Memory. They are lighter-weight mechanisms that persist the raw conversation message list to disk or S3 so an agent can resume exactly where it left off after a process restart, without incurring any AgentCore API costs.

### 1.2 Decision Matrix — FileSessionManager vs AgentCore Memory

| Criterion | FileSessionManager / S3SessionManager | AgentCore Memory |
| --- | --- | --- |
| What is stored | Full raw message list (JSON files per message) | Events → extracted long-term memories (vector store) |
| Retrieval | Chronological replay — all messages restored | Semantic search — top-K relevant memories |
| Cost | Storage cost only (negligible / S3 prices) | Per API call + storage + consolidation job |
| Latency | Local: &lt;5 ms, S3: ~50 ms cold | ~200 ms p99 (semantic search) |
| Extraction / Summarisation | None — raw turns only | Yes — managed or custom strategy |
| Cross-session intelligence | No — same session ID required | Yes — actor_id links sessions |
| GDPR compliance burden | Operator-owned encryption + lifecycle | Managed; CMK; erasure API built-in |
| Best for | Local dev, PoC, single-user resumption after restart | Production; personalisation; multi-session continuity |
| Conflict with AgentCore? | Can be used together — orthogonal layers | N/A |

### 1.3 When to Use FileSessionManager

**Use FileSessionManager when:** (1) You want zero infrastructure and zero API cost for conversation continuity. (2) Your use case is a single-user CLI tool, desktop app, or developer workflow where a session must resume after a restart but cross-session semantic recall is not required. (3) You are building a Proof-of-Concept and want to iterate quickly without provisioning AgentCore. (4) You run **BidiAgent** (bidirectional streaming / voice) — FileSessionManager handles the reconnect-after-timeout pattern natively for that agent class.

**Do NOT use FileSessionManager as a substitute for AgentCore Memory when:** You need semantic search over historical context, user preference extraction, GDPR right-to-erasure by actor_id, multi-session recall across days or weeks, or multi-agent shared memory.

### 1.4 Backends Available

| Backend | Import | Storage Path | When to Use |
| --- | --- | --- | --- |
| FileSessionManager | `strands.session.file_session_manager` | `./sessions/` (default: `/tmp/strands/sessions`) | Local dev, PoC, desktop agents |
| S3SessionManager | `strands.session.s3_session_manager` | `s3://bucket/prefix/session_<id>/` | Production; serverless Lambda agents |
| RepositorySessionManager | `strands.session.repository_session_manager` | Custom backend (DynamoDB, RDS, etc.) | Enterprise; custom compliance requirements |

### 1.5 Wiring Code — Key Patterns

#### Single agent (file backend):

```python
from strands import Agent
from strands.session.file_session_manager import FileSessionManager

session_manager = FileSessionManager(
    session_id='user-abc-123',
    storage_dir='./sessions'  # do NOT use /tmp in production
)
agent = Agent(
    agent_id='support_bot',        # REQUIRED when using session manager
    session_manager=session_manager,
    tools=[...]
)
```

#### Multi-agent constraint (critical):

```python
# WARNING: You CANNOT attach a session manager to individual agents inside
# a multi-agent graph or swarm. Only the ORCHESTRATOR should hold the
# session_manager. Sub-agents must be created without one.

# CORRECT
orchestrator = Agent(session_manager=session_manager, ...)
sub_agent_a = Agent(...)   # no session_manager
sub_agent_b = Agent(...)   # no session_manager
```

#### S3 backend (production):

```python
from strands.session.s3_session_manager import S3SessionManager

session_manager = S3SessionManager(
    session_id='user-abc-123',
    bucket='my-agent-sessions',
    prefix='sessions/',
    region='eu-central-1'
)
```

**Tip:** For EU banking deployments using S3SessionManager, apply S3 server-side encryption with CMK (SSE-KMS), enable versioning, and set a lifecycle rule to expire objects after your retention window. FileSessionManager has no built-in encryption — never use it with real PII.

## 2. Conversation Managers — Sliding Window, Summarising & Null

The Architecture Guide references "context compaction" and the ACON framework but does not explain the three built-in ConversationManagers in the Strands SDK. These are independent of AgentCore Memory and control how the in-memory message list is trimmed before each model call.

### 2.1 The Three Managers

| Manager | Default? | What It Does | When to Use |
| --- | --- | --- | --- |
| SlidingWindowConversationManager | YES | Keeps the last N messages. Drops oldest when `window_size` exceeded. Handles dangling message cleanup and overflow trimming. | Most agents. Simple, predictable, low overhead. |
| SummarizingConversationManager | No | Summarises the oldest (`summary_ratio`) fraction of history with an LLM call. Preserves `preserve_recent_messages` most recent turns verbatim. | Long advisory sessions, 1h+ conversations, wealth management agents. |
| NullConversationManager | No | Does nothing. Full history grows unbounded. | Short single-turn queries; testing; agents where full history is required and context budget is managed externally. |

### 2.2 SlidingWindowConversationManager — Full Config

```python
from strands.agent.conversation_manager import SlidingWindowConversationManager

agent = Agent(
    conversation_manager=SlidingWindowConversationManager(
        window_size=40,              # max messages to keep (default: varies by model)
        per_turn=True,                # apply trim before EVERY model call
        # per_turn=3                   # or apply every 3 model calls (reduces overhead)
        should_truncate_results=True  # truncate oversized tool results
    )
)
```

When sliding window alone is used with AgentCore Memory, the pattern is: AgentCore long-term memories (injected via `MemoryRetrievalHook` into the system prompt) survive the window trim because they live in the system prompt, not the message list. Only raw conversation turns are dropped. This is the preferred pattern for most production agents.

### 2.3 SummarizingConversationManager — Config & Prompt Customisation

```python
from strands.agent.conversation_manager import SummarizingConversationManager

BANKING_SUMMARY_PROMPT = '''You are summarising a financial advisory conversation.
Create a concise summary that:
- Preserves all stated financial goals, risk tolerance, and product preferences
- Retains specific amounts, account types, and regulatory mentions (MiFID II, GDPR)
- Omits pleasantries and conversational filler
- Flags any pending actions the client requested
Format as structured bullet points.'''

agent = Agent(
    conversation_manager=SummarizingConversationManager(
        summary_ratio=0.3,              # summarise oldest 30% when reducing
        preserve_recent_messages=10,     # always keep last 10 turns verbatim
        summary_prompt=BANKING_SUMMARY_PROMPT  # domain-specific prompt
    )
)
```

### 2.4 Interaction Matrix — Conversation Manager vs AgentCore Memory

| Combination | Behaviour | Recommended? |
| --- | --- | --- |
| SlidingWindow + AgentCore short-term | Raw turns trimmed in RAM; full event log persisted to AgentCore. No conflict. | YES — default production pattern |
| SlidingWindow + AgentCore long-term retrieval | Long-term memories injected into system prompt (survive window). Window trims raw turns only. | YES — best for relationship agents |
| Summarising + AgentCore SUMMARIZATION strategy | Double summarisation. AgentCore already summarises post-session. Redundant cost. | AVOID — pick one or the other |
| Summarising + AgentCore USER_PREFERENCE | Summariser may drop preference signals before AgentCore extraction fires. Risk of missed preferences. | CAUTION — lower `summary_ratio`; set AgentCore trigger earlier |
| Null + AgentCore Memory | Full history grows unbounded in RAM. AgentCore handles persistence. Works for short sessions. | Only for short sessions (&lt;50 turns) |

## 3. Custom Strategy Wiring — Built-in Overrides & Self-Managed Lambda

The Architecture Guide mentions "self-managed strategy Lambda" but does not explain the three-tier strategy system or the infrastructure wiring required. This section fills that gap.

### 3.1 Three Strategy Tiers

| Tier | Who Runs Extraction | Customisation Level | Extra Infrastructure |
| --- | --- | --- | --- |
| Built-in | AgentCore service account (fully managed) | Zero — fixed algorithms | None |
| Built-in Override (Custom Prompt) | AgentCore service account; your prompt appended | Medium — prompt append only; model choice | Bedrock model access in your account |
| Self-Managed | Your Lambda / pipeline (you own everything) | Full — any model, any schema, any logic | S3 bucket + SNS topic + IAM role + Lambda |

### 3.2 Built-in Override — Prompt Customisation (No Lambda Needed)

Built-in overrides let you append domain-specific instructions to AgentCore's managed extraction prompt. This is the right choice when the built-in schema (fact / preference / summary) is sufficient but the extraction misses domain terms.

```python
import boto3
client = boto3.client('bedrock-agentcore-control')

client.update_memory(
    memoryId='my-banking-memory',
    memoryStrategies=[
        {
            'semanticMemoryStrategy': {
                'name': 'BankingSemanticMemory',
                'configuration': {
                    'semanticOverrideConfiguration': {
                        'extractionConfiguration': {
                            'appendToPrompt': '''
Pay special attention to:
- Financial products: ISAs, SIPPs, GIAs, bonds, ETFs
- Risk appetite: cautious, balanced, adventurous
- Regulatory signals: MiFID II suitability, KYC flags
- Life events: retirement horizon, inheritance, divorce
Extract these as facts even if expressed informally.
''',
                            'modelId': 'anthropic.claude-sonnet-4-5'
                        }
                    }
                }
            }
        }
    ]
)
```

### 3.3 Self-Managed Strategy — Full Infrastructure Wiring

#### Required infrastructure (Terraform / CDK):

| Resource | Purpose | Key Config |
| --- | --- | --- |
| S3 bucket (payload delivery) | AgentCore drops batched event payloads here as JSON | Lifecycle: delete after 7 days; SSE-KMS |
| SNS topic (notification) | AgentCore publishes job-start notification | FIFO if ordering matters; SQS subscription for Lambda |
| IAM role (AgentCore trust) | AgentCore assumes this role to write S3 + publish SNS | Trust: `bedrock-agentcore.amazonaws.com` |
| Lambda function (extractor) | Your custom extraction + consolidation logic | Timeout: 5 min; mem: 1 GB; VPC if needed |
| EventBridge / SQS (trigger) | Routes SNS notification to Lambda | DLQ mandatory; retry=2; visibility 300s |

#### Self-managed trigger configuration in CreateMemory:

```python
client.create_memory(
    name='banking-self-managed',
    memoryStrategies=[
        {
            'customMemoryStrategy': {
                'name': 'FinancialEntityExtractor',
                'configuration': {
                    'customConfiguration': {
                        'lambdaArn': 'arn:aws:lambda:eu-central-1:123:function:extractor',
                        'triggerConfiguration': {
                            'messageCountThreshold': 10,   # trigger after 10 events
                            'idleTimeoutSeconds': 1800,     # or 30 min idle
                            'tokenCountThreshold': 4000     # or 4K tokens
                        },
                        'deliveryConfiguration': {
                            's3BucketName': 'my-payload-bucket',
                            'snsTopicArn': 'arn:aws:sns:eu-central-1:123:memory-jobs'
                        }
                    }
                }
            }
        }
    ]
)
```

**See [Part 2](./parts/16-agentcore-memory-gaps-extensions-2026-part2.md)** for advanced memory patterns: structured extraction schema design, graph memory (Graphiti/MAGMA), the 2025-2026 research landscape, and a consolidated memory-layer decision guide.
