---
title: "K8s Handbook Part 7: Storage (Part 2)"
doc_type: guide
domain: platforms
status: current
topic_id: k8s-handbook-part7-storage-part2
last_reviewed: 2026-07-27
maturity: practitioner
supersedes: []
tags: [kubernetes, storage, ai-infrastructure, backup, observability]
covers_version: "2025-2026 edition"
---

> Continues from [K8s Handbook Part 7: Storage](../40-k8s-handbook-part7-storage.md), covering Chapters 10-17: storage performance, AI artifact/model/vector-DB storage, backup and disaster recovery, observability, anti-patterns, and hands-on exercises.

## Storage Performance Optimisation

Storage is frequently the bottleneck in both database and AI workloads. Optimising storage performance in Kubernetes requires understanding the full I/O path: application → kernel page cache → filesystem → block device → CSI driver → network (for remote storage) → backend storage.

### I/O Path Optimisation

```bash
# Kernel page cache tuning (on node, via DaemonSet sysctl)
vm.dirty_ratio = 15                # % RAM for dirty pages before sync
vm.dirty_background_ratio = 5      # % RAM for background dirty writeback
vm.dirty_writeback_centisecs = 500 # Writeback every 5 seconds

# For databases: disable page cache reliance, use O_DIRECT
# PostgreSQL already uses O_DIRECT for WAL; fsync must stay enabled in production

# Block device queue depth (more parallel I/Os)
echo mq-deadline > /sys/block/nvme0n1/queue/scheduler
echo 64 > /sys/block/nvme0n1/queue/nr_requests

# XFS mount options for database workloads
mount -o noatime,nodiratime,nobarrier,inode64,allocsize=64m /dev/xvdf /data
# noatime:   no access time updates (reduces write I/O)
# nobarrier: disable write barriers (only safe with battery-backed cache)
# allocsize: large allocation unit for sequential workloads
```

### Storage Performance Benchmarking

```bash
# Run fio inside a Pod to benchmark PVC performance
kubectl run fio-bench --image=ljishen/fio --restart=Never -it \
  --overrides='{"spec":{"containers":[{"name":"fio","image":"ljishen/fio",
  "volumeMounts":[{"name":"bench","mountPath":"/data"}],"resources":{"requests":{"cpu":"4","memory":"4Gi"}}}],
  "volumes":[{"name":"bench","persistentVolumeClaim":{"claimName":"bench-pvc"}}]}}'

# Sequential read (streaming throughput for AI training)
fio --name=seq-read --rw=read --bs=1M --numjobs=4 --size=10G \
  --directory=/data --runtime=60 --time_based --group_reporting

# Random read (OLTP database pattern)
fio --name=rand-read --rw=randread --bs=4K --numjobs=16 \
  --size=10G --directory=/data --runtime=60 --time_based

# Sequential write (checkpoint, backup)
fio --name=seq-write --rw=write --bs=1M --numjobs=4 --size=10G \
  --directory=/data --runtime=60 --time_based --fsync=1
```

## AI Artifact Storage Patterns

AI and ML workloads have storage requirements fundamentally different from traditional enterprise applications. The size, access pattern, lifecycle, and sharing requirements of AI artifacts demand specific storage architectures for each artifact type.

### AI Artifact Storage Requirements

| Artifact Type | Typical Size | Access Pattern | Sharing | Recommended Storage |
|---|---|---|---|---|
| LLM Weights (full) | 7GB - 700GB | Read-heavy, sequential | Multi-pod RO | Object store + RWX PVC (WekaFS/NFS) |
| Fine-tuned adapter (LoRA) | 10MB - 5GB | Read-heavy | Multi-pod RO | Object store or RWO PVC |
| Training dataset | 100GB - 100TB | Sequential read, parallel | Multi-pod RO | Parallel FS (Lustre, WekaFS) or S3 |
| Training checkpoint | 1GB - 50GB | Write-heavy (training), read (resume) | Single writer | RWO NVMe SSD PVC |
| Embeddings/Index | 1GB - 10TB | Random read, write | Vector DB Pod | NVMe SSD RWO PVC |
| Experiment artifacts | Variable | Write once, read occasionally | Single namespace | Object store (MLflow, W&B) |
| Feature store data | 1GB - 1TB | Random read, batch write | Multi-service | Redis/Feast on SSD PVC |
| ONNX/TensorRT model | 100MB - 10GB | Read-only serving | Multi-replica RO | Container image or object store |

### Model Weight Serving Pattern

Serving large models (70B+ parameters) requires efficient weight loading. Three patterns are used in production:

