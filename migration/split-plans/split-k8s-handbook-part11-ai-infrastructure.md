# Split Plan: K8s Handbook Part 11 — AI Infrastructure

**Source:** `/workspace/knowledge-docs/docs/cloud-platforms/kubernetes/K8s_Handbook_Part11_AI_Infrastructure.md` (~4,052 words body)

**Reason:** Word count exceeds guide doc_type cap (2600 words hard cap)

## Split Boundary

**Part 1 (Main):** `docs/platforms/28-k8s-handbook-part11-ai-infrastructure.md`
- Source: Chapters 1–9 (AI Infrastructure Architecture on Kubernetes, NVIDIA GPU Operator, GPU Scheduling: MIG/Time-Slicing/MPS, Distributed Training: PyTorch DDP and FSDP, Kubeflow, Ray and Ray Serve, KServe, vLLM, SGLang)
- Content: the AI workload taxonomy and reference AI platform architecture (layered stack), GPU Operator components/installation/node taint strategy, GPU sharing approaches and NVIDIA MIG profiles, distributed training parallelism strategies and a PyTorchJob/Kubeflow Training Operator example, Kubeflow components and a KFP v2 pipeline example, Ray/KubeRay architecture and a RayCluster for LLM inference, KServe architecture and an InferenceService for vLLM, vLLM's key innovations (PagedAttention, continuous batching, prefix caching, tensor parallelism) and a production Deployment, SGLang vs vLLM comparison and a deployment example

**Part 2 (Supplementary):** `docs/platforms/parts/28-k8s-handbook-part11-ai-infrastructure-part2.md`
- Source: Chapters 10–17 (AI Gateways and Model Routing, Feature Stores with Feast, MLflow, Vector Databases on Kubernetes, AMD ROCm and Intel Gaudi Support, AI Infrastructure Cost Optimisation, AI Infrastructure Anti-Patterns, Hands-On Exercises)
- Content: AI gateway capabilities and a LiteLLM Proxy deployment, Feast feature store architecture, MLflow components on Kubernetes, a vector database comparison and Milvus Operator deployment, AMD ROCm/Intel Gaudi accelerator comparison and ROCm device plugin install, AI infrastructure cost optimisation strategies, 5 AI infrastructure anti-patterns, 2 hands-on exercises

## Source-quality notes (converted-pdf artifacts fixed during migration)

- Numerous flattened multi-line YAML/shell/Python blocks reconstructed into properly line-broken fenced blocks (GPU Operator Helm install, MIG profile configuration, PyTorchJob, KFP v2 pipeline, RayCluster, KServe InferenceService, vLLM production Deployment, SGLang deployment, and other chapters' examples).
- No content-loss (heading-then-nothing) artifacts were found in this source; all chapters retained their body text.

## Navigation

- Part 1 ends with a pointer to Part 2 (AI gateways, feature stores, MLflow, vector databases, alternative accelerators, cost optimisation, anti-patterns, exercises).
- Topic ID: both parts share the `k8s-handbook-part11-ai-infrastructure` topic family.
- Part 1 is canonical (`topic_id: k8s-handbook-part11-ai-infrastructure`).
- Part 2 uses `topic_id: k8s-handbook-part11-ai-infrastructure-part2`, `supersedes: []` (Part 1 carries the supersedes entry).
