// src/lib/progressEvents.js
//
// Shared DOM CustomEvent name dispatched whenever progressStore.js changes
// state. Components (StreakWidget, SectionProgress, the /progress page)
// listen for this instead of polling, so they update live within a single
// SPA session without needing React Router/context.
export const PROGRESS_UPDATED_EVENT = "archon:progress-updated";