- **Object store streaming** — models stored in S3/GCS; KServe or vLLM streams weights directly from the object store on startup. Simplest operational model; startup latency is proportional to model size (100GB at 10GB/s = 10s).
- **Shared RWX PVC** — model weights stored on a shared NFS/parallel filesystem PVC; multiple serving replicas mount the same PVC read-only. Fast access after the first load (no re-download); good for models served by multiple replicas.
- **Model baked into the container layer** — small models (under 2GB) can be embedded in the container image. A pull-through registry cache ensures fast node-local loading. Simplest for small models; impractical for large LLMs.

### S3-Compatible Model Storage with Mountpoint

```yaml
# Mount an S3 bucket as a PVC using Mountpoint for Amazon S3 CSI
# (also works with MinIO for on-premises S3-compatible storage)
apiVersion: v1
kind: PersistentVolume
metadata:
  name: model-weights-pv
spec:
  capacity:
    storage: 10Ti
  accessModes: [ReadOnlyMany]
  mountOptions:
    - allow-other
    - read-only
  csi:
    driver: s3.csi.aws.com
    volumeHandle: s3-model-weights-vol
    volumeAttributes:
      bucketName: company-model-registry
      region: us-east-1
---
# Use in an inference serving Pod
volumes:
  - name: model-weights
    persistentVolumeClaim:
      claimName: model-weights-pvc
      readOnly: true
containers:
  - name: vllm
    volumeMounts:
      - name: model-weights
        mountPath: /models
    env:
      - name: MODEL_PATH
        value: /models/llama-3-70b
```

## Model Repository Architecture

A model repository (model registry) is the system of record for ML models: it tracks model versions, metadata, lineage, metrics, and deployment status. In Kubernetes, the model registry must integrate with CI/CD, feature stores, inference serving, and observability systems.

### Model Registry Architecture Patterns

| Registry | Backend Storage | K8s Integration | Features |
|---|---|---|---|
| MLflow | S3, Azure Blob, local | Tracking server as Deployment; models from S3 | Tracking, metrics, packaging, registry |
| Weights & Biases | W&B cloud | SDK integration; artifacts from W&B | Experiment tracking, sweeps, artifacts |
| Kubeflow Model Registry | PostgreSQL + object store | CRD-based; native K8s | K8s-native versioning, serving integration |
| BentoML + Yatai | Object store + PostgreSQL | Yatai as K8s operator | Bento building, registry, deployment |
| Seldon Core v2 | OCI registry | CRD-based model server | Model mesh, A/B testing, explainability |
| DVC (Data Version Control) | Git + S3/GCS | Git-based; S3 for large files | Dataset + model versioning with Git |

### MLflow Deployment on Kubernetes

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: mlflow-tracking
  namespace: mlops
spec:
  replicas: 2
  selector:
    matchLabels: { app: mlflow }
  template:
    spec:
      containers:
        - name: mlflow
          image: ghcr.io/mlflow/mlflow:v2.13
          command:
            - mlflow
            - server
            - --backend-store-uri=postgresql://mlflow:PASSWORD@postgres:5432/mlflow
            - --default-artifact-root=s3://company-mlflow-artifacts/
            - --host=0.0.0.0
            - --port=5000
            - --workers=4
          env:
            - name: AWS_DEFAULT_REGION
              value: us-east-1
            - name: MLFLOW_S3_ENDPOINT_URL
              value: https://minio.internal.corp
          resources:
            requests: { cpu: 500m, memory: 1Gi }
            limits: { memory: 2Gi }
```

## Vector Database Storage

Vector databases are central to RAG (Retrieval-Augmented Generation) architectures. Their storage requirements are distinct: they maintain large in-memory indexes (for ANN search), persistent storage for durability, and require careful PVC sizing and performance tuning for production deployments.

### Vector Database Storage Sizing

| Database | Index Type | Memory Requirement | Disk Requirement | RWX Support |
|---|---|---|---|---|
| Weaviate | HNSW (in-memory) | 1.5x vector size in RAM | 3x for persistence | No (StatefulSet) |
| Qdrant | HNSW + memmap | Configurable (on-disk mode) | 2x vector size | No (StatefulSet) |
| Milvus | Multiple (HNSW, IVF, FLAT) | Variable by index type | 5x for segments | No (sharded) |
| pgvector | B-tree + IVFFlat | PostgreSQL shared_buffers | WAL + data files | No (StatefulSet) |
| Chroma | HNSW | In-process (embedding size) | SQLite + parquet | No |
| Pinecone | Managed SaaS | N/A (managed) | N/A (managed) | N/A |

### Qdrant on Kubernetes — Production Deployment

```yaml
# Qdrant StatefulSet with NVMe SSD storage
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: qdrant
  namespace: ai-platform
