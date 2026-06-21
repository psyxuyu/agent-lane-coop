from lane_store import common_parser, connect, print_json, row_to_dict, utc_now


def main():
    parser = common_parser("Claim or refresh ownership of a shared task.")
    parser.add_argument("--lane", required=True, help="Owner lane ID.")
    parser.add_argument("--task-id", required=True, help="Stable task ID.")
    parser.add_argument("--title", required=True, help="Short task title.")
    parser.add_argument("--context", default=None, help="Optional task context.")
    parser.add_argument("--status", default="claimed", help="Task status.")
    args = parser.parse_args()

    now = utc_now()
    with connect(args.db) as conn:
        existing = conn.execute("select created_at from tasks where task_id = ?", (args.task_id,)).fetchone()
        created_at = existing["created_at"] if existing else now
        conn.execute(
            """
            insert into tasks(task_id, owner_lane, status, title, context, result, created_at, updated_at)
            values (?, ?, ?, ?, ?, null, ?, ?)
            on conflict(task_id) do update set
              owner_lane = excluded.owner_lane,
              status = excluded.status,
              title = excluded.title,
              context = excluded.context,
              updated_at = excluded.updated_at
            """,
            (args.task_id, args.lane, args.status, args.title, args.context, created_at, now),
        )
        conn.execute(
            """
            insert into messages(from_lane, to_lane, topic, type, body, created_at)
            values (?, '*', ?, 'claim', ?, ?)
            """,
            (args.lane, args.task_id, f"claimed task: {args.title}", now),
        )
        conn.commit()
        row = conn.execute("select * from tasks where task_id = ?", (args.task_id,)).fetchone()

    print_json(row_to_dict(row))


if __name__ == "__main__":
    main()
