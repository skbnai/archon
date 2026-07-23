#!/usr/bin/env bash
# Installs this repo's git hooks into .git/hooks/. Run automatically by
# `npm install` (see package.json's "prepare" script); safe to re-run.
set -u
HOOK_DIR="$(git rev-parse --git-path hooks 2>/dev/null)"
if [ -z "$HOOK_DIR" ]; then
  echo "install-git-hooks: not inside a git repo, skipping" >&2
  exit 0
fi

cat > "$HOOK_DIR/pre-push" <<'HOOK'
#!/usr/bin/env bash
bash scripts/pre_push_check.sh
HOOK
chmod +x "$HOOK_DIR/pre-push"
echo "install-git-hooks: pre-push hook installed (runs scripts/pre_push_check.sh; bypass with git push --no-verify)"
