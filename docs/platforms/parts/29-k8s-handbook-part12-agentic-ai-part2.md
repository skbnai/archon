---
title: "K8s Handbook Part 12: Agentic AI (Part 2)"
doc_type: guide
domain: platforms
status: current
topic_id: k8s-handbook-part12-agentic-ai-part2
last_reviewed: 2026-07-27
maturity: practitioner
supersedes: []
tags: [kubernetes, agentic-ai, autoscaling, multi-tenancy, tool-registry]
covers_version: "2025-2026 edition"
---

> Continues from [K8s Handbook Part 12: Agentic AI](../29-k8s-handbook-part12-agentic-ai.md), covering Chapters 6-13: A2A communication, agent scheduling, autoscaling, runtime isolation, memory services, and tool/prompt/agent registries.

## A2A Communication Across Clusters

Agent-to-Agent (A2A) communication in enterprise environments must cross cluster, namespace, and sometimes regional boundaries. Kubernetes provides the networking primitives; the A2A protocol layer sits on top of standard HTTP/gRPC or message queue infrastructure.

### A2A Communication Patterns

| Pattern | Transport | Kubernetes Implementation | Best For |
|---|---|---|---|
| Synchronous HTTP | HTTP/gRPC | Service + Ingress/Gateway API | Request-response, real-time |
| Async via message queue | Kafka / NATS / SQS | Strimzi Kafka or NATS Operator | Decoupled, high-throughput |
| Event-driven | CloudEvents / Kafka | KEDA triggers on events | Reactive agent activation |
| Shared state | Redis / PostgreSQL | StatefulSet | Shared working memory between agents |
| Cross-cluster direct | Cilium Cluster Mesh | ClusterMesh service export | Low-latency cross-cluster |
| Cross-cluster via gateway | HTTP + mTLS | Istio multi-cluster / Linkerd | Federated agent networks |

### A2A via Kafka on Kubernetes

```yaml
# Strimzi Kafka for agent message bus
apiVersion: kafka.strimzi.io/v1beta2
kind: Kafka
metadata:
  name: agent-bus
  namespace: ai-platform
spec:
  kafka:
    replicas: 3
    listeners:
      - name: plain
        port: 9092
        type: internal
        tls: false
      - name: tls
        port: 9093
        type: internal
        tls: true
    storage: { type: persistent-claim, size: 100Gi, class: fast-ssd }
  zookeeper:
    replicas: 3
    storage: { type: persistent-claim, size: 10Gi }
```

Agent topics: `ai-agents.task-requests` (orchestrator → worker agents), `ai-agents.task-results` (worker agents → orchestrator), `ai-agents.tool-calls` (agents → MCP servers), `ai-agents.tool-results` (MCP servers → agents), `ai-agents.events` (system-wide agent lifecycle events).

```yaml
# KEDA trigger: scale agent workers on Kafka lag
triggers:
  - type: kafka
    metadata:
      bootstrapServers: agent-bus-kafka-bootstrap.ai-platform:9092
      consumerGroup: research-agent-workers
      topic: ai-agents.task-requests
      lagThreshold: '10'
      offsetResetPolicy: latest
```

### Cross-Cluster A2A with Cilium Cluster Mesh

```bash
# Export the agent API Service from cluster-1 to cluster-2
# (On cluster-1) Annotate the Service for global visibility
kubectl annotate service agent-orchestrator \
  -n ai-agents \
  service.cilium.io/global=true \
  service.cilium.io/shared=true
# On cluster-2, agents can now call:
#   http://agent-orchestrator.ai-agents.svc.cluster.local
# Traffic is load-balanced across both clusters' endpoints.

# For isolation (cluster-1 endpoints only preferred)
kubectl annotate service agent-orchestrator \
  service.cilium.io/global=true \
  service.cilium.io/shared=false  # Only exported, not imported
```

## Agent Scheduling and GPU-Aware Placement

