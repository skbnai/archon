---
title: "Identity/MCP/A2A Security Blueprint: MCP Security (Part 2)"
doc_type: guide
domain: trust
status: current
topic_id: identity-mcp-a2a-security-blueprint-part2
last_reviewed: 2026-07-27
maturity: practitioner
supersedes: [docs/ai-security-governance/security/02-Identity-MCP-A2A-Security-Blueprint.md]
tags: [ai-security, mcp, tool-poisoning, gateway]
covers_version: "as of 2026"
---

MCP protocol internals, the documented MCP threat landscape (context poisoning, rug pulls, tenant escape), the security tooling landscape, and the five-stage enterprise MCP gateway validation pipeline.

## Model Context Protocol (MCP) Security

MCP has become, in roughly eighteen months, the backbone integration protocol connecting AI agents to enterprise tools, data sources, and workflows — and its security posture has predictably followed the trajectory of every fast-adopted integration protocol before it: capability outpacing governance, followed by a wave of disclosed vulnerabilities, followed by the gateway and scanning tooling now emerging to close the gap.

**Protocol internals.** MCP is built on JSON-RPC 2.0 for its message format, with two principal transports in production use: Server-Sent Events (SSE) for remote/networked MCP servers and STDIO for local process-to-process communication. Transport security and session management are where the protocol's early design choices have caused the most operational pain: MCP's specification leaves a great deal of authentication and session-handling behavior to implementers rather than mandating it — the same root cause behind both the MCP vulnerability landscape below and the A2A authentication gaps covered in Part 3.

