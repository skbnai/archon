---
title: "K8s Handbook Part 7: Storage"
doc_type: guide
domain: platforms
status: current
topic_id: k8s-handbook-part7-storage
last_reviewed: 2026-07-27
maturity: practitioner
supersedes: [docs/cloud-platforms/kubernetes/K8s_Handbook_Part7_Storage.md]
tags: [kubernetes, storage, csi, ceph, longhorn]
covers_version: "2025-2026 edition"
---

Kubernetes storage is a three-layer abstraction designed to decouple storage provisioning (an infrastructure concern) from storage consumption (an application concern). Understanding each layer is essential for designing storage systems that are performant, durable, and operationally manageable at enterprise scale.

## Kubernetes Storage Architecture

### The Three Storage Layers

- **StorageClass (infrastructure layer)** — defines HOW storage is provisioned: the provisioner name, parameters (disk type, IOPS, encryption), reclaim policy, and binding mode. Created by the storage administrator; analogous to a product catalog entry for storage types.
- **PersistentVolume (storage layer)** — represents an actual piece of provisioned storage. Can be statically created (pre-provisioned) or dynamically created by a CSI provisioner. Lives at the cluster scope, not namespaced. Contains the actual volume details (volume ID, capacity, access modes, reclaim policy).
- **PersistentVolumeClaim (workload layer)** — a request for storage by an application. Created by developers; specifies desired capacity, access modes, and StorageClass. The PVC controller binds a PVC to an appropriate PV, either existing or newly provisioned. PVCs are namespaced.

### Storage Lifecycle

**Static provisioning:** an admin creates a PV manually, a developer creates a PVC, and the binder matches the PVC to the PV.

**Dynamic provisioning (recommended):** a developer creates a PVC with a StorageClass; the PVC controller detects the unbound PVC; the CSI provisioner creates a volume in the backend; a PV is auto-created and bound.

**Volume binding modes:** `Immediate` creates/binds the PV when the PVC is created (risk: the PV may end up in the wrong zone for the Pod); `WaitForFirstConsumer` creates the PV only when the Pod is scheduled, ensuring the volume is in the same zone as the Pod — recommended for zonal storage (EBS, Azure Disk).

**Reclaim policies:** `Delete` removes the PV and underlying volume when the PVC is deleted (use for ephemeral/dev storage); `Retain` keeps the PV and volume, requiring manual cleanup (required for production databases); `Recycle` is deprecated — do not use.

### Storage Class Design Matrix

| StorageClass | Backend | Access Mode | IOPS | Use Case |
|---|---|---|---|---|
| ultra-ssd | AWS io2/GCP pd-extreme | RWO | 64,000 | Databases, etcd |
| fast-ssd | AWS gp3/GCP pd-ssd | RWO | 16,000 | App storage, AI checkpoints |
| standard | AWS gp2/GCP pd-standard | RWO | 3,000 | General workloads |
| shared-nfs | NFS/NetApp | RWX | Variable | Shared datasets, config |
| fast-shared | Lustre/WekaFS | RWX | 1,000,000+ | AI training datasets |
| object-backed | Rook-Ceph RGW | RWX | Variable | Model artifacts, logs |
| local-nvme | Local NVMe (node-local) | RWO | 500,000+ | Ultra-low latency DB |

## CSI Architecture and Driver Development

The Container Storage Interface (CSI) is the standard API for storage plugins in Kubernetes. It replaced the in-tree volume plugins (which required Kubernetes core code changes) with an out-of-tree plugin model where storage vendors implement a gRPC server that Kubernetes calls.

### CSI Architecture

CSI drivers are typically deployed as a Deployment plus a DaemonSet. The **controller plugin** (Deployment, runs anywhere) implements the ControllerService — `CreateVolume`, `DeleteVolume`, `ControllerPublishVolume` (attach/detach a volume to/from a node) — via the `external-provisioner`, `external-attacher`, and `external-snapshotter` sidecars. The **node plugin** (DaemonSet, runs on every node) implements the NodeService — `NodePublishVolume` (mount to Pod), `NodeUnpublishVolume` (unmount from Pod), `NodeStageVolume` (global mount on node, for block devices) — via the `node-driver-registrar` sidecar.

CSI RPC flow for dynamic provisioning:

