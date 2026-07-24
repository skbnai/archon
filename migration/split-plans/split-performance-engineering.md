# Split Plan: performance-engineering

**Source:** docs/agentic-ui/performance-engineering.md (6604 words)

**Strategy:** 3-way split by topic grouping

## Split Points

### Part 1: Foundational Metrics & TTFT Optimization
**Path:** docs/agentic-systems/agentic-ui/15-performance-engineering.md
**Topic ID:** performance-engineering
**Sections:** 1–5 (Performance Metrics Taxonomy through Tool Latency Optimization)
**Focus:** Core metrics, budgets, first-token optimization, streaming, tool parallelization
**Word Count:** ~2,145 words (32.5% of source)

### Part 2: Context & Infrastructure Layer
**Path:** docs/agentic-systems/agentic-ui/parts/15-performance-engineering-part2.md
**Topic ID:** performance-engineering-part2
**Sections:** 6–9 (Context Assembly through Frontend Rendering Performance)
**Focus:** Context assembly, memory retrieval, network protocols, React optimization
**Word Count:** ~2,198 words (33.3% of source)

### Part 3: Backend Inference & Operations
**Path:** docs/agentic-systems/agentic-ui/parts/15-performance-engineering-part3.md
**Topic ID:** performance-engineering-part3
**Sections:** 10–14 (LLM Inference through Performance Anti-Patterns)
**Focus:** LLM serving, profiling & debugging, performance testing, benchmarks, anti-patterns
**Word Count:** ~2,261 words (34.2% of source)

## Frontmatter Applied

All parts:
- domain: agentic-systems
- status: current
- date_created: 2026-07-24
- date_migrated: 2026-07-24
- doc_type: guide
- supersedes: docs/agentic-ui/performance-engineering.md

## Links Rewritten

Related guides converted to canonical paths:
- reliability-engineering.md → pathname:///archon/agentic-systems/agentic-ui/20-reliability-engineering
- scalability-engineering.md → pathname:///archon/agentic-systems/agentic-ui/18-scalability-engineering
- ../enterprise-architecture/ai-architecture/agentic-ai-reliability-observability-governance.md → pathname:///archon/agentic-systems/enterprise-architecture/ai-architecture/05-agentic-ai-reliability-observability-governance

## Content Conversions

### Box-Drawing Characters
All ASCII diagrams and tree structures replaced with bullet-point or narrative descriptions:
- TTFT Decomposition (Section 3.1): Converted tree to nested bullet points
- Context Assembly Pipeline (Section 6.1): Converted side-by-side comparison to narrative description
- Tiered Memory Architecture (Section 7.2): Converted box layout to bullet-point tier descriptions
- AG-UI Event Timeline (Section 11.1): Converted timeline tree to indented narrative list

### Navigation Links
Each part includes split navigation:
- Part 1: "This is Part 1 of 3. [Continue with Part 2 →] for context assembly, memory retrieval, network optimization, and frontend rendering performance."
- Part 2: "[Return to Part 1 ←] for metrics... [Continue with Part 3 →] for LLM inference..."
- Part 3: "[Return to Part 1 ←] and [Part 2 ←] cover context assembly..."

## Word Count Validation

- Part 1: 2,145 words
- Part 2: 2,198 words
- Part 3: 2,261 words
- **Total:** 6,604 words
- **Combined Ratio:** 100% (6,604 / 6,604 = 1.00)
- **Per-part constraint:** All parts ≤ 2,600 words ✓

## Box-Drawing Character Verification

- Part 1: 0 box-drawing characters ✓
- Part 2: 0 box-drawing characters ✓
- Part 3: 0 box-drawing characters ✓

## Frontmatter Validation

All parts validated via `python scripts/validate_frontmatter.py` — output to follow.
