---
title: "AGUI Standards & Ecosystem Landscape — Part 2"
date_created: 2026-07-24
last_reviewed: 2026-07-24
status: current
domain: agentic-systems
doc_type: guide
topic_id: agui-standards-landscape-part2
covers_version: "as of 2026-07-10"
supersedes: []
---

# A2UI, MCP Apps, and NLWeb

This is Part 2 of 3. **[Back to Part 1](pathname:///archon/agentic-systems/agentic-ui/02-agui-standards-landscape) · [Continue to Part 3 →](pathname:///archon/agentic-systems/agentic-ui/parts/02-agui-standards-landscape-part3)**

## 3. A2UI Deep Dive (v0.9)

A2UI (Agent-to-UI) is a declarative specification developed by Google for generative UI. An agent emits JSON describing UI surfaces; the frontend renders those surfaces using its native component library. A2UI is part of the Oracle Open Agent Spec three-layer model.

**Status:** v0.9 — experimental as of July 2026, not yet GA  
**Origin:** Google  
**Transport:** Carried inside AG-UI CUSTOM events  
**Design Philosophy:** Safe (no arbitrary code execution), declarative (fully described by JSON schema), framework-agnostic (identical JSON renders on web, mobile, and desktop)

### 3.1 Design Philosophy

A2UI is built on five key principles. First, no arbitrary code execution: A2UI widgets are JSON data, never executable code. This prevents XSS and code injection attacks that could occur if agents generated JavaScript or custom component code. Second, every A2UI payload must validate against the A2UI JSON Schema before rendering, preventing malformed or malicious widget trees from reaching the render layer. Third, A2UI is framework-agnostic: the JSON schema defines widget semantics, and each host platform (web, mobile, desktop) renders using its native components. Fourth, widgets describe WHAT to show, not HOW to show it, avoiding vendor lock-in. Fifth, unknown widget types degrade gracefully to text fallbacks, so clients don't break when A2UI versions evolve.

### 3.2 Widget Catalog

A2UI provides a standard widget catalog covering common UI needs. Text widgets render styled text blocks with markdown support. Form widgets collect data with labeled inputs and validation rules. Table widgets display tabular data with sorting and filtering. Chart widgets render various data visualizations. Card widgets provide summary containers with optional actions. Carousel widgets present collections of cards in a scrollable interface. Action widgets render buttons or triggers. Progress widgets show step indicators or progress bars. Badge widgets display status indicators. Divider widgets create visual separators. Image widgets display images from allowlisted URLs. Link widgets render hyperlinks with optional new-tab behavior.

### 3.3 JSON Schema Reference

The A2UI schema is recursive: each widget can contain other widgets in its body array, enabling arbitrary nesting. Required fields include the widget `type`. Optional fields include `id`, `title`, and `style`. Tables have `columns` (array of column definitions) and `rows` (array of data objects). Forms have `fields` (array of input definitions) with name, type, label, required flag, options, and validation rules. Actions have `label`, `style`, `action_type`, and `payload`.

### 3.4 A2UI vs. Comparable Technologies

A2UI differs from React Server Components, JSON Schema Form, and OpenAI Tool Cards in several ways. React Server Components execute server-side JSX and can contain arbitrary JavaScript, offering maximum flexibility but requiring React/Next.js. JSON Schema Form generates forms only from a schema, suitable for narrower use cases. OpenAI Tool Cards are tied to the OpenAI platform with a fixed two-action limit. A2UI provides a framework-agnostic declarative surface with 12+ widget types, no execution, and optional streaming via AG-UI.

Organizations should choose A2UI when the agent must render task-appropriate UI components dynamically, the same output must work on web, mobile, and desktop natively, arbitrary code execution in generative UI is a security concern, or a standardized declarative format is desired. React Server Components are better for React/Next.js-exclusive apps. JSON Schema Form fits narrow form-generation use cases. OpenAI Apps SDK remains appropriate for existing OpenAI platform investments.

### 3.5 Production Readiness Assessment (July 2026)

A2UI v0.9 is experimental. Schema stability is low with breaking changes expected before 1.0. Widget coverage is moderate with 12 types, though charts require host library integration. Accessibility is partial with ARIA roles mentioned but no certification. Performance is good for pure JSON but spec offers no rendering performance guarantees. No security audit has been completed yet. Browser support is host-dependent. Mobile support is theoretical with no reference implementation.

For production enterprise deployments, organizations should either implement static/typed generative UI using AG-UI CUSTOM events with a bespoke component registry, or adopt A2UI with explicit version pinning and a documented migration plan for the 1.0 breaking changes.

---

## 4. MCP Apps

MCP Apps is an architectural pattern where MCP servers expose tools WITH associated UI resources bundled alongside them. When an agent calls a tool from an MCP App server, the frontend automatically fetches and renders the corresponding UI component. This pattern emerged from CopilotKit and the OpenAI Apps SDK ecosystem and is now standardized through the MCP specification.

### 4.1 Architecture

An MCP App server is a single service that exposes both tool definitions and UI resources. Tools are defined using the standard MCP tool interface with name, description, and parameters. UI resources are associated with tools via a naming convention or explicit mapping. When an agent calls a tool, the MCPAppsMiddleware (running in the frontend gateway) intercepts the `TOOL_CALL_START` event, looks up the corresponding UI resource, fetches the component code from the MCP server, and emits a `CUSTOM` event containing the A2UI surface or raw component code.

The frontend then renders this component with the tool's arguments passed as props. If the tool is marked `requires_approval`, an approval card is displayed. Otherwise, the component is rendered in the chat interface or as a side panel. User interactions with the component are captured and sent back to the agent via `/agent/action`.

### 4.2 Frontend Tool Execution Lifecycle

When an agent calls a tool from an MCP App server, a precise sequence of events occurs. The agent backend sends `TOOL_CALL_START` with the tool name and arguments. The MCPAppsMiddleware intercepts this and looks up the tool in the MCP resource registry. The middleware fetches the associated UI component code from the MCP server. It then emits a `CUSTOM` AG-UI event containing the UI component definition and tool arguments as props. The CopilotKit client receives this event and renders the component. The user interacts with the component (clicks buttons, fills forms, etc.). The client posts the interaction result to `/agent/action`. The agent backend receives the action and processes the result.

### 4.3 MCP Apps Security Model

UI resources must be sandboxed to prevent malicious code from accessing the parent DOM. Components should run in isolated iframes with strict Content Security Policy. MCP servers should sign UI resource bundles (not yet standard). MCPAppsMiddleware must enforce HITL gates for tools marked `requires_approval` without allowing agent instructions to bypass them. Each MCP App server exposes only its own tools; the MCP registry enforces namespace isolation. Every tool call and UI interaction should be logged with OTel correlation IDs for later audit.

### 4.4 Enterprise MCP Registry Pattern

Large organizations typically run multiple MCP App servers (Finance, HR, Legal, etc.). A centralized MCP Registry Service provides tool discovery, server health monitoring, access policies, rate limit configuration, and audit routing. The registry enforces role-based access control (Finance team can only call Finance MCP), data classification gates (PII tools require DLP approval), per-team rate limiting, and canary routing for gradual rollouts of new tool versions.

### 4.5 Code Example: Minimal MCP App Server

An MCP App server in Python uses FastMCP for tool registration and MCP resource exposure. Tools are decorated with `@mcp.tool()` and return structured results. UI resources are decorated with `@mcp.resource()` and return component code as strings. When deployed, the MCP server exposes a `/tools/list` endpoint for tool discovery and `/resources/read` for fetching UI components.

---

## 5. NLWeb

NLWeb is a Microsoft open project that makes any website queryable via natural language. It uses Schema.org markup, RSS feeds, and existing semi-structured web data as a knowledge source, adds vector search and an LLM query layer, and exposes the result via natural language API. Every NLWeb instance is simultaneously an MCP server, making website content discoverable by AI agents.

**GitHub:** `nlweb-ai/NLWeb` (MIT)  
**Reference implementation:** Python  
**Vision:** "Play a similar role to HTML in the emerging agentic web"  
**Cloudflare integration:** Native NLWeb support via AutoRAG (added early 2026)

### 5.1 Architecture

An NLWeb instance consists of a query layer, vector index, and source data layer. The query layer parses intent from natural language, extracts structured filters using Schema.org entity types, performs vector search over indexed content, synthesizes relevant chunks with an LLM, and returns grounded answers with source citations. The vector index contains chunked and embedded website content. The source data layer contains existing website HTML, Schema.org JSON-LD, RSS/Atom feeds, product catalogs, documentation, and FAQs.

Every NLWeb instance also exposes MCP server endpoints: `search_content`, `get_page`, and `list_topics` tools. Agents discover these tools via MCP registry lookups and can query website content natively without writing custom integrations.

### 5.2 Cloudflare AutoRAG Integration

Cloudflare added native NLWeb support via AutoRAG in early 2026. This allows any Cloudflare-hosted website to become an NLWeb-compatible MCP server without self-hosting infrastructure. Organizations choose between self-hosted NLWeb (full control, manual scaling, custom embeddings), Cloudflare AutoRAG (auto-scaling, usage-based pricing, Cloudflare data processing), or Azure AI Search + NLWeb adapter (enterprise-scale, Azure consumption, Azure governance).

### 5.3 NLWeb vs. Competing Approaches

NLWeb is designed for natural language queries over existing website content using Schema.org and RSS as source data. Custom RAG solutions offer higher flexibility for any document corpus but require more setup. Azure AI Search provides keyword and semantic search for enterprise documents. Enterprise portals like SharePoint offer built-in search but limited natural language. Knowledge assistants like Guru or Confluence AI provide natural language over wiki content.

Choose NLWeb when the organization has an existing public-facing website with Schema.org markup, the goal is making existing web content queryable without rebuilding the knowledge base, and low-friction agent integration is a priority. Choose Custom RAG when the knowledge base contains proprietary documents unsuitable for public NLWeb instances or fine-grained access control per document is required. Do not use NLWeb when content is classified or subject to data residency requirements, content isn't already in semi-structured form, or real-time data is required.

### 5.4 Governance Considerations

Every NLWeb instance is, by design, publicly queryable as an MCP server. This makes previously navigational-only website content fully extractable by any agent that discovers the MCP endpoint. Organizations must review website content against data classification policies before enabling NLWeb.

Governance concerns include: unintended data exposure (audit all indexed content; use `noindex` meta tags for excluded content), rate limit abuse (implement per-caller rate limiting at the MCP layer), data freshness (configure crawl/re-index frequency; stale content produces incorrect responses), competitive intelligence extraction (NLWeb makes structured extraction trivial), and PII in web content (scan website content before indexing; NLWeb does not automatically redact).

This is Part 2 of 3. **[Back to Part 1](pathname:///archon/agentic-systems/agentic-ui/02-agui-standards-landscape) · [Continue to Part 3 →](pathname:///archon/agentic-systems/agentic-ui/parts/02-agui-standards-landscape-part3)**
