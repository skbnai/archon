---
title: "K8s Handbook Part 12: Agentic AI (Part 3)"
doc_type: guide
domain: platforms
status: current
topic_id: k8s-handbook-part12-agentic-ai-part3
last_reviewed: 2026-07-27
maturity: practitioner
supersedes: []
tags: [kubernetes, agentic-ai, sovereign-ai, disaster-recovery, gitops]
covers_version: "2025-2026 edition"
---

> Continues from [K8s Handbook Part 12: Agentic AI](../29-k8s-handbook-part12-agentic-ai.md) and [Part 2](29-k8s-handbook-part12-agentic-ai-part2.md), covering Chapters 14-20: workload identity, AI observability, GitOps for AI assets, sovereign AI, multi-region architectures, disaster recovery, and hands-on exercises.

## Workload Identity and Secret Management for Agents

Each agent must have a unique, verifiable identity for accessing external services, calling other agents, and leaving audit trails. Kubernetes Service Accounts combined with SPIFFE/SPIRE or cloud workload identity provide cryptographic agent identity without managing long-lived credentials.

### Agent Identity Architecture

The agent identity hierarchy has three layers. **Agent Type Identity** (shared by all instances of an agent type) consists of a ServiceAccount (e.g. `research-agent-sa`) with a SPIFFE ID (`spiffe://company.com/ns/ai-agents/sa/research-agent-sa`) and a bound token with a 1-hour TTL, auto-rotated by kubelet. **Agent Instance Identity** (unique to each running instance) is the Pod name (e.g. `research-agent-7d9f8-abc12`), included in audit logs for forensic tracing. **Session Identity** (unique to each agent session) is a generated `session_id` (`uuid4()`), propagated in the `X-Agent-Session-ID` header and as the Kafka message key, used for multi-turn conversation correlation and cost attribution.

Cloud resource access flows through Workload Identity: on GKE, `research-agent-sa` maps to a GCP Service Account, which accesses S3/GCS/BigQuery; on EKS, `research-agent-sa` maps to an IAM Role (IRSA), which accesses S3/DynamoDB/Bedrock.

### Secret Injection for Agent Tools

```yaml
# External Secrets Operator: sync tool API keys from Vault
apiVersion: external-secrets.io/v1beta1
kind: ExternalSecret
metadata:
  name: agent-tool-secrets
  namespace: ai-agents
spec:
  refreshInterval: 1h
  secretStoreRef:
    name: vault-backend
    kind: ClusterSecretStore
  target:
    name: agent-tool-secrets
    creationPolicy: Owner
  data:
    - secretKey: tavily-api-key
      remoteRef: { key: secret/ai-agents/tools, property: tavily-api-key }
    - secretKey: anthropic-api-key
      remoteRef: { key: secret/ai-agents/models, property: anthropic-api-key }
---
# Agent Pod uses a projected volume for secrets
volumes:
  - name: agent-secrets
    secret:
      secretName: agent-tool-secrets
      defaultMode: 0400  # Read-only for owner only
containers:
  - volumeMounts:
      - name: agent-secrets
        mountPath: /run/secrets/agent
        readOnly: true
    # Never use env vars for secrets!
    env:
      - name: SECRETS_PATH
        value: /run/secrets/agent
```

## AI Observability for Multi-Agent Systems

Observing multi-agent systems requires tracking causality across dozens of LLM calls, tool executions, and sub-agent invocations that compose a single user request. Standard APM tools are insufficient; AI-specific observability must capture model inputs/outputs, tool call chains, token costs, and agent decision points.

### Agent Observability Signals

| Signal | What to Capture | Tool | Retention |
|---|---|---|---|
| Agent trace | Full span tree: user request → orchestrator → sub-agents → tools → LLMs | Tempo / Jaeger | 30 days |
| LLM call spans | Model, prompt hash, tokens (in/out), latency, finish reason | OpenTelemetry + Tempo | 30 days |
| Tool call spans | Tool name, input hash, output hash, latency, success/failure | OpenTelemetry + Tempo | 30 days |
| Agent session log | Complete conversation with tool calls (structured JSON) | Loki | 90 days |
| Token usage metrics | Tokens per model per session per agent per user | Prometheus | 1 year |
| Agent cost metrics | USD cost per session, task, agent type, user | OpenCost + custom | 1 year |
| Error and retry events | Failed LLM calls, tool timeouts, retries with context | Prometheus + Loki | 90 days |
| Agent decision log | Which agent was chosen, why, confidence (if available) | Loki structured log | 1 year (compliance) |

### OpenTelemetry for Agent Tracing

