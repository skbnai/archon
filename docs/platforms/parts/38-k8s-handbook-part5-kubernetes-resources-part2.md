---
title: "K8s Handbook Part 5: Kubernetes Resources (Part 2)"
doc_type: guide
domain: platforms
status: current
topic_id: k8s-handbook-part5-kubernetes-resources-part2
last_reviewed: 2026-07-27
maturity: practitioner
supersedes: []
tags: [kubernetes, rbac, networking, autoscaling, scheduling]
covers_version: "2025-2026 edition"
---

> Continues from [K8s Handbook Part 5: Kubernetes Resources](../38-k8s-handbook-part5-kubernetes-resources.md), covering Chapters 10-17: identity and access, network policies, autoscaling, scheduling, reliability, runtime/policy, resource anti-patterns, and hands-on exercises.

## Identity and Access: ServiceAccounts and RBAC

RBAC (Role-Based Access Control) is the primary authorisation mechanism in Kubernetes. It controls which identities (users, groups, service accounts) can perform which operations on which resources. ServiceAccounts provide identity for Pods.

### RBAC Model

RBAC primitives:

- **Role** — namespaced permissions
- **ClusterRole** — cluster-wide permissions (or shared across namespaces)
- **RoleBinding** — binds a Role or ClusterRole to subjects (namespaced)
- **ClusterRoleBinding** — binds a ClusterRole to subjects (cluster-wide)
- **Subject** — User | Group | ServiceAccount

```yaml
# Allow a ServiceAccount to read Pods in its namespace
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: pod-reader
  namespace: production
rules:
  - apiGroups: ['']
    resources: [pods, pods/log]
    verbs: [get, list, watch]
---
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: pod-reader-binding
  namespace: production
subjects:
  - kind: ServiceAccount
    name: monitoring-agent
    namespace: production
roleRef:
  kind: Role
  name: pod-reader
  apiGroup: rbac.authorization.k8s.io
```

### ServiceAccount Workload Identity

```yaml
# Minimal ServiceAccount for an application
apiVersion: v1
kind: ServiceAccount
metadata:
  name: myapp-sa
  namespace: production
  annotations:
    # Workload Identity (GKE) -- bind to GCP service account
    iam.gke.io/gcp-service-account: myapp@project.iam.gserviceaccount.com
    # IRSA (EKS) -- bind to AWS IAM role
    eks.amazonaws.com/role-arn: arn:aws:iam::ACCOUNT:role/MyAppRole
automountServiceAccountToken: false  # Opt-in, not opt-out
---
# Pod using the ServiceAccount
spec:
  serviceAccountName: myapp-sa
  automountServiceAccountToken: true  # Explicit opt-in for this pod
```

RBAC best practices:

1. Principle of least privilege: grant the minimum required verbs.
2. Never use `cluster-admin` for application service accounts.
3. Use a separate ServiceAccount per application.
4. Audit with `kubectl auth can-i --as=system:serviceaccount:ns:sa`.
5. Use Workload Identity (GKE) / IRSA (EKS) instead of mounting cloud credentials.

## Network Policies

NetworkPolicies are the Kubernetes firewall. They define which Pods can communicate with which other Pods and external endpoints. By default, all Pod-to-Pod communication is allowed (no NetworkPolicies = no restrictions). Applying a NetworkPolicy to a Pod makes that Pod's traffic subject to the policy's rules.

### Default Deny — Zero Trust Starting Point

```yaml
# Apply to a namespace to block all traffic by default,
# then add explicit allow rules for required communication
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: default-deny-all
  namespace: production
spec:
  podSelector: {}  # Selects ALL pods in namespace
  policyTypes:
    - Ingress
    - Egress
  # No ingress/egress rules = deny all
```

### Microservices Network Policy Pattern

