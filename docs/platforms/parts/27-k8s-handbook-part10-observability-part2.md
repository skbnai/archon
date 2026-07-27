---
title: "K8s Handbook Part 10: Observability (Part 2)"
doc_type: guide
domain: platforms
status: current
topic_id: k8s-handbook-part10-observability-part2
last_reviewed: 2026-07-27
maturity: practitioner
supersedes: []
tags: [kubernetes, observability, slo, cost-observability, ai-observability]
covers_version: "2025-2026 edition"
---

> Continues from [K8s Handbook Part 10: Observability](../27-k8s-handbook-part10-observability.md), covering Chapters 10-17: SLOs and error budgets, alerting strategy, cost observability, GPU/AI observability, capacity planning, anti-patterns, and hands-on exercises.

## SLOs, SLAs, and Error Budgets

Service Level Objectives (SLOs) are the internal targets that define what good service looks like. They are the operational commitment that reliability work is measured against. SLOs translate business requirements into measurable technical targets, and error budgets give teams permission to take risk.

### SLO Definitions

- **SLI (Service Level Indicator)** — the metric being measured, e.g. the ratio of successful HTTP requests to total requests.
- **SLO (Service Level Objective)** — the target value for the SLI over a time window, e.g. 99.9% of requests succeed over a 30-day rolling window.
- **SLA (Service Level Agreement)** — the contractual commitment to customers, usually more lenient than the internal SLO (e.g. SLO = 99.9%, SLA = 99.5%).
- **Error Budget** — the time allowed to be below the SLO. A 99.9% SLO gives a 0.1% error budget, or 43.8 minutes/month of acceptable downtime; 99.99% gives 0.01%, or 4.38 minutes/month; 99.999% gives 0.001%, or 26.3 seconds/month.

### Sloth: SLO-as-Code

```yaml
# Sloth generates Prometheus recording rules from SLO definitions
version: prometheus/v1
service: api-server
labels:
  team: platform
slos:
  - name: requests-availability
    objective: 99.9
    description: API server successful request rate
    sli:
      events:
        error_query: |
          sum(rate(http_requests_total{job='api-server',status=~'5..'}[{{.window}}]))
        total_query: |
          sum(rate(http_requests_total{job='api-server'}[{{.window}}]))
    alerting:
      name: APIHighErrorRate
      page_alert:
        labels: { severity: critical }
      ticket_alert:
        labels: { severity: warning }
```

Sloth's generated recording rules include `slo:sli_error:ratio_rate5m` (current error rate) and `slo:error_budget:ratio` (remaining error budget), which feed a Grafana SLO dashboard showing burn rate, budget remaining, and alerts.

## Alerting Strategy and Runbooks

Effective alerting is harder than collecting metrics. The two failure modes are alert fatigue (too many alerts, on-call ignores them) and alert blindness (not enough alerts, incidents discovered by customers). Good alerting requires discipline: every alert must be actionable, have a runbook, and page someone who can act on it.

### Alert Hierarchy

| Level | Severity | Response Time | Channel | Example |
|---|---|---|---|---|
| P1 | Critical | Immediate (5 min) | PagerDuty page | API server down; database unreachable |
| P2 | High | 30 minutes | PagerDuty notify + Slack | Error rate > 5%; P99 latency > 2s |
| P3 | Medium | Business hours | Slack + Ticket | Error rate > 1%; PVC 80% full |
| P4 | Low | Next sprint | Ticket only | Slow memory growth; minor config drift |
| Info | Informational | Never pages | Dashboard only | Deployment completed; autoscaling event |

### Alertmanager Production Configuration

```yaml
# alertmanager.yaml
global:
  resolve_timeout: 5m
  slack_api_url: https://hooks.slack.com/services/XXX
inhibit_rules:
  # If cluster is down, suppress pod-level alerts
  - source_match: { alertname: KubernetesClusterDown }
    target_match_re: { alertname: (Pod.*|Node.*|Deployment.*) }
    equal: [cluster]
route:
  receiver: default-slack
  group_by: [alertname, cluster, namespace]
  group_wait: 30s
  group_interval: 5m
  repeat_interval: 4h
  routes:
    - match: { severity: critical }
      receiver: pagerduty-critical
      repeat_interval: 1h
    - match: { team: ai-platform }
      receiver: ai-platform-slack
receivers:
  - name: pagerduty-critical
    pagerduty_configs:
      - routing_key: XXXXXXXXXXXXXXXX
        description: '{{ .CommonAnnotations.summary }}'
        links:
          - href: '{{ .CommonAnnotations.runbook_url }}'
            text: Runbook
```

