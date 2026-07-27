---
title: "Kong AI Gateway — Microsoft Entra ID Integration (Part 2: Auto-Provisioning, MFA, Multi-Tenant, Troubleshooting)"
doc_type: guide
domain: platforms
status: current
topic_id: kong-entra-id-integration-part2
last_reviewed: 2026-07-27
maturity: practitioner
supersedes: []
tags: [ai-gateway, kong, entra-id, azure, sso, oauth]
covers_version: "N/A"
---

*Part 2 of 2 of [Kong AI Gateway — Microsoft Entra ID Integration](../09-kong-entra-id-integration.md).*

## 8. Per-Consumer Auto-Provisioning from Entra ID

When a new Entra ID user or service authenticates for the first time, Kong can automatically create a consumer and assign the correct ACL group — no manual onboarding needed.

### OIDC Auto-Provisioning Config

```bash
curl -X POST http://localhost:8001/services/openai-service/plugins \
  --json '{
    "name": "openid-connect",
    "config": {
      "consumer_claim": "email",
      "consumer_by": ["username"],
      "consumer_optional": false,

      "groups_claim": "roles",

      "login_action": "redirect",
      "login_redirect_uri": ["https://kong.company.com/ai/chat"],

      "forbidden_redirect_uri": ["https://kong.company.com/no-access"]
    }
  }'
```

When `consumer_optional: false`, Kong will:

1. Extract the `email` claim from the Entra token
2. Search for a Kong consumer with that username
3. If not found -> create the consumer automatically
4. Assign groups from the `roles` claim

### Post-Provisioning Hook via post-function

After auto-provisioning, apply additional setup:

```bash
curl -X POST http://localhost:8001/services/openai-service/plugins \
  --json '{
    "name": "post-function",
    "config": {
      "access": [
        "local consumer = kong.client.get_consumer()",
        "if not consumer then return end",
        "",
        "-- Log new consumer provisioning event",
        "kong.log.info(\"[Entra Auto-Provision] Consumer: \" .. consumer.username)",
        "",
        "-- Inject consumer metadata as upstream headers",
        "kong.service.request.set_header(\"X-Consumer-Username\", consumer.username)",
        "kong.service.request.set_header(\"X-Consumer-ID\", consumer.id)",
        "",
        "-- Remove sensitive headers before reaching OpenAI",
        "kong.service.request.clear_header(\"Cookie\")",
        "kong.service.request.clear_header(\"Authorization\")"
      ]
    }
  }'
```

---

## 9. Conditional Access & MFA Enforcement

Entra Conditional Access policies can enforce MFA before tokens are issued. Kong enforces that the resulting token carries the required authentication method claim.

### Configure Conditional Access in Entra

```
Azure Portal ->
  Microsoft Entra ID ->
  Security ->
  Conditional Access ->
  New policy

Name: Require MFA for Kong AI Gateway

Assignments:
  Users: All users (or specific groups)
  Target resources: Kong AI Gateway (your app registration)

Access controls -> Grant:
  ☑ Require multifactor authentication
  ☑ Require compliant device (optional, for corporate devices)

Session:
  Sign-in frequency: 1 hour (for sensitive AI access)

Enable policy: On
```

### Validate MFA Claim in Kong

Entra tokens include an `amr` (Authentication Methods References) claim after MFA:

```json
{
  "amr": ["pwd", "mfa", "rsa"],
  "acr": "1"
}
```

Enforce MFA via pre-function:

```bash
curl -X POST http://localhost:8001/routes/enterprise-ai/plugins \
  --json '{
    "name": "pre-function",
    "config": {
      "access": [
        "-- Read the amr header injected by OIDC plugin",
        "local amr = kong.request.get_header(\"X-Auth-Methods\") or \"\"",
        "",
        "-- Require MFA for premium and enterprise routes",
        "local has_mfa = amr:find(\"mfa\") or amr:find(\"rsa\") or amr:find(\"otp\")",
        "",
        "if not has_mfa then",
        "  return kong.response.exit(403, {",
        "    error = \"MFA required\",",
        "    message = \"Multi-factor authentication is required to access this AI endpoint.\",",
        "    mfa_required = true",
        "  })",
        "end"
      ]
    }
  }'
```

