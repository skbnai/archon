# Split Plan: K8s Handbook Part 5 — Kubernetes Resources

**Source:** `/workspace/knowledge-docs/docs/cloud-platforms/kubernetes/K8s_Handbook_Part5_Kubernetes_Resources.md` (~4,396 words body)

**Reason:** Word count exceeds guide doc_type cap (2600 words hard cap)

## Split Boundary

**Part 1 (Main):** `docs/platforms/38-k8s-handbook-part5-kubernetes-resources.md`
- Source: Chapters 1–9 (Resource Taxonomy, Pods, Workload Resources, Batch Resources, Service/Endpoint Resources, Ingress and Gateway API, ConfigMaps/Secrets, Storage, Namespaces/ResourceQuota/LimitRange)
- Content: the universal resource structure and resource taxonomy table, Pod health probe types and multi-container patterns, Deployment/StatefulSet/DaemonSet, Jobs/CronJobs including an AI/ML gang-scheduled training pattern, Service types and EndpointSlices, Ingress and Gateway API, ConfigMaps/Secrets (with the Secret-encryption production warning) and External Secrets Operator, the PV/PVC/StorageClass/CSI storage model and AI/ML storage patterns, namespace strategy and ResourceQuota/LimitRange

**Part 2 (Supplementary):** `docs/platforms/parts/38-k8s-handbook-part5-kubernetes-resources-part2.md`
- Source: Chapters 10–17 (ServiceAccounts and RBAC, Network Policies, Autoscaling, Scheduling, PodDisruptionBudgets, RuntimeClass/PodSecurity, Resource Anti-Patterns, Hands-On Exercises)
- Content: the RBAC model and ServiceAccount workload identity (Workload Identity/IRSA), default-deny NetworkPolicy and a microservices allow-list pattern, the HPA/VPA/KEDA/Cluster Autoscaler/Karpenter autoscaling layers, PriorityClass preemption tiers and TopologySpread constraints, PodDisruptionBudgets and their anti-patterns, RuntimeClass and Pod Security Standards, a 10-item resource anti-pattern reference table, 3 hands-on exercises

## Source-quality notes (converted-pdf artifacts fixed during migration)

- Chapter 2's "Complete Production Pod Specification" subsection heading was followed by no content — the example YAML was stripped entirely during PDF extraction, leaving only the "Pod Health Probe Decision Guide" table that should have come after it. Since the exact original field values are unrecoverable, this was NOT reconstructed as "the original spec." Instead, a compact illustrative Pod example was written that ties together only the concepts the chapter itself goes on to describe (the three probe types, resource requests/limits) — consistent with how every other chapter in this source uses an illustrative (not company-specific) YAML example, and clearly serving the same teaching purpose rather than claiming to recover lost specifics.
- Chapter 15's Pod Security Standards table had its rightmost cell's content garbled into a single run-on cell mixing a namespace-enforcement YAML example with table syntax — separated back into a proper table plus a separate fenced YAML block.
- Numerous flattened multi-line YAML blocks reconstructed into properly line-broken fenced blocks (Deployment, StatefulSet, DaemonSet reference, Jobs/CronJobs, AI/ML training Job, Services, EndpointSlice, Ingress, Gateway API, ConfigMap/Secret, ExternalSecret, StorageClass, ResourceQuota/LimitRange, Role/RoleBinding, ServiceAccount, NetworkPolicy, HPA, KEDA ScaledObject, PriorityClass, TopologySpreadConstraints, PodDisruptionBudget, RuntimeClass, all 3 exercises).
- Tables split across a PDF page break with duplicated header rows (Resource Scope and Taxonomy) merged into a single table.
- One "Secret Security Warning" `<mark>` callout converted to a blockquote.

## Navigation

- Part 1 ends with a pointer to Part 2 (RBAC, NetworkPolicies, autoscaling, scheduling, PDBs, runtime/policy, anti-patterns, exercises).
- Topic ID: both parts share the `k8s-handbook-part5-kubernetes-resources` topic family.
- Part 1 is canonical (`topic_id: k8s-handbook-part5-kubernetes-resources`).
- Part 2 uses `topic_id: k8s-handbook-part5-kubernetes-resources-part2`, `supersedes: []` (Part 1 carries the supersedes entry).