| Transport | Typical Deployment | Primary Security Consideration |
|---|---|---|
| STDIO | Local MCP servers run as a subprocess of the client (e.g., a developer's IDE-integrated coding assistant) | Inherits the local process's full privilege; a malicious or compromised local MCP server can read SSH keys, cloud credentials, and environment variables directly |
| SSE / HTTP | Remote, networked MCP servers shared across an organization | Requires explicit transport security (TLS), session-token handling, and — critically — protection against cross-session and cross-tenant data leakage at the server |

## MCP Threat Landscape

This is not a theoretical risk category. Independent research analyzing over 7,000 public MCP servers found that 36.7% were vulnerable to server-side request forgery (SSRF). Separately, an analysis of 2,614 MCP implementations found that 82% used file operations prone to path traversal, 67% used APIs related to code injection, and 34% used APIs susceptible to command injection. The Vulnerable MCP Project tracks more than 50 known MCP vulnerabilities across servers, clients, and infrastructure, with 13 rated critical, and public CVE disclosures specific to MCP have continued at pace through 2026, including at least one CVSS 9.6 remote-code-execution flaw in a widely downloaded MCP package.

**Context / Tool Poisoning** is the highest-leverage attack class observed to date. A tool's description metadata — text the agent reads as part of its reasoning context but that a human reviewer typically never sees — contains hidden instructions. A tool described as "fetch data from S3" can also instruct the agent, invisibly, to exfiltrate the results to an attacker-controlled endpoint. Because the model treats tool descriptions as trusted context, this is structurally similar to indirect prompt injection but specific to the tool-discovery surface.

**Tool Spoofing and Rug Pulls** occur when a malicious server registers tools with names closely resembling legitimate ones (tool name collision), tricking the agent into selecting the wrong tool, or when a previously vetted, safe tool is silently updated post-installation with malicious instructions — a "rug pull" — meaning point-in-time review of a tool's safety provides no durable guarantee.

**Dynamic Tool Escalation** happens when an agent is granted a broad tool at low risk for an initial benign task, and the same standing grant is later reused for a higher-risk action the original approval never contemplated — the MCP-specific instance of privilege creep. **Tenant Escape** occurs in multi-tenant MCP server deployments where insufficient isolation between tenants' sessions, credentials, or cached context allows one tenant's agent to read or influence another's data. **Schema Manipulation** happens when tool input/output schemas are altered or under-validated such that an agent can be induced to pass malicious parameters (oversized payloads, path-traversal strings, injection payloads) that the receiving system does not adequately validate. **Credential Aggregation Risk** arises because MCP servers commonly store OAuth tokens for multiple integrated downstream services in one place, making a single compromised MCP server a single point of failure across every connected system — independent audits have documented more than 12,000 exposed API keys and passwords resulting from insecure MCP credential handling in configuration files.

**Emerging standard: OWASP MCP Top 10.** OWASP's dedicated MCP Top 10 entered beta in April 2026 and currently enumerates ten categories: token mismanagement and secret exposure, privilege escalation via scope creep, tool poisoning, software supply-chain attacks, command/code injection, and several others still stabilizing as the project moves toward a ratified release. Treat it as directionally authoritative but not yet final.

## MCP Security Controls and Tooling Landscape

A distinct tooling category has emerged specifically for MCP security, splitting roughly into pre-deployment scanners and runtime inspection/enforcement tools:

| Category | Representative Tools | Function |
|---|---|---|
| Static / pre-deployment scanners | MCP-Scan, Cisco mcp-scanner, Snyk agent-scan, Invariant, Backslash Security | Analyze tool definitions, descriptions, and schemas before deployment for poisoning patterns, injection risk, and known-vulnerable dependencies |
| Runtime gateways | Docker MCP Gateway, Runlayer, agentgateway, MintMCP, enterprise-built gateways | Centralize routing, authentication, and policy enforcement for all MCP traffic; re-validate tool schemas and call parameters at both discovery time and invocation time |
| Specialized vendor offerings | MCP Guardian, MCP Safety Scanner, Pillar Security, Wiz MCP Security guidance/posture tooling | Combine scanning, runtime monitoring, and posture management specifically for MCP estates, often integrated into broader AI-SPM platforms |

The architectural lesson from documented tool-poisoning disclosures is that validating tool schemas only at discovery time is necessary but not sufficient: a model that receives a clean, validated tool list can still be manipulated at the moment of invocation into calling that same clean tool with malicious parameters. Effective gateway architectures therefore gate twice — once when tools are discovered and registered, and again, against the identical schema, every time the tool is actually invoked.

## Enterprise MCP Gateway — Implementation Blueprint

The pattern converging as enterprise best practice treats MCP tool discovery the way a load balancer treats inbound HTTP traffic: as untrusted ingress that must be inspected and validated before being forwarded anywhere. This moves the security boundary from the individual developer's laptop or IDE configuration — where it lives by default and is invisible to any central team — to the network, where one platform engineering team can own and update policy for the entire organization regardless of how many MCP clients exist.

**Five-stage gateway validation pipeline:**

1. **Discovery-time schema validation** — every tool definition and description from any MCP server, before it ever reaches an agent's context, is validated against expected schema and scanned for hidden-instruction patterns in metadata fields.
2. **Server allowlisting and registration** — only MCP servers explicitly registered by platform engineering (scoped by environment and team) are reachable; no agent or developer's local configuration can silently add an unapproved server.
3. **Identity and transport enforcement** — every MCP connection requires mutual TLS and an authenticated workload identity, tying directly back to the SPIFFE substrate; unauthenticated or self-signed connections are rejected at the gateway.
4. **Policy evaluation at invocation** — every tool call is evaluated against centrally managed policy (Cedar or OPA) at the moment of the call, re-validating both the caller's authorization and the call's parameters against the original schema — the second gate that catches malicious parameters even when the tool definition itself was clean.
5. **Tamper-evident audit logging** — every allow, deny, and policy mutation is logged with cryptographic integrity protection, providing the immutable record required for incident response and audit.

| Control Layer | Technology | Purpose |
|---|---|---|
| Transport | mTLS | Mutual authentication and encryption for every MCP connection, eliminating unauthenticated default transports |
| Authorization policy | Cedar or OPA | Centrally defined, machine-evaluated policy for every tool call, independent of any individual MCP server's own (often absent) access control |
| Schema enforcement | JSON Schema Validation | Strict validation of tool inputs and outputs at both discovery and invocation time |
| Supply-chain integrity | Tool Signing | Cryptographic signatures over tool definitions so a server cannot silently modify a previously approved tool (defeating the "rug pull" pattern) |
| Execution containment | WASM Sandboxing | Sandboxes tool execution itself, limiting blast radius even if a malicious or compromised tool is invoked |

## Related

- [Identity & Non-Human Identity for Agentic AI (Part 1)](../34-identity-mcp-a2a-security-blueprint.md)
- [Identity/MCP/A2A Security Blueprint: A2A Security (Part 3)](34-identity-mcp-a2a-security-blueprint-part3.md) — A2A protocol mechanics, the A2A threat landscape, and the unified identity-to-trust chain
- [Agent, Tool & MCP Authorization](../27-agent-tool-mcp-authorization.md)
