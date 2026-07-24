# Split Plan: agent-ux-patterns

**Source:** `../knowledge-docs/docs/agentic-ui/agent-ux-patterns.md` (8525 words)

## Split Strategy

3-way split required to maintain ≤2600 word cap per guide part (source: 8525 words, ~2840-2900 per part):
- **Part 1:** Copilot Pattern Taxonomy (Section 1: Patterns 1-12 complete) + Streaming UX Design (Section 2.1-2.7) — foundational patterns and streaming design
- **Part 2:** Reasoning Visualization (Section 3) + Confidence & Uncertainty (Section 4) + Human Approval UX (Section 5) + Long-running Tasks (Section 6) — visualization and control patterns  
- **Part 3:** Multi-agent Collaboration (Section 7) + Undo/Replay/Checkpoint (Section 8) + Audit UX (Section 9) + Error UX (Section 10) + Accessibility (Section 11) + Anti-patterns (Section 12) — advanced operations and accessibility

## Line Ranges

| Part | Start Line | End Line | Sections | Est. Words |
|------|-----------|----------|----------|-----------|
| Part 1 | 1 | 430 | Frontmatter + S1 (Patterns 1-12 all) + S2 (Streaming 2.1-2.7) | ~2750 |
| Part 2 | 431 | 820 | S3 (Reasoning) + S4 (Confidence) + S5 (Approval) + S6 (Long-running) | ~2600 |
| Part 3 | 821 | 1179 | S7 (Multi-agent) + S8 (Undo) + S9 (Audit) + S10 (Error) + S11 (A11y) + S12 (Anti-patterns) | ~2900 |

## Frontmatter Settings

**Part 1:**
- `topic_id: agent-ux-patterns`
- `supersedes: ["../knowledge-docs/docs/agentic-ui/agent-ux-patterns.md"]`
- Continuation link to Part 2

**Part 2:**
- `topic_id: agent-ux-patterns-part2`
- `supersedes: []`
- Back-link to Part 1, continuation link to Part 3

**Part 3:**
- `topic_id: agent-ux-patterns-part3`
- `supersedes: []`
- Back-link to Part 2

## ASCII Diagrams Converted to Mermaid

All diagrams restored with full information:
- Streaming indicator status → structured table
- Tool call visualization → structured list with tool names and status
- Reasoning panel → structured content with evidence citations
- Multiple hypothesis display → structured hypothesis list with percentages
- Approval dialog → structured approval flow
- Batch approval queue → approval items table
- Progress visualization → milestone table
- Agent handoff → agent topology table
- Audit view → audit event log table
