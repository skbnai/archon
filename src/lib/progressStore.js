// src/lib/progressStore.js
//
// Lightweight localStorage-backed store for reading streaks, per-page visit
// tracking, and quiz scores. Everything lives in the reader's browser —
// there is no backend, and none should be added (single JSON blob, single
// reader). See .claude/skills/gamification/SKILL.md before changing this.

import { PROGRESS_UPDATED_EVENT } from "./progressEvents";

const STORAGE_KEY = "archon:progress:v1";

const EMPTY_STATE = {
  visitedPages: {}, // { [pageId]: isoDateFirstVisited }
  streak: { current: 0, longest: 0, lastVisitDate: null },
  quizzes: {}, // { [quizId]: { best, total, attempts, lastAttempt } }
};

function emptyState() {
  return JSON.parse(JSON.stringify(EMPTY_STATE));
}

function isBrowser() {
  return typeof window !== "undefined" && !!window.localStorage;
}

function load() {
  if (!isBrowser()) return emptyState();
  try {
    const raw = window.localStorage.getItem(STORAGE_KEY);
    if (!raw) return emptyState();
    const parsed = JSON.parse(raw);
    return {
      ...emptyState(),
      ...parsed,
      streak: { ...emptyState().streak, ...(parsed.streak || {}) },
    };
  } catch {
    return emptyState();
  }
}

function save(state) {
  if (!isBrowser()) return;
  try {
    window.localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
    window.dispatchEvent(new Event(PROGRESS_UPDATED_EVENT));
  } catch {
    // Storage full/disabled (private browsing, quota) — gamification is
    // non-critical, fail silently rather than break the page.
  }
}

function todayISO() {
  return new Date().toISOString().slice(0, 10);
}

function daysBetween(a, b) {
  return Math.round((new Date(b) - new Date(a)) / 86400000);
}

/**
 * Record a visit to `pageId` (e.g. "agentic-systems" or
 * "agentic-systems/01-topologies") and roll the daily streak forward.
 * Call once per route change — src/theme/Root.js already does this.
 */
export function recordVisit(pageId) {
  const state = load();
  const today = todayISO();

  if (pageId && !state.visitedPages[pageId]) {
    state.visitedPages[pageId] = today;
  }

  const last = state.streak.lastVisitDate;
  if (last !== today) {
    if (last && daysBetween(last, today) === 1) {
      state.streak.current += 1;
    } else {
      state.streak.current = 1;
    }
    state.streak.lastVisitDate = today;
    state.streak.longest = Math.max(state.streak.longest, state.streak.current);
  }

  save(state);
  return state;
}

export function getStreak() {
  return load().streak;
}

/** Count visited pages whose id is `domain` or starts with `domain/`. */
export function getVisitedCount(domain) {
  const state = load();
  return Object.keys(state.visitedPages).filter(
    (id) => id === domain || id.startsWith(`${domain}/`)
  ).length;
}

export function getVisitedPages() {
  return load().visitedPages;
}

/** Record a quiz attempt; keeps the best score across attempts. */
export function recordQuizAttempt(quizId, score, total) {
  const state = load();
  const prev = state.quizzes[quizId] || { best: 0, total, attempts: 0, lastAttempt: null };
  state.quizzes[quizId] = {
    best: Math.max(prev.best, score),
    total,
    attempts: prev.attempts + 1,
    lastAttempt: todayISO(),
  };
  save(state);
  return state.quizzes[quizId];
}

export function getQuizzes() {
  return load().quizzes;
}

export function resetProgress() {
  if (!isBrowser()) return;
  window.localStorage.removeItem(STORAGE_KEY);
  window.dispatchEvent(new Event(PROGRESS_UPDATED_EVENT));
}
