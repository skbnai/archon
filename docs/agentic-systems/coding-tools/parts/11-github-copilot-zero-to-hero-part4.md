---
status: current
title: "RAI, Best Practices, Antipatterns, Shortcuts, Troubleshooting"
date_created: 2026-07-07
doc_type: guide
domain: agentic-systems
topic_id: github-copilot-zero-to-hero-part4
tags: ["coding-tools", "github-copilot"]
last_reviewed: 2026-07-24
supersedes: []
---

## Why This Matters

Responsible deployment of AI coding assistants requires compliance frameworks, anti-pattern awareness, best practices, and operational know-how. This part covers the human and organizational dimensions of Copilot adoption.

---

## 18. RAI and Compliance

### GDPR Compliance

| Requirement | GitHub Copilot Enterprise provision |
| --- | --- |
| Lawful basis for processing | Covered under DPA as legitimate interest / contract performance |
| Data subject rights (access, deletion) | GitHub provides mechanisms; enterprise admin coordinates |
| Data processing agreement | Required — request from GitHub account team |
| Cross-border transfer | Standard Contractual Clauses (SCCs) included in Enterprise DPA |
| Data retention | Prompts/responses: zero-retention with Enterprise configuration |

### Data Residency

Copilot Enterprise supports regional data residency for inference (prompt processing). Configure during Enterprise organization setup:

- Available regions: United States, European Union.
- Customer code and prompts are processed in the configured region.
- Audit logs include region confirmation.

Note: Data residency for inference does not extend to model training — all fine-tuning uses isolated pipelines outside shared training.

### SOC 2 Type II

GitHub holds SOC 2 Type II certification covering:

- Security (CC6–CC9): access controls, monitoring, incident response.
- Availability (A1): uptime commitments.
- Confidentiality (C1–C2): data protection.

Request the report under NDA from your GitHub account team. Include in your vendor security assessment documentation.

### Responsible AI Use Policies

When deploying Copilot Enterprise, establish a responsible AI use policy covering:

**Permitted Uses**
- Generating code scaffolding and boilerplate
- Getting explanations of unfamiliar code
- Generating unit tests for existing functions
- Drafting documentation from code
- Debugging with AI assistance

**Required Human Review**
- All AI-generated code merged to main must be reviewed by a human
- Security-sensitive code (auth, crypto, data access) requires security team review
- AI-generated IaC changes require platform engineer review
- Agent-authored PRs must not be self-merged by the assignee without peer review

**Prohibited Uses**
- Submitting AI-generated code as entirely your own in contexts requiring original authorship
- Using Copilot to generate code for systems where AI assistance is contractually prohibited
- Pasting client confidential data or PII into Copilot prompts
- Relying on Copilot output without validation for safety-critical systems

**Credit and Attribution**
- AI-assisted code does not require attribution in commit messages, but significant AI-generated sections should be noted in PR descriptions for reviewer awareness

**Compliance Notes**
- Copilot Enterprise does not use your code to train shared models (per DPA)
- All Copilot activity is logged in org audit logs for 90 days
- Sensitive file exclusions are configured at the org level (see platform team)

### Copilot and Software Supply Chain

AI-generated code has the same supply chain requirements as human-written code:

- Must pass SAST scanning (CodeQL, Semgrep, SonarQube) — see Git & GitHub Platform Engineering Handbook Part 27.
- Must pass dependency scanning (Dependabot, pip-audit) — AI may suggest vulnerable package versions.
- Agent-authored commits should be signed (configure in branch protection).
- Run SonarSource/sonarqube-scan-action@v4 in CI on all PRs including agent-authored ones.

---

## 19. Best Practices

1. **Write high-quality issues before assigning to the coding agent.** The agent's output quality is directly proportional to the clarity of the issue. Include context, acceptance criteria, and constraints — not just a vague description.

2. **Use Plan Mode before large agent tasks.** Review the proposed file list and command sequence before execution. Catching a misunderstanding at plan time saves the entire execution cost.

