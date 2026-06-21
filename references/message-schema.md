# Message Schema

Messages are stored as JSON bodies plus indexed metadata.

When the SQLite registry is not used, place message files in:

```text
<project_root>/lane/inbox/
```

Name files with timestamp, sender, and recipient when practical. Always keep enough metadata in the message body for a new thread to route the message after reading the public `lane/agent_lane.json` file.

## Required Metadata

```json
{
  "from_lane": "planner-01",
  "to_lane": "reviewer-01",
  "topic": "frontend-review",
  "type": "request",
  "body": "Please review the state model before merge."
}
```

## Addressing

Use one of:

- exact lane ID: `reviewer-01`
- wildcard role or lane prefix: `reviewer-*`
- broadcast: `*`

## Message Types

- `status`: progress update
- `request`: request help or review
- `claim`: announce task ownership
- `handoff`: transfer work or context
- `result`: publish output or decision
- `blocker`: explain a blocking condition

## Body Guidance

Keep bodies concise. Include:

- task ID when relevant
- file paths or thread IDs needed for context
- expected action
- deadline or priority only when meaningful

Avoid embedding large logs. Save large artifacts to files and reference their paths.
