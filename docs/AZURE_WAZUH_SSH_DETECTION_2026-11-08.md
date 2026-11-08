# Azure → On-Premises Wazuh SIEM: Verified SSH Detection

**Validation date:** November 7, 2026 (Michigan) / November 8, 2026 (UTC)  
**Status:** Controlled laboratory integration completed. Azure VM subsequently deallocated.  
**Scope:** SSH event collection, transport, Wazuh detection, dashboard verification, and secure shutdown.

> This is a reproducible, authorized lab demonstration—not continuous production monitoring, evidence of a real intrusion, or an AI-assisted analysis of these particular Azure events.

## Architecture

~~~mermaid
flowchart TD
    A[Azure Ubuntu 24.04 VM] --> B[OpenSSH / systemd-journald]
    B --> C[Wazuh Agent 4.14.8]
    C -->|Tailscale private network, TCP 1514| D[Local VMware Ubuntu / Wazuh Manager 4.14.8]
    D --> E[SSH decoder: rule 5710, level 5]
    E --> F[Wazuh Dashboard / Threat Hunting]
~~~

Wazuh enrollment used TCP 1515 over the same tailnet. During this small-volume test, Tailscale reported a DERP relay path. No public inbound Wazuh ports were required.

## Proven test results

| Measurement | Result |
| --- | --- |
| Azure agent | `azure-devops-lab` |
| Agent ID | `002` |
| Wazuh Manager version | `4.14.8` |
| Wazuh Agent version | `4.14.8-1` |
| Agent status during lab | `Active` |
| SSH source | Azure VM, `journald` |
| Trigger | One invalid username on the VM's own loopback SSH service |
| Rule | `5710` — `sshd: Attempt to login using a non-existent user` |
| Level | `5` |
| Alert timestamp | `2026-11-08T00:30:25Z` |
| Source IP | `127.0.0.1` (lab loopback, not an external attacker) |
| MITRE ATT&CK mappings | `T1110.001`, `T1021.004` |
| Final Azure power state | `VM deallocated` |
| Final checked NSG | No remaining custom rules |

A filter in Wazuh Dashboard's Threat Hunting view:

~~~text
agent.id: "002" AND rule.id: "5710"
~~~

returned **one matching alert and one authentication failure**, with no successful authentications in that filtered sample. This is an independently observed result in addition to the Manager's `alerts.json` entry.

**Interpretation:** MITRE mappings are attributes of the Wazuh rule. A single deliberately invalid account test does **not** establish brute force or SSH lateral movement.

## Implementation and verification sequence

1. Confirmed that Wazuh Manager was running and recovered its internal DB socket service with a controlled restart when agent queries failed.
2. Validated SSH rule 5710 locally using the existing `ubuntu-soc` agent (ID `001`) as a baseline.
3. Connected the Azure VM and local Wazuh Manager to the same Tailscale private network.
4. Verified that Azure could reach TCP 1514 and 1515 on the Manager over the private overlay.
5. Installed the Wazuh 4.14.8 agent on Azure and confirmed its `Active` registration from the Manager.
6. Generated one controlled invalid-user SSH event at the Azure VM's loopback address and confirmed the event in `journald`.
7. Located the corresponding rule 5710 alert in Manager logs and Dashboard.
8. Tested a new private SSH session from Windows through Tailscale, removed the temporary public TCP/22 NSG allow rule, and verified public SSH unreachable while private SSH was reachable.
9. Deallocated the Azure VM and verified `VM deallocated`; inspected the NSG and found no remaining custom rules.

## Commands used for read-only verification

On the local Wazuh Manager:

~~~bash
sudo /var/ossec/bin/wazuh-control status
sudo /var/ossec/bin/agent_control -l
sudo grep -F 'wazuh-azure-test-2026' /var/ossec/logs/alerts/alerts.json | tail -n 3
~~~

On Azure Ubuntu while the VM was running:

~~~bash
sudo systemctl is-active wazuh-agent
sudo systemctl is-active ssh
tailscale status
sudo journalctl -u ssh -u sshd -n 20 --no-pager
~~~

Azure power-state verification from Azure CLI:

~~~powershell
az vm list -g <resource-group> -d --query "[].{Name:name,State:powerState}" -o table
~~~

Use placeholders and your own account-specific values when reproducing. Never commit SSH keys, Tailscale credentials, Azure tokens, unredacted logs, or private addressing to public repositories.

## Security, cost, and scope boundaries

- The public SSH NSG rule was created temporarily for a **single administrator IP** and removed after Tailscale SSH verification.
- Deallocating the VM stops **compute** charges; storage, public IP and other components may still incur costs.
- The Wazuh Azure agent becomes disconnected while the VM is deallocated. The experiment validates event transport **while the VM was running**, not 24/7 cloud detection.
- These Azure events were not sent through this repository's Qwen workflow. No AI threat assessment or automatic remediation was tested here.
- Screenshot evidence exists from the validated lab. Public images should be redacted before publication.

## Relationship to this repository

This document extends the existing [local AI-powered SOC proof of concept](../README.md) with a **separate, verified cloud-to-local Wazuh ingest path**. The original local OpenSearch/SQLite/Qwen pipeline is documented elsewhere in this repository. These two independently tested paths should not be represented as one automatically integrated production service.

The complementary TA551 engineering blog article is maintained in the private blog source repository and requires a separately controlled production release to appear on the public website.