## Cost Observability with OpenCost

Kubernetes cost visibility is a critical operational capability. Without it, teams over-provision resources (wasting money) or under-provision (causing performance issues). OpenCost (CNCF sandbox) provides real-time, workload-level cost allocation that integrates with Prometheus and Grafana.

### OpenCost Architecture

The OpenCost Deployment queries the Kubernetes API for resource requests and usage, and the cloud provider's billing API for node pricing, computing cost allocation per pod, namespace, label, team, and cluster; it exposes metrics via `/metrics` (Prometheus) and a REST API.

**Cost model:** node cost divided by node resources gives cost per CPU-hour and cost per GB-RAM-hour; pod cost is `(pod CPU request * CPU cost) + (pod RAM request * RAM cost)`; idle cost is `(node resources - sum of pod requests) * node cost`.

**GPU cost model:** GPU node cost divided by GPUs per node gives cost per GPU-hour; GPU pod cost is `GPU request count * cost per GPU-hour`.

```bash
# Install OpenCost
helm repo add opencost https://opencost.github.io/opencost-helm-chart
helm install opencost opencost/opencost \
  --namespace opencost --create-namespace \
  --set opencost.exporter.cloudProviderApiKey=AWS_KEY \
  --set opencost.prometheus.external.url=http://prometheus:9090
```

### Cost Allocation Queries

```bash
# OpenCost REST API -- cost by namespace (last 7 days)
curl 'http://opencost:9090/model/allocation?window=7d&aggregate=namespace'
```

```promql
# CPU cost per namespace (per hour)
sum(kube_pod_container_resource_requests{resource='cpu'}) by (namespace)
  * on(node) group_left() node_cpu_hourly_cost

# GPU cost per pod
sum(kube_pod_container_resource_requests{resource='nvidia_com_gpu'}) by (namespace, pod)
  * on(node) group_left() node_gpu_hourly_cost

# Monthly cost projection per team
sum(opencost:container:cpu_allocation:rate1h) by (label_team) * 720
```

## GPU Observability with DCGM

GPU workloads require specialised observability. CPU metrics tell you nothing about whether a GPU is being efficiently utilised for AI training or inference. NVIDIA Data Center GPU Manager (DCGM) provides comprehensive GPU telemetry that integrates with Prometheus and Grafana.

### DCGM Exporter Metrics Reference

| Metric | Unit | What It Means | Alert Threshold |
|---|---|---|---|
| DCGM_FI_DEV_GPU_UTIL | Percent | SM utilisation; proxy for compute utilisation | Below 50% for training = under-utilisation |
| DCGM_FI_DEV_MEM_COPY_UTIL | Percent | Memory bandwidth utilisation | Near 100% = memory bandwidth bottleneck |
| DCGM_FI_DEV_FB_USED | Bytes | GPU memory (VRAM) in use | Above 90% of FB_FREE+FB_USED = OOM risk |
| DCGM_FI_DEV_POWER_USAGE | Watts | Current power draw | Near TDP = thermal throttle risk |
| DCGM_FI_DEV_GPU_TEMP | Celsius | GPU die temperature | Above 85C = throttling; above 95C = critical |
| DCGM_FI_DEV_SM_CLOCK | MHz | SM clock frequency | Drop without thermal = throttle from other cause |
| DCGM_FI_DEV_XID_ERRORS | Count | GPU error events (Xid codes) | Any Xid = investigate; Xid 79 = GPU crash |
| DCGM_FI_PROF_GR_ENGINE_ACTIVE | Ratio | Graphics/compute engine active fraction | Low during training = I/O bound |
| DCGM_FI_PROF_TENSOR_ACTIVE | Ratio | Tensor core utilisation | Low during DL training = poor CUDA kernel |

### DCGM Exporter Deployment

```bash
# Install DCGM Exporter as a DaemonSet on GPU nodes
helm repo add gpu-helm-charts https://nvidia.github.io/dcgm-exporter/helm-charts
helm install dcgm-exporter gpu-helm-charts/dcgm-exporter \
  --namespace gpu-operator --create-namespace \
  --set serviceMonitor.enabled=true \
  --set serviceMonitor.additionalLabels.release=kube-prometheus-stack
```

Key DCGM field groups for AI workloads: `DCGM_FI_PROF_*` professional metrics (requires DCGM 2.0+, Ampere+), including `GR_ENGINE_ACTIVE`, `TENSOR_ACTIVE`, `DRAM_ACTIVE`.

