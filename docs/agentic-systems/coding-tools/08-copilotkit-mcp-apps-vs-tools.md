---
title: 'CopilotKit MCP Apps vs Tools — EU Bank Design Decision'
doc_type: guide
domain: agentic-systems
topic_id: copilotkit-mcp-apps-vs-tools
status: current
date_published: 2026-07-24
last_reviewed: 2026-07-24
supersedes:
  - ../knowledge-docs/docs/coding-tools/github-copilot/copilotkit-mcp-apps-vs-tools.md
tags:
  - copilotkit
  - mcp
  - github-copilot
  - design-decision
---

# CopilotKit MCP Apps vs Tools — EU Bank Design Decision

CopilotKit — Design Decision · EU Bank AI Copilot

## MCP Tools vs MCP Apps

Research-backed architecture recommendation for your Strands + AgentCore + CopilotKit platform, with EU banking security constraints applied.

**Verdict: Hybrid strategy — Tools for data, Apps for interaction**

## 01 — What's the difference

### Two Distinct Primitives

**MCP Tools**

- **Function-call pattern** · Returns data · Host owns UI
- **What it does**: Agent calls a function. Gets back JSON, text, or structured data. _Your app_ decides how to render it.
- **UI ownership**: Host application (your React code) builds the UI for every tool result. Full control, more work.
- **AG-UI protocol**: Streams tool progress events. UI components written in your codebase with `useCopilotAction`.
- **MCP spec**: Original MCP spec — stable, widely supported, all frameworks.
- **Security surface**: No iframes; No external scripts; CSP friendly
- **Best for**: Account lookups, balance queries, risk scores, read-only data display, background orchestration steps.

**MCP Apps**

- **Interactive UI surface** · Ships with MCP server · AG-UI sync
- **What it does**: MCP server ships an interactive HTML/JS UI alongside the tool. CopilotKit renders it; AG-UI keeps it in sync with agent state.
- **UI ownership**: Domain team (MCP server author) owns and ships their own UI. Rendered via `MCPAppsMiddleware` in sandboxed iframe.
- **AG-UI protocol**: AG-UI is the sync channel: tool lifecycle, user interactions (clicks, form submits), agent state — all coordinated in real-time.
- **MCP spec**: Proposed extension to MCP spec (Jan 2026, CopilotKit + community). Growing adoption. Newer — less stable
- **Security surface**: Sandbox iframe required; SRI hash enforcement; CSP frame-src policy
- **Best for**: Payment approval forms, KYC confirmation, multi-step wizards, data pickers, rich charts — UI the domain team owns end-to-end.

## 02 — Data flow comparison

### Under the Hood

**MCP Tools Flow**

```
Agent (Strands)
  ↓ calls tool
MCP Server (AgentCore)
  ↓ returns JSON
CopilotKit Runtime (BFF)
  ↓ AG-UI event stream
React UI (useCopilotAction render())
  ↓ renders natively
User sees result
```

Host app controls 100% of the rendering. No external bundles. Standard React component.

**MCP Apps Flow**

```
Agent (Strands)
  ↓ calls tool → returns ui:// ref
MCP Apps Server (ships HTML + JS)
  ↓ MCPAppsMiddleware fetches bundle
CopilotKit Runtime (validates SRI hash)
  ↓ renders in sandboxed iframe
Iframe: Domain Team UI
  ↕ AG-UI postMessage sync
  ↓ user interacts
Agent receives structured input
```

Domain team ships their own UI. AG-UI bridges iframe ↔ agent state in real-time.

## 03 — When to use which

### Decision Matrix by Banking Use Case

**USE TOOLS**

**Account Balance Lookup**: Read-only query. Returns structured data. The copilot renders it inline as text or a simple card. No interaction needed from user.

**USE APPS**

**Payment Initiation**: Payment team owns the form UX: beneficiary picker, IBAN validator, amount entry, review screen. Ships as MCP App with full domain-team UI control.

**USE TOOLS**

**Risk Score Query**: Returns a score + signal breakdown. Agent narrates it. A simple React component in your codebase renders the breakdown card.

**USE APPS**

