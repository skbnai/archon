---
name: dedup-canonicalization
description: >
  Use whenever creating a new page, migrating content from the old repo, merging
  documents, or when two pages appear to cover the same topic. Enforces the
  one-canonical-page rule and the supersede workflow. This skill is the
  procedure; the hooks and CI are the enforcement.
---

# Dedup & Canonicalization

## Before creating anything

1. Search `governance/CANONICAL_REGISTRY.yaml` for the topic (check `id`,
   `aliases`, `canonical` path). Grep, don't read the whole file.
2. **Topic exists** → you may only EDIT the canonical page (or a registered
   spoke). Do not create a sibling.
3. **Topic missing** → invoke the `librarian` agent to register it (id, domain,
   canonical path, aliases). Only after the registry commit may you write the file.

## Merging duplicates (the old repo's failure mode — do it right)

Given a duplicate cluster (from `migration/inventory.csv` `dup_cluster` column):

1. Pick ONE survivor: prefer (a) most recent `last_reviewed`, (b) most complete,
   (c) best structure — in that order. Record the choice + rationale in the
   cluster's merge plan under `migration/merge-plans/`.
4. Merge unique content from losers INTO the survivor (diff for unique sections;
   don't concatenate).
5. Losers are NOT copied to the new repo. In the registry, list loser old-paths
   under the topic's `supersedes:` so redirects can be generated.
6. One PR = whole cluster resolved. A PR that migrates a loser page alongside its
   survivor must fail review.

## Absolute rules (hook-enforced, but internalize them)

- Never resolve a blocked write by renaming (`-2`, `_new`, different folder).
- Never leave two pages with `status: current` for one registry topic.
- "Enhance existing" beats "create new" whenever the topic is registered.
