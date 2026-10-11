# SOC run telemetry (Stage 6)

This development branch creates a local `logs/soc_runs.jsonl` file containing **aggregate counts only** (timestamps, duration, fetched, pending, selected, completed, failed, status). No credentials, raw alerts, report bodies or model output are written to this file.

Statuses:
- `success`: no event failures were caught and the run returned normally.
- `partial_failure`: one or more selected events failed; the CLI returns a nonzero exit code.
- `failed`: an unhandled error occurred; the CLI returns nonzero.

`logs/` is ignored by Git. The existing manual `getpass` authentication still applies. **This branch does not schedule anything and does not eliminate interactive authentication.**

Offline test without live Wazuh or LM Studio:

```powershell
git fetch origin
git switch feat/soc-run-logging
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

Expected **31 tests** (27 previous and 4 new). Do not launch `soc_assistant.py` yet merely to validate logging: real Wazuh alerts could reach Qwen. Live smoke-test and eventual Task Scheduler configuration require a separate checkpoint and secure credential plan.

Limits: JSONL write failures can themselves cause a failed run; a forced process termination will not write a final record. The run journal is not an authoritative transactional event ledger (SQLite still owns event state).
