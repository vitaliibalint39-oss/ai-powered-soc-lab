# Screenshots selected for AI-Powered SOC Lab

These screenshots come from the user-provided October 2026 archive. They document the local lab, not a production SOC deployment.

| Filename | Evidence |
|---|---|
| `01-wazuh-endpoint-dashboard.png` | Wazuh agent overview and vulnerability/security configuration panels |
| `02-wazuh-threat-hunting.png` | Alert overview including authentication failure |
| `03-wazuh-events.png` | Wazuh events table from the monitored environment |
| `04-security-configuration-assessment.png` | CIS Ubuntu benchmark assessment summary |
| `05-qwen-local-model.png` | LM Studio Qwen model selection (not server proof) |
| `06-wazuh-agent-status.png` | Wazuh agent service active in terminal |
| `07-python-ai-analysis.png` | Python processing Wazuh events into local reports |

## Suggested README section

```markdown
## Lab screenshots

### Wazuh monitoring
![Wazuh endpoint dashboard](screenshots/01-wazuh-endpoint-dashboard.png)
![Wazuh threat hunting summary](screenshots/02-wazuh-threat-hunting.png)
![Wazuh security events](screenshots/03-wazuh-events.png)

### Security assessment
![Ubuntu CIS benchmark](screenshots/04-security-configuration-assessment.png)

### Local AI triage
![Qwen model in LM Studio](screenshots/05-qwen-local-model.png)
![Wazuh agent running](screenshots/06-wazuh-agent-status.png)
![Python AI event analysis](screenshots/07-python-ai-analysis.png)
```

## Before publishing

- Review every screenshot at full size for usernames, private IP addresses, notification popups, access tokens, passwords, personal emails and other potentially sensitive details. The lab's internal IPs and account name may be visible.
- The LM Studio screenshot shows available models, **not** proof that the inference API server is running.
- The CLI screenshot documents event processing in progress, **not** a screenshot of all 20 reports completed. The 20 reports were separately confirmed in conversation.
- Avoid committing actual incident reports unless carefully anonymized.
