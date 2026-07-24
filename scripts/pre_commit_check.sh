#!/usr/bin/env bash
# Fast per-commit gate: frontmatter + registry check on staged docs/ pages.
# Mirrors the same two checks in pre_push_check.sh but scoped to what's
# staged for this commit, so problems surface before push instead of after.
# Installed as .git/hooks/pre-commit by scripts/install-git-hooks.sh.
set -u
FAIL=0

STAGED_MD=$(git diff --cached --name-only --diff-filter=ACM -- 'docs/**/*.md' 2>/dev/null)

if [ -z "$STAGED_MD" ]; then
  echo "pre-commit: no docs/ pages staged, skipping frontmatter/registry check"
  exit 0
fi

echo "pre-commit: checking frontmatter on staged files..."
for f in $STAGED_MD; do
  [ -f "$f" ] || continue
  OUT=$(python3 scripts/validate_frontmatter.py "$f" 2>&1)
  if [ "$OUT" != "OK" ]; then
    echo "  FAIL: $f"
    echo "$OUT" | sed 's/^/    /'
    FAIL=1
  fi
done

DOMAINS=$(echo "$STAGED_MD" | sed -E 's#^docs/([a-z-]+)/.*#\1#' | sort -u | paste -sd, -)
echo "pre-commit: registry consistency (staged domains: $DOMAINS)..."
python3 scripts/registry_check.py --domains "$DOMAINS" || FAIL=1

if [ "$FAIL" -ne 0 ]; then
  echo ""
  echo "pre-commit: one or more docs-quality checks failed (see above)."
  echo "Fix them, or if this commit is intentionally mid-wave/WIP, use 'git commit --no-verify'."
  exit 1
fi

echo "pre-commit: frontmatter + registry checks passed."
exit 0
