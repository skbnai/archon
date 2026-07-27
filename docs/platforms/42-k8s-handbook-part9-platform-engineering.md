---
title: "K8s Handbook Part 9: Platform Engineering"
doc_type: guide
domain: platforms
status: current
topic_id: k8s-handbook-part9-platform-engineering
last_reviewed: 2026-07-27
maturity: practitioner
supersedes: [docs/cloud-platforms/kubernetes/K8s_Handbook_Part9_Platform_Engineering.md]
tags: [kubernetes, platform-engineering, gitops, argocd, backstage]
covers_version: "2025-2026 edition"
---

Platform Engineering emerged as a discipline in response to the complexity tax that Kubernetes imposed on development teams. The insight: Kubernetes is an excellent substrate for platform builders, but a terrible direct interface for application developers. Platform Engineering abstracts Kubernetes complexity into opinionated, self-service golden paths that improve developer velocity without sacrificing operational consistency or security.

## Platform Engineering Philosophy and Goals

### The Platform Engineering Value Proposition

Without Platform Engineering: a developer learns the Kubernetes API, writes YAML, debugs admission webhooks, configures RBAC, sets up monitoring, configures HPA, and so on — time to production is weeks, consistency is zero (every team does it differently), and security is highly variable (depends on individual knowledge).

With Platform Engineering: a developer uses a self-service platform and deploys via a golden path, with monitoring, scaling, and security enforced automatically — time to production is hours, consistency is high (the platform enforces standards), and security is high (baked into the golden path).

### Platform Engineering Core Principles

- **Product thinking** — the platform is a product with developers as customers. Apply product management discipline: understand developer pain points, measure adoption, iterate based on feedback. Treat platform SLOs as product commitments.
- **Golden paths, not golden cages** — golden paths should be the path of least resistance to production, not the only path. Escape hatches exist for teams with legitimate reasons to deviate.
- **Self-service by default** — developers should be able to deploy, scale, observe, and roll back their applications without filing tickets to platform or ops teams. Every manual approval is a tax on developer velocity.
- **Paved roads** — the platform team builds and maintains the roads; application teams drive on them. The platform team owns reliability of the infrastructure layer; app teams own reliability of their applications.
- **Shift left** — security, compliance, and cost visibility belong in the developer workflow, not as post-deployment surprises. Admission controllers and IDE plugins surface issues before code reaches production.

### Platform Team Topologies

| Model | Structure | Best For | Risk |
|---|---|---|---|
| Centralised Platform Team | Single team owns all platform capabilities | Large orgs (500+ engineers) | Bottleneck if understaffed |
| Embedded Platform Engineers | Platform engineers embedded in product squads | Medium orgs | Inconsistent standards across squads |
| Platform as a Product | Dedicated product team with PM, engineers, UX | Large orgs with mature platform | Higher investment required |
| Open Source Model | Platform team builds core; app teams contribute plugins | Very large orgs | Governance complexity |

## GitOps: Principles and Patterns

GitOps is an operational model where Git is the single source of truth for both application code and infrastructure configuration. The desired state of the system is declared in Git; an automated agent (ArgoCD, Flux) continuously reconciles the actual state of the cluster to match. Changes are made via pull requests, not via direct `kubectl` commands.

### GitOps Four Principles

- **Declarative** — the entire system is described declaratively; no imperative scripts that are hard to audit, reproduce, or roll back.
- **Versioned and immutable** — desired state is stored in Git with full history; every change is an atomic commit with a unique SHA; rollback is a `git revert`.
- **Pulled automatically** — approved changes are applied automatically by a software agent without human intervention; no manual `kubectl apply` in production.
- **Continuously reconciled** — software agents continuously compare actual state to desired state and take corrective action; drift is detected and corrected automatically.

### GitOps Repository Patterns

