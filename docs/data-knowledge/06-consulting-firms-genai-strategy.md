---
title: Consulting & Services Firms - GenAI Strategy Landscape
doc_type: reference-architecture
domain: data-knowledge
status: current
canonical: true
topic_id: consulting-firms-genai-strategy
maturity: practitioner
personas: [architect, strategist, executive]
date_created: 2026-07-13
last_reviewed: 2026-07-13
covers_version: "as of July 2026"
source_type: native-md
supersedes:
  - docs/knowledge-engineering/industry-practices/consulting-firms-genai-strategy.md
tags: [consulting, genai, strategy, SIs, big-four, MBB, industry-landscape]
sources: []
---

# Consulting & Services Firms: GenAI Strategy Landscape

**Method note:** Claims below synthesize firm publications, earnings disclosures, partnership announcements, and market reporting through July 2026. Alliance details and platform names change quarterly — re-verify before client use. Revenue splits are directional. Related reading: [Consulting Firm AI Knowledge Platforms](./07-consulting-firms.md) covers internal knowledge management systems (Lilli, GENE, PairD, EYQ, KymChat) in depth.

---

## 1. The Structural Shock

GenAI attacks the consulting pyramid at its base: research, drafting, analysis, code, and testing — the junior-hours engine that accounts for 40–60% of delivery cost at most firms — are precisely what frontier models automate. Simultaneously, AI transformation demand is the largest bookings driver since the cloud migration wave of the early 2010s. Every major firm therefore runs the same four-part response:

| Response | What it means |
|---|---|
| **Asset-ization** | Platforms and accelerators sold with or instead of hours |
| **Outcome / consumption pricing** | Moving away from pure time-and-materials |
| **Workforce reshaping** | Flatter pyramids, AI-fluency mandates, targeted headcount reductions |
| **Ecosystem embedding** | Co-sell with hyperscalers and model labs; forward-deployed-engineering analogues |

Differentiation increasingly comes from: proprietary delivery IP, model-lab intimacy, industry-process depth, and willingness to cannibalize one's own hours.

---

## 2. Strategy Firms (MBB)

### McKinsey (QuantumBlack)

**GenAI strategy**: McKinsey frames its response around breaking the "gen AI paradox" — nearly 80% of companies are using GenAI yet the same proportion report no significant bottom-line impact, because horizontal copilots have scaled while vertical, function-specific transformations remain stuck in pilot. The solution McKinsey sells is the move from copilots to **agentic AI**: systems with the ability to plan, act, remember, and learn autonomously.

**Doctrine**: The "Rewired" enterprise-transformation methodology, published as a book and client offering, describes AI adoption as an organizational rewiring — not a tech deployment. The concept of a "superagency" organization (where humans and agents together accomplish what neither can alone) is McKinsey's primary 2025–2026 thought-leadership frame.

**QuantumBlack**: Since joining McKinsey in 2015, QuantumBlack has evolved from a 45-person data-science boutique to the firm's global AI and engineering powerhouse. It contributes open-source tooling (Kedro, the ML pipeline framework), proprietary delivery accelerators, and the Horizon MLOps platform. It acts as the engineering spine inside a generalist firm — analogous to BCG X but historically more data-science focused.

**Internal deployment**: Lilli (firm-wide since July 2023) is McKinsey's internal knowledge platform serving 100,000+ documents to 72% of the firm with time savings up to 30%. See [Consulting Firm AI Knowledge Platforms](./07-consulting-firms.md) for full Lilli architecture details.

**Economics**: Growing share of outcome-linked fees; the firm is deliberately multi-model and positions as an orchestrator-neutral integrator across Anthropic, OpenAI, and all three hyperscalers.

**Differentiator / Risk**: Unmatched C-suite trust and organizational-change depth. Risk: engineering credibility vs. Accenture-scale delivery capacity.

---

### BCG (BCG X)

**Revenue signal**: BCG disclosed that approximately **25% of its $14.4B in 2025 revenue ($3.6B) came from AI-related engagements** — the most explicit AI-revenue disclosure from any strategy firm and a benchmark against which rivals are now measured.

**BCG X**: BCG's venture-grade software-build arm (approximately 3,000 technologists) builds production AI products alongside traditional advisory. This is a genuine product-engineering bench inside a strategy brand, not a rebranded IT consulting group.

**Doctrine**: The 10-20-70 principle — 10% of AI effort on algorithms, 20% on data and technology, 70% on people, processes, and culture — is BCG's primary client framework. BCG's research shows that AI leaders outpace laggards with double the revenue growth and 40% more cost savings. The "Closing the AI Impact Gap" research (Sept 2025) identifies the gap between AI adoption rate and business-outcome rate as the defining challenge of this phase.

