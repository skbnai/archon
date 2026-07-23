// src/theme/Root.js
//
// Swizzled Root: wraps the whole app to mount the floating streak widget.
// Root renders outside the Router, so it does NOT use useLocation — page
// visits are recorded by the src/clientModules/trackVisits.js lifecycle
// instead, and this component just listens for the resulting
// PROGRESS_UPDATED_EVENT. See .claude/skills/gamification/SKILL.md.
import React, { useEffect, useState } from "react";
import { getStreak } from "../lib/progressStore";
import { PROGRESS_UPDATED_EVENT } from "../lib/progressEvents";
import StreakWidget from "../components/StreakWidget";

function StreakTracker() {
  const [streak, setStreak] = useState(null);

  useEffect(() => {
    const refresh = () => setStreak(getStreak());
    refresh();
    window.addEventListener(PROGRESS_UPDATED_EVENT, refresh);
    return () => window.removeEventListener(PROGRESS_UPDATED_EVENT, refresh);
  }, []);

  if (!streak || streak.current === 0) return null;
  return <StreakWidget streak={streak} />;
}

export default function Root({ children }) {
  return (
    <>
      {children}
      <StreakTracker />
    </>
  );
}
