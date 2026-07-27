---
title: "K8s Handbook Part 12: Agentic AI"
doc_type: guide
domain: platforms
status: current
topic_id: k8s-handbook-part12-agentic-ai
last_reviewed: 2026-07-27
maturity: practitioner
supersedes: [docs/cloud-platforms/kubernetes/K8s_Handbook_Part12_Agentic_AI.md]
tags: [kubernetes, agentic-ai, mcp, temporal, argo-workflows]
covers_version: "2025-2026 edition"
---

This part assumes full knowledge of Agentic AI concepts: LLM-based agents, tool use, memory architectures, RAG, multi-agent orchestration, MCP, A2A, and enterprise AI governance. The focus here is exclusively on Kubernetes implementation patterns: how do you deploy, scale, secure, observe, and govern enterprise Agentic AI systems on Kubernetes?

## Kubernetes as the Agentic AI Substrate

### Why Kubernetes for Agentic AI

- **Workload heterogeneity** — agentic systems combine CPU-bound orchestration, GPU-bound inference, stateful memory stores, persistent vector databases, message queues, and event-driven workflows. Kubernetes is the only substrate that manages all of these in a unified operational model with consistent observability and policy.
- **Dynamic scaling** — agent workloads are inherently bursty. A single user request may spawn 0 to 50 sub-agent tasks. Kubernetes HPA and KEDA scale the agent worker pool in seconds; Karpenter provisions new GPU nodes in under 2 minutes.
- **Workload isolation** — enterprise multi-tenant agent platforms must isolate customer workloads from each other. Kubernetes Namespaces, NetworkPolicies, RuntimeClasses, and RBAC provide layered isolation at compute, network, and credential levels.
- **Operational consistency** — agent systems are complex distributed applications. Kubernetes brings the same deployment, rollout, health checking, and observability patterns used for traditional microservices to AI agents, reducing operational burden and enabling GitOps-based management of the entire platform.
- **Ecosystem** — the CNCF ecosystem provides Argo Workflows for orchestration, Temporal for durable execution, LiteLLM for the model gateway, Milvus for vector storage, Feast for feature serving, cert-manager for identity, and Vault for secrets — all Kubernetes-native and interoperable.

### Enterprise Agentic AI Platform Reference Architecture

The platform is layered from external interfaces down to data:

- **External interfaces** — an API Gateway (Kong/AWS API GW) fronting the Agent Orchestration API, a WebSocket endpoint for streaming agent responses, and webhook receivers for event-triggered agents.
- **AI Gateway layer** (Kubernetes Deployment) — LiteLLM / Kong AI Gateway handling auth, rate limiting, model routing, and cost tracking.
- **Agent orchestration layer** — the Agent API Server (FastAPI/gRPC, Kubernetes Deployment), a Temporal Worker Pool (Kubernetes Deployment, KEDA-scaled), and the Argo Workflows Controller.
- **Agent execution layer** — stateless, KEDA-scaled Agent Worker Pods; tool-specific MCP Server Deployments (sidecar pattern); GPU Inference Pods (vLLM, KServe).
- **Memory and knowledge layer** — short-term Redis (session memory, conversation history); long-term Qdrant/Milvus (vector memory, knowledge base); episodic PostgreSQL (structured agent history, audit log); semantic Feast (feature store, user/entity profiles).
- **Data and model layer** — a Model Registry (MLflow, Kubeflow Model Registry), a Tool Registry (custom CRD or Service Catalogue), a Prompt Registry (ConfigMap-based or a dedicated service), and object storage (S3/GCS) for datasets, model weights, and artifacts.

## Stateless vs Stateful Agent Execution Patterns

The most consequential architectural decision for an agent execution system is the choice between stateless and stateful execution. This choice determines the scalability model, failure recovery characteristics, cost profile, and operational complexity of the entire platform.

### Stateless Agent Execution

In stateless execution, the agent worker Pod holds no local state between steps. All context — conversation history, intermediate results, tool outputs — is externalised to a shared state store (Redis, PostgreSQL, object storage). If the Pod crashes at any point, another Pod can resume execution from the last committed state with no data loss.

The pattern: a request arrives at the Agent API Server, which creates a task in a task queue (Redis/SQS/Kafka) carrying `session_id`, `agent_config`, and `initial_message`. A Worker Pod dequeues the task, loads context from the state store (`GET agent:session:{session_id}:context`), executes an agent step (calls the LLM via the AI Gateway, executes tool calls, updates context), then saves the updated context back to the state store with a TTL. If more steps are needed, it enqueues the next step; if complete, it emits a result event.