**KYC Identity Check**: Complex multi-step wizard. The compliance team owns the flow. Ships as MCP App — they control the UX without touching the copilot shell.

**USE TOOLS**

**Transaction History**: Paginated data. Host app renders a standard table component. No benefit to an iframe for this use case.

**USE APPS**

**FX Rate Booking**: Live rate ticker, tenor picker, confirmation step. Markets desk team ships this as MCP App. Tight domain ownership. Interactive and stateful.

**USE TOOLS**

**AML Sanctions Check**: Binary pass/fail with explanation. Returns JSON verdict. Agent interprets and presents. Simple, auditable, no UI complexity needed.

**USE HYBRID**

**Loan Application**: Data gathering via MCP Tools (credit bureau query, income check) + MCP App for the multi-page application form with document upload.

**USE TOOLS**

**Regulatory Limit Check**: Returns structured compliance verdict. Agent includes it in reasoning chain. No UI surface needed — background orchestration step.

## Recommended Strategy: Tiered Hybrid

For the EU bank platform, use a **two-tier MCP strategy**. **MCP Tools** are the default for all data-retrieval and background orchestration steps — they have zero iframe surface area and fit naturally within your strict CSP and OWASP controls. **MCP Apps** are reserved for domain-owned interactive workflows where a team needs to ship their own UX (payment forms, KYC wizards, FX booking) — they carry a larger security surface that the architecture explicitly manages via sandbox policy and SRI enforcement.

## 04 — EU Bank security fit

### Security Analysis for Regulated Context

**MCP Apps — Key Consideration for Banking**: MCP Apps render external HTML/JS bundles in iframes. For a regulated EU bank, this introduces a content security policy challenge and requires explicit iframe sandboxing policy. It is solvable — but must be designed intentionally, not accepted as a default.

**MCP Tools — Security Profile ✅**

- **CSP Impact**: Zero impact. No additional script-src or frame-src entries needed. Fully compatible with strict `default-src 'self'`.
- **Iframe surface**: None. All rendering is native React components inside your controlled codebase. `frame-ancestors 'none'` remains unchanged.
- **Supply chain risk**: Standard dependency audit (Snyk/Dependabot) on your React components. No runtime bundle loading from external servers.
- **Audit & explainability**: Tool calls are discrete JSON-in/JSON-out events. Each invocation is a clean log entry. Easy to tie to regulatory audit trail.

**MCP Apps — Security Controls Required ⚠️**

- **Iframe sandbox policy**: Must set `sandbox="allow-scripts allow-forms"` — never `allow-same-origin`. Blocks DOM escape, cookie access, and parent-frame navigation.
- **CSP frame-src**: Add `frame-src https://assets.bank.eu` (bank-owned CDN only). Never wildcard. Reviewed per tool registration.
- **SRI enforcement**: Each bundle URL in Tool Registry carries a sha384 hash. MCPAppsMiddleware must verify hash before rendering. Reject mismatches.
- **postMessage origin check**: AG-UI ↔ iframe communication via postMessage must validate `event.origin === 'https://assets.bank.eu'`. Reject all other origins.
- **PII boundary**: MCP App iframes must never receive raw PII. Pass only opaque references (payment_id, customer_ref) — let the MCP server resolve via API.
- **Approval gate compatibility**: Human-in-loop interrupts must work across the iframe boundary. Test Strands `interrupt_before` with MCPAppsMiddleware in staging before prod.

**Spec Maturity Note**: MCP Apps was formally announced by CopilotKit in January 2026. The spec is inspired by the community's MCP-UI effort and OpenAI's Apps SDK, but is not yet an IANA-registered standard. For a regulated institution, treat MCP Apps as a "controlled preview" — deploy for internal staff-facing tools first, not customer-facing surfaces, until the spec stabilises.

## 05 — Implementation patterns

### Code Patterns for Each Approach

**Pattern A — MCP Tools + CopilotKit (data lookup)**

