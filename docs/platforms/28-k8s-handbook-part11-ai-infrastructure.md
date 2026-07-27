---
title: "K8s Handbook Part 11: AI Infrastructure"
doc_type: guide
domain: platforms
status: current
topic_id: k8s-handbook-part11-ai-infrastructure
last_reviewed: 2026-07-27
maturity: practitioner
supersedes: [docs/cloud-platforms/kubernetes/K8s_Handbook_Part11_AI_Infrastructure.md]
tags: [kubernetes, ai-infrastructure, gpu, vllm, kserve]
covers_version: "2025-2026 edition"
---

Kubernetes has become the de facto substrate for enterprise AI infrastructure. It provides the resource scheduling, workload management, and operational tooling that AI/ML workloads require. This part focuses exclusively on Kubernetes implementation patterns for AI infrastructure — not AI concepts themselves.

## AI Infrastructure Architecture on Kubernetes

### AI Workload Taxonomy

| Workload Type | Duration | Resource Pattern | K8s Resource | Restart Policy |
|---|---|---|---|---|
| LLM Inference Serving | Persistent (24x7) | Steady GPU + high RAM | Deployment + HPA/KEDA | Always |
| Batch Inference | Hours to days | High GPU burst | Job (Indexed) | OnFailure |
| Distributed Training (LLM) | Days to weeks | All GPUs, all nodes | Volcano Job / PyTorchJob | OnFailure |
| Fine-tuning (LoRA/QLoRA) | Hours to days | 1-8 GPUs | Job or Volcano Job | OnFailure |
| Hyperparameter Search | Hours | Many parallel small GPU jobs | Kubeflow Katib | OnFailure |
| Data preprocessing | Hours | CPU + large memory | Job | OnFailure |
| Embedding generation | Hours | GPU burst | Job | OnFailure |
| Notebook experiments | Interactive | Shared GPU (MIG) | StatefulSet (JupyterHub) | Always |
| Pipeline orchestration | Periodic or triggered | Minimal (orchestrator only) | CronJob or Argo WF | OnFailure |

### Reference AI Platform Architecture

The AI platform on Kubernetes is a layered architecture:

- **Layer 6: User interfaces** — Backstage AI Catalogue, JupyterHub, MLflow UI, Kubeflow Pipelines UI, Grafana AI Dashboards.
- **Layer 5: AI orchestration** — Kubeflow Pipelines, Argo Workflows, Ray, Feast Feature Store, MLflow Tracking.
- **Layer 4: Model serving** — KServe (multi-framework), vLLM (LLM-optimised), Ray Serve (distributed), Triton Inference Server.
- **Layer 3: AI gateway** — LiteLLM, OpenRouter, Kong AI Gateway; model routing, rate limiting, cost tracking, auth.
- **Layer 2: Compute scheduling** — NVIDIA GPU Operator, Volcano (gang scheduling), Karpenter (GPU node provisioning), KEDA (inference scaling).
- **Layer 1: Kubernetes foundation** — EKS/GKE/AKS with GPU node pools, Cilium (networking), Ceph/WekaFS (storage), Vault (secrets), ArgoCD (GitOps).

## NVIDIA GPU Operator

The NVIDIA GPU Operator automates the deployment and lifecycle management of all NVIDIA software components required to use GPUs in Kubernetes: drivers, container toolkit, device plugin, DCGM exporter, MIG manager, and GPU Feature Discovery. Without the GPU Operator, each component must be manually installed and maintained on every GPU node.

### GPU Operator Components

| Component | What It Installs | DaemonSet/Operator |
|---|---|---|
| Driver container | NVIDIA GPU driver on the host OS | DaemonSet (driver) |
| Container Toolkit | nvidia-container-runtime; enables GPU in containers | DaemonSet (toolkit) |
| Device Plugin | Exposes `nvidia.com/gpu` as a schedulable resource | DaemonSet (device-plugin) |
| DCGM Exporter | GPU telemetry for Prometheus | DaemonSet (dcgm-exporter) |
| GPU Feature Discovery | Detects GPU capabilities; adds node labels | DaemonSet (gfd) |
| MIG Manager | Manages MIG partitions on A100/H100 | DaemonSet (mig-manager) |
| Node Feature Discovery | General hardware feature labelling | DaemonSet (nfd) |
| Validator | Validates the GPU stack is working | Pod (validator) |

### GPU Operator Installation

