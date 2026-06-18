from fastapi import APIRouter

from app.services.mcp_registry import get_mcp_registry


router = APIRouter()


@router.get("/mcp/servers")
def list_mcp_servers() -> list[dict]:
    registry = get_mcp_registry()
    return [server.__dict__ for server in registry.servers()]


@router.get("/mcp/tools")
def list_mcp_tools() -> list[dict]:
    registry = get_mcp_registry()
    return [tool.__dict__ for tool in registry.tools()]


@router.post("/mcp/reload")
def reload_mcp() -> dict:
    registry = get_mcp_registry()
    registry.reload()
    return {"status": "reloaded"}