| Pattern | Structure | Pros | Cons |
|---|---|---|---|
| Mono-repo | All apps + all envs in one repo | Simple; atomic cross-app changes | Scales poorly; blast radius |
| App-per-repo | Each app has its own config repo | Good separation; team autonomy | Many repos to manage |
| Env-per-repo | Separate repo per environment | Clear env separation; branch protection | Cross-env PRs complex |
| Infra + App split | Infrastructure in a separate repo from app configs | Clear ownership boundaries | Two-repo coordination required |
| Trunk-based + overlays | Single branch; env differences via Kustomize overlays | Simple branching; DRY configs | Kustomize complexity |

### Recommended GitOps Repository Structure

```
infrastructure-gitops/
  clusters/
    production-us-east/
      cluster-config/   # Cluster-level config (RBAC, policies)
      namespaces/       # Namespace definitions and ResourceQuotas
      apps/             # ArgoCD ApplicationSets or Flux Kustomizations
    staging-us-east/
      ...
  components/
    monitoring/         # Prometheus, Grafana stack
    security/           # Falco, cert-manager, Vault agent
    networking/         # Cilium config, Gateway config
    storage/            # StorageClasses, Rook config

app-gitops/
  apps/
    myapp/
      base/             # Base Kustomize manifests
      overlays/
        dev/            # Dev-specific patches
        staging/        # Staging patches
        production/     # Production patches
      helm/             # Helm values files per environment
```

## ArgoCD: GitOps Continuous Delivery

ArgoCD is the most widely deployed GitOps tool for Kubernetes. It continuously monitors Git repositories and automatically synchronises Kubernetes cluster state to match the desired state defined in Git. It supports Helm, Kustomize, Jsonnet, and raw YAML manifests.

### ArgoCD Architecture

ArgoCD's components: `argocd-server` (API server and Web UI, gRPC + REST), `argocd-repo-server` (Git repository cloning and manifest generation), `argocd-application-controller` (the reconciliation loop that watches cluster vs. Git), `argocd-dex-server` (OIDC identity provider for delegated auth), `argocd-redis` (cache for the repo-server and app controller), and `argocd-applicationset-controller` (generates Applications from templates).

Reconciliation loop: the app controller fetches the desired state from `repo-server` (rendered manifests), queries the Kubernetes API for live state, computes a diff (`OutOfSync` if different), applies changes automatically if `syncPolicy.automated` is set, checks the health of deployed resources, then reports status as Synced/OutOfSync plus Healthy/Degraded/Progressing.

### ArgoCD Application

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: myapp-production
  namespace: argocd
  finalizers:
    - resources-finalizer.argocd.argoproj.io  # Cascade delete
spec:
  project: production
  source:
    repoURL: https://github.com/company/app-gitops
    targetRevision: main
    path: apps/myapp/overlays/production
  destination:
    server: https://production-cluster.internal:6443
    namespace: production
  syncPolicy:
    automated:
      prune: true      # Delete resources removed from Git
      selfHeal: true    # Re-sync if cluster drifts from Git
    syncOptions:
      - CreateNamespace=true
      - PrunePropagationPolicy=foreground
      - ApplyOutOfSyncOnly=true  # Only apply changed resources
    retry:
      limit: 5
      backoff: { duration: 5s, maxDuration: 3m, factor: 2 }
  ignoreDifferences:
    - group: apps
      kind: Deployment
      jsonPointers:
        - /spec/replicas  # Ignore HPA-managed replica count
```

### ApplicationSet — Multi-Cluster Deployment

ApplicationSet generates multiple Applications from a template, enabling a single definition to deploy to many clusters or environments:

```yaml
apiVersion: argoproj.io/v1alpha1
kind: ApplicationSet
metadata:
  name: myapp-all-clusters
  namespace: argocd
spec:
  generators:
    # Deploy to all clusters registered in ArgoCD
    - clusters:
        selector:
          matchLabels: { environment: production }
    # Or: a matrix of clusters x environments
    - matrix:
        generators:
          - clusters:
              values: { region: us-east-1 }
          - list:
              elements:
                - env: production
                - env: staging
  template:
    metadata:
      name: myapp-{{name}}
    spec:
      project: default
      source:
        repoURL: https://github.com/company/app-gitops
        path: apps/myapp/overlays/{{metadata.labels.environment}}
        targetRevision: main
      destination:
        server: '{{server}}'
        namespace: myapp
      syncPolicy:
        automated: { prune: true, selfHeal: true }
