from typing import Any, Dict, List

from utils.llm import call_llm
from utils.prompt_loader import load_prompt


class CoachAgent:
    def __init__(self):
        self._prompt = load_prompt("coach")

    def generate_feedback(
        self, history: List[Dict[str, Any]], context: Dict[str, str]
    ) -> str:
        history_text = self._format_history(history)
        scores_summary = self._compute_scores(history)

        prompt = f"""{self._prompt}

===== CANDIDATE PROFILE =====
Role Applied For: {context.get('role')}
Background: {context.get('background')}
Interview Focus: {context.get('focus')}

===== FULL INTERVIEW TRANSCRIPT =====
{history_text}

===== AGGREGATE SCORES =====
{scores_summary}

===== TASK =====
Generate comprehensive coaching feedback in Markdown with these EXACT section headers:

## Strengths
## Weaknesses
## Communication Style
## Key Gaps
## What To Practice
## Suggested Questions

Rules:
- Quote directly from candidate's answers to illustrate points
- Be specific, not generic ("You explained X using Y" not "You communicated well")
- For Suggested Questions: provide 5-7 questions tailored to their specific gaps
- Tone: honest, direct, constructive — like a mentor, not a cheerleader"""

        return call_llm(prompt)

    def _format_history(self, history: List[Dict[str, Any]]) -> str:
        lines = []
        for i, entry in enumerate(history, 1):
            eval_data = entry.get("evaluation") or {}
            lines.append(f"\n--- Turn {i} | Topic: {eval_data.get('topic', '?')} ---")
            lines.append(f"Interviewer: {entry['question']}")
            lines.append(f"Candidate:   {entry['answer']}")
            if eval_data:
                lines.append(
                    f"  Score: {eval_data.get('score')}/10  |  "
                    f"Confidence: {eval_data.get('confidence_level')}  |  "
                    f"Fluency: {eval_data.get('fluency')}  |  "
                    f"Fillers: {eval_data.get('filler_word_usage')}"
                )
                if eval_data.get("strengths"):
                    lines.append(f"  Strengths: {', '.join(eval_data['strengths'])}")
                if eval_data.get("weaknesses"):
                    lines.append(f"  Weaknesses: {', '.join(eval_data['weaknesses'])}")
                if eval_data.get("delivery_notes"):
                    lines.append(f"  Delivery: {eval_data['delivery_notes']}")
        return "\n".join(lines)

    def _compute_scores(self, history: List[Dict[str, Any]]) -> str:
        evaluated = [e for e in history if e.get("evaluation")]
        if not evaluated:
            return "No evaluations available."

        def avg(key: str) -> str:
            vals = [e["evaluation"].get(key, 0) for e in evaluated if e["evaluation"].get(key)]
            return f"{sum(vals)/len(vals):.1f}" if vals else "N/A"

        confidence_counts: Dict[str, int] = {"low": 0, "medium": 0, "high": 0}
        fluency_counts: Dict[str, int] = {"poor": 0, "average": 0, "good": 0}
        for e in evaluated:
            ev = e["evaluation"]
            cl = ev.get("confidence_level", "medium")
            fl = ev.get("fluency", "average")
            confidence_counts[cl] = confidence_counts.get(cl, 0) + 1
            fluency_counts[fl] = fluency_counts.get(fl, 0) + 1

        dominant_confidence = max(confidence_counts, key=lambda k: confidence_counts[k])
        dominant_fluency = max(fluency_counts, key=lambda k: fluency_counts[k])

        return (
            f"Average Score: {avg('score')}/10  |  "
            f"Avg Clarity: {avg('clarity')}/10  |  "
            f"Avg Depth: {avg('depth')}/10  |  "
            f"Avg Correctness: {avg('correctness')}/10\n"
            f"Dominant Confidence: {dominant_confidence}  |  "
            f"Dominant Fluency: {dominant_fluency}"
        )
