import React from "react";
import Link from "@docusaurus/Link";
import styles from "./styles.module.css";

export default function StreakWidget({ streak }) {
  const label = `Reading streak: ${streak.current} day${
    streak.current === 1 ? "" : "s"
  }. View your progress.`;

  return (
    <Link to="/progress" className={styles.widget} aria-label={label} title={label}>
      <span className={styles.flame} aria-hidden="true">
        🔥
      </span>
      <span className={styles.count}>{streak.current}</span>
    </Link>
  );
}