1. A developer creates a PVC.
2. The `external-provisioner` sidecar watches the PVC.
3. `external-provisioner` calls the `CSI.CreateVolume` RPC.
4. The CSI driver creates a volume in the backend (e.g. the AWS `CreateVolume` API).
5. The CSI driver returns a `volume_id`.
6. `external-provisioner` creates a PV with that `volume_id`.
7. The PV is bound to the PVC.
8. The Pod is scheduled.
9. `external-attacher` calls `CSI.ControllerPublishVolume` (e.g. attaches the EBS volume to the EC2 instance).
10. kubelet calls `CSI.NodePublishVolume` (e.g. mounts `/dev/xvdf` into the Pod filesystem).

### CSI Sidecar Containers

| Sidecar | Role | Watches |
|---|---|---|
| external-provisioner | Creates/deletes volumes; creates/deletes PVs | PVC with matching StorageClass |
| external-attacher | Calls ControllerPublish/UnpublishVolume | VolumeAttachment objects |
| external-snapshotter | Creates/deletes volume snapshots | VolumeSnapshot objects |
| external-resizer | Expands volumes | PVC with increased storage request |
| node-driver-registrar | Registers the CSI driver with kubelet | NodeServer socket |
| livenessprobe | Health check for the CSI driver | CSI driver gRPC endpoint |

### CSI Driver Capabilities Matrix

| Driver | Provisioning | Snapshots | Resize | RWX | Encryption | Clone |
|---|---|---|---|---|---|---|
| aws-ebs-csi | Yes | Yes | Yes | No | KMS | Yes |
| gcp-pd-csi | Yes | Yes | Yes | No | CMEK | Yes |
| azure-disk-csi | Yes | Yes | Yes | No | CMEK | Yes |
| azure-file-csi | Yes | No | Yes | Yes | No | No |
| efs-csi (AWS) | Yes | No | No | Yes | KMS | No |
| rook-ceph-rbd | Yes | Yes | Yes | No | LUKS | Yes |
| rook-ceph-cephfs | Yes | Yes | Yes | Yes | LUKS | No |
| longhorn | Yes | Yes | Yes | No | Yes | Yes |
| local-path-provisioner | Yes | No | No | No | No | No |

## Dynamic Provisioning Deep Dive

Dynamic provisioning automates the creation of PersistentVolumes when a PVC is submitted, eliminating the need for storage admins to pre-provision volumes and enabling self-service storage for development teams.

### StorageClass Production Examples

```yaml
# AWS EBS gp3 with encryption
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: ebs-gp3-encrypted
  annotations:
    storageclass.kubernetes.io/is-default-class: 'true'
provisioner: ebs.csi.aws.com
parameters:
  type: gp3
  iops: '3000'
  throughput: '125'
  encrypted: 'true'
  kmsKeyId: arn:aws:kms:us-east-1:123456789:key/mrk-abc123
reclaimPolicy: Retain  # CRITICAL for production data
volumeBindingMode: WaitForFirstConsumer
allowVolumeExpansion: true
mountOptions:
  - noatime
  - nodiratime
---
# GCP SSD persistent disk
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: gcp-ssd
provisioner: pd.csi.storage.gke.io
parameters:
  type: pd-ssd
  disk-encryption-kms-key: projects/myproject/locations/us-central1/keyRings/myring/cryptoKeys/mykey
reclaimPolicy: Retain
volumeBindingMode: WaitForFirstConsumer
allowVolumeExpansion: true
---
# Local NVMe for maximum performance (requires manual PV creation per node)
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: local-nvme
provisioner: kubernetes.io/no-provisioner
volumeBindingMode: WaitForFirstConsumer
reclaimPolicy: Delete
```

### PVC Best Practices

```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: database-data
  namespace: production
  labels:
    app: postgres
    tier: database
  annotations:
    storage.company.com/owner: 'platform-team'
    storage.company.com/backup: 'daily'
spec:
  accessModes: [ReadWriteOnce]
  storageClassName: ebs-gp3-encrypted
  resources:
    requests:
      storage: 100Gi
# Volume expansion (after initial creation, only increase allowed):
# edit resources.requests.storage to a larger value.
# StorageClass must have allowVolumeExpansion: true.
```

Production checklist for PVCs:

1. Always use the `Retain` reclaim policy for production databases.
2. Use `WaitForFirstConsumer` binding mode for zonal storage.
3. Enable volume expansion in the StorageClass.
4. Size 20-30% larger than the current need.
5. Monitor usage with the `kubelet_volume_stats_used_bytes` metric.

