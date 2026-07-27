---
title: "K8s Handbook Part 15: Implementation Labs"
doc_type: guide
domain: platforms
status: current
topic_id: k8s-handbook-part15-implementation-labs
last_reviewed: 2026-07-27
maturity: practitioner
supersedes: [docs/cloud-platforms/kubernetes/K8s_Handbook_Part15_Implementation_Labs.md]
tags: [kubernetes, hands-on-labs, gitops, vllm, rag]
covers_version: "2025-2026 edition"
---

These labs progress from basic cluster setup to a full production AI platform. Each lab builds on the previous. Complete all prerequisites before starting each lab. Estimated total time: 40-60 hours for all 10 labs.

## Progressive Implementation Path

| Lab | Title | Hours | Prerequisites | Key Skills |
|---|---|---|---|---|
| 1 | Bootstrap Production Cluster | 4-6 | Cloud account, kubectl, helm | kubeadm/managed K8s, Cilium, ArgoCD |
| 2 | Deploy and Scale Microservice | 3-4 | Lab 1 | Deployment, HPA, Ingress, cert-manager, Prometheus |
| 3 | Zero Trust Networking | 4-5 | Lab 2 | Kyverno, Istio Ambient, NetworkPolicy, Falco |
| 4 | GitOps with ArgoCD | 3-4 | Lab 1 | ApplicationSet, Argo Rollouts, canary deployment |
| 5 | Secure Secret Management | 3-4 | Lab 1 | Vault HA, ESO, dynamic secrets, secret rotation |
| 6 | Storage, Snapshots, DR | 4-5 | Lab 1 | CSI, StorageClass, VolumeSnapshot, Velero |
| 7 | GPU Workload + vLLM | 4-6 | Lab 1, GPU node | GPU Operator, MIG, vLLM, DCGM metrics |
| 8 | Full RAG Pipeline | 5-6 | Labs 6, 7 | Qdrant, embedding Job, RAG API, OTel traces |
| 9 | Agentic AI with Temporal | 5-6 | Labs 7, 8 | Temporal, agent worker, KEDA, MCP server |
| 10 | Production Hardening | 4-5 | Labs 1-9 | CIS benchmark, Trivy cluster scan, IR playbook |

## Lab 1: Bootstrap a Production Cluster

- Install kubeadm on 3 control plane VMs (or use managed EKS/GKE/AKS).
- Deploy Cilium CNI with kube-proxy replacement and WireGuard encryption.
- Configure OIDC (Dex or Keycloak) for cluster authentication.
- Install ArgoCD (HA mode) and bootstrap the App-of-Apps pattern.
- Install cert-manager, Vault (dev mode), the Prometheus stack, Loki, and Falco.
- Verify with `kubectl cluster-info`, `kubectl top nodes`, `argocd app list`.

```bash
kubectl get nodes -o wide
cilium status
argocd app list
kubectl get pods -A | grep -v Running
```

## Lab 2: Deploy and Scale a Microservice

- Create a Deployment with resource requests, security context, and health probes.
- Expose via a Service and configure Ingress with TLS via cert-manager ACME.
- Create an HPA targeting 70% CPU utilisation (`minReplicas=2`, `maxReplicas=10`).
- Create a Prometheus ServiceMonitor for the application metrics endpoint.
- Import or create a Grafana dashboard showing request rate, latency, and error rate.
- Load test with k6 and observe HPA scaling decisions in real time.

```bash
kubectl describe hpa myapp
kubectl get ingress
curl -k https://myapp.example.com/health
k6 run load-test.js
```

## Lab 3: Zero Trust Networking

- Apply a default-deny NetworkPolicy to the production namespace.
- Enable Istio Ambient Mesh: `kubectl label ns production istio.io/dataplane-mode=ambient`.
- Apply Kyverno ClusterPolicies: `require-nonroot`, `require-readonly-rootfs`, `require-seccomp`.
- Verify mTLS is enforced: `istioctl authn tls-check`.
- Test the NetworkPolicy: verify blocked traffic between non-allowed namespaces.
- Deploy Falco and trigger a test alert by spawning a shell in a container.

```bash
kubectl exec -n test -- sh  # Falco should alert
istioctl authn tls-check
kubectl get netpol -A
```

## Lab 4: GitOps with ArgoCD

- Create an ApplicationSet deploying to dev, staging, and production from one template.
- Implement an Argo Rollouts canary: 5% → 20% → 50% → 100% with Prometheus analysis.
- Simulate a bad deployment: cause errors in the canary and observe automatic rollback.
- Enable `selfHeal: true` and `prune: true`; make a manual `kubectl` change and watch it revert.
- Review the ArgoCD application history and practice rollback to a previous revision.

