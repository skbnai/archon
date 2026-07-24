---
title: "DPDP Act 2023 & DPDP Rules 2025 (Part 2 of 3): Data Discovery, DLP, Breach Notification, DPO & Penalties"
date_created: 2026-07-23
last_reviewed: 2026-07-24
status: current
doc_type: guide
domain: architecture
topic_id: dpdp-act-2023-comprehensive-guide-part2
supersedes: []
tags: [compliance, data-privacy, india, governance, dpdp, breach-notification, penalties]
covers_version: "DPDP Act 2023 + DPDP Rules 2025 (as of Gazette notification G.S.R. 846(E), 13 Nov 2025)"
sources:
  - url: https://www.dpdpa.com/dpdpa2023/chapter-8/section33.html
    title: "DPDP Act 2023, Section 33 & Schedule — penalty table"
    tier: 3
    retrieved: 2026-07-24
  - url: https://www.cybernx.com/data-breach-notification-under-dpdpa/
    title: "Data Breach Notification under DPDPA — Rule 7 Guide"
    tier: 3
    retrieved: 2026-07-24
  - url: https://www.dpdpa.com/dpdparules/rule7.html
    title: "DPDP Rules 2025, Rule 7 — breach notification requirements"
    tier: 3
    retrieved: 2026-07-24
  - url: https://www.dpdpa.com/dpdparules/rule14.html
    title: "DPDP Rules 2025, Rule 14 — Data Principal rights request timelines"
    tier: 3
    retrieved: 2026-07-24
  - url: https://www.india-briefing.com/news/india-dpdp-compliance-timeline-enforcement-2026-27-44740.html/
    title: "India's DPDP Timeline: Critical Compliance Deadlines for 2026-27"
    tier: 3
    retrieved: 2026-07-24
grounding_note: "Penalty amounts confirmed across multiple independent legal-press sources (converging on the same six-tier schedule). Breach-notification timeline corrected: secondary sources describe Rule 7 as requiring the Data Fiduciary to notify the Board 'without delay' with a detailed follow-up report within 72 hours, and to notify affected Data Principals 'without delay' — not a flat 'discovery+72h' step for Data Principals as the original draft implied. Full Gazette/Rules primary text not directly fetched this pass."
---

