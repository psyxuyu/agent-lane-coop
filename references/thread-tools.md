# Thread Tool Bridge

Use Codex thread tools when the task needs communication between Codex sessions.

## Available Tool Pattern

If thread tools are not visible, search for them first. Relevant tools include:

- `create_thread`
- `send_message_to_thread`
- `set_thread_title`
- `list_threads`
- `read_thread`
- `handoff_thread`

## Model Policy

Do not preset a model for this skill. When calling `create_thread` or `send_message_to_thread`, omit the `model` field unless the user explicitly requests a model. Also omit reasoning overrides unless the user explicitly requests them.

## Creating A Thread

Create a thread only when the user explicitly asks for a new/background thread or when the current task instruction requires a new collaborating session.

The created thread should be instructed to:

1. Use `$agent-lane-coop`.
2. Use an `XXAgent` lane name, where `XX` is Chinese characters, such as `检索Agent` or `审核Agent`.
3. Rename itself to the lane name with `set_thread_title` when the tool is available.
4. Register itself under the same project root.
5. Read `lane/agent_lane.json` and the public `lane/work_log.md`.
6. Create or refresh its own `lane/<role>/agent_lane.json`.
7. Write concise overall progress to `lane/work_log.md`.
8. Write detailed logs to its role `work_log.md`.
9. Put role outputs in its role `work_space/`.
10. Report status back through `send_message_to_thread` when available and through lane logs otherwise.

After `create_thread` succeeds:

1. Rename the created thread with `set_thread_title` to the assigned `XXAgent` name when the tool is available.
2. Send the created thread a bootstrap message with `send_message_to_thread` unless the initial prompt already contains the full bootstrap block.

The bootstrap message should include a short instruction plus a structured coordination block.

Recommended message:

````text
Use $agent-lane-coop for this collaboration lane.

Register yourself, read the public lane index, and proceed only within your assigned scope.

```json
{
  "message_type": "lane_bootstrap",
  "project_root": "<project_root>",
  "public_agent_lane": "<project_root>/lane/agent_lane.json",
  "public_work_log": "<project_root>/lane/work_log.md",
  "assigned_role": "<role>",
  "assigned_lane": "<XXAgent>",
  "purpose": "<what this thread is responsible for>",
  "current_session": "<created thread id>",
  "parent_session": "<creator thread id>",
  "parent_lane": "<creator XXAgent>",
  "write_scope": "<allowed project write scope>",
  "work_log": "<project_root>/lane/<role>/work_log.md",
  "work_space": "<project_root>/lane/<role>/work_space",
  "created_by_lane": "<creator lane name>",
  "creator_session": "<creator thread id>",
  "expected_actions": [
    "rename this thread to assigned_lane with set_thread_title when available",
    "register or refresh lane/<role>/agent_lane.json",
    "read lane/agent_lane.json before starting work",
    "read lane/work_log.md to understand overall progress",
    "read a role-specific work_log.md only when that detail is needed",
    "append concise overall progress to lane/work_log.md",
    "append detailed progress to lane/<role>/work_log.md",
    "place role outputs in work_space",
    "send status/result/blocker messages back to parent_session when thread tools are available"
  ],
  "handoff_context": "<brief task context, files, constraints, and next step>"
}
```
````

Keep the bootstrap block concrete. Replace placeholders before sending it. Do not include a model setting unless the user explicitly requested one.

## Parent Report

Child lanes must report to the parent thread before considering a task complete. Prefer running `scripts/lane_report.py` first so public files are updated, then send the printed report to `parent_session` with `send_message_to_thread`.

Completion report template:

```text
任务完成汇报

role: <role>
lane: <XXAgent>
task: <task name or id>
status: completed
outputs:
- <output path>
summary:
<brief result summary>
needs_parent_action:
<what the parent should do next, or none>
```

Blocker report template:

```text
任务阻塞汇报

role: <role>
lane: <XXAgent>
task: <task name or id>
status: blocker
attempted:
<what was tried>
blocker:
<what prevents progress>
needs_parent_action:
<decision or resource needed>
```

## Dispatch Check

Parent or manager lanes must run a dispatch check after planning, after receiving a child report, and before ending a management turn.

Ask:

- Is there a pending task that belongs to another existing lane?
- Is there a pending task that needs a new thread?
- Is the current thread doing work that should be delegated?
- Has each child lane received a bootstrap message and a clear parent session?
- Is `lane/work_log.md` updated with the dispatch decision?

If dispatch is needed, use `create_thread` or `send_message_to_thread`, then update `lane/work_log.md`.

## Messaging A Thread

When sending a message to another thread, include:

- target role or lane
- purpose of the message
- task ID or file paths
- expected action
- where to write logs and outputs

Keep messages short enough to be actionable without flooding the target thread.

## Reading A Thread

Use `read_thread` before sending a follow-up when current status is unclear. Summarize only the relevant status back into the lane `work_log.md`.

## Handoff

Before handoff:

1. Append a handoff note to the current role's `work_log.md`.
2. Send the destination thread a concise prompt with project root, role, task state, and expected next action.
3. Update `agent_lane.json` if the current session or role ownership changes.