spec:
  serviceName: qdrant-headless
  replicas: 3
  selector:
    matchLabels: { app: qdrant }
  template:
    spec:
      containers:
        - name: qdrant
          image: qdrant/qdrant:v1.9.0
          ports:
            - { name: http, containerPort: 6333 }
            - { name: grpc, containerPort: 6334 }
            - { name: p2p, containerPort: 6335 }
          resources:
            requests: { cpu: '4', memory: 32Gi }
            limits: { memory: 64Gi }
          env:
            - name: QDRANT__CLUSTER__ENABLED
              value: 'true'
            - name: QDRANT__STORAGE__STORAGE_PATH
              value: /qdrant/storage
          volumeMounts:
            - name: storage
              mountPath: /qdrant/storage
  volumeClaimTemplates:
    - metadata:
        name: storage
      spec:
        accessModes: [ReadWriteOnce]
        storageClassName: fast-nvme
        resources:
          requests:
            storage: 500Gi
```

## Backup and Disaster Recovery

Kubernetes backup encompasses two distinct concerns: application data (PVC contents) and cluster state (etcd). A complete DR strategy must address both, with clearly defined RPO (Recovery Point Objective) and RTO (Recovery Time Objective) targets.

### Velero — Kubernetes Backup and DR

Velero is the de facto standard for Kubernetes backup. It backs up Kubernetes resources (as YAML) and PersistentVolume data (via CSI snapshots or Restic/Kopia file-level backup) to object storage.

```bash
# Install Velero (AWS S3 backend)
velero install \
  --provider aws \
  --plugins velero/velero-plugin-for-aws:v1.9.0 \
  --bucket my-velero-backups \
  --backup-location-config region=us-east-1 \
  --snapshot-location-config region=us-east-1 \
  --secret-file ./credentials-velero \
  --use-node-agent \
  --features=EnableCSI

# Create a scheduled backup (daily at 2AM UTC)
velero schedule create daily-backup \
  --schedule='0 2 * * *' \
  --include-namespaces production,staging \
  --ttl 720h \
  --snapshot-volumes=true

# Create an on-demand backup
velero backup create pre-upgrade-backup \
  --include-namespaces production \
  --snapshot-volumes=true \
  --wait

# Restore from backup
velero restore create --from-backup pre-upgrade-backup \
  --include-namespaces production \
  --namespace-mappings production:production-restored

# Check backup status
velero backup describe pre-upgrade-backup
velero backup logs pre-upgrade-backup
```

### DR Architecture Patterns

| Pattern | RTO | RPO | Cost | Implementation |
|---|---|---|---|---|
| Active-Passive (warm) | 15-60 min | Minutes (async replication) | Medium | Velero backups + DR cluster in warm standby |
| Active-Active (multi-region) | Seconds | Near-zero | High | Cilium Cluster Mesh + global load balancer |
| Backup-Restore | Hours | Hours (backup frequency) | Low | Velero scheduled backup to S3 |
| Pilot Light | 30-60 min | Minutes | Low-Medium | Minimal DR cluster + data replication |

## Storage Observability

### Key Storage Metrics

| Metric | Source | Alert Threshold | Action |
|---|---|---|---|
| `kubelet_volume_stats_used_bytes / capacity_bytes` | kubelet | Greater than 80% full | Expand PVC or add storage |
| `kubelet_volume_stats_inodes_used / total` | kubelet | Greater than 80% | Clean up small files; expand |
| `node_disk_io_time_seconds_total` | node_exporter | Greater than 80% util | Move to faster storage tier |
| `node_disk_read_bytes_total` | node_exporter | Near line rate | Investigate hot spot |
| `node_disk_write_bytes_total` | node_exporter | Near line rate | Check for runaway write processes |
| `ceph_health_status` | rook-ceph | Not 0 (HEALTH_OK) | Investigate Ceph cluster health |
| `longhorn_volume_actual_size_bytes` | longhorn | Near PVC capacity | Expand volume |

### Storage Capacity Planning

```
# Prometheus queries for storage capacity planning

# PVCs approaching capacity (> 80% full)
kubelet_volume_stats_used_bytes / kubelet_volume_stats_capacity_bytes > 0.8

# Fastest growing PVCs (will fill in < 7 days)
predict_linear(kubelet_volume_stats_used_bytes[6h], 7*24*3600) > kubelet_volume_stats_capacity_bytes

