from typing import Any, Dict, List

from utils.llm import call_llm
from utils.prompt_loader import load_prompt


class InterviewerAgent:
    def __init__(self):
        self._prompt = load_prompt("interviewer")

    def ask_opening(self, role: str, focus: str) -> str:
        prompt = f"""{self._prompt}

===== TASK: OPENING QUESTION =====
Role being interviewed for: {role}
Focus areas for this interview: {focus}

Generate ONE strong opening question that:
- Establishes rapport and sets a professional tone
- Is broad enough to reveal the candidate's background
- Naturally leads to deeper follow-up
- Sounds like a real interviewer, not a template

Return ONLY the question text. No preamble, no labels, no punctuation beyond the question itself."""
        return call_llm(prompt, max_tokens=200)

    def ask_followup(
        self,
        history: List[Dict[str, Any]],
        strategy: Dict[str, Any],
        context: Dict[str, str],
    ) -> str:
        history_text = self._format_history(history)
        action = strategy.get("action", "move_on")
        reason = strategy.get("reason", "")
        next_focus = strategy.get("next_focus", "")

        prompt = f"""{self._prompt}

===== INTERVIEW CONTEXT =====
Role: {context.get('role')}
Candidate Background: {context.get('background')}
Interview Focus: {context.get('focus')}

===== CONVERSATION SO FAR =====
{history_text}

===== STRATEGIST DIRECTIVE =====
Action: {action}
Reason: {reason}
Next Focus Area: {next_focus}

===== TASK: GENERATE NEXT QUESTION =====
Based on the strategist directive, generate ONE question:

- probe_deeper  → Dig into the candidate's last answer. Ask "why", "how did that work", "what was your specific role", or expose a gap you noticed.
- move_on       → Ask a fresh, unrelated question on a new topic relevant to the role.
- increase_difficulty → Escalate: ask something harder, more scenario-based, or require deeper expertise than anything asked so far.
- change_topic  → Pivot cleanly to: "{next_focus}". Make the transition sound natural.

IMPORTANT:
- Do NOT repeat any question already asked.
- Sound like a real human interviewer.
- One question only. No preamble or labels.

Return ONLY the question text."""
        return call_llm(prompt, max_tokens=200)

    def _format_history(self, history: List[Dict[str, Any]]) -> str:
        lines = []
        for i, entry in enumerate(history, 1):
            lines.append(f"Q{i}: {entry['question']}")
            lines.append(f"A{i}: {entry['answer']}")
            eval_data = entry.get("evaluation") or {}
            if eval_data.get("score"):
                lines.append(
                    f"    [Score: {eval_data['score']}/10 | Topic: {eval_data.get('topic', '?')}]"
                )
        return "\n".join(lines)
