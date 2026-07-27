---
title: "K8s Handbook Part 4 (Part 2: Controller Manager, Cloud Controller Manager & kubelet)"
doc_type: guide
domain: platforms
status: current
topic_id: k8s-handbook-part4-kubernetes-internals-part2
last_reviewed: 2026-07-27
maturity: practitioner
supersedes: []
tags:
  - kubernetes
  - controller-manager
  - cloud-controller-manager
  - kubelet
covers_version: "2025-2026 edition"
---

*Part 2 of 4 of [K8s Handbook Part 4: Kubernetes Internals](../37-k8s-handbook-part4-kubernetes-internals.md).*

## Chapter 5: Controller Manager — Reconciliation Engines

The Controller Manager (`kube-controller-manager`) is a single binary that runs dozens of independent controllers, each responsible for reconciling one or more resource types. Each controller is a control loop that continuously watches for differences between desired state and actual state, and takes action to eliminate those differences.

### The Reconciliation Loop Pattern

Every Kubernetes controller implements this pattern:

```go
func (c *Controller) reconcile(key string) error {
    // 1. Get desired state from cache (Lister -- no API call)
    desired, err := c.lister.Get(key)
    if err != nil {
        return err
    }
    // 2. Get actual state from the system
    actual, err := c.getActualState(desired)
    // 3. Compute diff
    diff := computeDiff(desired, actual)
    // 4. Apply changes to drive actual -> desired
    return c.applyChanges(diff)
}
```

The loop runs continuously:
- Triggered by watch events (`ADDED`, `MODIFIED`, `DELETED`)
- Re-queued on failure with exponential backoff
- Periodically re-synced (resync period) for safety
- Level-triggered: processes CURRENT state, not event deltas — missed events don't cause divergence
- Controller restart = re-read all state = fully recovered

### Core Controllers and Their Functions

| Controller | Watches | Manages | Reconciliation Action |
| --- | --- | --- | --- |
| Deployment | Deployments | ReplicaSets | Create/update/delete RS to match `Deployment.spec` |
| ReplicaSet | ReplicaSets, Pods | Pods | Create/delete Pods to match `RS.spec.replicas` |
| StatefulSet | StatefulSets | Pods, PVCs | Manage ordered Pod creation/deletion + PVC binding |
| DaemonSet | DaemonSets, Nodes | Pods | Ensure one Pod per node matching `nodeSelector` |
| Job | Jobs, Pods | Pods | Create Pods; track completions; retry failures |
| CronJob | CronJobs | Jobs | Create Jobs on schedule; manage history |
| HPA | HPAs, Pods, Metrics | Deployment/RS replicas | Scale replicas based on metrics |
| Node | Nodes | Node status, taints | Manage node lifecycle, evict pods from failed nodes |
| Namespace | Namespaces | Resources in namespace | Cascade delete on namespace deletion |
| ServiceAccount | ServiceAccounts | Secrets (token) | Create default service account token |
| EndpointSlice | Services, Pods | EndpointSlices | Track ready Pod IPs for each Service |
| GarbageCollection | All resources | Owned resources | Delete resources when owner is deleted |
| TTLAfterFinished | Jobs | Jobs | Delete completed Jobs after TTL |

### Deployment Controller — Rollout Strategy Deep Dive

The Deployment controller implements rolling updates through ReplicaSet management. Understanding this mechanism explains rollout behaviour and debugging approaches.

**Rolling update internals** — before update: `Deployment → RS-v1 (replicas=3)`. Update triggered (new image):

1. Deployment controller creates RS-v2 (replicas=0)
2. Scale RS-v2 up by 1 (`maxSurge=1`): RS-v1=3, RS-v2=1 (total=4, max allowed with `maxSurge=1`)
3. Wait for the RS-v2 Pod to become Ready
4. Scale RS-v1 down by 1 (`maxUnavailable=0`): RS-v1=2, RS-v2=1
5. Repeat until RS-v2=3, RS-v1=0
6. RS-v1 retained (for rollback) but with 0 replicas

```yaml
# Key parameters:
strategy:
  type: RollingUpdate
  rollingUpdate:
    maxSurge: 1         # max pods above desired during update
    maxUnavailable: 0   # max pods below desired during update
# maxUnavailable: 0 = zero-downtime rolling update
# maxSurge: 0 = update in-place (one down, then one up)
```

```bash
# Monitor rollout:
kubectl rollout status deployment/myapp
kubectl rollout history deployment/myapp
kubectl rollout undo deployment/myapp   # rolls back to previous RS
```

## Chapter 6: Cloud Controller Manager

The Cloud Controller Manager (CCM) was introduced to separate cloud-provider-specific logic from the core Kubernetes codebase. It runs cloud-specific controllers that integrate Kubernetes resources with cloud provider APIs.

### CCM Controllers

