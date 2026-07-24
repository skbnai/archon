---
title: "Agent UX Patterns: Copilot Taxonomy (Part 1)"
date_created: 2026-07-24
last_reviewed: 2026-07-24
status: current
domain: agentic-systems
doc_type: guide
topic_id: agent-ux-patterns
supersedes:
  - ../knowledge-docs/docs/agentic-ui/agent-ux-patterns.md
covers_version: "as of 2026-07-10"
---

# Agent UX Patterns: Copilot Taxonomy (Part 1)

**Audience:** UX leads, product owners, and principal AI architects designing the human-facing layer of enterprise agentic applications.

**Related:**
[HITL Gates](pathname:///archon/architecture/23-agentic-ai-landing-zone-business-layer) |
[Memory Architecture](pathname:///archon/architecture/41-agent-memory-planning-architecture) |
[Security/OWASP](pathname:///archon/architecture/43-agentic-ai-reliability-observability-governance) |
[Governance](pathname:///archon/architecture/51-enterprise-ai-governance-compliance) |
[Observability](pathname:///archon/architecture/43-agentic-ai-reliability-observability-governance)

---

## 1. Copilot Pattern Taxonomy

Twelve canonical deployment archetypes. Every enterprise agentic application maps to one or more of these patterns. Use the table as a first-pass filter, then consult the detailed profiles below.

### 1.1 Summary Table

| # | Pattern | Autonomy Level | UX Surface | Primary Audience | Integration Point |
| --- | --------- | --------------- | ------------ | ----------------- | ------------------- |
| 1 | Chat Copilot | Low | Full-page chat | End users, knowledge workers | Standalone app or tab |
| 2 | Embedded Copilot | Low–Medium | Inline within host app | Power users, developers | Host app sidebar/toolbar |
| 3 | Floating Copilot | Low–Medium | Overlay on any page | All users | Browser extension / iframe |
| 4 | Workspace Copilot | Medium | Unified workspace panel | Knowledge workers | Document, calendar, email |
| 5 | Workflow Copilot | Medium–High | Step-driven wizard | Process workers | BPM / workflow engine |
| 6 | Decision Copilot | Medium | Structured recommendation panel | Analysts, managers | BI / dashboards |
| 7 | Coding Copilot | Medium | IDE inline + chat | Developers | IDE extension |
| 8 | Search Copilot | Low–Medium | SERP augmentation | All users | Search results page |
| 9 | Voice Agent | Medium | Voice + minimal visual | Field workers, drivers | Audio channel |
| 10 | Visual Agent | Medium | Image canvas + chat | Designers, analysts | Design / data tools |
| 11 | Multi-agent Dashboard | High | Status board | AI ops, platform teams | Orchestration layer |
| 12 | Autonomous Copilot | Very High | Notification surface only | Managers, approvers | Background process |

---

### 1.2 Pattern Profiles

#### Pattern 1 — Chat Copilot

**Definition:** A standalone conversational interface. The agent has no ambient context beyond what the user types and what is injected into the system prompt.

**Deployment Context:** Dedicated app, enterprise portal tab, or public-facing chatbot.

**UX Characteristics:** Linear conversation history, turn-by-turn interaction model, persistent message list with timestamps, file/image upload support for multimodal input, copy/cite/regenerate controls per message.

**AG-UI Integration Pattern:** Bidirectional streaming via AG-UI `TEXT_MESSAGE_CONTENT` and `TOOL_CALL_START/END` events. Session stored client-side or in backend session store keyed to user identity.

**A2UI Integration Pattern:** Agent may emit `GenerateUI` events to render structured forms, cards, or data tables inline in the chat thread.

**Recommended Approval Model:** Human-on-the-loop (HOTL) for read-only operations. Human-in-the-loop (HITL) for any write action (send email, create ticket, post to Slack).

**Example Products:** Claude.ai, ChatGPT, Microsoft Copilot standalone.

**When to use:** Users need an open-ended conversational interface, no ambient host application context, first deployment of AI, use case is primarily knowledge retrieval/writing/analysis.

---

#### Pattern 2 — Embedded Copilot

**Definition:** The agent UI is embedded within an existing application as a persistent sidebar, inline suggestion overlay, or contextual panel. The host application passes ambient context (current document, selected code, open ticket) to the agent automatically.

**Deployment Context:** IDE plugins, document editors, CRM panels, ticketing systems.

**UX Characteristics:** Triggered by hotkey/selection/ambient context change, inline suggestion acceptance (Tab/ESC), contextual actions ("Explain this", "Fix this", "Summarize"), minimal chrome blending into host app design system, side-by-side view.

**AG-UI Integration Pattern:** Host app injects AG-UI context events (`STATE_SNAPSHOT`, `MESSAGES_SNAPSHOT`) with current document/selection. Agent streams responses back. CopilotKit `useCopilotReadable` API synchronizes host app state.

**A2UI Integration Pattern:** Agent can generate structured output components (diff views, suggestion cards) slotting into the host app's design system using A2UI `ComponentSpec`.

**Recommended Approval Model:** Invisible AI for read-only suggestions. Single-click HITL for mutations (apply diff, insert text, update field).

**Example Products:** GitHub Copilot, JetBrains AI Assistant, Salesforce Einstein, Notion AI.

**When to use:** Users work primarily within one host application, ambient context makes suggestions immediately relevant, disruption to workflows must be minimized, host app vendor provides extension API.

---

#### Pattern 3 — Floating Copilot

**Definition:** A floating panel or sidebar that overlays any page in a browser or desktop application. The agent can observe the current page context but is not embedded in the host app.

**Deployment Context:** Browser extensions, desktop overlay apps, enterprise intranet widgets.

**UX Characteristics:** Draggable/collapsible floating panel, "What can I help with on this page?" entry point, page content summarization/form filling/extraction, context injected via DOM scraping or MCP NLWeb adapter, minimal footprint.

**AG-UI Integration Pattern:** The overlay connects to an AG-UI backend. Page context injected as a `STATE_SNAPSHOT` event via content script or NLWeb MCP server. Microsoft NLWeb enables website owners to expose structured MCP endpoint for agent queries.

**Recommended Approval Model:** HITL for any form fills or page mutations. HOTL for read/summarize.

**Example Products:** Copilot in Edge, Arc AI, Siri on iOS Safari.

**When to use:** Users work across many different web applications, no host-app extension API exists, primary use case is read/summarize/extract, deployment must not require backend changes.

---

#### Pattern 4 — Workspace Copilot

**Definition:** The agent has access to the user's full workspace context — documents, calendar, email, tasks, and people graph — and can act across all of them in a single conversation turn.

**Deployment Context:** M365 Copilot, Google Workspace Duet, enterprise digital assistant.

**UX Characteristics:** Unified "Ask about my work" entry point, cross-app context stitching (email → calendar → document), "Catch me up" and "Prepare me for my meeting" entry points, permission model shows data accessed per response, citation of source documents.

**AG-UI Integration Pattern:** Workspace Copilot uses AG-UI `STATE_SNAPSHOT` events to pass workspace context (recent emails, current document, upcoming calendar) at conversation start. Tool calls use MCP servers for each workspace service (Graph API, Drive API, etc.).

**Recommended Approval Model:** HITL for sends and mutations. HOTL for read/summarize. Data access logged to compliance audit trail.

**Example Products:** Microsoft 365 Copilot, Google Duet AI, Salesforce Agentforce.

**When to use:** Users need synthesis across multiple systems of record, meeting prep/status updates/drafting cover 80%+ of use cases, Enterprise SSO and permissions already exist, data residency and audit requirements met by platform provider.

---

#### Pattern 5 — Workflow Copilot

**Definition:** The agent is embedded in a business process and guides users through defined steps. Unlike a chat copilot, the state machine is the process — not the conversation.

**Deployment Context:** Loan origination, insurance underwriting, HR onboarding, procurement approval.

**UX Characteristics:** Step-driven wizard with agent assistance at each step, "What should I fill in here?" contextual help, data validation with natural language explanations, agent fills fields from documents with user confirmation, progress bar shows process position, exit and save-progress controls.

**AG-UI Integration Pattern:** The workflow engine emits `STATE_SNAPSHOT` events at each step transition. The agent receives current form state and can pre-fill or validate fields. User actions emit `USER_ACTION` events that advance the state machine.

**Recommended Approval Model:** HITL at each step boundary. Supervisor review for exceptions. Full audit trail mandatory for regulated processes.

**Example Products:** ServiceNow AI Agents, Pega GenAI, Camunda Copilot.

**When to use:** The business process is well-defined and compliance-regulated, errors in data entry carry financial or legal risk, users vary widely in expertise, audit trail is a compliance requirement.

---

#### Pattern 6 — Decision Copilot

**Definition:** The agent provides structured decision support: recommendation, confidence score, supporting evidence, and alternative options. The human retains decision authority — the agent makes the evidence structure explicit.

**Deployment Context:** Credit scoring review, medical triage support, security alert triage, investment recommendation.

**UX Characteristics:** Recommendation card with primary recommendation + confidence %, ranked alternative list with trade-off summary, evidence citations (documents, data, precedents), "Challenge this recommendation" conversational entry, decision capture recording human decision + rationale, audit trail showing recommendation vs. human decision delta.

**AG-UI Integration Pattern:** Agent emits structured `TOOL_CALL_END` events with JSON payloads matching A2UI `DecisionCard` component spec. The host app renders native decision UI. Streaming is used only for reasoning explanation; decision card is rendered as final structured response.

**Recommended Approval Model:** Human-in-the-loop is mandatory. Every recommendation requires explicit human decision capture. No auto-approve.

**Example Products:** Salesforce Einstein Decision, IBM Watson Assistant for financial services, custom underwriting platforms.

**When to use:** Consequential decisions with regulatory/financial accountability, decision-maker is accountable but needs AI synthesis of evidence, auditability of decision process is compliance requirement, false positive/negative costs are asymmetric.

---

#### Pattern 7 — Coding Copilot

**Definition:** An IDE-integrated agent providing code completion, generation, review, test writing, documentation, and refactoring.

**Deployment Context:** VS Code, JetBrains IDEs, Neovim, GitHub web editor.

**UX Characteristics:** Ghost text completions (gray inline suggestions), chat panel for multi-line generation, right-click "Ask AI" context menu, diff view for suggested changes, inline comment explanation for generated code, test generation with coverage visualization.

**AG-UI Integration Pattern:** IDE extension exposes current file, selection, and project context via `STATE_SNAPSHOT` events. GitHub Copilot uses proprietary protocol; open alternatives use AG-UI or Copilot Kit. CopilotKit React components can render inside IDE webview panels.

**Recommended Approval Model:** Invisible AI for completions (Tab to accept, ESC to reject). HITL for refactoring across multiple files. HOTL for test runs triggered by agent.

**Example Products:** GitHub Copilot, Cursor, Windsurf, JetBrains AI, Claude Code.

**When to use:** Development team productivity is primary ROI driver, codebase has enough context (docs, tests, comments) for grounding, security review process exists for AI-generated code, code review gates catch AI errors.

---

#### Pattern 8 — Search Copilot

**Definition:** The agent augments or replaces keyword search with semantic understanding, synthesis, and conversational follow-up.

**Deployment Context:** Enterprise knowledge base, intranet, documentation portal, e-commerce, customer support.

**UX Characteristics:** Answer at top of search results (not just links), cited sources beneath answer, conversational follow-up ("Tell me more about X"), "This answer might be outdated" freshness indicator, confidence indicators on answer cards, feedback buttons (Helpful/Not Helpful).

**AG-UI Integration Pattern:** Search query triggers AG-UI streaming response with citations. NLWeb MCP enables website content queryable by agent backend. `STATE_SNAPSHOT` includes current search filters and query history.

**Recommended Approval Model:** No approval needed (read-only). Feedback loop is primary quality control mechanism.

**Example Products:** Perplexity, Bing Copilot search, Glean, Notion AI search, Elastic ESRE.

**When to use:** Existing search returns too many results without synthesis, users need cross-document summarization not just retrieval, content corpus changes frequently (RAG preferred), user intent is primarily informational.

---

#### Pattern 9 — Voice Agent

**Definition:** A voice-first interface where the primary input is speech and primary output is audio, with minimal or no visual UI.

**Deployment Context:** Contact center IVR, hands-free field worker tools, automotive assistants, smart speaker skills.

**UX Characteristics:** Wake word or push-to-talk activation, spoken confirmation of actions ("I've created that ticket. Should I assign it to you?"), conversational repair ("Sorry, could you repeat that?"), short response format (no lists/markdown), barge-in support (user can interrupt mid-response), silence detection and graceful timeout.

**AG-UI Integration Pattern:** STT layer converts audio to text → AG-UI event stream → LLM → TTS converts response back to audio. Streaming is critical: the LLM must begin speaking while still generating. `TEXT_MESSAGE_CHUNK` events piped to streaming TTS service.

**Recommended Approval Model:** Verbal confirmation for all actions ("Say 'yes' to confirm"). No irreversible actions without spoken double-confirmation.

**Example Products:** Amazon Alexa for Business, Google CCAI, Twilio Voice AI, Bland.ai, Vapi.

**When to use:** Users' hands are occupied (warehouse, field service, driving), screen real estate is absent/minimal, response latency below 1.5 seconds is critical, use case involves structured transactions not open-ended reasoning.

---

#### Pattern 10 — Visual Agent

**Definition:** An agent that can understand images, diagrams, and charts, and can generate or annotate visual content.

**Deployment Context:** Design review, architecture diagram analysis, medical imaging support, quality control inspection.

**UX Characteristics:** Image upload/screenshot paste into chat, agent-generated image annotations (bounding boxes, labels), side-by-side view (original image + agent analysis), chart interpretation with natural language explanation, "Describe what you see" and "Identify anomalies" entry points.

**AG-UI Integration Pattern:** Images included in AG-UI `TEXT_MESSAGE_CONTENT` events as base64 or pre-signed URLs. Agent returns bounding box coordinates in structured JSON which UI renders as SVG overlays on original image.

**Recommended Approval Model:** HOTL for annotations (user can correct). HITL for any downstream actions triggered by image analysis (flag defect, reject shipment).

**Example Products:** GPT-4o Canvas, Claude with vision, AWS Rekognition + LLM overlay, custom quality-control platforms.

**When to use:** Source data is inherently visual (images, diagrams, charts, scans), textual description alone is insufficient, existing vision ML models lack reasoning capability, users need to understand agent's visual interpretation.

---

#### Pattern 11 — Multi-agent Dashboard

**Definition:** A UI that visualizes multiple collaborating agents, their current tasks, inter-agent communication, and aggregate outputs.

**Deployment Context:** AI ops platforms, enterprise automation centers, research orchestration, automated DevOps pipelines.

**UX Characteristics:** Agent status grid (name, current task, progress, last action), message bus visualization (inter-agent messages in real time), supervisor agent panel (current plan, sub-task delegation), task output aggregation (collated results from all agents), intervention controls (pause agent, reassign task, inject instruction), alert surface (failed agents, stuck tasks, budget warnings).

**AG-UI Integration Pattern:** Each agent in the topology connects to AG-UI independently. A supervisor UI component subscribes to all agent event streams simultaneously. `RUN_STARTED`, `RUN_FINISHED`, `TOOL_CALL_START`, `TOOL_CALL_END` events from all agents are muxed into a single timeline.

**Recommended Approval Model:** HITL at supervisor level for cross-agent decisions. Human-over-the-loop (HOOL) for individual agent actions within policy.

**Example Products:** LangGraph Studio, Microsoft Autogen Studio, CopilotKit multi-agent dashboard.

**When to use:** Multiple specialized agents must collaborate on single user goal, human oversight of overall system required without micromanaging each agent, debugging and observability of agent behavior are primary concerns, business process involves parallel workstreams requiring coordination.

---

#### Pattern 12 — Autonomous Copilot

**Definition:** The agent operates largely independently, completing multi-step tasks with minimal human interaction. The UX is primarily a notification and exception management surface.

**Deployment Context:** Automated report generation, background data enrichment, scheduled compliance checks, autonomous PR review, email triage.

**UX Characteristics:** Task submission (describe task + parameters + schedule), progress notification (email, Slack, push), exception queue (items requiring human judgment), output review (view completed work before publishing), audit log (every decision, tool call, data access), kill switch (emergency stop for all autonomous tasks).

**AG-UI Integration Pattern:** AG-UI events are consumed asynchronously. The frontend subscribes to a task status WebSocket, not a live streaming session. `RUN_FINISHED` event triggers a notification. Exception events (`TOOL_CALL_START` for high-risk tools) route to an approval queue.

**Recommended Approval Model:** Human-over-the-loop (HOOL). Exceptions surface to human automatically. Irreversible actions require approval even in HOOL mode.

**Example Products:** Devin (software engineering agent), Harvey AI (legal document review), custom autonomous workflows.

**When to use:** The task is well-defined, repetitive, and time-consuming, human review of final output (not each step) is sufficient, risk of individual step error is low and recoverable, volume of work exceeds human capacity.



---

**This is Part 1 of 3. [Continue with Part 2 →](pathname:///archon/agentic-systems/agentic-ui/parts/01-agent-ux-patterns-part2) for streaming UX design, reasoning visualization, confidence indicators, approval UX, and long-running task UX patterns.**
