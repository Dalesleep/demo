from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from threading import Lock
from uuid import uuid4

from app.sessions.models import ChatMessage, SessionRecord, make_default_deps


@dataclass
class InMemorySessionStore:
    _sessions: dict[str, SessionRecord]
    _lock: Lock

    def create(self) -> SessionRecord:
        with self._lock:
            session_id = uuid4().hex
            session = SessionRecord(session_id=session_id, deps=make_default_deps())
            self._sessions[session_id] = session
            return session

    def get(self, session_id: str) -> SessionRecord | None:
        return self._sessions.get(session_id)

    def reset(self, session_id: str) -> bool:
        with self._lock:
            session = self._sessions.get(session_id)
            if session is None:
                return False
            session.messages = []
            session.updated_at = datetime.now(timezone.utc)
            session.deps = make_default_deps()
            return True

    def set_active_skills(self, session_id: str, active_skills: list[str]) -> bool:
        with self._lock:
            session = self._sessions.get(session_id)
            if session is None:
                return False
            session.active_skills = active_skills
            session.updated_at = datetime.now(timezone.utc)
            return True

    def append_message(self, session_id: str, role: str, content: str) -> None:
        with self._lock:
            session = self._sessions.get(session_id)
            if session is None:
                return
            session.messages.append(ChatMessage(role=role, content=content))
            session.updated_at = datetime.now(timezone.utc)


_store = InMemorySessionStore(_sessions={}, _lock=Lock())


def get_session_store() -> InMemorySessionStore:
    return _store
