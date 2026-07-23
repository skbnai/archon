// src/components/SectionProgress/index.js
//
// Embed on a domain/track hub page:
//   import SectionProgress from '@site/src/components/SectionProgress';
//   <SectionProgress domain="agentic-systems" />
//
// `domain` must match the docs/ folder name — it's the key into the
// build-time manifest (scripts/build_progress_manifest.js). The visited
// count comes from localStorage. See
// .claude/skills/gamification/SKILL.md.
import React, { useEffect, useState } from "react";
import manifest from "@site/src/data/progress-manifest.json";
import { getVisitedCount } from "@site/src/lib/progressStore";
import { PROGRESS_UPDATED_EVENT } from "@site/src/lib/progressEvents";
import styles from "./styles.module.css";

export default function SectionProgress({ domain }) {
  const section = manifest[domain];
  const [visited, setVisited] = useState(0);

  useEffect(() => {
    const refresh = () => setVisited(getVisitedCount(domain));
    refresh();
    window.addEventListener(PROGRESS_UPDATED_EVENT, refresh);
    return () => window.removeEventListener(PROGRESS_UPDATED_EVENT, refresh);
  }, [domain]);

  if (!section || !section.totalPages) return null;

  const pct = Math.min(100, Math.round((visited / section.totalPages) * 100));

  return (
    <div className={styles.wrap}>
      <div className={styles.label}>
        <span>Your progress in {section.label}</span>
        <span className={styles.fraction}>
          {Math.min(visited, section.totalPages)} / {section.totalPages} pages
        </span>
      </div>
      <div
        className={styles.track}
        role="progressbar"
        aria-valuenow={pct}
        aria-valuemin={0}
        aria-valuemax={100}
        aria-label={`${section.label} reading progress`}
      >
        <div className={styles.fill} style={{ width: `${pct}%` }} />
      </div>
    </div>
  );
}
