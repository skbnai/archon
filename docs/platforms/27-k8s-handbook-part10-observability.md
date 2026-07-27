---
title: "K8s Handbook Part 10: Observability"
doc_type: guide
domain: platforms
status: current
topic_id: k8s-handbook-part10-observability
last_reviewed: 2026-07-27
maturity: practitioner
supersedes: [docs/cloud-platforms/kubernetes/K8s_Handbook_Part10_Observability.md]
tags: [kubernetes, observability, prometheus, opentelemetry, grafana]
covers_version: "2025-2026 edition"
---

Observability is the ability to understand the internal state of a system from its external outputs. In the context of Kubernetes and distributed systems, observability is not a nice-to-have — it is the operational foundation that makes everything else possible: incident response, capacity planning, SLO compliance, security forensics, and cost optimisation.

## Observability Philosophy: The Three Pillars

- **Metrics** — numeric time-series data describing system behaviour over time. Metrics are aggregated, low-cardinality, and cheap to store. They answer: is the system healthy, is it meeting its SLO, what is the trend? Implemented in Kubernetes via Prometheus.
- **Logs** — discrete, timestamped records of events. Logs are high-cardinality, rich with context, and expensive to store. They answer: what exactly happened, what were the surrounding conditions, what is the error message? Implemented via Loki, Elastic, or cloud logging services.
- **Traces** — end-to-end records of requests flowing through distributed systems. Traces show causality: which service called which, what was the latency at each hop, where did the error originate? Implemented via OpenTelemetry, Tempo, or Jaeger.

### The Four Golden Signals (Google SRE)

| Signal | Metric Type | Kubernetes Metric Example | Alert Threshold |
|---|---|---|---|
| Latency | Histogram | `http_request_duration_seconds_p99` | p99 > 500ms for 5min |
| Traffic | Counter/Gauge | `http_requests_total` (rate) | Sudden drop > 50% from baseline |
| Errors | Counter | `http_requests_total{status=~'5..'}` | Error rate > 1% of traffic |
| Saturation | Gauge | `container_cpu_usage / requests` | CPU throttle > 25% of periods |

### Observability Stack Architecture

An enterprise Kubernetes observability stack has five pipelines:

- **Metrics pipeline** — Application → Prometheus scrape → Thanos → Grafana → object store (S3) for long-term storage.
- **Log pipeline** — Container stdout/stderr → Fluent Bit (DaemonSet) → Loki → Grafana; or Fluent Bit → Elasticsearch → Kibana (ELK).
- **Trace pipeline** — Application (OTLP SDK) → OpenTelemetry Collector → Tempo → Grafana; or → Jaeger.
- **Events pipeline** — Kubernetes Events → kube-state-metrics → Prometheus; Kubernetes Audit → Fluent Bit → Loki.
- **AI/GPU metrics** — DCGM Exporter (DaemonSet) → Prometheus → Grafana GPU dashboards.
- **Cost pipeline** — OpenCost (DaemonSet) → Prometheus → Grafana cost dashboards.

## OpenTelemetry: The Unified Instrumentation Standard

OpenTelemetry (OTel) is the CNCF standard for generating, collecting, and exporting telemetry data (metrics, logs, traces). It merges OpenCensus and OpenTracing into a single, vendor-neutral SDK and wire protocol (OTLP). For Kubernetes platforms, OpenTelemetry enables auto-instrumentation without code changes and provides a unified collection pipeline that routes to any backend.

### OpenTelemetry Components

- **OTel SDK** — language-specific libraries (Go, Java, Python, Node.js, Rust, .NET) that add instrumentation to application code, providing APIs for spans, metrics, and logs. Auto-instrumentation libraries instrument popular frameworks (HTTP servers, database clients, message queues) without code changes.
- **OTel Collector** — a vendor-agnostic agent/gateway that receives telemetry from applications (via OTLP, Jaeger, Zipkin, Prometheus), processes it (batch, filter, transform, sample), and exports to backends. Deployed as a DaemonSet (agent mode) or a centralised Deployment (gateway mode).
- **OTLP (OTel Protocol)** — the wire protocol for all OTel data, over gRPC and HTTP/protobuf. Backends supporting OTLP include Tempo, Jaeger, Datadog, Dynatrace, New Relic, Honeycomb, and dozens more.

### OTel Collector Deployment on Kubernetes

