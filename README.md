# AI-Powered SOC Lab

**Wazuh SIEM + OpenSearch + Python + Local Qwen LLM**

A hands-on, defensive security operations lab that collects Linux security alerts, retrieves selected Wazuh alerts through a secured SSH tunnel, and uses a locally hosted language model to generate investigation notes. No cloud LLM API is required.

> **Project status:** Working proof of concept (manual batch processing). This is not an autonomous incident-response system or a production SOC deployment. Analyst review is required.

## Architecture


flowchart LR
  A[Ubuntu-SOC VM\n192.168.238.136\nWazuh Agent] -->|1514/TCP telemetry| B[Wazuh-SIEM VM\n192.168.238.135\nManager + Indexer]
  B -->|Index 9200 bound to loopback| C[SSH tunnel over TCP 22]
  C -->|Windows localhost:9200| D[Python SOC Assistant]
  D -->|localhost:1234/v1| E[LM Studio\nQwen 3.5 4B]
  E --> D
  D --> F[Local Markdown reports\nreports/]
  B --> G[Wazuh Dashboard\nHTTPS 443]


The local VM addresses above are **examples from this lab**. Adjust them for your network. The tunnel does not expose OpenSearch port 9200 to the VM network.

## Verified milestones

- Deployed Ubuntu 24.04 LTS VMs for the Wazuh server and monitored endpoint.
- Confirmed Wazuh Agent active and Wazuh Dashboard receiving security events.
- Injected a **synthetic** SSH authentication failure with `logger` and observed the matching Wazuh detection. This was not a real SSH attack.
- Queried alerts from OpenSearch using the Indexer API over an SSH tunnel.
- Used a `soc_reader` account with a custom `wazuh_soc_reader` role. Tested successful read access and `403 Forbidden` for the security administration endpoint.
- Sent alerts to a local Qwen 3.5 4B Instruct model via LM Studio and saved Markdown reports.
- Tested an initial batch run; subsequent successful events should be tracked via `processed_events.json`.

## Technology stack

| Layer | Technology |
| --- | --- |
| Virtualization | VMware (NAT / VMnet8) |
| Monitored host | Ubuntu 24.04 LTS; Wazuh Agent |
| SIEM / alert storage | Wazuh Manager, Dashboard, Indexer (OpenSearch API) |
| Secure access | SSH public-key auth, loopback port forwarding, Indexer CA certificate |
| Automation | Python 3.10+, `requests` |
| Local LLM | LM Studio OpenAI-compatible endpoint; Qwen 3.5 4B Instruct |
| Output | Local Markdown incident reports |

## Quick start (Windows PowerShell)

1. Install Python 3.10+, LM Studio, VMware, and the Wazuh infrastructure following the appropriate vendor guides. Load the Qwen model in LM Studio and start its local server at `127.0.0.1:1234`.
2. Configure an SSH key on the Wazuh server for the account allowed to establish the tunnel.
3. Ensure OpenSearch Indexer listens only on the server's loopback interface and is reachable locally as HTTPS `127.0.0.1:9200`.
4. On Windows, establish the tunnel in a **separate terminal** (keep it open):

   powershell

   ssh -i "$HOME\.ssh\id_ed25519_wazuh" -N -L 127.0.0.1:9200:127.0.0.1:9200 vitalii@192.168.238.135


   Replace the username, key path, and address as needed. Verify the SSH host fingerprint independently before first use.

5. Copy the **public CA certificate**, not any private key, to `root-ca.pem` beside the script. The HTTPS server certificate must validate for the hostname/IP used by the client. If certificate identity verification fails, fix certificate SAN/hostname rather than disabling verification.
6. Use an OpenSearch account with **read-only** access to `wazuh-alerts-*`, named `soc_reader` in the example.
7. In a second PowerShell terminal, run:


   cd "$HOME\AI-SOC-Lab"
   py -m venv .venv
   .\.venv\Scripts\python.exe -m pip install -r requirements.txt
   .\.venv\Scripts\python.exe -m py_compile soc_assistant.py
   .\.venv\Scripts\python.exe soc_assistant.py


The script requests the `soc_reader` password interactively. It retrieves up to **20 latest** alerts for `ubuntu-soc` at Wazuh rule level **5 or higher**, processes unseen IDs, and saves a Markdown report for each successful AI response.

## Configuration

Edit these constants at the top of `soc_assistant.py` as required:

