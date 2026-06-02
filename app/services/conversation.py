from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass
class ConversationTurn:
    role: str
    content: str
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


@dataclass
class ConversationSession:
    session_id: str
    turns: list[ConversationTurn] = field(default_factory=list)

    def add(self, role: str, content: str) -> None:
        self.turns.append(ConversationTurn(role=role, content=content))

    def context_block(self, max_turns: int = 6) -> str:
        recent = self.turns[-max_turns:]
        lines = [f"{t.role}: {t.content}" for t in recent]
        return "\n".join(lines)


class ConversationStore:
    def __init__(self) -> None:
        self._sessions: dict[str, ConversationSession] = {}

    def create(self) -> str:
        session_id = str(uuid.uuid4())
        self._sessions[session_id] = ConversationSession(session_id=session_id)
        return session_id

    def get(self, session_id: str) -> ConversationSession | None:
        return self._sessions.get(session_id)

    def get_or_create(self, session_id: str | None) -> tuple[str, ConversationSession]:
        if session_id and session_id in self._sessions:
            return session_id, self._sessions[session_id]
        new_id = self.create()
        return new_id, self._sessions[new_id]
