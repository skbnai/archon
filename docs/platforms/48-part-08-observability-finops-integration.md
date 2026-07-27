---
title: "Databricks Agentic AI, Part 8 — Observability, FinOps & Integration Ecosystem"
doc_type: guide
domain: platforms
status: current
topic_id: part-08-observability-finops-integration
last_reviewed: 2026-07-27
maturity: practitioner
supersedes:
  - docs/databricks-agentic-ai/part-08-observability-finops-integration.md
tags:
  - databricks
  - observability
  - mlflow
  - finops
  - cost-optimization
  - integrations
  - lakewatch
  - model-units
covers_version: "as of 2026-07-16"
---

*Part 8 of the [Databricks Agentic AI series](43-part-01-platform-vision-agentic-services.md).* Covers agent tracing, cost optimization, and ecosystem integrations.

## 1. Observability Architecture

### The Observability Stack

```mermaid
flowchart TD
    subgraph COLL["Collection Layer"]
        C1["MLflow Tracing<br/>(agent spans)"]
        C2["Unity AI Gateway<br/>(policy events)"]
        C3["Lakeflow Metrics<br/>(pipeline health)"]
    end
    COLL --> STORE
    subgraph STORE["Storage Layer"]
        DL["Delta Lake (UC-governed trace tables)<br/>mlflow.traces · uc_audit_log · agent_metrics · cost_events"]
    end
    STORE --> ANALYSIS
    subgraph ANALYSIS["Analysis Layer"]
        A1["Lakewatch SIEM<br/>(security)"]
        A2["Lakehouse Monitor<br/>(operational)"]
        A3["MLflow 3 Eval<br/>(quality eval)"]
    end
    ANALYSIS --> ACT["Action Layer<br/>Alerts (Slack/PagerDuty) · Auto-remediation · Dashboards · Reports"]
```

## 2. MLflow 3 Tracing — Production Observability

### What Gets Traced

Every call through the Databricks agent stack is traced end-to-end:

| Span Type | Captured Data | Use For |
| --- | --- | --- |
| `LLM` | model, prompt, response, tokens, latency, cost | Cost analysis, quality monitoring |
| `TOOL` | tool name, input params, output, duration, success/fail | Tool reliability, failure analysis |
| `RETRIEVAL` | query, retrieved chunks, scores, index name | RAG quality, freshness issues |
| `EMBEDDING` | input text, model, dimension, latency | Embedding pipeline performance |
| `CHAIN` | parent span grouping sub-calls | Multi-step agent trace |
| `AGENT` | full agent run: input, output, total tokens, total cost | Agent-level SLOs |
| `POLICY_CHECK` | rule matched, decision, context | Compliance audit |

### Trace Schema (Delta Table)

```sql
-- MLflow traces stored as Delta table (queryable via Spark/DBSQL)
DESCRIBE TABLE mlflow.traces.agent_production_traces;

-- trace_id           STRING     Unique trace identifier
-- run_id             STRING     MLflow experiment run
-- experiment_id      STRING     MLflow experiment
-- start_time         TIMESTAMP  Trace start
-- end_time           TIMESTAMP  Trace end
-- total_latency_ms   BIGINT     End-to-end latency
-- spans              ARRAY<STRUCT>  All spans with nested data
-- request            STRING     User input (serialized)
-- response           STRING     Agent output (serialized)
-- total_input_tokens BIGINT     Token count
-- total_output_tokens BIGINT
-- estimated_cost_usd DOUBLE     Cost estimate per Model Units pricing
-- quality_scores     MAP<STRING,DOUBLE>  Online judge scores
-- feedback_events    ARRAY<STRUCT>  Human feedback if collected
-- agent_id           STRING     UC Agent identifier
-- user_id            STRING     End user (if passed)
-- session_id         STRING     Conversation session
-- policy_decisions   ARRAY<STRUCT>  AI Gateway decisions
```

### Online Evaluation Pipeline

