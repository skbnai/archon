---
title: "K8s Handbook Part 1 (Part 2: Cloud Computing, Containers & the Kubernetes Precursors)"
doc_type: guide
domain: platforms
status: current
topic_id: k8s-handbook-part1-infrastructure-evolution-part2
last_reviewed: 2026-07-27
maturity: practitioner
supersedes: []
tags:
  - kubernetes
  - cloud-computing
  - containers
  - docker
  - google-borg
covers_version: "2025-2026 edition"
---

*Part 2 of 4 of [K8s Handbook Part 1: Infrastructure Evolution](../34-k8s-handbook-part1-infrastructure-evolution.md).*

## Chapter 4: Era 3 — Cloud Computing (2006–Present)

### The Amazon Revolution

Amazon Web Services launched EC2 in August 2006 with a radical proposition: compute as a utility, billed by the hour, available on demand. This was not merely a new way to buy servers — it was a fundamental restructuring of the economics and operational model of infrastructure. The capital expenditure (CapEx) model of buying physical servers was replaced by an operational expenditure (OpEx) model of renting virtual compute on demand.

AWS S3 had launched six months earlier, in March 2006, establishing the principle of infinitely scalable object storage as a service. Together, EC2 and S3 defined the two foundational primitives of cloud computing: compute and storage, both available on demand, both billed on consumption.

### Cloud Service Models

| Model | Abstraction Level | Customer Manages | Provider Manages | Example |
| --- | --- | --- | --- | --- |
| IaaS | Virtual machines | OS, runtime, app, data | Hardware, hypervisor, networking | AWS EC2, Azure VMs, GCP Compute Engine |
| PaaS | Application runtime | App code, data | OS, runtime, scaling, networking | Heroku, Google App Engine, Azure App Service |
| CaaS | Containers | Container images, configs | Orchestration, nodes, networking | GKE, EKS, AKS, GCP Cloud Run |
| FaaS/Serverless | Functions | Function code | Everything else | AWS Lambda, Google Cloud Functions, Azure Functions |
| SaaS | Application features | Data and configuration | Everything | Gmail, Salesforce, Snowflake |

### Cloud-Native Principles Introduced by AWS

- **Elasticity**: Resources scale up and down automatically based on demand — the end of peak-capacity provisioning.
- **Immutability**: Instead of patching running servers, replace them with new images. This principle directly inspired container immutability.
- **Everything as a service**: Storage, databases, queues, load balancers — every infrastructure component available as a managed API.
- **Pay-per-use**: Align cost with actual consumption, enabling fine-grained FinOps optimisation.
- **Global reach**: Deploy workloads in multiple geographic regions with consistent APIs — enabling multi-region Kubernetes clusters.
- **Managed services**: Offload operational burden of common infrastructure components to the cloud provider.

### The Rise of Cloud-Native Architecture

Cloud computing enabled but did not mandate cloud-native architecture. Early cloud adopters simply "lifted and shifted" their monolithic applications to EC2 instances, treating VMs like slightly faster physical servers. The economic benefits were real but the architectural benefits were unrealised.

True cloud-native architecture emerged from companies that built for the cloud from scratch: Amazon itself, Netflix, Google, Twitter. They developed patterns that exploited the cloud's strengths — elasticity, managed services, pay-per-use — and accommodated its weaknesses — instance failures, network partitions, variable latency. These patterns became the 12-Factor App methodology and later the CNCF cloud-native definition.

### What Cloud Computing Did Not Solve

- **Consistency**: EC2 instances still ran full operating systems with all their configuration complexity. "Works on my machine" moved to "works on my AMI".
- **Density**: VM-level granularity meant significant overhead per workload. Running 1000 microservices required 1000 VMs or complex hand-rolled process management.
- **Startup latency**: EC2 instance launch was measured in minutes, not seconds. Auto-scaling was reactive and slow.
- **Portability**: AMIs (Amazon Machine Images) were AWS-specific. Azure VMs used different image formats. Moving workloads between clouds required re-imaging.
- **Orchestration**: Scheduling workloads across multiple instances required custom tooling. AWS Auto Scaling Groups were primitive — no workload awareness, no bin-packing, no affinity rules.
- **Microservices complexity**: As services multiplied, managing their deployment, networking, discovery, and scaling manually became unmanageable.

