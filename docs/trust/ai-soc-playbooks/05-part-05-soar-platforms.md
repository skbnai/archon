---
title: "AI SOC Playbooks Part 05: SOAR Platform Comparison"
doc_type: guide
domain: trust
status: current
topic_id: part-05-soar-platforms
last_reviewed: 2026-07-28
maturity: practitioner
supersedes: [docs/ai-soc-playbooks/part-05-soar-platforms.md]
tags: [soar, microsoft-sentinel, splunk, cortex-xsoar, google-secops, tines]
covers_version: "2026"
---

SOAR platforms have moved through four generations — orchestration, intelligence, no-code, and now agentic — and picking one is primarily a SIEM-alignment decision, not a feature comparison. This part compares the major commercial and open-source platforms and closes with a selection framework.

## SOAR Platform Evolution

**Generation 1 (2015-2019), Orchestration**: API-centric automation connecting tools to reduce manual copy-paste — Phantom (later Splunk) and Demisto (later Palo Alto) defined this era. **Generation 2 (2019-2022), Intelligence**: threat-intel enrichment, ML scoring, and case management layered on top — Microsoft Sentinel and Google Chronicle SOAR. **Generation 3 (2022-2024), No-Code/Low-Code**: visual workflow builders widened adoption to non-developers — Tines, Torq, BlinkOps, Swimlane. **Generation 4 (2024 onward), Agentic SOAR**: LLM-generated playbooks and AI investigation agents embedded directly in the workflow — Sentinel plus Copilot, Cortex XSIAM, SentinelOne AI.

## Platform Comparison Matrix

| Platform | Architecture | Workflow Engine | Integrations | LLM Integration | Agentic Support | Pricing Model | Best For |
|---|---|---|---|---|---|---|---|
| MS Sentinel | Cloud-native SaaS | Logic Apps (JSON/Bicep) | 300+ | Native (Copilot) | Security Copilot Agents | Per-workspace/consumption | Azure-native |
| Splunk SOAR | Cloud + on-prem | Custom Python | 500+ | Splunk AI | Limited (preview) | Per user + capacity | Splunk-centric |
| Cortex XSOAR | Cloud + on-prem | D2 (custom, Python) | 1000+ | Cortex AI | XSOAR Agents (preview) | Per GB ingested | Enterprise SOC |
| Google SecOps | Cloud-native | SOAR engine (Python) | 400+ | Gemini native | Gemini agents | Consumption | Google/GCP shops |
| IBM QRadar | Cloud + on-prem | Ariel/Python | 450+ | Watson | Limited | Per user | Regulated industry |
| Swimlane | Cloud + on-prem | Turbine (Python/low-code) | 200+ | Partner | Turbine AI | Per analyst | Security posture mgmt focus |
| Tines | Cloud SaaS | Story Builder (JavaScript) | 800+ | API-based | Limited | Per action | No-code flexibility |
| Torq | Cloud SaaS | Visual DAG (no-code) | 500+ | API-based | Limited | Per action | Enterprise no-code |

## Microsoft Sentinel + Security Copilot

Data flows from M365 Defender, Azure Defender, Azure AD, network telemetry, and third-party connectors into a Log Analytics workspace, where Analytics Rules drive incidents and hunting; Security Copilot (GPT-4/Claude-based) sits alongside Logic Apps playbooks to drive automated response actions across Defender, Azure, and M365. A Logic Apps playbook typically triggers on a Sentinel incident webhook, pulls the incident's entities (e.g., IPs), and fans out enrichment calls (VirusTotal lookups) per entity — expressed as JSON workflow definitions rather than a general-purpose language. Security Copilot's SOC capabilities include incident summarization in plain English, natural-language-to-KQL query generation (asking "find all PowerShell executions that download content from the internet in the last 24 hours" produces a working `DeviceProcessEvents` query with the right filter conditions), script/malware explanation, threat-actor attribution via Mandiant plus Microsoft TI, and next-step playbook recommendations; 2025 added Copilot Agents — Microsoft-published agents for specific SOC workflows plus custom plugins orchestrated from Copilot Studio.

