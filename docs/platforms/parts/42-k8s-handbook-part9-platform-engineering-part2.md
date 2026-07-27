---
title: "K8s Handbook Part 9: Platform Engineering (Part 2)"
doc_type: guide
domain: platforms
status: current
topic_id: k8s-handbook-part9-platform-engineering-part2
last_reviewed: 2026-07-27
maturity: practitioner
supersedes: []
tags: [kubernetes, platform-engineering, multi-tenancy, progressive-delivery, ai-infrastructure]
covers_version: "2025-2026 edition"
---

> Continues from [K8s Handbook Part 9: Platform Engineering](../42-k8s-handbook-part9-platform-engineering.md), covering Chapters 10-17: multi-tenancy, progressive delivery, landing zones, self-service patterns, AI platform golden paths, developer experience metrics, anti-patterns, and hands-on exercises.

## Multi-Tenancy Architectures

Multi-tenancy in Kubernetes means multiple teams or customers sharing cluster infrastructure. The right isolation model depends on the trust level between tenants and the regulatory requirements.

### Multi-Tenancy Models

| Model | Isolation | Trust Level | Resource Efficiency | Use Case |
|---|---|---|---|---|
| Cluster per tenant | Maximum (separate cluster) | Untrusted | Low (cluster overhead per tenant) | High-compliance SaaS, regulated industries |
| Namespace per tenant | Moderate (RBAC + NetworkPolicy + Quota) | Semi-trusted | High | Internal teams, same organisation |
| vCluster per tenant | Strong (virtual cluster in namespace) | Semi-trusted | Medium | Dev environments, CI namespaces |
| HierarchicalNamespace | Moderate (namespace hierarchy) | Semi-trusted | High | Large orgs with sub-teams |
| Pod-level isolation (Kata) | Hypervisor boundary | Low-trust workloads | Medium | Multi-tenant inference serving |

### vCluster — Virtual Clusters

vCluster creates lightweight virtual Kubernetes clusters inside namespaces. Each tenant gets a dedicated API server (k3s or k0s), control plane, and RBAC — all running inside a single namespace on the host cluster:

```bash
# Create a virtual cluster for a development team
vcluster create dev-team-a \
  --namespace vcluster-dev-team-a \
  --chart-version 0.20.0 \
  --values - <<'YAML'
controlPlane:
  distro:
    k3s:
      enabled: true
  statefulSet:
    resources:
      requests: { cpu: 200m, memory: 256Mi }
sync:
  toHost:
    ingresses:
      enabled: true
YAML

# Connect to the virtual cluster
vcluster connect dev-team-a --namespace vcluster-dev-team-a
# Team sees a fully isolated K8s cluster
kubectl get nodes  # Shows virtual node
kubectl get ns      # Clean namespace list
```

## Progressive Delivery: Canary and Blue-Green

Progressive delivery extends GitOps by controlling how a new version is gradually released to production: starting with a small percentage of traffic, measuring quality signals, and automatically promoting or rolling back based on metrics. This reduces deployment risk to near zero.

### Argo Rollouts — Progressive Delivery Controller

Argo Rollouts extends Kubernetes Deployments with canary and blue-green strategies, integrated with service mesh and ingress controllers for traffic splitting:

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Rollout
metadata:
  name: api-server
spec:
  replicas: 10
  selector:
    matchLabels: { app: api-server }
  template:
    metadata:
      labels: { app: api-server }
    spec:
      containers:
        - name: api
          image: harbor.corp/api:v1.2.3
  strategy:
    canary:
      canaryService: api-server-canary
      stableService: api-server-stable
      trafficRouting:
        istio:
          virtualService: { name: api-server-vs }
      steps:
        - setWeight: 5  # 5% to canary
        - pause: { duration: 5m }
        - analysis:
            templates:
              - templateName: success-rate  # Automated quality gate
        - setWeight: 20
        - pause: { duration: 10m }
        - analysis:
            templates:
              - templateName: latency-check
        - setWeight: 50
        - pause: { duration: 10m }
        - setWeight: 100
---
apiVersion: argoproj.io/v1alpha1
kind: AnalysisTemplate
metadata:
  name: success-rate
