---
title: Apache Iceberg, Open Table Formats & Interoperability
doc_type: guide
domain: data-knowledge
status: current
canonical: true
topic_id: databricks-iceberg-open-formats
maturity: practitioner
personas: [architect, engineer, data-engineer]
date_created: 2026-07-16
last_reviewed: 2026-07-16
covers_version: "as of July 2026"
source_type: native-md
supersedes:
  - docs/databricks-agentic-ai/part-06-iceberg-open-formats.md
tags: [databricks, iceberg, delta-lake, uniform, catalog-federation, open-formats]
sources: []
---

# Apache Iceberg, Open Table Formats & Interoperability

Covers Research Areas 8 &amp; 9: Iceberg v3 deep dive, Delta UniForm, Catalog Federation, Delta vs Iceberg vs Hudi comparison

---

## 1. The Open Table Format Landscape (2026)

### The Format War is Over — Iceberg Won

The industry reached a defining convergence point in 2025–2026:

&gt; "Iceberg won the format war. Now the catalog counts." — Cloud Magazine, July 2026

**Evidence:**

- Every major cloud ships managed Iceberg services (AWS S3 Tables, Azure Iceberg, BigLake Iceberg)
- Snowflake and Databricks both read AND write Iceberg natively
- Delta Lake adopted Deletion Vectors and Row Lineage (features from Iceberg) in v4
- Apache Iceberg v3 GA'd across all major platforms in H1 2026

### Format Comparison (2026 State)

| Dimension | Delta Lake | Apache Iceberg v3 | Apache Hudi | Apache Paimon |
|-----------|-----------|-------------------|-------------|---------------|
| **Primary Backer** | Databricks | Multiple (Netflix, Apple, AWS, Databricks) | Uber → Apache | Alibaba → Apache |
| **Metadata** | Delta Log (JSON + checkpoint Parquet) | Iceberg metadata tree (JSON + Avro manifests) | Timeline (HFile) | Snapshot + changelog |
| **ACID** | Yes (optimistic concurrency) | Yes (optimistic + serializable) | Yes | Yes |
| **Schema Evolution** | Full (add, rename, drop) | Full (add, rename, drop, reorder) | Limited | Full |
| **Partition Evolution** | Via OPTIMIZE hints | First-class (partition spec versioning) | Limited | Yes |
| **Time Travel** | Full (VERSION AS OF, TIMESTAMP AS OF) | Full (snapshot IDs, timestamps) | Full (timeline) | Yes |
| **Deletion Vectors** | Yes (Delta v3+) | Yes (Iceberg v3 — new 2026) | Yes (MoR) | Yes |
| **Row Lineage** | Via MERGE tracking | Yes (Iceberg v3 — new 2026) | No | No |
| **Branching** | Via Delta cloning | Yes (Iceberg branches + tags) | No | Yes |
| **VARIANT type** | Yes (Delta v4) | Yes (Iceberg v3 — new 2026) | No | No |
| **Streaming** | Excellent (Spark Streaming native) | Good (improving) | Excellent (CoW + MoR) | Good |
| **Catalog** | Delta Log + Unity Catalog | Iceberg REST Catalog (standard) | Hive Metastore + custom | Flink Catalog |
| **Open Ecosystem** | Delta OSS + Databricks UC | Fully open + multi-catalog | Open | Open |
| **AI Compatibility** | Excellent (Databricks native) | Excellent (universal) | Limited | Limited |
| **Vendor Lock-in** | Low (Delta OSS) but UC-driven | Lowest (multi-vendor standard) | Low | Low |

---

## 2. Apache Iceberg v3 — Deep Dive

### New in Iceberg v3 (GA 2026)

#### 2.1 Deletion Vectors

Instead of rewriting data files on UPDATE/DELETE, Deletion Vectors mark deleted rows in a sidecar bitmap file:

```
Before v3 (Copy-on-Write):
  UPDATE order SET status='shipped' WHERE id=42
  → Rewrite entire Parquet file (expensive for large files)

After v3 (Deletion Vectors):
  UPDATE order SET status='shipped' WHERE id=42
  → Write deletion vector file marking row 42 as deleted
  → Write new file with updated row 42
  → Old file + DV = logically current state
  (read at query time: skip DV-marked rows, much faster writes)
```

