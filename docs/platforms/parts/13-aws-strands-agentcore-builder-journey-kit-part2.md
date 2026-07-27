---
title: "AWS Strands & Bedrock AgentCore Production Builder Journey Kit (Part 2: Memory, Gateway/MCP, Identity/Auth, Multi-Agent Patterns)"
doc_type: guide
domain: platforms
status: draft
topic_id: aws-strands-agentcore-builder-journey-kit-part2
last_reviewed: 2026-07-27
maturity: practitioner
supersedes: []
tags: [aws, agentcore, strands, mcp, observability, compliance, production]
covers_version: "N/A"
---

> **Known issue:** some fenced code examples on this page were flattened during the original PDF-to-markdown conversion (lost line breaks/indentation, stray artifact characters) and need reformatting. Tracked in migration/WAVE6_BATCH1_STATUS.md (repo root).

*Part 2 of 3 of [AWS Strands & Bedrock AgentCore Production Builder Journey Kit](../13-aws-strands-agentcore-builder-journey-kit.md). Continued in [Part 3](13-aws-strands-agentcore-builder-journey-kit-part3.md).*

## **AgentCore Gateway & MCP**

Tool Server · OAuth · OpenAPI · Lambda · Fargate · OpenShift

### **5.1 Gateway Core Concepts**

AgentCore Gateway is a **fully managed MCP server** . It acts as the centralized tool-access layer between agents and backend APIs/functions. Gateway handles: protocol translation (MCP ↔ REST/Lambda), inbound OAuth auth, outbound credential injection, and semantic tool search across thousands of tools.

- Each Gateway has a **unique MCP endpoint URL** usable by any MCP client.

- A Gateway can have multiple **Targets** (OpenAPI spec, Lambda, Smithy, Remote MCP).

- Built-in tool: x_amz_bedrock_agentcore_search for semantic tool discovery.

### **5.2 Creating a Gateway with OpenAPI Target**

###### **create_gateway.py**

```
import boto3
```

```
agentcore = boto3.client("bedrock-agentcore-control", region_name="us-east-1")
```

```
# Step 1: Create credential provider (for outbound auth to your API)
cred_provider = agentcore.create_agent_runtime_credential_provider(
    name="my-api-key-provider",
```

```
    credentialProviderType="API_KEY",
    apiKeyCredentialProvider={
```

```
        "apiKey": "Bearer my-secret-api-key",
```

- `"headerName": "Authorization"`

```
    }
)
# Step 2: Create Gateway (inbound: OAuth via Cognito)
gateway = agentcore.create_gateway(
    name="enterprise-tool-gateway",
    protocolType="MCP",
    authorizerType="OAUTH",  # or "AWS_IAM" for SigV4
    oauthConfig={
        "allowedAudience": ["my-agent-client"]
    },
    executionRoleArn="arn:aws:iam::123456789:role/GatewayExecRole"
)
# Step 3: Add OpenAPI target
target = agentcore.create_gateway_target(
    gatewayIdentifier=gateway["gatewayId"],
```

```
        "issuerUrl": "https://cognito-idp.us-east-1.amazonaws.com/us-east-1_XXXXX",
```

```
    name="orders-api",
    targetType="OPENAPI",
    openApiConfig={
        "inlineContent": open("orders_openapi.json").read(),
        "serverUrl": "https://api.example.com/v1"
    },
    credentialProviderId=cred_provider["credentialProviderId"]
)
```

### **5.3 Connecting Agent to Gateway via MCP**

###### **agent_with_gateway.py**

```
from strands.mcp import MCPClient
from bedrock_agentcore.identity.auth import get_sigv4_token  # or OAuth token
```

`#` II `Using SigV4 auth (Runtime` -> `Gateway, IAM-to-IAM)` IIIIIIIIIIIIIIIIII

```
from mcp_proxy_aws import SigV4MCPProxy  # MCP Proxy for AWS
```

```
with SigV4MCPProxy(endpoint_url="https://<gateway-id>.bedrock-agentcore.us-east-1.amazonaws.com") a
s proxy:
```

`tools = proxy.list_tools() agent = Agent( model="us.anthropic.claude-sonnet-4-20250514", system_prompt="You are an enterprise assistant with access to company tools.", mcp_clients=[proxy]   # Strands auto-converts MCP tools` -> `@tool functions ) result = agent("List all open orders for customer C-1001")`

###### II **NOTE**

**IAM vs OAuth choice** : Use IAM SigV4 when agent and gateway are in the same AWS account — simpler, no token exchange overhead. Use OAuth (M2M) when you need per-agent fine-grained scopes or cross-account/cross-tenant calls.