**Model/hyperscaler posture**: GENE (internal assistant on GPT-4o under OpenAI partnership) and Deckster (slide-tool). Strong OpenAI co-innovation history; multi-cloud delivery.

**Differentiator / Risk**: Build-capability inside a strategy brand; genuine engineering bench. Risk: productized-build margins tend to erode faster than strategy-advisory margins.

---

### Bain

**OpenAI alliance depth**: Bain's OpenAI relationship is the most structurally embedded in MBB. The original global services alliance (2023) became an expanded partnership (Oct 2024) and then direct investment in the **OpenAI Deployment Company** — a new $4B+ joint venture with TPG, Brookfield, Advent, and Bain Capital (May 2026) specifically targeting private equity firms and their portfolio companies.

**Private equity channel**: Bain is the global market leader in PE consulting. The Bain/OpenAI Deployment Company partnership focuses precisely on this sector — AI diligence, deal value-creation, and portfolio-company transformation — a structurally privileged distribution channel no MBB rival can replicate at the same depth.

**Vector platform**: Bain's methodology/technology wrapper for AI implementations, packaging delivery approaches and accelerators into repeatable program structures. "No-regrets" use cases (cost reduction in visible, measurable processes) are the recommended entry point before scaling to more ambitious reinvention programs.

**VC ecosystem**: Bain formalized partnerships with seven flagship VC firms to create an AI-innovation pipeline for clients — embedding Bain into the startup-to-enterprise AI diffusion chain.

**Differentiator / Risk**: PE channel depth is structurally unique. Risk: smaller engineering bench than BCG X; heavily dependent on ecosystem partnerships for delivery.

---

## 3. Big Four

### Deloitte

**Zora AI**: Launched at NVIDIA GTC (March 2025), Zora AI is Deloitte's portfolio of ready-to-deploy agentic AI workers covering finance, supply chain, human capital, procurement, sales/marketing, and customer service. Built on NVIDIA's AI stack (Llama Nemotron models, NVIDIA AI-Q Blueprint), with planned deployment to thousands of users by end of 2025. Deloitte subsequently integrated Zora with Oracle AI Agent Studio (embedded in Oracle Fusion Cloud) and made it available on HPE Private Cloud AI.

**Ecosystem footprint**: Deloitte holds enterprise alliances with all three hyperscalers, NVIDIA (AI Factories for enterprise GPU infrastructure), Oracle, SAP, Salesforce, and ServiceNow — the broadest multi-vendor coverage in the Big Four. The NVIDIA partnership positions Deloitte to sell AI infrastructure buildout alongside strategy and implementation.

**Internal deployment**: Sidekick is Deloitte's internal productivity assistant (successor to PairD). Anthropic enterprise deployment announcements (2025) make Deloitte one of the largest commercial Claude deployments.

**AI assurance**: Following a 2025 cautionary episode around AI-produced deliverable quality, Deloitte strengthened internal AI assurance frameworks — which it now also sells as a client service.

**Differentiator**: End-to-end coverage (strategy → ops → tax/audit adjacency) plus regulated-industry trust. The firm can land in a client's strategy phase and stay through implementation and audit — a complete lifecycle moat.

---

### PwC

**Agent OS**: PwC's "Agent OS" (launched 2025) is the firm's most distinctive platform bet — an **orchestration layer that coordinates AI agents from multiple vendors** (Anthropic, AWS, GitHub, Google Cloud, Microsoft Azure, OpenAI, Oracle, Salesforce, SAP, Workday, CrewAI, LangGraph) into unified enterprise workflows with governance built in. The "one ring to rule them all" framing positions PwC as the system integrator for heterogeneous agent stacks.

**AI assurance**: PwC's structural advantage is its audit DNA. Agent OS incorporates the AI Verify Foundation's "Continuous Assurance Loop" with automated, evidence-backed attestations. It is designed to support EU AI Act and UK DRCF requirements for high-risk AI systems with provable human oversight, real-time logging, and data-subject opt-out routes. PwC contributes telemetry schemas back to AI Verify's open spec — connecting the firm's commercial practice to standards-body influence.

**Scale**: ChatPwC (internal assistant) is deployed firm-wide. PwC has expanded Agent OS to support OpenAI GPT-5 and AWS Bedrock as of mid-2026.

**Differentiator / Risk**: AI assurance/attestation is a structural moat rooted in the firm's audit independence. The risk is the reverse: independence rules constrain how deeply PwC can co-build the systems it then must audit.

