---
title: "Terraform from Zero to Mastery (Part 4: Interview Questions & Operations Guide)"
doc_type: guide
domain: platforms
status: current
topic_id: terraform-mastery-guide-part4
last_reviewed: 2026-07-27
maturity: practitioner
supersedes: []
tags:
  - terraform
  - iac
  - interview-prep
  - production-readiness
  - operations
covers_version: "as of 2026-07-10"
---

*Part 4 of 4 of [Terraform from Zero to Mastery](../26-terraform-mastery-guide.md).*

## Appendix B — 125 Interview Questions

### Beginner (B01–B50)

1. What is Terraform and how does it differ from configuration management tools like Ansible?
2. What is Infrastructure as Code and why is it important?
3. Explain the difference between `terraform plan` and `terraform apply`.
4. What is a Terraform provider? Give 5 examples.
5. What is the `terraform.tfstate` file and why is it important?
6. What is the difference between `resource` and `data` blocks in Terraform?
7. What does `terraform init` do? What does it create?
8. How do you declare a variable in Terraform? How do you pass a value to it?
9. What is an output value in Terraform and when would you use it?
10. Explain the purpose of the `.terraform.lock.hcl` file.
11. What is the difference between `count` and `for_each`?
12. What are `locals` in Terraform? Give an example use case.
13. What is `terraform fmt` and why should you run it?
14. How do you reference an attribute of one resource in another resource?
15. What does `terraform destroy` do? When would you use it?
16. What is a Terraform module? What are the benefits of using modules?
17. How do you handle sensitive variables in Terraform?
18. What is the purpose of the `depends_on` meta-argument?
19. How do you use `terraform import` and when is it needed?
20. What does 'idempotent' mean in the context of Terraform?
21. What is a backend in Terraform? Give examples of remote backends.
22. How do Terraform workspaces work? What are their limitations?
23. What is the `lifecycle` meta-argument? Name 4 lifecycle options.
24. How do you pass outputs from one module to another?
25. What is the `terraform console` command used for?
26. What happens if someone makes manual changes to cloud resources managed by Terraform?
27. What is `terraform validate` and what does it check?
28. How do you specify which version of a provider to use?
29. What is the difference between `terraform apply` and `terraform apply tfplan`?
30. What is a Terraform registry?
31. Explain the declarative vs imperative approach with examples.
32. What types are supported for Terraform variables?
33. How do you use a `.tfvars` file?
34. What is the purpose of the `required_version` setting?
35. What happens if you rename a resource block in Terraform?
36. How does `for_each` differ from `count` when managing collections?
37. What is the `terraform graph` command and what does its output represent?
38. What is state locking and why is it important?
39. How do you reference the current AWS account ID in Terraform?
40. What is the `null_resource` / `terraform_data` resource used for?
41. What environment variable enables Terraform debug logging?
42. How do you pass provider configuration from a root module to a child module?
43. What is the difference between a data source and a resource?
44. How do you use string interpolation in Terraform HCL?
45. What are the three main files you'd find in a typical Terraform module?
46. How do you iterate over a map using `for_each`?
47. What is the `dynamic` block used for?
48. What is `provisioner` in Terraform? Why are they discouraged?
49. What is the `terraform output` command used for?
50. How do you validate variable values using validation blocks?

### Advanced (A01–A50)

