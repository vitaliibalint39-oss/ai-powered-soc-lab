# Live Qwen schema verification

Date: 2026-10-11; user-reported Windows/LM Studio local test.

- Model: `qwen3.5-4b-instruct` (explicit `SOC_MODEL_ID`).
- LM Studio 0.4.25 inference setting: **Enable Thinking off**.
- Short API response control: `finish_reason=stop`, 6 completion tokens, 0 reasoning tokens, `{"status":"ok"}`.
- `soc_assistant.analyze(..., "synthetic:ssh:005", synthetic_event)` returned a **VALIDATED SOC REPORT** with disposition SUSPICIOUS, LOW severity, and read-only investigation steps.
- This validates successful generation, JSON parsing, schema validation and Markdown rendering for one synthetic SSH event. It does not validate factual accuracy or continuous production processing.
- **Analyst caution:** model described port 54321 as an attempted connection port without clarifying it is the client-side **source port** in `from 192.0.2.10 port 54321`. Brute-force / lateral movement are hypotheses without supporting multi-event evidence. The source IP 192.0.2.10 is a reserved documentation address, not a real threat. Future prompt and factual-grounding tests should explicitly enforce these distinctions.
- `Enable Thinking` may be a model/load-time setting. Check it remains disabled when reopening LM Studio or running through the API. Retain validation and reject incomplete completions.
- No real Wazuh records or local SQLite were modified by this test.