```bash
# Add the NVIDIA Helm repo
helm repo add nvidia https://helm.ngc.nvidia.com/nvidia
helm repo update

# Install the GPU Operator
helm install gpu-operator nvidia/gpu-operator \
  --namespace gpu-operator --create-namespace \
  --set driver.enabled=true \
  --set driver.version=550.54.15 \
  --set toolkit.enabled=true \
  --set devicePlugin.enabled=true \
  --set dcgmExporter.enabled=true \
  --set gfd.enabled=true \
  --set mig.strategy=single \
  --set validator.plugin.env[0].name=WITH_WORKLOAD \
  --set validator.plugin.env[0].value='true'

# Verify GPU is available
kubectl get nodes -l nvidia.com/gpu.present=true
kubectl describe node GPU_NODE | grep nvidia.com
# Should show: nvidia.com/gpu: 8 (for an 8-GPU node)
```

GPU node labels added by GPU Feature Discovery include `nvidia.com/gpu.product=NVIDIA-A100-SXM4-80GB`, `nvidia.com/gpu.memory=81920` (80GB in MiB), `nvidia.com/gpu.count=8`, and `nvidia.com/gpu.family=ampere`.

### GPU Node Taint Strategy

```bash
# Taint GPU nodes to prevent non-GPU workloads consuming them
kubectl taint nodes -l nvidia.com/gpu.present=true \
  nvidia.com/gpu=true:NoSchedule
```

```yaml
# GPU workload tolerates the taint
spec:
  tolerations:
    - key: nvidia.com/gpu
      operator: Exists
      effect: NoSchedule
  containers:
    - resources:
        limits:
          nvidia.com/gpu: '1'
  # NodeSelector for a specific GPU model
  nodeSelector:
    nvidia.com/gpu.product: NVIDIA-H100-SXM5-80GB
```

## GPU Scheduling: MIG, Time-Slicing, and Multi-Instance

Full GPU allocation (one GPU per container) is often wasteful for small models or development workloads. NVIDIA provides three approaches to share GPU resources among multiple workloads, each with different isolation and performance characteristics.

### GPU Sharing Approaches

| Approach | Isolation | Memory | Performance | Best For |
|---|---|---|---|---|
| Full GPU | Complete | Dedicated 100% | 100% | LLM inference, large training |
| MIG (Multi-Instance GPU) | Hardware | Dedicated slice | Proportional to slice | Parallel small inference, dev notebooks |
| Time-slicing | Temporal only | Shared (no isolation) | Variable (context switch) | Dev workloads, testing |
| MPS (Multi-Process Service) | Process-level | Shared | High for compatible workloads | Batch inference, same-model multi-tenant |

### NVIDIA MIG (Multi-Instance GPU)

MIG partitions an A100 or H100 GPU into up to 7 hardware-isolated instances. Each instance has dedicated streaming multiprocessors (SMs), memory bandwidth, and L2 cache. Unlike time-slicing, MIG instances cannot interfere with each other.

A100 80GB MIG profiles: `1g.10gb` (1/7 GPU, 10GB VRAM, 7 instances max), `2g.20gb` (2/7 GPU, 20GB VRAM, 3 instances max), `3g.40gb` (3/7 GPU, 40GB VRAM, 2 instances max), `4g.40gb` (4/7 GPU, 40GB VRAM, 1 instance), `7g.80gb` (full GPU, 80GB VRAM, 1 instance, MIG disabled). H100 SXM5 80GB follows the same profile pattern.

```bash
# Enable MIG mode on a node (GPU Operator MIG Manager)
kubectl label node GPU_NODE nvidia.com/mig.config=all-1g.10gb
# The MIG Manager DaemonSet sees the label and configures MIG on that node

# After MIG is enabled, resources appear as:
kubectl describe node GPU_NODE | grep mig
# nvidia.com/mig-1g.10gb: 7
```

```yaml
# Request a MIG instance in a Pod
resources:
  limits:
    nvidia.com/mig-1g.10gb: '1'
```

## Distributed Training: PyTorch DDP and FSDP

Training large language models requires distributing compute across multiple GPUs and often multiple nodes. Kubernetes provides the infrastructure substrate; PyTorch provides the distributed training frameworks. Understanding the parallelism strategies is essential for designing efficient training infrastructure.

### Parallelism Strategies

