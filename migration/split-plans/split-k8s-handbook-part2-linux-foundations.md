# Split Plan: K8s Handbook Part 2 — Linux Foundations

**Source:** `/workspace/knowledge-docs/docs/cloud-platforms/kubernetes/K8s_Handbook_Part2_Linux_Foundations.md` (~5,658 words body)

**Reason:** Word count exceeds guide doc_type cap (2600 words hard cap)

## Split Boundary

**Part 1 (Main):** `docs/platforms/35-k8s-handbook-part2-linux-foundations.md`
- Source: Chapters 1–4 (Why Linux Fundamentals Matter, Processes/Threads/Scheduler, Linux Namespaces, cgroups)
- Content: Linux-to-Kubernetes concept mapping table, CFS scheduler and CPU throttling mechanics, the five Pod-relevant namespaces (PID, network, mount, user), cgroups v1 vs v2, QoS classes and cgroup hierarchy
- Target word count: ~2300 words

**Part 2 (Supplementary):** `docs/platforms/parts/35-k8s-handbook-part2-linux-foundations-part2.md`
- Source: Chapters 5–9 (OverlayFS, Linux Networking Stack, iptables/nftables, eBPF, System Calls & Container Security)
- Content: OverlayFS copy-on-write mechanics, veth pairs/bridges/packet flow (same-node and cross-node), iptables Service DNAT internals, eBPF hook points and Cilium's kube-proxy replacement, seccomp/Linux capabilities
- Target word count: ~2200 words

**Part 3 (Supplementary):** `docs/platforms/parts/35-k8s-handbook-part2-linux-foundations-part3.md`
- Source: Chapters 10–14 (OCI Runtime Spec & runc, Container Runtime Deep Dive, Kubernetes-to-Linux Primitive Mapping, Troubleshooting, Hands-On Exercises)
- Content: full container creation sequence (API server → kubelet → containerd → runc → kernel), CRI runtime comparison table, the definitive Kubernetes-concept-to-Linux-primitive mapping table, diagnostic command reference, common Linux-level Kubernetes issues, 3 hands-on exercises
- Target word count: ~1700 words

## Source-quality notes (converted-pdf artifacts fixed during migration)

This source suffered heavier PDF-extraction corruption than Part 1: multi-line shell/code blocks were flattened into single run-on paragraphs (arrows `→` and inline comments substituting for line breaks), and several ASCII tree/box diagrams were mangled into repeated `I`/`II`/`III` character runs (a stray-bullet-character artifact seen elsewhere in this migration wave) rather than real box-drawing Unicode. Fixed during migration:

- Every flattened shell/command block (CFS mechanism walkthrough, PID/network/mount namespace inspection commands, eBPF program lifecycle, container creation sequence, troubleshooting commands, all 3 exercises) reconstructed into properly line-broken fenced `bash`/`json` blocks.
- Two fenced code blocks that had been split mid-command across a PDF page break (troubleshooting namespace inspection, runc `config.json`) merged back into single blocks.
- ASCII tree diagrams (mount namespace filesystem layout, cgroups filesystem layout for a Pod, veth pair topology, packet flow same-node/cross-node, iptables Service DNAT chain, Cilium vs. traditional packet path) converted to Mermaid `flowchart`/`sequenceDiagram` blocks.
- Two tables split across a PDF page break with duplicated header rows (eBPF use-case table in Ch8, Kubernetes-to-Linux-primitive mapping table in Ch12) merged into single tables.
- The two "Key Insight" / "Warning" `<mark>` callouts converted to blockquotes.

## Navigation

- Each part ends with a pointer to the next part's topic coverage.
- Topic ID: all three parts share the `k8s-handbook-part2-linux-foundations` topic family.
- Part 1 is canonical (`topic_id: k8s-handbook-part2-linux-foundations`).
- Parts 2–3 use `topic_id: k8s-handbook-part2-linux-foundations-part2/3`; both `supersedes: []` (Part 1 carries the supersedes entry).