| Controller | Cloud Resource | Kubernetes Trigger |
| --- | --- | --- |
| Node controller | VM lifecycle (create/delete) | Node registers; cloud VM deleted → Node condition |
| Route controller | VPC routing table entries | Pod CIDR assigned to node → add route entry |
| Service controller | Cloud Load Balancer | Service type: LoadBalancer → provision LB + assign IP |
| Volume controller | Cloud storage volumes | PersistentVolume creation/deletion via CSI |

**LoadBalancer Service — CCM in action.** When you create a Service of type `LoadBalancer`, the CCM's service controller:

1. Detects the new Service (`type: LoadBalancer`) via watch
2. Calls the cloud provider API to provision a load balancer (AWS: ELB/NLB; GCP: Cloud Load Balancer; Azure: Azure Load Balancer)
3. Configures health checks pointing to the NodePort of the Service
4. Waits for the LB to become active (IP allocated)
5. Updates `Service.status.loadBalancer.ingress` with the IP/hostname

```yaml
apiVersion: v1
kind: Service
metadata:
  name: my-api
  annotations:
    service.beta.kubernetes.io/aws-load-balancer-type: external
    service.beta.kubernetes.io/aws-load-balancer-nlb-target-type: ip
spec:
  type: LoadBalancer
  selector: { app: my-api }
  ports:
    - port: 443
      targetPort: 8443
```

## Chapter 7: The kubelet — Node Agent

The kubelet is the primary node agent. It runs on every worker node (and control plane nodes) and is responsible for: registering the node with the API server, watching for Pods assigned to its node, managing the container runtime to run those Pods, managing volumes, reporting node and Pod status, and executing health checks.

### kubelet Responsibilities

**Node management:**
- Register the node with the API server (`POST /api/v1/nodes`)
- Report node capacity (CPU, memory, GPU, storage)
- Update node conditions (Ready, MemoryPressure, DiskPressure, PIDPressure)
- Report node heartbeat (every 10s via a Lease object)

**Pod lifecycle:**
- Watch the API server for Pods bound to this node
- Call CRI to create the Pod sandbox (network namespace via the pause container)
- Pull images via the CRI ImageService
- Create containers via the CRI RuntimeService
- Mount volumes (call the CSI driver for persistent volumes)
- Inject environment variables, ConfigMaps, Secrets
- Execute init containers in order, then app containers

**Health monitoring:**
- Execute liveness probes (HTTP, TCP, exec, gRPC)
- Execute readiness probes → update EndpointSlices
- Execute startup probes → delay liveness until started
- Restart containers on probe failure

**Status reporting:**
- Update `Pod.status` (phase, conditions, containerStatuses)
- Report container exit codes and restart counts
- Stream container logs to `/var/log/pods/`

### kubelet Static Pods

Static Pods are managed directly by the kubelet, not the API server. The kubelet watches a directory on the node filesystem and creates Pods for any manifest files found there. This is how control plane components (API server, etcd, controller manager, scheduler) run on control plane nodes in kubeadm-bootstrapped clusters:

```bash
# Static Pod manifest directory (configured in kubelet config):
ls /etc/kubernetes/manifests/
#   kube-apiserver.yaml
#   kube-controller-manager.yaml
#   kube-scheduler.yaml
#   etcd.yaml
# kubelet watches this directory; changes take effect immediately
# Static Pods appear in `kubectl get pods -n kube-system`
# but cannot be deleted via kubectl (kubelet recreates them)
```

```yaml
# kubelet configuration file: /var/lib/kubelet/config.yaml
# Key settings:
staticPodPath: /etc/kubernetes/manifests
cgroupDriver: systemd   # must match container runtime
clusterDNS: [10.96.0.10]   # CoreDNS Service IP
clusterDomain: cluster.local
evictionHard:
  memory.available: 200Mi   # Evict pods when node memory < 200Mi
  nodefs.available: 10%     # Evict when node disk < 10%
  nodefs.inodesFree: 5%
```

### Pod Lifecycle Phases and Conditions

| Phase | Meaning | Common Causes |
| --- | --- | --- |
| Pending | Pod accepted but not yet running | Scheduler finding node; image pulling; volume binding |
| Running | At least one container running | Normal operation |
| Succeeded | All containers exited with code 0 | Job/batch completion |
| Failed | All containers terminated, at least one non-zero | Crash, OOM kill, exec failure |
| Unknown | Pod state cannot be determined | Node communication failure; node unreachable |

## Related

- [Part 1: Architecture Overview, API Server, etcd & Scheduler](../37-k8s-handbook-part4-kubernetes-internals.md)
- [Part 3: kube-proxy, CoreDNS, Admission Controllers, CRDs & Operators](37-k8s-handbook-part4-kubernetes-internals-part3.md)
- [Part 4: Leader Election, API Request Lifecycle & Troubleshooting](37-k8s-handbook-part4-kubernetes-internals-part4.md)
