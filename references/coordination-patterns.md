# Coordination Patterns

## Planner And Implementer

Use a planner lane to decompose work and claim the parent task. Use implementer lanes to claim child tasks. Implementers post `status` and `result` messages back to the planner.

Planner or manager lanes must run a dispatch check after each planning exchange and before ending a management turn. If a task belongs to another lane, send it with `send_message_to_thread` or create a new `XXAgent` thread. Record the dispatch decision in `lane/work_log.md`.

## Builder And Reviewer

Use a builder lane to make code changes. Before final delivery, post a `request` to a reviewer lane with changed files and test results. The reviewer replies with `result` or `blocker`.

## Specialist Lanes

Use role-specific lanes for domains such as frontend, backend, documents, spreadsheets, or QA. Post requests to role patterns such as `frontend-*` when the exact lane is unknown.

## Cross-Session Handoff

Before handing off:

1. Post a `handoff` message with task ID, current state, files touched, and next action.
2. Refresh the task row with the new intended owner when known.
3. Close the original lane only after the handoff is visible in the registry.

The receiving lane must report back to `parent_session` after completion or blockage. A handoff is not complete if the parent lane cannot see the outcome in `lane/work_log.md` or through a thread message.

## Blocker Broadcast

When blocked, broadcast a `blocker` message with:

- what was attempted
- exact command or tool error, if any
- current hypothesis
- what help is needed
