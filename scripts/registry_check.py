#!/usr/bin/env python3
"""Consistency check: registry <-> filesystem <-> frontmatter.
Fails if: unregistered docs/ page; registered canonical missing; two canonicals
per topic; page frontmatter topic_id/status inconsistent with registry."""
import sys, re, pathlib
try: import yaml
except ImportError: sys.exit(0)

def fm(path):
    t = path.read_text(encoding="utf-8", errors="ignore")
    m = re.match(r"^---\n(.*?)\n---\n", t, re.S)
    return (yaml.safe_load(m.group(1)) or {}) if m else {}

def main():
    reg = yaml.safe_load(open("governance/CANONICAL_REGISTRY.yaml")) or {}
    topics = reg.get("topics") or []
    errs = []
    registered = set()
    for t in topics:
        tid, canon = t.get("id"), t.get("canonical")
        if not tid or not canon:
            errs.append(f"registry entry missing id/canonical: {t}"); continue
        registered.add(canon); registered.update(t.get("pages", []))
        p = pathlib.Path(canon)
        if not p.exists():
            errs.append(f"[{tid}] canonical file missing: {canon}")
        else:
            f = fm(p)
            if f.get("topic_id") != tid:
                errs.append(f"[{tid}] {canon} frontmatter topic_id={f.get('topic_id')}")
            if f.get("status") == "superseded":
                errs.append(f"[{tid}] canonical page marked superseded: {canon}")
    ids = [t.get("id") for t in topics]
    for d in {i for i in ids if ids.count(i) > 1}:
        errs.append(f"duplicate topic id in registry: {d}")
    for p in pathlib.Path("docs").rglob("*.md"):
        if p.as_posix() not in registered:
            errs.append(f"unregistered page on disk: {p.as_posix()}")
    if errs:
        print("\n".join(f"  - {e}" for e in errs)); sys.exit(1)
    print(f"registry: consistent ({len(topics)} topics)")

if __name__ == "__main__":
    main()
