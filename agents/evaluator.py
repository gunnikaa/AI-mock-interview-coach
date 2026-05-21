import json
import re
from typing import Any, Dict

from utils.llm import call_llm
from utils.prompt_loader import load_prompt

_FALLBACK_EVALUATION: Dict[str, Any] = {
    "score": 5,
    "strengths": ["Answer was provided"],
    "weaknesses": ["Could not parse full evaluation"],
    "clarity": 5,
    "depth": 5,
    "correctness": 5,
    "confidence_level": "medium",
    "filler_word_usage": "medium",
    "fluency": "average",
    "delivery_notes": "Evaluation parsing failed — answer may need manual review.",
    "follow_up_needed": True,
    "topic": "general",
}


class EvaluatorAgent:
    def __init__(self):
        self._prompt = load_prompt("evaluator")

    def evaluate(self, qa: Dict[str, Any]) -> Dict[str, Any]:
        question = qa.get("question", "")
        answer = qa.get("answer", "")

        filler_count = self._count_fillers(answer)

        prompt = f"""{self._prompt}

===== INPUT =====
QUESTION ASKED:
{question}

CANDIDATE'S ANSWER (verbatim — may be typed or speech-to-text converted):
{answer}

PRE-COMPUTED HINT — Filler word count detected in text: {filler_count}
(Use this as supporting signal for filler_word_usage, not the only signal.)

===== OUTPUT RULES =====
Return a JSON object with EXACTLY this structure and NO other text:

{{
  "score": <integer 1-10>,
  "strengths": ["<specific strength>", "..."],
  "weaknesses": ["<specific weakness>", "..."],
  "clarity": <integer 1-10>,
  "depth": <integer 1-10>,
  "correctness": <integer 1-10>,
  "confidence_level": "<low|medium|high>",
  "filler_word_usage": "<low|medium|high>",
  "fluency": "<poor|average|good>",
  "delivery_notes": "<2-3 sentences on tone, confidence, and delivery from the text>",
  "follow_up_needed": <true|false>,
  "topic": "<one short topic label, e.g. 'system design', 'leadership', 'algorithms'>"
}}

Strictly return only the JSON. No markdown fences, no explanation."""

        raw = call_llm(prompt, max_tokens=600)
        return self._parse_json(raw)

    def _count_fillers(self, text: str) -> int:
        fillers = [
            r"\bum\b",
            r"\buh\b",
            r"\blike\b",
            r"\byou know\b",
            r"\bsort of\b",
            r"\bkind of\b",
            r"\bbasically\b",
            r"\bactually\b",
            r"\bright\b",
            r"\bokay so\b",
            r"\bso basically\b",
            r"\bi mean\b",
        ]
        count = 0
        lower = text.lower()
        for pattern in fillers:
            count += len(re.findall(pattern, lower))
        return count

    def _parse_json(self, text: str) -> Dict[str, Any]:
        text = text.strip()
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
        try:
            result = json.loads(text)
            result.setdefault("score", 5)
            result.setdefault("strengths", [])
            result.setdefault("weaknesses", [])
            result.setdefault("clarity", 5)
            result.setdefault("depth", 5)
            result.setdefault("correctness", 5)
            result.setdefault("confidence_level", "medium")
            result.setdefault("filler_word_usage", "medium")
            result.setdefault("fluency", "average")
            result.setdefault("delivery_notes", "")
            result.setdefault("follow_up_needed", False)
            result.setdefault("topic", "general")
            return result
        except json.JSONDecodeError:
            return _FALLBACK_EVALUATION.copy()
