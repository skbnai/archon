# Split Plan: git-github-platform-engineering-handbook

**Source:** `../knowledge-docs/docs/coding-tools/github-copilot/git-github-platform-engineering-handbook.md` (15,198 words, 2,308 lines)  
**Domain:** agentic-systems  
**Doc Type:** reference-architecture  
**Split Strategy:** 4-part split by thematic content boundaries  
**Date Created:** 2026-07-24  
**Status:** executed

## Part Mapping

### Part 1: Git Foundations & GitHub Essentials
- **Topic ID:** `git-github-platform-engineering-handbook`
- **Target Path:** `docs/agentic-systems/coding-tools/09-git-github-platform-engineering-handbook.md`
- **Source Content:** Source lines 14–279 (Parts 1–5)
  - PART 1: Git Foundations (core concepts, objects, merge/rebase/cherry-pick)
  - PART 2: Git CLI Cheat Sheet (complete command reference)
  - PART 3: Git Internals (storage, refs, packfiles, gc)
  - PART 4: Git Workflow Strategies (GitHub Flow, Git Flow, Trunk-Based, Monorepo, Multi-Repo)
  - PART 5: GitHub Platform Deep Dive (repos, orgs, teams, PRs, Issues, Projects, CODEOWNERS)
- **Frontmatter:** domain=agentic-systems, topic_id=git-github-platform-engineering-handbook, supersedes=["docs/coding-tools/github-copilot/git-github-platform-engineering-handbook.md"]
- **Mermaid Diagrams:** 3 (Working tree→staging, Git storage hierarchy, Workflow decision tree)
- **ASCII Art Converted:** 0 (all source diagrams already mermaid-formatted)

### Part 2: GitHub Platform Depth & CI/CD
- **Topic ID:** `git-github-platform-engineering-handbook-part2`
- **Target Path:** `docs/agentic-systems/coding-tools/parts/09-git-github-platform-engineering-handbook-part2.md`
- **Source Content:** Source lines 280–1,163 (Parts 6–15)
  - PART 6: GitHub Wiki (lightweight docs, versioned)
  - PART 7: GitHub Pages (static site hosting, MkDocs, Docusaurus)
  - PART 8: GitHub Projects (Kanban, Tables, Roadmaps, Custom Fields)
  - PART 9: GitHub Packages (GHCR, npm, PyPI, Maven, NuGet)
  - PART 10: GitHub Releases (Tags, Release Notes, Semantic Versioning, Automation)
  - PART 11: GitHub Codespaces (Cloud dev environments, Dev Containers)
  - PART 11b: Dev Containers & Codespaces Deep Dive (devcontainer.json, Lifecycle, Features)
  - PART 12: GitHub CLI (`gh` — repos, issues, PRs, workflows, releases)
  - PART 13: GitHub Actions Complete Guide (concepts, jobs, steps, actions, triggers)
  - PART 14: Most Common GitHub Actions (checkout, cache, setup-*, codeql, OIDC auth)
  - PART 14b: AI Agent Platforms (Agent HQ, Copilot, Spark, MCP, multi-agent decisions)
  - PART 15: Python Engineering Toolchain (uv, Poetry, Ruff, MyPy, Pytest, Packaging)
- **Frontmatter:** domain=agentic-systems, topic_id=git-github-platform-engineering-handbook-part2, supersedes=[]
- **Mermaid Diagrams:** 4 (GitHub Pages deployment, Codespaces lifecycle sequence, GitHub Actions hierarchy, Agent HQ workflow)
- **ASCII Art Converted:** 0 (all source diagrams already mermaid-formatted)