Agent workloads have diverse and often unpredictable resource requirements. A research agent might spawn sub-agents that require different compute profiles: a web scraper (CPU only), a summarisation step (GPU), a code execution sandbox (isolated CPU), and a database query (CPU + network). Kubernetes scheduling must handle this heterogeneity efficiently.

### Agent Worker Pod Resource Profiles

| Worker Type | CPU | Memory | GPU | RuntimeClass | Use Case |
|---|---|---|---|---|---|
| Orchestrator | 2-4 cores | 4-8 GB | None | runc | Agent planning, routing, coordination |
| LLM Caller | 1-2 cores | 2-4 GB | None | runc | LLM API calls, response parsing |
| Tool Executor | 1-2 cores | 2-4 GB | None | runc or gVisor | Web search, API calls, file read |
| Code Executor | 2-4 cores | 4-8 GB | None | gVisor or Kata | Sandboxed code execution |
| Local Inference | 8-16 cores | 64-256 GB | 1-4 GPUs | runc | On-premise LLM, embedding |
| Data Processor | 4-16 cores | 16-64 GB | Optional | runc | ETL, RAG ingestion, chunking |

### Node Pool Strategy for Agentic AI

Recommended node pool architecture:

- **Node Pool 1: cpu-general** — `c5.2xlarge` (8 CPU, 16 GB) for orchestrators, LLM callers, tool executors; no taints (default pool).
- **Node Pool 2: cpu-memory-optimised** — `r5.4xlarge` (16 CPU, 128 GB) for RAG ingestion, embedding generation, data processing; tainted `workload-type=memory-intensive:NoSchedule`.
- **Node Pool 3: gpu-inference** — `g5.12xlarge` (48 CPU, 192 GB, 4x A10G) for local LLM inference and embedding models; tainted `nvidia.com/gpu=true:NoSchedule`.
- **Node Pool 4: gpu-training** — `p4d.24xlarge` (96 CPU, 1152 GB, 8x A100) for fine-tuning and RAG embedding generation at scale; tainted `nvidia.com/gpu=true:NoSchedule` and `workload-type=training:NoSchedule`.
- **Node Pool 5: isolated-execution** — `c5.xlarge` (4 CPU, 8 GB) for code execution (gVisor) and untrusted tool calls; tainted `workload-type=isolated:NoSchedule`, with the `gvisor` RuntimeClass enforced via Kyverno.

## Autoscaling Strategies for Agent Workloads

Agent workloads exhibit extreme burstiness that standard CPU/memory-based autoscaling handles poorly. A single customer request can spawn 0 to 100 sub-agent tasks in milliseconds, requiring the platform to scale from 2 to 200 workers in seconds. KEDA event-driven autoscaling is the correct tool for this pattern.

### KEDA for Agent Worker Scaling

```yaml
# Scale agent workers based on Kafka topic lag
apiVersion: keda.sh/v1alpha1
kind: ScaledObject
metadata:
  name: research-agent-workers
  namespace: ai-agents
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: research-agent-worker
  minReplicaCount: 2    # Always-warm minimum
  maxReplicaCount: 100  # Peak capacity
  cooldownPeriod: 120   # 2 min before scale-down
  pollingInterval: 5
  triggers:
    - type: kafka
      metadata:
        bootstrapServers: agent-bus-kafka-bootstrap:9092
        consumerGroup: research-agents
        topic: ai-agents.task-requests
        lagThreshold: '5'  # 1 worker per 5 pending tasks
        offsetResetPolicy: latest
    - type: prometheus
      metadata:
        serverAddress: http://prometheus:9090
        metricName: agent_active_sessions
        query: sum(agent_sessions_active)
        threshold: '10'  # 1 worker per 10 active sessions
  advanced:
    restoreToOriginalReplicaCount: false
    horizontalPodAutoscalerConfig:
      behavior:
        scaleUp:
          stabilizationWindowSeconds: 0  # Scale up immediately
          policies:
            - type: Percent
              value: 200  # Can triple in one step
              periodSeconds: 15
        scaleDown:
          stabilizationWindowSeconds: 300  # Wait 5 min before scale-down
```

