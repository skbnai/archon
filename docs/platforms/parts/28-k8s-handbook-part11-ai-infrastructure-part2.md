---
title: "K8s Handbook Part 11: AI Infrastructure (Part 2)"
doc_type: guide
domain: platforms
status: current
topic_id: k8s-handbook-part11-ai-infrastructure-part2
last_reviewed: 2026-07-27
maturity: practitioner
supersedes: []
tags: [kubernetes, ai-infrastructure, mlflow, vector-database, cost-optimization]
covers_version: "2025-2026 edition"
---

> Continues from [K8s Handbook Part 11: AI Infrastructure](../28-k8s-handbook-part11-ai-infrastructure.md), covering Chapters 10-17: AI gateways, feature stores, MLflow, vector databases, alternative accelerators, cost optimisation, anti-patterns, and hands-on exercises.

## AI Gateways and Model Routing

An AI Gateway sits between client applications and LLM backends, providing a unified API surface across multiple models, authentication and authorisation, rate limiting and cost controls, request routing (model selection), caching, observability, and fallback handling. As LLM usage scales, an AI gateway becomes essential infrastructure.

### AI Gateway Capabilities

| Capability | Business Value | Implementation |
|---|---|---|
| Unified API | Apps use one endpoint regardless of backend model | OpenAI-compatible /v1 endpoint for all models |
| Model routing | Route to best model by cost/latency/capability | Rules-based or ML-based routing |
| Authentication | Secure model access; track usage per team/user | API key or OIDC JWT validation |
| Rate limiting | Prevent runaway costs; enforce quotas per team | Token-per-minute limits per key |
| Semantic caching | Cache responses for identical/similar queries | Embedding similarity threshold cache |
| Cost tracking | Allocate AI costs to teams/applications | Per-request token tracking → OpenCost |
| Fallback handling | Route to backup model on primary failure | Retry with fallback model list |
| PII redaction | Strip sensitive data before sending to external LLMs | Presidio or custom regex pipeline |
| Prompt injection detection | Detect and block adversarial prompts | LLM-based or pattern-based detection |

### LiteLLM Proxy on Kubernetes

```yaml
# LiteLLM Proxy -- unified AI gateway
apiVersion: apps/v1
kind: Deployment
metadata:
  name: litellm-proxy
  namespace: ai-gateway
spec:
  replicas: 3
  template:
    spec:
      containers:
        - name: litellm
          image: ghcr.io/berriai/litellm:main-latest
          args: ['--config', '/app/config.yaml', '--port', '4000']
          resources:
            requests: { cpu: 1, memory: 2Gi }
            limits: { memory: 4Gi }
          volumeMounts:
            - name: config
              mountPath: /app/config.yaml
              subPath: config.yaml
```

```yaml
# litellm config.yaml
model_list:
  - model_name: gpt-4o
    litellm_params:
      model: azure/gpt-4o
      api_base: https://company.openai.azure.com
      api_key: os.environ/AZURE_API_KEY
  - model_name: llama3-70b
    litellm_params:
      model: openai/llama3-70b-instruct
      api_base: http://vllm-llama3-70b.ai-serving:8000
      api_key: dummy
  - model_name: claude-3-5-sonnet
    litellm_params:
      model: anthropic/claude-3-5-sonnet-20241022
      api_key: os.environ/ANTHROPIC_API_KEY
router_settings:
  routing_strategy: least-busy
  num_retries: 3
  fallbacks: [{ gpt-4o: [llama3-70b] }]
general_settings:
  master_key: os.environ/LITELLM_MASTER_KEY
  database_url: postgresql://litellm:PASS@postgres:5432/litellm
```

## Feature Stores with Feast

A feature store is the data layer that bridges data engineering and machine learning. It provides consistent, versioned, low-latency feature serving for both training (batch) and inference (online). Feast is the most widely deployed open-source feature store, with native Kubernetes integration.

### Feast Architecture on Kubernetes

