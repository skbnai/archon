#!/usr/bin/env python3
"""List pages past freshness SLA: 180d for current pages, 90d if covers_version set
or doc_type==research-report. Output: days_overdue | path | doc_type | covers_version"""
import re, pathlib, datetime, sys
try: import yaml
except ImportError: sys.exit(0)
today = datetime.date.today()
rows = []
for p in pathlib.Path("docs").rglob("*.md"):
    t = p.read_text(encoding="utf-8", errors="ignore")
    m = re.match(r"^---\n(.*?)\n---\n", t, re.S)
    if not m: continue
    fm = yaml.safe_load(m.group(1)) or {}
    if fm.get("status") != "current": continue
    lr = fm.get("last_reviewed")
    try: lr = datetime.date.fromisoformat(str(lr))
    except Exception: continue
    sla = 90 if (fm.get("covers_version") or fm.get("doc_type") == "research-report") else 180
    over = (today - lr).days - sla
    if over > 0:
        rows.append((over, str(p), fm.get("doc_type",""), str(fm.get("covers_version",""))))
for r in sorted(rows, reverse=True):
    print(f"{r[0]:5d}d overdue | {r[1]} | {r[2]} | {r[3]}")
print(f"\n{len(rows)} stale page(s)")
sys.exit(1 if rows else 0)