```yaml
# OTel Collector as DaemonSet (agent mode -- per node)
# Collects: host metrics, container logs, node-level telemetry
apiVersion: opentelemetry.io/v1alpha1
kind: OpenTelemetryCollector
metadata:
  name: otel-agent
  namespace: observability
spec:
  mode: daemonset
  config: |
    receivers:
      otlp:
        protocols:
          grpc: { endpoint: 0.0.0.0:4317 }
          http: { endpoint: 0.0.0.0:4318 }
      hostmetrics:
        collection_interval: 30s
        scrapers:
          cpu: {}
          memory: {}
          disk: {}
          network: {}
      kubeletstats:
        auth_type: serviceAccount
        endpoint: https://localhost:10250
        insecure_skip_verify: true
    processors:
      batch:
        timeout: 1s
        send_batch_size: 1024
      memory_limiter:
        limit_mib: 512
      k8sattributes:
        extract:
          metadata: [k8s.pod.name, k8s.namespace.name, k8s.deployment.name]
    exporters:
      otlp:
        endpoint: otel-gateway:4317
      prometheusremotewrite:
        endpoint: http://thanos-receive:10908/api/v1/receive
    service:
      pipelines:
        traces:
          receivers: [otlp]
          processors: [batch, k8sattributes]
          exporters: [otlp]
        metrics:
          receivers: [hostmetrics, kubeletstats]
          processors: [batch]
          exporters: [prometheusremotewrite]
```

### Auto-Instrumentation with OTel Operator

```yaml
# Instrument a Python application without code changes
apiVersion: opentelemetry.io/v1alpha1
kind: Instrumentation
metadata:
  name: python-instrumentation
  namespace: production
spec:
  exporter:
    endpoint: http://otel-agent:4317
  python:
    env:
      - name: OTEL_EXPORTER_OTLP_ENDPOINT
        value: http://otel-agent:4317
      - name: OTEL_METRICS_EXPORTER
        value: otlp
---
# Annotate the Pod for auto-instrumentation injection
metadata:
  annotations:
    instrumentation.opentelemetry.io/inject-python: 'true'
    # The OTel Operator injects an init container that installs
    # opentelemetry-distro and configures the OTLP exporter.
```

## Prometheus: Metrics Collection at Scale

Prometheus is the de facto metrics system for Kubernetes. It uses a pull model (scraping HTTP endpoints) with a powerful time-series database and PromQL query language. Understanding Prometheus internals is essential for designing reliable, scalable monitoring at enterprise scale.

### Prometheus Architecture

The **Prometheus Server** contains a scrape engine (discovers and scrapes `/metrics` endpoints), a TSDB (a local time-series database of 2-byte-aligned FLOAT64 values), a rules engine (evaluates recording and alerting rules), and an HTTP API (the PromQL query API used by Grafana). **Service discovery** includes `kubernetes_sd` (discovers Pods, Services, Nodes via the Kubernetes API) and `file_sd` (discovers targets from JSON/YAML files); a **ServiceMonitor** is the Prometheus Operator CRD for self-service scrape config. **Alertmanager** routes alerts to Slack, PagerDuty, OpsGenie, email, and webhooks, with deduplication, silencing, inhibition, and grouping. The **Pushgateway** accepts pushed metrics for Jobs that cannot be scraped — it is not a replacement for scraping and should be used for batch Jobs only.

### Prometheus Operator and ServiceMonitors

```bash
# Install kube-prometheus-stack (Prometheus Operator + Grafana + node_exporter)
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm install kube-prometheus-stack \
  prometheus-community/kube-prometheus-stack \
  --namespace monitoring --create-namespace \
  --set prometheus.prometheusSpec.retention=30d \
  --set prometheus.prometheusSpec.retentionSize=100GB \
  --set prometheus.prometheusSpec.storageSpec.volumeClaimTemplate.spec.storageClassName=fast-ssd \
  --set prometheus.prometheusSpec.storageSpec.volumeClaimTemplate.spec.resources.requests.storage=200Gi
```

```yaml
# ServiceMonitor: self-service scrape registration
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: myapp
  namespace: production
  labels:
    release: kube-prometheus-stack  # Must match the Prometheus selector
spec:
  selector:
    matchLabels: { app: myapp }
  endpoints:
    - port: http
      path: /metrics
      interval: 15s
      scrapeTimeout: 10s
      metricRelabelings:
        - sourceLabels: [__name__]
          regex: 'go_.*'
          action: drop  # Drop Go runtime metrics to save cardinality
```

