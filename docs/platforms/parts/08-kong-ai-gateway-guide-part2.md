---
title: "Kong AI Gateway — Complete End-to-End Guide (Part 2: Authentication & Authorization I)"
doc_type: guide
domain: platforms
status: current
topic_id: kong-ai-gateway-guide-part2
last_reviewed: 2026-07-27
maturity: practitioner
supersedes: []
tags: [ai-gateway, kong, kubernetes, auth, observability, cost-management]
covers_version: "N/A"
---

*Part 2 of 3 of [Kong AI Gateway — Complete End-to-End Guide](../08-kong-ai-gateway-guide.md). Continued in [Part 3](08-kong-ai-gateway-guide-part3.md).*

## 12. Observability & Analytics

### Built-in AI Logging

Enable detailed token and cost logging in the `ai-proxy` plugin:

```json
{
  "name": "ai-proxy",
  "config": {
    "logging": {
      "log_statistics": true,
      "log_payloads": true
    }
  }
}
```

This adds AI-specific fields to every Kong log entry:

```json
{
  "ai": {
    "meta": {
      "plugin_id": "...",
      "provider_name": "openai",
      "request_model": "gpt-4o",
      "response_model": "gpt-4o-2024-08-06",
      "llm_latency": 842
    },
    "usage": {
      "prompt_tokens": 127,
      "completion_tokens": 342,
      "total_tokens": 469,
      "cost": 0.00522
    }
  }
}
```

### HTTP Log Plugin (Send to Any Backend)

```bash
curl -X POST http://localhost:8001/services/openai-service/plugins \
  --json '{
    "name": "http-log",
    "config": {
      "http_endpoint": "http://your-logging-service:3000/logs",
      "method": "POST",
      "timeout": 5000,
      "keepalive": 60000,
      "flush_timeout": 2,
      "retry_count": 3
    }
  }'
```

### Prometheus Metrics

```bash
# Enable the Prometheus plugin globally
curl -X POST http://localhost:8001/plugins \
  --json '{
    "name": "prometheus",
    "config": {
      "per_consumer": true,
      "status_code_metrics": true,
      "ai_metrics": true,
      "upstream_health_metrics": true
    }
  }'

# Scrape metrics
curl http://localhost:8001/metrics
```

Key AI metrics exposed:

```
# Token usage by provider, model, and consumer
kong_ai_llm_provider_latency_ms_bucket
kong_ai_requests_total
kong_ai_tokens_per_api_product_total{ai_model="gpt-4o", provider="openai", token_type="prompt"}
kong_ai_tokens_per_api_product_total{ai_model="gpt-4o", provider="openai", token_type="completion"}
kong_ai_cost_per_token
kong_ai_cache_hits_total
kong_ai_cache_misses_total
```

### Grafana Dashboard

Import Kong's pre-built AI dashboard (Dashboard ID: `7424`):

```bash
# Grafana datasource — point to your Prometheus
curl -X POST http://grafana:3000/api/datasources \
  -H "Content-Type: application/json" \
  --json '{
    "name": "Prometheus",
    "type": "prometheus",
    "url": "http://prometheus:9090",
    "access": "proxy"
  }'
```

---

## 13. Authentication & Authorization

### API Key Authentication

```bash
# 1. Enable key-auth globally or per service
curl -X POST http://localhost:8001/services/openai-service/plugins \
  --json '{"name": "key-auth", "config": {"key_names": ["x-api-key", "apikey"]}}'

# 2. Create a consumer
curl -X POST http://localhost:8001/consumers \
  --json '{"username": "my-app"}'

# 3. Create a key for the consumer
curl -X POST http://localhost:8001/consumers/my-app/key-auth \
  --json '{"key": "my-secret-api-key"}'

# 4. Client usage
curl -X POST http://localhost:8000/ai/v1/chat/completions \
  -H "x-api-key: my-secret-api-key" \
  --json '{"messages": [{"role": "user", "content": "Hello!"}]}'
```

### JWT Authentication