### Karpenter for Dynamic GPU Node Provisioning

```yaml
# Karpenter NodePool for GPU agent workers
apiVersion: karpenter.sh/v1
kind: NodePool
metadata:
  name: gpu-agent-nodes
spec:
  template:
    metadata:
      labels: { node-type: gpu-agent }
    spec:
      nodeClassRef:
        apiVersion: karpenter.k8s.aws/v1
        kind: EC2NodeClass
        name: gpu-node-class
      requirements:
        - key: karpenter.k8s.aws/instance-family
          operator: In
          values: [g5, p3, p4d]
        - key: karpenter.sh/capacity-type
          operator: In
          values: [spot, on-demand]  # Prefer spot for cost
      taints:
        - key: nvidia.com/gpu
          value: 'true'
          effect: NoSchedule
  disruption:
    consolidationPolicy: WhenEmpty  # Remove idle GPU nodes
    consolidateAfter: 5m
```

## Runtime Isolation for Multi-Tenant Agents

Multi-tenant agentic AI platforms must isolate workloads from different customers or teams at multiple levels: compute, network, credentials, and data. The appropriate isolation level depends on the trust model and regulatory requirements.

### Isolation Levels for Agentic AI

| Isolation Level | Mechanism | Attack Surface | Overhead | Use Case |
|---|---|---|---|---|
| Namespace | RBAC + NetworkPolicy + ResourceQuota | Shared kernel | Minimal | Internal teams, trusted tenants |
| vCluster | Virtual K8s cluster per tenant | Shared kernel (namespaces) | Low | Dev environments, isolated control planes |
| gVisor (runsc) | User-space kernel per container | Separate user-space kernel | 10-20% | Semi-trusted agent code, SaaS |
| Kata Containers | VM per Pod | Separate VM kernel | 3-8% | Untrusted tenant code, regulated |
| Cluster per tenant | Separate cluster | Fully isolated | Highest | High-value customers, compliance-driven |

### Kata Containers for Untrusted Agent Code Execution

```yaml
# Enforce Kata for all agent code execution in a namespace
# Kyverno policy: code-exec namespace must use kata RuntimeClass
apiVersion: kyverno.io/v1
kind: ClusterPolicy
metadata:
  name: require-kata-in-code-exec-ns
spec:
  validationFailureAction: Enforce
  rules:
    - name: require-kata-runtime
      match:
        resources:
          kinds: [Pod]
          namespaces: [agent-code-execution]
      validate:
        message: Code execution namespace requires Kata Containers runtime
        pattern:
          spec:
            runtimeClassName: kata-qemu
---
# Code execution agent Pod
spec:
  runtimeClassName: kata-qemu  # VM isolation
  securityContext:
    runAsNonRoot: true
    seccompProfile: { type: RuntimeDefault }
  containers:
    - name: code-executor
      image: harbor.corp/sandbox-executor:v1
      resources:
        limits: { cpu: 2, memory: 4Gi }
      securityContext:
        readOnlyRootFilesystem: true
        capabilities: { drop: [ALL] }
```

## Externalized Memory Services on Kubernetes

Agentic AI systems require multiple categories of memory, each with different latency, persistence, and sharing requirements. All memory is externalised from agent Pods into dedicated Kubernetes services, enabling stateless agent execution and horizontal scaling.

### Memory Architecture

| Memory Type | Content | Latency | Persistence | Kubernetes Service |
|---|---|---|---|---|
| Working memory | Current task context, conversation turns | < 1ms | Session duration | Redis (in-memory) |
| Episodic memory | Past agent interactions, action history | < 5ms | Long-term | PostgreSQL + TimescaleDB |
| Semantic memory | Encoded knowledge, embeddings, facts | < 10ms | Permanent | Qdrant / Milvus / pgvector |
| Procedural memory | Tool definitions, agent prompts, workflows | < 1ms | Version-controlled | ConfigMap / Prompt Registry |
| Working set cache | Recently retrieved documents, tool outputs | < 1ms | Short-term | Redis with TTL |
| Entity memory | User/entity profiles, preferences | < 5ms | Long-term | Feast Feature Store + Redis |

