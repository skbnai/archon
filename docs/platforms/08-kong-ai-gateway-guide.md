---
title: "Kong AI Gateway — Complete End-to-End Guide"
doc_type: guide
domain: platforms
status: current
topic_id: kong-ai-gateway-guide
last_reviewed: 2026-07-27
maturity: practitioner
supersedes: [docs/cloud-platforms/ai-gateway/kong-ai-gateway-guide.md]
tags: [ai-gateway, kong, kubernetes, auth, observability, cost-management]
covers_version: "N/A"
---

# Kong AI Gateway — Complete End-to-End Guide

Kong AI Gateway is an enterprise-grade API gateway built on top of Kong that sits between your applications and LLM providers (OpenAI, Anthropic, Azure OpenAI, etc.). This comprehensive guide covers architecture, installation, core plugins (caching, rate limiting, guardrails, observability), authentication patterns, multi-model routing, and production deployment on Kubernetes.

---

## Table of Contents

1. [What is Kong AI Gateway?](#1-what-is-kong-ai-gateway)
2. [Architecture Overview](#2-architecture-overview)
3. [Installation & Setup](#3-installation--setup)
4. [Core Concepts](#4-core-concepts)
5. [Connecting AI Providers](#5-connecting-ai-providers)
6. [AI Proxy Plugin (Routing & Load Balancing)](#6-ai-proxy-plugin)
7. [Semantic Caching](#7-semantic-caching)
8. [Rate Limiting for AI](#8-rate-limiting-for-ai)
9. [Prompt Engineering Plugins](#9-prompt-engineering-plugins)
10. [AI Request / Response Transformation](#10-ai-request--response-transformation)
11. [AI Guardrails & Content Safety](#11-ai-guardrails--content-safety)
12. [Observability & Analytics](#12-observability--analytics)
13. [Authentication & Authorization](#13-authentication--authorization)
14. [Multi-Model Routing Strategies](#14-multi-model-routing-strategies)
15. [Cost Management](#15-cost-management)
16. [Streaming Responses](#16-streaming-responses)
17. [Kubernetes Deployment](#17-kubernetes-deployment)
18. [Production Best Practices](#18-production-best-practices)
19. [Troubleshooting](#19-troubleshooting)

---

## 1. What is Kong AI Gateway?

Kong AI Gateway is an **enterprise-grade, open-source AI infrastructure layer** built on top of Kong Gateway. It acts as a unified control plane sitting between your applications and multiple Large Language Model (LLM) providers (OpenAI, Anthropic, Azure OpenAI, Cohere, Mistral, Llama, etc.).

### Key Value Propositions

| Problem | Kong AI Gateway Solution |
| --- | --- |
| Multiple LLM provider SDKs | Single unified API surface |
| No token usage visibility | Built-in token metering & analytics |
| Prompt injection risks | Guardrail plugins |
| High latency repeated queries | Semantic caching |
| Cost unpredictability | Rate limiting per consumer/model |
| No fallback when provider is down | Automatic model failover |

### What Kong AI Gateway is NOT

- It is **not** a fine-tuning platform
- It is **not** a vector database
- It is **not** an LLM itself — it proxies requests to existing LLMs

---

## 2. Architecture Overview

```mermaid
flowchart TB
    Client["Client Application"]
    subgraph GW["Kong AI Gateway"]
        Auth["Auth & AuthZ"]
        RateLimit["Rate Limit (Tokens/$)"]
        Cache["Semantic Cache"]
        PromptInj["Prompt Injection"]
        Guardrails["Guardrails & Safety"]
        Observability["Observability"]
        Router["AI Proxy Router (Multi-model)"]
    end
    OpenAI["OpenAI GPT-4o"]
    Anthropic["Anthropic Claude"]
    Other["Azure / AWS / Cohere / Mistral"]

    Client -->|"HTTP/HTTPS (OpenAI-compatible API)"| GW
    Auth --> Router
    RateLimit --> Router
    Cache --> Router
    PromptInj --> Router
    Guardrails --> Router
    Observability --> Router
    Router --> OpenAI
    Router --> Anthropic
    Router --> Other
```

### Components

- **Kong Gateway (Data Plane):** Handles all traffic proxying, plugin execution, and TLS termination
- **Kong Admin API:** REST API for configuring routes, services, plugins, and consumers
- **Kong Manager (optional):** Web UI for managing configuration
- **AI Plugins:** A suite of plugins that add AI-specific capabilities on top of the standard Kong plugin system

---

## 3. Installation & Setup

### Option A: Docker Compose (Quickstart)

```yaml
# docker-compose.yml
version: "3.8"
services:
  kong-database:
    image: postgres:15
    environment:
      POSTGRES_DB: kong
      POSTGRES_USER: kong
      POSTGRES_PASSWORD: kongpass
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD", "pg_isready", "-U", "kong"]
      interval: 10s
      timeout: 5s
      retries: 5

  kong-migrations:
    image: kong/kong-gateway:3.7
    command: kong migrations bootstrap
    depends_on:
      kong-database:
        condition: service_healthy
    environment:
      KONG_DATABASE: postgres
      KONG_PG_HOST: kong-database
      KONG_PG_USER: kong
      KONG_PG_PASSWORD: kongpass
      KONG_PG_DATABASE: kong

  kong:
    image: kong/kong-gateway:3.7
    depends_on:
      - kong-migrations
    environment:
      KONG_DATABASE: postgres
      KONG_PG_HOST: kong-database
      KONG_PG_USER: kong
      KONG_PG_PASSWORD: kongpass
      KONG_PG_DATABASE: kong
      KONG_PROXY_ACCESS_LOG: /dev/stdout
      KONG_ADMIN_ACCESS_LOG: /dev/stdout
      KONG_PROXY_ERROR_LOG: /dev/stderr
      KONG_ADMIN_ERROR_LOG: /dev/stderr
      KONG_ADMIN_LISTEN: "0.0.0.0:8001"
      KONG_ADMIN_GUI_URL: http://localhost:8002
    ports:
      - "8000:8000"   # Proxy HTTP
      - "8443:8443"   # Proxy HTTPS
      - "8001:8001"   # Admin API HTTP
      - "8444:8444"   # Admin API HTTPS
      - "8002:8002"   # Kong Manager UI
```

```bash
# Start everything
docker compose up -d

# Verify Kong is running
curl http://localhost:8001/status
```

### Option B: Kong Gateway via Helm (Kubernetes)

```bash
helm repo add kong https://charts.konghq.com
helm repo update

helm install kong kong/kong \
  --namespace kong \
  --create-namespace \
  --set env.database=postgres \
  --set postgresql.enabled=true \
  --set ingressController.enabled=true
```

### Option C: DB-less / Declarative Mode

```yaml
# kong.yml (declarative config)
_format_version: "3.0"
_transform: true

services:
  - name: openai-service
    url: https://api.openai.com
    routes:
      - name: chat-route
        paths:
          - /ai/chat
```

```bash
# Run Kong with declarative config
docker run -d \
  -e KONG_DATABASE=off \
  -e KONG_DECLARATIVE_CONFIG=/kong/kong.yml \
  -v $(pwd)/kong.yml:/kong/kong.yml \
  -p 8000:8000 -p 8001:8001 \
  kong/kong-gateway:3.7
```

---

## 4. Core Concepts

Understanding these building blocks is essential before configuring AI features.

### Services

A **Service** represents an upstream API (e.g., OpenAI's API). It defines where to forward requests.

```bash
# Create a service pointing to OpenAI
curl -s -X POST http://localhost:8001/services \
  --json '{
    "name": "openai-chat-service",
    "url": "https://api.openai.com/v1/chat/completions",
    "connect_timeout": 60000,
    "read_timeout": 60000,
    "write_timeout": 60000
  }'
```

### Routes

A **Route** defines how incoming requests are matched and forwarded to a Service.

```bash
curl -s -X POST http://localhost:8001/services/openai-chat-service/routes \
  --json '{
    "name": "chat-route",
    "paths": ["/ai/v1/chat"],
    "methods": ["POST"],
    "strip_path": false
  }'
```

### Plugins

**Plugins** are the core extension mechanism. They execute at various stages of the request lifecycle. AI Gateway ships with a dedicated suite of AI plugins.

```bash
# List all available plugins (including AI plugins)
curl http://localhost:8001/plugins/enabled | jq .enabled_plugins
```

### Consumers

**Consumers** represent users or applications calling your AI APIs. They are used for authentication, rate limiting, and per-consumer analytics.

```bash
curl -X POST http://localhost:8001/consumers \
  --json '{"username": "team-backend", "custom_id": "team-backend-001"}'
```

---

## 5. Connecting AI Providers

### OpenAI

```bash
# Create a Service
curl -X POST http://localhost:8001/services \
  --json '{
    "name": "openai-service",
    "url": "https://api.openai.com"
  }'

# Create a Route
curl -X POST http://localhost:8001/services/openai-service/routes \
  --json '{
    "name": "openai-route",
    "paths": ["/openai"],
    "strip_path": true
  }'

# Apply the AI Proxy plugin with OpenAI config
curl -X POST http://localhost:8001/services/openai-service/plugins \
  --json '{
    "name": "ai-proxy",
    "config": {
      "route_type": "llm/v1/chat",
      "auth": {
        "header_name": "Authorization",
        "header_value": "Bearer sk-YOUR_OPENAI_API_KEY"
      },
      "model": {
        "provider": "openai",
        "name": "gpt-4o",
        "options": {
          "max_tokens": 2048,
          "temperature": 0.7
        }
      }
    }
  }'
```

### Anthropic (Claude)

```bash
curl -X POST http://localhost:8001/services/anthropic-service/plugins \
  --json '{
    "name": "ai-proxy",
    "config": {
      "route_type": "llm/v1/chat",
      "auth": {
        "header_name": "x-api-key",
        "header_value": "sk-ant-YOUR_ANTHROPIC_KEY"
      },
      "model": {
        "provider": "anthropic",
        "name": "claude-3-5-sonnet-20241022",
        "options": {
          "max_tokens": 4096,
          "temperature": 1.0
        }
      }
    }
  }'
```

### Azure OpenAI

```bash
curl -X POST http://localhost:8001/services/azure-openai-service/plugins \
  --json '{
    "name": "ai-proxy",
    "config": {
      "route_type": "llm/v1/chat",
      "auth": {
        "header_name": "api-key",
        "header_value": "YOUR_AZURE_API_KEY"
      },
      "model": {
        "provider": "azure",
        "name": "gpt-4o",
        "options": {
          "azure_instance": "your-azure-instance",
          "azure_deployment_id": "your-deployment-name",
          "azure_api_version": "2024-06-01"
        }
      }
    }
  }'
```

### AWS Bedrock (Claude / Titan)

```bash
curl -X POST http://localhost:8001/services/bedrock-service/plugins \
  --json '{
    "name": "ai-proxy",
    "config": {
      "route_type": "llm/v1/chat",
      "auth": {
        "aws_access_key_id": "AKIAIOSFODNN7EXAMPLE",
        "aws_secret_access_key": "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
      },
      "model": {
        "provider": "bedrock",
        "name": "anthropic.claude-3-5-sonnet-20241022-v2:0",
        "options": {
          "bedrock_region": "us-east-1"
        }
      }
    }
  }'
```

### Cohere

```bash
curl -X POST http://localhost:8001/services/cohere-service/plugins \
  --json '{
    "name": "ai-proxy",
    "config": {
      "route_type": "llm/v1/chat",
      "auth": {
        "header_name": "Authorization",
        "header_value": "Bearer YOUR_COHERE_KEY"
      },
      "model": {
        "provider": "cohere",
        "name": "command-r-plus"
      }
    }
  }'
```

### Self-Hosted / Local Models (Ollama, vLLM)

```bash
curl -X POST http://localhost:8001/services/local-llm-service/plugins \
  --json '{
    "name": "ai-proxy",
    "config": {
      "route_type": "llm/v1/chat",
      "model": {
        "provider": "openai",
        "name": "llama3.2",
        "options": {
          "upstream_url": "http://ollama:11434/v1/chat/completions"
        }
      }
    }
  }'
```

---

## 6. AI Proxy Plugin

The `ai-proxy` plugin is the **centerpiece** of Kong AI Gateway. It translates OpenAI-compatible requests into provider-specific formats.

### How Clients Call the Gateway

Once configured, clients use an OpenAI-compatible interface regardless of the backend model:

```bash
# Client sends a standard OpenAI-format request to Kong
curl -X POST http://localhost:8000/openai/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer consumer-api-key" \
  --json '{
    "messages": [
      {"role": "system", "content": "You are a helpful assistant."},
      {"role": "user", "content": "Summarize the benefits of API gateways."}
    ],
    "max_tokens": 500
  }'
```

### Route Types Supported

| Route Type | Description |
| --- | --- |
| `llm/v1/chat` | Chat completions (multi-turn) |
| `llm/v1/completions` | Text completions |
| `llm/v1/embeddings` | Vector embeddings |

### Full Plugin Configuration Reference

```json
{
  "name": "ai-proxy",
  "config": {
    "route_type": "llm/v1/chat",
    "auth": {
      "header_name": "Authorization",
      "header_value": "Bearer sk-YOUR_KEY",
      "param_name": null,
      "param_value": null,
      "param_location": "header"
    },
    "model": {
      "provider": "openai",
      "name": "gpt-4o",
      "options": {
        "max_tokens": 2048,
        "temperature": 0.7,
        "top_p": 1.0,
        "top_k": 50,
        "stream": false,
        "upstream_url": null,
        "input_cost": 0.0000025,
        "output_cost": 0.00001
      }
    },
    "response_streaming": "allow",
    "logging": {
      "log_statistics": true,
      "log_payloads": false
    }
  }
}
```

---

## 7. Semantic Caching

Semantic caching stores AI responses and returns them for **semantically similar** (not just identical) questions, dramatically reducing cost and latency.

### How It Works

```
Request: "What is machine learning?"
         ↓
[Embed query → compare to cached embeddings]
         ↓
   Similarity > threshold?
   YES → Return cached response (< 5ms, $0 cost)
   NO  → Forward to LLM, cache result
```

### Configuration

```bash
curl -X POST http://localhost:8001/services/openai-service/plugins \
  --json '{
    "name": "ai-semantic-cache",
    "config": {
      "embeddings": {
        "auth": {
          "header_name": "Authorization",
          "header_value": "Bearer sk-YOUR_OPENAI_KEY"
        },
        "model": {
          "provider": "openai",
          "name": "text-embedding-3-small"
        }
      },
      "vectordb": {
        "strategy": "redis",
        "threshold": 0.85,
        "dimensions": 1536,
        "distance_metric": "cosine",
        "redis": {
          "host": "redis",
          "port": 6379
        }
      }
    }
  }'
```

### Threshold Tuning

| Threshold | Behavior |
| --- | --- |
| `0.99` | Only near-identical questions hit cache |
| `0.90` | Moderate similarity — recommended starting point |
| `0.75` | Aggressive caching — may return slightly off-topic answers |

### Testing the Cache

```bash
# First request — cache miss (hits LLM)
time curl -X POST http://localhost:8000/ai/chat \
  --json '{"messages":[{"role":"user","content":"What is machine learning?"}]}'
# Response time: ~1200ms

# Second request — semantically similar
time curl -X POST http://localhost:8000/ai/chat \
  --json '{"messages":[{"role":"user","content":"Can you explain what machine learning is?"}]}'
# Response time: ~8ms  (served from cache!)
```

### Cache Invalidation

```bash
# Flush a specific cache by key pattern
redis-cli -h redis SCAN 0 MATCH "ai-semantic-cache:*" COUNT 1000

# Full cache purge (use with caution in production)
redis-cli -h redis FLUSHDB
```

---

## 8. Rate Limiting for AI

AI APIs are expensive. Kong provides **token-aware** rate limiting — limiting by the number of LLM tokens consumed rather than just request count.

### Token-Based Rate Limiting

```bash
curl -X POST http://localhost:8001/services/openai-service/plugins \
  --json '{
    "name": "ai-rate-limiting-advanced",
    "config": {
      "limit": [1000000],
      "window_size": [3600],
      "window_type": "sliding",
      "sync_rate": -1,
      "strategy": "redis",
      "redis": {
        "host": "redis",
        "port": 6379
      },
      "tokens_count_strategy": "total_tokens",
      "error_code": 429,
      "error_message": "Token quota exceeded. Please try again later."
    }
  }'
```

### Per-Consumer Token Limits

```bash
# Create a consumer
curl -X POST http://localhost:8001/consumers \
  --json '{"username": "premium-user"}'

# Apply a higher limit for premium consumers
curl -X POST http://localhost:8001/consumers/premium-user/plugins \
  --json '{
    "name": "ai-rate-limiting-advanced",
    "config": {
      "limit": [5000000],
      "window_size": [3600],
      "tokens_count_strategy": "total_tokens"
    }
  }'

# Apply a lower limit for free-tier consumers
curl -X POST http://localhost:8001/consumers/free-user/plugins \
  --json '{
    "name": "ai-rate-limiting-advanced",
    "config": {
      "limit": [50000],
      "window_size": [3600],
      "tokens_count_strategy": "total_tokens"
    }
  }'
```

### Rate Limiting by Model Cost

Token pricing varies by model. You can normalize by cost instead of raw token count:

```bash
# Configure cost-per-token in the ai-proxy plugin
curl -X POST http://localhost:8001/services/openai-service/plugins \
  --json '{
    "name": "ai-proxy",
    "config": {
      "model": {
        "provider": "openai",
        "name": "gpt-4o",
        "options": {
          "input_cost": 0.0000025,
          "output_cost": 0.00001
        }
      }
    }
  }'
```

---

## 9. Prompt Engineering Plugins

### AI Prompt Template

Inject standardized, versioned prompt templates so clients don't need to manage complex system prompts.

```bash
curl -X POST http://localhost:8001/services/openai-service/plugins \
  --json '{
    "name": "ai-prompt-template",
    "config": {
      "allow_prompt_in_body": false,
      "templates": [
        {
          "name": "customer-support",
          "template": "You are a helpful customer support agent for Acme Corp. Always be polite, concise, and refer users to support@acme.com if you cannot resolve their issue.\n\nUser query: {{query}}"
        },
        {
          "name": "code-reviewer",
          "template": "You are an expert software engineer. Review the following {{language}} code for bugs, security issues, and best practice violations.\n\nCode:\n```\{\{language}}\n\{\{code}}\n```"
        }
      ]
    }
  }'
```

**Client usage:**

```json
{
  "messages": [{
    "role": "user",
    "content": "{template://customer-support}{\"query\": \"How do I reset my password?\"}"
  }]
}
```

### AI Prompt Decorator

Prepend or append content to every request without the client needing to know.

```bash
curl -X POST http://localhost:8001/services/openai-service/plugins \
  --json '{
    "name": "ai-prompt-decorator",
    "config": {
      "prompts": {
        "prepend": [
          {
            "role": "system",
            "content": "You are a helpful assistant. Always respond in JSON format. Always end your response with a confidence score between 0 and 1."
          }
        ],
        "append": [
          {
            "role": "user",
            "content": "Please keep your response concise and under 200 words."
          }
        ]
      }
    }
  }'
```

---

## 10. AI Request / Response Transformation

### AI Request Transformer

Modify, redact, or enrich request payloads before they reach the LLM.

```bash
curl -X POST http://localhost:8001/services/openai-service/plugins \
  --json '{
    "name": "ai-request-transformer",
    "config": {
      "llm": {
        "route_type": "llm/v1/chat",
        "auth": {
          "header_name": "Authorization",
          "header_value": "Bearer sk-YOUR_KEY"
        },
        "model": {
          "provider": "openai",
          "name": "gpt-4o-mini"
        }
      },
      "prompt": "You are a data redaction assistant. Scan the user message and replace any PII (names, emails, phone numbers, SSNs, credit card numbers) with [REDACTED]. Return only the sanitized message, no explanations.",
      "transformation_extract_pattern": ".*"
    }
  }'
```

### AI Response Transformer

Modify LLM responses before they reach the client — useful for formatting, validation, or enrichment.

```bash
curl -X POST http://localhost:8001/services/openai-service/plugins \
  --json '{
    "name": "ai-response-transformer",
    "config": {
      "llm": {
        "route_type": "llm/v1/chat",
        "auth": {
          "header_name": "Authorization",
          "header_value": "Bearer sk-YOUR_KEY"
        },
        "model": {
          "provider": "openai",
          "name": "gpt-4o-mini"
        }
      },
      "prompt": "You are a JSON formatter. Take the following LLM response and ensure it is valid JSON. If it is not JSON, wrap it in a JSON object with a single key called \"message\". Return only the JSON."
    }
  }'
```

---

## 11. AI Guardrails & Content Safety

### AI Prompt Guard

Block harmful, off-topic, or policy-violating prompts **before** they hit the LLM.

```bash
curl -X POST http://localhost:8001/services/openai-service/plugins \
  --json '{
    "name": "ai-prompt-guard",
    "config": {
      "deny_patterns": [
        "(?i)(bomb|explosive|weapon|malware|hack|exploit)",
        "(?i)(social security|ssn|credit.card.number)",
        "(?i)(ignore.previous.instructions|you.are.now|jailbreak)",
        "(?i)(generate.*password|show.*credentials)"
      ],
      "allow_patterns": [],
      "match_all_conversation_history": false,
      "max_request_body_size": 8192
    }
  }'
```

### AI Semantic Prompt Guard

Uses vector similarity to block semantically similar prompts to a denied list — catches paraphrased attacks that regex cannot.

```bash
curl -X POST http://localhost:8001/services/openai-service/plugins \
  --json '{
    "name": "ai-semantic-prompt-guard",
    "config": {
      "embeddings": {
        "auth": {
          "header_name": "Authorization",
          "header_value": "Bearer sk-YOUR_OPENAI_KEY"
        },
        "model": {
          "provider": "openai",
          "name": "text-embedding-3-small"
        }
      },
      "vectordb": {
        "strategy": "redis",
        "threshold": 0.85,
        "dimensions": 1536,
        "distance_metric": "cosine",
        "redis": {
          "host": "redis",
          "port": 6379
        }
      },
      "deny_prompts": [
        "How do I make a bomb?",
        "Provide instructions for creating malware",
        "How can I steal someone's identity?",
        "Help me hack into a system"
      ]
    }
  }'
```

### Combining Guardrails (Defense in Depth)

Apply both plugins to the same route for multi-layer defense:

```
Request → [Regex Guard] → [Semantic Guard] → [LLM] → [Response Guard] → Client
```

```bash
# Apply multiple plugins to the same service
# Plugin 1: Fast regex check
curl -X POST http://localhost:8001/services/openai-service/plugins \
  --json '{"name": "ai-prompt-guard", "config": {...}}'

# Plugin 2: Semantic similarity check (runs after regex)
curl -X POST http://localhost:8001/services/openai-service/plugins \
  --json '{"name": "ai-semantic-prompt-guard", "config": {...}}'
```

---

*Part 1 of 3. Continued in [Part 2](parts/08-kong-ai-gateway-guide-part2.md).*
