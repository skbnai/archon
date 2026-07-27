---
title: "AgentCore Memory Architecture Guide (Part 4)"
doc_type: guide
domain: platforms
status: current
topic_id: agentcore-memory-architecture-guide-part4
last_reviewed: 2026-07-27
maturity: practitioner
supersedes: []
tags: [aws, agentcore, python, terraform, testing]
covers_version: "v3.0, June 2026"
---

> Continues from [AgentCore Memory Architecture Guide](../15-agentcore-memory-architecture-guide.md), [Part 2](15-agentcore-memory-architecture-guide-part2.md), and [Part 3](15-agentcore-memory-architecture-guide-part3.md): the four reference-implementation appendices — a complete resume orchestrator, the session catalog API, the warm pool/session close workflow, and the full test suite.

## Appendix A — Complete Resume Orchestrator (Python)

Production-ready implementation of all four session resume scenarios. The `ResumeOrchestrator` is the single entry point for all resume logic: it reads the DynamoDB session catalog to determine which scenario applies, then executes the correct reconstruction strategy. Deploy this as a Lambda function invoked by your agent harness at the start of every session.

### Session Status Detection

```python
import boto3, time, json
from dataclasses import dataclass
from enum import Enum

class ResumeScenario(Enum):
    A_WARM = 'A'       # microVM idle -- direct invocation
    B_COLD_STM = 'B'   # cold start, STM events alive
    C_LTM_ONLY = 'C'   # STM expired, LTM records exist
    D_ARCHIVE = 'D'    # LTM gone, S3 archive available
    E_FRESH = 'E'      # nothing -- start fresh (or post-erasure)

@dataclass
class SessionState:
    scenario: ResumeScenario
    session_id: str
    actor_id: str
    title: str
    stm_expires_at: int          # Unix timestamp
    ltm_extracted: bool
    s3_archive_key: str | None
    microvm_status: str | None    # ACTIVE | IDLE | TERMINATED

class SessionStatusDetector:
    def __init__(self, dynamo_table, agentcore_client, runtime_arn):
        self.table = dynamo_table
        self.ac = agentcore_client
        self.runtime = runtime_arn

    def detect(self, actor_id: str, session_id: str) -> SessionState:
        # 1. Load session catalog record
        rec = self.table.get_item(
            Key={'actor_id': actor_id, 'session_id': session_id}
        ).get('Item')
        if not rec:
            return SessionState(ResumeScenario.E_FRESH, session_id, actor_id, '', 0, False, None, None)

        stm_alive = int(rec.get('stm_expires_at', 0)) > int(time.time())
        ltm_ok = rec.get('ltm_extracted', False)
        archive = rec.get('s3_archive_key')

        # 2. Check microVM state via ping (warm = IDLE or ACTIVE)
        vm_status = self._ping_vm(session_id)

        # 3. Select scenario
        if vm_status in ('ACTIVE', 'IDLE'):
            scenario = ResumeScenario.A_WARM
        elif stm_alive:
            scenario = ResumeScenario.B_COLD_STM
        elif ltm_ok:
            scenario = ResumeScenario.C_LTM_ONLY
        elif archive:
            scenario = ResumeScenario.D_ARCHIVE
        else:
            scenario = ResumeScenario.E_FRESH

        return SessionState(
            scenario, session_id, actor_id, rec.get('title', 'Untitled'),
            int(rec.get('stm_expires_at', 0)), ltm_ok, archive, vm_status,
        )

    def _ping_vm(self, session_id: str) -> str:
        """Returns ACTIVE | IDLE | TERMINATED"""
        try:
            r = self.ac.get_runtime_session(
                agentRuntimeArn=self.runtime, runtimeSessionId=session_id
            )
            return r.get('status', 'TERMINATED')
        except self.ac.exceptions.ResourceNotFoundException:
            return 'TERMINATED'
```

### Resume Orchestrator — All Scenarios