spec:
  metrics:
    - name: success-rate
      successCondition: result[0] >= 0.99
      failureCondition: result[0] < 0.95
      provider:
        prometheus:
          address: http://prometheus:9090
          query: |
            sum(rate(http_requests_total{status!~'5..',app='api-server',track='canary'}[5m])) /
            sum(rate(http_requests_total{app='api-server',track='canary'}[5m]))
```

## Landing Zones and Cluster Blueprints

A landing zone is a pre-configured, security-hardened, compliance-ready environment that serves as the starting point for new clusters or new teams. Cluster blueprints encode all organisational standards as code, enabling new clusters to be spun up that are immediately production-ready.

### Cluster Bootstrap Architecture

The cluster bootstrap sequence follows the ArgoCD App of Apps pattern:

1. The cluster is provisioned (CAPI / EKS / GKE / AKS).
2. ArgoCD is installed (`helm install argocd`).
3. A bootstrap Application is applied (`kubectl apply -f bootstrap-app.yaml`).
4. The bootstrap App deploys an App of Apps: `networking.yaml` installs Cilium and Gateway; `security.yaml` installs cert-manager, the Vault agent, and Falco; `observability.yaml` installs the Prometheus stack, Loki, and Tempo; `storage.yaml` installs CSI drivers and StorageClasses; `policy.yaml` installs Kyverno and baseline policies; `platform.yaml` installs Backstage and Crossplane; `cluster-config.yaml` sets up RBAC, Namespaces, and ResourceQuotas.
5. All platform components become healthy.
6. The cluster is registered in the Backstage catalogue.
7. Developers can immediately self-serve.

### Standard Namespace Labels and Annotations

```yaml
# Every production namespace created with this template
apiVersion: v1
kind: Namespace
metadata:
  name: team-platform
  labels:
    team: platform
    cost-center: CC-1234
    environment: production
    tier: platform
    # Pod Security Standards
    pod-security.kubernetes.io/enforce: restricted
    pod-security.kubernetes.io/enforce-version: v1.30
    pod-security.kubernetes.io/warn: restricted
    # Istio mesh participation
    istio-injection: enabled
    # Network policy automation
    network-policy.company.com/default-deny: enabled
  annotations:
    company.com/team-contact: platform@company.com
    company.com/pagerduty-service: PXXXXXX
    company.com/runbook: https://wiki.company.com/platform
```

## Self-Service Platform Patterns

Self-service is the core value proposition of Platform Engineering. Every manual approval process, every ticket to ops, every JIRA to get a namespace created is a tax on developer velocity. The platform should enable developers to do everything they need for their application without waiting.

### Self-Service Capabilities Matrix

| Capability | Manual Process | Self-Service Implementation | Time Saving |
|---|---|---|---|
| New namespace | File ticket to ops | Backstage template + Crossplane | Days → Minutes |
| Database provisioning | DBA ticket | Crossplane XR claim | Days → Hours |
| TLS certificate | PKI team request | cert-manager auto-issue | Days → Seconds |
| Secret access | Security team approval | Vault policy + ESO | Days → Minutes |
| Deploy to production | Manual approval + ops deploy | ArgoCD sync (automated) | Hours → Minutes |
| Scale up | Ops team intervention | HPA / KEDA auto-scaling | Hours → Seconds |
| Add team member | Admin ticket | OIDC group + RBAC sync | Days → Self-service |
| New cluster (dev) | Infra team request | vCluster from Backstage template | Days → Minutes |

### Namespace-as-a-Service Pattern

```yaml
# Crossplane Composition for self-service namespace:
# Developer creates:  NamespaceClaim
# Platform creates:   Namespace + RBAC + ResourceQuota + NetworkPolicy + Vault path
apiVersion: platform.company.com/v1alpha1
kind: NamespaceClaim
metadata:
  name: myteam-dev
spec:
  team: myteam
  environment: development
  costCenter: CC-5678
  cpuQuota: '20'
  memoryQuota: 40Gi
  gpuQuota: '4'
