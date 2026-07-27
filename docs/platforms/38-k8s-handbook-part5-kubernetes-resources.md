---
title: "K8s Handbook Part 5: Kubernetes Resources"
doc_type: guide
domain: platforms
status: current
topic_id: k8s-handbook-part5-kubernetes-resources
last_reviewed: 2026-07-27
maturity: practitioner
supersedes:
  - docs/cloud-platforms/kubernetes/K8s_Handbook_Part5_Kubernetes_Resources.md
tags:
  - kubernetes
  - pods
  - workloads
  - services
  - storage
covers_version: "2025-2026 edition"
---

# K8s Handbook Part 5: Kubernetes Resources

*Part 1 of 2.* Prerequisites: [Parts 1](34-k8s-handbook-part1-infrastructure-evolution.md)–[4](37-k8s-handbook-part4-kubernetes-internals.md). Every core Kubernetes resource type — Pods, Deployments, StatefulSets, DaemonSets, Jobs, Services, Ingress, Gateway API, ConfigMaps, Secrets, and PersistentVolumes — with full YAML examples, internal implementation details, and production best practices.

## Chapter 1: Resource Taxonomy and API Conventions

Every Kubernetes resource follows a consistent structure and set of conventions. Mastering these conventions allows you to work with any resource — built-in or custom — without memorising each one individually.

### Universal Resource Structure

```yaml
# Every Kubernetes resource has this structure:
apiVersion: GROUP/VERSION    # e.g. apps/v1, v1, batch/v1
kind: RESOURCE_KIND          # e.g. Deployment, Pod, Service
metadata:
  name: my-resource          # unique within namespace
  namespace: default         # omit for cluster-scoped resources
  labels:                    # key-value pairs for selection
    app: myapp
    version: v1
  annotations:               # non-identifying metadata
    deployment.kubernetes.io/revision: '3'
  ownerReferences:           # garbage collection parent
    - apiVersion: apps/v1
      kind: Deployment
      name: myapp
      uid: abc123
      controller: true
  finalizers:                # prevent deletion until cleanup
    - kubernetes.io/pvc-protection
  resourceVersion: '12345'   # optimistic concurrency token
  uid: abc-def-123           # immutable unique identifier
spec:      # DESIRED state (user-controlled)
  ...
status:    # ACTUAL state (system-controlled)
  ...
```

### Resource Scope and Taxonomy

| Category | Resources | Scope | Primary Purpose |
| --- | --- | --- | --- |
| Workload | Pod, Deployment, StatefulSet, DaemonSet, ReplicaSet | Namespaced | Run containerised workloads |
| Batch | Job, CronJob | Namespaced | Run finite or scheduled tasks |
| Networking | Service, Endpoints, EndpointSlice, Ingress, NetworkPolicy | Namespaced | Expose and control traffic |
| Gateway | Gateway, HTTPRoute, GRPCRoute, TCPRoute | Namespaced | Next-gen ingress/routing |
| Config | ConfigMap, Secret | Namespaced | Inject configuration and secrets |
| Storage | PersistentVolume, StorageClass | Cluster | Persistent storage abstraction |
| Storage | PersistentVolumeClaim | Namespaced | Claim storage for a workload |
| Identity | ServiceAccount, Secret (token) | Namespaced | Workload identity and auth |
| RBAC | Role, RoleBinding | Namespaced | Namespace-scoped access control |
| RBAC | ClusterRole, ClusterRoleBinding | Cluster | Cluster-wide access control |
| Policy | LimitRange, ResourceQuota | Namespaced | Resource governance per namespace |
| Policy | PodDisruptionBudget | Namespaced | Availability during disruptions |
| Autoscaling | HPA, VPA | Namespaced | Automatic resource scaling |
| Scheduling | PriorityClass | Cluster | Pod preemption priority |
| Runtime | RuntimeClass | Cluster | Container runtime selection |
| Nodes | Node, CSINode | Cluster | Worker node representation |
| Cluster | Namespace, PersistentVolume | Cluster | Cluster-wide organisation |

