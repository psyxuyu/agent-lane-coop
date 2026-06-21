from lane_store import common_parser, connect, print_json, row_to_dict, utc_now


def main():
    parser = common_parser("Refresh an active lane heartbeat.")
    parser.add_argument("--lane", required=True, help="Lane ID.")
    args = parser.parse_args()

    now = utc_now()
    with connect(args.db) as conn:
        conn.execute(
            "update lanes set status = 'active', heartbeat_at = ? where lane_id = ?",
            (now, args.lane),
        )
        conn.commit()
        row = conn.execute("select * from lanes where lane_id = ?", (args.lane,)).fetchone()

    if row is None:
        raise SystemExit(f"Lane not found: {args.lane}")
    print_json(row_to_dict(row))


if __name__ == "__main__":
    main()