```

The Composition automatically creates: a Namespace with standard labels and PSS enforcement; RBAC RoleBindings for the team's OIDC group; a ResourceQuota with the requested limits; a LimitRange with defaults; a NetworkPolicy for default-deny plus DNS egress allow; a Vault namespace and KV path for team secrets; and a Backstage catalogue registration.

## Platform Engineering for AI Workloads

AI workloads place unique demands on the platform that standard application platform patterns do not address. GPU resource management, model lifecycle, experiment tracking, and the scale of compute required for LLM training all require platform-level abstractions beyond standard Kubernetes.

### AI Platform Golden Paths

- **LLM inference deployment** — one-click deployment of a model to KServe/vLLM. The developer selects a model from the registry and sets GPU count, replica count, and autoscaling policy; the platform provisions a Deployment, Service, Gateway HTTPRoute, HPA/KEDA, Prometheus metrics, a Grafana dashboard, and a PagerDuty alert.
- **Training job submission** — self-service ML training job submission. The developer fills a form (dataset path, model config, GPU count, max runtime); the platform submits a Volcano Job, a PVC for checkpoints, MLflow tracking setup, and a budget alert if compute exceeds a threshold.
- **RAG pipeline deployment** — a golden path for RAG architecture: vector database, embedding service, LLM, and retrieval API. The template provisions all components with correct networking, security, and observability.
- **Experiment namespace** — an isolated environment for ML experiments: a short-lived (72h TTL) namespace with GPU quota, MLflow tracking, object storage access, and a Jupyter notebook server.

### GPU Resource Management

GPU resources require special platform-level management. The **NVIDIA GPU Operator** (a platform DaemonSet) installs NVIDIA drivers, the container toolkit, the device plugin, and the DCGM exporter, and enables the `nvidia.com/gpu` resource type for scheduling.

```yaml
# GPU ResourceQuota per team namespace
requests.nvidia.com/gpu: 8
limits.nvidia.com/gpu: 8
# GPU requests == limits; fractional GPU is not supported in standard K8s
```

**MIG (Multi-Instance GPU)** enables shared GPU access: NVIDIA A100/H100 support splitting a GPU into up to 7 instances, each an isolated GPU with dedicated memory — useful for small models or development workloads.

```bash
# Enable MIG on a node
nvidia-smi mig -cgi 1g.10gb,1g.10gb,1g.10gb -C
# MIG resources appear as:
# nvidia.com/mig-1g.10gb: 3   (3 x 10GB MIG instances available)
```

GPU observability (DCGM Exporter metrics): `DCGM_FI_DEV_GPU_UTIL` (GPU utilisation %), `DCGM_FI_DEV_MEM_COPY_UTIL` (memory bandwidth utilisation %), `DCGM_FI_DEV_FB_USED` (GPU memory used, bytes), `DCGM_FI_DEV_POWER_USAGE` (power consumption, watts), `DCGM_FI_DEV_SM_CLOCK` (SM clock frequency, MHz).

## Developer Experience Metrics

Platform Engineering success must be measured. DORA metrics (from the DevOps Research and Assessment program) are the industry-standard framework for measuring software delivery performance, and platform engineering directly impacts all four.

### DORA Metrics and Kubernetes Indicators

| DORA Metric | Definition | Elite Target | K8s/Platform Indicator |
|---|---|---|---|
| Deployment Frequency | How often deployments reach production | On demand (multiple/day) | ArgoCD sync frequency; image update automation |
| Lead Time for Changes | Code commit to production | Less than 1 hour | CI pipeline + ArgoCD sync time |
| Change Failure Rate | % of deployments causing incidents | Less than 5% | Argo Rollout failures; incident rate post-deploy |
| Failed Deployment Recovery Time | Time to restore after failure | Less than 1 hour | Rollback time via Argo Rollouts |

### Platform-Specific Metrics

- **Time to First Deployment** — how long from developer onboarding to their first successful production deployment. Target: under 1 day with Backstage golden paths.
- **Self-service ratio** — the percentage of infrastructure changes made via self-service vs. tickets. Target: greater than 90%; measures platform adoption and ticket reduction.
- **Platform SLA** — uptime and latency of platform components (API server, ArgoCD, Backstage, Vault). The platform is now critical infrastructure and needs SLOs and alerting.
- **Cognitive load score** — a developer survey metric measuring how much mental overhead working with the platform imposes. Target: decrease over time with each platform improvement.

## Platform Anti-Patterns

- **Building a platform nobody uses** — the platform team builds features based on assumptions, not developer needs, leading to low adoption because it doesn't solve real pain points. Start with developer interviews, build the simplest useful thing first, measure adoption monthly, and run quarterly developer experience surveys.
- **Golden cage (not golden path)** — the platform is so restrictive that developers cannot do legitimate work without workarounds, so they bypass it entirely (shadow IT). Provide escape hatches for legitimate deviations, document the process, and make the golden path the easiest path, not the only path.
- **GitOps without drift detection** — using ArgoCD with `selfHeal: false` lets developers make ad-hoc `kubectl` changes that drift from Git, causing inconsistency and failed deployments. Enable `selfHeal: true` and `prune: true` in ArgoCD, and enforce cluster access via RBAC so only the ArgoCD SA has write access to production namespaces.
- **Helm chart sprawl** — hundreds of bespoke Helm charts, each slightly different, with no shared base charts and unenforced security defaults. Define 2-3 standard chart patterns (web service, worker, cronjob), enforce them via OPA/Kyverno, and use Helm library charts for shared templates.
- **Ignoring platform reliability** — ArgoCD, cert-manager, and Vault deployed without HA, no PDB, and no monitoring, so a platform outage blocks all deployments cluster-wide. Platform components are critical infrastructure and need HA, PDBs, Prometheus alerts, SLOs, and on-call coverage.
- **Manual cluster creation** — clusters created via console clicks with no IaC, so no two clusters are identical and reproducing configuration is impossible. All clusters should be created via Terraform/CAPI plus an ArgoCD bootstrap; cluster creation should be a PR to a GitOps repository.

## Hands-On Exercises

### Exercise 9.1 — GitOps with ArgoCD

Deploy an application using GitOps principles:

```bash
# Install ArgoCD
kubectl create namespace argocd
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml
kubectl wait --for=condition=available deployment/argocd-server -n argocd --timeout=5m

