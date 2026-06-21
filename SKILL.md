---
name: agent-lane-coop
description: Register Codex threads in a shared project-level agent lane file and coordinate multiple Codex agents, subagents, or separate Codex sessions through XXAgent lane naming, a public lane index, role lane folders, work logs, work spaces, thread-tool messages, task ownership, parent-thread completion reports, dispatch checks, and structured handoffs. Use when a task needs agent lane registration, multi-agent synchronization, inter-session communication, create_thread or send_message_to_thread coordination, thread renaming, parent-child task reporting, handoffs, status broadcasts, or collaborative task claiming.
---

# Agent Lane Coop

Use this skill to coordinate work across multiple Codex agents or sessions through a project-local public lane index, role lane folders, and optional thread-tool messages.

Do not choose or override a model for this skill. It must adapt to academic, work, coding, writing, analysis, and other task types. When creating or messaging threads, omit model fields unless the user explicitly requests a specific model.

## Core Workflow

1. Locate the project root. Use the git root when present; otherwise use the current working directory or the root specified by the user.
2. Choose a simple lane name in the required format `XXAgent`, where `XX` is Chinese characters, such as `规划Agent`, `检索Agent`, `写作Agent`, `审核Agent`, or `测试Agent`.
3. If a thread title tool is available, rename the thread to the lane name with `set_thread_title`.
4. Register the current thread as an agent lane before doing collaborative work:
   `python scripts/lane_register.py --root <project_root> --role <role> --lane <XXAgent> --purpose "<responsibility>" --current-session <thread_id> --parent-session <parent_thread_id> --write-scope <path>`.
5. Read or create the public lane index:
   `lane/agent_lane.json`.
6. Ensure registration creates this structure:
   `lane/agent_lane.json`
   `lane/work_log.md`
   `lane/coordination_log.md`
   `lane/<role>/agent_lane.json`
   `lane/<role>/work_log.md`
   `lane/<role>/work_space/`
7. Poll unread messages before claiming work:
   `python scripts/lane_poll.py --lane <lane_id>`.
8. Claim the shared task before editing files or producing final outputs:
   `python scripts/lane_claim.py --lane <lane_id> --task-id <task_id> --title "<title>"`.
9. Send concise progress messages at meaningful phase boundaries:
   `python scripts/lane_post.py --from-lane <lane_id> --topic status --type status --body "<message>"`.
10. Refresh heartbeat during long work:
   `python scripts/lane_heartbeat.py --lane <lane_id>`.
11. Before ending a task turn, run a dispatch check: decide whether any work should be delegated to another lane or new thread.
12. On handoff or completion, report to the parent thread, post a `handoff` or `result` message, and close the lane if no longer active:
   `python scripts/lane_close.py --lane <lane_id>`.

Use the Python executable available in the current environment, such as `python`,
`python3`, or the local preferred interpreter.

## Public Agent Lane File

The public coordination file is:

```text
<project_root>/lane/agent_lane.json
```

Every agent must read this file before deciding who to contact or how to proceed. It records all known lanes, their purposes, sessions, write scopes, logs, work spaces, and update times.

The public file should look like:

```json
{
  "project_root": "<project_root>",
  "updated_at": "<iso timestamp>",
  "lanes": {
    "<role>": {
      "lane": "<thread or lane name>",
      "purpose": "<responsibility>",
      "current_session": "<thread id>",
      "parent_session": "<parent thread id>",
      "parent_lane": "<parent lane>",
      "write_scope": "<path>",
      "work_log": "<path>",
      "work_space": "<path>",
      "role_agent_lane": "<path>",
      "status": "active",
      "last_report_at": "<iso timestamp>",
      "updated_at": "<iso timestamp>"
    }
  }
}
```

Use the public file to answer:

- Which threads exist?
- What is each thread responsible for?
- Which thread should receive a message?
- Where are that thread's logs and outputs?
- Which scopes are safe for each thread to write?

## Public Work Log

The public concise progress log is:

```text
<project_root>/lane/work_log.md
```

Every agent must read this file before starting or resuming work. Use it to understand overall progress across threads without opening every role's detailed log.

