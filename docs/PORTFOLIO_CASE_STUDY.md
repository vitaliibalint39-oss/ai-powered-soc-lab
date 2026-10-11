# AI-SOC-Lab: From AI Review to Tested Engineering Improvements

## Project summary

**Role:** Independent lab builder / system administrator / security engineering practitioner  
**Stack:** Ubuntu 24.04, VMware, Wazuh SIEM, OpenSearch, SSH, TLS, Python, SQLite, LM Studio, Qwen 3.5 4B, GitHub Actions  
**Purpose:** Showcase a defensive AI-assisted SOC triage workflow with realistic engineering controls, not a production security operations service.

## The problem

A proof-of-concept Python script initially queried only the 20 newest matching Wazuh alerts per run. This could omit earlier events if the backlog grew. Processed IDs were held in a JSON file, while unstructured LLM replies could be incomplete, inconsistent or misleading.

A public AI-assisted architecture review (Claude and Kimi) suggested areas to examine. Those reviews were not treated as independent proof of vulnerabilities; changes were validated through tests and controlled, synthetic exercises.

## What I implemented

### 1. Wazuh ingestion completeness

- Added OpenSearch Scroll pagination to enumerate a query snapshot.
- Scoped the Indexer account to relevant Wazuh alert searches and Scroll operations.
- Verified **152 fetched / 152 distinct** matching event identifiers against a count snapshot.
- Kept scroll cleanup and failures observable.

### 2. Reliable event state

- Replaced a JSON-only completed-ID ledger with SQLite.
- Imported 20 previously completed IDs without deleting the legacy file.
- Persisted full report text before Markdown export, enabling restoration after restart.
- Kept failed events eligible for retry and added a single-instance guard.

### 3. Safer local AI analysis

- Used an explicitly approved LM Studio model ID rather than silently falling back.
- Required JSON Schema-style triage output with compulsory human review.
- Rejected invalid IDs, malformed responses and truncated model completions.
- Troubleshot Qwen token exhaustion: thinking mode consumed nearly all completion budget; disabling thinking enabled a successful synthetic structured report.
- Added bounded alert text and narrow factual-claim checks (for example, SSH source port vs destination port).

### 4. Prompt-injection evaluation

A synthetic failed-SSH log contained an instruction impersonating a higher-priority system message. Qwen did not relabel the failed authentication as successful, but an initial answer suggested blocking an IP. That was outside the read-only investigation scope, so an additional recommendation filter and regression tests were added. A follow-up synthetic test produced only investigation-oriented steps.

**Caveat:** These are limited test cases. Prompt-injection resistance and model factual accuracy are not guaranteed.

### 5. Tests and CI

- Added **31 offline unit tests** using mocks and temporary SQLite files.
- Enabled GitHub Actions for Python **3.10 and 3.12**, without live Wazuh or LLM secrets.
- The first CI run exposed a regex word-boundary bug in the read-only filter; fixed it and obtained successful results for both Python versions.
- Added a five-event default processing cap and aggregate JSONL run journal for manual demonstrations.

## Verified security review

- Indexer TLS validation passed; unauthenticated Indexer requests were rejected.
- Indexer listened only on server loopback; Windows used SSH tunneling.
- SSH/UFW configuration and Windows file ACLs were reviewed.
- GitLeaks inspected 35 commits and flagged two instances of the same harmless sample JSON line, assessed as false positives.
- Eight portfolio screenshots were reviewed and replaced with redacted versions in the current repository.

**Acknowledged risks:** LM Studio listens on a network interface for the separate Hermes chatbot; its source restrictions were not verified. Historic screenshot versions persist in prior commits. This project is manual and intended for an isolated lab.

## What this demonstrates to an employer

- Linux administration, host logs and security-event interpretation
- Wazuh/OpenSearch query design and permission-aware API access
- SSH, TLS, least privilege and access-control review
- Python integration, defensive error handling, SQLite and test-driven fixes
- Local LLM integration with output contracts and human review
- Git/GitHub workflows and troubleshooting real CI failures

## Evidence

- [Project README](../README.md)
- [GitHub CI workflow](../.github/workflows/python-ci.yml)
- [Wazuh pagination verification](INGESTION_INTEGRATION_TEST_2026-10-10.md)
- [SQLite verification](SQLITE_VERIFICATION_2026-10-10.md)
- [Qwen live-model verification](QWEN_LIVE_VALIDATION_2026-10-11.md)
- [Prompt-injection retest](PROMPT_INJECTION_LIVE_TEST_2026-10-11.md)
- [Public audit overview](../audits/README.md)
- [Sanitized incident report](../examples/ssh-incident-report.md)

*All attack demonstrations described here were synthetic or authorized lab exercises.*
