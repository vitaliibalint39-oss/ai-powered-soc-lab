"""Validate untrusted local LLM triage output without extra dependencies."""
import json
import math

DISPOSITIONS = {"BENIGN", "SUSPICIOUS", "MALICIOUS", "INSUFFICIENT_EVIDENCE"}
SEVERITIES = {"INFO", "LOW", "MEDIUM", "HIGH", "CRITICAL"}
SCHEMA_VERSION = "1.0"
PROMPT_VERSION = "soc-json-v1"


def parse_analysis(content, event_id):
    if not isinstance(content, str) or not content.strip():
        raise ValueError("LLM returned empty content")
    try:
        obj = json.loads(content)
    except json.JSONDecodeError as exc:
        raise ValueError("LLM response is not valid JSON") from exc
    required = {"event_id", "disposition", "severity", "confidence",
                "observed_facts", "hypotheses", "recommended_readonly_steps",
                "requires_human_review"}
    if not isinstance(obj, dict) or set(obj) != required:
        raise ValueError("LLM JSON keys do not match the required schema")
    if obj["event_id"] != event_id:
        raise ValueError("LLM event ID mismatch")
    if obj["disposition"] not in DISPOSITIONS or obj["severity"] not in SEVERITIES:
        raise ValueError("Invalid disposition/severity")
    c = obj["confidence"]
    if isinstance(c, bool) or not isinstance(c, (float, int)) or not math.isfinite(c) or not 0 <= c <= 1:
        raise ValueError("Confidence must be a number between 0 and 1")
    for field in ("observed_facts", "hypotheses", "recommended_readonly_steps"):
        value = obj[field]
        if not isinstance(value, list) or len(value) > 20 or any(
            not isinstance(item, str) or not item.strip() or len(item) > 1000
            for item in value
        ):
            raise ValueError("Invalid list field: " + field)
    if obj["requires_human_review"] is not True:
        raise ValueError("Analyst review must be required")
    # This only verifies structure; claims still need analyst verification.
    return obj


def render_analysis(obj, model_id):
    def section(title, values):
        return "\n## " + title + "\n" + (
            "\n".join("- " + item for item in values) if values else "- None provided"
        ) + "\n"
    return (
        "## AI Triage (unverified; human review required)\n"
        + "Disposition: " + obj["disposition"] + "\n"
        + "Severity: " + obj["severity"] + "\n"
        + "Self-reported confidence (not calibrated): " + str(obj["confidence"]) + "\n"
        + "Model: " + model_id + "\n"
        + "Prompt version: " + PROMPT_VERSION + "\n"
        + "Schema version: " + SCHEMA_VERSION + "\n"
        + section("Observed facts (model claims)", obj["observed_facts"])
        + section("Hypotheses", obj["hypotheses"])
        + section("Read-only investigation steps", obj["recommended_readonly_steps"])
    )
