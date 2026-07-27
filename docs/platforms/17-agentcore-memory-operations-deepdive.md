---
title: "AgentCore Memory Operations Deep Dive"
doc_type: guide
domain: platforms
status: current
topic_id: agentcore-memory-operations-deepdive
last_reviewed: 2026-07-27
maturity: practitioner
supersedes:
  - docs/cloud-platforms/aws/AgentCore_Memory_Operations_DeepDive.md
tags:
  - aws
  - bedrock
  - agentcore
  - memory
  - kinesis
covers_version: "N/A"
---

# AgentCore Memory Operations Deep Dive

Metadata Options · Streaming & Batch · Issues/Fixes by Phase · Unit Testing · Evaluation & Retirement · Cleanup Strategies

| Section | Contents |
| --- | --- |
| 1 · Metadata Options | CreateEvent metadata fields, payload types, ListEvents filters, memory-record metadata, Kinesis stream event schema |
| 2 · Streaming Use Case | Kinesis Data Stream integration, real-time change notifications, consumer patterns, event schema, IAM wiring |
| 3 · Batch Use Case | BatchCreateMemoryRecords, BatchUpdateMemoryRecords, BatchDeleteMemoryRecords — limits, idempotency, retry patterns |
| 4 · Issues & Fixes by Phase | PoC → Cross-session → Multi-agent → Production — known issues, root causes, fixes, CloudWatch signals |
| 5 · Unit Testing | Mock patterns, test matrix, PII tests, isolation tests, hook tests, extraction tests, erasure tests — full code |
| 6 · Evaluation & Retirement | Metric thresholds, retire/graduate criteria, shadow evaluation, A/B strategy switch, evaluation teardown |
| 7 · Cleanup Strategies | Namespace purge, TTL enforcement, actor erasure, batch sweep, test teardown, cost-driven cleanup scheduler |

## 1. Metadata Options — Events, Records & Retrieval Filters

Every **CreateEvent** call accepts a metadata map of string key-value pairs that travel with the event but are not part of the conversation payload. Metadata is indexed and filterable via **ListEvents** — enabling efficient event retrieval without semantic search overhead.

| Parameter | Constraint | Notes |
| --- | --- | --- |
| Max metadata entries per event | 15 key-value pairs | Validation error if exceeded |
| Key length | 1–128 characters | Case-sensitive; no spaces |
| Value length | 1–256 characters | String only; no nested objects |
| Filter operator (ListEvents) | Exact match on key=value | No range or wildcard support on metadata |
| Metadata stored with | Short-term event (not extracted to long-term) | Use namespace/content for long-term recall |
| Visible in GetEvent response | Yes — full metadata map returned | CloudTrail logs include metadata keys only |

### CreateEvent with metadata — full parameter set:

```python
import boto3, time, uuid
client = boto3.client('bedrock-agentcore', region_name='eu-central-1')

response = client.create_event(
    memoryId = 'mem-abcdef1234-Ab1B2c3d4e',
    actorId = actor_id,           # from IdP — NEVER user-provided
    sessionId = session_id,
    clientToken = str(uuid.uuid4()),   # idempotency key
    eventTimestamp = int(time.time()),
    metadata = {
        'channel': {'stringValue': 'web-chat'},
        'product_line': {'stringValue': 'wealth-management'},
        'regulatory_ctx': {'stringValue': 'mifid2'},
        'case_type': {'stringValue': 'suitability-review'},
        'pii_redacted': {'stringValue': 'true'},          # audit flag
        'consent_basis': {'stringValue': 'legitimate-interest'},
        'agent_version': {'stringValue': '2.4.1'},
    },
    payload = [{
        'conversational': {
            'content': {'text': redacted_user_message},
            'role': 'USER'
        }
    }]
)
```

### 1.2 Payload Types in CreateEvent

| Payload Type | Structure Key | Use Case | Example |
| --- | --- | --- | --- |
| Conversational | `conversational: {role, content: {text}}` | Standard chat turn | User question / agent response |
| Blob / binary | `blob: {mimeType, data}` | PDF, image, audio stored in memory | KYC document reference |
| Structured JSON | `structured: {content: {text}}` | Tool outputs, API responses, extracted entities | Order status JSON, account details |
| Multi-payload (array) | Array of above | Store multiple data types in one event call | Text + metadata blob in same event |

### 1.3 ListEvents with Metadata Filters

```python
paginator = client.get_paginator('list_events')
pages = paginator.paginate(
    memoryId = memory_id,
    actorId = actor_id,
    sessionId = session_id,   # optional — omit for cross-session
    metadataFilter = {
        'equals': [
            {'key': 'product_line', 'value': 'wealth-management'},
            {'key': 'regulatory_ctx', 'value': 'mifid2'}
        ]
    },
    PaginationConfig={'PageSize': 50}
)
events = [e for page in pages for e in page['events']]
```

