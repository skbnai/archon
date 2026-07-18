#!/usr/bin/env python3
"""PreToolUse guard for Write/Edit tools.

Blocks (exit code 2 => Claude Code blocks the tool call and shows stderr):
  1. Versioned/duplicate filename patterns anywhere in repo.
  2. Creating a NEW .md under docs/ whose path is not in CANONICAL_REGISTRY.yaml.
Reads the tool input JSON from stdin per Claude Code hooks contract.
"""
import json, os, re, sys

FORBIDDEN = re.compile(
    r"(_v\d+|_final|_new|_old|_copy|_backup|-old|-copy|-final|-updated|\(\d+\))"
    r"(?=\.[a-z]+$)", re.I)

def registry_paths():
    try:
        import yaml
        with open("governance/CANONICAL_REGISTRY.yaml") as f:
            reg = yaml.safe_load(f) or {}
        paths = set()
        for topic in (reg.get("topics") or []):
            if topic.get("canonical"): paths.add(topic["canonical"])
            for p in topic.get("pages", []): paths.add(p)
        return paths
    except Exception:
        return None  # registry unreadable -> fail open on rule 2, CI still catches it

def main():
    try:
        data = json.load(sys.stdin)
    except Exception:
        sys.exit(0)
    path = (data.get("tool_input") or {}).get("file_path") or ""
    if not path:
        sys.exit(0)
    rel = os.path.relpath(path)
    rel_posix = rel.replace(os.sep, "/")

    if FORBIDDEN.search(os.path.basename(rel)):
        print(f"BLOCKED: '{rel}' uses a versioned/duplicate filename pattern. "
              f"Update the canonical file in place; use frontmatter 'supersedes' "
              f"for provenance. See Agents.md rule 2.", file=sys.stderr)
        sys.exit(2)

    if rel_posix.startswith("docs/") and rel_posix.endswith(".md") and not os.path.exists(rel):
        reg = registry_paths()
        if reg is not None and rel_posix not in reg:
            print(f"BLOCKED: new page '{rel_posix}' is not registered in "
                  f"governance/CANONICAL_REGISTRY.yaml. Register the topic first "
                  f"(librarian agent), then write. See Agents.md rule 1.",
                  file=sys.stderr)
            sys.exit(2)
    sys.exit(0)

if __name__ == "__main__":
    main()
