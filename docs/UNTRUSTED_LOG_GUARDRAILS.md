# Untrusted log guardrails — draft

This first hardening step treats Wazuh fields as untrusted evidence, limits log payload sizes, and **rejects a narrow class of unsupported claims** in model-observed facts: IPv4 addresses absent from the evidence and mistaken use of an SSH client source port as a destination/server port.

This is **not** comprehensive prompt-injection prevention or semantic fact verification. An attacker-controlled log may still influence generated hypotheses or investigation guidance. AI output remains untrusted and requires human review. The model does not receive tool-execution privileges.

## Offline test (no Wazuh / Qwen)

```powershell
git fetch origin
git switch feat/untrusted-log-guardrails
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

Expected: existing **16** tests and **6** new guardrail tests, **22** total if no earlier tests have changed.

## Follow-up before merge

1. Run the offline test suite.
2. Run an isolated synthetic hostile-log test against the local LM Studio model with thinking disabled and SOC_MODEL_ID set; do not run the full Wazuh backlog.
3. Add further attack scenarios (role spoofing, hidden instructions, invented evidence, dangerous recommendations) and evaluate the output manually.
4. Review IP parsing and source/destination port semantics for non-SSH log formats.

Do not commit local secrets, downloaded models, real alerts or generated incident reports.
