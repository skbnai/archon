# Split Plan: application-lifecycle

**Source:** docs/agentic-ui/application-lifecycle.md (8681 words)

**Split Strategy:** 3-way split at natural stage boundaries (lifecycle stages)

## Split Map

| Part | Target Path | Topic ID | Source Stages | Line Range | Word Count |
|------|------------|----------|-------------|-----------|-----------|
| 1 | docs/agentic-systems/agentic-ui/04-application-lifecycle.md | application-lifecycle | Lifecycle Overview + Stages 1-5 (Ideation through UX Design) | 14-512 | ~2850 |
| 2 | docs/agentic-systems/agentic-ui/parts/04-application-lifecycle-part2.md | application-lifecycle-part2 | Stages 6-11 (Context Engineering through Testing) | 513-997 | ~2880 |
| 3 | docs/agentic-systems/agentic-ui/parts/04-application-lifecycle-part3.md | application-lifecycle-part3 | Stages 12-17 (Deployment through Retirement) + Lifecycle Decision Matrix + ADR Template | 998-1338 | ~2951 |

## Split Rationale

The application-lifecycle document is organized as a sequential journey through 17 stages of the agentic application development lifecycle. The split preserves this logical flow:

**Part 1** covers the discovery and planning phases (Ideation through UX Design). These stages answer: "Is this worth doing?" and "What should it look like?"

**Part 2** covers the design and development phases (Context Engineering through Testing). These stages answer: "How do we build it?" and "Is it reliable?"

**Part 3** covers the operations and retirement phases (Deployment through Retirement), plus the decision matrix and architecture decision record template. These stages answer: "How do we run it?" and "How do we evolve it?"

Each part contains complete stage descriptions with templates, scorecards, and decision criteria.

## Supersedes

The three parts together completely supersede the original monolithic document at `docs/agentic-ui/application-lifecycle.md`.

## Verification

- Combined word count: ~2850 + ~2880 + ~2951 = ~8681 (100% word retention)
- All stage descriptions preserved completely
- All templates (scorecard, hypothesis canvas, ADR, runbook) included in appropriate parts
- All tables and decision matrices intact
- Code examples preserved (LLM-as-Judge setup, agent unit testing patterns)
- Navigation links connect parts with stage progression context