```yaml
# GPU utilisation alert
alert: GPUUnderutilised
expr: >
  avg_over_time(DCGM_FI_DEV_GPU_UTIL[30m]) < 10
  and on(pod) kube_pod_container_resource_requests{resource='nvidia_com_gpu'} > 0
for: 30m
annotations:
  summary: GPU {{ $labels.gpu }} in {{ $labels.pod }} below 10% utilisation for 30min
  action: Investigate if training job is stuck or misconfigured
```

## AI and LLM Observability

AI and LLM inference workloads require observability beyond standard application metrics. The quality and behaviour of AI responses — not just the latency of the HTTP response — must be monitored. This requires a new layer of AI-specific observability integrated into the Kubernetes monitoring stack.

### LLM Inference Metrics

| Metric | Source | What It Measures | SLO Target |
|---|---|---|---|
| Time to First Token (TTFT) | vLLM/KServe | Latency before streaming starts; user perceived | p50 < 500ms, p99 < 2s |
| Tokens per second (TPS) | vLLM/KServe | Generation throughput per request | Model-dependent; p50 > 50 tok/s |
| Inter-Token Latency (ITL) | vLLM/KServe | Time between generated tokens; streaming jitter | p50 < 50ms |
| Queue wait time | vLLM scheduler | Time request waited before processing | p95 < 1s; scale if exceeded |
| KV cache hit rate | vLLM | Prefix cache efficiency (reduces compute) | Target > 70% for prod workloads |
| GPU KV cache utilisation | vLLM | VRAM used for KV cache | Alert if > 95% (request throttling) |
| Request reject rate | vLLM | Requests dropped due to overload | Any rejection = scale trigger |
| Token budget exceeded | Application | Requests hitting max_tokens limit | High rate = prompt tuning needed |

### vLLM Metrics Configuration

vLLM exposes Prometheus metrics natively:

```bash
# Start vLLM with metrics enabled
python -m vllm.entrypoints.openai.api_server \
  --model meta-llama/Meta-Llama-3-70B-Instruct \
  --host 0.0.0.0 \
  --port 8000 \
  --metrics-url /metrics \
  --tensor-parallel-size 4 \
  --enable-prefix-caching
```

Key vLLM Prometheus metrics: `vllm:e2e_request_latency_seconds` (histogram, end-to-end), `vllm:time_to_first_token_seconds` (histogram, TTFT), `vllm:time_per_output_token_seconds` (histogram, ITL), `vllm:num_requests_running` (gauge, active requests), `vllm:num_requests_waiting` (gauge, queued requests), `vllm:gpu_cache_usage_perc` (gauge, KV cache utilisation), `vllm:gpu_prefix_cache_hit_rate` (gauge, prefix cache efficiency), `vllm:num_preemptions_total` (counter, preempted requests).

### LLM Observability with OpenTelemetry

OpenLLMetry brings OpenTelemetry to LLM applications, auto-instrumenting OpenAI, Anthropic, LangChain, and LlamaIndex:

```python
from opentelemetry.sdk.trace import TracerProvider
from openllmetry import Telemetry

Telemetry().init()  # Auto-instruments LLM calls
```

Captured span attributes for LLM calls include `gen_ai.system` (openai / anthropic / bedrock), `gen_ai.request.model` (gpt-4o / claude-3-opus), `gen_ai.request.max_tokens`, `gen_ai.usage.prompt_tokens`, `gen_ai.usage.completion_tokens`, and `gen_ai.response.finish_reason` (stop / length / tool_calls). These traces appear in Tempo as `user_request → agent_run → tool_call → LLM_call`, where each LLM call span shows model, tokens, latency, and cost, and agent loop spans show planning, tool execution, and synthesis.

## Capacity Planning with Observability Data

Observability data is the foundation of capacity planning. Rather than provisioning on intuition or over-provisioning for safety, capacity planning uses historical metrics to predict future needs with confidence intervals.

### Capacity Planning Signals

- **CPU headroom** — identify nodes consistently above 70% CPU utilisation; use `predict_linear(cpu_usage[7d], 30*24*3600)` to project the 30-day trend, and scale the cluster before reaching saturation.
- **Memory pressure** — watch for nodes with frequent page cache eviction or swap usage, and containers with memory usage approaching their limits (risk of OOM); correlate container memory growth with data volume growth.
- **Storage growth rate** — PVCs where `predict_linear(usage, 30d)` exceeds capacity; identify which namespaces/workloads are growing fastest, and alert when the projected fill date is within 14 days.
- **GPU utilisation trends** — model serving GPU utilisation by time of day and day of week, identifying peak hours for scaling policies; project GPU needs for model upgrades (a 70B model requires 4x the VRAM of a 7B model).
- **Network bandwidth** — identify inter-service communication patterns for network capacity planning, and detect N+1 query patterns (many small requests) vs. expected batch patterns.

