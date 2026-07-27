# Split Plan: K8s Handbook Part 4 — Kubernetes Internals

**Source:** `/workspace/knowledge-docs/docs/cloud-platforms/kubernetes/K8s_Handbook_Part4_Kubernetes_Internals.md` (~5,695 words body)

**Reason:** Word count exceeds guide doc_type cap (2600 words hard cap)

## Split Boundary

**Part 1 (Main):** `docs/platforms/37-k8s-handbook-part4-kubernetes-internals.md`
- Source: Chapters 1–4 (Kubernetes Architecture Overview, The API Server, etcd, The Scheduler)
- Content: control/data-plane split and core architectural principles, API request processing pipeline, API groups/versioning, the watch/informer mechanism, API server HA and scalability, etcd/Raft consensus, etcd key structure and performance targets, etcd backup/DR and compaction, the full scheduling lifecycle (filtering → scoring → binding), the scheduling framework extension points, node affinity/taints/tolerations

**Part 2 (Supplementary):** `docs/platforms/parts/37-k8s-handbook-part4-kubernetes-internals-part2.md`
- Source: Chapters 5–7 (Controller Manager, Cloud Controller Manager, The kubelet)
- Content: the reconciliation loop pattern, core built-in controllers table, Deployment rollout mechanics, CCM controllers and the LoadBalancer Service flow, kubelet responsibilities, static Pods, Pod lifecycle phases

**Part 3 (Supplementary):** `docs/platforms/parts/37-k8s-handbook-part4-kubernetes-internals-part3.md`
- Source: Chapters 8–12 (kube-proxy, CoreDNS, Admission Controllers, CRDs, The Operator Pattern)
- Content: kube-proxy modes and Service-type behaviour, CoreDNS resolution hierarchy and Corefile, built-in and dynamic (webhook) admission controllers with the webhook-failure-mode warning, OPA Gatekeeper vs. Kyverno, CRD structure and best practices, the Operator maturity model and production AI-workload operators

**Part 4 (Supplementary):** `docs/platforms/parts/37-k8s-handbook-part4-kubernetes-internals-part4.md`
- Source: Chapters 13–16 (Leader Election and High Availability, API Request Lifecycle, Troubleshooting the Control Plane, Hands-On Exercises)
- Content: the Lease-based leader election mechanism, the HA control-plane reference architecture, the complete kubectl-apply-to-running-Pod lifecycle across all 6 phases, 5 common control-plane troubleshooting scenarios, 3 hands-on exercises

## Source-quality notes (converted-pdf artifacts fixed during migration)

- Chapter 1's "High-Level Architecture" subsection heading was followed by no content at all — the architecture diagram image was stripped entirely during PDF extraction with no ASCII fallback. Reconstructed as a Mermaid diagram summarizing the control-plane/data-plane split using only the component names and relationships the source document itself goes on to describe in full in Chapters 2–9 (API server, etcd, scheduler, controller manager, CCM, kubelet, kube-proxy, CoreDNS) — no new facts introduced, just a visual summary of content already present elsewhere in the source.
- Numerous flattened multi-line shell/YAML/JSON/Go blocks reconstructed into properly line-broken fenced blocks (API request pipeline, watch API examples, etcd Raft write path, etcd backup/restore commands, scheduling lifecycle, CRD manifests, admission webhook configs, leader election mechanism, the full API request lifecycle, all 3 exercises).
- Two ASCII architecture diagrams (Kubernetes HA reference architecture control-plane-node layout) converted to Mermaid.
- Tables split across a PDF page break with duplicated header rows (etcd performance/sizing, Pod lifecycle phases, core controllers, scheduling extension points, node affinity/taints/tolerations mechanisms, operators for AI workloads) merged into single tables.
- One "Webhook Failure Modes" `<mark>` callout converted to a blockquote.

## Navigation

- Each part ends with a pointer to the next part's topic coverage.
- Topic ID: all four parts share the `k8s-handbook-part4-kubernetes-internals` topic family.
- Part 1 is canonical (`topic_id: k8s-handbook-part4-kubernetes-internals`).
- Parts 2–4 use `topic_id: k8s-handbook-part4-kubernetes-internals-part2/3/4`; all `supersedes: []` (Part 1 carries the supersedes entry).
