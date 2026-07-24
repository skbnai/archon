---
title: Claude Enterprise Deployment 2026
domain: agentic-systems
status: current
doc_type: guide
topic_id: claude-enterprise-2026
date_published: 2026-07-24
last_reviewed: 2026-07-24
supersedes:
  - docs/coding-tools/claude/claude-enterprise-2026.md
related_docs:
  - reliability-engineering
---

# Claude Enterprise Deployment 2026

Reference guide for enterprise architects and platform engineers deploying Claude at scale across cloud platforms, with comprehensive coverage of security, compliance, cost governance, guardrails, explainability, human-in-the-loop patterns, and responsible AI.

---

## 1. Deployment Options Overview

| Platform | Description | Auth | Billing | Best For |
| ---------- | ------------- | ------ | --------- | ---------- |
| **Claude API (Direct)** | Anthropic-hosted, direct access | Anthropic API keys | Anthropic invoices | Startups, developers, prototyping |
| **Claude Platform on AWS** | Anthropic-managed infrastructure on AWS; AWS billing and IAM auth | AWS IAM | AWS bill | Enterprises already on AWS, unified billing |
| **Amazon Bedrock** | AWS-managed service; Claude models alongside other foundation models | AWS IAM | AWS bill | AWS-native workloads, Bedrock Agents, Knowledge Bases |
| **Google Cloud Vertex AI** | GCP-managed; Model Garden access | GCP service accounts, ADC | GCP bill | GCP-native workloads, BigQuery integration, Vertex Pipelines |
| **Azure AI Foundry** | Azure Marketplace; Claude models via Azure cognitive services | Azure AD / Managed Identity | Azure bill | Microsoft 365 shops, Azure compliance frameworks |

:::tip Choosing a platform
    If your data is already in AWS (S3, RDS, Redshift), prefer Bedrock or Claude Platform on AWS for minimal egress and unified IAM. If you need EU data residency with minimal config, Vertex AI EU regions or Azure EU regions are the simplest path. For Microsoft 365 shops needing Conditional Access Policies and Purview integration, Azure AI Foundry is the natural fit.

---

## 2. Claude Platform on AWS

Announced in 2026, Claude Platform on AWS places Anthropic-managed infrastructure within AWS, delivering the full Claude API surface through AWS billing and IAM authentication. This differs from Bedrock: Bedrock is an AWS-managed service with AWS's abstraction layer; Claude Platform on AWS is Anthropic's own infrastructure accessed via AWS identity primitives.

### 2.1 Supported APIs

Claude Platform on AWS exposes the complete Anthropic API:

| API | Description |
| ----- | ------------- |
| Messages API | Core conversational and reasoning API |
| Files API | Upload once, reference by `file_id` across requests |
| Batch API | Async batch processing at 50% discount |
| Managed Agents | Scheduled agent deployments with durable state |
| Agent Skills | Modular skill packages for common agent tasks |
| Code Execution | Sandboxed code running for agent workflows |
| Tool Use | Structured tool calling with JSON schemas |

### 2.2 IAM Authentication

```python
import boto3
import anthropic

# Claude Platform on AWS uses AWS STS for token exchange
def get_claude_platform_client():
    sts = boto3.client("sts")
    # Exchange AWS credentials for a short-lived Claude Platform token
    assumed = sts.assume_role(
        RoleArn="arn:aws:iam::123456789012:role/ClaudePlatformRole",
        RoleSessionName="ClaudeSession"
    )
    creds = assumed["Credentials"]

    client = anthropic.Anthropic(
        # Claude Platform on AWS endpoint
        base_url="https://api.claude-platform.aws.anthropic.com",
        api_key=creds["SessionToken"],  # STS session token
    )
    return client

client = get_claude_platform_client()
response = client.messages.create(
    model="claude-sonnet-4-6-20250514",
    max_tokens=4096,
    messages=[{"role": "user", "content": "Analyse this architecture."}]
)
```

### 2.3 Billing Integration

- All Claude Platform on AWS usage appears on your AWS bill under the `anthropic` service namespace
- Standard AWS Cost Explorer tags (`CostCenter`, `Project`, `Team`) flow through
- Consolidated billing across AWS Organization accounts is supported
- AWS Budgets can trigger alerts at configurable thresholds

---

**This is Part 1 of 3. [Continue with Part 2 →](pathname:///archon/agentic-systems/coding-tools/parts/34-claude-enterprise-2026-part2) for Claude Enterprise Plan, Managed Agents, Security, and Compliance. [See Part 3 →](pathname:///archon/agentic-systems/coding-tools/parts/34-claude-enterprise-2026-part3) for Guardrails, Explainability, Responsible AI, and Deployment Checklists.**