Append short, plain progress notes to this file when a lane registers, starts a major phase, finishes a major phase, hands off work, reports a blocker, or completes its assignment. Keep entries concise: one or two sentences, enough for other threads to know what changed and where to look next.

Only read a role's detailed log when needed, such as when taking over that role's work, investigating a blocker, resolving conflicting changes, reviewing a handoff, or when the public log is too brief to proceed.

```text
<project_root>/lane/<role>/work_log.md
```

## Role Agent Lane File

Each role must register itself in:

```text
<project_root>/lane/<role>/agent_lane.json
```

The file must include:

- `lane`: thread or lane name
- `purpose`: responsibility of this role
- `current_session`: Codex thread ID when available
- `parent_session`: parent or creator Codex thread ID when available
- `parent_lane`: parent or creator lane name when available
- `write_scope`: writable scope for formal project work
- `work_log`: path to this role's `work_log.md`
- `work_space`: path to this role's output folder

Append important actions, messages, decisions, and handoffs to `work_log.md`.
Put role-specific outputs in `work_space/` unless the user or project convention requires another location.

## Root Lane Folder

Create the lane folder at the project root:

```text
<project_root>/lane/
  agent_lane.json
  work_log.md
  coordination_log.md
  inbox/
```

Create one folder per role:

```text
<project_root>/lane/<role>/
  agent_lane.json
  work_log.md
  work_space/
```

## Optional SQLite Registry

The project-local lane folder is authoritative. The SQLite registry is optional for lightweight messages and task state.

The default SQLite registry is:
`<home>/.codex/agent-lanes/agent_lanes.sqlite`.

Override it with:
`--db <path>` or the `AGENT_LANE_DB` environment variable.

Use stable lane names when a session resumes. If no lane name is provided, `lane_register.py` creates one from the role.

## Message Discipline

Post structured, short messages. Prefer these types:

- `status`: progress update
- `request`: ask another lane for help
- `claim`: announce task ownership
- `handoff`: transfer work to another lane
- `result`: publish completed work
- `blocker`: report a blocking condition

Read `references/message-schema.md` before adding new message types.

## Coordination Rules

- Read `lane/agent_lane.json` before starting substantial work.
- Read `lane/work_log.md` to understand overall project progress before deciding what to do next.
- Use `XXAgent` lane names only. `XX` must be Chinese characters, for example `规划Agent`.
- Check existing `lane/*/agent_lane.json` files when public index information is missing or stale.
- Append concise public progress to `lane/work_log.md`; append detailed role work to `lane/<role>/work_log.md`.
- Do not read every role's detailed `work_log.md` by default; inspect only the relevant role log when the task needs that detail.
- Do not write outside the registered `write_scope` unless the user explicitly expands scope.
- Do not overwrite another active lane's claimed task unless the existing lane is stale.
- Treat lanes with no heartbeat for 30 minutes as stale unless a project says otherwise.
- Broadcast blockers early with enough context for another lane to continue.
- Keep final outputs traceable to the lane that produced them.
- Treat parent-thread reporting as part of task completion. A child lane is not done until it updates logs and reports result, blocker, or handoff to its parent thread when thread tools are available.
- At the end of each planning or management exchange, run a dispatch check: identify pending work, decide whether it belongs in the current lane, an existing lane, or a new thread, then dispatch when appropriate.

Read `references/protocol.md` when implementing or changing the coordination behavior.
Read `references/coordination-patterns.md` when choosing a planning, review, handoff, or specialist-agent workflow.

## Thread Tool Bridge

When Codex thread tools are available and the user wants cross-session communication, use them as the primary bridge between sessions. Prefer `list_threads`, `read_thread`, `send_message_to_thread`, `create_thread`, and `handoff_thread`.

Before using thread tools, search for them if they are not already visible. When creating or messaging a thread, omit model and thinking overrides unless the user explicitly requests them.

After creating a new thread, send that thread a bootstrap message. The message must tell the new thread to use `$agent-lane-coop`, register itself in the same project root, read `lane/agent_lane.json`, and report back through both its work log and thread messaging when available.

If thread tools are unavailable, use the lane folder and optional SQLite registry as the communication channel.

Read `references/thread-tools.md` before creating, messaging, reading, or handing off Codex threads.
