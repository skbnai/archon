---
title: "Cybersecurity Architect Part 6: Identity Architecture"
doc_type: guide
domain: trust
status: current
topic_id: identity-architecture
last_reviewed: 2026-07-28
maturity: practitioner
supersedes: [docs/cybersec-architect/06-identity-architecture.md]
tags: [cybersec-architect, identity, oauth, spiffe, secrets-management, policy-as-code]
covers_version: "as of 2026"
---

Identity is the primary control plane for enterprise security in the cloud and AI era. This part covers the full identity spectrum — human to AI agent — and the protocols, patterns, and controls each requires.

## Identity Taxonomy

| Identity Type | Description | Scale | Primary Protocol | Key Challenge |
| --- | --- | --- | --- | --- |
| Human | Employees, contractors, partners, customers | Thousands | OIDC / SAML / FIDO2 | Phishing, credential theft, privilege creep |
| Machine | Servers, services, CI/CD, IoT | Tens of thousands | X.509 / mTLS / OAuth | Certificate sprawl, expiry management |
| AI | LLM endpoints, embedding services, model APIs | Hundreds | OAuth 2.1 / API keys | Key rotation, abuse detection |
| Agent | Autonomous AI agents, orchestrators | Hundreds–thousands | SPIFFE / Managed Identity / IETF AIMS | Delegation chains, least privilege, ephemeral nature |
| Service | Microservices, APIs, serverless functions | Thousands | SPIFFE / mTLS / OAuth | Service mesh complexity |
| Robot | Physical robots, RPA bots, automation platforms | Varies | OAuth / mTLS | Physical-digital boundary, offline scenarios |
| Digital Workforce | Virtual agents representing human roles | Varies | Entra Agent ID / OBO | Accountability, delegation scope |

## Authentication

Human authentication factors rank by phishing resistance: password (knowledge-based, not phishing-resistant, legacy only) and SMS OTP (avoid — SIM-swap risk) sit at the weak end; TOTP and push notifications are partial improvements; FIDO2/passkeys (possession + biometric), hardware tokens (YubiKey), and certificate-based auth (CAC/PIV) are the only phishing-resistant options and should be targeted for 100% adoption by 2027 — FIDO2 is the sole method that is phishing-resistant by design.

Machine and service authentication: long-lived API keys carry high risk (key theft/leak) and need rotation policy plus git secret-scanning; mTLS carries low risk, managed via cert-manager or Vault PKI; OAuth client credentials carry medium risk, mitigated with short-TTL tokens and vaulted secrets; workload identity federation and SPIFFE SVID both carry very-low risk since no credential exists to steal — identity is asserted via OIDC or automatic SPIRE-issued certificates.

Agent authentication follows the same priority order established in Part 5: managed identity first (agent workload claims identity from cloud IMDS, no credential storage), SPIFFE SVID second (SPIRE attests via k8s annotations or TPM, issues short-lived X.509), OAuth client credentials third (vaulted secret, frequent rotation) as fallback only. Hardcoded API keys in prompts, environment variables, or source control are never acceptable.

## Authorization

Five models cover the authorization landscape: RBAC (permissions on roles, the default for most IAM systems), ABAC (permissions on subject/resource/action/environment attributes, for fine-grained contextual decisions), ReBAC (permissions on entity relationships — the Google Zanzibar model, for Drive-like sharing and hierarchical ownership), PBAC (a centralized policy engine evaluating access in real time — OPA, Cedar — for Zero Trust enforcement), and the emerging IBAC (AI-evaluated intent, not yet production-ready for sensitive systems).

Modern authorization is code-based and evaluated at runtime. OPA/Rego:

```rego
allow if {
    input.principal.type == "ai_agent"
    agent_authorized(input.principal.agent_id)
    input.resource.classification != "restricted"
    input.action == "read"
}

agent_authorized(agent_id) if {
    data.authorized_agents[agent_id].status == "active"
    data.authorized_agents[agent_id].expiry > time.now_ns()
}
```

AWS Cedar:

```cedar
permit(
    principal is Agent,
    action == Action::"ReadDocument",
    resource is Document
) when {
    principal.status == "authorized" &&
    resource.classification != "restricted" &&
    context.task_id != ""
};
```

Agent authorization scopes must be task-specific and time-limited. A representative per-task JWT carries `sub: agent:research-agent-001`, an audience limited to the specific MCP servers needed (e.g., `search`, `docs`), a `scope` of `search:read docs:read`, a `task_id`, a 15-minute expiry, and a `principal_user` claim recording the delegating human. This achieves four things at once: the agent can reach only the named MCP servers, it can only read, the token's short window limits abuse even if stolen, and the delegation chain is recorded.

