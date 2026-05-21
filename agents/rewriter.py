import json
import re
from typing import Any, Dict

from utils.llm import call_llm
from utils.prompt_loader import load_prompt


class RewriterAgent:
    def __init__(self):
        self._prompt = load_prompt("rewriter")

    def rewrite(self, qa: Dict[str, Any]) -> Dict[str, Any]:
        evaluation = qa.get("evaluation") or {}
        original_answer = qa.get("answer", "")

        prompt = f"""{self._prompt}

===== INPUT =====
INTERVIEW QUESTION:
{qa.get('question', '')}

CANDIDATE'S ORIGINAL ANSWER:
{original_answer}

EVALUATION CONTEXT:
  Score:            {evaluation.get('score', 'N/A')}/10
  Weaknesses:       {evaluation.get('weaknesses', [])}
  Delivery Notes:   {evaluation.get('delivery_notes', 'N/A')}
  Confidence Level: {evaluation.get('confidence_level', 'N/A')}
  Filler Words:     {evaluation.get('filler_word_usage', 'N/A')}
  Fluency:          {evaluation.get('fluency', 'N/A')}

===== OUTPUT RULES =====
Rewrite the candidate's answer to be exceptional. Return a JSON object with EXACTLY this structure and NO other text:

{{
  "original": "<the original answer reproduced verbatim>",
  "improved": "<the rewritten, polished answer that addresses all weaknesses>",
  "what_changed": [
    "<specific, concrete description of change 1>",
    "<specific, concrete description of change 2>",
    "<specific, concrete description of change 3>"
  ]
}}

Requirements for "improved":
- Apply STAR structure for behavioral questions
- Remove all filler words
- Replace hedging language with confident assertions
- Add specificity (concrete actions, outcomes, numbers where plausible)
- Write it as natural speech, not bullet points
- Do NOT invent fictional companies or accomplishments — stay true to the original idea

Requirements for "what_changed":
- Each item must be specific: "Replaced 'I think maybe' with assertive 'I decided'"
- Not generic: "Added STAR structure" alone is not enough — explain what S/T/A/R became
- Minimum 3 items, maximum 6

Strictly return only the JSON. No markdown fences, no explanation."""

        raw = call_llm(prompt)
        return self._parse_json(raw, original_answer)

    def _parse_json(self, text: str, original: str) -> Dict[str, Any]:
        text = text.strip()
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
        try:
            result = json.loads(text)
            result.setdefault("original", original)
            result.setdefault("improved", "Improvement could not be generated.")
            result.setdefault("what_changed", ["Rewriter encountered an error."])
            return result
        except json.JSONDecodeError:
            return {
                "original": original,
                "improved": "Could not generate improvement due to a parsing error.",
                "what_changed": ["JSON parsing failed — please retry."],
            }
