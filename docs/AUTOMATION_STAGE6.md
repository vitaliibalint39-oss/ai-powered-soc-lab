# Bounded manual SOC runs (stage 6, first safety gate)

The Python SOC assistant defaults to analyzing at most **5 new events per run**, controlled by `SOC_MAX_EVENTS` (integer 1 to 20). Scroll still retrieves all matching Wazuh alerts for the snapshot; only inference is capped.

## Test without contacting Wazuh or Qwen

```powershell
git fetch origin
git switch feat/soc-bounded-runs
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

The tests should now total **27** (24 existing, 3 new). Do not start the full assistant just to test this feature.

## Follow-ups required before scheduling

- Design noninteractive credential retrieval that does not store passwords in source or Windows scheduled-task command lines.
- Add run logs, timing/health status, and appropriate exit codes on partial failure.
- Ensure local Qwen model is loaded, thinking disabled, and SSH tunnel is up.
- Add a dry-run mode and verify the cap against real read-only Wazuh counts.
- Add a Windows Task Scheduler entry only after an explicit activation decision.

No scheduled task was created in this change.