### Part 3: Security, Quality & Governance
- **Topic ID:** `git-github-platform-engineering-handbook-part3`
- **Target Path:** `docs/agentic-systems/coding-tools/parts/09-git-github-platform-engineering-handbook-part3.md`
- **Source Content:** Source lines 1,164–1,764 (Parts 16–24)
  - PART 16: Software Quality Engineering (code quality, technical debt, maintainability, quality gates)
  - PART 17: SonarQube Deep Dive (architecture, scanners, metrics, YAML examples)
  - PART 18: DevSecOps Toolchain (SAST, dependency scanning, secrets, container, IaC, K8s security)
  - PART 19: Supply Chain Security (SBOM, Cosign, SLSA levels, attacks: confusion, typosquatting, malicious packages)
  - PART 20: GitHub Advanced Security (CodeQL, Dependabot, Secret Scanning, Push Protection, Dependency Review, Security Campaigns)
  - PART 21: Identity, Governance & Compliance (SAML SSO, SCIM, EMU, RBAC, Audit Logs, Enterprise Identity Architecture)
  - PART 22: OIDC and Secretless Authentication (secrets vs OIDC, workflow, provider patterns, best practices)
  - PART 23: GitHub Copilot and AI Development (CLI commands, AI tool landscape comparison, multi-agent decision matrix)
  - PART 24: AI Security (risks, mitigation, testing tools, agent security architecture)
- **Frontmatter:** domain=agentic-systems, topic_id=git-github-platform-engineering-handbook-part3, supersedes=[]
- **Mermaid Diagrams:** 5 (Quality gate flow, DevSecOps pipeline, Enterprise identity architecture, OIDC sequence diagram, AI security architecture)
- **ASCII Art Converted:** 0 (all source diagrams already mermaid-formatted)

### Part 4: Enterprise Scale, Governance & Metrics
- **Topic ID:** `git-github-platform-engineering-handbook-part4`
- **Target Path:** `docs/agentic-systems/coding-tools/parts/09-git-github-platform-engineering-handbook-part4.md`
- **Source Content:** Source lines 1,765–2,308 (Parts 25–30)
  - PART 25: Complete Production GitHub Actions Workflows (Python CI, DevSecOps, Docker, K8s, Terraform, Release automation, Multi-environment promotion)
  - PART 26: Enterprise GitHub Governance (Branch protection, CODEOWNERS, Org policies, Merge Queue, Rulesets, Best practices, Antipatterns)
  - PART 27: GitHub Advanced Security (GHAS) — Deep Dive (CodeQL configuration, Secret Scanning, Push Protection, Dependabot, Dependency Review, Best practices)
  - PART 28: GitHub Copilot Enterprise at Scale (Seat management, AI Credits, Budget control, Codebase indexing, Fine-tuned models, MCP admin, Enterprise data privacy)
  - PART 29: AI-Assisted Platform Engineering (Agent mode for IaC, Runbook automation, Self-service infrastructure, Incident response, Drift detection, IaC code review)
  - PART 30: Measuring Platform Engineering Success (DORA metrics, AI productivity metrics, ROI analysis, Quarterly review template, Continuous improvement loop, Best practices)
- **Frontmatter:** domain=agentic-systems, topic_id=git-github-platform-engineering-handbook-part4, supersedes=[]
- **Mermaid Diagrams:** 3 (Multi-environment promotion, AI-assisted incident response, Continuous improvement loop)
- **ASCII Art Converted:** 0 (all source diagrams already mermaid-formatted)

## Validation Summary

All parts have:
- Zero ASCII art/box-drawing characters (all diagrams converted to mermaid format)
- At least 1 mermaid diagram per part (requirement: ≥1 per reference-architecture part)
- Correct frontmatter (domain, status, topic_id, date_created, last_reviewed)
- MDX-safe escaping (literal `<` converted to `&lt;` outside code blocks)
- Proper split nav-links between all parts
- Faithful complete transcription of source content (≥90% combined word ratio)

**Diagram Count by Part:**
- Part 1: 3 diagrams
- Part 2: 4 diagrams
- Part 3: 5 diagrams
- Part 4: 3 diagrams
- **Total: 15 mermaid diagrams** (all authentic, content-derived, no placeholders)

**Total Word Preservation Target:** ≥13,678 words (90% of 15,198 source)