```python
import mlflow

# Configure continuous production evaluation
eval_config = mlflow.genai.EvaluationConfig(
    experiment_id="agent-prod-monitoring",
    sample_rate=0.05,  # evaluate 5% of production traces
    scorers=[
        mlflow.genai.scorers.groundedness(),
        mlflow.genai.scorers.relevance_to_query(),
        mlflow.genai.scorers.safety(),
    ],
    alert_thresholds={
        "groundedness": {"min": 0.85, "action": "slack_alert"},
        "safety": {"min": 0.99, "action": "page_oncall"},
    }
)

# Register evaluation job (runs on Lakeflow Jobs schedule)
mlflow.genai.deploy_evaluation_job(
    config=eval_config,
    schedule="*/15 * * * *"  # every 15 minutes
)
```

### Hallucination Detection

```python
# Custom hallucination detector using knowledge graph grounding
@mlflow.genai.scorer
def hallucination_detector(inputs, outputs, retrieved_context):
    """Detect claims in outputs not supported by retrieved context."""
    claims = extract_claims(outputs["response"])

    grounded_count = 0
    for claim in claims:
        # Check if claim is supported by any retrieved chunk
        support_score = check_claim_in_context(claim, retrieved_context)
        if support_score > 0.7:
            grounded_count += 1

    return Score(
        value=grounded_count / max(len(claims), 1),
        reason=f"{grounded_count}/{len(claims)} claims grounded in context"
    )
```

## 3. Lakewatch — Lakehouse-Native SIEM

**Lakewatch** is Databricks' SIEM capability built natively on Delta Lake:

- Ingests all Unity AI Gateway audit events automatically
- Analyzes traces for anomalous patterns (unusual tool use, unexpected data access)
- Detects prompt injection attempts at scale via Delta Live Tables queries
- Integrates with Unity Catalog lineage to trace a security event back to its data source
- Exports to external SIEMs (Splunk, Microsoft Sentinel, AWS Security Hub) via Delta Sharing or direct connector

### Lakewatch Detection Patterns

```sql
-- Detect unusual agent behavior: tool call volume spike
WITH agent_baseline AS (
    SELECT
        agent_id,
        date_trunc('hour', start_time) as hour,
        COUNT(*) as tool_calls,
        AVG(COUNT(*)) OVER (
            PARTITION BY agent_id
            ORDER BY date_trunc('hour', start_time)
            ROWS BETWEEN 167 PRECEDING AND 1 PRECEDING
        ) as baseline_avg
    FROM mlflow.traces.agent_production_traces
    LATERAL VIEW explode(spans) s WHERE s.span_type = 'TOOL'
    GROUP BY 1, 2
)
SELECT *
FROM agent_baseline
WHERE tool_calls > baseline_avg * 3  -- 3x spike vs rolling 7-day avg
  AND hour = date_trunc('hour', current_timestamp());
```

## 4. Distributed Tracing — OpenTelemetry Integration

Databricks MLflow Tracing is compatible with **OpenTelemetry** trace format, enabling integration with enterprise observability stacks:

```python
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from mlflow.tracing.export.otel import MLflowOtelExporter

# Export MLflow traces to Datadog / Grafana Tempo / Jaeger
tracer_provider = TracerProvider()
tracer_provider.add_span_processor(
    BatchSpanProcessor(OTLPSpanExporter(endpoint="http://otel-collector:4317"))
)

# MLflow auto-traces map to OpenTelemetry spans
# agent span → otel parent span
# tool call → otel child span
# LLM call → otel child span with LLM semantic conventions
```

**Supported Export Destinations:** Datadog APM, Grafana Tempo, Jaeger, Zipkin, AWS X-Ray, Azure Monitor, Google Cloud Trace.

## 5. AI FinOps — Cost Optimization

### Cost Drivers for AI Agents

| Cost Component | Typical % of AI Bill | Optimization Levers |
| --- | --- | --- |
| **LLM Inference (tokens)** | 55–80% | Model routing, caching, prompt compression |
| **GPU Compute (training/fine-tune)** | 10–30% | Spot instances, LoRA, TAO instead of full fine-tune |
| **Vector Search** | 3–8% | Index type selection, embedding reuse |
| **Storage (Delta/Iceberg)** | 2–5% | ZORDER, VACUUM, partition pruning |
| **Networking (egress)** | 1–3% | Same-region model endpoints, VPC endpoints |

### Model Units — GPU Cost Revolution