# Node disk I/O saturation
rate(node_disk_io_time_seconds_total[5m]) > 0.8

# Storage throughput by PVC
sum by (persistentvolumeclaim) (rate(kubelet_volume_stats_used_bytes[5m]))

# Velero backup success rate
velero_backup_success_total / velero_backup_attempt_total < 1
```

## Storage Anti-Patterns

- **Using `Delete` reclaim policy for production databases** — the PVC and underlying volume are deleted if the StatefulSet is accidentally deleted, causing complete data loss. Set `reclaimPolicy: Retain` in the StorageClass and enforce it via an OPA/Kyverno admission policy.
- **`Immediate` volumeBindingMode with zonal storage** — the PVC binds to a volume in the wrong availability zone, so the Pod cannot schedule near its data. Always use `WaitForFirstConsumer` for EBS, Azure Disk, and GCP PD; reserve `Immediate` for cluster-wide storage only.
- **Not sizing headroom** — a PVC fills to 100%, causing filesystem errors and write failures that crash the database. Alert at 75%, expand at 80%, and size the initial PVC at 130% of the expected data volume.
- **Using HostPath volumes in production** — data is tied to a specific node, Pod mobility is lost, there is no redundancy, and it is a security risk (host filesystem access). Use PVCs for all persistent data; reserve HostPath for system-level DaemonSet Pods (log collection, etc.).
- **`emptyDir` for persistent application data** — `emptyDir` is ephemeral and data is lost on Pod restart or node failure. Use `emptyDir` only for temp files, caches, or shared memory between containers — never for business data.
- **Not testing restore procedures** — backups exist but the restore path has never been tested, so a broken restore is discovered during an actual disaster. Run quarterly restore drills, automate restore tests as a CronJob into a staging namespace, and measure RTO.
- **Single StorageClass for all workloads** — databases share a storage class with logs, so noisy workloads impact database I/O. Define tiered StorageClasses: `ultra-ssd` for databases, `fast-ssd` for app storage, `standard` for logs/batch.

## Hands-On Exercises

### Exercise 7.1 — Dynamic Provisioning and Expansion

Experience the full dynamic provisioning lifecycle:

```bash
# 1. Create PVC (triggers dynamic provisioning)
kubectl apply -f - <<'YAML'
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: test-pvc
spec:
  accessModes: [ReadWriteOnce]
  storageClassName: standard
  resources:
    requests:
      storage: 5Gi
YAML
kubectl get pvc test-pvc -w
# Watch: Pending -> Bound (when a Pod is created, for WaitForFirstConsumer)

# 2. Write data and verify persistence
kubectl run writer --image=busybox --restart=Never \
  --command -- sh -c 'echo PERSISTENT > /data/test.txt; sleep 3600' \
  --overrides='{"spec":{"volumes":[{"name":"d","persistentVolumeClaim":{"claimName":"test-pvc"}}],
  "containers":[{"name":"writer","volumeMounts":[{"name":"d","mountPath":"/data"}]}]}}'

# 3. Expand the PVC (edit the storage request)
kubectl patch pvc test-pvc -p '{"spec":{"resources":{"requests":{"storage":"10Gi"}}}}'
kubectl get pvc test-pvc
```

### Exercise 7.2 — Volume Snapshot and Restore

Create a snapshot and restore from it:

```bash
# Install snapshot CRDs (if not present)
kubectl apply -f https://raw.githubusercontent.com/kubernetes-csi/external-snapshotter/master/client/config/crd/snapshot.storage.k8s.io_volumesnapshotclasses.yaml

# Create a VolumeSnapshot
kubectl apply -f - <<'YAML'
apiVersion: snapshot.storage.k8s.io/v1
kind: VolumeSnapshot
metadata:
  name: test-snap
spec:
  volumeSnapshotClassName: csi-snapclass
  source:
    persistentVolumeClaimName: test-pvc
YAML

# Wait for the snapshot to be ready
kubectl get volumesnapshot test-snap -w

# Restore into a new PVC
kubectl apply -f - <<'YAML'
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: test-restored
spec:
  dataSource:
    name: test-snap
    kind: VolumeSnapshot
    apiGroup: snapshot.storage.k8s.io
  accessModes: [ReadWriteOnce]
  resources:
    requests:
      storage: 5Gi
YAML
```

## Related

- [K8s Handbook Part 7: Storage](../40-k8s-handbook-part7-storage.md) — Part 1: Storage Architecture, CSI, Dynamic Provisioning, Snapshots, Cloud Storage, Ceph/Rook, Longhorn, OpenEBS, NFS