```python
class ResumeOrchestrator:
    MAX_STM_TOKENS = 120_000  # 70% of 200K context window
    LTM_TOKEN_BUDGET = 900

    def __init__(self, detector, memory_client, s3_client, compactor, pii_redactor, memory_id):
        self.detector = detector
        self.memory = memory_client
        self.s3 = s3_client
        self.compactor = compactor
        self.redactor = pii_redactor
        self.mem_id = memory_id

    def build_context(self, actor_id: str, session_id: str, current_query: str) -> dict:
        state = self.detector.detect(actor_id, session_id)

        if state.scenario == ResumeScenario.A_WARM:
            # Scenario A: microVM is warm -- no memory calls needed
            return {'scenario': 'A', 'context_block': '', 'transcript': []}
        elif state.scenario == ResumeScenario.B_COLD_STM:
            return self._scenario_b(state, current_query)
        elif state.scenario == ResumeScenario.C_LTM_ONLY:
            return self._scenario_c(state, current_query)
        elif state.scenario == ResumeScenario.D_ARCHIVE:
            return self._scenario_d(state)
        else:
            # E_FRESH or post-erasure
            return {'scenario': 'E', 'context_block': '', 'transcript': []}

    def _scenario_b(self, state: SessionState, query: str) -> dict:
        """Scenario B: Cold start -- STM events alive"""
        # Step 1: fetch LTM for personalisation
        ltm_block = self._fetch_ltm(state.actor_id, query, scope='actor')  # actor-wide prefs

        # Step 2: replay STM events (full transcript)
        events = self.memory.list_events(
            memoryId=self.mem_id, actorId=state.actor_id,
            sessionId=state.session_id, maxResults=500,
        ).get('events', [])

        # Step 3: measure token budget
        transcript = [{'role': e['role'], 'content': e['content']} for e in events]
        token_est = sum(len(t['content'].split()) * 1.3 for t in transcript)

        # Step 4: compact if over 70% threshold
        if token_est > self.MAX_STM_TOKENS:
            transcript = self.compactor.compress(
                transcript, target_tokens=int(self.MAX_STM_TOKENS * 0.6)
            )

        ctx = f'=== RESUMED SESSION: {state.title} ===\n{ltm_block}'
        return {'scenario': 'B', 'context_block': ctx, 'transcript': transcript}

    def _scenario_c(self, state: SessionState, query: str) -> dict:
        """Scenario C: STM expired -- LTM reconstruction"""
        # Fetch session-scoped LTM (STRICTLY_CONSISTENT session_id filter)
        session_records = self.memory.retrieve_memory_records(
            memoryId=self.mem_id,
            namespace=f'/actors/{state.actor_id}/',
            # Metadata filter -- deterministic because of STRICTLY_CONSISTENT
            metadataFilter={'equals': {'key': 'session_id', 'value': state.session_id}},
            maxResults=20,
        ).get('memoryRecordSummaries', [])

        # Fetch actor-scoped LTM (latest cross-session preferences)
        actor_records = self._fetch_ltm(state.actor_id, query, scope='actor', max_results=5)

        # Extract summary record (highest value reconstruction artifact)
        summary = next((r['content'] for r in session_records
                        if r.get('strategyType') == 'SUMMARIZATION'), '')
        facts = [r['content'] for r in session_records
                 if r.get('strategyType') == 'SEMANTIC'][:5]
        prefs = [r['content'] for r in session_records
                 if r.get('strategyType') == 'USER_PREFERENCE'][:3]

        ctx = self._build_reconstruction_block(
            title=state.title, summary=summary, facts=facts,
            prefs=prefs, actor_context=actor_records,
        )
        return {'scenario': 'C', 'context_block': ctx, 'transcript': []}

    def _scenario_d(self, state: SessionState) -> dict:
        """Scenario D: S3 archive fallback"""
        archive = json.loads(
            self.s3.get_object(Bucket='agent-archives', Key=state.s3_archive_key)['Body'].read().decode()
        )
        ctx = (
            f'=== ARCHIVED CONVERSATION: {state.title} ===\n'
            f"Date: {archive['date']}\n"
            f"Summary: {archive['summary']}\n"
            f'Note: Original transcript and knowledge records are no longer available.\n'
        )
        return {'scenario': 'D', 'context_block': ctx, 'transcript': []}

    def _build_reconstruction_block(self, title, summary, facts, prefs, actor_context):
        lines = [f'=== PREVIOUS CONVERSATION: {title} ===']
        lines.append('Status: Resumed from archived session (original transcript no longer available)')
        if summary:
            lines += ['', 'CONVERSATION SUMMARY:', summary]
        if facts:
            lines += ['', 'KEY FACTS DISCUSSED:']
            lines.extend(f' - {f}' for f in facts)
        if prefs:
            lines += ['', 'RELEVANT USER PREFERENCES:']
            lines.extend(f' - {p}' for p in prefs)
        if actor_context:
            lines += ['', 'CURRENT USER CONTEXT (cross-session):', actor_context]
        lines += [
            '', 'INSTRUCTION: Reconstruct naturally from the above.',
            'Do not mention transcript unavailability to the user.',
            '=================================',
        ]
        return '\n'.join(lines)
```

