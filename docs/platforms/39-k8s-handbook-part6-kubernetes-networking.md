---
title: "K8s Handbook Part 6: Kubernetes Networking"
doc_type: guide
domain: platforms
status: current
topic_id: k8s-handbook-part6-kubernetes-networking
last_reviewed: 2026-07-27
maturity: practitioner
supersedes: [docs/cloud-platforms/kubernetes/K8s_Handbook_Part6_Kubernetes_Networking.md]
tags: [kubernetes, networking, cni, coredns, ingress]
covers_version: "2025-2026 edition"
---

Kubernetes networking is built on a flat, unified IP model. Unlike Docker's default NAT-based networking, Kubernetes requires that every Pod get a unique, routable IP address and that Pods communicate with each other without NAT. This model simplifies application networking dramatically but requires careful infrastructure design.

## Kubernetes Networking Model

### The Four Networking Requirements

1. **Pod-to-Pod (same node)** — Pods on the same node must communicate directly using their Pod IPs without NAT. Implemented via a Linux bridge or eBPF on the node.
2. **Pod-to-Pod (cross-node)** — Pods on different nodes must communicate using their Pod IPs without NAT. Implemented via overlay networks (VXLAN), BGP routing, or eBPF.
3. **Pod-to-Service** — Pods must reach Services by their ClusterIP or DNS name. Implemented via iptables DNAT (kube-proxy) or eBPF (Cilium).
4. **External-to-Service** — external clients must reach Services via NodePort, LoadBalancer, Ingress, or Gateway. Implemented via cloud load balancers and node routing.

### The Pod IP Model

Node IP space and Pod IP space are different and must not overlap:

```
Example cluster network design:
  Node IPs:     192.168.1.0/24  (physical/VM network)
  Pod CIDR:     10.244.0.0/16   (all Pod IPs in cluster)
    Node-01:    10.244.0.0/24   (Pods on node-01)
    Node-02:    10.244.1.0/24   (Pods on node-02)
    Node-03:    10.244.2.0/24   (Pods on node-03)
  Service CIDR: 10.96.0.0/12    (all Service ClusterIPs)
```

> CRITICAL: these CIDRs must not overlap with your physical/VM network, VPN routes (a very common enterprise problem), or on-premises RFC 1918 ranges already in use.

```bash
# Specify at cluster creation (kubeadm)
kubeadm init \
  --pod-network-cidr=10.244.0.0/16 \
  --service-cidr=10.96.0.0/12
# These cannot be changed after cluster creation without a rebuild
```

### Network Plugin Requirements (CNI Contract)

Every CNI plugin must satisfy the Kubernetes network contract:

1. Each Pod gets a unique IP within the cluster.
2. All Pods can communicate with all other Pods without NAT.
3. Agents on a node (kubelet, system daemons) can communicate with all Pods on that node.
4. The Pod IP the container sees is the same IP that others use to reach it.

Beyond these requirements, CNI plugins differ in implementation (iptables vs. eBPF vs. DPDK), performance characteristics, NetworkPolicy support, encryption capabilities (WireGuard, IPsec), multi-cluster support, and observability depth.

## Pod Networking Deep Dive

Understanding exactly what happens at the Linux level when a Pod is created and starts communicating is essential for network troubleshooting, CNI selection, and performance optimisation.

### Pod Network Namespace Setup Sequence

When kubelet creates a Pod, networking is set up in this sequence:

1. containerd creates the pause (infra) container; pause creates a new network namespace (netns). All other containers in the Pod JOIN this netns.
2. containerd calls the CNI plugin's `ADD` command — the CNI receives the container ID, netns path, and Pod name/namespace.
3. The CNI creates a veth pair: `eth0` (inside the Pod netns) `<--->` `veth_xxxx` (host netns).
4. The CNI assigns the Pod IP to `eth0` (`ip addr add 10.244.1.5/32 dev eth0`, via host-local IPAM or a central IPAM pool for Cilium/Calico).
5. The CNI sets up routing — inside the Pod netns: `default via 169.254.1.1 dev eth0` (Calico) or `default via 10.244.1.1 dev eth0` (Flannel bridge); on the host netns: `10.244.1.5 via veth_xxxx` (a direct route to the Pod).
6. The Pod is now reachable at its IP from anywhere in the cluster.

