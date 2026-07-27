---
title: "K8s Handbook Part 3 (Part 3: SBOM, SLSA, Vulnerability Scanning & Runtime Security)"
doc_type: guide
domain: platforms
status: current
topic_id: k8s-handbook-part3-containers-part3
last_reviewed: 2026-07-27
maturity: practitioner
supersedes: []
tags:
  - kubernetes
  - sbom
  - slsa
  - vulnerability-scanning
  - falco
  - tetragon
covers_version: "2025-2026 edition"
---

*Part 3 of 3 of [K8s Handbook Part 3: Containers](../36-k8s-handbook-part3-containers.md).*

## Chapter 10: SBOM Generation and Management

### Why SBOMs Are Now Mandatory

A Software Bill of Materials (SBOM) is a machine-readable inventory of all software components in an application or container image: package names, versions, checksums, licenses, and dependency relationships. Regulatory drivers have made SBOMs mandatory in many contexts:

- **US EO 14028 (2021)**: Executive Order on Improving Cybersecurity requires SBOMs for software sold to US federal government agencies.
- **EU Cyber Resilience Act (2024)**: Requires SBOMs for digital products sold in the EU market; includes container-based software products.
- **NIST SP 800-218**: Secure Software Development Framework includes SBOM generation as a recommended practice for secure software supply chains.
- **Financial services regulators**: OCC, FFIEC, and PRA guidance increasingly references SBOMs as part of third-party software risk management.

### SBOM Formats

| Format | Maintained By | Output Formats | Ecosystem Adoption |
| --- | --- | --- | --- |
| SPDX 2.3 | Linux Foundation / ISO 5962 | JSON, RDF, YAML, tag-value | GitHub, NTIA, many scanners |
| CycloneDX 1.6 | OWASP | JSON, XML, Protobuf | Syft, Grype, Trivy, OWASP |
| SWID | ISO/IEC 19770-2 | XML | Enterprise software assets, less common |

**Generating and attaching SBOMs:**

```bash
# Generate SBOM with Syft (supports SPDX and CycloneDX):
syft scan harbor.internal.corp/myapp:v1.2.3 \
  -o cyclonedx-json=sbom.cdx.json \
  -o spdx-json=sbom.spdx.json

# Attach SBOM as OCI attestation (Cosign):
cosign attest \
  --yes \
  --predicate sbom.cdx.json \
  --type cyclonedx \
  harbor.internal.corp/myapp@sha256:DIGEST

# Verify and retrieve SBOM attestation:
cosign verify-attestation \
  --type cyclonedx \
  --certificate-identity-regexp 'github.com/myorg' \
  --certificate-oidc-issuer 'https://token.actions.githubusercontent.com' \
  harbor.internal.corp/myapp@sha256:DIGEST \
  | jq -r '.payload' | base64 -d | jq '.predicate'

# Scan SBOM for known CVEs (without re-scanning image):
grype sbom:sbom.cdx.json --fail-on critical
```

**SBOM in Kubernetes admission control.** SBOMs enable policy decisions at admission time — a Kyverno policy requiring SBOM attestation:

```yaml
apiVersion: kyverno.io/v1
kind: ClusterPolicy
metadata:
  name: require-sbom-attestation
spec:
  validationFailureAction: Enforce
  rules:
    - name: check-sbom-exists
      match:
        resources: { kinds: [Pod] }
      verifyImages:
        - imageReferences: ['harbor.internal.corp/*']
          attestations:
            - type: https://cyclonedx.org/bom
              attestors:
                - entries:
                    - keyless:
                        subject: https://github.com/myorg/*
                        issuer: https://token.actions.githubusercontent.com
```

## Chapter 11: SLSA Framework for Container Builds

### SLSA Overview

Supply-chain Levels for Software Artifacts (SLSA, pronounced "salsa") defines a progressive security maturity model for software build and distribution. Each level adds requirements that protect against increasingly sophisticated attacks on the build process itself.

| Level | Key Requirements | Protects Against | Implementation |
| --- | --- | --- | --- |
| SLSA 0 | None | Nothing | Ad-hoc local builds |
| SLSA 1 | Build process generates provenance | Accidental build tampering | GitHub Actions + provenance generator |
| SLSA 2 | Hosted build, signed provenance by build service | Unauthorized build changes | GitHub Actions SLSA builder action |
| SLSA 3 | Hardened builds: non-falsifiable provenance, isolated environment | Compromised CI runner | Ephemeral isolated builders, reproducible builds |

**SLSA provenance — what it contains.** SLSA provenance is a signed attestation describing how an artifact was built (in-toto predicate format):

