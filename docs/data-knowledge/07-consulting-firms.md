---
title: Consulting Firm AI Knowledge Platforms
doc_type: guide
domain: data-knowledge
status: current
canonical: true
topic_id: consulting-firms
maturity: practitioner
personas: [architect, knowledge-engineer, manager]
date_created: 2026-07-05
last_reviewed: 2026-07-10
covers_version: "as of 2026-07-10"
source_type: native-md
supersedes:
  - docs/knowledge-engineering/industry-practices/consulting-firms.md
tags: [knowledge-engineering, industry-practices]
sources: []
---

# Consulting Firm AI Knowledge Platforms

The major consultancies are unusually valuable case studies: their product *is* knowledge, they deployed firm-wide generative AI earlier than most enterprises, and — uniquely — they published their lessons. Collectively the Big Four and top strategy houses have invested **$10B+ in AI initiatives since 2023**. Research current as of July 2026.

**Scope**: This guide focuses on internal knowledge management platforms (Lilli, GENE, PairD, EYQ, KymChat). For the broader GenAI business strategy — delivery model transformation, outcome pricing, agentic platforms (Zora AI, Agent OS, KPMG Workbench), and SI firm comparisons — see [Consulting &amp; Services Firms: GenAI Strategy Landscape](./06-consulting-firms-genai-strategy.md).

---

## McKinsey — Lilli

**Lilli** is the most thoroughly documented internal knowledge platform in the industry.

### What it is

A firm-wide assistant over McKinsey's proprietary corpus: **40+ curated knowledge sources, 100,000+ documents**, interview transcripts, and sector playbooks. A query is embedded, matched against the internal index, and the **five to seven most relevant artifacts** are surfaced with **inline citations**, plus a summary. Lilli then cross-references McKinsey's **expert graph** (spanning 70 countries) to recommend the partners or specialists best placed for follow-up. Two modes: internal knowledge search, and external sources.

McKinsey is explicit that Lilli is *not* "a RAG instance" but an orchestration stack combining many technologies.

### Adoption and impact

Rolled out firm-wide in July 2023; by 2025, **72% of the firm was active** on the platform, with reported time savings of **up to 30%** in searching and synthesizing knowledge.

### Published lessons

1. **Data quality is the product.** "Generative AI tools are only as good as the data" — a clear data strategy with tagging, labeling, and curation is prerequisite, not optional.
2. **Parse your real formats.** Most of McKinsey's knowledge lives in PowerPoint; off-the-shelf parsers extracted only ~15% of a deck. They built their own tooling to reach 85%+ extraction of any document type. Unglamorous ingestion engineering dominated the effort.
3. **Balance building vs learning.** The team deliberately slowed feature-building to wait for user feedback — the product improved more from usage learning than from code.
4. **Diverse expertise from the start.** The MVP team was lean and technical; the scaled team added legal, adoption/change-management, communications, and subject-matter specialists, because a knowledge platform touches all of them.

### Evaluation practice

McKinsey used **blind scoring**: outputs from consultants with and without Lilli were rated on a predefined **five-point scale for accuracy, content richness, and distinctiveness** — a human-judged golden-set evaluation predating today's automated LLM-as-judge norms.

## BCG — GENE and Deckster

- **GENE** is BCG's proprietary internal chatbot, built on GPT-4o under its OpenAI partnership and fed with BCG's internal knowledge.
- **Deckster** targets the firm's highest-volume artifact: PowerPoint slide preparation, trained on BCG's slide corpus and templates.

BCG's split — a general knowledge assistant plus a workflow-specific tool — reflects a broader consulting pattern: general chat drives adoption, but workflow-embedded tools (slides, proposals) drive measurable time savings.

## Deloitte — PairD

Deloitte launched **PairD** in late 2023 as its internal AI helper for drafting emails, writing code, creating presentations, and producing meeting agendas — a productivity-first assistant rolled out across a workforce of hundreds of thousands, later complemented by domain-specific assistants across audit and advisory.

## EY — EY.ai / EYQ

