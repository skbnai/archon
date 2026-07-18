// sidebars.js — hand-curated, mirrors governance/TAXONOMY.md exactly.
// See governance/SIDEBAR_GUIDE.md before editing. Every category anchors to
// its domain hub; items are in deliberate reading order, not alphabetical.
// Populate each `items` array during stage-04/06 as pages are registered —
// this file starts structurally complete but content-empty on purpose.

/** @type {import('@docusaurus/plugin-content-docs').SidebarsConfig} */
const sidebars = {
  wikiSidebar: [
    {
      type: "category",
      label: "Strategy & Operating Model",
      link: { type: "doc", id: "strategy/index" },
      collapsible: true,
      items: [
        // "strategy/01-ai-strategy-and-vision",
        // "strategy/02-business-architecture-capability-maps",
        // ...
      ],
    },
    {
      type: "category",
      label: "Architecture",
      link: { type: "doc", id: "architecture/index" },
      collapsible: true,
      items: [
        // "architecture/01-foundations-agentic-loop",
        // "architecture/02-landing-zones",
        // { type: "category", label: "ADR Library",
        //   link: { type: "doc", id: "architecture/adr/index" },
        //   items: ["architecture/adr/adr-001-...", "architecture/adr/adr-002-..."] },
      ],
    },
    {
      type: "category",
      label: "Agentic Systems",
      link: { type: "doc", id: "agentic-systems/index" },
      collapsible: true,
      items: [],
    },
    {
      type: "category",
      label: "Protocols & Interoperability",
      link: { type: "doc", id: "protocols/index" },
      collapsible: true,
      items: [],
    },
    {
      type: "category",
      label: "Data & Knowledge",
      link: { type: "doc", id: "data-knowledge/index" },
      collapsible: true,
      items: [],
    },
    {
      type: "category",
      label: "Platforms & Infrastructure",
      link: { type: "doc", id: "platforms/index" },
      collapsible: true,
      items: [],
    },
    {
      type: "category",
      label: "Trust: Security, Governance & RAI",
      link: { type: "doc", id: "trust/index" },
      collapsible: true,
      items: [],
    },
    {
      type: "category",
      label: "Operations & Economics",
      link: { type: "doc", id: "operations/index" },
      collapsible: true,
      items: [],
    },
    {
      type: "category",
      label: "Learning Paths",
      link: { type: "doc", id: "learning-paths/index" },
      collapsible: true,
      items: [
        // flat list per governance/SIDEBAR_GUIDE.md — no sub-categories
      ],
    },
    {
      type: "category",
      label: "Career & Skills",
      link: { type: "doc", id: "career/index" },
      collapsible: true,
      items: [],
    },
    {
      type: "category",
      label: "Asset Library",
      link: { type: "doc", id: "assets/index" },
      collapsible: true,
      items: [
        // sub-categories by engagement phase, not file type:
        // { type: "category", label: "Discovery", items: [] },
        // { type: "category", label: "Design", items: [] },
        // { type: "category", label: "Delivery", items: [] },
        // { type: "category", label: "Operate", items: [] },
      ],
    },
  ],
};

module.exports = sidebars;