```json
{
  "buildType": "https://slsa.dev/provenance/v1",
  "builder": { "id": "https://github.com/actions/runner/releases/tag/v2.304.0" },
  "buildDefinition": {
    "externalParameters": {
      "workflow": ".github/workflows/build.yml",
      "ref": "refs/tags/v1.2.3",
      "repository": "https://github.com/myorg/myapp"
    }
  },
  "runDetails": {
    "metadata": {
      "invocationId": "https://github.com/myorg/myapp/actions/runs/12345",
      "startedOn": "2025-06-01T12:00:00Z",
      "finishedOn": "2025-06-01T12:04:23Z"
    }
  }
}
```

```bash
# Verify SLSA provenance:
slsa-verifier verify-image \
  harbor.internal.corp/myapp@sha256:DIGEST \
  --source-uri github.com/myorg/myapp \
  --source-tag v1.2.3 \
  --slsa-verifier-version v2.4.1
```

**Tekton Chains — SLSA provenance in Kubernetes.** Tekton Chains is a Kubernetes-native solution that automatically generates SLSA provenance for every Tekton Pipeline build, signs it with Cosign, and stores it as an OCI attestation — enabling SLSA L2-L3 on-premises without dependency on GitHub Actions:

```yaml
# Tekton Chains configuration for SLSA provenance:
apiVersion: v1
kind: ConfigMap
metadata:
  name: chains-config
  namespace: tekton-chains
data:
  artifacts.oci.format: slsa/v1
  artifacts.oci.storage: oci
  signers.x509.fulcio.address: https://fulcio.internal.corp
  transparency.url: https://rekor.internal.corp
  # Automatically signs every TaskRun output image
  artifacts.pipelinerun.format: slsa/v1
  artifacts.pipelinerun.storage: oci,gcs
```

## Chapter 12: Vulnerability Scanning in Depth

### Scanning Architecture for Kubernetes

Vulnerability scanning must occur at multiple stages of the container lifecycle, not just at build time. CVEs are discovered continuously; an image clean at build time may be critical within weeks.

| Stage | When | Tools | Action on Critical CVE |
| --- | --- | --- | --- |
| Build time | Every CI build | Trivy, Grype, Snyk | Fail build; block registry push |
| Registry admission | On push to registry | Harbor + Trivy, ECR Inspector, GAR scanning | Block tag creation; alert security team |
| Pre-deployment | On every K8s admission | Kyverno image rules, OPA | Reject Pod; prevent deployment |
| Continuous (runtime) | Daily/weekly rescan of running images | Harbor scheduled scan, Anchore, Prisma | Alert; schedule forced rollout |
| SBOM-based rescan | On new CVE database update | Grype against stored SBOMs | Alert; correlate to running workloads |

**Trivy — production scanning configuration:**

```bash
# Scan image with full reporting:
trivy image \
  --severity CRITICAL,HIGH \
  --exit-code 1 \
  --format sarif \
  --output trivy-results.sarif \
  harbor.internal.corp/myapp:v1.2.3

# Scan with ignorefile (accepted risk):
trivy image \
  --ignorefile .trivyignore \
  --severity CRITICAL \
  --exit-code 1 \
  harbor.internal.corp/myapp:v1.2.3

# .trivyignore format:
# CVE-2024-12345
# accepted: no fix available, mitigated by network policy
# CVE-2024-67890
# accepted: component not reachable, expires 2025-01-01

# Scan filesystem (for CI before image build):
trivy fs --security-checks vuln,secret,config .

# Scan Kubernetes cluster for vulnerable images:
trivy k8s --report summary cluster
```

### Vulnerability Management Policy

| Severity | SLA to Patch | CI Policy | Production Policy |
| --- | --- | --- | --- |
| Critical (CVSS 9.0+) | 24–72 hours | Block build immediately | Alert + forced rollout within 24h |
| High (CVSS 7.0–8.9) | 7–14 days | Block build (configurable) | Alert + scheduled rollout |
| Medium (CVSS 4.0–6.9) | 30–90 days | Warn; track in ticket | Monitor; next release cycle |
| Low (CVSS 0.1–3.9) | Next major release | Log only | Track in backlog |
| No fix available | Accept + document | Allow with justification in `.trivyignore` | Mitigate via network policy |

## Chapter 13: Runtime Container Security

### Defence in Depth for Running Containers

Runtime security addresses threats that persist after an image has been scanned and deployed: zero-day exploits, configuration drift, insider threats, and supply chain attacks not yet known to vulnerability databases. Multiple independent security layers provide defence in depth.

### Falco — Runtime Threat Detection

Falco (CNCF graduated) detects anomalous behaviour in running containers by monitoring system calls via eBPF probes. Unlike image scanning (static), Falco observes actual runtime behaviour.

