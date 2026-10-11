# Claude vs Kimi: AI-SOC-Lab Review Experiment

**Date:** October 10, 2026  
**Project:** [AI-powered SOC lab](https://github.com/vitaliibalint39-oss/ai-powered-soc-lab)  
**Kimi-reported review commit:** `9be444ff7c271711d90920dbdac2bf62e3bbf382`

## Why I ran this experiment

Out of curiosity, I asked Claude and Kimi to review the same open-source proof-of-concept SOC project using Wazuh, Python, Qwen, LM Studio, and VMware. I wanted to compare their *actual review approaches*, not declare a universal winner.

## What happened

| Dimension | Claude | Kimi |
| --- | --- | --- |
| Reported access | Repository landing page and README | Source files, dependencies, documentation, screenshots |
| Source-level citations | No; acknowledged fetch errors | Yes; included paths and line numbers |
| Live Wazuh/LM Studio testing | No | No |
| Common findings | Alert ingestion limits, prompt injection, report/state reliability | Alert ingestion limits, prompt injection, report/state reliability |
| Additional emphasis | Verification checklist, cautious architectural review | LM Studio listener exposure question, model fallback, schema validation, documentation consistency |

Both reviews highlighted the potential for missed alerts when only the newest 20 matching events are queried between manual runs. Kimi also raised additional implementation and public-screenshot questions.

## How to interpret these results

- **This is not a controlled benchmark.** Source access differed and neither model tested the live lab.
- The reviews contain a mix of observations, assumptions and recommendations. They do not constitute a certified security assessment.
- A quoted line of code should be cross-checked against the referenced commit and validated with repeatable tests.
- Model-generated recommendations are advisory; an analyst should verify important findings.

## Audit documents

The original Claude PDF, a PDF formatted from Kimi's text, and an editorial comparison were prepared separately. **The PDF files are pending privacy review and are not included in this draft branch yet.** Once redacted as needed, the three files can be added here.

## Next steps

1. Validate the individual findings against the committed source.
2. Check live LM Studio listener bindings and review publicly committed screenshots.
3. Implement reliability tests for event ingestion, retry logic, state consistency and LLM response validation.
4. Publish fixes and test results as a follow-up engineering case study.

*This page documents one informal experiment. It does not establish which AI model is generally more capable.*