---

### EY

**EY.ai Agentic Platform**: Launched in March 2025 in collaboration with NVIDIA, the platform integrates 150 AI agents to support 80,000+ EY professionals across tax, risk, and finance — targeting **3M+ annual tax compliance outcomes** and redefining **30M+ tax processes annually**. The platform runs across client clouds, on-premises, at the edge, and on the NVIDIA Cloud Provider ecosystem.

**Investment scale**: EY committed $1.4B to EY.ai (2023), one of the largest disclosed AI platform investments in professional services. EYQ (the original enterprise GenAI environment for 300,000+ professionals) provides the governed prompt tooling and sandbox layer that underpins the agentic platform.

**Microsoft partnership**: Co-engineering with Microsoft Azure for agentic orchestration, governance, and deployment. EY and Microsoft partnered to bring agentic AI to risk management (WatersTechnology, 2025). Eurobank is deploying the EY.ai agentic platform via Microsoft Azure to embed agents into core banking.

**Physical AI expansion**: In December 2025 EY announced a new physical AI platform and the EY.ai Lab — extending the AI strategy from software agents into robotics and edge AI, a differentiating move for manufacturing and logistics clients.

**Differentiator**: Tax and finance domain agents are defensible because EY owns decades of process knowledge and regulatory interpretation that cannot be commoditized by a generic model. Post-Everest network fragmentation remains a platform-consistency risk.

---

### KPMG

**KPMG Workbench**: Launched June 2025, Workbench is KPMG's foundational multi-agent platform built on Microsoft Azure AI Foundry Services. It currently hosts **50 AI agents/chatbots with nearly 1,000 in development**, integrates partners including Oracle, Salesforce, ServiceNow, and Workday, and allows **agent-to-agent communications** across vendors.

**Trusted AI framework**: KPMG is the **first organization globally to achieve BSI/ISO 42001 certification** for AI Management Systems. Every agent on Workbench carries a "Trusted AI stamp" verified against KPMG's 10-pillar framework — a credentialing structure KPMG now sells to clients as an AI governance service.

**Microsoft depth**: In June 2026, KPMG and Microsoft announced an expansion deploying **Microsoft Agent 365 to all 276,000+ KPMG professionals across 138 countries** — one of the largest single enterprise AI-agent rollouts disclosed publicly.

**Differentiator**: The ISO 42001 certification and Trusted AI stamp give KPMG a standards-backed moat in AI risk/controls packaging. KPMG sells the same governance framework to clients that it uses internally — a rare "eat your own cooking" credibility signal. Smallest revenue scale among the Big Four, but sharpest Microsoft-stack depth.

---

## 4. Global System Integrators

### Accenture

**Market benchmark**: Accenture generated **$5.9B in GenAI new bookings in FY2025** (nearly doubling year-over-year) and **$2.7B in advanced AI revenue** (tripling from $0.9B in FY2024). Nearly **80% of Accenture's large deals include AI-enabled services**. These are the most concrete public benchmarks for measuring any firm's AI revenue claims.

**Reinvention Services**: Effective September 2025, Accenture reorganized its core capabilities — strategy, consulting, technology, operations, industry depth, and ecosystem partnerships — under a single "Reinvention Services" umbrella. The intent: eliminate silos and embed data/AI across every service line, with the Americas led by Manish Sharma.

**Delivery IP**: Proprietary model-routing switchboard (choosing the right model/cloud per task), delivery foundries (accelerators for specific process domains), and equity investments in the Anthropic ecosystem. The strategy is to be the general contractor of enterprise AI — neutral across model providers and clouds, opinionated in delivery methodology.

**Workforce scale**: 70,000+ trained AI practitioners; internal AI adoption among the most aggressive in the industry with AI use tied to promotion criteria.

**Differentiator / Risk**: Sheer scale and ecosystem neutrality. Risk: automation eats Accenture's own hours faster than anyone, and hyperscaler professional services teams and lab FDE programs target the highest-value integration work directly.

---

### IBM Consulting

**Structural asset**: IBM is unique in combining consulting + software (watsonx) + infrastructure in one P&L, giving IBM Consulting a vertically integrated stack no pure-services rival can replicate.

**Consulting Advantage / Enterprise Advantage**: The internal hybrid-AI platform delivers IBM services using watsonx. At Think 2026, IBM announced **Context Studio** (agents grounded in organizational data and process structure, supporting digital sovereignty) and the upcoming **Process Studio** (AI agents that extract logic from legacy SOPs to make processes agent-ready).

