---
title: "Prompt Engineering Cheat Sheet"
doc_type: guide
domain: agentic-systems
topic_id: cheatsheet-5-prompt-engineering
status: current
date_created: 2026-07-24
last_reviewed: 2026-07-24
supersedes:
  - docs/coding-tools/claude/Cheatsheet_5_Prompt_Engineering.md
---

# Prompt Engineering Cheat Sheet

JSON Schemas - Few-Shot Examples - Extraction Patterns - Context Management - Anthropic Partner Cert EA

**DOMAIN 4 · 20%**

**DOMAIN 5 · 15%**

**SCENARIOS 5 &amp; 6**

## Core Techniques — The Big 3

### 1. JSON Schema

Define exact structure: field names, types, required/optional fields, constraints, nesting. Model must match this exactly. Enables validation before downstream use.

### 2. Few-Shot Examples

Show the model EXACTLY what good output looks like. Include edge cases in examples. More examples = more consistent. Input→Output pairs teach format implicitly.

### 3. Extraction Patterns

Prompt constructs that direct the model to locate and pull specific fields from unstructured text. Handles varied document formats, layouts, and phrasing.

**✓ These 3 techniques are explicitly called out in Task Statement 4.x — know all three**

### Supporting Technique

**Chain-of-Thought (CoT)**

Have model reason through problem before producing structured output. Improves accuracy on complex extractions. Costs more tokens.

## JSON Schema — Production Pattern

**SYSTEM PROMPT:** Define the exact schema

```
Extract invoice data as JSON matching this schema exactly:
{
  'invoice_id': string (format: 'INV-XXXXX'),
  'vendor_name': string,
  'date': string (ISO 8601: YYYY-MM-DD),
  'line_items': [
    {
      'description': string,
      'quantity': number,
      'unit_price': number,
      'total': number
    }
  ],
  'subtotal': number,
  'tax_rate': number (0-1, e.g. 0.08 for 8%),
  'total_due': number,
  'due_date': string (ISO 8601) | null
}

Return ONLY the JSON object. No explanation. If a field is missing, use null.
```

**⚠️ Under-specified schemas → inconsistent field names, structures, missing fields across calls**

**✓ Always validate extracted JSON against schema before passing to downstream systems**

## Few-Shot Examples Design

### Structure of Good Few-Shot Prompts

```
/* Example 1: Normal case */
Input: "Invoice #12345 from Acme Corp dated January 15, 2024 for $1,250.00"
Output: {
  "invoice_id": "INV-12345",
  "vendor_name": "Acme Corp",
  "date": "2024-01-15",
  "total": 1250.00
}

/* Example 2: EDGE CASE — missing due date */
Input: "Bill from TechCo, Feb 2024, $500"
Output: {
  "invoice_id": null,
  "vendor_name": "TechCo",
  "date": "2024-02-01",
  "due_date": null
}

/* Example 3: EDGE CASE — ambiguous format */
```

### Few-Shot Principles

- Include edge cases — not just happy path
- Show null handling — missing/ambiguous fields
- Match real data — use realistic examples
- More = consistent — 3-5 examples recommended
- Cover format variations in input examples

## Extraction Pattern Design

### What Extraction Patterns Solve

Reliably pulling specific data fields from varied, unstructured source documents that may differ in layout, format, and phrasing

### Pattern Structure

```
"From the following text, extract:

1. DATE: The date mentioned (convert to YYYY-MM-DD)
2. AMOUNT: Dollar amount (as number, no $ symbol)
3. VENDOR: Company or person name
4. PURPOSE: Reason for payment (1-3 words)

If information is not present, use null. Extract ONLY what is explicitly stated.
Do not infer or assume missing values.

Text: {document_text}"
```

**✓ Numbered extraction list = systematic coverage**

**✓ "Do not infer" = reduces hallucination risk**

**⚠️ Without patterns, model may paraphrase instead of extract exact values**

## Scenario 5: CI/CD Feedback Prompts

### Actionable Feedback Schema

```json
// Each feedback item MUST have these fields:
{
  "file": "src/api/handler.js",
  "line": 42,
  "severity": "error" | "warning" | "suggestion",
  "issue": "Unhandled promise rejection",
  "suggestion": "Add .catch() or use try/catch with await"
}
```

### Minimize False Positives By

- Define exact criteria for each severity level
- Specify scope — what NOT to flag
- Provide examples of true positive vs false positive
- Context-aware — don't flag test code like production
- Avoid style opinions unless eslint rules are defined

### Primary Domains

- Claude Code Config
- Prompt Engineering

## Context Management &amp; Reliability (Domain 5)

### 3 Core Challenges

- **Long docs:** Chunking, RAG, or summarize earlier sections to fit in window
- **Multi-turn:** Retain relevant context, prune resolved subtopics proactively
- **Agent handoffs:** Preserve: decisions, gathered data, task state, user prefs, constraints

### Reliability Patterns

- **Human-in-loop:** Pause for approval at high-stakes decisions — not just errors
- **Self-evaluation:** Agent checks own FORMAT/COMPLETENESS — NOT factual accuracy
- **Clear escalation:** Deterministic criteria defined upfront, not left to model judgment
- **Structured handoffs:** Customer ID + root cause + recommended action for human agents

### Escalation Design

```javascript
// Define escalation criteria EXPLICITLY
const shouldEscalate = (ctx) => {
  // Confidence threshold
  if (ctx.confidence < 0.7) return true;

  // Issue category rules
  if (FRAUD_CASES.includes(ctx.category)) return true;

  // Policy boundary
  if (ctx.refundAmount > 500) return true;

  return false;
};
```

**✓ Deterministic criteria = reliable decisions at scale**

## Scenario 6: Structured Data Extraction

### System goal

Extract from unstructured docs, validate via JSON schema, integrate downstream

### Primary domains

Prompt Engineering &amp; Structured Output + Context Management &amp; Reliability

### System Requirements

- Handle unstructured docs
- JSON schema validation
- High accuracy maintained
- Graceful edge case handling
- Downstream system integration

### Design Checklist

- ✓ Define schema upfront
- ✓ 3-5 few-shot examples with edge cases
- ✓ Explicit null handling instruction
- ✓ "Extract only, don't infer"
- ✓ Validate output before use
- ✓ Handle malformed input gracefully

## Prompt Engineering Anti-Patterns

- **Vague output instructions** → inconsistent format, missing fields, type mismatches
- **No edge cases in examples** → model improvises inconsistently on unusual inputs
- **Schema without validation** → downstream errors discovered late
- **Allowing inference** → model "fills in" values it shouldn't, creating hallucinations

## Quick Reference: Domain Weight

- **Domain 4:** 20% of exam
- **Domain 5:** 15% of exam
- **Combined:** 35%

## Related

- [AI Fluency Cheat Sheet](18-cheatsheet-4-ai-fluency.md) — the previous section in this series.
- [Claude CLI Cheat Sheet](20-cheatsheet-6-claude-cli.md) — the next section in this series.