## Delegation

Token exchange (RFC 8693) lets one principal trade its token for a token representing a different principal or narrower scope: a human token with full access exchanges down to a task-scoped agent token, which can exchange further down to an even-more-limited sub-agent token. Key parameters: `subject_token` (the token being exchanged), `requested_token_type`, `scope` (must be a subset of the subject token's scope), and `audience` (the intended recipient).

On-Behalf-Of (OBO) is the specific token-exchange pattern for a service acting on a user's behalf. In the Microsoft Entra OBO flow: the user authenticates and receives a user token scoped to `read_documents`; the user delegates to an agent; the agent presents the user token plus its desired scope (which must be a subset of the user's scopes) to Entra; Entra issues an agent token carrying `sub: agent_id`, `on_behalf_of: user@corp.com`, and the constrained scope; the agent calls the document API with this token; the API verifies both that the agent is authorized and that it is acting for an identified user.

A Security Token Service issues, validates, and exchanges tokens. Leading STS platforms: Microsoft Entra ID (SAML, OIDC, OBO, managed identity, Entra Agent ID), AWS IAM/STS (AssumeRole, OIDC federation, Cognito), Google Cloud IAM (workload identity federation, service account keys), HashiCorp Vault (dynamic secrets, PKI, pluggable auth methods), and Keycloak (open-source OIDC/SAML with extensible flows).

## Token Standards

JWT (`header.payload.signature`, base64url dot-separated) remains the most widely used API authorization token format. Security requirements: always verify the signature before trusting claims, validate `exp`/`iss`/`aud`, use short expiry (5–15 minutes) for sensitive operations, store in HttpOnly cookies rather than localStorage in browser contexts, and use a JWK endpoint for public-key discovery. PASETO is a more secure alternative eliminating common JWT pitfalls — no algorithm-confusion attacks since the algorithm is fixed by version, unambiguous Local/Public token types, and simpler correct implementation — recommended for new builds without a JWT backward-compatibility requirement.

Short-lived credentials limit the abuse window of theft, force automated rotation, and reduce blast radius. Target maximum lifetimes: user session tokens 1–8 hours (re-authentication or refresh token); agent access tokens 5–15 minutes (automatic re-issuance); service-to-service tokens 15–60 minutes (client-credentials flow or managed identity); legacy API keys 90 days (automated rotation via secrets manager); TLS certificates 90 days (cert-manager/ACME); SPIFFE SVIDs 1 hour (automatic SPIRE renewal); cloud IAM temporary credentials 1–12 hours (instance metadata service).

## Secrets Management

Five anti-patterns must be eliminated: hardcoded credentials in source code (any repo access becomes credential theft — fix via secret scanning, immediate revocation, and a secrets manager); secrets in environment variables (process listing or logging exposes them — fix via dynamic injection); secrets in container images (an image pull becomes credential theft — fix via build-time CI injection or managed identity); long-lived shared credentials (actions can't be attributed to an individual — fix via a unique credential per identity); and plaintext secrets in config files (fix via encryption at rest and references instead of values).

A secrets-manager architecture authenticates the application or agent via managed identity, evaluates an authorization policy, generates a dynamic secret scoped to the caller and short-lived, and lets the application use it against the target resource until it expires — at which point the next call generates a fresh one. HashiCorp Vault's dynamic secrets exemplify this: a unique database username/password is generated per application instance, and Vault revokes it automatically when the instance shuts down, so no stored reusable credential ever exists.

Certificate expiry has caused major outages (Microsoft Teams 2020, Azure AD 2019), making rotation automation mandatory: cert-manager for Kubernetes-native ACME or internal-CA issuance and renewal; Vault PKI as an internal CA for service-to-service TLS; AWS ACM or Azure Key Vault for managed cloud-resource certificates; and monitoring that alerts at 30 days remaining and escalates to critical at 7 days.

Workload identity federation eliminates long-lived secrets entirely by trusting the workload's own identity. In the GitHub Actions → AWS pattern: GitHub's OIDC provider issues a JWT for the running workflow; the workflow presents it to AWS STS; STS validates the JWT signature against GitHub's JWKS endpoint; if valid and the role's trust policy matches, STS issues short-lived AWS credentials scoped to the workflow's duration only — no AWS access key or secret is stored anywhere.

## Related

- [Cybersecurity Architect Part 5: Agentic AI Security](05-agentic-ai-security.md)
- [Cybersecurity Architect Part 3: Security Domains](03-security-domains.md)
- [Cybersecurity Architect Part 7: Cloud Security](07-cloud-security.md)