**Interoperability leadership**: IBM and SAP expanded collaboration through the **Agent2Agent (A2A) interoperability standard**, with IBM Consulting Advantage agents now orchestrating SAP Joule agents through watsonx Orchestrate — the most concrete cross-vendor agent interoperability demo in the industry.

**Real-world metrics**: Providence Health System deployed IBM's HR agent (watsonx Orchestrate + existing HR platform) and achieved 90% less manager time on hiring steps and 70% more accurate job requests after eight months.

**Differentiator**: Regulated hybrid enterprises (financial services, healthcare, government) with mainframe adjacency. Claude integration via the Anthropic/IBM partnership adds frontier-model flexibility to the watsonx stack.

---

### Infosys

**Topaz umbrella**: Infosys Topaz is the AI-services brand covering industry-specific models, agentic frameworks, and domain accelerators. The **Agentic AI Foundry** (launched May 2025) runs on the NVIDIA Enterprise AI Factory validated design, enabling on-premises GPU-accelerated deployments globally.

**Verticalized SLMs**: Infosys launched NVIDIA-enabled small language models tuned for specific domains: **Topaz BankingSLM** (financial services) and **Topaz ITOpsSLM** (IT operations), allowing clients to fine-tune on proprietary data atop pre-built domain foundations — a middle path between generic frontier models and full custom training.

**Aster**: Infosys Aster (June 2024) is the AI-amplified marketing suite, covering 400+ assets and 50+ partner ecosystem — an early move into "AI as a service product" rather than "AI in a services engagement."

**Outcome pricing**: Infosys is actively steering client conversations toward outcomes and benefits rather than rates — embedding GenAI into deal structures as a commercial differentiator for price-conscious clients.

**Differentiator**: Strong data-engineering heritage (a prerequisite for Topaz quality), NVIDIA partnership depth, and verticalized SLMs that reduce fine-tuning cost for regulated industries.

---

### Tata Consultancy Services (TCS)

**WisdomNext**: Launched May 2024, TCS AI WisdomNext is an industry-first GenAI aggregation platform that orchestrates models, agents, and data types from a single interface. The platform includes a **library of thousands of industry-tested agents and workflows**, an Agentic Orchestrator Workbench, and visual agent-driven workflow design with end-to-end observability.

**Workforce scale**: **300,000+ associates trained** on foundational AI/ML skills including GenAI — TCS is building what it describes as one of the largest AI-ready workforces in the world.

**Strategy**: AI-led managed services — embedding agents into run-the-business contracts where TCS already owns operations. The play is incremental displacement of human-performed process steps from within existing long-term contracts, which are harder to displace than project-based competitors.

**Recognition**: Named Leader in Artificial Intelligence and Generative AI Services by Everest Group.

**Differentiator**: Scale, existing operations relationships, and the depth of the WisdomNext industry-agent library. Watch: 2025–2026 workforce restructuring announcements as the leading indicator of pyramid compression.

---

### Wipro

**ai360 ecosystem**: Launched July 2023 with a **$1B three-year AI investment commitment**, ai360 integrates AI into every platform, tool, and solution Wipro uses internally and delivers to clients.

**Lab45**: Wipro's innovation hub provides clients with talent, training, scale, and co-innovation capabilities. The Lab45 AI Platform includes **1,000+ GenAI agents and 10+ applications** across HR, sales, marketing, and operations — available in no-code and low-code form.

**WEGA**: The agent-native delivery platform under Wipro Intelligence — unifying Wipro's AI agents, intelligent assistants, and partner tools in a single extensible ecosystem.

**Recognition**: Recognized as Services-as-Software Star and Market Leader in HFS Horizons: Agentic Services 2026.

**NVIDIA**: Wipro is delivering sovereign AI services with NVIDIA AI to governments and enterprises — targeting regulated and public-sector clients requiring on-premises or data-sovereign AI deployments.

**Differentiator**: Sovereign AI positioning (few SIs are actively selling to government clients on this basis), broad Lab45 agent library, and the WEGA platform for agent-native delivery.

---

### Cognizant

**Neuro AI**: Cognizant's enterprise AI application platform, now featuring multi-agent orchestration via the **Neuro® AI Multi-Agent Accelerator** — an open-source framework (Neuro SAN, System of Agent Network) that lets organizations design, deploy, and scale networks of collaborating agents for complex workflows without coding.

**NVIDIA collaboration**: Deployed in March 2025, Cognizant's Neuro AI platform uses NVIDIA AI to deliver specialized LLMs and reasoning agents, targeting digital twins and domain-specific models.