```

## Flux: GitOps Toolkit

Flux (CNCF graduated) is a GitOps toolkit composed of independent controllers for different aspects of the GitOps pipeline. Unlike ArgoCD (a monolithic CD tool), Flux is composable: each controller handles one concern, and they work together via Kubernetes events.

### Flux Controllers

| Controller | Responsibility | Key CRDs |
|---|---|---|
| source-controller | Fetches and caches Git repos, Helm charts, OCI artifacts, S3 buckets | GitRepository, HelmRepository, OCIRepository, Bucket |
| kustomize-controller | Applies Kustomize overlays from Sources | Kustomization |
| helm-controller | Manages Helm releases declaratively | HelmRelease |
| notification-controller | Sends events to Slack, GitHub, Teams; receives webhooks | Alert, Provider, Receiver |
| image-automation-controller | Auto-updates image tags in Git when new images are pushed | ImageUpdateAutomation, ImagePolicy |
| image-reflector-controller | Scans registries for new image tags | ImageRepository |

### Flux GitRepository and Kustomization

```yaml
# Source: watch a Git repository
apiVersion: source.toolkit.fluxcd.io/v1
kind: GitRepository
metadata:
  name: app-gitops
  namespace: flux-system
spec:
  interval: 1m
  url: https://github.com/company/app-gitops
  ref: { branch: main }
  secretRef: { name: github-credentials }
---
# Apply: deploy the production overlay from the GitRepository
apiVersion: kustomize.toolkit.fluxcd.io/v1
kind: Kustomization
metadata:
  name: myapp-production
  namespace: flux-system
spec:
  interval: 5m
  path: ./apps/myapp/overlays/production
  prune: true
  sourceRef:
    kind: GitRepository
    name: app-gitops
  healthChecks:
    - apiVersion: apps/v1
      kind: Deployment
      name: myapp
      namespace: production
  timeout: 5m
  retryInterval: 2m
  postBuild:
    substituteFrom:
      - kind: ConfigMap
        name: cluster-vars  # Inject cluster-specific variables
```

### ArgoCD vs Flux Decision Matrix

| Dimension | ArgoCD | Flux |
|---|---|---|
| Architecture | Monolithic CD platform | Composable GitOps toolkit |
| UI | Rich web UI included | CLI-first; UI via Weave GitOps (separate) |
| Multi-cluster | Built-in cluster management | Hub-spoke via Flux on each cluster |
| Helm support | First-class | HelmRelease CRD; feature-rich |
| ApplicationSet | Native (powerful templating) | Requires workarounds |
| Image automation | Via ArgoCD Image Updater (plugin) | Built-in image-automation-controller |
| Progressive delivery | Via Argo Rollouts | Via Flagger |
| Notification | Via notification plugin | Built-in notification-controller |
| Drift detection | Real-time (continuous watch) | Interval-based (configurable down to 1m) |
| Best for | Teams wanting a full CD platform with UI | Teams wanting composable GitOps primitives |

## Helm: Package Management at Scale

Helm is the package manager for Kubernetes. A Helm chart packages all Kubernetes manifests for an application with configurable values, lifecycle hooks, and dependency management. At enterprise scale, Helm requires disciplined chart design, values management, and integration with GitOps tooling.

### Helm Chart Structure

```
myapp/
  Chart.yaml               # Chart metadata (name, version, appVersion, dependencies)
  values.yaml               # Default values (all configurable options documented)
  values-schema.json        # JSON Schema for values validation
  charts/                   # Dependency charts (pulled by helm dependency update)
  templates/
    _helpers.tpl             # Named templates (reusable snippets)
    deployment.yaml           # Deployment template
    service.yaml               # Service template
    ingress.yaml                # Ingress template (conditional)
    hpa.yaml                     # HPA template (conditional)
    configmap.yaml                 # ConfigMap template
    serviceaccount.yaml
    rbac.yaml
    pdb.yaml                          # PodDisruptionBudget
    networkpolicy.yaml
    NOTES.txt                          # Post-install instructions
  ci/
    test-values.yaml                    # Values for CI testing
    production-values.yaml
  tests/
    connection-test.yaml                  # Helm test Pod
