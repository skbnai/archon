# Split Plan: aws-strands-agentcore-advancedpatterns

## Overview
- **Source:** `../knowledge-docs-old/docs/cloud-platforms/aws/AWS_Strands_AgentCore_AdvancedPatterns_v3.md` (6320 words)
- **Topic ID:** `aws-strands-agentcore-advancedpatterns`
- **Doc Type:** guide (word cap 2600/part)
- **Domain:** platforms

## Part 1: Hooks through HITL
- **Topic ID:** `aws-strands-agentcore-advancedpatterns`
- **Target Path:** `docs/platforms/12-aws-strands-agentcore-advancedpatterns.md`
- **Content:** Lines 1-469 of source (~1965 words)
- **Sections:** Title/TOC (Chapters A1-A7), Chapter A1 (Strands Hooks: Full Lifecycle System — architecture, event inventory, production hook patterns), Chapter A2 (Human-in-the-Loop: the two HITL patterns, hook-based interrupt, ToolContext.interrupt(), async SQS/SNS approval, circuit breaker)

## Part 2: Checkpointer through Meta Tool Pattern
- **Topic ID:** `aws-strands-agentcore-advancedpatterns-part2`
- **Target Path:** `docs/platforms/parts/12-aws-strands-agentcore-advancedpatterns-part2.md`
- **Content:** Lines 470-860 of source (~2175 words)
- **Sections:** Chapter A3 (Checkpointer: SessionManager, LangGraph DynamoDBSaver, AgentCoreMemorySaver, multi-tier memory orchestrator), Chapter A4 (AgentCore Code Interpreter), Chapter A5 (AgentCore Browser Tool), Chapter A6 start (Meta Tool Pattern)

## Part 3: Meta Tool Pattern close, Expert Patterns
- **Topic ID:** `aws-strands-agentcore-advancedpatterns-part3`
- **Target Path:** `docs/platforms/parts/12-aws-strands-agentcore-advancedpatterns-part3.md`
- **Content:** Lines 861-1234 of source (~2266 words)
- **Sections:** Chapter A6 remainder (dynamic tool registration), Chapter A7 (Expert Patterns: memory branching, structured output, import-agent migration, Claude Code as remote A2A sub-agent, prompt-injection defence, cost-aware model routing), Appendix A: Advanced Patterns Quick Reference / Expert Decision Matrix

## ASCII Art / Diagram Conversions
None — no box-drawing characters detected in source.

## Key Considerations
- No internal cross-links in source requiring rewrite.
- All ~20 named code files (hooks_production.py, hitl_hook_pattern.py, session_manager.py, meta_tool_full.py, etc.) preserved verbatim as fenced code blocks within their assigned part.
- Each part gets a nav-link to the next/previous (1↔2↔3).
