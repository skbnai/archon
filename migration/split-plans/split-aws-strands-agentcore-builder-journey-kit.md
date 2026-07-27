# Split Plan: aws-strands-agentcore-builder-journey-kit

## Overview
- **Source:** `../knowledge-docs-old/docs/cloud-platforms/aws/AWS_Strands_AgentCore_Builder_Journey_Kit.md` (6483 words)
- **Topic ID:** `aws-strands-agentcore-builder-journey-kit`
- **Doc Type:** guide (word cap 2600/part)
- **Domain:** platforms

## Part 1: Foundation through AgentCore Memory
- **Topic ID:** `aws-strands-agentcore-builder-journey-kit`
- **Target Path:** `docs/platforms/13-aws-strands-agentcore-builder-journey-kit.md`
- **Content:** Lines 1-528 of source (~2131 words)
- **Sections:** Title/TOC (Chapters 1-12), Chapter 1 (Foundation & Architecture — Strands SDK, Bedrock AgentCore, ReAct loop, MicroVM isolation), Chapter 2 (Your First Agent — SDK install, hello-world, custom tools, deploying, invoking), Chapter 3 (AgentCore Runtime In Depth — architecture, deployment modes, custom FastAPI agent, AG-UI protocol), Chapter 4 start (AgentCore Memory — short-term)

## Part 2: AgentCore Memory close through Multi-Agent Patterns
- **Topic ID:** `aws-strands-agentcore-builder-journey-kit-part2`
- **Target Path:** `docs/platforms/parts/13-aws-strands-agentcore-builder-journey-kit-part2.md`
- **Content:** Lines 529-1103 of source (~2140 words)
- **Sections:** Chapter 4 remainder (long-term memory), Chapter 5 (AgentCore Gateway & MCP), Chapter 6 (Identity, Auth & Trust Layers — Cognito OAuth, M2M tokens, SigV4 bridge, cross-tenant A2A trust, policy engine), Chapter 7 (Multi-Agent Patterns — supervisor/sub-agent, A2A protocol, agent swarm)

## Part 3: Observability through End-to-End Production Blueprint
- **Topic ID:** `aws-strands-agentcore-builder-journey-kit-part3`
- **Target Path:** `docs/platforms/parts/13-aws-strands-agentcore-builder-journey-kit-part3.md`
- **Content:** Lines 1104-1675 of source (~2334 words)
- **Sections:** Chapter 8 (Observability, Tracing & Evaluation), Chapter 9 (RAI, PII & Compliance), Chapter 10 (LaaS Integration), Chapter 11 (Best Practices & Anti-Patterns), Chapter 12 (End-to-End Production Blueprint — reference architecture, IaC Terraform skeleton, CI/CD pipeline, production checklist), Appendix: Quick Reference

## ASCII Art / Diagram Conversions
None — no box-drawing characters detected in source.

## Key Considerations
- No internal cross-links in source requiring rewrite.
- All named code files (my_agent.py, custom_agent/main.py, cognito.tf, supervisor_pattern.py, guardrail.yaml, main.tf, deploy-agent.yml, etc.) preserved verbatim within their assigned part.
- Each part gets a nav-link to the next/previous (1↔2↔3).