## Chapter 2: Pods — The Atomic Unit

A Pod is the smallest deployable unit in Kubernetes. It represents one or more containers that share a network namespace (same IP address and port space), IPC namespace, and optionally a PID namespace. Containers in a Pod are always co-located, co-scheduled, and share storage volumes.

### Illustrative Pod Specification

The example below ties together requests/limits and all three probe types discussed in this chapter:

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: api-server
  labels: { app: api-server }
spec:
  containers:
    - name: api
      image: harbor.corp/api@sha256:abc
      resources:
        requests: { cpu: 250m, memory: 256Mi }
        limits: { memory: 512Mi }
      startupProbe:
        httpGet: { path: /healthz, port: 8080 }
        failureThreshold: 30
        periodSeconds: 2
      livenessProbe:
        httpGet: { path: /healthz, port: 8080 }
        periodSeconds: 10
      readinessProbe:
        httpGet: { path: /readyz, port: 8080 }
        periodSeconds: 5
```

### Pod Health Probe Decision Guide

| Probe | Triggers On Failure | When to Use | Recommended Check |
| --- | --- | --- | --- |
| `startupProbe` | Nothing (waits for success) | Slow-starting apps (JVM, large models) | Same endpoint as liveness; high `failureThreshold` |
| `livenessProbe` | Container restart | Detect deadlocks, hung processes | Lightweight internal health check; never external deps |
| `readinessProbe` | Remove from Service endpoints | Temporary unreadiness (DB reconnect, warmup) | Include dependency checks (DB, cache reachable) |

### Multi-Container Pod Patterns

- **Sidecar**: a helper container augmenting the main container: log shipper, metrics exporter, secret refresher, Istio Envoy proxy. Shares the Pod's lifetime.
- **Init Container**: runs before app containers to perform setup: wait for dependencies, populate a shared volume, run database migrations. Runs once to completion.
- **Sidecar (native, K8s 1.29+)**: a native sidecar type — an init container with `restartPolicy: Always`. Starts before app containers, stops after them. Solves the ordering issue with Istio Envoy and log shippers.
- **Ephemeral Container**: a debug container added to a running Pod without restart (`kubectl debug` in-cluster). Does not persist; cannot use volumes.
- **Ambassador**: a proxy container that simplifies external service access. The app connects to localhost; the ambassador handles service discovery and auth.

## Chapter 3: Workload Resources: Deployment, StatefulSet, DaemonSet

### Deployment — Stateless Workloads

Deployments manage stateless application replicas. They provide rolling updates, rollback capability, and scaling. Under the hood, a Deployment manages ReplicaSets which manage Pods.

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: api-server
  namespace: production
spec:
  replicas: 3
  revisionHistoryLimit: 5           # Keep 5 old ReplicaSets for rollback
  progressDeadlineSeconds: 600      # Fail rollout if not complete in 10min
  selector:
    matchLabels: { app: api-server }
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1          # +1 Pod above replicas during update
      maxUnavailable: 0    # Zero-downtime: no Pods removed until new ready
  template:
    metadata:
      labels: { app: api-server, version: v1.2.3 }
    spec:
      # Anti-affinity: spread Pods across nodes
      affinity:
        podAntiAffinity:
          preferredDuringSchedulingIgnoredDuringExecution:
            - weight: 100
              podAffinityTerm:
                labelSelector:
                  matchLabels: { app: api-server }
                topologyKey: kubernetes.io/hostname
      containers:
        - name: api
          image: harbor.corp/api@sha256:abc
          resources:
            requests: { cpu: 500m, memory: 512Mi }
            limits: { memory: 1Gi }
```

### StatefulSet — Stateful Workloads

StatefulSets manage stateful applications that require stable network identities, stable persistent storage, and ordered deployment/scaling. The canonical use cases are databases, message queues, and distributed caches.