The **Offline Store** provides batch features for training, reading from BigQuery, Redshift, Snowflake, Spark, or DuckDB to generate historical feature values for training datasets. The **Online Store** provides real-time features for inference, stored in Redis, DynamoDB, Bigtable, or SQLite (dev), with sub-millisecond feature lookup during inference. The **Feature Server** exposes an HTTP API (`GET /get-online-features`) deployed as a Kubernetes Deployment. The **Materialisation Job** is a batch job that copies the offline store to the online store, scheduled via a Kubernetes CronJob. The **Feature Registry** stores feature definitions in GCS, S3, or a SQL database.

```python
# Feast feature definition
from feast import Entity, Feature, FeatureView, ValueType
from feast.types import Float64, Int64

user = Entity(name='user_id', value_type=ValueType.STRING)

user_features = FeatureView(
    name='user_features',
    entities=[user],
    ttl=timedelta(days=30),
    schema=[
        Field(name='age', dtype=Int64),
        Field(name='lifetime_value', dtype=Float64),
        Field(name='preferred_language', dtype=String),
    ],
    source=BigQuerySource(table='company.features.user_features'),
)
```

## MLflow: Experiment Tracking and Model Registry

MLflow is the leading open-source MLOps platform for experiment tracking, model packaging, and model registry. In Kubernetes, MLflow serves as the system of record for all training runs, model versions, and deployment history.

### MLflow Components on Kubernetes

The **MLflow Tracking Server** (Deployment) exposes a REST API for logging metrics, parameters, and artifacts, backed by PostgreSQL for runs/experiments/params/metrics and an artifact store (S3, GCS, Azure Blob) for model files and plots. The **MLflow Model Registry** provides versioned model storage with lifecycle stages (Staging → Production → Archived) and an approval workflow via the REST API or the MLflow UI. Model serving via MLflow can use `mlflow models serve` for dev-only built-in serving, or export to KServe, vLLM, or custom serving for production.

```python
# Training code integration
import mlflow

mlflow.set_tracking_uri('http://mlflow.mlops.svc.cluster.local:5000')
mlflow.set_experiment('llama3-finetune-v2')

with mlflow.start_run():
    mlflow.log_param('model', 'meta-llama/Llama-3-70b')
    mlflow.log_param('learning_rate', 2e-4)
    mlflow.log_param('num_epochs', 3)
    for epoch in range(num_epochs):
        train_loss = train_one_epoch()
        mlflow.log_metric('train_loss', train_loss, step=epoch)
    mlflow.pytorch.log_model(
        model, 'model', registered_model_name='llama3-70b-finetune-v2'
    )
```

## Vector Databases on Kubernetes

Vector databases are foundational infrastructure for RAG pipelines. They store high-dimensional embeddings and enable approximate nearest neighbour (ANN) search to find semantically similar content. Production deployments require careful sizing, scaling, and operational management on Kubernetes.

### Vector Database Comparison

| Database | Algorithm | K8s Native | Scale-Out | Best For |
|---|---|---|---|---|
| Qdrant | HNSW (disk-indexed) | StatefulSet + Operator | Sharded cluster | Enterprise RAG, on-prem |
| Weaviate | HNSW (in-memory) | StatefulSet + Operator | Horizontal (modules) | Complex filtering + search |
| Milvus | Multiple (HNSW, IVF, FLAT) | Operator (Milvus Operator) | Fully distributed | Large scale, enterprise |
| pgvector | IVFFlat / HNSW | StatefulSet (CloudNativePG) | PostgreSQL HA | Existing Postgres users |
| Chroma | HNSW (in-process) | Deployment | Single server | Prototyping, small scale |
| Redis (RedisSearch) | HNSW + inverted index | StatefulSet | Redis Cluster | Low latency, hybrid search |

### Milvus Operator Deployment

```bash
# Install Milvus Operator
helm repo add milvus-operator https://zilliztech.github.io/milvus-operator/
helm install milvus-operator milvus-operator/milvus-operator \
  --namespace milvus-operator --create-namespace
```

