# Agent Lane Protocol

## Project Lane Folder

Use the project-local `lane/agent_lane.json` file as the authoritative public registry. Role folders provide detailed per-role state.

Each project that invokes this skill must have:

```text
<project_root>/lane/
  agent_lane.json
  work_log.md
  coordination_log.md
  inbox/
```

Each role must have:

```text
<project_root>/lane/<role>/
  agent_lane.json
  work_log.md
  work_space/
```

The public `lane/agent_lane.json` file must include all known lanes:

```json
{
  "project_root": "project root path",
  "updated_at": "ISO timestamp",
  "lanes": {
    "planner": {
      "lane": "thread or lane name",
      "purpose": "responsibility of this role",
      "current_session": "Codex thread id when available",
      "parent_session": "parent or creator Codex thread id when available",
      "parent_lane": "parent or creator lane name when available",
      "write_scope": "formal project writable scope",
      "work_log": "path to role work_log.md",
      "work_space": "path to role work_space folder",
      "role_agent_lane": "path to role agent_lane.json",
      "status": "active",
      "last_report_at": "ISO timestamp for last parent report",
      "updated_at": "ISO timestamp"
    }
  }
}
```

Each role `lane/<role>/agent_lane.json` must include:

```json
{
  "lane": "thread or lane name",
  "purpose": "responsibility of this role",
  "current_session": "Codex thread id when available",
  "parent_session": "parent or creator Codex thread id when available",
  "parent_lane": "parent or creator lane name when available",
  "write_scope": "formal project writable scope",
  "work_log": "path to work_log.md",
  "work_space": "path to work_space folder"
}
```

Append concise overall progress to `lane/work_log.md`. This public log is the default progress surface for all threads.

Append all meaningful role details to `lane/<role>/work_log.md`. The role log is allowed to be longer and more granular, but other lanes should read it only when they need role-specific context, such as handoff, takeover, blocker analysis, conflict resolution, or review.

Append cross-role coordination events to `lane/coordination_log.md`. Put generated artifacts for the role in `work_space/` unless the user or project conventions require another output location.

## Optional SQLite Registry

Use SQLite only as an optional message and task state store. The scripts create the schema automatically when SQLite-backed commands are used.

Default path:

```text
<home>/.codex/agent-lanes/agent_lanes.sqlite
```

Environment override:

```text
AGENT_LANE_DB
```

CLI override:

```text
--db <path>
```

## Lane Lifecycle

1. `register`: create or refresh `lane/agent_lane.json`, `lane/work_log.md`, `lane/coordination_log.md`, `lane/inbox/`, `lane/<role>/agent_lane.json`, role `work_log.md`, and `work_space/`; optionally refresh SQLite lane state.
2. `heartbeat`: update `heartbeat_at` and keep the lane active.
3. `poll`: read messages addressed to the lane or broadcast messages.
4. `claim`: claim or refresh ownership of a task.
5. `post`: send a structured message to one lane, a role pattern, or broadcast.
6. `close`: mark a lane inactive.

## Naming

Use only `XXAgent` lane names, where `XX` is Chinese characters. Good examples:

- `规划Agent`
- `检索Agent`
- `写作Agent`
- `审核Agent`
- `测试Agent`

When a thread title tool is available, rename the thread to the lane name after thread creation or registration.

## Completion Reporting

A child lane has not completed its assignment until it:

1. Updates `lane/<role>/work_log.md` with detailed work.
2. Updates `lane/work_log.md` with a concise public progress note.
3. Updates `lane/agent_lane.json` status and `last_report_at`.
4. Sends a result, blocker, or handoff message to `parent_session` with `send_message_to_thread` when available.

## Staleness

Treat a lane as stale when:

- `status` is not `active`; or
- `heartbeat_at` is older than the selected stale threshold.

The default stale threshold is 30 minutes.

## Ownership

Only one active lane should own a task at a time. A lane may take over a task when the current owner is stale. When in doubt, post a `request` message before taking over.

## Conflict Handling

If two active lanes claim the same task, prefer the earliest active claim. The later lane should post a `request` or `handoff` message and wait for confirmation unless the user explicitly directs otherwise.
