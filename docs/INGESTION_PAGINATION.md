# Wazuh alert ingestion pagination

The previous query returned only the latest 20 matching alerts. If more than 20 new alerts arrived between manual runs, some could be omitted indefinitely.

This branch uses OpenSearch's **Scroll API** with a page size of 20. The initial request searches `wazuh-alerts-*`; subsequent requests traverse the server's scroll snapshot until the indexer returns an empty page. The scroll context is then released.

## Verification

From the project directory on Windows, activate your virtual environment and run:

```powershell
python -m unittest discover -s tests -v
python soc_assistant.py
```

The SSH tunnel to the Indexer and the local LM Studio endpoint must already be running for the second command.

- Test with more than 20 *synthetic* matching events.
- Check that the fetched count exceeds 20 if enough events exist.
- Repeat the run to verify known event IDs are skipped.
- If OpenSearch reports 403, confirm whether the read-only `soc_reader` role has the permissions required for Scroll API. Do **not** switch to the admin account or disable TLS verification.
- Review whether your LM Studio model can process large backlogs before running against all history.

## Limitations / follow-up work

- **Not tested against the live lab yet.** These are mocked tests, not an integration certification.
- A scroll is a snapshot, not real-time ingestion; alerts added during the run are picked up by the next run.
- On the first run, the script may retrieve substantial historical data into memory and send unprocessed alerts for LLM analysis; monitor volume and costs (local inference still consumes resources).
- IDs are retained in `processed_events.json`; this file grows with the number of processed events.
- State and report writes are still not transactional. Parallel runs should be avoided until the planned SQLite and execution-lock improvements.
- Scroll contexts expire (2-minute keepalive); processing happens *after* the complete fetch, but fetching a very large index over a slow network can still require careful tuning.