```yaml
# Create a Milvus cluster
apiVersion: milvus.io/v1beta1
kind: Milvus
metadata:
  name: milvus-prod
  namespace: ai-platform
spec:
  mode: cluster
  components:
    queryNode:
      replicas: 3
      resources:
        requests: { cpu: 8, memory: 64Gi }
    indexNode:
      replicas: 2
      resources:
        requests: { cpu: 16, memory: 32Gi }
    dataNode:
      replicas: 2
  dependencies:
    etcd: { inCluster: { values: { replicaCount: 3 } } }
    minio: { inCluster: { values: { mode: distributed } } }
    pulsar: { inCluster: { enabled: true } }
```

## AMD ROCm and Intel Gaudi Support

NVIDIA dominates AI accelerator mindshare, but AMD MI300X and Intel Gaudi 3 offer compelling alternatives with significant cost advantages. Kubernetes supports all three via device plugins and operator patterns.

### Accelerator Comparison

| Accelerator | VRAM | FP16 TFLOPS | Int8 TOPS | K8s Integration | Key Use Case |
|---|---|---|---|---|---|
| NVIDIA H100 SXM5 | 80GB HBM3 | 1,979 | 3,958 | GPU Operator + CUDA | Best ecosystem, LLM training |
| NVIDIA A100 SXM4 | 80GB HBM2e | 312 | 624 | GPU Operator + CUDA | Training, inference baseline |
| AMD MI300X | 192GB HBM3 | 1,307 | 2,614 | ROCm Device Plugin | Large models (192GB = 70B+ no sharding) |
| Intel Gaudi 3 | 96GB HBM2e | 1,835 | 3,670 | Intel Gaudi Operator | Cost-effective training, PyTorch native |

### AMD ROCm on Kubernetes

```bash
# AMD ROCm Device Plugin
helm repo add rocm https://rocm.github.io/k8s-device-plugin
helm install rocm-device-plugin rocm/rocm-device-plugin --namespace kube-system
# AMD GPU appears as: amd.com/gpu resource on nodes
```

```yaml
# Run vLLM on AMD MI300X
containers:
  - name: vllm-rocm
    image: vllm/vllm-rocm:latest
    command: [python, -m, vllm.entrypoints.openai.api_server]
    args:
      - --model=meta-llama/Llama-3-70B-Instruct
      - --tensor-parallel-size=1  # MI300X has 192GB -- fits 70B solo!
    resources:
      limits: { amd.com/gpu: '1' }
```

## AI Infrastructure Cost Optimisation

GPU compute is the dominant cost in enterprise AI. A single H100 GPU node costs over $30/hour on-demand from AWS. Optimising GPU utilisation, scheduling strategy, and model efficiency can reduce AI infrastructure costs by 50-80%.

### Cost Optimisation Strategies

- **GPU utilisation maximisation** — batch requests to maximise GPU compute utilisation. vLLM continuous batching enables 70-90% GPU utilisation vs. 20-30% for naive serving. Monitor `DCGM_FI_DEV_GPU_UTIL` — target > 70% during serving hours.
- **Spot/preemptible instances for training** — use spot instances (AWS) or preemptible VMs (GCP) for batch training jobs, 60-90% cheaper than on-demand. Implement checkpoint-based fault tolerance so jobs resume after preemption.
- **Scale to zero for inference** — use KEDA to scale inference deployments to zero replicas during off-peak hours. Critical for internal tools with predictable usage patterns; model loading time (1-10 min for large LLMs) is acceptable for non-latency-sensitive apps.
- **Reserved/committed use discounts** — commit to 1 or 3 years of GPU instance usage for a 60-70% discount over on-demand. Use for baseline inference capacity; use spot for training peaks.
- **Quantisation** — INT8 and INT4 quantisation reduces GPU memory requirements by 2-4x with minimal quality loss for most use cases. A 70B FP16 model (140GB) becomes 70B INT8 (70GB), fitting on a single 80GB GPU instead of requiring 2.
- **Model right-sizing** — deploy the smallest model that meets quality requirements. An 8B model costs 10x less to serve than a 70B model; use A/B testing to find the quality/cost tradeoff.
- **Prefix caching** — enable vLLM prefix caching for RAG workloads with long context. Cache hit rates of 50-80% reduce compute by a proportional amount; monitor the `vllm:gpu_prefix_cache_hit_rate` metric.

## AI Infrastructure Anti-Patterns