Configure OIDC plugin to include `amr` as an upstream header:

```bash
# Add amr to upstream headers in OIDC config
curl -X PATCH http://localhost:8001/plugins/<oidc-plugin-id> \
  --json '{
    "config": {
      "upstream_headers_claims": ["email", "oid", "roles", "amr"],
      "upstream_headers_names": ["X-User-Email", "X-User-OID", "X-User-Roles", "X-Auth-Methods"]
    }
  }'
```

---

## 10. Multi-Tenant Entra ID Setup

For SaaS products serving multiple organizations, each with their own Entra ID tenant.

### Option A: Common Endpoint (Any Tenant)

```bash
curl -X POST http://localhost:8001/services/openai-service/plugins \
  --json '{
    "name": "openid-connect",
    "config": {
      "issuer": "https://login.microsoftonline.com/common/v2.0/.well-known/openid-configuration",
      "client_id": ["your-multitenant-app-id"],
      "client_secret": ["your-client-secret"],

      "auth_methods": ["bearer", "authorization_code"],

      "verify_claims": true,
      "verify_signature": true,
      "issuers_allowed": [
        "https://login.microsoftonline.com/TENANT-A-ID/v2.0",
        "https://login.microsoftonline.com/TENANT-B-ID/v2.0",
        "https://login.microsoftonline.com/TENANT-C-ID/v2.0"
      ],

      "consumer_claim": "oid",
      "consumer_by": ["custom_id"]
    }
  }'
```

### Option B: Per-Tenant Routes (Strict Isolation)

Create a separate Kong route per tenant, each with its own OIDC plugin pointing to that tenant's issuer:

```bash
# Tenant A route
curl -X POST http://localhost:8001/routes \
  --json '{
    "name": "tenant-a-ai",
    "paths": ["/tenant-a/ai"],
    "headers": {"X-Tenant-ID": ["tenant-a"]},
    "service": {"name": "openai-service"}
  }'

curl -X POST http://localhost:8001/routes/tenant-a-ai/plugins \
  --json '{
    "name": "openid-connect",
    "config": {
      "issuer": "https://login.microsoftonline.com/TENANT-A-ID/v2.0/.well-known/openid-configuration",
      "client_id": ["app-id-for-tenant-a"],
      "client_secret": ["{vault://aws/kong/tenant-a/client-secret}"],
      "audience_required": ["api://kong-ai-gateway-tenant-a"]
    }
  }'

# Tenant B route
curl -X POST http://localhost:8001/routes \
  --json '{
    "name": "tenant-b-ai",
    "paths": ["/tenant-b/ai"],
    "headers": {"X-Tenant-ID": ["tenant-b"]},
    "service": {"name": "openai-service"}
  }'

curl -X POST http://localhost:8001/routes/tenant-b-ai/plugins \
  --json '{
    "name": "openid-connect",
    "config": {
      "issuer": "https://login.microsoftonline.com/TENANT-B-ID/v2.0/.well-known/openid-configuration",
      "client_id": ["app-id-for-tenant-b"],
      "client_secret": ["{vault://aws/kong/tenant-b/client-secret}"],
      "audience_required": ["api://kong-ai-gateway-tenant-b"]
    }
  }'
```

### Enforce Tenant Isolation

Prevent cross-tenant token usage:

```bash
curl -X POST http://localhost:8001/services/openai-service/plugins \
  --json '{
    "name": "pre-function",
    "config": {
      "access": [
        "local tenant_id_from_token = kong.request.get_header(\"X-Tenant-ID\")",
        "local expected_tenant = kong.router.get_route().name:match(\"^tenant%-(.-)%-\")",
        "",
        "if tenant_id_from_token ~= expected_tenant then",
        "  return kong.response.exit(403, {",
        "    error = \"Tenant mismatch\",",
        "    message = \"Token tenant does not match the requested route tenant\"",
        "  })",
        "end"
      ]
    }
  }'
```

