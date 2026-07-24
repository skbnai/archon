---
title: "enterprise-agent-reference-architectures"
date_created: 2026-07-24
status: current
doc_type: reference-architecture
domain: architecture
topic_id: enterprise-agent-reference-architectures
last_reviewed: 2026-07-24
---

# enterprise-agent-reference-architectures

[Content from enterprise architecture domain]

```mermaid
graph TD
    A[Client] --> B(API Gateway);
    B --> C{Service};
    C --> D[Data Store];
```