**Navigation**: Read [Part 1: Executive Summary, Framework & Principles](pathname:///archon/architecture/79-dpdp-act-2023-comprehensive-guide) first. After this part, continue with [Part 3: Anti-Patterns, GDPR Comparison, Technology Architecture & Compliance Checklist](pathname:///archon/architecture/parts/32-dpdp-act-2023-comprehensive-guide-part3).

# DPDP Act 2023 & DPDP Rules 2025 (Part 2 of 3): Data Discovery, DLP, Breach Notification, DPO & Penalties

## 9. Data Discovery & Classification — Best Practices

You cannot protect what you cannot find. Data Discovery is universally cited by KPMG, EY, Deloitte, and MeitY as the **foundational first step** in DPDP compliance. The objective is a complete, living map of all personal data across your organization.

### Discovery Scope — Where to Look

- **Databases & Data Warehouses**: SQL/NoSQL databases, data lakes, analytics warehouses—profile for PII fields
- **SaaS Applications**: CRM (Salesforce), HRMS (Workday, SAP), ERP, Marketing Automation—often largest uncontrolled stores
- **Cloud Storage**: AWS S3, Azure Blob, GCP Storage—unstructured data with embedded PII in documents, logs
- **Endpoints & Devices**: Employee laptops, mobile devices—local copies of personal data
- **APIs & Microservices**: Data flows between services; often undocumented PII transit paths
- **AI/ML Systems**: Training datasets, model inputs, inference logs—frequently overlooked PII exposure
- **Email & Collaboration**: Outlook, Gmail, Slack, Teams—contracts, employee data, customer PII in unstructured form
- **Backup & Archive**: DR replicas, tape archives—often exempt from deletion workflows incorrectly

### Record of Processing Activities (RoPA) — Mandatory Foundation

Following discovery, organizations must build and maintain a **RoPA** (Record of Processing Activities) documenting:

- Data categories processed
- Purpose of processing
- Lawful basis (consent or legitimate use)
- Retention periods
- Recipients / processors with access
- Cross-border transfer status
- Security measures applied
- Last review date

**Tool Recommendation**: Automated data discovery platforms (e.g., Varonis, Securiti.ai, BigID, OneTrust) can reduce discovery timelines from months to weeks. For API-centric architectures, runtime visibility tools (e.g., Levo.ai) identify data flows that static scanning misses.

## 10. Data Protection & DLP Controls

The 'reasonable security safeguards' standard requires a layered defense-in-depth strategy. Leading frameworks converge on the following control domains:

### Technical Controls

- End-to-end encryption (AES-256) for data at rest and TLS 1.3 for data in transit
- Role-based access control (RBAC) + attribute-based access control (ABAC)
- Data Loss Prevention (DLP) tools to detect and block unauthorized exfiltration
- Database Activity Monitoring (DAM) with anomaly detection
- Pseudonymisation and data masking for non-production environments
- Multi-factor authentication for all systems processing personal data

### Organizational Controls

- Formal Data Classification Policy (Public / Internal / Confidential / Restricted)
- Privacy Impact Assessment (PIA) process for new projects touching personal data
- Annual security awareness training for all employees with access to personal data
- Background verification for employees in data-sensitive roles
- Clear desk and clear screen policy for physical security
- Documented Data Retention and Deletion Policy with automated enforcement

### Vendor Controls

- Security questionnaire and due diligence for all Data Processors
- Contractual security requirements aligned to DPDP Rules
- Right-to-audit clauses in all processor agreements
- Regular third-party security assessments (VAPT, SOC 2 reports)

## 11. Breach Notification — Standards & Timelines

**Critical**: ALL personal data breaches must be reported—regardless of severity or whether damage was caused. There is no materiality threshold. Failure to notify the DPBI or affected Data Principals attracts a penalty of up to ₹200 crore.

### Breach Notification Timeline

Per Rule 7 of the DPDP Rules 2025, both the Board and affected Data Principals are notified **without delay** — the 72-hour clock applies specifically to the Data Fiduciary's detailed follow-up report to the Board, not to the initial Data Principal notice:

| **Timeline** | **Action Required** |
|---|---|
| **Immediate** | Contain the breach; activate incident response team; preserve evidence |
| **Discovery, without delay** | Notify the Data Protection Board of India (DPBI) with initial details: nature of breach, categories affected, approximate number of Data Principals affected, likely consequences, remediation measures taken |
| **Discovery, without delay** | Notify all affected Data Principals: nature and extent of breach, timing and location, consequences, mitigating measures, guidance on protective action |
| **Discovery + 72h (or longer if the Board permits)** | Submit a detailed follow-up report to the DPBI: broad facts and causes, mitigation measures taken/proposed, findings on responsible parties, steps to prevent recurrence, summary of Data Principal notifications issued |
| **Post-Breach** | Conduct root cause analysis; implement systemic fixes; update incident response plan |

### Incident Response Program — Best Practice Components

- Documented IR Policy with defined roles (CISO, DPO, Legal, PR, HR, IT)
- Automated breach detection tooling (SIEM, EDR, DLP alerts)
- Pre-approved breach notification templates (DPBI and Data Principal versions)
- Tabletop exercises at least annually—test your 72-hour notification capability
- Forensic investigation retainer with a qualified cybersecurity firm
- Cyber insurance coverage aligned to DPDP penalty exposure

## 12. DPO as a Service & Managed Compliance

For Significant Data Fiduciaries, an India-based Data Protection Officer (DPO) is mandatory. For all other organizations, a DPO or equivalent Privacy Lead is strongly recommended. The miniOrange model of **DPO as a Service** and managed compliance is gaining rapid adoption among mid-market enterprises.

### DPO Responsibilities Under DPDP

- Oversee and coordinate DPDP compliance program across all business functions
- Serve as primary contact for the Data Protection Board of India
- Manage the Data Principal grievance redressal process
- Lead Data Protection Impact Assessments (DPIAs) for high-risk processing
- Monitor regulatory developments and update compliance posture
- Conduct employee training and build privacy-first culture
- Review and approve data processing agreements with third parties
- Prepare and present board-level compliance reports

### DPO as a Service — When to Consider

Organizations that lack the budget or scale for a full-time in-house DPO can leverage managed compliance services from firms such as miniOrange, Infodot Technologies, PwC India, EY India, KPMG India, Deloitte India and others. Key service components include:

- DPDP Gap Assessment—identify exactly where you stand on consent, data flows, retention, vendor exposure
- Consent Management platform deployment and ongoing management
- Data Discovery & Classification—automated scanning of databases, SaaS apps, cloud, and endpoints
- Regulatory coordination and Data Protection Board liaison
- Grievance management and Data Principal rights fulfillment
- Audit readiness and ongoing compliance monitoring
- DPIA and Data Protection Impact Assessment services

## 13. Penalty Structure — Full Schedule

Unlike GDPR's percentage-of-revenue model, DPDP penalties are fixed caps per violation. Penalties are discretionary and proportional—the DPBI considers severity, repetition, mitigation effort, and cooperation before imposing fines.

| **Violation** | **Maximum Penalty** | **Approx. USD** |
|---|---|---|
| Failure to implement reasonable security safeguards—resulting in a breach | ₹250 crore | ~$30 million |
| Failure to notify DPBI or Data Principals of a personal data breach | ₹200 crore | ~$24 million |
| Breach of children's data processing obligations | ₹200 crore | ~$24 million |
| Breach of additional Significant Data Fiduciary obligations | ₹150 crore | ~$18 million |
| Breach of any other provision of the Act or Rules | ₹50 crore | ~$6 million |
| Data Principal violations (false complaints, impersonation, etc.) | ₹10,000 | ~$120 |

**No Cure Period**: Unlike some global regimes, the DPDP Act does not provide a grace window to fix non-compliance before penalties are imposed. Organizations must be fully compliant before May 14, 2027 (18 months after the Rules' Gazette notification). Under Section 29, appeals against a DPBI order go to the TDSAT within 60 days of the order (extendable for sufficient cause), with TDSAT expected to dispose of appeals within 6 months; further appeal lies to the Supreme Court.

## 14. Implementation Roadmap — Phase-by-Phase (2025–2027)

**Industry Standard**: EY, KPMG, and Deloitte all recommend beginning compliance programs immediately. Typical enterprise DPDP programs require 9–12 months. With enforcement in May 2027, organizations starting today have adequate—but not excess—time.

### Phase 1: Foundation (Months 1–3)

- Conduct a comprehensive DPDP Gap Assessment against Act and Rules requirements
- Data mapping: inventory all personal data across cloud, SaaS, on-premises, and endpoints
- Classify data by processing purpose and identify lawful basis (consent vs. legitimate use)
- Conduct a RoPA (Record of Processing Activities) for all processing activities
- Review existing privacy policies, consent mechanisms, and vendor contracts for compliance gaps
- Assess current security controls against 'reasonable safeguards' standard
- Establish a cross-functional DPDP steering committee (Legal, IT, HR, Marketing, Procurement)

### Phase 2: Build (Months 4–8)

- Redesign consent workflows to meet free, specific, informed, unconditional, unambiguous standard
- Deploy consent management platform with audit trails and withdrawal mechanisms
- Draft and publish DPDP-compliant privacy notices in English + required Indian languages
- Implement Data Principal rights management system (access, correction, erasure, nomination)
- Build automated 72-hour breach notification workflow
- Implement Data Retention Policy with automated deletion jobs
- Renegotiate or amend all Data Processor agreements to include DPDP security requirements
- Deploy technical controls: encryption, access controls, DLP, audit logging
- Appoint Grievance Redressal Officer and publish contact details

### Phase 3: Validate (Months 9–12)

- Conduct a full internal or third-party DPDP compliance audit
- Issue retrospective notices for data collected before Rules came into effect
- Run tabletop exercises for incident response and breach notification
- Complete employee privacy training—all staff with data access
- Activate data retention and automated erasure policies
- SDFs: Appoint India-based DPO; initiate first annual DPIA; engage independent auditor
- Register with Consent Manager framework (Phase 2: November 2026)

### Phase 4: Sustain (Ongoing Post-May 2027)

- Maintain continuous compliance monitoring program
- Annual DPIA refresh (SDFs mandatory; all Fiduciaries best practice)
- Quarterly Data Principal rights request review and SLA reporting
- Annual consent audit—verify consent records are valid and current
- Monitor MeitY and DPBI regulatory guidance for updates
- Annual board-level privacy governance review
- Integrate privacy assessment into all new product/system development (Privacy by Design)

---

**Navigation**: Read [Part 1: Executive Summary, Framework & Principles](pathname:///archon/architecture/79-dpdp-act-2023-comprehensive-guide). Continue with [Part 3: Anti-Patterns, GDPR Comparison, Technology Architecture & Compliance Checklist](pathname:///archon/architecture/parts/32-dpdp-act-2023-comprehensive-guide-part3).

**Note**: Regulatory dates, the penalty schedule, and the breach-notification timeline in this 3-part guide were checked against multiple independent legal-press sources plus one primary MeitY document on 2026-07-24 (see frontmatter `sources`). The full Gazette/Rules primary text was not directly fetched this pass, so treat this as tier-2/3-substantiated rather than full tier-1 primary verification.
