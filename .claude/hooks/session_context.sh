#!/usr/bin/env bash
# SessionStart: inject a tiny status line instead of making Claude re-scan the repo.
echo "WIKI STATUS: $(ls docs 2>/dev/null | wc -l) domains | \
$(grep -c 'id:' governance/CANONICAL_REGISTRY.yaml 2>/dev/null || echo 0) registered topics | \
migration manifests in migration/ | rules: Agents.md (enforced by hooks)"