```yaml
# Example Falco rules for Kubernetes workloads:

# Rule 1: Shell spawned in container (highly suspicious)
- rule: Shell spawned in container
  desc: A shell was spawned in a container (possible compromise)
  condition: >
    spawned_process and container and
    proc.name in (bash, sh, zsh, fish) and
    not proc.pname in (containerd-shim, runc)
  output: "Shell spawned (user=%user.name cmd=%proc.cmdline container=%container.id)"
  priority: WARNING
  tags: [container, shell, mitre_execution]

# Rule 2: Unexpected network connection from a known-internal service
- rule: Outbound connection from database container
  desc: Database containers should not initiate outbound connections
  condition: >
    outbound and container and
    k8s.pod.label.app in (postgres, mysql, redis) and
    fd.sport != 5432 and fd.sport != 3306
  output: "DB container unexpected outbound (dest=%fd.rip:%fd.rport)"
  priority: CRITICAL

# Rule 3: Sensitive file access
- rule: Read sensitive file in container
  condition: >
    open_read and container and
    fd.name in (/etc/shadow, /etc/passwd)
  output: "Sensitive file read (file=%fd.name container=%container.id)"
  priority: WARNING
```

**Falco deployment in Kubernetes:**

```bash
# Install Falco with eBPF probe (preferred; no kernel module required):
helm repo add falcosecurity https://falcosecurity.github.io/charts
helm install falco falcosecurity/falco \
  --namespace falco --create-namespace \
  --set driver.kind=ebpf \
  --set falcosidekick.enabled=true \
  --set falcosidekick.config.slack.webhookurl=https://hooks.slack.com/... \
  --set falcosidekick.config.pagerduty.routingKey=xxxx
```

### Tetragon — eBPF Security Enforcement

Tetragon (Cilium project) goes beyond Falco's detection-only model by enforcing security policy in the kernel via eBPF — blocking malicious actions before they complete, not just alerting after the fact.

```yaml
# Tetragon TracingPolicy to block /bin/bash execution in production pods:
apiVersion: cilium.io/v1alpha1
kind: TracingPolicy
metadata:
  name: block-shell-execution
spec:
  kprobes:
    - call: sys_execve
      syscall: true
      args:
        - index: 0
          type: string
      selectors:
        - matchArgs:
            - index: 0
              operator: Equal
              values: ["/bin/sh", "/bin/bash", "/usr/bin/bash"]
          matchNamespaces:
            - namespace: Mnt
              operator: NotIn
              values: ["host_mnt_ns_id"]
          matchActions:
            - action: Sigkill   # Kill the process attempting to exec shell
```

### Security Context Best Practices

Complete hardened Pod security context (Pod Security Standards: Restricted):

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: hardened-app
  annotations:
    container.apparmor.security.beta.kubernetes.io/app: runtime/default
spec:
  securityContext:
    runAsNonRoot: true
    runAsUser: 1000
    runAsGroup: 1000
    fsGroup: 1000
    seccompProfile:
      type: RuntimeDefault
  containers:
    - name: app
      image: harbor.internal.corp/myapp@sha256:DIGEST
      securityContext:
        allowPrivilegeEscalation: false
        readOnlyRootFilesystem: true
        capabilities:
          drop: [ALL]
        seccompProfile:
          type: RuntimeDefault
      volumeMounts:
        - name: tmp
          mountPath: /tmp        # writable tmpfs for temp files
        - name: cache
          mountPath: /app/cache  # writable cache directory
  volumes:
    - name: tmp
      emptyDir: { medium: Memory }
    - name: cache
      emptyDir: {}