3. **Maintain a copilot-instructions.md** at .github/copilot-instructions.md for every significant repository. It is the highest-ROI action for improving suggestion quality and reducing convention violations.

4. **Select models appropriate to the task.** Use GPT-4o for completions (speed + cost), Claude Sonnet for complex reasoning and agent mode (quality). Mixing unnecessarily wastes credits.

5. **Treat agent-authored code like any other PR.** Apply the same review standards — no bypassing CI, no skipping CODEOWNERS review, no self-merging.

6. **Enable the "matching public code" filter** on Business/Enterprise to activate IP indemnification. Without it, the indemnification does not apply.

7. **Use .copilotignore to exclude vendor, generated, and sensitive files.** Keeps context clean, reduces credit consumption, and prevents accidental context leakage.

8. **Configure Enterprise MCP allow-list before enabling MCP for teams.** An open MCP policy allows any server, which expands the attack surface and creates compliance gaps.

9. **Set budget caps with three alert thresholds** (50%, 75%, 100%) before rollout. Surprised leadership over unexpected spend is avoidable.

10. **Run monthly seat utilization reviews.** Deprovision seats unused for 30+ days — typically recovers 10–20% of seat cost.

11. **Sign the GitHub DPA before going live in regulated environments.** The zero-training guarantee requires it.

12. **Use MCP servers with read-only credentials for database access.** Never connect an MCP server to a production database or use write-capable credentials.

13. **Save agent run traces for compliance-sensitive work.** The trace is your explainability artifact showing AI proposed → human validated → CI confirmed → human approved.

14. **Give agents specific, bounded tasks.** "Fix the null pointer in payments.py" produces better results than "fix all bugs in the payments service." Unbounded scope = unpredictable output.

15. **Review Copilot's inline suggestions before accepting, not after.** Accept means you own it — take a second to read each suggestion. Approving blindly is how AI-generated bugs reach production.

16. **For Enterprise: run GHAS secret scanning before enabling fine-tuned models.** Ensure no secrets or PII exist in repos selected for fine-tuning training data.

17. **Collect DORA metrics baseline before rollout.** You cannot demonstrate Copilot's DORA impact without a pre-rollout measurement.

18. **Establish a developer NPS survey cadence.** Quantitative metrics (acceptance rate) alone miss whether developers actually find the tool helpful.

---

## 20. Antipatterns

1. **Merging agent-authored PRs without review.** Even when all tests pass, AI can implement the wrong thing correctly. A human must confirm the approach is sound.

2. **Using Copilot as a documentation source.** Copilot generates plausible-sounding answers. For API specs, library behavior, and framework decisions, always cross-reference official documentation.

3. **Prompting with sensitive data.** Pasting database connection strings, API keys, PII, or client-confidential data into chat prompts is a data governance violation, even in Enterprise tier. Redact before prompting.

4. **Assigning ambiguous issues to the coding agent.** "Improve performance" will produce a well-executed PR that may not address the actual bottleneck. Issues for the coding agent must be specific and measurable.

5. **Auto-merging coding agent PRs without CI.** The agent passes tests in its environment; your CI catches environment-specific failures. Never bypass CI for agent PRs.

6. **Treating high acceptance rate as the only success metric.** A 95% acceptance rate on single-character completions tells you nothing. Pair with PR lead time, developer NPS, and change failure rate.

7. **Enabling all MCP servers without an allow-list.** Each MCP server expands the attack surface. In Enterprise, an open MCP policy means any developer can connect any server — a compliance violation.

8. **Expecting Copilot to know your internal frameworks without copilot-instructions.md.** Copilot will suggest patterns from its training data, not your internal conventions. Without instructions, you'll spend more time correcting suggestions than accepting them.

9. **Using coding agent for open-ended architecture work.** The agent produces concrete implementations. "Design our microservices architecture" is a human design task; "implement the user service per this ADR" is an agent task.

10. **Relying on Copilot's security suggestions without SAST.** Copilot may generate insecure code confidently. Always run CodeQL, Semgrep, and SonarSource/sonarqube-scan-action@v4 in CI — AI-generated code is not exempt.

