from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from pydantic_ai import messages

from app.agents.factory import get_agent_for_session
from app.sessions.store import get_session_store


router = APIRouter()


class ChatRequest(BaseModel):
    session_id: str = Field(min_length=1)
    message: str = Field(min_length=1)
    active_skills: list[str] | None = None


class ChatResponse(BaseModel):
    session_id: str
    reply: str
    active_skills: list[str]


def _build_message_history(session_messages: list) -> list[messages.ModelMessage]:
    history: list[messages.ModelMessage] = []
    for message in session_messages:
        if message.role == "user":
            history.append(messages.ModelRequest(parts=[messages.UserPromptPart(message.content)]))
        elif message.role == "assistant":
            history.append(messages.ModelResponse(parts=[messages.TextPart(message.content)]))
    return history


@router.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest) -> ChatResponse:
    store = get_session_store()
    session = store.get(req.session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Session not found")

    if req.active_skills is not None:
        session.active_skills = req.active_skills

    agent = get_agent_for_session(session)
    result = await agent.run(req.message, deps=session.deps, message_history=_build_message_history(session.messages))
    reply = getattr(result, "output", None)
    if reply is None:
        reply = str(result)

    store.append_message(req.session_id, role="user", content=req.message)
    store.append_message(req.session_id, role="assistant", content=reply)
    return ChatResponse(session_id=req.session_id, reply=reply, active_skills=session.active_skills)