```yaml
# Allow frontend to reach backend only
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: backend-ingress
  namespace: production
spec:
  podSelector:
    matchLabels: { tier: backend }
  policyTypes: [Ingress]
  ingress:
    - from:
        - podSelector:
            matchLabels: { tier: frontend }
        - namespaceSelector:
            matchLabels: { team: monitoring }
      ports:
        - protocol: TCP
          port: 8080
---
# Allow egress to DNS and external API only
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: backend-egress
  namespace: production
spec:
  podSelector:
    matchLabels: { tier: backend }
  policyTypes: [Egress]
  egress:
    - to:
        - namespaceSelector:
            matchLabels: { kubernetes.io/metadata.name: kube-system }
          podSelector:
            matchLabels: { k8s-app: kube-dns }
      ports: [{ port: 53, protocol: UDP }]
    - to:
        - ipBlock:
            cidr: 10.0.0.0/8  # Internal services only
      ports: [{ port: 443, protocol: TCP }]
```

## Autoscaling: HPA, VPA, KEDA, Cluster Autoscaler

### Autoscaling Layers

| Scaler | Dimension | Trigger | Response Time |
|---|---|---|---|
| HPA (Horizontal Pod Autoscaler) | Pod count | CPU, memory, custom/external metrics | 30-60 seconds |
| VPA (Vertical Pod Autoscaler) | Pod CPU/memory requests | Historical resource usage | Hours (requires restart) |
| KEDA | Pod count | Event sources (Kafka lag, SQS depth, Redis, Prometheus) | 10-30 seconds |
| Cluster Autoscaler | Node count | Unschedulable pods; underutilised nodes | 1-5 minutes |
| Karpenter | Node count + type | Unschedulable pods (intelligent bin-packing) | 30-90 seconds |

### HPA — Horizontal Pod Autoscaler

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: api-hpa
  namespace: production
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: api-server
  minReplicas: 3
  maxReplicas: 50
  metrics:
    - type: Resource
      resource:
        name: cpu
        target: { type: Utilization, averageUtilization: 70 }  # Scale when avg CPU > 70% of request
    - type: Resource
      resource:
        name: memory
        target: { type: AverageValue, averageValue: 400Mi }
    - type: Pods
      pods:
        metric: { name: http_requests_per_second }
        target: { type: AverageValue, averageValue: '1000' }
  behavior:
    scaleDown:
      stabilizationWindowSeconds: 300  # Wait 5min before scaling down
      policies:
        - type: Percent
          value: 10
          periodSeconds: 60  # Remove at most 10% of replicas per minute
    scaleUp:
      stabilizationWindowSeconds: 0  # Scale up immediately
      policies:
        - type: Percent
          value: 100
          periodSeconds: 15  # Can double every 15 seconds
```

### KEDA — Event-Driven Autoscaling for AI Workloads

KEDA (Kubernetes Event-Driven Autoscaling) is essential for AI inference serving: scale to zero when there are no requests, then scale up based on queue depth or request rate.

```yaml
# Scale LLM inference deployment based on request queue depth
apiVersion: keda.sh/v1alpha1
kind: ScaledObject
metadata:
  name: llm-inference-scaler
  namespace: ai-serving
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: llm-inference
  minReplicaCount: 0  # Scale to zero when idle
  maxReplicaCount: 10
  cooldownPeriod: 300  # Wait 5min before scaling to zero
  triggers:
    - type: prometheus
      metadata:
        serverAddress: http://prometheus:9090
        metricName: inference_queue_depth
        query: sum(inference_requests_pending)
        threshold: '5'  # Scale up when > 5 queued requests per replica
    - type: rabbitmq
      metadata:
        protocol: amqp
        queueName: inference-requests
        mode: QueueLength
        value: '10'
```

## Scheduling: PriorityClass, Affinity, TopologySpread

### PriorityClass — Workload Preemption

PriorityClasses define the scheduling priority of Pods. Higher-priority Pods can preempt (evict) lower-priority Pods when cluster resources are scarce. This is critical for AI platforms where inference serving (revenue-generating) must preempt batch training jobs.

```yaml
# Define priority tiers
apiVersion: scheduling.k8s.io/v1
kind: PriorityClass
metadata:
  name: critical-production
value: 1000000
globalDefault: false
preemptionPolicy: PreemptLowerPriority
description: 'Customer-facing production services'
---
apiVersion: scheduling.k8s.io/v1
kind: PriorityClass
metadata:
  name: ai-inference-serving
