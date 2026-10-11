"""Durable SOC event and report state with SQLite (Python standard library)."""
import json
import os
import sqlite3
from datetime import datetime, timezone
from pathlib import Path


class EventStore:
    def __init__(self, path, legacy_path):
        self.path = Path(path)
        self.legacy_path = Path(legacy_path)
        self.db = sqlite3.connect(str(self.path), timeout=30)
        self.db.execute("PRAGMA busy_timeout=30000")
        self.db.execute("""CREATE TABLE IF NOT EXISTS events (
            event_id TEXT PRIMARY KEY,
            status TEXT NOT NULL CHECK(status IN ('completed', 'failed')),
            report_name TEXT,
            report_body TEXT,
            error TEXT,
            updated_at TEXT NOT NULL
        )""")
        self.db.commit()
        self.migrate_legacy()

    def migrate_legacy(self):
        # A missing or corrupt legacy file must not be silently ignored.
        if not self.legacy_path.is_file():
            return
        values = json.loads(self.legacy_path.read_text(encoding="utf-8"))
        if not isinstance(values, list) or any(not isinstance(v, str) for v in values):
            raise ValueError("Legacy processed_events.json must be a list of strings")
        now = datetime.now(timezone.utc).isoformat()
        with self.db:
            self.db.executemany(
                """INSERT OR IGNORE INTO events(event_id,status,updated_at)
                   VALUES (?,'completed',?)""",
                [(value, now) for value in values],
            )
        # Leave original JSON intact as a backup; repeat migration is idempotent.

    def completed_ids(self):
        return {row[0] for row in self.db.execute(
            "SELECT event_id FROM events WHERE status='completed'")}

    def save_report(self, event_id, name, body):
        # Store the full report transactionally before exporting a Markdown copy.
        now = datetime.now(timezone.utc).isoformat()
        with self.db:
            self.db.execute(
                """INSERT INTO events(event_id,status,report_name,report_body,error,updated_at)
                   VALUES (?,'completed',?,?,NULL,?)
                   ON CONFLICT(event_id) DO UPDATE SET
                   status='completed',report_name=excluded.report_name,
                   report_body=excluded.report_body,error=NULL,updated_at=excluded.updated_at""",
                (event_id, name, body, now),
            )

    def record_failure(self, event_id, error):
        now = datetime.now(timezone.utc).isoformat()
        with self.db:
            self.db.execute(
                """INSERT INTO events(event_id,status,error,updated_at)
                   VALUES (?,'failed',?,?)
                   ON CONFLICT(event_id) DO UPDATE SET
                   status='failed',error=excluded.error,updated_at=excluded.updated_at
                   WHERE events.status!='completed'""",
                (event_id, str(error)[:1000], now),
            )

    def export_reports(self, directory):
        directory = Path(directory)
        directory.mkdir(parents=True, exist_ok=True)
        count = 0
        for name, body in self.db.execute(
            """SELECT report_name,report_body FROM events
               WHERE status='completed' AND report_name IS NOT NULL"""
        ):
            target = directory / name
            if target.is_file():
                continue
            tmp = directory / (name + ".tmp")
            tmp.write_text(body, encoding="utf-8")
            os.replace(tmp, target)
            count += 1
        return count

    def close(self):
        self.db.close()