### **5.4 API Gateway MCP Proxy Integration**

Amazon API Gateway now natively supports the MCP proxy capability, allowing existing REST APIs to become MCP tools without code changes:

###### **apigateway_mcp.yaml**

```
# CloudFormation snippet — API Gateway with MCP Proxy
Resources:
  MyMCPProxy:
    Type: AWS::ApiGateway::RestApi
      Name: OrdersAPIMCPProxy
  MCPProxyResource:
    Type: AWS::ApiGateway::Resource
      RestApiId: !Ref MyMCPProxy
      ParentId: !GetAtt MyMCPProxy.RootResourceId
      PathPart: "{proxy+}"
```

```
  MCPProxyMethod:
    Type: AWS::ApiGateway::Method
      RestApiId: !Ref MyMCPProxy
      ResourceId: !Ref MCPProxyResource
      HttpMethod: ANY
      AuthorizationType: AWS_IAM       # SigV4 inbound auth
      Integration:
        Type: AWS_PROXY
        IntegrationHttpMethod: POST
        Uri: !Sub "arn:aws:apigateway:${AWS::Region}:bedrock-agentcore:path/gateways/${GatewayId}/i
nvoke"
        Credentials: !GetAtt APIGWRole.Arn
```

### **5.5 Deploying MCP Server on Fargate / OpenShift**

###### **Dockerfile**

```
# Dockerfile for custom MCP server (Fargate / OpenShift)
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir fastmcp bedrock-agentcore uvicorn
COPY . .
EXPOSE 8080
CMD ["uvicorn", "mcp_server:app", "--host", "0.0.0.0", "--port", "8080"]
```

###### **mcp_server.py**

```
# mcp_server.py — FastMCP on Fargate with AgentCore Gateway auth
from fastmcp import FastMCP
from bedrock_agentcore.identity.auth import validate_oauth_token  # middleware helper
mcp = FastMCP("company-tools")
@mcp.tool()
def get_inventory(product_id: str) -> dict:
    """Returns inventory levels for a product."""
    return {"product_id": product_id, "quantity": 142, "warehouse": "WH-001"}
# Mount OAuth validation middleware
app = mcp.streamable_http_app()  # Returns FastAPI app with MCP routes
# Register with AgentCore Gateway as Remote MCP target:
# agentcore.create_gateway_target(targetType="REMOTE_MCP",
#   remoteMcpConfig={"url": "https://fargate-alb.example.com/mcp"})
```

###### I **BEST PRACTICE**

When running MCP servers on OpenShift, use OpenShift Routes with TLS passthrough or edge termination. Ensure the container port 8080 is exposed via a Service of type ClusterIP, and register the Route URL as the Remote MCP target URL in AgentCore Gateway.

##### **CHAPTER 6**

## **Identity, Auth & Trust Layers**

IAM · OAuth 2.1 · M2M · SigV4 · Cross-Tenant · Policy

### **6.1 AgentCore Identity Overview**

AgentCore Identity provides a two-sided authentication model: **Inbound** (who can call your agent/gateway) and **Outbound** (how your agent calls downstream services). This dual-sided model is the security backbone of enterprise multi-agent deployments.

|**Auth Method**|**Description**|**Used For**|
|---|---|---|
|Inbound — IAM SigV4|AWS accounts, roles calling Runtime/Gateway. Best for<br/>internal M2M.|Runtime, Gateway|
|Inbound — OAuth 2.1|External users, partner agents, third-party systems. Cognito<br/>or any IdP.|Gateway (MCP spec requires OAuth)|
|Outbound — API Key|Agent calling external REST APIs with static key.|Gateway->OpenAPI target|
|Outbound — OAuth M2M|Agent acquires token via client_credentials grant to call<br/>protected APIs.|Gateway->OAuth-protected APIs|
|Outbound — IAM Role|Agent assumes IAM role to call AWS services (Lambda, S3,<br/>DynamoDB).|Gateway->Lambda target|

### **6.2 Inbound: Cognito OAuth + JWT Validation**

###### **cognito.tf**

```
# Terraform — Cognito User Pool for AgentCore Gateway inbound auth
resource "aws_cognito_user_pool" "agents" {
  name = "agentcore-users"
}
resource "aws_cognito_resource_server" "gateway" {
  identifier   = "https://api.example.com"
  name         = "AgentCore Gateway"
  user_pool_id = aws_cognito_user_pool.agents.id
  scope {
    scope_name        = "tools:invoke"
    scope_description = "Invoke agent tools"
  }
}
resource "aws_cognito_user_pool_client" "agent_client" {
  name                                 = "agent-m2m-client"
  user_pool_id                         = aws_cognito_user_pool.agents.id
  generate_secret                      = true
  allowed_oauth_flows                  = ["client_credentials"]
```