```python
# Python agent with OTel instrumentation
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter

tracer = trace.get_tracer('research-agent', '3.0.0')

async def run_agent_task(task: AgentTask) -> AgentResult:
    with tracer.start_as_current_span('agent.run') as span:
        span.set_attribute('agent.type', 'research')
        span.set_attribute('agent.session_id', task.session_id)
        span.set_attribute('agent.task_id', task.task_id)
        span.set_attribute('agent.user_id', task.user_id)

        with tracer.start_as_current_span('agent.llm_call') as llm_span:
            llm_span.set_attribute('gen_ai.system', 'openai')
            llm_span.set_attribute('gen_ai.request.model', 'gpt-4o')
            response = await call_llm(task.prompt)
            llm_span.set_attribute('gen_ai.usage.prompt_tokens', response.usage.prompt_tokens)
            llm_span.set_attribute('gen_ai.usage.completion_tokens', response.usage.completion_tokens)

            if response.tool_calls:
                for tool_call in response.tool_calls:
                    with tracer.start_as_current_span('agent.tool_call') as tc_span:
                        tc_span.set_attribute('tool.name', tool_call.function.name)
                        result = await execute_tool(tool_call)
                        tc_span.set_attribute('tool.success', result.success)

        return AgentResult(response=response.content)
```

## GitOps for AI Assets

GitOps principles apply to AI assets as much as to application deployments. Prompts, agent configurations, tool registries, model deployments, and pipeline definitions should all be managed via Git with pull-request-based review and automated deployment via ArgoCD or Flux.

### AI GitOps Repository Structure

```
ai-gitops/
  agents/
    research-agent/
      agent.yaml            # Agent CRD definition
      deployment.yaml        # Worker Deployment
      keda-scaler.yaml         # KEDA ScaledObject
      servicemonitor.yaml        # Prometheus metrics
  prompts/
    research-agent/
      v3.2.1/
        system_prompt.txt    # System prompt (Git-versioned)
        few_shot.json          # Few-shot examples
        eval_results.json        # Test results (must pass before merge)
        configmap.yaml             # K8s ConfigMap for prompt
  tools/
    web-search/
      v2.1.0/
        tool.yaml             # AgentTool CRD
        deployment.yaml         # MCP server Deployment
        tests/                    # Tool integration tests
  models/
    llama3-70b-instruct/
      v1.0/
        inference-service.yaml   # KServe InferenceService
        vllm-deployment.yaml       # vLLM Deployment
        model-metrics.yaml           # ServiceMonitor
  pipelines/
    research-pipeline/
      workflow.yaml           # Argo Workflow template
      temporal-workflow.py     # Temporal workflow code
  config/
    ai-gateway/
      litellm-config.yaml    # Model routing config
    policies/
      agent-rbac.yaml       # RBAC for agent service accounts
```

### Prompt CI/CD Pipeline

```yaml
# .github/workflows/prompt-release.yaml
# Automated prompt evaluation before deployment
name: Prompt CI/CD
on:
  pull_request:
    paths: ['prompts/**']
jobs:
  evaluate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Run prompt evaluation suite
        run: |
          python -m pytest prompts/research-agent/v3.2.1/evals/ \
            --llm-provider openai \
            --min-pass-rate 0.95 \
            --output eval_results.json
      - name: Check for prompt injection vulnerabilities
        run: python -m prompt_security_scan prompts/
      - name: Update eval results in repo
        run: |
          cp eval_results.json prompts/research-agent/v3.2.1/eval_results.json
          git add -A && git commit -m 'Update eval results'
  deploy:
    needs: evaluate
    if: github.ref == 'refs/heads/main'
    steps:
      - name: ArgoCD sync
        run: argocd app sync prompts-production
```

## Sovereign AI Deployments

Sovereign AI refers to deploying AI infrastructure entirely within a specific jurisdiction, with full control over data, models, and compute — no data leaving the sovereign boundary. This is required for government agencies, regulated financial services, healthcare data, and enterprises operating under data residency requirements.

### Sovereign AI Requirements

- **Data residency** — all data processed by agents must remain within the geographic and legal jurisdiction specified; no data sent to external LLM APIs; no telemetry or logs leaving the boundary.
- **Model sovereignty** — LLM models deployed on-premise or in a sovereign cloud, with no dependency on external model providers (OpenAI, Anthropic); models must be hosted entirely within the sovereign boundary.
- **Supply chain control** — all software components (container images, dependencies) pulled from internal registries, not the public internet; an air-gapped cluster with no outbound internet access.
- **Cryptographic control** — encryption keys managed within the sovereign boundary (on-premise HSM or sovereign cloud KMS), with no key material accessible by the cloud provider or third parties.
- **Audit and compliance** — a complete audit trail of all agent actions, data access, and model invocations, stored within the sovereign boundary and exportable for regulatory inspection.

