---
title: "K8s Handbook Part 8: Security (Part 2)"
doc_type: guide
domain: platforms
status: current
topic_id: k8s-handbook-part8-security-part2
last_reviewed: 2026-07-27
maturity: practitioner
supersedes: []
tags: [kubernetes, security, compliance, supply-chain, runtime-security]
covers_version: "2025-2026 edition"
---

> Continues from [K8s Handbook Part 8: Security](../41-k8s-handbook-part8-security.md), covering Chapters 10-17: policy-as-code, supply chain security, runtime security, confidential computing, a hardening checklist, compliance mapping, incident response, and hands-on exercises.

## Policy-as-Code: OPA Gatekeeper and Kyverno

Policy-as-code enforces security and operational standards at admission time, preventing non-compliant workloads from being deployed rather than detecting violations after the fact. Two systems dominate the Kubernetes policy landscape: OPA Gatekeeper (using Rego) and Kyverno (using YAML/CEL).

### OPA Gatekeeper — Rego Policies

```yaml
# Gatekeeper ConstraintTemplate (defines the policy)
apiVersion: templates.gatekeeper.sh/v1
kind: ConstraintTemplate
metadata:
  name: requiredlabels
spec:
  crd:
    spec:
      names: { kind: RequiredLabels }
      validation:
        openAPIV3Schema:
          type: object
          properties:
            labels:
              type: array
              items: { type: string }
  targets:
    - target: admission.k8s.gatekeeper.sh
      rego: |
        package requiredlabels
        violation[{"msg": msg}] {
          required := input.parameters.labels[_]
          not input.review.object.metadata.labels[required]
          msg := sprintf("Missing required label: %v", [required])
        }
---
# Constraint (applies the template)
apiVersion: constraints.gatekeeper.sh/v1beta1
kind: RequiredLabels
metadata:
  name: require-team-label
spec:
  enforcementAction: deny
  match:
    kinds: [{ apiGroups: [apps], kinds: [Deployment] }]
  parameters:
    labels: [team, cost-center, environment]
```

### Kyverno — YAML-Native Policies

```yaml
# Kyverno policy: require non-root, read-only filesystem
apiVersion: kyverno.io/v1
kind: ClusterPolicy
metadata:
  name: require-pod-security-hardening
spec:
  validationFailureAction: Enforce
  background: true
  rules:
    - name: require-run-as-non-root
      match:
        resources: { kinds: [Pod] }
      validate:
        message: Pods must not run as root
        pattern:
          spec:
            securityContext:
              runAsNonRoot: true
    - name: require-readonly-rootfs
      match:
        resources: { kinds: [Pod] }
      validate:
        message: Root filesystem must be read-only
        pattern:
          spec:
            containers:
              - securityContext:
                  readOnlyRootFilesystem: true
---
# Kyverno generate: auto-create a NetworkPolicy on new namespace
apiVersion: kyverno.io/v1
kind: ClusterPolicy
metadata:
  name: add-default-networkpolicy
spec:
  rules:
    - name: default-deny
      match:
        resources: { kinds: [Namespace] }
      generate:
        apiVersion: networking.k8s.io/v1
        kind: NetworkPolicy
        name: default-deny-all
        namespace: '{{request.object.metadata.name}}'
        data:
          spec:
            podSelector: {}
            policyTypes: [Ingress, Egress]
```

## Supply Chain Security at Scale

At enterprise scale, supply chain security must be automated and enforced as policy rather than relying on developer discipline. The goal is a continuous verification pipeline from source code to running container:

1. **Source code** — signed commits (GPG/SSH), branch protection + CODEOWNERS, dependency scanning (Dependabot, Renovate).
2. **Build (CI/CD — GitHub Actions / Tekton)** — a BuildKit hermetic build, SBOM generation (Syft → CycloneDX JSON), SLSA provenance generation (`slsa-github-generator`), Cosign keyless signing, a Trivy vulnerability scan (fail on CRITICAL), and attestation upload (SBOM, provenance, scan results).
3. **Registry (Harbor)** — immutable tags enabled, a policy blocking CRITICAL-CVE images, continuous rescan (daily Trivy), and signature verification on push.
4. **Admission (Kubernetes)** — Kyverno `verifyImages` (signature required), Kyverno SBOM attestation required, Kyverno restricting to `harbor.internal.corp` images only, and OPA blocking any known CRITICAL CVEs.
5. **Runtime** — Falco detecting unexpected processes, Tetragon blocking unexpected network calls, and regular re-evaluation for continuous compliance.

