# Split Plan: K8s Handbook Part 7 — Storage

**Source:** `/workspace/knowledge-docs/docs/cloud-platforms/kubernetes/K8s_Handbook_Part7_Storage.md` (~4,171 words body)

**Reason:** Word count exceeds guide doc_type cap (2600 words hard cap)

## Split Boundary

**Part 1 (Main):** `docs/platforms/40-k8s-handbook-part7-storage.md`
- Source: Chapters 1–9 (Kubernetes Storage Architecture, CSI Architecture and Driver Development, Dynamic Provisioning Deep Dive, Volume Snapshots and Cloning, Cloud Storage Integrations, Distributed Storage: Ceph/Rook, Longhorn, OpenEBS, NFS and Shared Filesystems)
- Content: the three-layer storage abstraction (StorageClass/PV/PVC), storage lifecycle and reclaim policies, the StorageClass design matrix, CSI architecture and sidecar containers, the CSI driver capabilities matrix, production StorageClass examples, PVC best practices, volume snapshots/cloning, the cloud storage integration matrix (AWS/GCP/Azure/on-prem), AWS EBS CSI production config, Ceph/Rook architecture, Longhorn architecture and the Longhorn-vs-Ceph decision matrix, OpenEBS engines including Mayastor, NFS-based shared storage, and high-performance parallel filesystems for AI

**Part 2 (Supplementary):** `docs/platforms/parts/40-k8s-handbook-part7-storage-part2.md`
- Source: Chapters 10–17 (Storage Performance Optimisation, AI Artifact Storage Patterns, Model Repository Architecture, Vector Database Storage, Backup and Disaster Recovery, Storage Observability, Storage Anti-Patterns, Hands-On Exercises)
- Content: the full I/O path and kernel/filesystem tuning, fio-based storage benchmarking, AI artifact storage requirements and model-weight serving patterns, S3-compatible model storage via Mountpoint, model registry architecture and an MLflow deployment, vector database storage sizing and a Qdrant production deployment, Velero backup/DR and DR architecture patterns, key storage metrics and capacity-planning queries, 7 storage anti-patterns, 2 hands-on exercises

## Source-quality notes (converted-pdf artifacts fixed during migration)

- Numerous flattened multi-line YAML/shell blocks reconstructed into properly line-broken fenced blocks (StorageClass examples, PVC best-practice example, volume snapshot/clone workflow, AWS EBS CSI Helm install, Rook CephCluster, Mayastor install, NFS provisioner, fio benchmarking, Mountpoint S3 mount, MLflow deployment, Qdrant StatefulSet, Velero install, capacity-planning Prometheus queries, both exercises).
- Two tables (Storage Class Design Matrix in Chapter 1, CSI Driver Capabilities Matrix in Chapter 2) were each split across a PDF page break with a duplicated header row — merged into a single table.
- No content-loss (heading-then-nothing) artifacts were found in this source; all chapters retained their body text.

## Navigation

- Part 1 ends with a pointer to Part 2 (performance, AI artifact storage, model/vector-DB storage, backup/DR, observability, anti-patterns, exercises).
- Topic ID: both parts share the `k8s-handbook-part7-storage` topic family.
- Part 1 is canonical (`topic_id: k8s-handbook-part7-storage`).
- Part 2 uses `topic_id: k8s-handbook-part7-storage-part2`, `supersedes: []` (Part 1 carries the supersedes entry).
