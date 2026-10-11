"""Deterministic safeguards for untrusted Wazuh log text."""
import ipaddress
import re

MAX_LOG_CHARS = 4000
MAX_DESC_CHARS = 300

def safe_alert(alert):
    if not isinstance(alert, dict):
        raise ValueError("Alert must be an object")
    rule = alert.get("rule") if isinstance(alert.get("rule"), dict) else {}
    agent = alert.get("agent") if isinstance(alert.get("agent"), dict) else {}
    data = alert.get("data") if isinstance(alert.get("data"), dict) else {}
    return {
        "timestamp": str(alert.get("timestamp", ""))[:80],
        "agent": {"name": str(agent.get("name", ""))[:120]},
        "rule": {
            "level": rule.get("level") if isinstance(rule.get("level"), int) else None,
            "description": str(rule.get("description", ""))[:MAX_DESC_CHARS],
        },
        "data": {"srcip": str(data.get("srcip", ""))[:64]},
        "full_log": str(alert.get("full_log", ""))[:MAX_LOG_CHARS],
    }

def validate_grounding(result, alert):
    """Reject obvious unsupported assertions; does not establish factual accuracy."""
    facts = " ".join(result["observed_facts"])
    log = str(alert.get("full_log", ""))
    source = str(alert.get("data", {}).get("srcip", "")).strip()
    if source:
        try:
            ipaddress.ip_address(source)
        except ValueError:
            raise ValueError("Source IP in event is invalid")
    # Only reject claims of exact IPv4 addresses not present in evidence.
    evidence = repr(alert)
    ips = set(re.findall(r"(?<![\w.])(?:\d{1,3}\.){3}\d{1,3}(?![\w.])", facts))
    for ip in ips:
        if ip not in evidence:
            raise ValueError("Observed facts contain unsupported IP: " + ip)
    # Treat SSH 'from A.B.C.D port N' explicitly as source port.
    source_ports = re.findall(
        r"\bfrom\s+\S+\s+port\s+(\d+)\b", log, re.IGNORECASE
    )
    if source_ports and re.search(
        r"\b(?:destination|target|server|listening)\s+port\s+(" +
        "|".join(map(re.escape, source_ports)) + r")\b",
        facts, re.IGNORECASE
    ):
        raise ValueError("Client source port incorrectly labeled destination")
    return result

# Conservative denylist for actions that change systems. This is defense in depth,
# not a complete semantic safety classifier.
MUTATING_ACTION = re.compile(
    r"\b(?:block|ban|denylist|blacklist|drop|reject|delete|remove|"
    r"disable|stop|kill|restart|shutdown|quarantine|isolate|"
    r"modify|change|update|install|uninstall|reboot)\b",
    re.IGNORECASE,
)

def validate_readonly_steps(result):
    for step in result["recommended_readonly_steps"]:
        if MUTATING_ACTION.search(step):
            raise ValueError("Non-read-only recommendation rejected: " + step)
    return result
