# SQLite state migration — verification guide

This branch replaces the processed event ID JSON ledger with SQLite (`soc_state.sqlite3`). The original `processed_events.json` is **never deleted or overwritten**; its string IDs are imported with `INSERT OR IGNORE`.

## Safety first

This is an **unverified development branch**. Do not run a full `soc_assistant.py` batch against 152 alerts yet: it would invoke Qwen for every unprocessed alert.

After switching to this branch:

```powershell
git fetch origin
git switch feat/sqlite-event-state
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

Check that the existing pagination tests and the new SQLite tests pass. The new tests use a temporary database and do **not** connect to Wazuh or LM Studio.

Optional safe local migration check, without calling Wazuh or Qwen:

```powershell
Copy-Item .\processed_events.json .\processed_events.backup.json
@'
from event_store import EventStore
from pathlib import Path
s = EventStore(Path("soc_state.sqlite3"), Path("processed_events.json"))
print("Completed IDs migrated:", len(s.completed_ids()))
s.close()
'@ | .\.venv\Scripts\python.exe -
```

If `processed_events.json` does not exist, skip the `Copy-Item` command. Do not publish the backup or SQLite database.

## Behavior and limits

- Completed event IDs are migrated without changing the original JSON.
- A full report is committed to SQLite first; missing Markdown exports can be reconstructed at the next run.
- Failed events are recorded and remain eligible to retry.
- A `.soc_assistant.lock` file prevents two cooperative instances from running at once. On an abrupt process kill, confirm no instance is running before removing a stale lock file.
- `soc_state.sqlite3`, SQLite sidecars, and the lock are ignored by Git.
- This stage does **not** provide human review, complete schema validation, or a bounded AI backlog. A full run can take a long time.
- Report files should remain private; the database includes the full generated report content.

## Acceptance criteria

- All unit tests pass locally.
- Migration count matches the previous JSON set, if present.
- Report export recovers after a simulated crash.
- The main branch remains unchanged until the user verifies the results.
