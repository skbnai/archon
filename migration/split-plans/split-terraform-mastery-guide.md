# Split Plan: Terraform from Zero to Mastery

**Source:** `/workspace/knowledge-docs/docs/cloud-platforms/iac/terraform/terraform-mastery-guide.md` (~9,045 words body)

**Reason:** Word count exceeds guide doc_type cap (2600 words hard cap); source frontmatter's `doc_type: research-report` dropped in migration (no primary-source citations backing the technical content — reclassified as `guide`).

## Split Boundary

**Part 1 (Main):** `docs/platforms/26-terraform-mastery-guide.md`
- Source: Parts 1–4 (Terraform Fundamentals, Terraform Architecture Deep Dive, Resource Matching Internals, Terraform State Deep Dive)
- Content: IaC evolution/tool comparison, CLI architecture and provider plugin system, resource DAG, `moved` blocks, state file internals, remote backends (S3/Azure/GCS), state locking, corruption recovery
- Target word count: ~2330 words

**Part 2 (Supplementary):** `docs/platforms/parts/26-terraform-mastery-guide-part2.md`
- Source: Parts 5–12 (Complete CLI Command Mastery, Rollback Strategy & Failure Recovery, Infrastructure Decommissioning, Force Destroy Deep Dive, State Manipulation Mastery, Data Sources/Variables/Outputs, Advanced Lifecycle Controls, Modules Mastery)
- Content: full CLI command reference, Git-based and blue-green rollback, enterprise decommission playbook, `force_destroy`/`-replace`, `state mv`/import blocks, data sources & variable validation, lifecycle meta-arguments, module design and monorepo-vs-multirepo
- Target word count: ~2060 words

**Part 3 (Supplementary):** `docs/platforms/parts/26-terraform-mastery-guide-part3.md`
- Source: Parts 13–18 + Appendix A (Enterprise Terraform Architecture, Security Best Practices, Anti-Pattern Catalog, Troubleshooting Playbook, System Retirement Programs, OpenTofu & The Future of Terraform, CLI Cheat Sheet)
- Content: enterprise directory structure/GitOps CI, secrets management/IAM least privilege, 17-item anti-pattern catalog, troubleshooting quick reference, bulk retirement pattern, HashiCorp→OpenTofu licensing history and migration, AI-assisted IaC trends, full CLI cheat sheet
- Target word count: ~2290 words

**Part 4 (Supplementary):** `docs/platforms/parts/26-terraform-mastery-guide-part4.md`
- Source: Appendices B–D (125 Interview Questions, Production Readiness Checklist, Day-0/1/2 Operations Guide)
- Content: beginner/advanced/architect-level interview question bank, production readiness checklist (state/security/destroy-protection/code-quality/CI-CD/operations), Day-0 platform setup, Day-1 routine changes, Day-2 maintenance & incident response
- Target word count: ~2200 words

## Mapping

| Source Part | Target Part | Title |
|---|---|---|
| 1–4 | 1 | Terraform Fundamentals → Terraform State Deep Dive |
| 5–12 | 2 | Complete CLI Command Mastery → Modules Mastery |
| 13–18, A | 3 | Enterprise Terraform Architecture → CLI Cheat Sheet |
| B–D | 4 | 125 Interview Questions → Day-0/1/2 Operations Guide |

## Navigation

- Each part ends with a pointer to the next part's topic coverage.
- Topic ID: all four parts share the `terraform-mastery-guide` topic family.
- Part 1 is canonical (`topic_id: terraform-mastery-guide`).
- Parts 2–4 use `topic_id: terraform-mastery-guide-part2/3/4`; all `supersedes: []` (Part 1 carries the supersedes entry).
