# Archon

Enterprise AI Wiki — a governed knowledge base covering the full lifecycle of building,
running, and trusting enterprise AI systems: strategy, architecture, agentic systems,
protocols, data & knowledge, platforms, trust, and operations.

## Structure

- `docs/` — published content, organized into 8 domains + 2 tracks (see
  [governance/TAXONOMY.md](governance/TAXONOMY.md))
- `governance/` — canonical topic registry, doc types, naming rules, trusted sources
- `migration/` — inventory and merge plans for content migrated from prior sources
  (not published)
- `scripts/` — validation tooling (frontmatter, registry consistency, near-duplicate
  detection, freshness reports)
- `.claude/` — agents, hooks, and skills that enforce the governance rules in this
  repo when working with Claude Code

## Governance model

Every page belongs to exactly one canonical topic, registered in
[governance/CANONICAL_REGISTRY.yaml](governance/CANONICAL_REGISTRY.yaml) before it's
created. Updates happen in place — history lives in git, provenance lives in
frontmatter. See [AGENTS.md](AGENTS.md) for the full rule set enforced by hooks and CI.

## Development

A dev container is provided (`.devcontainer/`) with Python, GitHub CLI, and Claude
Code preinstalled. Content changes are validated on PRs via
`.github/workflows/docs-quality.yml` — frontmatter schema, registry consistency,
duplicate detection, and link checking.