Kubernetes resources: the Agent API Server is a stateless Deployment (REST/gRPC); the Task Queue is a Redis or Kafka StatefulSet; the Worker Pool is a Deployment, KEDA-scaled on queue depth; the State Store is a Redis StatefulSet + PVC.

Advantages: horizontal scale (add workers without coordination), fault tolerance (a Pod crash just re-queues the task from the last checkpoint), zero sticky sessions (any worker can process any task), and simple autoscaling (KEDA on queue depth).

### Stateful Agent Execution

In stateful execution, the agent process maintains its own in-memory context throughout the lifetime of an agent session. This is simpler to implement but requires sticky session routing (requests for the same session go to the same Pod) and makes horizontal scaling more complex.

The pattern: a request arrives at the Agent API Server, which checks session affinity (`GET session:{session_id}:pod_ip` from Redis) and routes to the existing Pod if active, or assigns a new one. The Agent Pod holds full context in memory — no serialization overhead, fast step transitions — but a Pod crash means session loss unless a checkpoint mechanism is added.

Kubernetes resources: the Agent Server is either a StatefulSet with stable Pod identities, or a Deployment with a session-affinity Service; a sidecar or service-mesh layer acts as the Session Router.

Use case: interactive real-time agents where latency matters and session duration is short (under 5 minutes). Avoid for long-running agents, batch agents, or regulated workloads requiring an audit trail of every step.

### Decision Matrix

| Dimension | Stateless | Stateful |
|---|---|---|
| Context storage | External (Redis, PostgreSQL, S3) | In-memory (Pod heap) |
| Fault tolerance | Excellent (resume from checkpoint) | Poor (Pod crash = session lost) |
| Horizontal scaling | Simple (add workers) | Complex (sticky routing required) |
| Latency per step | Higher (state serialization) | Lower (in-memory access) |
| Session duration | Any length | Best for short sessions |
| Autoscaling | KEDA on queue depth | HPA on memory/connections |
| Best for | Batch agents, long-running, regulated | Real-time interactive agents |

## Durable Execution: Temporal on Kubernetes

Temporal is the leading durable workflow execution engine. It enables writing agent workflows as ordinary code (Go, Java, Python, TypeScript) where every step is automatically checkpointed, retried on failure, and resumable after arbitrary downtime. For enterprise agentic AI, Temporal solves the hardest operational problem: ensuring long-running agent workflows complete reliably even when individual steps fail, infrastructure restarts, or the agent takes hours to complete.

### Temporal Architecture on Kubernetes

The **Frontend Service** (Deployment) exposes the gRPC API for workflow operations (start, signal, query, terminate), and is where the client SDK connects. The **History Service** (Deployment) stores workflow event history (every step, input, output) and executes deterministic workflow code replay, backed by PostgreSQL or Cassandra. The **Matching Service** (Deployment) matches tasks to workers via task queues, routing activities (tool calls) to appropriate worker types. The **Worker Service** (Deployment, custom code) runs workflow and activity implementations and scales independently, KEDA-scaled on task queue depth. The **Web UI** (Deployment) provides visual workflow inspection, debugging, and manual intervention. Persistence is PostgreSQL (StatefulSet) or managed RDS/CloudSQL, with an optional Elasticsearch for advanced search over workflow history.

### Temporal Deployment with Helm

```bash
# Install Temporal on Kubernetes
helm repo add temporal https://go.temporal.io/helm-charts
helm install temporal temporal/temporal \
  --namespace temporal --create-namespace \
  --set server.replicaCount=3 \
  --set server.config.persistence.default.driver=sql \
  --set server.config.persistence.default.sql.driver=postgres12 \
  --set server.config.persistence.default.sql.host=postgres \
  --set server.config.persistence.default.sql.port=5432 \
  --set server.config.persistence.default.sql.database=temporal \
  --set server.config.persistence.default.sql.user=temporal \
  --set server.config.persistence.default.sql.password=temporal \
  --set prometheus.enabled=true \
  --set grafana.enabled=true
```

### Agentic Workflow in Temporal (Python SDK)

