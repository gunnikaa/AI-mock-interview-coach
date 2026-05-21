from pydantic import BaseModel
from typing import Any, Dict, List, Optional


class StartRequest(BaseModel):
    role: str
    background: str
    focus: str


class AnswerRequest(BaseModel):
    session_id: str
    answer: str


class StartResponse(BaseModel):
    session_id: str
    question: str
    turn: int


class AnswerResponse(BaseModel):
    question: str
    turn: int
    done: bool


class RewrittenAnswer(BaseModel):
    original: str
    improved: str
    what_changed: List[str]


class FeedbackResponse(BaseModel):
    feedback_markdown: str
    rewritten_answers: List[Dict[str, Any]]
    total_turns: int
    average_score: Optional[float]
