// docusaurus.config.js — Archon: Enterprise AI Architecture Wiki
// Deploy target: https://skbnai.github.io/archon (GitHub Pages via .github/workflows/deploy.yml)
// Update organizationName/projectName/url below if the repo is renamed/forked.

const config = {
  title: "Archon",
  tagline: "The enterprise AI architecture knowledge base",
  favicon: "img/favicon.ico",

  url: "https://skbnai.github.io",
  baseUrl: "/archon/",
  organizationName: "skbnai",
  projectName: "archon",
  trailingSlash: false,

  onBrokenLinks: "throw",       // professional-grade: broken links fail the build, not just warn

  i18n: { defaultLocale: "en", locales: ["en"] },

  presets: [
    [
      "classic",
      /** @type {import('@docusaurus/preset-classic').Options} */
      ({
        docs: {
          routeBasePath: "/",         // docs ARE the site — no separate /docs prefix
          sidebarPath: "./sidebars.js",
          editUrl: "https://github.com/skbnai/archon/edit/main/",
          showLastUpdateTime: true,   // surfaces last_reviewed-adjacent signal to readers
        },
        blog: false,                  // this is a wiki, not a blog
        theme: { customCss: "./src/css/custom.css" },
      }),
    ],
  ],

  themeConfig:
    /** @type {import('@docusaurus/preset-classic').ThemeConfig} */
    ({
      image: "img/archon-social-card.png",
      navbar: {
        title: "Archon",
        logo: { alt: "Archon logo", src: "img/logo.svg" },
        items: [
          { to: "/learning-paths/", label: "Learning Paths", position: "left" },
          { to: "/architecture/", label: "Architecture", position: "left" },
          { to: "/trust/", label: "Trust & Security", position: "left" },
          { to: "/assets/", label: "Asset Library", position: "left" },
          {
            href: "https://github.com/skbnai/archon",
            label: "GitHub",
            position: "right",
          },
        ],
      },
      footer: {
        style: "dark",
        links: [
          {
            title: "Domains",
            items: [
              { label: "Strategy & Operating Model", to: "/strategy/" },
              { label: "Architecture", to: "/architecture/" },
              { label: "Agentic Systems", to: "/agentic-systems/" },
              { label: "Trust: Security & Governance", to: "/trust/" },
            ],
          },
          {
            title: "For",
            items: [
              { label: "Learning Paths", to: "/learning-paths/" },
              { label: "Career & Skills", to: "/career/" },
              { label: "Asset Library", to: "/assets/" },
            ],
          },
          {
            title: "Project",
            items: [
              { label: "GitHub", href: "https://github.com/skbnai/archon" },
              { label: "Governance", to: "/architecture/wiki-governance" },
            ],
          },
        ],
        copyright: `Archon — a living, self-grounding enterprise AI knowledge base.`,
      },
      prism: {
        theme: require("prism-react-renderer").themes.github,
        darkTheme: require("prism-react-renderer").themes.dracula,
        additionalLanguages: ["bash", "python", "yaml", "hcl", "json"],
      },
      colorMode: { defaultMode: "dark", respectPrefersColorScheme: true },
      tableOfContents: { minHeadingLevel: 2, maxHeadingLevel: 3 },
    }),

  markdown: {
    mermaid: true,               // required for diagram-standards skill output
    hooks: { onBrokenMarkdownLinks: "throw" },
  },
  themes: ["@docusaurus/theme-mermaid"],
};

module.exports = config;
