# Docusaurus Setup Reference

Prerequisite files already provided in this scaffold — do not recreate them,
extend them:

| File | Purpose |
|---|---|
| `docusaurus.config.js` | Site identity, navbar, footer, dark-mode default, Mermaid theme plugin, broken-link build failures |
| `sidebars.js` | Curated navigation — one category per `governance/TAXONOMY.md` domain; see `governance/SIDEBAR_GUIDE.md` |
| `src/css/custom.css` | Theme variables + the `.stat-row`/`.stat` and `.archon-card-grid`/`.archon-card` components referenced by the `page-styling` skill |
| `src/pages/index.js` (create in stage-06) | Homepage: persona entry tiles + domain tiles + flagship-assets row, per stage-06 prompt |

## First-time install

```bash
npx create-docusaurus@latest . classic --typescript=false
npm install @docusaurus/theme-mermaid prism-react-renderer
```
Then overlay this scaffold's `docusaurus.config.js`, `sidebars.js`, and
`src/css/custom.css` on top of the generated project (they replace the
defaults — do not merge conflicting keys, this scaffold's versions are
authoritative for a governed wiki).

## Required assets (add before stage-06 homepage work)

`static/img/`: `favicon.ico`, `logo.svg`, `archon-social-card.png`. Placeholder
these early so `docusaurus build` doesn't fail on missing references — swap in
real artwork later without touching config.

## Verifying the setup

```bash
npm run build     # onBrokenLinks: "throw" means this is also a structural check
npm run serve     # sanity-check locally before every deploy
```

The `deploy.yml` workflow runs `npm run build` on every push to `main` — a
broken sidebar reference or a dangling link fails CI before it fails a reader.
