import React, { useEffect, useState } from "react";
import Layout from "@theme/Layout";
import Link from "@docusaurus/Link";
import manifest from "@site/src/data/progress-manifest.json";
import {
  getStreak,
  getVisitedCount,
  getQuizzes,
  resetProgress,
} from "@site/src/lib/progressStore";
import { PROGRESS_UPDATED_EVENT } from "@site/src/lib/progressEvents";
import styles from "./progress.module.css";

export default function ProgressPage() {
  const [streak, setStreak] = useState(null);
  const [visited, setVisited] = useState({});
  const [quizzes, setQuizzes] = useState({});

  function refresh() {
    setStreak(getStreak());
    setQuizzes(getQuizzes());
    const v = {};
    Object.keys(manifest).forEach((domain) => {
      v[domain] = getVisitedCount(domain);
    });
    setVisited(v);
  }

  useEffect(() => {
    refresh();
    window.addEventListener(PROGRESS_UPDATED_EVENT, refresh);
    return () => window.removeEventListener(PROGRESS_UPDATED_EVENT, refresh);
  }, []);

  const quizEntries = Object.entries(quizzes);

  return (
    <Layout
      title="My Progress"
      description="Your reading streak, section progress, and quiz scores."
    >
      <main className={styles.main}>
        <h1>My progress</h1>
        <p>
          Tracked entirely in your browser&apos;s local storage — nothing is
          sent anywhere, and nothing is visible to anyone else. Clearing your
          browser data clears it too.
        </p>

        <div className="stat-row">
          <div className="stat">
            <span className="stat-value">{streak ? streak.current : "–"}</span>
            <span className="stat-label">Day streak</span>
          </div>
          <div className="stat">
            <span className="stat-value">{streak ? streak.longest : "–"}</span>
            <span className="stat-label">Longest streak</span>
          </div>
          <div className="stat">
            <span className="stat-value">{quizEntries.length}</span>
            <span className="stat-label">Quizzes attempted</span>
          </div>
        </div>

        <h2>Sections</h2>
        <ul className={styles.list}>
          {Object.entries(manifest).map(([domain, section]) => {
            const count = Math.min(visited[domain] || 0, section.totalPages);
            const pct = section.totalPages
              ? Math.round((count / section.totalPages) * 100)
              : 0;
            return (
              <li key={domain} className={styles.row}>
                <Link to={`/${domain}/`}>{section.label}</Link>
                <div className={styles.track}>
                  <div className={styles.fill} style={{ width: `${pct}%` }} />
                </div>
                <span className={styles.fraction}>
                  {count} / {section.totalPages}
                </span>
              </li>
            );
          })}
        </ul>

        {quizEntries.length > 0 && (
          <>
            <h2>Quiz scores</h2>
            <ul className={styles.list}>
              {quizEntries.map(([id, q]) => (
                <li key={id} className={styles.row}>
                  <span>{id}</span>
                  <span className={styles.fraction}>
                    best {q.best} / {q.total} · {q.attempts} attempt
                    {q.attempts === 1 ? "" : "s"}
                  </span>
                </li>
              ))}
            </ul>
          </>
        )}

        <button
          type="button"
          className="button button--secondary button--sm"
          onClick={() => {
            if (window.confirm("Reset your streak, page visits, and quiz scores?")) {
              resetProgress();
              refresh();
            }
          }}
        >
          Reset my progress
        </button>
      </main>
    </Layout>
  );
}
