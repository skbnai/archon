---
title: "AWS & Entra ID Federation: Registration, OIDC & Token Exchange"
doc_type: guide
domain: trust
status: current
topic_id: 4b-aws-entra-federation-patterns
last_reviewed: 2026-07-27
maturity: practitioner
supersedes: [docs/ai-security-governance/policy/Vol4b_AWS_Entra_Federation_Patterns.md]
tags: [authorization, aws, entra-id, oidc, oauth]
covers_version: "as of 2026"
---

Entra ID application registration and OIDC federation configuration, ADFS legacy claim normalization, and OAuth 2.0 On-Behalf-Of token exchange for agents calling downstream enterprise APIs.

## Entra ID Application Registration

The enterprise AI authorization platform is registered as a web application in Entra ID with application-level Microsoft Graph permissions for `User.Read.All`, `Group.Read.All`, and `Directory.Read.All` (the last required for group GUID resolution in the PIP Lambda). The application exposes three API scopes — `agent.invoke`, `tool.execute`, and `data.read` — and its token configuration adds optional claims to the access token (`groups` as GUIDs or names below 200 groups, `upn`, `department`, `employee_id`, `country`, and `onprem_sid` for hybrid ADFS environments) and to the ID token (`email`, `preferred_username`). Coarse-grained application roles (`Finance.Approver`, `Data.Reader`, `Agent.User`, `Agent.Admin`) provide an additional authorization dimension. A Conditional Access policy targets this application specifically, requiring MFA for all users and either a compliant device or hybrid Azure AD join.

## OIDC Federation Configuration