## Appendix B — Session Catalog API (Lambda Handlers)

REST API for the conversation history sidebar: list, create, rename, fork, delete. Deploy these Lambda functions behind API Gateway (or AppSync resolvers). All endpoints require Cognito JWT authorisation; `actor_id` is extracted from the JWT claims — never from the request body.

### List Sessions (Sidebar Render)

```python
import boto3, os, json, time
from boto3.dynamodb.conditions import Key

TABLE = boto3.resource('dynamodb').Table(os.environ['SESSIONS_TABLE'])
MEMORY = boto3.client('bedrock-agentcore', region_name='eu-central-1')

def list_sessions(event, context):
    """GET /sessions -- returns sidebar list for authenticated user"""
    actor_id = event['requestContext']['authorizer']['claims']['sub']
    limit = int(event.get('queryStringParameters', {}).get('limit', 50))
    last_key = event.get('queryStringParameters', {}).get('cursor')

    kwargs = dict(
        IndexName='actor-time-index',
        KeyConditionExpression=Key('actor_id').eq(actor_id),
        ScanIndexForward=False,  # newest first
        Limit=limit,
    )
    if last_key:
        kwargs['ExclusiveStartKey'] = json.loads(last_key)

    result = TABLE.query(**kwargs)
    items = result.get('Items', [])

    # Annotate STM status (alive / expired)
    now = int(time.time())
    for item in items:
        item['stm_alive'] = int(item.get('stm_expires_at', 0)) > now

    return {
        'statusCode': 200,
        'body': json.dumps({
            'sessions': items,
            'cursor': json.dumps(result.get('LastEvaluatedKey')) if result.get('LastEvaluatedKey') else None,
        }),
    }
```

### Create Session

```python
import uuid, time

def create_session(event, context):
    """POST /sessions -- called when user starts a new conversation"""
    actor_id = event['requestContext']['authorizer']['claims']['sub']
    body = json.loads(event.get('body', '{}'))
    session_id = str(uuid.uuid4())
    now = int(time.time())
    stm_ttl = now + 30 * 86_400  # STM expires in 30 days (configurable per product line)

    TABLE.put_item(Item={
        'actor_id': actor_id,
        'session_id': session_id,
        'title': body.get('title', 'New conversation'),
        'preview_text': '',
        'created_at': now,
        'last_updated_at': now,
        'model_id': body.get('model_id', 'claude-sonnet-4-6'),
        'stm_expires_at': stm_ttl,
        'stm_status': 'ALIVE',
        'ltm_extracted': False,
        'labels': body.get('labels', []),
        'parent_session_id': body.get('parent_session_id'),  # for forks
        's3_archive_key': None,
    })
    return {'statusCode': 201, 'body': json.dumps({'session_id': session_id})}
```