Pricing: Sentinel runs about $2.46/GB ingested pay-as-you-go (up to 65% discount on commitment tiers); Security Copilot runs about $4/Security Compute Unit at roughly 3-5 SCU/hour typical usage — a 100GB/day organization lands around $7,380/month for the SIEM plus $4,320/month for Copilot. Strengths: best-in-class Microsoft 365/Azure integration; the most mature enterprise AI copilot for security as of 2026; UEBA and Fusion detection built into Microsoft XDR at no extra cost; enterprise-grade Logic Apps reliability. Weaknesses: Azure lock-in with a poor story for AWS/GCP-primary organizations; Logic Apps are harder to debug than Python-based alternatives; Copilot's consumption billing gets unpredictable at scale; limited native support for non-Microsoft data sources.

## Splunk SOAR (Phantom)

Splunk SOAR (the former Phantom engine) sits behind Splunk Cloud/Enterprise via REST API, offering a visual drag-and-drop-plus-code playbook editor, a Python playbook runner (a Docker container per run), a 500+-app framework, parallel action execution, the Mission Control unified analyst console, and embedded case management. Playbooks are plain Python using the `phantom.rules` API — a triage function calls `phantom.act()` to fetch an email, chains to an enrichment callback that checks URL reputation in parallel across VirusTotal, and chains again to a quarantine decision based on the results. Splunk's AI layer spans the Machine Learning Toolkit (anomaly detection, classification, forecasting via SPL `fit` commands), SPL AI (natural-language-to-SPL translation, AI alert summarization, OpenAI-powered anomaly detection), and a preview Splunk AI Security Assistant for chat-based investigation.

Pricing: Splunk Enterprise runs about $150/GB/year indexed (or $50/user/year); Splunk SOAR runs a $2,000/analyst/year minimum — a typical 100-analyst SOC spends $200K-500K/year on SOAR alone. Strengths: the most mature Python SDK and largest developer community; 500+ apps via the Splunkbase marketplace; an excellent unified Mission Control UX; deep shared-data-model integration with Splunk SIEM. Weaknesses: expensive combined SOAR-plus-SIEM licensing; Python-only with no low-code option for non-developers; operationally heavy on-premises deployment; AI features less mature than Microsoft's or Palo Alto's as of 2026.

## Palo Alto Cortex XSOAR / XSIAM

XSOAR provides the War Room collaborative investigation console, D2 (YAML plus Python) workflow scripting, a 1000+-integration marketplace, full incident-lifecycle management, Threat Intelligence Management, and MSSP-ready multi-tenancy. XSIAM is the unified XDR-plus-SOAR evolution: a shared data lake for all security telemetry, Cortex AI-driven detection informed by Unit 42 threat intelligence, an automated investigation engine, and XSOAR running underneath for integrated response. Cortex AI clusters hundreds of alerts into 5-10 campaigns, produces a 1-100 ML-based alert risk score, reconstructs a full causality chain from raw telemetry, and automates root-cause analysis; Cortex Copilot adds natural-language alert explanation, playbook recommendations, semantic search across similar past incidents, and Unit 42 sandbox-backed malware analysis. The XSOAR Marketplace is the industry's largest content ecosystem — 1000+ integrations, 700+ pre-built playbooks, and an active GitHub-based community contribution model.

Pricing is complex: XSOAR charges per GB analyzed plus per analyst seat; XSIAM charges per endpoint-day, effectively replacing multiple tool licenses; a typical enterprise spends $1M-5M/year for a full XSIAM platform. Strengths: the widest integration marketplace in the industry; XSIAM is the most integrated single-console XDR+SOAR+TI platform available; Unit 42 threat intelligence rivals Mandiant; the War Room UI excels at IR team coordination. Weaknesses: persistent XSOAR-vs-XSIAM pricing confusion; heavy on-premises XSOAR deployment; D2 scripting has a steeper learning curve than pure Python; less competitive outside the Palo Alto EDR/NGFW customer base.

## Google SecOps (Chronicle + Gemini)