EY committed **$1.4B** to its EY.ai platform (2023) and deployed **EYQ to 300,000+ professionals** — secure enterprise chat, domain assistants, **governed prompt tooling**, and sandboxed generative-AI experimentation across all service lines. EY has since published a case study on building an **enterprise-scale agentic AI operating system**, moving from chat toward governed agent orchestration.

## KPMG — KymChat and the agent pivot

KPMG built **KymChat** as its internal assistant, then standardized on the Microsoft AI stack (Azure AI Foundry) to let **employees build their own AI agents** across audit, tax, and advisory — betting on enterprise-wide agent development under a common governance platform rather than a single central assistant.

## Accenture — AI Refinery, SynOps, and workforce mandate

Accenture's distinctive move is workforce-scale enablement backed by policy: it trained **550,000 of ~780,000 employees** in generative AI (tools including **AI Refinery** and **SynOps**), and from 2025 **promotion applications must explain how the employee uses AI** in their job — governance through incentive design, not just tooling.

## Cross-firm patterns

| Pattern | Evidence |
| --- | --- |
| **Curated corpus over "index everything"** | Lilli's 40+ *curated* sources; quality gates on what enters the knowledge base |
| **Citations + expert routing** | Lilli surfaces sources inline and routes to human experts — grounding plus human oversight in one flow |
| **Ingestion is the hard part** | McKinsey's PowerPoint parsing (15% → 85%) |
| **Human-judged evaluation baselines** | McKinsey's blind 5-point scoring before automated evals existed |
| **Governed experimentation** | EYQ's governed prompt tooling and safe sandboxes |
| **From chat to governed agents** | EY agentic AI OS, KPMG employee-built agents on Azure AI Foundry |
| **Adoption as a managed program** | Lilli's 72% active use; Accenture tying AI use to promotion |

---

## Sources

- [Rewiring the way McKinsey works with Lilli (McKinsey)](https://www.mckinsey.com/capabilities/tech-and-ai/how-we-help-clients/rewiring-the-way-mckinsey-works-with-lilli)
- [What McKinsey learned while creating its generative AI platform (McKinsey)](https://www.mckinsey.com/capabilities/tech-and-ai/our-insights/what-mckinsey-learned-while-creating-its-generative-ai-platform)
- [Meet Lilli (McKinsey blog)](https://www.mckinsey.com/about-us/new-at-mckinsey-blog/meet-lilli-our-generative-ai-tool)
- [We spent nearly a year building a gen AI tool — 5 hard lessons (Fast Company)](https://www.fastcompany.com/91138609/we-spent-nearly-a-year-building-a-gen-ai-tool-these-are-the-5-hard-lessons-we-learned)
- [McKinsey rolls out Lilli to 7K employees (CIO Dive)](https://www.ciodive.com/news/McKinsey-generative-AI-Lilli-platform-internal-employees/691231/)
- [Inside the AI boom transforming McKinsey, BCG, and Deloitte (Business Insider via Neuron)](https://neuron.expert/news/inside-the-ai-boom-thats-transforming-how-consultants-work-at-mckinsey-bcg-and-deloitte/12587/en/)
- [How the top consulting firms are using AI (Plus AI)](https://plusai.com/blog/how-consulting-firms-use-ai)
- [Building an enterprise-scale agentic AI operating system (EY)](https://www.ey.com/en_gl/insights/ai/building-an-enterprise-scale-agentic-ai-operating-system)
- [KPMG leads the AI era with Microsoft-powered agents (Microsoft Customer Stories)](https://www.microsoft.com/en/customers/story/25357-kpmg-azure-ai-foundry)
- [Accenture trained 550,000 workers in AI — promotions now hinge on using it (Fortune)](https://fortune.com/2026/02/23/last-year-accenture-trained-550000-staff-use-ai-now-promotions-hinge-on-putting-that-into-practice/)
- [The Big Consulting AI Frameworks, Compared 2026 (Consulting Huber)](https://consulting-huber.com/ai-consulting-frameworks-compared.html)
