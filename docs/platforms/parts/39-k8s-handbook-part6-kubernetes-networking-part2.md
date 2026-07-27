---
title: "K8s Handbook Part 6: Kubernetes Networking (Part 2)"
doc_type: guide
domain: platforms
status: current
topic_id: k8s-handbook-part6-kubernetes-networking-part2
last_reviewed: 2026-07-27
maturity: practitioner
supersedes: []
tags: [kubernetes, networking, service-mesh, gateway-api, observability]
covers_version: "2025-2026 edition"
---

> Continues from [K8s Handbook Part 6: Kubernetes Networking](../39-k8s-handbook-part6-kubernetes-networking.md), covering Chapters 10-17: Gateway API advanced patterns, service mesh, traffic patterns, multi-cluster networking, observability, troubleshooting, and hands-on exercises.

## Gateway API — Advanced Patterns

Gateway API is the next-generation Kubernetes networking API, graduating to stable (v1) in Kubernetes 1.28. It addresses the limitations of Ingress: role-based management, richer routing semantics, protocol support beyond HTTP, and extensibility.

### Gateway API Resource Hierarchy

Gateway API splits configuration across three roles:

```yaml
# ROLE: Infrastructure Provider (cloud team)
# GatewayClass -- defines the type of Gateway (which controller implements it)
apiVersion: gateway.networking.k8s.io/v1
kind: GatewayClass
metadata: { name: cilium }
spec:
  controllerName: io.cilium/gateway-controller
---
# ROLE: Cluster Operator (platform team)
# Gateway -- deploys a load balancer + listener configuration
apiVersion: gateway.networking.k8s.io/v1
kind: Gateway
metadata: { name: prod-gateway, namespace: infra }
spec:
  gatewayClassName: cilium
  listeners:
    - name: https
      port: 443
      protocol: HTTPS
      tls: { certificateRefs: [{ name: wildcard-cert }] }
  allowedRoutes: { namespaces: { from: Selector } }
---
# ROLE: Application Developer (app team)
# HTTPRoute -- defines routing rules for their application
apiVersion: gateway.networking.k8s.io/v1
kind: HTTPRoute
metadata: { name: api-routes, namespace: production }
spec:
  parentRefs: [{ name: prod-gateway, namespace: infra }]
  hostnames: [api.example.com]
  rules:
    - matches: [{ path: { type: PathPrefix, value: /api } }]
      backendRefs:
        - name: api-service
          port: 80
          weight: 90
        - name: api-canary
          port: 80
          weight: 10
```

Gateway API with traffic splitting is ideal for LLM inference canary deployments:

```yaml
# Canary deployment: route 5% of requests to a new LLM version
apiVersion: gateway.networking.k8s.io/v1
kind: HTTPRoute
metadata:
  name: llm-api-routing
  namespace: ai-serving
spec:
  parentRefs: [{ name: ai-gateway }]
  hostnames: [llm.internal.corp]
  rules:
    # Header-based routing for testing
    - matches:
        - headers:
            - name: X-Model-Version
              value: v2
      backendRefs: [{ name: llm-v2, port: 80 }]
    # Weighted split for canary
    - backendRefs:
        - name: llm-v1
          port: 80
          weight: 95
        - name: llm-v2
          port: 80
          weight: 5
      filters:
        - type: ResponseHeaderModifier
          responseHeaderModifier:
            add:
              - name: X-Served-By
                value: llm-gateway
```

## Service Mesh: Istio Deep Dive

A service mesh adds a transparent infrastructure layer for service-to-service communication, providing mutual TLS (mTLS) for encryption and authentication, observability (traces, metrics, logs), traffic management (retries, timeouts, circuit breaking, canary deployments), and policy enforcement — all without changing application code.

### Istio Architecture

**Control plane (`istiod`):** Pilot handles service discovery and pushes xDS config to proxies; Citadel is the certificate authority issuing workload certificates (SPIFFE); Galley handles configuration validation and distribution.

**Data plane:** one Envoy sidecar proxy per Pod, injected automatically. All inbound/outbound traffic is intercepted via iptables rules:

```bash
# Traffic interception (per Pod)
iptables -t nat -A PREROUTING -p tcp -j ISTIO_INBOUND
iptables -t nat -A OUTPUT -p tcp -j ISTIO_OUTPUT
# All TCP traffic redirected to Envoy (port 15001 egress, 15006 ingress)
```

