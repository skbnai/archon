---
title: "MCP Cheat Sheet"
doc_type: guide
domain: agentic-systems
topic_id: cheatsheet-3-mcp
status: current
date_created: 2026-07-24
last_reviewed: 2026-07-24
supersedes:
  - docs/coding-tools/claude/Cheatsheet_3_MCP.md
---

# MCP Cheat Sheet

Tool Design &amp; MCP Integration - Anthropic Partner Certification EA

**DOMAIN 2 · 18%**

## MCP Tools vs MCP Resources — Core Distinction

### MCP TOOLS

⚡ **Executable functions**

Perform actions with potential side effects

💥 **Has side effects**

Creates records, sends emails, modifies data

📋 **Examples**

process_refund, send_email, create_ticket, lookup_order

🎯 **When to use**

Agent needs to DO something in external system

### MCP RESOURCES

👁️ **Read-only data**

Expose data for reading — no side effects

📚 **Static/queryable**

Documentation, catalogs, configuration

📋 **Examples**

product_catalog, api_docs, feature_flags, user_schema

🎯 **When to use**

Agent needs to SEE available data without acting

**✓ Content catalogs as resources:** give agents visibility into available data WITHOUT requiring exploratory tool calls

## Tool Description Design — The #1 Factor

Tool descriptions are the PRIMARY mechanism LLMs use for tool selection — minimal descriptions = unreliable selection

### What every tool description MUST include

- **Purpose:** What the tool does in plain language
- **Input formats:** Expected data types, formats, constraints for each parameter
- **Example queries:** Sample inputs that should trigger this tool (not other similar tools)
- **Edge cases:** What happens with unusual inputs, what it cannot handle
- **Boundaries:** What this tool does NOT do — distinguishes from similar tools

### The Misrouting Problem

analyze_content vs analyze_document with near-identical descriptions → Claude misroutes consistently or alternates unpredictably

Keyword-sensitive system prompts can create unintended tool associations — test prompts carefully

**Bad — ambiguous description:**

```json
{
  "name": "analyze_content",
  "description": "Analyzes content"
}
{
  "name": "analyze_document",
  "description": "Analyzes documents"
}
```

**Good — distinct, specific boundaries:**

```json
{
  "name": "analyze_content",
  "description": "Extracts key topics from SHORT text snippets (under 500 tokens). Do NOT use for PDFs or multi-page documents. Input: plain text string."
}
{
  "name": "analyze_document",
  "description": "Processes structured files (PDF, DOCX). Use for multi-page documents. Input: file path."
}
```

## MCP Server Design Decisions

### Should I build a custom MCP server?

**YES, if:**
- Proprietary internal system
- Team-specific workflow
- No community server exists
- Custom authentication needed

**NO, instead use community server for:**
- Jira (project management)
- GitHub (version control)
- Slack (messaging)
- Standard API integrations

### Server Architecture Principles

- Expose resources for read-only data catalogs
- Expose tools for executable actions with side effects
- Group related tools in same server
- Version your MCP server interfaces

## Task 2.5 — Built-in Tools Mastery

- **Grep:** **Content search** — inside files. Find function callers, error messages, import patterns
- **Glob:** **Path matching** — file names/extensions. Find `**/*.test.tsx` file tree navigation
- **Read:** Full file read. Always Read before Write for existing files
- **Write:** Full file overwrite. Fallback when Edit fails on non-unique text
- **Edit:** Targeted modification via **unique** text matching only
- **Bash:** Shell execution — tests, git, build commands

**Edit requires text to appear exactly ONCE — falls back to Read+Write for non-unique matches**

## Exam Focus: Domain 2

- **Domain weight:** 18% — 2nd smallest domain
- **Key insight:** Tool DESCRIPTIONS are primary tool selection mechanism
- **Tools vs Resources:** Tools = actions + side effects; Resources = read-only data
- **Misrouting cause:** Ambiguous overlapping descriptions between similar tools
- **Community servers:** Use for Jira, GitHub, Slack — don't rebuild them
- **Content catalogs:** Expose as resources — no exploratory tool calls needed

### Task Statements

- 2.1 Tool interface design
- 2.2 MCP servers
- 2.3 Resources
- 2.4 Community servers
- 2.5 Built-in tools

### Scenario 1 MCP Tools

get_customer, lookup_order, process_refund, escalate_to_human

## MCP Server Structure — Code Reference

```javascript
// MCP Server Definition
const server = new MCPServer({
  name: "customer-support",
  version: "1.0.0"
});

// TOOL — executable with side effects
server.tool("process_refund", {
  description: "Processes a refund for an order. Use ONLY when customer confirms they want a refund and order is eligible. Input: orderId (string), amount (number, max 500), reason (string). Returns: confirmation_id or error.",
  parameters: {
    orderId: {
      type: "string",
      description: "Order ID from lookup_order"
    },
    amount: {
      type: "number",
      maximum: 500
    },
    reason: {
      type: "string",
      enum: ["damaged", "not_received", "changed_mind"]
    }
  }
}, async (params) => {
  // Execute refund — has side effect
  return await refundSystem.process(params);
});

// RESOURCE — read-only data catalog
server.resource("refund-policies", {
  description: "Read-only refund policy documentation and eligibility rules. No side effects."
}, async () => {
  return await getPolicyDocs();  // read only
});
```

## Tool Description — Best Practice Template

```javascript
// Template: Every element serves a purpose
{
  name: "lookup_order",
  description: `
PURPOSE: Retrieves complete order details including status, items, and tracking info.

USE WHEN: Customer provides an order ID and needs order status, delivery info, or item details.

DO NOT USE: For account-level queries (use get_customer) or refund processing (use process_refund).

INPUT: orderId — string, format "ORD-XXXXXX"

EXAMPLE: "ORD-123456", "ORD-789012"

RETURNS: { status, items[], tracking, estimated_delivery, eligible_for_refund }

ERRORS: Returns null if order not found.
  `
}
```

**✓ Include DO NOT USE section to prevent misrouting to similar tools**

**⚠️ System prompt keywords can create unintended tool associations — audit your prompts**