**Impact:** 10–50x faster UPDATE/DELETE/MERGE operations on large tables. Critical for operational/analytical convergence (LTAP pattern).

#### 2.2 Row Lineage

Every row now carries a system-generated `_row_id` and `_last_updated_sequence_number`:

```sql
-- Track exactly which rows changed since last checkpoint
SELECT * FROM catalog.schema.orders
FOR VERSION AS OF snapshot_id
WHERE _last_updated_sequence_number > 1000000;

-- Incremental processing for ML training
SELECT * FROM training_data
WHERE _last_updated_sequence_number > last_checkpoint_sequence;
```

**Impact:** Enables true incremental processing without full table scans. Critical for real-time ML feature pipelines and streaming agent knowledge updates.

#### 2.3 VARIANT Type

Stores semi-structured (JSON/BSON) data inline with columnar data, queried with path syntax:

```sql
-- Store flexible event data alongside structured columns
CREATE TABLE catalog.events.raw_events (
  event_id    BIGINT,
  event_time  TIMESTAMP,
  source      VARCHAR(50),
  payload     VARIANT   -- stores arbitrary JSON
);

-- Query nested fields efficiently
SELECT
  event_id,
  payload:customer.id AS customer_id,
  payload:order.total AS order_total
FROM catalog.events.raw_events
WHERE payload:event_type = 'purchase';
```

**Impact:** Eliminates the need to choose between columnar efficiency and schema flexibility. Single table for structured + semi-structured = massive simplification.

---

## 3. Delta UniForm — Write Once, Read Anywhere

UniForm (Universal Format) allows **any Iceberg-compatible engine to read Delta Lake tables** without data copying or format conversion.

### How UniForm Works

```mermaid
graph TD
    A["Delta Table Write<br/>(Databricks)"]
    
    A -->|generates Delta Log<br/>existing| B["Delta Log<br/>json/000000.json<br/>checkpoints/..."]
    A -->|generates Iceberg metadata<br/>new, automatic| C["Iceberg Metadata<br/>auto-generated<br/>metadata/<br/>v1.metadata.json<br/>snap-12345.avro<br/>(Iceberg snapshot)<br/>manifest-list.avro<br/>(Manifest list)"]
```

**The Iceberg metadata is automatically kept in sync** with every Delta commit. No pipeline, no delay.

### What External Engines Can Do with UniForm

| Engine | Read Delta via UniForm | Write via UniForm |
|--------|----------------------|-------------------|
| Snowflake | Yes (native Iceberg catalog) | No (read-only) |
| Amazon Redshift | Yes (Iceberg external tables) | No |
| Google BigQuery | Yes (BigLake Iceberg) | No |
| Trino/Presto | Yes (Iceberg catalog) | No |
| Spark (external) | Yes | No |
| DuckDB | Yes (Iceberg extension) | No |

### Enabling UniForm

```python
# Enable on new table
spark.sql("""
    CREATE TABLE catalog.schema.my_table (
        id BIGINT,
        name STRING,
        value DOUBLE
    )
    USING DELTA
    TBLPROPERTIES (
        'delta.universalFormat.enabledFormats' = 'iceberg',
        'delta.enableDeletionVectors' = 'true'
    )
""")

# Enable on existing table
spark.sql("""
    ALTER TABLE catalog.schema.my_table
    SET TBLPROPERTIES (
        'delta.universalFormat.enabledFormats' = 'iceberg'
    )
""")
```

### Cross-Engine Read Pattern

```mermaid
graph TD
    A["Databricks writes Delta + UniForm<br/>metadata to S3"]
    B["Unity Catalog exposes Iceberg<br/>REST Catalog endpoint"]
    C["Snowflake:<br/>CREATE ICEBERG TABLE<br/>USING catalog.schema.my_table<br/>(reads from Iceberg metadata,<br/>no data movement)"]
    D["Redshift Spectrum:<br/>external schema pointing<br/>to UC Iceberg REST"]
    E["BigQuery:<br/>BigLake external table<br/>via UC Iceberg REST"]
    
    A --> B
    B --> C
    B --> D
    B --> E
```

---

## 4. Unity Catalog — Iceberg REST Catalog

Unity Catalog implements the **Apache Iceberg REST Catalog API**, making it a universal catalog for any Iceberg-compatible engine.