**StatefulSet guarantees vs. Deployment:**

| Property | Deployment | StatefulSet |
| --- | --- | --- |
| Pod naming | Random suffix (`api-7d9f8-abc12`) | Ordinal index (`postgres-0`, `postgres-1`) |
| DNS | Shared Service ClusterIP | Per-Pod DNS: `pod-0.headless-svc.ns.svc.cluster.local` |
| Storage | Shared or no PVC per pod | Dedicated PVC per Pod (`volumeClaimTemplates`) |
| Startup order | Parallel (all at once) | Sequential (0 then 1 then 2) |
| Shutdown order | Random/parallel | Reverse ordinal (2 then 1 then 0) |
| Pod identity | Ephemeral (any Pod is equivalent) | Sticky (`postgres-0` always `postgres-0`) |
| Rolling update | All Pods updated with surge | Reverse ordinal (highest first) |
| Use cases | Web servers, APIs, stateless workers | Databases, Kafka, Elasticsearch, etcd |

```yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: postgres
spec:
  serviceName: postgres-headless   # REQUIRED: headless Service for DNS
  replicas: 3
  selector:
    matchLabels: { app: postgres }
  updateStrategy:
    type: RollingUpdate
    rollingUpdate:
      partition: 0   # Update all pods (set to N to protect first N pods)
  template:
    metadata:
      labels: { app: postgres }
    spec:
      containers:
        - name: postgres
          image: postgres:16-alpine
          env:
            - name: POD_NAME
              valueFrom: { fieldRef: { fieldPath: metadata.name } }
            - name: POSTGRES_PASSWORD
              valueFrom: { secretKeyRef: { name: pg-secret, key: password } }
          volumeMounts:
            - name: data
              mountPath: /var/lib/postgresql/data
          resources:
            requests: { cpu: 1, memory: 2Gi }
            limits: { memory: 4Gi }
  # Dedicated PVC per Pod -- created automatically, never deleted on scale-down
  volumeClaimTemplates:
    - metadata:
        name: data
      spec:
        accessModes: [ReadWriteOnce]
        storageClassName: fast-ssd
        resources:
          requests: { storage: 100Gi }
```

### DaemonSet — Node-Level Workloads

DaemonSets ensure exactly one Pod runs on every node (or every node matching a selector). DaemonSets are used for node-level infrastructure: log collection, monitoring agents, network plugins, storage drivers, security agents.

| Use Case | Example DaemonSet | Notes |
| --- | --- | --- |
| Log collection | Fluent Bit, Fluentd | One per node to collect `/var/log/pods/` |
| Metrics collection | node_exporter, DCGM GPU exporter | Node hardware/OS metrics |
| Networking | Cilium, Calico, Flannel agents | CNI plugin node agent |
| Storage | CSI node driver (EBS, Ceph RBD) | Volume attach/mount on node |
| Security | Falco, Tetragon | Kernel-level eBPF probes |
| GPU management | NVIDIA device plugin | Expose GPU resources to scheduler |
| Cluster DNS | CoreDNS (can also run as Deployment) | Per-node DNS caching |

## Chapter 4: Batch Resources: Jobs and CronJobs

### Jobs — Run-to-Completion Workloads

A Job creates one or more Pods that run to completion. Unlike Deployments (which keep Pods running), Jobs are designed for finite tasks: database migrations, batch data processing, ML training runs, report generation.

```yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: data-migration-v2
spec:
  completions: 1                  # Total successful completions required
  parallelism: 1                  # Pods running in parallel
  backoffLimit: 3                 # Retry failed pods up to 3 times
  activeDeadlineSeconds: 3600      # Kill job if running > 1 hour
  ttlSecondsAfterFinished: 86400   # Auto-delete 24h after completion
  template:
    spec:
      restartPolicy: OnFailure     # Never or OnFailure (not Always)
      containers:
        - name: migrator
          image: harbor.corp/migrator:v2
          command: ['python', 'migrate.py', '--version', 'v2']
          resources:
            requests: { cpu: 500m, memory: 1Gi }
# Parallel Job patterns:
#   Fixed completion count: completions=10, parallelism=3 (process 10 tasks, 3 at a time)
#   Work queue: completions=1, parallelism=5 (5 workers drain a queue)
#   Indexed Jobs (1.21+): completionMode: Indexed (each Pod gets JOB_COMPLETION_INDEX)
```

**AI/ML training Job pattern** (distributed PyTorch training):

```yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: llm-finetune-run-001
spec:
  completions: 8       # 8 workers total
  parallelism: 8        # All start simultaneously (gang scheduling)
  completionMode: Indexed
  template:
    spec:
      schedulerName: volcano   # Gang scheduler
      restartPolicy: OnFailure
      tolerations:
        - key: nvidia.com/gpu
          operator: Exists
          effect: NoSchedule
      containers:
        - name: trainer
          image: nvcr.io/nvidia/pytorch:24.05-py3
          command: [torchrun, --nproc_per_node=8, --nnodes=1, train.py]
          resources:
            limits: { nvidia.com/gpu: 8 }
            requests: { nvidia.com/gpu: 8, memory: 256Gi, cpu: 64 }
```

### CronJobs

CronJobs create Jobs on a schedule (cron syntax). Used for periodic tasks: database backups, report generation, cache warming, cleanup jobs.

```yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: database-backup
spec:
  schedule: '0 2 * * *'         # 02:00 UTC daily
  timeZone: 'UTC'                # Explicit timezone (K8s 1.27+)
  concurrencyPolicy: Forbid      # Skip if previous run still active
  successfulJobsHistoryLimit: 3
  failedJobsHistoryLimit: 1
  startingDeadlineSeconds: 300    # Skip if > 5min late to start
  jobTemplate:
    spec:
      ttlSecondsAfterFinished: 3600
      template:
        spec:
          restartPolicy: OnFailure
          containers:
            - name: backup
              image: harbor.corp/pg-backup:latest
              env:
                - name: BACKUP_DESTINATION
                  value: s3://backups/postgres/
              resources:
                requests: { cpu: 200m, memory: 256Mi }
```

## Chapter 5: Service and Endpoint Resources

Services provide stable network identities (IP addresses and DNS names) for groups of Pods. Without Services, Pods would need to track each other's ephemeral IPs directly — an impossible task at scale.

### Service Types Reference

```yaml
# ClusterIP (default) -- internal cluster communication:
apiVersion: v1
kind: Service
metadata:
  name: api-backend
spec:
  type: ClusterIP
  selector: { app: api-backend, version: v1 }
  ports:
    - name: http
      port: 80          # Port exposed by Service
      targetPort: 8080   # Port on Pod
      protocol: TCP
  sessionAffinity: None   # Or ClientIP for sticky sessions
---
# NodePort -- expose on each node's IP:
spec:
  type: NodePort
  ports:
    - port: 80
      targetPort: 8080
      nodePort: 30080   # Must be 30000-32767; omit for auto-assign
---
# LoadBalancer -- provision cloud LB:
spec:
  type: LoadBalancer
  loadBalancerSourceRanges:
    - 10.0.0.0/8         # Restrict LB to internal networks
  externalTrafficPolicy: Local   # Preserve client source IP
---
# Headless Service -- direct Pod DNS (for StatefulSets):
spec:
  clusterIP: None   # No virtual IP; DNS returns Pod IPs directly
  selector: { app: postgres }
---
# ExternalName -- DNS CNAME to external service:
spec:
  type: ExternalName
  externalName: legacy-api.internal.corp
```

### EndpointSlices — How Services Find Pods

EndpointSlices (replaced Endpoints in 1.21+) track the IP addresses and ports of Pods matching a Service's selector. kube-proxy watches EndpointSlices to update its routing rules. The EndpointSlice controller creates/updates them as Pods come and go:

```bash
# View EndpointSlices for a Service:
kubectl get endpointslices -l kubernetes.io/service-name=api-backend
```

```yaml
# Each EndpointSlice holds up to 100 endpoints (for scalability):
apiVersion: discovery.k8s.io/v1
kind: EndpointSlice
metadata:
  name: api-backend-abc
  labels:
    kubernetes.io/service-name: api-backend
addressType: IPv4
endpoints:
  - addresses: ['10.244.1.5']
    conditions: { ready: true, serving: true, terminating: false }
    targetRef: { kind: Pod, name: api-backend-xyz, namespace: default }
    hints:
      forZones: [{ name: us-east-1a }]   # Topology hints for zone-aware routing
ports:
  - name: http
    port: 8080
    protocol: TCP
```

## Chapter 6: Ingress and Gateway API

Ingress and Gateway API provide HTTP-level routing from external traffic into cluster Services. Ingress is the original API (stable since 1.19); Gateway API is the successor with richer routing semantics and role-based management.

### Ingress

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: api-ingress
  annotations:
    nginx.ingress.kubernetes.io/ssl-redirect: 'true'
    nginx.ingress.kubernetes.io/proxy-body-size: 100m
    nginx.ingress.kubernetes.io/rate-limit: '100'
    cert-manager.io/cluster-issuer: letsencrypt-prod
spec:
  ingressClassName: nginx
  tls:
    - hosts: [api.example.com]
      secretName: api-tls-cert
  rules:
    - host: api.example.com
      http:
        paths:
          - path: /v1
            pathType: Prefix
            backend:
              service: { name: api-v1, port: { number: 80 } }
          - path: /v2
            pathType: Prefix
            backend:
              service: { name: api-v2, port: { number: 80 } }
```

### Gateway API — The Ingress Successor

Gateway API (stable in 1.28) separates infrastructure (Gateway) from routing (HTTPRoute) and supports multi-tenancy through role separation. Different teams manage different parts of the routing configuration:

```yaml
# Infrastructure team manages the Gateway (allocates LB):
apiVersion: gateway.networking.k8s.io/v1
kind: Gateway
metadata:
  name: external-gateway
  namespace: ingress-system
spec:
  gatewayClassName: cilium   # or nginx, envoy, istio
  listeners:
    - name: https
      protocol: HTTPS
      port: 443
      tls:
        certificateRefs:
          - name: wildcard-tls
            namespace: ingress-system
      allowedRoutes:
        namespaces:
          from: Selector
          selector:
            matchLabels: { gateway-allowed: 'true' }
---
# Application team manages their own HTTPRoute:
apiVersion: gateway.networking.k8s.io/v1
kind: HTTPRoute
metadata:
  name: api-routes
  namespace: production
spec:
  parentRefs:
    - name: external-gateway
      namespace: ingress-system
  hostnames: ['api.example.com']
  rules:
    - matches:
        - path: { type: PathPrefix, value: /api }
          headers:
            - name: X-API-Version
              value: v2
      backendRefs:
        - name: api-v2
          port: 80
          weight: 90
        - name: api-v3-canary
          port: 80
          weight: 10
      filters:
        - type: RequestHeaderModifier
          requestHeaderModifier:
            add:
              - name: X-Forwarded-By
                value: gateway
```

## Chapter 7: Configuration: ConfigMaps and Secrets

### ConfigMaps — Externalised Non-Secret Configuration

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: app-config
  namespace: production
data:
  # Simple key-value pairs (used as env vars):
  LOG_LEVEL: info
  MAX_CONNECTIONS: '100'
  FEATURE_FLAGS: 'new-ui=true,beta-api=false'
  # File content (mounted as file in container):
  nginx.conf: |
    server {
      listen 8080;
      location / { proxy_pass http://backend; }
    }
  app.properties: |
    database.url=jdbc:postgresql://db:5432/mydb
    cache.ttl=300
```

