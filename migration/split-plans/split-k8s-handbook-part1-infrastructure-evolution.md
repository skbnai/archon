# Split Plan: K8s Handbook Part 1 — Infrastructure Evolution

**Source:** `/workspace/knowledge-docs/docs/cloud-platforms/kubernetes/K8s_Handbook_Part1_Infrastructure_Evolution.md` (~6,265 words body)

**Reason:** Word count exceeds guide doc_type cap (2600 words hard cap). Initially planned as a 3-way split, but the rewritten prose (merged split tables, spelled-out callouts) ran ~10-15% longer than the raw source word count, so Chapters 1-4 no longer fit in one part — revised to a 4-way split along the source's own chapter boundaries.

## Split Boundary

**Part 1 (Main):** `docs/platforms/34-k8s-handbook-part1-infrastructure-evolution.md`
- Source: Chapters 1–3 (The Imperative of Modern Infrastructure, Era 1 — Physical Servers, Era 2 — Virtualisation & Hypervisors)
- Content: core problem space, physical-server era anti-patterns, hypervisor architecture and types, key virtualisation technologies
- Actual word count: ~1990 words

**Part 2 (Supplementary):** `docs/platforms/parts/34-k8s-handbook-part1-infrastructure-evolution-part2.md`
- Source: Chapters 4–6 (Era 3 — Cloud Computing, Era 4 — Containers & Docker, Era 5 — Google Borg & Omega)
- Content: cloud service models (IaaS/PaaS/CaaS/FaaS/SaaS), cloud-native principles, managed Kubernetes offerings, container technology lineage, Linux namespaces/cgroups, OCI standards, Borg/Omega architecture and direct design lineage to Kubernetes
- Target word count: ~2400 words

**Part 3 (Supplementary):** `docs/platforms/parts/34-k8s-handbook-part1-infrastructure-evolution-part3.md`
- Source: Chapters 7–9 (Era 6 — Kubernetes, Era 7 — Cloud-Native Architecture, Era 8 — Platform Engineering & IDPs)
- Content: Kubernetes origin story, why Kubernetes won, core design principles, release cadence, 12-factor app mapping to Kubernetes, cloud-native patterns, platform engineering/Backstage/IDP capabilities
- Target word count: ~1700 words

**Part 4 (Supplementary):** `docs/platforms/parts/34-k8s-handbook-part1-infrastructure-evolution-part4.md`
- Source: Chapters 10–12 (Infrastructure Evolution Decision Matrix, Anti-Patterns & Migration Strategies, Hands-On Exercises)
- Content: workload-to-abstraction decision guidance, top infrastructure anti-patterns, 4-phase legacy-to-Kubernetes migration strategy, hands-on exercises
- Target word count: ~950 words

## Source-quality notes (converted-pdf artifacts fixed during migration)

- Several tables were split across a PDF page break with a duplicated header row (Cloud Provider Kubernetes Offerings, Container isolation mechanisms, What Virtualisation Solved vs. What It Left Unsolved, the 12-Factor table) — merged into single tables.
- The Chapter 10 "Infrastructure Evolution Decision Matrix" lost its per-cell rating glyphs (✓/○/— symbols) during PDF extraction, leaving only the `~` ("possible with caveats") marks and blank cells. Rather than fabricate which of the lost symbols corresponded to "Preferred" vs. "Suitable" vs. "Not recommended" per cell, the matrix was reconstructed as a two-column table (Recommendation + caveat notes) that preserves only what the source actually still contains: the prose recommendation and the surviving `~`/"+ Kata" annotations.
- Two ASCII architecture sketches (Physical Server Model, Hypervisor Architecture Type 1/Type 2) converted to Mermaid flowcharts.
- The "Key Insight" `<mark>` callout converted to a blockquote per page-styling conventions.

## Navigation

- Each part ends with a pointer to the next part's topic coverage.
- Topic ID: all four parts share the `k8s-handbook-part1-infrastructure-evolution` topic family.
- Part 1 is canonical (`topic_id: k8s-handbook-part1-infrastructure-evolution`).
- Parts 2–4 use `topic_id: k8s-handbook-part1-infrastructure-evolution-part2/3/4`; all `supersedes: []` (Part 1 carries the supersedes entry).