## Volume Snapshots and Cloning

Volume snapshots enable point-in-time copies of PersistentVolumes for backup, testing, and disaster recovery. Volume cloning creates a new volume pre-populated with the data from an existing PVC. Both are implemented via CSI and require driver support.

### Volume Snapshot Workflow

```yaml
# 1. Define a VolumeSnapshotClass
apiVersion: snapshot.storage.k8s.io/v1
kind: VolumeSnapshotClass
metadata:
  name: ebs-vsc
  annotations:
    snapshot.storage.kubernetes.io/is-default-class: 'true'
driver: ebs.csi.aws.com
deletionPolicy: Retain  # Keep snapshot even if VolumeSnapshot is deleted
parameters:
  tagSpecification_1: 'key=backup-type,value=pre-upgrade'
---
# 2. Take a snapshot
apiVersion: snapshot.storage.k8s.io/v1
kind: VolumeSnapshot
metadata:
  name: postgres-backup-20250601
  namespace: production
spec:
  volumeSnapshotClassName: ebs-vsc
  source:
    persistentVolumeClaimName: database-data
---
# 4. Restore from snapshot (new PVC from snapshot)
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: database-restored
  namespace: production
spec:
  storageClassName: ebs-gp3-encrypted
  dataSource:
    name: postgres-backup-20250601
    kind: VolumeSnapshot
    apiGroup: snapshot.storage.k8s.io
  accessModes: [ReadWriteOnce]
  resources:
    requests:
      storage: 100Gi
```

```bash
# 3. Check snapshot readiness
kubectl get volumesnapshot postgres-backup-20250601 -n production
kubectl describe volumesnapshot postgres-backup-20250601 -n production
# Wait for: ReadyToUse: true
```

### Volume Cloning

```yaml
# Clone a PVC to a new PVC (pre-populated with source data)
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: database-clone-for-testing
  namespace: staging
spec:
  storageClassName: ebs-gp3-encrypted
  dataSource:
    name: database-data  # Source PVC (must be in same namespace)
    kind: PersistentVolumeClaim
  accessModes: [ReadWriteOnce]
  resources:
    requests:
      storage: 100Gi
```

Use case: copy a production database to staging for testing. Much faster than backup/restore since there is no data movement at the storage layer — storage efficiency comes from copy-on-write at the backend (only changes are stored).

## Cloud Storage Integrations

| Cloud | Block Storage | File Storage | Object Storage | Key Considerations |
|---|---|---|---|---|
| AWS | EBS (gp3, io2) via aws-ebs-csi | EFS via aws-efs-csi | S3 via Mountpoint | EBS = zonal; EFS = regional; io2 for IOPS-heavy |
| GCP | Persistent Disk via pd-csi | Filestore via filestore-csi | GCS via gcsfuse | pd-extreme for ultra-high IOPS; balanced for general |
| Azure | Managed Disk via azuredisk-csi | Azure Files via azurefile-csi | Blob via blobfuse2 | Ultra Disk for VMs with UltraSSD support enabled |
| On-prem | Ceph RBD, vSphere VMDK | CephFS, NFS, NetApp | MinIO, Ceph RGW | Ceph = unified; NetApp = enterprise support + snapshots |

### AWS EBS CSI — Production Configuration

```bash
# Install AWS EBS CSI Driver (IAM required)
helm repo add aws-ebs-csi-driver https://kubernetes-sigs.github.io/aws-ebs-csi-driver
helm install aws-ebs-csi-driver aws-ebs-csi-driver/aws-ebs-csi-driver \
  --namespace kube-system \
  --set controller.serviceAccount.annotations."eks\.amazonaws\.com/role-arn"=arn:aws:iam::ACCOUNT:role/EBSCSIRole \
  --set enableVolumeScheduling=true \
  --set enableVolumeResizing=true \
  --set enableVolumeSnapshot=true
```

StorageClass tiers: gp3 base gives 3,000 IOPS / 125 MB/s at $0.08/GB-month; gp3 tuned reaches up to 16,000 IOPS / 1,000 MB/s (+$0.006/IOPS above 3,000); io2 reaches up to 64,000 IOPS at $0.125/GB + $0.065/IOPS. Prefer gp3 over gp2 for cost: gp2 gives only 3 IOPS/GB baseline (100GB = 300 IOPS), while gp3 always gives a 3,000 IOPS baseline regardless of size — gp3 is roughly 20% cheaper and 10x more performant by default.

