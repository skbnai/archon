# Split Plan: principal-enterprise-ai-guide-educative

- old_path: `docs/enterprise-architecture/specialization/Principal_Enterprise_AI_Guide_Educative.md`
- domain: architecture
- doc_type: learning-path (kept as-is; this is a persona-journey guide, not a
  technical blueprint, so it does not get the reference-architecture 6,600
  exception — but at 6,682 words it exceeds even that higher cap, so split
  regardless of type)
- wave: 2

Source is 6,659 words. Split in 2 by the source's own H2 sections.

## Parts (2)

- **part1**: topic_id=`principal-enterprise-ai-guide-educative` target=`docs/architecture/86-principal-enterprise-ai-guide-educative.md`
  Source lines 12-512: title/Scenario & Strategy Mastery framing, "Role,
  Mindset & Competency Map", "Enterprise LLM Architecture Patterns"
  (includes a conceptual AI Gateway request-context code example), "RAG,
  Knowledge Systems & Context Engineering", "Agentic AI System Design".
  ~3,727 words.

- **part2**: topic_id=`principal-enterprise-ai-guide-educative-part2` target=`docs/architecture/parts/36-principal-enterprise-ai-guide-educative-part2.md`
  title: Principal & Enterprise AI Architect (Part 2 of 2): Governance, Strategy & Decision Frameworks
  Source lines 513-end: "AI Governance, Risk & Responsible AI", "Strategy,
  Leadership & Executive Influence", "Principal AI Architect — Decision
  Frameworks & Cheat Sheet". ~2,932 words.

part1 owns `supersedes: [docs/enterprise-architecture/specialization/Principal_Enterprise_AI_Guide_Educative.md]`; part2 does not repeat it. Each part gets a "Part N of 2" note cross-linking the other. The source title has a leftover `<mark>` HTML tag artifact (`# <mark>Principal &</mark> Enterprise AI Architect`) — strip the `<mark>` tags during cleanup, keep the plain text title.