1. Explain the Terraform DAG and how it enables parallel execution.
2. How does Terraform handle partial failures during `terraform apply`?
3. What is state drift and how do you detect and remediate it?
4. Explain the difference between `terraform state mv` and `moved` blocks.
5. How does the `moved` block work internally in Terraform state?
6. What are the risks of using `-target` in production?
7. How would you migrate a large infrastructure from manually-provisioned to Terraform-managed?
8. Explain how `terraform plan -refresh-only` differs from `terraform plan`.
9. What is the `create_before_destroy` lifecycle option and when would you use it?
10. How do you implement blue-green deployments in Terraform?
11. Explain cross-state references using `terraform_remote_state`.
12. What is state serialization format? What is the 'serial' field in state?
13. How do you structure Terraform code for multi-environment deployments?
14. What is the difference between provider aliasing and multiple provider configurations?
15. How do you implement zero-downtime database migrations with Terraform?
16. Explain import blocks (Terraform 1.5+) vs legacy `terraform import` command.
17. How does Terraform handle resource dependencies with `for_each` collections?
18. What is the `-generate-config-out` flag and how does it work?
19. How would you implement Terraform for a multi-account AWS Organization?
20. Explain the risks of `force_destroy` on an S3 bucket.
21. How do you encrypt Terraform state at rest?
22. What is a provider lock and how do you manage cross-platform locks?
23. How do you test Terraform modules? What tools are available?
24. Explain the difference between `terraform destroy` and using `lifecycle { prevent_destroy = true }`.
25. How does Terraform's gRPC communication with providers work?
26. What is a Terraform Sentinel policy and how does it enforce governance?
27. How do you handle Terraform state in a monorepo with hundreds of modules?
28. What are the tradeoffs between Terraform workspaces and directory-based environments?
29. How do you safely rotate database passwords managed by Terraform?
30. Explain Terraform's resource lifecycle phases: Create, Read, Update, Delete.
31. How do you implement canary deployments with Terraform?
32. What is the `replace_triggered_by` lifecycle meta-argument?
33. How do you handle provider version constraints in a shared module library?
34. Explain how Terraform resolves type mismatches between variable types.
35. What is the difference between `jsonencode()` and `tostring()` in Terraform?
36. How do you use Terraform to manage Kubernetes manifests?
37. What is the purpose of `terraform providers lock` command?
38. How do you implement Infrastructure as Code for AI/ML platforms?
39. How would you decommission a production environment using Terraform?
40. Explain how `terraform apply -replace` works vs the deprecated `taint` command.
41. How do you handle circular dependencies in Terraform?
42. What is the ephemeral resource type introduced in newer Terraform versions?
43. How do you implement GitOps with Terraform and Atlantis?
44. How would you implement cost governance using Terraform policies?
45. Explain OPA (Open Policy Agent) integration with Terraform plans.
46. How do you manage Terraform provider upgrades in a large codebase?
47. What is the purpose of the `precondition` and `postcondition` lifecycle blocks?
48. How do you implement Terraform testing with the `terraform test` framework?
49. How do you handle state migration when splitting a monolithic state file?
50. What strategies exist for recovering from corrupted Terraform state?

### Architect-Level (AR01–AR25)

1. Design a Terraform architecture for a Fortune 500 company with 50+ engineering teams, multiple cloud providers, and strict compliance requirements.
2. How would you architect Terraform for a company migrating from on-premises data centers to AWS, with a 2-year timeline and 500+ servers?
3. What is your strategy for managing Terraform state across 200+ microservices, each with dev/staging/prod environments?
4. Design a Terraform module that implements a complete production-ready EKS cluster with auto-scaling, network policies, and monitoring.
5. How would you implement a Terraform-based Infrastructure as a Service (IaaS) platform for internal teams with self-service capabilities?
6. Describe your approach to Terraform state management for a company going through a merger and acquisition.
7. How would you implement a fully automated compliance framework for Terraform covering SOC 2, HIPAA, and PCI-DSS?
8. Design a cost optimization strategy using Terraform for a company spending $2M/month on AWS.
9. How would you architect Terraform for multi-cloud (AWS + Azure + GCP) with unified governance, consistent tagging, and cross-cloud networking?
10. What is your disaster recovery architecture for Terraform state, considering state corruption, accidental destroy, and regional failures?
11. How do you architect Terraform for a CI/CD platform that runs 1,000+ pipeline jobs per day, each provisioning temporary testing environments?
12. Design a Terraform module registry strategy for an enterprise with 300+ engineers.
13. How would you implement progressive delivery (canary/blue-green) for infrastructure changes in a zero-downtime requirement?
14. Describe a Terraform strategy for managing multi-tenant SaaS infrastructure where each customer gets isolated cloud resources.
15. How do you approach Terraform code review as an architect? What automated checks do you require in CI?
16. Design a drift detection and auto-remediation system using Terraform, AWS Lambda, and EventBridge.
17. How would you migrate an organization from Terraform Cloud to a self-hosted Atlantis + S3 backend setup?
18. Describe your approach to Terraform for AI/ML infrastructure (GPU clusters, Databricks, SageMaker, vector databases).
19. How do you architect Terraform for infrastructure decommissioning programs that span 18+ months and multiple application retirements?
20. What is your strategy for adopting OpenTofu in an organization that currently uses Terraform Cloud?
21. Design a Terraform-based Internal Developer Platform (IDP) using Backstage as the frontend and Terraform as the provisioning backend.
22. How would you implement AI-assisted Terraform code review and security scanning in a GitOps pipeline?
23. Describe how Terraform integrates with a Service Mesh (Istio/Linkerd) deployment architecture.
24. How do you design Terraform for regulated environments (financial services, healthcare) with immutable audit trails?
25. What is your vision for the future of Infrastructure as Code over the next 5 years?

## Appendix C — Production Readiness Checklist

### State Management