```
  allowed_oauth_scopes                 = ["https://api.example.com/tools:invoke"]
  supported_identity_providers         = ["COGNITO"]
  explicit_auth_flows                  = ["ALLOW_REFRESH_TOKEN_AUTH"]
}
```

### **6.3 Outbound: M2M Token Acquisition in Agent**

###### **outbound_auth.py**

```
from bedrock_agentcore.identity.auth import requires_access_token
# Decorator-based M2M token acquisition (cached, auto-refreshed)
@requires_access_token(
    provider_name="my-cognito-provider",  # Registered in AgentCore Identity
    scopes=["https://api.example.com/tools:invoke"],
    auth_flow="M2M",  # client_credentials grant
)
def call_protected_api(*, access_token: str):
    import httpx
    response = httpx.get(
        "https://api.example.com/v1/data",
        headers={"Authorization": f"Bearer {access_token}"}
    )
    return response.json()
```

### **6.4 MCP Proxy for AWS (SigV4 Bridge)**

The AWS MCP Proxy is a client-side library that transparently signs MCP requests with SigV4, bridging the gap between standard MCP clients and AgentCore's IAM-authenticated endpoints:

###### **sigv4_mcp.py**

```
pip install mcp-proxy-aws
# In agent code — automatic SigV4 signing, no manual credential handling
from mcp_proxy_aws import SigV4MCPProxy
import boto3
session = boto3.Session(region_name="us-east-1")
with SigV4MCPProxy(
    endpoint_url="https://<gateway-id>.bedrock-agentcore.us-east-1.amazonaws.com",
    aws_session=session,          # Uses instance profile, env vars, or explicit creds
    service="bedrock-agentcore"   # Used for SigV4 signing scope
) as client:
    tools = client.list_tools()
    result = client.call_tool("get_inventory", {"product_id": "SKU-001"})
```

### **6.5 Cross-Tenant A2A Trust (JWT Federation)**

Cross-tenant A2A allows agents in **different AWS accounts or organizations** to call each other. The trust model uses JWT bearer tokens issued by the calling tenant's IdP, validated by the receiving tenant's AgentCore Runtime authorizer:

###### **cross_tenant_a2a.py**

```
# Calling tenant: acquire JWT and invoke remote agent
```

```
import boto3, httpx
```

```
# Step 1: Get token from own IdP (Cognito or OIDC provider)
token_response = httpx.post(
    "https://cognito-idp.us-east-1.amazonaws.com/POOL/.well-known/token",
    data={
        "grant_type": "client_credentials",
        "client_id": PARTNER_CLIENT_ID,
        "client_secret": PARTNER_CLIENT_SECRET,
        "scope": "cross-tenant/agent:invoke"
    }
)
jwt_token = token_response.json()["access_token"]
# Step 2: Call remote agent runtime (cross-tenant)
remote_client = boto3.client("bedrock-agentcore", region_name="us-east-1")
response = remote_client.invoke_agent_runtime(
    agentRuntimeEndpointArn="arn:aws:bedrock-agentcore:us-east-1:PARTNER_ACCT:...",
    sessionId=f"cross-tenant-{my_tenant_id}-{session_id}",
    payload=json.dumps({"prompt": "Execute cross-org workflow", "caller": my_tenant_id}),
    # JWT passed via additional headers (Runtime authorizer validates iss, aud, exp)
    additionalHeaders={"Authorization": f"Bearer {jwt_token}"}
)
```

###### II **WARNING**

**Cross-tenant trust hardening** : (1) Validate iss claim against allowlist of trusted issuers. (2) Validate aud matches your runtime ARN. (3) Enforce exp with 5-minute clock skew max. (4) Use short-lived tokens (max 1h). (5) Log all cross-tenant invocations to CloudTrail with tenant context.

### **6.6 Policy Engine: Action-Level Authorization**

AgentCore Policy intercepts *every* tool call *before* execution. It works alongside Identity and Gateway to enforce business rules at runtime:

###### **policy.json**

```
        "attribute": "amount",
        "operator": "LESS_THAN_OR_EQUAL",
        "value": 10000
      }
    },
    {
      "ruleType": "DENY",
      "condition": {
        "userRole": { "notIn": ["ADMIN", "MANAGER"] },
        "toolName": "delete_record"
      },
      "message": "Only admins and managers can delete records."
    }
  ]
}
```

##### **CHAPTER 7**

## **Multi-Agent Patterns**