**Scale demonstration**: Cognizant used the Neuro AI Multi-Agent Accelerator to review **30,000+ hackathon submissions in under 24 hours** — a Guinness World Record–breaking event that doubled as a live proof-of-concept for agent-at-scale throughput.

**Recognition**: Neuro AI Multi-Agent Accelerator won the Global AI Award 2026 for innovative multi-agent design.

**Developer productivity**: Large-scale AI-assisted coding rollouts (among the largest enterprise coding-assistant deployments publicly referenced) are a signature differentiator for Cognizant's software engineering services.

**Differentiator**: Pragmatic agent industrialization for the Global 2000, open-source Neuro SAN framework (avoids vendor lock-in concern), and aggressive developer-productivity positioning.

---

### Capgemini

**WNS acquisition**: Capgemini acquired WNS (global BPO provider) for **$3.3B (completed October 2025)** to create what it calls a global leader in **"Agentic AI-powered Intelligent Operations"** — the explicit thesis being that the largest AI-value opportunity is fundamental business-process redesign, not IT transformation.

**Financial impact**: The deal is expected to increase Capgemini's normalized EPS by ~4% in 2026 and ~7% in 2027, with €100M–€140M in additional annual revenues from synergies by end of 2027.

**The BPO → APO thesis**: Traditional labor-intensive BPO is being displaced by AI-driven automation. Capgemini is positioning the combined entity as "Agentic Process Operations" — a new category above traditional BPO where consulting-led process redesign is delivered with AI agents rather than offshore headcount.

**EU positioning**: Capgemini's European scale and regulatory fluency (AI Act delivery kits, sovereign AI positioning) give it a structural advantage with EU-regulated clients that few global SIs can match.

**Differentiator**: The WNS acquisition makes Capgemini the only global SI that has structurally committed to the BPO→APO transition at scale via M&A. Watch for integration execution as the key risk.

---

### HCLTech

**AI Force**: HCLTech's GenAI and agentic platform is **LLM-agnostic** — integrating Microsoft GitHub Copilot, Google Gemini, AWS Claude, NVIDIA, IBM watsonx, and Meta Llama in a unified enterprise platform. AI Force 2.0 adds enterprise-grade agentic AI capabilities including autonomous workflow agents.

**Enterprise AI Foundry**: A complementary platform tuned for AWS, Azure, and GCP, removing complexity around industrial-scale foundation model deployment, data silos, and framework sprawl.

**Google partnership depth**: HCLTech integrated Gemini into AI Force (patented, system-agnostic integration) and announced expanded collaboration with Google Cloud to accelerate agentic AI — formalizing a program to cultivate Google Cloud champions and support **2,000+ GenAI-led customer engagements**.

**Engineering heritage**: HCLTech's Engineering and R&D Services (ERT) business gives it genuine credibility in AI in products (not just IT systems) — building AI into client products at the component level, not just deploying AI in enterprise software.

**Differentiator**: LLM-agnosticism removes a common client concern; ERT heritage is underrated for the product-embedded AI market.

---

### LTIMindtree

**BlueVerse**: Launched June 2025, BlueVerse is LTIMindtree's AI-native agentic ecosystem comprising three layers:

- **BlueVerse Marketplace**: 325+ pre-built, domain-specific solution accelerators across marketing, service support, supply chain, and digital sales
- **BlueVerse Foundry**: No-code designer + pro-code editor for composing and deploying AI agents, RAG pipelines, and intelligent business processes
- **Productized services**: Marketing-as-a-Service and Contact Center-as-a-Service built on agentic workflows

**Agent composability**: Agents in BlueVerse are built from discrete reusable "skills" — allowing rapid assembly of new workflows without rebuilding from scratch, and enabling client-specific combinations of pre-built and custom agents.

**Differentiator**: Marketplace-plus-foundry model lowers the barrier to entry (buy pre-built, build custom) while the productized service layers give LTIMindtree an upsell into outcome-based commercial models.

---

### Tech Mahindra

**Telecom-vertical moat**: Tech Mahindra's primary AI defensibility is its telecom depth. The **OpsamplifAIer** platform (agentic AI for IT operations) automates B2C order management, billing, invoicing, and network operations including RAN and fixed broadband — with a marketplace of 150+ telecom-specific agents.

**NVIDIA collaboration (March 2026)**: Jointly introduced an AI-powered **Telco Network Operations Reasoning Agent** — supporting autonomous alarm validation, root-cause analysis, and resolution across OSS and BSS environments. The solution enables Level 4+ autonomous network operations, converting traditional NOCs into closed-loop intelligent operations.