- [ ] Remote backend configured (S3+DynamoDB / Azure Blob / GCS)
- [ ] State file encryption enabled (at-rest and in-transit)
- [ ] State versioning enabled (S3 bucket versioning / GCS object versioning)
- [ ] DynamoDB locking table configured (AWS) or native locking (Azure/GCP)
- [ ] State backup schedule defined and tested
- [ ] State access controls: least-privilege IAM for state bucket
- [ ] State file never committed to Git (`.gitignore` includes `*.tfstate`)

### Security

- [ ] No secrets/passwords in `.tf` files or `.tfvars`
- [ ] All sensitive variables marked `sensitive = true`
- [ ] Secrets sourced from Secrets Manager / Key Vault / Vault
- [ ] CI/CD uses OIDC role assumption (not long-lived credentials)
- [ ] Terraform CI role follows least-privilege IAM
- [ ] SAST scanning enabled (Checkov, tfsec, or Snyk IaC)
- [ ] Provider version constraints use `~>` (pessimistic)
- [ ] `.terraform.lock.hcl` committed to Git

### Destroy Protection

- [ ] `lifecycle { prevent_destroy = true }` on all production stateful resources
- [ ] Production databases have `deletion_protection = true`
- [ ] S3 buckets with critical data do NOT have `force_destroy = true`
- [ ] `terraform destroy` requires manual approval in CI
- [ ] Final snapshot `before_destroy` configured for databases

### Code Quality

- [ ] `required_version` constraint set in all root modules
- [ ] `required_providers` versions pinned with `~>`
- [ ] `terraform fmt -recursive` passes with no changes
- [ ] `terraform validate` passes with no errors
- [ ] All resources have consistent tagging (environment, team, cost_center)
- [ ] Module `README.md` documents all inputs, outputs, and examples
- [ ] No hardcoded account IDs, region names, or environment values

### CI/CD Pipeline

- [ ] `terraform plan` runs on every PR and posts results as comment
- [ ] `terraform apply` only runs from main/master branch
- [ ] Plan output reviewed before apply is triggered
- [ ] Plan saved with `-out` and same plan applied (not re-planned)
- [ ] No `-auto-approve` in production pipelines without plan review
- [ ] Pipeline uses pinned Terraform/OpenTofu version
- [ ] Drift detection job runs on schedule (daily minimum)

### Operations

- [ ] Runbook exists for common operations (apply, destroy, import)
- [ ] Runbook exists for state corruption recovery
- [ ] On-call engineers can manually unlock state
- [ ] State is accessible to multiple engineers (not one person's laptop)
- [ ] Cost impact reviewed as part of infrastructure changes
- [ ] Resource naming conventions documented and enforced

## Appendix D — Day-0, Day-1, Day-2 Operations Guide

### Day-0: Platform Setup

```bash
# 1. Bootstrap remote state backend (run once by platform team)
cd infrastructure/bootstrap
terraform init -backend=false
terraform apply  # Creates S3 bucket + DynamoDB table

# 2. Set up Terraform version manager
brew install tfenv
tfenv install 1.9.0 && tfenv use 1.9.0

# 3. Configure provider credentials
aws configure sso                         # AWS SSO
az login                                  # Azure
gcloud auth application-default login    # GCP

# 4. Initialize first environment
cd environments/dev/us-east-1/networking
terraform init && terraform plan
```

### Day-1: Routine Changes

```bash
git checkout -b feature/add-rds-replica
vim environments/prod/us-east-1/data/main.tf
terraform validate && terraform fmt -recursive
terraform plan
git push origin feature/add-rds-replica
# PR → CI runs plan → post to PR comment
# Merge to main → CI runs terraform apply
terraform state show aws_db_instance.replica
terraform output
```

### Day-2: Maintenance & Incident Response

```bash
# Daily drift detection (CI schedule)
terraform plan -refresh-only -detailed-exitcode
# Exit 0: no changes  Exit 2: drift detected — alert team

# Provider upgrade maintenance
terraform init -upgrade
terraform plan  # Review breaking changes
# Update .terraform.lock.hcl and commit

# Incident: state lock stuck
terraform force-unlock <LOCK_ID>

# Incident: unexpected resource destroyed
aws s3api list-object-versions --bucket tf-state --prefix path/to/state
terraform import aws_rds_cluster.main <cluster-id>

# Quarterly: dependency updates
terraform init -upgrade && terraform plan
# Apply in dev → staging → prod
```

## Related

- [Part 1: Fundamentals → State Deep Dive](../26-terraform-mastery-guide.md)
- [Part 2: CLI Mastery, Rollback & Modules](26-terraform-mastery-guide-part2.md)
- [Part 3: Enterprise Architecture, Security & OpenTofu](26-terraform-mastery-guide-part3.md)
