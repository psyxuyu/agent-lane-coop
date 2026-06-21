import json
import re
from pathlib import Path

from lane_store import (
    common_parser,
    connect,
    encode_json,
    find_project_root,
    print_json,
    row_to_dict,
    safe_name,
    utc_now,
)

LANE_NAME_RE = re.compile(r"^[\u4e00-\u9fff]+Agent$")
HAN_RE = re.compile(r"^[\u4e00-\u9fff]+$")


def append_log(path, message):
    timestamp = utc_now()
    if not path.exists():
        path.write_text(f"# Work Log\n\n", encoding="utf-8")
    with path.open("a", encoding="utf-8") as handle:
        handle.write(f"- {timestamp} {message}\n")


def read_json(path, default):
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return default


def update_public_lane(public_lane_file, project_root, role, role_payload, role_agent_lane, status):
    now = utc_now()
    default = {
        "project_root": str(project_root),
        "updated_at": now,
        "lanes": {},
    }
    public_payload = read_json(public_lane_file, default)
    public_payload.setdefault("project_root", str(project_root))
    public_payload.setdefault("lanes", {})
    public_payload["updated_at"] = now
    public_payload["lanes"][role] = {
        **role_payload,
        "role_agent_lane": str(role_agent_lane),
        "status": status,
        "updated_at": now,
    }
    public_lane_file.write_text(json.dumps(public_payload, ensure_ascii=True, indent=2) + "\n", encoding="utf-8")
    return public_payload


def resolve_lane_name(role, lane):
    if lane:
        if not LANE_NAME_RE.fullmatch(lane):
            raise SystemExit("Lane name must use format XXAgent, where XX is Chinese characters. Example: 规划Agent")
        return lane
    if LANE_NAME_RE.fullmatch(role):
        return role
    if HAN_RE.fullmatch(role):
        return f"{role}Agent"
    raise SystemExit("Missing valid --lane. Use format XXAgent, where XX is Chinese characters. Example: --lane 规划Agent")


def main():
    parser = common_parser("Register or refresh an agent lane.")
    parser.add_argument("--root", default=None, help="Project root. Defaults to git root or current directory.")
    parser.add_argument("--role", required=True, help="Role folder name, preferably Chinese, such as 规划, 检索, 写作, 审核.")
    parser.add_argument("--lane", default=None, help="Thread or lane name. Must use format XXAgent, such as 规划Agent.")
    parser.add_argument("--purpose", required=True, help="Responsibility of this role.")
    parser.add_argument("--current-session", default=None, help="Codex thread ID when available.")
    parser.add_argument("--parent-session", default=None, help="Parent/creator Codex thread ID when available.")
    parser.add_argument("--parent-lane", default=None, help="Parent/creator lane name when available.")
    parser.add_argument("--write-scope", default=None, help="Writable scope for formal project work.")
    parser.add_argument("--capability", action="append", default=[], help="Repeatable capability label for optional SQLite state.")
    parser.add_argument("--cwd", default=str(Path.cwd()), help="Working directory for optional SQLite state.")
    args = parser.parse_args()

    project_root = Path(args.root).resolve() if args.root else find_project_root()
    role = safe_name(args.role)
    lane_name = resolve_lane_name(args.role, args.lane)
    write_scope = str(Path(args.write_scope).resolve()) if args.write_scope else str(project_root)

    lane_root = project_root / "lane"
    public_lane_file = lane_root / "agent_lane.json"
    public_work_log = lane_root / "work_log.md"
    coordination_log = lane_root / "coordination_log.md"
    inbox = lane_root / "inbox"
    role_dir = project_root / "lane" / role
    work_log = role_dir / "work_log.md"
    work_space = role_dir / "work_space"
    agent_lane_file = role_dir / "agent_lane.json"

    lane_root.mkdir(parents=True, exist_ok=True)
    inbox.mkdir(parents=True, exist_ok=True)
    role_dir.mkdir(parents=True, exist_ok=True)
    work_space.mkdir(parents=True, exist_ok=True)

    payload = {
        "lane": lane_name,
        "purpose": args.purpose,
        "current_session": args.current_session,
        "parent_session": args.parent_session,
        "parent_lane": args.parent_lane,
        "write_scope": write_scope,
        "work_log": str(work_log),
        "work_space": str(work_space),
    }
    agent_lane_file.write_text(json.dumps(payload, ensure_ascii=True, indent=2) + "\n", encoding="utf-8")
    update_public_lane(public_lane_file, project_root, role, payload, agent_lane_file, "active")
    append_log(public_work_log, f"{role} registered as {lane_name}: {args.purpose}")
    append_log(work_log, f"registered lane={lane_name} role={role} purpose={args.purpose}")
    append_log(coordination_log, f"registered role={role} lane={lane_name} session={args.current_session or 'unknown'}")

    now = utc_now()
    with connect(args.db) as conn:
        existing = conn.execute("select lane_id, created_at from lanes where lane_id = ?", (lane_name,)).fetchone()
        created_at = existing["created_at"] if existing else now
        capabilities = list(args.capability)
        capabilities.append(f"role:{role}")
        conn.execute(
            """
            insert into lanes(lane_id, thread_id, role, capabilities, cwd, status, created_at, heartbeat_at)
            values (?, ?, ?, ?, ?, 'active', ?, ?)
            on conflict(lane_id) do update set
              thread_id = excluded.thread_id,
              role = excluded.role,
              capabilities = excluded.capabilities,
              cwd = excluded.cwd,
              status = 'active',
              heartbeat_at = excluded.heartbeat_at
            """,
            (
                lane_name,
                args.current_session,
                role,
                encode_json(capabilities),
                args.cwd,
                created_at,
                now,
            ),
        )
        conn.commit()
        row = conn.execute("select * from lanes where lane_id = ?", (lane_name,)).fetchone()

    result = row_to_dict(row)
    result.update(
        {
            "agent_lane": str(agent_lane_file),
            "public_agent_lane": str(public_lane_file),
            "public_work_log": str(public_work_log),
            "coordination_log": str(coordination_log),
            "inbox": str(inbox),
            "work_log": str(work_log),
            "work_space": str(work_space),
            "project_root": str(project_root),
        }
    )
    print_json(result)


if __name__ == "__main__":
    main()