**The microservices catalyst:** Netflix's 2008–2011 migration from a monolithic DVD-by-mail system to streaming microservices on AWS became the canonical cloud-native case study. By 2011, Netflix ran hundreds of microservices on thousands of EC2 instances; managing their deployment, discovery, load balancing, fault tolerance, and scaling manually was unsustainable. Netflix open-sourced Eureka (service discovery), Hystrix (circuit breaking), and Ribbon (load balancing) — language-specific Java libraries, not a general platform. The industry needed an orchestration substrate. That substrate became Kubernetes.

**Cloud provider Kubernetes offerings:**

| Provider | Managed K8s Service | Launched | Key Differentiators |
| --- | --- | --- | --- |
| Google Cloud | GKE (Google Kubernetes Engine) | 2014 | Autopilot mode, Workload Identity, GKE Enterprise |
| Amazon Web Services | EKS (Elastic Kubernetes Service) | 2018 | Deep AWS integration, EKS Anywhere, Fargate |
| Microsoft Azure | AKS (Azure Kubernetes Service) | 2017 | Azure AD integration, Arc for hybrid, KEDA OSS origin |
| Red Hat / IBM | OpenShift | 2014 | Enterprise support, multi-cloud, developer experience |
| SUSE | Rancher / RKE2 | 2014 | Multi-cluster management, air-gap support |
| VMware / Broadcom | Tanzu | 2019 | vSphere integration, enterprise governance |

## Chapter 5: Era 4 — Containers & Docker (2013–Present)

### The Origins of Container Technology

Containers are not a Docker invention. The underlying Linux kernel technologies that make containers possible — namespaces and cgroups — predate Docker by over a decade. What Docker invented was the developer experience layer that made these kernel primitives accessible and composable:

- **1979** — chroot: UNIX V7 introduced `chroot()`, isolating a process's filesystem view
- **2000** — FreeBSD Jails: Extended chroot to include network, process, and user isolation
- **2004** — Solaris Zones: Oracle's container-like zones with OS-level virtualisation
- **2006** — Linux cgroups: Google engineers Paul Menage and Rohit Seth contributed cgroups to the Linux kernel
- **2008** — LXC: Linux Containers (LXC) combined namespaces and cgroups into the first complete Linux container implementation
- **2013** — Docker 0.1: Docker launched at PyCon, providing a simple CLI and image format on top of LXC (later replaced by libcontainer)
- **2014** — Kubernetes 0.1: Google open-sourced Kubernetes, initially using Docker as its runtime
- **2015** — OCI Founded: Open Container Initiative established to standardise container image and runtime specifications
- **2016** — containerd: Docker donated containerd to CNCF as a standalone container runtime
- **2017** — CRI-O 1.0: Red Hat's lightweight OCI-compliant runtime designed specifically for Kubernetes
- **2020** — Dockershim deprecation: Kubernetes deprecated its Docker-specific shim, moving to CRI
- **2022** — Dockershim removed: Kubernetes 1.24 completed removal of Dockershim

### What a Container Actually Is

A container is a process (or group of processes) running on a Linux host, with its view of the system constrained by kernel namespaces and its resource usage limited by cgroups. There is no hypervisor boundary, no guest kernel, no hardware emulation. The container process uses the host kernel directly.

**Container isolation mechanisms (Linux namespaces):**

| Linux Namespace | What It Isolates | Kubernetes Relevance |
| --- | --- | --- |
| `pid` | Process IDs — container sees only its own processes | Each Pod has isolated PID space; enables `pid=1` in container |
| `net` | Network interfaces, routing tables, iptables rules | Each Pod gets its own network namespace with dedicated IP |
| `mnt` | Filesystem mount points | Container sees only its image layers + mounted volumes |
| `uts` | Hostname and domain name | Container can have its own hostname independent of node |
| `ipc` | System V IPC, POSIX message queues | Containers cannot interfere with each other's IPC unless shared |
| `user` | User and group IDs | Enables rootless containers — container root != host root |
| `cgroup` | cgroup hierarchy view | Prevents container from escaping its resource limits |
| `time` | System clock (Linux 5.6+) | Allows containers to have different time offsets |

