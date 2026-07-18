import React from 'react';
import Layout from '@theme/Layout';
import Link from '@docusaurus/Link';

const DOMAINS = [
  {key: 'strategy', label: 'Strategy', scope: 'AI strategy, business architecture, operating models, transformation, economics & value'},
  {key: 'architecture', label: 'Architecture', scope: 'Foundations, landing zones, reference architectures, pattern catalogs, ADR library, ARB'},
  {key: 'agentic-systems', label: 'Agentic Systems', scope: 'Agents, multi-agent topologies, orchestration, memory, skills & tools, HITL, harness'},
  {key: 'protocols', label: 'Protocols', scope: 'MCP, A2A, emerging standards, agent identity & auth, connectors'},
  {key: 'data-knowledge', label: 'Data & Knowledge', scope: 'Data architecture, RAG, knowledge graphs/GraphRAG, semantic memory, lineage, lakehouse'},
  {key: 'platforms', label: 'Platforms', scope: 'Platform engineering, cloud providers, K8s for AI, gateways, runtimes, inference, silicon'},
  {key: 'trust', label: 'Trust', scope: 'Threat models, AI control, identity/authz, guardrails, red teaming, governance, compliance'},
  {key: 'operations', label: 'Operations', scope: 'LLMOps/MLOps, AgentOps, evaluation, observability, reliability, DR/BCP, FinOps'},
  {key: 'learning-paths', label: 'Learning Paths', scope: '8 persona journeys and EA masterclass modules'},
  {key: 'career', label: 'Career', scope: 'Interview prep, certifications, soft skills, mental models, role guides'},
  {key: 'assets', label: 'Assets', scope: 'Templates, checklists, workshop kits, transcripts, case studies, glossary'},
];

function DomainCard({domain}) {
  return (
    <div className="col col--4 margin-bottom--lg">
      <Link to={`/docs/${domain.key}/`} className="card padding--md" style={{height: '100%'}}>
        <h3>{domain.label}</h3>
        <p>{domain.scope}</p>
      </Link>
    </div>
  );
}

export default function Home() {
  return (
    <Layout
      title="Archon"
      description="Enterprise AI Wiki — strategy, architecture, agentic systems, protocols, data & knowledge, platforms, trust, and operations.">
      <header className="hero hero--primary">
        <div className="container">
          <h1 className="hero__title">Archon</h1>
          <p className="hero__subtitle">
            Enterprise AI Wiki — the governed knowledge base for building, running, and trusting enterprise AI systems.
          </p>
          <Link className="button button--secondary button--lg" to="/docs/architecture/00-wiki-governance">
            Read the governance model
          </Link>
        </div>
      </header>
      <main>
        <div className="container margin-vert--lg">
          <div className="row">
            {DOMAINS.map((domain) => (
              <DomainCard key={domain.key} domain={domain} />
            ))}
          </div>
        </div>
      </main>
    </Layout>
  );
}
