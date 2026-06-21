from lane_store import common_parser, connect, print_json, row_to_dict, utc_now


def main():
    parser = common_parser("Post a message to another lane or broadcast.")
    parser.add_argument("--from-lane", required=True, help="Sender lane ID.")
    parser.add_argument("--to-lane", default="*", help="Recipient lane ID, wildcard, or '*'.")
    parser.add_argument("--topic", required=True, help="Message topic.")
    parser.add_argument("--type", required=True, help="Message type.")
    parser.add_argument("--body", required=True, help="Short message body.")
    args = parser.parse_args()

    with connect(args.db) as conn:
        cursor = conn.execute(
            """
            insert into messages(from_lane, to_lane, topic, type, body, created_at)
            values (?, ?, ?, ?, ?, ?)
            """,
            (args.from_lane, args.to_lane, args.topic, args.type, args.body, utc_now()),
        )
        conn.commit()
        row = conn.execute("select * from messages where id = ?", (cursor.lastrowid,)).fetchone()

    print_json(row_to_dict(row))


if __name__ == "__main__":
    main()
