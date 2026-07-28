---
title: "AI SOC Playbooks Part 04: Network & Supply Chain Attack Playbooks (Part 3)"
doc_type: guide
domain: trust
status: current
topic_id: part-04-automation-playbooks-part3
last_reviewed: 2026-07-28
maturity: practitioner
supersedes: []
tags: [playbooks, soar, incident-response, c2, lateral-movement, supply-chain]
covers_version: "2026"
---

The final five AI automation playbooks — suspicious PowerShell/LOLBins, C2 beaconing, pass-the-hash/pass-the-ticket lateral movement, DNS tunneling, and supply chain attacks — plus a KPI summary across all 17 playbooks in this series.

## PB-013: Suspicious PowerShell / LOLBins

**Trigger:** PowerShell with `-EncodedCommand` from an unusual parent process, PowerShell with `-ExecutionPolicy Bypass`, a SIEM catching PowerShell downloading from the internet (`IEX(New-Object Net.WebClient).DownloadString`), or LOLBAS activity from `mshta.exe`, `regsvr32.exe`, `certutil.exe`, or `wscript.exe`.

Common living-off-the-land patterns include `Invoke-Expression` (IEX) combined with `DownloadString` for download-and-execute, `[Convert]::FromBase64String` for decode-and-execute, and `Start-Process -WindowStyle Hidden` for stealth execution — alongside LOLBins like `mshta.exe` (executes a remote HTA file), `certutil.exe -decode` (decodes a base64 payload), `regsvr32.exe` with a remote URL (executes a remote script), `wscript.exe`/`cscript.exe` (JS/VBS payloads), `msiexec.exe /quiet` (silent MSI installation), and `rundll32.exe` (DLL export execution). A regex pre-filter screens commands for these patterns before routing to deep AI analysis:

```python
SUSPICIOUS_PATTERNS = [
    r'(?i)iex\s*\(.*downloadstring',              # Download + execute
    r'(?i)-encodedcommand\s+[A-Za-z0-9+/=]{50,}',  # Encoded payload
    r'(?i)-executionpolicy\s+(bypass|unrestricted)',
    r'(?i)\[convert\]::fromb64string',
    r'(?i)invoke-mimikatz',
    r'(?i)net\.webclient',
    r'(?i)system\.reflection\.assembly::load',
]
```

Commands matching a pattern go to deep AI analysis; everything else gets heuristic scoring. MITRE: T1059.001 (PowerShell), T1027 (obfuscated files), T1140 (deobfuscate/decode), T1218 (system binary proxy execution / LOLBins).

## PB-014: Command and Control (C2) Beaconing

**Trigger:** regular periodic connections to an external host, firewall connections to high-entropy (DGA-style) domain names, a high volume of NXDOMAIN responses from a single host, or encrypted traffic with unusual jitter patterns.

The AI analyzes three dimensions of network flows. **Periodicity**: exact-regular intervals (e.g., precisely every 1,200 seconds) suggest low-sophistication C2; jittered intervals (1,200 seconds ± a random 120) suggest more advanced tooling, including Cobalt Strike's default profile; irregular-but-patterned intervals suggest custom C2 or deliberate beacon randomization. **Destination characteristics**: domain age, domain entropy (high entropy suggesting a DGA), IP geolocation and reputation, and hosting-provider type (bulletproof hosting is a red flag). **Traffic characteristics**: small check-in packets with occasional large tasking responses, unusual TLS certificate properties (self-signed, atypical), anomalous HTTP User-Agent strings, and DNS query patterns resolving to the C2 IP. Cobalt Strike's default profile is specifically fingerprintable — a characteristic default User-Agent string, 60-second sleep with zero jitter, and a `/submit.php` default C2 path are all detectable signatures when unmodified. MITRE: T1071.001/.004 (application-layer C2 over HTTP/S or DNS), T1568 (dynamic resolution/DGA), T1573 (encrypted channel).

## PB-015: Lateral Movement — Pass-the-Hash / Pass-the-Ticket

**Trigger:** NTLM authentication without a prior Kerberos TGT request (potential Pass-the-Hash), a Sysmon Event ID 4624 with Logon Type 3 (network) and NTLM logon process from an unexpected source, EDR detecting Mimikatz or similar credential-dumping tools, or a Kerberos TGT presented from a source IP different from where it was issued.

A representative detection query (Microsoft Sentinel KQL) filters `SecurityEvent` for `EventID == 4624`, `LogonType == 3`, `AuthenticationPackageName == "NTLM"`, excluding known-authorized hosts, machine accounts, and domain controllers themselves — surfacing exactly the anomalous network-NTLM-logon pattern Pass-the-Hash produces. Pass-the-Ticket indicators layer on top: a TGT used from a different IP than its issuance IP, a Golden Ticket showing abnormally long validity (over 10 hours), or Overpass-the-Hash where an NTLM hash gets converted into a Kerberos ticket. MITRE: T1550.002 (pass the hash), T1550.003 (pass the ticket), T1558/.001/.002 (steal or forge Kerberos tickets, golden ticket, silver ticket).

