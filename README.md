<div align="center">

# A2A Governance Bridge MCP

**MCP server for a2a governance bridge mcp operations**

[![PyPI](https://img.shields.io/pypi/v/meok-a2a-governance-bridge-mcp)](https://pypi.org/project/meok-a2a-governance-bridge-mcp/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![MEOK AI Labs](https://img.shields.io/badge/MEOK_AI_Labs-MCP_Server-purple)](https://meok.ai)

</div>

## Overview

A2A Governance Bridge MCP provides AI-powered tools via the Model Context Protocol (MCP).

## Tools

| Tool | Description |
|------|-------------|
| `verify_agent_compliance` | Verify a remote agent meets compliance requirements before allowing A2A transact |
| `authorize_a2a_transaction` | Authorize an agent-to-agent transaction after compliance verification. |
| `get_trust_registry` | Get the current agent trust registry. |
| `get_a2a_audit_trail` | Get audit trail of all A2A governance checks. |
| `cross_agent_risk_score` | Calculate composite risk score for a multi-agent workflow. |

## Installation

```bash
pip install meok-a2a-governance-bridge-mcp
```

## Usage with Claude Desktop

Add to your Claude Desktop MCP config (`claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "a2a-governance-bridge-mcp": {
      "command": "python",
      "args": ["-m", "meok_a2a_governance_bridge_mcp.server"]
    }
  }
}
```

## Usage with FastMCP

```python
from mcp.server.fastmcp import FastMCP

# This server exposes 5 tool(s) via MCP
# See server.py for full implementation
```

## License

MIT © [MEOK AI Labs](https://meok.ai)