- `INDEXER`: HTTPS connection through the SSH tunnel, default `https://127.0.0.1:9200`.
- `LM_STUDIO`: local inference endpoint, default `http://127.0.0.1:1234/v1`.
- `USERNAME`: read-only Indexer account, default `soc_reader`.
- `BATCH_SIZE`: 20.
- `MIN_LEVEL`: 5.
- `agent.name` filter inside `get_alerts()`: currently `ubuntu-soc`.

## Security design

- No remote execution or automatic firewall blocking by the model.
- Indexer connectivity uses SSH local forwarding; avoid opening TCP 9200 on the VM network.
- The script uses the Indexer root CA certificate with `requests` TLS verification enabled.
- The Indexer username is unprivileged; use admin credentials **only for initial role/user setup**, not the application.
- Log contents are treated as untrusted input. Model output is advisory and can be wrong.
- Do **not** commit credentials, private SSH keys, certificates containing private keys, environment files, real logs, raw incident reports, or local state.
- Although CA certificates are public, `root-ca.pem` is excluded from the public repo by default to avoid confusing environment-specific trust anchors.

## Known limitations

- This is **manually launched batch processing**, not scheduled or continuous monitoring.
- Only the latest 20 matching alerts are queried. Events outside that window can be missed; pagination and checkpoint-based ingestion are needed for completeness.
- Alerts can be benign. Wazuh rule levels and model severity assessments are not equivalent.
- `processed_events.json` prevents many reruns of the same alert ID, but report writing and state saving are not a transactional system.
- Model output can be truncated by its token limit and must be reviewed.
- Raw event metadata and AI report content can expose sensitive details. **Review and redact** any sample before publishing.
- Local inference performance depends on available RAM/VRAM and model settings.

## Validation evidence

- Synthetic SSH log: `Failed password for invalid user soc-test from 192.168.238.100 port 54321 ssh2` detected by Wazuh. `54321` is the **client source port** in that syntax.
- OpenSearch alert indexes were queried successfully; read-only credentials could read alerts, while the security administration endpoint returned HTTP 403.
- Qwen analyzed PAM, sudo, and AppArmor-related Wazuh alerts and generated report files. These are model-generated assessments, **not confirmed security incidents**.

## Roadmap

- [x] Wazuh Manager, Agent, Dashboard, Indexer
- [x] Synthetic SSH event test
- [x] SSH-tunneled Indexer connection
- [x] Read-only `soc_reader` account
- [x] Local Qwen analysis and Markdown reports
- [x] Basic processed-ID tracking in script
- [ ] Confirm clean repeat-run behavior on the current system
- [ ] Improve alert classification and false-positive handling
- [ ] Add paginated and checkpointed ingestion
- [ ] Add scheduling and operational monitoring
- [ ] Write unit/integration tests with sanitized fixtures
- [ ] Review/report truncation handling, sensitive-field redaction, and repo publish checklist

## Repository layout


AI-SOC-Lab/
├── soc_assistant.py
├── requirements.txt
├── .gitignore
├── README.md
├── docs/
│   ├── SETUP_UK.md
│   ├── SECURITY.md
│   └── TEST_PLAN.md
├── examples/
│   └── synthetic_event.json
├── root-ca.pem             # LOCAL ONLY: do not commit
├── processed_events.json   # LOCAL ONLY: do not commit
├── .venv/                  # LOCAL ONLY: do not commit
└── reports/                # LOCAL ONLY: do not commit


**Scope:** authorized defensive testing in an isolated local lab only.
## Example AI-generated security analysis

The lab demonstrates a synthetic SSH authentication alert detected by Wazuh and analyzed locally with Qwen via LM Studio. The published report is **sanitized and reviewed**: it is an example of the pipeline rather than evidence of a real intrusion.

[View the sanitized SSH incident report](examples/ssh-incident-report.md)

> The assistant provides triage suggestions, not definitive incident findings or automated remediation.

## Project Screenshots

### Wazuh Endpoint Monitoring
![Wazuh Dashboard](screenshots/01-wazuh-endpoint-dashboard.png)

### Threat Hunting
![Threat Hunting](screenshots/02-wazuh-threat-hunting.png)

### Security Events
![Wazuh Events](screenshots/03-wazuh-events.png)

### Security Configuration Assessment
![Security Assessment](screenshots/04-security-configuration-assessment.png)

### Local Qwen Model
![Qwen Model](screenshots/05-qwen-local-model.png)

### Wazuh Agent Status
![Wazuh Agent](screenshots/06-wazuh-agent-status.png)

### Python AI SOC Assistant
![Python AI Analysis](screenshots/07-python-ai-analysis.png)

### LM Studio Local API Server
![LM Studio API](screenshots/08-qwen-api-server.png)