## Runtime Security: Falco and Tetragon

### Falco — CNCF Runtime Security

Falco monitors system calls and Kubernetes audit events to detect anomalous behaviour at runtime. It uses eBPF probes (preferred) or a kernel module to observe every syscall made by every process in every container on a node.

```yaml
# Critical Falco rules for AI platform security

# 1. Detect crypto mining (GPU abuse)
- rule: Crypto mining process detected
  condition: spawned_process and container and proc.name in (xmrig, cryptonight, minerd)
  output: Crypto miner detected (proc=%proc.name container=%container.name)
  priority: CRITICAL

# 2. Model exfiltration attempt
- rule: Large data transfer from inference container
  condition: >
    outbound and container and k8s.pod.label.app = llm-inference
    and fd.net.bytes.out > 1073741824
    and not fd.rip in (10.0.0.0/8, 172.16.0.0/12)
  output: Possible model exfiltration (dest=%fd.rip bytes=%fd.net.bytes.out)
  priority: CRITICAL

# 3. Prompt injection via shell escape
- rule: Shell spawned in AI workload
  condition: >
    spawned_process and container and proc.name in (bash, sh, zsh)
    and k8s.pod.label.tier = ai
  output: Shell in AI container (user=%user.name cmd=%proc.cmdline)
  priority: WARNING
```

### Falco Alerting Integration

```bash
# Falco Sidekick routes alerts to multiple destinations
helm install falco falcosecurity/falco \
  --set driver.kind=ebpf \
  --set falcosidekick.enabled=true \
  --set falcosidekick.config.slack.webhookurl=SLACK_URL \
  --set falcosidekick.config.pagerduty.routingKey=PD_KEY \
  --set falcosidekick.config.elasticsearch.hostport=http://elastic:9200 \
  --set falcosidekick.config.alertmanager.hostport=http://alertmanager:9093
```

```
# Falco metrics for Prometheus
# Alert: any CRITICAL Falco event in production namespace
falco_events_total{rule=~'.*',priority='CRITICAL'} > 0
```

## Confidential Containers and Confidential Computing

### Confidential Computing Hardware

| Technology | Vendor | Protection | Kubernetes Integration |
|---|---|---|---|
| Intel TDX (Trust Domain Extensions) | Intel (4th gen Xeon+) | VM-level memory encryption; hardware attestation | Kata Containers + TDX; CoCo project |
| AMD SEV-SNP (Secure Encrypted Virtualisation) | AMD (EPYC 3rd gen+) | VM memory encrypted; SNP = nested page integrity | Kata Containers + SEV-SNP; widely available |
| ARM CCA (Confidential Compute Architecture) | ARM (v9.2+) | Realm VMs; hardware attestation | Emerging; ARM server adoption growing |
| Intel SGX (Software Guard Extensions) | Intel (older) | Enclave-level (user app) | EGo, Gramine; complex; limited memory |
| NVIDIA H100 Confidential Computing | NVIDIA | GPU memory encryption; TEE attestation | NVIDIA Confidential Containers; AI workloads |

### Confidential Containers (CoCo) Project

The Confidential Containers CNCF project enables running standard OCI containers inside hardware TEEs with cryptographic attestation. This provides confidentiality for AI model weights and inference data against cloud-provider-level attackers.

CoCo's architecture layers from the top down: the Kubernetes API selects a `kata-remote` RuntimeClass (the Confidential Containers runtime); a `cloud-api-adaptor` connects Kubernetes to the cloud TEE API; this provisions a TEE Virtual Machine (AMD SEV-SNP / Intel TDX) with encrypted memory and hardware attestation; inside the VM, an Attestation Agent provides evidence to an external Attestation Service (KBS — Key Broker Service), which verifies the hardware attestation and releases secrets only to attested workloads.

```yaml
# Deploy with CoCo RuntimeClass
apiVersion: node.k8s.io/v1
kind: RuntimeClass
metadata:
  name: kata-remote
handler: kata-remote
---
# Pod using confidential computing
spec:
  runtimeClassName: kata-remote
  containers:
    - name: llm-inference
      image: company/llm-server:v1
      # Model weights decrypted only inside the TEE;
      # the cloud provider cannot access the model or inference data.
```

## Kubernetes Security Hardening Checklist

### Control Plane

