# Split Plan: K8s Handbook Part 12 — Agentic AI

**Source:** `/workspace/knowledge-docs/docs/cloud-platforms/kubernetes/K8s_Handbook_Part12_Agentic_AI.md` (~5,551 words body, 20 chapters)

**Reason:** Word count exceeds guide doc_type cap (2600 words hard cap); 20 chapters is also unusually large for a 2-way split to stay well under cap with margin, so a 3-way split was used (same approach as Part 1 and Part 4).

## Split Boundary

**Part 1 (Main):** `docs/platforms/29-k8s-handbook-part12-agentic-ai.md`
- Source: Chapters 1–5 (Kubernetes as the Agentic AI Substrate, Stateless vs Stateful Agent Execution Patterns, Durable Execution: Temporal on Kubernetes, Argo Workflows for Agent Orchestration, MCP Server Deployment Patterns on Kubernetes)
- Content: why Kubernetes for agentic AI and the enterprise agentic AI platform reference architecture, the stateless-vs-stateful decision matrix, Temporal architecture/Helm deployment/an agentic workflow in the Python SDK, Argo Workflows vs Temporal and an agentic research pipeline, MCP server deployment topologies/a shared MCP server Deployment/MCP security controls

**Part 2 (Supplementary):** `docs/platforms/parts/29-k8s-handbook-part12-agentic-ai-part2.md`
- Source: Chapters 6–13 (A2A Communication Across Clusters, Agent Scheduling and GPU-Aware Placement, Autoscaling Strategies for Agent Workloads, Runtime Isolation for Multi-Tenant Agents, Externalized Memory Services on Kubernetes, Tool Registry and Tool Lifecycle Management, Prompt Registry and Prompt Lifecycle, Agent Registry and Agent Governance)
- Content: A2A communication patterns/Kafka message bus/cross-cluster Cilium Cluster Mesh, agent worker resource profiles and node pool strategy, KEDA agent autoscaling and Karpenter GPU node provisioning, isolation levels (namespace/vCluster/gVisor/Kata/cluster-per-tenant) and a Kata Containers example, the memory architecture taxonomy and Redis working memory, tool registry CRD design and tool lifecycle governance, prompt registry options and a ConfigMap-based GitOps prompt registry, agent registry CRD design

**Part 3 (Supplementary):** `docs/platforms/parts/29-k8s-handbook-part12-agentic-ai-part3.md`
- Source: Chapters 14–20 (Workload Identity and Secret Management for Agents, AI Observability for Multi-Agent Systems, GitOps for AI Assets, Sovereign AI Deployments, Multi-Region Agentic AI Architectures, Disaster Recovery for Agentic Platforms, Hands-On Exercises)
- Content: agent identity hierarchy and External Secrets Operator injection, agent observability signals and OpenTelemetry agent tracing, the AI GitOps repository structure and a prompt CI/CD pipeline, sovereign AI requirements and air-gapped Kubernetes architecture, multi-region patterns and a hub-spoke agent architecture, component-level DR strategy (RPO/RTO per component), 2 hands-on exercises

## Source-quality notes (converted-pdf artifacts fixed during migration)

- Numerous flattened multi-line YAML/shell/Python blocks reconstructed into properly line-broken fenced blocks across all three parts (Temporal Helm install and Python SDK workflow, Argo Workflow DAG, MCP server Deployment, Kafka/Strimzi config, Karpenter NodePool, Kata Containers Kyverno policy, Redis Helm install, Tool/Prompt/Agent CRD examples, External Secrets Operator, OpenTelemetry instrumentation, air-gapped containerd mirror config, both exercises).
- No content-loss (heading-then-nothing) artifacts were found in this source; all 20 chapters retained their body text.
- Exercise 12.2's MCP demo container `command` was garbled by the PDF conversion into an invalid exec-array mix (`[pip, install, mcp, -q, '&&', python, -c]`, which is not valid Kubernetes container command syntax). Rewritten as `command: [sh, -c, "pip install mcp -q && python server.py"]`, preserving the same intent (install the MCP package, then run the server) in valid syntax.

## Navigation

- Part 1 ends with a pointer to Part 2; Part 2 ends with a pointer to Part 3 (and back to Part 1).
- Topic ID: all three parts share the `k8s-handbook-part12-agentic-ai` topic family.
- Part 1 is canonical (`topic_id: k8s-handbook-part12-agentic-ai`).
- Part 2 uses `topic_id: k8s-handbook-part12-agentic-ai-part2`, Part 3 uses `k8s-handbook-part12-agentic-ai-part3`; both `supersedes: []` (Part 1 carries the supersedes entry).
