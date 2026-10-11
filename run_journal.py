"""Local, low-detail structured run logging without raw events or credentials."""
import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

def utc_now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")

class RunJournal:
    def __init__(self, path):
        self.path = Path(path)
        self.start = time.monotonic()
        self.started_at = utc_now()
        self.counts = {"fetched": 0, "pending": 0, "selected": 0, "completed": 0, "failed": 0}
        self.status = "running"

    def set_counts(self, **counts):
        for key, value in counts.items():
            if key not in self.counts or type(value) is not int or value < 0:
                raise ValueError("Invalid journal count")
            self.counts[key] = value

    def finish(self, status):
        if status not in ("success", "partial_failure", "failed"):
            raise ValueError("Invalid journal status")
        self.status = status
        record = {
            "started_at": self.started_at,
            "finished_at": utc_now(),
            "duration_seconds": round(time.monotonic() - self.start, 3),
            "status": status,
            **self.counts,
        }
        self.path.parent.mkdir(exist_ok=True, parents=True)
        with self.path.open("a", encoding="utf-8") as stream:
            stream.write(json.dumps(record, ensure_ascii=False) + "\n")
        return record

def print_summary(record):
    print(
        "SOC run status={status} fetched={fetched} selected={selected} "
        "completed={completed} failed={failed} duration={duration_seconds}s".format(**record)
    )
