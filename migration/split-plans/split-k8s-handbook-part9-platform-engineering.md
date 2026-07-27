# Split Plan: K8s Handbook Part 9 — Platform Engineering

**Source:** `/workspace/knowledge-docs/docs/cloud-platforms/kubernetes/K8s_Handbook_Part9_Platform_Engineering.md` (~4,714 words body)

**Reason:** Word count exceeds guide doc_type cap (2600 words hard cap)

## Split Boundary

**Part 1 (Main):** `docs/platforms/42-k8s-handbook-part9-platform-engineering.md`
- Source: Chapters 1–9 (Platform Engineering Philosophy and Goals, GitOps: Principles and Patterns, ArgoCD, Flux, Helm, Kustomize, Backstage, Crossplane, Cluster Lifecycle Management)
- Content: the platform engineering value proposition/core principles/team topologies, the four GitOps principles and repository patterns, ArgoCD architecture/Application/ApplicationSet, Flux controllers/GitRepository/Kustomization and the ArgoCD-vs-Flux decision matrix, Helm chart structure and a production values pattern, Kustomize architecture and kustomization files, Backstage core components/catalog-info.yaml/an AI-service software template, Crossplane architecture and a self-service database XRD/Claim example, cluster management tool comparison and the cluster upgrade strategy/checklist

**Part 2 (Supplementary):** `docs/platforms/parts/42-k8s-handbook-part9-platform-engineering-part2.md`
- Source: Chapters 10–17 (Multi-Tenancy Architectures, Progressive Delivery, Landing Zones and Cluster Blueprints, Self-Service Platform Patterns, Platform Engineering for AI Workloads, Developer Experience Metrics, Platform Anti-Patterns, Hands-On Exercises)
- Content: multi-tenancy models and vCluster virtual clusters, Argo Rollouts progressive delivery with automated quality gates, cluster bootstrap architecture and standard namespace labels/annotations, the self-service capabilities matrix and a Namespace-as-a-Service Crossplane pattern, AI platform golden paths and GPU resource management, DORA metrics and platform-specific developer experience metrics, 6 platform anti-patterns, 2 hands-on exercises

## Source-quality notes (converted-pdf artifacts fixed during migration)

- Numerous flattened multi-line YAML/shell blocks reconstructed into properly line-broken fenced blocks (GitOps repository tree, ArgoCD Application/ApplicationSet, Flux GitRepository/Kustomization, Helm values patterns, Kustomize files, Backstage catalog-info.yaml/software template, Crossplane XRD/Claim, cluster upgrade commands, vCluster creation, Argo Rollouts quality gates, namespace labeling template, Namespace-as-a-Service pattern, and both exercises).
- Two tables (Platform Team Topologies in Chapter 1, Flux Controllers/ArgoCD-vs-Flux comparison in Chapters 2 and 4) were split across PDF page breaks with duplicated header rows — merged into single tables.
- No content-loss (heading-then-nothing) artifacts were found in this source; all chapters retained their body text.

## Navigation

- Part 1 ends with a pointer to Part 2 (multi-tenancy, progressive delivery, landing zones, self-service patterns, AI platform golden paths, developer experience metrics, anti-patterns, exercises).
- Topic ID: both parts share the `k8s-handbook-part9-platform-engineering` topic family.
- Part 1 is canonical (`topic_id: k8s-handbook-part9-platform-engineering`).
- Part 2 uses `topic_id: k8s-handbook-part9-platform-engineering-part2`, `supersedes: []` (Part 1 carries the supersedes entry).