The Lambda Authorizer validates both Entra ID and legacy ADFS tokens through OIDC discovery. It caches the JWKS for each issuer (Entra ID's `.well-known/openid-configuration` or the ADFS equivalent) for the lifetime of the Lambda instance, decodes the token header and unverified claims to determine the issuer, and routes to the correct JWKS and expected audience/issuer set based on whether the issuer matches `login.microsoftonline.com`/`sts.windows.net` (Entra ID) or the enterprise ADFS host:

```python
@lru_cache(maxsize=1)
def get_jwks(issuer: str = "entra") -> dict:
    discovery_url = DISCOVERY_URL if issuer == "entra" else ADFS_DISCOVERY_URL
    discovery = requests.get(discovery_url, timeout=5).json()
    return requests.get(discovery["jwks_uri"], timeout=5).json()

def validate_token(token: str) -> dict:
    header = jwt.get_unverified_header(token)
    unverified = jwt.decode(token, options={"verify_signature": False})
    issuer = unverified.get("iss", "")

    if "login.microsoftonline.com" in issuer or "sts.windows.net" in issuer:
        jwks = get_jwks("entra")
        valid_audiences = [ENTRA_APP_ID, f"api://{ENTRA_APP_ID}"]
        valid_issuers = [
            f"https://login.microsoftonline.com/{ENTRA_TENANT_ID}/v2.0",
            f"https://sts.windows.net/{ENTRA_TENANT_ID}/",
        ]
    elif "adfs.bank.com" in issuer:
        jwks = get_jwks("adfs")
        valid_audiences = ["https://api.bank.com"]
        valid_issuers = ["https://adfs.bank.com/adfs"]
    else:
        raise ValueError(f"Unknown issuer: {issuer}")

    public_key = get_public_key_from_jwks(jwks, header["kid"])
    claims = jwt.decode(
        token, public_key, algorithms=["RS256", "ES256"],
        audience=valid_audiences, issuer=valid_issuers,
        options={"verify_exp": True, "verify_nbf": True, "verify_iat": True,
                 "require": ["exp", "iat", "sub", "iss", "aud"]},
    )
    validate_jti_not_replayed(claims.get("jti", ""), claims["exp"])
    return claims

def validate_jti_not_replayed(jti: str, exp: int):
    # Store jti in ElastiCache for the token lifetime; if it already exists, a replay was detected
    ttl = exp - int(time.time())
    result = r.set(f"jti:{jti}", "1", ex=ttl, nx=True)
    if not result:
        raise ValueError(f"JWT replay detected: {jti}")
```

**ADFS federation deep dive.** Legacy ADFS environments require additional configuration because ADFS tokens use different claim schemas, group references, and token lifetimes than Entra ID:

| Configuration Item | Entra ID | ADFS 4.0/5.0 | Normalization Action |
|---|---|---|---|
| User identifier | `sub` (GUID), `upn` | `upn`, `samaccountname` | Normalize to `upn` as the primary key |
| Groups | `groups` (GUID array) | `group` (DN strings or SAM names) | Parse DN or resolve SAM to capability |
| Token lifetime | Default 1 hour (configurable) | Default 8 hours (configurable) | Enforce max 1 hour at the normalization layer |
| Audience | App client ID GUID | Relying Party URI | Map both to a `BANK_AI_PLATFORM` constant |
| MFA claim | `amr: ['mfa', 'pwd', 'rsa']` | `authmethodsreferences` | Normalize to an `mfa_verified` boolean |
| Department | `department` (direct claim) | `department` (AD attribute — may not be in token) | SCIM lookup if not present in the token |
| Custom attributes | `extension_*` prefix | Custom claim rules in ADFS | Both normalized to canonical snake_case |
| Token signing | RS256, ES256 (tenant JWKS) | RS256 (ADFS federation metadata) | Both validated via JWKS; separate endpoints |

## OAuth 2.0 On-Behalf-Of and Token Exchange

When an agent must call downstream enterprise APIs (SAP, Salesforce, internal microservices) on behalf of the user, it needs a token scoped to those APIs that carries the user's identity. OAuth 2.0 On-Behalf-Of (OBO) flow and RFC 8693 Token Exchange are the standards for this.

**On-Behalf-Of flow for agent-to-enterprise-API calls.** After the user authenticates and receives an access token scoped to the AI Platform, the Agent Runtime invokes with that token and issues an OBO request to Entra ID: a `jwt-bearer` grant with the agent service's client credentials, the user's access token as the assertion, `requested_token_use=on_behalf_of`, and the target API's scope. Entra ID validates that the agent service has OBO permission for that API, that the user has consented to the agent acting on their behalf, and that the user is not blocked from the API, then returns a new access token whose `sub` preserves the user's identity, whose `aud` is the target API, whose `scp` reflects the user's own entitlement, and which carries an `act` claim (`{"sub": "agent-service-id"}`) per RFC 8693. The target API validates the OBO token, logging the action under the user's identity (`sub`) while the audit trail shows the agent acted on the user's behalf (`act`). Critically, Cedar authorization runs on the agent side *before* the OBO call is even made: it verifies the agent is authorized to call the target API on behalf of this user and that the user holds the required capability (e.g., `can_access_sap`).

**Token exchange implementation.** The exchange function first performs a Cedar pre-authorization check — can this agent call this API on behalf of this user? — before retrieving agent service credentials from Secrets Manager and performing the actual OBO exchange against the Entra ID token endpoint:

```python
def exchange_token_for_api(user_token: str, target_api: str, canonical_claims: dict, agent_id: str) -> str:
    authz = avp.is_authorized(
        policyStoreId=POLICY_STORE_ID,
        principal={"entityType": "BankAI::Agent", "entityId": agent_id},
        action={"actionType": "BankAI::Action", "actionId": "ExchangeTokenFor"},
        resource={"entityType": "BankAI::APITarget", "entityId": target_api},
        context={"contextMap": {
            "delegatedUserId": {"string": canonical_claims["principal"]["id"]},
            "targetApiCapability": {"string": f"can_access_{target_api.lower()}"},
            "userHasCapability": {
                "boolean": f"can_access_{target_api.lower()}" in canonical_claims["capabilities"]
            },
        }},
    )
    if authz["decision"] != "ALLOW":
        raise PermissionError(f"Agent not authorized to exchange token for {target_api}")

    secret = secrets.get_secret_value(SecretId=f"entra-agent-credentials/{target_api}")
    agent_creds = json.loads(secret["SecretString"])

    response = requests.post(TOKEN_ENDPOINT, data={
        "grant_type": "urn:ietf:params:oauth:grant-type:jwt-bearer",
        "client_id": agent_creds["client_id"],
        "client_secret": agent_creds["client_secret"],
        "assertion": user_token,
        "requested_token_use": "on_behalf_of",
        "scope": f"https://{target_api}/.default",
    }, timeout=10)
    if response.status_code != 200:
        raise RuntimeError(f"OBO exchange failed: {response.json()}")

    obo_token = response.json()["access_token"]
    log_token_exchange(agent_id, canonical_claims["principal"]["id"], target_api)
    return obo_token
```

## Related

- [AWS/Entra Federation Patterns (Part 2)](parts/30-4b-aws-entra-federation-patterns-part2.md) — VPC endpoints and network security, IAM Identity Center dual-plane integration, cross-account architecture, and authorization disaster recovery
- [RAG, Memory & Data Authorization](29-rag-memory-data-authorization.md)
- [AWS Implementation & Governance](31-aws-implementation-governance.md)
