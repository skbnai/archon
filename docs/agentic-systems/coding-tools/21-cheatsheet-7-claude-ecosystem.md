---
title: Claude Ecosystem Cheat Sheet
doc_type: guide
domain: agentic-systems
topic_id: cheatsheet-7-claude-ecosystem
status: current
date_created: 2026-07-24
last_reviewed: 2026-07-24
tags: [claude-ecosystem, cheatsheet, coding-tools, quick-reference]
supersedes:
  - docs/coding-tools/claude/Cheatsheet_7_Claude_Ecosystem.md
---

# Claude Ecosystem Cheat Sheet

## Claude Ecosystem — Complete Offerings Map

Cowork · CLI · Claude in Chrome · Claude in Excel/PowerPoint · API · Plans Comparison · Connectors · Plugins

Updated March 2026

Research Preview Products Included

### Claude.ai

Web, mobile & desktop chat

- Conversational AI assistant
- Web, iOS, Android, Desktop apps
- Projects with persistent memory
- Artifacts (code, HTML, React)
- Web search + deep research
- File upload & analysis
- Style customization

Plans: Free / Pro $20/mo / Max $100–200/mo / Team / Enterprise

URL: claude.ai · claude.com

### Claude Code

Terminal agentic coding tool

- npm i -g @anthropic-ai/claude-code
- Reads codebase, edits files, runs commands
- Full agentic loop with tool use
- MCP server integration
- CLAUDE.md project configuration
- Custom skills & subagents
- Hooks system (Pre/Post ToolUse)
- Plugins marketplace
- Local, Remote (cloud), SSH modes
- Desktop app + VS Code integration

Requires: Pro / Max / Team / Enterprise

Platforms: macOS · Linux · Windows (WSL)

URL: code.claude.com · npm @anthropic-ai/claude-code

### Cowork

Desktop AI agent — Claude Code for knowledge work

- Claude Desktop app tab (macOS + Windows)
- Direct local file access via isolated VM
- Sub-agent coordination, parallel workstreams
- Professional outputs: xlsx, pptx, docx, pdf
- Scheduled recurring & on-demand tasks
- MCP connectors (Google Drive, Gmail, DocuSign)
- Plugin marketplace + custom plugins
- Global & folder-level instructions
- Cowork + Chrome = research → deliverable
- Research preview — rapid improvements

Requires: Pro / Max / Team / Enterprise

Platform: Desktop app only · Not web/mobile

URL: Claude Desktop → Cowork tab · claude.com/download

### Claude in Chrome

Browser browsing agent

- Chrome extension — side panel in browser
- Navigate, click, fill forms, manage tabs
- Works with your logged-in accounts
- Multi-step web workflows automated
- Reads page content, executes actions
- Paired with Cowork = web → file deliverables
- Paired with Claude Code = build-test-verify
- Faster usage consumption than regular chat

Model by Plan:
- Max → Sonnet 4.6 / Opus 4.6
- Pro → Haiku 4.5 (limited)
- Heavy use eats usage limits fast → consider Max plan

Status: Chrome Web Store · Research preview

### Claude API

Build your own Claude-powered apps

- REST API + Python/TypeScript SDKs
- Agent SDK for agentic applications
- Tool use / function calling
- Streaming responses
- Batch processing
- Image & document input
- System prompts, multi-turn conversations
- All models: Opus, Sonnet, Haiku
- 1M token context window (Opus 4.6)

Models Available:
- claude-opus-4-6
- claude-sonnet-4-6
- claude-haiku-4-5-20251001

URL: console.anthropic.com · docs.claude.com

### Claude in Excel & PowerPoint — Microsoft Add-ins

**Claude in Excel**

- What it does: Reads entire workbook including nested formulas and multi-tab dependencies
- Capabilities: Pivot table editing, chart modifications, conditional formatting, cell-level citations
- Shortcut: Ctrl+Alt+C (Win) / Ctrl+Option+C (Mac)
- Data feeds: Moody's credit ratings, LSEG market prices — live data in spreadsheets
- Plans: Pro, Max, Team, Enterprise (since Jan 24, 2026)

**Claude in PowerPoint**

- What it does: Reads slide masters, layouts, fonts, colors — generates on-brand slides
- Capabilities: Generate from description, edit existing, restructure, native editable charts
- Templates: Respects brand guidelines — no off-brand elements injected
- Plans: Max, Team, Enterprise (Pro not yet included)
- Security note: Prompt injection risk — use only with trusted files (malicious templates can manipulate Claude)

**Workflow: Data to Presentation**

Excel → PowerPoint Pipeline:
1. Claude in Excel — Analyze data, build financial model, pivot tables
   (context passes automatically)
2. Claude in PowerPoint — Build slides from Excel data, match brand template
   (web research via)
3. Claude in Chrome — Research competitors, market data, verify facts

Models in Office Add-ins:
- Excel: Opus 4.6 with finance evals optimization
- PowerPoint: Switch Sonnet 4.6 (light edits) or Opus 4.6 (complex)
- Install: Microsoft Marketplace → "Claude by Anthropic in Excel/PowerPoint"

## Cowork Deep Dive

### How Cowork Works