**Differentiator**: Telecom-vertical AI (network AI, BSS/OSS agents) is a structurally defensible lane because the domain specificity (3GPP protocols, network topology reasoning, real-time SLA management) is not easily replicated by generic consulting entrants.

---

## 5. Boutiques and Specialists

### Slalom

Local-market delivery model plus deep hyperscaler partnerships (AWS, Salesforce heritage, now all-cloud). AI strategy-to-build for mid-enterprise; element-lab-style accelerators for faster time-to-value. Wins on speed, culture, and proximity; constrained on global-scale deal pursuit.

### Thoughtworks

Engineering-culture flagship with CD/DDD heritage — the reference firm for *how engineering organizations should actually adopt coding agents*. Took private by Apax (2025) with a refocus on AI-native software delivery and legacy modernization with agents. Technology Radar (semi-annual) is unmatched thought-leadership distribution across the software engineering community. Signature value: AI-assisted SDLC frameworks, sensible defaults for responsible AI in engineering, and deep modernization with agent-augmented delivery.

---

## 6. Cross-Firm Comparison

Scores are directional (1–5 scale) based on disclosed investments, platform depth, partnership tier, and published case studies as of July 2026.

| Firm | Platform/IP depth | Model-lab intimacy | Outcome-pricing progress | Internal AI adoption | Engineering bench | Regulated-industry trust |
|---|---|---|---|---|---|---|
| McKinsey | 4 | 4.5 | 3.5 | 4.5 (Lilli) | 3.5 | 4.5 |
| BCG | 4 | 4.5 | 3.5 | 4 | 4 | 4 |
| Bain | 3 | 4.5 | 3.5 | 3.5 | 3 | 4 |
| Deloitte | 4.5 | 4.5 | 3.5 | 4 | 4 | 5 |
| PwC | 4 | 4.5 | 3 | 4 | 3.5 | 5 |
| EY | 3.5 | 4 | 3 | 3.5 | 3.5 | 5 |
| KPMG | 3.5 | 4 (MSFT) | 3 | 3.5 | 3 | 5 |
| Accenture | 5 | 5 | 4 | 4.5 | 5 | 4.5 |
| IBM Consulting | 4.5 | 3.5 (self) | 3.5 | 5 | 4.5 | 5 |
| Infosys | 4 | 4 | 4 | 4.5 | 4.5 | 4 |
| TCS | 4 | 3.5 | 4 | 4 | 4.5 | 4.5 |
| Wipro | 3.5 | 3.5 | 3.5 | 3.5 | 4 | 4 |
| Cognizant | 4 | 4 | 3.5 | 4 | 4 | 4 |
| Capgemini | 4 | 4 | 3.5 | 4 | 4.5 | 4.5 (EU) |
| HCLTech | 3.5 | 4 | 3.5 | 3.5 | 4.5 | 4 |
| LTIMindtree | 3.5 | 3.5 | 3.5 | 3.5 | 4 | 3.5 |
| Tech Mahindra | 3 | 3.5 | 3 | 3.5 | 4 (telecom) | 3.5 |
| Slalom | 3 | 4 (AWS/SFDC) | 3 | 3.5 | 3.5 | 3 |
| Thoughtworks | 4 (eng IP) | 3.5 | 3 | 4.5 | 5 | 3.5 |

---

## 7. Buyer Guidance

```mermaid
graph TD
    Start["Choosing a GenAI delivery partner"] --> IP["Demand IP transparency:<br/>firm-owned vs. resold accelerators,<br/>exported-artifact rights at contract end"]
    IP --> Price["Price the pyramid honestly:<br/>rate cards reflect AI-assisted productivity;<br/>prefer outcome-based or capped-capacity structures"]
    Price --> Internal["Test internal adoption:<br/>ask for internal agent-fleet metrics<br/>and case studies before buying the pitch"]
    Internal --> Assurance["Separate assurance from build:<br/>use independent evaluators or audit-DNA firms<br/>(PwC Agent OS, KPMG Trusted AI/ISO 42001)"]
    Assurance --> FDE["FDE clause hygiene:<br/>contract for knowledge transfer, artifact/model ownership,<br/>runbook delivery, exit provisions"]
    FDE --> EU{"EU-regulated environment?"}
    EU -->|Yes| EUReq["Prioritize AI Act delivery kits,<br/>ISO 42001 certification,<br/>data-residency-compatible architecture"]
    EU -->|No| Done["Proceed to contracting"]
    EUReq --> Done
```

**Demand IP transparency.** Ask which accelerator or platform components are firm-owned vs. resold, what contractual rights you have to exported artifacts at contract end, and whether agents land in your runtime registry or theirs.

