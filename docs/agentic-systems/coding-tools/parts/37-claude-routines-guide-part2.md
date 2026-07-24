---
title: 'Claude Routines — Design Patterns & Reference (Part 2)'
doc_type: guide
domain: agentic-systems
topic_id: claude-routines-guide-part2
status: current
date_created: 2026-07-24
last_reviewed: 2026-07-24
supersedes: []
---

# Claude Routines — Design Patterns & Reference (Part 2)

**This is Part 2 of 2. [Back to Part 1 ←](pathname:///archon/agentic-systems/coding-tools/37-claude-routines-guide) for getting started and core concepts.**

---

## High-Value Use Cases

### Email Triage

**Schedule:** Daily 7:00 AM · **Connectors:** Gmail

Fetch unread emails from last 24h. Classify by urgency. Draft replies for routine questions. Flag anything needing human judgment with a summary in Slack.

### Automated PR Review

**Trigger:** GitHub PR opened · **Connector:** GitHub

On every new PR: analyze code changes, check for security vulnerabilities, verify test coverage, and post a structured review comment directly on the PR.

### Content Curation

**Schedule:** Daily 9:00 AM · **Network:** Custom allowlist

Fetch RSS feeds from target publications. Select articles matching your criteria. Format and post to Slack #reading-list. Avoid previously sent articles.

### Weekly Status Report

**Schedule:** Friday 5:00 PM · **Connectors:** GitHub + Slack

Compile merged PRs, closed issues, and open blockers from the week. Generate a formatted summary. Post to Slack #weekly-update and create a Google Doc archive.

### Nightly Security Scan

**Schedule:** Daily 2:00 AM · **Network:** Trusted

Clone repo, run dependency audit, check for newly published CVEs in used packages. Alert Slack #security immediately for CRITICAL findings. Weekly digest for lower severity.

### On-Call Alert Triage

**Trigger:** API (from PagerDuty/monitoring) · **Network:** Full

External monitoring fires HTTP POST to the API trigger. Claude analyzes alert context, checks recent deployments, suggests root cause, and posts runbook to the on-call Slack thread.

---

## Prompt Design for Routines

The prompt is the most important part of any Routine. Since it runs autonomously in a fresh cloud container, it must be completely self-contained. Here's the anatomy of a well-written Routine prompt:

### Anatomy of a Routine Prompt

```
## What to do (specific action steps)
1. Fetch all unread emails from the last 24 hours using the Gmail connector.
2. For each email: classify as [URGENT / ACTION / FYI / SPAM].
3. Draft a reply for any [ACTION] email that has a clear, short answer.
4. Compile a summary table: sender | subject | classification | action taken.

## What success looks like (verification criteria)
- All emails classified
- Replies drafted for ACTION items where a reply is clearly appropriate
- Summary posted to Slack #daily-triage

## How to handle edge cases
- If the email requires information you don't have: classify as NEEDS-HUMAN and skip drafting
- If Gmail connector fails: log the error and post an alert to Slack, then stop
- Never send emails — only draft. Always require human approval before sending.

## Output format
Post a Slack message with:
- Header: "Email Triage — {date}"
- Table: sender | subject | classification | action
- Footer: total count by classification
- Use plain text, no --- dividers (causes Slack invalid_blocks errors)
```

### Prompt Writing Rules

| Rule | Why It Matters |
|------|--------|
| State the goal, not just the steps | Claude can self-correct if a step fails while still achieving the goal |
| Define success explicitly | Claude knows when to stop; prevents over-execution |
| Handle the error path | Routines run unattended — silent failures are invisible |
| Specify output format exactly | Connector formatting quirks (Slack's invalid_blocks from `---`) must be pre-empted |
| No references to missing context | Fresh container — no session history, no local state |
| Start with human-in-the-loop | Drafts → human approves → auto-send as trust grows |

---

## Using Skills in Cloud Routines

Cloud Routine containers are fresh and have no access to skills defined on your local machine. The solution is a **secondary GitHub repository** that stores skills and is cloned alongside the primary repository.

### Setup Steps

1. **Create a skills repository**

   Create a GitHub repo (e.g., `routine-env`) with your skill files at `.agents/skills/skill-name/SKILL.md`. This repo serves as your cloud skill library.

2. **Add the skills repo to your Routine config**

   In the web UI, add `routine-env` as a secondary repository to the Routine. It will be cloned into the cloud container alongside your main repository.

3. **Add a SessionStart hook to copy skills**

   A `.claude/settings.json` in the skills repo tells Claude to copy skills into the right directory at session start:

```json
{
  "hooks": {
    "SessionStart": {
      "hooks": [
        {
          "type": "command",
          "command": "[ ! -d ~/.agents/skills ] && cp -r ~/routine-env/.agents/skills/. ~/.agents/skills"
        }
      ]
    }
  }
}
```

**The Skills Repository Pattern:** This is likely to become the standard pattern for Routines involving complex or reusable task definitions. A skills repository lets you version-control your automation logic separately from your application code, and share it across multiple Routines.

---

## Anti-Patterns to Avoid

### Vague or Stateful Prompts

Writing prompts like "check the usual stuff" or "continue from where you left off." Cloud containers start fresh — there is no session state, no previous context, no memory of last run.

**Fix:** Every prompt must be fully self-contained. Define what to check, what sources to use, and what to produce — as if explaining to someone with no context at all.

### Skipping the Manual Test

Activating a Routine without ever running it manually. Common failure modes: network blocked for a needed domain, connector auth expired, Slack formatting errors (--- dividers), missing environment variables.

**Fix:** Always click "Run now" at least once and review the live log before relying on the schedule. Fix all issues in the prompt or environment config before going live.

### Sub-Hourly Cron on Cloud Routines

Attempting to set a Cloud Routine with a cron expression that fires more than once per hour (e.g., */30 * * * *). Cloud Routines reject these expressions — minimum interval is 1 hour.

**Fix:** For sub-hourly polling, use /loop in an active session or Desktop Scheduled Tasks. Cloud Routines are for longer-cadence, unattended workflows.

### Bloated CLAUDE.md for Cloud Routines

Using a large CLAUDE.md file in your project that was written for interactive development. Every token in CLAUDE.md is consumed on each routine run. A 200-line CLAUDE.md wastes significant budget every execution.

**Fix:** Create a minimal CLAUDE.md (or none) for Routine-specific repositories. Put all instructions in the Routine prompt itself — it's loaded fresh each run anyway.

### Full Network Access by Default

Using "Full" network access for all Routines because it's simpler. This allows the Routine to reach any external endpoint, increasing the blast radius if the prompt is poorly written or the repository is compromised.

**Fix:** Use "Custom" allowlist mode for specific domains, or "Trusted" for pre-approved services. Only use "Full" when the task genuinely requires unrestricted access and you accept the security tradeoff.

### Using /loop Instead of Routines for Overnight Tasks

Leaving a /loop running overnight, requiring your machine to stay on and the terminal to stay open. This is fragile — a sleep, crash, or network drop kills the loop silently.

**Fix:** If a task needs to run while your laptop is off, it's a Cloud Routine. /loop is for in-session monitoring you're actively watching.

---

## Routines vs GitHub Actions

The question teams consistently ask: should I replace GitHub Actions with Routines? The answer is nuanced — they serve different purposes and work best together.

| Dimension | Cloud Routines | GitHub Actions |
|-----------|------|---------|
| Type of work | Judgment-based — reads, reasons, adapts | Deterministic — runs commands you defined |
| Trigger | Schedule, API, GitHub event | Git events, schedule, manual, API |
| Execution | Claude agent making decisions | YAML steps, shell commands |
| Self-healing | Yes — Claude retries with different approach | No — fails on unexpected state |
| Build / test / deploy | Possible but not ideal | Purpose-built |
| Code review with context | Purpose-built | Possible with complex prompts |
| Alert triage | Excels at reasoning about context | Very limited |
| Cost model | Token-based (inference cost) | Runner minutes (fixed) |
| Predictability | Probabilistic (AI reasoning) | Deterministic (scripted) |

**Recommended: Use Both Together**

Many production teams combine them: **Routines for the thinking work** (code review, bug triage, alert analysis, documentation updates) and **Actions for the mechanical work** (build, test, deploy). A Routine can review a PR; an Action builds and deploys it. They complement each other — neither replaces the other.

---

## Quick Reference

### Key URLs

```
claude.ai/code/routines        # Create and manage Routines
claude.ai/settings/usage       # Monitor run consumption
code.claude.com/docs/en/routines         # Official Cloud Routines docs
code.claude.com/docs/en/scheduled-tasks # /loop and session tasks docs
code.claude.com/docs/en/desktop-scheduled-tasks # Desktop tasks docs
```

### Essential Commands

```bash
# Create a cloud routine from CLI (schedule triggers only)
/schedule daily 9am briefing that summarizes Slack and email

# Loop with fixed interval
/loop 5m check if the deployment finished

# Loop with dynamic interval (Claude chooses delay)
/loop check CI and address any review comments

# One-time reminder
remind me at 3pm to push the release branch

# Manage tasks
what scheduled tasks do I have?
cancel the deploy check job

# Check version (need v2.1.72+ for scheduled tasks)
claude --version

# Disable scheduler entirely
export CLAUDE_CODE_DISABLE_CRON=1
```

### Setup Checklist for a New Cloud Routine

1. **Write a self-contained prompt**

   Goal + steps + success criteria + error handling + output format. No references to missing context.

2. **Choose the minimum network access**

   Custom allowlist > Trusted > Full. Blocked if no external calls needed.

3. **Set environment variables for secrets**

   Never hardcode API keys in the prompt. Use env vars in the Environment config.

4. **Add connectors you actually need**

   Only add Slack/Gmail/GitHub if the routine uses them. Unused connectors add surface area.

5. **Click Run now and watch the log**

   Fix any network, auth, or formatting issues before activating the schedule.

6. **Monitor the first week's runs**

   Edge cases surface early. Adjust the prompt based on what you see in the run logs.
