---
title: "K8s Handbook Part 4 (Part 3: kube-proxy, CoreDNS, Admission Controllers, CRDs & Operators)"
doc_type: guide
domain: platforms
status: current
topic_id: k8s-handbook-part4-kubernetes-internals-part3
last_reviewed: 2026-07-27
maturity: practitioner
supersedes: []
tags:
  - kubernetes
  - kube-proxy
  - coredns
  - admission-controllers
  - crds
  - operators
covers_version: "2025-2026 edition"
---

*Part 3 of 4 of [K8s Handbook Part 4: Kubernetes Internals](../37-k8s-handbook-part4-kubernetes-internals.md).*

## Chapter 8: kube-proxy — Service Networking

kube-proxy is a DaemonSet (or node daemon) that implements Kubernetes Service networking on each node. It watches Services and EndpointSlices and programs node-level network rules (iptables, IPVS, or eBPF) to route traffic to the correct backend Pods.

### kube-proxy Modes

| Mode | Implementation | Lookup Complexity | Max Scale | Recommendation |
| --- | --- | --- | --- | --- |
| iptables | iptables DNAT chains | O(n) linear scan | ~5,000 services | Legacy; avoid for large clusters |
| IPVS | kernel hash table | O(1) | 100,000+ services | Use for medium clusters |
| eBPF (Cilium) | BPF maps + XDP | O(1) | Unlimited | Best for all cluster sizes |
| nftables (1.31+) | nftables rules | O(log n) | Better than iptables | Emerging; replaces iptables mode |

### Service Types and kube-proxy Behaviour

| Service Type | ClusterIP | NodePort | External Access | kube-proxy Action |
| --- | --- | --- | --- | --- |
| ClusterIP | Virtual IP (cluster-internal only) | None | None (internal only) | iptables DNAT: ClusterIP → PodIP |
| NodePort | Virtual ClusterIP | Fixed port on all nodes | Via node IP:port | iptables DNAT: NodeIP:NodePort → PodIP |
| LoadBalancer | Virtual ClusterIP | Auto NodePort | Cloud LB IP | CCM creates LB; iptables for NodePort |
| ExternalName | None (DNS CNAME) | None | External DNS name | CoreDNS CNAME; no iptables |
| Headless | None (DNS A records) | None | Direct Pod IPs | CoreDNS A records per Pod; no proxy |

## Chapter 9: CoreDNS — Service Discovery

CoreDNS is the DNS server for Kubernetes clusters (replaced kube-dns in 1.11). It enables service discovery: pods can resolve Service names to ClusterIPs using DNS instead of hardcoding IP addresses. Every Pod has its `/etc/resolv.conf` configured to use CoreDNS as its DNS resolver.

### DNS Resolution Hierarchy

```
# /etc/resolv.conf in every Pod:
nameserver 10.96.0.10   # CoreDNS ClusterIP
search default.svc.cluster.local svc.cluster.local cluster.local
options ndots:5
```

DNS resolution search order (`ndots:5` means fewer than 5 dots → try search domains first):

- Query `my-service`:
  1. `my-service.default.svc.cluster.local` → Found (same namespace)
  2. `my-service.svc.cluster.local` → not tried (found in step 1)
- Query `my-service.other-namespace`:
  1. `my-service.other-namespace.default.svc.cluster.local` → not found
  2. `my-service.other-namespace.svc.cluster.local` → Found
- Query `api.external.com` (exceeds `ndots:5`): direct DNS query, no search domains tried

DNS name patterns: Service (same namespace) `<service>`; Service (cross-namespace) `<service>.<namespace>`; FQDN `<service>.<namespace>.svc.cluster.local`; Pod IP (rare) `10-244-1-5.default.pod.cluster.local`; StatefulSet Pod `<pod>.<service>.<namespace>.svc.cluster.local`.

### CoreDNS Corefile Configuration

```
# ConfigMap: kube-system/coredns (Corefile)
.:53 {
    errors
    health { lameduck 5s }
    ready
    kubernetes cluster.local in-addr.arpa ip6.arpa {
        pods insecure
        fallthrough in-addr.arpa ip6.arpa
        ttl 30
    }
    prometheus :9153   # Metrics endpoint
    forward . /etc/resolv.conf {   # Forward non-cluster queries to host DNS
        max_concurrent 1000
    }
    cache 30       # Cache TTL for responses
    loop          # Detect forwarding loops
    reload        # Auto-reload Corefile changes
    loadbalance   # Round-robin DNS load balancing
}

# Enterprise addition: forward internal domain to internal DNS
corp.internal:53 {
    forward . 10.0.0.53 10.0.0.54
    cache 30
}
```

