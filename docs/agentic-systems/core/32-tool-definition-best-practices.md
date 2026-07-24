---
title: "Tool Definition Best Practices"
domain: agentic-systems
doc_type: guide
topic_id: tool-definition-best-practices
status: current
supersedes:
  - "docs/agentic-systems/skill/enterprise/05-tool-definition-best-practices.md"
date_created: 2026-07-24
last_reviewed: 2026-07-24
---

# Part 5 — Tool Definitions Inside Skills (+ Deliverable 5: Best-Practice Template)

Tool description quality is, empirically, one of the highest-leverage things an enterprise controls — Salesforce's own Agentforce documentation is explicit that the Atlas Reasoning Engine selects actions based on label and description, and that a vague description leads directly to wrong action selection. AWS AgentCore's "recommendations" capability exists specifically because production traces show tool-description quality as a recurring, fixable failure mode. Treat tool descriptions as a governed artifact, not incidental documentation.

## 5.1 Tool naming

**Convention:** `verb_noun` (snake_case for API/function-calling contexts), namespaced by domain: `orders.get_status`, `orders.cancel`, `payments.refund`.

- **Verb-first** (`get_order_status`) is generally preferable to noun-first (`order_status_getter`) — it mirrors natural-language intent and is what most function-calling conventions (OpenAI, Anthropic, MCP) already assume.
- **Namespacing** (`domain.verb_noun` or `domain_verb_noun`) prevents collisions once an enterprise has hundreds of tools across systems — this is exactly the problem Google ADK's collision-prevention logic and AWS's Agent Registry (a private, governed catalog for agents, tools, skills, and MCP servers) exist to police at scale.
- Avoid vague or overloaded verbs (`process`, `handle`, `manage`) — they don't disambiguate intent for the model or for a human reviewer.
- One tool = one action. `update_or_create_customer` is two tools wearing a trenchcoat; split it (Salesforce's own guidance: "keep actions single-purpose... this makes them reusable across multiple topics").

## 5.2 Tool description — what belongs inside

A production-grade tool description answers, in this order:

1. **Purpose** — one sentence, plain language.
2. **When to use** — the situations that should trigger this tool.
3. **When NOT to use** — explicit negative guidance (this is as important as the positive case and is frequently omitted).
4. **Preconditions** — what must already be true/known (e.g., "requires a valid `customer_id` obtained from `search_customers`").
5. **Postconditions** — what state changes after a successful call (critical for idempotency reasoning and for the agent to avoid redundant calls).
6. **Expected latency** — rough order of magnitude (sub-second vs. multi-second) so the agent/orchestrator can set user expectations or choose async patterns.
7. **Authentication / permissions required** — which scope/role must be present; ties directly to the policy layer (file `09`).
8. **Business constraints** — e.g., "cannot cancel an order after it has shipped."
9. **Safety constraints** — e.g., "never expose full card numbers in the response."
10. **Failure modes** — the specific errors this tool can return and what each means.
11. **Examples / non-examples** — 1–2 concrete calls, plus 1 example of a *similar-looking but wrong* use case, disambiguating from a neighboring tool.
12. **Required context** — what upstream information the caller needs before invoking.
13. **Output expectations / schema explanation** — plain-language walkthrough of the returned shape, not just the raw schema.
14. **Decision boundaries** — for tools with siblings (`refund_full` vs. `refund_partial`), state exactly what distinguishes them.

### Template (Deliverable 5)

```yaml
tool:
  name: orders.cancel_order
  namespace: orders
  version: 1.3.0
  owner: order-management-team@enterprise.com
  summary: >
    Cancels an order that has not yet shipped and issues an automatic
    refund if payment was already captured.
  when_to_use:
    - "Customer explicitly requests cancellation of an unshipped order."
    - "An internal fraud-review workflow instructs cancellation."
  when_not_to_use:
    - "Order status is 'shipped' or 'delivered' — use orders.initiate_return instead."
    - "Customer wants a partial change (e.g., quantity) — use orders.modify_order."
  preconditions:
    - "order_id must be a valid, existing order."
    - "Caller must hold the 'orders:cancel' scope."
  postconditions:
    - "Order status transitions to 'cancelled'."
    - "If payment was captured, a refund is automatically initiated (see payments.refund_status to check progress)."
  expected_latency_ms: 800
  authentication:
    type: oauth2
    required_scopes: ["orders:cancel"]
  business_constraints:
    - "Cannot cancel orders older than 90 days without a manager override flag."
  safety_constraints:
    - "Do not log full payment instrument details in any response or trace."
  failure_modes:
    - code: ORDER_ALREADY_SHIPPED
      meaning: "Order passed the shipping cutoff; cancellation is not possible via this tool."
      agent_guidance: "Inform the user and offer orders.initiate_return instead."
    - code: INSUFFICIENT_SCOPE
      meaning: "Caller identity lacks orders:cancel."
      agent_guidance: "Escalate to a human agent with the required permission."
  parameters:
    order_id:
      type: string
      required: true
      description: "The unique order identifier, typically obtained from orders.search_orders."
      example: "ORD-2026-004821"
    reason_code:
      type: string
      required: true
      enum: ["customer_request", "fraud_review", "inventory_unavailable"]
      description: "Structured reason, used for downstream analytics; do not free-text this."
    notify_customer:
      type: boolean
      required: false
      default: true
      description: "Whether to trigger the customer-facing cancellation email."
  returns:
    type: object
    schema_ref: "https://schemas.enterprise.com/orders/cancel_order_response.json"
    fields_summary:
      status: "New order status string."
      refund:
        - "null if no payment was captured"
        - "object with refund_id and estimated_completion_date if a refund was initiated"
    confidence: "Not applicable — deterministic backend result, not a model-generated field."
    warnings_example: "['Refund initiated but original payment method is expired; refund routed to store credit.']"
    partial_success_semantics: >
      This operation is atomic; there is no partial-success state. Either the
      order is cancelled (with or without a refund side-effect) or the call fails.
  examples:
    - input: { order_id: "ORD-2026-004821", reason_code: "customer_request" }
      output: { status: "cancelled", refund: { refund_id: "RF-991", estimated_completion_date: "2026-07-14" } }
    - non_example:
        scenario: "Order already delivered."
        wrong_tool: "orders.cancel_order"
        correct_tool: "orders.initiate_return"
```

## 5.3 Parameters — how much explanation, and how to structure them

- **Naming**: descriptive, snake_case, consistent across the whole catalog (`customer_id` everywhere, never `cust_id` in one tool and `customerId` in another — inconsistency is a leading cause of duplicate/near-duplicate tools, file `06`).
- **Required vs. optional**: mark explicitly; for every optional parameter, state the default and the *behavioral consequence* of the default, not just its value.
- **Enums over free text** wherever the valid value set is finite and known — this is one of the single highest-value description investments, because it eliminates an entire class of malformed calls and downstream validation failures.
- **Validation constraints** (format, length, pattern) should be in the schema (machine-enforced), *and* summarized in plain language in the description (model-readable reasoning aid) — schema alone is necessary but not sufficient for good agent behavior, since the model reasons over the description before it ever hits schema validation.
- **Examples per parameter** for anything non-obvious (date formats, ID formats, composite structures).

## 5.4 Return values

- **Structured outputs**: always prefer a documented JSON Schema over prose-only description of the return shape.
- **Confidence**: include a confidence/certainty field when the tool itself involves model inference (e.g., a document-classification tool) — omit it (or explicitly mark "not applicable") for deterministic backend results, so the agent doesn't misinterpret a deterministic result as probabilistic.
- **Errors vs. warnings**: distinguish hard failures (call did not succeed, no side effect occurred) from soft warnings (call succeeded, but with a caveat the agent should relay to the user, as in the refund-routed-to-store-credit example above).
- **Partial success**: for any non-atomic operation (batch calls, multi-step backend transactions), explicitly document what state exists if the call is interrupted partway — this is a common source of duplicate-invocation bugs during retries (file `13`/`08` evaluation coverage should specifically test this).

## 5.5 Anti-patterns to avoid at the tool-definition layer

- **Kitchen-sink tools** that accept a dozen optional parameters covering many unrelated operations — split into single-purpose tools instead (directly echoed by Salesforce's "keep actions single-purpose" guidance).
- **Descriptions written for a human reader of API docs, not for a model deciding whether to call the tool** — omit implementation detail (internal service names, DB table names) the model doesn't need and that a security reviewer would rather not have exposed in a prompt-visible surface anyway.
- **Copy-pasted descriptions across near-duplicate tools** — a strong signal that the tools themselves should be consolidated (file `06`).
- **Missing "when NOT to use"** — the majority of observed wrong-tool-selection incidents trace back to two tools with overlapping positive descriptions and no negative disambiguation.
