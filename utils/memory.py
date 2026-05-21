import json
import os
from datetime import datetime
from typing import Any, Dict, List, Optional


class SessionMemory:
    def __init__(self):
        self.context: Dict[str, str] = {}
        self.history: List[Dict[str, Any]] = []
        self.current_question: Optional[str] = None
        self.created_at: datetime = datetime.now()

    def set_context(self, role: str, background: str, focus: str) -> None:
        self.context = {"role": role, "background": background, "focus": focus}

    def add_question(self, question: str) -> None:
        self.current_question = question

    def add_answer(self, answer: str) -> None:
        self.history.append(
            {
                "question": self.current_question,
                "answer": answer,
                "evaluation": None,
            }
        )

    def add_evaluation(self, evaluation: Dict[str, Any]) -> None:
        if self.history:
            self.history[-1]["evaluation"] = evaluation

    def get_current_qa(self) -> Optional[Dict[str, Any]]:
        return self.history[-1] if self.history else None

    def get_history(self) -> List[Dict[str, Any]]:
        return self.history

    def get_turn_count(self) -> int:
        return len(self.history)

    def get_weak_answers(self, count: int = 3) -> List[Dict[str, Any]]:
        scored = [
            entry
            for entry in self.history
            if entry.get("evaluation") and entry["evaluation"].get("score") is not None
        ]
        scored.sort(key=lambda x: x["evaluation"]["score"])
        return scored[:count]

    def get_average_score(self) -> Optional[float]:
        scored = [
            entry["evaluation"]["score"]
            for entry in self.history
            if entry.get("evaluation") and entry["evaluation"].get("score") is not None
        ]
        return round(sum(scored) / len(scored), 1) if scored else None

    def save_transcript(self) -> str:
        os.makedirs("transcripts", exist_ok=True)
        filename = f"transcripts/session_{self.created_at.strftime('%Y%m%d_%H%M%S')}.json"
        payload = {
            "context": self.context,
            "history": self.history,
            "created_at": self.created_at.isoformat(),
            "average_score": self.get_average_score(),
        }
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2, ensure_ascii=False)
        return filename
