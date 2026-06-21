import argparse
import datetime as dt
import json
import os
import sqlite3
import uuid
from pathlib import Path


DEFAULT_DB = Path.home() / ".codex" / "agent-lanes" / "agent_lanes.sqlite"


def utc_now():
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat()


def default_db_path():
    return Path(os.environ.get("AGENT_LANE_DB", str(DEFAULT_DB)))


def connect(db_path=None):
    path = Path(db_path) if db_path else default_db_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    init_schema(conn)
    return conn


def init_schema(conn):
    conn.executescript(
        """
        create table if not exists lanes (
            lane_id text primary key,
            thread_id text,
            role text,
            capabilities text,
            cwd text,
            status text not null,
            created_at text not null,
            heartbeat_at text not null
        );

        create table if not exists messages (
            id integer primary key autoincrement,
            from_lane text not null,
            to_lane text not null default '*',
            topic text not null,
            type text not null,
            body text not null,
            created_at text not null
        );

        create table if not exists message_reads (
            message_id integer not null,
            lane_id text not null,
            read_at text not null,
            primary key (message_id, lane_id)
        );

        create table if not exists tasks (
            task_id text primary key,
            owner_lane text not null,
            status text not null,
            title text not null,
            context text,
            result text,
            created_at text not null,
            updated_at text not null
        );
        """
    )
    conn.commit()


def add_db_arg(parser):
    parser.add_argument("--db", default=None, help="SQLite registry path.")


def new_lane_id(role):
    safe_role = "".join(ch if ch.isalnum() or ch == "-" else "-" for ch in role.lower())
    return f"{safe_role}-{uuid.uuid4().hex[:8]}"


def safe_name(value):
    cleaned = "".join(ch if ch.isalnum() or ch in ("-", "_") else "-" for ch in value.strip())
    return cleaned.strip("-_") or "agent"


def find_project_root(start=None):
    current = Path(start or Path.cwd()).resolve()
    for path in [current, *current.parents]:
        if (path / ".git").exists():
            return path
    return current


def encode_json(value):
    if value is None:
        return None
    if isinstance(value, str):
        return value
    return json.dumps(value, ensure_ascii=True, sort_keys=True)


def print_json(value):
    print(json.dumps(value, ensure_ascii=True, indent=2, sort_keys=True))


def row_to_dict(row):
    return {key: row[key] for key in row.keys()}


def common_parser(description):
    parser = argparse.ArgumentParser(description=description)
    add_db_arg(parser)
    return parser
