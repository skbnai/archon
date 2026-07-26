---
title: "Foundations: What Is an Agent Skill?"
date_created: 2026-07-24
last_reviewed: 2026-07-24
status: current
domain: agentic-systems
doc_type: concept
topic_id: foundations-what-is-an-agent-skill
supersedes: ["docs/agentic-systems/skill/enterprise/01-foundations-what-is-an-agent-skill.md"]
---

# Part 1 — Foundations: What Is an Agent Skill?

## 1.1 Definition

An **Agent Skill** is a reusable, named, versioned package of procedural knowledge — instructions, optional executable resources, and metadata — that an agent runtime can **discover, load on demand, and apply** to a class of task, rather than baking that knowledge permanently into the system prompt or into application code.

The defining architectural property is **progressive disclosure**: at rest, only a Skill's *name* and *description* (a few dozen tokens) sit in the agent's context. When a task matches, the agent (via a filesystem/code-execution tool, an API call, or a registry lookup) loads the full instructions — and, if the skill is large, loads only the specific reference file it needs (e.g., a `forms.md` inside a larger `pdf` skill), not the whole bundle. This is explicitly how Anthropic's reference implementation works, and it is the same mechanism Google ADK, Azure Foundry, and AWS AgentCore now implement, even though each calls the surrounding infrastructure something different (Skill Registry, Toolbox Skills API, curated skills catalog, respectively).

**Why this matters architecturally:** without progressive disclosure, every additional capability an enterprise gives its agents linearly inflates the system prompt, degrading latency, cost, and — past a certain point — instruction-following accuracy. Skills let the *addressable* capability surface of an agent grow effectively unbounded while the *loaded* context stays small and task-relevant.

## 1.2 Why Skills exist (the problem they solve)

Before Skills, enterprises building agents had three bad options:

1. **One giant system prompt** containing every policy, procedure, and edge case the agent might need — expensive, slow, prone to instruction conflicts, and a nightmare to update (change one rule, redeploy every agent that embeds it).
2. **One bespoke agent per use case** — duplicated boilerplate, duplicated tool wiring, no capability reuse, and an N-times maintenance burden as N grows.
3. **Tool descriptions alone** — a general-purpose MCP server exposes *what* is callable, but not the enterprise's opinion on *how* and *when* to use it, what the failure modes are, or what "good" looks like for this org specifically.

Skills solve this by **decoupling behavioral knowledge from agent code and from the base model**. This is precisely the framing both Anthropic and Microsoft Foundry use publicly: a support agent's escalation policy, a code-review agent's checklist, a sales agent's messaging constraints — encode each once, centrally, and every agent that needs it references the same versioned artifact instead of a copy baked into its own prompt or codebase. When the policy changes, you update the skill once instead of redeploying every consuming agent.

## 1.3 Philosophy

Three design principles recur across every mature implementation studied (Anthropic, AWS, Azure, Google):

1. **Progressive disclosure over exhaustive context.** Load metadata always; load full content on demand; load deep reference material only when the specific sub-task requires it.
2. **Skills as portable, inspectable artifacts, not opaque model behavior.** A Skill is a folder of Markdown and scripts a human can read, diff, review, and version-control — the same review discipline as code, not the same trust model as a black-box fine-tune.
3. **Composability over monoliths.** A well-designed Skill does one coherent thing well and can be combined with other Skills and Tools, rather than trying to be a complete agent on its own (see Part 7 in file `07`).

## 1.4 Skill vs. adjacent concepts

This is the section enterprises get wrong most often — using "Skill" as a catch-all for anything an agent can do. Precise boundaries:

### Skill vs. Tool

- A **Tool** is an atomic, typed, callable operation with a fixed input/output contract — `get_order_status(order_id)`. It has no opinion about *when* to be used.
- A **Skill** is procedural knowledge that may *reference* one or more Tools, plus the judgment about when, why, and in what sequence to call them, plus non-tool content (policy text, examples, decision trees).
- Rule of thumb: if removing the item would only remove a *capability*, it's a Tool. If removing it would remove *judgment* about existing capabilities, it's a Skill.

### Skill vs. Workflow

- A **Workflow** is a specific sequence of steps, often with a deterministic control-flow representation (a Flow, a Step Function, an Agentforce Script, a Joule Studio pipeline).
- A Skill *can contain* a workflow description in its instructions ("first do X, then Y, unless Z"), but a Skill is not itself the execution engine — it's the knowledge that tells the agent (or a downstream deterministic workflow engine) what to do.
- In practice: deterministic, compliance-critical sequences (e.g., "always run KYC before disbursing funds") should be encoded as an actual workflow/flow with enforced control flow, not merely as skill instructions the model might not follow exactly. Salesforce's Agentforce Script and SAP's hybrid reasoning are explicit responses to this — encoding rule-based determinism *alongside* natural-language instructions rather than relying on the model to always follow prose correctly.