| Strategy | Distributes | When to Use | Memory Reduction | K8s Pattern |
|---|---|---|---|---|
| Data Parallel (DDP) | Data batches across GPUs | Model fits in a single GPU | None (model replicated) | Job with NCCL all-reduce |
| Fully Sharded Data Parallel (FSDP) | Model parameters + gradients + optimizer | 70B+ models, limited VRAM | Up to 8x | Job with NVLink/InfiniBand |
| Tensor Parallel (TP) | Individual tensors across GPUs | Attention layers too large for 1 GPU | Proportional to TP degree | PyTorchJob, same-node GPUs |
| Pipeline Parallel (PP) | Model layers across nodes | Very deep models | Proportional to PP degree | PyTorchJob, multi-node |
| Sequence Parallel | Sequence dimension of attention | Very long context windows | Proportional | Advanced, with Megatron-LM |

### PyTorchJob with Kubeflow Training Operator

```yaml
# Distributed PyTorch training on 4 nodes x 8 GPUs = 32 GPUs total
apiVersion: kubeflow.org/v1
kind: PyTorchJob
metadata:
  name: llm-finetune-llama3-70b
  namespace: ml-training
spec:
  pytorchReplicaSpecs:
    Master:
      replicas: 1
      restartPolicy: OnFailure
      template:
        spec:
          tolerations:
            - key: nvidia.com/gpu
              operator: Exists
              effect: NoSchedule
          containers:
            - name: trainer
              image: harbor.corp/llm-trainer:v2.0
              command:
                - torchrun
                - --nproc_per_node=8
                - --nnodes=4
                - --node_rank=$(RANK)
                - --master_addr=$(MASTER_ADDR)
                - --master_port=23456
                - train_fsdp.py
                - --model=meta-llama/Llama-3-70b
                - --dataset=s3://training-data/dataset-v3
                - --output=s3://checkpoints/llama3-70b-ft-v1
              resources:
                limits: { nvidia.com/gpu: '8', memory: 1500Gi, cpu: '192' }
                requests: { nvidia.com/gpu: '8', memory: 1500Gi }
              env:
                - name: NCCL_DEBUG
                  value: INFO
                - name: NCCL_SOCKET_IFNAME
                  value: eth0
                - name: NCCL_IB_DISABLE
                  value: '0'  # Enable InfiniBand
    Worker:
      replicas: 3  # 3 workers + 1 master = 4 nodes total
```

## Kubeflow: MLOps Platform

Kubeflow is a collection of Kubernetes-native ML tools that together form an end-to-end MLOps platform. It provides pipeline orchestration, distributed training, hyperparameter optimisation, model serving, and notebook management on Kubernetes.

### Kubeflow Components

| Component | Function | CRD / API |
|---|---|---|
| Kubeflow Pipelines (KFP) | DAG-based ML workflow orchestration; tracks runs, artifacts | Pipeline, PipelineRun |
| Training Operator | Manages distributed training jobs | PyTorchJob, TFJob, MXJob, JAXJob, PaddleJob |
| Katib | Automated hyperparameter search (Bayesian, random, grid) | Experiment, Trial |
| KServe | Model serving (InferenceService) | InferenceService |
| Notebooks | JupyterHub-based notebook server management | Notebook |
| Volumes | PVC management for notebooks and pipelines | PodDefault |

### Kubeflow Pipeline Example

```python
# KFP v2 Python SDK pipeline
from kfp import dsl, compiler
from kfp.dsl import component, pipeline, Dataset, Model

@component(base_image='python:3.12', packages_to_install=['pandas', 'scikit-learn'])
def preprocess_data(input_path: str, output_dataset: dsl.Output[Dataset]):
    import pandas as pd
    df = pd.read_parquet(input_path)
    df_clean = df.dropna()
    df_clean.to_parquet(output_dataset.path)

@component(
    base_image='nvcr.io/nvidia/pytorch:24.05-py3',
    resources=dsl.ResourceSpec(accelerator_type='NVIDIA_TESLA_A100', accelerator_count=4),
)
def finetune_model(dataset: dsl.Input[Dataset], output_model: dsl.Output[Model]):
    # LoRA fine-tuning code here
    pass

@component(base_image='python:3.12', packages_to_install=['mlflow'])
def register_model(model: dsl.Input[Model], experiment_name: str):
    import mlflow
    mlflow.log_artifacts(model.path)

@pipeline(name='llm-finetune-pipeline', description='LLM fine-tuning with LoRA')
def llm_pipeline(input_path: str = 's3://data/training-v3', experiment: str = 'llama-finetune-v1'):
    preprocess_task = preprocess_data(input_path=input_path)
    finetune_task = finetune_model(dataset=preprocess_task.outputs['output_dataset'])
    register_task = register_model(
        model=finetune_task.outputs['output_model'],
        experiment_name=experiment,
    )

compiler.Compiler().compile(llm_pipeline, 'llm-pipeline.yaml')
```

## Ray and Ray Serve: Distributed AI Compute