---

## 11. Token Introspection & Revocation

For high-security scenarios, validate tokens against Entra's introspection endpoint on every request (at the cost of latency).

### Enable Token Introspection

```bash
curl -X POST http://localhost:8001/services/openai-service/plugins \
  --json "{
    \"name\": \"openid-connect\",
    \"config\": {
      \"issuer\": \"https://login.microsoftonline.com/${TENANT_ID}/v2.0/.well-known/openid-configuration\",
      \"client_id\": [\"${APP_ID}\"],
      \"client_secret\": [\"${CLIENT_SECRET}\"],

      \"introspect_jwt_tokens\": true,

      \"introspection_endpoint\": \"https://login.microsoftonline.com/${TENANT_ID}/oauth2/v2.0/introspect\",
      \"introspection_endpoint_auth_method\": \"client_secret_post\",

      \"introspection_hint\": \"access_token\",

      \"introspection_check_active\": true,

      \"cache_introspection\": true,
      \"cache_introspection_ttl\": 30
    }
  }"
```

### Handle Revoked Tokens Immediately

When a user is offboarded (e.g., leaves the company), their Entra account is disabled — tokens issued before that point may still be valid until they expire. Introspection catches this within the cache TTL.

```bash
# Reduce cache TTL for sensitive routes (trade latency for security)
curl -X PATCH http://localhost:8001/plugins/<oidc-plugin-id> \
  --json '{
    "config": {
      "cache_introspection": true,
      "cache_introspection_ttl": 10
    }
  }'
```

### Force Token Revocation on Logout

```bash
curl -X PATCH http://localhost:8001/plugins/<oidc-plugin-id> \
  --json '{
    "config": {
      "logout_revoke": true,
      "logout_revoke_access_token": true,
      "logout_revoke_refresh_token": true
    }
  }'
```

---

## 12. Managed Identity for Kong on Azure

When Kong runs on Azure (AKS, VM, Container Apps), use **Managed Identity** so Kong itself authenticates to Entra without storing any client secret.

### Enable Managed Identity on AKS

```bash
# Create AKS cluster with managed identity
az aks create \
  --resource-group kong-rg \
  --name kong-aks \
  --enable-managed-identity \
  --node-count 3

# Get the managed identity principal ID
IDENTITY_ID=$(az aks show \
  --resource-group kong-rg \
  --name kong-aks \
  --query "identityProfile.kubeletidentity.objectId" -o tsv)

echo "Managed Identity Object ID: $IDENTITY_ID"
```

### Grant Managed Identity Access to Key Vault (for secrets)

```bash
# Allow the AKS managed identity to read secrets
az keyvault set-policy \
  --name kong-keyvault \
  --object-id $IDENTITY_ID \
  --secret-permissions get list

# Or with RBAC (preferred)
az role assignment create \
  --role "Key Vault Secrets User" \
  --assignee $IDENTITY_ID \
  --scope "/subscriptions/{sub-id}/resourceGroups/kong-rg/providers/Microsoft.KeyVault/vaults/kong-keyvault"
```

### Configure Kong Vault to Use Managed Identity

```bash
curl -X POST http://localhost:8001/vaults \
  --json '{
    "name": "azure",
    "prefix": "azure",
    "description": "Azure Key Vault via Managed Identity",
    "config": {
      "vault_uri": "https://kong-keyvault.vault.azure.net",
      "auth_method": "managed_identity",
      "ttl": 300,
      "neg_ttl": 0
    }
  }'

# Reference secrets using the vault
# {vault://azure/openai-api-key}
# {vault://azure/entra-client-secret}
```

### Use Workload Identity (Recommended for AKS)

