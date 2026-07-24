---
title: "Agent UX Patterns: Reasoning, Confidence, Approval & Tasks (Part 2)"
date_created: 2026-07-24
last_reviewed: 2026-07-24
status: current
domain: agentic-systems
doc_type: guide
topic_id: agent-ux-patterns-part2
supersedes: []
covers_version: "as of 2026-07-10"
---

# Agent UX Patterns: Reasoning, Confidence, Approval & Tasks (Part 2)

**This is Part 2 of 3. [Back to Part 1 ←](pathname:///archon/agentic-systems/agentic-ui/01-agent-ux-patterns) for copilot pattern taxonomy and streaming design.**

---

## 3. Reasoning Visualization

Showing the agent's reasoning is a UX decision with significant downstream effects on trust, cognitive load, regulatory posture, and usability.

### 3.1 Decision Framework: When to Show Reasoning

Decision matrix based on stakes and confidence:

LOW stakes, LOW confidence: Hide (show result only)
LOW stakes, HIGH confidence: Hide (clean UX)
HIGH stakes, LOW confidence: Collapsible summary (this is where users need to see reasoning)
HIGH stakes, HIGH confidence: Full structured reasoning required

**Show full reasoning when:**

- Stakes are high AND confidence is uncertain
- The user needs to validate the reasoning (regulated decision support)
- The output will be challenged by a downstream reviewer
- The user has explicitly requested an explanation

**Show collapsible summary when:**

- Stakes are high but confidence is high (senior expert validation scenario)
- The use case is developer / analyst tooling

**Hide reasoning when:**

- Simple fact retrieval (clutter greater than benefit)
- End-user consumer app with low technical literacy
- High-confidence, low-stakes generation (email autocomplete)
- Regulated contexts where showing reasoning implies AI autonomy

---

### 3.2 Reasoning Visualization Formats

| Format | Description | Best For | Implementation |
| -------- | ------------- | ---------- | --------------- |
| **Chain-of-thought text** | Narrative reasoning shown in expandable block | General explanation | `<details><summary>View reasoning</summary>` |
| **Execution step log** | Numbered steps with timestamps and tool calls | Audit, debugging | Structured log panel |
| **Planning tree** | Visual tree: goal → sub-goals → tasks | Complex multi-step plans | D3.js / Mermaid tree diagram |
| **Confidence bar** | Horizontal bar 0-100% per claim | Fact-checking, verification | CSS progress bar per sentence |
| **Source citations** | [1], [2] footnotes linking to source documents | RAG-based responses | Superscript links + citation panel |
| **Scratchpad panel** | Agent's full internal monologue | Developer/debug mode only | Collapsible pre-formatted block |

---

### 3.3 Reasoning Panel Example

RECOMMENDATION: Approve the vendor contract with standard terms. Est. savings: $240K.
Confidence: 78% (progress bar showing 6 of 10 filled)

View supporting evidence (3 sources):
[1] Vendor pricing analysis — last updated 3 days ago
    "Per-unit cost 18% below market median"
[2] Legal review — standard terms approved
[3] Procurement policy — threshold: $500K needs VP approval

View reasoning steps:
Step 1: Retrieved vendor history (3 contracts)
Step 2: Compared pricing vs. market benchmarks
Step 3: Checked against procurement policy limits
Step 4: Drafted recommendation with evidence

[Approve] [Request Changes] [Escalate]

---

## 4. Confidence and Uncertainty Visualization

### 4.1 Visual Encodings for Confidence

| Encoding | How It Works | Accessible | Over-used Risk |
| ---------- | ------------- | ------------ | ---------------- |
| Color gradient (green → red) | Hue shifts with confidence | Fails for color blindness | High — use sparingly |
| Fill level (bar/circle) | Area proportional to confidence | Good | Medium |
| Text label ("High/Medium/Low") | Categorical language | Excellent | Low |
| Numeric percentage (78%) | Raw probability | Good for experts | May false-precision |
| Star rating (★★★☆☆) | Familiar consumer metaphor | Good | Trivializes for high-stakes |
| Icon (shield/warning/info) | Category indicator | Excellent with alt text | Low |
| Hedging language ("probably", "it appears") | Natural language | Excellent | Risk of legal ambiguity |

**Best practice:** Combine fill level (for quick scan) + text label (for accessibility) + hedging in prose. Avoid numeric percentages for non-expert audiences unless calibration is verified.

---

### 4.2 Calibration Considerations

**Overconfidence is a UX hazard:** LLM confidence scores are frequently miscalibrated — a model that says 85% confidence may be right only 60% of the time in your domain. Always validate calibration on your golden dataset before displaying numeric confidence to users. Miscalibrated confidence erodes trust faster than no confidence display.

| Domain | Calibration Risk | Recommendation |
| -------- | ----------------- | ---------------- |
| Open-domain Q&A | High | Use categorical labels; no numeric |
| RAG over enterprise knowledge | Medium | Show after calibration on domain eval set |
| Structured extraction (form filling) | Low | Numeric % acceptable with validation |
| Medical / legal / financial | Very High | Never display confidence — show "verify with expert" |
| Code generation | Medium | Show test pass rate instead of confidence |

---

### 4.3 Multiple-Hypothesis Display

For decisions with genuine uncertainty, show multiple hypotheses rather than a single answer with confidence.

ANALYSIS RESULTS

Three interpretations are consistent with the data:

1. Supply chain disruption (most likely) — 65%
   Evidence: inventory drop, lead time increase

2. Demand spike in Q3 — 25%
   Evidence: order backlog increase

3. Reporting error — 10%
   Evidence: inconsistency in warehouse records

[Investigate #1] [Investigate #2] [Request manual audit]

---

### 4.4 "I Don't Know" UX Patterns

The most trust-building thing an agent can do is accurately communicate the limits of its knowledge.

| Scenario | Poor Response | Better Response |
| ---------- | -------------- | ----------------- |
| Out-of-training-data question | Hallucinated answer | "I don't have information about this. [Search live sources]" |
| Ambiguous query | Best-guess answer | "I'm not sure what you mean. Did you mean A or B?" |
| Document not retrieved | Answer from training data | "I couldn't find relevant documents. I'm answering from general knowledge — verify before acting." |
| Conflicting sources | Arbitrary choice | "Sources disagree. Source A says X; Source B says Y. [Show both]" |
| Low confidence retrieval | Confident wrong answer | "I found this, but I'm not confident it's relevant. [Review source]" |

---

## 5. Human Approval UX

Approval UX is the most consequential pattern in agentic applications. Poor approval design leads to rubber-stamping (users approve without reading), approval fatigue, and compliance failures.

### 5.1 Approval Request Design Principles

Every approval request must answer four questions immediately visible without scrolling:

1. **What** is the agent asking to do?
2. **Why** is it asking to do this?
3. **What happens if I approve?** (Consequence)
4. **What happens if I reject?** (Alternative path)

Example approval dialog:

WARNING: ACTION REQUIRED: File Deletion

WHAT: Delete 47 files in /reports/archive/2021/
WHY: Your storage cleanup request (Task #4 of 8)
RISK: This action cannot be undone
IF NO: Skip this folder; continue with next task

[View file list (47)]

[Approve (A)] [Skip (S)] [Stop task (X)]

Respond within: 23:47 or task will pause

---

### 5.2 Approval Flow Types

| Flow Type | Description | When to Use | Risk |
| ----------- | ------------- | ------------- | ------ |
| **Single-click approve** | One button approves and executes | Low-risk, well-understood actions | Rubber-stamping |
| **Review-and-approve** | User must view detail before approve button activates | Medium-risk actions | Slower, more friction |
| **Dual confirmation** | Two separate "Approve" clicks required | High-risk irreversible actions | Friction may block legitimate use |
| **Typed confirmation** | User types action name to confirm | Catastrophic-risk actions (delete all, send to all) | High friction — reserve for nuclear options |
| **Delegated approval** | Routes to a different user (manager, admin) | Actions beyond user's authorization | Workflow delay |
| **Async approval** | Approval request sent via email/Slack/notification | User is not online / long-running tasks | Session management complexity |

---

### 5.3 Approval for High-Risk Tool Categories

| Tool Category | Risk Level | Required Approval Model | Audit Requirement |
| --------------- | ----------- | ------------------------ | ------------------- |
| Read data | None | No approval | Log only |
| Create (new record, new file) | Low | HOTL or HITL | Log |
| Update existing record | Medium | HITL | Log + before/after diff |
| Send communication (email, Slack) | Medium–High | HITL review-and-approve | Log + content capture |
| Delete data | High | Dual confirmation | Log + content backup |
| Financial transaction | Very High | Delegated approval (finance) | Full audit + reconciliation |
| Publish externally | High | Delegated approval (comms/legal) | Log + content snapshot |
| Grant access / permissions | Very High | Delegated approval (security) | Log + justification |
| Execute code | Very High | Typed confirmation | Log + code capture |

---

### 5.4 Batch Approval

For autonomous workflows generating multiple pending approvals:

PENDING APPROVALS (12 items) [Approve All]

- [ ] Update vendor record — Acme Corp (Low risk)
- [ ] Update vendor record — Beta Systems (Low risk)
- [ ] Send renewal notice — Acme Corp (Medium risk)
- [x] Delete archive /2019/Q1 (47 files) (High risk)
- [ ] Send renewal notice — Beta Systems (Medium risk)
- ... 7 more

[Approve Selected (1)] [Review Individual]

Note: "Approve All" excludes High Risk items

**Batch approval rules:**

- "Approve All" must exclude HIGH RISK items — these always require individual review
- Group items by risk level for visual triage
- Show aggregate consequence ("this will send 23 emails")
- Provide bulk-reject for all low-risk items in one action

---

### 5.5 Approval Timeout and Escalation

| Timeout State | Duration | Behavior |
| -------------- | ---------- | ---------- |
| First warning | 80% of timeout | "This approval will expire in 5 minutes" |
| Second warning | 95% of timeout | Visual urgency indicator (amber) |
| Timeout | 100% | Task pauses. Escalation notification sent. |
| Escalation wait | Configurable | Routes to backup approver |
| Final timeout | Configurable | Task cancelled. Audit log entry. |

**Escalation Chain Design:** Define a 3-level escalation chain for every autonomous task: primary approver → manager → task owner. Undeclared escalation chains are an operational risk for long-running autonomous workflows.

---

### 5.6 Audit Trail for Approvals

Every approval decision must be persisted with:

| Field | Content |
| ------- | --------- |
| `approval_id` | UUID |
| `task_id` | Parent task or agent run ID |
| `tool_call_id` | Specific tool call being approved |
| `tool_name` | Name of the tool |
| `tool_parameters` | Exact parameters (sanitized for PII if required) |
| `approver_id` | User identity (not just display name) |
| `decision` | `approved` / `rejected` / `modified` / `escalated` |
| `decision_at` | ISO 8601 timestamp |
| `response_time_seconds` | Time from request to decision |
| `context` | Screenshot or structured snapshot at time of request |
| `notes` | Optional user comment |

---

## 6. Long-running Task UX

### 6.1 Progress Visualization Patterns

Contract Analysis — 247 documents
Started: 14:32 | Est. completion: 15:45

Progress: 78% (192/247 docs)

CURRENT: Analyzing "Q3 2024 MSA - Vertex Corp.pdf"

COMPLETED MILESTONES
- Document ingestion — 14:32 (3 min) DONE
- Clause extraction — 14:40 (8 min) DONE
- Risk scoring — 14:48 (in progress)
- Summary report — (pending)
- Dashboard update — (pending)

[Pause] [View partial results] [Cancel]

| Progress Element | Required | Recommended When |
| ----------------- | ---------- | ----------------- |
| Overall % bar | Always | Any task greater than 10 seconds |
| Milestone list | Yes | Tasks with 3+ distinct phases |
| Current item name | Yes | Batch processing tasks |
| Time elapsed / estimated | Yes | Tasks greater than 1 minute |
| Items completed / total | Yes | Enumerable batch tasks |
| Cost consumed (tokens/$) | Optional | Developer / admin view |

---

### 6.2 Background Task Management

Minimized Task Bar: [Contract Analysis 78%] [Code Review Done ✓]

**Background task lifecycle:**

| State | Visual | Action Available |
| ------- | -------- | ----------------- |
| Running | Animated progress indicator | Pause, View, Cancel |
| Paused | Static progress bar (amber) | Resume, Cancel |
| Awaiting approval | Bell icon (red badge) | Review + Approve |
| Completed | Green check | View results, Dismiss |
| Failed | Red X | View error, Retry |
| Cancelled | Gray dash | — |

---

### 6.3 Notification Fallback

When the user is not active in the application, task completion must reach them through ambient channels.

| Delivery Channel | Trigger | Content |
| ---------------- | --------- | --------- |
| In-app toast | User active, task completes | "Contract analysis complete — 12 high-risk clauses found" |
| Browser push notification | User has tab open, focus elsewhere | Title + one-line summary |
| Email digest | User offline greater than 15 minutes | Subject, summary, link to results |
| Slack DM | User has Slack integration configured | Summary card + "View Results" button |
| Mobile push | User has mobile app installed | Summary + deep link to task result |



---

**This is Part 2 of 3. [Continue with Part 3 →](pathname:///archon/agentic-systems/agentic-ui/parts/01-agent-ux-patterns-part3) for multi-agent collaboration, undo/replay, audit UX, error handling, accessibility, and anti-patterns.**