**cgroups — resource limits.** Control Groups (cgroups) are the Linux kernel mechanism that limits, accounts for, and isolates the resource usage (CPU, memory, disk I/O, network bandwidth) of process groups. Kubernetes uses cgroups to enforce resource requests and limits in Pod specs. cgroups v2, now default in modern Linux distributions, provides a unified hierarchy and better resource accounting than the v1 subsystem model.

**cgroups resource controllers used by Kubernetes:**

| cgroup Controller | Resource Managed | Kubernetes Usage |
| --- | --- | --- |
| `cpu` | CPU time allocation, CFS bandwidth | Pod CPU requests/limits, CPU throttling |
| `memory` | Memory usage, OOM killing | Pod memory limits, OOM killer threshold |
| `blkio` / `io` | Block I/O bandwidth and IOPS | Storage I/O throttling (limited in practice) |
| `pids` | Number of processes/threads | Prevents fork bombs, PID limits per container |
| `devices` | Device access control | Restricts `/dev` access in containers |
| `hugetlb` | Huge page allocations | Required for high-performance DPDK workloads |
| `rdma` | RDMA/InfiniBand resources | GPU and HPC workloads using RDMA networking |

### Docker's Contribution — The Developer Experience

Docker did not invent container isolation. It invented the developer experience that made container isolation universally accessible. The three innovations that made Docker transformative were:

- **Dockerfile**: A declarative build format — a series of instructions to reproducibly build a container image from a base. Instead of documenting server setup procedures, you encoded them in machine-executable form.
- **Image layering**: Container images are composed of immutable filesystem layers, each representing a Dockerfile instruction. Layers are shared between images, reducing storage and transfer costs. This architecture directly influenced Kubernetes image management.
- **Docker Hub**: A public registry that made sharing and distributing container images trivially easy. The ecosystem of pre-built images (official images for nginx, postgres, redis, python) accelerated adoption by eliminating the need to build from scratch.

### Containers vs. Virtual Machines — Decision Matrix

| Dimension | Virtual Machine | Container | Winner for K8s |
| --- | --- | --- | --- |
| Isolation level | Hypervisor boundary, separate kernel | Kernel namespaces | VM (stronger); Container (practical) |
| Startup time | 30–120 seconds | 10–500 milliseconds | Container |
| Image size | 1–40 GB | 10 MB – 2 GB | Container |
| Resource overhead | 5–15% per VM | 1–3% overhead | Container |
| Density | 10–50 VMs/host | 100–1000 containers/node | Container |
| Portability | Hypervisor-dependent | OCI standard, any runtime | Container |
| Security | Strong isolation | Shared kernel attack surface | VM |
| Use for K8s nodes | Standard deployment model | Nested containers (DinD) | VM |
| Use for K8s workloads | Kata Containers (high security) | Standard workloads | Context-dependent |

### The OCI Standards — Why They Matter to Kubernetes

The Open Container Initiative (OCI), founded in 2015 under the Linux Foundation, standardised two specifications that underpin all modern container ecosystems:

- **OCI Image Specification**: Defines the format for container images — a manifest, a configuration object, and an ordered set of filesystem layers. Any tool that produces an OCI-compliant image can be run by any OCI-compliant runtime.
- **OCI Runtime Specification**: Defines the interface between a container image and a container runtime. Specifies how to unpack an image, configure namespaces and cgroups, and execute the container process. `runc` is the reference implementation.

These standards decoupled container images from any specific runtime. Kubernetes leverages this via the Container Runtime Interface (CRI), letting any CRI-compliant runtime (containerd, CRI-O, gVisor) serve as its container runtime.

## Chapter 6: Era 5 — Google Borg & Omega — The Kubernetes Precursors

### Google's Scale Problem

Google faced a cluster management problem no other organisation had encountered at the same scale. By the mid-2000s, Google ran thousands of servers worldwide hosting a diverse portfolio — the web crawler, the index builder, query serving, Gmail, Maps, YouTube, and hundreds of internal services. Managing these workloads manually was impossible.

Google's answer was Borg — an internal cluster manager that became the blueprint for Kubernetes. The 2015 paper "Large-scale cluster management at Google with Borg" (Verma et al.) revealed for the first time the architecture and lessons of a system that had been running in production for over a decade.

