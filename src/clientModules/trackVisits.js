// src/clientModules/trackVisits.js
//
// Docusaurus client-module lifecycle: onRouteDidUpdate fires on every route
// change (including first load), client-side only — no React Router context
// needed, which matters because src/theme/Root.js renders outside the
// Router. Registered in docusaurus.config.js under `clientModules`. See
// .claude/skills/gamification/SKILL.md.
import ExecutionEnvironment from "@docusaurus/ExecutionEnvironment";
import siteConfig from "@generated/docusaurus.config";
import { recordVisit } from "../lib/progressStore";

function pageIdFromPathname(pathname) {
  const base = siteConfig.baseUrl || "/";
  const rel = pathname.startsWith(base) ? pathname.slice(base.length) : pathname;
  const trimmed = rel.replace(/^\/+|\/+$/g, "");
  return trimmed || "home";
}

export function onRouteDidUpdate({ location }) {
  if (!ExecutionEnvironment.canUseDOM) return;
  recordVisit(pageIdFromPathname(location.pathname));
}
