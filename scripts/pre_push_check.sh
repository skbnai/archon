#!/usr/bin/env bash
# Mirrors the .github/workflows/docs-quality.yml "quality" job locally, so
# failures are caught before push instead of discovered on GitHub after.
# Installed as .git/hooks/pre-push by scripts/install-git-hooks.sh (which
# `npm install` runs automatically via package.json's "prepare" script).
set -u
BASE_BRANCH="${PRE_PUSH_BASE:-main}"
FAIL=0

git fetch origin "$BASE_BRANCH" --depth=1 >/dev/null 2>&1 || true
CHANGED_MD=$(git diff --name-only "origin/$BASE_BRANCH"...HEAD -- 'docs/**/*.md' 2>/dev/null || true)

if [ -z "$CHANGED_MD" ]; then
  echo "pre-push: no docs/ pages changed vs origin/$BASE_BRANCH -- running --paper registry check"
  python3 scripts/registry_check.py --paper || FAIL=1
else
  echo "pre-push: checking frontmatter on changed files..."
  for f in $CHANGED_MD; do
    [ -f "$f" ] || continue
    OUT=$(python3 scripts/validate_frontmatter.py "$f" 2>&1)
    if [ "$OUT" != "OK" ]; then
      echo "  FAIL: $f"
      echo "$OUT" | sed 's/^/    /'
      FAIL=1
    fi
  done

  DOMAINS=$(echo "$CHANGED_MD" | sed -E 's#^docs/([a-z-]+)/.*#\1#' | sort -u | paste -sd, -)
  echo "pre-push: registry consistency (changed domains: $DOMAINS)..."
  python3 scripts/registry_check.py --domains "$DOMAINS" || FAIL=1
fi

echo "pre-push: near-duplicate gate..."
python3 scripts/dedup_check.py --all 0.55 || FAIL=1

echo "pre-push: forbidden filename patterns..."
BAD=$(find docs -name '*_v[0-9]*' -o -name '*_final*' -o -name '*_copy*' \
      -o -name '*-old*' -o -name '*_new*' 2>/dev/null | grep . || true)
if [ -n "$BAD" ]; then
  echo "  FAIL: versioned filenames forbidden:"
  echo "$BAD" | sed 's/^/    /'
  FAIL=1
fi

if [ "$FAIL" -ne 0 ]; then
  echo ""
  echo "pre-push: one or more docs-quality checks failed (see above)."
  echo "Fix them, or if this push is intentionally mid-wave/WIP, use 'git push --no-verify'."
  exit 1
fi

echo "pre-push: all docs-quality checks passed."
exit 0
