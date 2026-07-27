---
title: "K8s Handbook Part 8: Security"
doc_type: guide
domain: platforms
status: current
topic_id: k8s-handbook-part8-security
last_reviewed: 2026-07-27
maturity: practitioner
supersedes: [docs/cloud-platforms/kubernetes/K8s_Handbook_Part8_Security.md]
tags: [kubernetes, security, zero-trust, rbac, secrets]
covers_version: "2025-2026 edition"
---

Kubernetes security requires a layered, defence-in-depth approach. No single control is sufficient; attackers who defeat one layer must face additional barriers. Enterprise Kubernetes security addresses four fundamental questions: who are you (identity), what can you do (authorisation), what are you running (workload security), and what is it doing (runtime detection)?

## Enterprise Security Model for Kubernetes

### Kubernetes Threat Model

| Threat | Attack Vector | Kubernetes Impact | Primary Controls |
|---|---|---|---|
| Container escape | Kernel exploit, misconfiguration | Host root access, lateral movement | gVisor/Kata, seccomp, capabilities, PSS |
| Supply chain attack | Compromised image or dependency | Malicious code in production | Image signing, scanning, admission control |
| Credential theft | Stolen kubeconfig, SA token | Full cluster compromise | OIDC, short-lived tokens, RBAC audit |
| Privilege escalation | Exploit RBAC misconfiguration | Cluster-admin from low-priv access | Least privilege RBAC, no wildcards |
| Data exfiltration | Network egress from compromised Pod | Data theft | NetworkPolicy, egress control, DLP |
| Denial of Service | Resource exhaustion | Node/cluster unavailability | ResourceQuota, LimitRange, PDB |
| API server attack | Exposed API server, brute force | Cluster takeover | Private API server, auth webhook, audit |
| etcd compromise | Direct etcd access | All secrets/config exposed | TLS client auth, encryption at rest, firewall |
| Insider threat | Malicious admin | Any cluster action | Audit logging, MFA, break-glass procedures |

### Security Control Layers

1. **Supply chain** — image signing (Cosign), SBOM, vulnerability scanning, SLSA provenance.
2. **Cluster hardening** — API server flags, etcd encryption, audit logging, CIS benchmark compliance.
3. **Identity and access** — OIDC authentication, RBAC least-privilege, SPIFFE workload identity.
4. **Workload security** — Pod Security Standards, seccomp, AppArmor, non-root, read-only filesystem.
5. **Network security** — NetworkPolicy default-deny, mTLS (Istio/Cilium), egress control.
6. **Secret management** — Vault/External Secrets, etcd encryption at rest, no Secrets in Git.
7. **Runtime detection** — Falco, Tetragon, anomaly detection, SIEM integration.
8. **Audit and compliance** — API audit logs, compliance scanning, penetration testing.

## Zero Trust Architecture on Kubernetes

Zero Trust rejects the perimeter security model. In Kubernetes, Zero Trust means every workload must prove its identity before accessing any resource, every connection is authenticated and encrypted (mTLS), every access is authorised per-request, and every action is logged and monitored. The implicit trust within a flat cluster network is eliminated.

### Zero Trust Principles Applied to Kubernetes

- **Verify explicitly** — every service-to-service call carries a cryptographic identity (a SPIFFE SVID); the receiving service verifies the identity before processing, implemented via service mesh mTLS (Istio, Linkerd, Cilium mTLS).
- **Least privilege access** — no workload has access beyond what it needs for its function; RBAC policies deny by default, service accounts have minimal permissions, and NetworkPolicies deny all traffic not explicitly allowed.
- **Assume breach** — security controls assume an attacker already has code execution inside the cluster; runtime monitoring (Falco) detects lateral movement, and blast radius is minimised through namespace isolation and network segmentation.
- **Continuous verification** — certificates expire (short TTL), tokens are rotated, policy is continuously enforced at admission and runtime, and audit logs capture every action for forensic analysis.

### Zero Trust Implementation Roadmap

| Phase | Controls | Timeline | Complexity |
|---|---|---|---|
| Phase 1: Identity | OIDC SSO, service accounts with IRSA/Workload Identity, audit logging | Month 1-2 | Low |
| Phase 2: Authorisation | RBAC audit and hardening, OPA/Kyverno policies, admission webhooks | Month 2-3 | Medium |
| Phase 3: Workload | Pod Security Standards Restricted, seccomp, image signing | Month 3-4 | Medium |
| Phase 4: Network | NetworkPolicy default-deny, egress control, FQDN policies | Month 4-5 | Medium |
| Phase 5: Encryption | mTLS via Istio/Linkerd/Cilium, secrets encryption at rest | Month 5-7 | High |
| Phase 6: Runtime | Falco deployment, alert routing, SIEM integration, IR playbooks | Month 7-9 | High |
| Phase 7: Confidential | Confidential Containers, attestation, HSM integration | Month 9-12 | Very High |

