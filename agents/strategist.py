import json
import re
from typing import Any, Dict, List

from utils.llm import call_llm
from utils.prompt_loader import load_prompt

_FALLBACK_STRATEGY: Dict[str, str] = {
    "action": "move_on",
    "reason": "Default fallback — moving to next topic.",
    "next_focus": "next relevant skill area",
}


class StrategistAgent:
    def __init__(self):
        self._prompt = load_prompt("strategist")

    def decide(
        self, history: List[Dict[str, Any]], last_evaluation: Dict[str, Any]
    ) -> Dict[str, str]:
        history_summary = self._summarize_history(history)
        consecutive_low = self._count_consecutive_low_scores(history)
        consecutive_high = self._count_consecutive_high_scores(history)

        prompt = f"""{self._prompt}

===== INTERVIEW STATE =====
Turn-by-turn history:
{history_summary}

Consecutive low scores (< 5): {consecutive_low}
Consecutive high scores (>= 8): {consecutive_high}

===== LATEST EVALUATION =====
Score:            {last_evaluation.get('score')}/10
Topic:            {last_evaluation.get('topic')}
Depth:            {last_evaluation.get('depth')}/10
Correctness:      {last_evaluation.get('correctness')}/10
Confidence:       {last_evaluation.get('confidence_level')}
Follow-up Needed: {last_evaluation.get('follow_up_needed')}
Weaknesses:       {last_evaluation.get('weaknesses')}

===== OUTPUT RULES =====
Return a JSON object with EXACTLY this structure and NO other text:

{{
  "action": "<probe_deeper|move_on|increase_difficulty|change_topic>",
  "reason": "<one clear sentence explaining why this action>",
  "next_focus": "<concrete topic or skill area for the next question>"
}}

Strictly return only the JSON. No markdown fences, no explanation."""

        raw = call_llm(prompt, max_tokens=250)
        return self._parse_json(raw)

    def _summarize_history(self, history: List[Dict[str, Any]]) -> str:
        lines = []
        for i, entry in enumerate(history, 1):
            eval_data = entry.get("evaluation") or {}
            score = eval_data.get("score", "N/A")
            topic = eval_data.get("topic", "unknown")
            fu = eval_data.get("follow_up_needed", False)
            lines.append(f"  Turn {i}: topic={topic}, score={score}/10, follow_up_needed={fu}")
        return "\n".join(lines) if lines else "  No turns yet."

    def _count_consecutive_low_scores(self, history: List[Dict[str, Any]]) -> int:
        count = 0
        for entry in reversed(history):
            score = (entry.get("evaluation") or {}).get("score")
            if score is not None and score < 5:
                count += 1
            else:
                break
        return count

    def _count_consecutive_high_scores(self, history: List[Dict[str, Any]]) -> int:
        count = 0
        for entry in reversed(history):
            score = (entry.get("evaluation") or {}).get("score")
            if score is not None and score >= 8:
                count += 1
            else:
                break
        return count

    def _parse_json(self, text: str) -> Dict[str, str]:
        text = text.strip()
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
        try:
            result = json.loads(text)
            valid_actions = {"probe_deeper", "move_on", "increase_difficulty", "change_topic"}
            if result.get("action") not in valid_actions:
                result["action"] = "move_on"
            return result
        except json.JSONDecodeError:
            return _FALLBACK_STRATEGY.copy()