### Essential Kubernetes PromQL Queries

| What to Monitor | PromQL Query |
|---|---|
| Pod CPU throttling rate | `sum(rate(container_cpu_cfs_throttled_periods_total[5m])) by (pod,namespace) / sum(rate(container_cpu_cfs_periods_total[5m])) by (pod,namespace)` |
| Memory usage vs limit | `container_memory_working_set_bytes / container_spec_memory_limit_bytes` |
| Pod restart rate | `increase(kube_pod_container_status_restarts_total[1h]) > 3` |
| Node disk pressure | `kubelet_volume_stats_used_bytes / kubelet_volume_stats_capacity_bytes > 0.80` |
| API server latency p99 | `histogram_quantile(0.99, sum(rate(apiserver_request_duration_seconds_bucket[5m])) by (le, verb))` |
| HTTP error rate | `sum(rate(http_requests_total{status=~'5..'}[5m])) / sum(rate(http_requests_total[5m]))` |
| Deployment replica lag | `kube_deployment_spec_replicas - kube_deployment_status_replicas_available` |

## Thanos: Long-Term Metrics Storage

Prometheus is excellent for short-term metrics (30-90 days local retention) but its single-node TSDB does not scale for enterprise requirements: multi-cluster queries, years of retention, high availability, and deduplication across replicas. Thanos solves all of these by adding a distributed layer over Prometheus.

### Thanos Architecture

The **Sidecar** runs alongside each Prometheus instance, uploading completed TSDB blocks to object storage (S3/GCS) and exposing Prometheus data via the Store API for the Querier. The **Querier** (Deployment) receives PromQL queries, fans out to all Sidecars/Store Gateways/Rulers, deduplicates results from Prometheus replicas, and returns a unified result. The **Store Gateway** (Deployment) reads historical blocks from object storage and exposes them via the Store API, backed by an in-memory index cache (Memcached/Redis). The **Compactor** (CronJob) compacts small blocks into larger ones (1h→2h→8h→48h→...), applies the retention policy (deleting blocks older than N days), and downsamples data (5m resolution after 40 days, 1h resolution after 1 year). An optional **Ruler** evaluates recording/alerting rules across long-term data and stores results back to object storage. An optional **Receive** component accepts Prometheus `remote_write`, enabling multi-cluster fan-in without a Sidecar.

### Thanos Deployment Pattern

```yaml
# Thanos Sidecar in the Prometheus StatefulSet
containers:
  - name: prometheus
    image: prom/prometheus:v2.51.0
    args:
      - --storage.tsdb.retention.time=2d
      - --storage.tsdb.min-block-duration=2h  # Required for Thanos
      - --storage.tsdb.max-block-duration=2h  # Required for Thanos
      - --web.enable-lifecycle
  - name: thanos-sidecar
    image: quay.io/thanos/thanos:v0.35.0
    args:
      - sidecar
      - --tsdb.path=/prometheus
      - --prometheus.url=http://localhost:9090
      - --objstore.config-file=/etc/thanos/objstore.yaml
      - --grpc-address=0.0.0.0:10901
    volumeMounts:
      - name: prometheus-storage
        mountPath: /prometheus
      - name: objstore-config
        mountPath: /etc/thanos
```

```yaml
# objstore.yaml (S3 backend)
type: S3
config:
  bucket: company-thanos-metrics
  region: us-east-1
  endpoint: s3.amazonaws.com
```

## Grafana: Dashboards and Alerting

Grafana is the primary visualisation and alerting layer for the Prometheus/Loki/Tempo observability stack. In enterprise environments, Grafana serves as the unified observability portal: operators, developers, and executives all use Grafana dashboards to understand system health.

### Essential Kubernetes Dashboards

| Dashboard | Source | What It Shows |
|---|---|---|
| Kubernetes / Compute Resources / Node | kube-prometheus | CPU, memory, network per node; identify hot nodes |
| Kubernetes / Compute Resources / Namespace | kube-prometheus | Per-namespace resource usage vs quotas |
| Kubernetes / Compute Resources / Pod | kube-prometheus | Per-pod CPU throttling, memory, network |
| Kubernetes / Networking / Namespace | kube-prometheus | Bytes in/out per namespace, pod, service |
| Node Exporter Full | node_exporter | Detailed OS metrics: disk I/O, filesystem, network |
| NVIDIA DCGM Exporter Dashboard | NVIDIA | GPU utilisation, memory, temperature, power |
| OpenCost | OpenCost | Cost per namespace, workload, pod, GPU hour |
| ArgoCD | ArgoCD plugin | Application sync status, health, history |
| Loki Dashboard | Loki | Log volumes, error rates, log search |

