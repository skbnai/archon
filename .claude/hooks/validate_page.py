#!/usr/bin/env python3
"""PostToolUse: validate frontmatter of any docs/ page just written.
Exit 2 surfaces the error to Claude so it fixes the page immediately."""
import json, subprocess, sys

try:
    data = json.load(sys.stdin)
except Exception:
    sys.exit(0)
path = (data.get("tool_input") or {}).get("file_path") or ""
if not (path and "docs/" in path and path.endswith(".md")):
    sys.exit(0)
r = subprocess.run([sys.executable, "scripts/validate_frontmatter.py", path],
                   capture_output=True, text=True)
if r.returncode != 0:
    print(f"Frontmatter invalid for {path}:\n{r.stdout}{r.stderr}\n"
          f"Fix per governance/DOC_TYPES.md before continuing.", file=sys.stderr)
    sys.exit(2)
sys.exit(0)
