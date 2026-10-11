# Screenshot privacy review — 2026-10-11

Source: eight PNGs supplied for inspection as an archive, corresponding to screenshots/01 through screenshots/08 in the public project.

No visually obvious plaintext passwords, API tokens, or private SSH keys were identified. This is a visual content review, **not** proof that screenshots are free of all sensitive data or metadata.

| Screenshot | Preliminary recommendation | Reason |
| --- | --- | --- |
| 01-wazuh-endpoint-dashboard.png | Review/redact as appropriate | Wazuh private IP in browser address bar; inventory and vulnerability findings |
| 02-wazuh-threat-hunting.png | Acceptable for a public synthetic lab | Aggregate event statistics and test agent |
| 03-wazuh-events.png | Acceptable for a public synthetic lab | Test agent and event descriptions |
| 04-security-configuration-assessment.png | Review/redact as appropriate | Dashboard private IP, failed CIS benchmark details |
| 05-qwen-local-model.png | Acceptable | Local model list, no apparent secrets |
| 06-wazuh-agent-status.png | Acceptable | Hostname and Fail2ban status; no apparent secrets |
| 07-python-ai-analysis.png | Recommend redacting | Windows username and local paths, real-like log entries |
| 08-qwen-api-server.png | Recommend redacting | Network-facing 100.115.12.74:1234 address; potentially private overlay networking |

Additional observations:
- 'Not secure' appears in the browser near the Dashboard URL in 01 and 04. It may reflect an untrusted browser certificate; this is distinct from the earlier successfully verified **Indexer** TLS endpoint.
- The user's LM Studio API is intentionally reachable on the network for Hermes; firewall/access restriction review is explicitly deferred.
- Redact **copies**, preserve originals for local documentation, and avoid reusing a sensitive original in future publications.
- This audit does not cover embedded image metadata, binaries in Git history, or other repository artifacts. Full security sign-off remains conditional on reviewed redactions and risk acceptance.