```bash
# Enable JWT plugin
curl -X POST http://localhost:8001/services/openai-service/plugins \
  --json '{"name": "jwt"}'

# Create JWT credentials for a consumer
curl -X POST http://localhost:8001/consumers/my-app/jwt \
  --json '{
    "algorithm": "HS256",
    "key": "my-jwt-issuer",
    "secret": "my-jwt-secret"
  }'
```

### OAuth 2.0

```bash
curl -X POST http://localhost:8001/services/openai-service/plugins \
  --json '{
    "name": "oauth2",
    "config": {
      "scopes": ["ai.read", "ai.write"],
      "mandatory_scope": true,
      "token_expiration": 7200,
      "enable_client_credentials": true,
      "enable_authorization_code": true
    }
  }'
```

### OIDC / SSO (Enterprise)

```bash
curl -X POST http://localhost:8001/services/openai-service/plugins \
  --json '{
    "name": "openid-connect",
    "config": {
      "issuer": "https://your-idp.com/.well-known/openid-configuration",
      "client_id": ["kong-ai-gateway"],
      "client_secret": ["your-client-secret"],
      "scopes": ["openid", "profile", "email"],
      "auth_methods": ["bearer", "introspection"]
    }
  }'
```

---


### Advanced Authentication Patterns
>
> The following patterns extend the auth fundamentals above. Source: Kong AI Gateway Auth Deep Dive.

### 4. Auth Proxy Offloading Patterns

Auth proxy offloading means Kong **takes full responsibility** for verifying identity so upstream services (LLM APIs) never deal with consumer identity at all.

### Pattern A: Passthrough Auth Offloading

Kong verifies the consumer, then forwards the request with injected identity headers but strips the original auth credential.

```mermaid
flowchart TD
    Client -->|"x-api-key: consumer-key"| Kong
    Kong --> V1["1. Verify consumer key"]
    V1 --> V2["2. Identify consumer = team-payments"]
    V2 --> V3["3. Strip x-api-key header"]
    V3 --> V4["4. Inject Authorization: Bearer MASTER-LLM-KEY"]
    V4 --> V5["5. Inject X-Kong-Consumer: team-payments (optional)"]
    V5 --> OpenAI
```

```bash
# Strip client credentials, inject identity metadata for the upstream
curl -X POST http://localhost:8001/services/openai-service/plugins \
  --json '\{
    "name": "request-transformer",
    "config": \{
      "remove": \{
        "headers": ["x-api-key", "Authorization"]
      },
      "add": \{
        "headers": [
          "X-Forwarded-Consumer:$(consumer.username)",
          "X-Consumer-Groups:$(consumer.groups)"
        ]
      }
    }
  }'
```

### Pattern B: External Auth Service Offloading

Delegate authentication decisions to an external auth service. Kong forwards a pre-check request and only routes to the LLM if auth passes.

```mermaid
flowchart TD
    Client --> Kong
    Kong -->|"auth sub-request"| AuthSvc["Auth Service (Keycloak / custom)"]
    AuthSvc -->|"pass"| OpenAI["OpenAI API"]
    AuthSvc -->|"fail: 403 Forbidden"| Deny["Request denied"]
```

```bash
curl -X POST http://localhost:8001/services/openai-service/plugins \
  --json '\{
    "name": "forward-auth",
    "config": \{
      "uri": "http://your-auth-service:8080/verify",
      "method": "GET",
      "upstreams_headers_request": ["Authorization", "x-api-key"],
      "response_headers": ["X-Auth-User", "X-Auth-Roles", "X-Auth-Tenant"],
      "status_codes": [200]
    }
  }'
```

Your external auth service receives the request headers, validates them, and returns 200 (with identity headers) or 401/403. Kong then passes the identity headers from the auth service to the LLM upstream.

### Pattern C: Pre-Auth with Request Termination

Kong authenticates AND makes the authorization decision, terminating the request entirely if policy fails — never touching the LLM.

