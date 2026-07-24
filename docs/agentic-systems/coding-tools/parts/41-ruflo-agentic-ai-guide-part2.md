---
title: 'Multi-Agent Orchestration — claude-flow & Beyond (Part 2)'
doc_type: guide
domain: agentic-systems
topic_id: ruflo-agentic-ai-guide-part2
status: current
date_created: 2026-07-24
last_reviewed: 2026-07-24
supersedes: []
---


**This is Part 2 of 2. [Back to Part 1 ←](pathname:///archon/agentic-systems/coding-tools/41-ruflo-agentic-ai-guide) for the beginning.**
    timeoutMs: 60_000,            // per-agent timeout
    retryOnTimeout: true,
    maxRetries: 2,
  },
});
```

---

## 11. Parallelism

### Spawning Concurrent Agents

```javascript
// parallel-agents.js
const \{ ClaudeFlow } = require('claude-flow');

const flow = new ClaudeFlow(\{
  apiKey: process.env.ANTHROPIC_API_KEY,
  model: 'claude-sonnet-4-6',
});

async function parallelFileProcessing(filePaths) \{
  // Process up to 5 files concurrently; serialise the rest
  const CONCURRENCY = 5;
  const results = [];

  for (let i = 0; i < filePaths.length; i += CONCURRENCY) \{
    const batch = filePaths.slice(i, i + CONCURRENCY);

    const batchResults = await Promise.all(
      batch.map(filePath =>
        flow.runAgent(
          \{
            role: 'file-processor',
            instructions: `Analyse this file and extract key information: $\{filePath}`,
            tools: ['file_read', 'memory_write'],
          },
          \{ memoryKey: `result:$\{filePath}` }
        )
      )
    );

    results.push(...batchResults);
    console.log(`Processed batch $\{Math.floor(i / CONCURRENCY) + 1}: $\{batch.length} files`);
  }

  return results;
}
```

### Result Aggregation and Race Condition Prevention

```javascript
// safe-aggregation.js
const \{ Mutex } = require('async-mutex');  // npm install async-mutex

const mutex = new Mutex();
const aggregatedResults = [];

async function safeAggregate(agentResult) \{
  // Serialise writes to prevent concurrent modification
  const release = await mutex.acquire();
  try \{
    aggregatedResults.push(agentResult);
  } finally \{
    release();
  }
}

// In your agent runner:
await Promise.all(
  agents.map(async agent => \{
    const result = await flow.runAgent(agent, {});
    await safeAggregate(result);
  })
);
```

---

## 12. Token Optimisation

### Per-Agent Token Budget

Assign token budgets at the agent level to prevent runaway spend from a single verbose agent.

```javascript
const swarm = await flow.createSwarm(\{
  agents: [
    \{
      role: 'coder',
      tokenBudget: \{
        maxInputTokens: 20_000,
        maxOutputTokens: 4_000,
      },
    },
    \{
      role: 'reviewer',
      tokenBudget: \{
        maxInputTokens: 8_000,
        maxOutputTokens: 1_000,    // reviewers write less than coders
      },
    },
  ],
});
```

### Shared Context Strategies

Agents sharing a large context window (e.g., a codebase) should read from the shared memory store rather than each receiving the full context.

```javascript
// Instead of this (wasteful — N agents each get the full codebase):
const fullCodebase = fs.readFileSync('src/index.ts', 'utf8');  // 50,000 tokens
agents.map(agent => flow.runAgent(agent, \{ context: fullCodebase }));

// Do this (agents retrieve only the relevant sections):
await memory.store('codebase:index', fullCodebase, \{ namespace: 'project' });
// Agent instructions: "Read the relevant sections from memory using memory_read."
// Each agent retrieves only the ~2,000 tokens it actually needs.
```

### Output Length Controls

```javascript
const agent = new Agent(\{
  role: 'summariser',
  instructions: 'Summarise the document in exactly 3 bullet points. Do not exceed 150 words.',
  // Explicit length constraints in the prompt reduce output token spend
  maxOutputTokens: 300,   // hard cap as a backstop
});
```

---

## 13. Cost Optimisation

### Model Routing by Task Complexity

Use the cheapest model capable of the task. Reserve expensive models for tasks that actually require their capability.

```javascript
// cost-optimised-swarm.js
const flow = new ClaudeFlow(\{ apiKey: process.env.ANTHROPIC_API_KEY });