## Distributed Storage: Ceph / Rook

Ceph is the most widely deployed open-source distributed storage system. It provides block (RBD), file (CephFS), and object (RADOS Gateway) storage from a single storage cluster. Rook is the Kubernetes Operator for Ceph, making it possible to run and manage Ceph entirely within Kubernetes.

### Ceph Architecture

Ceph's components: **MON** (Monitors, 3 or 5) maintain the cluster map using Paxos consensus; **MGR** (Managers, 2) provide metrics, dashboards, and an orchestration interface; **OSD** (Object Storage Daemons, 1 per disk) store data and handle replication; **MDS** (Metadata Servers, CephFS only) manage the filesystem namespace; **RGW** (RADOS Gateway) is an S3/Swift-compatible object storage endpoint.

Data distribution uses the CRUSH algorithm: data is divided into objects, placed into placement groups (PGs), and the CRUSH map determines which OSDs store each PG. Default is 3-way replication (data stored on 3 different OSDs); an alternative is erasure coding (k+m coding — more space-efficient, higher latency).

Performance characteristics: latency of 0.5-5ms (NVMe-backed) or 5-20ms (HDD-backed); throughput scales linearly with OSD count (~1GB/s per NVMe OSD typical); 100K+ IOPS per NVMe OSD; scale to petabytes across thousands of OSDs.

```bash
# Rook-Ceph quick start
kubectl apply -f https://raw.githubusercontent.com/rook/rook/master/deploy/examples/crds.yaml
kubectl apply -f https://raw.githubusercontent.com/rook/rook/master/deploy/examples/common.yaml
kubectl apply -f https://raw.githubusercontent.com/rook/rook/master/deploy/examples/operator.yaml
```

### Rook CephCluster Configuration

```yaml
apiVersion: ceph.rook.io/v1
kind: CephCluster
metadata:
  name: rook-ceph
  namespace: rook-ceph
spec:
  cephVersion:
    image: quay.io/ceph/ceph:v18.2
  dataDirHostPath: /var/lib/rook
  mon:
    count: 3
    allowMultiplePerNode: false
  mgr:
    count: 2
    modules:
      - name: pg_autoscaler
        enabled: true
      - name: dashboard
        enabled: true
  dashboard:
    enabled: true
    ssl: true
  storage:
    useAllNodes: false
    useAllDevices: false
    nodes:
      - name: storage-node-01
        devices:
          - name: nvme0n1
          - name: nvme1n1
      - name: storage-node-02
        devices:
          - name: nvme0n1
  network:
    provider: host  # Host networking for maximum performance
    selectors:
      public: en01   # Separate public and cluster networks
      cluster: en02
  placement:
    all:
      tolerations:
        - key: storage-node
          operator: Exists
          effect: NoSchedule
```

## Longhorn — Cloud-Native Block Storage

Longhorn (CNCF incubating, from Rancher/SUSE) is a lightweight, distributed block storage system for Kubernetes. Unlike Ceph (which requires dedicated storage nodes), Longhorn uses the existing worker node disks, making it ideal for smaller clusters, edge deployments, and environments without dedicated storage infrastructure.

### Longhorn Architecture

The **Longhorn Manager** (DaemonSet on every node) manages volume lifecycle on the node and schedules replicas across nodes. The **Longhorn Engine** (per volume, per node) exposes a block device to the Pod (frontend) and syncs data to replica processes on other nodes (replication). Each **Replica** (per volume, per node) stores actual data on the node-local disk; each volume has N replicas (default: 3).

Write path: Pod → Engine → (replica-1, replica-2, replica-3); all replicas must acknowledge before the write is confirmed. On node failure, Longhorn automatically rebuilds the missing replica.

Features: CSI-compliant (block only); volume snapshots and backups to S3/NFS; recurring backup schedules; volume encryption (LUKS); RWO only (block storage); live volume expansion; disaster recovery volumes (cross-cluster backup/restore).

### Longhorn vs Ceph Decision Matrix

