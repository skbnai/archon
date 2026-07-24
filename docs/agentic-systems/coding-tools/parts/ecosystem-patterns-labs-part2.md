---
title: "Hidden Features, Labs & Interview Q&A (Part 2)"
doc_type: guide
domain: agentic-systems
topic_id: ecosystem-patterns-labs-part2
status: current
date_published: 2026-07-24
last_reviewed: 2026-07-24
supersedes: []
tags:
  - coding-tools
  - labs
  - patterns
---

# Hidden Features, Labs & Interview Q&A (Part 2)

## Part 20 — Hidden GitHub Gems

### 1. Issue Forms

Issue Forms (YAML-based) replace free-text issue templates with structured forms, enabling consistent, machine-readable bug reports and feature requests.

`.github/ISSUE_TEMPLATE/bug_report.yml`:

```yaml
name: Bug Report
description: Report a bug
title: "[Bug]: "
labels: ["bug", "triage"]
assignees: ["platform-team"]
body:
  - type: markdown
    value: "Thanks for taking the time to fill this out!"
  - type: input
    id: version
    label: Version
    placeholder: "e.g., 2.1.0"
    validations:
      required: true
  - type: textarea
    id: reproduction
    label: Steps to Reproduce
    value: |
      1. Go to '...'
      2. Click on '...'
    validations:
      required: true
  - type: dropdown
    id: severity
    label: Severity
    options: [Critical, High, Medium, Low]
    validations:
      required: true
  - type: checkboxes
    id: terms
    label: Checklist
    options:
      - label: I have searched for existing issues
        required: true
```

### 2. Saved Replies

GitHub Saved Replies (github.com/settings/replies) are pre-written comment templates for common review responses — reduce repetition in code review.

- 'LGTM - Approve' for standard approvals
- 'Needs tests' for missing test coverage
- 'Please rebase on main' for outdated branches
- 'Security review needed' for sensitive changes

### 3. GitHub Search Power Features

Advanced search syntax:

```bash
is:pr is:open review:required org:myorg        # All PRs awaiting review
is:issue is:open label:bug created:>2024-01-01 # Recent bugs
is:pr merged:>2024-01-01 author:@me            # Your recent merges
repo:myorg/api is:pr is:merged "squash"        # Squash-merged PRs

path:.github/workflows language:YAML           # Find workflow files
filename:CODEOWNERS                            # Find CODEOWNERS files
is:secret-scanning-alert state:open            # Open secret alerts

# Code search (for GHEC/GitHub.com):
org:myorg language:python "import boto3"        # Find boto3 usage
org:myorg "GITHUB_TOKEN" path:.github           # Token usage in workflows
org:myorg extension:tf "azurerm"                # Terraform Azure files
```

### 4. Dependency Review Action

Block PRs that introduce vulnerable dependencies:

```yaml
name: Dependency Review
on:
  pull_request:
    branches: [main]
jobs:
  dependency-review:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/dependency-review-action@v4
        with:
          fail-on-severity: moderate
          deny-licenses: GPL-3.0, AGPL-3.0  # Block copyleft licenses
          allow-ghsas: GHSA-xxxx-xxxx-xxxx  # Allowlist known FPs
          comment-summary-in-pr: true
```

### 5. Actions Artifact Attestations

Generate cryptographic attestation for build artifacts:

```yaml
name: Build with Attestation
on:
  push:
    tags: ['v*']
jobs:
  build:
    permissions:
      id-token: write      # For OIDC signing
      contents: write
      attestations: write  # For artifact attestation
    steps:
      - uses: actions/checkout@v4
      - name: Build container image
        id: build
        run: |
          docker build -t ghcr.io/myorg/app:${{ github.sha }} .
          docker push ghcr.io/myorg/app:${{ github.sha }}
          DIGEST=$(docker inspect ghcr.io/myorg/app:${{ github.sha }} \
            --format '{{index .RepoDigests 0}}' | cut -d@ -f2)
          echo "digest=$DIGEST" >> $GITHUB_OUTPUT
      - name: Attest container image
        uses: actions/attest-build-provenance@v1
        with:
          subject-name: ghcr.io/myorg/app
          subject-digest: ${{ steps.build.outputs.digest }}
          push-to-registry: true
```

Verify attestation:

```bash
gh attestation verify ghcr.io/myorg/app:latest \
  --owner myorg
```

### 6. GitHub Search Syntax for Analytics (GraphQL)

Get comprehensive PR metrics via GraphQL:

```graphql
query PRMetrics($owner: String!, $repo: String!, $since: DateTime!) {
  repository(owner: $owner, name: $repo) {
    pullRequests(
      first: 100,
      states: [MERGED],
      orderBy: {field: UPDATED_AT, direction: DESC}
    ) {
      nodes {
        number
        title
        createdAt
        mergedAt
        author { login }
        additions
        deletions
        changedFiles
        reviewDecision
        timelineItems(first: 50, itemTypes: [REVIEW_REQUESTED_EVENT, PULL_REQUEST_REVIEW]) {
          nodes {
            ... on PullRequestReview {
              submittedAt
              state
              author { login }
            }
          }
        }
      }
    }
  }
}

# Calculate lead time, cycle time, review time from this data
```

## Part 21 — Hands-On Labs

## Lab 1: Multi-Stage CI Pipeline

Build a production-grade CI pipeline with parallel jobs, matrix testing, coverage reporting, and artifact promotion.

Lab 1: Multi-Stage CI Pipeline — Complete workflow implementing all best practices:

```yaml
name: Multi-Stage CI
on:
  push:
    branches: [main, 'release/**']
  pull_request:
    branches: [main]
concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: ${{ github.ref != 'refs/heads/main' }}
jobs:
  # Stage 1: Fast feedback (parallel)
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: {python-version: "3.11", cache: pip}
      - run: pip install ruff mypy
      - run: ruff check . && mypy src/
  # Stage 2: Test matrix
  test:
    needs: lint
    strategy:
      fail-fast: false
      matrix:
        python: ["3.10", "3.11", "3.12"]
        os: [ubuntu-latest, windows-latest]
    runs-on: ${{ matrix.os }}
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python }}
          cache: pip
      - run: pip install -r requirements.txt -r requirements-dev.txt
      - name: Run tests with coverage
        run: pytest tests/unit/ -n auto --cov=src --cov-report=xml
      - uses: codecov/codecov-action@v4
        if: matrix.python == '3.11' && matrix.os == 'ubuntu-latest'
  # Stage 3: Security
  security:
    needs: lint
    permissions:
      security-events: write
      contents: read
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: github/codeql-action/init@v3
        with: {languages: python, queries: security-extended}
      - uses: github/codeql-action/autobuild@v3
      - uses: github/codeql-action/analyze@v3
  # Stage 4: Build (only on main/release)
  build:
    if: github.ref == 'refs/heads/main' || startsWith(github.ref, 'refs/heads/release/')
    needs: [test, security]
    permissions:
      contents: read
      packages: write
      id-token: write
      attestations: write
    outputs:
      digest: ${{ steps.push.outputs.digest }}
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}
      - uses: docker/build-push-action@v5
        id: push
        with:
          push: true
          tags: ghcr.io/${{ github.repository }}:${{ github.sha }}
          cache-from: type=gha
          cache-to: type=gha,mode=max
      - uses: actions/attest-build-provenance@v1
        with:
          subject-name: ghcr.io/${{ github.repository }}
          subject-digest: ${{ steps.push.outputs.digest }}
          push-to-registry: true
```

## Lab 2: Kubernetes Deployment with OIDC Auth

Deploy to EKS with OIDC (no stored secrets):

