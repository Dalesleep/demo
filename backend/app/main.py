from fastapi import FastAPI

from app.api import chat, mcp, sessions, skills
from app.core.config import get_settings


settings = get_settings()

app = FastAPI(title=settings.app_name)

app.include_router(sessions.router, prefix="/api", tags=["sessions"])
app.include_router(chat.router, prefix="/api", tags=["chat"])
app.include_router(skills.router, prefix="/api", tags=["skills"])
app.include_router(mcp.router, prefix="/api", tags=["mcp"])


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
