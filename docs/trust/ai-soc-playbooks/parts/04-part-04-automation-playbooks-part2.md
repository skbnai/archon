---
title: "AI SOC Playbooks Part 04: Identity, Insider & Cloud Attack Playbooks (Part 2)"
doc_type: guide
domain: trust
status: current
topic_id: part-04-automation-playbooks-part2
last_reviewed: 2026-07-28
maturity: practitioner
supersedes: []
tags: [playbooks, soar, incident-response, insider-threat, cloud-security, kubernetes]
covers_version: "2026"
---

Six more AI automation playbooks: impossible travel, MFA fatigue/push bombing, insider threat data exfiltration, cloud storage public exposure, Kubernetes container escape, and Windows privilege escalation.

## PB-007: Impossible Travel Alert

**Trigger:** identity protection flags the same account authenticating from two geographically distant locations with insufficient travel time between them — for example, a New York login at 09:00 UTC followed by a Moscow login 47 minutes later, 7,500 km away, implying a required travel speed of 9,574 km/h against a fastest-commercial-flight ceiling of roughly 900 km/h.

The AI weighs plausible explanations before treating this as compromise: VPN usage (which can explain the geography gap entirely), known IPv6 geolocation inaccuracy, the user's actual travel history (did they fly the day before), cloud-workload IP confusion with user IP, and known false-positive patterns for this specific user. The workflow geolocates both login IPs and calculates minimum required travel time, checks whether either IP is a VPN/proxy, and enriches with the user's known VPN habits and travel-approval status. Confidence follows from that context: both IPs residential means high-confidence compromise; one IP being a VPN server lowers confidence and redirects to investigating the user's VPN usage; a second IP tracing to a cloud service redirects to false-positive investigation. Response scales with confidence — high confidence revokes sessions and forces MFA re-authentication; medium confidence notifies the user and forces MFA; low confidence just logs and monitors passively.

## PB-008: MFA Fatigue / Push Bombing

**Trigger:** more than 5 MFA push notifications to the same user within 30 minutes, a user reporting unrequested repeated MFA prompts, or repeated authentication attempts with a correct password but pending MFA.

The attack pattern: the attacker already has a valid username and password (from spray, stuffing, or a dark-web leak), sends repeated MFA push notifications to the victim's phone, the victim assumes their phone is malfunctioning and accepts a push just to make it stop, and the attacker gets an authenticated session — this is Lapsus$'s primary initial-access technique from 2022 onward. The response sequence: immediately lock the session in progress and rate-limit authentication to one attempt per 10 minutes (HOOL); simultaneously SMS the user's registered phone — "SECURITY ALERT: Someone is trying to access your account. DO NOT approve any authentication requests. Call IT Security: [number]"; treat the very fact that MFA pushes are firing as evidence the password is already compromised and begin credential-reset procedures; investigate the login attempts' origin and target service, and check whether the user's password appears in breach databases; and, after HITL approval, force a password reset, re-enroll MFA using phishing-resistant FIDO2 where available, and check for damage if any push was mistakenly accepted. MITRE: T1621 (MFA request generation), T1078 (valid accounts — the password is already known), T1110.004 (credential stuffing, the likely initial vector).

## PB-009: Insider Threat — Data Exfiltration

**Trigger:** a DLP alert on a large upload to personal cloud storage, UEBA flagging data-access volume at 10x baseline, an HR flag (performance improvement plan, resignation notice), mass email of sensitive files to a personal address, or a large file copy to removable media.

