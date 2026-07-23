#!/usr/bin/env node
/**
 * Builds src/data/progress-manifest.json from each domain/track's
 * docs/<domain>/_index.json (produced by the graphify skill's
 * build_section_indexes.py). Runs automatically before `start`/`build`
 * (see the `pre*` scripts in package.json) so the SectionProgress
 * denominators never drift from the actual page count.
 *
 * Owned by the gamification-curator agent — see
 * .claude/skills/gamification/SKILL.md. Never hand-edit the output file.
 */
const fs = require("fs");
const path = require("path");

const DOCS_DIR = path.join(__dirname, "..", "docs");
const OUT_FILE = path.join(__dirname, "..", "src", "data", "progress-manifest.json");

// Mirrors the domain labels in docusaurus.config.js / sidebars.js — keep in
// sync if a domain is renamed (see governance/TAXONOMY.md). A domain missing
// here still works, just falls back to its raw folder name.
const DOMAIN_LABELS = {
  strategy: "Strategy & Operating Model",
  architecture: "Architecture",
  "agentic-systems": "Agentic Systems",
  protocols: "Protocols & Interoperability",
  "data-knowledge": "Data & Knowledge",
  platforms: "Platforms & Infrastructure",
  trust: "Trust: Security, Governance & RAI",
  operations: "Operations & Economics",
  "learning-paths": "Learning Paths",
  career: "Career & Skills",
  assets: "Asset Library",
};

function build() {
  const manifest = {};
  const domains = fs
    .readdirSync(DOCS_DIR)
    .filter((entry) => fs.statSync(path.join(DOCS_DIR, entry)).isDirectory());

  for (const domain of domains.sort()) {
    const indexPath = path.join(DOCS_DIR, domain, "_index.json");
    if (!fs.existsSync(indexPath)) continue;

    let data;
    try {
      data = JSON.parse(fs.readFileSync(indexPath, "utf8"));
    } catch (err) {
      console.warn(`progress-manifest: skipping ${domain} (${indexPath} is not valid JSON)`);
      continue;
    }

    const pages = Array.isArray(data.pages) ? data.pages : [];
    manifest[domain] = {
      label: DOMAIN_LABELS[domain] || domain,
      totalPages: typeof data.page_count === "number" ? data.page_count : pages.length,
      pages: pages.map((p) => ({ id: p.id, title: p.title })),
    };

    if (!DOMAIN_LABELS[domain]) {
      console.warn(`progress-manifest: no DOMAIN_LABELS entry for "${domain}" — using folder name`);
    }
  }

  fs.mkdirSync(path.dirname(OUT_FILE), { recursive: true });
  fs.writeFileSync(OUT_FILE, JSON.stringify(manifest, null, 2) + "\n");

  const totalPages = Object.values(manifest).reduce((sum, d) => sum + d.totalPages, 0);
  console.log(
    `progress-manifest.json: ${Object.keys(manifest).length} sections, ${totalPages} pages total.`
  );
}

build();
