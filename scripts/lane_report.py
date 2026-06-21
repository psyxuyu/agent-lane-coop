import json
from pathlib import Path

from lane_store import common_parser, find_project_root, print_json, safe_name, utc_now
from lane_register import append_log, read_json


def main():
    parser = common_parser("Report lane status to public files and prepare parent-thread summary.")
    parser.add_argument("--root", default=None, help="Project root. Defaults to git root or current directory.")
    parser.add_argument("--role", required=True, help="Role folder name used under lane/.")
    parser.add_argument("--status", required=True, choices=["status", "completed", "blocker", "handoff"], help="Report status.")
    parser.add_argument("--summary", required=True, help="Concise public summary.")
    parser.add_argument("--task", default=None, help="Task name or ID.")
    parser.add_argument("--outputs", action="append", default=[], help="Repeatable output path.")
    parser.add_argument("--needs-parent-action", default="none", help="What the parent thread should do next.")
    args = parser.parse_args()

    project_root = Path(args.root).resolve() if args.root else find_project_root()
    role = safe_name(args.role)
    lane_root = project_root / "lane"
    public_lane_file = lane_root / "agent_lane.json"
    public_work_log = lane_root / "work_log.md"
    role_work_log = lane_root / role / "work_log.md"

    public_payload = read_json(public_lane_file, {"project_root": str(project_root), "lanes": {}})
    lane_entry = public_payload.get("lanes", {}).get(role, {})
    now = utc_now()
    lane_entry["status"] = args.status
    lane_entry["last_report_at"] = now
    public_payload.setdefault("lanes", {})[role] = lane_entry
    public_payload["updated_at"] = now
    public_lane_file.write_text(json.dumps(public_payload, ensure_ascii=True, indent=2) + "\n", encoding="utf-8")

    task_part = f" task={args.task}" if args.task else ""
    append_log(public_work_log, f"{role} {args.status}{task_part}: {args.summary}")
    append_log(role_work_log, f"report status={args.status}{task_part} summary={args.summary} outputs={args.outputs}")

    report = {
        "message_type": "lane_report",
        "role": role,
        "lane": lane_entry.get("lane"),
        "task": args.task,
        "status": args.status,
        "summary": args.summary,
        "outputs": args.outputs,
        "needs_parent_action": args.needs_parent_action,
        "reported_at": now,
        "public_work_log": str(public_work_log),
        "role_work_log": str(role_work_log),
    }
    print_json(report)


if __name__ == "__main__":
    main()