### Redis for Agent Working Memory

```bash
# Redis deployment for agent session memory
# Using Bitnami Redis Sentinel for HA
helm install redis bitnami/redis \
  --namespace ai-agents \
  --set architecture=replication \
  --set auth.enabled=true \
  --set auth.existingSecret=redis-secret \
  --set replica.replicaCount=2 \
  --set master.persistence.size=50Gi \
  --set master.persistence.storageClass=fast-ssd
```

Agent working memory patterns: session context at `agent:session:{id}:context` (TTL: 1 hour); tool cache at `agent:tool_cache:{hash}` (TTL: 5 minutes); rate limiting at `agent:ratelimit:{user_id}` (TTL: 1 minute); active sessions in `agent:active_sessions` (a sorted set by `last_seen`).

```
# Memory management: automatically evict LRU on memory pressure
maxmemory 50gb
maxmemory-policy allkeys-lru
maxmemory-samples 10
```

## Tool Registry and Tool Lifecycle Management

A tool registry is the system of record for all tools available to agents. It stores tool definitions, versions, access policies, SLAs, and deployment status. Without a tool registry, tool discovery is ad-hoc, versioning is uncontrolled, and access governance is impossible at enterprise scale.

### Tool Registry Design

```yaml
# Tool Registry CRD-based approach
apiVersion: ai.company.com/v1alpha1
kind: AgentTool
metadata:
  name: web-search-v2
  namespace: ai-platform
  labels:
    tool-category: information-retrieval
    tool-version: v2.1.0
    data-classification: public
  annotations:
    tool.ai.company.com/owner: platform-team
    tool.ai.company.com/sla: '99.9'
    tool.ai.company.com/max-latency-ms: '2000'
spec:
  description: Search the web for information using Tavily API
  mcp_server:
    service: mcp-tools-server
    namespace: ai-platform
    port: 8080
    tool_name: web_search
  input_schema:
    type: object
    properties:
      query: { type: string, description: Search query }
      max_results: { type: integer, default: 10 }
    required: [query]
  access_policy:
    allowed_namespaces: [ai-agents, ai-research, ai-support]
    allowed_service_accounts: [research-agent-sa, support-agent-sa]
    rate_limit: 100/minute/service_account
  cost_model:
    cost_per_call: 0.001  # USD
    billing_dimension: requests
```

### Tool Lifecycle Governance

- **Development** — the tool author registers the tool in the dev namespace; integration tests run via Argo Workflows; a security scan runs SBOM + CVE checks on the tool container image.
- **Staging** — the tool is promoted to staging via a GitOps PR, load-tested at target RPS, and the access policy is reviewed by the security team.
- **Production** — the tool is available in the production tool registry; a Backstage catalogue entry is created automatically; a Prometheus ServiceMonitor is deployed for observability.
- **Deprecation** — a new version is released, and the old version is marked deprecated; agents pinned to the old version receive upgrade notifications; traffic migrates via canary (Argo Rollouts).
- **Retirement** — the old version is removed from the registry; agent configurations referencing retired tools are flagged by an admission webhook; the audit trail is preserved.

## Prompt Registry and Prompt Lifecycle

In enterprise agentic AI, system prompts, few-shot examples, and instruction templates are operational assets that must be versioned, tested, reviewed, and deployed with the same rigour as application code. A prompt registry provides the governance infrastructure for the prompt lifecycle.

### Prompt Registry Implementation Options

