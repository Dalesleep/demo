import json
from pathlib import Path

from app.services.mcp_registry import get_mcp_registry


def test_mcp_registry_loads_mock_server():
    registry = get_mcp_registry()
    servers = registry.servers()

    assert any(server.id == "mock-server" for server in servers)
    mock = next(server for server in servers if server.id == "mock-server")
    assert mock.status == "online"


def test_mcp_registry_tools_exposes_mock_tools():
    registry = get_mcp_registry()
    tools = registry.tools()
    tool_names = {tool.tool_name for tool in tools}

    assert tool_names == {"search_docs", "analyze_text"}


def test_mcp_registry_enabled_false_changes_status_and_tools(tmp_path: Path):
    config_path = tmp_path / "mcp.json"
    config_path.write_text(
        json.dumps(
            {
                "mcpServers": [
                    {
                        "id": "mock-server",
                        "name": "Mock MCP",
                        "transport": "mock",
                        "enabled": False,
                    }
                ]
            }
        ),
        encoding="utf-8",
    )

    from app.services.mcp_registry import MCPRegistryService

    registry = MCPRegistryService(config_path)
    servers = registry.servers()

    assert servers[0].status == "offline"
    assert registry.tools() == []