### Fork Session

```python
def fork_session(event, context):
    """POST /sessions/{session_id}/fork -- branch from existing session"""
    actor_id = event['requestContext']['authorizer']['claims']['sub']
    src_session_id = event['pathParameters']['session_id']

    # Verify ownership
    src = TABLE.get_item(Key={'actor_id': actor_id, 'session_id': src_session_id}).get('Item')
    if not src:
        return {'statusCode': 404, 'body': json.dumps({'error': 'Not found'})}

    new_session_id = str(uuid.uuid4())
    now = int(time.time())

    # Fork inherits STM expiry from source
    TABLE.put_item(Item={
        **src,
        'session_id': new_session_id,
        'title': f"Fork of: {src['title']}",
        'created_at': now,
        'last_updated_at': now,
        'parent_session_id': src_session_id,  # provenance
        'ltm_extracted': False,
        's3_archive_key': None,
    })
    return {'statusCode': 201, 'body': json.dumps({'session_id': new_session_id, 'forked_from': src_session_id})}
```

### Delete Session (GDPR Art. 17 Cascade)

```python
def delete_session(event, context):
    """DELETE /sessions/{session_id} -- cascades all 4 data layers"""
    actor_id = event['requestContext']['authorizer']['claims']['sub']
    session_id = event['pathParameters']['session_id']

    rec = TABLE.get_item(Key={'actor_id': actor_id, 'session_id': session_id}).get('Item')
    if not rec:
        return {'statusCode': 404}

    # Layer 1: DynamoDB catalog
    TABLE.delete_item(Key={'actor_id': actor_id, 'session_id': session_id})

    # Layer 2: STM events (AgentCore Memory)
    try:
        MEMORY.delete_memory_namespace(
            memoryId=os.environ['MEMORY_RESOURCE_ID'],
            namespace=f'/actors/{actor_id}/sessions/{session_id}/',
        )
    except MEMORY.exceptions.ResourceNotFoundException:
        pass  # Already expired -- expected

    # Layer 3: LTM records (session-scoped)
    # delete_memory_records with metadataFilter session_id=session_id
    _delete_ltm_records(actor_id, session_id)

    # Layer 4: S3 archive
    if rec.get('s3_archive_key'):
        boto3.client('s3').delete_object(Bucket=os.environ['ARCHIVE_BUCKET'], Key=rec['s3_archive_key'])

    return {'statusCode': 204}
```

## Appendix C — Warm Pool & Session Close Workflow

Keep microVMs alive across idle periods, and fire the correct cleanup on session end.

### Warm Pool Heartbeat

A warm pool keeps a configurable number of microVMs in IDLE state by sending heartbeat pings every 10 minutes, preventing the idle timeout from firing. The pool is sized to expected peak concurrent users. Benchmark (April 2026): pre-warmed sessions serve requests in ~250ms vs. ~2.9s cold.