```python
import asyncio
from datetime import timedelta
from temporalio import activity, workflow
from temporalio.client import Client
from temporalio.worker import Worker

@activity.defn
async def call_llm(prompt: str, model: str) -> str:
    # Activity: one LLM call. Temporal retries on failure.
    response = await llm_client.chat(model=model, prompt=prompt)
    return response.content

@activity.defn
async def execute_tool(tool_name: str, tool_input: dict) -> dict:
    # Activity: one tool call. Retried on network failure.
    result = await tool_registry.call(tool_name, tool_input)
    return result

@workflow.defn
class ResearchAgentWorkflow:
    @workflow.run
    async def run(self, task: str) -> str:
        # Temporal checkpoints after EVERY await.
        # If the pod crashes here, replay resumes from the last checkpoint.
        plan = await workflow.execute_activity(
            call_llm,
            args=[f'Plan how to research: {task}', 'gpt-4o'],
            start_to_close_timeout=timedelta(minutes=2),
            retry_policy=RetryPolicy(maximum_attempts=3),
        )
        # Execute tool calls durably
        search_results = await workflow.execute_activity(
            execute_tool,
            args=['web_search', {'query': task}],
            start_to_close_timeout=timedelta(minutes=1),
        )
        # Synthesize results
        synthesis = await workflow.execute_activity(
            call_llm,
            args=[f'Synthesize: {search_results}', 'claude-3-5-sonnet'],
            start_to_close_timeout=timedelta(minutes=3),
        )
        return synthesis
```

## Argo Workflows for Agent Orchestration

Argo Workflows is a Kubernetes-native workflow engine that executes DAGs and step-based workflows as Kubernetes Pods. For agentic AI, Argo Workflows is particularly suited for batch agent pipelines, data processing workflows, and multi-step AI pipelines where each step can run independently.

### Argo Workflows vs Temporal

| Dimension | Argo Workflows | Temporal |
|---|---|---|
| Execution unit | Kubernetes Pod (each step) | Code function (activity) |
| State persistence | Kubernetes etcd (workflow CRD) | Dedicated database (PostgreSQL) |
| Step granularity | Container-level (coarse) | Function-level (fine) |
| Long-running workflows | Good (days, weeks) | Excellent (years if needed) |
| Sub-second steps | Poor (Pod startup overhead) | Excellent (in-process) |
| Language | YAML workflow definition | Go, Java, Python, TS SDK |
| GPU workloads | Native (Pod resources) | Via activity worker with GPU |
| Best for | ML pipelines, batch AI, data processing | Real-time agents, interactive, fine-grained retry |

### Agentic Research Pipeline in Argo Workflows

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Workflow
metadata:
  name: research-agent-pipeline
  namespace: ai-agents
spec:
  entrypoint: research-dag
  arguments:
    parameters:
      - name: research_topic
        value: enterprise AI adoption trends 2025
  templates:
    - name: research-dag
      dag:
        tasks:
          - name: plan
            template: llm-call
            arguments:
              parameters:
                - name: prompt
                  value: 'Create a research plan for: {{workflow.parameters.research_topic}}'
                - name: model
                  value: gpt-4o
          - name: web-search
            template: tool-call
            dependencies: [plan]
            arguments:
              parameters:
                - name: tool
                  value: web_search
                - name: query
                  value: '{{tasks.plan.outputs.parameters.search_queries}}'
          - name: synthesize
            template: llm-call
            dependencies: [web-search]
            arguments:
              parameters:
                - name: prompt
                  value: 'Synthesize findings: {{tasks.web-search.outputs.result}}'
                - name: model
                  value: claude-3-5-sonnet-20241022
    - name: llm-call
      inputs:
        parameters:
          - name: prompt
          - name: model
      container:
        image: harbor.corp/ai-agent-tools:v2
        command: [python, -m, agent_tools.llm_call]
        args: ['--prompt', '{{inputs.parameters.prompt}}', '--model', '{{inputs.parameters.model}}']
        env:
          - name: AI_GATEWAY_URL
            value: http://litellm.ai-gateway.svc.cluster.local:4000
        resources:
          requests: { cpu: 500m, memory: 1Gi }
        securityContext:
          runAsNonRoot: true
          runAsUser: 1000
          readOnlyRootFilesystem: true
