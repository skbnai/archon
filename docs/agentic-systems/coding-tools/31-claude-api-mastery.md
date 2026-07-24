---
title: "Claude API Mastery"
doc_type: guide
domain: agentic-systems
topic_id: claude-api-mastery
status: current
date_created: 2026-07-24
last_reviewed: 2026-07-24
supersedes:
  - ../knowledge-docs/docs/coding-tools/claude/claude-api-mastery.md
---

# Claude API Mastery

Complete guide to the Anthropic Claude API as of June 2026 — Messages API, Extended Thinking, Tool Use, Vision, Batch API, Files API, Streaming, and Prompt Caching.

---

## Messages API

The core API endpoint for all Claude interactions.

### Basic Request

```python
import anthropic

client = anthropic.Anthropic(api_key="your-key")

response = client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=4096,
    system="You are a senior software architect.",
    messages=[
        {"role": "user", "content": "Review this architecture: ..."}
    ]
)
print(response.content[0].text)
```

### Multi-turn Conversation

```python
messages = []

# Turn 1
messages.append({"role": "user", "content": "What is TOGAF?"})
response = client.messages.create(model="claude-sonnet-4-6", max_tokens=1024, messages=messages)
messages.append({"role": "assistant", "content": response.content[0].text})

# Turn 2
messages.append({"role": "user", "content": "How does it relate to APEX?"})
response = client.messages.create(model="claude-sonnet-4-6", max_tokens=1024, messages=messages)
```

### Key Parameters

| Parameter | Type | Description |
| ----------- | ------ | ------------- |
| `model` | string | Model ID (always pin to specific version) |
| `max_tokens` | int | Max output tokens (required) |
| `system` | string | System prompt |
| `messages` | list | Conversation history (alternating user/assistant) |
| `temperature` | float | 0–1, defaults to 1. Lower = more deterministic |
| `top_p` | float | Nucleus sampling threshold |
| `stop_sequences` | list | Stop generation at these strings |
| `stream` | bool | Enable streaming |
| `metadata` | dict | Pass user_id for abuse monitoring |

---

## Extended Thinking & Adaptive Reasoning

### Enabling Adaptive Reasoning

```python
response = client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=16000,
    thinking={
        "type": "enabled",
        "effort": "high",       # standard | high | xhigh | max
        "display": "omitted"    # omit reasoning from output stream
    },
    messages=[{"role": "user", "content": "Design a zero-downtime migration strategy for a 50TB Postgres database."}]
)
```

### Streaming with Extended Thinking

When `display` is not `"omitted"`, reasoning appears as `thinking` blocks:

```python
with client.messages.stream(
    model="claude-opus-4-6",
    max_tokens=16000,
    thinking={"type": "enabled", "effort": "xhigh"},
    messages=[...]
) as stream:
    for event in stream:
        if event.type == "content_block_start":
            if event.content_block.type == "thinking":
                print("Reasoning:", event.content_block.thinking)
            elif event.content_block.type == "text":
                print("Output:", event.content_block.text)
```

**Important:** When using `display: "omitted"`, no `thinking_delta` events are emitted — filter by event type before rendering to avoid leaking internal reasoning.

---

## Tool Use

Tool use is **generally available** (no beta header required) on all Claude 4.x models.

### Defining Tools

```python
tools = [
    {
        "name": "search_database",
        "description": "Query the enterprise knowledge base for relevant documents. Use when the user asks about internal policies, procedures, or historical decisions.",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The search query. Be specific and use relevant domain terms."
                },
                "max_results": {
                    "type": "integer",
                    "description": "Maximum number of results to return. Defaults to 5.",
                    "default": 5
                }
            },
            "required": ["query"]
        }
    }
]
```

### Tool Execution Loop

```python
def run_with_tools(user_message: str) -> str:
    messages = [{"role": "user", "content": user_message}]

    while True:
        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=4096,
            tools=tools,
            messages=messages
        )

        # If no tool calls, return final text
        if response.stop_reason == "end_turn":
            return next(b.text for b in response.content if b.type == "text")

        # Process tool calls
        messages.append({"role": "assistant", "content": response.content})
        tool_results = []

        for block in response.content:
            if block.type == "tool_use":
                result = execute_tool(block.name, block.input)
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": str(result)
                })

        messages.append({"role": "user", "content": tool_results})
```

### Parallel Tool Calls

Claude can call multiple tools simultaneously when they are independent:

```python
# Claude may respond with multiple tool_use blocks
for block in response.content:
    if block.type == "tool_use":
        # Execute all in parallel using asyncio or threading
        futures.append(executor.submit(execute_tool, block.name, block.input))
```

### Web Search Tool (Built-in)

```python
tools = [{"type": "web_search_20250305", "name": "web_search"}]
# No additional configuration needed — Claude handles query formation
```

---

## Vision & Multimodal

### Image Input (Base64)

```python
import base64

with open("architecture_diagram.png", "rb") as f:
    image_data = base64.standard_b64encode(f.read()).decode("utf-8")

response = client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=2048,
    messages=[{
        "role": "user",
        "content": [
            {
                "type": "image",
                "source": {
                    "type": "base64",
                    "media_type": "image/png",
                    "data": image_data
                }
            },
            {
                "type": "text",
                "text": "Identify the components in this architecture diagram and flag any single points of failure."
            }
        ]
    }]
)
```

### Image Input (URL)