### 1.4 Memory Record Metadata (Long-Term)

Long-term memory records (created by strategies or BatchCreateMemoryRecords) carry a different metadata concept: **namespace** (routing/isolation key) and **memoryRecordId** (idempotency + update anchor). These are set on write and are filterable by namespace prefix in ListMemoryRecords.

| Field | Set By | Purpose | Example Value |
| --- | --- | --- | --- |
| memoryRecordId | Caller (BatchCreate) or auto-generated | Idempotency; enables BatchUpdate to overwrite | `actor123-risk-appetite` |
| namespace | Strategy config or BatchCreate caller | Routing, isolation, IAM condition key | `/strategy/sem-001/actor/u-123/` |
| content.text | Strategy extraction or BatchCreate | Actual memory content | "Risk appetite: balanced" |
| sourceEventIds[] | Auto-populated by strategy | Provenance — which events produced this record | `[evt-001, evt-002]` |
| createdAt / updatedAt | Service-managed | TTL decisions; staleness audit | ISO-8601 timestamps |
| score | Returned by RetrieveMemoryRecords only | Semantic relevance 0–1 | 0.91 |

## 2. Streaming Use Case — Kinesis Real-Time Change Notifications

AgentCore Memory can push real-time notifications to a **Kinesis Data Stream** whenever a memory record is created, updated, or deleted. This enables event-driven downstream architectures — compliance dashboards, fraud monitors, CRM sync, audit pipelines — without polling the list APIs.

### 2.1 Streaming Architecture

| Layer | Component | Role |
| --- | --- | --- |
| Producer | AgentCore Memory service | Publishes record-lifecycle events to Kinesis on every Create / Update / Delete |
| Stream | Kinesis Data Stream (in your account) | Buffer; configurable shard count and retention (1–365d) |
| Consumer | Lambda / Kinesis Consumer App / Firehose | Processes events in near-real-time; fan-out via EventBridge Pipes |
| IAM Role | `bedrock-agentcore.amazonaws.com` trust | Must have `kinesis:PutRecord` + optional `kms:GenerateDataKey` |
| Encryption | SSE via KMS (optional) | If enabled, role must also have `kms:Decrypt` on consumer side |

### 2.2 Wiring — CreateMemory with Stream Delivery

```python
import boto3
control = boto3.client('bedrock-agentcore-control', region_name='eu-central-1')

response = control.create_memory(
    name = 'banking-memory-streaming',
    description = 'EU Banking memory with Kinesis change stream',
    eventExpiryDuration = 90,
    encryptionKeyArn = 'arn:aws:kms:eu-central-1:123:key/cmk-id',
    streamDeliveryResource = {
        'kinesisDataStream': {
            'streamArn': 'arn:aws:kinesis:eu-central-1:123:stream/memory-changes',
        }
    },
    memoryExecutionRoleArn = 'arn:aws:iam::123:role/AgentCoreStreamRole',
    memoryStrategies = [{'semanticMemoryStrategy': {'name': 'FactExtractor'}}]
)
```

### 2.3 Kinesis Event Schema — Memory Record Lifecycle

Each Kinesis record Data payload is a JSON object with the following structure:

```json
{
  "eventType": "CREATE | UPDATE | DELETE",
  "memoryId": "mem-abcdef1234-Ab1B2c3d4e",
  "memoryRecordId": "actor123-risk-appetite",
  "namespace": "/strategy/sem-001/actor/u-123/",
  "actorId": "cognito-sub-xxxx",
  "eventTimestamp": "2026-04-09T10:23:45Z",
  "memoryRecord": {
    "content": {"text": "Risk appetite: balanced"},
    "sourceEventIds": ["evt-001", "evt-002"],
    "createdAt": "2026-04-09T10:23:40Z",
    "updatedAt": "2026-04-09T10:23:45Z"
  },
  "previousMemoryRecord": null
}
```

`memoryRecord` is `null` on DELETE; `previousMemoryRecord` is `null` on CREATE.

### 2.4 Consumer Lambda — Compliance Audit Pipeline

```python
import json, boto3
firehose = boto3.client('firehose')

def handler(event, context):
    for record in event['Records']:
        payload = json.loads(record['kinesis']['data'])
        evt_type = payload['eventType']
        actor_id = payload['actorId']

        # Route to compliance audit store
        if evt_type in ('CREATE', 'UPDATE') and 'pep' in payload.get('namespace', ''):
            firehose.put_record(
                DeliveryStreamName='compliance-memory-audit',
                Record={'Data': json.dumps({
                    'event_type': evt_type,
                    'actor_id': actor_id,
                    'namespace': payload['namespace'],
                    'content': payload['memoryRecord']['content']['text'],
                    'ts': payload['eventTimestamp'],
                })}
            )

        # Alert on unexpected DELETE
        if evt_type == 'DELETE':
            # Verify this was a sanctioned SAR/erasure workflow
            if 'erasure-workflow' not in payload.get('namespace', ''):
                raise Exception(f'Unsanctioned DELETE for actor {actor_id}')
```

