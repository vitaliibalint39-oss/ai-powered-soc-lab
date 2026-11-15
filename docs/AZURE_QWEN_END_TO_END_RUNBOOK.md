# Azure SSH alert → local Qwen: controlled end-to-end runbook

**Status:** **Historical Azure alert → local Qwen end-to-end manual run verified on November 14, 2026 (Michigan).** This extends the [previously verified Azure-to-Wazuh transport](AZURE_WAZUH_SSH_DETECTION_2026-11-08.md) and the [local Qwen triage](../README.md). It does not imply the Azure VM was running during the November 14 analysis, continuous monitoring, autonomous response, or production readiness.

## Safety and prerequisites

- Work on authorized lab systems only; no public SSH port or inbound Wazuh port needs opening.
- The Azure VM can remain **deallocated** for the historical November 8 event if the local Wazuh Indexer still retains it. Only start Azure if new cloud evidence is essential; costs can accrue.
- Use the `soc_reader` read-only Indexer user, TLS CA verification and the existing SSH tunnel. Do not commit secrets, `root-ca.pem`, credentials, private IPs, reports, SQLite state, or raw logs.
- Human review is required. The Qwen output may be inaccurate and does not execute remediation commands.

## 1. Read-only Azure account check (PowerShell with Azure CLI)

```powershell
az account show --query "{Name:name,State:state}" -o table
az vm list -g rg-azure-devops-lab-ncus -d --query "[].{Name:name,Power:powerState}" -o table
az resource list -g rg-azure-devops-lab-ncus --query "[].{Name:name,Type:type}" -o table
```

Check Azure Portal → Cost Management + Billing → Credits/Usage for actual spend and the free-trial deadline. VM deallocation does not guarantee zero storage/IP cost.

## 2. Start local dependencies

Start the local VMware Wazuh Manager/Indexer VM (and Ubuntu SOC agent VM only if needed). Start LM Studio with the **exact** model used by `SOC_MODEL_ID`. The repo's [Ukrainian setup guide](SETUP_UK.md) documents the SSH tunnel.

Keep the tunnel open in its own PowerShell:

```powershell
ssh -i "$HOME\.ssh\id_ed25519_wazuh" -N -L 127.0.0.1:9200:127.0.0.1:9200 vitalii@192.168.238.135
```

Verify local connectivity from another PowerShell:

```powershell
Test-NetConnection 127.0.0.1 -Port 9200
Invoke-RestMethod http://127.0.0.1:1234/v1/models | Select-Object -ExpandProperty data | Select-Object id
```

The SSH destination is a previously used example and may have changed. Do **not** disable TLS verification if the CA certificate check fails.

## 3. Run the exact Azure event through the existing SOC assistant

Use an up-to-date checkout containing this change and an existing Python venv with dependencies.

```powershell
$env:SOC_AGENT_NAME = "azure-devops-lab"
$env:SOC_RULE_ID = "5710"
$env:SOC_MAX_EVENTS = "1"
$env:SOC_MODEL_ID = "qwen3.5-4b-instruct" # replace with exact ID reported by LM Studio
.\.venv\Scripts\python.exe soc_assistant.py
```

Enter `soc_reader` password **only at the local terminal prompt**. The assistant searches indexed Wazuh alerts for agent `azure-devops-lab`, Wazuh rule `5710`, level >= 5, and processes at most one new event.

## 4. Actual end-to-end verification (November 14, 2026, Michigan)

The Azure VM was not started for this run. A **historical, controlled** SSH invalid-user event from November 8 remained in the Wazuh archived alert JSON and the OpenSearch alert index.

- Wazuh Indexer returned **one matching document**, with agent `azure-devops-lab`, rule `5710`, level `5`, and timestamp `2026-11-08T00:30:25.167+0000`.
- `soc_reader` initially returned **403** after its password was updated: the existing `wazuh_soc_reader` role had correct index permissions but **no user mapping**. Assigning the existing internal user `soc_reader` to that role restored read-only search (`hits.total.value = 1`).
- SSH port forwarding from Windows to Indexer succeeded; LM Studio exposed the approved model ID `qwen3.5-4b-instruct`.
- Local offline test suite: **35 tests, OK**. GitHub Actions checks also passed on Python 3.10 and 3.12 for the proposed code.
- Initial attempt fetched one event but failed **safely** because the model output terminated with `finish_reason=length`: `completed=0, failed=1`. No incident report was accepted.
- Subsequent manual retry completed: `status=success fetched=1 selected=1 completed=1 failed=0 duration=11.172s`. A locally stored Markdown report was produced; no report content or credentials are committed here.
- The model output reported `SUSPICIOUS`, `LOW`, self-reported confidence `0.7`, and offered read-only investigation steps. **Analyst correction:** the event was the known authorized single-host loopback SSH test, so its final human disposition is **BENIGN (authorized laboratory activity)**. One failed local login does **not** establish brute force or compromise.

**Outstanding:** A second successful run with `0 new` has not yet been documented, so no-duplicate idempotence is not yet confirmed for this exact Azure event. Remaining cost / resource inventory and CI merge are separate checkpoints.

## 5. Acceptance checklist

- [x] The Wazuh indexer actually returns an event with agent `azure-devops-lab` and rule `5710`
- [x] One validated Qwen report is saved in the local `reports/` directory
- [x] The report's Wazuh rule ID and agent name match the source event
- [x] The validated report contains read-only investigation steps; human review remains required
- [ ] Re-run produces no duplicate report for the same event ID
- [x] Offline CI tests pass on supported Python versions
- [ ] No credentials, raw logs or private incident reports are pushed to GitHub

If no indexed events are found, inspect the Wazuh Dashboard / index retention and the original Manager alert data first. Do not fabricate a success report. A synthetic fixture can verify offline code only, **not** Azure-to-Qwen live connectivity.

## 6. Cost-controlled finish

Back up non-secret Terraform/Ansible and documentation to GitHub. Review `az resource list` and Azure billing before deleting or recreating anything. Deallocate any deliberately started VM when finished; resource deletion is a separate, explicit action.
