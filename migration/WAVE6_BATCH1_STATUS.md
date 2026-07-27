# Wave 6 Batch 1 Migration Status

Domain: `platforms` (`cloud-platforms` → `platforms`). Covers the first 10 rows of `migration/mapping.csv` for wave 6. Completed 2026-07-27.

## Done — clean, validated, registry updated

| # | Topic | Pages | Status |
|---|---|---|---|
| 1 | ai-infrastructure-silicon-landscape-2026 | 1 | ✅ complete |
| 2 | ai-gateway-full-comparison | 4 | ✅ complete |
| 3 | ai-gateway-multitenant-multicloud | 2 | ✅ complete |
| 4 | enterprise-ai-gateway | 2 | ✅ complete |
| 5 | kong-ai-gateway-guide | 3 | ✅ complete (7 ASCII diagrams/tables converted to Mermaid/markdown) |
| 6 | kong-entra-id-integration | 2 | ✅ complete (4 ASCII diagrams/tables converted) |
| 7 | aws-native-standards-first-agentic-architecture | 4 | ✅ complete |

Skipped correctly: `ai-gateway/index.md` — `MERGE-INTO hub-platforms`, not a migrate target.

All of the above: `validate_frontmatter.py` → OK, 0 box-drawing chars, 0 stray MDX `<`, word-ratio ≥0.90, `CANONICAL_REGISTRY.yaml` `supersedes` populated.

## Generated but flagged — needs a follow-up pass

| # | Topic | Pages | Issue |
|---|---|---|---|
| 8 | aws-strands-agentcore-advancedpatterns | 3 | 27 flattened code blocks |
| 9 | aws-strands-agentcore-builder-journey-kit | 3 | 19 flattened code blocks |

**Issue:** the two source PDFs lost line-break/indentation structure inside ~46 fenced code examples during their original PDF→markdown conversion — multi-line Python/config collapsed into single run-on paragraphs with stray `I`/`II` artifact characters (e.g. `` `#` II `Hook 3: retry_model...` IIIIIIIIIIIIIIIIIIIIIII `class QualityRetryHook(HookProvider):` ``). This wasn't caught by the standard migrator self-checks (frontmatter, box-drawing count, MDX-escape, word-ratio all pass) — only surfaced because one flattened block happened to contain a literal `<`.

All 6 pages are otherwise complete (frontmatter valid, content faithfully transcribed, word caps respected) and are live at their canonical paths, but `status:` was downgraded to `draft` and a known-issue note added to each, and `CANONICAL_REGISTRY.yaml` `supersedes` was deliberately left empty (not checked off as fully migrated) until the code blocks are fixed.

### Exact locations (old-repo source line numbers, for whoever picks this up)

**`AWS_Strands_AgentCore_AdvancedPatterns_v3.md` → `aws-strands-agentcore-advancedpatterns`** (27 blocks):
- Part 1 (`docs/platforms/12-...md`): source lines 209, 258, 274, 308, 345, 444
- Part 2 (`parts/12-...-part2.md`): source lines 497, 511, 563, 570, 572, 590, 592, 600, 744, 822, 839, 845, 857
- Part 3 (`parts/12-...-part3.md`): source lines 879, 1005, 1039, 1051, 1067, 1081, 1130, 1168

**`AWS_Strands_AgentCore_Builder_Journey_Kit.md` → `aws-strands-agentcore-builder-journey-kit`** (19 blocks):
- Part 1 (`docs/platforms/13-...md`): source lines 274, 276, 303
- Part 2 (`parts/13-...-part2.md`): source lines 614, 875, 888, 890, 1041, 1043
- Part 3 (`parts/13-...-part3.md`): source lines 1385, 1454, 1460, 1464, 1467, 1471, 1473, 1478, 1481, 1487

**Fix approach:** for each location, read the corrupted paragraph in the already-migrated page, reconstruct proper indented code (the variable names/logic/comments are all present in the flattened text, just missing line breaks/indentation — no new content needs to be invented), replace in place, then re-run `validate_frontmatter.py` and set `status: current` + remove the known-issue note once all blocks in that page are fixed. Update `CANONICAL_REGISTRY.yaml` `supersedes` for the topic once its 3 parts are clean.

## Batch 1 tally

10 mapping.csv rows in → 1 merge-skip, 7 topics fully done (17 pages), 2 topics generated-with-known-issue (6 pages) = 23 pages created, 15 new split-part canonical entries registered, 8 split-plans authored (`migration/split-plans/split-*.md`).

## Remaining wave 6 scope

51 of 61 mapping.csv rows for the `platforms` domain are still untouched (batch 2 onward), plus the `hub-platforms` merge-plan's final hub `index.md` update (deferred until its constituent MIGRATE targets exist).