### Air-Gapped Kubernetes for Sovereign AI

The air-gapped deployment architecture splits into two zones. The **internet-connected DMZ zone** hosts the CI/CD system (which pulls approved packages from the internet) and an artifact repository (storing approved, scanned images). A **one-way data diode / transfer mechanism** connects the DMZ to the **sovereign (air-gapped) zone**, which contains an internal Harbor registry (receiving images from the DMZ), the Kubernetes cluster (pulling only from the internal registry), all LLM models stored on internal NFS/Ceph, an internal HSM for key management, an internal OIDC provider (no external identity), and observability data that stays entirely in-cluster.

```toml
# containerd mirror config for the air-gapped cluster
[plugins.'io.containerd.grpc.v1.cri'.registry.mirrors]
  [plugins.'io.containerd.grpc.v1.cri'.registry.mirrors.'docker.io']
    endpoint = ['https://harbor.internal.sovereign:443/v2/dockerhub-mirror']
  [plugins.'io.containerd.grpc.v1.cri'.registry.mirrors.'quay.io']
    endpoint = ['https://harbor.internal.sovereign:443/v2/quay-mirror']
  [plugins.'io.containerd.grpc.v1.cri'.registry.mirrors.'registry.k8s.io']
    endpoint = ['https://harbor.internal.sovereign:443/v2/k8s-mirror']
```

```yaml
# Kyverno policy: no external registry images allowed
spec:
  validationFailureAction: Enforce
  rules:
    - name: only-internal-registry
      validate:
        message: Only harbor.internal.sovereign images allowed
        pattern:
          spec:
            containers:
              - image: harbor.internal.sovereign/*
```

## Multi-Region Agentic AI Architectures

Enterprise agentic AI platforms serving global users require multi-region deployment to meet latency requirements, data residency regulations, and availability SLAs. The architecture must balance consistency (shared knowledge base, model versions) with locality (data residency, low latency).

### Multi-Region Architecture Patterns

| Pattern | Data Locality | Latency | Complexity | Best For |
|---|---|---|---|---|
| Active-Active | Replicated across regions | Lowest (local routing) | Highest | Global SaaS, no strict residency |
| Active-Passive | Primary region; failover | Medium (failover) | Medium | HA without global latency |
| Region-per-jurisdiction | Strict per-region isolation | Medium | Medium | GDPR, data residency laws |
| Hub-spoke | Central hub; regional spokes | Medium | Medium-high | Central governance, regional execution |

### Hub-Spoke Agent Architecture

The hub-spoke pattern for regulated enterprises centralises governance while keeping execution and data regional. The **hub cluster** (`us-east-1`, primary) hosts the Agent Registry (central directory of all agents), the Prompt Registry (canonical prompt versions), the Tool Registry (canonical tool definitions), the MLflow Model Registry (central model catalogue), ArgoCD (managing all spoke clusters via GitOps), and Vault (secret distribution to spoke clusters).

The **EU spoke cluster** (`eu-west-1`, GDPR boundary) runs Agent Workers processing EU user requests, local EU-resident LLM inference, Redis holding only EU user session memory, and a vector DB holding only the EU knowledge base — data never leaves the EU boundary. The **APAC spoke cluster** (`ap-southeast-1`) mirrors this with APAC-resident Redis and vector DB data.

Cross-cluster communication: Hub → Spokes flows via GitOps (ArgoCD ApplicationSets) and Vault secret sync (enterprise replication); Spoke → Hub flows via metrics (Thanos multi-cluster query) and logs (Loki multi-tenant, region-labelled). Spoke → Spoke communication is **not allowed** — no cross-boundary data flow.

## Disaster Recovery for Agentic Platforms

Agentic AI platforms introduce unique DR challenges: in-flight agent workflows that may be mid-execution, accumulated vector database indexes, trained model weights, and complex multi-service state. A DR strategy must address each component with appropriate RPO and RTO targets.

### Component-Level DR Strategy

