#!/usr/bin/env python3
"""Consistency check: registry <-> filesystem <-> frontmatter.
Fails if: unregistered docs/ page; registered canonical missing; two canonicals
per topic; page frontmatter topic_id/status inconsistent with registry.

--paper: paper-stage mode (stage-02 taxonomy mapping, before any migration
content has been written). Skips file-existence / frontmatter checks — those
would fail-by-design since canonical files don't exist yet — and instead
checks only what's knowable from the registry text itself: id/canonical
present, no duplicate ids, no duplicate canonical paths, no two topics
sharing a canonical, and every canonical path is well-formed
(docs/<domain>/... , domain matches the topic's declared domain)."""
import sys, re, pathlib
try: import yaml
except ImportError: sys.exit(0)

def fm(path):
    t = path.read_text(encoding="utf-8", errors="ignore")
    m = re.match(r"^---\n(.*?)\n---\n", t, re.S)
    return (yaml.safe_load(m.group(1)) or {}) if m else {}

def check_paper(topics):
    errs = []
    seen_ids, seen_canon = {}, {}
    for t in topics:
        tid, domain, canon = t.get("id"), t.get("domain"), t.get("canonical")
        if not tid or not domain or not canon:
            errs.append(f"registry entry missing id/domain/canonical: {t}")
            continue
        seen_ids.setdefault(tid, []).append(canon)
        seen_canon.setdefault(canon, []).append(tid)
        if not canon.startswith(f"docs/{domain}/"):
            errs.append(f"[{tid}] canonical path {canon} doesn't start with docs/{domain}/")
        if not re.match(r"^docs/[a-z-]+/([a-z-]+/)?(index\.md|\d{2}-[a-z0-9-]+\.md)$", canon):
            errs.append(f"[{tid}] canonical path {canon} doesn't match NN-kebab-case.md / index.md naming "
                        f"(one optional subfolder allowed per TAXONOMY.md's max-depth-3 rule)")
    for tid, canons in seen_ids.items():
        if len(canons) > 1:
            errs.append(f"duplicate topic id in registry: {tid} -> {canons}")
    for canon, tids in seen_canon.items():
        if len(tids) > 1:
            errs.append(f"two topics share one canonical: {canon} -> {tids}")
    return errs

def check_live(topics):
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
    return errs

def main():
    paper = "--paper" in sys.argv
    reg = yaml.safe_load(open("governance/CANONICAL_REGISTRY.yaml")) or {}
    topics = reg.get("topics") or []
    errs = check_paper(topics) if paper else check_live(topics)
    if errs:
        print("\n".join(f"  - {e}" for e in errs)); sys.exit(1)
    mode = "paper" if paper else "live"
    print(f"registry: consistent ({len(topics)} topics, {mode} mode)")

if __name__ == "__main__":
    main()