- **One model per Deployment for serving** — running separate Deployments for each LLM variant wastes GPU resources: 3 models x 4 GPUs = 12 GPUs sitting idle between requests. Use model multiplexing in vLLM (the `--model` flag with multiple models) or Triton Inference Server for co-locating compatible models on shared GPUs.
- **Not setting GPU request == limit** — GPU resources in Kubernetes require request == limit; setting only requests without limits causes incorrect scheduling. Always set both `requests.nvidia.com/gpu` and `limits.nvidia.com/gpu` to the same value.
- **Training without checkpointing** — a multi-day training job fails at 95% completion with no checkpoint, requiring a restart from scratch and total loss of GPU hours. Checkpoint every N steps to S3/PVC, implement resume-from-checkpoint in training code, and test checkpoint/resume in dev before long training runs.
- **LLM inference without batching** — serving one request at a time on a 4-GPU H100 node gives 5% GPU utilisation and 20x higher cost per token than necessary. Use vLLM or SGLang with continuous batching enabled, and set an appropriate `max-num-batched-tokens` for your request mix.
- **No GPU node taints** — general workloads scheduled onto GPU nodes let CPU-only Pods consume GPU node resources, blocking AI workloads from scheduling. Always taint GPU nodes with `nvidia.com/gpu=true:NoSchedule` so only Pods with explicit GPU requests and tolerations can use GPU nodes.

## Hands-On Exercises

### Exercise 11.1 — Deploy vLLM for LLM Inference

Deploy a small LLM model using vLLM on a GPU node:

```bash
# Prerequisite: GPU node with NVIDIA GPU Operator installed
# Deploy vLLM with a small model (Qwen2.5-1.5B for dev)
kubectl apply -f - <<'YAML'
apiVersion: apps/v1
kind: Deployment
metadata:
  name: vllm-dev
  namespace: ai-dev
spec:
  replicas: 1
  selector:
    matchLabels: { app: vllm-dev }
  template:
    metadata:
      labels: { app: vllm-dev }
    spec:
      tolerations:
        - key: nvidia.com/gpu
          operator: Exists
          effect: NoSchedule
      containers:
        - name: vllm
          image: vllm/vllm-openai:latest
          args:
            - --model=Qwen/Qwen2.5-1.5B-Instruct
            - --port=8000
            - --host=0.0.0.0
          resources:
            limits: { nvidia.com/gpu: '1', memory: 16Gi }
YAML

# Expose and test
kubectl expose deployment vllm-dev --port=8000 -n ai-dev
kubectl port-forward -n ai-dev svc/vllm-dev 8000:8000

# Test the OpenAI-compatible API
curl http://localhost:8000/v1/chat/completions \
  -H 'Content-Type: application/json' \
  -d '{"model":"Qwen2.5-1.5B-Instruct","messages":[{"role":"user","content":"Hello!"}]}'
```

### Exercise 11.2 — GPU Utilisation Monitoring

Observe GPU metrics during inference load:

```bash
# Install DCGM Exporter (if not installed via GPU Operator)
helm repo add gpu-helm-charts https://nvidia.github.io/dcgm-exporter/helm-charts
helm install dcgm-exporter gpu-helm-charts/dcgm-exporter --namespace monitoring

# Verify GPU metrics are available in Prometheus
kubectl port-forward -n monitoring svc/kube-prom-kube-prometheus-prometheus 9090
# Query: DCGM_FI_DEV_GPU_UTIL

# Generate load on vLLM
pip install locust
# Create locustfile.py for an LLM load test
locust -H http://localhost:8000 --users=10 --spawn-rate=2

# Observe GPU utilisation rise in Grafana/Prometheus:
# DCGM_FI_DEV_GPU_UTIL should rise toward 80-90%
# DCGM_FI_DEV_FB_USED shows KV cache growing
```

## Related

- [K8s Handbook Part 11: AI Infrastructure](../28-k8s-handbook-part11-ai-infrastructure.md) — Part 1: AI Infrastructure Architecture, GPU Operator, GPU Scheduling, Distributed Training, Kubeflow, Ray, KServe, vLLM, SGLang