### REST Catalog Capabilities

```mermaid
graph TD
    A["Unity Catalog Iceberg REST Catalog"] --> B["/namespaces — List catalogs/schemas"]
    A --> C["/namespaces/ns/tables — List tables in schema"]
    A --> D["/tables/table/metadata — Get table metadata (snapshots, manifests)"]
    A --> E["/tables/table/scan — Server-side scan planning (ABAC enforced)"]
    A --> F["/credentials — Vend temporary cloud credentials for direct reads"]
```

### Credential Vending

UC vends **temporary, scoped cloud credentials** (S3 pre-signed URLs, Azure SAS tokens, GCS signed URLs) to external engines, avoiding the need to share permanent credentials:

```
External Engine (Trino) → UC REST API: "I want to read table X"
                       ← UC: Here are temporary credentials (15-minute TTL)
                              + filtered scan plan (ABAC applied)
External Engine reads files directly from S3 using temp credentials
(UC logs this access in audit trail)
```

---

## 5. Catalog Federation (Public Preview / GA)

Catalog Federation allows Unity Catalog to **govern tables that physically live in external catalogs** — no data movement required.

### Supported External Catalogs (2026)

| External Catalog | Status | What Federates |
|-----------------|--------|---------------|
| **AWS Glue** | GA | Tables, databases, partitions |
| **Snowflake Horizon** | GA | Snowflake tables as Iceberg |
| **Apache Hive Metastore** | GA | Hive tables |
| **Salesforce Data Cloud** | GA | Salesforce objects |
| **Google Cloud Lakehouse** | Preview | BigLake tables |
| **Palantir** | Preview | Palantir datasets |

### Federation Architecture

```mermaid
graph TD
    A["External Catalog<br/>(AWS Glue)"]
    B["Catalog Connector<br/>(read metadata + credentials)"]
    C["Unity Catalog Metastore<br/>federated tables appear<br/>as UC objects<br/>UC lineage, tagging,<br/>search apply<br/>ABAC policies enforced<br/>(cross-engine via REST<br/>scan API)"]
    D["Databricks Engines<br/>(Spark, DBSQL,<br/>Agent AI Functions)<br/>direct S3 reads using<br/>UC-vended credentials"]
    E["Data files in<br/>External Storage"]
    
    A --> B
    B --> C
    C --> D
    D --> E
```

**Key benefit:** A single Unity Catalog governance model applies across ALL data, regardless of where it lives — Databricks, AWS Glue, Snowflake, Salesforce, or Palantir.

---

## 6. Delta Sharing — Open Data Exchange

Delta Sharing is an **open protocol** (Apache-licensed) for sharing live, versioned data with external consumers without copying it.

### Architecture

```mermaid
graph TD
    A["Data Provider<br/>(Databricks)"]
    B["Delta Sharing Server<br/>(built into Unity Catalog)<br/>Shares: catalog.schema.table<br/>→ share → recipient"]
    C1["Recipient: Snowflake<br/>(reads live Delta/Iceberg<br/>via sharing API)"]
    C2["Recipient: Power BI<br/>(Delta Sharing connector)"]
    C3["Recipient: Pandas/Python<br/>(delta-sharing Python client)"]
    C4["Recipient: Any HTTP client<br/>(REST API, bearer token auth)"]
    
    A --> B
    B --> C1
    B --> C2
    B --> C3
    B --> C4
```

**Governance:** Every share has:

- Named recipients with authentication tokens
- Optional row-level filters applied at sharing layer
- Expiry dates
- Audit trail in Unity Catalog

---

## 7. AI Agents and Apache Iceberg — Integration Patterns

### How Agents Consume Iceberg Tables

**Pattern 1: SQL via Databricks SQL / Spark**

```python
# Agent uses UC Function (SQL tool) to query Iceberg table
@uc_function(catalog="corp", schema="sales")
def get_quarterly_sales(quarter: str) -> dict:
    """Returns total sales for the given quarter."""
    result = spark.sql(f"""
        SELECT SUM(amount) as total, COUNT(*) as transactions
        FROM corp.sales.transactions
        WHERE quarter = '{quarter}'
    """)
    return result.first().asDict()
```

**Pattern 2: Incremental Knowledge Updates (Row Lineage)**

