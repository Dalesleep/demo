from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from threading import Lock
from typing import Any, Literal
import json

from pydantic import BaseModel, Field, ValidationError, model_validator
from pydantic_deep.mcp import MCPRegistry as DeepMCPRegistry
from pydantic_deep.mcp import MCPServerConfig, MCPTransport

from app.core.config import get_settings

MCPStatus = Literal["online", "offline", "degraded"]


class MCPServerDefinition(BaseModel):
    id: str = Field(min_length=1)
    name: str = Field(min_length=1)
    transport: Literal["mock", "stdio", "http", "sse"]
    enabled: bool = True
    description: str = ""
    command: str | None = None
    args: list[str] = Field(default_factory=list)
    env: dict[str, str] = Field(default_factory=dict)
    url: str | None = None
    headers: dict[str, str] = Field(default_factory=dict)
    tool_prefix: str | None = None

    @model_validator(mode="after")
    def validate_transport_fields(self):
        if self.transport == "stdio" and not self.command:
            raise ValueError("stdio transport requires command")
        if self.transport in {"http", "sse"} and not self.url:
            raise ValueError(f"{self.transport} transport requires url")
        return self


class MCPConfigFile(BaseModel):
    mcpServers: list[MCPServerDefinition] = Field(default_factory=list)


@dataclass
class MCPTool:
    server_id: str
    tool_name: str


@dataclass
class MCPServerView:
    id: str
    name: str
    transport: str
    status: MCPStatus
    enabled: bool
    description: str = ""


class MCPRegistryService:
    def __init__(self, config_path: str | Path | None = None) -> None:
        self._lock = Lock()
        self._config_path = Path(config_path or get_settings().mcp_config_path)
        self._registry = DeepMCPRegistry([])
        self._definitions: list[MCPServerDefinition] = []
        self._tools: list[MCPTool] = []
        self._servers: list[MCPServerView] = []
        self.reload()

    def _load_config(self) -> MCPConfigFile:
        if not self._config_path.exists():
            return MCPConfigFile()
        raw = json.loads(self._config_path.read_text(encoding="utf-8"))
        return MCPConfigFile.model_validate(raw)

    def _status_for(self, definition: MCPServerDefinition) -> MCPStatus:
        if not definition.enabled:
            return "offline"
        if definition.transport == "mock":
            return "online"
        try:
            config = self._to_deep_config(definition)
            if self._registry.status(config) == "ready":
                return "online"
            return "degraded"
        except Exception:
            return "degraded"

    def _to_deep_config(self, definition: MCPServerDefinition) -> MCPServerConfig:
        transport_map: dict[str, MCPTransport] = {"stdio": "stdio", "http": "http", "sse": "sse"}
        return MCPServerConfig(
            name=definition.name,
            transport=transport_map[definition.transport],
            command=definition.command,
            args=definition.args,
            env=definition.env,
            url=definition.url,
            headers=definition.headers,
            tool_prefix=definition.tool_prefix,
            enabled=definition.enabled,
            description=definition.description,
        )

    def _tools_for(self, definition: MCPServerDefinition) -> list[MCPTool]:
        if not definition.enabled:
            return []
        if definition.transport == "mock":
            return [
                MCPTool(server_id=definition.id, tool_name="search_docs"),
                MCPTool(server_id=definition.id, tool_name="analyze_text"),
            ]
        return []

    def reload(self) -> None:
        with self._lock:
            config = self._load_config()
            self._definitions = config.mcpServers
            self._servers = [
                MCPServerView(
                    id=definition.id,
                    name=definition.name,
                    transport=definition.transport,
                    status=self._status_for(definition),
                    enabled=definition.enabled,
                    description=definition.description,
                )
                for definition in self._definitions
            ]
            self._tools = []
            for definition in self._definitions:
                self._tools.extend(self._tools_for(definition))

    def probe(self) -> list[MCPServerView]:
        with self._lock:
            self._servers = [
                MCPServerView(
                    id=definition.id,
                    name=definition.name,
                    transport=definition.transport,
                    status=self._status_for(definition),
                    enabled=definition.enabled,
                    description=definition.description,
                )
                for definition in self._definitions
            ]
            return list(self._servers)

    def servers(self) -> list[MCPServerView]:
        return list(self._servers)

    def tools(self) -> list[MCPTool]:
        return list(self._tools)

    def available_context(self) -> dict[str, Any]:
        return {
            "available_mcp_servers": [server.__dict__ for server in self.servers()],
            "available_tools": [tool.__dict__ for tool in self.tools()],
        }


_mcp_registry = MCPRegistryService()


def get_mcp_registry() -> MCPRegistryService:
    return _mcp_registry