Google SecOps combines Chronicle SIEM (1-year default retention versus the industry-standard 90 days, YARA-L detection rules, petabyte-scale storage at fixed cost, and Google's global threat intelligence), Chronicle SOAR (the former Siemplify, acquired 2022, with 400+ integrations), Mandiant Threat Intelligence, Gemini in Security, and Google VirusTotal. Gemini's security features include natural-language explanation of UDM events, YARA-L rule generation from plain English, incident summarization, natural-language-to-search-query generation, threat-actor attribution drawing on Mandiant plus Google data, and malware reverse-engineering assistance — Gemini Investigation adds cross-query support (natural language compiling to a YARA-L/SQL hybrid), timeline reconstruction, and attack-path visualization. Chronicle's fixed-price model is a genuine economic differentiator against per-GB competitors: where Splunk's $150/GB/year implies roughly $5.4M/year for a 100GB/day environment and Sentinel's $2.46/GB implies roughly $90K/year, Chronicle charges a fixed annual price regardless of volume — for data-rich environments, the economics favor Chronicle significantly.

Strengths: petabyte-scale storage at fixed cost wins decisively for large enterprises; Mandiant IR expertise is natively embedded; a full year of default retention at no additional cost; Gemini plus Mandiant is arguably the strongest threat-intelligence AI combination in the industry. Weaknesses: primarily Google Cloud-centric architecture; the Siemplify-derived SOAR engine is less mature than Splunk SOAR or XSOAR; limited on-premises deployment options; inconsistent customer support quality outside the enterprise tier.

## IBM QRadar SOAR

QRadar SOAR centers on case management, Python-based playbook automation (including dynamic playbooks that adapt to incident type), the IBM Security Connect integration hub, and Watson-powered natural-language investigation, bidirectionally synced with QRadar SIEM for shared context and compliance-focused reporting. Watson for Cybersecurity adds an AI Advisor for plain-language alert explanation, structured investigation reports, natural-language querying, exploitability-ranked vulnerability prioritization, and automated MITRE ATT&CK technique mapping. Best fit: regulated industries (financial, healthcare, government) already invested in the IBM Security ecosystem, and enterprise SOCs prioritizing case management and compliance reporting over integration breadth or AI sophistication.

## Tines and Torq (No-Code SOAR)

A Tines "Story" is a visual workflow of HTTP actions, built-in actions, and conditions — a phishing-response story might trigger on an email-gateway webhook, retrieve the email, check the URL against VirusTotal, branch on the VT score, and on a hit quarantine the email while opening a Jira ticket, alerting Slack, and notifying the user. Tines AI (2025) lets an LLM call slot directly into a Story with no code — an HTTP Request action pointed at the Anthropic API with the alert data interpolated into the prompt is a complete "analyze this alert" step. Torq differentiates on enterprise features (SSO, RBAC, audit) and stronger compliance reporting, while Tines offers a simpler UX and better documentation; both are REST-API-first, and Torq markets an AI-assisted "Hyperautomation" workflow-building capability.

## Open-Source SOAR

**Shuffle** is Python-plus-Docker, REST-based, with a 200+-app community ecosystem via OpenAPI, deployable via Docker Compose or Kubernetes — best for SMBs, security research, and cost-sensitive deployments, with a less polished UX and variable community-app quality. **StackStorm** is YAML-plus-Python, genuinely event-driven (sensors detect events, feeding triggers, rules, and actions natively rather than as a bolted-on layer), deployable via a Kubernetes Helm chart with enterprise support available through Extreme Networks — best for organizations automating NetOps and SecOps together.

## SOAR Selection Decision Framework

Weight the decision roughly as follows. **Primary SIEM alignment (40%, the dominant factor)**: Microsoft Sentinel pairs with Sentinel plus Copilot; Splunk Enterprise/Cloud pairs with Splunk SOAR; Palo Alto XSIAM pairs with Cortex XSOAR; Google Chronicle pairs with Google SecOps; a multi-SIEM or Elastic environment favors Tines or StackStorm instead of a SIEM-coupled platform. **Team coding capability (30%)**: strong Python developers favor Splunk SOAR or XSOAR; mixed technical levels favor Tines's visual-plus-code model; non-technical analysts favor Tines or Torq; an IT-operations-heavy team favors StackStorm. **Integration breadth needed (20%)**: 50+ required tools favor XSOAR's 1000+ integrations; standard REST APIs favor Tines's HTTP-native model; deep on-premises systems favor Splunk SOAR or StackStorm; a need for quick deployment favors Tines or Torq. **AI maturity requirement (10%)**: a full AI copilot embedded in the SOAR favors Microsoft Sentinel plus Copilot; the strongest threat-intel AI favors Cortex XSIAM or Google SecOps; DIY LLM integration favors Tines's direct API-call model; an on-premises LLM requirement favors StackStorm paired with a self-hosted model.

## Related

- [AI SOC Playbooks Part 04: Identity & Email Attack Playbooks](04-part-04-automation-playbooks.md)
- [AI SOC Playbooks Part 13: AI SOC Vendor Landscape](12-part-13-vendor-landscape.md)
- [AI SOC Playbooks Part 06: AI Models for SOC](06-part-06-ai-models.md)
