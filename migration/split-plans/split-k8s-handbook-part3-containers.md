# Split Plan: K8s Handbook Part 3 — Containers

**Source:** `/workspace/knowledge-docs/docs/cloud-platforms/kubernetes/K8s_Handbook_Part3_Containers.md` (~5,736 words body)

**Reason:** Word count exceeds guide doc_type cap (2600 words hard cap)

## Split Boundary

**Part 1 (Main):** `docs/platforms/36-k8s-handbook-part3-containers.md`
- Source: Chapters 1–4 (Container Technology Overview, Docker Architecture Deep Dive, OCI Image and Runtime Specifications, Container Runtimes)
- Content: full container stack architecture, Docker's decomposition into containerd/runc and the dockershim removal, BuildKit features, OCI image/manifest/config structure and content addressing, the OCI Distribution Spec registry API, containerd/CRI-O/gVisor/Kata architecture and trade-offs, runtime selection decision matrix
- Target word count: ~2000 words

**Part 2 (Supplementary):** `docs/platforms/parts/36-k8s-handbook-part3-containers-part2.md`
- Source: Chapters 5–9 (Image Building, Container Registry Architecture, Image Optimisation Strategies, Secure Software Supply Chain, Image Signing)
- Content: multi-stage/distroless/scratch build patterns, distroless image reference, alternative build tools (ko, Jib, Buildpacks, Bazel, Nix), enterprise registry architectures and lifecycle policies, layer cache/image-size optimisation, the supply-chain threat model and defence-in-depth layers, Sigstore (Cosign/Fulcio/Rekor) keyless signing workflow
- Target word count: ~1950 words

**Part 3 (Supplementary):** `docs/platforms/parts/36-k8s-handbook-part3-containers-part3.md`
- Source: Chapters 10–15 (SBOM Generation, SLSA Framework, Vulnerability Scanning, Runtime Container Security, Container Anti-Patterns, Hands-On Exercises)
- Content: SBOM formats/regulatory drivers/generation and attestation, the SLSA maturity levels and Tekton Chains provenance, multi-stage vulnerability scanning architecture and SLA policy, Falco/Tetragon runtime detection and enforcement, 7 container anti-patterns with remediation, 3 hands-on exercises
- Target word count: ~2150 words

## Source-quality notes (converted-pdf artifacts fixed during migration)

- Numerous multi-line shell/Dockerfile/YAML/JSON blocks were flattened into run-on paragraphs during PDF extraction (containerd config.toml, OCI image manifest/config JSON, Cosign keyless signing workflow, Kyverno ClusterPolicy definitions, SLSA provenance JSON, Falco/Tetragon policy YAML, all 3 hands-on exercises) — every one reconstructed into properly line-broken fenced blocks.
- Several blocks were also split mid-command across a PDF page break (containerd config.toml, SBOM generation commands, Exercise 3.1/3.2/3.3 commands) and were merged back into single blocks.
- Three ASCII architecture diagrams (Container Stack Architecture, Docker pre/post-decomposition + Kubernetes path, containerd internal architecture, gVisor architecture, Kata Containers architecture) converted to Mermaid flowcharts.
- Tables split across a PDF page break with duplicated header rows (BuildKit features, CRI-O vs containerd, Runtime Selection Decision Matrix, Distroless Images Reference, Supply Chain Defence in Depth, SBOM Formats, Vulnerability Management Policy) merged into single tables.
- Two "Key Insight"/"Critical" `<mark>` callouts converted to blockquotes.

## Navigation

- Each part ends with a pointer to the next part's topic coverage.
- Topic ID: all three parts share the `k8s-handbook-part3-containers` topic family.
- Part 1 is canonical (`topic_id: k8s-handbook-part3-containers`).
- Parts 2–3 use `topic_id: k8s-handbook-part3-containers-part2/3`; both `supersedes: []` (Part 1 carries the supersedes entry).