```bash
# Create a user-assigned managed identity
az identity create \
  --name kong-workload-identity \
  --resource-group kong-rg

UAMI_CLIENT_ID=$(az identity show \
  --name kong-workload-identity \
  --resource-group kong-rg \
  --query clientId -o tsv)

UAMI_OBJECT_ID=$(az identity show \
  --name kong-workload-identity \
  --resource-group kong-rg \
  --query principalId -o tsv)

# Enable OIDC issuer on AKS
az aks update \
  --resource-group kong-rg \
  --name kong-aks \
  --enable-oidc-issuer \
  --enable-workload-identity

# Create federated credential for Kong's service account
AKS_OIDC_ISSUER=$(az aks show \
  --resource-group kong-rg \
  --name kong-aks \
  --query "oidcIssuerProfile.issuerUrl" -o tsv)

az identity federated-credential create \
  --name kong-federated-cred \
  --identity-name kong-workload-identity \
  --resource-group kong-rg \
  --issuer $AKS_OIDC_ISSUER \
  --subject "system:serviceaccount:kong:kong" \
  --audiences "api://AzureADTokenExchange"
```

```yaml
# kong-serviceaccount.yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: kong
  namespace: kong
  annotations:
    azure.workload.identity/client-id: "<uami-client-id>"
    azure.workload.identity/tenant-id: "<tenant-id>"
```

```yaml
# kong-deployment.yaml (add workload identity label)
spec:
  template:
    metadata:
      labels:
        azure.workload.identity/use: "true"
```

---

## 13. Troubleshooting Entra ID Auth Issues

### Common Error: `401 Unauthorized` — Invalid Token

```bash
# Decode and inspect the token manually
TOKEN="eyJ0eXAiOiJKV1QiLCJhbGci..."
echo $TOKEN | cut -d. -f2 | base64 -d 2>/dev/null | jq '{iss, aud, exp, roles, tid, ver}'

# Common causes:
# 1. aud claim doesn't match Kong's audience_required config
#    Token aud: "https://graph.microsoft.com"
#    Expected:  "api://kong-ai-gateway"
#    Fix: request token with scope "api://kong-ai-gateway/.default"

# 2. Token issued for wrong tenant
#    Check tid claim matches your TENANT_ID

# 3. Token expired (exp < now)
#    Refresh the token and retry

# Check Kong OIDC plugin logs
docker logs kong 2>&1 | grep -i "oidc\|openid\|entra\|401\|403"
```

### Common Error: `403 Forbidden` — Missing Role

```bash
# Check if the user has the app role assigned
az rest --method GET \
  --uri "https://graph.microsoft.com/v1.0/users/alice@company.com/appRoleAssignments" \
  | jq '.value[] | {appRoleId, principalDisplayName}'

# Check role is included in token (v2.0 tokens include roles in access token by default)
# But you must request the right scope: "api://kong-ai-gateway/.default"
# NOT just "openid profile email" — those don't include app roles

# Force include roles in token via optional claims
# Azure Portal -> App Registration -> Token configuration -> Add optional claim -> roles
```

### Common Error: `JWKS fetch failed`

```bash
# Test JWKS endpoint reachability from Kong's network
docker exec kong curl -s \
  "https://login.microsoftonline.com/${TENANT_ID}/discovery/v2.0/keys" | jq .keys[0].kid

# If blocked, check Kong's outbound network policy allows:
# login.microsoftonline.com:443
# graph.microsoft.com:443 (for introspection)

# Increase JWKS cache TTL to reduce fetch frequency
curl -X PATCH http://localhost:8001/plugins/<oidc-plugin-id> \
  --json '{"config": {"cache_jwks_ttl": 600}}'
```

### Common Error: Session Not Persisting

```bash
# Check session secret is consistent across all Kong nodes
# (All replicas must use the SAME session_secret)
curl http://localhost:8001/plugins/<oidc-plugin-id> | jq .config.session_secret

# Verify session cookie is being set
curl -v https://kong.company.com/ai/chat 2>&1 | grep -i "set-cookie"

# Check session backend — for multi-node Kong, use Redis-backed sessions
curl -X PATCH http://localhost:8001/plugins/<oidc-plugin-id> \
  --json '{
    "config": {
      "session_storage": "redis",
      "session_redis_host": "redis",
      "session_redis_port": 6379,
      "session_redis_prefix": "kong_oidc"
    }
  }'
```