| Component | DR Strategy | RPO | RTO | Implementation |
|---|---|---|---|---|
| Kubernetes cluster | Velero backup + standby cluster | 1 hour | 30 min | Velero daily + Velero pre-change |
| etcd (cluster state) | Snapshot to S3 every 30 min | 30 min | 15 min | Automated etcd backup CronJob |
| Agent workflows (Temporal) | Temporal persistence replicated (Cassandra multi-DC) | Near-zero | Minutes | Temporal HA with multi-region DB |
| Agent workflows (Argo) | Workflow CRDs in etcd; etcd backup | 1 hour | 30 min | Velero includes etcd backup |
| Redis (session memory) | Redis replication + Velero RDB snapshot | 15 min | 10 min | Redis Sentinel HA + backup |
| PostgreSQL (agent history) | Streaming replication + pgBackRest | 5 min | 15 min | CloudNativePG HA + backup |
| Vector database | Qdrant backup to S3; rebuild from source | 1 hour | 1-2 hours | Qdrant snapshot + rebuild |
| Model weights | Object store (S3/GCS) as primary + cross-region replication | Near-zero | Minutes (re-pull) | S3 CRR; models never in cluster only |
| Prompt/Tool registry | Git (inherently versioned) + ConfigMap backup | Near-zero | Minutes | ArgoCD re-sync to DR cluster |

## Hands-On Exercises

### Exercise 12.1 — Deploy a Stateless Agent with KEDA Scaling

Build a minimal stateless agent worker with a Redis queue and KEDA autoscaling:

```bash
# 1. Deploy Redis for the task queue and session memory
helm install redis bitnami/redis \
  --set auth.enabled=false \
  --set architecture=standalone \
  --namespace ai-agents --create-namespace

# 2. Install KEDA
helm install keda kedacore/keda --namespace keda --create-namespace

# 3. Deploy a simple agent worker Deployment
kubectl apply -n ai-agents -f - <<'YAML'
apiVersion: apps/v1
kind: Deployment
metadata:
  name: demo-agent-worker
spec:
  replicas: 1
  selector:
    matchLabels: { app: demo-agent-worker }
  template:
    metadata:
      labels: { app: demo-agent-worker }
    spec:
      containers:
        - name: worker
          image: python:3.12-slim
          command: [python, -c]
          args:
            - |
              import redis, time
              r = redis.Redis(host='redis-master', port=6379)
              while True:
                  task = r.blpop('agent:tasks', timeout=5)
                  if task:
                      print(f'Processing: {task[1]}')
                  time.sleep(2)  # Simulate work
          resources:
            requests: { cpu: 100m, memory: 128Mi }
YAML

# 4. Create a KEDA ScaledObject for the Redis list
kubectl apply -n ai-agents -f - <<'YAML'
apiVersion: keda.sh/v1alpha1
kind: ScaledObject
metadata:
  name: agent-worker-scaler
spec:
  scaleTargetRef:
    name: demo-agent-worker
  minReplicaCount: 0
  maxReplicaCount: 10
  triggers:
    - type: redis
      metadata:
        address: redis-master.ai-agents:6379
        listName: agent:tasks
        listLength: '5'
YAML

# 5. Push tasks and observe scaling
kubectl exec -n ai-agents deploy/redis-master -- \
  redis-cli RPUSH agent:tasks task1 task2 task3 task4 task5 task6
kubectl get pods -n ai-agents -w  # Watch workers scale up
```

### Exercise 12.2 — Deploy MCP Server and Test Tool Call

Deploy an MCP server and verify tool invocation from an agent client:

```bash
# Deploy a minimal MCP server with a mock tool
kubectl apply -n ai-agents -f - <<'YAML'
apiVersion: apps/v1
kind: Deployment
metadata:
  name: mcp-demo-server
spec:
  replicas: 1
  selector:
    matchLabels: { app: mcp-demo }
  template:
    metadata:
      labels: { app: mcp-demo }
    spec:
      containers:
        - name: mcp
          image: python:3.12-slim
          # Run a minimal MCP server with a simple tool
          command: [sh, -c, "pip install mcp -q && python server.py"]
          resources:
            requests: { cpu: 100m, memory: 256Mi }
          ports:
            - containerPort: 8080
YAML
kubectl expose deployment mcp-demo-server --port=8080 -n ai-agents

# Test tool listing via the MCP protocol
kubectl exec -n ai-agents deploy/mcp-demo-server -- \
  curl -s http://localhost:8080/tools/list

# For production MCP: use the official MCP Python SDK
# pip install 'mcp[cli]'
# mcp install server.py
```

## Related

- [K8s Handbook Part 12: Agentic AI](../29-k8s-handbook-part12-agentic-ai.md) — Part 1: Kubernetes as the Agentic AI Substrate, Stateless vs Stateful Execution, Temporal, Argo Workflows, MCP Server Deployment
- [K8s Handbook Part 12: Agentic AI (Part 2)](29-k8s-handbook-part12-agentic-ai-part2.md) — A2A communication, agent scheduling, autoscaling, runtime isolation, memory services, tool/prompt/agent registries