```bash
# Inspect Pod network setup on the node
# Find the Pod PID:
crictl pods --name my-pod -q
crictl inspect POD_ID | python3 -c "import json,sys; print(json.load(sys.stdin)['status']['pid'])"
# Inspect from the host:
nsenter -t POD_PID -n ip addr show
nsenter -t POD_PID -n ip route show
ip link show | grep veth
```

### Packet Flow: Pod-to-Pod Same Node (Bridge CNI)

Pod-A (`10.244.1.5`) to Pod-B (`10.244.1.6`), same node with a Linux bridge:

1. Pod-A sends `src=10.244.1.5, dst=10.244.1.6`.
2. Pod-A's kernel sees the destination is in `10.244.1.0/24` — routed via `eth0` (direct, same subnet); an ARP request resolves Pod-B's veth MAC via the bridge.
3. The packet exits `eth0`, enters the host veth pair, and arrives at the bridge (`cni0`).
4. The bridge performs L2 forwarding to Pod-B's veth by destination MAC.
5. The packet crosses the veth pair and arrives at Pod-B's `eth0`; Pod-B receives it.

Total path: 2 veth crossings plus one bridge L2 lookup — sub-microsecond latency on the same host.

### Packet Flow: Pod-to-Pod Cross-Node (VXLAN)

Pod-A (node-01: `10.244.0.5`) to Pod-B (node-02: `10.244.1.7`):

**VXLAN overlay path** (Flannel/Calico VXLAN mode):

