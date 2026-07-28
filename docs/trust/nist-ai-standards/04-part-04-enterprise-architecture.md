---
title: "NIST AI Standards — Enterprise Architecture & Cloud Implementation"
doc_type: reference-architecture
domain: trust
status: current
topic_id: part-04-enterprise-architecture
last_reviewed: 2026-07-28
maturity: practitioner
supersedes: [docs/nist-ai-standards/part-04-enterprise-architecture.md]
tags: [enterprise-architecture, aws, azure, gcp, cloud-native, nist, implementation]
covers_version: "as of 2026"
---

**Audience:** Enterprise architect, cloud architect, security engineer.

## Enterprise AI Security Architecture Framework

```mermaid
flowchart TB
    subgraph GOV["Governance Layer"]
        G1["AI RMF: GOVERN-MAP-MEASURE-MANAGE cycle"]
        G2["ISO 42001 AI Management System"]
        G3["EU AI Act compliance controls"]
        G4["CISO-owned AI Risk Register"]
    end
    subgraph TRUST["Trust and Identity Layer"]
        T1["Workload Identity: SPIFFE/SPIRE or Cloud IAM"]
        T2["Cryptographic agent identity: mTLS, signed messages"]
        T3["Authorization chains: human to orchestrator to agent"]
        T4["Model registry with signed model artifacts"]
    end
    subgraph RUNTIME["AI Runtime Layer"]
        R1["Model serving: Bedrock / Vertex AI / Azure AI / vLLM"]
        R2["Agent orchestration: LangGraph / AutoGen / Strands"]
        R3["Tool execution sandbox: OPA policy + rate limits"]
        R4["Guardrails: NeMo / LlamaGuard / custom"]
    end
    subgraph DATA["Data Layer"]
        D1["Training data governance: provenance, signing"]
        D2["Vector databases with access controls"]
        D3["PII redaction pipeline"]
        D4["Synthetic content detection pipeline"]
    end
    subgraph OBS["Observability Layer"]
        O1["LLM tracing: Langfuse / Arize Phoenix"]
        O2["Adversarial input monitoring"]
        O3["Model behavior drift detection"]
        O4["Immutable, tamper-evident audit trail"]
    end
    GOV --> TRUST --> RUNTIME --> DATA --> OBS
```
*A five-layer reference architecture spanning NIST AI 100-1, AI 100-2, AI 100-4, and CAISI: governance decisions flow down to identity/trust, runtime, data, and observability controls.*

## AWS Implementation

Least-privilege IAM roles per agent type (CAISI), Bedrock Guardrails for prompt-injection and PII filtering (AI 100-2/100-4), invocation logging, WORM-protected training data, and drift-detection alarms:

```hcl
# AWS AI Security Foundation — Terraform
# Implements NIST AI 100-2, AI 100-4, CAISI controls

# --- IDENTITY AND ACCESS ---
resource "aws_iam_role" "ai_agent" {
  for_each = var.agent_types  # "triage", "investigation", "ir"
  name = "ai-agent-${each.key}-role"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{ Effect = "Allow", Principal = { Service = "bedrock.amazonaws.com" },
      Action = "sts:AssumeRole" }]
  })
}

# Triage agent — read-only Bedrock + CloudWatch, explicit deny on write/admin
resource "aws_iam_role_policy" "triage_read_only" {
  name = "triage-agent-read-only"
  role = aws_iam_role.ai_agent["triage"].id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      { Effect = "Allow", Action = ["bedrock:InvokeModel", "bedrock:InvokeModelWithResponseStream"],
        Resource = "arn:aws:bedrock:*::foundation-model/anthropic.claude-*" },
      { Effect = "Allow", Action = ["logs:FilterLogEvents", "logs:GetLogEvents"], Resource = "*",
        Condition = { StringEquals = { "aws:RequestedRegion" = var.regions } } },
      { Effect = "Deny", Action = ["ec2:*", "iam:*", "s3:DeleteObject", "s3:PutObject"], Resource = "*" }
    ]
  })
}

# --- MODEL SECURITY ---
resource "aws_bedrock_model_invocation_logging_configuration" "ai_security_logging" {
  logging_config {
    embedding_data_delivery_enabled = true
    image_data_delivery_enabled     = true
    text_data_delivery_enabled      = true
    s3_config { bucket_name = aws_s3_bucket.ai_audit_logs.id, key_prefix = "bedrock-invocations/" }
    cloudwatch_config { log_group_name = aws_cloudwatch_log_group.ai_invocations.name
      role_arn = aws_iam_role.bedrock_logging.arn }
  }
}

# Guardrails (AI 100-2 mitigation: input/output filtering)
resource "aws_bedrock_guardrail" "ai_security_guardrail" {
  name = "ai-security-guardrail-prod"
  blocked_input_messaging   = "Your input has been flagged as potentially malicious."
  blocked_outputs_messaging = "The AI's response has been filtered for safety."

  sensitive_information_policy_config {
    regexes_config {
      name = "PromptInjectionPatterns"
      pattern = "(ignore|disregard).{0,20}(previous|instruction|prompt)"
      action = "BLOCK"
    }
  }
  # PII protection (AI 100-4 control)
  sensitive_information_policy_config {
    pii_entities_config { type = "EMAIL", action = "ANONYMIZE" }
    pii_entities_config { type = "PHONE", action = "ANONYMIZE" }
    pii_entities_config { type = "US_SOCIAL_SECURITY_NUMBER", action = "BLOCK" }
  }
}

# --- TRAINING DATA PROTECTION ---
resource "aws_s3_bucket" "ai_training_data" { bucket = "ai-training-data-${var.account_id}" }
resource "aws_s3_bucket_versioning" "training_data" {
  bucket = aws_s3_bucket.ai_training_data.id
  versioning_configuration { status = "Enabled" }
}
resource "aws_s3_bucket_server_side_encryption_configuration" "training_data" {
  bucket = aws_s3_bucket.ai_training_data.id
  rule { apply_server_side_encryption_by_default {
    sse_algorithm = "aws:kms", kms_master_key_id = aws_kms_key.ai_training_data.arn } }
}
# Object Lock: WORM for training data integrity
resource "aws_s3_bucket_object_lock_configuration" "training_data" {
  bucket = aws_s3_bucket.ai_training_data.id
  rule { default_retention { mode = "COMPLIANCE", days = 365 } }
}

# --- MONITORING AND DETECTION ---
resource "aws_cloudwatch_event_rule" "adversarial_input_detected" {
  name = "ai-adversarial-input-detected"
  event_pattern = jsonencode({ source = ["aws.bedrock"], detail-type = ["Guardrail Intervention"],
    detail = { action = ["BLOCKED"] } })
}
resource "aws_cloudwatch_event_target" "security_alert_adversarial" {
  rule = aws_cloudwatch_event_rule.adversarial_input_detected.name
  arn  = aws_sns_topic.security_alerts.arn
}
# Model behavior drift detection (AI 100-2)
resource "aws_cloudwatch_metric_alarm" "model_behavior_drift" {
  alarm_name = "ai-model-behavior-drift"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods = 5
  metric_name = "ModelAnomalyScore"
  namespace = "AI/SOC"
  period = 3600
  statistic = "Average"
  threshold = 0.15  # 15% anomaly rate triggers alert
  alarm_actions = [aws_sns_topic.security_alerts.arn]
}
```

## Azure Implementation

Private-network-only AI Foundry hosting, GPT-4o content filtering with jailbreak and indirect-attack detection, per-agent managed identity with deny-by-default write access, private endpoints, full request/response audit logging, and immutable (WORM) training data storage with customer-managed keys:

```hcl
# Azure AI Security Foundation — Terraform (NIST AI 100-2, 100-4, CAISI)

# --- AI FOUNDRY (Model Hosting) ---
resource "azurerm_ai_foundry_hub" "enterprise" {
  name = "enterprise-ai-hub-prod"
  location = var.location
  resource_group_name = var.resource_group_name
  sku = "Basic"
  identity { type = "SystemAssigned" }
  public_network_access_enabled = false  # Private network only
}

# --- CONTENT FILTERING (AI 100-4) ---
resource "azurerm_cognitive_deployment" "gpt4o_with_filter" {
  name = "gpt-4o-prod"
  cognitive_account_id = azurerm_cognitive_account.openai.id
  model { format = "OpenAI", name = "gpt-4o", version = "2024-08-06" }
  content_filter {
    hate     { input_action = "Block", output_action = "Block", threshold_level = "Low" }
    violence { input_action = "Block", output_action = "Block", threshold_level = "Low" }
    jailbreak        { input_action = "Block" }  # Prompt injection / jailbreak detection
    indirect_attack   { input_action = "Block" }  # Indirect prompt injection
    protected_material_text { output_action = "Block" }
  }
  sku { name = "Standard" }
}

# --- MANAGED IDENTITY FOR AGENTS (CAISI) ---
resource "azurerm_user_assigned_identity" "ai_agents" {
  for_each = toset(["triage", "investigation", "ir", "orchestrator"])
  name = "ai-agent-${each.key}-prod"
  resource_group_name = var.resource_group_name
  location = var.location
}
resource "azurerm_role_assignment" "triage_log_reader" {
  scope = azurerm_log_analytics_workspace.sentinel.id
  role_definition_name = "Log Analytics Reader"
  principal_id = azurerm_user_assigned_identity.ai_agents["triage"].principal_id
}
resource "azurerm_role_assignment" "triage_deny_write" {
  scope = var.subscription_scope
  role_definition_name = "Reader"  # Read-only at subscription level
  principal_id = azurerm_user_assigned_identity.ai_agents["triage"].principal_id
}

# --- PRIVATE ENDPOINTS (Data Isolation) ---
resource "azurerm_private_endpoint" "openai" {
  name = "pe-openai-prod"
  location = var.location
  resource_group_name = var.resource_group_name
  subnet_id = var.private_subnet_id
  private_service_connection {
    name = "openai-connection"
    private_connection_resource_id = azurerm_cognitive_account.openai.id
    is_manual_connection = false
    subresource_names = ["account"]
  }
}

# --- AI AUDIT LOGGING ---
resource "azurerm_monitor_diagnostic_setting" "openai_audit" {
  name = "openai-audit-logs"
  target_resource_id = azurerm_cognitive_account.openai.id
  log_analytics_workspace_id = azurerm_log_analytics_workspace.ai_audit.id
  enabled_log { category = "RequestResponse" }  # Log all AI requests and responses
  enabled_log { category = "Audit" }
  metric { category = "AllMetrics", enabled = true }
}

# --- TRAINING DATA INTEGRITY (AI 100-2) ---
resource "azurerm_storage_account" "ai_training_data" {
  name = "aitrainingdata${var.environment}"
  resource_group_name = var.resource_group_name
  location = var.location
  account_tier = "Standard"
  account_replication_type = "GRS"
  immutability_policy {
    state = "Locked"
    period_since_creation_in_days = 365
    allow_protected_append_writes = false  # True WORM
  }
  customer_managed_key {  # GDPR compliance
    key_vault_key_id = azurerm_key_vault_key.ai_training_cmk.id
    user_assigned_identity_id = azurerm_user_assigned_identity.ai_agents["orchestrator"].id
  }
}
```

## GCP Implementation

Vertex AI safety settings aligned to AI 100-4, VPC Service Controls restricting AI project egress to approved services and identities, and Cloud Armor rate limiting (model-extraction defense) plus injection-pattern blocking at the API edge:

```python
from google.cloud.aiplatform_v1beta1.types import SafetySetting, HarmCategory, HarmBlockThreshold

def configure_vertex_ai_with_safety():
    """Vertex AI Gemini safety filters aligned with NIST AI 100-4."""
    return [
        SafetySetting(category=HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
                       threshold=HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE),
        SafetySetting(category=HarmCategory.HARM_CATEGORY_HARASSMENT,
                       threshold=HarmBlockThreshold.BLOCK_LOW_AND_ABOVE),
    ]
```

```json
{
  "accessPolicies": [{
    "name": "accessPolicies/ai-security-policy",
    "title": "AI Security VPC-SC Policy",
    "scopes": ["projects/AI_PROJECT_ID"],
    "serviceRestrictions": {
      "allowedServices": ["aiplatform.googleapis.com", "storage.googleapis.com", "logging.googleapis.com"],
      "enableRestriction": true
    },
    "ingressPolicies": [{
      "ingressFrom": {
        "identities": ["serviceAccount:ai-orchestrator@PROJECT_ID.iam.gserviceaccount.com"],
        "sources": [{"resource": "projects/ALLOWED_PROJECTS"}]
      },
      "ingressTo": { "operations": [{"serviceName": "aiplatform.googleapis.com",
        "methodSelectors": [{"method": "predict"}]}] }
    }]
  }]
}
```