| Dimension | Longhorn | Ceph/Rook |
|---|---|---|
| Deployment complexity | Low (helm install) | High (dedicated nodes, tuning) |
| Minimum cluster size | 3 nodes | 5+ nodes recommended |
| Dedicated storage nodes | No (uses worker disks) | Yes (recommended) |
| Storage types | Block (RWO) only | Block, File (RWX), Object |
| Performance | Good (network replication overhead) | Excellent (NVMe-backed) |
| Snapshots | Yes (software snapshots) | Yes (RBD snapshots, very fast) |
| Backup | Yes (to S3, NFS) | Yes (RBD mirror, RGW) |
| Scale | Small-medium (up to 500TB) | Petabyte scale |
| UI | Built-in web UI | Ceph Dashboard, custom |
| Best for | Edge, small clusters, RKE/k3s | Large enterprise, AI storage |

## OpenEBS — Container-Attached Storage

OpenEBS (CNCF sandbox) pioneered the Container-Attached Storage (CAS) pattern: each volume has its own dedicated storage controller running as a Pod. This gives each volume complete isolation — a noisy volume cannot impact others. OpenEBS provides multiple storage engines for different use cases.

| Engine | Type | Technology | Use Case |
|---|---|---|---|
| Mayastor (now OpenEBS v3) | Block | NVMe-oF/SPDK | Ultra-high performance (sub-ms latency) |
| LocalPV-Hostpath | Block | Hostpath bind mount | Simple local storage; no replication |
| LocalPV-ZFS | Block | ZFS on node | Snapshots, compression, checksums locally |
| LocalPV-LVM | Block | LVM on node | Volume groups, thin provisioning |
| Jiva | Block | iSCSI | Legacy; use Mayastor instead |

### Mayastor (OpenEBS v3) — NVMe Performance

Mayastor uses SPDK (Storage Performance Development Kit) and NVMe-oF to deliver sub-millisecond latency and near-wire-speed throughput for Kubernetes volumes. It is purpose-built for performance-sensitive AI and database workloads: latency of 100-500 microseconds (vs. 1-5ms for traditional CSI), 1M+ IOPS (limited by NVMe hardware), near line-rate throughput on 100Gbps NICs, and SPDK poll-mode (dedicated cores) for zero-copy I/O.

```bash
# Install Mayastor
helm repo add openebs https://openebs.github.io/charts
helm install openebs openebs/openebs \
  --namespace openebs --create-namespace \
  --set mayastor.enabled=true \
  --set localprovisioner.enabled=true
```

Node requirements for Mayastor: `hugepages-2Mi: 2Gi` (SPDK requires huge pages) and dedicated CPU cores for SPDK reactor threads.

## NFS and Shared Filesystems

NFS (Network File System) provides ReadWriteMany (RWX) access — multiple Pods on multiple nodes mounting the same filesystem simultaneously. This is essential for shared datasets in AI training, shared configuration, and legacy applications requiring shared filesystem semantics.

### NFS-based StorageClass with nfs-subdir-external-provisioner

```bash
# Install NFS provisioner
helm repo add nfs-subdir-external-provisioner https://kubernetes-sigs.github.io/nfs-subdir-external-provisioner/
helm install nfs-provisioner \
  nfs-subdir-external-provisioner/nfs-subdir-external-provisioner \
  --set nfs.server=nfs.internal.corp \
  --set nfs.path=/shared/k8s-volumes \
  --set storageClass.name=nfs-shared \
  --set storageClass.reclaimPolicy=Retain
```

```yaml
# PVC using NFS
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: shared-dataset
spec:
  accessModes: [ReadWriteMany]
  storageClassName: nfs-shared
  resources:
    requests:
      storage: 10Ti
```

The same PVC can be mounted in multiple Pods simultaneously — for example, training workers reading a dataset concurrently while a preprocessing job writes new data.

### High-Performance Parallel Filesystems for AI

| Filesystem | Protocol | Peak Throughput | Latency | K8s Integration |
|---|---|---|---|---|
| Lustre | Custom | TB/s aggregate | Low ms | Lustre CSI (Trident, Weka) |
| GPFS/IBM Spectrum Scale | NFS/GPFS | 500GB/s+ | Sub-ms | Spectrum Scale CSI |
| WekaFS | WekaFS+NFS | Up to 100GB/s per client | Sub-ms | Weka CSI |
| BeeGFS | BeeGFS | High; scales linearly | Low ms | BeeGFS CSI (ThinkParQ) |
| Quobyte | Quobyte protocol | High | Low ms | Quobyte CSI |

## Related

- [K8s Handbook Part 7: Storage (Part 2)](parts/40-k8s-handbook-part7-storage-part2.md) — performance optimisation, AI artifact/model/vector-DB storage, backup and disaster recovery, observability, anti-patterns, and exercises