Supervisor · A2A · Cross-Tenant · Swarm

### **7.1 Supervisor / Sub-Agent Pattern**

The **supervisor pattern** is the most common multi-agent topology for enterprise workflows. A supervisor agent orchestrates specialized sub-agents via tool invocations. Each sub-agent has a focused capability (research, coding, data, compliance). The supervisor never has direct tool access — it delegates everything.

###### **supervisor_pattern.py**

```
from strands import Agent, tool
```

`#` II `Sub-agents as @tool functions` IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII `@tool def research_agent(query: str) -> str: """Performs deep research on a topic using web search and RAG.""" specialist = Agent( model="us.anthropic.claude-sonnet-4-20250514", system_prompt="You are an expert researcher. Always cite sources.", tools=[web_search, rag_retrieval] ) return specialist(query).message @tool def coding_agent(task: str) -> str: """Writes, reviews, and executes code.""" specialist = Agent( model="us.anthropic.claude-sonnet-4-20250514", system_prompt="You are a senior software engineer.", tools=[code_interpreter, file_write] ) return specialist(task).message @tool def compliance_agent(content: str) -> dict: """Reviews content for regulatory compliance issues.""" specialist = Agent( model="us.anthropic.claude-opus-4-20250514", system_prompt="You are a regulatory compliance expert. Check for PII, bias, legal issues.", tools=[guardrail_check, policy_lookup] ) return {"review": specialist(content).message, "approved": True} #` II `Supervisor` IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII `supervisor = Agent( model="us.anthropic.claude-opus-4-20250514", system_prompt="""You are an enterprise orchestrator. For complex tasks: use research_agent first, then coding_agent if code needed, always pass output through compliance_agent before returning.""",`

```
    tools=[research_agent, coding_agent, compliance_agent]
)
```

### **7.2 A2A Protocol: Cross-Runtime Communication**

A2A (Agent-to-Agent) protocol enables agents deployed on *different* AgentCore Runtimes to call each other as peers — each with its own identity and session:

###### **a2a_protocol.py**

`#` II `Server-side: expose agent as A2A executor` IIIIIIIIIIIIIIIIIIIIIIII `from strands import Agent from strands.a2a import StrandsA2AExecutor from bedrock_agentcore.runtime import serve_a2a agent = Agent( model="us.anthropic.claude-sonnet-4-20250514", system_prompt="You are a specialized data analysis agent." ) # Registers /.well-known/agent.json + A2A invoke endpoint serve_a2a(StrandsA2AExecutor(agent))`

`#` II `Client-side: call remote A2A agent` IIIIIIIIIIIIIIIIIIIIIIIIIIIIIII `from strands.a2a import A2AClient # A2A client discovers capabilities from /.well-known/agent.json a2a_client = A2AClient(`

```
    endpoint_url="https://<runtime-endpoint>.bedrock-agentcore.us-east-1.amazonaws.com",
    auth_token=get_bearer_token()  # OAuth or SigV4 signed
)
result = a2a_client.send_message(
    task="Analyze sales data for Q1 2026",
    context={"tenant_id": "ACME-CORP"}
)
```

###### II **NOTE**

A2A protocol support in AgentCore Runtime is GA. Broader A2A support (across Memory, Gateway, etc.) is on the roadmap. Use A2A for cross-runtime calls; use agents-as-tools for same-runtime calls.

### **7.3 Agent Swarm (Mesh Topology)**

Strands provides swarm primitives for peer-to-peer multi-agent collaboration without a central supervisor:

###### **swarm.py**

```
from strands.swarm import AgentSwarm
# Each agent in the swarm can call others by capability name
swarm = AgentSwarm(agents={
    "researcher":  research_agent_instance,
    "coder":       coding_agent_instance,
    "validator":   validation_agent_instance,
    "summarizer":  summary_agent_instance,
})
# Swarm resolves routing based on agent card / capability descriptors
```

```
result = swarm.run(
```

```
    task="Build and validate a data pipeline for customer churn prediction",
    entry_agent="researcher"
```

```
)
```

##### **CHAPTER 8**

## **Observability, Tracing & Evaluation**

CloudWatch · Phoenix · OpenInference · Strands Eval · LLM-as-Judge

### **8.1 AgentCore Native Observability (CloudWatch + OTEL)**

AgentCore emits OpenTelemetry spans for every agent invocation, tool call, MCP server request, auth flow, and memory operation. These flow to CloudWatch Transaction Search and the GenAI Observability Dashboard.

###### **cloudwatch_setup.sh**