```python
import boto3, os, time, logging
from concurrent.futures import ThreadPoolExecutor

class WarmPool:
    PING_INTERVAL_S = 600  # 10 min -- must be < idleRuntimeSessionTimeout (900s)
    POOL_SIZE = int(os.environ.get('WARM_POOL_SIZE', '10'))

    def __init__(self, runtime_arn, agentcore_client, dynamo_table):
        self.runtime = runtime_arn
        self.ac = agentcore_client
        self.table = dynamo_table
        self.pool = {}  # session_id -> last_ping_at

    def add_to_pool(self, session_id: str):
        """Call after first invocation to register session in warm pool."""
        self.pool[session_id] = time.time()

    def heartbeat_loop(self):
        """Run as background thread or EventBridge scheduled Lambda."""
        while True:
            time.sleep(self.PING_INTERVAL_S)
            stale = [sid for sid, t in self.pool.items()
                     if time.time() - t > self.PING_INTERVAL_S - 30]
            with ThreadPoolExecutor(max_workers=20) as ex:
                futures = {ex.submit(self._ping, sid): sid for sid in stale}
                for fut, sid in futures.items():
                    if not fut.result():  # microVM terminated
                        del self.pool[sid]

    def _ping(self, session_id: str) -> bool:
        """Send HealthyBusy ping. Returns True if VM still alive."""
        try:
            self.ac.invoke_agent_runtime(
                agentRuntimeArn=self.runtime, runtimeSessionId=session_id,
                payload=b'{"__ping": true}',
            )
            self.pool[session_id] = time.time()
            return True
        except Exception as e:
            logging.warning(f'Ping failed for {session_id}: {e}')
            return False

    def evict_inactive(self, inactive_threshold_s: int = 7200):
        """Remove sessions inactive > 2h from pool to free microVM cost."""
        cutoff = time.time() - inactive_threshold_s
        to_evict = [sid for sid, t in self.pool.items() if t < cutoff]
        for sid in to_evict:
            self.ac.stop_runtime_session(agentRuntimeArn=self.runtime, runtimeSessionId=sid)
            del self.pool[sid]
```

### Session Close — EventBridge Workflow

When a session ends (user navigates away, explicit close, or timeout), fire an EventBridge event that triggers the consolidation pipeline and S3 archive in parallel. This is the single most important event in the memory lifecycle.

```python
# agent/skills/session_close.py -- call this at session end
import boto3, json, time, os, gzip

def close_session(actor_id: str, session_id: str, session_manager, memory_client, s3_client):
    """
    1. Flush any buffered STM events (batch_size buffer)
    2. Fire EventBridge event to trigger async LTM consolidation
    3. Export compressed S3 archive (Scenario D fallback)
    4. Update DynamoDB catalog (preview text, last_updated)
    """
    # 1. Flush STM buffer
    session_manager.close()  # flushes remaining batch

    # 2. Trigger LTM consolidation via EventBridge
    events_client = boto3.client('events', region_name='eu-central-1')
    events_client.put_events(Entries=[{
        'Source': 'agent.session',
        'DetailType': 'SessionEnded',
        'Detail': json.dumps({
            'actor_id': actor_id,
            'session_id': session_id,
            'memory_id': os.environ['MEMORY_RESOURCE_ID'],
            'timestamp': int(time.time()),
        }),
        'EventBusName': os.environ['EVENT_BUS_NAME'],
    }])

    # 3. Build S3 archive -- compressed JSON (Scenario D fallback)
    events = memory_client.list_events(
        memoryId=os.environ['MEMORY_RESOURCE_ID'], actorId=actor_id,
        sessionId=session_id, maxResults=500,
    ).get('events', [])

    archive_payload = gzip.compress(json.dumps({
        'actor_id': actor_id,
        'session_id': session_id,
        'date': time.strftime('%Y-%m-%d'),
        'event_count': len(events),
        # Let LLM summarise if needed -- or inline for small sessions
        'events': events[:100],  # cap at 100 for size
    }).encode())
    archive_key = f'archives/{actor_id}/{session_id}/session.json.gz'
    s3_client.put_object(
        Bucket=os.environ['ARCHIVE_BUCKET'], Key=archive_key, Body=archive_payload,
        ServerSideEncryption='aws:kms', SSEKMSKeyId=os.environ['KMS_KEY_ID'],
    )

    # 4. Update DynamoDB catalog
    preview = events[-1]['content'][:120] if events else ''
    boto3.resource('dynamodb').Table(os.environ['SESSIONS_TABLE']).update_item(
        Key={'actor_id': actor_id, 'session_id': session_id},
        UpdateExpression='SET last_updated_at=:t, preview_text=:p, s3_archive_key=:k',
        ExpressionAttributeValues={
            ':t': int(time.time()), ':p': preview, ':k': archive_key,
        },
    )
```