## Chapter 10: Admission Controllers

Admission controllers are plug-ins that intercept API requests after authentication and authorisation but before persistence. They are the primary enforcement mechanism for policy, defaults, and security constraints in Kubernetes. Admission webhooks extend this mechanism to external policy engines.

### Built-in Admission Controllers

| Controller | Type | Function |
| --- | --- | --- |
| NamespaceLifecycle | Validating | Reject operations on terminating namespaces |
| LimitRanger | Mutating+Validating | Apply default resource requests/limits from LimitRange |
| ResourceQuota | Validating | Enforce namespace resource quotas |
| ServiceAccount | Mutating | Auto-inject default ServiceAccount and token volume |
| PodSecurity | Validating | Enforce Pod Security Standards (Restricted/Baseline/Privileged) |
| NodeRestriction | Validating | Restrict kubelet to only modify its own Node and Pods |
| DefaultStorageClass | Mutating | Assign default StorageClass to PVCs without one |
| MutatingAdmissionWebhook | Mutating | Call an external webhook to modify objects |
| ValidatingAdmissionWebhook | Validating | Call an external webhook to approve/reject objects |
| Priority | Mutating | Assign PriorityClass to Pods |
| RuntimeClass | Mutating | Apply RuntimeClass overhead to Pod resource requests |

### Dynamic Admission Webhooks

Webhooks are the most powerful admission extension. A webhook is an HTTPS endpoint that receives an `AdmissionReview` request and returns an `AdmissionReview` response with approval/rejection or mutations:

```yaml
# MutatingWebhookConfiguration example:
apiVersion: admissionregistration.k8s.io/v1
kind: MutatingWebhookConfiguration
metadata:
  name: inject-sidecar
webhooks:
  - name: sidecar.injection.company.com
    clientConfig:
      service:
        name: sidecar-injector
        namespace: istio-system
        path: /inject
      caBundle: <base64-ca-bundle>
    rules:
      - apiGroups: ['']
        apiVersions: [v1]
        resources: [pods]
        operations: [CREATE]
    namespaceSelector:
      matchLabels:
        istio-injection: enabled
    failurePolicy: Fail   # FAIL the request if webhook unreachable
    sideEffects: None      # No out-of-band side effects
    admissionReviewVersions: [v1]
    timeoutSeconds: 5      # Webhook must respond within 5s
```

> **Webhook failure modes — critical production consideration.** `failurePolicy: Fail` (the secure default) means that if your webhook is unavailable, NO PODS CAN BE SCHEDULED. A broken admission webhook has caused complete cluster outages. Always: (1) run webhooks with a minimum of 2 replicas, (2) set a PodDisruptionBudget, (3) exclude the `kube-system` namespace from webhook scope, (4) set a realistic `timeoutSeconds`, (5) test webhook degradation.

### OPA Gatekeeper and Kyverno

| Feature | OPA Gatekeeper | Kyverno |
| --- | --- | --- |
| Language | Rego (custom) | YAML/CEL (Kubernetes-native) |
| Learning curve | High (Rego) | Low (familiar YAML) |
| Policy types | ConstraintTemplate + Constraint | ClusterPolicy + Policy |
| Mutation support | Limited (assign/assignMetadata) | Full (strategic merge patch) |
| Generate resources | No | Yes (generate rules) |
| Image verification | Via external data | Native (`verifyImages` block) |
| Policy reports | Via audit | Native PolicyReport CRD |
| Maturity | CNCF Graduated | CNCF Incubating |
| Best for | Complex Rego policies, OPA ecosystem | K8s-native, ease of use, image signing |

## Chapter 11: Custom Resource Definitions (CRDs)

CRDs allow extending the Kubernetes API with custom resource types. Once a CRD is installed, users can create, read, update, and delete instances of the custom resource using kubectl and the Kubernetes API — just like built-in resources. CRDs are the foundation of the Operator pattern and the entire CNCF ecosystem.

