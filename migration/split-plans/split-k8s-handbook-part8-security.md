# Split Plan: K8s Handbook Part 8 — Security

**Source:** `/workspace/knowledge-docs/docs/cloud-platforms/kubernetes/K8s_Handbook_Part8_Security.md` (~4,329 words body)

**Reason:** Word count exceeds guide doc_type cap (2600 words hard cap)

## Split Boundary

**Part 1 (Main):** `docs/platforms/41-k8s-handbook-part8-security.md`
- Source: Chapters 1–9 (Enterprise Security Model, Zero Trust Architecture, Authentication, RBAC, SPIFFE/SPIRE, Secret Management: Vault, cert-manager, mTLS, Pod Security)
- Content: the Kubernetes threat model and 8-layer security control stack, Zero Trust principles and implementation roadmap, authentication method comparison and OIDC integration, tiered RBAC architecture/hardening rules/audit queries, SPIFFE/SPIRE workload identity, HashiCorp Vault architecture/Kubernetes auth/dynamic secrets, External Secrets Operator, cert-manager architecture and ClusterIssuer/Certificate examples, mTLS implementation options and Istio strict-mTLS PeerAuthentication, Pod Security Standards and a fully-compliant Restricted securityContext

**Part 2 (Supplementary):** `docs/platforms/parts/41-k8s-handbook-part8-security-part2.md`
- Source: Chapters 10–17 (Policy-as-Code: OPA Gatekeeper and Kyverno, Supply Chain Security, Runtime Security: Falco and Tetragon, Confidential Containers, Security Hardening Checklist, Compliance Mapping, Security Incident Response, Hands-On Exercises)
- Content: OPA Gatekeeper Rego ConstraintTemplates and Kyverno YAML-native policies, the end-to-end supply chain security pipeline, Falco runtime detection rules and alert routing, confidential computing hardware and the Confidential Containers (CoCo) project, a control-plane/node/workload/RBAC/network hardening checklist, compliance mapping across NIST/CIS/SOC2/PCI/HIPAA/EU AI Act, a security incident response playbook, 2 hands-on exercises

## Source-quality notes (converted-pdf artifacts fixed during migration)

- Numerous flattened multi-line YAML/shell blocks reconstructed into properly line-broken fenced blocks (OIDC kube-apiserver config, RBAC tiered architecture and audit queries, SPIRE Helm install/registration, Vault architecture/auth/dynamic secrets, External Secrets Operator, cert-manager ClusterIssuer/Certificate, Istio PeerAuthentication, Pod Security Restricted context, Gatekeeper/Kyverno policies, Falco rules, and both exercises).
- No content-loss (heading-then-nothing) artifacts were found in this source; all chapters retained their body text.

## Navigation

- Part 1 ends with a pointer to Part 2 (policy-as-code, supply chain, runtime security, confidential computing, hardening checklist, compliance, incident response, exercises).
- Topic ID: both parts share the `k8s-handbook-part8-security` topic family.
- Part 1 is canonical (`topic_id: k8s-handbook-part8-security`).
- Part 2 uses `topic_id: k8s-handbook-part8-security-part2`, `supersedes: []` (Part 1 carries the supersedes entry).
