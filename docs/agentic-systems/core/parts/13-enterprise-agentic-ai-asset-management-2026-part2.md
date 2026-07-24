---
title: "Enterprise Agentic AI Asset Management 2026 — Part 2"
date_created: 2026-07-24
last_reviewed: 2026-07-24
status: current
domain: agentic-systems
doc_type: research-report
topic_id: enterprise-agentic-ai-asset-management-2026-part2
sources:
  - "Enterprise Agentic AI Asset Management 2026 — Original Research (Part 2)"
supersedes: []
---

**This is Part 2 of 3. [← Back to Part 1](pathname:///archon/agentic-systems/core/13-enterprise-agentic-ai-asset-management-2026) | [Continue to Part 3 →](pathname:///archon/agentic-systems/core/parts/13-enterprise-agentic-ai-asset-management-2026-part3)**

# Part 2: Enterprise Asset Lifecycle & Organization

## Enterprise Asset Lifecycle

How assets move from conception to retirement through a governed, multi-stage process.

Every agentic AI asset traverses a canonical 17-stage lifecycle. Ownership, tooling, and governance requirements change at each stage. Skipping stages — especially validation, simulation, and approval — is the root cause of most production AI incidents.

| Stage | Description | Owner |
|---|---|---|
| **Ideation** | Business need identified. Initial capability assessment. Asset request created by Product Owner. | M |
| **Design** | Architecture defined. Prompt strategy, tool selection, memory design, evaluation criteria specified. Design review. | M |
| **Authoring** | Asset created by specialist engineer. v0.1.0-alpha. Stored in feature branch. Iterative refinement. | M |
| **Peer Review** | Second engineer review for quality, safety, standards compliance — the code review equivalent for AI assets. | M |
| **Validation** | Automated linting, schema validation, security scanning, PII detection. Quality Gate #1. | M |
| **Simulation** | Agent run in sandboxed environment against synthetic scenarios. No real tool calls or production data. | M |
| **Testing** | Evaluation suite: unit tests, integration tests, regression tests, safety tests. Quality Gate #2. | M |
| **Approval** | Human review: Prompt/Agent Reviewer, RAI Officer, Security sign-off. Governance Board for high-risk. | M |
| **Publishing** | Promoted to Staging registry. Release candidate created and cryptographically signed. | M |
| **Registry** | Registered in production registry with full metadata, lineage, and dependency graph. | M |
| **Deployment** | Deployed via CI/CD pipeline. Canary or blue-green strategy. Gradual traffic ramp. | M |
| **Runtime** | Serving live traffic. Governed by execution policies, guardrails, and cost limits. | M |
| **Monitoring** | Continuous observability: latency, errors, cost, quality, safety violations, drift detection. | M |
| **Evaluation** | Periodic offline evaluation vs golden datasets. A/B testing. Quality regression detection. | M |
| **Improvement** | Feedback loop triggers new authoring cycle. Updates follow full lifecycle from Authoring. | M |
| **Deprecation** | Marked deprecated. Migration path communicated. Traffic gradually migrated to successor. | M |
| **Retirement** | Removed from production. Archived with immutable record. Successor asset documented. | |

### Ownership by Lifecycle Stage

| Stage | Primary Owner / Approver / Tooling |
|---|---|
| Ideation–Design | AI Product Owner / AI Architect / Jira + ADR |
| Authoring | Prompt/Agent Engineer / Tech Lead / IDE + Git |
| Peer Review | Senior Engineer / Team Lead / GitHub PR |
| Validation | Platform CI (automated) / CI Pipeline |
| Simulation | Agent Engineer / QA Engineer / Simulation Platform |
| Testing | Evaluation Engineer / Automated + Human / Eval Platform |
| Approval | Governance Board / RAI Officer + CISO / Approval Workflow |
| Publishing–Registry | AI Platform Engineer / Release Manager / Registry |
| Deployment | Platform Engineer / Change Advisory Board / CD Pipeline |
| Runtime–Monitoring | SRE / On-Call Engineer / Observability Stack |
| Evaluation | Evaluation Engineer / AI Quality Lead / Eval Platform |
| Deprecation–Retirement | AI Product Owner / Platform Architect / Registry + ITSM |

---

## Part 3: Enterprise Repositories

How enterprises organize version-controlled storage for agentic AI assets.

Repository strategy is a foundational architectural decision affecting discoverability, governance, CI/CD complexity, and developer experience.

### Strategy Comparison

| Strategy | Best For / Advantages / Disadvantages |
|---|---|
| Monorepo (All assets) | Small-medium orgs · Unified CI, atomic refactoring · Access control complexity, CI performance |
| Domain Monorepos (Per BU) | Large orgs with distinct domains · Team autonomy + consistency · Cross-domain reuse requires explicit publishing |
| Polyrepo (Per asset type) | Mature platform teams · Clean ownership, independent versioning · Discovery overhead, dependency complexity |
| Hybrid (Monorepo + Feeds) | Enterprise standard (recommended) · Best of both · Requires tooling investment and governance discipline |

### Recommended Directory Structure

The enterprise AI platform repository uses the following recommended directory layout:

- **enterprise-ai-platform/** (root)
  - **prompts/**: Prompt asset storage
    - system/ — System prompts by domain
    - task/ — Task-specific prompts
    - safety/ — Safety & guardrail prompts
    - evaluation/ — Judge & evaluation prompts
    - macros/ — Reusable prompt components
  - **agents/**: Agent definitions and configurations
    - manifests/ — Agent manifest YAML
    - configs/ — Environment-specific configs
    - blueprints/ — Agent templates & archetypes
  - **tools/**: Tool definitions and specifications
    - definitions/ — Function schemas (JSON Schema)
    - openapi/ — OpenAPI 3.x specs
    - mcp/ — MCP server definitions
    - a2a/ — A2A skill descriptors
  - **knowledge/**: Knowledge asset management
    - collections/ — RAG document collections
    - chunking/ — Chunking policy configs
    - ontologies/ — Domain ontologies
  - **evaluations/**: Evaluation and testing assets
    - datasets/ — Golden datasets
    - benchmarks/ — Benchmark suites
    - red-team/ — Adversarial scenarios
  - **governance/**: Governance and compliance
    - policies/ — Guardrails & RAI rules
    - compliance/ — Regulatory rule sets
    - workflows/ — Approval workflow definitions
  - **.github/**: CI/CD configuration
    - workflows/ — CI/CD pipeline definitions
  - **CODEOWNERS**: Asset ownership map
  - **metadata/**: Metadata management
    - schemas/ — Metadata schema definitions
    - catalog/ — Asset catalog entries

### Repository Governance Requirements

| Requirement | Implementation | Why It Matters |
|---|---|---|
| CODEOWNERS | Named owners for every directory. Changes require owner approval via PR review. | Enforces clear accountability and domain expertise review |
| Branch Protection | Main requires 2 approvals + passing status checks. No direct pushes. Signed commits enforced. | Prevents accidental deployments and enables audit trail |
| Automated Scanning | Pre-merge: secrets detection, PII scanning, prompt injection patterns, schema violations. | Catches governance violations before they reach registries |
| Semantic Versioning | Assets tagged with semver. Breaking changes require major bump and migration guide. | Enables consumers to understand compatibility without reading changelog |
| Immutable Releases | Release tags protected — no force-push, no deletion. Production references exact tags. | Enables reproducible deployments and forensic incident analysis |
| Dependency Lockfiles | Agent manifests include locked dependency versions. Updates trigger automated evaluation. | Prevents silent breaking changes when upstream assets update |

**Enforcement:** Automated CI/CD checks validate every requirement before merge. Violations block PR approval. This shifts governance left (into development) rather than post-deployment, where fixes are expensive and risky.

---

## Part 4: Enterprise Registries

Centralized discovery, publishing, and governance hubs for agentic AI assets.

A registry is the runtime-facing complement to a repository. While repositories store source assets, registries serve as the authoritative publication point for approved, versioned, discoverable artifacts consumed at runtime.

### Registry Types

| Registry | Purpose and Key Capabilities |
|---|---|
| Prompt Registry | Versioned approved prompts with semantic search, lineage tracking, A/B variant management, model-compatibility metadata. |
| Agent Registry | Deployable agent packages: manifests, configs, capability declarations, dependency graphs, certification records. |
| Tool Registry | Available tools: function schemas, MCP addresses, permission templates, health status, compatibility matrices. |
| MCP Registry | MCP server discovery, capability negotiation, authentication config, usage metering, health monitoring. |
| A2A Skill Registry | A2A-compatible skill discovery enabling agents to find and invoke skills from other agents across platforms. |
| Knowledge Registry | RAG collections, vector indexes, knowledge graphs, context packs with freshness indicators and access controls. |
| Evaluation Registry | Golden datasets, benchmarks, judge prompts, evaluation rubrics — shared across teams for consistency. |
| Policy Registry | Authoritative guardrail definitions, compliance rules, and approval workflow specs consumed by policy engines. |
| Model Registry | Approved base models, fine-tuned adapters, embedding models with benchmarks and deployment constraints. |

### Universal Registry Capability Requirements

| Capability | Notes |
|---|---|
| Semantic Search | Vector-based search over asset names, descriptions, capabilities. Enables discovery without knowing exact names. |
| Dependency Management | Transitive resolution, conflict detection, lock file generation, dependency graph visualization. |
| RBAC | Role-based access for publish/read/approve/deprecate. Namespace-level isolation per business unit. |
| Approval Workflows | Configurable multi-stage gates before publication. Automated reviewer assignment by asset type and risk. |
| Lineage Tracking | Full provenance graph: derived-from, authoring tool, model used, evaluation run IDs. |
| Certification | Security, RAI, and compatibility certification records attached to asset versions. |
| Marketplace UI | Browse, rate, and discover assets. Consumption analytics. Starred/featured collections. |
| OCI Artifact Support | Binary asset storage (models, embeddings) as OCI artifacts for toolchain portability. |
| Webhook Integration | Events on publication, deprecation, certification, policy violations — for automation pipelines. |

### Registry Environment Strategy

| Environment | Characteristics | Purpose |
|---|---|---|
| Development Registry | Team-scoped. Unrestricted publish. No approval gates. No evaluation gates. | Safe experimentation and rapid iteration without blocking teammates |
| Integration Registry | Cross-team scope. Peer review required. Automated evaluation gates against integration test suites. | Validate cross-team compatibility and integration behavior |
| Staging Registry | Production-equivalent topology. Full approval workflow. Mandatory security + RAI sign-off. Full evaluation pass required. | Final pre-production validation in production-like environment |
| Production Registry | Immutable signed releases only. Full audit trail of every access. Break-glass emergency rollback procedures only. | Serve approved, tested, stable assets to production agents |
| Archive Registry | Retired assets. Read-only. Immutable. Retained per data retention policy (typically 7 years for compliance). | Preserve historical record without risking accidental re-activation |

Each registry is independently versioned. An asset version 1.0.0 in development may differ significantly from version 1.0.0 in production — the production version is the authoritative one. Assets flow strictly upward: development → integration → staging → production (never backwards).

---

## Part 5: Universal Metadata Model

A canonical schema enabling discovery, governance, lineage, and interoperability across all asset types.

A unified metadata model is the connective tissue of the AAMP platform. It enables semantic search, dependency resolution, governance enforcement, cost attribution, and regulatory compliance across all asset types. Every asset must carry a complete metadata record.

### Universal Agentic AI Asset Metadata Schema v2.1

```yaml
id:               'asset-uuid-v4'          # Globally unique
type:             'prompt|agent|tool|...'   # Category
subtype:          'system-prompt|manifest'  # Detailed type
name:             'string'
version:          '1.2.3'                   # SemVer
lifecycle_state:  'draft|review|approved|deprecated|retired'
created_at:       '2026-01-15T10:00:00Z'
owner:
  team:           'string'
  email:          'team@company.com'
  business_unit:  'string'
  cost_center:    'CC-12345'
description:      'string'
purpose:          'string'
capabilities:     ['list', 'of', 'capabilities']
tags:             ['domain:finance', 'use-case:rag']
security:
  classification: 'public|internal|confidential|restricted'
  pii_risk:       'none|low|medium|high'
risk:
  rating:         'low|medium|high|critical'
  assessment_id:  'risk-assessment-uuid'
dependencies:
  prompts:        ['prompt-uuid-1']
  tools:          ['tool-uuid-1']
  models:         ['claude-sonnet-4-6']
compatibility:
  models:         ['claude-*', 'gpt-4*']
  schema_version: '>=2.0'
evaluation:
  quality_score:  0.92
  safety_score:   0.98
  last_eval_date: '2026-06-01'
governance:
  approval_status: 'approved'
  approvers:      ['rai-officer', 'ciso']
  review_cycle:   '90d'
  license:        'internal-use-only'
cost:
  avg_tokens_per_call: 1250
  monthly_cost_usd:    450.00
lineage:
  derived_from:   ['parent-asset-uuid']
  creation_source: 'human|ai-assisted|auto-generated'
change_history:
  - version:      '1.0.0'
    date:         '2026-01-15'
    author:       'engineer@company.com'
    summary:      'Initial release'
```

### Field Governance Rules

| Field Group | Governance Rule |
|---|---|
| id, type, name, version | System-generated or required at creation. Immutable once set. |
| owner, business_unit | Required. Validated against enterprise directory. Drives approval routing and cost allocation. |
| security.classification | Required. Determines access control (public/internal/confidential/restricted), storage location, and data handling policies including encryption and retention. |
| risk.rating | Required for agent and tool assets. Computed from risk assessment questionnaire covering threat models, compliance scope, and operational impact. |
| governance.approval_status | System-managed. Transitions only via approved workflow. Cannot be manually overridden. State machine enforces valid transitions. |
| evaluation.quality_score | Computed by evaluation platform. Read-only. Populated after each evaluation run with metrics like accuracy, latency, safety, and cost efficiency. |
| lineage.derived_from | Auto-populated by authoring tools. Critical for impact analysis when upstream assets change or are deprecated. |
| compatibility.models | Required for prompt and agent assets. Validated against model compatibility matrix enforced at build time. |

### Metadata-Driven Discovery and Governance

Rich metadata enables semantic search where engineers find related assets by describing their use-case rather than knowing exact names. Metadata catalogs maintain complete dependency graphs showing which agents depend on which prompts, tools, and knowledge sources. This enables rapid impact analysis: when a tool API changes, the platform automatically identifies all dependent agents and can trigger re-evaluation or require explicit approval for upgrade paths.

**Practical Implementation:**
- Start with minimal metadata (owner, version, purpose, tags, classification)
- Gradually expand as platform matures (lineage, compatibility, evaluation metrics, cost attribution)
- Automate metadata capture where possible (git authorship, CI pipeline results, runtime traces)
- Make metadata queryable through both keyword search and semantic/vector search
- Link metadata to approval workflows so governance decisions are recorded with assets

---

**[← Back to Part 1](pathname:///archon/agentic-systems/core/13-enterprise-agentic-ai-asset-management-2026) | [Continue to Part 3 →](pathname:///archon/agentic-systems/core/parts/13-enterprise-agentic-ai-asset-management-2026-part3)**