value: 900000
description: 'LLM inference endpoints'
---
apiVersion: scheduling.k8s.io/v1
kind: PriorityClass
metadata:
  name: ai-training-batch
value: 100000
preemptionPolicy: Never  # Batch training: never preempts others
description: 'ML training jobs -- preemptable'
---
# Assign to Pod
spec:
  priorityClassName: ai-inference-serving
```

### TopologySpread Constraints — Zone-Aware Spreading

TopologySpreadConstraints distribute Pods evenly across topology domains (availability zones, nodes) for high availability:

```yaml
spec:
  topologySpreadConstraints:
    # Spread evenly across availability zones
    - maxSkew: 1
      topologyKey: topology.kubernetes.io/zone
      whenUnsatisfiable: DoNotSchedule
      labelSelector:
        matchLabels: { app: api-server }
    # Also spread evenly across nodes (best-effort)
    - maxSkew: 1
      topologyKey: kubernetes.io/hostname
      whenUnsatisfiable: ScheduleAnyway
      labelSelector:
        matchLabels: { app: api-server }
```

`maxSkew` is the max difference in Pod count between any two topology domains. `whenUnsatisfiable: DoNotSchedule` is a hard requirement; `whenUnsatisfiable: ScheduleAnyway` is a soft preference.

## Reliability: PodDisruptionBudgets

PodDisruptionBudgets (PDBs) protect applications from being disrupted by voluntary disruptions: node drain, cluster upgrades, Cluster Autoscaler scale-down. They guarantee a minimum number of Pods remain available during disruptions.

```yaml
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: api-server-pdb
  namespace: production
spec:
  # Option A: minimum available
  minAvailable: 2  # At least 2 Pods always available during disruption
  # Option B: maximum unavailable
  # maxUnavailable: 1  # At most 1 Pod unavailable at any time
  # Option C: percentage
  # minAvailable: 75%  # At least 75% of Pods available
  selector:
    matchLabels: { app: api-server }
```

PDB interaction with node drain: `kubectl drain node-01 --ignore-daemonsets` honours the PDB and evicts Pods only when the PDB allows. If the PDB blocks eviction, the drain waits (or fails with a timeout). Critically, a PDB only protects against **voluntary** disruptions — node failure (hardware) bypasses it. Best practice: always create a PDB for production Deployments with `replicas > 1`; without one, all Pods can be evicted simultaneously.

### PDB Anti-Patterns

- **`minAvailable: 100%` or `maxUnavailable: 0`** — if the PDB requires ALL Pods available, node drains and upgrades block permanently.
- **PDB with single-replica Deployment** — `minAvailable: 1` + `replicas: 1` means cluster upgrades are blocked forever.
- **No PDB for stateful services** — without a PDB, all PostgreSQL replicas can be evicted simultaneously during an upgrade, causing data unavailability.

## Runtime and Policy: RuntimeClass, PodSecurity

### RuntimeClass

```yaml
apiVersion: node.k8s.io/v1
kind: RuntimeClass
metadata:
  name: kata-qemu
handler: kata-qemu
overhead:
  podFixed:
    memory: 120Mi  # VM overhead added to all resource calculations
    cpu: 250m
scheduling:
  tolerations:
    - key: kata-containers
      operator: Exists
      effect: NoSchedule
---
# Use in Pod
spec:
  runtimeClassName: kata-qemu
```

### Pod Security Standards

| Policy | Restrictions | Use Case |
|---|---|---|
| Privileged | No restrictions | Trusted system workloads: CNI, CSI, GPU operator |
| Baseline | Block known privilege escalations; restrict hostNetwork/hostPID | General workloads |
| Restricted | Strict: requires non-root, no privilege escalation, seccomp, dropped caps | Security-critical; PCI, HIPAA |

```yaml
# Enforce Pod Security Standards at namespace level
apiVersion: v1
kind: Namespace
metadata:
  name: production
  labels:
    pod-security.kubernetes.io/enforce: restricted
    pod-security.kubernetes.io/enforce-version: v1.30
    pod-security.kubernetes.io/warn: restricted
    pod-security.kubernetes.io/audit: restricted