**Price the pyramid honestly.** Insist rate cards reflect AI-assisted productivity. If a firm's junior staff are 30–50% faster with AI, the blended rate should reflect that. Prefer outcome-based or capped-capacity structures for build work.

**Test internal adoption.** Firms that can't show their own agent fleets (Lilli, Sidekick, Consulting Advantage, Workbench, WEGA) at scale internally have limited credibility selling you one. Ask for internal adoption metrics and case studies before buying the external pitch.

**Separate assurance from build.** Use audit-DNA firms (PwC's Agent OS, KPMG's Trusted AI/ISO 42001) or independent evaluators for AI assurance over the builder's work. A firm that builds your agent stack and then attests to its safety is a conflict-of-interest risk.

**FDE clause hygiene.** If buying forward-deployed engineering (from labs, hyperscalers, or firms), contract explicitly for: knowledge transfer milestones, artifact and model ownership, runbook delivery, and exit provisions. Lab FDE teams are excellent but create dependency without these safeguards.

**EU-specific procurement.** For EU-regulated environments, prioritize firms with AI Act delivery kits (Capgemini, PwC), ISO 42001 certifications (KPMG), and data-residency-compatible architectures. These are table stakes post-2026.

---

## 8. Sector Predictions (2026–2028)

- **25–40% of AI delivery revenue** at leading firms will be non-linear (platforms, outcomes, managed agents) by 2028, up from single digits in 2024.
- **At least one Big-Four-scale firm** launches a standalone agent-assurance/attestation business line with regulator recognition by 2027. PwC's Agent OS assurance layer and KPMG's ISO 42001 stamp are the leading candidates.
- **Indian SIs bifurcate**: Leaders (Infosys, TCS, Cognizant) convert BPO into Agentic Process Operations at higher margin with proprietary domain agents. Laggards face pricing-driven revenue compression as generic offshore labor becomes easier to replicate with commodity models.
- **Model-lab FDE teams and hyperscaler professional services** will capture an increasing share of the highest-value integration work, pushing all consulting firms further toward industry-process IP as the defensible layer.
- **The WNS acquisition template** (Capgemini, $3.3B) will be replicated: at least one other SI acquires a large BPO to accelerate the BPO→APO transition rather than building it organically.

---

## Related

- [Consulting Firm AI Knowledge Platforms](07-consulting-firms.md) — the internal knowledge-management systems (Lilli, GENE, PairD, EYQ, KymChat) behind these firms' strategy plays.
- [Strategy Hub](../strategy/index.md) — broader AI transformation and operating-model strategy context.

## Sources

