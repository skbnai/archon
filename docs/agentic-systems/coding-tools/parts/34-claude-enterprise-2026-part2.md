---
title: Claude Enterprise Deployment 2026 — Part 2
domain: agentic-systems
status: current
doc_type: guide
topic_id: claude-enterprise-2026-part2
date_published: 2026-07-24
last_reviewed: 2026-07-24
supersedes: []
---

**[Back to Part 1 ←](pathname:///archon/agentic-systems/coding-tools/34-claude-enterprise-2026)** | **[Continue to Part 3 →](pathname:///archon/agentic-systems/coding-tools/parts/34-claude-enterprise-2026-part3)**

---

## 6. Claude Enterprise Plan

### 6.1 Admin Console Features

The Claude Enterprise admin console (`console.anthropic.com`) provides:

| Feature | Description |
| --------- | ------------- |
| Usage analytics | Request volume, token consumption, cost by model and team |
| Model-level entitlements | Grant or restrict specific models per user group |
| Spend alerts | Configurable alerts at percentage thresholds (50%, 80%, 100%) |
| Per-team cost attribution | Track spend by team, project, or cost centre |
| Productivity trends | Output volume over time for teams and individuals |
| Audit log export | Full request/response logs for SIEM ingestion |

### 6.2 Model-Level Access Controls

```json
{
  "entitlements": {
    "engineering": {
      "models": ["claude-sonnet-4-6", "claude-haiku-4-5", "claude-opus-4-8"],
      "max_tokens_per_request": 100000,
      "monthly_token_budget": 50000000
    },
    "support": {
      "models": ["claude-haiku-4-5"],
      "max_tokens_per_request": 8192,
      "monthly_token_budget": 5000000
    },
    "executives": {
      "models": ["claude-sonnet-4-6"],
      "max_tokens_per_request": 32768,
      "monthly_token_budget": 10000000
    }
  }
}
```

### 6.3 SSO / SAML Integration

Claude Enterprise supports SAML 2.0 and OIDC for single sign-on:

- **Okta**: Native SAML app available in Okta Integration Network
- **Azure AD**: Enterprise app with SAML federation
- **Google Workspace**: SAML application with group-based provisioning
- **JIT provisioning**: Users provisioned on first login with role from IdP attributes
- **SCIM**: Automated deprovisioning when user is offboarded from IdP

### 6.4 Audit Logs

Audit logs capture every interaction at the message level:

```json
{
  "timestamp": "2026-07-04T10:23:45.123Z",
  "event_type": "message.create",
  "user_id": "user_abc123",
  "team_id": "engineering",
  "model": "claude-sonnet-4-6-20250514",
  "input_tokens": 1247,
  "output_tokens": 823,
  "cost_usd": 0.016,
  "session_id": "sess_xyz789",
  "ip_address": "10.0.1.45",
  "request_id": "req_def456"
}
```

Export audit logs to SIEM:

```bash
# Export via API (Enterprise plan)
curl -H "Authorization: Bearer $ANTHROPIC_ADMIN_KEY" \
  "https://api.anthropic.com/v1/admin/audit-logs?start=2026-07-01&end=2026-07-04&format=jsonl" \
  -o audit-2026-07-01-to-07-04.jsonl
```

---

## 7. Managed Agents in Enterprise

Managed Agents are Anthropic-hosted agentic deployments available in the Enterprise plan. They differ from self-built agents: Anthropic handles infrastructure, scaling, and runtime; you configure behaviour via a management API.

### 7.1 Scheduled Deployments

```python
import anthropic

client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

# Create a scheduled agent that runs nightly
scheduled_agent = client.managed_agents.create(
    name="nightly-report-agent",
    model="claude-sonnet-4-6-20250514",
    schedule="0 2 * * *",  # Cron: 2 AM UTC daily
    system_prompt="""
    You are a data analyst. Each night you:
    1. Query the reports API for yesterday's metrics
    2. Generate an executive summary
    3. Post the summary to Slack #exec-reports
    """,
    tools=[
        {"type": "mcp", "server": "reports-api"},
        {"type": "mcp", "server": "slack"}
    ],
    hitl_policy={
        "mode": "HOTL",         # Human On The Loop — monitor, can intervene
        "alert_channel": "slack://alerts-channel",
        "escalation_threshold": "error"
    }
)

print(f"Agent created: {scheduled_agent.id}")
```

### 7.2 Self-Hosted Sandboxes

For sensitive workloads, Managed Agents support deployment into customer-controlled sandboxes:

```yaml
# managed-agent-sandbox.yaml
apiVersion: anthropic.com/v1
kind: ManagedAgentSandbox
metadata:
  name: secure-code-executor
spec:
  deployment_target:
    type: self_hosted
    endpoint: https://sandbox.internal.company.com/agents
    auth:
      type: mTLS
      cert_secret: sandbox-tls-cert
  agent:
    model: claude-sonnet-4-6-20250514
    max_tokens: 32768
    timeout_seconds: 300
  isolation:
    network: none       # No outbound network
    filesystem: ephemeral
    max_memory_mb: 2048
  governance:
    audit_log: true
    hitl_required: ["file_write", "process_exec"]
```

### 7.3 Governance for Managed Agents

| Control | Description |
| --------- | ------------- |
| Action whitelists | Define which tool calls agents are permitted to make |
| Pre-approval gates | Certain action types require human approval before execution |
| Budget limits | Per-agent token and cost limits with automatic shutdown |
| Rollback capability | Agents can be paused, rolled back to prior configuration |
| Audit trail | Every agent action logged with full context |
| Alert routing | Anomalous behaviour triggers alerts to on-call channels |

---

## 8. Security Architecture

### 8.1 Data Flow and Isolation

The following flow illustrates how data flows through Claude API deployments without persisting in training pipelines:

1. **User / Application** initiates request with HTTPS / TLS 1.3 encryption
2. **Platform Perimeter** (VPC Endpoint / VPC-SC / Private Endpoint) authenticates and routes the request
3. **Claude API / Cloud Platform** processes the request through ephemeral containers
   - Request processing occurs in isolated, short-lived compute
   - Response generation completes without intermediate persistence
   - Audit logs are written to encrypted, append-only storage
4. **Model Training Pipeline** never receives customer API data — this data is excluded from training regardless of plan tier

This isolation ensures customer data remains confidential and is not used to improve models.

### 8.2 Encryption

| Layer | Mechanism |
| ------- | ----------- |
| In transit | TLS 1.3 minimum; ECDHE key exchange |
| At rest (API logs) | AES-256; Anthropic-managed keys by default |
| At rest (Bedrock) | AWS KMS; customer-managed keys (CMK) available |
| At rest (Vertex AI) | Google Cloud KMS; CMEK supported |
| At rest (Azure) | Azure Key Vault; CMK available |

### 8.3 API Key Management

```python
# Never hardcode API keys — use secret managers
import boto3
import json
import anthropic

def get_client() -> anthropic.Anthropic:
    """Fetch API key from AWS Secrets Manager at runtime."""
    sm = boto3.client("secretsmanager", region_name="us-east-1")
    secret = sm.get_secret_value(SecretId="prod/anthropic/api-key")
    api_key = json.loads(secret["SecretString"])["api_key"]
    return anthropic.Anthropic(api_key=api_key)

# For Kubernetes: use External Secrets Operator
# For Azure: use Key Vault References in App Service
# For GCP: use Secret Manager with Workload Identity
```

Key rotation policy:

- Rotate API keys every 90 days
- Use Secrets Manager rotation Lambda for automated rotation
- Immediately revoke compromised keys via `console.anthropic.com` → API Keys

### 8.4 No Training on Customer API Data

Anthropic does not use data sent through the API to train models. This applies to:

- All plans (Free, Pro, Team, Enterprise)
- All cloud platforms (direct API, Bedrock, Vertex AI, Azure)
- Both prompt/completion data

Confirm this in writing: request the current Data Processing Agreement (DPA) from your account team.

---

## 9. Compliance Framework

### 9.1 SOC 2 Type II

Anthropic holds SOC 2 Type II certification covering security, availability, and confidentiality.

**Enterprise obligations:**

- Request the Anthropic SOC 2 report via your account team (sign NDA required)
- Include Claude API endpoints in your own SOC 2 audit scope
- Document data flows: what user data enters the API, what categories of data
- Assess Anthropic as a sub-processor in your vendor risk management program

### 9.2 GDPR

GDPR requirements when using Claude in EU contexts:

```python
# Correct Presidio import and PII anonymisation before API calls
from presidio_analyzer import AnalyzerEngine          # correct import
from presidio_anonymizer import AnonymizerEngine

def anonymize_prompt(text: str) -> str:
    """Strip PII from text before sending to Claude API."""
    analyzer = AnalyzerEngine()
    results = analyzer.analyze(
        text=text,
        language="en",
        entities=["PERSON", "EMAIL_ADDRESS", "PHONE_NUMBER",
                  "CREDIT_CARD", "IP_ADDRESS", "LOCATION"]
    )
    anonymized = AnonymizerEngine().anonymize(
        text=text,
        analyzer_results=results
    )
    return anonymized.text

# Usage
safe_prompt = anonymize_prompt(raw_user_message)
response = client.messages.create(
    model="claude-sonnet-4-6-20250514",
    max_tokens=4096,
    messages=[{"role": "user", "content": safe_prompt}]
)
```

GDPR operational requirements:

| Requirement | Implementation |
| ------------- | --------------- |
| Data processing agreement | Request DPA from Anthropic account team |
| Data subject rights | Log which prompts contain personal data; implement deletion workflows |
| Purpose limitation | System prompt should state the processing purpose |
| Data minimisation | Strip unnecessary personal data before API calls (Presidio above) |
| Breach notification | Include Anthropic in your 72-hour breach notification chain |
| Cross-border transfers | Verify Standard Contractual Clauses (SCCs) are in DPA |

### 9.3 HIPAA

HIPAA-eligible deployments:

- Requires a Business Associate Agreement (BAA) with Anthropic — contact sales (Enterprise plan)
- Without a BAA, do **not** send Protected Health Information (PHI) through the API
- AWS Bedrock within a HIPAA-eligible AWS account adds AWS's HIPAA controls
- Recommended architecture: PHI anonymised before Claude; Claude processes de-identified data only

```python
import re

# Minimal PHI de-identification before Claude
PHI_PATTERNS = {
    "MRN": r"\bMRN[:\s]*\d{6,10}\b",
    "DOB": r"\b\d{2}/\d{2}/\d{4}\b",
    "SSN": r"\b\d{3}-\d{2}-\d{4}\b",
    "NPI": r"\bNPI[:\s]*\d{10}\b"
}

def deidentify(text: str) -> str:
    for label, pattern in PHI_PATTERNS.items():
        text = re.sub(pattern, f"[{label}]", text)
    return text
```

### 9.4 ISO 27001 and ISO 42001

- **ISO 27001**: Anthropic's information security management system alignment; request security questionnaire responses from account team
- **ISO 42001**: AI management system standard — use Anthropic's model cards and safety documentation as evidence for your own ISO 42001 certification

### 9.5 FedRAMP

- Direct Anthropic API is not currently FedRAMP authorized
- AWS Bedrock in `us-gov-west-1` and `us-gov-east-1` may be available; verify current availability in the Bedrock console under Government regions
- For FedRAMP High workloads, assess whether Bedrock's FedRAMP boundary covers Claude model invocations in the current authorization scope

---

## 10. Cost Governance

### 10.1 Spend Alerts and Budgets

```python
# Application-level budget enforcement
import anthropic
from dataclasses import dataclass

@dataclass
class BudgetConfig:
    team_id: str
    monthly_limit_usd: float
    alert_at_pct: float = 0.80  # Alert at 80% of budget

class BudgetedClient:
    def __init__(self, config: BudgetConfig):
        self.config = config
        self.client = anthropic.Anthropic()

    async def create_message(self, **kwargs) -> anthropic.types.Message:
        spent = await get_monthly_spend(self.config.team_id)
        budget = self.config.monthly_limit_usd

        if spent >= budget:
            raise BudgetExceededError(
                f"Team {self.config.team_id}: monthly budget of ${budget:.2f} exhausted"
            )

        if spent >= budget * self.config.alert_at_pct:
            await send_alert(
                f"Team {self.config.team_id} at {spent/budget*100:.0f}% of monthly budget"
            )

        response = self.client.messages.create(**kwargs)

        cost = estimate_cost(response.usage, kwargs.get("model", ""))
        await record_spend(self.config.team_id, cost)
        return response

def estimate_cost(usage: anthropic.types.Usage, model: str) -> float:
    """Approximate cost from token counts. Verify against current pricing."""
    # Example rates — update from console.anthropic.com
    rates = {
        "claude-sonnet-4-6": {"input": 3.00, "output": 15.00},
        "claude-haiku-4-5":  {"input": 1.00, "output":  5.00},
        "claude-opus-4-8":   {"input": 5.00, "output": 25.00},
    }
    for key, rate in rates.items():
        if key in model:
            return (
                usage.input_tokens  * rate["input"]  / 1_000_000 +
                usage.output_tokens * rate["output"] / 1_000_000
            )
    return 0.0
```

### 10.2 Per-Team Cost Attribution

Tag every API call with cost-centre metadata:

```python
response = client.messages.create(
    model="claude-sonnet-4-6-20250514",
    max_tokens=4096,
    metadata={
        "user_id": user.id,
        "team_id": team.id,
        "cost_centre": team.cost_centre_code,  # e.g. "ENG-PLATFORM"
        "project_id": project.id,
        "environment": "production"
    },
    messages=[...]
)
```

Export and aggregate in BI tooling:

```sql
-- Example: daily cost by team from exported audit logs
SELECT
    team_id,
    SUM(cost_usd) AS daily_cost,
    SUM(input_tokens) AS input_tokens,
    SUM(output_tokens) AS output_tokens,
    COUNT(*) AS requests
FROM audit_logs
WHERE date = CURRENT_DATE - 1
GROUP BY team_id
ORDER BY daily_cost DESC;
```

### 10.3 Token Quota Management

```python
# Redis-backed per-team token quota
import redis
import time

r = redis.Redis(host="redis", port=6379, decode_responses=True)

DAILY_LIMITS = {
    "engineering":   50_000_000,
    "support":        5_000_000,
    "analytics":     20_000_000,
}

def check_token_quota(team_id: str, estimated_tokens: int) -> None:
    today = time.strftime("%Y-%m-%d")
    key = f"quota:{team_id}:{today}"

    pipe = r.pipeline()
    pipe.incrby(key, estimated_tokens)
    pipe.expire(key, 86400)  # TTL = 1 day
    results = pipe.execute()

    used = results[0]
    limit = DAILY_LIMITS.get(team_id, 1_000_000)
    if used > limit:
        raise QuotaExceededError(
            f"Team {team_id}: daily token quota of {limit:,} exceeded"
        )
```

### 10.4 Batch API for Non-Real-Time Workloads

For overnight processing, analytics, and evaluation runs, the Batch API provides 50% cost reduction:

```python
import anthropic

client = anthropic.Anthropic()

# Submit a batch of 1,000 document summaries
requests = [
    {
        "custom_id": f"doc-{i}",
        "params": {
            "model": "claude-haiku-4-5-20250714",  # Use Haiku for batch cost efficiency
            "max_tokens": 500,
            "messages": [
                {"role": "user", "content": f"Summarise in 3 sentences: {doc}"}
            ]
        }
    }
    for i, doc in enumerate(documents)
]

batch = client.messages.batches.create(requests=requests)
print(f"Batch submitted: {batch.id} — check status at {batch.request_counts}")

# Poll until complete (typical: < 1 hour, SLA: 24 hours)
import time
while True:
    status = client.messages.batches.retrieve(batch.id)
    if status.processing_status == "ended":
        break
    time.sleep(60)

# Retrieve results
for result in client.messages.batches.results(batch.id):
    if result.result.type == "succeeded":
        print(f"{result.custom_id}: {result.result.message.content[0].text}")
```

### 10.5 Model Routing for Cost Efficiency

```python
from enum import Enum

class TaskComplexity(Enum):
    SIMPLE = "simple"       # Classification, extraction, short Q&A
    STANDARD = "standard"   # Summarisation, code review, moderate reasoning
    COMPLEX = "complex"     # Architecture design, novel reasoning, long documents

def route_model(complexity: TaskComplexity) -> str:
    routing = {
        TaskComplexity.SIMPLE:   "claude-haiku-4-5-20250714",
        TaskComplexity.STANDARD: "claude-sonnet-4-6-20250514",
        TaskComplexity.COMPLEX:  "claude-opus-4-8-20251101",
    }
    return routing[complexity]

# Example classifier
def classify_task(prompt: str) -> TaskComplexity:
    word_count = len(prompt.split())
    if word_count < 50 and any(kw in prompt.lower() for kw in ["classify", "extract", "yes or no"]):
        return TaskComplexity.SIMPLE
    elif any(kw in prompt.lower() for kw in ["architect", "design system", "compare tradeoffs"]):
        return TaskComplexity.COMPLEX
    return TaskComplexity.STANDARD
```

---

**[Back to Part 1 ←](pathname:///archon/agentic-systems/coding-tools/34-claude-enterprise-2026)** | **[Continue to Part 3 →](pathname:///archon/agentic-systems/coding-tools/parts/34-claude-enterprise-2026-part3)**