Ray is a distributed computing framework purpose-built for AI workloads. It enables scaling Python code from a laptop to a cluster without rewriting, provides native support for GPU scheduling, and includes Ray Serve for production model serving. The KubeRay Operator manages Ray clusters on Kubernetes.

### Ray Architecture on Kubernetes

The KubeRay Operator manages `RayCluster` CRDs. The **Head Node** (Deployment) runs the Ray head process (scheduler, GCS, dashboard) and is typically CPU-only with medium memory. **Worker Groups** (Deployment or StatefulSet) can define multiple groups with different resource profiles — e.g. `cpu-workers`, `gpu-workers-a100`, `gpu-workers-h100`. A **RayJob** creates a temporary RayCluster for a single job and deletes the cluster when the job completes, ideal for batch inference and training jobs. A **RayService** is a long-running Ray Serve deployment managing the head, workers, and Serve deployment config, with zero-downtime upgrades via in-place rolling updates.

### RayCluster for LLM Inference

```yaml
apiVersion: ray.io/v1
kind: RayCluster
metadata:
  name: llm-serving-cluster
  namespace: ai-serving
spec:
  headGroupSpec:
    replicas: 1
    template:
      spec:
        containers:
          - name: ray-head
            image: rayproject/ray-ml:2.20.0-py311-gpu
            resources:
              requests: { cpu: '8', memory: 32Gi }
              limits: { cpu: '8', memory: 32Gi }
            ports:
              - containerPort: 6379   # GCS port
              - containerPort: 8265   # Dashboard
              - containerPort: 10001  # Client
  workerGroupSpecs:
    - groupName: gpu-workers
      replicas: 4
      minReplicas: 2
      maxReplicas: 8
      template:
        spec:
          tolerations:
            - key: nvidia.com/gpu
              operator: Exists
              effect: NoSchedule
          containers:
            - name: ray-worker
              image: rayproject/ray-ml:2.20.0-py311-gpu
              resources:
                requests: { cpu: '32', memory: 256Gi, nvidia.com/gpu: '4' }
                limits: { cpu: '32', memory: 256Gi, nvidia.com/gpu: '4' }
```

## KServe: Model Serving Framework

KServe (formerly KFServing, CNCF incubating) is the standard Kubernetes-native model serving framework. It abstracts model serving complexity behind a single `InferenceService` CRD, supporting multiple frameworks (PyTorch, TensorFlow, sklearn, XGBoost, Triton) with auto-scaling, canary deployments, and request batching.

### KServe Architecture

The **InferenceService controller** reconciles the `InferenceService` CRD, creating a Deployment (predictor), Service, and Istio VirtualService. The **Predictor** runs the model serving runtime (Triton, vLLM, Hugging Face TGI), loads the model from storage (S3, GCS, PVC), and exposes gRPC (port 9000) and HTTP (port 8080). An optional **Transformer** does pre/post processing before/after the predictor via custom Python code. An optional **Explainer** provides model explanation endpoints (SHAP, LIME, Captum). **Knative Serving** provides scale-to-zero and request-based autoscaling — KServe uses Knative for auto-scaling out of the box.

### InferenceService for LLM (vLLM runtime)

```yaml
apiVersion: serving.kserve.io/v1beta1
kind: InferenceService
metadata:
  name: llama3-70b-instruct
  namespace: ai-serving
  annotations:
    serving.kserve.io/deploymentMode: RawDeployment
spec:
  predictor:
    model:
      modelFormat: { name: huggingface }
      runtime: kserve-vllm
      storageUri: s3://company-models/llama3-70b-instruct
      args:
        - --tensor-parallel-size=4
        - --max-model-len=8192
        - --enable-prefix-caching
        - --dtype=bfloat16
      resources:
        requests: { nvidia.com/gpu: '4', memory: 256Gi, cpu: '16' }
        limits: { nvidia.com/gpu: '4', memory: 256Gi }
    minReplicas: 1
    maxReplicas: 4
    scaleMetric: rps    # Requests per second
    scaleTarget: 10     # Scale up when > 10 RPS per replica
```

```bash
# Query the InferenceService
curl -X POST \
  http://llama3-70b-instruct.ai-serving.svc.cluster.local/v1/chat/completions \
  -H 'Content-Type: application/json' \
  -d '{"model":"llama3-70b","messages":[{"role":"user","content":"Hello"}]}'
```

## vLLM: High-Throughput LLM Inference

vLLM is the leading open-source LLM inference engine for production deployments. It achieves 3-24x higher throughput than naive HuggingFace Transformers inference through PagedAttention (GPU memory management), continuous batching, and prefix caching. It is OpenAI-compatible and runs on Kubernetes natively.