```

## Chapter 14: Container Anti-Patterns and Remediation

**Running containers as root.** Problem: container process runs as UID 0. If the container escapes (via kernel exploit or misconfiguration), the attacker has root on the node. Solution: set `runAsNonRoot: true` and `runAsUser: 1000+` in securityContext. Build images with the `USER` instruction. Enforce via Pod Security Standards Restricted.

**Storing secrets in environment variables.** Problem: environment variables are visible in `docker inspect`, `kubectl describe pod`, and any process that can read `/proc/self/environ`. Secrets in env vars are also logged by many frameworks. Solution: use Kubernetes Secrets mounted as files (not env vars where possible). Use External Secrets Operator syncing from Vault. Mount secrets to tmpfs paths (`/run/secrets/`).

**Mutable container images (tag-based deployments).** Problem: deploying with `:latest` or `:v1.2` tags. Tags are mutable pointers; the underlying image can change without your awareness, enabling supply chain substitution attacks. Solution: always pin images by SHA-256 digest in production PodSpecs. Use Kyverno `mutateDigest` to automatically resolve tags to digests at admission.

**Privileged containers.** Problem: `spec.containers[].securityContext.privileged: true` gives the container full host access — effectively root on the node. Used (incorrectly) when developers need capabilities they cannot get another way. Solution: identify the specific capability needed; add only that capability. For DaemonSet node agents, use `hostPID`/`hostNetwork` minimally. Enforce no-privileged via Pod Security Standards.

**Mounting the Docker socket.** Problem: mounting `/var/run/docker.sock` into a container gives it full control over the Docker daemon — and therefore all containers on the node. Used in CI/CD Docker-in-Docker patterns. Solution: use Kaniko, BuildKit (rootless), or Tekton for in-cluster builds. Use external CI (GitHub Actions) for image builds. Never mount the Docker socket in production workloads.

**Single large container instead of microservices.** Problem: running a large application as a single container misses K8s benefits: independent scaling, independent deployment, independent failure domains. Solution: decompose over time using the Strangler Fig pattern. Start with multi-container Pods (sidecar pattern) before full decomposition. Not every app benefits from decomposition — assess ROI.

**Ignoring ephemeral storage limits.** Problem: applications write large files to the container filesystem or `emptyDir` without limits, causing node disk exhaustion — a node-level failure affecting all Pods on the node. Solution: set `resources.limits.ephemeral-storage`. Use PVCs for large/persistent writes. Mount `emptyDir` with `sizeLimit` for temporary storage. Monitor node disk usage with Prometheus `node_filesystem_avail_bytes`.

## Chapter 15: Hands-On Exercises

### Exercise 3.1 — Multi-Stage Build Optimisation

Compare image sizes between naive and optimised build strategies:

```bash
# 1. Build a naive single-stage Python image:
cat > Dockerfile.naive << 'EOF'
FROM python:3.12
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
CMD ["python", "app.py"]
EOF
docker build -t myapp:naive -f Dockerfile.naive .
docker images myapp:naive   # typically 1.0-1.5 GB

# 2. Build an optimised distroless multi-stage image:
cat > Dockerfile.optimised << 'EOF'
FROM python:3.12-slim AS builder
WORKDIR /build
COPY requirements.txt .
RUN pip install --prefix=/install -r requirements.txt

FROM gcr.io/distroless/python3-debian12:nonroot
COPY --from=builder /install /usr/local
COPY app.py /app/app.py
WORKDIR /app
USER nonroot:nonroot
CMD ["app.py"]
EOF
docker build -t myapp:optimised -f Dockerfile.optimised .
docker images myapp:optimised   # typically 60-100 MB

# 3. Inspect layers with dive:
docker run --rm -it -v /var/run/docker.sock:/var/run/docker.sock \
  wagoodman/dive:latest myapp:optimised
```

### Exercise 3.2 — Image Signing with Cosign

Sign a container image and enforce signature verification in Kubernetes:

```bash
# 1. Install cosign:
brew install cosign   # macOS
# or:
go install github.com/sigstore/cosign/v2/cmd/cosign@latest

# 2. Sign with a local key (for lab; use keyless in production):
cosign generate-key-pair   # Creates cosign.key and cosign.pub

# 3. Push and sign an image:
docker tag myapp:optimised ttl.sh/myapp:1h   # ttl.sh = ephemeral public registry
docker push ttl.sh/myapp:1h
IMAGE_DIGEST=$(docker inspect --format='{{index .RepoDigests 0}}' ttl.sh/myapp:1h)
cosign sign --key cosign.key $IMAGE_DIGEST

# 4. Verify the signature:
cosign verify --key cosign.pub $IMAGE_DIGEST

# 5. (Advanced) Scan signature in Kubernetes with Kyverno:
# Install Kyverno, apply the ClusterPolicy from Chapter 9,
# then try deploying a signed vs unsigned image and observe enforcement
```

### Exercise 3.3 — Supply Chain Security Audit

Perform a supply chain security audit of a production image:

```bash
# 1. Scan for CVEs:
trivy image nginx:alpine

# 2. Generate SBOM:
syft nginx:alpine -o cyclonedx-json=nginx-sbom.cdx.json
cat nginx-sbom.cdx.json | jq '.components | length'   # Count packages in the image

# 3. Check for secrets in image:
trivy image --security-checks secret nginx:alpine

# 4. Inspect image configuration for security issues:
trivy image --security-checks config nginx:alpine

# 5. Verify OCI manifest structure:
crane manifest nginx:alpine | jq .
crane ls nginx   # list available tags

# 6. Check if image is signed:
cosign verify --certificate-identity-regexp . \
  --certificate-oidc-issuer-regexp . \
  nginx:alpine 2>&1 | head -5
# nginx:alpine is NOT signed -- demonstrates why an internal mirror matters
```

## Related

- [Part 1: Container Stack, Docker Architecture & OCI Runtimes](../36-k8s-handbook-part3-containers.md)
- [Part 2: Image Building, Registry, Optimisation & Supply Chain](36-k8s-handbook-part3-containers-part2.md)