| Approach | Storage | Versioning | Access | Best For |
|---|---|---|---|---|
| Git + ConfigMap | ConfigMap in cluster | Git history (immutable) | Kubernetes RBAC | Simple; GitOps-native |
| LangSmith Hub | LangSmith cloud | Semantic versioning | API key | LangChain users |
| Weights and Biases | W&B Artifacts | Run-linked versioning | W&B API | ML-heavy teams |
| Custom CRD (Prompt resource) | etcd via K8s API | ResourceVersion + labels | RBAC + admission | Enterprise governance |
| Database + API service | PostgreSQL + REST API | Full semantic versioning | OIDC + RBAC | Largest scale; audit requirements |

### ConfigMap-Based Prompt Registry (GitOps)

```yaml
# Prompt stored as ConfigMap (versioned via GitOps)
apiVersion: v1
kind: ConfigMap
metadata:
  name: prompt-research-agent-v3
  namespace: ai-platform
  labels:
    prompt-name: research-agent
    prompt-version: v3.2.1
    prompt-type: system
    model-family: gpt-4
    language: en
  annotations:
    prompt.ai.company.com/owner: ai-platform-team
    prompt.ai.company.com/approved-by: alice@company.com
    prompt.ai.company.com/approved-at: 2025-06-01T10:00:00Z
    prompt.ai.company.com/test-results: passed (100% evals)
data:
  system_prompt: |
    You are an enterprise research analyst with access to web search,
    database query, and document analysis tools. Always cite sources.
    Never reveal internal company data. Response format: structured
    JSON with citations.
  few_shot_examples: |
    [Example 1: Research query -> structured response]
    [Example 2: Multi-step research with tool use]
---
# Agent deployment mounts the prompt as a volume
volumes:
  - name: agent-prompts
    configMap: { name: prompt-research-agent-v3 }
containers:
  - volumeMounts:
      - name: agent-prompts
        mountPath: /prompts
        readOnly: true
    env:
      - name: SYSTEM_PROMPT_PATH
        value: /prompts/system_prompt
```

## Agent Registry and Agent Governance

As enterprise agent deployments scale to hundreds of specialised agents, an agent registry becomes essential: a directory of available agents, their capabilities, access policies, resource requirements, and deployment status. The agent registry integrates with Backstage for discoverability and with Kubernetes RBAC for governance.

### Agent CRD Design

```yaml
apiVersion: ai.company.com/v1alpha1
kind: Agent
metadata:
  name: research-agent-v3
  namespace: ai-agents
  labels:
    agent-type: research
    agent-version: v3.0.0
    data-classification: confidential
spec:
  description: Enterprise research agent for market analysis
  capabilities: [web_search, document_analysis, database_query, report_generation]
  model_config:
    primary_model: gpt-4o
    fallback_model: claude-3-5-sonnet
    embedding_model: text-embedding-3-large
  prompt_ref:
    configmap: prompt-research-agent-v3
    namespace: ai-platform
  tool_refs:
    - name: web-search-v2
      namespace: ai-platform
    - name: database-query-v1
      namespace: ai-platform
  resource_requirements:
    cpu: 2
    memory: 4Gi
    max_concurrent_tasks: 10
    max_context_tokens: 128000
  access_policy:
    allowed_callers:
      - service_account: research-portal-sa
        namespace: research-portal
      - service_account: executive-assistant-sa
        namespace: executive-tools
  data_access:
    allowed_data_sources: [public-web, internal-kb]
    forbidden_data_sources: [pii-database, financial-records]
```

## Related

- [K8s Handbook Part 12: Agentic AI](../29-k8s-handbook-part12-agentic-ai.md) — Part 1: Kubernetes as the Agentic AI Substrate, Stateless vs Stateful Execution, Temporal, Argo Workflows, MCP Server Deployment
- [K8s Handbook Part 12: Agentic AI (Part 3)](29-k8s-handbook-part12-agentic-ai-part3.md) — workload identity, AI observability, GitOps for AI assets, sovereign AI, multi-region architectures, disaster recovery, exercises