- [Seizing the Agentic AI Advantage — McKinsey QuantumBlack](https://www.mckinsey.com/capabilities/quantumblack/our-insights/seizing-the-agentic-ai-advantage)
- [CEO Strategies for Leading in the Age of Agentic AI — McKinsey](https://www.mckinsey.com/capabilities/quantumblack/our-insights/the-change-agent-goals-decisions-and-implications-for-ceos-in-the-agentic-age)
- [QuantumBlack AI Consulting — McKinsey](https://www.mckinsey.com/capabilities/quantumblack/how-we-help-clients)
- [Rewiring the Way McKinsey Works with Lilli — McKinsey](https://www.mckinsey.com/capabilities/tech-and-ai/how-we-help-clients/rewiring-the-way-mckinsey-works-with-lilli)
- [BCG Rode AI to $3.6B in Revenue — Metaintro](https://www.metaintro.com/blog/bcg-25-percent-ai-revenue-consulting-jobs-2026)
- [AI Leaders Outpace Laggards with Double the Revenue Growth — BCG Press, Sept 2025](https://www.bcg.com/press/30september2025-ai-leaders-outpace-laggards-revenue-growth-cost-savings)
- [Bain &amp; Company Invests in the OpenAI Deployment Company — Bain Press Release, 2026](https://www.bain.com/about/media-center/press-releases/2026/bain-company-openai-a-new-venture-to-deploy-ai-at-enterprise-scale/)
- [Bain &amp; OpenAI Alliance — Bain &amp; Company](https://www.bain.com/vector-digital/partnerships-alliance-ecosystem/openai-alliance/)
- [Deloitte Unveils Zora AI — Deloitte Press Room, March 2025](https://www.deloitte.com/us/en/about/press-room/deloitte-unveils-zora-ai-agentic-ai-for-tomorrows-workforce.html)
- [The Deloitte NVIDIA Relationship — Deloitte](https://www.deloitte.com/us/en/alliances/nvidia-alliance.html)
- [PwC's Agent OS — PwC](https://www.pwc.com/us/en/services/ai/agent-os.html)
- [Scaling Enterprise Operations with PwC's AI Strategy and Agent OS — theCUBE Research](https://thecuberesearch.com/pwc-ai-agentic-enterprise-operations/)
- [EY Launching EY.ai Agentic Platform with NVIDIA — EY Newsroom, March 2025](https://www.ey.com/en_gl/newsroom/2025/03/ey-launching-ey-ai-agentic-platform-created-with-nvidia-ai-to-drive-multi-sector-transformation-starting-with-tax-risk-and-finance-domains)
- [Building an Enterprise-Scale Agentic AI Operating System — EY](https://www.ey.com/en_gl/insights/ai/building-an-enterprise-scale-agentic-ai-operating-system)
- [KPMG Launches KPMG Workbench — KPMG Press Release, June 2025](https://kpmg.com/xx/en/media/press-releases/2025/06/kpmg-launches-a-multi-agent-ai-platform-transforming-client-delivery-and-ways-of-working-across-the-global-organization.html)
- [KPMG and Microsoft Scale Trusted Enterprise AI Agents — KPMG Press Release, June 2026](https://kpmg.com/xx/en/media/press-releases/2026/06/kpmg-and-microsoft-scale-trusted-enterprise-ai-agents-globally.html)
- [KPMG and Microsoft Scale Trusted Enterprise AI Agents Globally — Microsoft Source, June 2026](https://news.microsoft.com/source/2026/06/09/kpmg-and-microsoft-scale-trusted-enterprise-ai-agents-globally-through-deployment-of-agent-365-and-copilot/)
- [$5.9B in GenAI Bookings: Accenture Posts Record $80.6B New Bookings — StockTitan / Accenture FY2025 Results](https://www.stocktitan.net/news/ACN/accenture-reports-fourth-quarter-and-full-year-fiscal-2025-t7wo8n3bfooo.html)
- [AI Transformation Is a Workforce Transformation — BCG (10-20-70 context); Accenture Reinvention Services reorg per Accenture Q2 FY2026 earnings (SEC Form 8-K)](https://www.sec.gov/Archives/edgar/data/1467373/000146737326000013/q2fy26earnings8-kexhibit.htm)
- [IBM Consulting Expands AI Capabilities — IBM Newsroom, May 2026](https://newsroom.ibm.com/2026-05-06-ibm-consulting-expands-ai-capabilities-to-accelerate-enterprise-transformation)
- [IBM Consulting Advantage — IBM](https://www.ibm.com/consulting/advantage)
- [IBM Enterprise Advantage AI Agents Explained for 2026 — Marketing Scoop](https://www.marketingscoop.com/enterprise-ai-consulting-software/ibm-enterprise-advantage-ai-agents-explained-for-2026/)
- [Infosys Readies to Deliver Outcomes at Scale Through Enterprise AI — TBR](https://tbri.com/special-reports/infosys-readies-to-deliver-outcomes-at-scale-through-ai/)
- [TCS Launches WisdomNext — TCS Newsroom](https://www.tcs.com/who-we-are/newsroom/press-release/tcs-launches-wisdomnext-an-industry-first-genai-aggregation-platform)
- [Wipro Unveils AI360 and Commits $1B in AI Investing — Wipro Newsroom, July 2023](https://www.wipro.com/newsroom/press-releases/2023/wipro-launches-wipro-ai360-commits-to-investing-1-billion-in-ai-over-the-next-three-years/)
- [Cognizant Neuro AI Multi-Agent Accelerator — Cognizant](https://www.cognizant.com/us/en/services/cognizant-platforms/neuro-generative-ai-adoption/enterprise-agentic-ai)
- [Capgemini Completes Acquisition of WNS — Capgemini Press Release, October 2025](https://www.capgemini.com/news/press-releases/capgemini-completes-the-acquisition-of-wns-and-creates-a-global-leader-in-agentic-ai-powered-intelligent-operations/)
- [AI Force — HCLTech](https://www.hcltech.com/ai-force)
- [LTIMindtree Launches BlueVerse — LTIMindtree / NASDAQ Press Release, June 2025](https://www.nasdaq.com/press-release/ltimindtree-launches-blueverse-ai-ecosystem-will-define-enterprise-future-2025-06-19)
- [Tech Mahindra Advances AI-Driven Autonomous Network Operations with NVIDIA — Tech Mahindra Press Release, March 2026](https://www.prnewswire.com/news-releases/tech-mahindra-advances-ai-driven-autonomous-network-operations-for-csps-globally-with-nvidia-302702431.html)