- API server: `--anonymous-auth=false`
- API server: `--audit-log-path`, `--audit-log-maxage=30`, `--audit-log-maxbackup=3`
- API server: `--tls-min-version=VersionTLS12`
- API server: `--disable-admission-plugins` does not include `NodeRestriction`
- etcd: `--client-cert-auth=true`, `--peer-client-cert-auth=true`
- etcd: encryption at rest enabled (`EncryptionConfiguration` with AES-GCM or KMS)
- Scheduler: `--profiling=false`
- Controller manager: `--profiling=false`, `--use-service-account-credentials=true`

### Node/kubelet

- kubelet: `--anonymous-auth=false`, `--authorization-mode=Webhook`
- kubelet: `--rotate-certificates=true`, `--rotate-server-certificates=true`
- kubelet: `--protect-kernel-defaults=true`
- kubelet: `--event-qps=0` (disable event rate limiting for audit)
- Node OS: CIS-hardened image (Bottlerocket, Flatcar, Ubuntu CIS)
- Node OS: SSH access restricted; no direct SSH in production (use `kubectl debug`)
- Node: no direct internet access; egress via NAT gateway or proxy

### Workloads

- Pod Security Standards: Restricted for all production namespaces
- All Pods: `runAsNonRoot: true`, `readOnlyRootFilesystem: true`
- All Pods: `capabilities.drop: ALL`
- All Pods: `seccompProfile: RuntimeDefault`
- No Pods with `hostNetwork`, `hostPID`, `hostIPC`
- No privileged containers
- Resource requests and limits on all containers

### RBAC and Identity

- No `cluster-admin` bindings for service accounts
- No wildcard verbs or resources in RBAC rules
- ServiceAccount `automountServiceAccountToken: false` by default
- OIDC for human authentication (not a static kubeconfig with certs)
- Workload Identity (IRSA/GKE WI) for cloud API access

### Network

- Default-deny NetworkPolicy in all production namespaces
- API server not publicly exposed (private endpoint only)
- Node-to-node communication encrypted (Cilium WireGuard or IPsec)
- Egress NetworkPolicy restricts outbound to known endpoints

## Compliance Mapping: NIST, CIS, SOC2, PCI, HIPAA, EU AI Act

Enterprise Kubernetes deployments must satisfy multiple overlapping compliance frameworks. The following mapping shows which Kubernetes controls satisfy requirements from the most common frameworks.

| Kubernetes Control | NIST SP 800-53 | CIS K8s Benchmark | SOC2 | PCI DSS | HIPAA | EU AI Act |
|---|---|---|---|---|---|---|
| RBAC least privilege | AC-6 | 5.1 | CC6.3 | 7.1.2 | 164.312(a) | Art.9 (access) |
| Audit logging | AU-2, AU-12 | 3.2 | CC7.2 | 10.2 | 164.312(b) | Art.13 (transparency) |
| etcd encryption at rest | SC-28 | 1.2.33 | CC6.7 | 3.5 | 164.312(a)(2)(iv) | Art.10 (data) |
| mTLS / encryption in transit | SC-8 | 5.7 | CC6.7 | 4.1 | 164.312(e)(2)(ii) | Art.10 |
| Image signing + SBOM | SA-12, CM-14 | N/A | CC7.1 | 6.3.2 | 164.312(c) | Art.15 (supply chain) |
| Pod Security Standards | SI-7 | 5.2 | CC6.1 | 2.2 | 164.312(c) | Art.9 |
| Network policy default-deny | SC-7 | 5.3 | CC6.6 | 1.2 | 164.312(e) | Art.9 |
| Secret management (Vault) | IA-5, SC-28 | Implicit | CC6.7 | 8.3 | 164.312(a) | Art.10 |
| Runtime detection (Falco) | SI-4, IR-5 | Implicit | CC7.3 | 10.6 | 164.312(b) | Art.14 (monitoring) |
| Vulnerability scanning | RA-5, SI-2 | Implicit | CC7.1 | 6.3.3 | 164.308(a)(1) | Art.15 |
| Backup + DR | CP-9, CP-10 | Implicit | A1.2 | 12.10.1 | 164.308(a)(7) | Art.12 |

### EU AI Act — Kubernetes-Specific Requirements

The EU AI Act (fully applicable August 2026) introduces specific requirements for high-risk AI systems that directly impact Kubernetes AI platform design:

- **Article 9 — Risk management** — implement RBAC, NetworkPolicy, and admission controls to enforce access boundaries around AI model access and inference endpoints.
- **Article 10 — Data governance** — use encrypted PVCs for training data, implement data lineage tracking (MLflow), and enforce namespace isolation between data categories.
- **Article 12 — Record keeping** — maintain immutable audit logs (Kubernetes audit + Falco events) stored outside the cluster; log all model access, inference requests to high-risk models, and configuration changes.
- **Article 13 — Transparency** — maintain an SBOM for all AI components, and document model versions and training data provenance in the model registry.
- **Article 15 — Accuracy and robustness** — implement canary deployments and A/B testing for model updates, and monitor inference accuracy metrics in Prometheus/Grafana.