```yaml
# Consume as env vars:
envFrom:
  - configMapRef: { name: app-config }
# Or selectively:
env:
  - name: LOG_LEVEL
    valueFrom:
      configMapKeyRef: { name: app-config, key: LOG_LEVEL }
# Mount as files:
volumes:
  - name: config
    configMap:
      name: app-config
      items:
        - key: nginx.conf
          path: nginx.conf
          mode: 0444
```

### Secrets — Sensitive Configuration

Kubernetes Secrets store sensitive data (passwords, TLS certs, API keys). Secrets are base64-encoded (NOT encrypted) by default — encryption at rest requires additional configuration or an external secrets manager.

> **Secret security warning:** Kubernetes Secrets are NOT encrypted by default — only base64-encoded. Anyone with RBAC access to read Secrets can decode them. Enable etcd encryption at rest (`EncryptionConfiguration`) and use External Secrets Operator with HashiCorp Vault, AWS Secrets Manager, or GCP Secret Manager for production secret management. Never commit Secrets to Git.

Secret types: `Opaque` (generic key-value, most common), `kubernetes.io/tls` (TLS certificate + private key), `kubernetes.io/dockerconfigjson` (registry pull secret), `kubernetes.io/service-account-token` (SA token, auto-created).

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: db-credentials
  namespace: production
type: Opaque
stringData:   # kubectl encodes to base64 automatically
  username: dbadmin
  password: my-secure-password
  connection-string: postgresql://dbadmin:my-secure-password@db:5432/mydb
---
# TLS Secret (for Ingress/Gateway TLS):
apiVersion: v1
kind: Secret
metadata:
  name: api-tls
type: kubernetes.io/tls
data:
  tls.crt: <base64-cert>
  tls.key: <base64-key>
```

**External Secrets Operator — production secret management:**

```yaml
apiVersion: external-secrets.io/v1beta1
kind: ExternalSecret
metadata:
  name: db-credentials
  namespace: production
spec:
  refreshInterval: 1h
  secretStoreRef:
    name: vault-backend
    kind: ClusterSecretStore
  target:
    name: db-credentials
    creationPolicy: Owner
    deletionPolicy: Delete
  data:
    - secretKey: password
      remoteRef:
        key: secret/production/database
        property: password
```

## Chapter 8: Storage: PV, PVC, StorageClass, CSI

Kubernetes abstracts storage through a three-layer model: StorageClass (defines storage capabilities), PersistentVolume (represents actual storage), and PersistentVolumeClaim (requests storage for a workload). CSI drivers implement the actual storage operations.

### Storage Architecture

**Dynamic provisioning flow:**

1. StorageClass defined (once, by storage admin): parameters, provisioner, reclaimPolicy, volumeBindingMode
2. PVC created (by developer): accessModes, `resources.requests.storage`, storageClassName
3. PVC controller detects the unbound PVC
4. CSI provisioner creates a volume in the backend (AWS EBS, GCS, Ceph)
5. PV created automatically, bound to the PVC
6. Pod created referencing the PVC
7. kubelet calls CSI `NodePublishVolume` on the scheduled node
8. Volume attached to the node (CSI `ControllerPublishVolume`)
9. Volume mounted into the Pod filesystem

```yaml
# StorageClass example (AWS EBS):
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: fast-ssd
  annotations:
    storageclass.kubernetes.io/is-default-class: 'true'
provisioner: ebs.csi.aws.com
parameters:
  type: gp3
  iops: '3000'
  throughput: '125'
  encrypted: 'true'
  kmsKeyId: arn:aws:kms:us-east-1:ACCOUNT:key/KEY-ID