```

### Production Helm Values Pattern

```yaml
# values.yaml (chart defaults -- safe, minimal)
replicaCount: 1
image:
  repository: harbor.internal.corp/myapp
  tag: latest  # Overridden in CI/CD
  pullPolicy: IfNotPresent
resources:
  requests: { cpu: 100m, memory: 128Mi }
  limits: { memory: 256Mi }
autoscaling:
  enabled: false
  minReplicas: 1
  maxReplicas: 10
  targetCPUUtilizationPercentage: 70
podSecurityContext:
  runAsNonRoot: true
  runAsUser: 10001
  fsGroup: 10001
  seccompProfile: { type: RuntimeDefault }
securityContext:
  allowPrivilegeEscalation: false
  readOnlyRootFilesystem: true
  capabilities: { drop: [ALL] }
pdb:
  enabled: false
  minAvailable: 1
---
# values-production.yaml (production overrides)
replicaCount: 3
image:
  tag: v1.2.3  # Set by CI/CD pipeline
autoscaling:
  enabled: true
  minReplicas: 3
  maxReplicas: 50
pdb:
  enabled: true
  minAvailable: 2
```

## Kustomize: Configuration Management

Kustomize is a template-free configuration customisation tool built into `kubectl`. It allows defining a base set of manifests and applying environment-specific overlays (patches, transformers, generators) without templates or variable substitution. This makes base manifests always valid Kubernetes YAML.

### Kustomize Architecture

```
base/
  kustomization.yaml   # Lists all resources
  deployment.yaml      # Production-ready base deployment
  service.yaml
  configmap.yaml
overlays/
  dev/
    kustomization.yaml   # References base + patches
    replica-patch.yaml    # Patch: replicas=1 for dev
    resource-patch.yaml    # Patch: smaller resource requests
  staging/
    kustomization.yaml
    replica-patch.yaml   # Patch: replicas=2
  production/
    kustomization.yaml
    replica-patch.yaml   # Patch: replicas=5
    hpa.yaml              # Additional resource: HPA
    pdb.yaml              # Additional resource: PDB
```

### Kustomization Files

```yaml
# base/kustomization.yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization
resources:
  - deployment.yaml
  - service.yaml
  - configmap.yaml
commonLabels:
  app.kubernetes.io/managed-by: kustomize
images:
  - name: myapp
    newName: harbor.internal.corp/myapp
    newTag: v1.0.0
---
# overlays/production/kustomization.yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization
namespace: production
resources:
  - ../../base
  - hpa.yaml
  - pdb.yaml
images:
  - name: myapp
    newTag: v1.2.3  # Override image tag
patches:
  - patch: |-
      - op: replace
        path: /spec/replicas
        value: 5
    target: { kind: Deployment, name: myapp }
configMapGenerator:
  - name: app-config
    behavior: merge
    literals:
      - LOG_LEVEL=warn
      - ENVIRONMENT=production