const swarm = await flow.createSwarm(\{
  agents: [
    \{
      role: 'router',
      // Routing decisions do not need a frontier model
      model: 'claude-haiku-4-5',
      instructions: 'Classify the task type and route to the appropriate specialist.',
    },
    \{
      role: 'coder',
      // Complex reasoning benefits from a mid-tier model
      model: 'claude-sonnet-4-6',
      instructions: 'Implement the feature to spec.',
    },
    \{
      role: 'tester',
      // Test generation is pattern-following — haiku is sufficient
      model: 'claude-haiku-4-5',
      instructions: 'Write unit tests for the implementation.',
    },
    \{
      role: 'architect',
      // Architecture decisions with high stakes warrant the best model
      model: 'claude-fable-5',
      instructions: 'Review the architecture and identify systemic risks.',
    },
  ],
});
```

**Model reference (July 2026):**

| Model | Input (per MTok) | Output (per MTok) | Best for in multi-agent |
| ------- | ----------------- | ------------------ | ----------------------- |
| Claude Haiku 4.5 | Low cost | Low cost | Routing, classification, test generation, summarisation |
| Claude Sonnet 4.6 | Moderate | Moderate | Implementation, research, standard reasoning |
| Claude Sonnet 5 | $3 | $15 | Production-quality reasoning, most enterprise tasks |
| Claude Fable 5 | $10 | $50 | Complex architecture decisions, high-stakes reasoning |

For current pricing, see [Models 2026](claude-models-2026.md).

### Cost Tracking Per Workflow

```javascript
// cost-tracker.js
class CostTracker \{
  constructor() \{
    this.records = [];
  }

  record(workflowId, agentRole, usage) \{
    this.records.push(\{
      workflowId,
      agentRole,
      inputTokens: usage.input_tokens,
      outputTokens: usage.output_tokens,
      timestamp: new Date().toISOString(),
    });
  }

  summary(workflowId) \{
    const workflow = this.records.filter(r => r.workflowId === workflowId);
    return \{
      totalInput: workflow.reduce((s, r) => s + r.inputTokens, 0),
      totalOutput: workflow.reduce((s, r) => s + r.outputTokens, 0),
      byAgent: Object.groupBy(workflow, r => r.agentRole),
    };
  }
}

const tracker = new CostTracker();

// Instrument each agent run:
const result = await flow.runAgent(agent, {});
tracker.record('workflow-001', agent.role, result.usage);
```

---

## 14. Guardrails

### Agent Action Whitelists

```javascript
// guardrailed-swarm.js
const AGENT_PERMISSIONS = \{
  coder:    ['file_read', 'file_write', 'bash', 'memory_read'],
  tester:   ['file_read', 'bash', 'memory_read', 'memory_write'],
  reviewer: ['file_read', 'memory_read'],
  queen:    ['spawn_agent', 'memory_read', 'memory_write'],
};

// Enforce at runtime — reject tool calls outside the whitelist
function buildAgent(role) \{
  const allowedTools = AGENT_PERMISSIONS[role] ?? [];
  return new Agent(\{
    role,
    tools: allowedTools,
    onToolCall: (toolName, args) => \{
      if (!allowedTools.includes(toolName)) \{
        throw new Error(`GUARDRAIL: $\{role} is not authorised to call $\{toolName}`);
      }
    },
  });
}
```

### Output Validation

```python
# output_validator.py — validates agent outputs before they leave the system
import re
import json

# Patterns that should never appear in outputs
BLOCKED_PATTERNS = [
    r'\b\d\{4}[- ]?\d\{4}[- ]?\d\{4}[- ]?\d\{4}\b',   # credit card
    r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]\{2,}\b',  # email (when unexpected)
    r'AKIA[0-9A-Z]\{16}',                            # AWS access key
    r'sk-[a-zA-Z0-9]\{40,}',                         # API key pattern
]

def validate_output(output: str, context: dict) -> tuple[bool, list[str]]:
    """Returns (is_valid, list_of_violations)."""
    violations = []
    for pattern in BLOCKED_PATTERNS:
        if re.search(pattern, output):
            violations.append(f"Blocked pattern detected: \{pattern}")
    if len(output) > context.get('max_output_length', 10_000):
        violations.append("Output exceeds maximum allowed length")
    return len(violations) == 0, violations

# Use in your agent pipeline:
is_valid, violations = validate_output(agent_result.output, \{'max_output_length': 5_000})
if not is_valid:
    log_violation(violations)
    raise GuardrailViolation(f"Output blocked: \{violations}")