## Authentication: Users, OIDC, Service Accounts

Kubernetes supports multiple authentication mechanisms. Choosing the right mechanism for each identity type — human users, CI/CD systems, and workloads — is foundational to a secure cluster.

### Authentication Methods

| Method | Identity Type | Token Lifetime | Enterprise Recommendation |
|---|---|---|---|
| X.509 client certificate | Admin users (break-glass only) | Certificate validity (often years) | Avoid for regular use; use for emergency admin only |
| OIDC (OpenID Connect) | Human users, CI/CD | Short (minutes to hours) | Preferred for all human access; integrates with SSO |
| Service Account Token (static) | In-cluster workloads | Infinite (until deleted) | Legacy; avoid; use bound tokens instead |
| Service Account Token (bound) | In-cluster workloads | Configurable (1h default) | Use TokenRequest API; auto-rotated by kubelet |
| IRSA (EKS) / Workload Identity (GKE) | Cloud API access from Pods | Short (hours) | Best for cloud service access from Pods |
| Webhook Token Auth | Any | Depends on webhook | Integrates with external IdP when OIDC not available |

### OIDC Integration — kube-apiserver Configuration

```yaml
# kube-apiserver flags for OIDC (kubeadm ClusterConfiguration)
apiServer:
  extraArgs:
    oidc-issuer-url: https://accounts.google.com
    # Or a corporate IdP:
    # oidc-issuer-url: https://idp.company.com/realms/kubernetes
    oidc-client-id: kubernetes
    oidc-username-claim: email
    oidc-groups-claim: groups
    oidc-username-prefix: 'oidc:'
    oidc-groups-prefix: 'oidc:'
```

```yaml
# kubeconfig for the OIDC user (managed by kubelogin)
users:
  - name: my-user
    user:
      exec:
        apiVersion: client.authentication.k8s.io/v1
        command: kubectl
        args:
          [
            oidc-login, get-token,
            --oidc-issuer-url=https://idp.company.com/realms/kubernetes,
            --oidc-client-id=kubernetes,
            --oidc-client-secret=CLIENT_SECRET,
          ]
```

```yaml
# Bind an OIDC group to a ClusterRole
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: platform-admins
subjects:
  - kind: Group
    name: 'oidc:platform-admins'
    apiGroup: rbac.authorization.k8s.io
roleRef:
  kind: ClusterRole
  name: cluster-admin
  apiGroup: rbac.authorization.k8s.io
```

## RBAC: Design and Hardening

RBAC is the most frequently misconfigured Kubernetes security control. Overly permissive RBAC — wildcard verbs, `cluster-admin` for application service accounts, namespace-admin for everyone — is the most common path to cluster compromise in production environments.

### Common RBAC Roles Architecture

A tiered RBAC architecture for the enterprise:

**Cluster level** (ClusterRole + ClusterRoleBinding): `cluster-admin` (platform team break-glass only; MFA required), `cluster-viewer` (read-only across all namespaces, for auditors/monitoring), `node-admin` (node management for the SRE team), `storage-admin` (StorageClass and PV management).

**Namespace level** (Role + RoleBinding per namespace): `namespace-admin` (team tech lead, full access within the namespace), `developer` (deploy, read logs, port-forward; no secret reads), `readonly` (view all resources; no exec or port-forward), `ci-cd` (deploy only; cannot read secrets or exec).

**Service account level** (minimal per application): `app-sa` grants only what the specific application needs — for example, leader-election lease read/write only.

### RBAC Hardening Rules

- **Never use wildcards** — `verbs: ['*']` or `resources: ['*']` grants excessive permission; always enumerate specific verbs and resources.
- **Never bind `cluster-admin` to service accounts** — an application SA with `cluster-admin` is a critical risk; if the container is compromised, the attacker has full cluster access.
- **Audit regularly** — use `rbac-lookup`, `rakkess`, or `kubectl-who-can` to audit who can do what, and automate weekly audits.
- **Separate read and write** — create separate roles for read and write operations; CI/CD pipelines that only read should not have write access.
- **Use aggregated ClusterRoles** — define view/edit/admin ClusterRoles using `aggregationRule` to extend built-in roles cleanly.
- **Avoid ClusterRoleBindings for namespace work** — prefer a RoleBinding with a ClusterRole to limit scope to a specific namespace.
- **Time-limited elevated access** — use tools like Pinniped or custom webhooks to grant temporary elevated access with automatic expiry for break-glass scenarios.