```hcl
# Cloud Armor security policy for AI API endpoints
resource "google_compute_security_policy" "ai_api_protection" {
  name = "ai-api-waf-policy"

  # Rate limiting (AI 100-2: model extraction defense)
  rule {
    action = "rate_based_ban"
    priority = 1000
    match { versioned_expr = "SRC_IPS_V1", config { src_ip_ranges = ["*"] } }
    rate_limit_options {
      rate_limit_threshold { count = 100, interval_sec = 60 }
      exceed_action = "deny(429)"
      ban_duration_sec = 3600
    }
  }
  # Block known injection patterns
  rule {
    action = "deny(403)"
    priority = 900
    match { expr { expression = "evaluatePreconfiguredExpr('crs-v33-id944130-sqli')" } }
    description = "Block prompt injection patterns"
  }
  rule {
    action = "allow"
    priority = 2147483647
    match { versioned_expr = "SRC_IPS_V1", config { src_ip_ranges = ["*"] } }
  }
}
```

## On-Premises / Air-Gapped Architecture

For regulated industries (government, defense, classified) requiring air-gapped AI, a Kubernetes stack implements NIST AI 100-2 controls without cloud dependency: a zero-trust network policy scoping ingress/egress to the AI namespace and named ports, a least-privilege vLLM inference deployment (non-root, read-only root filesystem, all capabilities dropped, read-only model volume mount), and a scheduled model-integrity verification job hashing deployed models against a signed manifest.

```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: ai-security
  labels: { security-tier: "high", nist-compliance: "ai-100-2" }
---
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: ai-agents-zero-trust
  namespace: ai-security
spec:
  podSelector: {}
  policyTypes: [Ingress, Egress]
  ingress:
    - from:
        - namespaceSelector: { matchLabels: { name: ai-security } }
        - podSelector: { matchLabels: { role: authorized-caller } }
  egress:
    - to: [{ namespaceSelector: { matchLabels: { name: ai-security } } }]
    - ports:
        - { port: 8000, protocol: TCP }  # vLLM inference
        - { port: 6333, protocol: TCP }  # Qdrant vector DB
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: vllm-inference
  namespace: ai-security
spec:
  replicas: 2
  selector: { matchLabels: { app: vllm-inference } }
  template:
    spec:
      serviceAccountName: vllm-sa  # Least-privilege SA
      securityContext:
        runAsNonRoot: true
        runAsUser: 1000
        seccompProfile: { type: RuntimeDefault }
      containers:
        - name: vllm
          image: vllm/vllm-openai:latest
          command: ["python", "-m", "vllm.entrypoints.openai.api_server",
                    "--model", "/models/llama-3.1-70b", "--tensor-parallel-size", "4",
                    "--max-model-len", "32768", "--enforce-eager"]  # Disable CUDA graphs for audit
          securityContext:
            allowPrivilegeEscalation: false
            readOnlyRootFilesystem: true
            capabilities: { drop: ["ALL"] }
          resources:
            requests: { nvidia.com/gpu: "4", memory: "80Gi" }
            limits: { nvidia.com/gpu: "4", memory: "160Gi" }
          volumeMounts:
            - { name: models, mountPath: /models, readOnly: true }
            - { name: tmp, mountPath: /tmp }
      volumes:
        - name: models
          persistentVolumeClaim: { claimName: ai-models-pvc, readOnly: true }
        - name: tmp
          emptyDir: { sizeLimit: 1Gi }
---
apiVersion: batch/v1
kind: CronJob
metadata:
  name: model-integrity-check
  namespace: ai-security
spec:
  schedule: "0 */6 * * *"  # Every 6 hours
  jobTemplate:
    spec:
      template:
        spec:
          containers:
            - name: integrity-checker
              image: model-integrity-checker:latest
              command: ["python", "/scripts/verify_model_hashes.py",
                        "--manifest", "/manifests/model-sha256-manifest.json",
                        "--models-dir", "/models", "--alert-on-mismatch"]
              volumeMounts:
                - { name: models, mountPath: /models, readOnly: true }
                - { name: manifests, mountPath: /manifests, readOnly: true }
```

## Related

- [NIST AI Standards Part 3: CAISI Agentic AI Security](03-part-03-caisi-agentic-ai.md)
- [NIST AI Standards Part 5: Control Mappings](05-part-05-control-mappings.md)
- [NIST AI Standards Part 6: Implementation Checklist](06-part-06-implementation-checklist.md)
