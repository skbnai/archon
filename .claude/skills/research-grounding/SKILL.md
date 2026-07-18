---
name: research-grounding
description: >
  MANDATORY before writing or updating any wiki page that contains factual or
  technical claims about products, protocols, specs, standards, versions,
  regulations, benchmarks, pricing, or vendor capabilities. Also use when a
  freshness audit flags a page, or when the user asks to "update", "refresh",
  or "verify" content. Grounds every claim in trusted primary sources and
  produces citation frontmatter.
---

# Research Grounding

Purpose: no claim ships from memory. Every page is verifiable.

## Procedure

1. **Classify the claims** in the draft/page: (a) timeless concept, (b) versioned
   fact (spec, API, product feature), (c) regulatory/standards fact, (d) market/
   vendor claim, (e) benchmark/number. Types b–e REQUIRE grounding.
2. **Pick sources from the allowlist** in `governance/TRUSTED_SOURCES.md`
   (tier 1 = primary: spec repos, official docs, standards bodies, regulator
   sites; tier 2 = vendor engineering blogs; tier 3 = reputable secondary —
   allowed only to corroborate, never as sole source for a b/c/e claim).
3. **Delegate the fetching to the `researcher` subagent** — do NOT pull long
   pages into the main context. Ask it for: claim → verdict
   (confirmed / corrected / unverifiable) → source URL → retrieval date →
   one-line evidence summary.
4. **Apply verdicts**: correct the draft for every 'corrected' claim; DELETE or
   explicitly caveat every 'unverifiable' claim. Never keep an unverified
   number.
5. **Record provenance** in frontmatter:
   ```yaml
   sources:
     - url: https://…
       title: "…"
       tier: 1
       retrieved: 2026-07-18
   covers_version: "MCP spec 2026-07-28"
   ```
   and add inline citation footnotes for numbers, dates, and spec behaviors.
6. **Version pinning**: any page about a versioned artifact must state the
   version it covers in `covers_version` and in the intro sentence.

## Red flags — stop and re-ground

- A number with no source. A spec behavior described without a spec link.
- "As of <date>" older than 6 months on a `status: current` page.
- Only tier-3 sources for a versioned/regulatory claim.
