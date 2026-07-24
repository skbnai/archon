---
title: "Agent UX Patterns: Multi-Agent, Operations & Reference (Part 3)"
date_created: 2026-07-24
last_reviewed: 2026-07-24
status: current
domain: agentic-systems
doc_type: guide
topic_id: agent-ux-patterns-part3
supersedes: []
covers_version: "as of 2026-07-10"
---

# Agent UX Patterns: Multi-Agent, Operations & Reference (Part 3)

**This is Part 3 of 3. [Back to Part 2 ←](pathname:///archon/agentic-systems/agentic-ui/parts/01-agent-ux-patterns-part2) for reasoning, confidence, approval, and long-running task UX.**

---

## 7. Multi-agent Collaboration UX

### 7.1 Agent Handoff Visualization

**Active Agents:**
- Orchestrator: "Analyze contract and identify risks"
  - Legal Analyst: Reading clauses (Progress: 3/12 sections)
  - Risk Scorer: Waiting for clauses

**Message Bus:**
- 14:32:41 Orchestrator → Legal Analyst: "Start clause analysis..."
- 14:33:15 Legal Analyst → Risk Scorer: "Clause 3: payment terms identified"

**Actions Available:** [Intervene] [View full message log] [Stop all]

### 7.2 Multi-agent Status Dashboard

| Dashboard Element | Content | Refresh |
| ------------------ | --------- | --------- |
| Agent status grid | Name, state, current task, last action | Real-time |
| Inter-agent message feed | Timestamped messages between agents | Real-time |
| Shared workspace panel | Files/data being worked on | Real-time |
| Conflict alerts | When two agents modify the same resource | Immediate |
| Resource consumption | Token usage, API calls per agent | Per-turn |
| Human approval queue | Pending approvals from any agent | Real-time |

---

## 8. Undo, Replay, and Checkpoint UX

### 8.1 What Can and Cannot Be Undone

| Action Type | Undoable? | Recovery Path |
| ------------- | ----------- | --------------- |
| Text generation in chat | Yes | Delete message; regenerate |
| File created by agent | Yes | Agent-initiated delete |
| File modified by agent | Yes | Restore from checkpoint |
| Email sent by agent | No | Draft was stored; send notification only |
| Database record updated | Depends | If event-sourced: yes. CRUD: requires backup |
| External API call | No | Log the call; manual reversal only |
| Payment initiated | No | Cancellation via financial system; not agent |
| Slack message sent | No | Delete via Slack API (time-limited) |

---

### 8.2 Conversation Branching

**Conversation Timeline:**

- Turn 1: "Analyze Q3 contracts"
- Turn 2: [Agent returns analysis]
- Turn 3: "Focus on payment terms" (BRANCH POINT)
  - Branch A: "Focus on liability" (current)
  - Branch B: "Focus on payment terms" (fork from here)

**Branch controls:**

- Every message in history shows a "Fork from here" icon on hover
- Branching creates a new conversation tab with the shared prefix
- Side-by-side comparison mode shows branch A vs. branch B responses
- Branches are named automatically ("Branch from Turn 3") and can be renamed

---

### 8.3 Checkpoint UX

| Checkpoint Feature | Description |
| ------------------- | ------------- |
| **Auto-checkpoint** | System creates checkpoint at every tool call and major milestone |
| **Named checkpoint** | User clicks "Save checkpoint" and names it ("Before risk analysis") |
| **Checkpoint list** | Timeline showing all checkpoints with metadata |
| **Restore** | One click loads checkpoint; current state is auto-saved before restore |
| **Compare** | Side-by-side view of agent state at two checkpoints |
| **Re-run from checkpoint** | Re-execute from a checkpoint with modified parameters |

---

## 9. Audit UX

### 9.1 Audit View Components

**Agent Audit View**

| Field | Value |
| --- | --- |
| Session | AGT-2024-09-15-0042 |
| User | sarah.chen@corp.com |
| Started | 2024-09-15 14:32 UTC |
| Duration | 18m 42s |
| Status | Completed |
| Risk Score | 2/10 (Low) |

**Event Timeline:**

- 14:32:00 Session started. User query: "Analyze Q3 vendor contracts for renewal"
- 14:32:15 Tool: search_documents. Query: "vendor contracts 2024 Q3". Result: 23 documents found [View]
- 14:33:42 Tool: read_document. File: "MSA_AcmeCorp_2024.pdf". Pages: 1-24 [View]
- 14:35:11 APPROVAL REQUESTED. Action: Update contract status to "Under Review". Approver: sarah.chen@corp.com. Decision: Approved at 14:35:24 (13 seconds) [View]
- 14:50:41 Final output generated [View]
- 14:50:41 Session ended

**Available Actions:** [Export CSV] [Export PDF] [Send to compliance inbox]

---

### 9.2 Compliance Evidence Export

| Export Format | Content | Use For |
| -------------- | --------- | --------- |
| CSV | Structured log of all tool calls and approvals | SIEM integration, bulk analysis |
| PDF report | Human-readable audit report with signatures | Regulatory submission, legal proceedings |
| JSON trace | Full structured event stream | Technical audit, LLM training |
| Screenshots | Visual captures of approval dialogs | Evidence in disputes |

---

## 10. Failure and Error UX

### 10.1 Error Classification by User Impact

| Error Class | Example | User Impact | UX Response |
| ------------- | --------- | ------------ | ------------- |
| **Transient** | API timeout | Minor delay | Auto-retry silently; show spinner |
| **Recoverable** | Rate limit | Short delay | "Retrying (1/3)..." |
| **Content error** | LLM refused request | Task fails | "I can't help with this. [Why?] [Try differently]" |
| **Tool failure** | Database connection lost | Partial result | "Could not access X. Showing partial results." |
| **Partial failure** | 4 of 8 steps completed | Incomplete result | "Completed 4/8 steps. Failed: 5-8. [View] [Retry failed steps]" |
| **Fatal** | Session corrupt | Full task failure | "Something went wrong. Progress saved. [Resume] [Start over]" |

---

### 10.2 Error Message Design

Good error messages answer: what happened, why it happened, what user can do.

| Anti-pattern | Example | Better |
| ------------- | --------- | -------- |
| Technical jargon | "500 Internal Server Error" | "Something went wrong on our end. Please try again." |
| Vague failure | "An error occurred" | "The document search failed because the knowledge base is temporarily unavailable." |
| No action offered | "This failed." | "The search failed. [Retry] [Search differently] [Ask for help]" |
| Blaming user | "Your request was malformed" | "I didn't understand that request. Could you rephrase it?" |
| Missing context | "Rate limit exceeded" | "I'm processing too many requests right now. I'll continue automatically in about 30 seconds." |

---

## 11. Accessibility for Agentic UIs

### 11.1 WCAG 2.1 AA Requirements Specific to Agentic UX

| Agentic UX Element | WCAG Criterion | Implementation |
| -------------------- | --------------- | ---------------- |
| Streaming text | 4.1.3 Status Messages | ARIA live region: aria-live="polite" for streaming, "assertive" for errors |
| Approval dialogs | 2.1.1 Keyboard, 2.4.3 Focus Order | Trap focus in modal, approve/reject on Enter/Escape |
| Confidence indicators | 1.4.1 Use of Color | Never color alone, include text label or icon + text |
| Progress bars | 4.1.3 Status Messages | role="progressbar" with aria-valuenow/valuemin/valuemax |
| Tool call callouts | 1.3.1 Info and Relationships | Semantic aside or role="status" |
| Agent status icons | 1.1.1 Non-text Content | aria-label on all icon-only indicators |
| Cancel/stop button | 2.1.1 Keyboard | Always keyboard-accessible, never icon-only |
| Notification toasts | 4.1.3 Status Messages | role="alert" for urgent, role="status" for informational |

---

### 11.2 Screen Reader Support for Streaming Content

Use ARIA pattern: div role="log" aria-live="polite" aria-label="Agent response" with token-by-token content appended. For tool call status: div role="status" aria-live="polite" aria-atomic="true". For approval dialogs: dialog aria-modal="true" aria-labelledby="approval-title".

---

### 11.3 Color-blind Accessible Confidence Indicators

| Confidence Level | Color (WCAG AA) | Icon | Text Label |
| --- | --- | --- | --- |
| Very High (90-100%) | #2E7D32 (green, 4.5:1) | Shield | "Very High" |
| High (70-89%) | #1565C0 (blue, 5.1:1) | Trend up | "High" |
| Medium (40-69%) | #E65100 (orange, 3.1:1) | Wavy | "Medium" |
| Low (20-39%) | #B71C1C (red, 5.8:1) | Trend down | "Low" |
| Very Low (<20%) | #4A148C (purple, 7.3:1) | Question | "Very Low" |

Use fill level as primary encoding. Color is secondary. Text label always present.

---

## 12. Agent UX Anti-patterns

### 12.1 Complete Anti-pattern Catalog

| # | Anti-pattern | Severity | Description | Mitigation |
| --- | ------------- | ---------- | ------------- | ------------ |
| 1 | **Ghost approvals** | Critical | Approval dialogs auto-close or disappear before reading | Set minimum display time (3s), no auto-close |
| 2 | **Confirmation fatigue** | High | Every trivial action requires approval, trains users to click through | Calibrate approval thresholds, use HOTL for low-risk |
| 3 | **Silent tool execution** | High | Agent calls APIs or mutates data without visibility | Always surface tool calls to users |
| 4 | **Hallucinated citations** | High | Agent fabricates document references in citation list | Verify all citations against retrieved chunks |
| 5 | **Anthropomorphism overflow** | Medium | Agent uses first-person emotional language | Keep agent persona professional, avoid emotional language |
| 6 | **Streaming wall of text** | High | Agent streams 2000+ word responses with no structure | Enforce response length limits, use structured output |
| 7 | **Context collapse** | High | Agent appears to remember what it cannot | Clearly indicate what session context is in use |
| 8 | **Overconfident errors** | Critical | Agent states incorrect facts with high confidence | Implement uncertainty-aware prompting, validate before rendering |
| 9 | **Approval without consequence** | Critical | Approval dialog doesn't state what happens if approved | Every approval dialog must show consequence |
| 10 | **No undo for mutations** | High | Agent modifies data with no way to reverse | Implement pre-action snapshots, offer undo within 30 seconds |
| 11 | **Invisible agent identity** | Medium | User cannot tell which AI/agent/model produced output | Always show agent identity in response header |
| 12 | **Missing stop button** | High | User cannot cancel a running task | Stop button always visible during active task |
| 13 | **Streaming jank on mobile** | Medium | Character-level streaming causes layout thrash on mobile | Use word-buffered streaming on mobile |
| 14 | **Progress bar that never moves** | Medium | Progress bar stuck at 0% or 99% for long periods | Use milestone-based progress, reflect real state |
| 15 | **Error messages in logs only** | High | Errors visible only in console or server logs | Surface all user-impacting errors in UI |
| 16 | **Reasoning shown always** | Medium | Every response shows full chain-of-thought | Gate reasoning display on stakes × confidence matrix |
| 17 | **Multi-agent confusion** | Medium | User cannot tell which agent is speaking | Prefix each agent message with name/role |
| 18 | **Async task orphan** | High | Background tasks continue after user logs out | Tie task lifecycle to session, email completion |
| 19 | **No audit export** | High | Audit log exists but cannot be exported by user | Provide CSV/PDF export from every audit view |
| 20 | **Color-only confidence** | Medium | Confidence shown only as color without text/icon | Add text label to all confidence indicators |
| 21 | **Keyboard trap in modal** | High | Approval dialog cannot be dismissed with keyboard | Implement focus trap with Escape to close/reject |
| 22 | **Streaming ARIA spam** | Medium | Screen reader announces every token | Use aria-live="polite" only, batch updates |
| 23 | **Implied causality** | Medium | UI implies agent caused outcome that was coincidental | Be precise: "The agent suggested X" not "achieved Y" |
| 24 | **Tool parameter leakage** | High | Internal parameters (API keys, IDs) shown in tool UI | Sanitize tool call display, show user-facing summaries |
| 25 | **Perpetual loading state** | Medium | Task appears running forever with no update | Auto-escalate tasks > 2× estimated duration |
| 26 | **No empty state for agent list** | Low | Multi-agent dashboard shows blank page before start | Always show agent roster with pending/queued states |
| 27 | **Approval context missing** | High | Approval dialog shows action with no context | Include task goal and reasoning summary in every approval |
| 28 | **Irreversible default** | High | Default action in approval dialog is destructive | Place destructive action as secondary, safe as primary |

---

### 12.2 Getting Started with UX Pattern Selection

For a new agentic application, start with the **Copilot Pattern Taxonomy** (Part 1, Section 1) to identify your deployment archetype. Use the **Decision Framework** guide for technology selection. For lifecycle planning, see application-lifecycle documentation.

**Protocol Reference:** AG-UI event types throughout this document (TEXT_MESSAGE_CONTENT, TOOL_CALL_START, STATE_SNAPSHOT, etc.) are specified in the AG-UI open protocol. MCP integration patterns are detailed in MCP Deep Guide.

---

**[Back to Part 1 ←](pathname:///archon/agentic-systems/agentic-ui/01-agent-ux-patterns) for copilot patterns and streaming UX design. [Back to Part 2 ←](pathname:///archon/agentic-systems/agentic-ui/parts/01-agent-ux-patterns-part2) for reasoning, confidence, approval, and long-running task UX.**
