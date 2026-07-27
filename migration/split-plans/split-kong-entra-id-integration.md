# Split Plan: kong-entra-id-integration

## Overview
- **Source:** `../knowledge-docs-old/docs/cloud-platforms/ai-gateway/kong-entra-id-integration.md` (4378 words)
- **Topic ID:** `kong-entra-id-integration`
- **Doc Type:** guide (word cap 2600/part)
- **Domain:** platforms

## Part 1: Overview through Group & Role Mapping
- **Topic ID:** `kong-entra-id-integration`
- **Target Path:** `docs/platforms/09-kong-entra-id-integration.md`
- **Content:** Lines 1-789 of source (~2492 words)
- **Sections:** 1. Overview & Architecture (2 flow diagrams → Mermaid, see below), 2. Entra ID App Registration, 3. OAuth 2.0 Client Credentials Flow (M2M), 4. Authorization Code Flow (User Login/SSO), 5. JWT/Bearer Token Validation, 6. OIDC Plugin Full Configuration, 7. Group & Role Mapping to Kong ACL

## Part 2: Auto-Provisioning through Complete Reference Config
- **Topic ID:** `kong-entra-id-integration-part2`
- **Target Path:** `docs/platforms/parts/09-kong-entra-id-integration-part2.md`
- **Content:** Lines 790-1541 of source (~2122 words)
- **Sections:** 8. Per-Consumer Auto-Provisioning, 9. Conditional Access & MFA Enforcement, 10. Multi-Tenant Entra ID Setup, 11. Token Introspection & Revocation, 12. Managed Identity for Kong on Azure, 13. Troubleshooting Entra ID Auth Issues, 14. Complete Working Reference Config, Quick Reference: Entra ID Endpoints

## ASCII Art / Diagram Conversions
- **Source lines 44-60 ("FLOW: M2M" box diagram in §1):** Convert to Mermaid `sequenceDiagram` — App/Service → Entra ID Token Endpoint (client_id+secret) → access_token; App/Service → Kong AI Gateway (Bearer JWT) → validates via Entra JWKS → checks roles/scopes → injects LLM master key → OpenAI API.
- **Source lines 62-79 ("FLOW: User SSO" box diagram in §1):** Convert to Mermaid `sequenceDiagram` — Browser → Kong → 302 redirect → Entra Login → user authenticates → auth code → Browser → Kong exchanges code for tokens with Entra → session cookie set, user mapped to Kong consumer, group membership enforced → OpenAI API.
- Both land in Part 1.

## Key Considerations
- No internal cross-links in source requiring rewrite.
- Part 1 ends with nav-link forward to Part 2.
- All ~80 fenced code/config snippets (Azure CLI, Kong Admin API, declarative `deck` YAML) preserved verbatim within their assigned part.