## Security Incident Response on Kubernetes

When a Kubernetes security incident occurs — a compromised container, credential theft, suspicious lateral movement — the response must be fast and systematic. Kubernetes provides unique tools for containment and forensics.

### Incident Response Playbook

**Phase 1: Detection (seconds to minutes)** — a Falco alert fires (e.g. a shell spawned in a production container); the alert routes to PagerDuty and an on-call engineer; the team correlates with Kubernetes audit logs and network flows (Hubble).

**Phase 2: Containment (minutes)**

```bash
# Immediately isolate the compromised Pod with a NetworkPolicy
kubectl label pod COMPROMISED_POD quarantine=true
kubectl apply -f - <<'YAML'
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata: { name: quarantine }
spec:
  podSelector:
    matchLabels: { quarantine: 'true' }
  policyTypes: [Ingress, Egress]
  # No rules = deny all traffic
YAML

# Scale down the compromised Deployment (remove it from the Service)
kubectl scale deployment COMPROMISED_DEPLOY --replicas=0
```

**Phase 3: Forensics (minutes to hours)**

```bash
# Capture Pod state before deletion
kubectl describe pod COMPROMISED_POD > forensics/pod-describe.txt
kubectl get events --field-selector involvedObject.name=COMPROMISED_POD
kubectl logs COMPROMISED_POD --all-containers > forensics/pod-logs.txt
kubectl exec -it COMPROMISED_POD -- ps aux > forensics/processes.txt

# Export the filesystem for analysis
crictl export CONTAINER_ID forensics/container-fs.tar

# Review the API audit log
grep COMPROMISED_POD /var/log/kubernetes/audit.log | jq .
```

**Phase 4: Remediation** — rotate any credentials the compromised container had access to, rebuild affected images from scratch, apply any missing security controls (PSS, NetworkPolicy, seccomp), and update Falco rules if a new attack pattern was identified.

## Hands-On Exercises

### Exercise 8.1 — RBAC Hardening

Audit and fix over-privileged RBAC:

```bash
# Identify over-privileged service accounts
kubectl auth can-i --list \
  --as=system:serviceaccount:default:default -n default

# Create a minimal service account
kubectl create serviceaccount myapp-minimal-sa -n default

# Create a minimal Role (read own configmap only)
kubectl create role myapp-role \
  --verb=get --resource=configmaps \
  --resource-name=myapp-config -n default
kubectl create rolebinding myapp-binding \
  --role=myapp-role \
  --serviceaccount=default:myapp-minimal-sa -n default

# Verify: can read its own configmap
kubectl auth can-i get configmaps/myapp-config \
  --as=system:serviceaccount:default:myapp-minimal-sa -n default

# Verify: cannot read secrets
kubectl auth can-i get secrets \
  --as=system:serviceaccount:default:myapp-minimal-sa -n default
```

### Exercise 8.2 — Kyverno Policy Enforcement

Deploy Kyverno and enforce security policies:

```bash
# Install Kyverno
helm repo add kyverno https://kyverno.github.io/kyverno/
helm install kyverno kyverno/kyverno --namespace kyverno --create-namespace

# Apply a policy requiring non-root
kubectl apply -f - <<'YAML'
apiVersion: kyverno.io/v1
kind: ClusterPolicy
metadata:
  name: require-nonroot
spec:
  validationFailureAction: Enforce
  rules:
    - name: nonroot
      match:
        resources: { kinds: [Pod] }
      validate:
        message: Must run as non-root
        pattern:
          spec:
            securityContext:
              runAsNonRoot: true
YAML

# Try to deploy a root container (should be blocked)
kubectl run root-test --image=nginx --restart=Never
# Expected: the admission webhook denies the request

# Deploy a compliant Pod
kubectl run nonroot-test --image=nginx:alpine \
  --overrides='{"spec":{"securityContext":{"runAsNonRoot":true,"runAsUser":101}}}'
```

## Related

- [K8s Handbook Part 8: Security](../41-k8s-handbook-part8-security.md) — Part 1: Enterprise Security Model, Zero Trust, Authentication, RBAC, SPIFFE/SPIRE, Vault, cert-manager, mTLS, Pod Security