```

### HITL Gates

```javascript
// hitl-gate.js
async function withHumanApproval(action, actionDescription, \{
  timeoutMs = 300_000,   // 5 minutes
  onTimeout = 'reject',  // 'reject' | 'approve' | 'escalate'
} = {}) \{
  const approvalRequest = await notifyApprover(\{
    description: actionDescription,
    requestedAt: new Date().toISOString(),
  });

  return new Promise((resolve, reject) => \{
    const timer = setTimeout(() => \{
      if (onTimeout === 'approve') \{
        console.warn(`HITL timeout: auto-approving "$\{actionDescription}"`);
        resolve(action());
      } else if (onTimeout === 'escalate') \{
        notifyEscalation(approvalRequest);
        reject(new Error(`HITL timeout: escalated "$\{actionDescription}"`));
      } else \{
        reject(new Error(`HITL timeout: rejected "$\{actionDescription}"`));
      }
    }, timeoutMs);

    approvalRequest.onDecision(decision => \{
      clearTimeout(timer);
      if (decision === 'approved') \{
        resolve(action());
      } else \{
        reject(new Error(`Human rejected action: "$\{actionDescription}"`));
      }
    });
  });
}

// Usage — wrap irreversible agent actions:
await withHumanApproval(
  () => deployToProduction(build),
  'Deploy build v1.42 to production',
  \{ timeoutMs: 600_000, onTimeout: 'reject' }
);
```

:::warning Timeout handling is not optional
    Every HITL gate must specify what happens when no human responds within the timeout. Leaving the agent blocked indefinitely creates availability problems. Define the default explicitly — and for most irreversible actions, the right default is to reject and log, not to approve automatically.

---

## 15. Governance

### Audit Logging

Every agent action, tool call, and decision should be logged with enough context to reconstruct what happened and why.

```javascript
// audit-logger.js
class AuditLogger \{
  constructor(workflowId) \{
    this.workflowId = workflowId;
    this.entries = [];
  }

  log(event) \{
    const entry = \{
      workflowId: this.workflowId,
      timestamp: new Date().toISOString(),
      ...event,
    };
    this.entries.push(entry);
    // In production: ship to your observability backend
    console.log(JSON.stringify(entry));
  }

  agentStarted(agentId, role, task) \{
    this.log(\{ type: 'AGENT_STARTED', agentId, role, task });
  }

  toolCalled(agentId, toolName, args) \{
    // Redact sensitive args before logging
    const safeArgs = redactSensitive(args);
    this.log(\{ type: 'TOOL_CALLED', agentId, toolName, args: safeArgs });
  }

  agentCompleted(agentId, outputSummary, usage) \{
    this.log(\{ type: 'AGENT_COMPLETED', agentId, outputSummary, usage });
  }

  policyViolation(agentId, violation) \{
    this.log(\{ type: 'POLICY_VIOLATION', agentId, violation, severity: 'HIGH' });
  }
}
```

### Agent Activity Tracking

```javascript
// activity-tracker.js
const swarm = await flow.createSwarm(\{
  agents: ['coder', 'tester', 'reviewer'],
  onAgentEvent: (event) => \{
    auditLogger.log(event);   // every event goes to audit log
    if (event.type === 'tool_call' && SENSITIVE_TOOLS.includes(event.toolName)) \{
      notifyGovernanceChannel(event);
    }
  },
});
```

### Rollback Capability

```javascript
// rollback-support.js
class CheckpointedWorkflow \{
  constructor() \{
    this.checkpoints = [];
  }

  async saveCheckpoint(label, state) \{
    this.checkpoints.push(\{
      label,
      timestamp: new Date().toISOString(),
      state: JSON.parse(JSON.stringify(state)),  // deep clone
    });
  }

  async rollbackTo(label) \{
    const checkpoint = this.checkpoints.findLast(c => c.label === label);
    if (!checkpoint) throw new Error(`Checkpoint "$\{label}" not found`);
    console.log(`Rolling back to checkpoint: $\{label} ($\{checkpoint.timestamp})`);
    return checkpoint.state;
  }
}

const workflow = new CheckpointedWorkflow();

// Save state before each risky phase
await workflow.saveCheckpoint('pre-refactor', \{ files: currentFiles });
const refactorResult = await swarm.run(\{ task: 'refactor auth module' });