### RBAC Audit Queries

```bash
# Find all subjects with cluster-admin
kubectl get clusterrolebindings -o json | python3 -c "
import json, sys
d = json.load(sys.stdin)
for item in d['items']:
    if item['roleRef']['name'] == 'cluster-admin':
        for s in item.get('subjects', []):
            print(f'{s[\"kind\"]}: {s.get(\"name\", \"?\")} in {s.get(\"namespace\", \"cluster-wide\")}')"

# Check what a service account can do
kubectl auth can-i --list \
  --as=system:serviceaccount:production:myapp-sa \
  -n production

# Find roles that allow secret access
kubectl get roles,clusterroles -A -o json | python3 -c "
import json, sys
d = json.load(sys.stdin)
for item in d['items']:
    for rule in item.get('rules', []):
        if 'secrets' in rule.get('resources', []):
            print(item['metadata']['name'])"

# Install rakkess for a detailed permissions matrix view
kubectl krew install rakkess
kubectl rakkess --sa production:myapp-sa
```

## SPIFFE and SPIRE: Workload Identity

SPIFFE (Secure Production Identity Framework For Everyone) is a CNCF graduated standard for workload identity. It assigns cryptographic identities to workloads regardless of where they run, enabling strong mutual authentication between services without managing application-level credentials.

### SPIFFE Architecture

A SPIFFE Identity has the form `spiffe://trust-domain/path`, e.g. `spiffe://company.com/ns/production/sa/api-server`. A SPIFFE Verifiable Identity Document (SVID) comes in two forms: **X.509-SVID** (an X.509 certificate with the SPIFFE URI in the SAN) and **JWT-SVID** (a JWT token whose `sub` claim is the SPIFFE ID).

SPIRE (the SPIFFE Runtime Environment) has two components. The **SPIRE Server** (control plane) maintains the trust domain and registration entries, issues SVIDs to attested workloads, and acts as a CA (self-signed or an upstream CA such as Vault PKI or AWS PCA). The **SPIRE Agent** (a DaemonSet on every node) attests node identity (via the AWS instance identity document or the Kubernetes PSAT), delivers SVIDs to workloads via a UNIX socket, and rotates SVIDs automatically before expiry. Workloads fetch their SVID via the Workload API (UNIX socket `/run/spire/sockets/agent.sock`) without any application changes — no secrets, passwords, or API keys required; SDKs are available for Go, Java, Python, Rust, and C.

### SPIRE on Kubernetes

```bash
# Install SPIRE with Helm
helm repo add spiffe https://spiffe.github.io/helm-charts/
helm install spire spiffe/spire \
  --namespace spire-system --create-namespace \
  --set global.spiffe.trustDomain=company.com \
  --set spire-server.ca.subject.country=US \
  --set spire-server.ca.subject.organization=Company \
  --set spire-server.ca.keyType=ec-p384

# Register a workload
kubectl exec -n spire-system spire-server-0 -- \
  spire-server entry create \
  -spiffeID spiffe://company.com/ns/production/sa/api-server \
  -parentID spiffe://company.com/k8s-workload-registrar/node \
  -selector k8s:ns:production \
  -selector k8s:sa:api-server
```

```yaml
# The SPIRE agent socket is projected into the Pod
volumes:
  - name: spire-agent-socket
    hostPath:
      path: /run/spire/sockets
      type: DirectoryOrCreate
containers:
  - volumeMounts:
      - name: spire-agent-socket
        mountPath: /run/spire/sockets
        readOnly: true
    env:
      - name: SPIFFE_ENDPOINT_SOCKET
        value: unix:///run/spire/sockets/agent.sock
```

## Secret Management: Vault and External Secrets

Kubernetes Secrets are insufficient for enterprise secret management: they are base64-encoded (not encrypted) by default, difficult to audit, and lack dynamic secret generation, automatic rotation, and fine-grained access policies. HashiCorp Vault and the External Secrets Operator address these gaps.

### HashiCorp Vault Architecture

Vault provides a unified secrets management platform. **Secret engines** include KV v2 (static key-value secrets with versioning), PKI (dynamic TLS certificate generation), Database (dynamic database credentials, auto-rotated), AWS/GCP/Azure (dynamic cloud credentials), Transit (encryption-as-a-service), and TOTP (time-based one-time passwords). **Auth methods** include Kubernetes (a Pod authenticates using its SA token), OIDC (human users via SSO), AWS IAM (EC2/ECS workloads), and LDAP (enterprise directory). **Policies** (HCL) provide fine-grained path-based access control with capabilities `[read, write, create, delete, list]`.