Envoy enforces mTLS, policies, retries, timeouts, and circuit breaking, and exports request metrics and distributed traces (Jaeger/Zipkin). `istiod` pushes configuration to all Envoy proxies via gRPC streaming using the xDS protocol: LDS (Listeners), RDS (Routes), CDS (Clusters), EDS (Endpoints).

### Istio Traffic Management

```yaml
# VirtualService -- traffic routing rules
apiVersion: networking.istio.io/v1
kind: VirtualService
metadata:
  name: api-routing
spec:
  hosts: [api-service]
  http:
    # Header-based routing
    - match:
        - headers: { X-API-Version: { exact: v2 } }
      route:
        - destination: { host: api-service, subset: v2 }
    # Canary with retries
    - route:
        - destination: { host: api-service, subset: v1 }
          weight: 90
        - destination: { host: api-service, subset: v2 }
          weight: 10
      retries:
        attempts: 3
        perTryTimeout: 2s
        retryOn: gateway-error,connect-failure,refused-stream
      timeout: 10s
      fault:
        delay:
          percentage: { value: 0.1 }
          fixedDelay: 5s  # Inject 5s delay to 0.1% of requests (chaos testing)
---
# DestinationRule -- load balancing and connection pool
apiVersion: networking.istio.io/v1
kind: DestinationRule
metadata:
  name: api-destination
spec:
  host: api-service
  trafficPolicy:
    connectionPool:
      tcp: { maxConnections: 100 }
      http: { http2MaxRequests: 1000, pendingRequests: 100 }
    outlierDetection:
      consecutive5xxErrors: 5
      interval: 10s
      baseEjectionTime: 30s
  subsets:
    - name: v1
      labels: { version: v1 }
    - name: v2
      labels: { version: v2 }
```

## Linkerd and Ambient Mesh

### Linkerd — Lightweight Service Mesh

Linkerd focuses on simplicity, performance, and security. Unlike Istio's Envoy-based heavy sidecar, Linkerd uses a micro-proxy written in Rust (`linkerd2-proxy`) that is much smaller and faster:

| Dimension | Istio | Linkerd |
|---|---|---|
| Proxy | Envoy (C++) | linkerd2-proxy (Rust) |
| Proxy memory | 50-200MB per Pod | 10-30MB per Pod |
| Proxy CPU | 50-200m per Pod | 5-30m per Pod |
| Configuration complexity | High (many CRDs) | Low (simple CRDs) |
| L7 protocol | HTTP/1, HTTP/2, gRPC, WebSocket | HTTP/1, HTTP/2, gRPC |
| Traffic management | Very rich (VirtualService, DR) | Basic (HTTPRoute, TrafficSplit) |
| Multi-cluster | Yes (complex) | Yes (simpler) |
| mTLS | Yes (cert-manager or Citadel) | Yes (automatic, cert-manager) |
| Best for | Complex traffic management, full control | Simplicity, low overhead, Rust-safe |

### Istio Ambient Mesh — Sidecar-Free Architecture

Ambient Mesh (Istio 1.21+, stable 2025) eliminates the sidecar model entirely, moving mesh functionality to the node level and a dedicated waypoint proxy layer. This reduces resource overhead dramatically and removes the Pod-restart requirement for mesh adoption.

Ambient Mesh has two layers. **Layer 1 (`ztunnel`)** is a lightweight Rust proxy deployed as a per-node DaemonSet, providing mTLS, L4 telemetry, and L4 policy; every Pod on the node participates automatically with zero sidecars, and traffic is intercepted via eBPF and redirected to `ztunnel`. **Layer 2 (Waypoint Proxy)** is an optional, Envoy-based proxy deployed per namespace/service, needed only for L7 features such as HTTP routing, header manipulation, and L7 policy.

Benefits over the sidecar model: no Pod restart required to join the mesh, ~90% lower memory overhead vs. sidecars, a shared `ztunnel` with no per-Pod proxy overhead, and simpler upgrades (update the `ztunnel` DaemonSet, not every Pod).

```bash
# Enable Ambient Mesh
helm install istio-cni istio/cni -n istio-system --set profile=ambient
helm install ztunnel istio/ztunnel -n istio-system
# Opt a namespace into ambient mesh
kubectl label namespace production istio.io/dataplane-mode=ambient
```

## East-West and North-South Traffic Patterns