Databricks' **Model Units** (2026) are the most impactful FinOps development for inference:

| Model | GPU Allocation | Cost Behavior |
| --- | --- | --- |
| Traditional Dedicated Endpoint | 4× A100 GPUs reserved for 1 model | $12/hr regardless of utilization; 20% average utilization = $9.60/hr wasted |
| Model Units (Multi-tenant) | 4× A100 GPUs shared across 50 agent endpoints | Each endpoint pays only for actual tokens consumed; 80% GPU cost reduction reported by Databricks |

**How Model Units Work:**
- Multiple agent endpoints share GPU capacity via bin-packing
- Request queuing handles bursty traffic
- Warm pool prevents cold-starts for active endpoints
- Dedicated capacity available for latency-SLO critical workloads

### Smart Routing via Unity AI Gateway

Unity AI Gateway's **smart routing** matches tasks to the cheapest capable model:

```yaml
routing_policy:
  rules:
    - task_type: "simple_classification"
      model: "databricks-llama-3-8b"     # cheap, fast
      max_complexity_score: 0.3

    - task_type: "complex_reasoning"
      model: "databricks-llama-3-70b"    # capable
      complexity_range: [0.3, 0.7]

    - task_type: "critical_decision"
      model: "openai-gpt-4o"             # premium, accurate
      complexity_range: [0.7, 1.0]

  cost_target: "minimize"  # vs "quality" vs "latency"
```

**Measured savings from smart routing:** 40–60% token cost reduction for mixed-workload agents (per enterprise case studies as of 2026).

### Caching — Three Layers

| Cache Level | What's Cached | Savings |
| --- | --- | --- |
| **Prompt Cache** (Model Serving) | System prompt prefix tokens | 60–80% fewer input tokens for repeated system prompts |
| **Semantic Cache** (Vector Search) | Prior query → response pairs | 30–70% cache hit rate for similar questions |
| **Embedding Cache** (Feature Store) | Pre-computed embeddings for static documents | 100% embedding cost elimination for unchanged content |

**Prompt Cache Implementation:**

```python
# Model Serving endpoint with prompt caching enabled
serving_endpoint_config = {
    "name": "finance-agent-endpoint",
    "config": {
        "served_entities": [{
            "foundation_model": {
                "name": "databricks-meta-llama-3-70b-instruct",
                "prompt_caching": {
                    "enabled": True,
                    "cache_ttl_seconds": 3600
                }
            }
        }]
    }
}
```

### Cost Attribution (Chargeback/Showback)

Unity AI Gateway provides **token-level cost attribution** by:
- Agent identifier
- User / user group
- Application / use case
- Department (via UC tags)
- Cloud region

```sql
-- Monthly AI cost by department (from UC audit logs)
SELECT
    ua.user_department,
    ua.agent_id,
    SUM(ua.total_input_tokens) as input_tokens,
    SUM(ua.total_output_tokens) as output_tokens,
    SUM(ua.estimated_cost_usd) as total_cost_usd,
    COUNT(*) as total_invocations
FROM uc_audit.ai_gateway.invocation_log ua
WHERE date_trunc('month', ua.timestamp) = date_trunc('month', current_date())
GROUP BY 1, 2
ORDER BY total_cost_usd DESC;
```

### Databricks-Specific Cost Optimization Checklist

| Strategy | Impact | Effort |
| --- | --- | --- |
| Jobs Compute instead of All-Purpose for batch agents | 40% DBU reduction | Low |
| Spot instances for non-HITL evaluation jobs | 60–80% GPU cost | Low |
| Auto-terminate idle clusters (&lt; 20 min timeout) | Eliminate idle waste | Low |
| Model Units for inference (vs dedicated endpoints) | 80% GPU reduction | Medium |
| Smart routing via AI Gateway | 40–60% token cost | Medium |
| Prompt compression (summarize long contexts) | 20–40% input tokens | Medium |
| Embedding reuse / caching | 30–100% embed cost | Medium |
| Semantic cache for repetitive queries | 30–70% cache hit | Medium |
| ZORDER + OPTIMIZE Delta tables (reduce scan) | 10–40% storage cost | Medium |
| Switch from GPT-4o → Llama-3-70B where quality matches | 5–10x cost reduction | High |
| Fine-tune smaller model to match large model quality | 10–50x cost reduction | High |

