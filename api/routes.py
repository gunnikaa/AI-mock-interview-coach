import uuid
from typing import Dict

from fastapi import APIRouter, HTTPException

from agents.coach import CoachAgent
from agents.evaluator import EvaluatorAgent
from agents.interviewer import InterviewerAgent
from agents.rewriter import RewriterAgent
from agents.strategist import StrategistAgent
from models.schemas import (
    AnswerRequest,
    AnswerResponse,
    FeedbackResponse,
    StartRequest,
    StartResponse,
)
from utils.memory import SessionMemory

router = APIRouter()

# In-memory session store (sufficient for localhost single-user use)
_sessions: Dict[str, SessionMemory] = {}

# Agent singletons — instantiated once, reused across requests
_interviewer = InterviewerAgent()
_evaluator = EvaluatorAgent()
_strategist = StrategistAgent()
_coach = CoachAgent()
_rewriter = RewriterAgent()

MAX_TURNS = 6  # 5–7 range; configurable


@router.post("/start", response_model=StartResponse)
async def start_interview(request: StartRequest):
    """
    Begin a new mock interview session.
    Returns a session_id and the first question.
    """
    try:
        session_id = str(uuid.uuid4())
        memory = SessionMemory()
        memory.set_context(request.role, request.background, request.focus)
        _sessions[session_id] = memory

        opening_question = _interviewer.ask_opening(request.role, request.focus)
        memory.add_question(opening_question)

        return StartResponse(session_id=session_id, question=opening_question, turn=1)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/answer", response_model=AnswerResponse)
async def submit_answer(request: AnswerRequest):
    """
    Submit a candidate's answer (typed or speech-to-text).
    Runs Evaluator → Strategist → Interviewer pipeline.
    Returns the next question or signals interview completion.
    """
    memory = _sessions.get(request.session_id)
    if memory is None:
        raise HTTPException(status_code=404, detail="Session not found. Call POST /start first.")

    if not request.answer.strip():
        raise HTTPException(status_code=422, detail="Answer cannot be empty.")

    # Step 1: Record the answer
    memory.add_answer(request.answer)

    # Step 2: Evaluate — fall back to neutral evaluation if it fails
    current_qa = memory.get_current_qa()
    try:
        evaluation = _evaluator.evaluate(current_qa)
    except Exception as e:
        print(f"[WARN] Evaluator failed: {e}")
        evaluation = {
            "score": 6, "strengths": [], "weaknesses": [],
            "clarity": 6, "depth": 6, "correctness": 6,
            "confidence_level": "medium", "filler_word_usage": "medium",
            "fluency": "average", "delivery_notes": "Evaluation skipped due to API error.",
            "follow_up_needed": False, "topic": "general",
        }
    memory.add_evaluation(evaluation)

    turn = memory.get_turn_count()
    if turn >= MAX_TURNS:
        return AnswerResponse(question="", turn=turn, done=True)

    # Step 3: Strategy — fall back to "move_on" if it fails
    try:
        strategy = _strategist.decide(memory.get_history(), evaluation)
    except Exception as e:
        print(f"[WARN] Strategist failed: {e}")
        strategy = {"action": "move_on", "reason": "fallback", "next_focus": "next topic"}

    # Step 4: Next question — this one we DO need; if it fails return 500
    try:
        next_question = _interviewer.ask_followup(
            memory.get_history(), strategy, memory.context
        )
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail=f"Could not generate next question (likely rate limit). Wait 60s and try the same answer again. Error: {e}",
        )

    memory.add_question(next_question)
    return AnswerResponse(question=next_question, turn=turn + 1, done=False)


@router.get("/feedback", response_model=FeedbackResponse)
async def get_feedback(session_id: str):
    """
    Retrieve full coaching feedback and rewritten answers after interview completion.
    Saves a JSON transcript to the /transcripts directory.
    """
    memory = _sessions.get(session_id)
    if memory is None:
        raise HTTPException(status_code=404, detail="Session not found.")

    if memory.get_turn_count() == 0:
        raise HTTPException(status_code=400, detail="No answers recorded yet.")

    history = memory.get_history()

    try:
        # Coach generates full markdown feedback
        feedback_markdown = _coach.generate_feedback(history, memory.context)
    except Exception as e:
        feedback_markdown = (
            f"## Feedback Unavailable\n\n"
            f"The coach agent failed to generate feedback. Error:\n\n`{e}`\n\n"
            f"Your interview was still recorded. Try again or check the backend logs."
        )

    # Rewriter improves the 3 weakest answers — wrap each so one failure doesn't kill all
    weak_answers = memory.get_weak_answers(count=3)
    rewritten_answers = []
    for qa in weak_answers:
        try:
            rewritten_answers.append(_rewriter.rewrite(qa))
        except Exception as e:
            rewritten_answers.append({
                "original": qa.get("answer", ""),
                "improved": f"(Could not generate rewrite: {e})",
                "what_changed": ["Rewriter failed for this answer."],
            })

    # Persist transcript to disk (best-effort)
    try:
        memory.save_transcript()
    except Exception as e:
        print(f"[WARN] Could not save transcript: {e}")

    return FeedbackResponse(
        feedback_markdown=feedback_markdown,
        rewritten_answers=rewritten_answers,
        total_turns=memory.get_turn_count(),
        average_score=memory.get_average_score() or 0.0,
    )


@router.delete("/session/{session_id}")
async def delete_session(session_id: str):
    """Clean up a session from memory."""
    if session_id not in _sessions:
        raise HTTPException(status_code=404, detail="Session not found.")
    del _sessions[session_id]
    return {"message": "Session deleted."}