```

## MCP Server Deployment Patterns on Kubernetes

Model Context Protocol (MCP) servers expose tools, resources, and prompts to LLM-based agents via a standardised protocol. Deploying MCP servers on Kubernetes enables centralised, scalable, secure tool infrastructure that multiple agents can consume simultaneously.

### MCP Server Deployment Topologies

| Topology | Description | Isolation | Scalability | Best For |
|---|---|---|---|---|
| Sidecar per agent | MCP server as sidecar container in agent Pod | High (per-pod) | Limited (scales with agent) | Sensitive tool access; process isolation |
| Shared Deployment | One MCP server Deployment, many agent clients | Low (shared process) | High (HPA/KEDA) | Stateless tools; high-throughput; cost-efficient |
| Per-namespace Deployment | MCP server Deployment per team namespace | Medium (namespace) | Medium | Multi-tenant; team tool customisation |
| Gateway (aggregator) | Single MCP gateway routing to multiple backends | High (gateway) | Very high | Enterprise; unified tool registry; audit logging |

### Shared MCP Server Deployment

```yaml
# Production MCP server for web search and code execution tools
apiVersion: apps/v1
kind: Deployment
metadata:
  name: mcp-tools-server
  namespace: ai-platform
spec:
  replicas: 3
  selector:
    matchLabels: { app: mcp-tools-server }
  template:
    spec:
      serviceAccountName: mcp-tools-sa
      securityContext:
        runAsNonRoot: true
        runAsUser: 1000
        seccompProfile: { type: RuntimeDefault }
      containers:
        - name: mcp-server
          image: harbor.corp/mcp-tools:v1.5
          command: [python, -m, mcp_server]
          args:
            - --transport=streamable-http
            - --host=0.0.0.0
            - --port=8080
            - --tools=web_search,code_executor,file_reader,database_query
          env:
            - name: SEARCH_API_KEY
              valueFrom:
                secretKeyRef: { name: mcp-tool-secrets, key: search-api-key }
          ports:
            - name: mcp
              containerPort: 8080
          resources:
            requests: { cpu: 500m, memory: 512Mi }
            limits: { memory: 1Gi }
          readinessProbe:
            httpGet: { path: /health, port: 8080 }
            periodSeconds: 5
          securityContext:
            readOnlyRootFilesystem: true
            allowPrivilegeEscalation: false
            capabilities: { drop: [ALL] }
---
apiVersion: v1
kind: Service
metadata:
  name: mcp-tools-server
  namespace: ai-platform
spec:
  selector: { app: mcp-tools-server }
  ports:
    - name: mcp
      port: 8080
      targetPort: 8080
---
# KEDA ScaledObject: scale the MCP server on tool call rate
apiVersion: keda.sh/v1alpha1
kind: ScaledObject
metadata:
  name: mcp-tools-scaler
spec:
  scaleTargetRef:
    name: mcp-tools-server
  minReplicaCount: 2
  maxReplicaCount: 20
  triggers:
    - type: prometheus
      metadata:
        query: sum(rate(mcp_tool_calls_total[1m]))
        threshold: '50'
```

### MCP Server Security Controls

- **Authentication** — MCP clients (agents) authenticate to the MCP server via Kubernetes Service Account tokens or mTLS; the MCP server validates the identity before executing tool calls.
- **Authorisation** — RBAC at the MCP level: agent identity determines which tools it can invoke. Use OPA or a custom admission layer in the MCP server to enforce tool-level permissions based on the agent's service account.
- **Tool sandboxing** — code execution tools must run in isolated environments. Use gVisor (RuntimeClass `kata-gvisor`) for the code execution container, and never run code execution in the same Pod as the MCP server process.
- **Audit logging** — all tool calls logged with agent identity, tool name, input parameters (sanitised), output (truncated), timestamp, and request ID — essential for EU AI Act compliance and security forensics.
- **NetworkPolicy** — the MCP server should only accept connections from authorised agent namespaces, with default-deny egress except to explicitly allowed external services.

## Related

- [K8s Handbook Part 12: Agentic AI (Part 2)](parts/29-k8s-handbook-part12-agentic-ai-part2.md) — A2A communication, agent scheduling, autoscaling, runtime isolation, memory services, tool/prompt/agent registries
- [K8s Handbook Part 12: Agentic AI (Part 3)](parts/29-k8s-handbook-part12-agentic-ai-part3.md) — workload identity, AI observability, GitOps for AI assets, sovereign AI, multi-region architectures, disaster recovery, exercises