### Budget Governance

```python
# Configure budget alerts and hard caps in Unity AI Gateway
budget_policy = {
    "name": "finance-team-budget",
    "applies_to": {"groups": ["finance-team"]},
    "limits": {
        "daily_tokens": 10_000_000,
        "monthly_cost_usd": 5000,
    },
    "alerts": {
        "warning_at_pct": 0.75,   # alert at 75% of budget
        "critical_at_pct": 0.90,  # page oncall at 90%
        "hard_stop": True          # block all calls when 100% reached
    },
    "notification_channels": [
        {"type": "slack", "channel": "#ai-costs-alerts"},
        {"type": "email", "to": "finance-lead@company.com"}
    ]
}
```

## 6. Integration Ecosystem

### Agent Framework Integrations

| Framework | Integration Depth | Status | Best For |
| --- | --- | --- | --- |
| **LangChain** | Native (`databricks-langchain` package) | GA | General-purpose agents, RAG |
| **LangGraph** | Native (with `ChatDatabricks`) | GA | Stateful multi-step agents |
| **OpenAI Agents SDK** | Via AI Gateway proxy | GA | Teams already on OpenAI SDK |
| **CrewAI** | Via AI Gateway proxy + UC tools | GA | Role-based multi-agent |
| **Semantic Kernel** | Via AI Gateway proxy | GA | .NET-first enterprise |
| **LlamaIndex** | Native (`llama-index-llms-databricks`) | GA | Complex RAG pipelines |
| **Haystack** | Via OpenAI-compatible endpoint | Community | Pipeline-first RAG |

**LangChain + Databricks Integration:**

```python
from databricks_langchain import ChatDatabricks, DatabricksVectorSearch
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate

# Use Databricks model through Unity AI Gateway
llm = ChatDatabricks(
    endpoint="databricks-meta-llama-3-70b-instruct",
    temperature=0.1
)

# Unity Catalog Functions as LangChain tools
from unitycatalog.ai.langchain.toolkit import UCFunctionToolkit
toolkit = UCFunctionToolkit(
    function_names=["catalog.finance.get_revenue", "catalog.finance.analyze_trend"]
)

# Full governed agent: model calls route through AI Gateway,
# tool calls are UC Functions with RBAC enforced
agent = create_tool_calling_agent(llm, toolkit.get_tools(), prompt)
agent_executor = AgentExecutor(agent=agent, tools=toolkit.get_tools())
```

### MCP Integration

Databricks exposes its core services as **managed MCP servers**, enabling any MCP-compatible agent to access governed Databricks resources:

| Managed MCP Server | Exposes | Access Control |
| --- | --- | --- |
| **Genie MCP** | Natural-language data questions | UC + AI Gateway |
| **Vector Search MCP** | Hybrid search over governed indexes | UC RBAC |
| **DBSQL MCP** | SQL query execution on governed tables | UC RBAC + row filters |
| **UC Functions MCP** | Execute any registered UC Function | UC EXECUTE privilege |
| **Unity Catalog MCP** | Table discovery, lineage queries | UC browse privilege |

**External MCP Client (e.g., Claude Code) connecting to Databricks:**

```python
from databricks.sdk.mcp import DatabricksMCPClient

# All external MCP calls route through Unity AI Gateway
client = DatabricksMCPClient(
    host=DATABRICKS_HOST,
    token=DATABRICKS_TOKEN
)

# Discover available Databricks tools
tools = await client.list_tools()
# Returns: genie_query, vector_search, sql_query, uc_function_*, etc.

# Execute governed tool
result = await client.call_tool(
    "genie_query",
    {"question": "What was total revenue in Q3 2026?", "space_id": "finance-genie"}
)
```

### Data Pipeline Integrations

| Tool | Integration | Use Case |
| --- | --- | --- |
| **Apache Kafka** | Native (Spark Structured Streaming) | Real-time event ingestion into Delta |
| **dbt** | dbt-databricks adapter | SQL transformations on Delta/Iceberg |
| **Airflow** | `apache-airflow-providers-databricks` | Orchestrate Databricks jobs externally |
| **Apache Spark** | Native (Databricks Runtime) | Large-scale ETL, ML training |
| **Ray** | Databricks Runtime + Ray on Spark | Distributed model training, hyperparameter tuning |
| **Kafka Connect** | Confluent/AWS MSK connector | CDC ingestion to Delta |
| **Flink** | Flink-Iceberg connector | Streaming to Iceberg tables |

