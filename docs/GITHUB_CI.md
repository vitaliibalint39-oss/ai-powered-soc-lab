# GitHub Actions CI (stage 7)

The `Python CI` workflow runs on pull requests, pushes to `main`, and manual dispatch. It runs a matrix of Python 3.10 and 3.12 on GitHub-hosted Ubuntu, compiles source files, and executes the standard-library `unittest` suite.

This is an **offline/mock test job**. No SSH key, Indexer password, Wazuh server, VMware machine, or LM Studio/Qwen API is needed. The workflow grants the GitHub token read-only repository access and has a 10-minute job timeout.

## Acceptance check

1. Visit PR Actions / Checks and confirm both Python matrix jobs pass.
2. If GitHub Actions are disabled on the repository, enable them in repository settings.
3. A passing CI suite shows that the mocked tests passed; it does not demonstrate live Wazuh or Qwen correctness.

Do not add live SOC credentials as GitHub Actions secrets just to run these unit tests.