```bash
# Vault on Kubernetes (HA)
helm repo add hashicorp https://helm.releases.hashicorp.com
helm install vault hashicorp/vault \
  --namespace vault --create-namespace \
  --set server.ha.enabled=true \
  --set server.ha.replicas=3 \
  --set server.ha.raft.enabled=true \
  --set injector.enabled=true \
  --set csi.enabled=true
```

### Vault Kubernetes Auth and Dynamic Database Secrets

```bash
# Configure Vault Kubernetes auth
vault auth enable kubernetes
vault write auth/kubernetes/config \
  kubernetes_host=https://kubernetes.default.svc \
  kubernetes_ca_cert=@/var/run/secrets/kubernetes.io/serviceaccount/ca.crt

# Create a policy for an application
vault policy write myapp-policy - <<'EOF'
path "secret/data/production/myapp/*" { capabilities = ["read"] }
path "database/creds/myapp-role" { capabilities = ["read"] }
EOF

# Create a Kubernetes auth role
vault write auth/kubernetes/role/myapp \
  bound_service_account_names=myapp-sa \
  bound_service_account_namespaces=production \
  policies=myapp-policy \
  ttl=1h

# Configure dynamic PostgreSQL credentials
vault secrets enable database
vault write database/config/myapp-db \
  plugin_name=postgresql-database-plugin \
  connection_url='postgresql://vaultadmin:PASS@postgres:5432/mydb' \
  allowed_roles=myapp-role
vault write database/roles/myapp-role \
  db_name=myapp-db \
  creation_statements="CREATE ROLE ..." \
  default_ttl=1h max_ttl=24h
# Result: each Pod request gets a unique DB user that auto-expires
```

### External Secrets Operator

```yaml
apiVersion: external-secrets.io/v1beta1
kind: ClusterSecretStore
metadata:
  name: vault-backend
spec:
  provider:
    vault:
      server: https://vault.internal.corp:8200
      path: secret
      version: v2
      caBundle: BASE64_CA_CERT
      auth:
        kubernetes:
          mountPath: kubernetes
          role: external-secrets
          serviceAccountRef:
            name: external-secrets-sa
---
apiVersion: external-secrets.io/v1beta1
kind: ExternalSecret
metadata:
  name: myapp-secrets
  namespace: production
spec:
  refreshInterval: 1h
  secretStoreRef:
    kind: ClusterSecretStore
    name: vault-backend
  target:
    name: myapp-secrets
    creationPolicy: Owner
  data:
    - secretKey: api-key
      remoteRef: { key: secret/production/myapp, property: api-key }
    - secretKey: db-password
      remoteRef: { key: secret/production/myapp, property: db-password }
```

## Certificate Lifecycle: cert-manager

cert-manager is the de facto standard for TLS certificate lifecycle management in Kubernetes. It automates certificate issuance, renewal, and rotation from multiple certificate authorities: Let's Encrypt, HashiCorp Vault, AWS ACM, Venafi, and self-signed/internal CAs.

### cert-manager Architecture