### Cloud Platform Integrations

| Cloud | Storage | Secrets | Identity | Catalog Federation | Streaming | AI | Networking |
| --- | --- | --- | --- | --- | --- | --- | --- |
| **AWS** | S3 with Lake Formation permissions + UC | AWS Secrets Manager via Secret Scope | IAM role passthrough for S3 access | AWS Glue federation (GA) | Kinesis → Lakeflow Connect | Bedrock via AI Gateway external model proxy | AWS PrivateLink for control plane |
| **Azure** | ADLS Gen2 + Azure Private Endpoint | Azure Key Vault-backed Secret Scope | Azure Entra ID (AAD) SSO + SCIM | Purview metadata sync (via connector) | Event Hubs → Lakeflow Connect | Azure OpenAI via AI Gateway external model | Azure Private Link |
| **GCP** | GCS with IAM + Unity Catalog | Secret Manager via Secret Scope | Google Workspace SSO (OIDC) | Google Cloud Lakehouse federation (Preview) | Pub/Sub → Lakeflow Connect | Vertex AI Gemini via AI Gateway external model | GCP Private Service Connect |

### Snowflake Interoperability

Despite being competitors, Databricks and Snowflake have significant interoperability:

| Integration | Mechanism | Direction |
| --- | --- | --- |
| Read Delta tables from Snowflake | Delta UniForm → Iceberg → Snowflake Iceberg tables | Snowflake reads Databricks |
| Read Snowflake data from Databricks | UC Catalog Federation (Snowflake Horizon) | Databricks reads Snowflake |
| Share data bidirectionally | Delta Sharing protocol (open) | Either direction |
| Join cross-platform datasets | Lakebase CDF → Delta Sharing → Snowflake | Real-time operational joins |

### Infrastructure as Code

**Terraform Provider (Official):**

```hcl
# Create a Unity Catalog table with Terraform
resource "databricks_sql_table" "customer_data" {
  catalog_name = "prod"
  schema_name  = "customers"
  name         = "customer_profile"
  table_type   = "MANAGED"
  data_source_format = "DELTA"

  column {
    name = "customer_id"
    type = "BIGINT"
  }
  column {
    name = "email"
    type = "STRING"
  }

  properties = {
    "delta.enableDeletionVectors" = "true"
    "delta.universalFormat.enabledFormats" = "iceberg"
  }
}

# Create an agent serving endpoint
resource "databricks_model_serving" "finance_agent" {
  name = "finance-agent-prod"
  config {
    served_entities {
      name = "finance-agent-v3"
      external_model {
        name     = "my-finance-agent"
        provider = "databricks"
      }
    }
  }
}
```

## 7. AI-Native SOC Playbook Patterns

(For organizations using Databricks as a security operations platform)

### Security Operations on Databricks

```mermaid
flowchart TD
    subgraph SRC["Security Event Sources"]
        S1["Lakewatch (AI Gateway audit events)"]
        S2["UC Audit Logs (data access)"]
        S3["Cluster/workspace logs"]
        S4["External SIEM (Splunk/Sentinel) ingesting above"]
    end
    SRC --> DL["Delta Lake / Iceberg (security data lake)"]
    DL --> SOC["AI SOC Agent (Databricks Agent Bricks)"]
    SOC --> T1["Threat detection (pattern matching via SQL AI Functions)"]
    SOC --> T2["Anomaly detection (MLflow model serving)"]
    SOC --> T3["Incident enrichment (Vector Search on threat intel)"]
    SOC --> T4["Response recommendation (LLM reasoning on context)"]
    SOC --> T5["Human escalation (HITL via AI Gateway policy)"]
```

## Related

- [Part 7: Security Architecture](47-part-07-security-architecture.md)
- [Part 9: Competitive Comparison & Industry Reference Architectures](49-part-09-competitive-reference-architectures.md)
