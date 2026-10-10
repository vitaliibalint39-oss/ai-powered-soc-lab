# AI SOC Incident Report — Synthetic SSH Test

> **Demonstration only.** This is an edited, sanitized example based on an authorized synthetic SSH log generated in an isolated lab. Identifiers, addresses and timestamps were replaced. AI-generated conclusions require human review.

## Event metadata

| Field | Value |
| --- | --- |
| Data source | Wazuh SIEM / OpenSearch |
| Agent | `ubuntu-soc` (lab host) |
| Wazuh rule | `sshd: Attempt to login using a non-existent user` |
| Wazuh rule level | 5 |
| Event category | SSH authentication failure |
| Event origin | Synthetic test using `logger` (not an actual remote login attempt) |

### Sanitized log example


Oct 10 02:21:25 ubuntu-soc sshd[1234]: Failed password for invalid user soc-test from 192.0.2.10 port 54321 ssh2

`192.0.2.10` is a documentation-only IP address. In this log syntax, `54321` is the **client source port**, not the server's SSH listening port.

## Observed facts

- A log entry describes a failed SSH password attempt for the nonexistent username `soc-test`.
- Wazuh detected and indexed the synthetic event with rule level 5.
- The sample was intentionally generated in the authorized lab; this record does **not** establish that any network connection occurred.

## Risk assessment

**Low / test event.** There is no evidence of compromise in the single synthetic record. Repeated failures for multiple users or corroborating network evidence could change the assessment.

## Suggested analyst checks (read-only)

1. Correlate related SSH logs by time and source address.
2. Confirm the source and target hosts belong to the authorized lab scope.
3. Review repeated invalid-user attempts and any succeeding successful logins.
4. Record whether the event resulted from approved testing or unexpected activity.

## Automation note

The local Python assistant retrieved indexed Wazuh alerts using a restricted OpenSearch reader account, passed selected fields to Qwen through LM Studio, and generated Markdown analysis. This edited sample documents the verified test without exposing real alert IDs or local connection details.