### EventBridge Rules — Terraform

```hcl
# EventBridge rule: SessionEnded -> trigger LTM consolidation Lambda
resource "aws_cloudwatch_event_rule" "session_ended" {
  name           = "${var.project}-session-ended"
  event_bus_name = aws_cloudwatch_event_bus.agent.name
  event_pattern = jsonencode({
    source      = ["agent.session"]
    detail-type = ["SessionEnded"]
  })
}

resource "aws_cloudwatch_event_target" "consolidation" {
  rule           = aws_cloudwatch_event_rule.session_ended.name
  event_bus_name = aws_cloudwatch_event_bus.agent.name
  arn            = aws_lambda_function.consolidation.arn
}

# Consolidation Lambda: reads events -> triggers AgentCore extraction
resource "aws_lambda_function" "consolidation" {
  function_name = "${var.project}-consolidation"
  handler       = "consolidation.handler"
  runtime       = "python3.12"
  timeout       = 300  # 5 min max for large sessions

  environment {
    variables = {
      MEMORY_RESOURCE_ID = aws_bedrockagentcore_memory.banking_memory.id
      SESSIONS_TABLE     = aws_dynamodb_table.sessions.name
      ARCHIVE_BUCKET     = aws_s3_bucket.archives.bucket
      KMS_KEY_ID         = aws_kms_key.memory_cmk.key_id
    }
  }
}
```

## Appendix D — Complete Test Suite

Unit, integration, and compliance tests for all resume scenarios and memory controls. Tests are split into three tiers: unit tests (mocked, fast CI), integration tests (real AgentCore Memory in a dev account, slower), and compliance tests (GDPR Art. 17, Art. 25, namespace isolation). All three must pass before the production deployment gate.

### Resume Scenario Tests

```python
import pytest, time
from unittest.mock import MagicMock, patch
from resume_orchestrator import ResumeOrchestrator, ResumeScenario

class TestScenarioA_WarmResume:
    def test_warm_vm_returns_empty_context(self, mock_detector):
        mock_detector.detect.return_value = MagicMock(scenario=ResumeScenario.A_WARM)
        orch = ResumeOrchestrator(mock_detector, MagicMock(), MagicMock(), MagicMock(), MagicMock(), 'mem-id')
        ctx = orch.build_context('actor-1', 'sess-1', 'hello')
        assert ctx['scenario'] == 'A'
        assert ctx['context_block'] == ''
        assert ctx['transcript'] == []

class TestScenarioB_ColdSTMAlive:
    def test_transcript_injected(self, mock_detector, mock_memory):
        mock_detector.detect.return_value = MagicMock(
            scenario=ResumeScenario.B_COLD_STM, actor_id='actor-1',
            session_id='sess-1', title='Test session',
        )
        mock_memory.list_events.return_value = {'events': [
            {'role': 'user', 'content': 'What is my balance?'},
            {'role': 'assistant', 'content': 'Your balance is [REDACTED].'},
        ]}
        ctx = orch.build_context('actor-1', 'sess-1', 'continue')
        assert ctx['scenario'] == 'B'
        assert len(ctx['transcript']) == 2

    def test_transcript_compacted_at_70pct_threshold(self, ...):
        # Generate 130K-token conversation (above 70% of 200K)
        long_events = [{'role': 'user', 'content': 'x ' * 500} for _ in range(500)]
        mock_memory.list_events.return_value = {'events': long_events}
        ctx = orch.build_context('actor-1', 'sess-1', 'continue')
        # After compaction, token estimate should be under 120K
        total = sum(len(t['content'].split()) * 1.3 for t in ctx['transcript'])
        assert total < 120_000

class TestScenarioC_STMExpired:
    def test_session_scoped_ltm_retrieved(self, mock_detector, mock_memory):
        mock_detector.detect.return_value = MagicMock(
            scenario=ResumeScenario.C_LTM_ONLY, actor_id='actor-1',
            session_id='sess-old', title='Old conversation',
        )
        # Mock: session-scoped records include a summary
        mock_memory.retrieve_memory_records.return_value = {
            'memoryRecordSummaries': [{
                'strategyType': 'SUMMARIZATION',
                'content': 'User asked about Q3 fraud patterns.',
            }]
        }
        ctx = orch.build_context('actor-1', 'sess-old', 'continue')
        assert ctx['scenario'] == 'C'
        assert 'PREVIOUS CONVERSATION' in ctx['context_block']
        assert 'Q3 fraud' in ctx['context_block']
        assert ctx['transcript'] == []  # no STM replay in Scenario C

    def test_metadatafilter_uses_session_id(self, ...):
        # Verify STRICTLY_CONSISTENT filter is applied
        orch.build_context('actor-1', 'sess-old', 'continue')
        call_kwargs = mock_memory.retrieve_memory_records.call_args[1]
        assert call_kwargs['metadataFilter'] == {'equals': {'key': 'session_id', 'value': 'sess-old'}}
```

