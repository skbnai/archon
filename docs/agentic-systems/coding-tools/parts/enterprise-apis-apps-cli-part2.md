---
title: "GitHub CLI & Enterprise Automation (Part 2)"
doc_type: guide
domain: agentic-systems
topic_id: enterprise-apis-apps-cli-part2
status: current
date_published: 2026-07-24
last_reviewed: 2026-07-24
supersedes: []
tags:
  - coding-tools
  - cli
  - automation
---

# GitHub CLI & Enterprise Automation (Part 2)

## Part 17 — GitHub CLI

## 17.1 gh CLI Overview

The GitHub CLI (gh) is the official command-line tool for GitHub. It enables scripting almost any GitHub operation without leaving the terminal, and integrates tightly with git for a seamless workflow.

Install:

```bash
brew install gh              # macOS
winget install GitHub.cli    # Windows
sudo apt install gh          # Debian/Ubuntu
```

Authenticate:

```bash
gh auth login                # Interactive
gh auth login --with-token < token.txt  # CI
GITHUB_TOKEN=xxx gh ...      # Env var
```

Switch between hosts (GitHub.com + GHES):

```bash
gh auth login --hostname github.mycompany.com
gh config set git_protocol ssh

# Check auth status:
gh auth status
```

### PR Automation

Create PR with all options:

```bash
gh pr create \
  --title "feat: add OIDC authentication" \
  --body-file .github/pull_request_template.md \
  --base main \
  --head feature/oidc-auth \
  --reviewer alice,bob,@platform-team \
  --assignee @me \
  --label "enhancement,security" \
  --project "Platform Q3 Roadmap" \
  --milestone "v2.0.0"
```

Merge PR with specific strategy:

```bash
gh pr merge 123 \
  --squash \
  --auto \
  --delete-branch \
  --body "Squashed: feat: add OIDC authentication"
```

Batch operations across repos:

```bash
for repo in $(gh repo list myorg --limit 100 --json name -q '.[].name'); do
  gh pr list --repo "myorg/$repo" --state open \
    --json title,number,author --jq '.[] | {repo: "'"$repo"'", title, number}'
done
```

### Release Automation

Create a release with auto-generated notes:

```bash
gh release create v2.1.0 \
  --title "Release v2.1.0" \
  --generate-notes \
  --notes-start-tag v2.0.0 \
  ./dist/app-linux-amd64 \
  ./dist/app-darwin-arm64 \
  ./dist/sbom.spdx.json
```

List releases and download assets:

```bash
gh release list --limit 10 | head -5
gh release download v2.0.0 --pattern '*.tar.gz' --dir ./downloads
```

Edit a release (add assets post-publish):

```bash
gh release upload v2.1.0 ./dist/app-windows-amd64.exe
```

### Enterprise Administration via CLI

List all repositories in an org with metadata:

```bash
gh repo list myorg \
  --limit 1000 \
  --json name,isPrivate,isArchived,defaultBranchRef,updatedAt \
  --jq '.[] | select(.isArchived == false)' \
  | jq -r '[.name, .defaultBranchRef.name, .updatedAt] | @csv'
```

Audit open PRs older than 30 days:

```bash
gh pr list --repo myorg/api-service \
  --state open \
  --json number,title,createdAt,author \
  --jq '.[] | select(.createdAt < (now - 2592000 | todate))'
```

Apply a label to all repos in org:

```bash
gh repo list myorg --json name -q '.[].name' | while read repo; do
  gh label create "needs-review" \
    --color "FF6B35" \
    --description "Needs security review" \
    --repo "myorg/$repo" 2>/dev/null || true
done
```

Run a workflow in all repos:

```bash
gh repo list myorg --json name -q '.[].name' | while read repo; do
  gh workflow run security-scan.yml \
    --repo "myorg/$repo" \
    --ref main 2>/dev/null || true
done
```

Check which repos are missing a CODEOWNERS file:

```bash
gh repo list myorg --json name -q '.[].name' | while read repo; do
  exists=$(gh api "repos/myorg/$repo/contents/.github/CODEOWNERS" \
    --silent -q '.name' 2>/dev/null)
  [ -z "$exists" ] && echo "Missing CODEOWNERS: $repo"
done
```

### gh CLI Extensions

gh CLI supports custom extensions written in any language, distributed as GitHub repositories prefixed with gh-.

Install popular extensions:

```bash
gh extension install nicholasgasior/gh-report   # Org activity reports
gh extension install dlvhdr/gh-dash             # Dashboard TUI
gh extension install mislav/gh-branch           # Branch management
gh extension install yuler/gh-todo              # TODO list from issues
```

Create your own extension:

```bash
gh extension create my-extension
cd gh-my-extension
```

The entry point is any executable named gh-my-extension

Example shell extension:

```bash
#!/bin/bash
# gh-security-audit: audit all repos for security settings
for repo in $(gh repo list $1 --json name -q '.[].name'); do
  branch_protection=$(gh api "repos/$1/$repo/branches/main/protection" 2>/dev/null)
  echo "$repo: $(echo $branch_protection | jq -r '.required_pull_request_reviews // "NONE"')"
done

chmod +x gh-my-extension
gh extension install .
```

## Interview Questions — Enterprise, APIs & Apps

### Q: What is the difference between a GitHub App and an OAuth App?

A: GitHub Apps are installations (scoped to repos/orgs) with fine-grained permissions, dedicated rate limits, short-lived tokens (1 hour), and are tied to the installation not a user. OAuth Apps act on behalf of a user, inherit the user's permissions, share the user's rate limit, and tokens don't expire. GitHub Apps are always preferred for automation because they don't depend on a user account and have better security scoping.

### Q: Explain SCIM provisioning and why enterprises need it.

A: SCIM automates user lifecycle management between an Identity Provider (Okta, Azure AD) and GitHub. When HR creates an employee in the IdP, SCIM automatically adds them to GitHub and the correct teams. When they leave, SCIM removes their access immediately. Without SCIM, offboarding requires manual GitHub deprovisioning — a security risk in large organizations where manual processes are error-prone.

### Q: What are the rate limits for the GitHub APIs, and how do GitHub Apps differ?

A: REST API authenticated requests: 5,000/hour per token. GraphQL API: 5,000 points/hour. GitHub Apps get installation-based limits: 5,000/hour baseline plus 50 requests per user per hour up to 15,000/hour for high-traffic installations. GITHUB_TOKEN in Actions: 1,000/hour per repo. Search API: 30/minute authenticated.

### Q: How would you audit all repositories in an organization for missing branch protection?

A: Use the GitHub GraphQL API or REST API via 'gh api' with pagination: list all repos, then check /repos/{owner}/{repo}/branches/main/protection for each. A bash script using gh repo list + gh api can do this efficiently. For org-wide enforcement, use Repository Rulesets which apply to ALL repos matching a pattern without requiring per-repo configuration.

---

**[Back to Part 1 ←](pathname:///archon/agentic-systems/coding-tools/04-enterprise-apis-apps-cli.md) for Enterprise GitHub, APIs & Apps.**