### Borg Architecture

Borg introduced the conceptual framework that Kubernetes directly implements:

- **Borgmaster**: The central controller — equivalent to Kubernetes control plane. A replicated, fault-tolerant master that managed the state of the entire cluster. Five replicas using Paxos consensus. Direct ancestor of Kubernetes API Server + etcd.
- **Borglet**: The node agent — equivalent to Kubernetes kubelet. Ran on every machine, reported to Borgmaster, executed tasks assigned by the scheduler.
- **Jobs and Tasks**: Borg managed "Jobs" containing multiple "Tasks". Kubernetes adopted this as "Deployments" containing "Pods".
- **Allocs**: Resource reservations that could be shared by multiple tasks. Directly inspired Kubernetes Pods — co-located containers sharing resources.
- **Priority and Preemption**: Borg used priorities to allow high-priority production workloads to preempt lower-priority batch jobs. Kubernetes implements this with PriorityClasses and preemption.
- **Cell**: Borg's unit of cluster — a set of machines managed as a unit. Equivalent to a Kubernetes cluster.

### Key Lessons from Borg That Shaped Kubernetes

- **Declarative configuration**: Operators specified what they wanted (desired state), not how to achieve it. Borg's scheduler determined placement. This became Kubernetes' foundational philosophy: `spec.replicas: 3`, not "start three containers".
- **Labels and selectors**: Borg used labels for flexible grouping and selection. Kubernetes adopted this directly — label selectors are the primary mechanism for Services finding Pods, Deployments managing ReplicaSets, etc.
- **No port conflicts**: Borg assigned each task its own IP address within the machine's IP namespace, eliminating port-mapping complexity. Kubernetes adopted this as the "every Pod gets its own IP" requirement in the network model.
- **Resource utilisation insights**: The Borg paper revealed that real-world resource utilisation was dramatically lower than reservations. This motivated Kubernetes request/limit separation — requests for scheduling, limits for enforcement.
- **High availability through replication**: Borg's Borgmaster used Paxos replication for fault tolerance. Kubernetes uses etcd (Raft consensus) for the same purpose.

**Omega — advancing the scheduler.** Omega was Google's research prototype for a next-generation cluster manager, described in the 2013 paper "Omega: flexible, scalable schedulers for large compute clusters." Key Omega innovations that influenced Kubernetes:

- Shared-state scheduling — multiple schedulers operate on a shared, optimistically locked cluster state, enabling parallelism and scheduler specialisation.
- Optimistic concurrency control — schedulers propose placements and resolve conflicts at commit time, rather than holding locks. Kubernetes uses optimistic concurrency in its API (resource versions, conflict detection).
- Gang scheduling concepts — scheduling groups of tasks atomically. Relevant to Kubernetes for distributed training jobs where all workers must start together.

### Borg → Kubernetes: Direct Design Lineage

| Borg Concept | Kubernetes Equivalent | Key Differences |
| --- | --- | --- |
| Borgmaster | API Server + etcd + Controller Manager + Scheduler | Decomposed into separate components for extensibility |
| Borglet | kubelet | CRI abstraction allows pluggable runtimes |
| Job | Deployment / StatefulSet / DaemonSet | Kubernetes has richer workload abstractions |
| Task | Pod (container group) | Pod enables multi-container co-location |
| Alloc | Pod resource specs | Kubernetes adds QoS classes (Guaranteed/Burstable/BestEffort) |
| Cell | Cluster | Kubernetes adds Namespace for multi-tenancy within cluster |
| Borg config language | YAML manifests + Helm + Kustomize | Open, declarative, ecosystem-driven |
| Priority | PriorityClass | Kubernetes adds preemption policies |
| Labels | Labels + Selectors | Extended with Annotations for non-identifying metadata |

## Related

- [Part 1: The Imperative, Physical Servers & Virtualisation](../34-k8s-handbook-part1-infrastructure-evolution.md)
- [Part 3: The Kubernetes Era, Cloud-Native Architecture & Platform Engineering](34-k8s-handbook-part1-infrastructure-evolution-part3.md)
- [Part 4: Decision Matrix, Anti-Patterns & Migration Strategy](34-k8s-handbook-part1-infrastructure-evolution-part4.md)
