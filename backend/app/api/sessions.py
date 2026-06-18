from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.sessions.store import get_session_store


router = APIRouter()


class SessionCreateResponse(BaseModel):
    session_id: str


class SessionSkillsRequest(BaseModel):
    active_skills: list[str] = Field(default_factory=list)


@router.post("/sessions", response_model=SessionCreateResponse)
def create_session() -> SessionCreateResponse:
    store = get_session_store()
    session = store.create()
    return SessionCreateResponse(session_id=session.session_id)


@router.get("/sessions/{session_id}")
def get_session(session_id: str) -> dict:
    store = get_session_store()
    session = store.get(session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Session not found")
    return session.to_dict()


@router.post("/sessions/{session_id}/reset")
def reset_session(session_id: str) -> dict:
    store = get_session_store()
    ok = store.reset(session_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Session not found")
    return {"status": "reset"}


@router.post("/sessions/{session_id}/skills")
def update_session_skills(session_id: str, req: SessionSkillsRequest) -> dict:
    store = get_session_store()
    ok = store.set_active_skills(session_id, req.active_skills)
    if not ok:
        raise HTTPException(status_code=404, detail="Session not found")
    return {"session_id": session_id, "active_skills": req.active_skills}
