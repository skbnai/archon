# Trusted Source Allowlist (research-grounding skill + researcher agent)

## Tier 1 — Primary (required for versioned/regulatory/numeric claims)
- Protocol/spec: modelcontextprotocol.io + spec GitHub, A2A spec repo, W3C, IETF RFCs
- Standards/regulators: nist.gov (AI 100-x, RMF), iso.org (42001), owasp.org (LLM Top 10),
  eur-lex.europa.eu / digital-strategy.ec.europa.eu (EU AI Act), nvlpubs.nist.gov
- India regulatory: meity.gov.in (Ministry of Electronics & IT — administers DPDP Act/Rules),
  egazette.gov.in (Official Gazette of India — authoritative for enactment/notification dates),
  indiacode.nic.in (Government of India's official legislation repository). prsindia.org
  (PRS Legislative Research) is tier-2/3 corroboration only, never sole source for a numeric claim.
- Official vendor docs: docs.claude.com / docs.anthropic.com, platform.openai.com/docs,
  cloud.google.com, learn.microsoft.com, docs.aws.amazon.com, docs.databricks.com,
  docs.nvidia.com, kubernetes.io, opentelemetry.io, langchain / langgraph /
  crewai / autogen official docs
- Peer-reviewed / arXiv (cite versioned arXiv id)

## Tier 2 — Vendor engineering blogs & official announcements
anthropic.com/news, openai.com/blog, aws.amazon.com/blogs, cloud & azure blogs,
engineering blogs of the above. Fine for capability claims; pin the date.

## Tier 3 — Reputable secondary (corroboration only)
Established tech press, well-known practitioner blogs. NEVER the sole source for
a spec, regulatory, or numeric claim. Marketing content-farms: not allowed at all.

## Rules
- Every source entry records: url, title, tier, retrieved date.
- Conflicting tier-1 sources → surface the conflict in the page; don't pick silently.
- Sources older than the artifact's latest release cannot support "current" claims.