### PII Redaction Tests (Zero-Tolerance)

```python
PII_TEST_VECTORS = [
    ('Full name', 'My name is John Smith', 'John Smith'),
    ('IBAN', 'IBAN: GB82 WEST 1234 5698 7654 32', 'GB82 WEST'),
    ('Card number', '4111 1111 1111 1111', '4111'),
    ('Email', 'contact me at j.smith@bank.com', 'j.smith@bank'),
    ('Passport', 'Passport: AB1234567', 'AB1234567'),
    ('ISIN', 'bought ISIN: GB00BH4HKS39', 'GB00BH4HKS39'),
    ('LEI code', 'LEI: 213800WSGIIZCXF1P572', 'WSGIIZCXF1P572'),
]

class TestPIIRedaction:
    @pytest.mark.parametrize('name,text,pattern', PII_TEST_VECTORS)
    def test_pii_not_in_redacted_output(self, name, text, pattern, redactor):
        result = redactor.redact(text)
        assert pattern not in result, f'FAIL [{name}]: pattern "{pattern}" survived redaction.'

    def test_redacted_output_stored_in_memory(self, hook, memory_client):
        """Verify that raw PII never reaches put_events"""
        event = make_event(role='user', content='My IBAN is GB82 WEST 1234')
        hook.on_message_added(event)
        # Intercept the content that would be written
        stored = memory_client.put_events.call_args[1]['payload']
        assert 'GB82 WEST 1234' not in str(stored)

    def test_pii_leakage_rate_is_zero(self, eval_runner):
        """Production metric: run 100 test sessions, 0 PII leaks allowed"""
        results = eval_runner.run_pii_eval(n_sessions=100)
        assert results['pii_leakage_rate'] == 0.0, f'PII LEAK DETECTED: {results["leaks"]}'
```

### Namespace Isolation Tests

