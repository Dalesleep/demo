from __future__ import annotations

from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from typing import Any

from pydantic_deep import DeepAgentDeps, StateBackend


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


@dataclass
class ChatMessage:
    role: str
    content: str
    created_at: datetime = field(default_factory=utc_now)


@dataclass
class SessionRecord:
    session_id: str
    messages: list[ChatMessage] = field(default_factory=list)
    created_at: datetime = field(default_factory=utc_now)
    updated_at: datetime = field(default_factory=utc_now)
    meta: dict[str, Any] = field(default_factory=dict)
    active_skills: list[str] = field(default_factory=list)
    deps: DeepAgentDeps = field(default_factory=lambda: DeepAgentDeps(backend=StateBackend()))

    def to_dict(self) -> dict[str, Any]:
        return {
            "session_id": self.session_id,
            "messages": [asdict(m) for m in self.messages],
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "meta": self.meta,
            "active_skills": self.active_skills,
        }


def make_default_deps() -> DeepAgentDeps:
    return DeepAgentDeps(backend=StateBackend())