if (!refactorResult.testsPass) \{
  const previousState = await workflow.rollbackTo('pre-refactor');
  await restoreFiles(previousState.files);
}
```

---

## 16. Best Practices

1. **Decompose before spawning.** Define the work breakdown structure at the Queen level before spinning up workers. Agents with unclear scope waste tokens and produce inconsistent results.

2. **Use hierarchical topology for complex tasks, mesh for collaborative ones.** Hierarchical gives the Queen clear authority over sequencing; mesh enables peer-to-peer knowledge sharing for research or creative tasks.

3. **Single responsibility per agent.** A coder + tester + reviewer monolith agent is harder to route, harder to evaluate, and harder to replace. Three separate agents compose more predictably.

4. **Store patterns, not just outputs.** Capture reusable engineering decisions in memory under stable keys. Later workflows retrieve them rather than rediscovering the same conclusions.

5. **Use SPARC for all non-trivial feature work.** The specification-first discipline prevents scope creep, ensures testability, and creates a natural audit trail.

6. **Namespace your memory keys.** Use consistent prefixes (`patterns:`, `decisions:`, `context:`) to prevent key collisions across agents and sessions.

7. **Set explicit token budgets.** Per-agent token budgets prevent a verbose agent from consuming the entire workflow budget. Define them before the first production run.

8. **Route by model capability.** Use Haiku for routing, classification, and test generation; Sonnet for implementation and reasoning; Fable for high-stakes architectural decisions. Do not overprovision.

9. **Evaluate trajectories, not just outputs.** A correct final answer via a broken path is still a broken agent. Measure tool selection, step efficiency, and error recovery alongside output quality.

10. **Integrate evals into CI/CD.** Every prompt change, tool change, or model version bump should trigger the eval suite. Block deployment on regression — not just on code errors.

11. **Instrument with OTel from day one.** Retrofitting observability to a production agent system is expensive and incomplete. Emit traces at agent start, tool call, and completion from the first deployment.

12. **Define HITL gates before go-live.** Enumerate which action categories require human approval. Implement the gates and test them — do not assume agents will stay within safe boundaries without enforcement.

---

## 17. Antipatterns

1. **The Monolith Agent.** One agent tries to do everything: plan, code, test, review, deploy. It becomes impossible to route, evaluate, or replace individual capabilities. *Fix: split by single responsibility.*

2. **Agent Sprawl.** Spawning 50 agents for a task that 5 can handle. Coordination overhead grows faster than throughput. *Fix: start with the minimum viable swarm; scale up based on measurement.*

3. **Context Window Stuffing.** Passing the entire codebase into every agent's context. This maximises token cost and degrades reasoning quality as the model tries to process irrelevant content. *Fix: use semantic memory retrieval to pass only relevant context.*

4. **Stateless Design.** No persistent memory between sessions. Agents re-learn the same patterns on every run. *Fix: store reusable patterns in a stable namespace; retrieve at session start.*

5. **Tool Overloading.** Giving every agent access to every tool. This violates least privilege and makes agent behaviour harder to reason about. *Fix: each agent gets only the tools its role requires.*

6. **Skipping SPARC.** Jumping straight to implementation without a specification phase. Agents code the wrong thing confidently. *Fix: enforce specification-first for all non-trivial features.*

7. **Infinite Retry Loops.** Agents that retry failing tool calls without circuit breakers. A broken external dependency causes the agent to loop indefinitely. *Fix: set max retry limits and circuit breakers at the orchestrator level.*

8. **Cascade Failure.** One agent failure blocks the entire swarm. *Fix: design for partial success; isolate agent failures and allow the swarm to continue with degraded capability.*

9. **Token Burn on Simple Tasks.** Running a 5-agent debate to answer a question that a single prompt can resolve. 5 agents × multiple rounds = many unnecessary LLM calls. *Fix: match orchestration complexity to task complexity; use a single agent for simple tasks.*

10. **Provider Lock-in.** Tightly coupling agent logic to one LLM provider's API idioms. A provider outage, price change, or capability regression has no mitigation path. *Fix: build model-agnostic abstractions; test failover paths.*

11. **Launch-Day Evals Only.** Running evals once before deployment and never again. Model behaviour changes without code changes; prompt regressions from later changes go undetected. *Fix: continuous evaluation in CI/CD; treat evals as an operational process.*

12. **Observability as an Afterthought.** Adding logging and tracing after a production incident. By then, the incident is over and the logs that would have explained it were never captured. *Fix: OTel-first from the first deployment; treat traces as a first-class system requirement.*

---

## 18. CI/CD Integration

A complete GitHub Actions workflow that runs the eval suite on every PR that changes agent, prompt, or tool files.

```yaml
# .github/workflows/claude-flow-eval.yml
name: claude-flow Agent Evaluation