```python
messages=[{
    "role": "user",
    "content": [
        {
            "type": "image",
            "source": {"type": "url", "url": "https://example.com/diagram.png"}
        },
        {"type": "text", "text": "What does this diagram show?"}
    ]
}]
```

### PDF Document Processing

```python
with open("report.pdf", "rb") as f:
    pdf_data = base64.standard_b64encode(f.read()).decode("utf-8")

messages=[{
    "role": "user",
    "content": [
        {
            "type": "document",
            "source": {"type": "base64", "media_type": "application/pdf", "data": pdf_data}
        },
        {"type": "text", "text": "Summarise the key recommendations."}
    ]
}]
```

---

## Batch API

Process up to 100,000 requests asynchronously at 50% off standard pricing.

### Creating a Batch

```python
batch = client.messages.batches.create(
    requests=[
        {
            "custom_id": f"request-{i}",
            "params": {
                "model": "claude-sonnet-4-6",
                "max_tokens": 1024,
                "messages": [{"role": "user", "content": docs[i]}]
            }
        }
        for i in range(len(docs))
    ]
)
print(f"Batch ID: {batch.id}")
```

### Polling for Completion

```python
import time

while True:
    batch = client.messages.batches.retrieve(batch.id)
    if batch.processing_status == "ended":
        break
    print(f"In progress: {batch.request_counts.processing} remaining")
    time.sleep(60)
```

### Reading Results

```python
for result in client.messages.batches.results(batch.id):
    if result.result.type == "succeeded":
        print(f"{result.custom_id}: {result.result.message.content[0].text}")
    else:
        print(f"{result.custom_id}: FAILED - {result.result.error}")
```

**Key facts:**

- 50% price discount vs synchronous API
- Most batches complete in < 1 hour
- Compatible with prompt caching (additional discount)
- Requests expire if not processed within 24 hours
- Up to 300K `max_tokens` per request in Opus/Sonnet via beta header

---

## Files API

Upload files once, reference by `file_id` in multiple requests.

### Upload a File

```python
with open("knowledge_base.pdf", "rb") as f:
    file_obj = client.beta.files.upload(
        file=("knowledge_base.pdf", f, "application/pdf")
    )
file_id = file_obj.id  # e.g. "file_abc123"
```

### Use in Messages

```python
messages=[{
    "role": "user",
    "content": [
        {
            "type": "document",
            "source": {"type": "file", "file_id": file_id}
        },
        {"type": "text", "text": "Answer questions based on this document."}
    ]
}]
```

### Benefits

- Eliminate repeated base64 encoding overhead
- Reduce network transfer for large documents
- Works with Batch API and Code Execution
- Compatible with prompt caching for further cost reduction

---

## Prompt Caching

Cache stable prompt prefixes to reduce costs on repeated calls.

### Cache Breakpoint

```python
messages=[
    {
        "role": "user",
        "content": [
            {
                "type": "text",
                "text": system_context_10k_tokens,
                "cache_control": {"type": "ephemeral"}  # Mark cache boundary
            },
            {"type": "text", "text": user_question}
        ]
    }
]
```

### Caching Rules

| Rule | Detail |
| ------ | -------- |
| Minimum prefix | 1,024 tokens |
| Cache TTL | 5 minutes (resets on each hit) |
| Cache read discount | 90% off input token price |
| Cache write cost | Standard input price |
| Max cache breakpoints | 4 per request |

### Best Practice: Stable Prefix Design

Structure prompts so stable content comes first:

```
[System prompt]          ← cache here
[Document / context]     ← cache here
[Few-shot examples]      ← optionally cache
[User question]          ← NOT cached (changes every request)
```

---

## Streaming

### Basic Streaming

```python
with client.messages.stream(
    model="claude-sonnet-4-6",
    max_tokens=2048,
    messages=[{"role": "user", "content": "Write a technical specification for..."}]
) as stream:
    for text in stream.text_stream:
        print(text, end="", flush=True)
```

### Event-Based Streaming

```python
with client.messages.stream(...) as stream:
    for event in stream:
        match event.type:
            case "message_start":
                print(f"Usage: {event.message.usage}")
            case "content_block_delta":
                if event.delta.type == "text_delta":
                    print(event.delta.text, end="")
            case "message_delta":
                print(f"\nStop reason: {event.delta.stop_reason}")
```

---

## Error Handling

```python
from anthropic import (
    APIConnectionError,
    APIStatusError,
    RateLimitError,
    APITimeoutError
)
import time

def call_with_retry(messages, max_retries=3):
    for attempt in range(max_retries):
        try:
            return client.messages.create(
                model="claude-sonnet-4-6",
                max_tokens=2048,
                messages=messages
            )
        except RateLimitError:
            wait = 2 ** attempt  # Exponential backoff
            time.sleep(wait)
        except APITimeoutError:
            if attempt == max_retries - 1:
                raise
            time.sleep(5)
        except APIStatusError as e:
            if e.status_code in (529, 503):  # Overloaded
                time.sleep(10)
            else:
                raise
```

### Common Error Codes

| Code | Meaning | Action |
| ------ | --------- | -------- |
| 401 | Invalid API key | Check key |
| 403 | Permission denied | Check model access |
| 429 | Rate limit exceeded | Exponential backoff |
| 500 | Internal server error | Retry with backoff |
| 529 | Overloaded | Wait and retry |