1. Pod-A sends `src=10.244.0.5, dst=10.244.1.7`.
2. Host routing on node-01 sends `10.244.1.0/24` via `flannel.1` (the VXLAN interface, with ARP/FDB entries mapping `10.244.1.7` to node-02's MAC/IP).
3. VXLAN encapsulation wraps the inner packet (`src=10.244.0.5, dst=10.244.1.7`) in an outer UDP packet (`src=node-01:8472, dst=node-02:8472`, `src=192.168.1.10, dst=192.168.1.11`).
4. The physical network delivers the outer UDP packet to node-02.
5. node-02's `flannel.1` decapsulates the VXLAN packet.
6. The inner packet is routed to Pod-B via the local veth.

Overhead: a 50-byte VXLAN header per packet; requires UDP port 8472 open between nodes.

**Direct routing path** (Calico BGP / Cilium native routing):

1. Pod-A sends `src=10.244.0.5, dst=10.244.1.7`.
2. Host routing on node-01 (a BGP-learned route) sends `10.244.1.0/24` via `192.168.1.11` (node-02's IP).
3. The packet is routed directly across the physical network.
4. node-02 receives it and routes to Pod-B via the local veth.

No encapsulation overhead; requires L2 adjacency or a BGP peer.

## CNI Architecture and Plugin Selection

The Container Network Interface (CNI) is a specification and set of libraries for writing plugins that configure network interfaces in Linux containers. When a Pod is created or deleted, kubelet calls the CNI plugin to set up or tear down networking.

```
kubelet
  |
  | executes CNI plugin binary with:
  |   - CNI_COMMAND=ADD|DEL|CHECK
  |   - CNI_CONTAINERID=<id>
  |   - CNI_NETNS=/proc/PID/ns/net
  |   - CNI_IFNAME=eth0
  |   - CNI_ARGS=K8S_POD_NAME=...
  |   + stdin: JSON network config
  v
CNI plugin binary (e.g. /opt/cni/bin/calico)
  -> performs network setup
  -> returns JSON result with assigned IPs
```

```bash
# CNI config location
ls /etc/cni/net.d/
cat /etc/cni/net.d/10-calico.conflist
# CNI binaries
ls /opt/cni/bin/
```

### CNI Plugin Comparison Matrix

| Feature | Calico | Cilium | Flannel | Antrea | WeaveNet |
|---|---|---|---|---|---|
| Data plane | iptables or eBPF | eBPF (primary) | iptables | iptables or OVS | iptables |
| kube-proxy replacement | Yes (eBPF mode) | Yes (KPR mode) | No | Partial | No |
| NetworkPolicy | Full (K8s + custom) | Full (K8s + custom L7) | None | Full | Full |
| FQDN policies | Yes | Yes | No | No | No |
| L7 policy (HTTP) | Via Envoy integration | Native eBPF | No | No | No |
| Encryption | WireGuard, IPsec | WireGuard, IPsec | No | IPsec | Yes |
| Multi-cluster | Calico Federation | Cluster Mesh, Hubble | No | Multi-cluster SVC | No |
| Overlay | VXLAN, IPIP | VXLAN, Geneve | VXLAN | Geneve | VXLAN |
| Direct routing | BGP, cross-subnet | Native routing | No | No | No |
| Observability | Flow logs | Hubble (L7 flows) | Basic | Theia | Basic |
| Scale (nodes) | 5,000+ | 10,000+ | 500 | 1,000+ | 200 |
| Best for | BGP environments, on-prem | Large scale, eBPF, AI | Simple clusters | VMware/OVS | Dev/test |

### CNI Selection Guide for Enterprise

- **Greenfield cloud-native cluster at scale** — Cilium with eBPF kube-proxy replacement: best performance, richest observability via Hubble, native L7 policy, WireGuard encryption.
- **On-premises with BGP infrastructure** — Calico with BGP mode: native routing without overlay, integrates with existing network fabric, mature enterprise support.
- **Simple cluster (dev, edge, small production)** — Flannel for simplicity, or Calico for NetworkPolicy support without complexity.
- **OpenShift / Red Hat environment** — OVN-Kubernetes (default in OpenShift 4.x), or Calico.
- **AI/ML cluster with high network throughput** — Cilium with native routing plus RDMA-capable NICs for GPU-to-GPU communication; consider SR-IOV for network-intensive workloads.

## Calico — Policy-First Networking

Calico (Tigera) is the most widely deployed Kubernetes CNI, particularly in enterprise on-premises environments. It supports multiple data planes (iptables, eBPF, VPP) and offers rich NetworkPolicy with BGP-based routing for zero-overhead direct Pod networking.

### Calico Architecture

Calico's `calico-node` DaemonSet runs on every node with three components: **Felix** programs iptables/eBPF rules, routes, and ARP entries; **BIRD** is the BGP daemon that advertises Pod CIDR routes to peers; **confd** watches etcd/the K8s API and updates BIRD's config. The `calico-kube-controllers` Deployment syncs K8s resources to the Calico datastore; an optional `calico-apiserver` serves Calico-specific CRDs via K8s API aggregation; an optional **Typha** fanout proxy reduces datastore load for clusters of 50+ nodes. Data planes: standard iptables (default, most compatible), eBPF (replaces iptables with eBPF maps for better scale), and VPP (DPDK-based, ultra-high performance, specialist use).

```yaml
# Default BGP configuration (full mesh between nodes)
apiVersion: projectcalico.org/v3
kind: BGPConfiguration
metadata:
  name: default
spec:
  logSeverityScreen: Info
  nodeToNodeMeshEnabled: true  # Full mesh (default, OK up to ~50 nodes)
  asNumber: 64512
---
# For larger clusters: route reflectors
apiVersion: projectcalico.org/v3
kind: BGPPeer
metadata:
  name: bgppeer-rr
spec:
  nodeSelector: has(is-route-reflector)  # Route reflector nodes
  peerIP: 192.168.1.10
  asNumber: 64512
---
# Upstream BGP peer (top-of-rack switch)
apiVersion: projectcalico.org/v3
kind: BGPPeer
metadata:
  name: bgppeer-tor
spec:
  peerIP: 192.168.1.1
  asNumber: 64500
  nodeSelector: all()  # All nodes peer with the ToR switch
```

Calico extends Kubernetes NetworkPolicy with GlobalNetworkPolicy (cluster-scoped) and richer selector syntax:

```yaml
# Calico GlobalNetworkPolicy -- applies across all namespaces
apiVersion: projectcalico.org/v3
kind: GlobalNetworkPolicy
metadata:
  name: deny-egress-to-metadata
spec:
  order: 100
  selector: all()
  types: [Egress]
  egress:
    - action: Deny
      destination:
        nets: [169.254.169.254/32]  # Block cloud metadata endpoint
---
# FQDN-based policy (Calico Enterprise)
apiVersion: projectcalico.org/v3
kind: NetworkPolicy
metadata:
  name: allow-api-egress
  namespace: production
spec:
  selector: app == 'myapp'
  types: [Egress]
  egress:
    - action: Allow
      destination:
        domains: ['api.openai.com', '*.anthropic.com']
```

## Cilium — eBPF-Native Networking

Cilium uses eBPF as its primary data plane, replacing iptables for service routing, network policy enforcement, and load balancing. This enables significantly better performance, richer observability (Hubble), and L7-aware policies at scale. Cilium is the recommended CNI for large-scale enterprise and AI workloads.

### Cilium Architecture

The `cilium` DaemonSet runs on every node: the **Cilium Agent** manages eBPF programs, policies, and endpoints; **eBPF programs** load into the kernel at XDP, TC, and socket hooks; **BPF maps** store endpoint state, policy, conntrack, and load-balancing tables; an optional **Envoy** proxy handles L7 HTTP/gRPC policy and observability. The `cilium-operator` Deployment manages IPAM and KVStore sync. **Hubble** provides observability: `hubble-relay` aggregates flow data from all nodes, and `hubble-ui` is the web interface for flow visualisation. eBPF programs attach at different hook points: XDP (NIC driver level) handles NodePort/LoadBalancer packet processing, Direct Server Return (DSR), and DDoS protection; TC (Traffic Control) handles endpoint-to-endpoint routing, policy enforcement, and connection tracking; socket hooks handle service routing without packet looping and transparent proxy insertion.

Cilium's most significant capability is replacing kube-proxy entirely with eBPF, eliminating iptables from the Service routing path:

```bash
# Install Cilium with full kube-proxy replacement
helm repo add cilium https://helm.cilium.io/
helm install cilium cilium/cilium \
  --namespace kube-system \
  --set kubeProxyReplacement=true \
  --set k8sServiceHost=API_SERVER_IP \
  --set k8sServicePort=6443 \
  --set loadBalancer.mode=dsr \
  --set encryption.enabled=true \
  --set encryption.type=wireguard \
  --set hubble.enabled=true \
  --set hubble.relay.enabled=true \
  --set hubble.ui.enabled=true
# Verify kube-proxy replacement
cilium status | grep KubeProxyReplacement
```

Performance comparison (kube-proxy vs. Cilium eBPF): Service lookup goes from iptables `O(n)` to eBPF `O(1)` — at 10,000 services, iptables adds ~10ms of overhead vs. ~1us for eBPF; conntrack moves from kernel conntrack to custom eBPF conntrack; overall CPU overhead for network processing drops 30-40% at scale.

Hubble provides real-time, L3-L7 network flow visibility across the entire cluster without any application instrumentation:

```bash
# Observe all network flows in real time
hubble observe --follow
# Filter: flows to/from a specific Pod
hubble observe --pod production/api-server-abc
# Filter: only dropped flows (policy violations)
hubble observe --verdict DROPPED
# Filter: HTTP flows with status codes
hubble observe --protocol http --follow
# Service dependency map
hubble observe --output json | \
  jq -r '[.source.namespace,.source.pod_name,.destination.namespace,.destination.pod_name] | @csv'
# Hubble metrics in Prometheus:
#   hubble_flows_processed_total
#   hubble_drop_total (by reason, namespace, direction)
#   hubble_tcp_flags_total
#   hubble_http_requests_total (L7 visibility)
```

Cilium can enforce HTTP/gRPC policy at L7 using its embedded Envoy proxy or eBPF-native HTTP inspection:

```yaml
apiVersion: cilium.io/v2
kind: CiliumNetworkPolicy
metadata:
  name: api-l7-policy
  namespace: production
spec:
  endpointSelector:
    matchLabels: { app: api-server }
  ingress:
    - fromEndpoints:
        - matchLabels: { app: frontend }
      toPorts:
        - ports:
            - port: '8080'
              protocol: TCP
          rules:
            http:
              - method: GET
                path: /api/v1/.*
              - method: POST
                path: /api/v1/inference
                headers:
                  - 'X-API-Key: .*'
```

## Flannel and Other CNIs

Flannel is the simplest widely-used CNI. It provides basic overlay networking without NetworkPolicy support, suitable for development clusters, edge deployments, and simple production environments where Calico or Cilium capabilities are not needed.

### Flannel Backends

| Backend | Mechanism | Performance | Requirements |
|---|---|---|---|
| VXLAN | UDP encapsulation (L2 over L3) | Good; ~10-15% overhead | UDP 8472 between nodes |
| host-gw | Direct routing via host gateway | Best; zero overhead | Requires L2 adjacency (same subnet) |
| WireGuard | Encrypted VXLAN | Good; encryption overhead | WireGuard kernel module |
| UDP (deprecated) | Userspace UDP | Poor; avoid | Legacy only |

### Other Notable CNIs

- **Antrea** — VMware-originated; OVS-based; integrates with NSX; Octant UI.
- **OVN-Kubernetes** — OpenVSwitch + OVN; default in OpenShift; good for VMware environments.
- **Multus** — meta-CNI enabling multiple CNI plugins per Pod; used for SR-IOV plus a primary CNI.
- **Whereabouts** — IPAM plugin for static IP management across clusters.
- **SR-IOV CNI** — hardware NIC virtualisation; near wire-speed networking for AI/HPC workloads.
- **DPDK/VPP** — kernel-bypass networking for extreme throughput (100Gbps+); specialist use.

## Service Networking Internals

Understanding exactly how Service ClusterIPs work at the Linux level is essential for troubleshooting connectivity issues and understanding performance characteristics. The implementation differs significantly between iptables, IPVS, and eBPF modes.

### iptables Service Implementation

iptables chains created by kube-proxy for a Service with 3 endpoints (`my-svc`, ClusterIP `10.96.50.100:80` → Pods `10.244.1.5`, `10.244.2.3`, `10.244.3.9`):

```
PREROUTING -t nat:
  -> KUBE-SERVICES -> match 10.96.50.100:80
    -> KUBE-SVC-XXXXXXXX
      -> 33.3% probability: KUBE-SEP-AAAA (DNAT to 10.244.1.5:8080)
      -> 50.0% probability: KUBE-SEP-BBBB (DNAT to 10.244.2.3:8080)
      -> 100% probability:  KUBE-SEP-CCCC (DNAT to 10.244.3.9:8080)
```

```bash
# View Service iptables rules
iptables -t nat -L KUBE-SERVICES -n | grep my-svc
iptables -t nat -L KUBE-SVC-XXXXXXXX -n
iptables-save -t nat | grep KUBE-SVC
```

Performance implication: an `O(n)` linear scan — 10,000 services means up to 200,000 iptables rules on the packet path; each rule evaluation takes ~1-2 microseconds, so at 10K services this can add 200-400ms of latency, severe for high-rate traffic.

### IPVS Service Implementation

IPVS (IP Virtual Server) uses kernel hash tables for `O(1)` Service lookup. kube-proxy creates virtual server entries in IPVS:

```
TCP 10.96.50.100:80 rr
  -> 10.244.1.5:8080  weight=1
  -> 10.244.2.3:8080  weight=1
  -> 10.244.3.9:8080  weight=1
```

Load balancing algorithms: `rr` round-robin (default), `lc` least connections, `dh` destination hash (session affinity), `sh` source hash (client IP affinity), `sed` shortest expected delay, `nq` never queue.

```yaml
# Enable IPVS mode (kube-proxy config)
mode: ipvs
ipvs:
  scheduler: rr
  strictARP: true  # Required for MetalLB
```

```bash
# Inspect IPVS tables
ipvsadm -Ln | grep -A5 10.96.50.100
```

### Cilium eBPF Service Implementation

Cilium replaces IPVS and iptables with eBPF maps at the socket level:

```
BPF map: SERVICE_MAP
  Key:   (10.96.50.100, port=80, proto=TCP)
  Value: [backend_id_1, backend_id_2, backend_id_3]
BPF map: BACKEND_MAP
  Key:   backend_id_1
  Value: (10.244.1.5, port=8080)
```

Socket-level hook (`BPF_PROG_TYPE_CGROUP_SOCK_ADDR`): when an app calls `connect(10.96.50.100:80)`, the eBPF hook intercepts at socket creation, looks up the service in the BPF map (`O(1)` hash), and rewrites the destination to the backend IP:port. The connection goes directly to the backend Pod IP — no packet encap/decap, no iptables traversal, no conntrack overhead for established connections, `O(1)` lookup regardless of service count, and the source IP is preserved (no SNAT for same-node backends).

```bash
# Inspect Cilium BPF service map
cilium service list
cilium bpf lb list
```

## CoreDNS Advanced Patterns

CoreDNS is the DNS backbone of every Kubernetes cluster. Advanced configurations include forwarding to internal DNS, stub zones for external services, response caching tuning, and External DNS for automatic DNS record management.

External DNS automatically creates DNS records for Services/Ingress — when you create a `type=LoadBalancer` Service with IP `35.1.2.3`, ExternalDNS creates `api.example.com -> 35.1.2.3` in Route53/Cloud DNS:

```bash
# Install External DNS
helm repo add external-dns https://kubernetes-sigs.github.io/external-dns/
helm install external-dns external-dns/external-dns \
  --set provider=aws \
  --set aws.zoneType=public \
  --set txtOwnerId=my-cluster
```

```yaml
# Annotate a Service for DNS record creation
metadata:
  annotations:
    external-dns.alpha.kubernetes.io/hostname: api.example.com
    external-dns.alpha.kubernetes.io/ttl: '60'
```

```
# CoreDNS ConfigMap tuning for large clusters
.:53 {
  errors
  health { lameduck 5s }
  ready
  kubernetes cluster.local in-addr.arpa ip6.arpa {
    pods insecure
    fallthrough in-addr.arpa ip6.arpa
    ttl 30
  }
  cache {
    success 9984 30   # 9984 positive entries, 30s TTL
    denial 9984 5     # 9984 negative entries, 5s TTL
  }
  forward . /etc/resolv.conf {
    prefer_udp
    max_concurrent 1000
  }
  autopath @kubernetes
  prometheus :9153
  reload
  loadbalance
}
```

Rule of thumb: scale CoreDNS at 1 replica per 500 nodes:

```bash
kubectl scale deployment coredns -n kube-system --replicas=4
```

NodeLocal DNSCache runs a local DNS cache as a DaemonSet on each node, reducing CoreDNS load by 80%+ in large clusters:

```bash
kubectl apply -f https://raw.githubusercontent.com/kubernetes/kubernetes/master/cluster/addons/dns/nodelocaldns/nodelocaldns.yaml
```

## Ingress Controllers in Production

An Ingress controller implements the Ingress resource, providing HTTP routing, TLS termination, and load balancing for external traffic entering the cluster. The Ingress resource is controller-agnostic; the controller implements the behaviour.

### Ingress Controller Comparison

| Controller | Proxy | Strengths | Scale | Use Case |
|---|---|---|---|---|
| ingress-nginx | Nginx | Mature, widespread, rich annotations | Large | General purpose production |
| HAProxy Ingress | HAProxy | High performance, fine-grained TCP | Very large | High-traffic, complex routing |
| Traefik | Traefik | Auto-discovery, Let's Encrypt, dashboard | Medium | Dev-friendly, dynamic configs |
| AWS ALB Ingress | AWS ALB | Native AWS integration, WAF, Shield | Very large | AWS-native workloads |
| Istio Gateway | Envoy | Full service mesh, mTLS, telemetry | Large | Service mesh environments |
| Cilium Gateway | eBPF+Envoy | eBPF performance, Gateway API native | Very large | Cilium clusters |
| Kong | Nginx+Kong | API gateway features (auth, rate limit, plugins) | Large | API management |

```bash
# Install ingress-nginx with production settings
helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx
helm install ingress-nginx ingress-nginx/ingress-nginx \
  --namespace ingress-nginx --create-namespace \
  --set controller.replicaCount=3 \
  --set controller.minAvailable=2 \
  --set controller.resources.requests.cpu=100m \
  --set controller.resources.requests.memory=256Mi \
  --set controller.resources.limits.memory=512Mi \
  --set controller.metrics.enabled=true \
  --set controller.podAnnotations.prometheus\.io/scrape=true \
  --set controller.config.use-forwarded-headers=true \
  --set controller.config.compute-full-forwarded-for=true \
  --set controller.config.use-proxy-protocol=false
```

```yaml
# Key ConfigMap settings for production
data:
  keep-alive: '75'
  keep-alive-requests: '100'
  upstream-keepalive-connections: '32'
  proxy-connect-timeout: '5'
  proxy-send-timeout: '60'
  proxy-read-timeout: '60'
  log-format-escape-json: 'true'
  log-format-upstream: '{"time":"$time_iso8601","status":"$status",...}'
```

## Related

- [K8s Handbook Part 6: Kubernetes Networking (Part 2)](parts/39-k8s-handbook-part6-kubernetes-networking-part2.md) — Gateway API, service mesh, traffic patterns, multi-cluster networking, observability, troubleshooting, and exercises