# Get the admin password
kubectl -n argocd get secret argocd-initial-admin-secret \
  -o jsonpath='{.data.password}' | base64 -d

# Port-forward the ArgoCD UI
kubectl port-forward svc/argocd-server -n argocd 8080:443

# Create an Application pointing to a Git repo
argocd login localhost:8080 --username admin --insecure
argocd app create guestbook \
  --repo https://github.com/argoproj/argocd-example-apps.git \
  --path guestbook \
  --dest-server https://kubernetes.default.svc \
  --dest-namespace guestbook \
  --sync-policy automated \
  --auto-prune --self-heal

# Observe reconciliation
argocd app get guestbook
argocd app history guestbook
```

### Exercise 9.2 — Kustomize Overlay Pipeline

Create a multi-environment deployment with Kustomize:

```bash
# Create base manifests
mkdir -p myapp/base myapp/overlays/{dev,production}
# base/deployment.yaml: replicas=1, image=nginx:alpine
# base/kustomization.yaml: resources: [deployment.yaml]
# overlays/dev/kustomization.yaml:
#   resources: [../../base]
#   patches: (replicas=1, small resources)
# overlays/production/kustomization.yaml:
#   resources: [../../base]
#   patches: (replicas=5, larger resources)
#   commonLabels: {environment: production}

# Preview what would be deployed
kubectl kustomize myapp/overlays/dev
kubectl kustomize myapp/overlays/production

# Deploy the development overlay
kubectl apply -k myapp/overlays/dev
# Deploy the production overlay
kubectl apply -k myapp/overlays/production
```

## Related

- [K8s Handbook Part 9: Platform Engineering](../42-k8s-handbook-part9-platform-engineering.md) — Part 1: Platform Engineering Philosophy, GitOps, ArgoCD, Flux, Helm, Kustomize, Backstage, Crossplane, Cluster Lifecycle Management
