from lane_store import common_parser, connect, print_json, row_to_dict, utc_now


def matches_clause():
    return """
    not exists (
      select 1 from message_reads r
      where r.message_id = messages.id and r.lane_id = ?
    )
    and (
      to_lane = '*'
      or to_lane = ?
      or (instr(to_lane, '*') > 0 and ? glob replace(to_lane, '*', '*'))
    )
    """


def main():
    parser = common_parser("Poll unread lane messages.")
    parser.add_argument("--lane", required=True, help="Recipient lane ID.")
    parser.add_argument("--limit", type=int, default=20, help="Maximum messages to return.")
    parser.add_argument("--mark-read", action="store_true", help="Mark returned messages as read.")
    args = parser.parse_args()

    with connect(args.db) as conn:
        rows = conn.execute(
            f"select * from messages where {matches_clause()} order by id limit ?",
            (args.lane, args.lane, args.lane, args.limit),
        ).fetchall()
        messages = [row_to_dict(row) for row in rows]
        if args.mark_read and rows:
            now = utc_now()
            conn.executemany(
                """
                insert or replace into message_reads(message_id, lane_id, read_at)
                values (?, ?, ?)
                """,
                [(row["id"], args.lane, now) for row in rows],
            )
            conn.commit()

    print_json(messages)


if __name__ == "__main__":
    main()