reclaimPolicy: Delete   # Delete PV when PVC deleted (use Retain for prod)
volumeBindingMode: WaitForFirstConsumer   # Provision on node with Pod
allowVolumeExpansion: true
```

### Access Modes

| Mode | Abbreviation | Semantics | Typical Use |
| --- | --- | --- | --- |
| ReadWriteOnce | RWO | Read/write by one node at a time | Databases, single-instance apps |
| ReadOnlyMany | ROX | Read-only by many nodes | Shared config files, static assets |
| ReadWriteMany | RWX | Read/write by many nodes simultaneously | Shared ML datasets, NFS workloads |
| ReadWriteOncePod | RWOP | Read/write by exactly one Pod | Strongest guarantee; K8s 1.22+ |

### AI/ML Storage Patterns

- **Model artifacts**: large read-only model weights (10–700GB). Store in object storage (S3, GCS). Mount read-only via CSI or init container download. Consider a ReadOnlyMany PVC backed by NFS or a parallel filesystem for multi-replica serving.
- **Training datasets**: massive datasets (TB scale). Use ReadOnlyMany PVCs backed by parallel filesystems (Lustre, GPFS, WekaFS) for high-throughput sequential read. Or stream from object storage (S3) with a dataset caching layer.
- **Checkpoints**: write-heavy during training, read-heavy during restart. Use a ReadWriteOnce SSD PVC for low-latency checkpoint writes. Async copy to object storage for durability.
- **Vector databases**: high-performance read/write with specific IOPS requirements. Use gp3 EBS (AWS) or Premium SSD (Azure) with StorageClass IOPS tuning. Size for 2–3x index size for memory-mapped files.

## Chapter 9: Namespaces, ResourceQuota, LimitRange

Namespaces provide a virtual cluster within a physical cluster. They partition resources between teams, environments, or tenants. ResourceQuota and LimitRange provide the governance layer: controlling how much resource a namespace can consume and enforcing default resource specifications.

### Namespace Strategy

| Pattern | Namespaces | Isolation | Use Case |
| --- | --- | --- | --- |
| Per environment | dev, staging, production | Low (same cluster) | Small teams, simple workloads |
| Per team | team-a, team-b, shared | Medium | Multi-team platform |
| Per application | myapp-dev, myapp-prod | Medium | Application-centric teams |
| Per tenant | tenant-acme, tenant-globex | Medium-High | SaaS multi-tenancy |
| Per cluster | (all in one namespace) | Highest | Dedicated cluster per env/tenant |

### ResourceQuota — Namespace Resource Limits

```yaml
apiVersion: v1
kind: ResourceQuota
metadata:
  name: production-quota
  namespace: production
spec:
  hard:
    # Compute:
    requests.cpu: '20'        # Total CPU requests across all Pods
    limits.cpu: '40'
    requests.memory: 40Gi
    limits.memory: 80Gi
    # GPU (requires device plugin):
    requests.nvidia.com/gpu: '8'
    # Storage:
    requests.storage: 500Gi
    persistentvolumeclaims: '20'
    # Object counts:
    pods: '50'
    services: '20'
    services.loadbalancers: '2'
    configmaps: '30'
    secrets: '30'
```

```bash
# Check quota usage:
kubectl describe resourcequota -n production
```

### LimitRange — Per-Pod Defaults and Constraints

```yaml
apiVersion: v1
kind: LimitRange
metadata:
  name: default-limits
  namespace: production
spec:
  limits:
    - type: Container
      # Defaults applied when not specified:
      defaultRequest: { cpu: 100m, memory: 128Mi }
      default: { cpu: 500m, memory: 256Mi }
      # Allowed ranges:
      min: { cpu: 50m, memory: 64Mi }
      max: { cpu: '4', memory: 8Gi }
    - type: PersistentVolumeClaim
      min: { storage: 1Gi }
      max: { storage: 100Gi }
```

## Related

- [Part 2: RBAC, NetworkPolicies, Autoscaling, Scheduling & Anti-Patterns](parts/38-k8s-handbook-part5-kubernetes-resources-part2.md)