### Traffic Flow Classification

| Pattern | Direction | Examples | Primary Controls |
|---|---|---|---|
| North-South (inbound) | Internet → Cluster | User HTTP/HTTPS requests | Ingress, Gateway, LB, WAF |
| North-South (outbound) | Cluster → Internet | API calls to external SaaS | Egress gateway, NetworkPolicy, proxy |
| East-West (in-cluster) | Pod ↔ Pod | Service-to-service, DB calls | Service, NetworkPolicy, mTLS |
| East-West (cross-cluster) | Cluster ↔ Cluster | Multi-region failover | Cluster Mesh, Federation |

### Egress Control Patterns

Controlling outbound traffic from Pods prevents data exfiltration and enforces compliance. Multiple layers provide defence in depth:

- **NetworkPolicy egress rules** — block all egress by default; allow only specific destinations. Kubernetes-native but limited to IP/port (no FQDN).
- **Calico FQDN-based egress** — allow egress to `api.openai.com` without knowing IPs; Calico Enterprise resolves the FQDN to IPs dynamically and enforces accordingly.
- **Cilium FQDN policy** — the same capability, native in open-source Cilium.
- **Istio Egress Gateway** — route all external traffic through a dedicated Egress Gateway Pod, enabling centralised logging, access control, and TLS origination for external calls.
- **HTTP proxy (Squid/Envoy)** — a traditional HTTP CONNECT proxy; some enterprises require all outbound HTTP to traverse a proxy for DLP scanning.

## Multi-Cluster Networking

Multi-cluster networking extends Kubernetes Services and networking across multiple clusters. This is essential for global deployments, disaster recovery, regulatory data locality, and AI platform architectures requiring model serving in multiple regions.

### Multi-Cluster Approaches

| Approach | Mechanism | Latency | Complexity | Best For |
|---|---|---|---|---|
| Cilium Cluster Mesh | Direct Pod-to-Pod routing | Low (direct) | Medium | Same-org, trusted clusters |
| Istio Multi-Cluster | Gateway-based service mirroring | Medium (via GW) | High | Service mesh environments |
| Submariner | IPsec tunnels between clusters | Medium | Medium | Any CNI, on-premises |
| Admiral | Istio service federation | Medium | High | Large Istio deployments |
| DNS-based (external-dns) | DNS round-robin/failover | High (DNS TTL) | Low | Simple failover, CDN |
| Service API (Multi-Cluster SIGs) | Standard API (emerging) | Varies | Low | Future standard |

### Cilium Cluster Mesh

Cilium Cluster Mesh enables transparent cross-cluster service discovery and direct Pod-to-Pod communication between clusters sharing the same Cilium installation:

```bash
# Connect two clusters with Cilium Cluster Mesh
# On cluster-1:
cilium clustermesh enable --service-type LoadBalancer
cilium clustermesh status
# On cluster-2:
cilium clustermesh enable --service-type LoadBalancer
# Connect cluster-2 to cluster-1:
cilium clustermesh connect \
  --context cluster-1 \
  --destination-context cluster-2
# Export a Service from cluster-1 to cluster-2:
kubectl annotate service my-api service.cilium.io/global='true'
# Service is now reachable from cluster-2 as
# 'my-api.namespace.svc.cluster.local' -- traffic distributed across
# endpoints in BOTH clusters.
# Prefer local cluster (failover to remote if local unavailable):
kubectl annotate service my-api \
  service.cilium.io/shared=false service.cilium.io/global=true
```

## Network Observability

Network observability in Kubernetes spans from basic connectivity metrics to full L7 flow visibility. The right observability stack depends on your CNI choice and observability requirements.

### Observability Stack by CNI

| CNI | L3/L4 Flows | L7 Visibility | Tool |
|---|---|---|---|
| Cilium | Native Hubble | Native Hubble (HTTP, gRPC, DNS) | Hubble CLI + UI, Prometheus |
| Calico | Flow logs | Via sidecar (Istio/Linkerd) | Calico flow logs, Kibana |
| Any CNI | Network metrics | Via service mesh | Prometheus + Grafana |
| Any CNI | eBPF tracing | Syscall-level | Pixie, BPFTrace |

### Key Network Metrics to Monitor