```
# Enable AgentCore Observability (AWS CLI)
aws bedrock-agentcore update-agent-runtime \
  --agent-runtime-id "runtime-abc123" \
  --observability-config '{
    "enableTracing": true,
    "tracingDestination": "CLOUDWATCH",
    "logLevel": "INFO"
  }'
# View traces
aws logs get-query-results --query-id $(aws logs start-query \
  --log-group-name "/aws/bedrock-agentcore/runtimes/runtime-abc123-DEFAULT" \
  --start-time $(date -d '1 hour ago' +%s) \
  --end-time $(date +%s) \
  --query-string 'fields @timestamp, @message | sort @timestamp desc | limit 50' \
  --query queryId)
```

### **8.2 Arize Phoenix: Self-Hosted LLM Observability**

Arize Phoenix is the recommended open-source LLM observability platform for Strands + AgentCore. It uses OpenTelemetry and OpenInference standards, avoiding vendor lock-in:

###### **phoenix_deploy.sh**

```
# Option A: Docker (development / internal)
docker run -p 6006:6006 -p 4317:4317 arizephoenix/phoenix:latest
# Option B: ECS Fargate (production, with RDS PostgreSQL backend)
# See ECS task definition below
# Option C: AWS EKS / OpenShift
helm repo add arize https://storage.googleapis.com/arize-assets/phoenix/chart
helm install phoenix arize/phoenix \
  --set postgresql.enabled=true \
  --set service.type=LoadBalancer
```

###### **phoenix_ecs_task.json**

```
# ECS Task Definition snippet for Phoenix on Fargate
{
```

```
  "family": "phoenix-prod",
```

```
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "1024", "memory": "2048",
  "containerDefinitions": [{
    "name": "phoenix",
    "image": "arizephoenix/phoenix:latest",
    "portMappings": [
      {"containerPort": 6006, "protocol": "tcp"},
      {"containerPort": 4317, "protocol": "tcp"}
    ],
    "environment": [
      {"name": "DATABASE_URL",
       "value": "postgresql://phoenix:SECRET@rds-endpoint:5432/phoenix"},
      {"name": "PHOENIX_PORT", "value": "6006"},
      {"name": "PHOENIX_GRPC_PORT", "value": "4317"},
      {"name": "PHOENIX_TELEMETRY_ENABLED", "value": "false"}
    ],
    "logConfiguration": {
      "logDriver": "awslogs",
      "options": {
        "awslogs-group": "/ecs/phoenix",
        "awslogs-region": "us-east-1",
        "awslogs-stream-prefix": "phoenix"
```

```
      }
    }
  }]
}
```

### **8.3 Instrumenting Strands with OpenInference**

###### **phoenix_instrumentation.py**

```
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from phoenix.otel import register  # arize-phoenix-otel
```

`#` II `Configure Phoenix as OTEL collector` IIIIIIIIIIIIIIIIIIIIIIIIIIIIII `tracer_provider = register( project_name="strands-agentcore-prod", endpoint="http://phoenix.internal:4317",  # Self-hosted Phoenix gRPC auto_instrument=True,  # Auto-instruments Bedrock calls )`

`#` II `Create Strands agent with trace context` IIIIIIIIIIIIIIIIIIIIIIIIII `agent = Agent( model="us.anthropic.claude-sonnet-4-20250514", system_prompt="You are a production assistant.", tools=[...], trace_attributes={ "session.id": context.session_id,`

```
        "user.id": context.user_id,
        "tenant.id": "ACME-CORP",
        "deployment.env": "production",
        "agent.version": "1.3.2"
    }
)
```

### **8.4 Strands Eval Framework**

Strands includes a built-in evaluation framework for systematic agent testing:

###### **strands_eval.py**

### **8.5 LLM-as-Judge Evaluation**

###### **llm_judge.py**

```
from strands.eval import LLMJudge
# Judge agent evaluates response quality
judge = LLMJudge(
```

```
    model="us.anthropic.claude-opus-4-20250514",  # Use strongest model for judging
    criteria={
```

```
        "accuracy":    "Is the factual content correct and verifiable?",
```

```
        "helpfulness": "Does the response directly address the user's request?",
```

```
        "safety":      "Is the response free of harmful, biased, or misleading content?",
        "conciseness": "Is the response appropriately concise without losing important detail?"
    },
    scale=5  # Score each criterion 1-5
)
# Evaluate a batch of responses
for case in eval_cases:
    judgment = judge.evaluate(
        prompt=case["input"],
        response=case["agent_output"],
        context=case.get("retrieved_context")  # For RAG grounding check
    )
```

```
    print(f"Accuracy: {judgment.accuracy}/5, Safety: {judgment.safety}/5")
```

##### **CHAPTER 9**