### Debug Mode

```bash
# Enable OIDC debug logging
curl -X PATCH http://localhost:8001/plugins/<oidc-plugin-id> \
  --json '{"config": {"resolve_distributed_claims": true}}'

# Set Kong log level to debug
curl -X PATCH http://localhost:8001/config \
  --json '{"log_level": "debug"}'

# Watch for OIDC events
docker logs -f kong 2>&1 | grep -E "oidc|openid|Bearer|jwt|claim"

# Reset log level when done
curl -X PATCH http://localhost:8001/config \
  --json '{"log_level": "warn"}'
```

---

## 14. Complete Working Reference Config

Full declarative config (`deck sync`) for Entra ID integration:

```yaml
# entra-kong-ai.yaml
_format_version: "3.0"
_transform: true

vaults:
  - name: azure
    prefix: azure
    description: "Azure Key Vault via Managed Identity"
    config:
      vault_uri: "https://kong-keyvault.vault.azure.net"
      auth_method: "managed_identity"
      ttl: 300

services:
  - name: openai-service
    url: https://api.openai.com
    read_timeout: 120000
    connect_timeout: 10000
    tls_verify: true

    routes:
      - name: ai-chat
        paths: ["/ai/v1/chat/completions"]
        methods: ["POST"]
        strip_path: false

      - name: ai-embeddings
        paths: ["/ai/v1/embeddings"]
        methods: ["POST"]
        strip_path: false

      - name: entra-callback
        paths: ["/ai/callback"]
        methods: ["GET", "POST"]
        strip_path: false

    plugins:

      # -- 1. OIDC: Entra ID Authentication ------------------------
      - name: openid-connect
        config:
          issuer: "https://login.microsoftonline.com/YOUR-TENANT-ID/v2.0/.well-known/openid-configuration"
          client_id:
            - "YOUR-APP-CLIENT-ID"
          client_secret:
            - "{vault://azure/kong-entra-client-secret}"
          auth_methods:
            - session
            - bearer
            - client_credentials
            - authorization_code
          scopes:
            - openid
            - profile
            - email
            - "api://kong-ai-gateway/ai.chat"
          audience_required:
            - "api://kong-ai-gateway"
          consumer_claim: email
          consumer_by:
            - username
            - custom_id
          groups_claim: roles
          hide_credentials: true
          upstream_headers_claims:
            - email
            - oid
            - roles
            - name
            - tid
          upstream_headers_names:
            - X-User-Email
            - X-User-OID
            - X-User-Roles
            - X-User-Name
            - X-Tenant-ID
          session_secret: "{vault://azure/kong-session-secret}"
          session_cookie_name: kong_entra_session
          session_cookie_secure: true
          session_cookie_http_only: true
          session_cookie_same_site: Lax
          session_rolling_timeout: 3600
          session_absolute_timeout: 28800
          session_storage: redis
          session_redis_host: redis
          session_redis_port: 6379
          session_redis_prefix: kong_oidc
          redirect_uri: "https://kong.company.com/ai/callback"
          login_action: redirect
          login_redirect_uri:
            - "https://kong.company.com/ai/chat"
          logout_uri: "/logout"
          logout_redirect_uri:
            - "https://kong.company.com/"
          logout_revoke: true
          forbidden_redirect_uri:
            - "https://kong.company.com/access-denied"
          unauthorized_redirect_uri:
            - "https://kong.company.com/login"
          verify_claims: true
          verify_signature: true
          verify_expiry: true
          cache_jwks: true
          cache_jwks_ttl: 300
          ssl_verify: true

      # -- 2. ACL: Entra Role-based Access -------------------------
      - name: acl
        config:
          allow:
            - AI.Free
            - AI.Standard
            - AI.Premium
            - AI.Admin
          hide_groups_header: true

      # -- 3. Rate Limiting: Token-based per consumer ---------------
      - name: ai-rate-limiting-advanced
        config:
          limit: [500000]
          window_size: [3600]
          tokens_count_strategy: total_tokens
          strategy: redis
          redis:
            host: redis
            port: 6379

      # -- 4. Guardrails: Block prompt injection --------------------
      - name: ai-prompt-guard
        config:
          deny_patterns:
            - "(?i)(ignore.previous.instructions|jailbreak)"
            - "(?i)(reveal.*system.prompt|you.are.now)"

      # -- 5. Strip all client headers, inject request ID -----------
      - name: request-transformer
        config:
          remove:
            headers:
              - Authorization
              - Cookie
              - x-api-key
              - x-forwarded-for
              - x-real-ip
          add:
            headers:
              - "X-Gateway-Request-ID:$(request.id)"

      # -- 6. AI Proxy: Inject LLM master key ----------------------
      - name: ai-proxy
        config:
          route_type: "llm/v1/chat"
          auth:
            header_name: Authorization
            header_value: "{vault://azure/openai-master-api-key}"
          model:
            provider: openai
            name: gpt-4o
            options:
              max_tokens: 2048
              input_cost: 0.0000025
              output_cost: 0.00001
          logging:
            log_statistics: true
            log_payloads: false

      # -- 7. Audit log all AI events -------------------------------
      - name: http-log
        config:
          http_endpoint: "http://audit-service:9000/ai-events"
          flush_timeout: 2
          retry_count: 3
```

