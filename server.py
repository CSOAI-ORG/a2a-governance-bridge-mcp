#!/usr/bin/env python3
"""A2A Governance Bridge MCP — MEOK AI Labs. First agent-to-agent compliance protocol. Zero competitors."""

import sys, os
sys.path.insert(0, os.path.expanduser('~/clawd/meok-labs-engine/shared'))
from auth_middleware import check_access

import json, os, hashlib
from datetime import datetime, timezone
from typing import Optional
from collections import defaultdict
from mcp.server.fastmcp import FastMCP

FREE_DAILY_LIMIT = 10
_usage = defaultdict(list)
def _rl(c="anon"):
    now = datetime.now(timezone.utc)
    _usage[c] = [t for t in _usage[c] if (now-t).total_seconds() < 86400]
    if len(_usage[c]) >= FREE_DAILY_LIMIT: return json.dumps({"error": f"Limit {FREE_DAILY_LIMIT}/day"})
    _usage[c].append(now); return None

mcp = FastMCP("a2a-governance-bridge", instructions="MEOK AI Labs — A2A Governance Bridge. Compliance checking for agent-to-agent transactions. First in market.")

_trust_registry = {}
_audit_trail = []

@mcp.tool()
def verify_agent_compliance(agent_id: str, agent_description: str, required_frameworks: str = "eu_ai_act", api_key: str = "") -> str:
    """Verify a remote agent meets compliance requirements before allowing A2A transaction."""
    allowed, msg, tier = check_access(api_key)
    if not allowed:
        return {"error": msg, "upgrade_url": "https://meok.ai/pricing"}

    if err := _rl(): return err
    frameworks = [f.strip() for f in required_frameworks.split(",")]
    desc = agent_description.lower()
    checks = {}
    for fw in frameworks:
        if fw == "eu_ai_act":
            checks[fw] = {"has_risk_assessment": any(w in desc for w in ["risk", "assessment"]),
                         "has_documentation": any(w in desc for w in ["document", "technical"]),
                         "has_human_oversight": any(w in desc for w in ["human", "oversight"]),
                         "has_logging": any(w in desc for w in ["log", "audit", "trace"])}
        elif fw == "gdpr":
            checks[fw] = {"has_data_governance": any(w in desc for w in ["data", "privacy", "gdpr"]),
                         "has_consent_mechanism": any(w in desc for w in ["consent", "permission"])}
        else:
            checks[fw] = {"general_compliance": len(desc) > 50}
    
    all_pass = all(all(v.values()) for v in checks.values())
    trust_score = sum(sum(v.values()) for v in checks.values()) / max(sum(len(v) for v in checks.values()), 1)
    
    _trust_registry[agent_id] = {"score": round(trust_score, 2), "verified": datetime.now(timezone.utc).isoformat()}
    _audit_trail.append({"type": "verification", "agent": agent_id, "result": "pass" if all_pass else "fail",
                         "timestamp": datetime.now(timezone.utc).isoformat()})
    
    return {"agent_id": agent_id, "compliant": all_pass, "trust_score": round(trust_score, 2),
        "frameworks_checked": frameworks, "details": checks,
        "recommendation": "Agent cleared for A2A transactions" if all_pass else "Agent fails compliance — block transaction"}

@mcp.tool()
def authorize_a2a_transaction(source_agent: str, target_agent: str, task_description: str, data_types: str = "", api_key: str = "") -> str:
    """Authorize an agent-to-agent transaction after compliance verification."""
    allowed, msg, tier = check_access(api_key)
    if not allowed:
        return {"error": msg, "upgrade_url": "https://meok.ai/pricing"}

    if err := _rl(): return err
    source_trust = _trust_registry.get(source_agent, {}).get("score", 0)
    target_trust = _trust_registry.get(target_agent, {}).get("score", 0)
    
    authorized = source_trust >= 0.5 and target_trust >= 0.5
    
    txn_id = hashlib.sha256(f"{source_agent}{target_agent}{datetime.now(timezone.utc).isoformat()}".encode()).hexdigest()[:12]
    _audit_trail.append({"type": "transaction", "id": txn_id, "source": source_agent, "target": target_agent,
                         "authorized": authorized, "timestamp": datetime.now(timezone.utc).isoformat()})
    
    return {"transaction_id": txn_id, "authorized": authorized,
        "source": {"agent": source_agent, "trust": source_trust},
        "target": {"agent": target_agent, "trust": target_trust},
        "task": task_description, "data_sensitivity": data_types,
        "governance_note": "Both agents verified. Transaction authorized." if authorized else "One or both agents not verified. Run verify_agent_compliance first."}

@mcp.tool()
def get_trust_registry(api_key: str = "") -> str:
    """Get the current agent trust registry."""
    allowed, msg, tier = check_access(api_key)
    if not allowed:
        return {"error": msg, "upgrade_url": "https://meok.ai/pricing"}

    return {"agents": _trust_registry, "total": len(_trust_registry)}
    return {"agents": _trust_registry, "total": len(_trust_registry)}

@mcp.tool()
def get_a2a_audit_trail(limit: int = 20, api_key: str = "") -> str:
    """Get audit trail of all A2A governance checks."""
    allowed, msg, tier = check_access(api_key)
    if not allowed:
        return {"error": msg, "upgrade_url": "https://meok.ai/pricing"}

    return {"total": len(_audit_trail), "recent": _audit_trail[-limit:]}
    return {"total": len(_audit_trail), "recent": _audit_trail[-limit:]}

@mcp.tool()
def cross_agent_risk_score(agents: str, task_complexity: str = "medium", api_key: str = "") -> str:
    """Calculate composite risk score for a multi-agent workflow."""
    allowed, msg, tier = check_access(api_key)
    if not allowed:
        return {"error": msg, "upgrade_url": "https://meok.ai/pricing"}

    if err := _rl(): return err
    agent_list = [a.strip() for a in agents.split(",")]
    scores = [_trust_registry.get(a, {}).get("score", 0) for a in agent_list]
    avg = sum(scores) / max(len(scores), 1)
    complexity_mult = {"low": 0.8, "medium": 1.0, "high": 1.3, "critical": 1.5}.get(task_complexity, 1.0)
    risk = round(max(0, 1.0 - avg) * complexity_mult, 2)
    return {"agents": agent_list, "individual_trust": dict(zip(agent_list, scores)),
        "average_trust": round(avg, 2), "task_complexity": task_complexity,
        "composite_risk": risk, "recommendation": "Proceed" if risk < 0.5 else "Add human oversight" if risk < 0.8 else "Block transaction"}

if __name__ == "__main__":
    mcp.run()