on:
  pull_request:
    paths:
      - 'agents/**'
      - 'prompts/**'
      - 'tools/**'
      - 'evals/**'
  push:
    branches: [main]
    paths:
      - 'agents/**'
      - 'prompts/**'

jobs:
  eval-gate:
    name: Evaluation Gate
    runs-on: ubuntu-latest
    timeout-minutes: 30

    steps:
      - name: Check out code
        uses: actions/checkout@v4

      - name: Set up Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'npm'

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.12'
          cache: 'pip'

      - name: Install Node dependencies
        run: npm ci

      - name: Install claude-flow
        run: npm install -g claude-flow

      - name: Install Python eval dependencies
        run: pip install anthropic

      - name: Run offline eval suite
        env:
          ANTHROPIC_API_KEY: $\{\{ secrets.ANTHROPIC_API_KEY }}
        run: |
          RESULTS_FILE="evals/results/ci-$(date +%Y%m%d-%H%M%S).json"
          python evals/eval_harness.py evals/datasets/baseline.jsonl \
            --output "$RESULTS_FILE" \
            --pass-threshold 0.75
          echo "RESULTS_FILE=$RESULTS_FILE" >> "$GITHUB_ENV"

      - name: Check regression against baseline
        env:
          ANTHROPIC_API_KEY: $\{\{ secrets.ANTHROPIC_API_KEY }}
        run: |
          npx claude-flow eval compare \
            --current "$RESULTS_FILE" \
            --baseline evals/results/baseline.json \
            --fail-on-regression \
            --regression-threshold 0.05

      - name: Upload eval results
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: eval-results-$\{\{ github.run_number }}
          path: evals/results/
          retention-days: 90

      - name: Post eval summary to PR
        if: github.event_name == 'pull_request'
        uses: actions/github-script@v7
        with:
          script: |
            const fs = require('fs');
            const results = JSON.parse(fs.readFileSync(process.env.RESULTS_FILE));
            const body = [
              '## Eval Results',
              `Pass rate: **$\{(results.pass_rate * 100).toFixed(1)}%** ($\{results.passed}/$\{results.total})`,
              `Average score: **$\{results.avg_score.toFixed(2)}**`,
              results.failures.length > 0
                ? `\n### Failures\n$\{results.failures.map(f => `- \`$\{f.task}\`: $\{f.reason}`).join('\n')}`
                : '\nNo failures.',
            ].join('\n');
            github.rest.issues.createComment(\{
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body,
            });

  stress-test:
    name: Stress Test (main branch only)
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    needs: eval-gate

    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'npm'

      - run: npm ci && npm install -g claude-flow

      - name: Run concurrent agent stress test
        env:
          ANTHROPIC_API_KEY: $\{\{ secrets.ANTHROPIC_API_KEY }}
        run: node evals/stress-test.js --concurrent 5 --tasks-per-agent 3
```

:::note Secrets management
    `ANTHROPIC_API_KEY` must be stored as a GitHub Actions secret, not hardcoded. Navigate to repository Settings → Secrets and variables → Actions → New repository secret.

---

## References

- **claude-flow GitHub:** [github.com/ruvnet/claude-flow](https://github.com/ruvnet/claude-flow)
- **Claude API documentation:** [docs.anthropic.com](https://docs.anthropic.com)
- **MCP specification:** [modelcontextprotocol.io](https://modelcontextprotocol.io)
- **AGENTSAFE governance framework:** arxiv.org/pdf/2512.03180
- **LLM agent evaluation survey:** arxiv.org/pdf/2507.21504
- **Agentic AI Governance (IMDA):** imda.gov.sg/mgf-for-agentic-ai
- **Related guides in this site:**
  - [MCP Deep Guide](../39-mcp-deep-guide.md)
  - [Agent SDK Production](../30-claude-agent-sdk-production.md)
  - [Models 2026](../35-claude-models-2026.md)
  - [Enterprise AI Architecture Patterns](../../../architecture/49-enterprise-ai-architecture-patterns.md)
  - [Governance & Compliance](../../../architecture/51-enterprise-ai-governance-compliance.md)
  - [Skills Assessment](../../../architecture/52-enterprise-ai-skills-assessment.md)

---

*Guide current as of July 2026. claude-flow is an active open-source project — verify feature availability against the [GitHub repo](https://github.com/ruvnet/claude-flow) changelog before designing production systems.*