```bash
argocd app get myapp-production
kubectl argo rollouts status myapp
kubectl argo rollouts undo myapp
```

## Lab 5: Secure Secret Management

- Install Vault in HA mode with a Raft backend and auto-unseal (cloud KMS).
- Configure the Kubernetes auth method in Vault.
- Create dynamic PostgreSQL credentials with a 1-hour TTL via the Vault database engine.
- Install the External Secrets Operator and create an ExternalSecret syncing from Vault.
- Demonstrate secret rotation: rotate the PostgreSQL password and confirm the Pod gets new creds without a restart.
- Verify no secrets appear in environment variables or log output.

```bash
vault status
vault read database/creds/myapp-role
kubectl get externalsecret -A
kubectl describe secret myapp-db-creds
```

## Lab 6: Storage, Snapshots, and Disaster Recovery

- Install a cloud CSI driver and create a gp3 StorageClass with a Retain reclaim policy.
- Deploy a PostgreSQL StatefulSet with a PVC and write test data.
- Install VolumeSnapshot CRDs and the CSI snapshotter, then take a snapshot.
- Restore the snapshot to a new PVC in the staging namespace and verify data integrity.
- Expand the original PVC by 50% without downtime.
- Install Velero, create a scheduled backup, simulate a disaster, and restore from the backup.

```bash
kubectl get pvc -A
kubectl get volumesnapshot -A
velero backup describe my-backup
velero restore create --from-backup my-backup
```

## Lab 7: GPU Workload and vLLM Deployment

- Install the NVIDIA GPU Operator on a GPU node (`g5.xlarge` or similar).
- Verify the GPU resource is schedulable: `kubectl describe node | grep nvidia.com/gpu`.
- Configure MIG partitioning on A100 (if available): 3x `1g.10gb` instances.
- Deploy vLLM with Qwen2.5-1.5B-Instruct (a small model for cost-effective testing).
- Load test with 10 concurrent users and observe DCGM GPU utilisation in Grafana.
- Implement a KEDA ScaledObject scaling vLLM replicas on request queue depth.

```bash
kubectl describe node gpu-node | grep -i nvidia
curl http://vllm:8000/v1/models
kubectl top pods -n ai-serving
```

## Lab 8: Full RAG Pipeline

- Deploy a Qdrant StatefulSet with a 500GB NVMe PVC.
- Run an embedding generation Job: ingest 10,000 documents from S3 into Qdrant.
- Deploy a RAG API server (FastAPI) with OTel instrumentation.
- Wire RAG API → Qdrant (vector search) → vLLM (generation) → response.
- Run 20 test queries and verify retrieved context plus generated responses.
- Open Grafana and view traces in Tempo showing the full RAG request path.

```bash
kubectl get pods -n ai-platform
curl http://rag-api/query -d '{"question": "What is our refund policy?"}'
hubble observe --namespace ai-platform
```

## Lab 9: Agentic AI with Temporal

- Install Temporal on Kubernetes with a PostgreSQL backend and web UI.
- Write a simple research agent workflow in the Python SDK (web search + LLM synthesis).
- Deploy an agent worker Deployment (2 replicas) and apply a KEDA ScaledObject on the Kafka task queue.
- Submit 5 workflows via the Temporal CLI and observe execution in the Temporal web UI.
- Kill a worker mid-execution and observe Temporal automatically resume it on another worker.
- Deploy an MCP server with a web search tool and update the agent to use MCP for tool calls.

```bash
temporal workflow list
temporal workflow describe -w WORKFLOW_ID
kubectl delete pod temporal-worker-xyz  # Test fault tolerance
temporal workflow list  # Verify workflow resumed
```

## Lab 10: Production Hardening and Compliance

- Run the `kube-bench` CIS Kubernetes Benchmark and remediate all Level 1 findings.
- Run `trivy k8s --report summary cluster` and remediate CRITICAL image CVEs.
- Enforce Pod Security Standards Restricted on all production namespaces.
- Configure Falco with PagerDuty integration and test with a simulated attack (shell exec).
- Run an RBAC audit: find all `cluster-admin` bindings and remove unnecessary ones.
- Document and test the incident response playbook: detect, contain, forensics, remediate.

```bash
kube-bench run --targets master,node
trivy k8s --report summary cluster
kubectl auth can-i --list --as=system:serviceaccount:prod:myapp-sa
```
