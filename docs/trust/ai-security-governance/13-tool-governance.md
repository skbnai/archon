---
title: "Tool Governance"
doc_type: guide
domain: trust
status: current
topic_id: tool-governance
last_reviewed: 2026-07-27
maturity: practitioner
supersedes: [docs/ai-security-governance/deep-mind/Part09_Tool_Governance.md]
tags: [ai-security, tool-governance, deepmind, mcp]
covers_version: "as of 2026"
---

Enterprise tool registry, approval workflow, MCP governance gaps, tool trust scoring, secrets management, and tool observability for AI agent tool use.

## The Tool Governance Imperative

Tools are the primary interface through which AI agents affect the world. A tool invocation can read sensitive data, modify production systems, make financial transactions, communicate on behalf of the enterprise, or trigger downstream automated processes. The security posture of an agent deployment is fundamentally bounded by the security posture of its tools: a perfectly aligned agent with poorly governed tools is a serious security risk.

**Tool governance scope:** includes all mechanisms by which agents invoke external functionality — MCP servers, OpenAPI-defined REST endpoints, function calling, subprocess execution, database queries, file system operations, SDK method calls, and internal microservice calls via any protocol.

## Enterprise Tool Registry

Every tool available to enterprise AI agents must be registered in a centralized Tool Registry before any agent can invoke it. The registry serves as the single source of truth for tool metadata, trust assessments, capability definitions, and version history. Agents cannot discover or invoke unregistered tools.

| Registry Field | Description | Source |
|---|---|---|
| Tool ID | Unique, immutable identifier (UUID) | Registry on registration |
| Tool Name + Version | Human-readable name and semantic version | Tool developer on submission |
| Tool Type | MCP / REST / Function / Internal / External | Tool developer on submission |
| Capability Spec | Structured definition of what the tool can do (read/write/execute/external) | Tool developer on submission |
| Endpoint / Package | URL, NPM package, or deployment reference | Tool developer on submission |
| Trust Score | 0-100 computed trust score | Registry computed on approval |
| Security Assessment | Last security review findings and date | Security team |
| SBOM | Software Bill of Materials for tool implementation | Tool developer on submission |
| Allowable Agents | Agent types authorized to use this tool | AI Security team |
| Rate Limits | Maximum invocations per agent per time period | Ops team configuration |
| Data Classification | Classification of data the tool can access | Data governance team |
| Approval Status | Draft / Review / Approved / Deprecated / Retired | Registry workflow |
| Behavioral Tests | Last behavioral test run results and date | Automated testing pipeline |

## Tool Approval Workflow

**Tool submission and review process:**

1. **Developer Submission:** tool developer submits tool specification, SBOM, source code reference, and self-assessment. The tool receives DRAFT status.
2. **Automated Scanning:** CI/CD pipeline scans tool code for known vulnerabilities (CVE matching), secrets in code, dependency vulnerabilities, and license compliance. Tools with critical findings are blocked at this stage.
3. **Security Review:** the AI Security team reviews tool capability scope (does the spec match the implementation?), data access scope, external call patterns, secret handling, and error handling (does the tool expose sensitive data in errors?).
4. **Behavioral Testing:** the tool is deployed in an isolated sandbox with monitoring. An automated test suite runs normal operation tests, adversarial input tests, boundary condition tests, and injection attempt tests. A behavioral baseline is captured.
5. **Privacy Review:** the data governance team reviews what data the tool accesses, whether it sends data externally, retention of data within the tool, and GDPR/CCPA compliance for user data.
6. **Approval Decision:** a joint decision by AI Security, Data Governance, and AI Platform teams. Approval may be conditional (limited to specific agent types or data classifications).
7. **Registry Publication:** the tool is published to the registry with metadata, trust score, and allowable agent list. The version is pinned.

## MCP (Model Context Protocol) Governance

**MCP security model gaps.** MCP, while providing a standardized interface for tool use, has significant security gaps in its base specification that enterprises must address through additional controls:

| Gap | Risk | Mitigation |
|---|---|---|
| No authentication in base spec | MCP client-server communication has no mandatory authentication; any client can call any server | Implement mTLS for all MCP connections; MCP server validates client certificate against agent allowlist |
| No response integrity | MCP tool results are not signed; MITM can modify results without detection | Implement HMAC signatures on all MCP responses; client verifies signature before processing |
| No server discovery security | MCP server discovery (stdio, SSE) lacks integrity guarantees | Use registry-controlled server URLs; reject dynamic discovery from untrusted sources |
| No audit trail in spec | MCP does not mandate logging of tool calls or results | Implement audit proxy that logs all MCP traffic including full request/response |
| No rate limiting | MCP does not define rate limiting; DoS possible through tool calls | Implement rate limiting at the MCP proxy layer |
| Tool result injection | Malicious MCP server can return results containing injection payloads | Scan all MCP tool results for injection patterns before including in agent context |

## Tool Trust Scoring

Tool trust scores enable dynamic, risk-proportionate access decisions. A higher-trust tool can be invoked more freely; lower-trust tools require additional approval. Trust scores are computed from multiple factors and updated continuously.

**Trust score components:**

| Factor | Weight | Score Components |
|---|---|---|
| Provenance | 20% | Open source (verifiable) vs. closed source; vendor reputation; CVE history of developer |
| Code Quality | 15% | Static analysis findings; test coverage; dependency vulnerability count |
| Behavioral Testing | 25% | Pass rate on security behavioral tests; anomaly rate in sandbox testing; injection resistance score |
| Production History | 20% | Invocation volume; error rate; incident history; time since last security issue |
| External Assessment | 10% | Third-party security audit; CVE disclosures; vendor security certifications |
| Data Handling | 10% | Scope of data access; external data transmission; retention practices |

**Trust score usage in authorization:**

| Trust Score | Label | Authorization Policy |
|---|---|---|
| 90-100 | Highly Trusted | Agent can invoke without approval; standard rate limits apply |
| 70-89 | Trusted | Agent can invoke with enhanced logging; rate limits enforced |
| 50-69 | Conditionally Trusted | Invocation permitted only for approved task types; elevated logging |
| 30-49 | Low Trust | Human approval required for each invocation in sensitive contexts |
| 10-29 | Restricted | Human approval required for all invocations; supervisor AI monitor required |
| 0-9 | Untrusted | Not invocable by agents; requires re-assessment before use |

## Secrets Management for Tool Credentials

Tools require credentials to access external services — API keys, OAuth tokens, database passwords, and certificates. These secrets must never be embedded in agent prompts, hardcoded in tool configurations, or accessible through agent memory. A dedicated secrets management system must provide dynamic, short-lived credentials to tools at invocation time.

**Secrets architecture:**

- **HashiCorp Vault / AWS Secrets Manager / Azure Key Vault:** enterprise secrets vault; tools retrieve credentials via authenticated API at runtime.
- **Dynamic Secrets:** credentials generated on-demand per tool invocation with minimal TTL (e.g., 5-minute database passwords).
- **Secrets Injection:** secrets injected into the tool execution environment at invocation time via environment variables or volume mounts; never persisted.
- **Credential Rotation:** all credentials rotated on a defined schedule; breached credentials invalidated within 15 minutes.
- **Agent Secret Isolation:** each agent instance has access only to secrets for its authorized tool set; no cross-agent secret sharing.
- **Audit of Secret Access:** every secret access logged with which agent, which tool, which task, and timestamp; anomalous access triggers an alert.

## Tool Observability

Every tool invocation must generate telemetry data that enables performance monitoring, security audit, behavioral analysis, and incident investigation. Tool observability is a first-class architectural requirement, not an afterthought.

| Telemetry Type | Collected Data | Retention | Primary Use |
|---|---|---|---|
| Invocation Log | Tool ID, agent ID, task ID, parameters (masked), timestamp, duration | 90 days | Audit, debugging |
| Result Log | Tool ID, result type, result classification, size, anomaly flags | 90 days | Security analysis |
| Error Log | Tool ID, error type, error message (sanitized), retry count | 30 days | Operations |
| Performance Metric | Latency, error rate, timeout rate per tool and agent type | 1 year | Operations, SLA |
| Behavioral Metric | Usage patterns, parameter distributions, result patterns | 1 year | Threat detection |
| Security Event | Policy violations, anomaly detections, injection attempts | 3 years | Compliance, forensics |

## Related

- [Memory Governance](12-memory-governance.md)
- [Reasoning Governance](14-reasoning-governance.md)
- [AI Control Series Overview](01-ai-control-series-overview.md)
