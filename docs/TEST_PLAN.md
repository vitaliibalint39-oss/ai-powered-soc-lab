# Test plan

Run on an authorized isolated lab. Keep sensitive outputs local.

| ID | Test | Expected result | Status |
| --- | --- | --- | --- |
| T01 | Wazuh Agent active on Ubuntu-SOC | Agent active and server displays events | Observed |
| T02 | Inject synthetic invalid-user SSH entry with `logger` | Matching Wazuh rule / event visible | Observed |
| T03 | SSH tunnel + local OpenSearch GET | HTTPS endpoint responds with 401 without login | Observed |
| T04 | OpenSearch read-only user `_count` | Valid JSON count | Observed |
| T05 | OpenSearch security administration GET as `soc_reader` | HTTP 403 | Observed |
| T06 | Run script with LM Studio | Markdown incident reports are written | Observed |
| T07 | Run script twice without new alerts | No duplicate reports for processed IDs | To verify |
| T08 | Stop LM Studio, then run | Friendly failure; unprocessed ID remains retriable | To verify |
| T09 | Stop SSH tunnel, then run | Connection error; no state corruption | To verify |
| T10 | Invalid CA / hostname | TLS verification fails closed | To verify |
| T11 | Simulated high alert volume beyond 20 entries | Known gap documented / planned pagination | Not implemented |
| T12 | Redact report sample before public commit | No personal data/secrets in Git diff | To verify |

## Synthetic SSH test

On the monitored Ubuntu-SOC VM, the previously used laboratory entry was:

```bash
sudo logger -p authpriv.warning -t sshd "Failed password for invalid user soc-test from 192.168.238.100 port 54321 ssh2"
```

This is a **log injection**, not an actual SSH connection attempt. The number after `port` is the client source port. Depending on Wazuh log collection settings and detection rules, matching alerts may vary.