### vLLM Key Innovations

- **PagedAttention** — traditional attention allocates GPU memory for maximum sequence length upfront, wasting memory on shorter sequences. PagedAttention manages KV cache memory in non-contiguous pages (like OS virtual memory), enabling near-100% GPU memory utilisation and 3-5x more concurrent requests per GPU.
- **Continuous Batching** — instead of waiting for a batch to complete, new requests are added to running batches as sequences finish. This eliminates GPU idle time between batches and dramatically increases throughput for mixed-length workloads.
- **Prefix Caching** — common prompt prefixes (system prompts, few-shot examples) are cached in GPU memory and reused across requests. For RAG workloads with long context, prefix caching reduces TTFT by 50-80%.
- **Tensor Parallelism** — model weights are sharded across multiple GPUs using tensor parallelism. A 70B model requiring 140GB VRAM can run across 2x 80GB GPUs (2-way tensor parallel) or 4x 40GB GPUs (4-way tensor parallel).

### vLLM Production Kubernetes Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: vllm-llama3-70b
  namespace: ai-serving
spec:
  replicas: 2
  selector:
    matchLabels: { app: vllm-llama3-70b }
  template:
    spec:
      tolerations:
        - key: nvidia.com/gpu
          operator: Exists
          effect: NoSchedule
      containers:
        - name: vllm
          image: vllm/vllm-openai:v0.5.0
          command: [python, -m, vllm.entrypoints.openai.api_server]
          args:
            - --model=/models/llama3-70b-instruct
            - --tensor-parallel-size=4
            - --max-model-len=8192
            - --enable-prefix-caching
            - --dtype=bfloat16
            - --gpu-memory-utilization=0.92
            - --max-num-batched-tokens=32768
            - --port=8000
            - --host=0.0.0.0
            - --served-model-name=llama3-70b-instruct
          resources:
            limits: { nvidia.com/gpu: '4', memory: 512Gi, cpu: '64' }
            requests: { nvidia.com/gpu: '4', memory: 512Gi, cpu: '64' }
          volumeMounts:
            - name: model-weights
              mountPath: /models
              readOnly: true
          readinessProbe:
            httpGet: { path: /health, port: 8000 }
            initialDelaySeconds: 120  # Model loading takes time
            periodSeconds: 10
          startupProbe:
            httpGet: { path: /health, port: 8000 }
            failureThreshold: 60  # Up to 10 minutes for a 70B model load
            periodSeconds: 10
      volumes:
        - name: model-weights
          persistentVolumeClaim:
            claimName: llama3-70b-weights
```

## SGLang: Structured Generation at Scale

SGLang (Structured Generation Language) is an LLM inference framework optimised for structured outputs and multi-call programmes. It provides RadixAttention (a more efficient variant of prefix caching) and is particularly well-suited for agentic workloads that involve structured JSON outputs, multi-step reasoning, and repeated calls with shared prefixes.

### SGLang vs vLLM Comparison

| Feature | vLLM | SGLang |
|---|---|---|
| Architecture | PagedAttention + continuous batching | RadixAttention + compressed FSM |
| Structured output | Via guided generation (slow) | Native compressed finite-state machine (fast) |
| Prefix caching | Block-level prefix cache | Radix tree (more granular sharing) |
| Multi-call programs | Not native | Native via SGL language primitives |
| JSON schema enforcement | Outlines integration | Built-in, 10x faster than vLLM+outlines |
| DP Attention | Partial | Full data parallelism in disaggregated serving |
| Best for | General LLM serving, high throughput | Agentic AI, structured output, tool calling |

### SGLang Kubernetes Deployment

```yaml
# SGLang server deployment
containers:
  - name: sglang
    image: lmsysorg/sglang:latest-cu121
    command: [python, -m, sglang.launch_server]
    args:
      - --model-path=/models/qwen2.5-72b-instruct
      - --tp=4
      - --port=30000
      - --host=0.0.0.0
      - --enable-torch-compile  # Torch compile for 20% speedup
      - --max-prefill-tokens=16384
    resources:
      limits: { nvidia.com/gpu: '4', memory: 512Gi }
```

## Related

- [K8s Handbook Part 11: AI Infrastructure (Part 2)](parts/28-k8s-handbook-part11-ai-infrastructure-part2.md) — AI gateways, feature stores, MLflow, vector databases, alternative accelerators (AMD ROCm, Intel Gaudi), cost optimisation, anti-patterns, and exercises