```yaml
deploy-staging:
  needs: build
  runs-on: ubuntu-latest
  environment:
    name: staging
    url: https://staging.api.example.com
  permissions:
    id-token: write
    contents: read
  steps:
    - uses: actions/checkout@v4
    # OIDC → AWS credentials (no stored secrets!)
    - uses: aws-actions/configure-aws-credentials@v4
      with:
        role-to-assume: arn:aws:iam::123456789:role/github-staging-deploy
        aws-region: us-east-1
    # Update kubeconfig for EKS
    - run: aws eks update-kubeconfig --name staging-cluster --region us-east-1
    # Deploy with Helm
    - name: Deploy with Helm
      run: |
        helm upgrade --install api-service ./charts/api-service \
          --namespace staging \
          --set image.repository=ghcr.io/${{ github.repository }} \
          --set image.tag=${{ github.sha }} \
          --set image.digest=${{ needs.build.outputs.digest }} \
          --wait \
          --timeout 5m \
          --atomic  # Rollback on failure
    # Smoke test
    - name: Smoke test
      run: |
        kubectl rollout status deployment/api-service -n staging --timeout=120s
        curl -f https://staging.api.example.com/health | jq .

deploy-production:
  needs: deploy-staging
  runs-on: ubuntu-latest
  environment:
    name: production  # Has required reviewers + 10min wait timer
  permissions:
    id-token: write
    contents: read
  steps:
    - uses: aws-actions/configure-aws-credentials@v4
      with:
        role-to-assume: arn:aws:iam::123456789:role/github-prod-deploy
        aws-region: us-east-1
    - run: aws eks update-kubeconfig --name prod-cluster --region us-east-1
    - run: |
        helm upgrade api-service ./charts/api-service \
          --namespace production \
          --set image.tag=${{ github.sha }} \
          --wait --atomic
```

## Lab 3: ARC Ephemeral Runners on Kubernetes

Complete ARC setup:

```bash
# Step 1: Install cert-manager (ARC dependency):
kubectl apply -f \
  https://github.com/cert-manager/cert-manager/releases/download/v1.14.0/cert-manager.yaml

# Step 2: Install ARC:
helm install arc \
  --namespace arc-systems \
  --create-namespace \
  oci://ghcr.io/actions/actions-runner-controller-charts/gha-runner-scale-set-controller

# Step 3: Create GitHub App credentials secret:
kubectl create secret generic controller-manager \
  --namespace arc-systems \
  --from-literal=github_app_id=$APP_ID \
  --from-literal=github_app_installation_id=$INSTALL_ID \
  --from-literal=github_app_private_key="$(cat private-key.pem)"

# Step 4: Deploy RunnerScaleSet:
helm install arc-runner-set \
  --namespace arc-runners \
  --create-namespace \
  oci://ghcr.io/actions/actions-runner-controller-charts/gha-runner-scale-set \
  --set githubConfigUrl="https://github.com/myorg" \
  --set githubConfigSecret=controller-manager \
  --set minRunners=0 \
  --set maxRunners=20 \
  --set runnerScaleSetName=arc-runner-set

# Step 5: Use in workflow:
# runs-on: arc-runner-set
```

## Lab 4: Complete Supply Chain Security

SLSA + Cosign + SBOM + Attestation:

```yaml
name: Secure Release Pipeline
on:
  push:
    tags: ['v*.*.*']
jobs:
  build-and-sign:
    permissions:
      contents: write
      packages: write
      id-token: write
      attestations: write
    outputs:
      digest: ${{ steps.build.outputs.digest }}
      version: ${{ steps.version.outputs.version }}
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with: {fetch-depth: 0}
      - name: Get version
        id: version
        run: echo "version=${GITHUB_REF_NAME#v}" >> $GITHUB_OUTPUT
      # Install signing tools
      - uses: sigstore/cosign-installer@v3
      - uses: anchore/sbom-action/download-syft@v0
      # Build multi-arch image
      - uses: docker/setup-buildx-action@v3
      - uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}
      - uses: docker/build-push-action@v5
        id: build
        with:
          platforms: linux/amd64,linux/arm64
          push: true
          tags: |
            ghcr.io/${{ github.repository }}:${{ github.ref_name }}
            ghcr.io/${{ github.repository }}:latest
      # Sign the image with Sigstore (keyless)
      - name: Sign image
        run: |
          cosign sign --yes \
            ghcr.io/${{ github.repository }}@${{ steps.build.outputs.digest }}
      # Generate SBOM
      - name: Generate SBOM
        uses: anchore/sbom-action@v0
        with:
          image: ghcr.io/${{ github.repository }}@${{ steps.build.outputs.digest }}
          artifact-name: sbom.spdx.json
          output-file: /tmp/sbom.spdx.json
      # Attach SBOM to image
      - name: Attest SBOM
        run: |
          cosign attest --yes \
            --predicate /tmp/sbom.spdx.json \
            --type spdxjson \
            ghcr.io/${{ github.repository }}@${{ steps.build.outputs.digest }}
      # GitHub attestation (SLSA provenance)
      - uses: actions/attest-build-provenance@v1
        with:
          subject-name: ghcr.io/${{ github.repository }}
          subject-digest: ${{ steps.build.outputs.digest }}
          push-to-registry: true
      # Create GitHub Release with SBOM
      - uses: softprops/action-gh-release@v2
        with:
          generate_release_notes: true
          files: /tmp/sbom.spdx.json
```

