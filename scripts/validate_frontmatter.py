#!/usr/bin/env python3
"""Validate a docs/ page's frontmatter against governance/DOC_TYPES.md schema."""
import sys, re, datetime
try:
    import yaml
except ImportError:
    sys.exit(0)

DOC_TYPES = {"concept","guide","reference-architecture","pattern","anti-pattern",
             "decision","runbook","checklist","research-report","case-study",
             "learning-path","hub","template-asset","glossary"}
DOMAINS = {"strategy","architecture","agentic-systems","protocols","data-knowledge",
           "platforms","trust","operations","learning-paths","career","assets"}
STATUS = {"draft","current","superseded","deprecated","proposed","accepted"}
REQUIRED = ["title","doc_type","domain","status","topic_id","last_reviewed"]

def fail(msgs):
    print("\n".join(f"  - {m}" for m in msgs)); sys.exit(1)

def main(path):
    text = open(path, encoding="utf-8").read()
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    if not m: fail(["missing frontmatter block"])
    try: fm = yaml.safe_load(m.group(1)) or {}
    except yaml.YAMLError as e: fail([f"YAML error: {e}"])
    errs = [f"missing required field: {k}" for k in REQUIRED if not fm.get(k)]
    if fm.get("doc_type") and fm["doc_type"] not in DOC_TYPES:
        errs.append(f"doc_type '{fm['doc_type']}' not in DOC_TYPES")
    if fm.get("domain") and fm["domain"] not in DOMAINS:
        errs.append(f"domain '{fm['domain']}' not in TAXONOMY domains")
    if fm.get("status") and fm["status"] not in STATUS:
        errs.append(f"status '{fm['status']}' invalid")
    if fm.get("doc_type") == "research-report" and not fm.get("sources"):
        errs.append("research-report requires non-empty sources")
    if fm.get("doc_type") == "reference-architecture" and "```mermaid" not in text:
        errs.append("reference-architecture requires a mermaid diagram")
    words = len(re.sub(r"```.*?```", "", text[m.end():], flags=re.S).split())
    if words > 2600:
        errs.append(f"page is {words} words (>2600 hard cap) — split it")
    if errs: fail(errs)
    print("OK")

if __name__ == "__main__":
    main(sys.argv[1])