## PB-016: DNS Tunneling

**Trigger:** abnormally long DNS query names (subdomains over 50 characters), unusually high query volume from a single host (over 100/minute), queries for many unique subdomains of the same parent domain, or excessive use of TXT/CNAME record types.

Detection characteristics: a legitimate host queries DNS fewer than 10 times per minute, legitimate subdomain labels rarely exceed 30 characters, tunneling traffic shows high subdomain entropy (base64/hex-encoded data), tunneling tools produce an unusually high NXDOMAIN ratio from querying many nonexistent names, and TXT records get abused specifically for data exfiltration. A representative Splunk SPL detection computes subdomain length and entropy per query, filters for length over 60 characters and entropy over 3.5, and flags source IPs generating more than 50 such queries. Known tunneling tools include iodine (IPv4-over-DNS), DNScat2 (DNS-based C2), and various dnscat/dnsgrep-style exfiltration utilities. MITRE: T1071.004 (DNS application-layer protocol), T1048.001 (exfiltration over a non-C2 encrypted protocol), T1132 (data encoding, if the DNS payload is encoded).

## PB-017: Supply Chain Attack Detection

**Trigger:** a dependency check flagging a known-malicious package version in a build, unusual behavior from trusted software following an update, an SBOM scan surfacing a new unknown dependency, or a software update arriving from an unexpected server.

Three well-known patterns illustrate the risk: **SolarWinds (2020)** — trusted software auto-updated with a backdoor (SUNBURST) that activated 14 days after install specifically to evade sandbox analysis, with C2 traffic mimicking legitimate SolarWinds communication. **3CX (2023)** — legitimate VoIP software trojanized via DLL side-loading, phoning home to C2. **PyPI/NPM typosquatting** — a package like `requestss` (a typo of `requests`) containing a credential stealer that runs on `pip install`. Detection strategy spans three layers: build-time controls (dependency pinning with hash verification, SBOM generation compared against a trusted baseline, package signature verification, SLSA-framework build provenance); runtime controls (behavioral baselines for software, allowed-destination network connections, file-system access pattern monitoring — software shouldn't touch `/etc/passwd` — and child-process creation monitoring, since npm shouldn't spawn PowerShell); and update controls (update-source certificate pinning, timing-anomaly detection for updates arriving outside maintenance windows, and size-anomaly detection for updates several times larger than the previous version). MITRE: T1195/.001/.002 (supply chain compromise, software dependencies, software supply chain), T1072 (software deployment tools, if the update mechanism itself is abused).

## Playbook KPI Summary

Targets across the full 17-playbook catalog (this part plus Parts 1 and 2): Phishing — under 2 min MTTD, under 15 min MTTR, 85% automation, under 5% FP. BEC — under 5 min / under 30 min / 30% / under 8%. Malware — under 3 min / under 20 min / 70% / under 3%. Ransomware — under 60 sec / under 5 min / 95% / under 1%. Password Spray — under 2 min / under 15 min / 80% / under 5%. OAuth Abuse — under 5 min / under 30 min / 60% / under 8%. Impossible Travel — under 2 min / under 20 min / 65% / under 10%. MFA Fatigue — under 60 sec / under 10 min / 85% / under 2%. Insider Threat — under 10 min MTTD, human-led resolution, 0% automation by design. Cloud Exposure — under 5 min / under 15 min / 80% / under 3%. Container Escape — under 2 min / under 20 min / 75% / under 5%. Privilege Escalation — under 3 min / under 20 min / 70% / under 5%. LOLBins — under 2 min / under 15 min / 65% / under 8%. C2 Beaconing — under 10 min / under 30 min / 75% / under 5%. Lateral Movement — under 5 min / under 30 min / 70% / under 5%. DNS Tunneling — under 10 min / under 30 min / 60% / under 10%. Supply Chain — under 15 min MTTD, human-led resolution, 20% automation, under 5% FP.

The pattern across all 17 is consistent with the operating-model principles from Part 01: automation rate and false-positive tolerance both track how reversible and well-understood the threat class is — ransomware and MFA fatigue earn the highest automation because delay is catastrophic and the trigger patterns are extremely low-noise, while insider threat and supply chain stay human-led because the actions involved (against employees, against build infrastructure) carry consequences no confidence score should authorize autonomously.

## Related

- [AI SOC Playbooks Part 04: Identity, Insider & Cloud Attack Playbooks (Part 2)](04-part-04-automation-playbooks-part2.md)
- [AI SOC Playbooks Part 01: SOC Operating Model & Maturity](../01-part-01-soc-operating-model.md)
- [AI SOC Playbooks Part 05: SOAR Platform Comparison](../05-part-05-soar-platforms.md)
