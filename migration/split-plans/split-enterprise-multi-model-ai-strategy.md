# Split Plan: enterprise-multi-model-ai-strategy

- old_path: `docs/enterprise-architecture/ai-architecture/enterprise-multi-model-ai-strategy.md`
- domain: architecture
- doc_type: reference-architecture (6,000-word ceiling per doc-standards)
- wave: 2

Source is 12,514 words, split into 3 parts by the source's own `Part I`–`Part VIII`
headings. Part 1 is already migrated (`docs/architecture/54-enterprise-multi-model-ai-strategy.md`,
covers source lines 1–462: Part I "The Case for Multi-Model" + Part II "The 2026
Model Landscape", sections 1–5). This plan covers the two remaining parts.

## Parts (3, part1 already landed)

- **part1** (existing, do not re-migrate): topic_id=`enterprise-multi-model-ai-strategy`
  target=`docs/architecture/54-enterprise-multi-model-ai-strategy.md`
  Source lines 1–462 (front matter, TOC, Part I, Part II — sections 1–5).

- **part2**: topic_id=`enterprise-multi-model-ai-strategy-part2` target=`docs/architecture/parts/18-enterprise-multi-model-ai-strategy-part2.md`
  title: Enterprise Multi-Model AI Strategy — Technical Comparison, Decision Frameworks & Architecture (Part 2 of 3)
  Source lines 463–1133: Part III "Technical Comparison" (§6 Claude vs GPT vs
  Gemini vs Open Source), Part IV "Decision Frameworks" (§7 Enterprise Model
  Decision Tree, §8 Dynamic Model Selection), Part V "Architecture" (§9 Model
  Routing Architecture, §10 Multi-Model Agent Architecture, §11 Context Window
  Strategy, §12 Enterprise Reference Architectures). ~4,027 words.

- **part3**: topic_id=`enterprise-multi-model-ai-strategy-part3` target=`docs/architecture/parts/19-enterprise-multi-model-ai-strategy-part3.md`
  title: Enterprise Multi-Model AI Strategy — Operations, Governance & Future Trends (Part 3 of 3)
  Source lines 1134–end: Part VI "Operations" (§13 Model Evaluation Framework,
  §14 Cost Optimisation, §15 Enterprise Model Registry), Part VII "Governance
  and Security" (§16 Enterprise Governance, §17 Security, §18 Vendor Lock-in
  Prevention, §19 Prompt Portability), Part VIII "Looking Ahead" (§20 Future
  Trends 2026-2030), plus trailing Best Practices & Anti-Patterns, Migration
  Roadmap, Governance Checklist, Glossary, Further Reading. ~5,004 words.

Each part needs its own "Part N of 3" note at the top linking to the other two
parts (part1's existing page already has a `## Related` / series nav — extend
it to reference part2/part3 once their paths exist), and its own `supersedes`
scoped to this split (part1 already has `supersedes: [docs/enterprise-architecture/ai-architecture/enterprise-multi-model-ai-strategy.md]` — part2/part3 do NOT repeat that `supersedes`, only part1 owns it, per the one-owner-per-old-path convention used in the wave-1 split plans).