```bash
# Use pre-function plugin to implement custom auth logic
curl -X POST http://localhost:8001/services/openai-service/plugins \
  --json '\{
    "name": "pre-function",
    "config": \{
      "access": [
        "local consumer = kong.client.get_consumer()",
        "if not consumer then",
        "  return kong.response.exit(401, \{message = \"Authentication required\"})",
        "end",
        "",
        "-- Check consumer is in allowed groups",
        "local groups = kong.client.get_consumer_groups()",
        "local allowed = \{[\"ai-users\"] = true, [\"ai-premium\"] = true}",
        "local has_access = false",
        "for _, g in ipairs(groups) do",
        "  if allowed[g.name] then has_access = true; break end",
        "end",
        "",
        "if not has_access then",
        "  return kong.response.exit(403, \{message = \"Insufficient permissions for AI access\"})",
        "end"
      ]
    }
  }'
```

### Pattern D: Token Exchange (Consumer Key -> Short-lived Token)

Issue short-lived tokens to consumers so long-lived credentials never leave internal systems.

```mermaid
sequenceDiagram
    participant Client
    participant KongAuth as Kong Auth Route
    participant KongAI as Kong AI Route
    participant OpenAI

    Client->>KongAuth: POST /auth/token + credentials
    KongAuth->>KongAuth: Validate credentials, issue JWT (TTL 1hr)
    KongAuth-->>Client: {access_token: "eyJ..."}
    Client->>KongAI: Bearer eyJ...
    KongAI->>KongAI: Verify JWT
    KongAI->>OpenAI: forward request (with master key)
```

```bash
# Route 1: Token issuance endpoint
curl -X POST http://localhost:8001/routes \
  --json '\{
    "name": "token-issuance",
    "paths": ["/auth/token"],
    "methods": ["POST"],
    "service": \{"name": "internal-auth-service"}
  }'

# Route 2: AI endpoint — only accepts the short-lived JWT
curl -X POST http://localhost:8001/services/openai-service/plugins \
  --json '\{
    "name": "jwt",
    "config": \{
      "header_names": ["Authorization"],
      "claims_to_verify": ["exp"],
      "key_claim_name": "iss"
    }
  }'
```

---

### 5. Credential Injection & Header Manipulation

### Injecting Different Credentials Per Route

Different routes can use different LLM providers — each with their own injected credential:

```bash
# Route A: GPT-4o (OpenAI) — production
curl -X POST http://localhost:8001/routes/production-ai-route/plugins \
  --json '\{
    "name": "ai-proxy",
    "config": \{
      "auth": \{
        "header_name": "Authorization",
        "header_value": "Bearer sk-openai-PROD-KEY"
      },
      "model": \{"provider": "openai", "name": "gpt-4o"}
    }
  }'

# Route B: Claude (Anthropic) — experimental
curl -X POST http://localhost:8001/routes/experimental-ai-route/plugins \
  --json '\{
    "name": "ai-proxy",
    "config": \{
      "auth": \{
        "header_name": "x-api-key",
        "header_value": "sk-ant-ANTHROPIC-KEY"
      },
      "model": \{"provider": "anthropic", "name": "claude-3-5-sonnet-20241022"}
    }
  }'
```

### Injecting Identity Headers Downstream

After authentication, Kong can inject consumer context as headers for downstream services or logging:

```bash
curl -X POST http://localhost:8001/services/openai-service/plugins \
  --json '\{
    "name": "request-transformer",
    "config": \{
      "add": \{
        "headers": [
          "X-Kong-Consumer-ID:$(consumer.id)",
          "X-Kong-Consumer-Username:$(consumer.username)",
          "X-Kong-Consumer-Custom-ID:$(consumer.custom_id)",
          "X-Kong-Request-ID:$(request.id)",
          "X-Kong-Timestamp:$(now)"
        ]
      },
      "remove": \{
        "headers": ["Authorization", "x-api-key", "Cookie"]
      }
    }
  }'
```

### Dynamic Credential Injection from Consumer Metadata

Assign different LLM accounts to different consumers using consumer tags/metadata:

