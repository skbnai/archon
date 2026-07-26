---
title: 'Claude Routines — Complete Help Guide (Part 1)'
doc_type: guide
domain: agentic-systems
topic_id: claude-routines-guide
status: current
date_created: 2026-07-24
last_reviewed: 2026-07-24
supersedes:
  - docs/coding-tools/claude/claude_routines_guide.md
---

# Claude Routines — Complete Help Guide

**This is Part 1 of 2. [Continue with Part 2 →](pathname:///archon/agentic-systems/coding-tools/parts/37-claude-routines-guide-part2) for design patterns, anti-patterns, and quick reference.**

The complete guide to automated, persistent AI workflows — from in-session /loop commands to cloud-native Routines that run while your laptop is closed.

- Cloud-managed infrastructure
- Schedule, API, GitHub webhooks
- Pro plan required ($20/mo)
- v2.1.72+ required for /loop

## Three Scheduling Tiers

### /loop — CLI / Session

Quick, in-session polling. Lives inside an active terminal and stops when you exit.

- Runs on your machine
- Machine must be on: Yes
- Session required: Yes
- Min interval: 1 minute
- Max tasks: 50 per session
- Auto-expires: 7 days

**Example:** `/loop 5m check deploy`

### Desktop Scheduled Tasks

Persistent local tasks. Survive restarts. Fire each session at your chosen interval with full local file access.

- Runs on your machine
- Machine must be on: Yes
- Session required: No
- Min interval: 1 minute
- Local files: Yes
- Worktree isolation: Supported

Navigate to Sidebar → Schedule → + New task

### Cloud Routines

Runs on Anthropic's managed infrastructure. Laptop can be closed. Trigger by schedule, API call, or GitHub event.

- Runs on Anthropic cloud
- Machine must be on: No
- Session required: No
- Min interval: 1 hour
- Local files: No (fresh clone)
- GitHub trigger: Yes

Use `/schedule` or `claude.ai/code/routines`

## Which Should You Use?

| Scenario | Best Tier | Why |
|----------|-----------|-----|
| Poll deployment for 20 minutes | `/loop 5m` | Session-scoped, simple, zero setup |
| Daily 7am standup briefing | Desktop Task | Local calendar/Slack access, persistent schedule |
| Nightly security scan at 2am | Cloud Routine | Laptop closed; must run unattended |
| Auto-review every new PR | Cloud Routine | GitHub webhook trigger, runs in cloud per event |
| Run on external system trigger | Cloud Routine | API trigger accepts any HTTP POST |
| Babysit a long-running test | `/loop 10m` | Interactive, can cancel with Esc |

---

## Cloud Routines — What They Are

Cloud Routines (launched April 14, 2026 as a research preview) run on Anthropic's managed infrastructure. You configure a prompt, repository, and connectors once — then the routine executes on its own trigger without any active session or open laptop required.

**The key difference from traditional automation:** a Routine is an agent, not a script. It receives a prompt and decides how to reach the outcome. It can reason about what it encounters, self-heal errors, and adapt execution to context — unlike a GitHub Actions workflow that runs commands you pre-defined.

### Anthropic-Managed Infrastructure

You don't provision servers, configure environments, or manage cron infrastructure. Anthropic handles the execution environment, container lifecycle, and retry logic. The execution environment is a fresh, sandboxed container with a fresh repository clone on each run.

### No Local File Access

Cloud Routine containers clone your repository fresh on each run. They cannot access files from your local machine, local MCP servers, or local plugin configs. Skills must be stored in the repository or a secondary repository. See Skills in Routines for the workaround pattern.

---

## Trigger Types

A single Routine can combine multiple trigger types. GitHub triggers have per-routine and per-account hourly caps during preview — events beyond the limit are dropped until the window resets.

### Schedule Trigger

Time-based recurring execution. Use presets (Hourly, Daily, Weekdays, Weekly) or any valid 5-field cron expression.

- Min interval: 1 hour
- Cron syntax: standard 5-field
- Sub-hourly cron rejected

### API Trigger

HTTP POST to a per-routine endpoint with a bearer token. Any external system — Jenkins, Slack bot, monitoring tool — can fire a Routine.

- Method: POST
- Auth: Bearer token
- Body: optional context JSON

### GitHub Event Trigger

Fire on PR opened, PR merged, release published, push, and other repository events. Branch security: Claude pushes only to `claude/`-prefixed branches by default.

**Branch Security Default:** By default Claude can push only to branches prefixed `claude/`. This prevents a poorly written routine from touching `main`. Disable only where you have robust downstream review processes.

---

## Core Components of a Routine

Every Routine has four configurable parts. Getting these right is the difference between a routine that runs reliably and one that fails silently.

### Prompt

Natural language instructions describing what Claude should do. Since the routine runs autonomously, the prompt must be **fully self-contained** — explain what to do, what to verify, how success looks, and how to handle edge cases. No references to context missing from the clean cloud session.

### Triggers

The event that starts the routine. Schedule (recurring), GitHub Event (PR, push, release), or API (HTTP endpoint). A single routine can combine multiple triggers. GitHub and API triggers must be configured in the web UI.

### Environment

The sandboxed execution context. Configure: **Network access** (blocked by default, or allowlisted domains / trusted / full), **environment variables** for secrets and API keys, and **setup scripts** that run before Claude Code launches.

### Connectors

Pre-built integrations with external services. Currently: **Slack** (read/write), **Gmail**, **Google Calendar**, **GitHub** (full repo access). Each connector provides tools Claude can call natively within the routine.

### Network Access Modes

| Mode | What's Allowed | Best For |
|------|--------|----------|
| Blocked (default) | No outbound requests | Pure code analysis, no external data needed |
| Custom (allowlist) | Only specified domains | RSS feeds, specific APIs — most secure option |
| Trusted | Pre-approved Anthropic list | Common services without custom allowlisting |
| Full | Unrestricted internet | General research; use with caution |

---

## Creating Your First Routine

### Method 1 — CLI (Schedule triggers only)

```bash
# One-liner — Claude parses, asks clarifying questions, creates the routine
/schedule Create a daily 9am trigger that fetches RSS from JavaScript Weekly,
picks 10 good articles for YouTube, and sends to Slack #dev-feed

# Or from any active session — creates a cloud routine, not a local task
/schedule daily PR review at 9am on weekdays
```

**Claude asks clarifying questions:** After your `/schedule` command, Claude will ask clarifying questions to fill in details (destination channel, selection criteria, etc.) before creating the routine. Answer them, and Claude confirms creation and provides a link to manage it in the web UI.

### Method 2 — Web UI (all trigger types)

1. **Navigate to Routines**

   Go to `claude.ai/code/routines` and click **New routine**. This is the only place to create API or GitHub event triggers.

2. **Write your prompt**

   Be specific and self-contained. Include: what to do, what success looks like, how to handle edge cases, and what outputs to produce. The routine runs without you present.

3. **Choose your trigger(s)**

   Select Schedule (cron preset or custom expression), GitHub Event (pick event type and repository), or API (generates a bearer-token endpoint). You can combine multiple triggers on one routine.

4. **Configure the environment**

   Add network access if the task fetches external data. Set environment variables for API keys and secrets. Add a setup script if the routine needs dependencies installed before Claude launches.

5. **Add connectors**

   Connect Slack, Gmail, or GitHub to give Claude tools it can call. Each connector grants specific read/write actions in that service.

6. **Test with Run now**

   Hit **Run now** before relying on the schedule. Watch the live log — if an approach fails, Claude self-corrects and retries. Fix any issues (network access, connector auth, prompt ambiguities) now.

**Always run at least one manual test:** Edge cases appear in the first week. Catching permission issues, connector auth problems, and output formatting errors (e.g., Slack's `invalid_blocks` from `---` dividers) in a test run costs nothing. Catching them after the routine has been running for a week costs much more.

---

## Plan Limits & Pricing

| Plan | Runs per day | Cost |
|------|-------------|------|
| Free | — | $0/mo |
| Pro | 5 | $20/mo |
| Max | 15 | $100/mo |
| Team / Enterprise | 25 | Custom |

**Metered Overage Available:** Routines draw down the same subscription limit as interactive sessions. Organizations with extra usage enabled can go past the cap at metered overage rates. Monitor usage at `claude.ai/settings/usage`. GitHub triggers have additional per-routine and per-account hourly caps — events beyond the limit are dropped until the window resets.

### Token Cost Per Run

Each Routine run consumes inference tokens based on: the prompt length, any context Claude reads (repository files, fetched URLs), and the output it produces. There's no separate fee for Routines — you pay standard Claude API rates for usage. A large `CLAUDE.md` file consumes a significant portion of the session token budget on every run — keep it concise for cloud contexts.

---

## /loop — Session Scheduling

The `/loop` bundled skill is the quickest way to run a prompt on repeat within an active session. Both interval and prompt are optional.

| Command | Behavior |
|---------|----------|
| `/loop 5m check if the deployment finished` | Fixed interval — runs every 5 minutes |
| `/loop check if the deployment finished` | Dynamic interval — Claude chooses delay based on what it observes |
| `/loop 20m /review-pr 1234` | Re-runs a slash command on a schedule |
| `/loop` | Runs built-in maintenance prompt (PR triage, bug hunts) at dynamic interval |
| `/loop 15m` | Runs built-in maintenance prompt every 15 minutes |

### Interval Units

Examples:

```bash
/loop 30s  # 30 seconds — rounded up to 1 minute (cron minimum)
/loop 5m   # Every 5 minutes
/loop 2h   # Every 2 hours
/loop 1d   # Once per day
# Intervals like 7m are rounded to nearest clean cron step — Claude tells you what it picked
```

### Dynamic Interval Behavior

When you omit the interval, Claude chooses a delay between 1 minute and 1 hour based on what it observes: short waits while a build is active, longer waits when nothing is pending. Claude may use the **Monitor tool** instead of polling — which streams background script output and is more token-efficient for event-driven watching.

### Stopping a Loop

Press `Esc` to stop a `/loop` while it's waiting for the next iteration. This clears the pending wakeup. Tasks you scheduled by asking Claude directly (e.g. "remind me at 3pm") are _not_ affected by Esc — cancel those explicitly.

---

## Cron Expression Reference

Standard 5-field cron expressions. All times use your local timezone for `/loop` and Desktop tasks; UTC for Cloud Routines. Cloud Routines reject expressions that run more frequently than once per hour.

**Format: minute hour day-of-month month day-of-week**

Fields support: `*` (wildcard), single values (`5`), steps (`*/15`), ranges (`1-5`), comma lists (`1,15,30`). Day-of-week: `0` or `7` = Sunday. Extended syntax like `L`, `W`, `?`, and name aliases (`MON`, `JAN`) are NOT supported.

### Common Cron Expressions

| Expression | Time | Use Case |
|-----------|------|----------|
| `0 9 * * 1-5` | 9:00 AM every weekday | Daily standup briefing |
| `0 2 * * *` | 2:00 AM every night | Nightly security scan |
| `0 8 * * 1` | 8:00 AM every Monday | Weekly review digest |
| `0 * * * *` | Every hour (top of hour) | Use `3 * * * *` to avoid jitter |
| `0 18 * * 5` | 6:00 PM every Friday | End-of-week PR summary |
| `0 9,17 * * 1-5` | 9 AM and 5 PM on weekdays | Twice-daily email triage |
| `30 6 1 * *` | 6:30 AM on the 1st of each month | Monthly report generation |

**Jitter Awareness:** The scheduler adds a small deterministic offset to fire times. Recurring tasks may fire up to 10% of their period late (capped at 15 min). One-shot tasks at :00 or :30 fire up to 90 seconds early. To avoid jitter: use minutes like `3 9 * * *` instead of `0 9 * * *`.

---

## Customizing /loop with loop.md

A `loop.md` file replaces the built-in maintenance prompt with your own default. It defines the prompt for a bare `/loop` invocation. It is ignored when you supply a prompt on the command line.

| Path | Scope |
|------|-------|
| `.claude/loop.md` | Project-level. Takes precedence when both exist. |
| `~/.claude/loop.md` | User-level. Applies in any project without its own. |

### Example: Release branch keeper

```
Check the `release/next` PR. If CI is red, pull the failing job log,
diagnose, and push a minimal fix to a `claude/fix-*` branch. If new review
comments have arrived, address each one and resolve the thread.
If everything is green and quiet, say so in one line.

# Constraints
- Never push directly to `main` or `release/next`
- Only fix failures you can diagnose from the log alone
- If the fix requires context you don't have, leave a comment and stop
```

**Size Limit:** Content beyond 25,000 bytes is truncated. Keep `loop.md` concise. Edits take effect on the next iteration — you can refine instructions while a loop is running.

---

## One-Time Reminders

For single-fire tasks, use natural language directly — no `/loop` needed. Claude schedules a single-fire task that deletes itself after running.

### Natural language examples

```bash
# Relative time
in 45 minutes, check whether the integration tests passed

# Absolute time
remind me at 3pm to push the release branch

# After an event
when the CI run finishes, tell me the result and suggest next steps
```

Claude pins the fire time to a specific minute using a cron expression and confirms when it will fire. One-shot tasks resume on `--resume` or `--continue` if the scheduled time hasn't passed yet. Background Bash and Monitor tasks are never restored on resume.

## Related

- [Claude Code CLI — Zero to Mastery 2026](33-claude-code-complete-2026.md) — the broader Claude Code guide this routines feature is part of.