### CRD Structure

```yaml
apiVersion: apiextensions.k8s.io/v1
kind: CustomResourceDefinition
metadata:
  name: postgresclusters.postgres-operator.crunchydata.com
spec:
  group: postgres-operator.crunchydata.com
  names:
    kind: PostgresCluster
    plural: postgresclusters
    singular: postgrescluster
    shortNames: [pgc]
  scope: Namespaced
  versions:
    - name: v1beta1
      served: true
      storage: true
      schema:
        openAPIV3Schema:
          type: object
          properties:
            spec:
              type: object
              properties:
                instances:
                  type: array
                  items:
                    type: object
                    properties:
                      replicas:
                        type: integer
                        minimum: 1
                      postgresVersion:
                        type: integer
                        enum: [14, 15, 16]
      additionalPrinterColumns:
        - name: Age
          jsonPath: .metadata.creationTimestamp
          type: date
      subresources:
        status: {}   # Enable status subresource
```

### CRD Best Practices

- **Versioning strategy**: plan API versions from day one. Use a `v1alpha1 → v1beta1 → v1` progression. Implement conversion webhooks for multi-version support.
- **Schema validation**: define a complete OpenAPI v3 schema. Reject invalid objects at admission time rather than discovering problems at reconciliation time.
- **Status subresource**: always enable the status subresource. Allows status updates without triggering watch events on spec. Prevents accidental status overwrites by users.
- **Printer columns**: define `additionalPrinterColumns` for useful `kubectl get` output.
- **Finalizers**: use finalizers for resources requiring external cleanup (cloud resources, certificates, DNS records). Prevents deletion before cleanup completes.
- **Owner references**: set `ownerReferences` on resources created by the operator so garbage collection automatically cleans up when the owner is deleted.

## Chapter 12: The Operator Pattern

An Operator is a controller that manages a complex, stateful application (a database, message queue, ML model server) using the same reconciliation loop pattern as Kubernetes' built-in controllers — but encoding application-specific operational knowledge. Operators automate the Day 2 operations that would otherwise require a human expert: provisioning, configuration, upgrades, scaling, backup, and recovery.

### Operator Maturity Model

| Level | Capabilities | Example |
| --- | --- | --- |
| Level 1: Basic Install | Automated application install and configuration | Deploy MySQL with correct config |
| Level 2: Seamless Upgrades | Patch and minor version upgrades managed | Upgrade PostgreSQL 15 → 16 safely |
| Level 3: Full Lifecycle | App lifecycle: backup, restore, failure recovery | Automated PITR restore for PostgreSQL |
| Level 4: Deep Insights | Metrics, alerts, log processing, workload analysis | Custom Grafana dashboards via operator |
| Level 5: Auto Pilot | Horizontal/vertical scaling, anomaly detection, tuning | Auto-tune PostgreSQL based on workload |

### Production Operators for AI Workloads

| Operator | Manages | Key Capabilities |
| --- | --- | --- |
| NVIDIA GPU Operator | NVIDIA driver, container toolkit, device plugin | Full GPU stack on Kubernetes nodes |
| KServe | ML model serving | Multi-framework inference, auto-scaling, canary |
| Kubeflow Operator | Kubeflow ML platform | Pipelines, notebooks, training jobs |
| Ray Operator | Ray distributed compute clusters | RayCluster, RayJob, RayService |
| Strimzi | Apache Kafka | Kafka cluster lifecycle, topic management, MirrorMaker |
| CloudNativePG | PostgreSQL clusters | HA Postgres, backup, replica management |
| Argo Workflows Operator | Workflow execution engine | DAG workflows for ML pipelines |
| Prometheus Operator | Prometheus monitoring stack | ServiceMonitor, PrometheusRule CRDs |
| cert-manager | TLS certificates | ACME, Vault, self-signed certs for all services |
| External Secrets Operator | Secret synchronisation | Sync from Vault, AWS SM, GCP SM |

## Related

- [Part 2: Controller Manager, Cloud Controller Manager & kubelet](37-k8s-handbook-part4-kubernetes-internals-part2.md)
- [Part 4: Leader Election, API Request Lifecycle & Troubleshooting](37-k8s-handbook-part4-kubernetes-internals-part4.md)
