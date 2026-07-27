# Split Plan: kong-ai-gateway-guide

## Overview
- **Source:** `../knowledge-docs-old/docs/cloud-platforms/ai-gateway/kong-ai-gateway-guide.md` (7272 words)
- **Topic ID:** `kong-ai-gateway-guide`
- **Doc Type:** guide (word cap 2600/part)
- **Domain:** platforms
- **Note:** Section "13. Authentication & Authorization" (source lines 967-2125, ~3465 words) exceeds the cap alone; sub-split at its own `###` sub-headings (Auth Proxy Offloading Patterns, Credential Injection, Model Access Control, OIDC/SSO, mTLS, Vault, ACL/RBAC, Zero-Trust, Audit Logging) rather than the parent `##` boundary.

## Part 1: Intro through Observability & Analytics
- **Topic ID:** `kong-ai-gateway-guide`
- **Target Path:** `docs/platforms/08-kong-ai-gateway-guide.md`
- **Content:** Lines 1-859 of source (~2432 words)
- **Sections:** 1. What is Kong AI Gateway?, 2. Architecture Overview (diagram → Mermaid, see below), 3. Installation & Setup, 4. Core Concepts, 5. Connecting AI Providers, 6. AI Proxy Plugin, 7. Semantic Caching, 8. Rate Limiting for AI, 9. Prompt Engineering Plugins, 10. AI Request/Response Transformation, 11. AI Guardrails & Content Safety, 12. Observability & Analytics

## Part 2: Authentication & Authorization (first half)
- **Topic ID:** `kong-ai-gateway-guide-part2`
- **Target Path:** `docs/platforms/parts/08-kong-ai-gateway-guide-part2.md`
- **Content:** Lines 860-1753 of source (~2560 words)
- **Sections:** 13. Authentication & Authorization (API Key, JWT, OAuth 2.0, OIDC/SSO, Advanced Auth Patterns A–D, Credential Injection & Header Manipulation, Per-Consumer Model Access Control through Step 2)

## Part 3: Authentication & Authorization (second half) through Troubleshooting
- **Topic ID:** `kong-ai-gateway-guide-part3`
- **Target Path:** `docs/platforms/parts/08-kong-ai-gateway-guide-part3.md`
- **Content:** Lines 1754-2586 of source (~2580 words)
- **Sections:** Model Access Control (remainder), 7. OIDC/SSO Integration, 8. mTLS, 9. Vault Integration, 10. ACL & RBAC, 11. Zero-Trust Architecture, 12. Audit Logging, 13. Complete Working Example, 14. Multi-Model Routing Strategies, 15. Cost Management, 16. Streaming Responses, 17. Kubernetes Deployment, 18. Production Best Practices, 19. Troubleshooting, Quick Reference Card

## ASCII Art / Diagram Conversions
- **Source lines 68-94 (box-drawing "CLIENT APPLICATION → KONG AI GATEWAY → providers" diagram in §2 Architecture Overview):** Convert to a Mermaid `flowchart TB` — client → gateway (subgraph containing Auth/RateLimit/Cache/PromptInjection/Guardrails/Observability feeding an AI Proxy Router) → OpenAI/Anthropic/Azure-AWS-Cohere-Mistral. Lands in Part 1.

## Key Considerations
- No internal cross-links in source requiring rewrite.
- All ~100 fenced code/config snippets (Docker Compose, Kong Admin API curl calls, Terraform-adjacent YAML, Lua pre-functions) preserved verbatim within their assigned part.
- Each part gets a nav-link to the next (1→2→3) and back-link to the previous (2→1, 3→2).
