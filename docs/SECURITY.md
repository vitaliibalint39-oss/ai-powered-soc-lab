# Security notes

This project operates only on systems owned by or explicitly authorized for the operator.

## Privilege boundaries

- `soc_reader`: OpenSearch index search permission scoped to `wazuh-alerts-*`.
- The assistant does not require index administration, document writes, host root privileges, firewall access, or SSH execution.
- Verify effective privileges with a read-only index request and an expected 403 on the security administration API. A 403 on one endpoint is not proof that *all* write endpoints are denied; verify actual role policies before deployment.

## Network and TLS

- Indexer listens on server loopback. Use local SSH forwarding, not a firewall allow rule for TCP 9200.
- Use `root-ca.pem` and verify endpoint identity. `--ssl-revoke-best-effort` used during Windows curl diagnostics is not equivalent to full revocation assurance.
- Avoid `verify=False`, `curl -k` or global certificate bypass in operational code.
- Consider using an SSH configuration alias and certificate with suitable Subject Alternative Name if localhost identity checking fails.

## Secret and privacy handling

- Password supplied via `getpass` at run time; never store it in source code.
- Exclude `.ssh/`, key files, `.venv/`, `root-ca.pem`, `reports/`, processed state, local settings, and unredacted Wazuh exports from Git.
- Do not publish raw alert IDs, internal user names, IP details, token strings, or sensitive command logs in examples.
- The Qwen model runs locally; still review model output as it can hallucinate or overstate threats.

## Defensive only

No automatic blocks, containment, deletion, privilege changes, or offensive scanning are performed by `soc_assistant.py`.
