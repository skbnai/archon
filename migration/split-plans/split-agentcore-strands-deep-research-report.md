# Split Plan: Amazon Bedrock AgentCore & Strands SDK — Deep Technical Research Report

**Source:** `/workspace/knowledge-docs/docs/cloud-platforms/aws/agentcore_strands_deep_research_report.md` (~18,900 words body excluding the source's own table-of-contents, `source_type: converted-pdf`, 23 numbered "Part" chapters + 2 appendices)

**Reason:** Word count vastly exceeds the guide doc_type cap (2600 words hard cap); a 9-way split was required — the largest single-document split in this migration wave, driven by the source being an unusually long, densely-referenced research report with almost no fenced code (most content counts toward the word cap, unlike code-heavy architecture docs).

## Split Boundary

**Part 1 (Main):** `docs/platforms/18-agentcore-strands-deep-research-report.md`
- Source: Executive Summary + Part I (Platform Foundations) + Part II (Runtime) + Part III (Gateway)
- Content: report thesis and April–June 2026 quarter highlights; why AgentCore exists and the service map; Runtime's Firecracker-microVM isolation model, session lifecycle, cold starts, protocols/versioning, networking patterns, pricing; Gateway's dual-sided OAuth security architecture, request lifecycle, semantic tool search, ingress networking

**Part 2:** `docs/platforms/parts/18-agentcore-strands-deep-research-report-part2.md`
- Source: Part IV (Policy) + Part V (Registry) + Part VI (Harness)
- Content: Cedar policy engine, evaluation semantics, neuro-symbolic NL authoring, LOG_ONLY→ENFORCE rollout discipline, interceptor composability, GA timeline; Registry's four-persona IAM model and preview limitations; Harness's two-API-call abstraction, GA auto-provisioning, multi-model mid-session switching, inline-function escape hatch

**Part 3:** `docs/platforms/parts/18-agentcore-strands-deep-research-report-part3.md`
- Source: Part VII (Identity) + Part VIII (Memory) + Part IX (Browser and Code Interpreter) + Part X (MCP Server Hosting)
- Content: the delegation-not-impersonation identity chain, workload identity trust boundaries, federation and cross-agent propagation; Memory's two-tier model and four built-in strategies; Browser and Code Interpreter design intent plus the independently-documented Sandbox-mode DNS-exfiltration and IAM-reachability security findings (Unit 42, BeyondTrust, Sonrai); MCP server hosting on Runtime and its statelessness requirement

**Part 4:** `docs/platforms/parts/18-agentcore-strands-deep-research-report-part4.md`
- Source: Part XI (Strands Agents SDK Deep Dive) + Part XII (Observability)
- Content: the Strands ReAct agentic loop, tools/hot-reload risk, model abstraction, MCP/A2A as tool sources, multi-agent orchestration patterns (Graph/Swarm/Workflow), hooks, documented production gaps, the Strands↔AgentCore service-mapping table; CloudWatch/OTEL-native observability, Phoenix, the CloudWatch-vs-Phoenix-vs-hybrid comparison table, distributed tracing

**Part 5:** `docs/platforms/parts/18-agentcore-strands-deep-research-report-part5.md`
- Source: Part XIII (Security: Complete Threat Model) + Part XIV (Production Architecture) + Part XV (Release Analysis)
- Content: the full threat model (prompt injection, tool/MCP poisoning, data exfiltration, cross-agent attacks, privilege escalation, replay attacks, secret management); network connectivity patterns, multi-account/region patterns, DR, hybrid cloud; the April–June 2026 chronological release timeline and feature-level migration guidance

**Part 6:** `docs/platforms/parts/18-agentcore-strands-deep-research-report-part6.md`
- Source: Part XVI (Roadmap Prediction) + Part XVII (Adjacent Roadmap Signal) + Part XVIII (Best Practices) + Part XIX (Anti-Patterns)
- Content: evidence-scored 6/12/24-month roadmap predictions; AWS Continuum and AWS Context as adjacent trust-ladder signals; best practices across Runtime/Harness, Gateway/Policy, Identity, Memory, Code Interpreter/Browser, Observability; the anti-patterns list

**Part 7:** `docs/platforms/parts/18-agentcore-strands-deep-research-report-part7.md`
- Source: Part XX (Production Readiness Checklist) + Part XXI (Cost Optimization Guide) + Part XXII (Security Hardening Guide) + Part XXIII §44–47 (Stress Testing, Kill Switch, Circuit Breakers, Canary Release and Progressive Rollout)
- Content: the production readiness checklist (converted to markdown checkboxes); cost-optimization guidance; the layered security-hardening summary; load-testing methodology, the `StopRuntimeSession` kill switch and its documented gaps, circuit-breaking patterns, and Gateway/Optimization-based canary rollout with A/B testing

**Part 8:** `docs/platforms/parts/18-agentcore-strands-deep-research-report-part8.md`
- Source: Part XXIII §47a–51 (Feature Gates, Resume Workflow, Failover and Timeout/Retry Discipline, Exception Handling, Human-in-the-Loop Switch)
- Content: Configuration Bundles vs. LaunchDarkly AgentControl feature gating; the three resume scenarios (session continuity, async-task/ping, Step Functions human-approval pauses); failover/retry discipline and the exception-class taxonomy table; the four composable HITL patterns
- Note: the initial draft of this part measured 2728 counted words; the Sampling subsection (370 source words) was moved to the start of Part 9 to bring it to 2095

**Part 9:** `docs/platforms/parts/18-agentcore-strands-deep-research-report-part9.md`
- Source: Part XXIII §52–53 (Sampling, moved from Part 8; Synthesis) + Appendix A (Sources) + Appendix B (Glossary)
- Content: MCP protocol sampling vs. observability trace sampling; the closing eight-layer "Keep It Live" resilience-stack synthesis; the report's source bibliography and glossary

## Source-quality notes (converted-pdf artifacts fixed during migration)

- This source's `source_type: converted-pdf` artifacts were comparatively mild versus other PDF-converted sources migrated in this wave (e.g., the K8s Handbook, the AgentCore Memory Architecture Guide): most body prose survived extraction cleanly, and the primary defect was in the source's own table-of-contents block (mangled `. . .` leader-dot runs and stray `<br>` tags), which was excluded from all nine parts rather than reconstructed, since the actual section content that follows was clean and the TOC carries no unique information not already present as page headings.
- One bare-XML-tag MDX-breaking sequence was found and fixed: `<topic>-tagged` (in the Memory strategies discussion, Part 3) was wrapped in backticks as `` `<topic>` `` to prevent MDX from parsing it as an unclosed JSX element.
- One ASCII-arrow pseudo-code diagram (the Strands agentic-loop outline in Part 4, using `→` sequencing rather than box-drawing characters) was converted to a Mermaid `flowchart TD` per the diagram-standards skill's migration duty for ASCII layouts, even though it did not contain zero-tolerance box-drawing characters specifically.
- The Production Readiness Checklist (Part 7) had lost most of its checkbox markers during PDF conversion, leaving a handful of stray literal `□` (U+25A1 ballot box) characters scattered inconsistently through an otherwise plain bullet list; the entire list was normalized to proper markdown `- [ ]` checkboxes for consistency (this is not a box-drawing-range character, so it was a formatting cleanup rather than a zero-tolerance-rule fix).
- No content-loss (heading-then-nothing) artifacts were found; every chapter and appendix retained its full body text.

## Navigation

- Each part ends with a pointer to the adjacent parts; Parts 2–9 also link back to Part 1.
- Topic ID: all nine parts share the `agentcore-strands-deep-research-report` topic family.
- Part 1 is canonical (`topic_id: agentcore-strands-deep-research-report`, carries `supersedes: [docs/cloud-platforms/aws/agentcore_strands_deep_research_report.md]`).
- Parts 2–9 use `topic_id: agentcore-strands-deep-research-report-part{2..9}`, all `supersedes: []`.