Insider threat requires the most careful handling in the entire playbook catalog. Scope assessment covers how much data moved (size × sensitivity × destination), what kind (IP, customer PII, financial, strategic), and where it went (personal email, USB, cloud, a competitor's domain). Intent determination is harder and more consequential: is there a legitimate business reason (authorized remote work), a recent HR trigger (termination notice, denied promotion), or a genuine behavioral anomaly (unusual hours, after-hours access) — and context matters, including whether HR already has flags on this employee, whether they've accessed data relevant to a competitor, and whether this is a single event or a days/weeks pattern.

This is the one playbook where the AI **never** autonomously takes action against an employee. Every finding routes immediately, without exception, to a Human Investigator plus Legal Counsel plus HR — the AI produces only an initial assessment, then escalates to the SOC Manager, HR Business Partner, Legal Counsel, and (for high-value data) the CISO, at which point a human-led investigation begins with the AI providing investigation support only, every action requiring Legal-plus-HR approval, and chain of custody rigorously maintained throughout. Legal considerations are load-bearing here: disabling employee access requires Legal confirmation it's appropriate in the relevant jurisdiction; evidence collection follows legal-hold procedures; data is preserved, not deleted, even if it was the exfiltrated data itself, because it's needed as evidence; and any law-enforcement engagement is a CISO-plus-Legal decision, never an autonomous SOC action.

## PB-010: Cloud Storage Bucket Public Exposure

**Trigger:** a CSPM alert on an S3/Azure Blob/GCS bucket changing to public, a CNAPP tool (Wiz, Prisma, Defender) discovering public storage, or a SIEM catching a `PutBucketAcl` call with an `AllUsers` principal.

Severity determination samples the first ~100 bucket objects to classify content (customer PII, credentials, code, backups, or genuinely public-safe content like static website assets), checks audit logs for exactly when exposure started and whether external IPs accessed it during the window, and investigates whether the exposure was intentional — was the bucket meant to be public (website hosting), who made the change, and was there an approved change-management ticket. Even brief exposure matters, since breach-intelligence firms index public buckets quickly. Immediate remediation, HOTL if PII or credentials are detected, restricts the bucket to private, removes public IAM policies, enables versioning if not already on, and enables access logging. Exposure assessment then determines what data was present, whether credentials were exposed, whether PII was exposed (triggering the regulatory notification process), and the exposure's total duration; access-log analysis identifies who accessed the bucket while public and checks for systematic scraper-pattern enumeration. Notification is Legal-driven: a Data Protection Officer is notified immediately for PII exposure, EU residents start the GDPR Article 33 72-hour notification clock, US state breach-notification laws (California, New York, etc.) apply as relevant, and cyber insurance is notified per policy terms. MITRE: T1530 (data from cloud storage, if accessed), T1078.004 (valid accounts: cloud accounts, if credentials were in the bucket).

## PB-011: Kubernetes Container Escape

**Trigger:** a Falco alert on a container attempting to read the host filesystem, a Kubernetes audit-log exec into a pod with a privileged security context, a network-policy violation reaching the node metadata service (169.254.169.254), or `nsenter`/`chroot` commands originating from container context.

Six escape techniques and their detection signals: a **privileged container** (`privileged: true` in the pod spec) is caught at pod-creation audit; a **hostPath mount** of `/` or `/etc` is caught as a PodSecurityPolicy violation; a **Docker socket mount** (`/var/run/docker.sock` inside the container) is caught via volume analysis; a **kernel exploit** attempt is caught as an abnormal syscall pattern via Falco; **nsenter to host** is caught by Falco plus process audit correlation; and **metadata API abuse** (HTTP to 169.254.169.254 from a pod) is caught via network flow analysis. MITRE ATT&CK for Containers: T1611 (escape to host), T1613 (container and resource discovery), T1552.005 (unsecured credentials via the cloud instance metadata API), T1610 (deploy container).

## PB-012: Windows Privilege Escalation

**Trigger:** an EDR alert on a process holding SYSTEM/Administrator tokens it shouldn't have, a SIEM catching `SeImpersonatePrivilege` token-impersonation events, a scheduled task created by a non-admin user with SYSTEM execution context, or EDR-detected DLL side-loading into a privileged process.

AI evaluates the specific escalation technique (token impersonation via tools like PrintSpoofer or RoguePotato, service misconfiguration exploitation, unquoted service paths, DLL hijacking, or UAC bypass), the severity of the achieved privilege level (SYSTEM versus local admin versus network admin) and what ran afterward in the process tree, and — critically — predicts the next step, since privilege escalation is rarely the end goal: the AI actively looks for follow-on lateral movement, persistence installation, or data access already in progress rather than treating the escalation event as the end of the investigation. MITRE: T1548 (abuse elevation control mechanism), T1134/T1134.001 (token impersonation/manipulation), T1053.005 (scheduled task), T1574.001/.009 (DLL search-order hijacking, unquoted service path).

## Related

- [AI SOC Playbooks Part 04: Identity & Email Attack Playbooks (Part 1)](../04-part-04-automation-playbooks.md)
- [AI SOC Playbooks Part 04: Network & Supply Chain Attack Playbooks (Part 3)](04-part-04-automation-playbooks-part3.md) — LOLBins, C2 beaconing, lateral movement, DNS tunneling, supply chain, KPI summary
- [AI SOC Playbooks Part 05: SOAR Platform Comparison](../05-part-05-soar-platforms.md)