## Lab 5: Enterprise CI/CD Platform Design

This lab synthesizes all concepts into an enterprise-grade platform design supporting 500+ repositories, thousands of developers, governance, security, and operational excellence.

Enterprise CI/CD Platform — Architecture Overview:

Repository structure:

```
github.com/myenterprise/
  platform-workflows/      → Reusable workflow library
  platform-actions/        → Composite action library
  platform-policies/       → Policy-as-code (OPA/Rego)
  backstage/               → Internal developer portal
  k8s-platform/            → GitOps: cluster configuration
  arc-configuration/       → ARC runner configuration
```

Platform team's reusable workflow library:

```
.github/workflows/
  ci-python.yml          - Python CI golden path
  ci-node.yml            - Node.js CI golden path
  ci-java.yml            - Java/Maven CI golden path
  build-container.yml    - Docker build + GHCR + signing
  deploy-ecs.yml         - ECS deployment (OIDC, blue-green)
  deploy-eks.yml         - EKS deployment (OIDC, Helm, ArgoCD)
  release.yml            - Semantic release + SBOM + SLSA
  security-scan.yml      - Full security battery
```

Product team workflow (3 lines to production-grade CI/CD):

```yaml
name: API Service CI/CD
on:
  push: {branches: [main]}
  pull_request: {branches: [main]}
jobs:
  ci:
    uses: myenterprise/platform-workflows/.github/workflows/ci-python.yml@v2
    secrets: inherit
  build:
    needs: ci
    uses: myenterprise/platform-workflows/.github/workflows/build-container.yml@v2
    with:
      registry: ghcr.io
      image-name: myenterprise/api-service
    secrets: inherit
  deploy:
    needs: build
    uses: myenterprise/platform-workflows/.github/workflows/deploy-eks.yml@v2
    with:
      environment: production
      cluster: prod-us-east-1
      image-digest: ${{ needs.build.outputs.digest }}
    secrets: inherit
```

The platform team owns the golden-path workflows. Product teams consume them with minimal configuration. Policy enforcement, security scanning, signing, and observability are baked in — product teams cannot skip them.

Governance via Organization Rulesets:

```
- All repos: require PR reviews, block force push to main
- All repos: require status checks (ci/test, security/codeql)
- All repos: require signed commits (enterprise setting)
- Pattern 'release/*': require 2 reviews + security team review
```

Observability:

```
- Audit log → Splunk (SIEM integration)
- Actions metrics → Datadog (workflow duration, failure rate)
- Runner utilization → Grafana
- DORA metrics from GitHub GraphQL → custom dashboard
```

Cost controls:

```
- Self-hosted ARC runners on spot/preemptible VMs (80% savings)
- Concurrency cancel on PRs (save superseded run minutes)
- Cache everything (Docker layers, dependencies, build outputs)
- Larger runners for compilations (faster wall clock = same cost, better UX)
```

Security controls:

```
- OIDC for all cloud authentication (zero stored cloud credentials)
- Fine-grained PATs for all automation (no classic PATs)
- GitHub Apps for all bots (not machine users)
- GHAS enabled org-wide: CodeQL, secret scanning, push protection
- Dependency review on all PRs
- Artifact signing + SBOM on all releases
- OpenSSF Scorecard weekly for all repos
```

## Master Interview Q&A — Principal Engineer Level

### Q: Design a GitHub Actions CI/CD system for 500 microservices. What are the key architectural decisions?

A: Key decisions: (1) Reusable workflows library — product teams consume, platform team owns. (2) Self-hosted ARC runners on Kubernetes spot instances for cost (80%+ savings). (3) OIDC for all cloud auth — zero stored credentials. (4) Repository Rulesets for org-wide policy without per-repo config. (5) GHAS org-wide — CodeQL, secret scanning, push protection. (6) GitHub Packages / GHCR as the artifact registry — same auth model. (7) Merge Queue for high-traffic repos to prevent the 'pending head' problem. (8) Audit log streaming to SIEM for compliance.