```bash
# Tag consumers with their assigned project account
curl -X POST http://localhost:8001/consumers \
  --json '\{
    "username": "project-alpha",
    "tags": ["project:alpha", "account:openai-account-2", "tier:premium"]
  }'

# Use pre-function to dynamically select credentials
curl -X POST http://localhost:8001/services/openai-service/plugins \
  --json '\{
    "name": "pre-function",
    "config": \{
      "access": [
        "local consumer = kong.client.get_consumer()",
        "local tags = consumer and consumer.tags or {}",
        "local account_key = \"sk-openai-DEFAULT-KEY\"",
        "",
        "for _, tag in ipairs(tags) do",
        "  if tag == \"account:openai-account-2\" then",
        "    account_key = os.getenv(\"OPENAI_ACCOUNT_2_KEY\")",
        "    break",
        "  elseif tag == \"account:openai-account-3\" then",
        "    account_key = os.getenv(\"OPENAI_ACCOUNT_3_KEY\")",
        "    break",
        "  end",
        "end",
        "",
        "kong.service.request.set_header(\"Authorization\", \"Bearer \" .. account_key)"
      ]
    }
  }'
```

---

### 6. Per-Consumer Model Access Control

Restrict which models and providers each consumer can access using ACL groups combined with multiple routes.

### Step 1: Create ACL Groups

```bash
# Create groups representing model tiers
curl -X POST http://localhost:8001/consumers/free-user/acls \
  --json '\{"group": "ai-free-tier"}'

curl -X POST http://localhost:8001/consumers/pro-user/acls \
  --json '\{"group": "ai-pro-tier"}'

curl -X POST http://localhost:8001/consumers/enterprise-user/acls \
  --json '\{"group": "ai-enterprise-tier"}'
```

### Step 2: Create Model-Specific Routes with ACL Restrictions

```bash
# Free tier route: GPT-4o-mini only
curl -X POST http://localhost:8001/routes \
  --json '\{"name": "free-tier-ai", "paths": ["/ai/free"], "service": \{"name": "mini-model-service"}}'

curl -X POST http://localhost:8001/routes/free-tier-ai/plugins \
  --json '\{
    "name": "acl",
    "config": \{
      "allow": ["ai-free-tier", "ai-pro-tier", "ai-enterprise-tier"],
      "hide_groups_header": true
    }
  }'

curl -X POST http://localhost:8001/routes/free-tier-ai/plugins \
  --json '\{
    "name": "ai-proxy",
    "config": \{
      "model": \{"provider": "openai", "name": "gpt-4o-mini"},
      "auth": \{"header_name": "Authorization", "header_value": "Bearer sk-MASTER-KEY"}
    }
  }'

# Pro tier route: GPT-4o only
curl -X POST http://localhost:8001/routes \
  --json '\{"name": "pro-tier-ai", "paths": ["/ai/pro"], "service": \{"name": "pro-model-service"}}'

curl -X POST http://localhost:8001/routes/pro-tier-ai/plugins \
  --json '\{
    "name": "acl",
    "config": \{
      "allow": ["ai-pro-tier", "ai-enterprise-tier"],
      "hide_groups_header": true
    }
  }'

# Enterprise tier route: All models including Claude, GPT-4o, fine-tuned models
curl -X POST http://localhost:8001/routes \
  --json '\{"name": "enterprise-ai", "paths": ["/ai/enterprise"], "service": \{"name": "enterprise-model-service"}}'

curl -X POST http://localhost:8001/routes/enterprise-ai/plugins \
  --json '\{
    "name": "acl",
    "config": \{
      "allow": ["ai-enterprise-tier"],
      "hide_groups_header": true
    }
  }'
```

### Step 3: Enforce Model Override Prevention

Prevent consumers from specifying their own model in the request body — Kong enforces the assigned model:

```bash
curl -X POST http://localhost:8001/routes/free-tier-ai/plugins \
  --json '\{
    "name": "pre-function",
    "config": \{
      "access": [
        "local body = kong.request.get_body()",
        "if body and body.model then",
        "  -- Overwrite any model the consumer tries to specify",
        "  body.model = nil",
        "  kong.request.set_body(body)",
        "end"
      ]
    }
  }'
```

---