```javascript
// In your React app — useCopilotAction handles rendering
useCopilotAction({
  name: "get_account_balance",
  description: "Fetch account balance for the authenticated customer",
  parameters: [{ name: "account_id", type: "string", required: true }],

  // All rendering is YOUR React component — no external bundles
  render: ({ args, status, result }) => (
    <AccountBalanceCard
      accountId={args.account_id}
      balance={result?.balance}
      currency={result?.currency}
      status={status}          // "inProgress" | "complete" | "error"
    />
  ),

  handler: async (args) => {
    // Goes to BFF → AgentCore → Strands → MCP Tool
    return await bffClient.post("/copilot/tool", args);
  },
});
```

**Pattern B — MCP Apps (payment form — domain team owns UI)**

```javascript
// In your Next.js BFF / agent runtime — attach MCPAppsMiddleware
// The payment domain team's MCP server ships its OWN form UI

import { MCPAppsMiddleware } from "@copilotkit/runtime";

const middleware = MCPAppsMiddleware({
  mcpServers: [
    {
      url: "https://mcp-payment.internal.agentcore.eu-west-1.amazonaws.com",
      transport: "streamable-http",
      // Bank-owned CDN — never external. SRI enforced by middleware
      allowedBundleOrigin: "https://assets.bank.eu",
      sandboxPolicy: "allow-scripts allow-forms",  // Never allow-same-origin
      sriRequired: true,
    }
  ],
});

// Payment domain team's MCP server registers its App like this:
// tool description includes: ui://payment-confirm?bundle=sha384:abc...
// CopilotKit resolves bundle from CDN, renders in sandboxed iframe
// AG-UI syncs form state back to Strands agent for approval flow
```

**Pattern C — Hybrid in Strands agent (recommended)**

```python
# strands_agent/agent.py — configure tool tiers explicitly
from strands import Agent
from mcp import MCPClient

async def build_agent(session_ctx):
    registry = await ToolRegistry.fetch(session_ctx["team_id"])

    # Tier 1 — MCP Tools: data retrieval, background ops
    # These produce JSON. CopilotKit renders via useCopilotAction
    data_tools = await MCPClient.list_tools(
        registry.filter(type="data_tool")
    )

    # Tier 2 — MCP Apps: interactive domain UIs
    # These produce ui:// references. MCPAppsMiddleware renders iframes
    app_tools = await MCPClient.list_tools(
        registry.filter(type="mcp_app")
    )

    return Agent(
        model=BedrockModel(model_id="anthropic.claude-3-5-sonnet..."),
        tools=[*data_tools, *app_tools],
        # Human-in-loop: pause BEFORE any MCP App tool fires
        # This gives the approval gate a chance to validate
        interrupt_before=registry.get_gated_tool_names(),
        system_prompt=build_prompt(session_ctx),
    )
```

## 06 — Summary

### At a Glance

| Criterion | MCP Tools | MCP Apps | Use in Bank |
|-----------|-----------|----------|---|
| Spec maturity | ✅ Stable (original MCP) | ⚠️ Jan 2026 — evolving | Tools for core ops, Apps for non-critical workflows |
| Security surface | ✅ Minimal — no iframes | ⚠️ Larger — requires iframe policy | Tools for gated/sensitive ops; Apps with sandbox controls |
| UI ownership | Host app (central team) | Domain team (MCP server author) | Apps where domain teams need full UX autonomy |
| Strands compatibility | ✅ Full — standard tool call | ✅ Via MCPAppsMiddleware | Both supported in same Strands agent |
| Human-in-loop | ✅ interrupt_before works | ⚠️ Requires testing across iframe boundary | Validate in staging before production rollout |
| Dynamic registration | ✅ Tool Registry → manifest | ✅ Tool Registry → manifest + bundle URL | Same Tool Registry serves both |
| GDPR / PII risk | ✅ Data stays in controlled code | ⚠️ Must not pass PII into iframe | Pass opaque references only into MCP Apps |
| Audit trail | ✅ Clean JSON events | ✅ AG-UI events auditable | Both loggable — ensure postMessage events are captured |

**EU BANK AI COPILOT — MCP DESIGN DECISION**
Strands · AgentCore · CopilotKit · AG-UI · MCP
Research: CopilotKit Docs · Jan 2026