### Capacity Planning Prometheus Queries

```promql
# Project PVC fill date (which PVCs will fill in < 7 days)
predict_linear(kubelet_volume_stats_used_bytes[6h], 7*24*3600)
  > kubelet_volume_stats_capacity_bytes

# Node CPU saturation trend (which nodes need scaling in 30 days)
predict_linear(instance:node_cpu_utilisation:rate5m[7d], 30*24*3600) > 0.85

# GPU memory growth for a model serving deployment
predict_linear(DCGM_FI_DEV_FB_USED{pod=~'llm-inference.*'}[24h], 7*24*3600)
  / DCGM_FI_DEV_FB_TOTAL > 0.95

# Cluster node count projection based on pod growth
predict_linear(kube_node_info[7d], 30*24*3600)
```

## Observability Anti-Patterns

- **Alert fatigue — alerting on symptoms not causes** — hundreds of alerts fire simultaneously during an incident, and the on-call engineer cannot identify the root cause amid the noise, with alerts paging for things that auto-recover. Alert on SLO burn rate (user impact), not individual metrics; use inhibition rules; every alert must have a runbook and be actionable.
- **High cardinality metric explosions** — using user IDs, request IDs, or trace IDs as metric labels means 1M users becomes 1M time series, causing Prometheus OOM or extreme cost. Labels must be low cardinality (max 10,000 unique values per label); use trace IDs in tracing backends (Tempo), not Prometheus labels.
- **No trace context propagation** — services don't pass W3C `traceparent` headers, so traces are broken with each service showing isolated spans with no connection. Enforce trace context propagation via a service mesh (Istio/Linkerd) or the OTel SDK, and validate with OTel Collector trace sampling.
- **Logging everything at DEBUG level in production** — production services logging at DEBUG level generate 100x more logs, exploding Loki ingestion costs and slowing log search. Default production logging to INFO or WARN, use dynamic log level adjustment (Zap, logrus, structured logging frameworks) for DEBUG, and filter debug logs in Fluent Bit before shipping.
- **No SLOs — alerting without user impact context** — teams track hundreds of internal metrics but cannot answer whether the service is meeting its availability commitment to users. Define SLOs for every customer-facing service; multi-window multi-burn-rate alerts are more actionable than threshold alerts.

## Hands-On Exercises

### Exercise 10.1 — Deploy the Full Observability Stack

Install the kube-prometheus-stack and configure Loki:

```bash
# Add Helm repos
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo add grafana https://grafana.github.io/helm-charts
helm repo update

# Install kube-prometheus-stack (Prometheus + Grafana + Alertmanager)
helm install kube-prom prometheus-community/kube-prometheus-stack \
  --namespace monitoring --create-namespace \
  --set grafana.adminPassword=admin123 \
  --set prometheus.prometheusSpec.retention=7d

# Install the Loki stack
helm install loki grafana/loki-stack \
  --namespace monitoring \
  --set grafana.enabled=false \
  --set promtail.enabled=true

# Access Grafana
kubectl port-forward -n monitoring svc/kube-prom-grafana 3000:80
# Login: admin / admin123
# Explore dashboards: Kubernetes / Compute Resources / Namespace

# Verify metrics
kubectl get servicemonitor -n monitoring
kubectl port-forward -n monitoring svc/kube-prom-kube-prometheus-prometheus 9090
# Query: count(kube_pod_info)
```

### Exercise 10.2 — Write SLO Alerts

Create a PrometheusRule for an availability SLO:

```bash
# Deploy a sample HTTP application
kubectl create deployment slo-demo --image=nginx:alpine --replicas=2
kubectl expose deployment slo-demo --port=80

# Create a PrometheusRule for a 99.9% availability SLO
kubectl apply -f - <<'YAML'
apiVersion: monitoring.coreos.com/v1
kind: PrometheusRule
metadata:
  name: slo-demo-rules
  namespace: default
  labels:
    release: kube-prom
spec:
  groups:
    - name: slo-demo
      rules:
        - alert: HighBurnRate
          expr: |
            (1 - rate(nginx_http_requests_total{status!~'5..'}[5m])
               / rate(nginx_http_requests_total[5m])) > 0.001
          for: 2m
          labels:
            severity: critical
          annotations:
            summary: SLO burn rate high
YAML
```

## Related

- [K8s Handbook Part 10: Observability](../27-k8s-handbook-part10-observability.md) — Part 1: The Three Pillars, OpenTelemetry, Prometheus, Thanos, Grafana, Loki, Tempo, Fluent Bit, Elastic Stack