11. **Using @master versions for actions in Copilot-generated YAML.** Agent mode may suggest @master action references. Pin all actions to specific major versions (@v4, @v3) — @master is unpinned and a supply-chain risk.

12. **Letting credits pool drain without a cap.** Organizations without a hard spend cap discover overages at end-of-month billing. Set caps proactively.

13. **Running fine-tuning on repos with third-party licensed code.** Some licenses (GPL, AGPL, certain commercial licenses) restrict ML training. Conduct a legal review before selecting repos for fine-tuning.

14. **Disabling the coding agent's confirmation dialogs.** Removing all confirmation dialogs allows the agent to run destructive commands silently. Keep at least "risky" level confirmation enabled.

15. **Using Copilot for production incident remediation without HITL gates.** In the heat of an incident, it's tempting to let the agent apply fixes directly. Always keep a human in the approval loop for production changes — the stakes are too high for autonomous execution.

---

## 21. Keyboard Shortcuts

### VS Code (Windows/Linux)

| Action | Shortcut |
| --- | --- |
| Accept suggestion | Tab |
| Dismiss suggestion | Escape |
| Next suggestion | Alt+] |
| Previous suggestion | Alt+[ |
| Open completions panel | Ctrl+Enter |
| Accept word-by-word | Ctrl+Right |
| Open Copilot Chat | Ctrl+Shift+I |
| Open inline chat | Ctrl+I (with selection) |
| New Copilot Chat | command palette: "GitHub Copilot: New Chat" |
| Open agent mode | command palette: "GitHub Copilot: Open Agent Mode" |
| Toggle Copilot on/off | Status bar Copilot icon → Enable/Disable |

### VS Code (macOS)

| Action | Shortcut |
| --- | --- |
| Accept suggestion | Tab |
| Dismiss suggestion | Escape |
| Next suggestion | Option+] |
| Previous suggestion | Option+[ |
| Open completions panel | Ctrl+Return |
| Accept word-by-word | Cmd+Right |
| Open Copilot Chat | Cmd+Shift+I |
| Open inline chat | Cmd+I (with selection) |

### JetBrains (All Platforms)

| Action | Shortcut |
| --- | --- |
| Accept suggestion | Tab |
| Dismiss suggestion | Escape |
| Next suggestion | Alt+] |
| Previous suggestion | Alt+[ |
| Open inline chat | Alt+\ (with selection) |
| Open Copilot Chat tool window | View → Tool Windows → GitHub Copilot Chat |
| Enable/disable Copilot | Tools → GitHub Copilot → Enable/Disable |

---

## 22. Troubleshooting

### Common Issues

**Suggestions not appearing**

Symptoms: No ghost text; no spinner in status bar.

Diagnostics:
- VS Code: Open Output panel → select "GitHub Copilot" → Look for authentication errors or network issues
- Check Copilot status: Click the Copilot icon in VS Code status bar → Check for error messages

Fixes:
1. Sign out and sign back in: command palette → "GitHub Copilot: Sign Out" → "Sign In".
2. Check your plan has Copilot enabled at your org level.
3. Check your seat is assigned: your GitHub org admin confirms seat assignment.
4. Disable conflicting extensions: other AI completion extensions can interfere.
5. Check network: corporate proxies may block Copilot endpoints (api.githubcopilot.com).

**Agent mode not available**

Symptoms: No "Agent" tab or mode in Copilot Chat.

Fixes:
1. Verify plan: agent mode requires Pro, Business, or Enterprise.
2. Update VS Code and the Copilot extension to latest versions.
3. Check org policy: org admin may have disabled agent mode (Org → Settings → Copilot → Policies).
4. JetBrains: ensure plugin version is 1.5.0+ (agent mode reached JetBrains parity July 2025).

**MCP servers not connecting**

Symptoms: MCP tools don't appear in chat; "server not found" errors.

Diagnostics:
- VS Code: Open Output panel → "GitHub Copilot MCP" → Look for connection errors or missing executables
- Test MCP server manually: npx @modelcontextprotocol/server-github (should print server info)

Fixes:
1. Verify the command in mcp.json resolves: run it directly in terminal.
2. Check environment variables: `${env:GITHUB_TOKEN}` requires the variable set in your shell.
3. Enterprise: verify the server is on the org allow-list.
4. Restart MCP connection: command palette → "GitHub Copilot: Restart MCP Servers".

**Coding agent not starting**

Symptoms: Assigned copilot to issue but no activity.

Fixes:
1. Verify the coding agent is enabled in org settings.
2. Check GitHub Actions is enabled for the repository.
3. Check the .github/workflows/ directory for the copilot agent workflow — it must exist and have correct permissions.
4. Check the repo's GitHub Actions permissions: Settings → Actions → General → Workflow permissions → "Read and write permissions".
5. Review the Actions run: the failed run will have diagnostic output.

**High credit consumption**

Symptoms: Credits depleting faster than expected.

Diagnostics:
```bash
# Identify top credit consumers
gh api /orgs/myorg/copilot/billing/seats --paginate \
  | jq '[.seats[] | {user: .assignee.login, credits: .credits_used_this_cycle}] | sort_by(-.credits) | .[0:10]'

# Break down by feature (requires Copilot Metrics API)
gh api /orgs/myorg/copilot/metrics | jq '.[] | {date, agent_runs, review_runs, completions}'
```

Fixes:
1. Set up budget cap and alerts (see Section 11).
2. Identify top consumers; review whether agent mode usage is scoped appropriately.
3. Add .copilotignore to high-consumption repos to reduce context size.
4. Switch completions model to GPT-4o (cheaper) if team is using premium models for all tasks.

**Code review not triggering**

Symptoms: Assigned Copilot as reviewer but no review posted.

Fixes:
1. Check org policy: Copilot code review must be enabled at org level.
2. Verify PR size: very large PRs (1000+ files) may exceed review capacity — split the PR.
3. Check for conflicting branch protection settings.
4. Manual trigger: on the PR → Reviewers → re-request review from Copilot.

**Poor suggestion quality**

Symptoms: Suggestions consistently irrelevant, violating conventions, or for wrong framework.

Fixes:
1. Add .github/copilot-instructions.md with project conventions (highest impact).
2. Enable codebase indexing (Enterprise) for cross-file context awareness.
3. Keep relevant files open in editor — completions use open tabs as context.
4. Switch to a premium model for complex tasks (Claude Sonnet for architecture/reasoning).
5. Check if .copilotignore is accidentally excluding important context files.

### Diagnostic Commands

```bash
# Check Copilot seat status for a user
gh api /orgs/myorg/copilot/billing/seats \
  | jq '.seats[] | select(.assignee.login == "username")'

# Check org Copilot settings
gh api /orgs/myorg/copilot/billing

# List available MCP servers (VS Code CLI)
# No CLI command; check .vscode/mcp.json and user settings

# GitHub Copilot extension diagnostics (VS Code)
# Help → Toggle Developer Tools → Console → filter "copilot"

# Verify GitHub authentication
gh auth status
```

### Getting Help

- **GitHub Copilot documentation:** docs.github.com/copilot
- **GitHub Copilot status:** githubstatus.com
- **Enterprise support:** your GitHub account team or support.github.com
- **Community forum:** github.com/orgs/community/discussions

---

## Related Links

- [GitHub Copilot Zero to Hero Part 1](../11-github-copilot-zero-to-hero.md) — What Is Copilot, Plans, Setup, Model Selection, Code Completion
- [GitHub Copilot Zero to Hero Part 2](11-github-copilot-zero-to-hero-part2.md) — Chat Interface, Agent Mode, MCP Integration, Code Review, Coding Agent, Billing
- [GitHub Copilot Zero to Hero Part 3](11-github-copilot-zero-to-hero-part3.md) — Enterprise Features, Parallelism, Token Optimization, Guardrails, Explainability, HITL

---

*This guide reflects the state of GitHub Copilot as of July 2026. GitHub Copilot is evolving rapidly — check docs.github.com/copilot for the latest feature status.*