### 7. OIDC / SSO Integration

Integrate with enterprise identity providers (Keycloak, Okta, Azure AD, Auth0) so employees authenticate with their corporate SSO.

### Full OIDC Configuration

```bash
curl -X POST http://localhost:8001/services/openai-service/plugins \
  --json '\{
    "name": "openid-connect",
    "config": \{
      "issuer": "https://keycloak.company.com/realms/production",
      "client_id": ["kong-ai-gateway"],
      "client_secret": ["your-client-secret-from-keycloak"],

      "scopes": ["openid", "profile", "email", "ai:access"],
      "scopes_required": ["ai:access"],

      "auth_methods": [
        "bearer",
        "introspection",
        "client_credentials",
        "authorization_code"
      ],

      "bearer_token_param_type": ["header"],

      "token_endpoint_auth_method": "client_secret_post",

      "consumer_claim": "email",
      "consumer_by": ["username", "custom_id"],

      "groups_claim": "groups",
      "groups_required": ["ai-gateway-users"],

      "hide_credentials": true,

      "introspect_jwt_tokens": true,
      "introspection_endpoint": "https://keycloak.company.com/realms/production/protocol/openid-connect/token/introspect",

      "session_secret": "random-32-char-session-secret-here",
      "session_cookie_name": "kong_ai_session",
      "session_cookie_secure": true,
      "session_cookie_http_only": true,
      "session_cookie_same_site": "Strict",

      "ssl_verify": true,
      "timeout": 10000,

      "upstream_headers_claims": ["email", "sub", "groups"],
      "upstream_headers_names": ["X-User-Email", "X-User-ID", "X-User-Groups"]
    }
  }'
```

### Auto-Create Consumers from OIDC Claims

When a user authenticates via SSO for the first time, Kong can auto-create a consumer:

```bash
curl -X POST http://localhost:8001/services/openai-service/plugins \
  --json '\{
    "name": "openid-connect",
    "config": \{
      "issuer": "https://accounts.google.com",
      "client_id": ["your-google-client-id"],
      "client_secret": ["your-google-client-secret"],
      "consumer_claim": "email",
      "consumer_by": ["username"],
      "consumer_optional": false,
      "login_action": "redirect",
      "login_redirect_uri": ["https://your-app.com/ai-chat"],
      "forbidden_redirect_uri": ["https://your-app.com/access-denied"]
    }
  }'
```

### Mapping OIDC Groups to Kong ACL Groups

```bash
# Use post-function to map OIDC groups -> Kong ACL groups for model access control
curl -X POST http://localhost:8001/services/openai-service/plugins \
  --json '\{
    "name": "post-function",
    "config": \{
      "access": [
        "local oidc_groups = kong.request.get_header(\"X-User-Groups\") or \"\"",
        "",
        "-- Map OIDC group claims to Kong ACL groups",
        "if oidc_groups:find(\"ai%-enterprise\") then",
        "  kong.request.set_header(\"X-Kong-ACL-Group\", \"ai-enterprise-tier\")",
        "elseif oidc_groups:find(\"ai%-pro\") then",
        "  kong.request.set_header(\"X-Kong-ACL-Group\", \"ai-pro-tier\")",
        "else",
        "  kong.request.set_header(\"X-Kong-ACL-Group\", \"ai-free-tier\")",
        "end"
      ]
    }
  }'
```

---

### 8. mTLS Between Kong and LLM Providers

Mutual TLS ensures that even Kong's outgoing connection to the LLM provider is cryptographically verified — preventing MITM attacks between Kong and the LLM.

### Step 1: Create a CA Certificate in Kong

```bash
# Load your CA certificate (or use the LLM provider's public CA)
curl -X POST http://localhost:8001/ca_certificates \
  --json '\{
    "cert": "-----BEGIN CERTIFICATE-----\nMIIBpzCC...\n-----END CERTIFICATE-----"
  }'
# Returns: \{"id": "ca-cert-uuid-here", ...}
```

### Step 2: Create a Client Certificate for Kong

