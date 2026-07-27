# Split Plan: K8s Handbook Part 6 — Kubernetes Networking

**Source:** `/workspace/knowledge-docs/docs/cloud-platforms/kubernetes/K8s_Handbook_Part6_Kubernetes_Networking.md` (~4,850 words body)

**Reason:** Word count exceeds guide doc_type cap (2600 words hard cap)

## Split Boundary

**Part 1 (Main):** `docs/platforms/39-k8s-handbook-part6-kubernetes-networking.md`
- Source: Chapters 1–9 (Kubernetes Networking Model, Pod Networking Deep Dive, CNI Architecture and Plugin Selection, Calico, Cilium, Flannel and Other CNIs, Service Networking Internals, CoreDNS Advanced Patterns, Ingress Controllers in Production)
- Content: the four networking requirements and Pod IP model, CNI contract, Pod network namespace setup and same-node/cross-node packet flow walkthroughs, the CNI plugin comparison matrix and enterprise selection guide, Calico BGP/GlobalNetworkPolicy, Cilium architecture/kube-proxy replacement/Hubble/L7 policy, Flannel backends and other notable CNIs, iptables/IPVS/eBPF Service implementation internals, CoreDNS tuning and ExternalDNS, the Ingress controller comparison matrix and ingress-nginx production config

**Part 2 (Supplementary):** `docs/platforms/parts/39-k8s-handbook-part6-kubernetes-networking-part2.md`
- Source: Chapters 10–17 (Gateway API Advanced Patterns, Service Mesh: Istio Deep Dive, Linkerd and Ambient Mesh, East-West/North-South Traffic Patterns, Multi-Cluster Networking, Network Observability, Network Troubleshooting Playbook, Hands-On Exercises)
- Content: Gateway API resource hierarchy and role split, an AI-serving canary HTTPRoute, Istio architecture and traffic management, Linkerd and Istio Ambient Mesh, east-west/north-south traffic classification and egress control, multi-cluster approaches and Cilium Cluster Mesh, the observability stack by CNI and key network metrics, a troubleshooting playbook for three common failure modes, 2 hands-on exercises

## Source-quality notes (converted-pdf artifacts fixed during migration)

- Numerous flattened multi-line YAML/shell/config blocks reconstructed into properly line-broken fenced blocks (Pod IP CIDR config, CNI plugin execution flow, Calico BGP/GlobalNetworkPolicy, Cilium install/L7 policy, iptables/IPVS/eBPF Service internals, CoreDNS ConfigMap tuning, ingress-nginx Helm values, Gateway API resource hierarchy, Istio architecture/VirtualService, Cilium Cluster Mesh, troubleshooting commands, both exercises).
- The CNI plugin comparison matrix (Chapter 3) was split across a PDF page break with a duplicated header row — merged into a single table.
- No content-loss (heading-then-nothing) artifacts were found in this source; all chapters retained their body text.
- Exercise 6.2's closing lines were garbled by the PDF conversion (a `kubectl apply -f - <<EOF` heredoc for the default-deny NetworkPolicy collapsed into a stray `<backend:` fragment followed by a parenthetical). Rewritten as a plain instruction to apply the same `default-deny-all.yaml` NetworkPolicy introduced earlier in this handbook (Part 5), verify the block, then apply an allow rule and verify recovery — no new commands invented beyond what the source's own narrative describes.

## Navigation

- Part 1 ends with a pointer to Part 2 (Gateway API, service mesh, traffic patterns, multi-cluster, observability, troubleshooting, exercises).
- Topic ID: both parts share the `k8s-handbook-part6-kubernetes-networking` topic family.
- Part 1 is canonical (`topic_id: k8s-handbook-part6-kubernetes-networking`).
- Part 2 uses `topic_id: k8s-handbook-part6-kubernetes-networking-part2`, `supersedes: []` (Part 1 carries the supersedes entry).
