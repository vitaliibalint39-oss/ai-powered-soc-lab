# Azure SSH alert → local Qwen: controlled end-to-end runbook

**Status:** Prepared for live validation, **not yet verified end to end**. This extends the [already verified Azure-to-Wazuh transport](AZURE_WAZUH_SSH_DETECTION_2026-11-08.md) and the [already verified local Qwen triage](../README.md). Do not claim the combined path works until a matching Azure event is retrieved and a validated report is saved.

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

## 4. Acceptance checklist

- [ ] The Wazuh indexer actually returns an event with agent `azure-devops-lab` and rule `5710`
- [ ] One validated Qwen report is saved in the local `reports/` directory
- [ ] The report's Wazuh rule ID and agent name match the source event
- [ ] No mutating remediation steps are accepted; human review remains required
- [ ] Re-run produces no duplicate report for the same event ID
- [ ] Offline CI tests pass on supported Python versions
- [ ] No credentials, raw logs or private incident reports are pushed to GitHub

If no indexed events are found, inspect the Wazuh Dashboard / index retention and the original Manager alert data first. Do not fabricate a success report. A synthetic fixture can verify offline code only, **not** Azure-to-Qwen live connectivity.

## 5. Cost-controlled finish

Back up non-secret Terraform/Ansible and documentation to GitHub. Review `az resource list` and Azure billing before deleting or recreating anything. Deallocate any deliberately started VM when finished; resource deletion is a separate, explicit action.