```bash
# Kong's own certificate + private key for mutual TLS
curl -X POST http://localhost:8001/certificates \
  --json '\{
    "cert": "-----BEGIN CERTIFICATE-----\nMIIDpzCC...\n-----END CERTIFICATE-----",
    "key": "-----BEGIN RSA PRIVATE KEY-----\nMIIEowIB...\n-----END RSA PRIVATE KEY-----"
  }'
# Returns: \{"id": "client-cert-uuid-here", ...}
```

### Step 3: Apply to the AI Upstream Service

```bash
# Attach the client certificate to the service for outgoing mTLS
curl -X PATCH http://localhost:8001/services/openai-service \
  --json '\{
    "client_certificate": \{"id": "client-cert-uuid-here"},
    "tls_verify": true,
    "tls_verify_depth": 3,
    "ca_certificates": ["ca-cert-uuid-here"]
  }'
```

### Step 4: mTLS via SNI (for Multiple LLM Providers)

```bash
# Create an SNI-based TLS config for api.openai.com
curl -X POST http://localhost:8001/snis \
  --json '\{
    "name": "api.openai.com",
    "certificate": \{"id": "client-cert-uuid-here"}
  }'

# Create for Anthropic
curl -X POST http://localhost:8001/snis \
  --json '\{
    "name": "api.anthropic.com",
    "certificate": \{"id": "client-cert-uuid-here"}
  }'
```

### Verify mTLS is Working

```bash
# Check the service's TLS configuration
curl http://localhost:8001/services/openai-service | jq '\{tls_verify, client_certificate, ca_certificates}'

# Kong logs will show TLS handshake details
docker logs kong 2>&1 | grep -i "tls\|ssl\|certificate"
```

---

### 9. Vault Integration for Secret Management

Never store raw LLM API keys in Kong's config. Use Vault to retrieve secrets dynamically.

### Supported Vault Backends

| Vault | Config Key |
| --- | --- |
| HashiCorp Vault | `hcv` |
| AWS Secrets Manager | `aws` |
| GCP Secret Manager | `gcp` |
| Azure Key Vault | `azure` |
| Environment Variables | `env` |

### HashiCorp Vault Setup

```bash
# 1. Configure the Vault backend in Kong
curl -X POST http://localhost:8001/vaults \
  --json '{
    "name": "hcv",
    "prefix": "hcv",
    "description": "HashiCorp Vault for LLM API Keys",
    "config": {
      "protocol": "https",
      "host": "vault.company.com",
      "port": 8200,
      "mount": "secret",
      "kv": "v2",
      "auth_method": "kubernetes",
      "kube_role": "kong-ai-gateway",
      "kube_api_token_file": "/var/run/secrets/kubernetes.io/serviceaccount/token",
      "ttl": 300,
      "neg_ttl": 0,
      "resurrect_ttl": 30
    }
  }'

# 2. Store secrets in Vault
vault kv put secret/kong/ai-keys \
  openai_api_key="sk-proj-REAL-KEY-HERE" \
  anthropic_api_key="sk-ant-REAL-KEY-HERE" \
  azure_openai_key="AZURE-REAL-KEY-HERE"

# 3. Reference secrets by Vault path in plugin config
curl -X POST http://localhost:8001/services/openai-service/plugins \
  --json '{
    "name": "ai-proxy",
    "config": {
      "auth": {
        "header_name": "Authorization",
        "header_value": "{vault://hcv/kong/ai-keys/openai_api_key}"
      },
      "model": {"provider": "openai", "name": "gpt-4o"}
    }
  }'
```

Kong resolves `\{vault://hcv/...}` references at runtime, caches the value for `ttl` seconds, and automatically refreshes — no restart needed on key rotation.

### AWS Secrets Manager Setup