### Grafana Alerting Configuration

```yaml
# Grafana unified alerting rule (PromQL-based)
apiVersion: 1
groups:
  - orgId: 1
    name: kubernetes-critical
    folder: Production Alerts
    interval: 1m
    rules:
      - uid: pod-oom-killed
        title: Pod OOM Killed
        condition: C
        data:
          - refId: A
            model:
              expr: |
                sum by (namespace, pod, container) (
                  kube_pod_container_status_last_terminated_reason{reason='OOMKilled'}
                ) > 0
        noDataState: NoData
        execErrState: Error
        for: 1m
        annotations:
          summary: Pod OOM Killed
          description: Pod {{ $labels.pod }} in {{ $labels.namespace }} was OOM killed
          runbook_url: https://wiki.company.com/runbooks/pod-oom-kill
        labels:
          severity: critical
          team: platform
---
# Contact points (notification channels)
contactPoints:
  - name: pagerduty-critical
    receivers:
      - type: pagerduty
        settings:
          integrationKey: XXXXXXXXXXXXXXXX
          severity: critical
```

## Loki: Log Aggregation for Kubernetes

Loki (Grafana Labs) is a horizontally scalable log aggregation system designed for Kubernetes. Unlike Elasticsearch (which indexes all log content), Loki only indexes labels and stores log chunks compressed in object storage. This makes Loki dramatically cheaper than Elasticsearch for high-volume Kubernetes log ingestion.

### Loki Architecture

In microservices mode, Loki's components are: **Distributor** (receives log streams from Fluent Bit/Promtail, validates, shards), **Ingester** (buffers recent logs in memory, flushes to object storage), **Querier** (executes LogQL queries, reads from ingesters plus the object store), **Query Frontend** (request splitting, caching, parallelisation), **Ruler** (evaluates alerting rules on log streams), and **Compactor** (retention policy, compacts chunks). Storage splits into an index (DynamoDB, Cassandra, BoltDB, or filesystem for small deployments) and chunks (S3, GCS, Azure Blob, or filesystem). Scale modes: `monolithic` (single binary, dev/small clusters), `simple-scalable` (read/write/backend split, medium clusters), and `microservices` (full component split, large enterprise).

### LogQL — Loki Query Language

```logql
# Log stream selector (label-based)
{namespace='production', app='api-server'}

# Filter for errors
{namespace="production"} |= "ERROR" | json

# Parse structured JSON logs
{namespace="production", app="llm-inference"} | json | level="error"

# Error rate over time (metric query)
sum(rate({namespace="production"} |= "ERROR" [5m])) by (app)

# Find slow requests (latency > 1s in structured logs)
{app="api-server"} | json | duration > 1s

# Pattern detection (find common patterns in unstructured logs)
{namespace="production"} | pattern `<_> level= msg=` | level='error' | line_format '{{.message}}'
```

```yaml
# Alert rule on log error rate
groups:
  - name: loki-alerts
    rules:
      - alert: HighErrorRate
        expr: |
          sum(rate({namespace="production"} |= "ERROR" [5m])) by (app) > 10
        for: 5m
        annotations:
          summary: High error rate in {{ $labels.app }}
```

## Tempo: Distributed Tracing

Distributed tracing follows a request as it flows through multiple services, recording the time spent at each hop and any errors encountered. In Kubernetes microservice environments, tracing is the only way to understand end-to-end latency and pinpoint bottlenecks across service boundaries.

### Tracing Concepts

A **trace** is a directed acyclic graph of spans representing one request. A **span** is a unit of work with a `trace_id` (shared across all spans in a trace), a `span_id` (unique to this span), a `parent_span_id` (linking to the calling span), an `operation_name` (e.g. `HTTP GET /api/v1/query`), a start time and duration, a status (OK / ERROR), key-value attributes (e.g. `http.status_code`, `db.statement`), and timestamped events within the span.

**Context propagation** uses the `traceparent` header (`00-TRACE_ID-SPAN_ID-FLAGS`), the W3C TraceContext standard supported by all OTel SDKs — Service A passes `traceparent` to Service B, so they share the same `trace_id` and their spans are connected.

### Tempo Deployment and Configuration