```

## Resource Anti-Patterns Reference

| Anti-Pattern | Problem | Solution |
|---|---|---|
| No resource requests or limits | Pods consume unbounded resources, causing noisy-neighbour effects and unpredictable OOM kills on nodes | Set requests and limits on all containers; use LimitRange for defaults; use VPA recommendations |
| Mutable image tags in production | Deploying `:latest` or `:v1.2` allows image substitution without detection | Pin images to SHA-256 digest; use Kyverno mutateDigest |
| Running as root | UID 0 in container = host root if container escapes | `runAsNonRoot: true`; `runAsUser: 1000`; enforce via PodSecurity Restricted |
| Privileged containers in production | Full host access equivalent to root on node | Identify minimal capabilities needed; drop ALL; add specific caps |
| No readiness probe | Service routes to Pod before it is ready to serve | Always implement readinessProbe; health endpoint must check dependencies |
| StatefulSet with no PodDisruptionBudget | All database replicas can be evicted simultaneously during node drain | PDB `minAvailable >=` quorum for every StatefulSet |
| Flat namespace (everything in default) | No isolation, quota, or governance | Namespace per team/environment; RBAC per namespace; ResourceQuota per namespace |
| ClusterRoleBinding cluster-admin for apps | Application SA has full cluster admin access | Minimum RBAC: only verbs and resources required for the application |
| No NetworkPolicy (open flat network) | Any Pod can talk to any Pod; lateral movement trivial | Default-deny per namespace; explicit allow rules |
| Jobs without ttlSecondsAfterFinished | Completed Jobs accumulate; etcd grows unboundedly | Set `ttlSecondsAfterFinished` on all Jobs; configure CronJob history limits |

## Hands-On Exercises

### Exercise 5.1 — StatefulSet DNS

Deploy a StatefulSet and verify per-Pod stable DNS:

```bash
kubectl apply -f statefulset-nginx.yaml
kubectl get pods -l app=nginx-sts -w
# Verify stable DNS:
kubectl run dns-test --image=busybox:1.36 --restart=Never -it -- sh
nslookup nginx-0.nginx-headless.default.svc.cluster.local
# Delete Pod; verify it returns with same name:
kubectl delete pod nginx-1
kubectl get pods -l app=nginx-sts -w
```

### Exercise 5.2 — HPA Load Test

Deploy an HPA and observe CPU-triggered scaling:

```bash
kubectl create deployment php-apache --image=registry.k8s.io/hpa-example
kubectl expose deployment php-apache --port=80
kubectl autoscale deployment php-apache --cpu-percent=50 --min=1 --max=10
# Generate load:
kubectl run load-gen --image=busybox:1.36 --restart=Never -it -- \
  sh -c 'while true; do wget -q -O- http://php-apache; done'
# Watch scale-up in a separate terminal:
kubectl get hpa php-apache -w
kubectl get pods -l app=php-apache -w
```

### Exercise 5.3 — RBAC Audit

Audit and tighten RBAC permissions for a namespace:

```bash
# List all bindings:
kubectl get rolebindings,clusterrolebindings -A
# Check default SA permissions:
kubectl auth can-i --list --as=system:serviceaccount:default:default
# Find cluster-admin bindings (over-privileged):
kubectl get clusterrolebindings -o json | python3 -c "
import json, sys
d = json.load(sys.stdin)
for item in d['items']:
    if item['roleRef']['name'] == 'cluster-admin':
        for s in item.get('subjects', []):
            print(s.get('name', '?'))"
# Test NetworkPolicy enforcement:
kubectl apply -f default-deny-all.yaml
kubectl run test-client --image=busybox --restart=Never -it -- wget -T 3 http://api-backend
```

## Related

- [K8s Handbook Part 5: Kubernetes Resources](../38-k8s-handbook-part5-kubernetes-resources.md) — Part 1: Resource Taxonomy, Pods, Workloads, Services, Ingress, Configuration, Storage, Namespaces
