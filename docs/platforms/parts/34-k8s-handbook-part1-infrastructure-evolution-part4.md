---
title: "K8s Handbook Part 1 (Part 4: Decision Matrix, Anti-Patterns & Migration Strategy)"
doc_type: guide
domain: platforms
status: current
topic_id: k8s-handbook-part1-infrastructure-evolution-part4
last_reviewed: 2026-07-27
maturity: practitioner
supersedes: []
tags:
  - kubernetes
  - decision-framework
  - anti-patterns
  - migration
covers_version: "2025-2026 edition"
---

*Part 4 of 4 of [K8s Handbook Part 1: Infrastructure Evolution](../34-k8s-handbook-part1-infrastructure-evolution.md).*

## Chapter 10: Infrastructure Evolution Decision Matrix

### When to Choose Each Abstraction Layer

Enterprise architects face the question of which infrastructure abstraction layer is appropriate for each workload.

> **Source-quality note:** the original decision matrix used per-cell rating glyphs (preferred/suitable/not-recommended icons) to rate Physical, VM, Container/K8s, and Serverless for each workload type. Those glyphs were lost during PDF extraction, leaving only scattered `~` ("possible with caveats") marks and the prose recommendation. Rather than guess which glyph belonged in which now-blank cell, the table below preserves only what is actually recoverable from the source: the recommendation itself, plus the caveat annotations that did survive.

| Workload Type | Recommendation | Caveats (from surviving source annotations) |
| --- | --- | --- |
| Legacy monolith, no refactor | VMs (lift-and-shift) | Containerising without refactoring is possible but with caveats |
| Microservices (new) | Kubernetes | — |
| Batch processing (large) | Kubernetes + Jobs | Physical/VM/Serverless all possible with caveats |
| Event-driven functions | Serverless or KEDA on K8s | — |
| GPU ML training | Kubernetes + GPU Operator | Physical/VM possible with caveats |
| LLM inference (high volume) | Kubernetes + vLLM | Physical/VM/Serverless possible with caveats |
| Stateful database (OLTP) | Managed DB or K8s StatefulSet | Physical possible with caveats |
| Edge AI workloads | K3s / MicroK8s at edge | Physical/VM/Serverless possible with caveats |
| Air-gapped / sovereign | Kubernetes (self-managed) | Physical possible with caveats |
| High-security (FinServ/Gov) | Kubernetes + Confidential Containers (Kata) | Physical/Serverless possible with caveats |

## Chapter 11: Anti-Patterns & Migration Strategies

### Top Infrastructure Anti-Patterns and Remediation

**Lift-and-shift monoliths into Pods.** Problem: teams containerise a monolithic application and run it as a single Pod, expecting Kubernetes benefits without architectural change. Remediation: extract stateless components first. Use the Strangler Fig pattern to decompose incrementally. Run the monolith on VMs alongside new microservices on Kubernetes during transition.

**Treating Kubernetes nodes as pets.** Problem: manually configuring nodes, installing packages directly on nodes, or modifying node configuration outside of cluster lifecycle management. Remediation: immutable node images (Bottlerocket, Flatcar). Node configuration via DaemonSets. ClusterAPI or Karpenter for node lifecycle management.

**Ignoring resource requests/limits.** Problem: deploying Pods without resource requests and limits, causing noisy-neighbour problems and unpredictable OOM kills. Remediation: enforce resource requirements via LimitRange (defaults) and admission webhooks that reject Pods without resource specifications.

**One big cluster for everything.** Problem: running all workloads in a single cluster creates blast radius risk, resource contention, and compliance challenges. Remediation: separate clusters by environment (dev/staging/prod), by criticality, and by compliance boundary. Use GitOps to manage multi-cluster consistently.

**Storing secrets in ConfigMaps or environment variables.** Problem: sensitive data (API keys, passwords) stored in ConfigMaps or baked into container images is a security violation. Remediation: External Secrets Operator syncing from Vault or cloud secret managers. Sealed Secrets for GitOps-compatible secret management.

### Migration Strategy: Legacy to Kubernetes

**Phase 1: Containerise**
- Containerise existing applications without architectural changes
- Run containers on VMs using Docker Compose or simple orchestration
- Establish CI/CD pipeline building OCI-compliant images
- Implement basic container image scanning

**Phase 2: Orchestrate**
- Deploy containerised apps to Kubernetes (start with dev/test)
- Implement basic RBAC and namespace isolation
- Deploy observability stack (Prometheus, Grafana, Loki)
- Establish GitOps workflow (ArgoCD or Flux)

**Phase 3: Cloud-Nativise**
- Decompose monoliths using Strangler Fig or feature extraction
- Implement service mesh for mTLS and observability
- Adopt operator pattern for stateful services
- Implement autoscaling (HPA, VPA, KEDA)

**Phase 4: Platform**
- Build or adopt Internal Developer Platform (Backstage)
- Implement self-service namespace provisioning
- Establish FinOps practices (OpenCost, chargeback)
- Automate compliance and policy enforcement (OPA, Kyverno)

## Chapter 12: Hands-On Exercises

### Exercise 1.1 — Infrastructure Evolution Audit

Conduct an audit of your organisation's current infrastructure estate. For each major workload category, document:

- Current deployment model (physical/VM/container/serverless)
- Average CPU utilisation over the past 30 days
- Deployment frequency (how often the application is updated)
- Time from code commit to production deployment
- Mean time to recover from failure
- Monthly infrastructure cost per workload
- Kubernetes readiness assessment (stateless? 12-factor? externally configured?)

### Exercise 1.2 — Container Fundamentals Lab

Run these commands on a Linux host with Docker or Podman installed to directly observe the kernel primitives underlying containers:

```bash
# Observe namespaces of a running container
docker run -d --name demo nginx:alpine
PID=$(docker inspect --format '{{.State.Pid}}' demo)
ls -la /proc/$PID/ns/

# Compare host and container network namespaces
ip netns list
nsenter -t $PID -n ip addr show

# Observe cgroup limits
cat /sys/fs/cgroup/system.slice/docker-*.scope/memory.max
docker run --memory=256m nginx:alpine

# Build and inspect a layered image
docker build -t myapp:v1 .
docker inspect myapp:v1 --format '{{json .RootFS.Layers}}' | jq
docker history myapp:v1
```

### Exercise 1.3 — Design a Cloud-Native Migration Plan

Select a representative enterprise application from your environment. Design a migration plan addressing:

- Assess 12-Factor compliance — identify gaps and remediation steps
- Container image strategy — base image selection, layer optimisation, signing
- Configuration externalisation — identify all hardcoded config
- State management — categorise stateful components and appropriate K8s resource type
- Health check implementation — liveness, readiness, and startup probes
- Resource sizing — estimate requests and limits from current utilisation data
- Observability — structured logging, metrics exposition, distributed tracing hooks
- Security — non-root user, read-only filesystem, dropped capabilities

## Related

- [Part 1: The Imperative, Physical Servers & Virtualisation](../34-k8s-handbook-part1-infrastructure-evolution.md)
- [Part 2: Cloud Computing, Containers & the Kubernetes Precursors](34-k8s-handbook-part1-infrastructure-evolution-part2.md)
- [Part 3: The Kubernetes Era, Cloud-Native Architecture & Platform Engineering](34-k8s-handbook-part1-infrastructure-evolution-part3.md)