### Q: How would you implement a secure, auditable deployment pipeline for a regulated industry?

A: Requirements: (1) Immutable artifacts — build once, sign, promote same binary through environments. (2) SLSA Level 3 provenance — GitHub hosted runners provide this. (3) Artifact signing with Cosign + Sigstore transparency log. (4) Environment gates — required reviewers, minimum soak time. (5) Audit log to immutable storage (S3 with Object Lock). (6) OIDC for all cloud access — no long-lived credentials. (7) SBOM attached to every release. (8) Dependency review blocking vulnerable or GPL-licensed deps. (9) Two-person approval for production (environment required reviewers). (10) Rollback SOP tested regularly.

### Q: A developer accidentally committed an AWS secret key to a public GitHub repository. What is your incident response?

A: Immediate (first 5 minutes): (1) Assume the secret is compromised — it has been indexed by bots within seconds. (2) Rotate/invalidate the secret in AWS IAM immediately. (3) Check CloudTrail for any use of the leaked credentials. Then remediate: (4) Use 'git filter-repo' to remove from history and force-push (doesn't help — already distributed). (5) Contact GitHub Support to report the leak. (6) Enable push protection to prevent recurrence. Then improve: (7) Deploy OIDC to eliminate all stored cloud credentials. (8) Enable org-wide secret scanning + push protection. (9) Run a secret scan on all repos (truffleHog, gitleaks).

### Q: Explain how you would implement zero-trust security for GitHub Actions workflows.

A: Zero-trust principles applied: (1) Identity: OIDC for all cloud auth — short-lived, identity-verified tokens. (2) Least privilege: every job has minimal permissions block; GITHUB_TOKEN read-only by default. (3) Verified builds: SLSA provenance, Cosign signing, attestations — consumer verifies before deploying. (4) No persistent credentials: ephemeral runners, OIDC-only cloud access, rotation for remaining secrets. (5) Policy enforcement: Organization Rulesets, allowed actions list, Dependabot + CodeQL mandatory. (6) Auditability: all workflow runs logged, audit log streamed to immutable SIEM. (7) Network: VPC-connected runners, no public internet access for sensitive builds.

### Q: How does GitHub's merge queue solve the 'pending head problem' and what are its tradeoffs?

A: The pending head problem: PR A and PR B are both approved and tested against main at commit X. If both merge independently, the combined state (X + A + B) is never tested — one may break the other. Merge queue tests the combined state: it creates a synthetic branch merging current main + PR, runs CI, and only merges if CI passes. Tradeoffs: (1) Increased CI load — every merge queued PR runs CI again. (2) Queue contention — if CI is slow, the queue backs up. (3) Added latency — developers wait longer for merge. Mitigations: fast CI (< 5 min), larger runners, test parallelization, selective merge queue for high-risk branches only.

## Reference — Key Resources

### Official Documentation

- GitHub Docs: docs.github.com — comprehensive reference for all features
- GitHub Actions: docs.github.com/en/actions — complete workflow reference
- GitHub REST API: docs.github.com/en/rest — all REST endpoints
- GitHub GraphQL API: docs.github.com/en/graphql — schema explorer
- GitHub Enterprise: docs.github.com/en/enterprise-cloud@latest

### Security & Supply Chain

- SLSA Framework: slsa.dev
- Sigstore: sigstore.dev — keyless signing infrastructure
- OpenSSF Scorecards: github.com/ossf/scorecard
- CISA Secure Software Development: cisa.gov/sse

### Key Open Source Projects

- ARC: github.com/actions/actions-runner-controller
- Cosign: github.com/sigstore/cosign
- Argo Rollouts: argoproj.github.io/argo-rollouts
- Flux: fluxcd.io — GitOps for Kubernetes
- ArgoCD: argo-cd.readthedocs.io
- Backstage: backstage.io — Internal developer portal
- Syft: github.com/anchore/syft — SBOM generation

### Learning Resources

- GitHub Skills: skills.github.com — interactive learning labs
- GitHub Blog: github.blog — engineering posts from GitHub
- GitHub Engineering: githubengineering.com

---

**[Back to Part 1 ←](pathname:///archon/agentic-systems/coding-tools/06-ecosystem-patterns-labs.md) for Ecosystem & Enterprise Patterns.**
