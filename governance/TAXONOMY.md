# Information Architecture — 8 Domains + 2 Tracks + Asset Library

| Key (frontmatter `domain`) | Folder | Scope |
|---|---|---|
| strategy | docs/strategy/ | AI strategy, business architecture, operating models, transformation, economics & market, value/OKRs |
| architecture | docs/architecture/ | Foundations, landing zones, reference architectures, pattern & anti-pattern catalogs, ADR library, DDD for agents, integration patterns, ARB |
| agentic-systems | docs/agentic-systems/ | Agents, multi-agent topologies, orchestration & workflow engines, memory hub, skills & tools, planning, HITL, agent UX, digital employees, harness |
| protocols | docs/protocols/ | MCP (hub + changelog), A2A, emerging standards, agent identity & auth, connectors |
| data-knowledge | docs/data-knowledge/ | Data architecture & engineering, RAG hub, knowledge graphs/GraphRAG, semantic & long-term memory, lineage, lakehouse |
| platforms | docs/platforms/ | Platform engineering, AWS/Azure/GCP, K8s for AI, gateways, runtimes, inference serving, silicon, IaC, edge |
| trust | docs/trust/ | Threat models, AI control, identity/authz, guardrails, red teaming, governance frameworks, RAI/constitutional, sovereign, compliance index, AI SOC |
| operations | docs/operations/ | LLMOps/MLOps, AgentOps, evaluation hub + benchmark catalog, observability hub, reliability, chaos, production readiness, DR/BCP, FinOps hub |
| learning-paths | docs/learning-paths/ | 8 persona journeys + EA masterclass modules |
| career | docs/career/ | Interview prep, certifications, soft skills, mental models, role guides |
| assets | docs/assets/ | Templates, checklists, workshop kits, transcripts, case studies, glossary |

Rules: max depth 3 under docs/; each domain has ONE hub `index.md` (doc_type: hub);
old-repo sections map into these — no new top-level folders without a taxonomy PR.