```

## Backstage: Internal Developer Platform

Backstage (Spotify, donated to CNCF) is the most widely adopted framework for building Internal Developer Platforms. It provides a plugin-based architecture for building a unified developer portal: service catalogue, software templates, documentation, and integrations with every tool in the developer ecosystem.

### Backstage Core Components

- **Software Catalogue** — the living inventory of all software components, APIs, teams, resources, and systems in the organisation. Every service has a `catalog-info.yaml` describing ownership, documentation, dependencies, and deployment status, powering discovery of who owns a service, what APIs it exposes, and how to contact the team.
- **Software Templates (Scaffolder)** — golden path templates that developers use to create new services. A template encodes all organisational standards: repository structure, CI/CD pipeline, Kubernetes manifests, monitoring config, security scanning, RBAC — all pre-configured and policy-compliant, so a new service is ready in minutes, not weeks.
- **TechDocs** — documentation-as-code: Markdown docs stored alongside the service code, rendered and indexed by Backstage, discoverable in the catalogue alongside the service, eliminating stale wiki documentation.
- **Search** — unified search across the catalogue, docs, APIs, and all integrated tools, so developers find information without knowing which system it lives in.
- **Plugins** — over 200 community plugins integrate Backstage with GitHub, GitLab, Jenkins, ArgoCD, Kubernetes, Prometheus, Grafana, PagerDuty, Datadog, Vault, SonarQube, Snyk, and hundreds more.

### catalog-info.yaml — Service Catalogue Entry

```yaml
apiVersion: backstage.io/v1alpha1
kind: Component
metadata:
  name: inference-api
  description: LLM inference API for enterprise AI platform
  labels:
    tier: ai-serving
    team: ai-platform
  annotations:
    github.com/project-slug: company/inference-api
    backstage.io/techdocs-ref: dir:.
    argocd/app-name: inference-api-production
    grafana/dashboard-selector: 'title=inference-api'
    pagerduty.com/service-id: PXXXXXX
    sonarqube.org/project-key: inference-api
  tags: [ai, production, python]
spec:
  type: service
  lifecycle: production
  owner: group:ai-platform-team
  system: ai-platform
  providesApis: [inference-api-v2]
  dependsOn:
    - component:vector-database
    - component:model-registry
    - resource:gpu-cluster
```

### Backstage Software Template for AI Service

```yaml
# template.yaml (new AI inference service golden path)
apiVersion: scaffolder.backstage.io/v1beta3
kind: Template
metadata:
  name: ai-inference-service
  title: AI Inference Service
  description: Deploy a new LLM inference endpoint on Kubernetes
  tags: [ai, kubernetes, python]
spec:
  owner: ai-platform-team
  type: service
  parameters:
    - title: Service Details
      required: [name, model, team]
      properties:
        name: { type: string, title: Service Name }
        model:
          type: string
          title: Base Model
          enum: [llama-3-8b, llama-3-70b, mistral-7b, custom]
        gpuCount:
          type: integer
          title: Number of GPUs
          default: 1
          minimum: 1
          maximum: 8
        team: { type: string, title: Owning Team }
  steps:
    - id: fetch
      name: Fetch Template
      action: fetch:template
      input:
        url: ./skeleton
        values:
          name: '${{ parameters.name }}'
          model: '${{ parameters.model }}'
          gpuCount: '${{ parameters.gpuCount }}'
    - id: create-repo
      name: Create GitHub Repository
      action: publish:github
      input:
        repoUrl: github.com?owner=company&repo=${{ parameters.name }}
    - id: argocd-app
      name: Register ArgoCD Application
      action: argocd:create-resources
      input:
        appName: '${{ parameters.name }}-production'
        projectName: ai-serving
```

## Crossplane: Infrastructure as Code on Kubernetes

Crossplane (CNCF graduated) extends Kubernetes to manage cloud infrastructure resources using the same declarative API model used for application workloads. It enables platform teams to define Composite Resources — opinionated abstractions over cloud services — that developers consume via familiar Kubernetes APIs.

### Crossplane Architecture

Crossplane's core controller manages XR composition. **Providers** map K8s resources to cloud API calls: `provider-aws` (RDS, S3, ElastiCache, EKS...), `provider-gcp` (CloudSQL, GCS, GKE...), `provider-azure` (AKS, Cosmos DB, Storage...). A **CompositeResourceDefinition (XRD)** defines a new API type (like a CRD); a **Composition** maps the XR to concrete managed resources; a **Composite Resource (XR)** is a cluster-scoped instance of an XRD; a **Claim** is a namespace-scoped reference to an XR, for developers.

Request flow: a developer creates a Claim → an XR is created → the Composition creates managed resources → the Provider calls the cloud API → the cloud resource is created → status propagates back.

### Crossplane: Self-Service Database

```yaml
# Platform team defines the XRD (the API that developers use)
apiVersion: apiextensions.crossplane.io/v1
kind: CompositeResourceDefinition
metadata:
  name: xpostgresqlinstances.db.company.com