```bash
# Apply the full config
deck sync --state entra-kong-ai.yaml

# Verify
curl http://localhost:8001/services/openai-service/plugins | jq '[.data[].name]'
# -> ["openid-connect", "acl", "ai-rate-limiting-advanced", "ai-prompt-guard",
#    "request-transformer", "ai-proxy", "http-log"]
```

---

## Quick Reference: Entra ID Endpoints

```
| Endpoint | URL Pattern |
| --- | --- |
| OIDC Discovery (use as issuer) | `https://login.microsoftonline.com/{tenant}/v2.0/.well-known/openid-configuration` |
| JWKS (signature verification) | `https://login.microsoftonline.com/{tenant}/discovery/v2.0/keys` |
| Token Endpoint | `https://login.microsoftonline.com/{tenant}/oauth2/v2.0/token` |
| Authorization Endpoint | `https://login.microsoftonline.com/{tenant}/oauth2/v2.0/authorize` |
| Logout Endpoint | `https://login.microsoftonline.com/{tenant}/oauth2/v2.0/logout` |
| Multi-Tenant (common) | Replace `{tenant}` with: `common` |
| Any Microsoft Account | Replace `{tenant}` with: `consumers` |
| Any Org Account | Replace `{tenant}` with: `organizations` |
```

*Guide covers Kong Gateway 3.7 with the openid-connect plugin (Enterprise) and Microsoft Entra ID (Azure AD v2.0 endpoints). Refer to [docs.konghq.com/hub/kong-inc/openid-connect](https://docs.konghq.com/hub/kong-inc/openid-connect/) for the latest plugin schema.*

---

## Related

- [Kong AI Gateway — Complete End-to-End Guide](../08-kong-ai-gateway-guide.md) — core Kong plugins, routing, caching, rate limiting, and production deployment patterns.
- [AI Gateway Full Comparison](../05-ai-gateway-full-comparison.md) — feature matrix and selection guide for enterprise API gateways handling LLM integrations.
- [AI Gateway Multi-Tenant Multi-Cloud](../06-ai-gateway-multitenant-multicloud.md) — isolation, billing, and multi-region deployment for SaaS AI platforms.
- [Enterprise AI Gateway Architecture](../07-enterprise-ai-gateway.md) — high-availability, observability, cost governance, and zero-trust patterns at scale.