The **cert-manager controller** watches Certificate resources and calls issuers; the **cert-manager webhook** validates and mutates cert-manager resources; **cert-manager cainjector** injects CA bundles into webhook configurations. **Issuers** come in two scopes: `Issuer` (namespace-scoped, issues certs for one namespace) and `ClusterIssuer` (cluster-scoped, issues certs for any namespace). Issuer types include ACME (Let's Encrypt, via HTTP-01 or DNS-01 challenge), Vault (the Vault PKI secret engine), CA (sign with a Kubernetes Secret containing a CA key/cert), Self-signed (for internal CAs), Venafi (enterprise PKI integration), and AWS ACM PCA (AWS Private Certificate Authority).

### cert-manager ClusterIssuer and Certificate

```yaml
# Internal CA ClusterIssuer (for mTLS between services)
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  name: internal-ca
spec:
  ca:
    secretName: internal-ca-key-pair  # Secret with tls.crt and tls.key
---
# Vault PKI ClusterIssuer
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  name: vault-issuer
spec:
  vault:
    server: https://vault.internal.corp:8200
    path: pki/sign/kubernetes-role
    caBundle: BASE64_VAULT_CA
    auth:
      kubernetes:
        role: cert-manager
        mountPath: /v1/auth/kubernetes
        secretRef:
          name: cert-manager-vault-token
          key: token
---
# Certificate resource (auto-renewed 30 days before expiry)
apiVersion: cert-manager.io/v1
kind: Certificate
metadata:
  name: api-server-tls
  namespace: production
spec:
  secretName: api-server-tls-secret
  duration: 2160h    # 90 days
  renewBefore: 720h  # Renew 30 days before expiry
  subject:
    organizations: [Company]
  commonName: api.production.svc.cluster.local
  dnsNames:
    - api.production.svc.cluster.local
    - api.example.com
  ipAddresses:
    - 10.96.50.100
  issuerRef:
    name: vault-issuer
    kind: ClusterIssuer
  privateKey:
    algorithm: ECDSA
    size: 384
```

## mTLS and Encryption in Transit

Mutual TLS (mTLS) provides both encryption and mutual authentication: both client and server present certificates and verify each other's identity. In Kubernetes, mTLS is implemented at different layers with different trade-offs.

### mTLS Implementation Options

| Approach | Where Implemented | Operation | Overhead | Best For |
|---|---|---|---|---|
| Istio sidecar mTLS | Envoy sidecar proxy | Automatic; app unaware | Medium (sidecar CPU) | Full service mesh |
| Linkerd mTLS | Rust micro-proxy | Automatic; app unaware | Low | Simple mTLS |
| Cilium mTLS | eBPF + WireGuard | Transparent L3 encryption | Low | Network-level encryption |
| SPIFFE/SPIRE + app SDK | Application code | App manages SVID | Highest control | Zero trust native apps |
| cert-manager + app | Application code | Manual cert loading | App manages rotation | Legacy apps with TLS support |

### Istio PeerAuthentication — Strict mTLS

```yaml
# Enforce strict mTLS for all services in a namespace
apiVersion: security.istio.io/v1
kind: PeerAuthentication
metadata:
  name: default
  namespace: production
spec:
  mtls:
    mode: STRICT
    # STRICT: all connections must use mTLS
    # PERMISSIVE: accept both mTLS and plaintext
    # DISABLE: plaintext only
---
# Enforce mTLS cluster-wide
apiVersion: security.istio.io/v1
kind: PeerAuthentication
metadata:
  name: default
  namespace: istio-system  # Root namespace = cluster-wide
spec:
  mtls:
    mode: STRICT
```

```bash
# Verify mTLS is working
istioctl authn tls-check ...svc.cluster.local
# Should show: OK / mTLS
```

## Pod Security: Standards, Contexts, Profiles

Hardening Pod security reduces the blast radius if a container is compromised. Multiple controls work together: Pod Security Standards (namespace-level policy), `securityContext` (per-Pod/container), seccomp (syscall filtering), and AppArmor/SELinux (mandatory access control).

### Pod Security Standards (PSS)

| Control | Privileged | Baseline | Restricted |
|---|---|---|---|
| Privileged containers | Allowed | Blocked | Blocked |
| Host namespaces (PID, Net, IPC) | Allowed | Blocked | Blocked |
| HostPath volumes | Allowed | Blocked | Blocked |
| runAsRoot | Allowed | Allowed | Must be False |
| Capabilities | Allowed | Only safe subset | Drop ALL; no adds except NET_BIND_SERVICE |
| seccompProfile | Not required | Not required | RuntimeDefault or Localhost required |
| allowPrivilegeEscalation | Allowed | Allowed | Must be False |
| readOnlyRootFilesystem | Not required | Not required | Required |
| Volume types | Any | Limited set | ConfigMap, Secret, PVC, projected, emptyDir |

### Complete Restricted Pod Security Context

```yaml
# Fully compliant with PSS Restricted
apiVersion: v1
kind: Pod
spec:
  securityContext:
    runAsNonRoot: true
    runAsUser: 10001
    runAsGroup: 10001
    fsGroup: 10001
    fsGroupChangePolicy: OnRootMismatch
    seccompProfile:
      type: RuntimeDefault
  containers:
    - name: app
      securityContext:
        allowPrivilegeEscalation: false
        readOnlyRootFilesystem: true
        runAsNonRoot: true
        capabilities:
          drop: [ALL]
        seccompProfile:
          type: RuntimeDefault
      # Writable paths via emptyDir
      volumeMounts:
        - { name: tmp, mountPath: /tmp }
        - { name: cache, mountPath: /app/cache }
  volumes:
    - { name: tmp, emptyDir: { medium: Memory } }
    - { name: cache, emptyDir: {} }
```

## Related

- [K8s Handbook Part 8: Security (Part 2)](parts/41-k8s-handbook-part8-security-part2.md) — policy-as-code, supply chain security, runtime security, confidential computing, hardening checklist, compliance mapping, incident response, and exercises
