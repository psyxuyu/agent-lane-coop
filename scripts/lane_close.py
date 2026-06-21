from lane_store import common_parser, connect, print_json, row_to_dict, utc_now


def main():
    parser = common_parser("Mark a lane inactive.")
    parser.add_argument("--lane", required=True, help="Lane ID.")
    parser.add_argument("--reason", default="closed", help="Reason to store as a final message.")
    args = parser.parse_args()

    now = utc_now()
    with connect(args.db) as conn:
        conn.execute(
            "update lanes set status = 'inactive', heartbeat_at = ? where lane_id = ?",
            (now, args.lane),
        )
        conn.execute(
            """
            insert into messages(from_lane, to_lane, topic, type, body, created_at)
            values (?, '*', 'lane', 'status', ?, ?)
            """,
            (args.lane, args.reason, now),
        )
        conn.commit()
        row = conn.execute("select * from lanes where lane_id = ?", (args.lane,)).fetchone()

    if row is None:
        raise SystemExit(f"Lane not found: {args.lane}")
    print_json(row_to_dict(row))


if __name__ == "__main__":
    main()