### Skill vs. Agent

- An **Agent** is the runtime loop — the thing that plans, selects skills/tools, executes, and reflects.
- A Skill has no independent runtime; it is inert until an agent loads and interprets it. An agent can consume many skills; a skill (in the base Anthropic/AAIF model) does not "run" other skills — though enterprise platforms increasingly support skill-to-skill and skill-to-subagent invocation (see file `07`, Skill Composition).

### Skill vs. Prompt

- A **Prompt** (in the "system prompt" or "prompt template" sense) is typically a single, monolithic, always-loaded block of instructions for one agent.
- A **Skill** is modular, independently versioned, conditionally loaded, and — critically — **reusable across multiple agents and even multiple platforms** if it conforms to the open spec.
- A Skill's SKILL.md *contains* prompt-like instruction text, but the packaging, discovery, and lifecycle model is what differentiates it from "a prompt."

### Skill vs. MCP Server

- An **MCP Server** is infrastructure: a process exposing Tools/Resources/Prompts over a protocol, with its own connection, auth, and versioning lifecycle.
- A **Skill** is content: it may *reference* an MCP server's tools by name inside its instructions, but does not itself implement network calls, auth handshakes, or protocol framing.
- Do not build "a skill" when what you actually need is "a new MCP server" — see Part 6 anti-patterns in file `06`. Conversely, do not build a new MCP server just to encode a procedure that involves tools you already have — that's a Skill.

### Skill vs. Plugin

- "Plugin" is heavily overloaded across ecosystems. In the Claude Code / Skills ecosystem, a **Plugin** is typically a distribution mechanism (a marketplace-installable bundle that can include one or more Skills, MCP server configs, and slash commands together). A Skill is a *content unit*; a Plugin is a *packaging/distribution unit* that may bundle several content units.

### Skill vs. Capability

- **Capability** is the informal, business-facing term ("this agent has the capability to process refunds"). A Capability is typically realized by *some combination* of one or more Skills and Tools. Enterprise capability registries (see file `06`) map business capabilities to the underlying Skills/Tools that implement them — this mapping is itself valuable governance metadata.

### Skill vs. Function

- A **Function** (in the "function calling" sense) is the technical mechanism by which a model requests a Tool invocation. It is a synonym for Tool at the protocol level, not for Skill.

### Skill vs. API

- An **API** is the backend interface a Tool or MCP server wraps. Skills never talk to APIs directly; that responsibility belongs to Tools/MCP servers/backend services (see the decision matrix in file `04`).

## 1.5 When to create a new Skill vs. reuse an existing one

Decision checklist, in order:

1. **Does an existing Skill in the registry already cover this domain and audience?** If yes, extend it (add a reference file, add an example) rather than fork. Forking creates the duplication problem addressed at length in file `06`.
2. **Is the new need actually a missing Tool, not a missing Skill?** If the agent has the judgment but lacks the capability, add a Tool to an existing MCP server or Toolbox; don't wrap it in a new Skill just to introduce it.
3. **Is the procedure genuinely reusable across more than one agent/use case?** If it's a one-off, single-agent instruction, it may not be worth registry-level packaging overhead — a scoped prompt fragment may suffice until reuse is proven (start with evaluation, per Anthropic's own build guidance: identify a concrete capability gap by running representative tasks before authoring a skill).
4. **Does the procedure require its own audience, owner, and lifecycle distinct from anything existing?** (e.g., a new regulatory domain, a new business unit's escalation policy). If yes, new Skill.
5. **Would combining this with an existing Skill create instruction conflicts or context bloat** (mutually exclusive contexts, e.g., US tax rules vs. EU tax rules)? If yes, prefer a *new, separate* Skill over cramming an `if/else` into one bloated file — Anthropic's own authoring guidance explicitly recommends splitting mutually-exclusive content into separate files/skills to reduce token usage and avoid the model conflating contexts.

The overarching test used across every platform studied: **a Skill should be scoped narrowly enough that its name and one-paragraph description alone let the agent (and a human reviewer) correctly predict when it will and won't be used.** If you can't write that description in a paragraph, the Skill is trying to do too much and should be split.

## Related

- [Skill Execution Lifecycle & Tracing](30-execution-lifecycle-and-tracing.md) — the next section in this series.