spec:
  group: db.company.com
  names:
    kind: XPostgreSQLInstance
    plural: xpostgresqlinstances
  claimNames:
    kind: PostgreSQLInstance  # What developers use
    plural: postgresqlinstances
  versions:
    - name: v1alpha1
      served: true
      referenceable: true
      schema:
        openAPIV3Schema:
          type: object
          properties:
            spec:
              type: object
              properties:
                parameters:
                  type: object
                  properties:
                    storageGB: { type: integer, default: 20 }
                    tier: { type: string, enum: [dev, staging, production] }
---
# Developer creates a Claim (no cloud knowledge required)
apiVersion: db.company.com/v1alpha1
kind: PostgreSQLInstance
metadata:
  name: myapp-db
  namespace: production
spec:
  parameters:
    storageGB: 100
    tier: production
  writeConnectionSecretToRef:
    name: myapp-db-credentials
```

## Cluster Lifecycle Management

Enterprise Kubernetes fleets require automated cluster provisioning, upgrading, scaling, and decommissioning. Manual cluster management does not scale beyond a handful of clusters. ClusterAPI and managed Kubernetes services provide the declarative cluster lifecycle management that mirrors application GitOps.

### Cluster Management Tools

| Tool | Approach | Multi-Cloud | Best For |
|---|---|---|---|
| ClusterAPI (CAPI) | Declarative cluster lifecycle via K8s API | Yes (providers for AWS, GCP, Azure, vSphere, bare metal) | Standardised cluster provisioning across environments |
| EKS (eksctl/Terraform) | AWS-managed control plane | AWS only | AWS-native deployments |
| GKE (Terraform/Config Connector) | GCP-managed control plane | GCP only | GCP-native; GKE Autopilot for serverless nodes |
| AKS (Terraform/Bicep) | Azure-managed control plane | Azure only | Azure-native; Arc for hybrid |
| Rancher | Multi-cluster management UI + RKE/RKE2 | Yes | On-premises + multi-cloud; edge clusters |
| Tanzu (VMware/Broadcom) | vSphere-integrated K8s | VMware + cloud | VMware-centric enterprises |
| OpenShift | Full enterprise K8s platform | Yes | Enterprises needing an integrated platform |

### Cluster Upgrade Strategy

Kubernetes releases 3 minor versions per year; the support window is the latest 3 minor versions. Enterprise recommendation: stay within 1-2 minor versions of latest.

**Upgrade order (must be followed):** 1) etcd (if self-managed); 2) control plane nodes, one at a time for HA; 3) worker nodes, via rolling drain and upgrade.

**Pre-upgrade checklist:** back up etcd (mandatory); review API deprecations (`kubectl convert`, `kube-no-trouble`); test the upgrade in staging first; check addon compatibility (CNI, CSI, ingress versions); verify PodDisruptionBudgets protect critical workloads.

```bash
# Check for deprecated APIs before upgrade
kubectl krew install deprecations
kubectl deprecations --k8s-version v1.32

# Drain a node for upgrade
kubectl drain node-01 \
  --ignore-daemonsets \
  --delete-emptydir-data \
  --timeout=300s

# Upgrade node OS/k8s binaries, then:
kubectl uncordon node-01
```

## Related

- [K8s Handbook Part 9: Platform Engineering (Part 2)](parts/42-k8s-handbook-part9-platform-engineering-part2.md) — multi-tenancy, progressive delivery, landing zones, self-service patterns, AI platform golden paths, developer experience metrics, anti-patterns, and exercises
