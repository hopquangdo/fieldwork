from __future__ import annotations

from pydantic import BaseModel, Field


class AnswerOut(BaseModel):
    q_id: str
    folder: str | None = Field(None, description="Chosen folder name from the candidates, or null if none fit.")
    is_blueprint: bool = Field(False, description="True if the image is a hand-drawn blueprint (white paper, pen lines).")
    confidence: float = Field(0.0, ge=0.0, le=1.0)


class BatchAnswer(BaseModel):
    answers: list[AnswerOut]