```python
# Agent updates its knowledge base with only new/changed rows
import mlflow

def refresh_agent_knowledge(last_checkpoint_sequence: int):
    new_data = spark.sql(f"""
        SELECT * FROM corp.products.catalog
        WHERE _last_updated_sequence_number > {last_checkpoint_sequence}
    """)

    # Upsert to Vector Search index
    vector_search_client.upsert(
        index_name="catalog.ai.product_knowledge_index",
        data=generate_embeddings(new_data)
    )

    # Update checkpoint
    return new_data.agg(max("_last_updated_sequence_number")).first()[0]
```

**Pattern 3: Time-Travel for Evaluation**

```python
# Agent evaluation against historical data snapshots
def evaluate_agent_on_historical_state(agent, evaluation_date):
    """Run agent against data as it existed on evaluation_date."""
    with mlflow.start_run():
        historical_data = spark.sql(f"""
            SELECT * FROM corp.finance.transactions
            TIMESTAMP AS OF '{evaluation_date}'
        """)
        results = agent.run_batch(historical_data)
        mlflow.genai.log_evaluation_results(results)
```

### Performance Considerations for AI Workloads

| Optimization | Iceberg Feature | When to Apply |
|-------------|----------------|---------------|
| Reduce files scanned | Partition pruning (hidden partitioning) | Large tables with date/category partitions |
| Faster incremental reads | Row Lineage (`_last_updated_sequence_number`) | Streaming feature updates, knowledge refresh |
| Fast UPDATEs for feedback | Deletion Vectors | High-frequency write-back from agents |
| Schema flexibility | VARIANT type | Mixed structured/unstructured agent outputs |
| Historical comparison | Time travel | A/B evaluation, audit, replay |
| Cross-engine sharing | UniForm + Iceberg REST | Multi-tool agent ecosystems |

---

## 8. Open Lakehouse Vision

Databricks' stated long-term strategy is an **open, Iceberg-compatible, agent-native AI data platform** with the following properties:

| Property | Implementation |
|----------|---------------|
| **Open formats** | Delta Lake (OSS) + Iceberg v3 native support |
| **Open catalog protocol** | Iceberg REST Catalog API via Unity Catalog |
| **Open data exchange** | Delta Sharing (Apache-licensed) |
| **Open compute** | Apache Spark (OSS) — Databricks contributes upstream |
| **Open agent protocol** | MCP support in Unity Catalog / Agent Bricks |
| **Open agent framework** | Omnigent (Apache 2.0) |
| **Interoperability** | Read from Snowflake, AWS Glue, Salesforce, Google via federation |
| **Vendor neutrality** | Catalog Federation — governance without data movement |

**Enterprise Architecture Implication:** Organizations adopting this stack are not locked into a single format or catalog. Data can be read by Snowflake, BigQuery, Trino, DuckDB, or any Iceberg-compatible tool — while governance remains centralized in Unity Catalog. This is a deliberate strategy to become the **governance hub** of the open data ecosystem rather than a proprietary silo.

---

## Sources

- [Apache Iceberg v3 Public Preview on Databricks](https://www.databricks.com/blog/next-era-open-lakehouse-apache-icebergtm-v3-public-preview-databricks)
- [Full Apache Iceberg Support in Databricks](https://www.databricks.com/blog/announcing-full-apache-iceberg-support-databricks)
- [Delta UniForm Universal Format](https://www.databricks.com/blog/delta-uniform-universal-format-lakehouse-interoperability)
- [Advancing Apache Iceberg: Iceberg v3 GA, Open Sharing](https://www.databricks.com/blog/unity-catalog-and-next-era-apache-icebergtm)
- [State of Apache Iceberg Catalogs June 2026](https://dev.to/alexmercedcoder/the-state-of-apache-iceberg-catalogs-in-june-2026-265e)
- [Databricks Eliminates Table Format Lock-In](https://www.databricks.com/company/newsroom/press-releases/databricks-eliminates-table-format-lock-and-adds-capabilities)
- [Lakehouse Table Formats 2026 — DEV Community](https://dev.to/alexmercedcoder/lakehouse-table-formats-in-2026-iceberg-delta-lake-hudi-paimon-and-ducklake-how-they-work-p1k)