### Streaming Issues Quick-Reference

| Issue | Symptom | Fix |
| --- | --- | --- |
| Shard hot-spotting | Single Kinesis shard overwhelmed; records dropped | Set partition key = `actorId[:3]` (hash spread) not constant string |
| Out-of-order events | Consumer sees DELETE before CREATE for same record | Use sequence number from Kinesis; sort within actor_id window |
| Consumer falling behind | Iterator age > 1 min; memory changes missed | Increase shard count; add Enhanced Fan-Out consumer |
| CMK decrypt failure on consumer | AccessDeniedException in consumer Lambda | Add `kms:Decrypt` on consumer role for stream's CMK |
| Duplicate events processed twice | Same memoryRecordId | Implement idempotency table (DynamoDB) keyed on record:sequenceNumber |

## 3. Batch Use Case — BatchCreate / Update / Delete Memory Records

The three batch APIs operate on long-term memory records directly, bypassing the async extraction pipeline. They are used by self-managed Lambda extractors, migration scripts, SAR (Subject Access Request) cleanup, and direct data hydration.

### 3.1 API Comparison

| Operation | Endpoint | Max Records | Idempotency | Common Use |
| --- | --- | --- | --- | --- |
| BatchCreateMemoryRecords | `POST /memories/{id}/memoryRecords/batchCreate` | 100 per call | clientToken per call; memoryRecordId for record-level | Self-managed extractor, initial data load, migration |
| BatchUpdateMemoryRecords | `POST /memories/{id}/memoryRecords/batchUpdate` | 100 per call | memoryRecordId must match existing record | Correct stale preferences, update entity facts post-review |
| BatchDeleteMemoryRecords | `POST /memories/{id}/memoryRecords/batchDelete` | 100 per call | Idempotent — delete non-existent returns success | GDPR erasure, TTL sweep, stale record pruning, test cleanup |

### 3.2 BatchCreateMemoryRecords — Full Example

```python
response = client.batch_create_memory_records(
    memoryId = memory_id,
    clientToken = str(uuid.uuid4()),   # call-level idempotency
    records = [
        {
            'memoryRecordId': f'{actor_id}-risk-appetite',   # stable id allows BatchUpdate later
            'content': {'text': 'Risk appetite: balanced'},
            'namespace': f'/actors/{actor_id}/financial-profile/'
        },
        {
            'memoryRecordId': f'{actor_id}-inv-horizon',
            'content': {'text': 'Investment horizon: 12 years'},
            'namespace': f'/actors/{actor_id}/financial-profile/'
        },
        # ... up to 100 records per call
    ]
)

# Partial failure pattern — check per-record status
for result in response.get('results', []):
    if result['status'] != 'SUCCESS':
        logger.error(f'Failed: {result["memoryRecordId"]} — {result["errorMessage"]}')
        dead_letter_queue.send(result)
```

### 3.3 Pagination Pattern for Batch > 100 Records

```python
def batch_create_all(client, memory_id, records, batch_size=100):
    """Split large record lists into batches of <=100."""
    failed = []
    for i in range(0, len(records), batch_size):
        chunk = records[i:i + batch_size]
        try:
            resp = client.batch_create_memory_records(
                memoryId = memory_id,
                clientToken = str(uuid.uuid4()),
                records = chunk
            )
            failed.extend([r for r in resp.get('results', []) if r['status'] != 'SUCCESS'])
        except client.exceptions.ThrottlingException:
            time.sleep(2 ** (i // batch_size))   # exponential backoff
            # re-queue chunk to DLQ for retry
            failed.extend(chunk)
    return failed
```

### 3.4 Streaming vs Batch — Decision Guide

| Scenario | Use Streaming (Kinesis) | Use Batch API | Notes |
| --- | --- | --- | --- |
| Real-time compliance alerting | YES | No | Alert within seconds of memory creation |
| CRM / downstream system sync | YES | Alternative | Streaming preferred for &lt;5s latency |
| Initial data migration (10K+ records) | No | YES | Batch create in chunks; no stream needed |
| GDPR erasure (actor deletion) | No | YES — BatchDelete | Batch delete all records in actor namespace |
| Self-managed Lambda extractor | No | YES — BatchCreate | Lambda writes extracted records back to AgentCore |
| Monitoring memory health | YES (consume stream) | No | Count creates/deletes per hour in CloudWatch |
| Test environment teardown | No | YES — BatchDelete | Delete all test actor records before next run |
| Nightly stale preference purge | No | YES — BatchDelete after ListMemoryRecords | TTL-driven cleanup job |

**See [Part 2](./parts/17-agentcore-memory-operations-deepdive-part2.md)** for production operations: troubleshooting by development phase, comprehensive unit test patterns, strategy evaluation and retirement criteria, and cleanup workflows.