- **Pod network throughput** — `container_network_transmit_bytes_total`, `container_network_receive_bytes_total`
- **DNS latency and errors** — `coredns_dns_request_duration_seconds`, `coredns_dns_responses_total`
- **Service latency** — `istio_request_duration_milliseconds` (Istio), `hubble_http_request_duration` (Cilium)
- **Connection errors** — `container_network_transmit_errors_total`, `net_conntrack_entries` (conntrack table)
- **iptables/eBPF drops** — `node_netstat_IpExt_InOctets`, `cilium_drop_count_total`
- **DNS lookup failures** — `coredns_dns_responses_total` where `rcode=SERVFAIL,NXDOMAIN`

## Network Troubleshooting Playbook

### Issue: Pod cannot reach another Pod

```bash
# Step 1: Verify Pod IPs and routing
kubectl get pod -o wide  # Check Pod IPs
nsenter -t POD_PID -n ip route show
# Step 2: Test connectivity from source Pod
kubectl exec -it source-pod -- ping DEST_IP
kubectl exec -it source-pod -- curl -v http://DEST_IP:PORT
# Step 3: Check NetworkPolicy (if any)
kubectl get networkpolicies -A  # Check if policies select source or dest Pod
# Step 4: CNI-specific
# Cilium:
cilium monitor --from-pod source-pod
# Calico:
kubectl logs -n kube-system -l k8s-app=calico-node
```

### Issue: Service not resolving

```bash
# Step 1: Verify DNS configuration
kubectl exec -it test-pod -- cat /etc/resolv.conf
kubectl exec -it test-pod -- nslookup kubernetes.default
# Step 2: Check CoreDNS pods
kubectl get pods -n kube-system -l k8s-app=kube-dns
kubectl logs -n kube-system -l k8s-app=kube-dns
# Step 3: Verify Service and Endpoints
kubectl get svc my-service
kubectl get endpoints my-service  # Empty endpoints = selector matches no Ready Pods
```

### Issue: High network latency

```bash
# Step 1: Baseline with iperf3
kubectl run iperf-server --image=networkstatic/iperf3 -- iperf3 -s
kubectl run iperf-client --image=networkstatic/iperf3 -- iperf3 -c IPERF_SERVER_IP
# Step 2: Check CNI overhead
# VXLAN: measure encap overhead vs direct routing
# iptables: check number of rules
iptables-save | wc -l
# Step 3: Check conntrack table
sysctl net.netfilter.nf_conntrack_count
sysctl net.netfilter.nf_conntrack_max  # If count approaches max: connection tracking exhaustion
```

## Hands-On Exercises

### Exercise 6.1 — Trace End-to-End Packet Flow

Trace every hop of a cross-node request:

```bash
# Deploy two pods on different nodes
kubectl run pod-a --image=nicolaka/netshoot -- sleep 3600
kubectl run pod-b --image=nginx:alpine
# Verify they are on different nodes
kubectl get pods -o wide
# Get Pod-B IP
POD_B_IP=$(kubectl get pod pod-b -o jsonpath='{.status.podIP}')
# From Pod-A, test connectivity
kubectl exec -it pod-a -- curl -v http://$POD_B_IP
# On the Pod-A node: trace routing (shows via flannel.1, a Calico interface, or direct)
ip route get $POD_B_IP
# Capture VXLAN traffic (if overlay), then replay the request and inspect encapsulation
tcpdump -i flannel.1 -n host $POD_B_IP -w /tmp/capture.pcap
```

### Exercise 6.2 — NetworkPolicy Enforcement

Apply default-deny and verify enforcement:

```bash
# Create an isolated namespace
kubectl create namespace netpol-test
# Deploy frontend and backend
kubectl run frontend -n netpol-test --image=nicolaka/netshoot -- sleep 3600
kubectl run backend -n netpol-test --image=nginx:alpine
kubectl expose pod backend -n netpol-test --port=80
# Verify connectivity works before the policy is applied
kubectl exec -n netpol-test frontend -- curl -s http://backend
# Apply default-deny, confirm connectivity now fails, then apply an allow
# policy scoped to frontend -> backend and verify connectivity is restored
kubectl apply -n netpol-test -f default-deny-all.yaml
```

## Related

- [K8s Handbook Part 6: Kubernetes Networking](../39-k8s-handbook-part6-kubernetes-networking.md) — Part 1: Networking Model, Pod Networking, CNI Selection, Calico, Cilium, Flannel, Service Networking Internals, CoreDNS, Ingress