```python
class TestNamespaceIsolation:
    def test_actor_a_cannot_read_actor_b_memories(self, memory_client):
        """Core multi-tenant isolation guarantee"""
        # Write memory for actor A
        memory_client.put_events(
            actorId='actor-A', sessionId='sess-1',
            payload=[{'role': 'user', 'content': 'Secret: A prefers X'}],
        )
        # Retrieve as actor B -- must get empty results
        records = memory_client.retrieve_memory_records(
            namespace='/actors/actor-B/',  # actor-B's namespace
            text='preferences',
        ).get('memoryRecordSummaries', [])
        assert records == [], 'ISOLATION FAILURE: actor-B retrieved actor-A memories'

    def test_iam_namespace_condition_blocks_cross_tenant(self, sts_client):
        """Verify IAM condition key prevents namespace escape"""
        # Assume writer role for actor-A
        writer_creds = sts_client.assume_role(
            RoleArn=WRITER_ROLE_ARN, RoleSessionName='test-actor-a',
            # The role policy conditions namespace to users/{actor_id}
        )['Credentials']
        writer_client = boto3.client('bedrock-agentcore', **creds_to_kwargs(writer_creds))
        with pytest.raises(writer_client.exceptions.AccessDeniedException):
            writer_client.put_events(
                memoryId=MEMORY_ID,
                namespace='/actors/actor-B/',  # different actor's namespace
                payload=[],
            )

class TestRightToErasure:
    def test_delete_removes_all_four_layers(self, all_clients):
        # Setup: create session with STM, LTM, S3 archive, DDB record
        actor_id, session_id = setup_complete_session(all_clients)

        # Execute: call delete_session API
        delete_session_api(actor_id, session_id)

        # Assert: all 4 layers are empty
        ddb_rec = all_clients.dynamo.get_item(
            Key={'actor_id': actor_id, 'session_id': session_id}
        ).get('Item')
        assert ddb_rec is None, 'DDB record not deleted'

        stm = all_clients.memory.list_events(actorId=actor_id, sessionId=session_id).get('events', [])
        assert stm == [], 'STM events not deleted'

        ltm = all_clients.memory.retrieve_memory_records(
            namespace=f'/actors/{actor_id}/', text='anything'
        ).get('memoryRecordSummaries', [])
        assert ltm == [], 'LTM records not deleted'

        with pytest.raises(ClientError, match='NoSuchKey'):
            all_clients.s3.get_object(
                Bucket=ARCHIVE_BUCKET, Key=f'archives/{actor_id}/{session_id}/session.json.gz'
            )
```

### Resume Quality Metric

```python
def test_scenario_c_reconstruction_quality(memory_client, orchestrator, embedder):
    """
    Evaluation metric: Scenario C Resume Quality
    Target: cosine similarity of LTM-reconstructed context vs original STM context >= 0.80
    """
    # 1. Create a session with known content
    actor_id, session_id = create_test_session(memory_client, events=[
        {'role': 'user', 'content': 'I want to review Q3 fraud alerts'},
        {'role': 'assistant', 'content': 'I found 47 flagged transactions...'},
        {'role': 'user', 'content': 'Focus on card-present fraud above EUR 500'},
    ])

    # 2. Run LTM consolidation (post-session)
    run_consolidation(actor_id, session_id, memory_client)

    # 3. Simulate STM expiry
    expire_stm(actor_id, session_id)  # marks stm_status='EXPIRED'

    # 4. Build Scenario C context
    ctx = orchestrator.build_context(actor_id, session_id, 'continue')
    assert ctx['scenario'] == 'C'

    # 5. Measure semantic similarity vs original STM
    original_embedding = embedder.embed('Q3 fraud alerts card-present EUR 500')
    reconstructed_embed = embedder.embed(ctx['context_block'])
    similarity = cosine_similarity(original_embedding, reconstructed_embed)
    assert similarity >= 0.80, f'Scenario C reconstruction quality below threshold: {similarity:.3f}'
```

## Related

- [AgentCore Memory Architecture Guide](../15-agentcore-memory-architecture-guide.md) — Part 1: release timeline, executive summary, architecture core concepts, memory types taxonomy
- [AgentCore Memory Architecture Guide (Part 2)](15-agentcore-memory-architecture-guide-part2.md) — sidebar reference architecture, session resume lifecycle, multi-agent memory patterns, memory processors, framework comparison
- [AgentCore Memory Architecture Guide (Part 3)](15-agentcore-memory-architecture-guide-part3.md) — token optimisation, Strands best practices, EU banking/GDPR compliance, security/threat model, cost optimisation, PoC-to-production journey, evaluation, Terraform IaC