- Architecture: Built on same agent foundation as Claude Code — runs in isolated VM (Apple Virtualization / VMware)
- File access: You grant access to specific folder — Claude reads/writes/creates inside it only
- Execution: Analyze → Plan → Execute in VM → Coordinate sub-agents → Deliver to filesystem
- Parallel work: Queue tasks — Claude works through them in parallel, you don't wait
- Deletion protection: Claude always asks explicit permission before permanently deleting files
- Scheduled tasks: Set recurring tasks — Claude completes automatically on schedule

### Cowork Tasks Examples

- Re-organize downloads folder by sorting & renaming
- Create expense spreadsheet from receipt screenshots
- Draft report from scattered notes in folder
- Research + synthesize into formatted document
- Monitor plant growth (from photo folders)
- Build slide deck from existing data files

### Connectors & Plugins

- Web connectors: Browser-based APIs — Google Drive, Gmail, Google Calendar, DocuSign, FactSet
- Desktop ext.: Deep system access — n8n, AWS, Honeycomb, Fellow.ai, Apollo, Clay
- Plugins: Packaged skills + agents + hooks + MCP. Install via /plugins. Anthropic-reviewed.
- Enterprise plugins: HR, finance, engineering, ops, investment banking, equity research, wealth mgmt
- Global instructions: Set preferred tone/format/role once — applies to every Cowork session
- Folder instructions: Per-folder context that activates when working in that folder

### Security Considerations

- Cowork can take destructive actions (delete files) if instructed — give very clear guidance
- Prompt injection: malicious content in files could manipulate Claude's actions
- Do NOT use for regulated workloads — activity not in Audit Logs or Compliance API
- Runs in sandboxed VM — Claude cannot access files outside what you explicitly grant

## Plans Comparison — Feature Access Matrix (March 2026)

| Feature | Free | Pro $20/mo | Max $100–200/mo | Team | Enterprise |
|---------|------|-----------|-----------------|------|-----------|
| Claude.ai chat (Sonnet 4.6) | ✓ limited | ✓ | ✓ 5x usage | ✓ | ✓ |
| Claude Code (CLI + Desktop) | ✗ | ✓ | ✓ | ✓ included | ✓ |
| Cowork (desktop agent) | ✗ | ✓ research preview | ✓ | ✓ research preview | ✓ |
| Claude in Chrome (browser agent) | ✗ | △ Haiku only | ✓ Sonnet/Opus | ✓ | ✓ |
| Claude in Excel add-in | ✗ | ✓ since Jan 2026 | ✓ | ✓ | ✓ |
| Claude in PowerPoint add-in | ✗ | ✗ | ✓ | ✓ | ✓ |
| Opus 4.6 access | ✗ | △ limited | ✓ | ✓ | ✓ |
| Extended thinking (ultrathink) | ✗ | △ | ✓ | ✓ | ✓ |
| API access | ✗ | Separate API key | Separate API key | Separate API key | ✓ enterprise |
| Admin controls + audit logs | ✗ | ✗ | ✗ | △ | ✓ |
| Private plugin marketplace | ✗ | ✗ | ✗ | △ | ✓ |
| HIPAA compliance | ✗ | ✗ | ✗ | ✗ | ✓ HIPAA-ready |
| 1M token context (Opus 4.6) | ✗ | △ | ✓ | ✓ | ✓ |

✓ Full access △ Partial/limited ✗ Not included research preview = beta, may change

## Claude Ecosystem Integration Map — How Products Work Together

### Power User Workflows

**Research → Document Pipeline**

Chrome → web research, scrape structured data
\+ Cowork → synthesize into formatted Word report
\+ Excel → build supporting data tables
\+ PowerPoint → convert to presentation deck

**Developer Build-Test-Verify**

Claude Code CLI → write feature code
\+ Chrome extension → test in browser, read console
\+ Claude Code → debug from console logs
\+ API → integrate into production system

**Enterprise Knowledge Work**

Cowork → local file org + report drafting
\+ MCP connectors → Google Drive, Gmail, DocuSign
\+ Enterprise plugins → domain-specific workflows
\+ Admin controls → compliance + audit logs

### MCP Connectors Available (Cowork + Claude Code)

- **Google Suite**: Drive, Gmail, Calendar
- **MS Office**: Excel, PowerPoint via add-in
- **DocuSign**: Signature workflows
- **FactSet**: Financial data & analytics
- **Slack**: Team messaging + search
- **GitHub**: Code, PRs, Issues
- **Apollo/Clay**: Sales intelligence
- **LegalZoom**: Legal document workflows
- **WordPress**: Content management
- **Harvey**: Legal AI integration

## Anthropic Labs — Experimental Products

Anthropic Labs (led by Instagram co-founder Mike Krieger) incubates frontier products. Claude in Chrome, Cowork, and Skills all originated from Labs-style rapid experimentation.

Claude Code → Cowork lineage: same agent architecture, Cowork adds non-coding-friendly UI + VM sandbox + office format skills

### Model Tier Strategy

- **Opus 4.6**: 1M token context, 128K output — complex enterprise tasks, lead agent in multi-agent systems
- **Sonnet 4.6**: Smart, efficient — everyday tasks, most Claude.ai interactions, subagents
- **Haiku 4.5**: Fast + cheap — high-volume subagents, Chrome (Pro), rapid iteration tasks

## Related

- [Claude CLI Cheat Sheet](20-cheatsheet-6-claude-cli.md) — the previous section in this series.
- [Claude Code Agents & Parallelism](22-cheatsheet-9-agents-parallelism.md) — the next section in this series.
