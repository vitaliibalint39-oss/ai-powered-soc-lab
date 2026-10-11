# Local Qwen output contract — development test

This branch changes Qwen analysis to require a **single validated JSON object**. It is not yet verified against the user's live LM Studio build or model.

## Windows checks (without Wazuh or Qwen)

```powershell
git fetch origin
git switch feat/qwen-validated-analysis
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

These tests mock the network: they do not process a 132-event backlog.

## Check the actual LM Studio model ID (read only)

With LM Studio running locally:

```powershell
.\.venv\Scripts\python.exe -c "import requests; print([m['id'] for m in requests.get('http://127.0.0.1:1234/v1/models',timeout=15).json().get('data',[])])"
```

Set the exact model ID for **the current PowerShell window only**:

```powershell
$env:SOC_MODEL_ID = "PASTE_EXACT_ID_HERE"
```

No automatic fallback is allowed.

## Compatibility note

The local LM Studio API must support `response_format: {"type": "json_object"}`. Some models may fail to follow the contract despite JSON mode. A `finish_reason` other than `stop` results in a failure, which stays retryable in the SQLite store. A successful JSON parse and shape check **does not prove factual correctness**; analyst review is mandatory.

Do **not** run `soc_assistant.py` against the full alert backlog during this step. Next, use one sanitized *synthetic* alert to verify live-model compatibility separately from OpenSearch.
