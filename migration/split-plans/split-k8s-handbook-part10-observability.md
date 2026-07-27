# Split Plan: K8s Handbook Part 10 — Observability

**Source:** `/workspace/knowledge-docs/docs/cloud-platforms/kubernetes/K8s_Handbook_Part10_Observability.md` (~4,478 words body)

**Reason:** Word count exceeds guide doc_type cap (2600 words hard cap)

## Split Boundary

**Part 1 (Main):** `docs/platforms/27-k8s-handbook-part10-observability.md`
- Source: Chapters 1–9 (Observability Philosophy: The Three Pillars, OpenTelemetry, Prometheus, Thanos, Grafana, Loki, Tempo, Fluent Bit, Elastic Stack)
- Content: the three pillars of observability and the Four Golden Signals, the enterprise observability stack architecture, OpenTelemetry components/OTel Collector deployment/auto-instrumentation, Prometheus architecture/Operator/ServiceMonitors/essential PromQL queries, Thanos architecture and deployment pattern, Grafana dashboards and unified alerting, Loki architecture and LogQL, Tempo tracing concepts and deployment, Fluent Bit pipeline architecture and ConfigMap, the Elastic Stack and a Loki-vs-Elasticsearch decision matrix

**Part 2 (Supplementary):** `docs/platforms/parts/27-k8s-handbook-part10-observability-part2.md`
- Source: Chapters 10–17 (SLOs/SLAs/Error Budgets, Alerting Strategy and Runbooks, Cost Observability with OpenCost, GPU Observability with DCGM, AI and LLM Observability, Capacity Planning, Observability Anti-Patterns, Hands-On Exercises)
- Content: SLO definitions and Sloth SLO-as-code, the alert hierarchy and Alertmanager production config, OpenCost architecture and cost allocation queries, DCGM exporter metrics and deployment, LLM inference metrics/vLLM Prometheus metrics/OpenLLMetry, capacity planning signals and Prometheus queries, 5 observability anti-patterns, 2 hands-on exercises

## Source-quality notes (converted-pdf artifacts fixed during migration)

- Numerous flattened multi-line YAML/shell blocks reconstructed into properly line-broken fenced blocks (OTel Collector DaemonSet config, OTel auto-instrumentation, kube-prometheus-stack Helm install, ServiceMonitor, Thanos Sidecar/objstore config, Grafana alerting rule, LogQL queries, Tempo Helm install/Grafana datasource, Fluent Bit ConfigMap, and both exercises).
- Two tables (Essential Kubernetes PromQL Queries in Chapter 3) were split across a PDF page break with a duplicated header row — merged into a single table.
- No content-loss (heading-then-nothing) artifacts were found in this source; all chapters retained their body text.

## Navigation

- Part 1 ends with a pointer to Part 2 (SLOs, alerting, cost observability, GPU/AI observability, capacity planning, anti-patterns, exercises).
- Topic ID: both parts share the `k8s-handbook-part10-observability` topic family.
- Part 1 is canonical (`topic_id: k8s-handbook-part10-observability`).
- Part 2 uses `topic_id: k8s-handbook-part10-observability-part2`, `supersedes: []` (Part 1 carries the supersedes entry).