```bash
# Configure AWS Secrets Manager vault
curl -X POST http://localhost:8001/vaults \
  --json '{
    "name": "aws",
    "prefix": "aws",
    "config": {
      "region": "us-east-1",
      "ttl": 600,
      "neg_ttl": 0
    }
  }'

# Store the key in AWS
aws secretsmanager create-secret \
  --name "kong/ai-keys/openai" \
  --secret-string '{"api_key":"sk-proj-REAL-KEY"}'

# Reference it in Kong
# {vault://aws/kong/ai-keys/openai#api_key}
curl -X POST http://localhost:8001/services/openai-service/plugins \
  --json '{
    "name": "ai-proxy",
    "config": {
      "auth": {
        "header_name": "Authorization",
        "header_value": "{vault://aws/kong/ai-keys/openai#api_key}"
      }
    }
  }'
```

### Environment Variable Vault (Simple Setup)

```bash
# Set API keys as environment variables on the Kong container
export OPENAI_API_KEY="sk-proj-REAL-KEY"
export ANTHROPIC_API_KEY="sk-ant-REAL-KEY"

# Configure the env vault
curl -X POST http://localhost:8001/vaults \
  --json '{
    "name": "env",
    "prefix": "env",
    "config": {
      "prefix": "KONG_"
    }
  }'

# Export with the configured prefix
export KONG_OPENAI_API_KEY="sk-proj-REAL-KEY"

# Reference in plugin config
# {vault://env/openai_api_key}
```

### Key Rotation Without Downtime

```bash
# 1. Update the secret in Vault
vault kv put secret/kong/ai-keys openai_api_key="sk-proj-NEW-ROTATED-KEY"

# 2. Kong auto-picks up the new key after TTL expires (default: 300s)
# Force immediate refresh if needed:
curl -X DELETE http://localhost:8001/cache/secret:hcv:kong/ai-keys/openai_api_key

# 3. Verify the new key is being used (check a test request succeeds)
curl -X POST http://localhost:8000/ai/v1/chat/completions \
  -H "x-api-key: test-consumer-key" \
  --json '{"messages": [{"role": "user", "content": "ping"}]}'
```

---

### 10. ACL & RBAC for AI Routes

### ACL Plugin — Group-based Access Control

```bash
# Apply ACL to the enterprise AI route
curl -X POST http://localhost:8001/routes/enterprise-ai/plugins \
  --json '{
    "name": "acl",
    "config": {
      "allow": ["ai-enterprise-tier", "ai-admin"],
      "deny": [],
      "hide_groups_header": true
    }
  }'

# Assign a consumer to a group
curl -X POST http://localhost:8001/consumers/enterprise-user/acls \
  --json '{"group": "ai-enterprise-tier"}'

# Remove a consumer from a group (revoke access instantly)
# First, find the ACL ID
curl http://localhost:8001/consumers/enterprise-user/acls | jq .
# Then delete it
curl -X DELETE http://localhost:8001/consumers/enterprise-user/acls/<acl-id>
```

### RBAC (Kong Enterprise) — Fine-Grained Admin API Control

In Kong Enterprise (Konnect), RBAC governs who can modify gateway config:

```bash
# Create roles for AI gateway administrators
curl -X POST http://localhost:8001/rbac/roles \
  --json '{"name": "ai-gateway-admin", "comment": "Full AI gateway management"}'

curl -X POST http://localhost:8001/rbac/roles \
  --json '{"name": "ai-readonly", "comment": "View-only access to AI gateway config"}'

# Assign endpoints to roles
curl -X POST http://localhost:8001/rbac/roles/ai-gateway-admin/endpoints \
  --json '{
    "workspace": "default",
    "endpoint": "/services/*/plugins",
    "actions": "create,read,update,delete"
  }'

curl -X POST http://localhost:8001/rbac/roles/ai-readonly/endpoints \
  --json '{
    "workspace": "default",
    "endpoint": "/services/*/plugins",
    "actions": "read"
  }'

# Assign a role to an admin user
curl -X POST http://localhost:8001/rbac/users \
  --json '{"name": "alice", "user_token": "alice-admin-token"}'

curl -X POST http://localhost:8001/rbac/users/alice/roles \
  --json '{"roles": ["ai-gateway-admin"]}'
```

---

### 11. Zero-Trust Architecture

In a Zero-Trust model, every request is verified regardless of origin — no implicit trust, even from internal services.