```bash
# Install Tempo with an S3 backend
helm repo add grafana https://grafana.github.io/helm-charts
helm install tempo grafana/tempo-distributed \
  --namespace observability \
  --set storage.trace.backend=s3 \
  --set storage.trace.s3.bucket=company-traces \
  --set storage.trace.s3.region=us-east-1 \
  --set ingester.replicas=3 \
  --set querier.replicas=2 \
  --set compactor.replicas=1
```

```yaml
# OTel Collector exporter to Tempo
exporters:
  otlp:
    endpoint: tempo-distributor:4317
    tls: { insecure: true }
```

```yaml
# Grafana data source for Tempo with trace-to-log correlation
datasources:
  - name: Tempo
    type: tempo
    url: http://tempo-query-frontend:3100
    jsonData:
      tracesToLogsV2:
        datasourceUid: loki
        filterByTraceID: true
        filterBySpanID: false
      serviceMap:
        datasourceUid: prometheus
```

## Fluent Bit: Log Pipeline Engineering

Fluent Bit is the lightweight, high-performance log processor deployed as a DaemonSet on every Kubernetes node. It collects container logs, enriches them with Kubernetes metadata (pod name, namespace, labels), filters and transforms them, and routes to multiple destinations.

### Fluent Bit Pipeline Architecture

Fluent Bit runs as a per-node DaemonSet with three pipeline stages. **Input** reads container logs via `tail` on `/var/log/pods/` and node logs via `systemd`. **Filter** enriches records with Kubernetes metadata via the `kubernetes` filter. **Output** routes the enriched records to one or more destinations: Loki, Elasticsearch/OpenSearch, S3 (long-term archive), Splunk, or Datadog.

### Fluent Bit ConfigMap for Kubernetes

```
[SERVICE]
    Flush         1
    Log_Level     info
    Parsers_File  parsers.conf
    HTTP_Server   On
    HTTP_Listen   0.0.0.0
    HTTP_Port     2020

[INPUT]
    Name              tail
    Path              /var/log/containers/*.log
    multiline.parser  docker, cri
    Tag               kube.*
    Mem_Buf_Limit     50MB
    Skip_Long_Lines   On

[FILTER]
    Name                  kubernetes
    Match                 kube.*
    Merge_Log             On    # Parse JSON logs into structured fields
    Keep_Log              Off   # Remove original 'log' field after merge
    K8S-Logging.Parser    On
    K8S-Logging.Exclude   On
    Annotations           Off   # Exclude pod annotations (reduce size)
    Labels                On    # Include pod labels

[FILTER]
    Name     grep
    Match    kube.*
    Exclude  kubernetes_namespace_name kube-system   # Skip system logs

[OUTPUT]
    Name         loki
    Match        kube.*
    Host         loki-gateway
    Port         80
    Labels       job=fluent-bit,namespace=$kubernetes['namespace_name'],app=$kubernetes['labels']['app']
    Batch_Wait   1s
    Batch_Size   1048576
    Line_Format  json
    Remove_Keys  kubernetes,stream
```

## Elastic Stack on Kubernetes

The Elastic Stack (Elasticsearch, Kibana, Logstash/Fluent Bit, Beats) provides full-text search and analytics over logs, metrics, and security events. ECK (Elastic Cloud on Kubernetes) is the official Operator for deploying the Elastic Stack on Kubernetes.

### Loki vs Elasticsearch Decision Matrix

| Dimension | Loki | Elasticsearch |
|---|---|---|
| Indexing | Label-only (low cost) | Full text (high cost, powerful search) |
| Storage cost | Very low (S3 + compression) | Medium-high (index overhead) |
| Query language | LogQL (label + regex) | KQL / Lucene (full text, facets) |
| Cardinality | High label cardinality OK | Index explosion with high cardinality |
| Search capability | Regex + pattern matching | Full text, fuzzy, aggregations |
| Kubernetes integration | Native (tail filter) | Via Beats or Fluent Bit |
| Retention | Object store (cheap, long) | Hot/warm/cold tiers |
| SIEM capability | Limited | Native (Elastic Security, ECS schema) |
| Best for | Kubernetes log aggregation | SIEM, compliance, full-text search |

## Related

- [K8s Handbook Part 10: Observability (Part 2)](parts/27-k8s-handbook-part10-observability-part2.md) — SLOs/error budgets, alerting strategy, cost observability, GPU/AI observability, capacity planning, anti-patterns, and exercises
